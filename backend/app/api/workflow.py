from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.api.auth import get_current_user
from app.services.workflow_engine import WorkflowEngine
from app.database.models import WorkflowModel

router = APIRouter()


class WorkflowStartRequest(BaseModel):
    user_request: str
    plugin: Optional[str] = None


def get_workflow_engine(request: Request) -> WorkflowEngine:
    """
    Get the WorkflowEngine pre-created during app startup (lifespan).
    It is wired to the PluginLifecycleManager that has all registered plugins.
    Falls back to creating a new one without plugins if state is not ready.
    """
    engine = getattr(request.app.state, "workflow_engine", None)
    if engine is None:
        # Fallback: create engine with whatever lifecycle manager is available
        plugin_lifecycle_manager = getattr(request.app.state, "plugin_lifecycle_manager", None)
        engine = WorkflowEngine(plugin_lifecycle_manager)
        request.app.state.workflow_engine = engine
    return engine


@router.post("/start")
async def start_workflow(
    request: Request,
    body: WorkflowStartRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start a new workflow execution. Returns workflow_id immediately; execution runs in background."""

    engine = get_workflow_engine(request)

    import uuid, asyncio
    from datetime import datetime

    # Create workflow record up-front so frontend can start polling immediately
    workflow_id = str(uuid.uuid4())
    workflow_data = {
        "workflow_id": workflow_id,
        "user_id": current_user["_id"],
        "user_request": body.user_request,
        "status": "in_progress",
        "steps": [],
        "errors": [],
        "retry_count": 0,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Save initial record to DB so GET works immediately
    try:
        await WorkflowModel.create_workflow(workflow_data)
    except Exception as e:
        print(f"⚠️  Could not pre-save workflow: {e}")

    # Run the actual execution in the background
    async def run_in_bg():
        try:
            result = await engine.execute_workflow(
                user_request=body.user_request,
                user_id=current_user["_id"],
                selected_plugin_override=body.plugin,
                workflow_id_override=workflow_id,
            )
        except Exception as e:
            print(f"❌ Background workflow error: {e}")
            await WorkflowModel.update_workflow(workflow_id, {
                "status": "failed",
                "errors": [str(e)]
            })

    asyncio.create_task(run_in_bg())

    return {
        "success": True,
        "workflow": workflow_data
    }


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get workflow by ID."""

    workflow = await WorkflowModel.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check ownership
    if workflow.get("user_id") != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return workflow


@router.get("/")
async def list_workflows(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List user's workflows."""

    workflows = await WorkflowModel.list_workflows(current_user["_id"])
    return workflows


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a workflow execution from history."""
    workflow = await WorkflowModel.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    if workflow.get("user_id") != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workflow")

    deleted = await WorkflowModel.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete workflow")

    return {"success": True, "message": "Workflow deleted successfully"}







