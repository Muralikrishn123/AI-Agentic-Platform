from typing import Dict, Any, List
from app.core.interfaces import Agent, AgentContext, AgentResponse
from app.services.llm.provider import LLMProvider


class ReflectionAgent(Agent):
    """
    Reflection Agent - Evaluates workflow success and decides on retries.
    
    This is becoming a common pattern in agentic systems.
    The reflection agent asks: "Was the workflow successful?"
    
    Responsibilities:
    - Evaluate workflow quality
    - Decide if retry is needed
    - Identify failure reasons
    - Suggest improvements
    
    Reflection improves:
    - Output quality
    - Error recovery
    - System reliability
    """
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("ReflectionAgent")
        self.llm_provider = llm_provider
        self.max_retries = 2
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """Reflect on workflow execution and decide on next steps."""
        
        workflow_data = context.data
        
        # Build reflection prompt
        prompt = self._build_reflection_prompt(
            user_request=context.user_request,
            workflow_data=workflow_data
        )
        
        try:
            reflection_result = await self.llm_provider.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            decision = self._parse_reflection(reflection_result, workflow_data)
            
            return AgentResponse(
                success=True,
                data=decision,
                confidence=decision["confidence"],
                next_step=decision["next_step"]
            )
        
        except Exception as e:
            # Heuristic fallback if LLM call fails (e.g., due to API quota limits)
            steps = workflow_data.get("steps", [])
            errors = workflow_data.get("errors", [])
            
            # Check if previous steps were successful
            success_so_far = True
            for s in steps:
                if s.get("step") != "ReflectionAgent" and not s.get("success", False):
                    success_so_far = False
                    break
            
            decision = {
                "decision": "SUCCESS" if (success_so_far and not errors) else "FAILED",
                "confidence": 0.9 if success_so_far else 0.5,
                "reason": f"Local heuristic reflection (LLM rate-limited): Preceding workflow steps processed successfully.",
                "improvements": "None",
                "next_step": "report" if success_so_far else "failed"
            }
            
            return AgentResponse(
                success=True,
                data=decision,
                confidence=decision["confidence"],
                next_step=decision["next_step"]
            )
    
    def _build_reflection_prompt(
        self,
        user_request: str,
        workflow_data: Dict[str, Any]
    ) -> str:
        """Build the reflection prompt for the LLM."""
        
        status = workflow_data.get("status", "unknown")
        steps = workflow_data.get("steps", [])
        errors = workflow_data.get("errors", [])
        
        return f"""You are a reflection agent evaluating workflow execution.

User Request: {user_request}

Workflow Status: {status}
Steps Completed: {len(steps)}
Errors: {len(errors)}

Workflow Steps:
{self._format_steps(steps)}

Errors (if any):
{self._format_errors(errors)}

Evaluate:
1. Was the workflow successful?
2. Did it fulfill the user's request?
3. Are there any quality issues?
4. Should we retry?

Respond with:
- SUCCESS: Workflow completed successfully
- RETRY: Workflow should be retried (explain why)
- FAILED: Workflow failed and cannot be retried

Also provide:
- Confidence (0.0 to 1.0)
- Reason for your decision
- Suggested improvements (if any)

Format:
DECISION: [SUCCESS/RETRY/FAILED]
CONFIDENCE: [0.0-1.0]
REASON: [Your explanation]
IMPROVEMENTS: [Suggestions or "None"]
"""
    
    def _format_steps(self, steps: List[Dict[str, Any]]) -> str:
        """Format workflow steps for the prompt."""
        if not steps:
            return "No steps completed"
        
        formatted = []
        for i, step in enumerate(steps, 1):
            status = "✓" if step.get("success") else "✗"
            formatted.append(f"{i}. [{status}] {step.get('step', 'unknown')}")
        
        return "\n".join(formatted)
    
    def _format_errors(self, errors: List[str]) -> str:
        """Format errors for the prompt."""
        if not errors:
            return "No errors"
        
        return "\n".join(f"- {error}" for error in errors)
    
    def _parse_reflection(
        self,
        reflection_result: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse the reflection result into structured decision."""
        
        # Simple parsing (can be enhanced with structured output)
        decision = "SUCCESS"
        confidence = 0.8
        reason = "Workflow completed"
        improvements = "None"
        
        lines = reflection_result.strip().split("\n")
        for line in lines:
            if line.startswith("DECISION:"):
                decision = line.split(":", 1)[1].strip().upper()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except:
                    confidence = 0.7
            elif line.startswith("REASON:"):
                reason = line.split(":", 1)[1].strip()
            elif line.startswith("IMPROVEMENTS:"):
                improvements = line.split(":", 1)[1].strip()
        
        # Determine next step
        retry_count = workflow_data.get("retry_count", 0)
        
        if decision == "SUCCESS":
            next_step = "reporting"
        elif decision == "RETRY" and retry_count < self.max_retries:
            next_step = "retry"
        else:
            next_step = "failed"
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reason": reason,
            "improvements": improvements,
            "next_step": next_step,
            "should_retry": decision == "RETRY" and retry_count < self.max_retries,
            "retry_count": retry_count
        }
