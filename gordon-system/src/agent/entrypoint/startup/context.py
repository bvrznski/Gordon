"""Gordon Agent Startup Context.

Phase 3.7.33-I: Agent Startup Coordination
==========================================

Operation-scoped context for a single startup transaction.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple


@dataclass(frozen=True)
class AgentStartupContext:
    """Operation-scoped context for a single startup transaction.
    
    This context is created at the start of each startup and contains
    all necessary state for that specific startup operation. It must not
    be shared across different startup transactions.
    
    The context provides:
        - Deterministic identity for this startup
        - Operation-scoped clock for timing operations
        - Diagnostics access for event publication
        - Validation helpers
    
    Architecture boundaries:
        This owns:
            - Context identity (context_id)
            - Startup identity binding
            - Clock access for timing
            - Diagnostic access
        
        This does NOT own:
            - Runtime resources
            - Component instances
            - Mutable registries
            - Active event loops
    """
    
    context_id: str
    """Unique identifier for this startup context."""
    
    startup_id: str
    """Startup operation ID (same as request startup_id)."""
    
    launch_id: str
    """Launch session ID from the original launch request."""
    
    process_id: int
    """Process ID where startup is occurring."""
    
    start_time_ns: int
    """Start time in nanoseconds for timing operations."""
    
    current_phase: AgentStartupPhase
    """Current startup phase."""
    
    completed_phases: Tuple[AgentStartupPhase, ...]
    """Phases that have been successfully completed."""
    
    pending_phases: Tuple[AgentStartupPhase, ...]
    """Phases remaining in the sequence."""
    
    # Operation-scoped clock (injectable for testing)
    _clock_ns: Callable[[], int] = field(default_factory=lambda: time.time_ns)
    
    @property
    def elapsed_seconds(self) -> float:
        """Return elapsed time since startup started."""
        return (self._clock_ns() - self.start_time_ns) / 1_000_000_000.0
    
    @classmethod
    def create(
        cls,
        startup_id: str,
        launch_id: str,
        process_id: int,
    ) -> "AgentStartupContext":
        """Create a new startup context.
        
        Args:
            startup_id: Startup operation ID from the request
            launch_id: Launch session ID from the original launch request
            process_id: Process ID where startup is occurring
            
        Returns:
            New AgentStartupContext in CREATED state
        """
        now_ns = time.time_ns()
        
        return cls(
            context_id=str(uuid.uuid4()),
            startup_id=startup_id,
            launch_id=launch_id,
            process_id=process_id,
            start_time_ns=now_ns,
            current_phase=AgentStartupPhase.CREATED,
            completed_phases=(),
            pending_phases=AgentStartupPhase.ALL[1:],  # All phases except CREATED
            _clock_ns=lambda: time.time_ns(),
        )
    
    def enter_phase(self, new_phase: AgentStartupPhase) -> "AgentStartupContext":
        """Enter a new startup phase.
        
        Validates that the transition is allowed and returns a new context.
        
        Args:
            new_phase: The phase to enter
            
        Returns:
            New AgentStartupContext with updated phase state
        """
        current = self.current_phase
        
        # Define valid transitions (deterministic)
        valid_transitions: Dict[AgentStartupPhase, Tuple[AgentStartupPhase, ...]] = {
            AgentStartupPhase.CREATED: (
                AgentStartupPhase.VALIDATING_REQUEST,
            ),
            AgentStartupPhase.VALIDATING_REQUEST: (
                AgentStartupPhase.RESOLVING_POLICY,
                AgentStartupPhase.FAILED,
                AgentStartupPhase.BLOCKED,
            ),
            AgentStartupPhase.RESOLVING_POLICY: (
                AgentStartupPhase.PREPARING_CONTEXT,
            ),
            AgentStartupPhase.PREPARING_CONTEXT: (
                AgentStartupPhase.PREPARING_PREFLIGHT_REQUEST,
            ),
            AgentStartupPhase.PREPARING_PREFLIGHT_REQUEST: (
                AgentStartupPhase.INVOKING_PREFLIGHT,
            ),
            AgentStartupPhase.INVOKING_PREFLIGHT: (
                AgentStartupPhase.VALIDATING_PREFLIGHT,
                AgentStartupPhase.CANCELLING,
                AgentStartupPhase.TIMED_OUT,
            ),
            AgentStartupPhase.VALIDATING_PREFLIGHT: (
                AgentStartupPhase.PREPARING_INITIALIZATION_REQUEST,
                AgentStartupPhase.BLOCKED,
                AgentStartupPhase.FAILED,
                AgentStartupPhase.CANCELLED,
            ),
            AgentStartupPhase.PREPARING_INITIALIZATION_REQUEST: (
                AgentStartupPhase.INVOKING_INITIALIZATION,
            ),
            AgentStartupPhase.INVOKING_INITIALIZATION: (
                AgentStartupPhase.VALIDATING_INITIALIZATION,
                AgentStartupPhase.CANCELLING,
                AgentStartupPhase.TIMED_OUT,
            ),
            AgentStartupPhase.VALIDATING_INITIALIZATION: (
                AgentStartupPhase.TRANSFERRING_OWNERSHIP,
                AgentStartupPhase.BLOCKED,
                AgentStartupPhase.FAILED,
                AgentStartupPhase.REQUESTING_ROLLBACK,
                AgentStartupPhase.CANCELLED,
            ),
            AgentStartupPhase.TRANSFERRING_OWNERSHIP: (
                AgentStartupPhase.VERIFYING_HANDOFF,
                AgentStartupPhase.FAILED,
            ),
            AgentStartupPhase.VERIFYING_HANDOFF: (
                AgentStartupPhase.COMPLETED,
                AgentStartupPhase.BLOCKED,
                AgentStartupPhase.FAILED,
            ),
            AgentStartupPhase.COMPLETED: (),  # Terminal state
            AgentStartupPhase.BLOCKED: (),  # Terminal state
            AgentStartupPhase.CANCELLING: (
                AgentStartupPhase.CANCELLED,
                AgentStartupPhase.FAILED,
            ),
            AgentStartupPhase.REQUESTING_ROLLBACK: (
                AgentStartupPhase.COMPLETED,  # Rollback completed, but failed
                AgentStartupPhase.FAILED,
            ),
            AgentStartupPhase.REQUESTING_SHUTDOWN: (),  # Shutdown in progress
            AgentStartupPhase.CANCELLED: (),  # Terminal state
            AgentStartupPhase.TIMED_OUT: (),  # Terminal state
            AgentStartupPhase.FAILED: (),  # Terminal state
        }
        
        valid_next = valid_transitions.get(current, ())
        
        if new_phase not in valid_next and new_phase != current:
            raise ValueError(
                f"Invalid phase transition from {current} to {new_phase}"
            )
        
        # Update completed and pending phases
        completed = tuple(set(self.completed_phases) | {current})
        pending_list = list(self.pending_phases)
        if current in pending_list:
            pending_list.remove(current)
        if new_phase not in completed and new_phase not in pending_list:
            pending_list.insert(0, new_phase)
        
        return dataclass_replace(
            self,
            current_phase=new_phase,
            completed_phases=completed,
            pending_phases=tuple(pending_list),
        )
    
    def cancel(self) -> "AgentStartupContext":
        """Return context for cancellation.
        
        Returns:
            New AgentStartupContext with CANCELLING phase
        """
        return self.enter_phase(AgentStartupPhase.CANCELLING)
    
    def rollback(self) -> "AgentStartupContext":
        """Return context for rollback.
        
        Returns:
            New AgentStartupContext with REQUESTING_ROLLBACK phase
        """
        return self.enter_phase(AgentStartupPhase.REQUESTING_ROLLBACK)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace that handles frozen dataclasses.
    
    Since our dataclasses are @dataclass(frozen=True), we need a way to create
    modified copies. This uses the underlying __dict__ to create new instances.
    """
    import copy
    
    cls = type(instance)
    new_dict = copy.copy(instance.__dict__)
    new_dict.update(kwargs)
    
    return cls(**new_dict)


