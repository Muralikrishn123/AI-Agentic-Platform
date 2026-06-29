from typing import Dict, Optional, List, Any
from app.core.interfaces import Agent


class AgentRegistry:
    """
    Agent Registry - Central registry for all agents.
    
    This is a critical component that allows:
    - Platform agents to register themselves
    - Plugin agents to register themselves
    - Dynamic agent discovery
    - No hardcoded agent references
    
    Responsibilities:
    - Register agents
    - Get agent by name
    - List all available agents
    - Unregister agents
    """
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
    
    def register(self, agent: Agent) -> None:
        """Register an agent in the registry."""
        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered")
        
        self._agents[agent.name] = agent
        print(f"✅ Registered agent: {agent.name}")
    
    def unregister(self, agent_name: str) -> bool:
        """Unregister an agent from the registry."""
        if agent_name in self._agents:
            del self._agents[agent_name]
            print(f"❌ Unregistered agent: {agent_name}")
            return True
        return False
    
    def get(self, agent_name: str) -> Optional[Agent]:
        """Get an agent by name."""
        return self._agents.get(agent_name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return [
            {
                "name": agent.name,
                "type": agent.__class__.__name__,
                "module": agent.__class__.__module__
            }
            for agent in self._agents.values()
        ]
    
    def has_agent(self, agent_name: str) -> bool:
        """Check if an agent is registered."""
        return agent_name in self._agents
    
    def clear(self) -> None:
        """Clear all registered agents (for testing)."""
        self._agents.clear()


# Global registry instance
_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    return _registry
