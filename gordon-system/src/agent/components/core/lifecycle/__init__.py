# Core Lifecycle Management
# ==========================

"""
Core runtime lifecycle management.

Implements explicit lifecycle transitions with validation and observability.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
import threading
from enum import Enum

from ..contracts import LifecycleState, LifecycleEntity
from ..types import Timestamp, EntityId, LifecycleEvent
from ..exceptions import LifecycleError


# Valid lifecycle transitions
TRANSITIONS: Dict[LifecycleState, List[LifecycleState]] = {
    LifecycleState.CREATED: [
        LifecycleState.INITIALIZING,
        LifecycleState.FAILED,
    ],
    LifecycleState.INITIALIZING: [
        LifecycleState.READY,
        LifecycleState.FAILED,
    ],
    LifecycleState.READY: [
        LifecycleState.STARTING,
        LifecycleState.STOPPED,
        LifecycleState.FAILED,
    ],
    LifecycleState.STARTING: [
        LifecycleState.RUNNING,
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    ],
    LifecycleState.RUNNING: [
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    ],
    LifecycleState.STOPPING: [
        LifecycleState.STOPPED,
        LifecycleState.FAILED,
    ],
    LifecycleState.STOPPED: [
        LifecycleState.STARTING,  # Allow restart
        LifecycleState.FAILED,
    ],
    LifecycleState.FAILED: [],  # Terminal state
}


class LifecycleController:
    """
    Controller for managing lifecycle transitions.
    
    Provides:
    - State validation before transition
    - Event logging for transitions
    - Idempotent operations where appropriate
    - Failure cause preservation
    """
    
    def __init__(self, entity_id: EntityId) -> None:
        self._entity_id = entity_id
        self._state = LifecycleState.CREATED
        self._lock = threading.Lock()
        self._events: List[LifecycleEvent] = []
        self._failure_cause: Optional[Exception] = None
    
    @property
    def state(self) -> LifecycleState:
        """Return current lifecycle state."""
        with self._lock:
            return self._state
    
    @property
    def failure_cause(self) -> Optional[Exception]:
        """Return the failure cause if in FAILED state."""
        with self._lock:
            return self._failure_cause
    
    @property
    def events(self) -> List[LifecycleEvent]:
        """Return a copy of lifecycle event history."""
        with self._lock:
            return list(self._events)
    
    def _record_event(self, from_state: LifecycleState, to_state: LifecycleState) -> None:
        """Record a lifecycle transition event."""
        event = LifecycleEvent(
            timestamp=Timestamp.now(),
            from_state=from_state.value,
            to_state=to_state.value,
            entity_id=self._entity_id.value
        )
        with self._lock:
            self._events.append(event)
    
    def _validate_transition(self, target: LifecycleState) -> None:
        """Validate that a transition to the target state is allowed."""
        current = self.state
        
        # Idempotent operations - same state is always valid
        if current == target:
            return
        
        with self._lock:
            allowed = TRANSITIONS.get(current, [])
        
        if target not in allowed:
            raise LifecycleError(
                f"Invalid transition from {current.value} to {target.value}",
                from_state=current.value,
                to_state=target.value
            )
    
    async def initialize(self) -> None:
        """Transition from CREATED to INITIALIZING."""
        with self._lock:
            current = self._state
        
        if current != LifecycleState.CREATED:
            raise LifecycleError(
                f"Cannot initialize: already in {current.value}",
                from_state=current.value,
                to_state=LifecycleState.INITIALIZING.value
            )
        
        try:
            self._validate_transition(LifecycleState.INITIALIZING)
            
            with self._lock:
                old = self._state
                self._state = LifecycleState.INITIALIZING
            
            self._record_event(old, self._state)
            
        except Exception as e:
            await self._fail(e)
    
    async def ready(self) -> None:
        """Transition from INITIALIZING to READY."""
        with self._lock:
            current = self._state
        
        if current != LifecycleState.INITIALIZING:
            raise LifecycleError(
                f"Cannot become ready: not initializing (current: {current.value})",
                from_state=current.value,
                to_state=LifecycleState.READY.value
            )
        
        try:
            with self._lock:
                old = self._state
                self._state = LifecycleState.READY
            
            self._record_event(old, self._state)
            
        except Exception as e:
            await self._fail(e)
    
    async def start(self) -> None:
        """Transition from READY to STARTING, then to RUNNING."""
        with self._lock:
            current = self._state
        
        if current != LifecycleState.READY:
            raise LifecycleError(
                f"Cannot start: not ready (current: {current.value})",
                from_state=current.value,
                to_state=LifecycleState.STARTING.value
            )
        
        try:
            with self._lock:
                old = self._state
                self._state = LifecycleState.STARTING
            
            self._record_event(old, self._state)
            
            # Transition to RUNNING
            with self._lock:
                old = self._state
                self._state = LifecycleState.RUNNING
            
            self._record_event(old, self._state)
            
        except Exception as e:
            await self._fail(e)
    
    async def stop(self) -> None:
        """Transition from RUNNING to STOPPING, then to STOPPED."""
        with self._lock:
            current = self._state
        
        # Idempotent: can stop multiple times safely
        if current == LifecycleState.STOPPED:
            return
        
        if current not in (LifecycleState.RUNNING, LifecycleState.STARTING):
            raise LifecycleError(
                f"Cannot stop: not running (current: {current.value})",
                from_state=current.value,
                to_state=LifecycleState.STOPPING.value
            )
        
        try:
            with self._lock:
                old = self._state
                self._state = LifecycleState.STOPPING
            
            self._record_event(old, self._state)
            
            # Transition to STOPPED
            with self._lock:
                old = self._state
                self._state = LifecycleState.STOPPED
            
            self._record_event(old, self._state)
            
        except Exception as e:
            await self._fail(e)
    
    async def shutdown(self) -> None:
        """Transition to STOPPED regardless of current state."""
        with self._lock:
            current = self._state
        
        if current == LifecycleState.STOPPED:
            return
        
        try:
            target = (
                LifecycleState.STOPPED
                if current in (LifecycleState.RUNNING, LifecycleState.STARTING)
                else LifecycleState.STOPPED  # Direct to stopped for non-running states
            )
            
            with self._lock:
                old = self._state
                self._state = target
            
            self._record_event(old, self._state)
            
        except Exception as e:
            await self._fail(e)
    
    async def _fail(self, cause: Exception) -> None:
        """Transition to FAILED state with preserved cause."""
        with self._lock:
            current = self._state
        
        try:
            with self._lock:
                old = self._state
                self._state = LifecycleState.FAILED
                self._failure_cause = cause
            
            self._record_event(old, self._state)
            
        except Exception:
            # If recording fails, we're still in FAILED state
            pass


class EntityWithLifecycle:
    """
    Base class for entities with lifecycle management.
    
    Usage:
        class MyService(EntityWithLifecycle):
            async def _do_start(self) -> None:
                # Implementation
                pass
            
            async def _do_stop(self) -> None:
                # Implementation
                pass
    """
    
    def __init__(self, entity_id: Optional[EntityId] = None) -> None:
        import uuid as uuid_module
        self._entity_id = entity_id or EntityId(str(uuid_module.uuid4()))
        self._controller = LifecycleController(self._entity_id)
        self._running_tasks: List["asyncio.Task"] = []
    
    @property
    def state(self) -> LifecycleState:
        return self._controller.state
    
    @property
    def entity_id(self) -> EntityId:
        return self._entity_id
    
    async def initialize(self) -> None:
        await self._controller.initialize()
    
    async def start(self) -> None:
        if self.state == LifecycleState.RUNNING:
            return  # Idempotent
        
        await self._controller.start()
    
    async def stop(self) -> None:
        await self._controller.stop()
    
    async def shutdown(self) -> None:
        await self._controller.shutdown()


__all__ = [
    "TRANSITIONS",
    "LifecycleController",
    "EntityWithLifecycle",
]