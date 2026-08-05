"""Gordon Agent Shutdown Context.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination
======================================================

Operation-scoped context for a single shutdown transaction.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, Optional, Tuple


# =============================================================================
# SHUTDOWN PHASE MODEL
# =============================================================================


class AgentShutdownPhase(Enum):
    """Canonical shutdown phase enumeration.
    
    Defines the deterministic shutdown sequence:
        CREATED -> VALIDATING_REQUEST -> RESOLVING_POLICY
        -> PREPARING_CONTEXT -> VALIDATING_RUNTIME_IDENTITY
        -> VALIDATING_OWNERSHIP -> FENCING_DUPLICATE_SHUTDOWN
        -> PREPARING_CORE_REQUEST -> INVOKING_GRACEFUL_SHUTDOWN
        -> VALIDATING_GRACEFUL_RESULT -> ESCALATING_TO_FORCED
        -> INVOKING_FORCED_SHUTDOWN -> VALIDATING_FORCED_RESULT
        -> VERIFYING_TERMINAL_STATE -> AGGREGATING_RESULT -> COMPLETED
        
    Invalid transitions must be rejected.
    
    Terminal states:
        - COMPLETED: Successful shutdown
        - FAILED: Shutdown failed with an error
        - CANCELLED: Shutdown was cancelled
        - TIMED_OUT: Shutdown exceeded deadline
        - ALREADY_TERMINAL: Runtime already in terminal state
        - INVALID_RUNTIME: Invalid runtime identity or ownership
    """
    
    # Initial states
    CREATED = "created"
    VALIDATING_REQUEST = "validating_request"
    RESOLVING_POLICY = "resolving_policy"
    PREPARING_CONTEXT = "preparing_context"
    
    # Runtime validation phases
    VALIDATING_RUNTIME_IDENTITY = "validating_runtime_identity"
    VALIDATING_OWNERSHIP = "validating_ownership"
    FENCING_DUPLICATE_SHUTDOWN = "fencing_duplicate_shutdown"
    
    # Core shutdown preparation
    PREPARING_CORE_REQUEST = "preparing_core_request"
    
    # Graceful and forced phases
    INVOKING_GRACEFUL_SHUTDOWN = "invoking_graceful_shutdown"
    VALIDATING_GRACEFUL_RESULT = "validating_graceful_result"
    ESCALATING_TO_FORCED = "escalating_to_forced"
    INVOKING_FORCED_SHUTDOWN = "invoking_forced_shutdown"
    VALIDATING_FORCED_RESULT = "validating_forced_result"
    
    # Terminal verification
    VERIFYING_TERMINAL_STATE = "verifying_terminal_state"
    AGGREGATING_RESULT = "aggregating_result"
    
    # Terminal states
    COMPLETED = "completed"
    COMPLETED_WITH_RESIDUALS = "completed_with_residuals"
    ALREADY_TERMINAL = "already_terminal"
    CANCELLING = "cancelling"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    INVALID_RUNTIME = "invalid_runtime"


# =============================================================================
# SHUTDOWN CONTEXT
# =============================================================================


@dataclass(frozen=True)
class AgentShutdownContext:
    """Operation-scoped context for a single shutdown transaction.
    
    This context is created at the start of each shutdown and contains
    all necessary state for that specific shutdown operation. It must not
    be shared across different shutdown transactions.
    
    Architecture boundaries:
        This owns:
            - Context identity (context_id)
            - Shutdown execution identity
            - Clock access for timing operations
            - Phase tracking
        
        This does NOT own:
            - Runtime resources
            - Component instances
            - Mutable registries
            - Active event loops
    """
    
    context_id: str
    """Unique identifier for this shutdown context."""
    
    shutdown_execution_id: str
    """Execution ID for this coordinator run."""
    
    intent_id: str
    """Intent ID from the original request."""
    
    runtime_id: str
    """Runtime being shut down."""
    
    boot_session_id: str
    """Boot session for this runtime."""
    
    start_time_ns: int
    """Start time in nanoseconds for timing operations."""
    
    current_phase: AgentShutdownPhase
    """Current shutdown phase."""
    
    completed_phases: Tuple[AgentShutdownPhase, ...]
    """Phases that have been successfully completed."""
    
    pending_phases: Tuple[AgentShutdownPhase, ...]
    """Phases remaining in the sequence."""
    
    # Operation-scoped clock (injectable for testing)
    _clock_ns: Callable[[], int] = field(default_factory=lambda: time.time_ns)
    
    @property
    def elapsed_seconds(self) -> float:
        """Return elapsed time since shutdown started."""
        return (self._clock_ns() - self.start_time_ns) / 1_000_000_000.0
    
    @classmethod
    def create(
        cls,
        shutdown_execution_id: str,
        intent_id: str,
        runtime_id: str,
        boot_session_id: str,
    ) -> "AgentShutdownContext":
        """Create a new shutdown context.
        
        Args:
            shutdown_execution_id: Execution ID for this coordinator run
            intent_id: Intent ID from the original request
            runtime_id: Runtime being shut down
            boot_session_id: Boot session for this runtime
            
        Returns:
            New AgentShutdownContext in CREATED state
        """
        now_ns = time.time_ns()
        
        return cls(
            context_id=str(uuid.uuid4()),
            shutdown_execution_id=shutdown_execution_id,
            intent_id=intent_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            start_time_ns=now_ns,
            current_phase=AgentShutdownPhase.CREATED,
            completed_phases=(),
            pending_phases=tuple(AgentShutdownPhase)[1:],  # All phases except CREATED
            _clock_ns=lambda: time.time_ns(),
        )
    
    def enter_phase(self, new_phase: AgentShutdownPhase) -> "AgentShutdownContext":
        """Enter a new shutdown phase.
        
        Validates that the transition is allowed and returns a new context.
        
        Args:
            new_phase: The phase to enter
            
        Returns:
            New AgentShutdownContext with updated phase state
        """
        current = self.current_phase
        
        # Define valid transitions (deterministic)
        valid_transitions: Dict[AgentShutdownPhase, Tuple[AgentShutdownPhase, ...]] = {
            AgentShutdownPhase.CREATED: (
                AgentShutdownPhase.VALIDATING_REQUEST,
            ),
            AgentShutdownPhase.VALIDATING_REQUEST: (
                AgentShutdownPhase.RESOLVING_POLICY,
                AgentShutdownPhase.FAILED,
                AgentShutdownPhase.INVALID_RUNTIME,
            ),
            AgentShutdownPhase.RESOLVING_POLICY: (
                AgentShutdownPhase.PREPARING_CONTEXT,
            ),
            AgentShutdownPhase.PREPARING_CONTEXT: (
                AgentShutdownPhase.VALIDATING_RUNTIME_IDENTITY,
            ),
            AgentShutdownPhase.VALIDATING_RUNTIME_IDENTITY: (
                AgentShutdownPhase.VALIDATING_OWNERSHIP,
                AgentShutdownPhase.INVALID_RUNTIME,
            ),
            AgentShutdownPhase.VALIDATING_OWNERSHIP: (
                AgentShutdownPhase.FENCING_DUPLICATE_SHUTDOWN,
                AgentShutdownPhase.INVALID_RUNTIME,
            ),
            AgentShutdownPhase.FENCING_DUPLICATE_SHUTDOWN: (
                AgentShutdownPhase.PREPARING_CORE_REQUEST,
                AgentShutdownPhase.ALREADY_TERMINAL,
                AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
            ),
            AgentShutdownPhase.PREPARING_CORE_REQUEST: (
                AgentShutdownPhase.INVOKING_GRACEFUL_SHUTDOWN,
            ),
            AgentShutdownPhase.INVOKING_GRACEFUL_SHUTDOWN: (
                AgentShutdownPhase.VALIDATING_GRACEFUL_RESULT,
                AgentShutdownPhase.ESCALATING_TO_FORCED,
                AgentShutdownPhase.CANCELLING,
                AgentShutdownPhase.TIMED_OUT,
            ),
            AgentShutdownPhase.VALIDATING_GRACEFUL_RESULT: (
                AgentShutdownPhase.COMPLETED,
                AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
                AgentShutdownPhase.ESCALATING_TO_FORCED,
                AgentShutdownPhase.FAILED,
            ),
            AgentShutdownPhase.ESCALATING_TO_FORCED: (
                AgentShutdownPhase.INVOKING_FORCED_SHUTDOWN,
                AgentShutdownPhase.FAILED,
            ),
            AgentShutdownPhase.INVOKING_FORCED_SHUTDOWN: (
                AgentShutdownPhase.VALIDATING_FORCED_RESULT,
                AgentShutdownPhase.CANCELLING,
                AgentShutdownPhase.TIMED_OUT,
            ),
            AgentShutdownPhase.VALIDATING_FORCED_RESULT: (
                AgentShutdownPhase.VERIFYING_TERMINAL_STATE,
                AgentShutdownPhase.FAILED,
            ),
            AgentShutdownPhase.VERIFYING_TERMINAL_STATE: (
                AgentShutdownPhase.AGGREGATING_RESULT,
                AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
                AgentShutdownPhase.FAILED,
            ),
            AgentShutdownPhase.AGGREGATING_RESULT: (
                AgentShutdownPhase.COMPLETED,
                AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
                AgentShutdownPhase.CANCELLED,
                AgentShutdownPhase.FAILED,
            ),
            # Terminal states
            AgentShutdownPhase.COMPLETED: (),
            AgentShutdownPhase.COMPLETED_WITH_RESIDUALS: (),
            AgentShutdownPhase.ALREADY_TERMINAL: (),
            AgentShutdownPhase.CANCELLING: (
                AgentShutdownPhase.CANCELLED,
                AgentShutdownPhase.FAILED,
            ),
            AgentShutdownPhase.FAILED: (),
            AgentShutdownPhase.CANCELLED: (),
            AgentShutdownPhase.TIMED_OUT: (),
            AgentShutdownPhase.INVALID_RUNTIME: (),
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
    
    def cancel(self) -> "AgentShutdownContext":
        """Return context for cancellation.
        
        Returns:
            New AgentShutdownContext with CANCELLING phase
        """
        return self.enter_phase(AgentShutdownPhase.CANCELLING)
    
    @property
    def is_terminal(self) -> bool:
        """Check if context is in a terminal phase."""
        return self.current_phase in (
            AgentShutdownPhase.COMPLETED,
            AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
            AgentShutdownPhase.ALREADY_TERMINAL,
            AgentShutdownPhase.CANCELLED,
            AgentShutdownPhase.TIMED_OUT,
            AgentShutdownPhase.FAILED,
            AgentShutdownPhase.INVALID_RUNTIME,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace that handles frozen dataclasses."""
    import copy
    
    cls = type(instance)
    new_dict = copy.copy(instance.__dict__)
    new_dict.update(kwargs)
    
    return cls(**new_dict)


