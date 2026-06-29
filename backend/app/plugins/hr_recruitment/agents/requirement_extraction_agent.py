"""
Requirement Extraction Agent - Stage C Iteration 1

This is the FIRST agent to use AI (Gemini) in the HR plugin.
Everything else still uses Stage B logic.
"""

from typing import Dict, Any
from app.core.interfaces import Agent, AgentContext, AgentResponse
from app.services.llm.provider import LLMProvider
from app.services.agent_registry import get_agent_registry
from ..tools.services import RequirementExtractionService


class RequirementExtractionAgent(Agent):
    """
    Extract structured requirements from job description using Gemini.
    
    Stage C Iteration 1: First AI-powered agent in HR plugin.
    
    Responsibilities:
    - Parse job description
    - Extract structured requirements using Gemini
    - Validate output using platform Validation Agent
    - Return JSON with skills, experience, location, education
    
    What this agent does NOT do:
    - Search candidates (that's CandidateSearchAgent)
    - Match candidates (that's CandidateMatchingAgent)
    - Score candidates (that's CandidateScoringAgent)
    
    Clean separation of concerns.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        super().__init__("RequirementExtractionAgent")
        self.llm_provider = llm_provider
        self.service = RequirementExtractionService(
            llm_provider=llm_provider,
            use_ai=True
        )
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Extract requirements from job description.
        
        Args:
            context: Contains job description in user_request
        
        Returns:
            AgentResponse with structured requirements
        """
        job_description = context.user_request
        
        if not job_description or len(job_description.strip()) < 10:
            return AgentResponse(
                success=False,
                error="Job description is too short or empty",
                confidence=0.0
            )
        
        try:
            # Extract requirements using Gemini
            requirements = await self.service.extract(job_description)
            
            # Use platform Validation Agent to validate requirements
            validation_result = await self._validate_requirements(requirements, context)
            
            if not validation_result["valid"]:
                return AgentResponse(
                    success=False,
                    error=f"Requirements validation failed: {validation_result.get('errors')}",
                    confidence=0.0,
                    data={
                        "requirements": requirements,
                        "validation_errors": validation_result.get("errors")
                    }
                )
            
            # Get confidence from requirements (added by service)
            confidence = requirements.get("confidence", 0.7)
            
            # Extract metadata for monitoring
            metadata = requirements.pop("_metadata", {})
            
            # Success
            return AgentResponse(
                success=True,
                data={
                    "requirements": requirements,
                    "source": metadata.get("source", "unknown"),
                    "prompt_version": metadata.get("prompt_version", "unknown"),
                    "execution_time_seconds": metadata.get("execution_time_seconds", 0),
                    "job_description_length": len(job_description),
                    "validation": validation_result
                },
                confidence=confidence,
                next_step="candidate_search"
            )
        
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Requirement extraction failed: {str(e)}",
                confidence=0.0
            )
    
    async def _validate_requirements(self, requirements: Dict[str, Any], context: AgentContext) -> Dict[str, bool]:
        """
        Use platform Validation Agent to validate requirements.
        
        Validates:
        - Required fields present
        - Experience is valid number
        - Skills list is non-empty
        - Valid against schema
        """
        agent_registry = get_agent_registry()
        validation_agent = agent_registry.get("ValidationAgent")
        
        if not validation_agent:
            # Validation agent not available, do basic validation
            return self._basic_validation(requirements)
        
        # Use platform validation agent
        validation_context = AgentContext(
            workflow_id=context.workflow_id,
            user_request="Validate job requirements",
            current_step="validation",
            data={
                "object_to_validate": requirements,
                "schema": {
                    "required_fields": ["required_skills", "experience_years_min", "location", "education"],
                    "types": {
                        "required_skills": "list",
                        "experience_years_min": "number",
                        "location": "string",
                        "education": "string"
                    },
                    "rules": {
                        "required_skills": "non_empty",
                        "experience_years_min": ">=0"
                    }
                }
            }
        )
        
        try:
            validation_response = await validation_agent.execute(validation_context)
            
            if validation_response.success:
                return {
                    "valid": True,
                    "validation_method": "platform_validation_agent"
                }
            else:
                return {
                    "valid": False,
                    "validation_method": "platform_validation_agent",
                    "errors": validation_response.error
                }
        except Exception as e:
            print(f"⚠️  Platform validation failed: {e}, using basic validation")
            return self._basic_validation(requirements)
    
    def _basic_validation(self, requirements: Dict[str, Any]) -> Dict[str, bool]:
        """Basic validation fallback."""
        errors = []
        
        # Check required fields
        required_fields = ["required_skills", "experience_years_min", "location", "education"]
        for field in required_fields:
            if field not in requirements:
                errors.append(f"Missing required field: {field}")
        
        # Validate skills
        if not requirements.get("required_skills"):
            errors.append("required_skills cannot be empty")
        
        # Validate experience
        if requirements.get("experience_years_min", -1) < 0:
            errors.append("experience_years_min cannot be negative")
        
        if errors:
            return {
                "valid": False,
                "validation_method": "basic_validation",
                "errors": errors
            }
        
        return {
            "valid": True,
            "validation_method": "basic_validation"
        }
    
    async def validate_input(self, context: AgentContext) -> bool:
        """Validate that job description exists."""
        return bool(context.user_request and len(context.user_request.strip()) >= 10)
