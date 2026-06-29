from typing import Dict, Optional, List, Any, Callable, Awaitable
from pydantic import BaseModel


class Tool(BaseModel):
    """Tool definition."""
    name: str
    description: str
    category: str  # e.g., "search", "database", "email", "crm"
    parameters: Dict[str, Any]
    
    class Config:
        arbitrary_types_allowed = True


class ToolRegistry:
    """
    Tool Registry - Central registry for all tools.
    
    Tools are capabilities that agents can use:
    - Search (web search, document search)
    - Database (query, insert, update)
    - Communication (email, slack, SMS)
    - CRM (Salesforce, HubSpot)
    - RAG (vector search, embeddings)
    
    Responsibilities:
    - Register tools
    - Get tool by name
    - List tools by category
    - Execute tool (via Tool Executor)
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._executors: Dict[str, Callable] = {}
    
    def register(
        self,
        name: str,
        description: str,
        category: str,
        parameters: Dict[str, Any],
        executor: Callable[..., Awaitable[Any]]
    ) -> None:
        """Register a tool in the registry."""
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered")
        
        tool = Tool(
            name=name,
            description=description,
            category=category,
            parameters=parameters
        )
        
        self._tools[name] = tool
        self._executors[name] = executor
        print(f"🔧 Registered tool: {name} (category: {category})")
    
    def unregister(self, tool_name: str) -> bool:
        """Unregister a tool from the registry."""
        if tool_name in self._tools:
            del self._tools[tool_name]
            del self._executors[tool_name]
            print(f"❌ Unregistered tool: {tool_name}")
            return True
        return False
    
    def get(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def get_executor(self, tool_name: str) -> Optional[Callable]:
        """Get a tool executor by name."""
        return self._executors.get(tool_name)
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered tools, optionally filtered by category."""
        tools = self._tools.values()
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "parameters": tool.parameters
            }
            for tool in tools
        ]
    
    def list_categories(self) -> List[str]:
        """List all tool categories."""
        return list(set(tool.category for tool in self._tools.values()))
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools
    
    async def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool with given parameters."""
        if tool_name not in self._executors:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        executor = self._executors[tool_name]
        return await executor(**kwargs)
    
    def clear(self) -> None:
        """Clear all registered tools (for testing)."""
        self._tools.clear()
        self._executors.clear()


# Global registry instance
_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _registry
