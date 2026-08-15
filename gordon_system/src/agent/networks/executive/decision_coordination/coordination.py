# Gordon Executive Decision Coordination Contracts - Phase 4.4.10C Part 1
# =======================================================================

"""
Decision Coordination Contract Types.

This module defines the canonical contract types used for decision coordination.
All contracts are immutable, runtime-neutral, and preserve subsystem ownership.

ARCHITECTURAL PRINCIPLES:
========================

IMMUTABILITY:
    Every contract is frozen at creation. No mutation is possible after
    instantiation. This ensures determinism across all coordination rounds.

RUNTIME-NEUTRALITY:
    Contracts contain no runtime state, no callbacks, no schedulers,
    no coroutines, no threads, and no external references.

BOUNDEDNESS:
    All collections are bounded. Unbounded growth would break determinism
    and replay capability.

DETERMINISM:
    Given identical inputs, the same outputs must be produced every time.
    This enables replay validation and property testing.

OWNERSHIP-PRESERVING:
    No subsystem ownership is transferred through contracts. Every target
    retains full control over its internal implementation.

COOKED DATA FLOW:
================

ExecutiveDecisionCoordinationRequest
         ↓ (targets + requirements)
TargetProjections (one per target)
         ↓ (returned products)
CoordinationResponses (one per target)
         ↓ (validation)
CoordinationOutcome
         ↓ (readiness assessment)
ActionSelectionRequest (terminal Executive product)

NO RUNTIME:
===========
- No callbacks
- No coroutines
- No threads/processes
- No schedulers
- No asyncio constructs
- No external provider references
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional, Literal, FrozenSet
from enum import Enum, auto


# =============================================================================
# DECISION COORDINATION SUBJECT
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationSubject:
    """
    Immutable coordination subject reference.
    
    This identifies WHAT is being coordinated (e.g., a Decision Commitment,
    revision, or continuation).
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    kind: ExecutiveDecisionCoordinationSubjectKind
    """The type of coordination subject."""
    
    decision_identity: Optional[str] = None
    """Reference to the Decision Identity (if applicable)."""
    
    decision_revision: Optional[int] = 1
    """Revision number being coordinated."""
    
    subject_id: str = field(default_factory=lambda: f"coord_subject_{id(object())}")
    """Unique identifier for this subject reference."""