# =============================================================================
# SHUTDOWN STATE MACHINE
# =============================================================================


class ShutdownStateMachine:
    """State machine for shutdown transaction.
    
    Ensures valid phase transitions and provides transition history.
    Used internally by the coordinator to track progress.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._state = AgentShutdownPhase.CREATED
        self._lock = None  # Simplified - no threading in this implementation
        self._transitions: list = []
    
    @property
    def state(self) -> AgentShutdownPhase:
        """Return current phase/state."""
        return self._state
    
    @property
    def is_terminal(self) -> bool:
        """Check if in a terminal state."""
        return self._state in (
            AgentShutdownPhase.COMPLETED,
            AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
            AgentShutdownPhase.ALREADY_TERMINAL,
            AgentShutdownPhase.CANCELLED,
            AgentShutdownPhase.TIMED_OUT,
            AgentShutdownPhase.FAILED,
            AgentShutdownPhase.INVALID_RUNTIME,
        )
    
    @property
    def transitions(self) -> list:
        """Return copy of transition history."""
        return list(self._transitions)
    
    def transition(
        self,
        to_state: AgentShutdownPhase,
        reason: Optional[str] = None,
    ) -> bool:
        """Attempt to transition to a new phase.
        
        Args:
            to_state: Target phase
            reason: Why transitioning (optional)
            
        Returns:
            True if transition succeeded, False otherwise
        """
        current = self._state
        
        # Idempotent - same state is always valid
        if current == to_state:
            return True
        
        # Check if valid transition
        valid = AgentShutdownPhaseTransitionRules.is_valid_transition(current, to_state)
        
        if not valid:
            return False
        
        self._transitions.append({
            "from": current,
            "to": to_state,
            "reason": reason,
            "timestamp_ns": time.time_ns(),
        })
        
        self._state = to_state
        return True
    
    def force_transition(self, to_state: AgentShutdownPhase) -> None:
        """Force a state transition regardless of validity.
        
        Used for emergency transitions.
        """
        old = self._state
        
        self._transitions.append({
            "from": old,
            "to": to_state,
            "reason": f"Force transition (emergency): {to_state.value}",
            "timestamp_ns": time.time_ns(),
            "forced": True,
        })
        
        self._state = to_state
    
    def snapshot(self) -> Dict[str, Any]:
        """Return immutable state snapshot."""
        return {
            "runtime_id": self._runtime_id,
            "current_phase": self.state.value,
            "transition_count": len(self._transitions),
            "is_terminal": self.is_terminal,
        }


class AgentShutdownPhaseTransitionRules:
    """Deterministic phase transition rules for shutdown.
    
    All valid transitions must be defined here to ensure
    deterministic behavior across the transaction.
    """
    
    VALID_TRANSITIONS = {
        AgentShutdownPhase.CREATED: (
            AgentShutdownPhase.VALIDATING_REQUEST,
        ),
        AgentShutdownPhase.VALIDATING_REQUEST: (
            AgentShutdownPhase.RESOLVING_POLICY,
            AgentShutdownPhase.FAILED,
            AgentShutdownPhase.INVALID_RUNTIME,
        ),
        AgentShutdownPhase.RESOLVING_POLICY: (
            AgentShutdownPhase.PREPARING_CONTEXT,
        ),
        AgentShutdownPhase.PREPARING_CONTEXT: (
            AgentShutdownPhase.VALIDATING_RUNTIME_IDENTITY,
        ),
        AgentShutdownPhase.VALIDATING_RUNTIME_IDENTITY: (
            AgentShutdownPhase.VALIDATING_OWNERSHIP,
            AgentShutdownPhase.INVALID_RUNTIME,
        ),
        AgentShutdownPhase.VALIDATING_OWNERSHIP: (
            AgentShutdownPhase.FENCING_DUPLICATE_SHUTDOWN,
            AgentShutdownPhase.INVALID_RUNTIME,
        ),
        AgentShutdownPhase.FENCING_DUPLICATE_SHUTDOWN: (
            AgentShutdownPhase.PREPARING_CORE_REQUEST,
            AgentShutdownPhase.ALREADY_TERMINAL,
            AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
        ),
        AgentShutdownPhase.PREPARING_CORE_REQUEST: (
            AgentShutdownPhase.INVOKING_GRACEFUL_SHUTDOWN,
        ),
        AgentShutdownPhase.INVOKING_GRACEFUL_SHUTDOWN: (
            AgentShutdownPhase.VALIDATING_GRACEFUL_RESULT,
            AgentShutdownPhase.ESCALATING_TO_FORCED,
            AgentShutdownPhase.CANCELLING,
            AgentShutdownPhase.TIMED_OUT,
        ),
        AgentShutdownPhase.VALIDATING_GRACEFUL_RESULT: (
            AgentShutdownPhase.COMPLETED,
            AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
            AgentShutdownPhase.ESCALATING_TO_FORCED,
            AgentShutdownPhase.FAILED,
        ),
        AgentShutdownPhase.ESCALATING_TO_FORCED: (
            AgentShutdownPhase.INVOKING_FORCED_SHUTDOWN,
            AgentShutdownPhase.FAILED,
        ),
        AgentShutdownPhase.INVOKING_FORCED_SHUTDOWN: (
            AgentShutdownPhase.VALIDATING_FORCED_RESULT,
            AgentShutdownPhase.CANCELLING,
            AgentShutdownPhase.TIMED_OUT,
        ),
        AgentShutdownPhase.VALIDATING_FORCED_RESULT: (
            AgentShutdownPhase.VERIFYING_TERMINAL_STATE,
            AgentShutdownPhase.FAILED,
        ),
        AgentShutdownPhase.VERIFYING_TERMINAL_STATE: (
            AgentShutdownPhase.AGGREGATING_RESULT,
            AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
            AgentShutdownPhase.FAILED,
        ),
        AgentShutdownPhase.AGGREGATING_RESULT: (
            AgentShutdownPhase.COMPLETED,
            AgentShutdownPhase.COMPLETED_WITH_RESIDUALS,
            AgentShutdownPhase.CANCELLED,
            AgentShutdownPhase.FAILED,
        ),
    }
    
    @classmethod
    def is_valid_transition(
        cls,
        from_phase: AgentShutdownPhase,
        to_phase: AgentShutdownPhase,
    ) -> bool:
        """Check if a transition is valid.
        
        Args:
            from_phase: Source phase
            to_phase: Target phase
            
        Returns:
            True if transition is valid, False otherwise
        """
        if from_phase == to_phase:
            return True
        
        valid_next = cls.VALID_TRANSITIONS.get(from_phase, ())
        return to_phase in valid_next