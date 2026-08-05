# Core Lifecycle Interface
# ========================

"""
Core lifecycle interface - defines the contract for component lifecycle state transitions.

This interface does NOT implement the state machine itself, but defines the
behavioral contract that all lifecycle implementations must conform to.

ARCHITECTURAL PRINCIPLES:
- Represents a stable runtime boundary (not an organizational convenience)
- Defines HOW components transition between states, not WHAT they do
- State transitions are explicit and validated
"""

from typing import Protocol, Optional, List
from dataclasses import dataclass
from enum import Enum
import time


class LifecycleState(Enum):
    """
    Canonical lifecycle states for all runtime entities.
    
    Transitions must follow the defined state machine:
        CREATED -> INITIALIZING -> READY -> STARTING -> RUNNING <-> SUSPENDED
            -> STOPPING -> STOPPED
        
        Any state -> FAILED (on error)
    """
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    SUSPENDED = "suspended"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class LifecycleEvent:
    """
    A lifecycle state transition event.
    
    Used for observability and debugging lifecycle transitions.
    """
    timestamp_utc: float
    from_state: str
    to_state: str
    entity_id: str


class ILifecycleController(Protocol):
    """
    Controller interface for managing component lifecycle transitions.
    
    This is a BEHAVIORAL contract - implementations can use threading, async,
    or other mechanisms as long as they conform to the transition rules.
    
    INVARIANTS:
        1. State transitions must be validated before execution
        2. Failure state captures the exception cause
        3. Transitions are idempotent where appropriate
        4. Event history is maintained for debugging
    """
    
    @property
    def state(self) -> LifecycleState:
        """Get the current lifecycle state."""
        ...
    
    @property
    def failure_cause(self) -> Optional[Exception]:
        """Get the exception that caused a FAILED state, if any."""
        ...
    
    @property
    def events(self) -> List[LifecycleEvent]:
        """Get a copy of all lifecycle transition events."""
        ...
    
    async def initialize(self) -> None:
        """
        Transition from CREATED to INITIALIZING.
        
        Raises:
            LifecycleTransitionError: If transition is invalid
        """
        ...
    
    async def ready(self) -> None:
        """
        Transition from INITIALIZING to READY.
        
        Raises:
            LifecycleTransitionError: If transition is invalid
        """
        ...
    
    async def start(self) -> None:
        """
        Transition from READY through STARTING to RUNNING.
        
        Idempotent: calling multiple times has no additional effect.
        
        Raises:
            LifecycleTransitionError: If transition is invalid
        """
        ...
    
    async def stop(self) -> None:
        """
        Transition from RUNNING through STOPPING to STOPPED.
        
        Idempotent: can be called when already stopped.
        
        Raises:
            LifecycleTransitionError: If transition is invalid
        """
        ...
    
    async def shutdown(self) -> None:
        """
        Force transition to STOPPED regardless of current state.
        
        Used for emergency shutdown or cleanup operations.
        """
        ...
    
    async def suspend(self) -> None:
        """
        Transition from RUNNING to SUSPENDED.
        
        Component retains its state and can be resumed later.
        """
        ...
    
    async def resume(self) -> None:
        """
        Transition from SUSPENDED back to RUNNING.
        
        Resumes operation from the suspended state.
        """
        ...
    
    async def fail(self, cause: Exception) -> None:
        """
        Transition to FAILED state with preserved exception.
        
        Args:
            cause: The exception that caused the failure
        """
        ...


class IComponentLifecycle(Protocol):
    """
    Interface for components that have lifecycle management.
    
    Components implementing this interface provide lifecycle control
    through an internal controller.
    
    INVARIANT: Lifecycle methods delegate to a controller that validates
    and executes state transitions.
    """
    
    @property
    def entity_id(self) -> str:
        """Get the unique identifier for this component."""
        ...
    
    @property
    def lifecycle_state(self) -> LifecycleState:
        """Get the current lifecycle state of the component."""
        ...
    
    async def initialize(self) -> None:
        """
        Initialize the component.
        
        Transitions: CREATED -> INITIALIZING
        Must be called before start().
        """
        ...
    
    async def start(self) -> None:
        """
        Start the component.
        
        Transitions: READY -> STARTING -> RUNNING
        
        This method should NOT be overridden by subclasses. Override
        _do_start() for custom startup logic.
        """
        ...
    
    async def stop(self) -> None:
        """
        Stop the component.
        
        Transitions: RUNNING -> STOPPING -> STOPPED
        
        This method should NOT be overridden by subclasses. Override
        _do_stop() for custom shutdown logic.
        """
        ...
    
    async def shutdown(self) -> None:
        """
        Force shutdown regardless of current state.
        
        Used during application termination to ensure cleanup.
        """
        ...


class LifecycleTransitionError(Exception):
    """
    Raised when an invalid lifecycle transition is attempted.
    
    Args:
        message: Human-readable error description
        from_state: The current state before the failed transition
        to_state: The target state that was not allowed
    """
    
    def __init__(
        self,
        message: str,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
    ):
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state


# Valid transition graph (implementation detail)
_VALID_TRANSITIONS: dict = {
    LifecycleState.CREATED: [LifecycleState.INITIALIZING, LifecycleState.FAILED],
    LifecycleState.INITIALIZING: [LifecycleState.READY, LifecycleState.FAILED],
    LifecycleState.READY: [LifecycleState.STARTING, LifecycleState.STOPPED, LifecycleState.FAILED],
    LifecycleState.STARTING: [LifecycleState.RUNNING, LifecycleState.STOPPING, LifecycleState.FAILED],
    LifecycleState.RUNNING: [LifecycleState.SUSPENDED, LifecycleState.STOPPING, LifecycleState.FAILED],
    LifecycleState.SUSPENDED: [LifecycleState.RUNNING, LifecycleState.STOPPING, LifecycleState.FAILED],
    LifecycleState.STOPPING: [LifecycleState.STOPPED, LifecycleState.FAILED],
    LifecycleState.STOPPED: [LifecycleState.STARTING, LifecycleState.FAILED],  # Allow restart
    LifecycleState.FAILED: [],  # Terminal state - requires external recovery
}


__all__ = [
    "LifecycleState",
    "LifecycleEvent",
    "ILifecycleController",
    "IComponentLifecycle",
    "LifecycleTransitionError",
    "_VALID_TRANSITIONS",
]