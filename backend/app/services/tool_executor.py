from typing import Any, Dict, Optional
from app.services.tool_registry import get_tool_registry


class ToolExecutor:
    """
    Tool Executor - Executes tools registered in the Tool Registry.
    
    Agents never call tools directly.
    They ask the Tool Executor to run a tool.
    
    Benefits:
    - Centralized execution
    - Logging and monitoring
    - Error handling
    - Rate limiting (future)
    - Caching (future)
    
    Responsibilities:
    - Execute registered tools
    - Handle tool errors
    - Log tool executions
    - Return results to agents
    """
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
    
    async def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        
        # Check if tool exists
        if not self.tool_registry.has_tool(tool_name):
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found in registry",
                "result": None
            }
        
        try:
            # Log execution (for monitoring)
            print(f"🔧 Executing tool: {tool_name}")
            if workflow_id:
                print(f"   Workflow: {workflow_id}")
            
            # Execute the tool
            result = await self.tool_registry.execute(tool_name, **parameters)
            
            return {
                "success": True,
                "error": None,
                "result": result
            }
        
        except Exception as e:
            print(f"❌ Tool execution failed: {tool_name} - {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    async def execute_multiple(
        self,
        tools: list[Dict[str, Any]],
        workflow_id: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """Execute multiple tools in sequence."""
        
        results = []
        for tool_spec in tools:
            tool_name = tool_spec.get("tool")
            parameters = tool_spec.get("parameters", {})
            
            result = await self.execute(
                tool_name=tool_name,
                parameters=parameters,
                workflow_id=workflow_id
            )
            results.append(result)
        
        return results


# Global instance
_tool_executor = ToolExecutor()


def get_tool_executor() -> ToolExecutor:
    """Get the global tool executor instance."""
    return _tool_executor
