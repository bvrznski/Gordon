# Memory Lifecycle States - Phase 5.1.4 Canonical State Machine
# ================================================================
"""
Memory Lifecycle States: The state machine for Memory Artifact existence.

This module defines the canonical lifecycle states and their transitions:

    CANDIDATE → ACTIVE → RETAINED → ARCHIVED → SUPERSEDED
      │          │          │          │
      ▼          ▼          ▼          ▼
     FAILED   (recovery)  (retention) (failure)

Memory Lifecycle State Laws:
    STATE-LAW-001: Every Memory Artifact has exactly one lifecycle state
    STATE-LAW-002: State transitions are explicitly validated
    STATE-LAW-003: Illegal transitions are rejected
    STATE-LAW-004: State history is preserved and inspectable
    STATE-LAW-005: State changes preserve semantic identity
    STATE-LAW-006: State changes produce transition records
    STATE-LAW-007: State evaluation is deterministic

Canonical States:
    CANDIDATE     : Candidate for admission into Memory Substrate
    ACTIVE        : Fully participating in current cognition
    RETAINED      : Preserved for long-term access
    ARCHIVED      : Inactive but preserved (queryable)
    SUPERSEDED    : Replaced by newer revision
    FAILED        : Lifecycle integrity compromised
    RECOVERING    : Attempting to restore lifecycle consistency

Transition Graph:
    CANDIDATE → ACTIVE          (Admission complete)
    ACTIVE → RETAINED           (Retention policy evaluation)
    RETAINED → ARCHIVED         (Archival decision)
    ACTIVE → SUPERSEDED         (New revision created)
    ACTIVE → FAILED             (Validation failure)
    RETAINED → FAILED
    ARCHIVED → FAILED
    FAILED → RECOVERING         (Recovery attempt)
    RECOVERING → ACTIVE         (Recovery successful)
    RECOVERING → FAILED         (Recovery failed)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# MEMORY LIFECYCLE STATES
# =============================================================================


class LifecycleState(Enum):
    """
    Canonical lifecycle states for Memory Artifacts.
    
    | State       | Description                                           |
    |-------------|-------------------------------------------------------|
    | CANDIDATE   | Candidate for admission into Memory Substrate        |
    | ACTIVE      | Fully participating in current cognition             |
    | RETAINED    | Preserved for long-term access                       |
    | ARCHIVED    | Inactive but preserved (queryable)                   |
    | SUPERSEDED  | Replaced by newer revision                           |
    | FAILED      | Lifecycle integrity compromised                      |
    | RECOVERING  | Attempting to restore lifecycle consistency          |
    """
    
    CANDIDATE = "candidate"       # Candidate for admission
    ACTIVE = "active"             # Fully participating in cognition
    RETAINED = "retained"         # Preserved for long-term access
    ARCHIVED = "archived"         # Inactive but preserved (queryable)
    SUPERSEDED = "superseded"     # Replaced by newer revision
    FAILED = "failed"             # Lifecycle integrity compromised
    RECOVERING = "recovering"     # Attempting to restore consistency


# =============================================================================
# TRANSITION TYPES - What caused a state change?
# =============================================================================


class TransitionType(Enum):
    """
    Types of lifecycle transitions.
    
    | Type          | Description                                       |
    |---------------|---------------------------------------------------|
    | ADMISSION     | Artifact admitted into substrate                  |
    | ACTIVATION    | Artifact activated for cognition                  |
    | RETENTION     | Retention policy decision                         |
    | ARCHIVAL      | Artifact archived                                 |
    | SUPERSESSION  | New revision supersedes old                       |
    | FAILURE       | Lifecycle failure detected                        |
    | RECOVERY      | Recovery attempt initiated                        |
    | VALIDATION    | Validation result recorded                        |
    """
    
    ADMISSION = "admission"        # Admission into substrate
    ACTIVATION = "activation"      # Activation for cognition
    RETENTION = "retention"        # Retention policy decision
    ARCHIVAL = "archival"          # Artifact archived
    SUPERSESSION = "supersession"  # New revision supersedes old
    FAILURE = "failure"            # Lifecycle failure detected
    RECOVERY = "recovery"          # Recovery attempt initiated
    VALIDATION = "validation"      # Validation result recorded


# =============================================================================
# TRANSITION TRIGGERS - What initiates a transition?
# =============================================================================


class TransitionTrigger(Enum):
    """
    Types of triggers that cause state transitions.
    
    | Trigger           | Description                                       |
    |-------------------|---------------------------------------------------|
    | MEMORY_OPERATION  | Memory operation initiated the transition         |
    | GOVERNANCE        | Governance policy decision                        |
    | LEARNING          | Learning system request                           |
    | COORDINATION      | Coordination system request                       |
    | RECOVERY          | Recovery process initiated                        |
    | VALIDATION        | Validation process result                         |
    """
    
    MEMORY_OPERATION = "memory_operation"  # Memory operation
    GOVERNANCE = "governance"             # Governance policy
    LEARNING = "learning"                 # Learning system
    COORDINATION = "coordination"         # Coordination system
    RECOVERY = "recovery"                 # Recovery process
    VALIDATION = "validation"             # Validation result


# =============================================================================
# TRANSITION RECORD - Immutable transition history entry
# =============================================================================


@dataclass(frozen=True)
class LifecycleTransitionRecord:
    """
    Immutable record of a state transition.
    
    Every transition produces exactly one record with complete provenance.
    
    Fields:
        transition_id:       Unique ID for this transition
        previous_state:      State before the transition
        next_state:          State after the transition
        trigger:             What initiated the transition?
        type_:               Type of transition (admission, activation, etc.)
        
        # Validation
        validation_passed:   Was the transition validated?
        validation_result:   Details if validation failed
        
        # Provenance
        timestamp_utc:       When did the transition occur?
        provenance:          Where did this transition come from?
        
        # Diagnostics
        diagnostics:         Any diagnostic information
        recovery_info:       If recovery, details of what was repaired
    """
    
    transition_id: str                        # Unique ID for this transition
    
    previous_state: LifecycleState            # State before
    next_state: LifecycleState                # State after
    
    trigger: TransitionTrigger                # What caused the transition?
    type_: TransitionType                     # Type of transition
    
    # Validation
    validation_passed: bool = True            # Was it validated?
    validation_result: Optional[str] = None   # Details if failed
    
    # Provenance
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    recovery_info: Optional[Dict[str, Any]] = None  # If recovery

# =============================================================================
# LIFECYCLE STATE MACHINE - State and transition validation
# =============================================================================


class LifecycleStateMachine:
    """
    State machine for Memory Artifact lifecycle transitions.
    
    This validates whether transitions are legal according to the canonical
    state graph. It never modifies artifacts - it only validates transitions.
    
    Legal Transitions (directed graph):
        CANDIDATE → ACTIVE
        ACTIVE → RETAINED
        ACTIVE → SUPERSEDED
        ACTIVE → FAILED
        RETAINED → ARCHIVED
        RETAINED → FAILED
        ARCHIVED → FAILED
        FAILED → RECOVERING
        RECOVERING → ACTIVE
        RECOVERING → FAILED
    
    Illegal transitions raise ValueError.
    
    Lifecycle Laws:
        TRANSITION-LAW-001: Transitions occur only through State Machine
        TRANSITION-LAW-002: Transitions preserve substrate consistency
        TRANSITION-LAW-003: Transitions preserve revision lineage
        TRANSITION-LAW-004: Transitions preserve historical states
    """
    
    def __init__(self):
        """Initialize the state machine with legal transitions."""
        # Define legal transitions as adjacency list
        self._legal_transitions: Dict[LifecycleState, Tuple[LifecycleState, ...]] = {
            LifecycleState.CANDIDATE: (LifecycleState.ACTIVE,),
            LifecycleState.ACTIVE: (
                LifecycleState.RETAINED,
                LifecycleState.SUPERSEDED,
                LifecycleState.FAILED,
            ),
            LifecycleState.RETAINED: (
                LifecycleState.ARCHIVED,
                LifecycleState.FAILED,
            ),
            LifecycleState.ARCHIVED: (LifecycleState.FAILED,),
            LifecycleState.FAILED: (LifecycleState.RECOVERING,),
            LifecycleState.RECOVERING: (
                LifecycleState.ACTIVE,
                LifecycleState.FAILED,
            ),
        }
    
    def is_legal_transition(
        self,
        from_state: LifecycleState,
        to_state: LifecycleState,
    ) -> bool:
        """
        Check if a transition is legal.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if the transition is legal, False otherwise
        """
        if from_state not in self._legal_transitions:
            return False
        
        return to_state in self._legal_transitions[from_state]
    
    def validate_transition(
        self,
        from_state: LifecycleState,
        to_state: LifecycleState,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a transition and return result with error message if illegal.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            (is_valid, error_message) tuple
        """
        if not self.is_legal_transition(from_state, to_state):
            return False, (
                f"Illegal transition: {from_state.value} → {to_state.value}. "
                f"Legal transitions from {from_state.value}: "
                f"{[s.value for s in self._legal_transitions.get(from_state, ())]}"
            )
        return True, None
    
    def get_legal_next_states(self, state: LifecycleState) -> Tuple[LifecycleState, ...]:
        """
        Get all legal next states from a given state.
        
        Args:
            state: Current state
            
        Returns:
            Tuple of possible next states
        """
        return self._legal_transitions.get(state, ())
    
    def record_transition(
        self,
        artifact_id: str,
        previous_state: LifecycleState,
        next_state: LifecycleState,
        trigger: TransitionTrigger,
        type_: TransitionType,
        validation_passed: bool = True,
        validation_result: Optional[str] = None,
        diagnostics: Tuple[str, ...] = (),
        recovery_info: Optional[Dict[str, Any]] = None,
    ) -> LifecycleTransitionRecord:
        """
        Create a transition record for recording history.
        
        This does NOT perform the state change - it only creates the record.
        
        Args:
            artifact_id: ID of the artifact
            previous_state: State before transition
            next_state: State after transition
            trigger: What caused the transition?
            type_: Type of transition
            validation_passed: Was validation successful?
            validation_result: Details if validation failed
            diagnostics: Any diagnostic information
            recovery_info: If recovery, details of what was repaired
            
        Returns:
            New LifecycleTransitionRecord
        """
        return LifecycleTransitionRecord(
            transition_id=f"trans:{artifact_id}:{time.time():.6f}",
            previous_state=previous_state,
            next_state=next_state,
            trigger=trigger,
            type_=type_,
            validation_passed=validation_passed,
            validation_result=validation_result,
            provenance={"origin": "lifecycle", "artifact_id": artifact_id},
            diagnostics=diagnostics,
            recovery_info=recovery_info,
        )


