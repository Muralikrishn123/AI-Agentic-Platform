"""
HelloWorld Plugin - Plugin wrapper for HelloWorld functionality.
"""

from typing import Dict, Any
from app.core.interfaces import Plugin, AgentContext, AgentResponse
from app.services.agent_registry import get_agent_registry
from app.services.capability_registry import get_capability_registry, CapabilityCategory
from .agent import HelloWorldAgent


class HelloWorldPlugin(Plugin):
    """
    HelloWorld Plugin - Validates platform architecture.
    
    This plugin demonstrates:
    - Plugin lifecycle (initialize → execute)
    - Agent registration
    - Capability registration
    - End-to-end workflow
    """
    
    def __init__(self):
        super().__init__(
            name="hello_world",
            version="1.0.0",
            description="Simple plugin for testing platform architecture"
        )
        self._agent: HelloWorldAgent = None
    
    async def initialize(self):
        """
        Initialize the plugin.
        
        This is where we:
        - Create agent instances
        - Register agents
        - Register capabilities
        """
        print(f"🔧 Initializing {self.name} plugin...")
        
        try:
            # Create agent instance
            self._agent = HelloWorldAgent()
            
            # Get registries
            agent_registry = get_agent_registry()
            capability_registry = get_capability_registry()
            
            # Register agent (check if already registered)
            if not agent_registry.has_agent(self._agent.name):
                agent_registry.register(self._agent)
            else:
                print(f"⚠️  Agent already registered: {self._agent.name}")
            
            # Register capability (check if already registered)
            if not capability_registry.has_capability("hello_world"):
                capability_registry.register(
                    name="hello_world",
                    description="Say hello to validate platform architecture",
                    category=CapabilityCategory.CUSTOM,
                    agent_name=self._agent.name
                )
            else:
                print(f"⚠️  Capability already registered: hello_world")
            
            print(f"✅ {self.name} plugin initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize {self.name} plugin: {e}")
            raise
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Execute the plugin.
        
        Args:
            context: Agent execution context
            
        Returns:
            AgentResponse from the HelloWorldAgent
        """
        if self._agent is None:
            return AgentResponse(
                success=False,
                error="Plugin not initialized"
            )
        
        return await self._agent.execute(context)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return plugin capabilities."""
        return {
            "capabilities": ["hello_world"],
            "description": self.description,
            "version": self.version,
            "agent": self._agent.name if self._agent else None
        }
    
    async def cleanup(self):
        """Clean up plugin resources."""
        print(f"🗑️  Cleaning up {self.name} plugin...")
        self._agent = None
        print(f"✅ {self.name} plugin cleaned up")
