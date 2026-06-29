from typing import Dict, Optional, List, Any, Set
from enum import Enum


class CapabilityCategory(str, Enum):
    """Standard capability categories."""
    DISCOVERY = "discovery"
    ANALYSIS = "analysis"
    ENRICHMENT = "enrichment"
    RECOMMENDATION = "recommendation"
    COMMUNICATION = "communication"
    REPORTING = "reporting"
    VALIDATION = "validation"
    PLANNING = "planning"
    CUSTOM = "custom"
    EXTRACTION = "extraction"
    SEARCH = "search"
    MATCHING = "matching"
    SCORING = "scoring"
    SHORTLISTING = "shortlisting"
    EXPLANATION = "explanation"  # Iteration 2: AI explanations for algorithm decisions


class Capability:
    """Represents a capability that an agent provides."""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: CapabilityCategory,
        agent_name: str,
        required_tools: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.name = name
        self.description = description
        self.category = category
        self.agent_name = agent_name
        self.required_tools = required_tools or []
        self.metadata = metadata or {}


class CapabilityRegistry:
    """
    Capability Registry - Maps capabilities to agents.
    
    This is THE KEY to making the platform truly extensible.
    
    Instead of:
        Planner → knows agent names → calls specific agents
    
    We have:
        Planner → knows capabilities → Capability Registry → resolves to agent
    
    Benefits:
    - Planner doesn't know any agent names
    - Multiple agents can provide same capability
    - Easy to add new capabilities
    - Capability-based routing
    - Plugin capabilities auto-discovered
    
    Example:
        User: "Find healthcare companies"
        Planner: "Need capability: company_discovery"
        Registry: "CompanyDiscoveryAgent provides that"
        Workflow: Execute CompanyDiscoveryAgent
    """
    
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        # Maps category to list of capability names
        self._by_category: Dict[str, Set[str]] = {
            category.value: set() for category in CapabilityCategory
        }
    
    def register(
        self,
        name: str,
        description: str,
        category: CapabilityCategory,
        agent_name: str,
        required_tools: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Register a capability."""
        
        if name in self._capabilities:
            # Allow override for plugin capabilities
            print(f"⚠️  Overriding capability: {name}")
        
        capability = Capability(
            name=name,
            description=description,
            category=category,
            agent_name=agent_name,
            required_tools=required_tools,
            metadata=metadata
        )
        
        self._capabilities[name] = capability
        self._by_category[category.value].add(name)
        
        print(f"🎯 Registered capability: {name} → {agent_name}")
    
    def get_agent_for_capability(self, capability_name: str) -> Optional[str]:
        """Get the agent name that provides a capability."""
        capability = self._capabilities.get(capability_name)
        return capability.agent_name if capability else None
    
    def resolve(self, capability_name: str) -> Optional[str]:
        """Resolve a capability to its agent name. Alias for get_agent_for_capability."""
        return self.get_agent_for_capability(capability_name)
    
    def get_capability(self, capability_name: str) -> Optional[Capability]:
        """Get capability details."""
        return self._capabilities.get(capability_name)
    
    def list_capabilities(
        self,
        category: Optional[CapabilityCategory] = None
    ) -> List[Dict[str, Any]]:
        """List all capabilities, optionally filtered by category."""
        
        capabilities = self._capabilities.values()
        
        if category:
            capabilities = [c for c in capabilities if c.category == category]
        
        return [
            {
                "name": cap.name,
                "description": cap.description,
                "category": cap.category.value,
                "agent": cap.agent_name,
                "required_tools": cap.required_tools,
                "metadata": cap.metadata
            }
            for cap in capabilities
        ]
    
    def list_by_category(self, category: CapabilityCategory) -> List[str]:
        """List capability names by category."""
        return list(self._by_category.get(category.value, set()))
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if a capability is registered."""
        return capability_name in self._capabilities
    
    def unregister(self, capability_name: str) -> bool:
        """Unregister a capability."""
        if capability_name in self._capabilities:
            capability = self._capabilities[capability_name]
            self._by_category[capability.category.value].discard(capability_name)
            del self._capabilities[capability_name]
            print(f"❌ Unregistered capability: {capability_name}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all capabilities (for testing)."""
        self._capabilities.clear()
        for category_set in self._by_category.values():
            category_set.clear()


# Global registry instance
_registry = CapabilityRegistry()


def get_capability_registry() -> CapabilityRegistry:
    """Get the global capability registry instance."""
    return _registry
