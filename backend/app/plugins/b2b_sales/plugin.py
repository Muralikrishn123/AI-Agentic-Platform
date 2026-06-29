"""
B2B Sales Intelligence Plugin — Main Plugin Class.

Implements the full 7-step B2B customer discovery workflow:
  1. TriggerMonitorAgent    — Monitor signals (job posts, funding, leadership changes)
  2. ICPMatcherAgent        — Score companies against configurable ICP
  3. CompanyEnricherAgent   — Validate & enrich company data
  4. DecisionMakerFinder    — Identify contacts by persona config
  5. ContactEnricherAgent   — Enrich with Email, Phone, LinkedIn
  6. ProspectSummaryAgent   — Ranked list + personalised outreach + next actions
  (7. HITL handled by WorkflowEngine after this plugin completes)

Reusability:
  - All ICP/persona criteria are configurable at runtime via /api/config
  - Trigger types, signal strength, scoring thresholds all configurable
  - Zero changes to core platform required for any new domain
"""

from typing import Dict, Any
from app.core.interfaces import Plugin, AgentContext, AgentResponse
from app.services.capability_registry import get_capability_registry, CapabilityCategory
from app.services.agent_registry import get_agent_registry


class B2BSalesPlugin(Plugin):
    """
    B2B Sales Intelligence Plugin.

    Demonstrates platform reusability — completely different domain from HR,
    same Plugin interface, zero core platform changes required.
    """

    def __init__(self):
        super().__init__(
            name="b2b_sales",
            version="1.0.0",
            description="B2B customer discovery: trigger monitoring → ICP matching → company enrichment → decision-maker identification → contact enrichment → actionable prospect summary",
        )
        self._agents: Dict[str, Any] = {}

    async def initialize(self):
        """Register capabilities and initialise all 6 pipeline agents."""
        print(f"🔧 Initializing {self.name} plugin...")

        capability_registry = get_capability_registry()
        agent_registry = get_agent_registry()

        capabilities = [
            ("trigger_monitoring", "Monitor web/market sources for business trigger signals", CapabilityCategory.SEARCH),
            ("icp_matching", "Score companies against Ideal Customer Profile criteria", CapabilityCategory.MATCHING),
            ("company_enrichment", "Validate and enrich company information", CapabilityCategory.EXTRACTION),
            ("decision_maker_discovery", "Identify decision-makers by configurable personas", CapabilityCategory.SEARCH),
            ("contact_enrichment", "Enrich contacts with email, phone and LinkedIn", CapabilityCategory.EXTRACTION),
            ("prospect_summarisation", "Generate ranked prospect list with next actions", CapabilityCategory.REPORTING),
        ]

        for cap_name, description, category in capabilities:
            if not capability_registry.has_capability(cap_name):
                capability_registry.register(
                    name=cap_name,
                    description=description,
                    category=category,
                    agent_name=self._cap_to_agent(cap_name),
                )

        # Import and register agents
        agent_classes = {
            "trigger_monitoring": ("trigger_monitor", "TriggerMonitorAgent"),
            "icp_matching": ("icp_matcher", "ICPMatcherAgent"),
            "company_enrichment": ("company_enricher", "CompanyEnricherAgent"),
            "decision_maker_discovery": ("decision_maker_finder", "DecisionMakerFinderAgent"),
            "contact_enrichment": ("contact_enricher", "ContactEnricherAgent"),
            "prospect_summarisation": ("prospect_summary", "ProspectSummaryAgent"),
        }

        for cap_name, (module_name, class_name) in agent_classes.items():
            try:
                module = __import__(
                    f"app.plugins.b2b_sales.agents.{module_name}",
                    fromlist=[class_name],
                )
                agent_cls = getattr(module, class_name)
                agent = agent_cls()

                if not agent_registry.has_agent(agent.name):
                    agent_registry.register(agent)

                self._agents[cap_name] = agent
                print(f"✅ Registered B2B agent: {agent.name}")

            except Exception as e:
                print(f"⚠️  Failed to load {class_name}: {e}")
                import traceback; traceback.print_exc()

        print(f"✅ {self.name} plugin initialized — {len(self._agents)}/6 agents ready")

    def _cap_to_agent(self, cap: str) -> str:
        mapping = {
            "trigger_monitoring": "TriggerMonitorAgent",
            "icp_matching": "ICPMatcherAgent",
            "company_enrichment": "CompanyEnricherAgent",
            "decision_maker_discovery": "DecisionMakerFinderAgent",
            "contact_enrichment": "ContactEnricherAgent",
            "prospect_summarisation": "ProspectSummaryAgent",
        }
        return mapping.get(cap, cap)

    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Execute the full 6-step B2B sales intelligence pipeline.
        Results from each step feed into the next (pipeline pattern).
        """
        # Load configurable ICP + persona settings from context
        icp_config = context.data.get("icp_config", {
            "min_employees": 50,
            "max_employees": 5000,
            "sectors": ["SaaS", "Cloud Infrastructure", "AI/ML", "FinTech", "Analytics", "Enterprise SaaS"],
            "funding_stages": ["Series A", "Series B", "Series C"],
            "preferred_tech": ["Python", "FastAPI", "React", "Node.js"],
            "geographies": ["India"],
            "min_icp_score": 0.50,
            "trigger_types": ["rapid_hiring", "funding_round", "leadership_change", "product_launch"],
            "min_signal_strength": "medium",
        })

        persona_config = context.data.get("persona_config", {
            "target_seniorities": ["C-Suite", "VP", "Director"],
            "target_departments": ["Engineering", "HR", "Leadership"],
        })

        pipeline_data = {
            "icp_config": icp_config,
            "persona_config": persona_config,
        }
        sub_steps = []

        pipeline = [
            ("trigger_monitoring", "triggers"),
            ("icp_matching", "qualified_companies"),
            ("company_enrichment", "enriched_companies"),
            ("decision_maker_discovery", "companies_with_contacts"),
            ("contact_enrichment", "enriched_prospects"),
            ("prospect_summarisation", "prospect_list"),
        ]

        for cap_name, output_key in pipeline:
            agent = self._agents.get(cap_name)
            if not agent:
                sub_steps.append({"step": cap_name, "success": False, "error": "Agent not loaded"})
                continue

            step_context = AgentContext(
                workflow_id=context.workflow_id,
                user_request=context.user_request,
                current_step=cap_name,
                data=pipeline_data,
            )

            try:
                response = await agent.execute(step_context)
                sub_steps.append({
                    "step": cap_name,
                    "success": response.success,
                    "confidence": response.confidence,
                    "summary": self._step_summary(cap_name, response.data),
                })

                if response.success:
                    # Merge step output into pipeline_data for next step
                    pipeline_data.update(response.data)
                else:
                    sub_steps[-1]["error"] = response.error
                    # Don't abort — some steps can degrade gracefully

            except Exception as e:
                sub_steps.append({"step": cap_name, "success": False, "error": str(e)})

        # Build final output
        prospect_list = pipeline_data.get("prospect_list", [])
        pipeline_summary = pipeline_data.get("pipeline_summary", {})

        return AgentResponse(
            success=True,
            data={
                "plugin": "b2b_sales",
                "domain": "B2B Sales Intelligence — Staffing/Recruitment",
                "sub_steps": sub_steps,
                "prospect_list": prospect_list,
                "pipeline_summary": pipeline_summary,
                "icp_config_used": icp_config,
                "persona_config_used": persona_config,
                "total_prospects": len(prospect_list),
                "high_priority": len([p for p in prospect_list if p.get("priority") == "high"]),
                "requires_hitl_approval": True,
            },
            confidence=0.91,
            next_step="hitl_approval",
        )

    def _step_summary(self, step: str, data: dict) -> str:
        summaries = {
            "trigger_monitoring": f"{data.get('triggers_found', 0)} triggers found across {len(data.get('sources_monitored', []))} sources",
            "icp_matching": f"{data.get('companies_matched', 0)}/{data.get('companies_evaluated', 0)} companies qualify",
            "company_enrichment": f"{data.get('companies_enriched', 0)} companies enriched",
            "decision_maker_discovery": f"{data.get('total_decision_makers_found', 0)} decision-makers identified",
            "contact_enrichment": f"{data.get('total_contacts_enriched', 0)} contacts enriched (email + phone + LinkedIn)",
            "prospect_summarisation": f"{data.get('total_prospects', 0)} prospects ranked, {data.get('high_priority_count', 0)} high-priority",
        }
        return summaries.get(step, "Step completed")

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "capabilities": list(self._agents.keys()),
            "description": self.description,
            "version": self.version,
            "workflow_steps": 6,
            "requires_hitl": True,
        }

    async def cleanup(self):
        print(f"🗑️  Cleaning up {self.name} plugin...")
        self._agents.clear()
