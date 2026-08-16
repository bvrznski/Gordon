# Executive State Transitions
# ============================

"""
Immutable transition types for executive state changes.

Transitions represent how the executive state evolves from one revision
to another through validated, deterministic operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# EXECUTIVE STATE TRANSITION KINDS
# =============================================================================


class ExecutiveStateTransitionKind:
    """
    Kinds of executive state transitions.
    
    Each kind represents a semantic change in the executive's organization
    or assessment. Transitions must be validated before being applied.
    """
    
    # Initialization
    STATE_INITIALIZED = "state_initialized"
    """Initial state creation."""
    
    CONTEXT_ACCEPTED = "context_accepted"
    """Context accepted for assessment."""
    
    CONTEXT_REJECTED = "context_rejected"
    """Context rejected for assessment."""
    
    # Mode transitions
    MODE_CHANGED = "mode_changed"
    """Executive mode changed."""
    
    # Task set references
    TASK_SET_REFERENCE_ACTIVATED = "task_set_reference_activated"
    """Task set activated as active."""
    
    TASK_SET_REFERENCE_SUSPENDED = "task_set_reference_suspended"
    """Task set suspended."""
    
    TASK_SET_REFERENCE_REPLACED = "task_set_reference_replaced"
    """Active task set replaced by new one."""
    
    # Goal and commitment references
    GOAL_REFERENCE_ADDED = "goal_reference_added"
    """Goal added to active goals."""
    
    GOAL_REFERENCE_REMOVED = "goal_reference_removed"
    """Goal removed from active goals."""
    
    COMMITMENT_REFERENCE_ADDED = "commitment_reference_added"
    """Commitment added to active commitments."""
    
    COMMITMENT_REFERENCE_REMOVED = "commitment_reference_removed"
    """Commitment removed from active commitments."""
    
    # Strategy reference
    STRATEGY_REFERENCE_CHANGED = "strategy_reference_changed"
    """Active strategy changed."""
    
    # Summary updates (bounded summaries, not full implementations)
    CONTROL_STATE_UPDATED = "control_state_updated"
    """Control state summary updated."""
    
    CONFLICT_STATE_UPDATED = "conflict_state_updated"
    """Conflict state summary updated."""
    
    PERFORMANCE_STATE_UPDATED = "performance_state_updated"
    """Performance state summary updated."""
    
    DECISION_STATE_UPDATED = "decision_state_updated"
    """Decision state summary updated."""
    
    INHIBITION_STATE_UPDATED = "inhibition_state_updated"
    """Inhibition state summary updated."""
    
    SWITCHING_STATE_UPDATED = "switching_state_updated"
    """Switching state summary updated."""
    
    RECOVERY_STATE_UPDATED = "recovery_state_updated"
    """Recovery state summary updated."""
    
    # External requests and results
    EXTERNAL_REQUEST_ADDED = "external_request_added"
    """External request added to pending."""
    
    EXTERNAL_REQUEST_RESOLVED = "external_request_resolved"
    """External request resolved."""
    
    # Proposals and decisions
    PROPOSAL_ADDED = "proposal_added"
    """Executive proposal added to pending."""
    
    PROPOSAL_RESOLVED = "proposal_resolved"
    """Executive proposal resolved."""
    
    AUTHORITY_DECISION_ACCEPTED = "authority_decision_accepted"
    """Authority decision accepted."""
    
    AUTHORITY_DECISION_REJECTED = "authority_decision_rejected"
    """Authority decision rejected."""
    
    # State lifecycle
    STATE_WAITING = "state_waiting"
    """State entered waiting for external result."""
    
    STATE_SUSPENDED = "state_suspended"
    """State suspended by authority."""
    
    STATE_RESUMED = "state_resumed"
    """State resumed from suspension."""
    
    STATE_COMPLETED = "state_completed"
    """Executive evaluation completed successfully."""
    
    STATE_FAILED = "state_failed"
    """Executive evaluation failed."""
    
    STATE_REVISED = "state_revised"
    """State revised with new context or results."""


# =============================================================================
# EXECUTIVE STATE TRANSITION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateTransition:
    """
    Immutable transition from one executive state to another.
    
    A transition includes:
        - Unique ID identifying this transition instance
        - Prior revision (what was changed FROM)
        - Resulting revision (what is changed TO)
        - Transition kind (semantic type of change)
        - Affected references (items modified by the transition)
        - Reason for the change
        - Originating context reference
        - Authority that approved it
        - Semantic time when it occurred
        - Correlation IDs for tracing
        - Causation chain
        - Provenance record
    
    Transitions are:
        - Immutable: Cannot be modified after creation
        - Validated: Must pass transition legality checks
        - Ordered: Applied in a specific sequence to produce deterministic results
        - Replayable: Given the same state and transitions, the same result is produced
    """
    
    transition_id: str = "exec_transition_unknown"
    """Unique identifier for this transition."""
    
    prior_revision: int = 0
    """Revision before this transition is applied."""
    
    resulting_revision: int = 1
    """Revision after this transition is applied."""
    
    kind: str = ExecutiveStateTransitionKind.STATE_INITIALIZED
    """Semantic type of the transition."""
    
    affected_task_set_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Task set IDs affected by this transition."""
    
    affected_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Goal IDs affected by this transition."""
    
    affected_commitment_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Commitment IDs affected by this transition."""
    
    reason: str = "unknown"
    """Human-readable reason for the transition."""
    
    originating_context_id: Optional[str] = None
    """Context that triggered this transition (if any)."""
    
    authority_approved: bool = False
    """Whether an external authority approved this change."""
    
    semantic_time_utc: float = 0.0
    """Semantic time when transition was created (seconds since epoch)."""
    
    correlation_id: Optional[str] = None
    """ID for correlating transitions across assessments."""
    
    causation_chain: Tuple[str, ...] = field(default_factory=tuple)
    """Chain of prior transitions that caused this one."""
    
    provenance_id: Optional[str] = None
    """ID of provenance record for this transition."""
    
    @classmethod
    def initialized(cls) -> ExecutiveStateTransition:
        """
        Create an initial state transition.
        
        Returns:
            A new ExecutiveStateTransition instance
        """
        return cls(
            kind=ExecutiveStateTransitionKind.STATE_INITIALIZED,
            reason="initial_state_created",
        )
    
    @classmethod
    def mode_changed(
        cls,
        prior_revision: int,
        resulting_revision: int,
        new_mode: str,
    ) -> ExecutiveStateTransition:
        """
        Create a mode change transition.
        
        Args:
            prior_revision: Revision before the change
            resulting_revision: Revision after the change
            new_mode: New executive mode
        
        Returns:
            A new ExecutiveStateTransition instance
        """
        return cls(
            prior_revision=prior_revision,
            resulting_revision=resulting_revision,
            kind=ExecutiveStateTransitionKind.MODE_CHANGED,
            reason=f"mode_changed_to_{new_mode}",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveStateTransitionKind",
    "ExecutiveStateTransition",
)