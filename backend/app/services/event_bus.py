from typing import Dict, List, Callable, Any, Awaitable, Optional
from enum import Enum
from datetime import datetime
import asyncio


class EventType(str, Enum):
    """Standard platform events."""
    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    
    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    
    # Plugin events
    PLUGIN_INSTALLED = "plugin.installed"
    PLUGIN_ENABLED = "plugin.enabled"
    PLUGIN_DISABLED = "plugin.disabled"
    PLUGIN_UNINSTALLED = "plugin.uninstalled"
    
    # Tool events
    TOOL_EXECUTED = "tool.executed"
    TOOL_FAILED = "tool.failed"
    
    # System events
    SYSTEM_READY = "system.ready"
    SYSTEM_SHUTDOWN = "system.shutdown"


class Event:
    """Represents an event in the system."""
    
    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str = "system",
        metadata: Dict[str, Any] = None
    ):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.event_id = f"{event_type.value}_{datetime.utcnow().timestamp()}"


class EventBus:
    """
    Event Bus - Decouples components through event-driven architecture.
    
    Instead of:
        Component A → directly calls → Component B
    
    We have:
        Component A → emits event → Event Bus → notifies → Component B
    
    Benefits:
    - Components don't need to know about each other
    - Easy to add new event listeners
    - Asynchronous processing
    - Better scalability
    - Event logging and monitoring
    
    Example:
        # Emit event
        await event_bus.emit(EventType.WORKFLOW_COMPLETED, {
            "workflow_id": "123",
            "status": "success"
        })
        
        # Listen for event
        async def on_workflow_complete(event: Event):
            print(f"Workflow {event.data['workflow_id']} completed!")
        
        event_bus.subscribe(EventType.WORKFLOW_COMPLETED, on_workflow_complete)
    """
    
    def __init__(self):
        # Maps event type to list of subscribers
        self._subscribers: Dict[str, List[Callable]] = {}
        
        # Event history for debugging
        self._history: List[Event] = []
        self._max_history = 1000
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], Awaitable[None]]
    ) -> None:
        """Subscribe to an event type."""
        
        if event_type.value not in self._subscribers:
            self._subscribers[event_type.value] = []
        
        self._subscribers[event_type.value].append(handler)
        print(f"📡 Subscribed to {event_type.value}")
    
    def unsubscribe(
        self,
        event_type: EventType,
        handler: Callable
    ) -> bool:
        """Unsubscribe from an event type."""
        
        if event_type.value in self._subscribers:
            try:
                self._subscribers[event_type.value].remove(handler)
                print(f"📡 Unsubscribed from {event_type.value}")
                return True
            except ValueError:
                pass
        
        return False
    
    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str = "system",
        metadata: Dict[str, Any] = None
    ) -> None:
        """Emit an event to all subscribers."""
        
        event = Event(
            event_type=event_type,
            data=data,
            source=source,
            metadata=metadata
        )
        
        # Add to history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # Notify subscribers
        subscribers = self._subscribers.get(event_type.value, [])
        
        if subscribers:
            # Run all handlers concurrently
            await asyncio.gather(
                *[handler(event) for handler in subscribers],
                return_exceptions=True  # Don't let one handler failure stop others
            )
            
            print(f"📤 Emitted {event_type.value} to {len(subscribers)} subscribers")
        else:
            print(f"📤 Emitted {event_type.value} (no subscribers)")
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history, optionally filtered by type."""
        
        events = self._history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get number of subscribers for an event type."""
        return len(self._subscribers.get(event_type.value, []))
    
    def list_event_types(self) -> List[str]:
        """List all event types that have subscribers."""
        return list(self._subscribers.keys())


# Global instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus
