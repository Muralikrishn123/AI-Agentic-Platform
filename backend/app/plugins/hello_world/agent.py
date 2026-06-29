"""
HelloWorld Agent - Simple agent for testing platform architecture.
"""

from typing import Dict, Any
from app.core.interfaces import Agent, AgentContext, AgentResponse


class HelloWorldAgent(Agent):
    """
    HelloWorld Agent - Returns a simple greeting.
    
    This agent validates that:
    - Agent registration works
    - Agent execution works
    - Context passing works
    - Response format works
    """
    
    def __init__(self):
        super().__init__("HelloWorldAgent")
        self.description = "A simple agent that says hello"
        self.capabilities = ["hello_world"]
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """
        Execute the HelloWorld agent.
        
        Args:
            context: Agent execution context with user request
            
        Returns:
            AgentResponse with greeting message
        """
        
        # Extract user name from context data if provided
        user_name = context.data.get("user_name", "World")
        
        # Create greeting message
        message = f"Hello {user_name} from the Agentic AI Platform!"
        
        # Return response
        return AgentResponse(
            success=True,
            data={
                "greeting": message,
                "agent": self.name,
                "capability": "hello_world",
                "platform_version": "3.0",
                "user_request": context.user_request
            },
            confidence=1.0
        )
