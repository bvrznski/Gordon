# Gordon Phase 3.26: Core Lifecycle Architecture
# ================================================
#
# Canonical Lifecycle State Machine Definitions for Runtime Entities

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
# CANONICAL LIFECYCLE FOUNDATIONS (Phase 3.26)
# =============================================================================

from .foundations import (
    LifecycleState,
    LifecycleEvent,
    LifecycleContext,
    LifecycleTransitionRequest as CanonicalLifecycleTransitionRequest,
    LifecycleTransitionResult as CanonicalLifecycleTransitionResult,
    LifecycleSnapshot as CanonicalLifecycleSnapshot,
    LifecycleHistory as CanonicalLifecycleHistory,
    LifecycleHistoryEntry as CanonicalLifecycleHistoryEntry,
    dataclass_replace,
)


# =============================================================================
# THREAD LIFECYCLE STATE MACHINE (Phase 3.10)
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
    
    NEW = "new"
    QUEUED = "queued"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    FAILED = "failed"


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
    """
    
    READY = "ready"
    EXECUTING = "executing"
    STAGE_0 = "stage_0"
    STAGE_N = "stage_n"
    INTERRUPTIBLE = "interruptible"
    POSTCONDITION_CHECK = "postcondition_check"
    
    COMPLETED = "completed"
    CONTINUE = "continue"
    WAIT = "wait"
    DELEGATE = "delegate"
    FAIL = "fail"


@dataclass(frozen=True)
class StateTransition:
    """
    A single transition in a state machine.
    """
    
    from_state: str
    to_state: str
    
    requester: str
    committer: str
    
    precondition: Optional[str] = None
    postcondition: Optional[str] = None
    
    observable: bool = True
    persists_state: bool = False


class ThreadLifecycleTransitionGraph:
    """
    Thread lifecycle state transition graph.
    """
    
    def __init__(self) -> None:
        self._transitions: Dict[Tuple[str, str], StateTransition] = {
            ("new", "queued"): StateTransition(
                from_state="new",
                to_state="queued",
                requester="thread",
                committer="core",
                observable=True,
            ),
            ("queued", "active"): StateTransition(
                from_state="queued",
                to_state="active",
                requester="core",
                committer="core",
                observable=True,
            ),
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
            ("terminating", "terminated"): StateTransition(
                from_state="terminating",
                to_state="terminated",
                requester="core",
                committer="core",
                observable=True,
                persists_state=False,
            ),
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
            ("failed", "queued"): StateTransition(
                from_state="failed",
                to_state="queued",
                requester="core",
                committer="core",
                observable=True,
            ),
        }
    
    def get_transition(self, from_state: str, to_state: str) -> Optional[StateTransition]:
        return self._transitions.get((from_state, to_state))
    
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        return (from_state, to_state) in self._transitions
    
    def get_allowed_transitions(self, state: str) -> Tuple[str, ...]:
        return tuple(
            to for (f, to) in self._transitions.keys()
            if f == state
        )


class CycleTransitionGraph:
    """
    Cycle execution state transition graph.
    """
    
    def __init__(self) -> None:
        self._transitions: Dict[Tuple[str, str], StateTransition] = {
            ("ready", "executing"): StateTransition(
                from_state="ready",
                to_state="executing",
                requester="cycle",
                committer="core",
                observable=True,
            ),
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
        return self._transitions.get((from_state, to_state))
    
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        return (from_state, to_state) in self._transitions


@dataclass(frozen=True)
class LifecycleTransitionRequest:
    """
    Request to perform a lifecycle state transition.
    """
    
    execution_id: str
    from_state: str
    to_state: str
    
    reason: Optional[str] = None
    timestamp: float = field(default_factory=lambda: 0.0)
    requested_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
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
    """
    
    accepted: bool
    previous_state: str
    current_state: str
    
    rejection_reason: Optional[str] = None
    committed_at: float = field(default_factory=lambda: 0.0)
    transition_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ThreadLifecycleSnapshot:
    """
    Immutable snapshot of thread lifecycle state.
    """
    
    execution_id: str
    state: ThreadLifecycleState
    
    purpose: Optional[str] = None
    completion_condition_satisfied: bool = False
    loop_binding_type: Optional[str] = None


@dataclass(frozen=True)
class CycleLifecycleSnapshot:
    """
    Immutable snapshot of cycle lifecycle state.
    """
    
    execution_id: str
    cycle_state: CycleState
    
    current_stage_index: int = 0
    stages_completed: Tuple[str, ...] = field(default_factory=tuple)


__all__ = [
    # ====== CANONICAL LIFECYCLE FOUNDATIONS (Phase 3.26) ======
    "LifecycleState",
    "LifecycleEvent",
    "LifecycleContext",
    "CanonicalLifecycleTransitionRequest",
    "CanonicalLifecycleTransitionResult",
    "CanonicalLifecycleSnapshot",
    "CanonicalLifecycleHistory",
    "CanonicalLifecycleHistoryEntry",
    "dataclass_replace",
    
    # ====== THREAD LIFECYCLE (Phase 3.10) ======
    "ThreadLifecycleState",
    "CycleState",
    
    # ====== TRANSITION TYPES ======
    "StateTransition",
    "ThreadLifecycleTransitionGraph",
    "CycleTransitionGraph",
    
    # ====== REQUEST/RESULT TYPES ======
    "LifecycleTransitionRequest",
    "LifecycleTransitionResult",
    
    # ====== SNAPSHOT TYPES ======
    "ThreadLifecycleSnapshot",
    "CycleLifecycleSnapshot",
]