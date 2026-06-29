from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class AgentContext(BaseModel):
    """Context passed between agents."""
    workflow_id: str
    user_request: str
    current_step: str
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Standard response from agents."""
    success: bool
    data: Dict[str, Any] = {}
    error: Optional[str] = None
    confidence: float = 1.0
    next_step: Optional[str] = None


class Agent(ABC):
    """Base interface for all agents."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResponse:
        """Execute the agent's logic."""
        pass
    
    async def validate_input(self, context: AgentContext) -> bool:
        """Validate input context."""
        return True
    
    async def log_execution(self, context: AgentContext, response: AgentResponse):
        """Log agent execution."""
        # Will be implemented by logging service
        pass


class Plugin(ABC):
    """Base interface for all plugins."""
    
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.enabled = True
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResponse:
        """Execute the plugin's logic."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return plugin capabilities and requirements."""
        pass
    
    async def initialize(self):
        """Initialize plugin resources."""
        pass
    
    async def cleanup(self):
        """Clean up plugin resources."""
        pass
