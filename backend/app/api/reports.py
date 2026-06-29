from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.api.auth import get_current_user
from app.database.models import ReportModel

router = APIRouter()


@router.get("/")
async def list_reports(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List all reports."""
    
    reports = await ReportModel.list_reports()
    return reports


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a specific report."""
    
    report = await ReportModel.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report
