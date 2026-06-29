"""
HR Recruitment Plugin - Automated recruitment workflow.

Capabilities:
- extract_requirements: Extract job requirements from description
- candidate_search: Search for matching candidates
- candidate_matching: Match candidates to requirements
- candidate_scoring: Score candidates based on fit
- candidate_shortlisting: Generate candidate shortlist
"""

from .plugin import HRRecruitmentPlugin

__all__ = ["HRRecruitmentPlugin"]
