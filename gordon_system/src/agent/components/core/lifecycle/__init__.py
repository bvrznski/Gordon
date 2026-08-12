# Core Lifecycle Infrastructure
# =============================

"""
Core lifecycle state machine definitions for runtime entities.

This module provides canonical lifecycle state machines used throughout
the Gordon runtime system. Execution may use these definitions but should
not duplicate them.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Any
from enum import Enum


# =============================================================================
# Thread Lifecycle State Machine
# =============================================================================

class ThreadLifecycleState(Enum):
    """
    Thread lifecycle states.

    State Flow:
        [NEW] → [QUEUED] → [ACTIVE] ⇄ [PAUSED] → [TERMINATING] → [TERMINATED]
          |             ↘     ↙            ↓
          └───── RECOVER ───┘           FAIL
    
    Ownership:
        - Thread owns semantic intent (when to terminate)
        - Core owns runtime state transitions
    """
    
    NEW = "new"              # Just created, not yet queued
    QUEUED = "queued"        # In scheduler queue, awaiting execution
    ACTIVE = "active"        # Currently running cycles
    PAUSED = "paused"        # Temporarily suspended
    TERMINATING = "terminating"  # Requested termination, cleaning up
    TERMINATED = "terminated"    # Terminated completely
    FAILED = "failed"          # Failed during any phase


# =============================================================================
# Cycle Lifecycle State Machine  
# =============================================================================

class CycleState(Enum):
    """
    Cycle execution states.

    State Flow:
        [READY] → [EXECUTING]
                   ↓
               [STAGE_i] ⇄ [INTERRUPTIBLE]
                   ↓
            [POSTCONDITION_CHECK]
                   ↓
          {COMPLETED, CONTINUE, WAIT, DELEGATE, FAIL}
    
    Ownership:
        - Cycle owns stage progression
        - Core owns interruption and rescheduling
    """
    
    READY = "ready"              # Ready to start execution
    EXECUTING = "executing"      # Currently executing a stage
    STAGE_0 = "stage_0"
    STAGE_N = "stage_n"          # N-th stage (generic placeholder)
    INTERRUPTIBLE = "interruptible"  # Stage that may be interrupted
    POSTCONDITION_CHECK = "postcondition_check"
    
    # Terminal states
    COMPLETED = "completed"
    CONTINUE = "continue"        # May continue with next cycle
    WAIT = "wait"                # Waiting for external event
    DELEGATE = "delegate"        # Delegated to another unit
    FAIL = "fail"


# =============================================================================
# State Transitions
# =============================================================================

@dataclass(frozen=True)
class StateTransition:
    """
    A single transition in a state machine.
    
    Defines the rules for one state → another state transition.
    """
    
    from_state: str  # Source state identifier
    to_state: str    # Target state identifier
    
    # Ownership
    requester: str   # Who may request this transition (e.g., "thread", "core")
    committer: str   # Who commits the transition ("core" or specific component)
    
    # Conditions
    precondition: Optional[str] = None  # Precondition string (for documentation)
    postcondition: Optional[str] = None  # Postcondition string
    
    # Behavior
    observable: bool = True  # Should this be logged?
    persists_state: bool = False  # Should state be persisted before transition?


# =============================================================================
# Thread Lifecycle Transition Graph
# =============================================================================

class ThreadLifecycleTransitionGraph:
    """
    Thread lifecycle state transition graph.
    
    Rules:
        - NEW → QUEUED (Thread requests, Core commits)
        - QUEUED → ACTIVE (Core scheduler decides)
        - ACTIVE → PAUSED (Core or Thread requests)
        - PAUSED → ACTIVE (Core scheduler)
        - ACTIVE → TERMINATING (Thread requests completion condition satisfied)
        - TERMINATING → TERMINATED (Core cleans up and commits)
        - Any state → FAILED (Core detects failure)
        - FAILED → QUEUED (Core recovery, if recoverable)
    """
    
    def __init__(self) -> None:
        self._transitions: Dict[Tuple[str, str], StateTransition] = {
            # Initial states
            ("new", "queued"): StateTransition(
                from_state="new",
                to_state="queued",
                requester="thread",
                committer="core",
                observable=True,
            ),
            
            # Scheduling
            ("queued", "active"): StateTransition(
                from_state="queued",
                to_state="active",
                requester="core",
                committer="core",
                observable=True,
            ),
            
            # Pausing (bidirectional)
            ("active", "paused"): StateTransition(
                from_state="active",
                to_state="paused",
                requester="core",
                committer="core",
                observable=True,
            ),
            ("paused", "active"): StateTransition(
                from_state="paused",
                to_state="active",
                requester="core",
                committer="core",
                observable=True,
            ),
            
            # Termination
            ("active", "terminating"): StateTransition(
                from_state="active",
                to_state="terminating",
                requester="thread",
                committer="core",
                observable=True,
            ),
            ("paused", "terminating"): StateTransition(
                from_state="paused",
                to_state="terminating",
                requester="thread",
                committer="core",
                observable=True,
            ),
            
            # Final state
            ("terminating", "terminated"): StateTransition(
                from_state="terminating",
                to_state="terminated",
                requester="core",
                committer="core",
                observable=True,
                persists_state=False,  # Terminated state need not be persisted
            ),
            
            # Failure paths
            ("new", "failed"): StateTransition(
                from_state="new",
                to_state="failed",
                requester="core",
                committer="core",
                observable=True,
            ),
            ("queued", "failed"): StateTransition(
                from_state="queued",
                to_state="failed",
                requester="core",
                committer="core",
                observable=True,
            ),
            ("active", "failed"): StateTransition(
                from_state="active",
                to_state="failed",
                requester="core",
                committer="core",
                observable=True,
            ),
            ("paused", "failed"): StateTransition(
                from_state="paused",
                to_state="failed",
                requester="core",
                committer="core",
                observable=True,
            ),
            ("terminating", "failed"): StateTransition(
                from_state="terminating",
                to_state="failed",
                requester="core",
                committer="core",
                observable=True,
            ),
            
            # Recovery
            ("failed", "queued"): StateTransition(
                from_state="failed",
                to_state="queued",
                requester="core",
                committer="core",
                observable=True,
            ),
        }
    
    def get_transition(self, from_state: str, to_state: str) -> Optional[StateTransition]:
        """Get the transition between two states."""
        return self._transitions.get((from_state, to_state))
    
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition is valid according to the graph."""
        return (from_state, to_state) in self._transitions
    
    def get_allowed_transitions(self, state: str) -> Tuple[str, ...]:
        """Get all states that can be reached from given state."""
        return tuple(
            to for (f, to) in self._transitions.keys()
            if f == state
        )


