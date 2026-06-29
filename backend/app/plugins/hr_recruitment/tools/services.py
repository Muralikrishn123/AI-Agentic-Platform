"""
Business Logic Services - Stage B implementation.

These services contain the business logic for HR recruitment.
Agents call these services rather than implementing logic directly.

Stage B: Simple, rule-based logic
Stage C: Can enhance with AI where beneficial
"""

from typing import List, Dict, Any, Optional
import time
import os
import json


class RequirementExtractionService:
    """
    Extract requirements from job description.
    
    Stage B: Simple parsing (mock/hardcoded)
    Stage C Iteration 1: Gemini LLM extraction (CURRENT)
    """
    
    PROMPT_VERSION = "v1"
    MIN_CONFIDENCE_THRESHOLD = 0.5
    
    def __init__(self, llm_provider=None, use_ai: bool = True):
        """
        Initialize service.
        
        Args:
            llm_provider: LLM provider for AI extraction
            use_ai: If False, falls back to simple parsing (for testing)
        """
        self.llm_provider = llm_provider
        self.use_ai = use_ai
        self._load_prompt()
    
    def _load_prompt(self):
        """Load prompt template from file."""
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            f"requirement_extraction_{self.PROMPT_VERSION}.txt"
        )
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            print(f"⚠️  Prompt file not found: {prompt_path}")
            print(f"   Using inline prompt as fallback")
            # Fallback inline prompt
            self.prompt_template = """You are an expert HR analyst. Extract structured job requirements from this job description.

Job Description:
{job_description}

Extract the following information and return ONLY valid JSON."""
    
    async def extract(self, job_description: str) -> Dict[str, Any]:
        """
        Extract requirements from job description.
        
        Stage C Iteration 1: Uses Gemini for intelligent extraction.
        """
        if self.use_ai and self.llm_provider:
            return await self._extract_with_gemini(job_description)
        else:
            return self._extract_simple(job_description)
    
    async def _extract_with_gemini(self, job_description: str) -> Dict[str, Any]:
        """
        Extract requirements using Gemini LLM with retry logic.
        
        This provides much better extraction than simple parsing.
        Implements: Gemini → Validate → Retry Once → Fallback
        """
        max_retries = 1  # Retry once on failure
        
        for attempt in range(max_retries + 1):
            start_time = time.time()
            
            # Build prompt from template
            prompt = self.prompt_template.format(job_description=job_description)
            
            try:
                # Call Gemini
                raw_response = await self.llm_provider.generate(
                    prompt=prompt,
                    temperature=0.2,  # Low temperature for factual extraction
                    max_tokens=3000
                )
                
                execution_time = time.time() - start_time
                
                # Parse and validate JSON response
                requirements = self._parse_and_validate_response(raw_response)
                
                # Success! Store metadata
                requirements["_metadata"] = {
                    "source": "gemini_llm",
                    "prompt_version": self.PROMPT_VERSION,
                    "execution_time_seconds": round(execution_time, 2),
                    "raw_response": raw_response,  # Store full response for debugging
                    "timestamp": time.time(),
                    "retry_count": attempt  # Track if we had to retry
                }
                
                # Validate confidence
                if "confidence" not in requirements:
                    print("⚠️  Gemini response missing confidence, using default 0.7")
                    requirements["confidence"] = 0.7
                
                if requirements["confidence"] < self.MIN_CONFIDENCE_THRESHOLD:
                    print(f"⚠️  Low confidence ({requirements['confidence']}), consider fallback")
                
                if attempt > 0:
                    print(f"✅ Gemini succeeded on retry #{attempt}")
                
                return requirements
                
            except ValueError as e:
                # JSON validation error - could be truncated response
                execution_time = time.time() - start_time
                
                if attempt < max_retries:
                    print(f"⚠️  Gemini extraction failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    print(f"   Retrying...")
                    continue  # Retry
                else:
                    # Max retries reached, fall back
                    print(f"⚠️  Gemini extraction failed after {max_retries + 1} attempts: {e}")
                    print(f"   Total time: {execution_time:.2f}s")
                    print(f"   Falling back to simple extraction")
                    return self._extract_simple(job_description)
            
            except Exception as e:
                # Other error (API, network, etc)
                execution_time = time.time() - start_time
                print(f"⚠️  Gemini extraction error after {execution_time:.2f}s: {e}")
                print(f"   Falling back to simple extraction")
                return self._extract_simple(job_description)
        
        # Should not reach here, but fallback just in case
        return self._extract_simple(job_description)
    
    def _parse_and_validate_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse and validate Gemini response.
        
        Pipeline:
        1. Clean raw text (remove markdown)
        2. Parse JSON
        3. Validate schema
        4. Return validated object
        """
        # Debug: Show what Gemini returned
        print(f"🔍 Raw Gemini response length: {len(raw_response)} chars")
        print(f"🔍 First 150 chars: {raw_response[:150]}...")
        if len(raw_response) > 150:
            print(f"🔍 Last 50 chars: ...{raw_response[-50:]}")
        
        # Clean response aggressively
        cleaned = raw_response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Try to find JSON object if there's extra text
        if not cleaned.startswith('{'):
            # Find first { and last }
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start:end+1]
        
        # Remove any trailing commas before closing braces (invalid JSON)
        cleaned = cleaned.replace(',}', '}').replace(',]', ']')
        
        # Remove line breaks (Gemini sometimes adds them)
        cleaned = cleaned.replace('\n', ' ').replace('\r', '')
        
        print(f"🔍 Cleaned JSON length: {len(cleaned)} chars")
        print(f"🔍 Cleaned JSON: {cleaned}")
        
        # Parse JSON
        try:
            requirements = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"❌ Attempted to parse: {cleaned}")
            raise ValueError(f"Invalid JSON from Gemini: {e}")
        
        # Validate schema - required keys
        required_keys = ["required_skills", "experience_years_min", "location", "education"]
        missing_keys = [key for key in required_keys if key not in requirements]
        
        if missing_keys:
            raise ValueError(f"Missing required keys in Gemini response: {missing_keys}")
        
        # Validate types
        if not isinstance(requirements["required_skills"], list):
            raise ValueError("required_skills must be a list")
        
        if not isinstance(requirements["experience_years_min"], (int, float)):
            raise ValueError("experience_years_min must be a number")
        
        # Validate business rules
        if requirements["experience_years_min"] < 0:
            raise ValueError("experience_years_min cannot be negative")
        
        if requirements.get("experience_years_max") is not None:
            if requirements["experience_years_max"] < requirements["experience_years_min"]:
                raise ValueError("experience_years_max cannot be less than min")
        
        if len(requirements["required_skills"]) == 0:
            raise ValueError("required_skills cannot be empty")
        
        return requirements
    
    def _extract_simple(self, job_description: str) -> Dict[str, Any]:
        """
        Simple extraction (fallback).
        
        Stage B implementation - basic keyword matching.
        """
        description_lower = job_description.lower()
        
        # Mock extraction based on keywords
        requirements = {
            "required_skills": [],
            "experience_years_min": 0,
            "experience_years_max": None,
            "location": "Not specified",
            "education": "Not specified",
            "confidence": 0.5  # Lower confidence for simple parsing
        }
        
        # Extract skills (very basic)
        skills = ["Python", "FastAPI", "MongoDB", "Docker", "React", "TypeScript", "Django", "Flask", "PostgreSQL"]
        for skill in skills:
            if skill.lower() in description_lower:
                requirements["required_skills"].append(skill)
        
        # Extract experience (basic regex would be better, but keeping it simple)
        if "3-5 years" in description_lower or "3+ years" in description_lower:
            requirements["experience_years_min"] = 3
            requirements["experience_years_max"] = 5
        elif "2-4 years" in description_lower or "2+ years" in description_lower:
            requirements["experience_years_min"] = 2
            requirements["experience_years_max"] = 4
        
        # Extract location
        if "remote" in description_lower:
            requirements["location"] = "Remote"
        elif "new york" in description_lower:
            requirements["location"] = "New York, NY"
        
        # Extract education
        if "bachelor" in description_lower:
            requirements["education"] = "Bachelor's degree"
        elif "master" in description_lower:
            requirements["education"] = "Master's degree"
        elif "phd" in description_lower:
            requirements["education"] = "PhD"
        
        # Add metadata
        requirements["_metadata"] = {
            "source": "simple_parsing",
            "prompt_version": "none",
            "execution_time_seconds": 0.001,
            "timestamp": time.time()
        }
        
        return requirements


class MatchingService:
    """
    Match candidates to job requirements.
    
    Business logic for calculating match scores.
    Iteration 2: Enhanced with semantic skill understanding.
    """
    
    def match_candidates(
        self,
        requirements: Dict[str, Any],
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate match scores for candidates with semantic understanding.
        
        Iteration 2: Now recognizes related skills (Flask ~ FastAPI).
        
        Args:
            requirements: Job requirements
            candidates: List of candidate profiles
        
        Returns:
            List of candidates with match data added
        """
        from .semantic_skills import find_skill_relationships, calculate_skill_similarity
        
        required_skills = requirements.get("required_skills", [])
        required_skills_lower = set(s.lower() for s in required_skills)
        
        matched = []
        for candidate in candidates:
            candidate_skills = candidate.get("skills", [])
            candidate_skills_lower = set(s.lower() for s in candidate_skills)
            
            # Exact matches
            matching_skills = required_skills_lower & candidate_skills_lower
            missing_skills = required_skills_lower - candidate_skills_lower
            
            # Find related skills (semantic understanding) - only for missing skills
            # Extract original case required skills that are missing
            missing_skills_original = [s for s in required_skills if s.lower() in missing_skills]
            skill_relationships = find_skill_relationships(missing_skills_original, candidate_skills)
            
            # Calculate score with partial credit for related skills
            exact_match_count = len(matching_skills)
            related_match_count = len(skill_relationships)
            
            if len(required_skills) > 0:
                # Exact matches: 100% credit
                # Related matches: 50% credit (partial)
                total_credit = exact_match_count + (related_match_count * 0.5)
                skill_match_score = (total_credit / len(required_skills)) * 100
            else:
                skill_match_score = 0
            
            matched.append({
                "candidate": candidate,
                "match_data": {
                    "skill_match_score": round(skill_match_score, 1),
                    "matching_skills": list(matching_skills),
                    "missing_skills": list(missing_skills),
                    "related_skills": skill_relationships,  # NEW: Semantic understanding
                    "total_matching": len(matching_skills),
                    "total_related": len(skill_relationships),  # NEW
                    "total_required": len(required_skills)
                }
            })
        
        # Sort by skill match score
        matched.sort(key=lambda x: x["match_data"]["skill_match_score"], reverse=True)
        
        return matched


class ScoringService:
    """
    Score candidates using weighted algorithm.
    
    Business logic for comprehensive candidate scoring.
    """
    
    def __init__(self):
        # Scoring weights
        self.skill_weight = 0.40
        self.experience_weight = 0.30
        self.education_weight = 0.20
        self.location_weight = 0.10
    
    def score_candidates(
        self,
        requirements: Dict[str, Any],
        matched_candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Apply weighted scoring to matched candidates.
        
        Args:
            requirements: Job requirements
            matched_candidates: Candidates with match data
        
        Returns:
            Candidates with comprehensive scores
        """
        scored = []
        
        for item in matched_candidates:
            candidate = item["candidate"]
            match_data = item["match_data"]
            
            # Component scores
            skill_score = match_data["skill_match_score"]
            exp_score = self._score_experience(candidate, requirements)
            edu_score = self._score_education(candidate, requirements)
            loc_score = self._score_location(candidate, requirements)
            
            # Weighted final score
            final_score = (
                skill_score * self.skill_weight +
                exp_score * self.experience_weight +
                edu_score * self.education_weight +
                loc_score * self.location_weight
            )
            
            scored.append({
                "candidate": candidate,
                "match_data": match_data,
                "scores": {
                    "skill": round(skill_score, 1),
                    "experience": round(exp_score, 1),
                    "education": round(edu_score, 1),
                    "location": round(loc_score, 1),
                    "final": round(final_score, 1)
                }
            })
        
        # Sort by final score
        scored.sort(key=lambda x: x["scores"]["final"], reverse=True)
        
        return scored
    
    def _score_experience(self, candidate: Dict, requirements: Dict) -> float:
        """Score experience match (0-100)."""
        candidate_exp = candidate.get("experience_years", 0)
        min_exp = requirements.get("experience_years_min", 0)
        max_exp = requirements.get("experience_years_max")
        
        if candidate_exp < min_exp:
            # Under-qualified
            return max(0, 50 - (min_exp - candidate_exp) * 10)
        elif max_exp and candidate_exp > max_exp:
            # Over-qualified (not necessarily bad)
            return max(70, 100 - (candidate_exp - max_exp) * 5)
        else:
            # Within range
            return 100
    
    def _score_education(self, candidate: Dict, requirements: Dict) -> float:
        """Score education match (0-100)."""
        candidate_edu = candidate.get("education", "").lower()
        required_edu = requirements.get("education", "").lower()
        
        if not required_edu or "not specified" in required_edu:
            return 100  # No requirement
        
        edu_levels = {
            "phd": 4,
            "doctorate": 4,
            "master": 3,
            "bachelor": 2,
            "associate": 1,
            "high school": 0
        }
        
        candidate_level = 0
        required_level = 0
        
        for edu, level in edu_levels.items():
            if edu in candidate_edu:
                candidate_level = max(candidate_level, level)
            if edu in required_edu:
                required_level = max(required_level, level)
        
        if candidate_level >= required_level:
            return 100
        elif candidate_level == required_level - 1:
            return 70
        else:
            return 40
    
    def _score_location(self, candidate: Dict, requirements: Dict) -> float:
        """Score location match (0-100)."""
        candidate_loc = candidate.get("location", "").lower()
        required_loc = requirements.get("location", "").lower()
        
        if not required_loc or "not specified" in required_loc:
            return 100  # No requirement
        
        if "remote" in required_loc and "remote" in candidate_loc:
            return 100  # Perfect match for remote
        
        if "remote" in candidate_loc:
            return 90  # Remote candidate for on-site (flexible)
        
        if required_loc in candidate_loc or candidate_loc in required_loc:
            return 100  # Location match
        
        return 30  # No match


class MatchExplanationService:
    """
    Generate AI-powered explanations for candidate match scores.
    
    Iteration 2: New service that explains WHY a candidate scored what they did.
    Uses Gemini to provide context and reasoning for algorithm scores.
    """
    
    PROMPT_VERSION = "v1"
    
    def __init__(self, llm_provider=None):
        """
        Initialize explanation service.
        
        Args:
            llm_provider: LLM provider for AI explanations
        """
        self.llm_provider = llm_provider
        self._load_prompt()
    
    def _load_prompt(self):
        """Load explanation prompt template."""
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            f"match_explanation_{self.PROMPT_VERSION}.txt"
        )
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        except FileNotFoundError:
            print(f"⚠️  Match explanation prompt not found: {prompt_path}")
            print(f"   Using inline prompt as fallback")
            # Fallback inline prompt
            self.prompt_template = """You are an expert HR analyst explaining candidate match scores.

Job Requirements:
{requirements}

Candidate Profile:
{candidate_profile}

Match Analysis:
- Algorithm Score: {match_score}%
- Skills Matched: {skills_matched}
- Skills Missing: {skills_missing}
- Related Skills: {related_skills}

Write a concise explanation (2-3 sentences) of why this candidate scored {match_score}%.
Focus on:
1. Skill relevance and relationships
2. Strengths that justify the score
3. Any notable gaps

Be specific and factual. Return ONLY the explanation text."""
    
    async def explain_match(
        self,
        requirements: Dict[str, Any],
        candidate: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI explanation for a candidate's match score.
        
        Args:
            requirements: Job requirements
            candidate: Candidate profile
            match_data: Algorithm's match analysis
        
        Returns:
            Explanation with metadata
        """
        if not self.llm_provider:
            # No AI available, return basic explanation
            return self._generate_basic_explanation(match_data)
        
        try:
            return await self._explain_with_gemini(requirements, candidate, match_data)
        except Exception as e:
            print(f"⚠️  AI explanation failed: {e}")
            print(f"   Falling back to basic explanation")
            return self._generate_basic_explanation(match_data)
    
    async def _explain_with_gemini(
        self,
        requirements: Dict[str, Any],
        candidate: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate explanation using Gemini with retry logic."""
        max_retries = 1
        
        for attempt in range(max_retries + 1):
            start_time = time.time()
            
            # Build context-rich prompt
            prompt = self._build_explanation_prompt(requirements, candidate, match_data)
            
            try:
                # Call Gemini
                raw_response = await self.llm_provider.generate(
                    prompt=prompt,
                    temperature=0.3,  # Low temperature for factual explanation
                    max_tokens=3000
                )
                
                execution_time = time.time() - start_time
                
                # Clean and validate response
                explanation = raw_response.strip()
                
                # Remove markdown if present
                if explanation.startswith("```"):
                    lines = explanation.split('\n')
                    explanation = '\n'.join(lines[1:-1] if len(lines) > 2 else lines)
                
                explanation = explanation.strip()
                
                # Validate explanation is reasonable
                if len(explanation) < 20:
                    raise ValueError(f"Explanation too short: {len(explanation)} chars")
                
                if len(explanation) > 1000:
                    explanation = explanation[:1000] + "..."
                
                # Success!
                return {
                    "explanation": explanation,
                    "confidence": 0.9,  # High confidence for successful generation
                    "_metadata": {
                        "source": "gemini_llm",
                        "prompt_version": self.PROMPT_VERSION,
                        "execution_time_seconds": round(execution_time, 2),
                        "timestamp": time.time(),
                        "retry_count": attempt
                    }
                }
                
            except ValueError as e:
                # Validation error - retry
                if attempt < max_retries:
                    print(f"⚠️  Explanation validation failed (attempt {attempt + 1}): {e}")
                    print(f"   Retrying...")
                    continue
                else:
                    raise  # Max retries reached
            
            except Exception as e:
                # Other error
                execution_time = time.time() - start_time
                print(f"⚠️  Gemini explanation error after {execution_time:.2f}s: {e}")
                raise
        
        # Should not reach here
        return self._generate_basic_explanation(match_data)
    
    def _build_explanation_prompt(
        self,
        requirements: Dict[str, Any],
        candidate: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> str:
        """Build context-rich prompt for explanation."""
        
        # Format requirements
        req_text = f"Skills: {', '.join(requirements.get('required_skills', []))}\n"
        req_text += f"Experience: {requirements.get('experience_years_min', 0)}+ years\n"
        req_text += f"Location: {requirements.get('location', 'Not specified')}"
        
        # Format candidate profile
        cand_text = f"Name: {candidate.get('name', 'Unknown')}\n"
        cand_text += f"Skills: {', '.join(candidate.get('skills', []))}\n"
        cand_text += f"Experience: {candidate.get('experience_years', 0)} years\n"
        cand_text += f"Location: {candidate.get('location', 'Not specified')}"
        
        # Format match analysis
        match_score = match_data.get('skill_match_score', 0)
        skills_matched = ', '.join(match_data.get('matching_skills', []))
        skills_missing = ', '.join(match_data.get('missing_skills', []))
        
        # Format related skills with relationships
        related_skills_text = ""
        related_skills = match_data.get('related_skills', {})
        if related_skills:
            related_items = []
            for req_skill, rel_data in related_skills.items():
                cand_skill = rel_data.get('candidate_has', '')
                relationship = rel_data.get('relationship', 'related')
                related_items.append(f"{req_skill} (candidate has {cand_skill} - {relationship})")
            related_skills_text = '; '.join(related_items)
        else:
            related_skills_text = "None"
        
        # Build final prompt
        return self.prompt_template.format(
            requirements=req_text,
            candidate_profile=cand_text,
            match_score=int(match_score),
            skills_matched=skills_matched or "None",
            skills_missing=skills_missing or "None",
            related_skills=related_skills_text
        )
    
    def _generate_basic_explanation(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic explanation without AI (fallback)."""
        score = match_data.get('skill_match_score', 0)
        matched = match_data.get('total_matching', 0)
        related = match_data.get('total_related', 0)
        required = match_data.get('total_required', 1)
        
        # Generate template-based explanation
        if score >= 90:
            explanation = f"Excellent match with {matched}/{required} exact skill matches."
        elif score >= 75:
            explanation = f"Strong candidate with {matched}/{required} exact matches"
            if related > 0:
                explanation += f" and {related} related skills."
            else:
                explanation += "."
        elif score >= 60:
            explanation = f"Good fit with {matched}/{required} exact matches"
            if related > 0:
                explanation += f" plus {related} related skills that provide relevant experience."
            else:
                explanation += "."
        else:
            explanation = f"Partial match with {matched}/{required} exact matches"
            if related > 0:
                explanation += f" and {related} related skills."
            else:
                explanation += ". Significant skill gaps exist."
        
        return {
            "explanation": explanation,
            "confidence": 0.5,  # Lower confidence for template
            "_metadata": {
                "source": "template_fallback",
                "prompt_version": "none",
                "execution_time_seconds": 0.001,
                "timestamp": time.time(),
                "retry_count": 0
            }
        }


class ShortlistingService:
    """
    Generate candidate shortlist with recommendations.
    
    Business logic for creating final shortlist.
    """
    
    def generate_shortlist(
        self,
        scored_candidates: List[Dict[str, Any]],
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Generate shortlist from scored candidates.
        
        Args:
            scored_candidates: Candidates with scores
            top_n: Number of candidates to shortlist
        
        Returns:
            Shortlist with recommendations
        """
        # Select top N
        shortlist = scored_candidates[:top_n]
        
        # Generate recommendations
        for i, item in enumerate(shortlist, 1):
            score = item["scores"]["final"]
            candidate = item["candidate"]
            
            # Generate recommendation based on score
            if score >= 90:
                recommendation = "Excellent match. Proceed to interview immediately."
                priority = "High"
            elif score >= 75:
                recommendation = "Strong candidate. Schedule interview."
                priority = "High"
            elif score >= 60:
                recommendation = "Good fit. Consider for interview."
                priority = "Medium"
            else:
                recommendation = "Acceptable match. Review carefully before interview."
                priority = "Low"
            
            # Add rank and recommendation
            item["rank"] = i
            item["recommendation"] = recommendation
            item["priority"] = priority
        
        # Generate summary
        summary = {
            "total_candidates": len(scored_candidates),
            "shortlisted": len(shortlist),
            "average_score": round(sum(item["scores"]["final"] for item in shortlist) / len(shortlist), 1) if shortlist else 0,
            "high_priority": sum(1 for item in shortlist if item["priority"] == "High"),
            "medium_priority": sum(1 for item in shortlist if item["priority"] == "Medium"),
            "low_priority": sum(1 for item in shortlist if item["priority"] == "Low")
        }
        
        return {
            "shortlist": shortlist,
            "summary": summary
        }
