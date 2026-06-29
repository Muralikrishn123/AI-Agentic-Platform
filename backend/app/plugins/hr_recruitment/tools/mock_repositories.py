"""
Mock Repositories - Data access layer for Stage B.

This layer abstracts data access so we can easily swap implementations:
- Stage B: Mock data (in-memory)
- Stage D: Real data (MongoDB, ATS, LinkedIn, etc.)

Agents call repositories, not data directly.
"""

from typing import List, Dict, Any, Optional


# ============================================================================
# MOCK DATA
# ============================================================================

MOCK_JOBS = [
    {
        "id": "JOB001",
        "title": "Senior Python Backend Developer",
        "description": """
        We're looking for a Senior Python Backend Developer.
        
        Required Skills:
        - Python (3+ years)
        - FastAPI or Django
        - MongoDB or PostgreSQL
        - Docker
        
        Experience: 3-5 years
        Location: Remote
        Education: Bachelor's degree in Computer Science or related field
        """,
        "required_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
        "experience_years_min": 3,
        "experience_years_max": 5,
        "location": "Remote",
        "education": "Bachelor's degree"
    },
    {
        "id": "JOB002",
        "title": "Frontend Engineer",
        "description": """
        Seeking a Frontend Engineer with React expertise.
        
        Required Skills:
        - React (2+ years)
        - TypeScript
        - CSS/SCSS
        
        Experience: 2-4 years
        Location: New York, NY
        """,
        "required_skills": ["React", "TypeScript", "CSS"],
        "experience_years_min": 2,
        "experience_years_max": 4,
        "location": "New York, NY",
        "education": "Bachelor's degree"
    }
]

MOCK_CANDIDATES = [
    {
        "id": "CAND001",
        "name": "Alice Johnson",
        "email": "alice.j@example.com",
        "skills": ["Python", "FastAPI", "MongoDB", "Docker", "AWS"],
        "experience_years": 4,
        "location": "Remote",
        "education": "Bachelor's in Computer Science",
        "current_role": "Backend Developer",
        "availability": "2 weeks notice"
    },
    {
        "id": "CAND002",
        "name": "Bob Smith",
        "email": "bob.s@example.com",
        "skills": ["Java", "Spring Boot", "MySQL", "Kubernetes"],
        "experience_years": 5,
        "location": "San Francisco, CA",
        "education": "Master's in Software Engineering",
        "current_role": "Senior Java Developer",
        "availability": "Immediate"
    },
    {
        "id": "CAND003",
        "name": "Charlie Williams",
        "email": "charlie.w@example.com",
        "skills": ["Python", "Django", "PostgreSQL", "Redis"],
        "experience_years": 3,
        "location": "Remote",
        "education": "Bachelor's in Computer Science",
        "current_role": "Full Stack Developer",
        "availability": "1 month notice"
    },
    {
        "id": "CAND004",
        "name": "Diana Martinez",
        "email": "diana.m@example.com",
        "skills": ["Python", "FastAPI", "MongoDB", "React", "Docker"],
        "experience_years": 3,
        "location": "Remote",
        "education": "Bachelor's in Information Technology",
        "current_role": "Full Stack Engineer",
        "availability": "2 weeks notice"
    },
    {
        "id": "CAND005",
        "name": "Eve Chen",
        "email": "eve.c@example.com",
        "skills": ["React", "TypeScript", "CSS", "HTML", "JavaScript"],
        "experience_years": 3,
        "location": "New York, NY",
        "education": "Bachelor's in Design",
        "current_role": "Frontend Developer",
        "availability": "Immediate"
    },
    {
        "id": "CAND006",
        "name": "Frank Davis",
        "email": "frank.d@example.com",
        "skills": ["Python", "TensorFlow", "Pandas", "SQL"],
        "experience_years": 2,
        "location": "Boston, MA",
        "education": "PhD in Computer Science",
        "current_role": "Data Scientist",
        "availability": "1 month notice"
    },
    {
        "id": "CAND007",
        "name": "Grace Lee",
        "email": "grace.l@example.com",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Jenkins"],
        "experience_years": 5,
        "location": "Remote",
        "education": "Bachelor's in Computer Science",
        "current_role": "Backend Engineer",
        "availability": "2 weeks notice"
    },
    {
        "id": "CAND008",
        "name": "Henry Brown",
        "email": "henry.b@example.com",
        "skills": ["JavaScript", "Node.js", "MongoDB", "Express"],
        "experience_years": 2,
        "location": "Austin, TX",
        "education": "Bachelor's in Information Systems",
        "current_role": "Backend Developer",
        "availability": "Immediate"
    }
]


# ============================================================================
# REPOSITORY CLASSES
# ============================================================================

class MockJobRepository:
    """
    Mock Job Repository - Returns job data.
    
    Stage B: Returns hardcoded mock data
    Stage D: Replace with real ATS integration
    """
    
    def __init__(self):
        self._jobs = MOCK_JOBS
    
    def get_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        for job in self._jobs:
            if job["id"] == job_id:
                return job
        return None
    
    def get_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Get job by title (fuzzy match)."""
        title_lower = title.lower()
        for job in self._jobs:
            if title_lower in job["title"].lower():
                return job
        return None
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all jobs."""
        return self._jobs.copy()


class MockCandidateRepository:
    """
    Mock Candidate Repository - Returns candidate data.
    
    Stage B: Returns hardcoded mock data
    Stage D: Replace with real database/ATS
    """
    
    def __init__(self):
        self._candidates = MOCK_CANDIDATES
    
    def get_by_id(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get candidate by ID."""
        for candidate in self._candidates:
            if candidate["id"] == candidate_id:
                return candidate
        return None
    
    def search(
        self,
        skills: List[str] = None,
        min_experience: int = 0,
        location: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search candidates by criteria.
        
        Args:
            skills: Required skills (any match)
            min_experience: Minimum years of experience
            location: Location filter (supports "Remote")
        
        Returns:
            List of matching candidates
        """
        results = []
        
        for candidate in self._candidates:
            # Check experience
            if candidate["experience_years"] < min_experience:
                continue
            
            # Check location
            if location:
                if location.lower() == "remote":
                    if candidate["location"].lower() != "remote":
                        continue
                else:
                    if location.lower() not in candidate["location"].lower():
                        continue
            
            # Check skills (at least one match)
            if skills:
                candidate_skills = set(s.lower() for s in candidate["skills"])
                required_skills = set(s.lower() for s in skills)
                if not (candidate_skills & required_skills):  # No intersection
                    continue
            
            results.append(candidate.copy())
        
        return results
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all candidates."""
        return self._candidates.copy()


# ============================================================================
# REPOSITORY FACTORY
# ============================================================================

_job_repo = None
_candidate_repo = None


def get_job_repository() -> MockJobRepository:
    """Get job repository instance (singleton)."""
    global _job_repo
    if _job_repo is None:
        _job_repo = MockJobRepository()
    return _job_repo


def get_candidate_repository() -> MockCandidateRepository:
    """Get candidate repository instance (singleton)."""
    global _candidate_repo
    if _candidate_repo is None:
        _candidate_repo = MockCandidateRepository()
    return _candidate_repo
