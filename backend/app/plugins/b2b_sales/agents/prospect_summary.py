"""
Step 6 — Prospect Summary Agent
Generates an actionable summary with ranked prospects and
recommended next actions for each company/contact.
"""
from app.core.interfaces import Agent, AgentContext, AgentResponse
from datetime import datetime


_OUTREACH_TEMPLATES = {
    "rapid_hiring": (
        "Hi {first_name}, I noticed {company} has been on a strong hiring sprint recently "
        "— {open_roles} open engineering roles is impressive growth. We specialise in helping "
        "{sector} companies like yours find senior {tech} engineers within 2–3 weeks. "
        "Would a quick 15-min call this week make sense?"
    ),
    "funding_round": (
        "Hi {first_name}, congrats on {company}'s recent funding round — exciting times! "
        "As you scale the team, finding the right senior engineers quickly becomes critical. "
        "We've helped similar {sector} companies hire {tech} talent 40% faster than traditional methods. "
        "Happy to share how — open to a short call?"
    ),
    "leadership_change": (
        "Hi {first_name}, I see you recently joined {company} as {title} — congrats! "
        "Many technical leaders in their first 90 days prioritise building the right team. "
        "We specialise in {tech} talent for {sector} companies and can move fast. "
        "Would love to connect and understand your roadmap."
    ),
    "product_launch": (
        "Hi {first_name}, saw the news about {company}'s new product launch — exciting! "
        "Scaling engineering capacity after a launch is always a challenge. "
        "We help {sector} companies hire vetted {tech} engineers in weeks, not months. "
        "Worth a quick conversation?"
    ),
}


def _build_outreach(contact: dict, company: dict) -> str:
    trigger = company.get("trigger", {})
    signal_type = trigger.get("signal_type", "rapid_hiring")
    template = _OUTREACH_TEMPLATES.get(signal_type, _OUTREACH_TEMPLATES["rapid_hiring"])

    tech_stack = company.get("tech_stack", ["Python"])
    top_tech = ", ".join(tech_stack[:2])

    return template.format(
        first_name=contact["name"].split()[0],
        company=company["name"],
        title=contact["title"],
        sector=company.get("sector", "Tech"),
        tech=top_tech,
        open_roles=company.get("open_roles_count", "several"),
    )


def _next_actions(contact: dict, company: dict) -> list:
    actions = []
    trigger_type = company.get("trigger", {}).get("signal_type", "")

    if contact.get("persona_score", 0) >= 0.85:
        actions.append("🔥 Priority outreach — C-Suite / VP decision maker")
    else:
        actions.append("📧 Send personalised email via outreach sequence")

    if trigger_type == "funding_round":
        actions.append("⏰ Time-sensitive — contact within 48h of funding announcement")
    elif trigger_type == "leadership_change":
        actions.append("🎯 New leader in role — optimal 30-day window for first contact")

    if company.get("icp_score", 0) >= 0.8:
        actions.append("✅ High ICP match — escalate to senior account executive")
    
    actions.append(f"🔗 Connect on LinkedIn: linkedin.com/in/{contact.get('linkedin_id', '')}")
    actions.append("📅 Add to 5-touch outreach cadence in CRM")

    return actions


class ProspectSummaryAgent(Agent):
    """
    Step 6: Generate actionable prospect summary with ranked list and next actions.

    Output:
    - Ranked prospect list by ICP score + signal strength
    - Personalised outreach message per contact
    - Recommended next actions per prospect
    - Overall pipeline summary
    """

    def __init__(self):
        super().__init__("ProspectSummaryAgent")

    async def execute(self, context: AgentContext) -> AgentResponse:
        prospects = context.data.get("enriched_prospects", [])
        user_request = context.user_request

        if not prospects:
            return AgentResponse(
                success=False,
                error="No enriched prospects to summarise",
                confidence=0.0,
            )

        # Build actionable prospect records
        prospect_list = []
        for company in prospects:
            top_contact = company.get("decision_makers", [None])[0]
            if not top_contact:
                continue

            prospect_list.append({
                "rank": 0,  # will be set after sort
                "company": {
                    "name": company["name"],
                    "sector": company.get("sector"),
                    "employee_count": company.get("employee_count"),
                    "funding_stage": company.get("funding_stage"),
                    "hq": company.get("hq"),
                    "website": company.get("website"),
                    "linkedin_url": company.get("linkedin_url"),
                    "icp_score": company.get("icp_score"),
                    "qualification_status": company.get("qualification_status"),
                    "qualification_reason": company.get("qualification_reason"),
                    "trigger": company.get("trigger"),
                    "glassdoor_rating": company.get("glassdoor_rating"),
                    "recent_news": company.get("recent_news", [])[:1],
                    "open_roles_count": company.get("open_roles_count"),
                    "growth_rate": company.get("growth_rate"),
                },
                "primary_contact": {
                    "name": top_contact.get("name"),
                    "title": top_contact.get("title"),
                    "email": top_contact.get("email"),
                    "phone": top_contact.get("phone"),
                    "linkedin_url": top_contact.get("linkedin_url"),
                    "persona_score": top_contact.get("persona_score"),
                },
                "all_contacts": company.get("decision_makers", []),
                "outreach_message": _build_outreach(top_contact, company),
                "next_actions": _next_actions(top_contact, company),
                "priority": "high" if company.get("icp_score", 0) >= 0.75 else "medium",
            })

        # Sort by ICP score
        prospect_list.sort(key=lambda p: p["company"]["icp_score"], reverse=True)
        for i, p in enumerate(prospect_list):
            p["rank"] = i + 1

        high_priority = [p for p in prospect_list if p["priority"] == "high"]

        return AgentResponse(
            success=True,
            data={
                "prospect_list": prospect_list,
                "total_prospects": len(prospect_list),
                "high_priority_count": len(high_priority),
                "pipeline_summary": {
                    "total_companies_analysed": len(prospects),
                    "qualified_prospects": len(prospect_list),
                    "high_priority": len(high_priority),
                    "estimated_pipeline_value": f"${len(prospect_list) * 15_000:,} – ${len(prospect_list) * 40_000:,}",
                    "recommended_weekly_outreach": min(len(high_priority), 10),
                },
                "generated_at": datetime.utcnow().isoformat(),
                "domain": "B2B Sales Intelligence",
            },
            confidence=0.93,
            next_step="hitl_approval",
        )
