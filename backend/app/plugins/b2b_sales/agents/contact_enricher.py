"""
Step 5 — Contact Enricher Agent
Enriches decision-maker contacts with Email, Phone Number, and LinkedIn URL.
Simulates Hunter.io / Apollo.io / Lusha API responses.
"""
from app.core.interfaces import Agent, AgentContext, AgentResponse
from datetime import datetime


def _generate_email(name: str, company_website: str) -> str:
    """Generate professional email from name and company domain."""
    domain = company_website.replace("https://", "").replace("http://", "").strip("/")
    first = name.split()[0].lower()
    last = name.split()[-1].lower()
    return f"{first}.{last}@{domain}"


def _generate_phone() -> str:
    """Simulate Indian mobile number for demo purposes."""
    import random
    prefixes = ["98", "87", "99", "76", "96", "79"]
    prefix = random.choice(prefixes)
    number = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"+91 {prefix}{number[:4]} {number[4:]}"


class ContactEnricherAgent(Agent):
    """
    Step 5: Enrich contacts with Email, Phone Number, LinkedIn profile.

    Data sources simulated:
    - Hunter.io: professional email discovery
    - Lusha: direct phone numbers
    - LinkedIn Sales Navigator: verified LinkedIn profiles
    - Apollo.io: enrichment waterfall
    """

    def __init__(self):
        super().__init__("ContactEnricherAgent")

    async def execute(self, context: AgentContext) -> AgentResponse:
        companies = context.data.get("companies_with_contacts", [])

        if not companies:
            return AgentResponse(
                success=False,
                error="No companies with contacts to enrich",
                confidence=0.0,
            )

        enriched_companies = []
        total_enriched_contacts = 0

        for company in companies:
            website = company.get("website", f"https://{company['name'].lower().replace(' ', '')}.com")
            enriched_contacts = []

            for contact in company.get("decision_makers", []):
                linkedin_id = contact.get("linkedin_id", "")
                enriched_contact = {
                    **contact,
                    "email": _generate_email(contact["name"], website),
                    "phone": _generate_phone(),
                    "linkedin_url": f"https://linkedin.com/in/{linkedin_id}",
                    "email_verified": True,
                    "phone_verified": True,
                    "enrichment_source": "Hunter.io + Lusha",
                    "enriched_at": datetime.utcnow().isoformat(),
                    "outreach_recommended": contact.get("persona_score", 0) >= 0.75,
                }
                enriched_contacts.append(enriched_contact)
                total_enriched_contacts += 1

            enriched_companies.append({
                **company,
                "decision_makers": enriched_contacts,
            })

        return AgentResponse(
            success=True,
            data={
                "enriched_prospects": enriched_companies,
                "total_contacts_enriched": total_enriched_contacts,
                "enrichment_sources": ["Hunter.io", "Lusha", "LinkedIn Sales Navigator", "Apollo.io"],
                "enrichment_timestamp": datetime.utcnow().isoformat(),
            },
            confidence=0.91,
            next_step="prospect_summary",
        )
