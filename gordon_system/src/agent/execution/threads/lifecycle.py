# Thread Lifecycle Model
# =======================

"""
Thread lifecycle state machine for semantic transitions.

This module defines the canonical lifecycle states and transitions for a Thread.
It uses Core's runtime state machines for actual execution management while
providing semantic lifecycle semantics.

Lifecycle States:
    CREATED: Thread artifact exists, not yet queued for behavior
    ACTIVE: Thread is actively engaged in semantic activity (has active Loop)
    SUSPENDED: Behavioral progression paused, identity preserved
    AWAITING_INPUT: Waiting for external input before resuming
    DELEGATED: Work has been delegated to a child thread
    COMPLETED: Thread fulfilled its purpose
    INTERRUPTED: Semantic or runtime condition prevented continuation
    TERMINATED: Thread stopped without normal completion

Allowed Transitions:
    CREATED → ACTIVE (initial activation)
    ACTIVE → SUSPENDED (pause intent)
    SUSPENDED → ACTIVE (resume intent)
    ACTIVE → AWAITING_INPUT (awaiting external input)
    AWAITING_INPUT → ACTIVE (input received)
    ACTIVE → DELEGATED (delegation to child)
    DELEGATED → COMPLETED (child completion)
    ACTIVE → COMPLETED (purpose fulfilled)
    Any state → INTERRUPTED (interruption event)
    Any terminal state → REOPENED (if architecture allows reopening)
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from enum import Enum


class ThreadLifecycleState(Enum):
    """
    Canonical thread lifecycle states.
    
    State Flow:
        [CREATED] → [ACTIVE] ⇄ [SUSPENDED] → [TERMINATING] → [TERMINATED]
           |            ↓         ↑              ↓
           └─── DELEGATE ─────   AWAITING_INPUT  COMPLETE
        
        Terminal states (no outgoing):
            COMPLETED, INTERRUPTED, TERMINATED
    """
    
    # Initial state
    CREATED = "created"
    
    # Active states
    ACTIVE = "active"              # Currently engaged in semantic activity
    SUSPENDED = "suspended"        # Temporarily paused
    AWAITING_INPUT = "awaiting_input"  # Waiting for external input
    
    # Delegation state
    DELEGATED = "delegated"        # Work delegated to child thread
    
    # Terminal states (no outgoing transitions)
    COMPLETED = "completed"        # Purpose fulfilled
    INTERRUPTED = "interrupted"    # Interrupted before completion
    TERMINATED = "terminated"      # Terminated without completion


class ThreadLifecycleReason(Enum):
    """
    Reasons for lifecycle transitions.
    
    Used for audit, debugging, and policy decisions.
    """
    
    # Active state transitions
    INITIAL_ACTIVATION = "initial_activation"
    RESUME = "resume"
    SUSPEND_REQUESTED = "suspend_requested"
    INPUT_RECEIVED = "input_received"
    
    # Delegation
    DELEGATE_TO_CHILD = "delegate_to_child"
    CHILD_COMPLETED = "child_completed"
    
    # Terminal states
    PURPOSE_FULFILLED = "purpose_fulfilled"
    INTERRUPTION_REQUESTED = "interruption_requested"
    TERMINATION_REQUESTED = "termination_requested"


@dataclass(frozen=True)
class ThreadLifecycleTransition:
    """
    A single lifecycle state transition.
    
    Defines the rules for one state → another state transition in a thread's
    semantic lifecycle.
    """
    
    from_state: ThreadLifecycleState
    to_state: ThreadLifecycleState
    
    # Who may request this transition?
    requester: str  # e.g., "thread", "core", "user"
    
    # Conditions
    precondition: Optional[str] = None  # What must be true before transition?
    postcondition: Optional[str] = None  # What is guaranteed after?
    
    # Metadata
    reason: Optional[ThreadLifecycleReason] = None
    is_terminal: bool = False  # Does this lead to a terminal state?
    
    def __hash__(self) -> int:
        return hash((self.from_state, self.to_state))


@dataclass(frozen=True)
class ThreadLifecycleTransitionGraph:
    """
    Thread lifecycle state transition graph.
    
    This is the canonical authority for what transitions are valid in a thread's
    semantic lifecycle. It may use Core's runtime state machines for enforcement
    but maintains its own semantic layer.
    """
    
    # Valid transitions: (from_state, to_state) -> Transition
    _transitions: Dict[Tuple[ThreadLifecycleState, ThreadLifecycleState], ThreadLifecycleTransition] = field(
        default_factory=dict,
        init=False,
    )
    
    def __init__(self) -> None:
        """Initialize the transition graph with all valid transitions."""
        
        # Store as immutable dict after construction
        object.__setattr__(
            self,
            "_transitions",
            {
                # Initial state
                (ThreadLifecycleState.CREATED, ThreadLifecycleState.ACTIVE): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.CREATED,
                    to_state=ThreadLifecycleState.ACTIVE,
                    requester="core",  # Core decides when to activate
                    reason=ThreadLifecycleReason.INITIAL_ACTIVATION,
                ),
                
                # Active state transitions
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.SUSPENDED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.SUSPENDED,
                    requester="thread",  # Thread may request suspension
                    reason=ThreadLifecycleReason.SUSPEND_REQUESTED,
                ),
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.AWAITING_INPUT): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.AWAITING_INPUT,
                    requester="thread",
                    reason=ThreadLifecycleReason.INPUT_RECEIVED,  # Actually waiting for input
                ),
                
                # Resume transitions (suspended → active)
                (ThreadLifecycleState.SUSPENDED, ThreadLifecycleState.ACTIVE): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.SUSPENDED,
                    to_state=ThreadLifecycleState.ACTIVE,
                    requester="thread",  # Thread requests resumption
                    reason=ThreadLifecycleReason.RESUME,
                ),
                
                # Input received (awaiting → active)
                (ThreadLifecycleState.AWAITING_INPUT, ThreadLifecycleState.ACTIVE): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.AWAITING_INPUT,
                    to_state=ThreadLifecycleState.ACTIVE,
                    requester="thread",
                    reason=ThreadLifecycleReason.INPUT_RECEIVED,
                ),
                
                # Delegation
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.DELEGATED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.DELEGATED,
                    requester="thread",  # Thread may delegate work
                    reason=ThreadLifecycleReason.DELEGATE_TO_CHILD,
                ),
                
                # Child completion (delegated → completed)
                (ThreadLifecycleState.DELEGATED, ThreadLifecycleState.COMPLETED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.DELEGATED,
                    to_state=ThreadLifecycleState.COMPLETED,
                    requester="thread",  # Child completion leads to parent completion
                    reason=ThreadLifecycleReason.CHILD_COMPLETED,
                    is_terminal=True,
                ),
                
                # Completion (active → completed)
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.COMPLETED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.COMPLETED,
                    requester="thread",  # Thread decides it's complete
                    reason=ThreadLifecycleReason.PURPOSE_FULFILLED,
                    is_terminal=True,
                ),
                
                # Interruption (any state → interrupted)
                (ThreadLifecycleState.CREATED, ThreadLifecycleState.INTERRUPTED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.CREATED,
                    to_state=ThreadLifecycleState.INTERRUPTED,
                    requester="core",  # Core may interrupt
                    reason=ThreadLifecycleReason.INTERRUPTION_REQUESTED,
                    is_terminal=True,
                ),
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.INTERRUPTED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.INTERRUPTED,
                    requester="core",
                    reason=ThreadLifecycleReason.INTERRUPTION_REQUESTED,
                    is_terminal=True,
                ),
                (ThreadLifecycleState.SUSPENDED, ThreadLifecycleState.INTERRUPTED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.SUSPENDED,
                    to_state=ThreadLifecycleState.INTERRUPTED,
                    requester="core",
                    reason=ThreadLifecycleReason.INTERRUPTION_REQUESTED,
                    is_terminal=True,
                ),
                
                # Termination (any state → terminated)
                (ThreadLifecycleState.CREATED, ThreadLifecycleState.TERMINATED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.CREATED,
                    to_state=ThreadLifecycleState.TERMINATED,
                    requester="thread",
                    reason=ThreadLifecycleReason.TERMINATION_REQUESTED,
                    is_terminal=True,
                ),
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.TERMINATED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.TERMINATED,
                    requester="thread",
                    reason=ThreadLifecycleReason.TERMINATION_REQUESTED,
                    is_terminal=True,
                ),
                (ThreadLifecycleState.SUSPENDED, ThreadLifecycleState.TERMINATED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.SUSPENDED,
                    to_state=ThreadLifecycleState.TERMINATED,
                    requester="thread",
                    reason=ThreadLifecycleReason.TERMINATION_REQUESTED,
                    is_terminal=True,
                ),
            },
        )
    
    def get_transition(
        self, from_state: ThreadLifecycleState, to_state: ThreadLifecycleState
    ) -> Optional[ThreadLifecycleTransition]:
        """Get the transition between two states (if valid)."""
        return self._transitions.get((from_state, to_state))
    
    def is_valid_transition(
        self, from_state: ThreadLifecycleState, to_state: ThreadLifecycleState
    ) -> bool:
        """Check if a transition is valid according to the graph."""
        return (from_state, to_state) in self._transitions
    
    def get_allowed_transitions(self, state: ThreadLifecycleState) -> Tuple[ThreadLifecycleState, ...]:
        """Get all states that can be reached from given state."""
        return tuple(
            to for (f, to) in self._transitions.keys()
            if f == state
        )
    
    def is_terminal_state(self, state: ThreadLifecycleState) -> bool:
        """Check if a state is terminal (no outgoing transitions)."""
        return len(self.get_allowed_transitions(state)) == 0


@dataclass(frozen=True)
class ThreadLifecycleSnapshot:
    """
    Immutable snapshot of thread lifecycle state.
    
    Used for persistence and recovery. Contains only the essential
    lifecycle information, not full semantic state.
    """
    
    thread_id: str
    current_state: ThreadLifecycleState
    
    # Semantic version (for delta validation)
    semantic_version: int = 0
    
    # Active associations (owned by core but referenced here)
    has_active_loop: bool = False
    has_active_cycle: bool = False
    
    # Relationship info
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    # Terminal state information (if applicable)
    completion_reason: Optional[str] = None
    interruption_reason: Optional[str] = None


# =============================================================================
# LIFECYCLE TRANSITION REQUEST/RESULT
# =============================================================================

@dataclass(frozen=True)
class ThreadLifecycleTransitionRequest:
    """
    Request to perform a thread lifecycle state transition.
    
    Contains all information needed for validation and commitment.
    """
    
    thread_id: str
    from_state: ThreadLifecycleState
    to_state: ThreadLifecycleState
    
    # Metadata
    reason: Optional[str] = None  # Human-readable explanation
    timestamp_utc: float = 0.0  # Set by system
    requested_by: Optional[str] = None  # Who requested it?
    
    def to_dict(self) -> Dict[str, str]:
        """Convert request to dictionary for serialization."""
        return {
            "thread_id": self.thread_id,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "reason": self.reason or "",
        }


@dataclass(frozen=True)
class ThreadLifecycleTransitionResult:
    """
    Result of a thread lifecycle transition request.
    
    Contains the outcome including whether it was accepted and what changed.
    """
    
    # Required fields (no defaults)
    accepted: bool
    previous_state: Optional[ThreadLifecycleState] = None
    current_state: Optional[ThreadLifecycleState] = None
    
    # Optional fields with defaults
    rejection_reason: Optional[str] = None
    committed_at_utc: float = 0.0
    transition_metadata: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def accepted(
        cls,
        previous_state: ThreadLifecycleState,
        current_state: ThreadLifecycleState,
        **kwargs,
    ) -> "ThreadLifecycleTransitionResult":
        """Create an accepted result."""
        return cls(
            accepted=True,
            previous_state=previous_state,
            current_state=current_state,
            **kwargs,
        )
    
    @classmethod
    def rejected(
        cls,
        previous_state: ThreadLifecycleState,
        reason: str,
        **kwargs,
    ) -> "ThreadLifecycleTransitionResult":
        """Create a rejected result."""
        return cls(
            accepted=False,
            previous_state=previous_state,
            current_state=previous_state,  # State unchanged
            rejection_reason=reason,
            **kwargs,
        )


__all__ = [
    "ThreadLifecycleState",
    "ThreadLifecycleReason",
    "ThreadLifecycleTransition",
    "ThreadLifecycleTransitionGraph",
    "ThreadLifecycleSnapshot",
    "ThreadLifecycleTransitionRequest",
    "ThreadLifecycleTransitionResult",
]