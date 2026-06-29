"""
HR Recruitment Agents.

Stage C Iteration 1: RequirementExtractionAgent added (uses Gemini)
Stage C Iteration 2: CandidateMatchExplanationAgent added (AI explanations for algorithm scores)
Other agents: Not yet implemented
"""

from .requirement_extraction_agent import RequirementExtractionAgent
from .candidate_match_explanation_agent import CandidateMatchExplanationAgent

__all__ = ["RequirementExtractionAgent", "CandidateMatchExplanationAgent"]
