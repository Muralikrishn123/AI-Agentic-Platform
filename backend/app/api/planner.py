from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.core.planner import PlannerAgent
from app.core.interfaces import AgentContext
from app.services.llm import get_llm_provider
from app.api.auth import get_current_user
import uuid

router = APIRouter()


class PlannerRequest(BaseModel):
    user_request: str


@router.post("/")
async def create_plan(
    request: PlannerRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a workflow plan from user request."""
    
    try:
        llm_provider = get_llm_provider()
        planner = PlannerAgent(llm_provider)
        
        context = AgentContext(
            workflow_id=str(uuid.uuid4()),
            user_request=request.user_request,
            current_step="planning",
            data={}
        )
        
        response = await planner.execute(context)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)
        
        return {
            "success": True,
            "workflow_plan": response.data,
            "confidence": response.confidence
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
