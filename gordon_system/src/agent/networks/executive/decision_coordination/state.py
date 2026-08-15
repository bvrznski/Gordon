# Gordon Executive Decision State - Phase 4.4.10C Part 3
# =======================================================

"""
Executive Decision State, History, Lineage, Delta, and Transition definitions.

This module defines the canonical data structures for tracking the lifecycle of
Executive Decisions through coordination, Action Selection, and potential
execution phases.

ARCHITECTURAL PRINCIPLES:
========================

DECISION STATE:
    - Bounded semantic projection of all relevant Decision identities
    - Subordinate to ExecutiveState (not root state)
    - Immutable snapshots at each transition
    - Bounded collections for determinism

HISTORY:
    - Bounded references to Decision lifecycle events
    - Preserves revision lineage and causal ordering
    - Never retains unlimited external subsystem state

LINEAGE:
    - Graph of semantic relationships among Decisions
    - Distinguishes revision, succession, support, and causation
    - Immutable once established

DELTA:
    - Declarative semantic difference between states
    - Never mutates source artifacts
    - Represents proposed or accepted transitions

TRANSITION:
    - Accepted movement from one valid Decision State to another
    - Must preserve authority, continuity, and provenance
    - Invalidates stale downstream products when applicable

CONTINUATION:
    - Advisory specification of next coordination step
    - Never invokes or schedules runtime work
    - Represents semantic requirements only

EXECUTIVE DECISION STATE:
========================

ExecutiveDecisionState is a bounded projection of all currently relevant
Decision identities, revisions, commitments, transitions, and downstream
selection states.

INVARIANTS:
- ExecutiveDecisionState is subordinate to ExecutiveState
- All collections are bounded
- State transitions are immutable snapshots
- No direct subsystem ownership or mutation

EXECUTIVE DECISION HISTORY:
==========================

ExecutiveDecisionHistory preserves semantic references to Decision lifecycle
events: creation, revisions, commitments, reviews, suspensions, restorations,
replacements, terminations, expirations, completions, coordination requests,
projections, responses, Action Selection requests, outcomes.

INVARIANTS:
- Bounded entries (not unlimited)
- Preserves semantic-time ordering
- Preserves causal ordering
- Never retains full external subsystem state

EXECUTIVE DECISION LINEAGE:
==========================

ExecutiveDecisionLineage preserves the graph of semantic relationships among
Decision identities and revisions.

Supported relations:
    - REVISION_OF: same Decision Identity, different revision
    - DERIVED_FROM: one artifact contributed to another
    - SUPPORTS/SUPPORTED_BY: related but independently valid Decisions
    - SPECIALIZES/GENERALIZES: specialization relationship
    - DEPENDS_ON: dependency between Decisions
    - PRECEDES/FOLLOWS: temporal ordering
    - REPLACES/REPLACED_BY: replacement chain
    - SUPERSEDES/SUPERSEDED_BY: supersedes relationship
    - FALLBACK_FOR/RECOVERY_FOR: fallback/recovery purpose
    - SUSPENDS/RESTORES: suspension/restoration chain

EXECUTIVE DECISION DELTA:
========================

ExecutiveDecisionDelta expresses a proposed or accepted semantic difference
between two Decision-related states or revisions.

Delta kinds include:
    - CREATE, REVISE, COMMIT, SUSPEND, RESTORE, REPLACE, TERMINATE
    - ADD/REMOVE/REVISE_CONSTRAINT, ADD/INVALIDATE_ASSUMPTION
    - ADD/REMOVE_DEPENDENCY, ADD/EVIDENCE_JUSTIFICATION
    - CHANGE_AUTHORITY/SCOPE/HORIZON_STABILITY_CONTINUATION

INVARIANT: Delta never mutates source artifacts.

EXECUTIVE DECISION TRANSITION:
=============================

ExecutiveDecisionTransition represents the accepted semantic movement from one
valid Decision State to another.

TRANSITIONS include:
    - CREATE, REVIEW, REVISE, COMMIT, SUSPEND, RESTORE
    - REPLACE, SUPERSEDE, EXPIRE, COMPLETE, FAIL, TERMINATE
    - INVALIDATE, DEFER, REJECT

INVARIANT: Transition must validate authority, continuity, and provenance.

EXECUTIVE DECISION CONTINUATION:
===============================

ExecutiveDecisionContinuation specifies the next semantic coordination requirement
after a Decision state transition or Action Selection outcome.

Kinds include:
    - COMPLETE, MAINTAIN_DECISION, REVIEW_DECISION, REVISE_DECISION
    - SUSPEND_DECISION, RESTORE_DECISION, REPLACE_DECISION, TERMINATE_DECISION
    - REQUEST_PLANNING, REQUEST_REASONING, REQUEST_POLICY_REVIEW
    - WAIT_FOR_CONTEXT/AUTHORITY/PRODUCT/EVIDENCE
    - FAIL, CANCEL

INVARIANT: Continuation performs no runtime work.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional, Literal, FrozenSet
from enum import Enum, auto


# =============================================================================
# EXECUTIVE DECISION STATE ID
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionStateId:
    """Unique identifier for decision state."""
    value: str = field(default_factory=lambda: f"exec_dec_state_{id(object())}")


# =============================================================================
# DECISION STATE STRUCTURE
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionState:
    """
    Immutable Decision State projection.
    
    This is a bounded semantic projection of all currently relevant Decision
    identities, revisions, commitments, transitions, and downstream selection
    states required by the Executive Network.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Subordinate to ExecutiveState (not root state)
    INVARIANT: All collections are bounded
    """
    
    state_id: ExecutiveDecisionStateId = field(default_factory=ExecutiveDecisionStateId)
    """Unique identifier for this state instance."""
    
    revision: int = 1
    """Revision number of the Decision State."""
    
    schema_version: str = "1.0.0"
    """Schema version of this state type."""
    
    executive_state_reference: Optional[str] = None
    """Reference to current ExecutiveState (for revision tracking)."""
    
    executive_context_reference: Optional[str] = None
    """Reference to current ExecutiveContext (if applicable)."""
    
    # Active decisions (current working set)
    active_decisions: Tuple[str, ...] = field(default_factory=tuple)
    """Active Decision references."""
    
    committed_decisions: Tuple[str, ...] = field(default_factory=tuple)
    """Committed Decision reference IDs."""
    
    suspended_decisions: Tuple[str, ...] = field(default_factory=tuple)
    """Suspended Decision reference IDs."""
    
    terminal_decisions: Tuple[str, ...] = field(default_factory=tuple)
    """Terminal (completed/terminated/expired) Decision references."""
    
    # Coordination tracking
    coordination_requests: Tuple[str, ...] = field(default_factory=tuple)
    """Active coordination request references."""
    
    coordination_outcomes: Tuple[str, ...] = field(default_factory=tuple)
    """Coordination outcome references."""
    
    # Action selection tracking
    action_selection_requests: Tuple[str, ...] = field(default_factory=tuple)
    """Action Selection request references."""
    
    action_selection_outcomes: Tuple[str, ...] = field(default_factory=tuple)
    """Action Selection outcome references."""
    
    # Pending work
    pending_authority_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Pending authority requirement references."""
    
    pending_external_products: Tuple[str, ...] = field(default_factory=tuple)
    """Pending external product references (planning, reasoning, etc.)."""
    
    # Diagnostics
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Coordination conflict references."""
    
    continuation_ref: Optional[str] = None
    """Current continuation reference (if any)."""
    
    summary: "ExecutiveDecisionStateSummary" = field(
        default_factory=lambda: ExecutiveDecisionStateSummary()
    )
    """Bounded state summary."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"state_time_{id(object())}")
    """Reference to semantic time."""
    
    privacy_scope: str = "public"
    """Privacy scope of this state."""
    
    provenance_ref: str = field(default_factory=lambda: f"state_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# DECISION STATE SUMMARY
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionStateSummary:
    """
    Bounded non-authoritative summary of Decision State.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: This is NEVER authoritative (always references canonical artifacts).
    """
    
    active_decision_count: int = 0
    """Count of active decisions."""
    
    committed_decision_count: int = 0
    """Count of committed decisions."""
    
    suspended_decision_count: int = 0
    """Count of suspended decisions."""
    
    terminal_decision_count: int = 0
    """Count of terminal decisions."""
    
    pending_coordination_count: int = 0
    """Count of pending coordination rounds."""
    
    pending_action_selection_count: int = 0
    """Count of pending Action Selection requests."""
    
    conflict_count: int = 0
    """Count of unresolved conflicts."""
    
    current_authority_status: Literal["satisfied", "pending", "unknown"] = "unknown"
    """Current authority status."""
    
    policy_status: Literal["compliant", "non_compliant", "review_required", "unknown"] = "unknown"
    """Policy compliance status."""
    
    security_status: Literal["authorized", "unauthorized", "review_required", "unknown"] = "unknown"
    """Security authorization status."""
    
    coordination_completeness: Literal["complete", "partial", "blocked"] = "partial"
    """Coordination completeness assessment."""
    
    action_selection_readiness: Literal[
        "not_ready", "ready", "ready_with_conditions", "blocked"
    ] = "not_ready"
    """Action Selection readiness assessment."""
    
    execution_readiness_status: Literal[
        "not_ready", "ready_for_review", "ready_with_conditions", "blocked"
    ] = "not_ready"
    """Execution-readiness status."""
    
    latest_transition_kind: Optional[str] = None
    """Kind of the latest Decision transition."""
    
    latest_outcome_ref: Optional[str] = None
    """Reference to the latest outcome (if any)."""
    
    unresolved_blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Unresolved blockers affecting coordination or Action Selection."""


# =============================================================================
# EXECUTIVE DECISION HISTORY ENTRY
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionHistoryEntry:
    """
    Immutable history entry for Decision lifecycle events.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: History is bounded (not unlimited).
    """
    
    entry_id: str = field(default_factory=lambda: f"history_entry_{id(object())}")
    """Unique identifier for this entry."""
    
    decision_identity: Optional[str] = None
    """Decision Identity associated with this event."""
    
    decision_revision_ref: int = 1
    """Revision number at time of event."""
    
    event_kind: Literal[
        "DECISION_CREATED", "DECISION_RECOMMENDED", "DECISION_APPROVED",
        "DECISION_COMMITTED", "DECISION_REVIEWED", "DECISION_REVISED",
        "DECISION_SUSPENDED", "DECISION_RESTORED", "DECISION_REPLACED",
        "DECISION_TERMINATED", "DECISION_EXPIRED", "DECISION_COMPLETED",
        "DECISION_FAILED", "COORDINATION_REQUESTED", "PROJECTION_PREPARED",
        "TARGET_RESPONSE_RECEIVED", "ACTION_SELECTION_REQUESTED",
        "ACTION_SELECTION_COMPLETED", "ACTION_SELECTION_REJECTED",
        "EXECUTION_REVIEW_READY", "EXECUTION_REVIEW_BLOCKED",
        "OUTCOME_RECORDED", "LEARNING_REVIEW_REQUESTED"
    ] = "DECISION_CREATED"
    
    referenced_artifact: Optional[str] = None
    """Artifact that triggered this event (if any)."""
    
    source_owner: str = "external"
    """Owner of the artifact that produced this event."""
    
    source_authority: Optional[str] = None
    """Authority that validated this event."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"event_time_{id(object())}")
    """Reference to semantic time of event."""
    
    causal_parent_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to prior events in causal chain."""
    
    prior_state_ref: Optional[str] = None
    """State reference before this event."""
    
    resulting_state_ref: Optional[str] = None
    """State reference after this event."""
    
    privacy_scope: str = "public"
    """Privacy scope of this entry."""
    
    provenance_ref: str = field(default_factory=lambda: f"entry_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# EXECUTIVE DECISION LINEAGE
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionLineage:
    """
    Immutable lineage of Decision relationships.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Lineage is immutable once established.
    """
    
    lineage_id: str = field(default_factory=lambda: f"lineage_{id(object())}")
    """Unique identifier for this lineage."""
    
    source_decision_identity: Optional[str] = None
    """Source Decision Identity."""
    
    target_decision_identity: Optional[str] = None
    """Target Decision Identity."""
    
    relation_kind: Literal[
        "REVISION_OF", "DERIVED_FROM", "SUPPORTS", "SUPPORTED_BY",
        "SPECIALIZES", "GENERALIZES", "DEPENDS_ON", "PRECEDES", "FOLLOWS",
        "REPLACES", "REPLACED_BY", "SUPERSEDES", "SUPERSEDED_BY",
        "FALLBACK_FOR", "RECOVERY_FOR", "SUSPENDS", "RESTORES",
        "INVALIDATES", "CONTINUES", "TERMINATES"
    ] = "REVISION_OF"
    
    provenance_ref: str = field(default_factory=lambda: f"lineage_prov_{id(object())}")
    """Reference to provenance trail."""
    
    @property
    def is_revision_lineage(self) -> bool:
        """True if this is revision lineage (same Decision Identity)."""
        return self.relation_kind == "REVISION_OF"
    
    @property
    def is_succession_lineage(self) -> bool:
        """True if this is succession lineage (different Decision identities)."""
        return self.relation_kind in ("REPLACES", "SUPERSEDES")


# =============================================================================
# EXECUTIVE DECISION DELTA
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionDelta:
    """
    Immutable semantic difference between two states.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Delta never mutates source artifacts.
    """
    
    delta_id: str = field(default_factory=lambda: f"delta_{id(object())}")
    """Unique identifier for this delta."""
    
    kind: Literal[
        "CREATE", "REVISE", "COMMIT", "SUSPEND", "RESTORE", "REPLACE",
        "TERMINATE", "EXPIRE", "COMPLETE", "FAIL",
        "ADD_CONSTRAINT", "REMOVE_CONSTRAINT", "REVISE_CONSTRAINT",
        "ADD_ASSUMPTION", "INVALIDATE_ASSUMPTION",
        "ADD_DEPENDENCY", "REMOVE_DEPENDENCY",
        "ADD_EVIDENCE", "ADD_JUSTIFICATION",
        "CHANGE_AUTHORITY", "CHANGE_SCOPE", "CHANGE_HORIZON",
        "CHANGE_STABILITY", "CHANGE_CONTINUATION"
    ] = "CREATE"
    
    source_decision_identity: Optional[str] = None
    """Source Decision Identity."""
    
    source_revision_ref: int = 1
    """Source revision number."""
    
    target_revision_ref: Optional[int] = None
    """Target revision number (if applicable)."""
    
    changed_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Names of fields that changed."""
    
    unchanged_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that must be preserved (if any)."""
    
    reason: str = ""
    """Reason for this delta."""
    
    evidence_ref: Optional[str] = None
    """Evidence supporting this delta."""
    
    authority_required: Optional[str] = None
    """Authority required to apply this delta."""
    
    continuity_preserved: bool = True
    """True if semantic continuity is preserved."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"delta_time_{id(object())}")
    """Reference to semantic time."""
    
    provenance_ref: str = field(default_factory=lambda: f"delta_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# EXECUTIVE DECISION TRANSITION
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionTransition:
    """
    Immutable accepted transition between Decision States.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Transition must be validated before acceptance.
    """
    
    transition_id: str = field(default_factory=lambda: f"transition_{id(object())}")
    """Unique identifier for this transition."""
    
    revision: int = 1
    """Revision number of the transition schema."""
    
    decision_identity: Optional[str] = None
    """Decision Identity being transitioned."""
    
    source_decision_revision_ref: int = 1
    """Source revision number."""
    
    target_decision_revision_ref: Optional[int] = None
    """Target revision number (if applicable)."""
    
    source_state: Literal[
        "DRAFT", "CANDIDATE", "RECOMMENDED", "APPROVED", "COMMITTED",
        "SUSPENDED", "RESTORED", "REPLACED", "COMPLETED", "TERMINATED",
        "ARCHIVED"
    ] = "DRAFT"
    
    target_state: Literal[
        "DRAFT", "CANDIDATE", "RECOMMENDED", "APPROVED", "COMMITTED",
        "SUSPENDED", "RESTORED", "REPLACED", "COMPLETED", "TERMINATED",
        "ARCHIVED"
    ] = "DRAFT"
    
    kind: Literal[
        "CREATE", "RECOMMEND", "APPROVE", "COMMIT", "ACTIVATE_SEMANTICALLY",
        "REVIEW", "MAINTAIN", "REVISE", "SUSPEND", "RESTORE", "REPLACE",
        "SUPERSEDE", "EXPIRE", "COMPLETE", "FAIL", "TERMINATE", "INVALIDATE",
        "DEFER", "REJECT"
    ] = "CREATE"
    
    delta_ref: Optional[str] = None
    """Reference to the Delta that caused this transition."""
    
    authority_review: Optional[str] = None
    """Reference to authority review (if any)."""
    
    continuity_assessment: Literal[
        "preserved", "modified", "broken", "unknown"
    ] = "unknown"
    
    invalidated_products: Tuple[str, ...] = field(default_factory=tuple)
    """References to downstream products that become stale."""
    
    preserved_products: Tuple[str, ...] = field(default_factory=tuple)
    """References to downstream products that remain valid."""
    
    required_follow_up: Tuple[str, ...] = field(default_factory=tuple)
    """Required follow-up actions or coordination."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"trans_time_{id(object())}")
    """Reference to semantic time."""
    
    provenance_ref: str = field(default_factory=lambda: f"trans_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# EXECUTIVE DECISION CONTINUATION
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionContinuation:
    """
    Advisory continuation specification.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Continuation performs no runtime work.
    """
    
    continuation_id: str = field(default_factory=lambda: f"continuation_{id(object())}")
    """Unique identifier for this continuation."""
    
    decision_identity: Optional[str] = None
    """Decision Identity that this applies to."""
    
    decision_revision_ref: int = 1
    """Revision number of the Decision."""
    
    kind: Literal[
        "COMPLETE", "CONTINUE_COORDINATION", "REQUEST_CONTEXT_REFRESH",
        "REQUEST_DECISION_REVIEW", "REQUEST_STRATEGY_REVIEW", "REQUEST_PLANNING",
        "REQUEST_REASONING", "REQUEST_GOAL_REVIEW", "REQUEST_COMMITMENT_REVIEW",
        "REQUEST_POLICY_REVIEW", "REQUEST_SECURITY_REVIEW",
        "REQUEST_ALERTING_REVIEW", "REQUEST_FOCUSING_REVIEW",
        "REQUEST_DEFAULT_NETWORK_REVIEW", "REQUEST_MEMORY",
        "REQUEST_WORKING_MEMORY_REVIEW", "REQUEST_WORKSPACE_REVIEW",
        "REQUEST_MONITORING", "REQUEST_RECOVERY", "REQUEST_LEARNING_REVIEW",
        "REQUEST_ACTION_SELECTION", "REVIEW_ACTION_SELECTION_OUTCOME",
        "REQUEST_EXECUTION_REVIEW", "WAIT_FOR_CONTEXT", "WAIT_FOR_EVIDENCE",
        "WAIT_FOR_AUTHORITY", "WAIT_FOR_PRODUCT", "WAIT_FOR_ACTION_SELECTION",
        "WAIT_FOR_EXECUTION_OUTCOME", "SUSPEND", "FAIL", "CANCEL"
    ] = "COMPLETE"
    
    target_ref: Optional[str] = None
    """Target subsystem that should act (if any)."""
    
    required_products: FrozenSet[str] = field(default_factory=frozenset)
    """Products that must be available before continuing."""
    
    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must hold for continuation."""
    
    blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Blocking conditions that must be resolved."""
    
    authority_required: Optional[str] = None
    """Authority required to continue (if any)."""
    
    expiration_ref: str = field(default_factory=lambda: f"cont_exp_{id(object())}")
    """Reference under which continuation expires."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"cont_time_{id(object())}")
    """Reference to semantic time."""
    
    provenance_ref: str = field(default_factory=lambda: f"cont_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# COORDINATION PLAN
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationPlan:
    """
    Declarative coordination plan.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Plan contains no callbacks or runtime commands.
    """
    
    plan_id: str = field(default_factory=lambda: f"coord_plan_{id(object())}")
    """Unique identifier for this plan."""
    
    decision_ref: Optional[str] = None
    """Reference to Decision being coordinated."""
    
    stage_sequence: Tuple["CoordinationStage", ...] = field(default_factory=tuple)
    """Ordered sequence of coordination stages."""
    
    validation_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Validation requirements for each stage."""
    
    target_resolution: Optional[str] = None
    """Reference to target resolution output."""
    
    disclosure_assessment: Optional[str] = None
    """Reference to minimal-disclosure assessment."""
    
    action_selection_readiness_check: Optional[str] = None
    """Reference to Action Selection readiness check."""
    
    completion_assessment: Optional[str] = None
    """Reference to coordination completion assessment."""


# =============================================================================
# COORDINATION STAGE
# =============================================================================

@dataclass(frozen=True)
class CoordinationStage:
    """
    Single stage in a coordination plan.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Stage contains no runtime commands.
    """
    
    stage_id: str = field(default_factory=lambda: f"coord_stage_{id(object())}")
    """Unique identifier for this stage."""
    
    kind: Literal[
        "VALIDATE_COORDINATION_REQUEST", "VALIDATE_DECISION_COMMITMENT",
        "VALIDATE_DECISION_REVISION", "VALIDATE_DECISION_STATE",
        "VALIDATE_AUTHORITY", "VALIDATE_POLICY", "VALIDATE_SECURITY",
        "RESOLVE_TARGETS", "ASSESS_DISCLOSURE",
        "PREPARE_STRATEGY_PROJECTION", "PREPARE_PLANNING_REQUEST",
        "PREPARE_REASONING_REQUEST", "PREPARE_GOAL_PROJECTION",
        "PREPARE_COMMITMENT_PROJECTION", "PREPARE_POLICY_REVIEW_REQUEST",
        "PREPARE_SECURITY_REVIEW_REQUEST", "PREPARE_ALERTING_PROJECTION",
        "PREPARE_FOCUSING_PROJECTION", "PREPARE_DEFAULT_NETWORK_PROJECTION",
        "PREPARE_MEMORY_REQUEST", "PREPARE_WORKING_MEMORY_REQUEST",
        "PREPARE_WORKSPACE_REQUEST", "PREPARE_MONITORING_REQUEST",
        "PREPARE_RECOVERY_REQUEST", "PREPARE_LEARNING_REQUEST",
        "VALIDATE_TARGET_RESPONSES", "ASSESS_COORDINATION_COMPLETENESS",
        "ASSESS_ACTION_SELECTION_READINESS", "PREPARE_ACTION_SELECTION_REQUEST",
        "VALIDATE_ACTION_SELECTION_REQUEST", "VALIDATE_ACTION_SELECTION_OUTCOME",
        "ASSESS_SELECTED_ACTION_COMPATIBILITY",
        "ASSESS_EXECUTION_REVIEW_READINESS", "COMPOSE_DECISION_DELTA",
        "COMPOSE_DECISION_TRANSITION", "COMPOSE_DECISION_CONTINUATION",
        "COMPOSE_COORDINATION_OUTCOME"
    ] = "VALIDATE_COORDINATION_REQUEST"
    
    requires: Tuple[str, ...] = field(default_factory=tuple)
    """Preconditions that must be satisfied."""
    
    produces: Tuple[str, ...] = field(default_factory=tuple)
    """Outputs produced by this stage."""
    
    blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Blocking conditions for this stage."""


# =============================================================================
# DOWNSTREAM INVALIDATION
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionDownstreamInvalidation:
    """
    Specification of downstream product invalidation.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    invalidation_id: str = field(default_factory=lambda: f"invalidate_{id(object())}")
    """Unique identifier for this invalidation."""
    
    invalidates_product_ref: str = field(default_factory=lambda: f"invalidated_prod_{id(object())}")
    """Reference to the invalidated product."""
    
    reason: Literal[
        "DECISION_REVISION_CHANGED", "DECISION_SUSPENDED", "DECISION_REPLACED",
        "DECISION_TERMINATED", "DECISION_EXPIRED", "CONTEXT_STALE",
        "STRATEGY_CHANGED", "POLICY_CHANGED", "SECURITY_CHANGED",
        "AUTHORITY_CHANGED", "PLAN_STALE", "REASONING_STALE",
        "ACTION_SELECTION_STALE", "SELECTED_ACTION_STALE",
        "EXECUTION_CONTEXT_STALE", "PRIVACY_SCOPE_CHANGED"
    ] = "DECISION_REVISION_CHANGED"
    
    decision_ref: Optional[str] = None
    """Decision that caused invalidation."""
    
    decision_revision_ref: int = 1
    """Revision number at time of invalidation."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"invalidate_time_{id(object())}")
    """Reference to semantic time."""
    
    provenance_ref: str = field(default_factory=lambda: f"invalidate_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# COORDINATION REPLAY RECORD
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationReplayRecord:
    """
    Immutable replay record for coordination reconstruction.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Replay performs no external work.
    """
    
    record_id: str = field(default_factory=lambda: f"replay_rec_{id(object())}")
    """Unique identifier for this record."""
    
    original_request_ref: Optional[str] = None
    """Reference to original coordination request."""
    
    target_resolution: Tuple["TargetResolution", ...] = field(default_factory=tuple)
    """Record of target resolution results."""
    
    projection_generation: Tuple["ProjectionGeneration", ...] = field(default_factory=tuple)
    """Record of projection generation."""
    
    disclosure_assessment: Optional[str] = None
    """Record of minimal-disclosure assessment."""
    
    returned_products: Tuple[str, ...] = field(default_factory=tuple)
    """Record of received products."""
    
    coordination_completeness: str = ""
    """Record of completeness assessment."""
    
    action_selection_readiness: str = ""
    """Record of Action Selection readiness assessment."""
    
    action_selection_request_ref: Optional[str] = None
    """Reference to prepared Action Selection request (if any)."""
    
    @property
    def can_reconstruct(self) -> bool:
        """True if this record can fully reconstruct coordination."""
        return len(self.target_resolution) > 0 and self.coordination_completeness != ""


# =============================================================================
# TARGET RESOLUTION
# =============================================================================

@dataclass(frozen=True)
class TargetResolution:
    """
    Record of target subsystem resolution.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    target_ref: str = field(default_factory=lambda: f"resolved_target_{id(object())}")
    """Reference to resolved target."""
    
    decision_identity: Optional[str] = None
    """Decision Identity being coordinated."""
    
    decision_revision_ref: int = 1
    """Revision number at resolution time."""
    
    projection_count: int = 0
    """Number of projections prepared for this target."""
    
    response_received: bool = False
    """True if response was received."""
    
    response_kind: Optional[str] = None
    """Kind of response received (if any)."""
    
    acceptance_status: Literal["accepted", "conditionally_accepted", "rejected"] = "accepted"
    """Target's acceptance status."""


# =============================================================================
# PROJECTION GENERATION
# =============================================================================

@dataclass(frozen=True)
class ProjectionGeneration:
    """
    Record of projection generation for a target.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    projection_ref: str = field(default_factory=lambda: f"generated_proj_{id(object())}")
    """Reference to generated projection."""
    
    target_ref: str = field(default_factory=lambda: f"projection_target_{id(object())}")
    """Target subsystem reference."""
    
    decision_identity: Optional[str] = None
    """Decision Identity being projected."""
    
    decision_revision_ref: int = 1
    """Revision number at generation time."""
    
    projection_kind: Literal[
        "REQUIREMENT_PROJECTION", "CONSTRAINT_PROJECTION", "CONTEXT_PROJECTION",
        "EVIDENCE_REQUEST", "ANALYSIS_REQUEST", "PLAN_REQUEST", "REVIEW_REQUEST",
        "AUTHORITY_REQUEST", "MAINTENANCE_REQUEST", "RECONFIGURATION_REQUEST",
        "MONITORING_REQUEST", "RECOVERY_REQUEST", "LEARNING_REVIEW_REQUEST",
        "ACTION_SELECTION_REQUEST_PREPARATION", "STATE_INTEGRATION",
        "CONTINUATION_COORDINATION", "OUTCOME_COORDINATION"
    ] = "REQUIREMENT_PROJECTION"
    
    minimal_disclosure: bool = True
    """True if minimal-disclosure semantics applied."""
    
    privacy_scope: str = "public"
    """Privacy scope of projection."""