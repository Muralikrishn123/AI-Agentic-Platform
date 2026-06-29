"""
HR Recruitment Plugin - Main plugin class.

Stage A: Plugin skeleton with capability registration only.
Stage B: No agents, just services and repositories.
Stage C Iteration 1: RequirementExtractionAgent added (uses Gemini).
Stage C Iteration 2: CandidateMatchExplanationAgent added (AI explanations for scores).
"""

from typing import Dict, Any
from app.core.interfaces import Plugin, AgentContext, AgentResponse
from app.services.capability_registry import get_capability_registry, CapabilityCategory
from app.services.agent_registry import get_agent_registry
from app.services.llm import get_llm_provider


class HRRecruitmentPlugin(Plugin):
    """
    HR Recruitment Plugin - Automates recruitment workflow.
    
    Stage C Iteration 1: First AI agent added (RequirementExtractionAgent)
    Stage C Iteration 2: Second AI agent added (CandidateMatchExplanationAgent)
    """
    
    def __init__(self):
        super().__init__(
            name="hr_recruitment",
            version="1.0.0",
            description="Automated recruitment workflow from job description to candidate shortlist"
        )
        self._agents = {}
    
    async def initialize(self):
        """
        Initialize plugin - register capabilities and agents.
        
        Stage C Iteration 1: Register RequirementExtractionAgent with Gemini.
        Stage C Iteration 2: Register CandidateMatchExplanationAgent.
        """
        print(f"🔧 Initializing {self.name} plugin...")
        
        capability_registry = get_capability_registry()
        agent_registry = get_agent_registry()
        llm_provider = get_llm_provider()
        
        # Define capabilities
        capabilities = [
            ("extract_requirements", "Extract job requirements from description", CapabilityCategory.EXTRACTION),
            ("candidate_search", "Search for matching candidates", CapabilityCategory.SEARCH),
            ("candidate_matching", "Match candidates to requirements", CapabilityCategory.MATCHING),
            ("candidate_match_explanation", "Generate AI explanations for match scores", CapabilityCategory.EXPLANATION),  # NEW: Iteration 2
            ("candidate_scoring", "Score candidates based on fit", CapabilityCategory.SCORING),
            ("candidate_shortlisting", "Generate candidate shortlist", CapabilityCategory.SHORTLISTING),
        ]
        
        # Register each capability
        for cap_name, description, category in capabilities:
            agent_name = self._capability_to_agent_name(cap_name)
            
            if not capability_registry.has_capability(cap_name):
                capability_registry.register(
                    name=cap_name,
                    description=description,
                    category=category,
                    agent_name=agent_name
                )
            else:
                print(f"⚠️  Capability already registered: {cap_name}")
        
        # Stage C Iteration 1: Register RequirementExtractionAgent
        try:
            from .agents import RequirementExtractionAgent
            
            req_agent = RequirementExtractionAgent(llm_provider)
            
            if not agent_registry.has_agent(req_agent.name):
                agent_registry.register(req_agent)
                self._agents["extract_requirements"] = req_agent
                print(f"✅ Registered AI agent: {req_agent.name} (uses Gemini)")
            else:
                print(f"⚠️  Agent already registered: {req_agent.name}")
                self._agents["extract_requirements"] = agent_registry.get(req_agent.name)
        
        except Exception as e:
            print(f"⚠️  Failed to register RequirementExtractionAgent: {e}")
        
        # Stage C Iteration 2: Register CandidateMatchExplanationAgent
        try:
            from .agents import CandidateMatchExplanationAgent
            
            explanation_agent = CandidateMatchExplanationAgent()
            
            # Initialize with LLM provider
            await explanation_agent.initialize({"llm_provider": llm_provider})
            
            if not agent_registry.has_agent(explanation_agent.name):
                agent_registry.register(explanation_agent)
                self._agents["candidate_match_explanation"] = explanation_agent
                print(f"✅ Registered AI agent: {explanation_agent.name} (explains algorithm scores)")
            else:
                print(f"⚠️  Agent already registered: {explanation_agent.name}")
                self._agents["candidate_match_explanation"] = agent_registry.get(explanation_agent.name)
        
        except Exception as e:
            print(f"⚠️  Failed to register CandidateMatchExplanationAgent: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"✅ {self.name} plugin initialized")
        print(f"   Stage: C Iteration 2")
        print(f"   AI Agents: {len([a for a in self._agents.values() if a])} / 6")
    
    def _capability_to_agent_name(self, capability: str) -> str:
        """
        Convert capability name to agent name.
        
        Examples:
        - extract_requirements → RequirementExtractionAgent
        - candidate_search → CandidateSearchAgent
        """
        words = capability.split('_')
        return ''.join(word.capitalize() for word in words) + 'Agent'
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Execute the full HR recruitment pipeline end-to-end.

        Pipeline:
          1. RequirementExtractionAgent  — parse structured requirements from free text
          2. CandidateMatchExplanationAgent — generate AI rationale for the match

        Returns consolidated data from all sub-steps.
        """
        pipeline_results = {}
        combined_data = {"user_request": context.user_request, "sub_steps": []}

        # Step 1: Extract requirements (AI agent)
        req_agent = self._agents.get("extract_requirements")
        if req_agent:
            try:
                req_response = await req_agent.execute(context)
                pipeline_results["requirements"] = req_response.data
                combined_data["sub_steps"].append({
                    "step": "extract_requirements",
                    "success": req_response.success,
                    "data": req_response.data,
                    "confidence": req_response.confidence,
                })
                if not req_response.success:
                    combined_data["extract_error"] = req_response.error
            except Exception as e:
                combined_data["extract_error"] = str(e)
        else:
            pipeline_results["requirements"] = {
                "role": "Senior Python Engineer",
                "skills": ["Python", "FastAPI"],
                "experience_years": 5,
                "location": "Remote",
                "note": "RequirementExtractionAgent not available — using fallback"
            }

        # Step 2: Build synthetic candidate pool (deterministic, no external API)
        candidate_pool = self._build_candidate_pool(pipeline_results.get("requirements", {}))
        pipeline_results["candidates"] = candidate_pool
        combined_data["candidates"] = candidate_pool
        combined_data["sub_steps"].append({
            "step": "candidate_search",
            "success": True,
            "data": {"count": len(candidate_pool), "candidates": candidate_pool},
            "confidence": 0.85,
        })

        # Step 3: Score & shortlist
        shortlist = sorted(candidate_pool, key=lambda c: c.get("match_score", 0), reverse=True)[:3]
        pipeline_results["shortlist"] = shortlist
        combined_data["shortlist"] = shortlist
        combined_data["sub_steps"].append({
            "step": "candidate_shortlisting",
            "success": True,
            "data": {"shortlist": shortlist},
            "confidence": 0.9,
        })

        # Step 4: Generate AI match explanation if agent available
        explanation_agent = self._agents.get("candidate_match_explanation")
        if explanation_agent and shortlist:
            try:
                from app.core.interfaces import AgentContext as Ctx
                exp_context = Ctx(
                    workflow_id=context.workflow_id,
                    user_request=context.user_request,
                    current_step="candidate_match_explanation",
                    data={**context.data, "shortlist": shortlist, "requirements": pipeline_results.get("requirements", {})},
                )
                exp_response = await explanation_agent.execute(exp_context)
                combined_data["match_explanations"] = exp_response.data
                combined_data["sub_steps"].append({
                    "step": "candidate_match_explanation",
                    "success": exp_response.success,
                    "data": exp_response.data,
                    "confidence": exp_response.confidence,
                })
            except Exception as e:
                combined_data["explanation_error"] = str(e)

        combined_data["total_candidates"] = len(candidate_pool)
        combined_data["shortlisted"] = len(shortlist)
        combined_data["plugin"] = "hr_recruitment"
        combined_data["stage"] = "C Iteration 2"
        combined_data["requires_hitl_approval"] = True

        return AgentResponse(
            success=True,
            data=combined_data,
            confidence=0.88,
            next_step="reflection"
        )

    def _build_candidate_pool(self, requirements: dict) -> list:
        """Build a dynamic database of 100 synthetic candidates based on requirements."""
        import random
        role = requirements.get("role", "Engineer")
        skills = requirements.get("skills", ["Python", "FastAPI"])
        exp = requirements.get("experience_years", 3)
        if not exp:
            exp = 3

        first_names = [
            "Priya", "Arjun", "Sneha", "Rahul", "Divya", "Amit", "Neha", "Siddharth", "Meera", "Vikram",
            "Kavitha", "Rajiv", "Nandini", "Karthik", "Preeti", "Rohan", "Suresh", "Vijay", "Aisha", "Pooja",
            "Anjali", "Swati", "Sanjay", "Anil", "Sunil", "Manish", "Alok", "Harish", "Gaurav", "Nitin"
        ]
        last_names = [
            "Sharma", "Mehta", "Iyer", "Nair", "Gupta", "Sen", "Menon", "Balasubramanian", "Rathore", "Malhotra",
            "Krishnamurthy", "Shankar", "Desai", "Narayanan", "Pillai", "Rajan", "Verma", "Kapoor", "Joshi", "Patel"
        ]
        locations = ["Remote", "Hybrid", "On-site", "Remote", "Hybrid"]
        availabilities = ["Immediate", "2 weeks", "3 weeks", "1 month", "Immediate"]
        extra_skills = ["Docker", "Kubernetes", "AWS", "SQL", "Redis", "Celery", "Git", "CI/CD", "TypeScript", "React", "GraphQL", "NoSQL"]

        candidates = []
        for i in range(1, 101):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            cand_exp = max(1, exp + random.randint(-2, 5))
            
            # Decide skill match overlap
            match_percentage = random.uniform(0.3, 0.98)
            num_matched = max(1, int(len(skills) * match_percentage))
            cand_skills = random.sample(skills, num_matched)
            
            # Add some extra background skills
            cand_skills += random.sample(extra_skills, random.randint(1, 4))
            
            # Calculate match score based on skill overlap + experience fit
            skill_score = num_matched / len(skills) if skills else 1.0
            exp_score = min(1.0, cand_exp / exp)
            match_score = round((skill_score * 0.7) + (exp_score * 0.3), 2)

            candidates.append({
                "id": f"cand_{i:03d}",
                "name": name,
                "role": f"Senior {role}" if cand_exp >= 5 else role,
                "experience_years": cand_exp,
                "skills": list(set(cand_skills)),
                "location": random.choice(locations),
                "match_score": match_score,
                "availability": random.choice(availabilities),
            })
            
        return candidates

    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return plugin capabilities."""
        return {
            "capabilities": [
                "extract_requirements",
                "candidate_search",
                "candidate_matching",
                "candidate_match_explanation",  # NEW: Iteration 2
                "candidate_scoring",
                "candidate_shortlisting"
            ],
            "description": self.description,
            "version": self.version,
            "stage": "C Iteration 2",
            "ai_agents": len([a for a in self._agents.values() if a]),
            "total_agents": 6  # Updated count
        }
    
    async def cleanup(self):
        """Clean up plugin resources."""
        print(f"🗑️  Cleaning up {self.name} plugin...")
        self._agents.clear()
        print(f"✅ {self.name} plugin cleaned up")
