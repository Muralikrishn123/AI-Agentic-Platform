"""
Step 1 — Trigger Monitor Agent
Monitors business signals: job postings, funding rounds, product launches,
leadership changes. These are warm signals that a company may need our services.
"""
from app.core.interfaces import Agent, AgentContext, AgentResponse
from datetime import datetime, timedelta
import random


# Simulated trigger feed — in production this would query LinkedIn Jobs API,
# Crunchbase, TechCrunch RSS, Google News, etc.
_TRIGGER_FEED = [
    {
        "company": "Nexus Technologies",
        "signal_type": "rapid_hiring",
        "signal": "Posted 12 engineering roles in the last 30 days",
        "source": "LinkedIn Jobs",
        "date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "strength": "high",
    },
    {
        "company": "CloudPeak Solutions",
        "signal_type": "funding_round",
        "signal": "Raised $18M Series B — expanding engineering team",
        "source": "TechCrunch",
        "date": (datetime.utcnow() - timedelta(days=5)).isoformat(),
        "strength": "high",
    },
    {
        "company": "DataStream AI",
        "signal_type": "leadership_change",
        "signal": "New CTO hired — typically triggers tech team restructuring",
        "source": "LinkedIn",
        "date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "strength": "medium",
    },
    {
        "company": "Veritas SaaS",
        "signal_type": "rapid_hiring",
        "signal": "Posted 8 senior roles in DevOps and ML Engineering",
        "source": "Indeed",
        "date": (datetime.utcnow() - timedelta(days=3)).isoformat(),
        "strength": "high",
    },
    {
        "company": "Meridian Analytics",
        "signal_type": "product_launch",
        "signal": "Launched new AI product — scaling engineering capacity",
        "source": "Product Hunt",
        "date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
        "strength": "medium",
    },
    {
        "company": "Quantum Dynamics",
        "signal_type": "rapid_hiring",
        "signal": "Opened 5 backend engineer positions — Python/FastAPI focus",
        "source": "LinkedIn Jobs",
        "date": (datetime.utcnow() - timedelta(days=4)).isoformat(),
        "strength": "high",
    },
]


class TriggerMonitorAgent(Agent):
    """
    Step 1: Monitor web and market sources for configurable business triggers.

    Sources monitored (simulated):
    - LinkedIn Jobs: rapid hiring signals
    - Crunchbase: funding rounds
    - TechCrunch: leadership changes, product launches
    - Indeed / Naukri: job posting volume

    Configurable trigger types:
    - rapid_hiring: company posted N+ roles in last X days
    - funding_round: recently funded (Series A-D)
    - leadership_change: new CTO/VP Eng hired
    - product_launch: new product / expansion signal
    """

    def __init__(self):
        super().__init__("TriggerMonitorAgent")

    async def execute(self, context: AgentContext) -> AgentResponse:
        """Scan trigger feed and return companies with active business signals."""

        # Get configurable filters from context (set by ICP config)
        config = context.data.get("icp_config", {})
        trigger_types = config.get("trigger_types", ["rapid_hiring", "funding_round", "leadership_change"])
        min_strength = config.get("min_signal_strength", "medium")
        strength_order = {"low": 0, "medium": 1, "high": 2}
        min_level = strength_order.get(min_strength, 1)

        # Filter triggers matching config
        matched_triggers = [
            t for t in _TRIGGER_FEED
            if t["signal_type"] in trigger_types
            and strength_order.get(t["strength"], 0) >= min_level
        ]

        return AgentResponse(
            success=True,
            data={
                "triggers_found": len(matched_triggers),
                "triggers": matched_triggers,
                "sources_monitored": ["LinkedIn Jobs", "TechCrunch", "Crunchbase", "Indeed", "Product Hunt"],
                "trigger_types_active": trigger_types,
                "scan_timestamp": datetime.utcnow().isoformat(),
            },
            confidence=0.92,
            next_step="icp_matching",
        )
