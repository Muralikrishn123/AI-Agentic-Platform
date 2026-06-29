from typing import Dict, Any, List
from datetime import datetime
from app.core.interfaces import AgentContext, AgentResponse
from app.database.models import WorkflowModel
from app.services.agent_registry import get_agent_registry
from app.services.memory_service import get_memory_service
import uuid


class WorkflowEngine:
    """
    Workflow Engine - Orchestrates agent execution.
    
    Key Changes:
    - Uses Agent Registry instead of hardcoded agents
    - No Router Agent (Plugin Manager handles routing)
    - Uses Memory Service for state management
    - Supports Reflection Agent for quality checks
    
    Responsibilities:
    - Orchestrate workflow execution
    - Call agents from Agent Registry
    - Handle failures and retries
    - Track execution state
    - Use Memory Service for persistence
    """
    
    def __init__(self, plugin_lifecycle_manager=None):
        self.agent_registry = get_agent_registry()
        self.plugin_lifecycle_manager = plugin_lifecycle_manager
        self.memory_service = get_memory_service()

    
    async def execute_workflow(
        self,
        user_request: str,
        user_id: str,
        selected_plugin_override: str = None,
        workflow_id_override: str = None,
    ) -> Dict[str, Any]:
        """
        Execute workflow using Agent Registry.
        """
        
        workflow_id = workflow_id_override or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        workflow_data = {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "user_request": user_request,
            "status": "in_progress",
            "steps": [],
            "errors": [],
            "retry_count": 0
        }
        
        try:
            # Step 1: Planning (from Agent Registry)
            planner = self.agent_registry.get("PlannerAgent")
            if not planner:
                raise ValueError("PlannerAgent not found in Agent Registry")
            
            planning_result = await self._execute_agent(
                planner,
                workflow_id,
                user_request,
                {}
            )
            workflow_data["steps"].append(planning_result)
            
            if not planning_result["success"]:
                workflow_data["status"] = "failed"
                workflow_data["errors"].append("Planning failed")
                if workflow_id_override:
                    await WorkflowModel.update_workflow(workflow_id, workflow_data)
                else:
                    await WorkflowModel.create_workflow(workflow_data)
                return workflow_data
            
            # Step 2: Plugin Selection
            workflow_plan = planning_result["data"]
            selected_plugin = await self._select_plugin(workflow_plan, user_request, selected_plugin_override)
            
            # Step 3: Plugin Execution (if available)
            if selected_plugin:
                plugin_result = await self._execute_plugin(
                    workflow_id,
                    user_request,
                    selected_plugin,
                    workflow_plan
                )
                workflow_data["steps"].append(plugin_result)

                # Step 3b: HITL Approval (if plugin requests it)
                if plugin_result.get("data", {}).get("requires_hitl_approval"):
                    hitl_agent = self.agent_registry.get("HITLApprovalAgent")
                    if hitl_agent:
                        hitl_result = await self._execute_agent(
                            hitl_agent,
                            workflow_id,
                            user_request,
                            plugin_result.get("data", {}),
                        )
                        workflow_data["steps"].append(hitl_result)
                        workflow_data["hitl_status"] = "pending"
                        workflow_data["hitl_message"] = hitl_result["data"].get("approval_message", "")

            
            # Step 4: Reflection (evaluate workflow quality)
            reflection = self.agent_registry.get("ReflectionAgent")
            if reflection:
                workflow_data["total_steps"] = len(workflow_data["steps"])
                workflow_data["successful_steps"] = sum(1 for s in workflow_data["steps"] if s["success"])
                
                reflection_result = await self._execute_agent(
                    reflection,
                    workflow_id,
                    user_request,
                    workflow_data
                )
                workflow_data["steps"].append(reflection_result)
                
                # Handle retry if reflection suggests it
                if reflection_result.get("data", {}).get("should_retry"):
                    workflow_data["retry_count"] += 1
                    # In a real system, you would retry the workflow here
            
            # Step 5: Validation
            validator = self.agent_registry.get("ValidationAgent")
            if validator:
                validation_context = {
                    "output": workflow_plan,
                    "confidence": planning_result.get("confidence", 1.0)
                }
                validation_result = await self._execute_agent(
                    validator,
                    workflow_id,
                    user_request,
                    validation_context
                )
                workflow_data["steps"].append(validation_result)
            
            # Step 6: Report Generation
            report_generator = self.agent_registry.get("ReportGenerator")
            if report_generator:
                report_context = {
                    "workflow_plan": workflow_plan,
                    "status": "completed",
                    "total_steps": len(workflow_data["steps"]),
                    "successful_steps": sum(1 for s in workflow_data["steps"] if s["success"])
                }
                report_result = await self._execute_agent(
                    report_generator,
                    workflow_id,
                    user_request,
                    report_context
                )
                workflow_data["steps"].append(report_result)
                workflow_data["report"] = report_result["data"]
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            workflow_data["status"] = "completed"
            workflow_data["execution_time"] = f"{execution_time:.2f}s"
            workflow_data["completed_at"] = end_time.isoformat()
            
        except Exception as e:
            workflow_data["status"] = "failed"
            workflow_data["errors"].append(str(e))
        
        # Save/update workflow in database
        if workflow_id_override:
            # Pre-created record exists — update it with final state
            await WorkflowModel.update_workflow(workflow_id, workflow_data)
        else:
            await WorkflowModel.create_workflow(workflow_data)
        
        # Store in memory service
        await self.memory_service.store_workflow_state(
            workflow_id=workflow_id,
            step="final",
            data=workflow_data
        )
        
        return workflow_data
    
    async def _select_plugin(self, workflow_plan: Dict[str, Any], user_request: str = "", selected_plugin_override: str = None) -> str:
        """
        Select plugin using Plugin Lifecycle Manager.
        """
        # If there is an explicit override select it
        if selected_plugin_override and selected_plugin_override != "none" and selected_plugin_override != "":
            return selected_plugin_override

        if not self.plugin_lifecycle_manager:
            return None

        plugins = self.plugin_lifecycle_manager._plugins
        states = getattr(self.plugin_lifecycle_manager, '_states', {})
        from app.services.plugin_lifecycle_manager import PluginState

        # Fetch custom plugins from database
        custom_plugins = []
        custom_names = []
        try:
            from app.database.models import CustomPluginModel
            custom_plugins = await CustomPluginModel.get_plugins()
            custom_names = [cp["name"] for cp in custom_plugins]
        except Exception as e:
            print("Error loading custom plugins for selection:", e)

        def is_enabled(name):
            if name in custom_names:
                return True
            return name in plugins and states.get(name) == PluginState.ENABLED

        # Check if user query matches any custom plugin name OR its target keywords/triggers
        req_lower = user_request.lower()
        for cp in custom_plugins:
            cn = cp["name"]
            cn_space = cn.replace("_", " ")
            
            # Match plugin name directly
            if cn_space in req_lower or cn in req_lower:
                print(f"🔀 Matched custom dynamic plugin by name: {cn}")
                return cn
                
            # Match custom keywords configured on the plugin
            keywords = cp.get("keywords") or []
            if any(k.lower() in req_lower for k in keywords if k):
                print(f"🔀 Matched custom dynamic plugin by keyword: {cn}")
                return cn
                
            # Match custom triggers configured on the plugin
            triggers = cp.get("businessTriggers", cp.get("triggers", []))
            if any(t.lower() in req_lower for t in triggers if t):
                print(f"🔀 Matched custom dynamic plugin by trigger: {cn}")
                return cn

        # ── Step 1: Calculate keyword scores ──
        b2b_keywords = [
            "prospect", "b2b", "lead", "customer discovery", "company", "icp",
            "saas", "sales intelligence", "market", "trigger", "funding",
            "decision maker", "outreach", "pipeline", "crm", "contact enrichment",
            "find companies", "identify companies", "prospecting"
        ]
        hr_keywords = [
            "hire", "hiring", "recruit", "recruitment", "candidate", "staffing",
            "talent", "resume", "job description", "shortlist", "applicant"
        ]

        b2b_score = sum(1 for kw in b2b_keywords if kw in req_lower)
        hr_score  = sum(1 for kw in hr_keywords  if kw in req_lower)

        # If keyword scoring is heavily skewed toward B2B Sales, override LLM
        if b2b_score > 0 and b2b_score > hr_score and is_enabled("b2b_sales"):
            print(f"🔀 Strong B2B keyword signal (score={b2b_score} vs HR={hr_score}): routing to b2b_sales")
            return "b2b_sales"
            
        # If keyword scoring is heavily skewed toward HR, override LLM
        if hr_score > 0 and hr_score > b2b_score and is_enabled("hr_recruitment"):
            print(f"🔀 Strong HR keyword signal (score={hr_score} vs B2B={b2b_score}): routing to hr_recruitment")
            return "hr_recruitment"

        # ── Step 2: Fall back to LLM-selected plugin if keywords are equal or zero ──
        required_plugin = workflow_plan.get("required_plugin", "none")
        if required_plugin and required_plugin != "none" and is_enabled(required_plugin):
            if required_plugin == "b2b_sales":
                # Only use predefined b2b_sales if the query is actually about SaaS, software, or tech
                saas_keywords = ["saas", "software", "tech", "cloud", "developer", "it", "enterprise software", "digital"]
                if not any(k in req_lower for k in saas_keywords):
                    print("🔀 LLM requested b2b_sales, but query is non-SaaS/non-tech. Routing to dynamic generic discovery instead.")
                    return "generic_discovery"
            return required_plugin

        # ── Step 3: Default fallback if nothing matches ──
        if hr_score > 0 and is_enabled("hr_recruitment"):
            print("🔀 No specific domain plugin matched. Routing to 'hr_recruitment' based on keyword signal.")
            return "hr_recruitment"
            
        print("🔀 No specific domain plugin matched. Initializing dynamic query-based generic discovery.")
        return "generic_discovery"
    
    async def _execute_agent(
        self,
        agent,
        workflow_id: str,
        user_request: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an agent from the registry."""
        
        context = AgentContext(
            workflow_id=workflow_id,
            user_request=user_request,
            current_step=agent.name,
            data=data
        )
        
        response: AgentResponse = await agent.execute(context)
        
        # Store in memory
        await self.memory_service.store_agent_output(
            workflow_id=workflow_id,
            agent_name=agent.name,
            output=response.data
        )
        
        return {
            "step": agent.name,
            "agent": agent.name,
            "success": response.success,
            "data": response.data,
            "error": response.error,
            "confidence": response.confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
    

    
    async def _execute_plugin(
        self,
        workflow_id: str,
        user_request: str,
        plugin_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a plugin via the lifecycle manager or database configurations."""

        try:
            plugin = None
            if self.plugin_lifecycle_manager:
                plugin = self.plugin_lifecycle_manager._plugins.get(plugin_name)

            if not plugin:
                # Look up in database custom plugins
                from app.database.models import CustomPluginModel
                cp = await CustomPluginModel.get_plugin_by_name(plugin_name)
                if cp:
                    from app.plugins.generic_domain.plugin import GenericDomainPlugin
                    plugin = GenericDomainPlugin(
                        name=cp["name"],
                        description=cp["description"],
                        geography=cp.get("geography", []),
                        organization_types=cp.get("organizationTypes", []),
                        keywords=cp.get("keywords", []),
                        triggers=cp.get("businessTriggers", cp.get("triggers", [])),
                        personas=cp.get("personas", []),
                        requirements=cp.get("requirements", []),
                        icp_config=cp.get("icp_config"),
                        rules=cp.get("rules")
                    )
                elif plugin_name == "generic_discovery":
                    from app.plugins.generic_domain.plugin import GenericDomainPlugin
                    plugin = GenericDomainPlugin(
                        name="generic_discovery",
                        description="Completely dynamic query-based discovery",
                        icp_config={
                            "min_employees": 1,
                            "max_employees": 1000000,
                            "sectors": [],
                            "funding_stages": [],
                            "min_icp_score": 0.0
                        },
                        personas=[],
                        rules=[]
                    )
            
            if not plugin:
                raise ValueError(f"Plugin '{plugin_name}' not found in registry or custom definitions")

            context = AgentContext(
                workflow_id=workflow_id,
                user_request=user_request,
                current_step="plugin_execution",
                data=data
            )

            response = await plugin.execute(context)

            return {
                "step": "plugin_execution",
                "agent": plugin_name,
                "success": response.success,
                "data": response.data,
                "error": response.error,
                "confidence": response.confidence,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "step": "plugin_execution",
                "agent": plugin_name,
                "success": False,
                "data": {},
                "error": str(e),
                "confidence": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
