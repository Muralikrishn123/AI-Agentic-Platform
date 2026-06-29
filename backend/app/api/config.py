"""ICP and Persona configuration API endpoints."""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.api.auth import get_current_user
from app.database.models import ICPConfigModel
from config.settings import settings

router = APIRouter()


class ICPConfig(BaseModel):
    # Generic domain config — NO SaaS-specific fields
    organization_types: List[str] = ["Company", "Institution", "Hospital", "College", "Factory"]
    target_geographies: List[str] = ["India"]
    target_keywords: List[str] = []
    business_triggers: List[str] = ["expansion", "procurement", "new_project"]
    min_signal_strength: str = "medium"
    min_match_score: float = 0.6
    # Size range — generic enough to apply to headcount, students, beds, sq ft etc.
    size_min: str = ""
    size_max: str = ""
    size_unit: str = "employees"


class PersonaConfig(BaseModel):
    role: str
    seniority: str
    department: str
    priority: int = 1


class FullConfig(BaseModel):
    icp: ICPConfig
    personas: List[PersonaConfig]


def _user_id_from_request(request: Request) -> Optional[str]:
    """Extract user_id from Bearer token without raising — returns None if invalid/absent."""
    try:
        from jose import jwt as _jwt
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth.split(" ", 1)[1]
        payload = _jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None


# ── Public read endpoints (no auth required) ────────────────────────────────

@router.get("/defaults")
async def get_defaults() -> Dict[str, Any]:
    """Return the default ICP and persona configuration (public)."""
    return await ICPConfigModel.get_default_config()


@router.get("/")
async def get_config(request: Request) -> Dict[str, Any]:
    """
    Get ICP + persona config.
    - If authenticated: returns user's saved config (or defaults).
    - If not authenticated: returns platform defaults.
    Always succeeds — never returns 401.
    """
    user_id = _user_id_from_request(request)
    if user_id:
        config = await ICPConfigModel.get_config(user_id)
        if config:
            return config
    return await ICPConfigModel.get_default_config()


# ── Protected write endpoint ─────────────────────────────────────────────────

@router.post("/")
async def save_config(
    body: FullConfig,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Save ICP and persona configuration for the authenticated user."""
    config_data = {
        "icp": body.icp.model_dump(),
        "personas": [p.model_dump() for p in body.personas],
    }
    saved = await ICPConfigModel.save_config(current_user["_id"], config_data)
    return {"success": True, "config": saved}
