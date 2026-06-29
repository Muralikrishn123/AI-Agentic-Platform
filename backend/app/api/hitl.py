"""HITL (Human-in-the-Loop) approval API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.api.auth import get_current_user
from app.database.models import HITLModel, WorkflowModel

router = APIRouter()


class ApprovalAction(BaseModel):
    workflow_id: str
    action: str  # "approve" or "reject"
    notes: Optional[str] = None
    approved_item_ids: Optional[List[str]] = None
    rejected_items: Optional[List[Dict[str, Any]]] = None


@router.get("/")
async def list_approvals(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List all HITL approval records (pending + resolved)."""
    return await HITLModel.list_all()


@router.get("/pending")
async def list_pending_approvals(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List pending HITL approvals awaiting human review."""
    return await HITLModel.list_pending()


@router.get("/{workflow_id}")
async def get_approval(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get HITL approval record for a specific workflow."""
    record = await HITLModel.get_approval(workflow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Approval record not found")
    return record


@router.post("/action")
async def take_approval_action(
    body: ApprovalAction,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Approve or reject a HITL review item, applying granular selection filters."""
    if body.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    # 1. Update the HITL approval record
    updated = await HITLModel.update_status(
        workflow_id=body.workflow_id,
        status="approved" if body.action == "approve" else "rejected",
        notes=body.notes,
        approved_item_ids=body.approved_item_ids,
        rejected_items=body.rejected_items
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Approval record not found or already resolved")

    # 2. Update the corresponding Workflow document to sync execution states
    workflow = await WorkflowModel.get_workflow(body.workflow_id)
    if workflow:
        workflow_update: Dict[str, Any] = {
            "hitl_status": "approved" if body.action == "approve" else "rejected",
            "status": "completed" if body.action == "approve" else "failed"
        }
        
        # If granular approvals are provided, filter the workflow's plugin execution outputs
        if body.approved_item_ids is not None:
            steps = workflow.get("steps", [])
            for step in steps:
                if step.get("step") == "plugin_execution":
                    step_data = step.get("data", {})
                    
                    # Filter B2B prospects / qualified companies
                    target_key = None
                    if "prospect_list" in step_data:
                        target_key = "prospect_list"
                    elif "qualified_companies" in step_data:
                        target_key = "qualified_companies"
                    elif "prospects" in step_data:
                        target_key = "prospects"

                    if target_key:
                        filtered_list = [
                            p for p in step_data[target_key]
                            if (p.get("company", {}).get("name") in body.approved_item_ids or 
                                p.get("name") in body.approved_item_ids)
                        ]
                        step_data[target_key] = filtered_list
                        if "pipeline_summary" in step_data and isinstance(step_data["pipeline_summary"], dict):
                            step_data["pipeline_summary"]["qualified_prospects"] = len(filtered_list)
                        
                    # Filter HR candidates
                    if "shortlist" in step_data:
                        filtered_list = [
                            c for c in step_data["shortlist"]
                            if c.get("name") in body.approved_item_ids
                        ]
                        step_data["shortlist"] = filtered_list
            
            workflow_update["steps"] = steps

        # Update the workflow in MongoDB
        await WorkflowModel.update_workflow(body.workflow_id, workflow_update)

    return {
        "success": True,
        "workflow_id": body.workflow_id,
        "action": body.action,
        "message": f"Workflow {body.workflow_id[:8]}… has been {'approved ✅' if body.action == 'approve' else 'rejected ❌'}",
    }
