from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List
from app.api.auth import get_current_user


router = APIRouter()


def get_lifecycle_manager(request: Request):
    """Get the shared PluginLifecycleManager from app state."""
    mgr = getattr(request.app.state, "plugin_lifecycle_manager", None)
    if mgr is None:
        raise HTTPException(status_code=503, detail="Plugin manager not initialized")
    return mgr


class PluginEnableRequest(BaseModel):
    plugin_name: str


@router.get("/")
async def list_plugins(
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List all registered plugins (built-in + custom from MongoDB)."""
    mgr = get_lifecycle_manager(request)

    # Built-in plugins from the lifecycle manager
    plugins_list = mgr.list_plugins()

    # Merge custom plugins from MongoDB (user-created)
    try:
        from app.database.models import CustomPluginModel
        customs = await CustomPluginModel.get_plugins()
        registered_names = {p["name"] for p in plugins_list}
        for cp in customs:
            if cp["name"] in registered_names:
                continue
            plugins_list.append({
                "name": cp["name"],
                "version": "1.0.0",
                "description": cp["description"],
                "enabled": cp.get("enabled", True),
                "capabilities": {
                    "capabilities": ["research_agent", "qualification_agent", "contact_discovery_agent"],
                    "description": cp["description"],
                    "version": "1.0.0",
                    "stage": "Dynamic Custom Domain",
                    "custom": True,
                    "geography": cp.get("geography", []),
                    "organizationTypes": cp.get("organizationTypes", []),
                    "keywords": cp.get("keywords", []),
                    "triggers": cp.get("businessTriggers", cp.get("triggers", [])),
                    "personas": cp.get("personas", []),
                    "requirements": cp.get("requirements", []),
                    # Keep fallbacks for backwards compatibility in UI if needed
                    "icp_config": cp.get("icp_config", {}),
                    "rules": cp.get("rules", []),
                }
            })
    except Exception as e:
        print("Error merging custom plugins:", e)

    return plugins_list


@router.post("/enable")
async def enable_plugin(
    request: Request,
    body: PluginEnableRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Enable a plugin."""
    mgr = get_lifecycle_manager(request)
    result = await mgr.enable_plugin(body.plugin_name)
    if not result.get("success"):
        from app.database.models import CustomPluginModel
        cp = await CustomPluginModel.get_plugin_by_name(body.plugin_name)
        if cp:
            cp["enabled"] = True
            await CustomPluginModel.create_plugin(cp)
            return {"success": True, "message": f"Plugin '{body.plugin_name}' enabled", "state": "enabled"}
        raise HTTPException(status_code=404, detail=result.get("error", "Plugin not found"))
    return {"success": True, "message": f"Plugin '{body.plugin_name}' enabled", "state": result.get("state")}


@router.post("/disable")
async def disable_plugin(
    request: Request,
    body: PluginEnableRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Disable a plugin."""
    mgr = get_lifecycle_manager(request)
    result = await mgr.disable_plugin(body.plugin_name)
    if not result.get("success"):
        from app.database.models import CustomPluginModel
        cp = await CustomPluginModel.get_plugin_by_name(body.plugin_name)
        if cp:
            cp["enabled"] = False
            await CustomPluginModel.create_plugin(cp)
            return {"success": True, "message": f"Plugin '{body.plugin_name}' disabled", "state": "disabled"}
        raise HTTPException(status_code=404, detail=result.get("error", "Plugin not found"))
    return {"success": True, "message": f"Plugin '{body.plugin_name}' disabled", "state": result.get("state")}


class PersonaConfig(BaseModel):
    role: str
    department: str
    seniority: str


class RequirementConfig(BaseModel):
    field: str
    operator: str
    value: str


class CustomPluginCreateRequest(BaseModel):
    domainName: str
    description: str
    geography: List[str] = []
    organizationTypes: List[str] = []
    keywords: List[str] = []
    businessTriggers: List[str] = []
    personas: List[PersonaConfig] = []
    requirements: List[RequirementConfig] = []


@router.post("/create")
async def create_custom_plugin(
    request: CustomPluginCreateRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new custom domain plugin dynamically."""
    from app.database.models import CustomPluginModel
    plugin_data = {
        "name": request.domainName.lower().replace(" ", "_"),
        "display_name": request.domainName,
        "description": request.description,
        "geography": request.geography,
        "organizationTypes": request.organizationTypes,
        "keywords": request.keywords,
        "businessTriggers": request.businessTriggers,
        "personas": [p.dict() for p in request.personas],
        "requirements": [r.dict() for r in request.requirements],
        "enabled": True
    }
    await CustomPluginModel.create_plugin(plugin_data)
    return {"success": True, "plugin": plugin_data}


@router.delete("/{name}")
async def delete_plugin(
    name: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a plugin — works for both custom (MongoDB) and built-in (lifecycle) plugins."""
    from app.database.models import CustomPluginModel

    # 1. Try deleting from MongoDB custom plugins first
    deleted_from_mongo = await CustomPluginModel.delete_plugin(name)

    # 2. Try uninstalling from the lifecycle manager (built-in plugins)
    mgr = getattr(request.app.state, "plugin_lifecycle_manager", None)
    uninstalled = False
    if mgr and name in mgr._plugins:
        result = await mgr.uninstall_plugin(name)
        uninstalled = result.get("success", False)

    if not deleted_from_mongo and not uninstalled:
        raise HTTPException(
            status_code=404,
            detail=f"Plugin '{name}' not found."
        )

    return {"success": True, "message": f"Plugin '{name}' deleted successfully"}

