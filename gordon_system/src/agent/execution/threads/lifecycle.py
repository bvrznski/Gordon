# Thread Lifecycle Model
# =======================
#
# PHASE 3.10.3 UPDATE - Canonical Thread lifecycle model.
#
# This module defines the semantic lifecycle states for a Thread.
# 
# Ownership Model:
#     - Core owns runtime state transitions (via core.lifecycle.ThreadLifecycleState)
#     - Thread owns semantic lifecycle intent (when to complete/interrupt/terminate)
#
# Semantic vs Runtime States:
#     Runtime (Core):   NEW, QUEUED, ACTIVE, PAUSED, TERMINATING, TERMINATED
#     Semantic (Thread): CREATED, ACTIVE, SUSPENDED, AWAITING_INPUT, DELEGATED,
#                        COMPLETED, INTERRUPTED, TERMINATED

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional
from enum import Enum


# =============================================================================
# SEMANTIC LIFECYCLE STATES (Thread-owned intent)
# =============================================================================


class ThreadLifecycleState(Enum):
    """
    Semantic thread lifecycle states.
    
    These represent the thread's *intention* about its state:
        - CREATED: Thread artifact exists, not yet activated by Core
        - ACTIVE: Thread is actively engaged in semantic activity
        - SUSPENDED: Behavioral progression paused, identity preserved
        - AWAITING_INPUT: Waiting for external input before resuming
        - DELEGATED: Work delegated to child thread
        - COMPLETED: Thread fulfilled its purpose (semantic intent)
        - INTERRUPTED: Semantic/interrupted condition prevented continuation
        - TERMINATED: Thread stopped without normal completion
    
    Runtime state transitions are managed by Core, but semantic intent
    comes from the Thread.
    
    Allowed Transitions:
        CREATED → ACTIVE (Core activates thread)
        ACTIVE → SUSPENDED (Thread requests pause intent)
        SUSPENDED → ACTIVE (Thread resumes)
        ACTIVE → AWAITING_INPUT (Thread awaits external input)
        AWAITING_INPUT → ACTIVE (Input received, resume intent)
        ACTIVE → DELEGATED (Thread delegates to child)
        DELEGATED → COMPLETED (Child completion triggers parent completion)
        ACTIVE → COMPLETED (Thread completes by semantic intent)
        Any state → INTERRUPTED (Core or Thread interruption)
        Terminal states have no outgoing transitions
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
    COMPLETED = "completed"        # Purpose fulfilled (semantic intent)
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
    A single semantic lifecycle state transition.
    
    This defines the *semantic intent* for a transition - what the thread
    wants to happen. Core validates and commits runtime transitions.
    """
    
    from_state: ThreadLifecycleState
    to_state: ThreadLifecycleState
    
    # Semantic requester (who has the intent)
    requester: str  # e.g., "thread", "core"
    
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
    Thread semantic lifecycle state transition graph.
    
    This defines valid semantic transitions for threads. The graph is
    immutable and used for validation of thread intent before Core
    executes the runtime transition.
    
    Runtime execution is handled by core.lifecycle.ThreadLifecycleTransitionGraph,
    but this graph validates semantic correctness first.
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
                # Initial state - Core activates the thread
                (ThreadLifecycleState.CREATED, ThreadLifecycleState.ACTIVE): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.CREATED,
                    to_state=ThreadLifecycleState.ACTIVE,
                    requester="core",
                    reason=ThreadLifecycleReason.INITIAL_ACTIVATION,
                ),
                
                # Active state transitions (thread may request)
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.SUSPENDED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.SUSPENDED,
                    requester="thread",
                    reason=ThreadLifecycleReason.SUSPEND_REQUESTED,
                ),
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.AWAITING_INPUT): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.AWAITING_INPUT,
                    requester="thread",
                    reason=ThreadLifecycleReason.INPUT_RECEIVED,
                ),
                
                # Resume transitions
                (ThreadLifecycleState.SUSPENDED, ThreadLifecycleState.ACTIVE): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.SUSPENDED,
                    to_state=ThreadLifecycleState.ACTIVE,
                    requester="thread",
                    reason=ThreadLifecycleReason.RESUME,
                ),
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
                    requester="thread",
                    reason=ThreadLifecycleReason.DELEGATE_TO_CHILD,
                ),
                
                # Child completion
                (ThreadLifecycleState.DELEGATED, ThreadLifecycleState.COMPLETED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.DELEGATED,
                    to_state=ThreadLifecycleState.COMPLETED,
                    requester="thread",
                    reason=ThreadLifecycleReason.CHILD_COMPLETED,
                    is_terminal=True,
                ),
                
                # Completion
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.COMPLETED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.COMPLETED,
                    requester="thread",
                    reason=ThreadLifecycleReason.PURPOSE_FULFILLED,
                    is_terminal=True,
                ),
                
                # Interruption
                (ThreadLifecycleState.CREATED, ThreadLifecycleState.INTERRUPTED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.CREATED,
                    to_state=ThreadLifecycleState.INTERRUPTED,
                    requester="core",
                    reason=ThreadLifecycleReason.INTERRUPTION_REQUESTED,
                    is_terminal=True,
                ),
                (ThreadLifecycleState.ACTIVE, ThreadLifecycleState.INTERRUPTED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.ACTIVE,
                    to_state=ThreadLifecycleState.INTERRUPTED,
                    requester="thread_or_core",
                    reason=ThreadLifecycleReason.INTERRUPTION_REQUESTED,
                    is_terminal=True,
                ),
                (ThreadLifecycleState.SUSPENDED, ThreadLifecycleState.INTERRUPTED): ThreadLifecycleTransition(
                    from_state=ThreadLifecycleState.SUSPENDED,
                    to_state=ThreadLifecycleState.INTERRUPTED,
                    requester="thread_or_core",
                    reason=ThreadLifecycleReason.INTERRUPTION_REQUESTED,
                    is_terminal=True,
                ),
                
                # Termination
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
        """Check if a semantic transition is valid."""
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
    Immutable snapshot of thread semantic lifecycle state.
    
    Used for persistence and recovery. Contains only the essential
    semantic lifecycle information, not runtime details.
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
    Request to perform a thread semantic lifecycle state transition.
    
    Contains all information needed for validation and commitment.
    The request goes through Core's runtime state machine after validation.
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
