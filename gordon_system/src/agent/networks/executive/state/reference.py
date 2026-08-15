# Executive State References
# ==========================

"""
Reference types for executive state.

References provide stable, immutable identifiers and bounded summaries that
can be included in state without copying full objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# BASE REFERENCE TYPES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateReference:
    """
    Immutable reference to an executive state.
    
    Used when full state transfer is unnecessary - e.g., for storage,
    history entries, or brief communication between systems.
    """
    
    state_id: str = "exec_state_unknown"
    """The unique identifier of the referenced state."""
    
    revision: int = 0
    """Revision number at time of reference creation."""
    
    schema_version: str = "1.0.0"
    """Schema version when this reference was created."""
    
    mode: Optional[str] = None
    """Executive mode at time of reference."""
    
    active_task_set_id: Optional[str] = None
    """ID of the currently active task set (if any)."""
    
    confidence_class: str = "unknown"
    """Confidence classification."""
    
    completeness_class: str = "unknown"
    """Completeness classification."""
    
    integrity_digest: Optional[str] = None
    """Hash digest for integrity verification."""
    
    provenance_reference: Optional[str] = None
    """Reference to provenance information."""
    
    @classmethod
    def from_state(cls, state_id: str, revision: int) -> ExecutiveStateReference:
        """Create a reference from basic state info."""
        return cls(state_id=state_id, revision=revision)


@dataclass(frozen=True)
class ExecutiveContextReference:
    """
    Immutable reference to an executive context.
    
    Context references are immutable and preserve no mutable data from
    the source system.
    """
    
    context_id: str = "exec_context_unknown"
    """The unique identifier of the referenced context."""
    
    revision: int = 1
    """Revision number at time of reference creation."""
    
    schema_version: str = "1.0.0"
    """Schema version when this reference was created."""
    
    purpose: Optional[str] = None
    """Purpose for which this context was assembled."""
    
    subject: Optional[str] = None
    """Subject being assessed in the context."""
    
    validity_class: str = "unknown"
    """Validity classification."""
    
    confidence_class: str = "unknown"
    """Confidence classification."""
    
    completeness_class: str = "unknown"
    """Completeness classification."""
    
    integrity_digest: Optional[str] = None
    """Hash digest for integrity verification."""
    
    provenance_reference: Optional[str] = None
    """Reference to provenance information."""
    
    @classmethod
    def from_context(cls, context_id: str, revision: int) -> ExecutiveContextReference:
        """Create a reference from basic context info."""
        return cls(context_id=context_id, revision=revision)


# =============================================================================
# TASK-SET AND EXECUTIVE PROGRAM REFERENCES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveTaskSetReference:
    """
    Immutable reference to an executive task set.
    
    Task sets will be defined in detail in Phase 4.4.3. This is a forward-
    compatible placeholder that preserves the relationship.
    """
    
    task_set_id: str = "exec_taskset_unknown"
    """The unique identifier of the referenced task set."""
    
    parent_state_revision: int = 0
    """State revision when this task set was activated."""
    
    activation_time_utc: float = 0.0
    """When this task set became active (seconds since epoch)."""
    
    status: str = "unknown"
    """Task set status (e.g., 'active', 'suspended', 'candidate')."""
    
    confidence_class: str = "unknown"
    """Confidence in the task set."""
    
    completeness_class: str = "unknown"
    """Completeness of the task set definition."""
    
    @classmethod
    def new(cls, task_set_id: str) -> ExecutiveTaskSetReference:
        """Create a new task set reference with default values."""
        return cls(task_set_id=task_set_id)


@dataclass(frozen=True)
class ExecutiveGoalReference:
    """
    Immutable reference to an executive goal.
    
    Goals will be defined in detail in Phase 4.4.4. This is a forward-
    compatible placeholder that preserves the relationship.
    """
    
    goal_id: str = "exec_goal_unknown"
    """The unique identifier of the referenced goal."""
    
    task_set_id: Optional[str] = None
    """Task set this goal belongs to (if known)."""
    
    priority_class: str = "medium"
    """Priority classification."""
    
    status: str = "pending"
    """Goal status."""
    
    @classmethod
    def new(cls, goal_id: str) -> ExecutiveGoalReference:
        """Create a new goal reference with default values."""
        return cls(goal_id=goal_id)


@dataclass(frozen=True)
class ExecutiveCommitmentReference:
    """
    Immutable reference to an executive commitment.
    
    Commitments will be defined in detail in Phase 4.4.4. This is a forward-
    compatible placeholder that preserves the relationship.
    """
    
    commitment_id: str = "exec_commitment_unknown"
    """The unique identifier of the referenced commitment."""
    
    task_set_id: Optional[str] = None
    """Task set this commitment belongs to (if known)."""
    
    strength_class: str = "medium"
    """Strength classification."""
    
    status: str = "pending"
    """Commitment status."""
    
    @classmethod
    def new(cls, commitment_id: str) -> ExecutiveCommitmentReference:
        """Create a new commitment reference with default values."""
        return cls(commitment_id=commitment_id)


@dataclass(frozen=True)
class ExecutiveStrategyReference:
    """
    Immutable reference to an executive strategy.
    
    Strategies will be defined in detail in later phases. This is a forward-
    compatible placeholder that preserves the relationship.
    """
    
    strategy_id: str = "exec_strategy_unknown"
    """The unique identifier of the referenced strategy."""
    
    task_set_id: Optional[str] = None
    """Task set this strategy applies to (if known)."""
    
    confidence_class: str = "unknown"
    """Confidence in the strategy."""
    
    status: str = "pending"
    """Strategy status."""
    
    @classmethod
    def new(cls, strategy_id: str) -> ExecutiveStrategyReference:
        """Create a new strategy reference with default values."""
        return cls(strategy_id=strategy_id)


# =============================================================================
# EXTERNAL REQUEST AND RESULT REFERENCES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveExternalRequestReference:
    """
    Immutable reference to an external request.
    
    Requests from outside the executive network are referenced, not owned.
    """
    
    request_id: str = "exec_request_unknown"
    """The unique identifier of the referenced request."""
    
    source_system: str = "unknown"
    """System that made the request."""
    
    request_type: str = "unknown"
    """Type of request (e.g., 'evaluate', 'continuation')."""
    
    created_at_utc: float = 0.0
    """When the request was created."""
    
    status: str = "pending"
    """Request status."""
    
    @classmethod
    def new(cls, request_id: str) -> ExecutiveExternalRequestReference:
        """Create a new external request reference with default values."""
        return cls(request_id=request_id)


@dataclass(frozen=True)
class ExecutiveExternalResultReference:
    """
    Immutable reference to an external result.
    
    Results from outside the executive network are referenced, not owned.
    """
    
    result_id: str = "exec_result_unknown"
    """The unique identifier of the referenced result."""
    
    request_id: Optional[str] = None
    """ID of the request this results (if any)."""
    
    status: str = "pending"
    """Result status."""
    
    consumed_at_utc: float = 0.0
    """When this result was consumed by executive evaluation."""
    
    @classmethod
    def new(cls, result_id: str) -> ExecutiveExternalResultReference:
        """Create a new external result reference with default values."""
        return cls(result_id=result_id)


# =============================================================================
# PROPOSAL AND AUTHORITY DECISION REFERENCES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveProposalReference:
    """
    Immutable reference to an executive proposal.
    
    Proposals are suggestions from the executive network that may or may not
    be accepted by downstream systems.
    """
    
    proposal_id: str = "exec_proposal_unknown"
    """The unique identifier of the referenced proposal."""
    
    proposal_type: str = "unknown"
    """Type of proposal (e.g., 'task_set_activation', 'control_allocation')."""
    
    status: str = "pending"
    """Proposal status."""
    
    created_at_utc: float = 0.0
    """When the proposal was made."""
    
    @classmethod
    def new(cls, proposal_id: str) -> ExecutiveProposalReference:
        """Create a new proposal reference with default values."""
        return cls(proposal_id=proposal_id)


@dataclass(frozen=True)
class ExecutiveAuthorityDecisionReference:
    """
    Immutable reference to an authority decision.
    
    Authority decisions are made by external authorities that may accept or
    reject executive proposals.
    """
    
    decision_id: str = "exec_decision_unknown"
    """The unique identifier of the referenced decision."""
    
    proposal_id: Optional[str] = None
    """ID of the proposal this decision addresses."""
    
    outcome: str = "pending"
    """Decision outcome (e.g., 'accepted', 'rejected', 'deferred')."""
    
    made_at_utc: float = 0.0
    """When the decision was made."""
    
    @classmethod
    def new(cls, decision_id: str) -> ExecutiveAuthorityDecisionReference:
        """Create a new authority decision reference with default values."""
        return cls(decision_id=decision_id)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveStateReference",
    "ExecutiveContextReference",
    "ExecutiveTaskSetReference",
    "ExecutiveGoalReference",
    "ExecutiveCommitmentReference",
    "ExecutiveStrategyReference",
    "ExecutiveExternalRequestReference",
    "ExecutiveExternalResultReference",
    "ExecutiveProposalReference",
    "ExecutiveAuthorityDecisionReference",
)