# =============================================================================
# STARTUP PHASE ENUM (defined separately for cross-module imports)
# =============================================================================

class AgentStartupPhase:
    """Canonical startup phase enumeration.
    
    Defines the deterministic startup sequence:
        CREATED -> VALIDATING_REQUEST -> RESOLVING_POLICY
        -> PREPARING_CONTEXT -> PREPARING_PREFLIGHT_REQUEST -> INVOKING_PREFLIGHT
        -> VALIDATING_PREFLIGHT -> PREPARING_INITIALIZATION_REQUEST
        -> INVOKING_INITIALIZATION -> VALIDATING_INITIALIZATION
        -> TRANSFERRING_OWNERSHIP -> VERIFYING_HANDOFF -> COMPLETED
        
    Invalid transitions must be rejected and diagnosed.
    
    Terminal states:
        - COMPLETED: Successful startup
        - BLOCKED: Preflight blocked startup
        - CANCELLED: Startup was cancelled
        - TIMED_OUT: Startup exceeded deadline
        - FAILED: Startup failed with an error
    """
    
    # Initial state
    CREATED = "created"
    
    # Request validation phase
    VALIDATING_REQUEST = "validating_request"
    
    # Policy resolution phase
    RESOLVING_POLICY = "resolving_policy"
    
    # Context preparation phase
    PREPARING_CONTEXT = "preparing_context"
    
    # Preflight phases
    PREPARING_PREFLIGHT_REQUEST = "preparing_preflight_request"
    INVOKING_PREFLIGHT = "invoking_preflight"
    VALIDATING_PREFLIGHT = "validating_preflight"
    
    # Initialization phases
    PREPARING_INITIALIZATION_REQUEST = "preparing_initialization_request"
    INVOKING_INITIALIZATION = "invoking_initialization"
    VALIDATING_INITIALIZATION = "validating_initialization"
    
    # Handoff phases
    TRANSFERRING_OWNERSHIP = "transferring_ownership"
    VERIFYING_HANDOFF = "verifying_handoff"
    
    # Terminal states
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLING = "cancelling"
    REQUESTING_ROLLBACK = "requesting_rollback"
    REQUESTING_SHUTDOWN = "requesting_shutdown"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    FAILED = "failed"
    
    # All phases as a tuple for iteration
    ALL = (
        CREATED,
        VALIDATING_REQUEST,
        RESOLVING_POLICY,
        PREPARING_CONTEXT,
        PREPARING_PREFLIGHT_REQUEST,
        INVOKING_PREFLIGHT,
        VALIDATING_PREFLIGHT,
        PREPARING_INITIALIZATION_REQUEST,
        INVOKING_INITIALIZATION,
        VALIDATING_INITIALIZATION,
        TRANSFERRING_OWNERSHIP,
        VERIFYING_HANDOFF,
        COMPLETED,
        BLOCKED,
        CANCELLING,
        REQUESTING_ROLLBACK,
        REQUESTING_SHUTDOWN,
        CANCELLED,
        TIMED_OUT,
        FAILED,
    )
    
    @classmethod
    def is_terminal(cls, phase: str) -> bool:
        """Check if a phase is terminal (cannot transition further)."""
        return phase in (
            cls.COMPLETED,
            cls.BLOCKED,
            cls.CANCELLED,
            cls.TIMED_OUT,
            cls.FAILED,
        )
    
    @classmethod
    def success_phases(cls) -> Tuple[str, ...]:
        """Return phases that indicate successful startup."""
        return (cls.COMPLETED,)
    
    @classmethod
    def failure_phases(cls) -> Tuple[str, ...]:
        """Return phases that indicate failed startup."""
        return (
            cls.BLOCKED,
            cls.CANCELLED,
            cls.TIMED_OUT,
            cls.FAILED,
        )