from datetime import datetime
from typing import Dict, Any
from app.core.interfaces import Agent, AgentContext, AgentResponse
from app.services.llm import get_llm_provider


class ReportGenerator(Agent):
    """
    Report Generator - Converts workflow results into structured reports.
    Uses Gemini to generate rich, narrative summaries and conceptual recommendations
    if no domain plugin is active.
    """
    
    def __init__(self):
        super().__init__("ReportGenerator")
        self.llm_provider = get_llm_provider()
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """Generate a rich, narrative report from workflow results."""
        workflow_data = context.data
        
        # Check if a plugin actually executed (has plugin execution steps)
        has_plugin = any(s.get("step") == "plugin_execution" for s in workflow_data.get("steps", []))
        
        # Extract plugin-specific results for richer prompting
        plugin_context_text = ""
        plugin_step = next((s for s in workflow_data.get("steps", []) if s.get("step") == "plugin_execution"), None)
        if plugin_step and plugin_step.get("data"):
            pd = plugin_step["data"]
            plugin_name = pd.get("plugin", plugin_step.get("agent", ""))
            
            if plugin_name == "hr_recruitment":
                shortlist = pd.get("shortlist", [])
                total = pd.get("total_candidates", 0)
                if shortlist:
                    cands = "\n".join(
                        f"  - {c['name']} | {c.get('role','')} | {c.get('experience_years',0)}y exp | "
                        f"Skills: {', '.join(c.get('skills',[])[:4])} | Match: {int(c.get('match_score',0)*100)}% | {c.get('availability','')}"
                        for c in shortlist
                    )
                    plugin_context_text = f"""
Plugin Execution: HR Recruitment
Total Candidates Scanned: {total}
Top 3 Shortlisted Candidates:
{cands}
"""
            elif plugin_name == "b2b_sales":
                prospects = pd.get("prospects", [])
                if prospects:
                    prosp_text = "\n".join(
                        f"  - {p.get('company_name','?')} | {p.get('sector','?')} | {p.get('funding_stage','?')} | "
                        f"Employees: {p.get('employee_count','?')} | Score: {p.get('icp_score','?')}"
                        for p in prospects[:5]
                    )
                    plugin_context_text = f"""
Plugin Execution: B2B Sales Intelligence
Prospects Identified: {len(prospects)}
Top Prospects:
{prosp_text}
"""

        # ── Generate Rich Narrative Summary with Gemini ──
        if has_plugin and plugin_context_text:
            summary_prompt = f"""You are a Lead Analyst for a multi-agent AI Platform.
The platform just completed an automated workflow using an active plugin. Write a professional executive summary for the user.

User Request: {context.user_request}

{plugin_context_text}

Instructions:
1. Start by confirming the plugin ran successfully and what it found.
2. Highlight the top results (candidates or prospects) with specific details.
3. Give 2-3 concrete next-step recommendations for the user.
4. Keep it concise — 3 to 4 paragraphs maximum.
5. Use markdown bold for key names and metrics.
6. Write all text in your own words.
"""
        else:
            summary_prompt = f"""You are a Lead Analyst for a multi-agent AI Platform.
Analyze this request and generate a detailed professional advisory report:

User Request: {context.user_request}
Mode: Conceptual Fallback Discovery

Instructions:
1. Provide a comprehensive summary answering the user's request. 
2. If this is a Fallback Mode request (like a Hospital query), write a detailed, multi-paragraph conceptual guide with concrete operational recommendations.
3. Suggest how the user can leverage our platform's two capabilities to implement this:
   - Sourcing target companies or B2B vendors using B2B Sales intelligence.
   - Hiring implementation specialists or developers using HR Recruitment.
4. Format with professional markdown headers (###), bold styling, and clear action items. Write all text in your own words.
"""
        llm_active = False
        try:
            summary_text = await self.llm_provider.generate(
                prompt=summary_prompt,
                temperature=0.4,
                max_tokens=8000
            )
            llm_active = True
        except Exception as e:
            print(f"⚠️  Report LLM generation failed ({e}). Returning local analytical summary fallback.")
            if has_plugin and plugin_context_text:
                summary_text = f"""### B2B Target Sourcing Executive Summary

The platform has successfully executed the discovery request using the target enrichment engine. 

* **Status**: Discovery completed successfully.
* **Results**: Target entities are available on the **Approvals** screen.
* **Next Steps**: Please review the sourced entities in Approvals, select the targets you wish to proceed with, and approve them.
"""
            else:
                summary_text = f"""### Advisor Report (Local Fallback)

The request '{context.user_request}' was successfully processed.

* **Status**: Completed successfully.
* **Results**:Sourced prospects are available in the **Approvals** tab.
* **Next Steps**:
  1. Navigate to the **Approvals** page.
  2. Review the target listings.
  3. Select preferred contacts to initiate next-stage workflow tasks.
"""

        report = {
            "report_id": f"report_{context.workflow_id}",
            "workflow_id": context.workflow_id,
            "generated_at": datetime.utcnow().isoformat(),
            "user_request": context.user_request,
            "summary": summary_text.strip(),
            "details": self._format_details(workflow_data),
            "metadata": {
                "total_steps": workflow_data.get("total_steps", 0),
                "successful_steps": workflow_data.get("successful_steps", 0),
                "execution_time": workflow_data.get("execution_time", "N/A"),
                "status": workflow_data.get("status", "completed"),
                "plugin_active": has_plugin,
                "llm_active": llm_active
            }
        }
        
        return AgentResponse(
            success=True,
            data={
                "report": report,
                "format": "json",
                "exportable": True
            },
            confidence=1.0
        )
    
    def _format_details(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format workflow details for display."""
        return {
            "workflow_plan": workflow_data.get("workflow_plan", {}),
            "execution_steps": workflow_data.get("steps", []),
            "validation_results": workflow_data.get("validation_results", {}),
            "output": workflow_data.get("output", {}),
            "errors": workflow_data.get("errors", [])
        }
    
    async def generate_dashboard_summary(
        self, 
        workflow_id: str, 
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a quick summary for dashboard display."""
        steps = workflow_data.get("total_steps", 0)
        successful = workflow_data.get("successful_steps", 0)
        return {
            "workflow_id": workflow_id,
            "status": workflow_data.get("status", "unknown"),
            "progress": f"{successful}/{steps}",
            "duration": workflow_data.get("execution_time", "N/A"),
            "summary": f"Workflow completed successfully. {successful}/{steps} steps succeeded."
        }
