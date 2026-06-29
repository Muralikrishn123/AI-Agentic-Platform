from typing import List, Dict, Any
from app.core.interfaces import Agent, AgentContext, AgentResponse
from app.services.llm.provider import LLMProvider
from app.services.capability_registry import get_capability_registry


class PlannerAgent(Agent):
    """
    Planner Agent - Plans workflows based on required capabilities.
    
    Key Change (v3.0):
    - Plans in terms of CAPABILITIES, not specific agents
    - Doesn't know agent names
    - Capability Registry resolves capabilities to agents
    
    Example:
        User: "Find healthcare companies"
        Planner: Need capability "company_discovery"
        Registry: "CompanyDiscoveryAgent provides that"
    
    Responsibilities:
    - Understand user request
    - Identify required capabilities
    - Create execution plan
    - Let Capability Registry resolve to agents
    """
    
    def __init__(self, llm_provider: LLMProvider, plugin_manager=None):
        super().__init__("PlannerAgent")
        self.llm_provider = llm_provider
        self.capability_registry = get_capability_registry()
        self.plugin_manager = plugin_manager
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """Create a workflow plan from user request."""
        
        # Collect available plugin details to pass into the prompt
        available_plugins = []
        plugin_details = []
        if self.plugin_manager:
            try:
                plugins = await self.plugin_manager.list_plugins()
                for p in plugins:
                    if p.get("enabled"):
                        available_plugins.append(p["name"])
                        disp = p.get("display_name", p["name"])
                        desc = p.get("description", "")
                        plugin_details.append(f"- Name: {p['name']} (Display Name: {disp}) | Description: {desc}")
            except Exception:
                available_plugins = []

        prompt = self._build_planning_prompt(context.user_request, available_plugins, plugin_details)
        
        try:
            llm_response = await self.llm_provider.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4000
            )
            
            workflow_plan = self._parse_workflow_plan(llm_response)
            
            return AgentResponse(
                success=True,
                data={
                    "workflow_plan": workflow_plan,
                    "steps": workflow_plan.get("steps", []),
                    "estimated_duration": workflow_plan.get("estimated_duration"),
                    "required_plugin": workflow_plan.get("required_plugin")
                },
                confidence=0.9,
                next_step="routing"
            )
            
        except Exception as e:
            # Heuristic fallback if LLM call fails (e.g., due to API quota limits)
            req_lower = context.user_request.lower()
            
            # Detect which plugin might fit
            # Check HR
            if any(k in req_lower for k in ["candidate", "recruit", "hiring", "resume", "cv", "job", "staff"]):
                plugin = "hr_recruitment" if "hr_recruitment" in available_plugins else "none"
                goal = "HR Candidate Sourcing and Shortlisting"
                steps = [
                    {"step": 1, "capability": "extract_requirements", "action": "Extract requirements from job description"},
                    {"step": 2, "capability": "candidate_search", "action": "Search and score candidate profiles"},
                    {"step": 3, "capability": "candidate_shortlisting", "action": "Shortlist top matched candidates"}
                ]
            else:
                # B2B / target search
                # Check if any available plugin name is in request
                matched_plugin = None
                for p in available_plugins:
                    if p != "hr_recruitment" and p != "b2b_sales":
                        if p.lower() in req_lower:
                            matched_plugin = p
                            break
                
                # Check healthcare dynamic plugin keywords
                if not matched_plugin and any(k in req_lower for k in ["clinic", "hospital", "doctor", "health", "pediatric", "medical"]):
                    matched_plugin = "healthcare"
                            
                plugin = matched_plugin or ("b2b_sales" if "b2b_sales" in available_plugins else "none")
                goal = f"B2B Target Discovery in {plugin} domain"
                steps = [
                    {"step": 1, "capability": "trigger_monitoring", "action": "Monitor signals and triggers"},
                    {"step": 2, "capability": "icp_matching", "action": "Match targets against ICP criteria"},
                    {"step": 3, "capability": "decision_maker_discovery", "action": "Discover key decision makers"}
                ]
                
            workflow_plan = {
                "goal": goal,
                "steps": steps,
                "required_plugin": plugin,
                "estimated_duration": "1 minute",
                "expected_outputs": ["qualified_leads" if plugin != "hr_recruitment" else "shortlisted_candidates"]
            }
            
            print(f"⚠️  Planner LLM failed ({e}). Returning local heuristic plan for {plugin}.")
            return AgentResponse(
                success=True,
                data={
                    "workflow_plan": workflow_plan,
                    "steps": workflow_plan["steps"],
                    "estimated_duration": workflow_plan["estimated_duration"],
                    "required_plugin": workflow_plan["required_plugin"]
                },
                confidence=0.5,
                next_step="routing"
            )

    
    def _build_planning_prompt(self, user_request: str, available_plugins: list = None, plugin_details: list = None) -> str:
        """Build the prompt for the LLM with available capabilities and plugins."""
        
        # Get available capabilities
        capabilities = self.capability_registry.list_capabilities()
        capabilities_list = "\n".join([
            f"- {cap['name']}: {cap['description']} (category: {cap['category']})"
            for cap in capabilities
        ])

        # Build plugin list for the prompt
        plugins_section = ""
        if plugin_details:
            plugins_section = f"""
Available Plugins (use exact Name in required_plugin field if it matches user's request):
""" + "\n".join(plugin_details)
        elif available_plugins:
            plugins_section = f"""
Available Plugins (use exact Name in required_plugin field if it matches user's request):
""" + "\n".join(f"- {p}" for p in available_plugins)
        
        return f"""You are a workflow planner for a reusable B2B Agentic AI Platform. Given a user request, available capabilities, and available plugins, create an execution plan.

User Request: {user_request}

Available Capabilities:
{capabilities_list if capabilities else "- No capabilities registered yet"}
{plugins_section}

Instructions:
- Plan the workflow in terms of CAPABILITIES needed.
- Inspect the Available Plugins list. If the user request directly matches the domain, keywords, or triggers of any available dynamic/custom plugin, set required_plugin to that plugin's exact "Name" (e.g. "healthcare", "solar_energy").
- If the request relates to general HR, staffing, recruitment, or hiring, set required_plugin to "hr_recruitment".
- If the request relates to general SaaS sales prospecting or SaaS leads discovery, set required_plugin to "b2b_sales".
- If the request is a generic discovery query that does not match any specific custom domain plugin, set required_plugin to "none".
- Return ONLY valid JSON (no markdown, no code blocks):
{{
    "goal": "Main objective",
    "steps": [
        {{"step": 1, "capability": "capability_name", "action": "Description"}},
        {{"step": 2, "capability": "capability_name", "action": "Description"}}
    ],
    "required_plugin": "plugin_name",
    "estimated_duration": "2 minutes",
    "expected_outputs": ["output1", "output2"]
}}
"""
    
    def _parse_workflow_plan(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured workflow plan."""
        import json
        
        # Try to extract JSON from response
        try:
            # Simple JSON parsing (can be enhanced with better extraction)
            start = llm_response.find('{')
            end = llm_response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = llm_response[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        # Fallback to basic plan
        return {
            "goal": "Process user request",
            "steps": [
                {"step": 1, "action": "Analyze request", "agent": "PlannerAgent"},
                {"step": 2, "action": "Route to appropriate handler", "agent": "RouterAgent"}
            ],
            "required_plugin": "none",
            "estimated_duration": "1 minute",
            "expected_outputs": ["workflow_result"]
        }
