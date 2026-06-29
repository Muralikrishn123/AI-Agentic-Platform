"""
Step 4 — Decision Maker Finder Agent
Identifies relevant decision-makers at each company based on configurable
target personas (role, seniority, department).

Configurable personas (via /api/config/personas):
- CTO / VP Engineering — technical hiring decisions
- Head of Talent / HR Director — staffing partner decisions
- CEO/Founder (small companies < 100 emp) — direct decision maker
"""
from app.core.interfaces import Agent, AgentContext, AgentResponse

# Simulated contact directory (in production: LinkedIn Sales Navigator, Hunter.io, Apollo.io)
_CONTACTS_DATABASE = {
    "Nexus Technologies": [
        {"name": "Arjun Krishnamurthy", "title": "Chief Technology Officer", "department": "Engineering",
         "seniority": "C-Suite", "linkedin_id": "arjun-krishnamurthy-cto", "tenure_years": 2.5},
        {"name": "Meera Shankar", "title": "VP Engineering", "department": "Engineering",
         "seniority": "VP", "linkedin_id": "meera-shankar-vpe", "tenure_years": 1.8},
        {"name": "Rohit Desai", "title": "Head of Talent Acquisition", "department": "HR",
         "seniority": "Director", "linkedin_id": "rohit-desai-ta", "tenure_years": 3.1},
    ],
    "CloudPeak Solutions": [
        {"name": "Suresh Narayanan", "title": "CTO & Co-Founder", "department": "Engineering",
         "seniority": "C-Suite", "linkedin_id": "suresh-narayanan-cto", "tenure_years": 4.0},
        {"name": "Divya Pillai", "title": "Director of Engineering", "department": "Engineering",
         "seniority": "Director", "linkedin_id": "divya-pillai-eng", "tenure_years": 1.2},
    ],
    "DataStream AI": [
        {"name": "Dr. Priya Kapoor", "title": "Chief Technology Officer", "department": "Engineering",
         "seniority": "C-Suite", "linkedin_id": "priya-kapoor-cto", "tenure_years": 0.3},
        {"name": "Vikram Menon", "title": "CEO & Founder", "department": "Leadership",
         "seniority": "C-Suite", "linkedin_id": "vikram-menon-ceo", "tenure_years": 3.5},
    ],
    "Veritas SaaS": [
        {"name": "Anand Balasubramanian", "title": "VP of Engineering", "department": "Engineering",
         "seniority": "VP", "linkedin_id": "anand-bala-vpe", "tenure_years": 2.0},
        {"name": "Kavitha Rajan", "title": "HR Director", "department": "HR",
         "seniority": "Director", "linkedin_id": "kavitha-rajan-hr", "tenure_years": 4.5},
    ],
    "Meridian Analytics": [
        {"name": "Siddharth Nair", "title": "Head of Engineering", "department": "Engineering",
         "seniority": "Director", "linkedin_id": "siddharth-nair-eng", "tenure_years": 2.8},
        {"name": "Preeti Gupta", "title": "Talent Acquisition Manager", "department": "HR",
         "seniority": "Manager", "linkedin_id": "preeti-gupta-ta", "tenure_years": 1.5},
    ],
    "Quantum Dynamics": [
        {"name": "Karthik Iyer", "title": "CTO", "department": "Engineering",
         "seniority": "C-Suite", "linkedin_id": "karthik-iyer-cto", "tenure_years": 3.2},
        {"name": "Nandini Sharma", "title": "VP Product & Engineering", "department": "Engineering",
         "seniority": "VP", "linkedin_id": "nandini-sharma-vpe", "tenure_years": 1.6},
    ],
}

# Persona priority scoring
_PERSONA_WEIGHTS = {
    "C-Suite": 1.0,
    "VP": 0.85,
    "Director": 0.75,
    "Manager": 0.60,
    "Individual Contributor": 0.40,
}


class DecisionMakerFinderAgent(Agent):
    """
    Step 4: Identify decision-makers by configurable target personas.

    Target personas (configurable):
    - Primary: CTO, VP Engineering (technical buying power)
    - Secondary: HR Director, Head of Talent (staffing decisions)
    - Tertiary: CEO/Founder (small company direct decision)
    """

    def __init__(self):
        super().__init__("DecisionMakerFinderAgent")

    async def execute(self, context: AgentContext) -> AgentResponse:
        companies = context.data.get("enriched_companies", [])
        persona_config = context.data.get("persona_config", {})

        target_seniorities = persona_config.get(
            "target_seniorities", ["C-Suite", "VP", "Director"]
        )
        target_departments = persona_config.get(
            "target_departments", ["Engineering", "HR", "Leadership"]
        )

        companies_with_contacts = []
        total_contacts = 0

        for company in companies:
            company_name = company["name"]
            all_contacts = _CONTACTS_DATABASE.get(company_name, [])

            # Filter by persona criteria
            matched_contacts = [
                c for c in all_contacts
                if c["seniority"] in target_seniorities
                and c["department"] in target_departments
            ]

            # Score contacts by persona weight
            for c in matched_contacts:
                c["persona_score"] = _PERSONA_WEIGHTS.get(c["seniority"], 0.5)

            matched_contacts.sort(key=lambda c: c["persona_score"], reverse=True)

            company_record = {
                **company,
                "decision_makers": matched_contacts,
                "contacts_found": len(matched_contacts),
            }
            companies_with_contacts.append(company_record)
            total_contacts += len(matched_contacts)

        return AgentResponse(
            success=True,
            data={
                "companies_with_contacts": companies_with_contacts,
                "total_decision_makers_found": total_contacts,
                "persona_filters": {
                    "seniorities": target_seniorities,
                    "departments": target_departments,
                },
            },
            confidence=0.87,
            next_step="contact_enrichment",
        )