# =============================================================================
# Cycle Lifecycle Transition Graph
# =============================================================================

class CycleTransitionGraph:
    """
    Cycle execution state transition graph.
    
    Rules:
        - READY → STAGE_0 (Cycle starts)
        - STAGE_i → STAGE_{i+1} (Stage completed successfully)
        - Any stage → INTERRUPTIBLE (when cycle marks stage as interruptible)
        - Any state → COMPLETED/CONTINUE/WAIT/DELEGATE/FAIL (terminal states)
    """
    
    def __init__(self) -> None:
        self._transitions: Dict[Tuple[str, str], StateTransition] = {
            # Starting execution
            ("ready", "executing"): StateTransition(
                from_state="ready",
                to_state="executing",
                requester="cycle",
                committer="core",
                observable=True,
            ),
            
            # Stage progression (generic N stages)
            ("executing", "stage_0"): StateTransition(
                from_state="executing",
                to_state="stage_0",
                requester="cycle",
                committer="cycle",
                observable=True,
            ),
            ("stage_0", "interruptible"): StateTransition(
                from_state="stage_0",
                to_state="interruptible",
                requester="cycle",
                committer="core",
                observable=True,
            ),
            
            # Terminal states
            ("stage_0", "completed"): StateTransition(
                from_state="stage_0",
                to_state="completed",
                requester="cycle",
                committer="cycle",
                observable=True,
            ),
            ("interruptible", "completed"): StateTransition(
                from_state="interruptible",
                to_state="completed",
                requester="cycle",
                committer="cycle",
                observable=True,
            ),
        }
    
    def get_transition(self, from_state: str, to_state: str) -> Optional[StateTransition]:
        """Get the transition between two states."""
        return self._transitions.get((from_state, to_state))
    
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition is valid according to the graph."""
        return (from_state, to_state) in self._transitions


# =============================================================================
# Lifecycle Transition Requests
# =============================================================================

@dataclass(frozen=True)
class LifecycleTransitionRequest:
    """
    Request to perform a lifecycle state transition.
    
    Contains all information needed for Core to validate and commit the transition.
    """
    
    execution_id: str  # Which unit is transitioning?
    from_state: str    # Current (expected) state
    to_state: str      # Target state
    
    # Metadata
    reason: Optional[str] = None  # Why is this transition requested?
    timestamp: float = field(default_factory=lambda: 0.0)  # Set by Core
    
    # Ownership tracking
    requested_by: Optional[str] = None  # Who requested it? (thread id, etc.)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert request to dictionary for serialization."""
        return {
            "execution_id": self.execution_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "reason": self.reason or "",
        }


@dataclass(frozen=True)
class LifecycleTransitionResult:
    """
    Result of a lifecycle transition request.
    
    Contains the outcome including whether it was accepted and what changed.
    """
    
    # Required fields
    accepted: bool
    previous_state: str
    current_state: str
    
    # Optional fields with defaults
    rejection_reason: Optional[str] = None
    committed_at: float = field(default_factory=lambda: 0.0)
    transition_metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# State Snapshots (for checkpointing)
# =============================================================================

@dataclass(frozen=True)
class ThreadLifecycleSnapshot:
    """
    Immutable snapshot of thread lifecycle state.
    
    Used for persistence and recovery.
    """
    
    execution_id: str
    state: ThreadLifecycleState
    
    # Semantic information (owned by thread)
    purpose: Optional[str] = None
    completion_condition_satisfied: bool = False
    loop_binding_type: Optional[str] = None


@dataclass(frozen=True)
class CycleLifecycleSnapshot:
    """
    Immutable snapshot of cycle lifecycle state.
    
    Used for persistence and recovery.
    """
    
    execution_id: str
    cycle_state: CycleState
    
    # Stage information (owned by cycle)
    current_stage_index: int = 0
    stages_completed: Tuple[str, ...] = field(default_factory=tuple)


__all__ = [
    # State enums
    "ThreadLifecycleState",
    "CycleState",
    
    # Transition classes
    "StateTransition",
    "ThreadLifecycleTransitionGraph",
    "CycleTransitionGraph",
    
    # Request/response types
    "LifecycleTransitionRequest",
    "LifecycleTransitionResult",
    
    # Snapshots for persistence
    "ThreadLifecycleSnapshot",
    "CycleLifecycleSnapshot",
]