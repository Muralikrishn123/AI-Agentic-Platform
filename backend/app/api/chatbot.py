from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.llm import get_llm_provider
from app.database.models import WorkflowModel
from app.api.auth import get_current_user
import json

router = APIRouter()


class ChatbotQueryRequest(BaseModel):
    query: str
    workflow_id: Optional[str] = None
    page_context: Optional[str] = None


SYSTEM_INSTRUCTIONS = """You are the AI Platform Assistant for the "Agentic AI Platform".
Your goal is to answer questions about the application, guide the user on how to use it, and explain specific workflow results (e.g., explaining why a prospect matched, why a candidate was shortlisted, or what signals were identified).

---
ABOUT THE APPLICATION:
1. Multi-Agent AI Platform: Orchestrates collaborative agents (Planner, Research, Qualification, Contact Discovery, Validation, Reflection, and Report Generator) to execute discovery workflows.
2. Domain Plugins: Supports built-in plugins (HR Recruitment, B2B Sales) and custom plugins.
3. Custom Plugins: Users can define custom domains on the "Plugins" page (e.g., "Solar Energy", "Healthcare Equipment") by specifying custom qualification requirements.
4. Settings / Configuration: On the "Settings" page, users configure target organization types, geographies, keywords, size ranges with custom units (e.g., employees, beds, students, sq ft), and target personas (by department/seniority).
5. Dynamic Planner: The Planner Agent analyzes the user's natural language request on the Dashboard and automatically routes it to the most relevant plugin or runs a generic domain discovery.
6. Execution Pipeline: Each workflow runs through:
   - Research (web scraping & entity extraction)
   - Qualification (scoring against settings & custom requirements)
   - Contact Discovery (finding key target personas & emails)
   - Validation & Reflection (quality checks)
   - Report Generation (producing a structured final advisory report)
7. Approvals: Supports Human-in-the-Loop (HITL) checkpoints. Some plugins pause for human review before proceeding to contact discovery.

---
HOW TO RESPOND:
- If the user is asking general questions about how the platform works, how to configure settings, or how to create plugins, provide clear, step-by-step instructions.
- If the user is asking about a specific workflow result they are currently viewing (e.g. "Why did IIT Bombay match?", "Explain the qualification for candidate X", "Why them?"), refer to the provided Workflow Context to give a specific, detailed explanation. If the context does not contain the answer, politely state that.
- Keep responses clean, readable, professional, and relatively concise.
"""


@router.post("/query")
async def query_chatbot(
    request: ChatbotQueryRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Query the chatbot with optional workflow results context."""
    try:
        workflow_context = ""
        
        # 1. Fetch workflow results if workflow_id is provided
        if request.workflow_id and request.workflow_id != "None" and request.workflow_id != "undefined":
            workflow = await WorkflowModel.get_workflow(request.workflow_id)
            if workflow:
                # Find the plugin execution details to list prospects/candidates
                plugin_step = next((s for s in workflow.get("steps", []) if s.get("step") == "plugin_execution"), None)
                pd = plugin_step.get("data", {}) if plugin_step else {}
                
                prospects = pd.get("prospect_list") or pd.get("qualified_companies") or pd.get("prospects") or []
                candidates = pd.get("shortlist") or []
                report_step = next((s for s in workflow.get("steps", []) if s.get("step") == "ReportGenerator" or s.get("agent") == "ReportGenerator"), None)
                report_summary = report_step.get("data", {}).get("report", {}).get("summary", "") if report_step else ""
                
                context_data = {
                    "workflow_id": workflow.get("workflow_id"),
                    "user_request": workflow.get("user_request"),
                    "status": workflow.get("status"),
                    "report_summary": report_summary,
                    "prospects_matched": [
                        {
                            "name": p.get("company", {}).get("name") or p.get("company_name") or p.get("name"),
                            "sector": p.get("company", {}).get("sector") or p.get("sector"),
                            "score": p.get("company", {}).get("icp_score") or p.get("icp_score"),
                            "org_type": p.get("company", {}).get("org_type") or p.get("org_type") or p.get("company", {}).get("funding_stage") or p.get("funding_stage"),
                            "contact": p.get("primary_contact", {}),
                            "reason": p.get("matching_reason") or p.get("company", {}).get("matching_reason")
                        } for p in prospects
                    ] if prospects else [],
                    "candidates_shortlisted": [
                        {
                            "name": c.get("name"),
                            "role": c.get("role"),
                            "score": c.get("match_score"),
                            "skills": c.get("skills", []),
                            "location": c.get("location")
                        } for c in candidates
                    ] if candidates else []
                }
                workflow_context = f"\n\nCURRENT WORKFLOW CONTEXT:\n{json.dumps(context_data, indent=2)}"

        # 2. Build LLM prompt
        prompt = f"{SYSTEM_INSTRUCTIONS}{workflow_context}\n\nUser Question: {request.query}\nAssistant:"
        
        # 3. Call LLM
        llm_provider = get_llm_provider()
        response_text = await llm_provider.generate(prompt, temperature=0.7, max_tokens=1500)
        
        return {
            "success": True,
            "response": response_text
        }
        
    except Exception as e:
        err_msg = str(e).lower()
        is_quota = "429" in err_msg or "quota" in err_msg or "rate limit" in err_msg or "requestsperday" in err_msg
        if is_quota:
            query_lower = request.query.lower()
            if "why" in query_lower or "match" in query_lower or "reason" in query_lower or "explain" in query_lower:
                fallback_reply = (
                    "⚠️ **[Daily AI Quota Limit Reached]**\n\n"
                    "I cannot perform an active LLM analysis on these workflow results right now because the Google Gemini API daily free-tier quota is exhausted.\n\n"
                    "However, based on the local qualification engine, prospects are qualified based on the target organization types and keywords configured in your **ICP & Config** page. For example, if a prospect matches your selected organization types (e.g., Hospital or College) and matches your target keywords (e.g. Solar), it gets a higher match percentage.\n\n"
                    "Please check the matching reason badge or text directly inside the qualified prospect cards below."
                )
            elif "create" in query_lower or "plugin" in query_lower or "domain" in query_lower:
                fallback_reply = (
                    "⚠️ **[Daily AI Quota Limit Reached]**\n\n"
                    "To create a new custom business domain plugin:\n"
                    "1. Navigate to the **Plugins** page.\n"
                    "2. Click the **+ Create Plugin** button.\n"
                    "3. Set the domain name and description.\n"
                    "4. Add your custom qualification requirements and target roles.\n"
                    "5. Save the configuration, and the system will instantly load the new plugin!"
                )
            else:
                fallback_reply = (
                    "⚠️ **[Daily AI Quota Limit Reached]**\n\n"
                    "The daily free-tier API request limit for Gemini has been reached. Please try again later or configure a paid API key in your `.env` file.\n\n"
                    "**Quick Platform Guide:**\n"
                    "- **Run Workflows:** Enter a request (e.g., 'Find hospitals in Delhi needing beds') on the Dashboard.\n"
                    "- **Target Profile:** Update target geographies, keywords, organization size and unit in **ICP & Config**.\n"
                    "- **Manage Domains:** Enable built-in plugins or build custom business configurations under **Plugins**."
                )
            return {
                "success": True,
                "response": fallback_reply
            }
        
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
