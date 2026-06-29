from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List, Optional
from app.api.auth import get_current_user
from app.database.models import LogModel

router = APIRouter()


@router.get("/")
async def get_logs(
    workflow_id: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get logs with optional filtering."""
    
    logs = await LogModel.get_logs(workflow_id=workflow_id, limit=limit)
    return logs