# =============================================================================
# LIFECYCLE STATISTICS - Metrics about lifecycle behavior
# =============================================================================


@dataclass(frozen=True)
class LifecycleStatistics:
    """
    Statistics about memory artifact lifecycle behavior.
    
    These are observational metrics, NOT semantic authority.
    
    Fields:
        total_admissions:      Total artifacts admitted
        total_activations:     Total activations performed
        total_retentions:      Total retention decisions made
        total_archivals:       Total archivals performed
        total_supersessions:   Total supersessions performed
        total_failures:        Total failures recorded
        
        # Current state distribution
        candidate_count:       Currently in CANDIDATE state
        active_count:          Currently in ACTIVE state
        retained_count:        Currently in RETAINED state
        archived_count:        Currently in ARCHIVED state
        superseded_count:      Currently in SUPERSEDED state
        failed_count:          Currently in FAILED state
        
        # Timing stats
        mean_transition_time_ms: Average time between transitions (ms)
        
        # Health
        recovery_rate:         Fraction of failures that recovered (0.0-1.0)
    """
    
    total_admissions: int = 0
    total_activations: int = 0
    total_retentions: int = 0
    total_archivals: int = 0
    total_supersessions: int = 0
    total_failures: int = 0
    
    # Current distribution
    candidate_count: int = 0
    active_count: int = 0
    retained_count: int = 0
    archived_count: int = 0
    superseded_count: int = 0
    failed_count: int = 0
    
    # Timing
    mean_transition_time_ms: float = 0.0
    
    # Health
    recovery_rate: float = 1.0


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def is_transition_valid(
    state_machine: LifecycleStateMachine,
    from_state: LifecycleState,
    to_state: LifecycleState,
) -> bool:
    """
    Convenience function to check if a transition is valid.
    
    Args:
        state_machine: The state machine instance
        from_state: Current state
        to_state: Target state
        
    Returns:
        True if valid, False otherwise
    """
    return state_machine.is_legal_transition(from_state, to_state)


def get_transition_record(
    artifact_id: str,
    previous_state: LifecycleState,
    next_state: LifecycleState,
    trigger: TransitionTrigger = TransitionTrigger.MEMORY_OPERATION,
    type_: TransitionType = TransitionType.ACTIVATION,
) -> LifecycleTransitionRecord:
    """
    Convenience function to create a transition record.
    
    Args:
        artifact_id: ID of the artifact
        previous_state: State before transition
        next_state: State after transition
        trigger: What caused the transition?
        type_: Type of transition
        
    Returns:
        New LifecycleTransitionRecord
    """
    return LifecycleStateMachine().record_transition(
        artifact_id=artifact_id,
        previous_state=previous_state,
        next_state=next_state,
        trigger=trigger,
        type_=type_,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # States
    "LifecycleState",
    
    # Transition types and triggers
    "TransitionType",
    "TransitionTrigger",
    
    # Records
    "LifecycleTransitionRecord",
    
    # State machine
    "LifecycleStateMachine",
    
    # Statistics
    "LifecycleStatistics",
    
    # Utilities
    "is_transition_valid",
    "get_transition_record",
]