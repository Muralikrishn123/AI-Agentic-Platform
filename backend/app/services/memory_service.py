from typing import Dict, Any, List, Optional
from datetime import datetime
from app.database.connection import get_database


class MemoryService:
    """
    Memory Service - Stores and retrieves workflow state and agent memory.
    
    This is NOT an agent - it's a storage service.
    Agents call this service to store/retrieve information.
    
    Responsibilities:
    - Store workflow state
    - Store agent outputs
    - Store conversation history
    - Retrieve context for agents
    
    Phase 1: MongoDB storage
    Phase 2: Vector database (ChromaDB) for semantic search
    """
    
    def __init__(self):
        pass
    
    async def store_workflow_state(
        self,
        workflow_id: str,
        step: str,
        data: Dict[str, Any]
    ) -> None:
        """Store workflow state for a specific step."""
        db = get_database()
        
        memory_entry = {
            "workflow_id": workflow_id,
            "step": step,
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
        await db.memory.insert_one(memory_entry)
    
    async def get_workflow_state(
        self,
        workflow_id: str,
        step: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get workflow state, optionally filtered by step."""
        db = get_database()
        
        query = {"workflow_id": workflow_id}
        if step:
            query["step"] = step
        
        cursor = db.memory.find(query).sort("timestamp", 1)
        memories = await cursor.to_list(length=None)
        
        for memory in memories:
            memory["_id"] = str(memory["_id"])
        
        return memories
    
    async def store_agent_output(
        self,
        workflow_id: str,
        agent_name: str,
        output: Dict[str, Any]
    ) -> None:
        """Store agent output for later retrieval."""
        db = get_database()
        
        memory_entry = {
            "workflow_id": workflow_id,
            "agent": agent_name,
            "output": output,
            "timestamp": datetime.utcnow()
        }
        
        await db.agent_memory.insert_one(memory_entry)
    
    async def get_agent_outputs(
        self,
        workflow_id: str,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get agent outputs, optionally filtered by agent name."""
        db = get_database()
        
        query = {"workflow_id": workflow_id}
        if agent_name:
            query["agent"] = agent_name
        
        cursor = db.agent_memory.find(query).sort("timestamp", 1)
        outputs = await cursor.to_list(length=None)
        
        for output in outputs:
            output["_id"] = str(output["_id"])
        
        return outputs
    
    async def store_conversation(
        self,
        workflow_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store conversation turn for context building."""
        db = get_database()
        
        conversation_entry = {
            "workflow_id": workflow_id,
            "role": role,  # "user", "assistant", "system"
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        }
        
        await db.conversations.insert_one(conversation_entry)
    
    async def get_conversation_history(
        self,
        workflow_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a workflow."""
        db = get_database()
        
        cursor = db.conversations.find({"workflow_id": workflow_id}).sort("timestamp", 1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        conversations = await cursor.to_list(length=None)
        
        for conv in conversations:
            conv["_id"] = str(conv["_id"])
        
        return conversations
    
    async def clear_workflow_memory(self, workflow_id: str) -> None:
        """Clear all memory for a workflow."""
        db = get_database()
        
        await db.memory.delete_many({"workflow_id": workflow_id})
        await db.agent_memory.delete_many({"workflow_id": workflow_id})
        await db.conversations.delete_many({"workflow_id": workflow_id})


# Global instance
_memory_service = MemoryService()


def get_memory_service() -> MemoryService:
    """Get the global memory service instance."""
    return _memory_service
