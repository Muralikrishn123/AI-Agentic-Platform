import json
from typing import Dict, Any, List
from app.core.interfaces import Agent, AgentContext, AgentResponse


class ValidationAgent(Agent):
    """
    Validation Agent - Validates outputs from other agents and plugins.

    Checks:
    - Plan structure completeness
    - Confidence levels
    - Empty responses
    - Data integrity
    - Plugin selection correctness
    """

    def __init__(self):
        super().__init__("ValidationAgent")
        self.min_confidence = 0.6

    async def execute(self, context: AgentContext) -> AgentResponse:
        """Validate the workflow output."""

        validation_results = []
        is_valid = True

        # The context.data contains {"output": workflow_plan, "confidence": float}
        # workflow_plan is what the PlannerAgent returned in its data dict
        workflow_plan = context.data.get("output", {})

        # Check 1: Plan has a goal
        goal = workflow_plan.get("goal") or workflow_plan.get("workflow_plan", {}).get("goal")
        if not goal:
            validation_results.append({
                "check": "plan_goal",
                "status": "failed",
                "message": "Workflow plan is missing a goal"
            })
            is_valid = False
        else:
            validation_results.append({
                "check": "plan_goal",
                "status": "passed",
                "message": f"Goal defined: {str(goal)[:80]}"
            })

        # Check 2: Steps defined
        steps = (
            workflow_plan.get("steps")
            or workflow_plan.get("workflow_plan", {}).get("steps")
            or []
        )
        if not steps:
            validation_results.append({
                "check": "plan_steps",
                "status": "failed",
                "message": "No execution steps defined in plan"
            })
            is_valid = False
        else:
            validation_results.append({
                "check": "plan_steps",
                "status": "passed",
                "message": f"{len(steps)} step(s) planned"
            })

        # Check 3: JSON serialisable
        json_valid = self._check_json_validity(workflow_plan)
        if not json_valid:
            validation_results.append({
                "check": "json_validity",
                "status": "failed",
                "message": "Plan is not JSON-serialisable"
            })
            is_valid = False
        else:
            validation_results.append({
                "check": "json_validity",
                "status": "passed"
            })

        # Check 4: Empty response guard
        if self._is_empty_response(workflow_plan):
            validation_results.append({
                "check": "empty_response",
                "status": "warning",
                "message": "Plan contains no meaningful data"
            })
        else:
            validation_results.append({
                "check": "empty_response",
                "status": "passed"
            })

        # Check 5: Confidence level of the planner
        confidence = context.data.get("confidence", 1.0)
        if isinstance(confidence, (int, float)) and confidence < self.min_confidence:
            validation_results.append({
                "check": "confidence",
                "status": "warning",
                "message": f"Low planner confidence: {confidence:.0%}"
            })
        else:
            validation_results.append({
                "check": "confidence",
                "status": "passed",
                "message": f"Confidence: {confidence:.0%}" if isinstance(confidence, (int, float)) else "OK"
            })

        return AgentResponse(
            success=is_valid,
            data={
                "validation_results": validation_results,
                "is_valid": is_valid,
                "checks_passed": sum(1 for r in validation_results if r["status"] == "passed"),
                "checks_failed": sum(1 for r in validation_results if r["status"] == "failed"),
                "warnings": sum(1 for r in validation_results if r["status"] == "warning")
            },
            confidence=1.0 if is_valid else 0.5,
            next_step="reporting"
        )

    def _check_json_validity(self, data: Any) -> bool:
        """Check if data is valid JSON-serializable."""
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False

    def _is_empty_response(self, data: Dict[str, Any]) -> bool:
        """Check if response is empty or meaningless."""
        if not data:
            return True

        if isinstance(data, dict):
            # Check if all values are empty
            return all(
                not v or (isinstance(v, (list, dict)) and not v)
                for v in data.values()
            )

        return False
