"""
Step 2 — ICP Matcher Agent
Scores each triggered company against the configured Ideal Customer Profile (ICP).
Configurable criteria: company size, sector, funding stage, tech stack, geography.
"""
from app.core.interfaces import Agent, AgentContext, AgentResponse

# Enriched company data (in production: Crunchbase/Clearbit API)
_COMPANY_DATABASE = {
    "Nexus Technologies": {
        "name": "Nexus Technologies",
        "sector": "SaaS",
        "employee_count": 280,
        "funding_stage": "Series B",
        "total_funding_usd": 22_000_000,
        "hq": "Bangalore, India",
        "tech_stack": ["Python", "FastAPI", "React", "PostgreSQL", "AWS"],
        "annual_revenue_est": "5-10M",
        "founded": 2019,
        "growth_rate": "45% YoY",
    },
    "CloudPeak Solutions": {
        "name": "CloudPeak Solutions",
        "sector": "Cloud Infrastructure",
        "employee_count": 150,
        "funding_stage": "Series B",
        "total_funding_usd": 18_000_000,
        "hq": "Hyderabad, India",
        "tech_stack": ["Go", "Kubernetes", "Terraform", "AWS", "GCP"],
        "annual_revenue_est": "3-7M",
        "founded": 2020,
        "growth_rate": "60% YoY",
    },
    "DataStream AI": {
        "name": "DataStream AI",
        "sector": "AI/ML",
        "employee_count": 95,
        "funding_stage": "Series A",
        "total_funding_usd": 9_000_000,
        "hq": "Chennai, India",
        "tech_stack": ["Python", "TensorFlow", "FastAPI", "MongoDB", "Azure"],
        "annual_revenue_est": "1-3M",
        "founded": 2021,
        "growth_rate": "80% YoY",
    },
    "Veritas SaaS": {
        "name": "Veritas SaaS",
        "sector": "Enterprise SaaS",
        "employee_count": 420,
        "funding_stage": "Series C",
        "total_funding_usd": 55_000_000,
        "hq": "Mumbai, India",
        "tech_stack": ["Java", "Spring Boot", "React", "Oracle", "AWS"],
        "annual_revenue_est": "15-25M",
        "founded": 2017,
        "growth_rate": "30% YoY",
    },
    "Meridian Analytics": {
        "name": "Meridian Analytics",
        "sector": "Analytics",
        "employee_count": 180,
        "funding_stage": "Series A",
        "total_funding_usd": 12_000_000,
        "hq": "Pune, India",
        "tech_stack": ["Python", "Spark", "Airflow", "Snowflake", "GCP"],
        "annual_revenue_est": "3-6M",
        "founded": 2020,
        "growth_rate": "55% YoY",
    },
    "Quantum Dynamics": {
        "name": "Quantum Dynamics",
        "sector": "FinTech",
        "employee_count": 210,
        "funding_stage": "Series B",
        "total_funding_usd": 28_000_000,
        "hq": "Bangalore, India",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis", "AWS"],
        "annual_revenue_est": "8-12M",
        "founded": 2018,
        "growth_rate": "40% YoY",
    },
}


def _score_company(company: dict, icp: dict) -> float:
    """Score a company 0.0–1.0 against ICP criteria."""
    score = 0.0
    max_score = 5.0

    # Size match
    min_emp = icp.get("min_employees", 50)
    max_emp = icp.get("max_employees", 5000)
    if min_emp <= company["employee_count"] <= max_emp:
        score += 1.0

    # Sector match
    target_sectors = icp.get("sectors", ["SaaS", "Cloud Infrastructure", "AI/ML", "FinTech", "Analytics"])
    if company["sector"] in target_sectors:
        score += 1.5

    # Funding stage match
    target_stages = icp.get("funding_stages", ["Series A", "Series B", "Series C"])
    if company["funding_stage"] in target_stages:
        score += 1.0

    # Tech stack overlap (signals Python/modern stack preferred)
    preferred_tech = icp.get("preferred_tech", ["Python", "FastAPI", "React"])
    overlap = len(set(company["tech_stack"]) & set(preferred_tech))
    score += min(overlap * 0.25, 0.75)  # up to 0.75 for tech overlap

    # Geography
    target_geos = icp.get("geographies", ["India"])
    hq = company.get("hq", "")
    if any(geo in hq for geo in target_geos):
        score += 0.75

    return round(score / max_score, 2)


def _generate_icp_reason(company: dict, icp: dict, score: float) -> str:
    """Generate a readable explanation of why the company matches the ICP."""
    reasons = []
    
    # Sector match
    target_sectors = icp.get("sectors", [])
    if company["sector"] in target_sectors:
        reasons.append(f"Sector '{company['sector']}' matches target profile")
        
    # Size match
    min_emp = icp.get("min_employees", 50)
    max_emp = icp.get("max_employees", 5000)
    if min_emp <= company["employee_count"] <= max_emp:
        reasons.append(f"Size of {company['employee_count']} employees fits target range")
        
    # Funding match
    target_stages = icp.get("funding_stages", [])
    if company["funding_stage"] in target_stages:
        reasons.append(f"Stage '{company['funding_stage']}' matches criteria")
        
    # Tech overlap
    preferred_tech = icp.get("preferred_tech", [])
    overlap = list(set(company["tech_stack"]) & set(preferred_tech))
    if overlap:
        reasons.append(f"Uses preferred technologies: {', '.join(overlap)}")
        
    if not reasons:
        return f"Overall fit score of {int(score * 100)}% passes minimum qualification threshold."
        
    return " | ".join(reasons)


class ICPMatcherAgent(Agent):
    """
    Step 2: Score triggered companies against configurable ICP criteria.

    ICP criteria (all configurable via /api/config/icp):
    - Employee count range
    - Target sectors
    - Funding stages
    - Preferred tech stack
    - Target geographies
    """

    def __init__(self):
        super().__init__("ICPMatcherAgent")

    async def execute(self, context: AgentContext) -> AgentResponse:
        triggers = context.data.get("triggers", [])
        icp_config = context.data.get("icp_config", {})

        if not triggers:
            return AgentResponse(
                success=False,
                error="No triggers to match against ICP",
                confidence=0.0,
            )

        matched_companies = []
        for trigger in triggers:
            company_name = trigger["company"]
            company = _COMPANY_DATABASE.get(company_name)
            if not company:
                continue

            icp_score = _score_company(company, icp_config)
            if icp_score >= icp_config.get("min_icp_score", 0.5):
                matched_companies.append({
                    **company,
                    "icp_score": icp_score,
                    "trigger": trigger,
                    "qualification_status": "qualified" if icp_score >= 0.7 else "warm",
                    "matching_reason": _generate_icp_reason(company, icp_config, icp_score)
                })

        # Sort by ICP score desc
        matched_companies.sort(key=lambda c: c["icp_score"], reverse=True)


        return AgentResponse(
            success=True,
            data={
                "companies_evaluated": len(triggers),
                "companies_matched": len(matched_companies),
                "qualified_companies": matched_companies,
                "icp_criteria_used": icp_config,
            },
            confidence=0.90,
            next_step="company_enrichment",
        )
