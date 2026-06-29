"""
Step 3 — Company Enricher Agent
Validates and enriches matched company data: website, LinkedIn URL,
Glassdoor rating, recent news, tech stack verification, and a
qualification summary explaining WHY this company is a good fit.
"""
from app.core.interfaces import Agent, AgentContext, AgentResponse
from datetime import datetime

_ENRICHMENT_DATA = {
    "Nexus Technologies": {
        "website": "https://nexustech.io",
        "linkedin_url": "https://linkedin.com/company/nexus-technologies",
        "glassdoor_rating": 4.3,
        "recent_news": [
            "Nexus Technologies wins 'Fastest Growing SaaS Startup' at TechAwards 2025",
            "Partners with AWS to expand India cloud infrastructure",
        ],
        "open_roles_count": 12,
        "verified_tech_stack": ["Python 3.11", "FastAPI", "React 18", "PostgreSQL 15", "AWS EKS"],
        "hiring_velocity": "High — 12 roles/month",
        "company_type": "Private",
    },
    "CloudPeak Solutions": {
        "website": "https://cloudpeak.io",
        "linkedin_url": "https://linkedin.com/company/cloudpeak-solutions",
        "glassdoor_rating": 4.1,
        "recent_news": [
            "CloudPeak closes $18M Series B led by Sequoia India",
            "Expanding team from 150 to 250 by Q4 2025",
        ],
        "open_roles_count": 8,
        "verified_tech_stack": ["Go", "Kubernetes 1.28", "Terraform", "AWS", "GCP"],
        "hiring_velocity": "High — 8 roles/month",
        "company_type": "Private",
    },
    "DataStream AI": {
        "website": "https://datastreamai.com",
        "linkedin_url": "https://linkedin.com/company/datastream-ai",
        "glassdoor_rating": 4.5,
        "recent_news": [
            "New CTO Dr. Priya Kapoor joins from Google DeepMind",
            "DataStream AI integrates Gemini API into core platform",
        ],
        "open_roles_count": 6,
        "verified_tech_stack": ["Python", "TensorFlow 2.15", "FastAPI", "MongoDB", "Azure ML"],
        "hiring_velocity": "Medium — 6 roles/month",
        "company_type": "Private",
    },
    "Veritas SaaS": {
        "website": "https://veritassaas.com",
        "linkedin_url": "https://linkedin.com/company/veritas-saas",
        "glassdoor_rating": 3.9,
        "recent_news": [
            "Veritas SaaS expands DevOps and ML engineering teams",
            "Achieves SOC 2 Type II certification",
        ],
        "open_roles_count": 8,
        "verified_tech_stack": ["Java 21", "Spring Boot", "React", "Oracle", "AWS"],
        "hiring_velocity": "Medium — 8 roles/month",
        "company_type": "Private",
    },
    "Meridian Analytics": {
        "website": "https://meridiananalytics.in",
        "linkedin_url": "https://linkedin.com/company/meridian-analytics",
        "glassdoor_rating": 4.2,
        "recent_news": [
            "Launches Meridian AI — real-time analytics platform",
            "Partnership with Snowflake for data warehousing",
        ],
        "open_roles_count": 5,
        "verified_tech_stack": ["Python", "Apache Spark", "Airflow", "Snowflake", "GCP"],
        "hiring_velocity": "Medium — 5 roles/month",
        "company_type": "Private",
    },
    "Quantum Dynamics": {
        "website": "https://quantumdynamics.io",
        "linkedin_url": "https://linkedin.com/company/quantum-dynamics",
        "glassdoor_rating": 4.4,
        "recent_news": [
            "Quantum Dynamics raises $28M Series B to expand FinTech platform",
            "Opens new engineering hub in Bangalore with 50+ seats",
        ],
        "open_roles_count": 5,
        "verified_tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis", "AWS Lambda"],
        "hiring_velocity": "Medium — 5 roles/month",
        "company_type": "Private",
    },
}


class CompanyEnricherAgent(Agent):
    """
    Step 3: Validate and enrich company information.

    Enrichment sources (simulated):
    - Clearbit: company website, size, logo
    - Glassdoor: rating, reviews
    - LinkedIn: company page, employee count
    - News APIs: recent press coverage
    - BuiltWith: verified tech stack
    """

    def __init__(self):
        super().__init__("CompanyEnricherAgent")

    async def execute(self, context: AgentContext) -> AgentResponse:
        companies = context.data.get("qualified_companies", [])

        if not companies:
            return AgentResponse(
                success=False,
                error="No qualified companies to enrich",
                confidence=0.0,
            )

        enriched = []
        for company in companies:
            extra = _ENRICHMENT_DATA.get(company["name"], {})
            enriched_company = {
                **company,
                **extra,
                "enriched_at": datetime.utcnow().isoformat(),
                "data_confidence": "high" if extra else "low",
                "qualification_reason": self._build_reason(company),
            }
            enriched.append(enriched_company)

        return AgentResponse(
            success=True,
            data={
                "enriched_companies": enriched,
                "enrichment_sources": ["Clearbit", "LinkedIn", "Glassdoor", "BuiltWith", "NewsAPI"],
                "companies_enriched": len(enriched),
            },
            confidence=0.88,
            next_step="decision_maker_discovery",
        )

    def _build_reason(self, company: dict) -> str:
        reasons = []
        score = company.get("icp_score", 0)
        trigger = company.get("trigger", {})

        if score >= 0.8:
            reasons.append("Strong ICP match")
        elif score >= 0.6:
            reasons.append("Good ICP fit")

        signal = trigger.get("signal_type", "")
        if signal == "rapid_hiring":
            reasons.append("actively hiring tech talent")
        elif signal == "funding_round":
            reasons.append("recently funded — scaling now")
        elif signal == "leadership_change":
            reasons.append("new technical leadership — change window")

        reasons.append(f"{company.get('sector', '')} sector")
        reasons.append(f"Series {company.get('funding_stage', '').split()[-1] if company.get('funding_stage') else 'unknown'}")

        return " | ".join(reasons)
