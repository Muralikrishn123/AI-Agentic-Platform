import sys

# Workaround for Python 3.14 + protobuf metaclass bug
sys.modules['google._upb._message'] = None

# Workaround for Windows Application Control policy blocking grpc native DLL (cygrpc)
class MockObject:
    def __getattr__(self, name):
        return self
    def __call__(self, *args, **kwargs):
        return self
    def __getitem__(self, item):
        return self

sys.modules['grpc._cython.cygrpc'] = MockObject()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api import auth, planner, workflow, plugins, reports, logs, hitl, config
from config.settings import settings

# Import for registries
from app.services.agent_registry import get_agent_registry
from app.services.capability_registry import get_capability_registry, CapabilityCategory
from app.services.event_bus import get_event_bus, EventType
from app.services.plugin_lifecycle_manager import PluginLifecycleManager
from app.core.planner import PlannerAgent
from app.core.validation import ValidationAgent
from app.core.reflection import ReflectionAgent
from app.core.report import ReportGenerator
from app.core.hitl import HITLApprovalAgent
from app.services.llm import get_llm_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    # Startup
    await connect_to_mongo()
    
    # Initialize registries
    agent_registry = get_agent_registry()
    capability_registry = get_capability_registry()
    event_bus = get_event_bus()
    llm_provider = get_llm_provider()
    
    # Register platform agents
    agent_registry.register(PlannerAgent(llm_provider))
    agent_registry.register(ValidationAgent())
    agent_registry.register(ReflectionAgent(llm_provider))
    agent_registry.register(ReportGenerator())
    agent_registry.register(HITLApprovalAgent())
    
    # Register platform capabilities
    capability_registry.register(
        name="planning",
        description="Plan workflows based on user requests",
        category=CapabilityCategory.PLANNING,
        agent_name="PlannerAgent"
    )
    
    capability_registry.register(
        name="validation",
        description="Validate workflow outputs",
        category=CapabilityCategory.VALIDATION,
        agent_name="ValidationAgent"
    )
    
    capability_registry.register(
        name="reflection",
        description="Evaluate workflow quality and decide retries",
        category=CapabilityCategory.ANALYSIS,
        agent_name="ReflectionAgent"
    )
    
    capability_registry.register(
        name="reporting",
        description="Generate workflow reports",
        category=CapabilityCategory.REPORTING,
        agent_name="ReportGenerator"
    )
    
    print("✅ All core agents registered")
    print("✅ All core capabilities registered")
    
    # Initialize plugins via Plugin Lifecycle Manager
    plugin_lifecycle_manager = PluginLifecycleManager()
    
    try:
        from app.plugins.hr_recruitment.plugin import HRRecruitmentPlugin
        hr_plugin = HRRecruitmentPlugin()
        result = await plugin_lifecycle_manager.install_plugin(hr_plugin)
        if result.get("success"):
            await plugin_lifecycle_manager.initialize_plugin("hr_recruitment")
            await plugin_lifecycle_manager.enable_plugin("hr_recruitment")
            print("✅ HR Recruitment Plugin installed & enabled")
        else:
            print(f"⚠️  HR Plugin install failed: {result.get('error')}")
    except Exception as e:
        print(f"⚠️  HR Plugin startup error: {e}")
        import traceback
        traceback.print_exc()

    # Install B2B Sales Intelligence Plugin
    try:
        from app.plugins.b2b_sales.plugin import B2BSalesPlugin
        b2b_plugin = B2BSalesPlugin()
        result = await plugin_lifecycle_manager.install_plugin(b2b_plugin)
        if result.get("success"):
            await plugin_lifecycle_manager.initialize_plugin("b2b_sales")
            await plugin_lifecycle_manager.enable_plugin("b2b_sales")
            print("✅ B2B Sales Intelligence Plugin installed & enabled")
        else:
            print(f"⚠️  B2B Plugin install failed: {result.get('error')}")
    except Exception as e:
        print(f"⚠️  B2B Plugin startup error: {e}")
        import traceback
        traceback.print_exc()

    # Store plugin lifecycle manager on app state for API access
    app.state.plugin_lifecycle_manager = plugin_lifecycle_manager
    
    # Give PlannerAgent access to the plugin lifecycle manager so it can include
    # available plugin names in its LLM prompt for correct routing
    planner_agent = agent_registry.get("PlannerAgent")
    if planner_agent:
        # Adapt lifecycle manager to match the interface PlannerAgent expects
        from app.services.plugin_lifecycle_manager import PluginState as _PS
        class _PluginManagerAdapter:
            def __init__(self, mgr):
                self._mgr = mgr
            async def list_plugins(self):
                plugs = [
                    {"name": name, "enabled": True}
                    for name, state in self._mgr._states.items()
                    if state == _PS.ENABLED
                ]
                try:
                    from app.database.models import CustomPluginModel
                    customs = await CustomPluginModel.get_plugins()
                    for cp in customs:
                        if cp.get("enabled", True):
                            plugs.append({
                                "name": cp["name"],
                                "enabled": True,
                                "display_name": cp.get("display_name", cp["name"]),
                                "description": cp.get("description", "")
                            })
                except Exception as e:
                    print("Error loading custom plugins for PlannerAgent adapter:", e)
                return plugs
        planner_agent.plugin_manager = _PluginManagerAdapter(plugin_lifecycle_manager)
        print("✅ PlannerAgent wired to PluginManager for dynamic routing")

    # Pre-create WorkflowEngine with the live plugin_lifecycle_manager
    # so workflow.py always picks up the right instance
    from app.services.workflow_engine import WorkflowEngine
    app.state.workflow_engine = WorkflowEngine(plugin_lifecycle_manager)
    print("✅ WorkflowEngine created with PluginLifecycleManager")

    
    # Emit system ready event
    await event_bus.emit(EventType.SYSTEM_READY, {"version": "3.0"})
    
    yield
    
    # Shutdown
    await event_bus.emit(EventType.SYSTEM_SHUTDOWN, {})
    await close_mongo_connection()


app = FastAPI(
    title="Agentic AI Platform",
    description="A reusable multi-agent platform for domain-specific AI plugins",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(planner.router, prefix="/api/planner", tags=["Planner"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["Workflow"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["Plugins"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(hitl.router, prefix="/api/hitl", tags=["HITL"])
app.include_router(config.router, prefix="/api/config", tags=["Config"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agentic AI Platform API",
        "version": "3.0.0",
        "status": "running"
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    agent_registry = get_agent_registry()
    capability_registry = get_capability_registry()
    agents = [a['name'] for a in agent_registry.list_agents()] if hasattr(agent_registry, 'list_agents') else []
    capabilities = [c['name'] for c in capability_registry.list_capabilities()]
    return {
        "status": "healthy",
        "agents_registered": len(agents),
        "capabilities_registered": len(capabilities),
        "agents": agents,
        "capabilities": capabilities
    }


@app.get("/api/agents")
async def list_agents():
    """List all registered agents."""
    agent_registry = get_agent_registry()
    agents = agent_registry.list_agents()
    return {"agents": agents, "total": len(agents)}


@app.get("/api/capabilities")
async def list_capabilities():
    """List all registered capabilities."""
    capability_registry = get_capability_registry()
    caps = capability_registry.list_capabilities()
    return {"capabilities": caps, "total": len(caps)}
