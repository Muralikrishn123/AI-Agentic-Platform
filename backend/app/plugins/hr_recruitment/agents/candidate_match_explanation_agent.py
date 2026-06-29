"""
Candidate Match Explanation Agent - Iteration 2

This agent generates AI-powered explanations for candidate match scores.
It takes deterministic algorithm scores and adds human-understandable reasoning.

Architecture:
- Algorithm computes scores (deterministic, fast, reproducible)
- AI explains scores (contextual, understandable, insightful)

This is the recommended pattern: precision + understanding.
"""

from typing import Dict, Any
from app.core.interfaces import Agent, AgentResponse, AgentContext


class CandidateMatchExplanationAgent(Agent):
    """
    Agent that generates explanations for candidate match scores.
    
    Iteration 2: New capability that explains WHY candidates scored what they did.
    Uses Gemini to add context and reasoning to algorithm scores.
    """
    
    def __init__(self):
        """Initialize the agent."""
        super().__init__(name="CandidateMatchExplanationAgent")
        self.capabilities = ["candidate_match_explanation"]
        self.description = "Generates AI-powered explanations for candidate match scores"
        self.explanation_service = None
        self.llm_provider = None
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the agent with configuration.
        
        Args:
            config: Configuration including LLM provider
        """
        from ..tools.services import MatchExplanationService
        
        # Get LLM provider from config
        self.llm_provider = config.get("llm_provider")
        
        # Initialize explanation service
        self.explanation_service = MatchExplanationService(
            llm_provider=self.llm_provider
        )
        
        print(f"✅ {self.name} initialized")
        if self.llm_provider:
            print(f"   Using AI explanations (Gemini)")
        else:
            print(f"   Using fallback explanations (no LLM)")
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Generate explanations for candidate match scores.
        
        Expected context.data:
            - requirements: Job requirements
            - matched_candidates: List of candidates with match_data from algorithm
        
        Returns:
            AgentResponse with candidates + explanations
        """
        try:
            # Extract input data
            requirements = context.data.get("requirements")
            matched_candidates = context.data.get("matched_candidates", [])
            
            if not requirements:
                return AgentResponse(
                    success=False,
                    data={},
                    error="Missing requirements in context",
                    confidence=0.0,
                    agent_name=self.name
                )
            
            if not matched_candidates:
                return AgentResponse(
                    success=True,
                    data={
                        "candidates_with_explanations": [],
                        "total_candidates": 0,
                        "explanations_generated": 0
                    },
                    error=None,
                    confidence=1.0,
                    agent_name=self.name
                )
            
            # Generate explanations for each candidate
            print(f"\n🧠 Generating AI explanations for {len(matched_candidates)} candidates...")
            
            candidates_with_explanations = []
            successful_explanations = 0
            failed_explanations = 0
            total_ai_time = 0.0
            
            for i, matched_item in enumerate(matched_candidates, 1):
                candidate = matched_item.get("candidate", {})
                match_data = matched_item.get("match_data", {})
                
                print(f"   {i}. {candidate.get('name', 'Unknown')} (Score: {match_data.get('skill_match_score', 0)}%)")
                
                # Generate explanation
                explanation_result = await self.explanation_service.explain_match(
                    requirements=requirements,
                    candidate=candidate,
                    match_data=match_data
                )
                
                # Track metrics
                metadata = explanation_result.get("_metadata", {})
                exec_time = metadata.get("execution_time_seconds", 0)
                total_ai_time += exec_time
                
                if metadata.get("source") == "gemini_llm":
                    successful_explanations += 1
                    print(f"      ✅ AI explanation generated ({exec_time:.2f}s)")
                else:
                    failed_explanations += 1
                    print(f"      ⚠️  Used fallback explanation")
                
                # Combine match data with explanation
                candidates_with_explanations.append({
                    "candidate": candidate,
                    "match_data": match_data,
                    "explanation": explanation_result.get("explanation"),
                    "explanation_confidence": explanation_result.get("confidence"),
                    "explanation_metadata": metadata
                })
            
            # Calculate average confidence
            avg_confidence = sum(
                c.get("explanation_confidence", 0.5)
                for c in candidates_with_explanations
            ) / len(candidates_with_explanations) if candidates_with_explanations else 0.0
            
            # Prepare response
            result_data = {
                "candidates_with_explanations": candidates_with_explanations,
                "total_candidates": len(matched_candidates),
                "explanations_generated": successful_explanations,
                "explanations_failed": failed_explanations,
                "total_ai_time_seconds": round(total_ai_time, 2),
                "average_ai_time_seconds": round(total_ai_time / len(matched_candidates), 2) if matched_candidates else 0.0,
                "_metadata": {
                    "agent": self.name,
                    "capability": "candidate_match_explanation",
                    "llm_available": self.llm_provider is not None,
                    "ai_success_rate": round(successful_explanations / len(matched_candidates) * 100, 1) if matched_candidates else 0.0
                }
            }
            
            print(f"\n✅ Explanations complete:")
            print(f"   AI explanations: {successful_explanations}/{len(matched_candidates)}")
            print(f"   Fallback used: {failed_explanations}/{len(matched_candidates)}")
            print(f"   Total AI time: {total_ai_time:.2f}s")
            
            return AgentResponse(
                success=True,
                data=result_data,
                error=None,
                confidence=avg_confidence,
                agent_name=self.name
            )
        
        except Exception as e:
            print(f"❌ {self.name} error: {e}")
            import traceback
            traceback.print_exc()
            
            return AgentResponse(
                success=False,
                data={},
                error=str(e),
                confidence=0.0,
                agent_name=self.name
            )
    
    def get_required_capabilities(self) -> list:
        """Return required capabilities (none - this agent is self-contained)."""
        return []