# =============================================================================
# DECISION COORDINATION TARGET
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationTarget:
    """
    Immutable coordination target reference.
    
    This identifies WHICH subsystem will participate in coordination while
    retaining full ownership of its implementation.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    kind: ExecutiveDecisionCoordinationTargetKind
    """The type of coordination target."""
    
    target_id: Optional[str] = None
    """Optional unique identifier for the target instance."""
    
    revision: Optional[int] = None
    """Optional revision number for the target state reference."""
    
    owner_system: str = "external"
    """Identifier for the subsystem owner (preserved but not owned by Executive)."""
    
    authority_required: Literal["none", "advisory", "binding"] = "none"
    """Level of authority required from this target."""
    
    def __post_init__(self):
        # Validate that kind and owner are consistent
        if self.kind in (
            ExecutiveDecisionCoordinationTargetKind.PLANNING,
            ExecutiveDecisionCoordinationTargetKind.REASONING,
        ):
            object.__setattr__(self, "owner_system", "planning_reasoning")
        
        elif self.kind in (
            ExecutiveDecisionCoordinationTargetKind.GOAL_SYSTEM,
            ExecutiveDecisionCoordinationTargetKind.COMMITMENT_SYSTEM,
        ):
            object.__setattr__(self, "owner_system", "goal_commitment")
        
        elif self.kind == ExecutiveDecisionCoordinationTargetKind.ACTION_SELECTION:
            object.__setattr__(self, "owner_system", "action_selection")
        
        elif self.kind == ExecutiveDecisionCoordinationTargetKind.EXECUTION:
            object.__setattr__(self, "owner_system", "execution")


# =============================================================================
# DECISION COORDINATION REQUIREMENT
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationRequirement:
    """
    Immutable coordination requirement.
    
    This expresses WHAT a downstream target must consider, preserve, review,
    or return as part of coordination.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    kind: ExecutiveDecisionCoordinationRequirementKind
    """The type of requirement."""
    
    source_decision_identity: Optional[str] = None
    """Identity of the Decision that requires this."""
    
    source_revision: int = 1
    """Revision number of the Decision."""
    
    target_ref: str = field(default_factory=lambda: f"target_{id(object())}")
    """Reference to the target subsystem."""
    
    mandatory: bool = True
    """Whether this requirement must be satisfied for coordination completion."""
    
    authority_required: Optional[str] = None
    """Authority that must validate satisfaction (if any)."""
    
    satisfaction_condition: str = ""
    """Condition that must hold for satisfaction."""
    
    expiration_context: str = ""
    """Context under which this requirement expires or needs review."""
    
    provenance_ref: str = field(default_factory=lambda: f"prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# DECISION COORDINATION CONSTRAINT
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationConstraint:
    """
    Immutable coordination constraint.
    
    This expresses a bound on downstream processing that must be preserved.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    source_kind: Literal["decision", "strategy", "goal", "commitment", "policy", "security"] = "decision"
    """Source of the constraint."""
    
    source_id: Optional[str] = None
    """Identifier for the source artifact."""
    
    constraint_text: str = ""
    """The actual constraint (e.g., policy rule, security requirement)."""
    
    authority_required: Optional[str] = None
    """Authority that established this constraint."""
    
    scope_limitation: bool = False
    """True if this constraint limits downstream scope."""
    
    invalidates_downstream: bool = False
    """True if violation invalidates downstream products."""


# =============================================================================
# DECISION COORDINATION DEPENDENCY
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationDependency:
    """
    Immutable coordination dependency.
    
    This expresses semantic dependencies between coordination activities.
    Dependencies are NOT runtime task dependencies.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    kind: Literal[
        "REQUIRES", "PRECEDES", "FOLLOWS",
        "DEPENDS_ON_CONTEXT", "DEPENDS_ON_PLAN", "DEPENDS_ON_REASONING",
        "DEPENDS_ON_POLICY", "DEPENDS_ON_SECURITY", "DEPENDS_ON_AUTHORITY",
        "DEPENDS_ON_MEMORY", "DEPENDS_ON_WORKSPACE", "DEPENDS_ON_MONITORING",
        "DEPENDS_ON_RECOVERY", "DEPENDS_ON_LEARNING", "DEPENDS_ON_ACTION_SELECTION",
        "BLOCKED_BY", "ENABLES", "INVALIDATES", "SUPERSEDES"
    ] = "REQUIRES"
    
    dependency_ref: str = field(default_factory=lambda: f"dep_{id(object())}")
    """Reference to the dependent artifact."""
    
    dependency_kind: Optional[str] = None
    """Kind of the dependent artifact (if known)."""
    
    semantic_only: bool = True
    """True if this is purely semantic, not runtime-related."""


# =============================================================================
# DECISION COORDINATION PROJECTION
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionProjection:
    """
    Immutable decision projection to a target subsystem.
    
    A projection expresses the subset of Decision context that a specific
    target needs to know. This follows minimal-disclosure semantics.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    projection_id: ExecutiveDecisionProjectionId
    """Unique identifier for this projection."""
    
    revision: int = 1
    """Revision number of the projection schema."""
    
    schema_version: str = "1.0.0"
    """Schema version of this projection type."""
    
    decision_identity: Optional[str] = None
    """Identity of the Decision being projected."""
    
    decision_revision_ref: Tuple[int, ...] = field(default_factory=tuple)
    """Revision references that this projection covers."""
    
    commitment_reference: Optional[str] = None
    """Reference to the accepted commitment (if any)."""
    
    target: ExecutiveDecisionCoordinationTarget
    """The target subsystem receiving this projection."""
    
    purpose: ExecutiveDecisionCoordinationPurpose
    """Purpose of this projection."""
    
    kind: ExecutiveDecisionCoordinationKind
    """Kind of coordination activity."""
    
    context_reference: Optional[str] = None
    """Reference to coordination context (if any)."""
    
    scope: str = ""
    """Bounded scope of this projection."""
    
    requirements: Tuple[ExecutiveDecisionCoordinationRequirement, ...] = field(default_factory=tuple)
    """Requirements imposed on target."""
    
    constraints: Tuple[ExecutiveDecisionCoordinationConstraint, ...] = field(default_factory=tuple)
    """Constraints that must be preserved."""
    
    dependencies: Tuple[ExecutiveDecisionCoordinationDependency, ...] = field(default_factory=tuple)
    """Dependencies required for this projection."""
    
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from target."""
    
    acceptance_conditions: Tuple["AcceptanceCondition", ...] = field(default_factory=tuple)
    """Conditions under which target may accept."""
    
    completion_conditions: Tuple["CompletionCondition", ...] = field(default_factory=tuple)
    """Conditions under which coordination completes."""
    
    authority_context: Optional[str] = None
    """Authority context for this projection."""
    
    privacy_scope: str = "public"
    """Privacy scope of this projection (public, protected, private)."""
    
    provenance_ref: str = field(default_factory=lambda: f"proj_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# ACCEPTANCE AND COMPLETION CONDITIONS
# =============================================================================

@dataclass(frozen=True)
class AcceptanceCondition:
    """
    Condition under which a target may accept coordination.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    condition_text: str = ""
    """Text description of the acceptance condition."""
    
    mandatory: bool = False
    """True if acceptance requires this condition to be met."""


@dataclass(frozen=True)
class CompletionCondition:
    """
    Condition under which coordination with a target completes.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    condition_text: str = ""
    """Text description of the completion condition."""
    
    product_kind_required: Optional[str] = None
    """Required product kind for completion (if any)."""


# =============================================================================
# DECISION COORDINATION REQUEST
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationRequest:
    """
    Immutable coordination request.
    
    This is the canonical input to Decision Coordination. It specifies what
    decisions should be coordinated with which targets and what requirements
    must be satisfied.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: At least one target must be specified.
    INVARIANT: All projections must reference a valid Decision Commitment.
    """
    
    request_id: ExecutiveDecisionCoordinationRequestId = field(default_factory=ExecutiveDecisionCoordinationRequestId.generate)
    """Unique identifier for this coordination request."""
    
    revision: int = 1
    """Revision number of the request schema."""
    
    schema_version: str = "1.0.0"
    """Schema version of this request type."""
    
    purpose: ExecutiveDecisionCoordinationPurpose
    """Overall purpose of this coordination."""
    
    subject: ExecutiveDecisionCoordinationSubject
    """What is being coordinated."""
    
    decision_commitment_reference: Optional[str] = None
    """Reference to the Decision Commitment (if any)."""
    
    executive_state_reference: Optional[str] = None
    """Reference to current Executive State (for revision tracking)."""
    
    executive_context_reference: Optional[str] = None
    """Reference to current Executive Context (if applicable)."""
    
    targets: Tuple[ExecutiveDecisionCoordinationTarget, ...] = field(default_factory=tuple)
    """Subsystems that should participate in coordination."""
    
    required_projections: FrozenSet[str] = field(default_factory=frozenset)
    """Projection kinds that must be prepared."""
    
    existing_products: Tuple["ProductReference", ...] = field(default_factory=tuple)
    """Products already available from prior coordination."""
    
    scope: str = ""
    """Bounded scope of this coordination (max targets, products, etc.)."""
    
    authority_context: Optional[str] = None
    """Authority context for validation."""
    
    completion_requirements: "CompletionRequirements" = field(default_factory=lambda: CompletionRequirements(min_required_targets=1))
    """Requirements for marking coordination complete."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"time_{id(object())}")
    """Reference to semantic time (not wall-clock)."""
    
    privacy_scope: str = "public"
    """Privacy scope for all projections in this request."""
    
    provenance_ref: str = field(default_factory=lambda: f"req_prov_{id(object())}")
    """Reference to provenance trail."""
    
    def __post_init__(self):
        # Ensure at least one target is specified
        if not self.targets:
            raise ValueError("ExecutiveDecisionCoordinationRequest must specify at least one target")


# =============================================================================
# PRODUCT REFERENCES
# =============================================================================

@dataclass(frozen=True)
class ProductReference:
    """
    Reference to a coordination product.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    product_id: str = field(default_factory=lambda: f"prod_{id(object())}")
    """Identifier for the product."""
    
    kind: str = ""
    """Kind of product (e.g., 'plan', 'reasoning_result')."""
    
    source_ref: Optional[str] = None
    """Reference to originating coordination."""
    
    revision: int = 1
    """Revision number."""


# =============================================================================
# COMPLETION REQUIREMENTS
# =============================================================================

@dataclass(frozen=True)
class CompletionRequirements:
    """
    Requirements for marking coordination complete.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    min_required_targets: int = 1
    """Minimum number of targets that must respond."""
    
    all_mandatory_requirements_satisfied: bool = True
    """Whether all mandatory requirements must be satisfied."""
    
    timeout_seconds: Optional[int] = None
    """Maximum time for coordination (None means no timeout)."""
    
    allow_partial_completion: bool = False
    """True if partial completion is acceptable."""


# =============================================================================
# DECISION COORDINATION RESPONSE
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationResponse:
    """
    Immutable response from a target subsystem.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    response_id: ExecutiveDecisionCoordinationResponseId = field(default_factory=ExecutiveDecisionCoordinationResponseId.generate)
    """Unique identifier for this response."""
    
    revision: int = 1
    """Revision number of the response schema."""
    
    originating_request_ref: Optional[str] = None
    """Reference to originating coordination request."""
    
    originating_projection_ref: Optional[str] = None
    """Reference to originating projection."""
    
    decision_identity: Optional[str] = None
    """Decision Identity being coordinated."""
    
    decision_revision_ref: int = 1
    """Revision number of the Decision."""
    
    target_owner: str = "external"
    """Owner system that produced this response."""
    
    authority_context: Optional[str] = None
    """Authority context for validation."""
    
    kind: Literal[
        "ACCEPTED", "ACCEPTED_WITH_CONDITIONS", "PARTIALLY_ACCEPTED",
        "PRODUCT_RETURNED", "MULTIPLE_PRODUCTS_RETURNED",
        "CONFLICT_IDENTIFIED", "MISSING_CONTEXT", "MISSING_AUTHORITY",
        "MISSING_EVIDENCE", "POLICY_REVIEW_REQUIRED", "SECURITY_REVIEW_REQUIRED",
        "STALE_REQUEST", "STALE_DECISION_REVISION", "UNSUPPORTED_REQUEST",
        "REJECTED", "DEFERRED", "EXPIRED", "FAILED"
    ] = "ACCEPTED"
    
    returned_products: Tuple["ReturnedProduct", ...] = field(default_factory=tuple)
    """Products returned by target."""
    
    acceptance_status: Literal["accepted", "conditionally_accepted", "rejected"] = "accepted"
    """Status of target's acceptance."""
    
    completeness: Literal["complete", "partial", "insufficient"] = "complete"
    """Completeness of the response."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on the response (if any)."""
    
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Any identified conflicts with coordination requirements."""
    
    missing_inputs: Tuple[str, ...] = field(default_factory=tuple)
    """Inputs that were missing or insufficient."""
    
    continuation_recommendation: Optional[str] = None
    """Recommended next step (if any)."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"resp_time_{id(object())}")
    """Reference to semantic time."""
    
    privacy_scope: str = "public"
    """Privacy scope of this response."""
    
    provenance_ref: str = field(default_factory=lambda: f"resp_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# RETURNED PRODUCTS
# =============================================================================

@dataclass(frozen=True)
class ReturnedProduct:
    """
    Product returned by a target subsystem.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    product_id: str = field(default_factory=lambda: f"ret_prod_{id(object())}")
    """Identifier for the product."""
    
    kind: Literal[
        "DECISION_PROJECTION", "STRATEGY_COORDINATION_PROJECTION",
        "PLANNING_REQUEST", "REASONING_REQUEST", "GOAL_COORDINATION_PROJECTION",
        "COMMITMENT_COORDINATION_PROJECTION", "POLICY_REVIEW_REQUEST",
        "SECURITY_REVIEW_REQUEST", "ALERTING_REVIEW_PROJECTION",
        "FOCUSING_REVIEW_PROJECTION", "DEFAULT_NETWORK_PROJECTION",
        "MEMORY_REQUEST", "WORKING_MEMORY_SUPPORT_PROPOSAL",
        "WORKSPACE_REVIEW_PROPOSAL", "MONITORING_REQUEST",
        "RECOVERY_REQUEST", "LEARNING_REVIEW_REQUEST",
        "EXECUTIVE_STATE_DELTA_PROPOSAL", "DECISION_CONTINUATION",
        "ACTION_SELECTION_REQUEST", "COORDINATION_CONFLICT",
        "COORDINATION_DIAGNOSTIC", "NO_MEANINGFUL_RESULT"
    ] = "NO_MEANINGFUL_RESULT"
    
    validity: Literal["valid", "stale", "invalid"] = "valid"
    """Validity status of the product."""
    
    completeness: Literal["complete", "partial", "insufficient"] = "complete"
    """Completeness of the product."""
    
    authority_required: Optional[str] = None
    """Authority requirement for this product."""
    
    privacy_scope: str = "public"
    """Privacy scope of the product."""
    
    provenance_ref: str = field(default_factory=lambda: f"ret_prod_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# DECISION COORDINATION OUTCOME
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionCoordinationOutcome:
    """
    Immutable coordination outcome.
    
    This is the result of a complete coordination round. It summarizes what
    projections were prepared, which responses were received, and whether
    Action Selection readiness was achieved.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    outcome_id: ExecutiveDecisionCoordinationOutcomeId = field(default_factory=ExecutiveDecisionCoordinationOutcomeId.generate)
    """Unique identifier for this outcome."""
    
    revision: int = 1
    """Revision number of the outcome schema."""
    
    request_reference: Optional[str] = None
    """Reference to originating coordination request."""
    
    decision_identity: Optional[str] = None
    """Decision Identity being coordinated."""
    
    decision_revision_ref: int = 1
    """Revision number of the Decision."""
    
    commitment_reference: Optional[str] = None
    """Reference to accepted Decision Commitment (if any)."""
    
    kind: Literal[
        "PROJECTIONS_PREPARED", "PROJECTIONS_PARTIALLY_PREPARED",
        "TARGET_ACKNOWLEDGEMENTS_PENDING", "MANDATORY_PRODUCT_PENDING",
        "PLANNING_REQUIRED", "REASONING_REQUIRED", "POLICY_REVIEW_REQUIRED",
        "SECURITY_REVIEW_REQUIRED", "ATTENTION_REVIEW_REQUIRED",
        "WORKING_MEMORY_SUPPORT_REQUIRED", "WORKSPACE_REVIEW_REQUIRED",
        "MONITORING_REQUIRED", "RECOVERY_REQUIRED", "LEARNING_REVIEW_REQUIRED",
        "ACTION_SELECTION_REQUEST_READY", "ACTION_SELECTION_REQUEST_PREPARED",
        "ACTION_SELECTION_REQUEST_BLOCKED", "DECISION_COORDINATION_COMPLETE",
        "DECISION_COORDINATION_PARTIAL", "WAITING_FOR_CONTEXT",
        "WAITING_FOR_AUTHORITY", "WAITING_FOR_PRODUCTS",
        "COORDINATION_CONFLICT_IDENTIFIED", "NO_MEANINGFUL_RESULT",
        "FAILED", "CANCELLED", "EXPIRED"
    ] = "PROJECTIONS_PREPARED"
    
    status: Literal[
        "SUCCESS", "PARTIAL_SUCCESS", "FAILURE", "BLOCKED",
        "WAITING", "CANCELLED", "EXPIRED"
    ] = "SUCCESS"
    
    projections: Tuple[str, ...] = field(default_factory=tuple)
    """References to prepared projections."""
    
    responses: Tuple[str, ...] = field(default_factory=tuple)
    """References to received responses."""
    
    returned_products: Tuple[str, ...] = field(default_factory=tuple)
    """References to returned products."""
    
    action_selection_request_ref: Optional[str] = None
    """Reference to prepared Action Selection request (if any)."""
    
    action_selection_outcome_ref: Optional[str] = None
    """Reference to received Action Selection outcome (if any)."""
    
    execution_readiness_projection_ref: Optional[str] = None
    """Reference to prepared Execution readiness projection (if any)."""
    
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Identified coordination conflicts."""
    
    blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Blocking conditions that must be resolved."""
    
    omissions_summary: "OmissionSummary" = field(default_factory=lambda: OmissionSummary())
    """Summary of omitted targets/products (if any)."""
    
    completeness_assessment: Literal[
        "COMPLETE", "SUBSTANTIALLY_COMPLETE", "PARTIAL",
        "BLOCKED", "MISSING_MANDATORY_TARGET", "MISSING_MANDATORY_PRODUCT",
        "MISSING_AUTHORITY", "MISSING_CONTEXT", "STALE", "INVALID"
    ] = "COMPLETE"
    
    continuation: "DecisionContinuation" = field(default_factory=lambda: DecisionContinuation(kind="COMPLETE"))
    """Recommended next coordination step."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"outcome_time_{id(object())}")
    """Reference to semantic time."""
    
    privacy_scope: str = "public"
    """Privacy scope of this outcome."""
    
    provenance_ref: str = field(default_factory=lambda: f"outcome_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# OMISSION SUMMARY
# =============================================================================

@dataclass(frozen=True)
class OmissionSummary:
    """
    Summary of omitted targets and products.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Mandatory omissions must be explicitly recorded.
    """
    
    target_omissions: Tuple[str, ...] = field(default_factory=tuple)
    """Omitted target identifiers."""
    
    product_omissions: Tuple[str, ...] = field(default_factory=tuple)
    """Omitted product kinds."""
    
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons for omissions."""
    
    is_acceptable: bool = True
    """True if omissions are acceptable (no mandatory items omitted)."""


# =============================================================================
# DECISION CONTINUATION
# =============================================================================

@dataclass(frozen=True)
class DecisionContinuation:
    """
    Advisory decision continuation specification.
    
    This describes what should happen next in the coordination flow.
    Continuation is NEVER a runtime instruction; it is advisory only.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Continuation must not invoke or schedule any work.
    """
    
    continuation_id: ExecutiveDecisionContinuationId = field(default_factory=ExecutiveDecisionContinuationId.generate)
    """Unique identifier for this continuation."""
    
    decision_identity: Optional[str] = None
    """Decision Identity that this continuation applies to."""
    
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
# ACTION SELECTION REQUEST - TERMINAL EXECUTIVE PRODUCT
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionRequest:
    """
    Immutable request for action selection.
    
    This is the TERMINAL Executive-owned product. It represents the canonical
    boundary where Executive decision-making yields to Action Selection
    capability.
    
    DO NOT contain:
        - Concrete actions
        - Selected actions
        - Executable code
        - Tool invocations
        - Runtime tasks
    
    Contains:
        - Decision references
        - Constraints and requirements
        - Scope definitions
        - Return expectations
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    request_id: ActionSelectionRequestId = field(default_factory=ActionSelectionRequestId.generate)
    """Unique identifier for this action selection request."""
    
    revision: int = 1
    """Revision number of the request schema."""
    
    schema_version: str = "1.0.0"
    """Schema version of this request type."""
    
    decision_identity: Optional[str] = None
    """Identity of the Decision that initiated this request."""
    
    decision_revision_ref: int = 1
    """Revision number of the Decision."""
    
    decision_commitment_reference: Optional[str] = None
    """Reference to accepted Decision Commitment."""
    
    subject: Literal[
        "EXECUTIVE_DECISION", "EXECUTIVE_PROGRAM", "EXECUTIVE_TASK_SET",
        "GOAL", "COMMITMENT", "STRATEGY", "PLAN", "RECOVERY", "MONITORING",
        "COMMUNICATION", "DELEGATION", "CAPABILITY_USE", "RESOURCE_OPERATION",
        "GENERAL_INTENT"
    ] = "EXECUTIVE_DECISION"
    
    purpose: Literal[
        "ADVANCE_DECISION", "SATISFY_PRECONDITION", "ACQUIRE_EVIDENCE",
        "REDUCE_UNCERTAINTY", "EXECUTE_PLAN_STEP", "FULFILL_COMMITMENT",
        "PRESERVE_POLICY_COMPLIANCE", "PRESERVE_SECURITY_COMPLIANCE",
        "RECOVER_PROGRESS", "MONITOR_STATE", "COMMUNICATE", "DELEGATE",
        "WAIT", "SUSPEND_PROGRESS", "TERMINATE_PROGRESS", "GENERAL_ACTION_SELECTION"
    ] = "ADVANCE_DECISION"
    
    scope: str = ""
    """Bounded scope of action selection (max candidates, comparisons, etc.)."""
    
    horizon_ref: Optional[str] = None
    """Reference to Decision horizon (temporal validity)."""
    
    goals: Tuple[str, ...] = field(default_factory=tuple)
    """References to related Goals."""
    
    commitments: Tuple[str, ...] = field(default_factory=tuple)
    """References to related Commitments."""
    
    strategy_reference: Optional[str] = None
    """Reference to active Strategy (if any)."""
    
    plan_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant Plans."""
    
    reasoning_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant Reasoning results."""
    
    admissibility_constraints: Tuple["ActionSelectionConstraint", ...] = field(default_factory=tuple)
    """Constraints that actions must satisfy for admissibility."""
    
    policy_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Policy constraints that must be satisfied."""
    
    security_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Security constraints that must be satisfied."""
    
    authority_requirements: Tuple["ActionAuthorityRequirement", ...] = field(default_factory=tuple)
    """Authority requirements for action selection."""
    
    required_capabilities: Tuple[str, ...] = field(default_factory=tuple)
    """Capabilities required by selected actions."""
    
    excluded_action_classes: FrozenSet[str] = field(default_factory=frozenset)
    """Action classes that must be excluded."""
    
    preferred_action_properties: Tuple["ActionPropertyPreference", ...] = field(default_factory=tuple)
    """Preferred action properties (not constraints)."""
    
    expected_outcomes: Tuple[str, ...] = field(default_factory=tuple)
    """Expected outcomes from selected actions."""
    
    unacceptable_outcomes: Tuple[str, ...] = field(default_factory=tuple)
    """Outcomes that would make an action unacceptable."""
    
    reversibility_requirement: Literal["required", "preferred", "optional"] = "optional"
    """Reversibility requirement for selected actions."""
    
    evidence_requirements: Tuple["ActionSelectionEvidenceRequirement", ...] = field(default_factory=tuple)
    """Evidence requirements for action evaluation."""
    
    return_requirements: "ActionSelectionReturnRequirements" = field(default_factory=lambda: ActionSelectionReturnRequirements())
    """Expected products from Action Selection."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"as_req_time_{id(object())}")
    """Reference to semantic time."""
    
    expiration_ref: str = field(default_factory=lambda: f"as_req_exp_{id(object())}")
    """Reference under which this request expires."""
    
    privacy_scope: str = "public"
    """Privacy scope of this request."""
    
    provenance_ref: str = field(default_factory=lambda: f"as_req_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# ACTION SELECTION CONSTRAINTS
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionConstraint:
    """
    Immutable constraint on action selection.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Constraints must preserve source authority.
    """
    
    kind: Literal[
        "GOAL_CONSTRAINT", "COMMITMENT_CONSTRAINT", "STRATEGY_CONSTRAINT",
        "PLAN_CONSTRAINT", "POLICY_CONSTRAINT", "SECURITY_CONSTRAINT",
        "AUTHORITY_CONSTRAINT", "CAPABILITY_CONSTRAINT", "RESOURCE_CONSTRAINT",
        "TEMPORAL_CONSTRAINT", "REVERSIBILITY_CONSTRAINT", "PRIVACY_CONSTRAINT",
        "DISCLOSURE_CONSTRAINT", "SIDE_EFFECT_CONSTRAINT", "OUTCOME_CONSTRAINT",
        "EXECUTION_BOUNDARY_CONSTRAINT"
    ] = "GOAL_CONSTRAINT"
    
    source_ref: str = field(default_factory=lambda: f"constraint_src_{id(object())}")
    """Reference to the source artifact (e.g., goal, policy)."""
    
    constraint_text: str = ""
    """The actual constraint specification."""
    
    mandatory: bool = True
    """True if this constraint must be satisfied for admissibility."""


# =============================================================================
# ACTION AUTHORITY REQUIREMENT
# =============================================================================

@dataclass(frozen=True)
class ActionAuthorityRequirement:
    """
    Requirement for action authority validation.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    authority_ref: str = field(default_factory=lambda: f"auth_req_{id(object())}")
    """Reference to required authority."""
    
    kind: Literal["binding", "advisory", "none"] = "none"
    """Level of authority required."""
    
    mandatory: bool = False
    """True if action is inadmissible without this authority."""


# =============================================================================
# ACTION PROPERTY PREFERENCE
# =============================================================================

@dataclass(frozen=True)
class ActionPropertyPreference:
    """
    Preferred property for action selection (not a constraint).
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Preferences are NOT mandatory.
    """
    
    property_name: str = ""
    """Name of the preferred property."""
    
    preference_value: str = ""
    """Preferred value (if applicable)."""
    
    strength: Literal["weak", "medium", "strong"] = "medium"
    """Strength of the preference."""


# =============================================================================
# ACTION SELECTION EVIDENCE REQUIREMENT
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionEvidenceRequirement:
    """
    Evidence requirement for action evaluation.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    kind: Literal[
        "SUFFICIENT_EVIDENCE", "CURRENT_EVIDENCE", "EVIDENCE_GAP_IDENTIFIED"
    ] = "SUFFICIENT_EVIDENCE"
    
    required_evidence_ref: str = field(default_factory=lambda: f"evidence_req_{id(object())}")
    """Reference to required evidence."""
    
    minimum_confidence: float = 0.5
    """Minimum confidence level for evidence (0.0 to 1.0)."""


# =============================================================================
# ACTION SELECTION RETURN REQUIREMENTS
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionReturnRequirements:
    """
    Requirements for products returned by Action Selection.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Return requirements must not demand execution.
    """
    
    selected_action_required: bool = True
    """True if selected action reference is required."""
    
    alternative_actions_required: bool = False
    """True if alternative action references are required."""
    
    admissibility_assessment_required: bool = True
    """True if admissibility assessment is required."""
    
    policy_assessment_required: bool = True
    """True if Policy assessment is required."""
    
    security_assessment_required: bool = True
    """True if Security assessment is required."""
    
    authority_assessment_required: bool = False
    """True if Authority assessment is required."""
    
    feasibility_assessment_required: bool = True
    """True if feasibility assessment is required."""
    
    reversibility_assessment_required: bool = False
    """True if reversibility assessment is required."""
    
    expected_outcomes_assessment_required: bool = True
    """True if expected outcomes assessment is required."""
    
    rejected_candidates_dispositions_required: bool = False
    """True if rejected candidate dispositions are required."""
    
    unresolved_conflicts_required: bool = False
    """True if unresolved conflicts must be reported."""
    
    justification_required: bool = True
    """True if selection justification is required."""
    
    confidence_required: bool = True
    """True if selection confidence is required."""
    
    completeness_required: Literal["full", "partial"] = "full"
    """Required completeness of the return."""


# =============================================================================
# ACTION SELECTION OUTCOME - EXTERNAL OWNED
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionOutcome:
    """
    Immutable outcome from Action Selection.
    
    This artifact is owned by Action Selection capability, not Executive.
    Executive consumes it through a projection or reference.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Action Selection owns this artifact completely.
    """
    
    outcome_id: ActionSelectionOutcomeId = field(default_factory=ActionSelectionOutcomeId.generate)
    """Unique identifier for this outcome."""
    
    revision: int = 1
    """Revision number of the outcome schema."""
    
    schema_version: str = "1.0.0"
    """Schema version of this outcome type."""
    
    request_reference: Optional[str] = None
    """Reference to originating Action Selection request."""
    
    decision_identity: Optional[str] = None
    """Decision Identity that initiated selection."""
    
    decision_revision_ref: int = 1
    """Revision number of the Decision."""
    
    decision_commitment_reference: Optional[str] = None
    """Reference to accepted Decision Commitment."""
    
    status: Literal[
        "ACTION_SELECTED", "ACTION_SELECTED_WITH_CONDITIONS",
        "MULTIPLE_ACTIONS_REMAIN", "NO_ADMISSIBLE_ACTION", "NO_FEASIBLE_ACTION",
        "POLICY_REVIEW_REQUIRED", "SECURITY_REVIEW_REQUIRED", "AUTHORITY_REQUIRED",
        "MORE_EVIDENCE_REQUIRED", "REQUEST_STALE", "DECISION_STALE",
        "DECISION_SUSPENDED", "DECISION_TERMINATED", "PARTIAL", "DEFERRED",
        "REJECTED", "FAILED", "CANCELLED", "EXPIRED", "UNKNOWN"
    ] = "ACTION_SELECTED"
    
    selected_action_ref: Optional[str] = None
    """Reference to selected action (owned by Action Selection)."""
    
    alternative_action_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to alternative actions."""
    
    rejected_dispositions: Tuple["ActionDisposition", ...] = field(default_factory=tuple)
    """Dispositions for rejected candidates."""
    
    admissibility_assessment: "AdmissibilityAssessment" = field(
        default_factory=lambda: AdmissibilityAssessment(status="unknown")
    )
    """Assessment of action admissibility."""
    
    feasibility_assessment: "FeasibilityAssessment" = field(
        default_factory=lambda: FeasibilityAssessment(status="unknown")
    )
    """Assessment of action feasibility."""
    
    policy_assessment: "PolicyAssessment" = field(
        default_factory=lambda: PolicyAssessment(status="unknown")
    )
    """Assessment of Policy compliance."""
    
    security_assessment: "SecurityAssessment" = field(
        default_factory=lambda: SecurityAssessment(status="unknown")
    )
    """Assessment of Security compliance."""
    
    authority_assessment: "AuthorityAssessment" = field(
        default_factory=lambda: AuthorityAssessment(status="unknown")
    )
    """Assessment of authority requirements."""
    
    reversibility_assessment: "ReversibilityAssessment" = field(
        default_factory=lambda: ReversibilityAssessment(status="unknown")
    )
    """Assessment of action reversibility."""
    
    expected_outcomes_assessments: Tuple["ExpectedOutcomeAssessment", ...] = field(default_factory=tuple)
    """Assessments of expected outcomes."""
    
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Identified conflicts in selection."""
    
    unresolved_questions: Tuple[str, ...] = field(default_factory=tuple)
    """Unresolved questions about the selection."""
    
    justification: str = ""
    """Justification for the selected action (if any)."""
    
    confidence: float = 0.5
    """Confidence in the selection (0.0 to 1.0)."""
    
    completeness_assessment: Literal["full", "partial"] = "partial"
    """Completeness of the outcome."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this outcome."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"as_outcome_time_{id(object())}")
    """Reference to semantic time."""
    
    privacy_scope: str = "public"
    """Privacy scope of this outcome."""
    
    provenance_ref: str = field(default_factory=lambda: f"as_outcome_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# ASSESSMENT TYPES
# =============================================================================

@dataclass(frozen=True)
class AdmissibilityAssessment:
    """Admissibility assessment of action candidates."""
    
    status: Literal["admissible", "inadmissible", "unknown"] = "unknown"
    """Overall admissibility status."""
    
    constraints_satisfied: Tuple[str, ...] = field(default_factory=tuple)
    """Satisfied constraint references."""
    
    constraints_violated: Tuple[str, ...] = field(default_factory=tuple)
    """Violated constraint references."""


@dataclass(frozen=True)
class FeasibilityAssessment:
    """Feasibility assessment of action candidates."""
    
    status: Literal["feasible", "partially_feasible", "infeasible", "unknown"] = "unknown"
    """Overall feasibility status."""
    
    capability_gaps: Tuple[str, ...] = field(default_factory=tuple)
    """Identified capability gaps."""
    
    resource_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Identified resource constraints."""


@dataclass(frozen=True)
class PolicyAssessment:
    """Policy compliance assessment."""
    
    status: Literal["compliant", "non_compliant", "review_required", "unknown"] = "unknown"
    """Overall policy compliance status."""
    
    violated_policies: Tuple[str, ...] = field(default_factory=tuple)
    """Violated policy references."""
    
    review_recommendations: Tuple[str, ...] = field(default_factory=tuple)
    """Policy review recommendations."""


@dataclass(frozen=True)
class SecurityAssessment:
    """Security compliance assessment."""
    
    status: Literal["authorized", "unauthorized", "review_required", "unknown"] = "unknown"
    """Overall security authorization status."""
    
    violated_security_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Violated security rule references."""
    
    authorization_recommendations: Tuple[str, ...] = field(default_factory=tuple)
    """Security authorization recommendations."""


@dataclass(frozen=True)
class AuthorityAssessment:
    """Authority requirement assessment."""
    
    status: Literal["authority_satisfied", "authority_missing", "unknown"] = "unknown"
    """Overall authority status."""
    
    missing_authority_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Missing authority references."""


@dataclass(frozen=True)
class ReversibilityAssessment:
    """Reversibility assessment of actions."""
    
    status: Literal["reversible", "irreversible", "partially_reversible", "unknown"] = "unknown"
    """Overall reversibility status."""
    
    rollback_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Rollback requirements for reversible actions."""


@dataclass(frozen=True)
class ExpectedOutcomeAssessment:
    """Assessment of expected action outcomes."""
    
    outcome_ref: str = field(default_factory=lambda: f"outcome_assess_{id(object())}")
    """Reference to the outcome being assessed."""
    
    probability_estimate: float = 0.5
    """Estimated probability (0.0 to 1.0)."""
    
    alignment_with_expected: Literal["matches", "partially_matches", "contradicts", "unknown"] = "unknown"
    """Alignment with expected outcomes."""


@dataclass(frozen=True)
class ActionDisposition:
    """
    Disposition of a rejected action candidate.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    action_ref: str = field(default_factory=lambda: f"rejected_action_{id(object())}")
    """Reference to the rejected action."""
    
    reason: str = ""
    """Reason for rejection."""
    
    disqualifying_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Factors that disqualified this action."""


# =============================================================================
# EXECUTION READINESS PROJECTION - DECLARATIVE
# =============================================================================

@dataclass(frozen=True)
class ExecutiveExecutionReadinessProjection:
    """
    Declarative execution readiness projection.
    
    This states whether a selected-action reference may proceed to Execution
    owned review. It does NOT authorize or perform execution.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: This is NEVER an execution authorization.
    """
    
    projection_id: ExecutiveExecutionReadinessProjectionId = field(default_factory=ExecutiveExecutionReadinessProjectionId.generate)
    """Unique identifier for this projection."""
    
    decision_identity: Optional[str] = None
    """Decision Identity being executed."""
    
    decision_revision_ref: int = 1
    """Revision number of the Decision."""
    
    decision_commitment_reference: Optional[str] = None
    """Reference to accepted Decision Commitment."""
    
    action_selection_request_ref: Optional[str] = None
    """Reference to Action Selection request."""
    
    action_selection_outcome_ref: Optional[str] = None
    """Reference to Action Selection outcome."""
    
    selected_action_ref: Optional[str] = None
    """Reference to selected action (owned by Action Selection)."""
    
    decision_compatibility: Literal["compatible", "incompatible", "unknown"] = "compatible"
    """Compatibility with current Decision state."""
    
    policy_status: Literal["compliant", "non_compliant", "review_required", "unknown"] = "compliant"
    """Policy compliance status."""
    
    security_status: Literal["authorized", "unauthorized", "review_required", "unknown"] = "authorized"
    """Security authorization status."""
    
    authority_status: Literal["satisfied", "missing", "unknown"] = "satisfied"
    """Authority status."""
    
    context_freshness: Literal["fresh", "stale", "unknown"] = "fresh"
    """Freshness of execution context."""
    
    reversibility_status: Literal["reversible", "irreversible", "unknown"] = "reversible"
    """Reversibility status of selected action."""
    
    unresolved_blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Blocking conditions that must be resolved."""
    
    required_execution_reviews: Tuple[str, ...] = field(default_factory=tuple)
    """Required execution review steps."""
    
    validity_status: Literal["valid", "invalid", "stale"] = "valid"
    """Validity of this projection."""
    
    completeness_status: Literal["complete", "partial"] = "complete"
    """Completeness of the projection."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"readiness_time_{id(object())}")
    """Reference to semantic time."""
    
    provenance_ref: str = field(default_factory=lambda: f"readiness_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# EXECUTION READINESS STATUS
# =============================================================================

class ExecutiveExecutionReadinessStatus(Enum):
    """
    Status of execution readiness.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    NOT_READY = "not_ready"
    MISSING_SELECTED_ACTION = "missing_selected_action"
    MISSING_AUTHORITY = "missing_authority"
    MISSING_POLICY_APPROVAL = "missing_policy_approval"
    MISSING_SECURITY_APPROVAL = "missing_security_approval"
    DECISION_STALE = "decision_stale"
    ACTION_STALE = "action_stale"
    CONTEXT_STALE = "context_stale"
    COMPATIBILITY_REVIEW_REQUIRED = "compatibility_review_required"
    READY_FOR_EXECUTION_REVIEW = "ready_for_execution_review"
    READY_WITH_CONDITIONS = "ready_with_conditions"
    BLOCKED = "blocked"
    INVALID = "invalid"
    UNKNOWN = "unknown"


# =============================================================================
# DECISION OUTCOME INTEGRATION
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDecisionOutcomeIntegration:
    """
    Integration of downstream outcomes with governing Decision.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Source ownership is preserved.
    """
    
    integration_id: str = field(default_factory=lambda: f"outcome_int_{id(object())}")
    """Unique identifier for this integration."""
    
    source_artifact_ref: str = field(default_factory=lambda: f"src_artifact_{id(object())}")
    """Reference to the downstream outcome (e.g., Action Selection, Execution)."""
    
    source_owner: str = "external"
    """Owner of the source artifact."""
    
    decision_identity: Optional[str] = None
    """Decision Identity that governed this outcome."""
    
    decision_revision_ref: int = 1
    """Revision number of the Decision."""
    
    expected_outcome_ref: Optional[str] = None
    """Reference to expected outcome (if any)."""
    
    observed_outcome_ref: str = field(default_factory=lambda: f"obs_outcome_{id(object())}")
    """Reference to actual observed outcome."""
    
    attribution_confidence: float = 0.5
    """Confidence in outcome attribution (0.0 to 1.0)."""
    
    mismatch: Literal["none", "partial", "significant"] = "none"
    """Level of mismatch between expected and observed outcomes."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this integration."""
    
    semantic_time_ref: str = field(default_factory=lambda: f"int_time_{id(object())}")
    """Reference to semantic time."""
    
    provenance_ref: str = field(default_factory=lambda: f"int_prov_{id(object())}")
    """Reference to provenance trail."""


# =============================================================================
# OUTCOME RELATION
# =============================================================================

class ExecutiveDecisionOutcomeRelation(Enum):
    """
    Relation between expected and observed outcomes.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    MATCHES_EXPECTATION = "matches_expectation"
    PARTIALLY_MATCHES = "partially_matches"
    EXCEEDS_EXPECTATION = "exceeds_expectation"
    UNDERPERFORMS_EXPECTATION = "underperforms_expectation"
    CONTRADICTS_EXPECTATION = "contradicts_expectation"
    UNRELATED = "unrelated"
    ATTRIBUTION_UNCERTAIN = "attribution_uncertain"
    OUTCOME_PENDING = "outcome_pending"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNKNOWN = "unknown"


# =============================================================================
# POST-SELECTION ASSESSMENT
# =============================================================================

class ExecutiveDecisionPostSelectionAssessment(Enum):
    """
    Assessment of Decision status after Action Selection.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Does not automatically complete or terminate Decision.
    """
    
    MAINTAIN = "maintain"
    MAINTAIN_WITH_CONDITIONS = "maintain_with_conditions"
    REQUEST_NEW_ACTION_SELECTION = "request_new_action_selection"
    REVISE_ACTION_SELECTION_REQUEST = "revise_action_selection_request"
    REVIEW_DECISION = "review_decision"
    REVISE_DECISION = "revise_decision"
    SUSPEND_DECISION = "suspend_decision"
    REPLACE_DECISION = "replace_decision"
    TERMINATE_DECISION = "terminate_decision"
    WAIT_FOR_AUTHORITY = "wait_for_authority"
    WAIT_FOR_CONTEXT = "wait_for_context"
    READY_FOR_EXECUTION_REVIEW = "ready_for_execution_review"
    UNKNOWN = "unknown"


# =============================================================================
# COORDINATION COMPLETION ASSESSMENT
# =============================================================================

class ExecutiveDecisionCoordinationCompletionAssessment(Enum):
    """
    Assessment of coordination completion.
    
    Runtime-neutral: Yes
    Executable: No
    
    INVARIANT: Distinct from Decision completion.
    """
    
    NOT_COMPLETE = "not_complete"
    PROJECTIONS_COMPLETE = "projections_complete"
    WAITING_FOR_PRODUCTS = "waiting_for_products"
    ACTION_SELECTION_REQUEST_COMPLETE = "action_selection_request_complete"
    WAITING_FOR_ACTION_SELECTION = "waiting_for_action_selection"
    ACTION_SELECTION_COMPLETE = "action_selection_complete"
    EXECUTION_REVIEW_READY = "execution_review_ready"
    COMPLETE_WITH_LIMITATIONS = "complete_with_limitations"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"
    UNKNOWN = "unknown"