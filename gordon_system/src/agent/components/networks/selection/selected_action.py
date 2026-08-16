# Gordon Cognitive Architecture - Phase 4.5.8
# ===========================================
#
"""
Selected Action Subsystem

This module defines the canonical Selected Action architecture for the Gordon
autonomous cognitive agent.

CANONICAL DEFINITION
====================

A Selected Action is an immutable semantic artifact identifying one exact Action
Candidate and Action revision accepted by the Action Selection subsystem for
possible downstream Execution review under explicit Decision, authority, Policy,
Security, context, scope, precondition, and provenance constraints.

A Selected Action represents:
    - The result of selection

It does NOT represent:
    - The act of executing
    - Runtime code or callable
    - A coroutine or runtime task
    - An Effector or Executor
    - An Effect or ExecutionOutcome

SELECTED ACTION IS NOT:
    - An executing Action (execution is separate phase)
    - An ExecutionRequest (that's downstream)
    - An ExecutionThread, ExecutionCycle, or ExecutionAttempt
    - A tool invocation (implementation detail)
    - A runtime command (runtime belongs elsewhere)

ARCHITECTURE
============

SelectedActionArtifact (base concept)
    ↓
SelectedAction
    ├── Identity: unique selected action identity
    ├── Revision: monotonically increasing revision number
    ├── Candidate Reference: exact accepted Action Candidate
    ├── Action Reference: exact Action representation
    ├── Context: bounded semantic environment
    ├── Scope: explicit bounds on the action
    ├── Selection Mode: how selection was made
    └── Selection Policy Reference: governing policy

SelectedActionRevision
    ├── Parent Revision: prior revision (if any)
    ├── Fields Changed: what changed in this revision
    ├── Reason: why the revision occurred
    └── Reviewing Authority: authority that performed revision

SelectedActionReference
    ├── Selected Action Identity
    ├── Selected Action Revision
    ├── Action Identity and Revision
    └── Candidate Identity and Revision

SELECTED-ACTION-LAW-001: A Selected Action is semantic and never executes itself.
SELECTED-ACTION-LAW-002: Selected Action Identity is distinct from Action,
                        Candidate, ExecutionRequest, and ExecutionAttempt Identity.
SELECTED-ACTION-LAW-003: Every Selected Action references one exact Candidate
                        revision and one exact Action revision.
SELECTED-ACTION-LAW-004: Selection does not imply Action authorization.
SELECTED-ACTION-LAW-005: Action authorization does not imply Execution authority.
SELECTED-ACTION-LAW-006: Policy and Security remain externally authoritative.
SELECTED-ACTION-LAW-007: Every readiness status is declarative.
SELECTED-ACTION-LAW-008: Execution-review readiness is distinct from
                        execution-request readiness.
SELECTED-ACTION-LAW-009: Execution-request readiness is distinct from
                        Execution authorization.
SELECTED-ACTION-LAW-010: Selected Action revisions never overwrite history.
SELECTED-ACTION-LAW-011: Selected Action invalidation is explicit and immutable.
SELECTED-ACTION-LAW-012: Replacement never mutates the prior Selected Action.
SELECTED-ACTION-LAW-013: Suspension preserves restoration semantics.
SELECTED-ACTION-LAW-014: Execution rejection never causes hidden reselection.
SELECTED-ACTION-LAW-015: The terminal Action Selection product is an
                        ExecutionRequest projection, not a concrete ExecutionRequest.
SELECTED-ACTION-LAW-016: Execution owns construction and acceptance of concrete
                        ExecutionRequests.
SELECTED-ACTION-LAW-017: All external reviews preserve exact artifact revisions.
SELECTED-ACTION-LAW-018: All semantic collections are immutable and bounded.
SELECTED-ACTION-LAW-019: Equivalent semantic inputs produce equivalent Selected
                        Action artifacts and projections.
SELECTED-ACTION-LAW-020: Package import performs no review, dispatch, scheduling,
                        or Execution work.

OWNERSHIP
=========

Action Selection Subsystem owns:
    - Canonical Selected Action semantics
    - Selected Action Identity model
    - Selected Action Revision model
    - Selected Action Reference model
    - Selected Action Context and Scope models
    - Selected Action lifecycle (before execution)
    - Validity, completeness, freshness assessments
    - Authorization state representation
    - Policy review references (not interpretation)
    - Security review references (not interpretation)
    - Target review references (not inspection)
    - Precondition review
    - Capability review (not implementation)
    - Resource review (not allocation)
    - Reversibility, rollback, compensation reviews
    - Idempotency, retryability reviews
    - Monitoring requirements
    - Expiration
    - Invalidations (with source and authority)
    - Suspensions and restorations
    - Replacements and supersessions
    - Cancellations and terminations
    - Deltas, Transitions, Continuations
    - History and Lineage
    - Execution-review readiness
    - Execution-request readiness
    - Execution-review projection
    - Execution-request projection

Action Selection Subsystem does NOT own:
    - Action implementation
    - Policy interpretation or enforcement
    - Security authorization (only references)
    - Capability implementations
    - Resource allocation or reservation
    - Runtime target locking or inspection
    - ExecutionRequest construction
    - Scheduling or runtime execution
    - Tool invocation or Effector usage

IMPORT SAFETY
=============

This package is designed to be import-safe:
    - No filesystem access during import
    - No network access during import
    - No model loading during import
    - No runtime initialization during import
    - No random identity generation during import
    - No wall-clock acquisition during import

All construction is deterministic given identical semantic inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# IDENTITY TYPES
# =============================================================================

SelectedActionIdentity = str
"""Unique identifier for a selected action instance."""


SelectedActionRevision = int
"""Monotonically increasing revision number for a selected action."""


SelectedActionSchemaVersion = str
"""Schema version for serialization compatibility."""


# =============================================================================
# SELECTED ACTION REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionReference:
    """
    Reference to a specific SelectedAction.

    PROPERTIES:
        • identity: Selected Action Identity
        • revision: Selected Action revision number
        • action_identity: Referenced Action Identity
        • action_revision: Referenced Action revision
        • candidate_identity: Referenced Candidate Identity

    IMPORTANT:
        • References are immutable semantic identifiers
        • No runtime objects, callbacks, or implementations embedded
        • References may point to stale revisions (for history preservation)
    """

    identity: SelectedActionIdentity = ""
    """Selected Action Identity."""

    revision: int = 1
    """Selected Action revision number."""

    action_identity: str = ""
    """Referenced Action Identity."""

    action_revision: int = 1
    """Referenced Action revision."""

    candidate_identity: str = ""
    """Referenced Candidate Identity."""


# =============================================================================
# SELECTED ACTION REVISION REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionRevisionReference:
    """
    Reference to a specific revision of a SelectedAction.

    PROPERTIES:
        • identity: Selected Action Identity
        • revision: Specific revision number
        • parent_revision: Prior revision (if any)

    IMPORTANT:
        • Revision references preserve history without embedding full revisions
        • Parent reference enables lineage traversal
    """

    identity: SelectedActionIdentity = ""
    """Selected Action Identity."""

    revision: int = 1
    """Specific revision number."""

    parent_revision: int | None = None
    """Prior revision (if any)."""


# =============================================================================
# SELECTED ACTION REVISION METADATA
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionRevisionMetadata:
    """
    Metadata about a specific SelectedAction revision.

    PROPERTIES:
        • changed_fields: Which fields changed in this revision
        • reason: Why the revision occurred
        • reviewing_authority: Authority that performed revision
        • semantic_time: Semantic time of revision

    IMPORTANT:
        • No mutation - revisions are immutable historical records
        • Revision metadata enables audit and replay
    """

    changed_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Which fields changed in this revision."""

    reason: str = "GENERAL"
    """Why the revision occurred."""

    reviewing_authority: str = ""
    """Authority that performed revision."""

    semantic_time: str = ""
    """Semantic time of revision (external reference, not wall-clock)."""


# =============================================================================
# SELECTED ACTION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionContext:
    """
    Bounded semantic context for a SelectedAction.

    Context contains references to related artifacts without embedding them.

    PROPERTIES:
        • action_selection_request_reference: Parent selection request reference
        • final_selection_request_reference: Final selection request reference
        • arbitration_result_reference: Source arbitration result reference
        • selection_frontier_reference: Selection frontier reference
        • action_selection_outcome_reference: Selection outcome reference
        • executive_decision_reference: Governing decision reference (if any)
        • commitment_reference: Active commitment reference (if any)
        • strategy_reference: Strategy context reference (if any)
        • plan_reference: Plan context reference (if any)
        • semantic_time: Semantic time reference for this action

    IMPORTANT:
        • Context contains only references, not full artifacts
        • No implementation callbacks or runtime state
        • Context is bounded to prevent unbounded embedding
    """

    action_selection_request_reference: str = ""
    """Parent Action Selection Request reference."""

    final_selection_request_reference: str = ""
    """Final Action Selection Request reference."""

    arbitration_result_reference: str = ""
    """Source Arbitration Result reference."""

    selection_frontier_reference: str = ""
    """Action Selection Frontier reference."""

    action_selection_outcome_reference: str = ""
    """Action Selection Outcome reference."""

    executive_decision_reference: str = ""
    """Governing Executive Decision reference."""

    commitment_reference: str = ""
    """Active Commitment reference."""

    strategy_reference: str = ""
    """Strategy context reference."""

    plan_reference: str = ""
    """Plan context reference."""

    semantic_time: str = ""
    """Semantic time reference (external, not wall-clock)."""


# =============================================================================
# SELECTED ACTION SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionScope:
    """
    Bounded scope for a SelectedAction.

    Every action must be explicitly bounded to prevent unbounded operations.

    PROPERTIES:
        • selected_action_scope: Scope of the selected action itself
        • target_scope: Permitted target scope
        • effect_scope: Permitted effect scope
        • capability_scope: Permitted capability scope
        • resource_scope: Permitted resource scope
        • authority_scope: Permitted authority scope
        • policy_scope: Policy review scope
        • security_scope: Security review scope
        • temporal_scope: Time-bound scope
        • privacy_scope: Privacy scope

    IMPORTANT:
        • Scope cannot exceed request scope, Action scope, or authority scope
        • Bounded by design - no unbounded scopes
        • Scope overflow is explicit
    """

    selected_action_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Scope of the selected action itself."""

    target_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Target scopes where the action may be applied."""

    effect_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Permitted effect scopes."""

    capability_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Permitted capability scopes."""

    resource_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Permitted resource scopes."""

    authority_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Authority IDs that may review this action."""

    policy_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Policy domains that apply."""

    security_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Security clearance scopes required."""

    temporal_scope: str = ""
    """Temporal scope (e.g., 'session', 'task', 'immediate')."""

    privacy_scope: str = ""
    """Privacy scope constraints."""


# =============================================================================
# SELECTED ACTION LIFECYCLE STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionLifecycleState:
    """
    Current lifecycle state of a SelectedAction.

    States represent semantic position in the selection-to-execution journey.
    Execution runtime states are explicitly excluded.

    STATES:
        • CREATED: Initial creation
        • VALIDATION_PENDING: Waiting for validation
        • VALIDATING: Currently validating
        • VALID: Passed all validity checks
        • VALID_WITH_CONDITIONS: Valid but with conditions
        • INCOMPLETE: Missing required information
        • AUTHORIZATION_PENDING: Awaiting authorization review
        • AUTHORIZED: Authorization granted
        • AUTHORIZED_WITH_CONDITIONS: Authorized with conditions
        • AUTHORIZATION_DENIED: Authorization denied
        • POLICY_REVIEW_PENDING: Policy review pending
        • SECURITY_REVIEW_PENDING: Security review pending
        • TARGET_REVIEW_PENDING: Target review pending
        • CAPABILITY_REVIEW_PENDING: Capability review pending
        • RESOURCE_REVIEW_PENDING: Resource review pending
        • EXECUTION_REVIEW_PENDING: Awaiting execution review
        • READY_FOR_EXECUTION_REVIEW: Ready for execution review
        • READY_FOR_EXECUTION_REQUEST_PROJECTION: Ready for request projection
        • SUSPENDED: Temporarily suspended
        • RESTORATION_PENDING: Waiting for restoration review
        • STALE: External state has changed
        • INVALIDATED: Explicitly invalidated
        • REPLACEMENT_PENDING: Replacement in progress
        • REPLACED: Replaced by another selection
        • SUPERSEDED: Superseded by newer selection
        • EXPIRED: Time or condition expiration reached
        • CANCELLED: Cancelled externally
        • TERMINATED: Lifecycle permanently ended

    IMPORTANT:
        • These are semantic states, not runtime states
        • No EXECUTING, RUNNING, SUCCEEDED, FAILED_EXECUTION (runtime)
        • State transitions are explicit and auditable
    """

    state: str = "CREATED"
    """Canonical lifecycle state."""


# =============================================================================
# SELECTED ACTION VALIDITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionValidity:
    """
    Validity assessment of a SelectedAction.

    Validity is distinct from authorization, completeness, and freshness.

    STATES:
        • VALID: Passed all validity checks
        • VALID_WITH_WARNINGS: Valid but with warnings
        • VALID_WITH_CONDITIONS: Valid but with explicit conditions
        • VALID_WITH_LIMITATIONS: Valid but with known limitations
        • INCOMPLETE: Missing required information
        • STALE: External state has changed
        • EXPIRED: Time or condition expiration reached
        • POLICY_REVIEW_REQUIRED: Policy review needed
        • SECURITY_REVIEW_REQUIRED: Security review needed
        • AUTHORIZATION_REQUIRED: Authorization needed
        • TARGET_REVIEW_REQUIRED: Target review needed
        • CAPABILITY_REVIEW_REQUIRED: Capability review needed
        • RESOURCE_REVIEW_REQUIRED: Resource review needed
        • PRECONDITION_REVIEW_REQUIRED: Precondition review needed
        • INVALIDATED: Explicitly invalidated
        • INVALID: Failed validity checks
        • UNKNOWN: Cannot determine validity

    IMPORTANT:
        • Validity is a semantic assessment, not runtime evaluation
        • A Selected Action can be valid but unauthorized
        •Validity is revision-specific (stale revisions may be invalid)
    """

    status: str = "VALID"
    """Current validity status."""

    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Specific findings supporting the validity assessment."""


# =============================================================================
# SELECTED ACTION COMPLETENESS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionCompleteness:
    """
    Completeness assessment of a SelectedAction.

    Completeness is distinct from validity and authorization.

    LEVELS:
        • COMPLETE: All required fields present
        • SUBSTANTIALLY_COMPLETE: Most required fields present with minor gaps
        • PARTIAL: Only some required information present
        • MISSING_CONTEXT: Semantic context incomplete
        • MISSING_SCOPE: Scope definition incomplete
        • MISSING_AUTHORITY: Authority information missing
        • MISSING_POLICY_REVIEW: Policy review references missing
        • MISSING_SECURITY_REVIEW: Security review references missing
        • MISSING_TARGET_REVIEW: Target review references missing
        • MISSING_CAPABILITY_REVIEW: Capability review references missing
        • MISSING_RESOURCE_REVIEW: Resource review references missing
        • MISSING_PRECONDITION_REVIEW: Precondition reviews missing
        • MISSING_EXECUTION_REQUIREMENTS: Execution requirements incomplete
        • MISSING_PROVENANCE: Provenance information missing
        • CAPACITY_LIMITED: Bounded by capacity limits
        • INVALID: Structure is invalid

    IMPORTANT:
        • A Selected Action can be complete but not valid
        • Completeness does not imply authorization
        • Lower completeness means lower downstream confidence
    """

    level: str = "COMPLETE"
    """Completeness level."""

    fields_present: int = 0
    """Number of expected fields that are present."""

    fields_expected: int = 0
    """Total number of expected fields."""


# =============================================================================
# SELECTED ACTION FRESHNESS DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionFreshnessDimension:
    """
    A freshness dimension for a SelectedAction.

    Each dimension represents one external artifact whose revision affects freshness.

    DIMENSIONS:
        • ACTION_SELECTION_REQUEST: Parent selection request revision
        • FINAL_SELECTION_REQUEST: Final selection request revision
        • ARBITRATION_RESULT: Source arbitration result revision
        • SELECTION_FRONTIER: Selection frontier revision
        • CANDIDATE: Selected candidate revision
        • ACTION: Referenced action revision
        • DECISION: Governing decision revision
        • COMMITMENT: Active commitment revision
        • PLAN: Active plan revision
        • TARGET: Target state revision
        • POLICY: Policy approval status revision
        • SECURITY: Security authorization status revision
        • AUTHORITY: Selection authority status revision
        • CAPABILITY: Required capability status revision
        • RESOURCE_PROJECTION: Resource projection revision

    IMPORTANT:
        • Freshness is revision-specific
        • A stale dimension doesn't necessarily invalidate the selection
        • Downstream systems must consider all freshness dimensions
    """

    dimension: str = "ACTION_SELECTION_REQUEST"
    """Freshness dimension name."""

    current_revision: int = 1
    """Current external revision."""

    reference_revision: int = 1
    """Revision referenced in this SelectedAction."""

    stale: bool = False
    """Whether this dimension is stale."""


# =============================================================================
# SELECTED ACTION FRESHNESS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionFreshness:
    """
    Freshness assessment of a SelectedAction.

    Freshness considers all external revision dependencies.

    STATES:
        • CURRENT: All referenced revisions are current
        • CURRENT_WITH_LIMITATIONS: Current but with known limitations
        • PARTIALLY_STALE: Some dimensions stale, some current
        • STALE_REQUEST: Parent request revision is stale
        • STALE_FRONTIER: Selection frontier revision is stale
        • STALE_CANDIDATE: Selected candidate revision is stale
        • STALE_ACTION: Referenced action revision is stale
        • STALE_DECISION: Governing decision revision is stale
        • STALE_TARGET: Target state revision is stale
        • STALE_POLICY: Policy approval status revision is stale
        • STALE_SECURITY: Security authorization status revision is stale
        • STALE_AUTHORITY: Authority status revision is stale
        • STALE_CAPABILITY: Required capability status revision is stale
        • STALE_RESOURCE: Resource projection revision is stale
        • EXPIRED: Semantic expiration reached
        • UNKNOWN: Cannot determine freshness

    IMPORTANT:
        • Freshness is distinct from validity and authorization
        • Stale freshness may block readiness but doesn't invalidate the artifact
        • Freshness must be revalidated before execution review
    """

    status: str = "CURRENT"
    """Current freshness status."""

    stale_dimensions: Tuple[SelectedActionFreshnessDimension, ...] = field(
        default_factory=tuple
    )
    """Dimensions that are stale."""


# =============================================================================
# SELECTED ACTION AUTHORIZATION STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionAuthorizationStatus:
    """
    Authorization status of a SelectedAction.

    Authorization is separate from selection and execution authority.

    STATUSES:
        • NOT_REVIEWED: No authorization review performed
        • REVIEW_REQUIRED: Review required but not started
        • PENDING: Review in progress
        • AUTHORIZED: Authorization granted
        • AUTHORIZED_WITH_CONDITIONS: Authorized with explicit conditions
        • PARTIALLY_AUTHORIZED: Some authority domains authorized
        • DENIED: Authorization denied
        • REVOKED: Prior authorization revoked
        • STALE: Authorization reference is stale
        • EXPIRED: Authorization time window passed
        • CONFLICTING: Conflicting authorizations from different authorities
        • UNKNOWN: Cannot determine authorization status

    IMPORTANT:
        • Authorization does not imply selection or execution authority
        • A selected action may be unauthorized
        • Unauthorized actions cannot proceed to execution review
    """

    status: str = "NOT_REVIEWED"
    """Current authorization status."""


# =============================================================================
# SELECTED ACTION AUTHORIZATION STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionAuthorizationState:
    """
    Complete authorization state of a SelectedAction.

    PROPERTIES:
        • status: Authorization status
        • authority_references: References to authorizing authorities
        • authorized_operations: Which operations are authorized
        • target_scope_authorized: Whether target scope is authorized
        • conditions: Authorization conditions that must hold
        • expiration: When authorization expires
        • provenance: Source of authorization

    IMPORTANT:
        • Authorization state is immutable - changes create new revisions
        • Authority references are semantic, not runtime objects
    """

    status: str = "NOT_REVIEWED"
    """Authorization status."""

    authority_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to authorizing authorities."""

    authorized_operations: Tuple[str, ...] = field(default_factory=tuple)
    """Operations that are authorized."""

    target_scope_authorized: bool = False
    """Whether target scope is authorized."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Authorization conditions that must hold."""

    expiration: str = ""
    """When authorization expires (semantic time reference)."""

    provenance: str = ""
    """Source of authorization."""


# =============================================================================
# SELECTED ACTION AUTHORIZATION REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionAuthorizationReview:
    """
    Authorization review result for a SelectedAction.

    OUTCOMES:
        • AUTHORIZED: Authorization granted
        • AUTHORIZED_WITH_CONDITIONS: Authorized with explicit conditions
        • DENIED: Authorization denied
        • DEFERRED: Review deferred to later mechanism
        • HIGHER_AUTHORITY_REQUIRED: Need higher authority review
        • USER_CONFIRMATION_REQUIRED: User confirmation required
        • POLICY_REVIEW_REQUIRED: Policy review needed first
        • SECURITY_REVIEW_REQUIRED: Security review needed first
        • TARGET_REVIEW_REQUIRED: Target review needed first
        • MORE_EVIDENCE_REQUIRED: Insufficient evidence for decision
        • STALE_SELECTION: Selection is stale
        • INVALID_SELECTION: Selection is invalid
        • UNKNOWN: Cannot determine authorization

    IMPORTANT:
        • Review is performed by external authority, not embedded in artifact
        • The SelectedAction references the review, doesn't perform it
    """

    outcome: str = "AUTHORIZED"
    """Authorization review outcome."""

    reviewed_revision: int = 1
    """Exact revision that was reviewed."""

    reviewing_authority: str = ""
    """Authority that performed review."""

    conditions_applied: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions applied by authorization."""

    expiration: str = ""
    """When this authorization expires (semantic time)."""

    provenance: str = ""
    """Source of review result."""


# =============================================================================
# SELECTED ACTION AUTHORIZATION CONDITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionAuthorizationCondition:
    """
    A condition that must hold for authorization to remain valid.

    CONDITIONS:
        • TARGET_REVISION_MUST_MATCH: Target must match expected revision
        • POLICY_APPROVAL_MUST_REMAIN_VALID: Policy approval must remain valid
        • SECURITY_APPROVAL_MUST_REMAIN_VALID: Security approval must remain valid
        • CAPABILITY_SCOPE_MUST_MATCH: Capability scope must not change
        • RESOURCE_LIMIT_MUST_HOLD: Resource limits must still hold
        • USER_CONFIRMATION_MUST_REMAIN_VALID: User confirmation must persist
        • ROLLBACK_MUST_BE_AVAILABLE: Rollback mechanism must be available
        • COMPENSATION_MUST_BE_AVAILABLE: Compensation mechanism must be available
        • MONITORING_MUST_BE_ACTIVE: Monitoring must remain active
        • EXECUTION_ENVIRONMENT_MUST_MATCH: Environment must match requirements
        • PRIVACY_SCOPE_MUST_BE_PRESERVED: Privacy scope must not expand
        • GENERAL: General condition without specific category

    IMPORTANT:
        • Conditions are semantic propositions, not evaluators
        • External validation means another system evaluates the condition
    """

    kind: str = "GENERAL"
    """Condition category."""

    description: str = ""
    """Human-readable condition description."""

    external_validation: bool = True
    """Whether this must be validated externally."""


# =============================================================================
# SELECTED ACTION POLICY REVIEW STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionPolicyReviewStatus:
    """
    Policy review status of a SelectedAction.

    STATES:
        • NOT_REVIEWED: No policy review performed
        • NOT_REQUIRED: Policy review not required for this action
        • REQUIRED: Review required but not started
        • PENDING: Review in progress
        • COMPLIANT: Action is policy-compliant
        • COMPLIANT_WITH_CONDITIONS: Compliant with explicit conditions
        • PROHIBITED: Policy explicitly prohibits this action
        • EXCEPTION_REQUIRED: Requires policy exception
        • EXCEPTION_APPROVED: Policy exception approved
        • EXCEPTION_DENIED: Policy exception denied
        • STALE: Policy reference is stale
        • EXPIRED: Policy review time window passed
        • UNKNOWN: Cannot determine policy status

    IMPORTANT:
        • Policy review remains externally owned - the SelectedAction only references
        • A prohibited action cannot become ready for execution review
    """

    status: str = "NOT_REVIEWED"
    """Policy review status."""


# =============================================================================
# SELECTED ACTION POLICY REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionPolicyReview:
    """
    Policy review result for a SelectedAction.

    PROPERTIES:
        • status: Policy review status
        • policy_reference: Reference to reviewed Policy artifact
        • applicable_rules: Which rules were applied
        • conditions: Policy-imposed conditions
        • exceptions: Any approved exceptions
        • expiration: When this review expires (semantic time)
        • provenance: Source of review result

    IMPORTANT:
        • The SelectedAction does not interpret policy - it references review results
        • No Policy engine invocation in the semantic package
    """

    status: str = "NOT_REVIEWED"
    """Policy review status."""

    policy_reference: str = ""
    """Reference to reviewed Policy artifact."""

    applicable_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Which rules were applied."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Policy-imposed conditions."""

    exceptions: Tuple[str, ...] = field(default_factory=tuple)
    """Any approved exceptions."""

    expiration: str = ""
    """When this review expires (semantic time)."""

    provenance: str = ""
    """Source of review result."""


# =============================================================================
# SELECTED ACTION SECURITY REVIEW STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionSecurityReviewStatus:
    """
    Security review status of a SelectedAction.

    STATES:
        • NOT_REVIEWED: No security review performed
        • NOT_REQUIRED: Security review not required
        • REQUIRED: Review required but not started
        • PENDING: Review in progress
        • AUTHORIZED: Security authorization granted
        • AUTHORIZED_WITH_CONDITIONS: Authorized with conditions
        • PARTIALLY_AUTHORIZED: Partial security authorization
        • DENIED: Security authorization denied
        • PRIVILEGE_REVIEW_REQUIRED: Privilege review needed
        • CREDENTIAL_REVIEW_REQUIRED: Credential review needed
        • DISCLOSURE_REVIEW_REQUIRED: Disclosure review needed
        • STALE: Security reference is stale
        • EXPIRED: Review time window passed
        • UNKNOWN: Cannot determine security status

    IMPORTANT:
        • No credentials embedded in the SelectedAction
        • Security remains externally authoritative
    """

    status: str = "NOT_REVIEWED"
    """Security review status."""


# =============================================================================
# SELECTED ACTION SECURITY REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionSecurityReview:
    """
    Security review result for a SelectedAction.

    PROPERTIES:
        • status: Security review status
        • security_reference: Reference to reviewed Security artifact
        • authorization_scope: Scope of security authorization
        • capability_scope_authorized: Which capabilities are authorized
        • target_scope_authorized: Which targets are authorized
        • disclosure_scope: What can be disclosed
        • conditions: Security-imposed conditions
        • expiration: When this review expires (semantic time)
        • provenance: Source of review result

    IMPORTANT:
        • No credentials, secrets, or sensitive data in the SelectedAction
        • Reference only to security artifacts, not implementations
    """

    status: str = "NOT_REVIEWED"
    """Security review status."""

    security_reference: str = ""
    """Reference to reviewed Security artifact."""

    authorization_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Scope of security authorization."""

    capability_scope_authorized: Tuple[str, ...] = field(default_factory=tuple)
    """Which capabilities are authorized."""

    target_scope_authorized: Tuple[str, ...] = field(default_factory=tuple)
    """Which targets are authorized."""

    disclosure_scope: str = ""
    """What can be disclosed (e.g., 'public', 'internal', 'restricted')."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Security-imposed conditions."""

    expiration: str = ""
    """When this review expires (semantic time)."""

    provenance: str = ""
    """Source of review result."""


# =============================================================================
# SELECTED ACTION TARGET REVIEW STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionTargetReviewStatus:
    """
    Target review status of a SelectedAction.

    STATES:
        • CURRENT: Target state matches expected revision
        • CURRENT_WITH_CONDITIONS: Current but with conditions
        • REVISION_MATCH: Revision matches reference
        • REVISION_MISMATCH: Revision does not match reference
        • TARGET_MISSING: Target no longer exists
        • TARGET_AMBIGUOUS: Target identification is ambiguous
        • TARGET_CHANGED: Target state has changed
        • TARGET_LOCK_REQUIRED: Lock required for modification
        • TARGET_VALIDATION_REQUIRED: Validation needed before proceeding
        • STALE: Target revision is stale
        • UNKNOWN: Cannot determine target status

    IMPORTANT:
        • The SelectedAction does not inspect live targets - it references review results
        • Target state changes may require reselection
    """

    status: str = "CURRENT"
    """Target review status."""


# =============================================================================
# SELECTED ACTION TARGET REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionTargetReview:
    """
    Target review result for a SelectedAction.

    PROPERTIES:
        • status: Target review status
        • target_reference: Reference to the target
        • expected_revision: Revision referenced in this selection
        • actual_revision: Current revision (if known)
        • freshness: How fresh the review is
        • conditions: Any conditions applied
        • expiration: When this review expires (semantic time)

    IMPORTANT:
        • No live target access in semantic package
        • Review result is supplied by external system
    """

    status: str = "CURRENT"
    """Target review status."""

    target_reference: str = ""
    """Reference to the target."""

    expected_revision: int = 1
    """Revision referenced in this selection."""

    actual_revision: int | None = None
    """Current revision (if known)."""

    freshness: str = "UNKNOWN"
    """How fresh the review is."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Any conditions applied."""

    expiration: str = ""
    """When this review expires (semantic time)."""


# =============================================================================
# SELECTED ACTION PRECONDITION REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionPreconditionReview:
    """
    Precondition review for a SelectedAction.

    STATES:
        • SATISFIED: Precondition is satisfied
        • SATISFIED_WITH_CONDITIONS: Satisfied with conditions
        • UNSATISFIED: Precondition is not satisfied
        • UNKNOWN: Cannot determine satisfaction
        • STALE: Review reference is stale
        • VALIDATION_REQUIRED: Runtime validation needed
        • AUTHORITY_REQUIRED: Authorization needed first
        • POLICY_REVIEW_REQUIRED: Policy review needed first
        • SECURITY_REVIEW_REQUIRED: Security review needed first

    IMPORTANT:
        • Precondition review remains declarative
        • Runtime checking belongs to Execution review
    """

    satisfied: bool = False
    """Whether the precondition is satisfied."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Any conditions on satisfaction."""

    external_validation_required: bool = False
    """Whether runtime validation is required."""

    expiration: str = ""
    """When this review expires (semantic time)."""

    provenance: str = ""
    """Source of review result."""


# =============================================================================
# SELECTED ACTION CAPABILITY REVIEW STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionCapabilityReviewStatus:
    """
    Capability review status of a SelectedAction.

    STATES:
        • AVAILABLE: Required capability is available
        • AVAILABLE_WITH_LIMITATIONS: Available but with known limitations
        • COMPATIBLE: Capability is compatible with the action
        • COMPATIBLE_WITH_CONDITIONS: Compatible with conditions
        • MISSING: Capability not found
        • UNAVAILABLE: Capability is currently unavailable
        • VERSION_MISMATCH: Version doesn't match requirements
        • SCOPE_MISMATCH: Scope doesn't match requirements
        • AUTHORITY_REQUIRED: Authorization needed first
        • SECURITY_REVIEW_REQUIRED: Security review needed first
        • STALE: Capability status reference is stale
        • UNKNOWN: Cannot determine capability status

    IMPORTANT:
        • Capability references are semantic, not implementations
        • No live capability inspection in semantic package
    """

    status: str = "AVAILABLE"
    """Capability review status."""


# =============================================================================
# SELECTED ACTION CAPABILITY REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionCapabilityReview:
    """
    Capability review result for a SelectedAction.

    PROPERTIES:
        • status: Capability review status
        • capability_reference: Reference to the required capability
        • version_required: Required version
        • scope_required: Required scope
        • conditions: Any conditions on availability
        • expiration: When this review expires (semantic time)

    IMPORTANT:
        • No capability implementation embedded in SelectedAction
        • Review references external capability artifact
    """

    status: str = "AVAILABLE"
    """Capability review status."""

    capability_reference: str = ""
    """Reference to the required capability."""

    version_required: int = 1
    """Required version."""

    scope_required: Tuple[str, ...] = field(default_factory=tuple)
    """Required scope."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Any conditions on availability."""

    expiration: str = ""
    """When this review expires (semantic time)."""


# =============================================================================
# SELECTED ACTION RESOURCE REVIEW STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionResourceReviewStatus:
    """
    Resource review status of a SelectedAction.

    STATES:
        • SUFFICIENT: Required resources are sufficient
        • SUFFICIENT_WITH_LIMITATIONS: Sufficient but with known limitations
        • ESTIMATED_SUFFICIENT: Estimated to be sufficient
        • INSUFFICIENT: Resources are insufficient
        • RESERVATION_REQUIRED: Resource reservation needed first
        • CONFLICTING: Conflicting resource requirements
        • STALE: Resource projection reference is stale
        • UNKNOWN: Cannot determine resource status

    IMPORTANT:
        • Resource review does not reserve resources
        • Actual allocation happens in execution phase
    """

    status: str = "SUFFICIENT"
    """Resource review status."""


# =============================================================================
# SELECTED ACTION RESOURCE REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionResourceReview:
    """
    Resource review result for a SelectedAction.

    PROPERTIES:
        • status: Resource review status
        • resources_required: Which resources are required
        • estimated_quantity: Estimated quantity needed
        • availability_estimate: Current availability estimate
        • conditions: Any conditions on resource use
        • expiration: When this review expires (semantic time)

    IMPORTANT:
        • No actual reservation occurs in semantic package
        • Review is based on projections, not live allocation
    """

    status: str = "SUFFICIENT"
    """Resource review status."""

    resources_required: Tuple[str, ...] = field(default_factory=tuple)
    """Which resources are required."""

    estimated_quantity: float = 0.0
    """Estimated quantity needed."""

    availability_estimate: float | None = None
    """Current availability estimate (if known)."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Any conditions on resource use."""

    expiration: str = ""
    """When this review expires (semantic time)."""


# =============================================================================
# SELECTED ACTION REVERSIBILITY REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionReversibilityReview:
    """
    Reversibility review for a SelectedAction.

    STATES:
        • CONFIRMED_REVERSIBLE: Action is confirmed reversible
        • REVERSIBLE_WITH_CONDITIONS: Reversible with explicit conditions
        • COMPENSATABLE: Can be compensated if not fully reversible
        • PARTIALLY_REVERSIBLE: Only partial reversal possible
        • IRREVERSIBLE: Action cannot be reversed
        • REVIEW_REQUIRED: Reversibility needs external review
        • STALE: Reversibility reference is stale
        • UNKNOWN: Cannot determine reversibility

    IMPORTANT:
        • Reversibility assessment is semantic, not runtime execution
    """

    status: str = "UNKNOWN"
    """Reversibility review status."""

    declared_reversibility: str = ""
    """Declared reversibility by action author."""

    rollback_available: bool | None = None
    """Whether rollback mechanism is available (if known)."""

    compensation_available: bool | None = None
    """Whether compensation mechanism is available (if known)."""

    irreversible_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Effects that cannot be reversed."""

    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions on reversibility."""

    expiration: str = ""
    """When this review expires (semantic time)."""


# =============================================================================
# SELECTED ACTION ROLLBACK REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionRollbackReview:
    """
    Rollback review for a SelectedAction.

    PROPERTIES:
        • rollback_action_reference: Reference to rollback Action
        • rollback Preconditions: Precondition requirements for rollback
        • rollback authority: Authority required for rollback
        • rollback Policy and Security requirements: Review requirements
        • target_snapshot_reference: Reference to snapshot needed for rollback
        • rollback scope: Scope of rollback operation
        • monitoring_requirements: What must be monitored during rollback
        • readiness: Whether rollback is ready
        • limitations: Known limitations

    IMPORTANT:
        • No rollback execution occurs in semantic package
    """

    rollback_action_reference: str = ""
    """Reference to rollback Action."""

    rollback_preconditions_satisfied: bool | None = None
    """Whether rollback Preconditions are currently satisfied (if known)."""

    rollback_authority: str = ""
    """Authority required for rollback."""

    policy_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Policy requirements for rollback."""

    security_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Security requirements for rollback."""

    target_snapshot_reference: str | None = None
    """Reference to snapshot needed for rollback."""

    rollback_scope: str = ""
    """Scope of rollback operation."""

    monitoring_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """What must be monitored during rollback."""

    readiness: str = "UNKNOWN"
    """Whether rollback is ready (not a runtime state)."""

    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of rollback."""


# =============================================================================
# SELECTED ACTION COMPENSATION REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionCompensationReview:
    """
    Compensation review for a SelectedAction.

    PROPERTIES:
        • compensation_action_reference: Reference to compensation Action
        • triggering conditions: When compensation is triggered
        • authority required: Authority needed for compensation
        • Policy requirements: Policy constraints
        • Security requirements: Security constraints
        • intended mitigating effects: What this compensates for
        • limitations: Known limitations

    IMPORTANT:
        • No compensation execution occurs in semantic package
        • Compensation does not imply reversibility
    """

    compensation_action_reference: str = ""
    """Reference to compensation Action."""

    triggering_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """When compensation is triggered."""

    authority_required: str = ""
    """Authority needed for compensation."""

    policy_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Policy constraints."""

    security_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Security constraints."""

    intended_mitigating_effects: Tuple[str, ...] = field(default_factory=tuple)
    """What this compensates for."""

    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations."""


# =============================================================================
# SELECTED ACTION IDEMPOTENCY REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionIdempotencyReview:
    """
    Idempotency review for a SelectedAction.

    STATES:
        • CONFIRMED_IDEMPOTENT: Action is confirmed idempotent
        • IDEMPOTENT_WITH_KEY: Idempotent when key provided
        • CONDITIONALLY_IDEMPOTENT: Idempotent under certain conditions
        • NON_IDEMPOTENT: Action is not idempotent
        • REVIEW_REQUIRED: Idempotency needs external review
        • UNKNOWN: Cannot determine idempotency

    IMPORTANT:
        • No runtime idempotency keys are generated in semantic package
    """

    status: str = "UNKNOWN"
    """Idempotency review status."""

    key_required: bool | None = None
    """Whether an idempotency key is required (if known)."""

    target_revision_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Target revision constraints for idempotency."""

    semantic_scope: str = ""
    """Semantic scope of idempotency."""

    evidence: str = ""
    """Evidence supporting this assessment."""

    provenance: str = ""
    """Source of review result."""


# =============================================================================
# SELECTED ACTION RETRYABILITY REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionRetryabilityReview:
    """
    Retryability review for a SelectedAction.

    STATES:
        • SAFE_TO_RETRY: Safe to retry without conditions
        • SAFE_WITH_IDEMPOTENCY_KEY: Safe with idempotency key
        • SAFE_AFTER_TARGET_REFRESH: Safe after target refresh
        • SAFE_AFTER_PRECONDITION_REVIEW: Safe after precondition review
        • UNSAFE_TO_RETRY: Unsafe to retry
        • REQUIRES_COMPENSATION: Retry requires compensation
        • UNKNOWN: Cannot determine retryability

    IMPORTANT:
        • No runtime retry behavior in semantic package
        • Runtime retries are execution-layer concern
    """

    status: str = "UNKNOWN"
    """Retryability review status."""

    key_requirement: bool | None = None
    """Whether an idempotency key is required (if known)."""

    conditions_for_retry: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must hold before retrying."""

    expiration: str = ""
    """When this review expires (semantic time)."""

    provenance: str = ""
    """Source of review result."""


# =============================================================================
# SELECTED ACTION MONITORING REQUIREMENT KIND
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionMonitoringRequirementKind:
    """
    Kinds of monitoring requirements for a SelectedAction.

    REQUIREMENTS:
        • OBSERVE_EXECUTION_START: Monitor when execution starts
        • OBSERVE_EXECUTION_COMPLETION: Monitor when execution completes
        • VERIFY_TARGET_REVISION: Verify target revision during execution
        • VERIFY_INTENDED_EFFECT: Verify intended effects occur
        • DETECT_SIDE_EFFECT: Detect side effects
        • DETECT_UNINTENDED_EFFECT: Detect unintended effects
        • VERIFY_POLICY_CONTINUITY: Verify policy remains compliant
        • VERIFY_SECURITY_CONTINUITY: Verify security remains valid
        • VERIFY_RESOURCE_USE: Monitor resource usage
        • VERIFY_ROLLBACK_READINESS: Confirm rollback is still ready
        • VERIFY_COMPENSATION_READINESS: Confirm compensation is still ready
        • AUDIT_EXECUTION: Audit trail for execution
        • GENERAL: General monitoring requirement

    IMPORTANT:
        • Monitoring declares requirements, does not perform observation
    """

    kind: str = "GENERAL"
    """Monitoring requirement kind."""


# =============================================================================
# SELECTED ACTION MONITORING REQUIREMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionMonitoringRequirement:
    """
    A monitoring requirement for a SelectedAction.

    PROPERTIES:
        • kind: Monitoring requirement category
        • description: Human-readable requirement description
        • external_observer_required: Whether an external observer is required

    IMPORTANT:
        • Runtime observation is owned by monitoring subsystem, not semantic package
    """

    kind: str = "GENERAL"
    """Monitoring requirement kind."""

    description: str = ""
    """Human-readable requirement description."""

    external_observer_required: bool = False
    """Whether an external observer is required."""


# =============================================================================
# SELECTED ACTION PRIVACY REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionPrivacyReview:
    """
    Privacy review for a SelectedAction.

    PROPERTIES:
        • action_privacy: Action's own privacy classification
        • target_privacy: Target's privacy classification
        • disclosure_scope: What can be disclosed (e.g., 'public', 'internal')
        • evidence_disclosure: Whether evidence can be disclosed
        • justification_disclosure: Whether justification can be disclosed
        • execution_projection_disclosure: Can projections be shared?
        • logging_restrictions: Any logging constraints
        • monitoring_restrictions: Monitoring visibility constraints

    IMPORTANT:
        • Minimal disclosure is preserved at the Execution boundary
    """

    action_privacy: str = "PUBLIC"
    """Action's privacy classification."""

    target_privacy: str = "PUBLIC"
    """Target's privacy classification."""

    disclosure_scope: str = "INTERNAL"
    """What can be disclosed (e.g., 'public', 'internal', 'restricted')."""

    evidence_disclosure: bool = False
    """Whether evidence can be disclosed."""

    justification_disclosure: bool = True
    """Whether justification can be disclosed."""

    execution_projection_disclosure: bool = True
    """Can execution projections be shared?"""

    logging_restrictions: Tuple[str, ...] = field(default_factory=tuple)
    """Any logging constraints."""

    monitoring_restrictions: Tuple[str, ...] = field(default_factory=tuple)
    """Monitoring visibility constraints."""


# =============================================================================
# SELECTED ACTION EXECUTION ENVIRONMENT REQUIREMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionEnvironmentRequirement:
    """
    Execution environment requirements for a SelectedAction.

    REQUIREMENTS:
        • operating_system_class: Required OS class (e.g., 'linux', 'windows')
        • sandbox_class: Sandbox class if applicable
        • transaction_support: Whether transaction support is required
        • network_isolation_required: Whether network isolation is required
        • filesystem_isolation_required: Filesystem isolation requirement
        • capability_version: Minimum required capability version
        • runtime_security_context: Required security context
        • model_availability: Model availability requirements
        • hardware_class: Hardware class (e.g., 'cpu', 'gpu')
        • accelerator_class: Accelerator requirements if any

    IMPORTANT:
        • Requirements remain semantic - no environment creation or inspection
    """

    operating_system_class: str = ""
    """Required OS class."""

    sandbox_class: str | None = None
    """Sandbox class if applicable."""

    transaction_support_required: bool = False
    """Whether transaction support is required."""

    network_isolation_required: bool = False
    """Whether network isolation is required."""

    filesystem_isolation_required: bool = False
    """Whether filesystem isolation is required."""

    capability_version_minimum: int = 1
    """Minimum required capability version."""

    runtime_security_context: str = ""
    """Required security context."""

    model_availability: Tuple[str, ...] = field(default_factory=tuple)
    """Model availability requirements (if any)."""

    hardware_class: str = ""
    """Hardware class (e.g., 'cpu', 'gpu')."""

    accelerator_class: str | None = None
    """Accelerator requirements if any."""


# =============================================================================
# SELECTED ACTION EXECUTION REVIEW REQUIREMENT KIND
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionReviewRequirementKind:
    """
    Kinds of execution review requirements for a SelectedAction.

    REQUIREMENTS:
        • VALIDATE_SELECTED_ACTION_REVISION: Validate exact selected action revision
        • VALIDATE_ACTION_REVISION: Validate referenced action revision
        • VALIDATE_CANDIDATE_REVISION: Validate candidate revision
        • VALIDATE_SELECTION_OUTCOME: Validate selection outcome
        • VALIDATE_DECISION_REVISION: Validate governing decision revision
        • VALIDATE_COMMITMENT_REVISION: Validate commitment revision
        • VALIDATE_TARGET: Validate target state and revision
        • VALIDATE_PRECONDITIONS: Validate Preconditions are satisfied
        • VALIDATE_ACTION_AUTHORIZATION: Validate action authorization
        • VALIDATE_EXECUTION_AUTHORITY: Validate execution authority
        • VALIDATE_POLICY: Validate Policy compliance
        • VALIDATE_SECURITY: Validate Security authorization
        • VALIDATE_CAPABILITY: Validate capability availability
        • VALIDATE_RESOURCES: Validate resource sufficiency
        • VALIDATE_ENVIRONMENT: Validate environment requirements
        • VALIDATE_IDEMPOTENCY: Validate idempotency requirements
        • VALIDATE_REVERSIBILITY: Validate reversibility requirements
        • VALIDATE_ROLLBACK: Validate rollback readiness
        • VALIDATE_COMPENSATION: Validate compensation readiness
        • VALIDATE_MONITORING: Validate monitoring is available
        • VALIDATE_PRIVACY: Validate privacy constraints
        • GENERAL: General execution review requirement

    IMPORTANT:
        • Execution owns its own review process
        • These are requirements, not the review itself
    """

    kind: str = "GENERAL"
    """Execution review requirement kind."""


# =============================================================================
# SELECTED ACTION EXECUTION REVIEW REQUIREMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionReviewRequirement:
    """
    An execution review requirement for a SelectedAction.

    PROPERTIES:
        • kind: Execution review requirement category
        • description: Human-readable requirement description
        • must_be_satisfied_before_execution: Whether satisfied before execution

    IMPORTANT:
        • These requirements are for Execution's review process, not semantic evaluation
    """

    kind: str = "GENERAL"
    """Execution review requirement kind."""

    description: str = ""
    """Human-readable requirement description."""

    must_be_satisfied_before_execution: bool = True
    """Whether this must be satisfied before execution begins."""


# =============================================================================
# SELECTED ACTION EXECUTION REVIEW READINESS STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionReviewReadinessStatus:
    """
    Execution review readiness status of a SelectedAction.

    STATUSES:
        • NOT_READY: Not ready for execution review (basic blocking)
        • VALIDATION_PENDING: Waiting for initial validation
        • AUTHORIZATION_PENDING: Awaiting authorization review
        • POLICY_REVIEW_PENDING: Policy review pending
        • SECURITY_REVIEW_PENDING: Security review pending
        • TARGET_REVIEW_PENDING: Target review pending
        • CAPABILITY_REVIEW_PENDING: Capability review pending
        • RESOURCE_REVIEW_PENDING: Resource review pending
        • PRECONDITION_REVIEW_PENDING: Precondition review pending
        • CONDITIONS_PENDING: Conditions not yet resolved
        • READY_FOR_EXECUTION_REVIEW: Ready for execution review
        • READY_WITH_CONDITIONS: Ready but with conditions
        • BLOCKED: Hard constraints block progression
        • STALE: External state has changed
        • EXPIRED: Semantic expiration reached
        • INVALID: Artifact is invalid
        • UNKNOWN: Cannot determine readiness

    IMPORTANT:
        • This readiness means only: Execution may begin its own review
        • It does NOT mean: Execution may begin performing the Action
    """

    status: str = "NOT_READY"
    """Execution review readiness status."""


# =============================================================================
# SELECTED ACTION EXECUTION REVIEW READINESS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionReviewReadiness:
    """
    Execution review readiness assessment of a SelectedAction.

    PROPERTIES:
        • status: Current readiness status
        • blocking_issues: Issues preventing readiness
        • conditions_pending: Conditions not yet resolved
        • external_dependencies: Dependencies on external systems

    IMPORTANT:
        • Readiness is declarative, not a runtime state
    """

    status: str = "NOT_READY"
    """Current readiness status."""

    blocking_issues: Tuple[str, ...] = field(default_factory=tuple)
    """Issues preventing readiness."""

    conditions_pending: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions not yet resolved."""

    external_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies on external systems."""


# =============================================================================
# SELECTED ACTION EXECUTION REQUEST READINESS STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionRequestReadinessStatus:
    """
    Execution request readiness status of a SelectedAction.

    STATUSES:
        • NOT_READY: Not ready for execution request (basic blocking)
        • EXECUTION_REVIEW_REQUIRED: Must pass execution review first
        • EXECUTION_AUTHORITY_REQUIRED: Execution authority needed
        • EXECUTION_POLICY_REVIEW_REQUIRED: Policy review needed
        • EXECUTION_SECURITY_REVIEW_REQUIRED: Security review needed
        • EXECUTION_ENVIRONMENT_REVIEW_REQUIRED: Environment review needed
        • READY_FOR_REQUEST_PROJECTION: Ready for request projection
        • READY_WITH_CONDITIONS: Ready but with conditions
        • BLOCKED: Hard constraints block progression
        • STALE: External state has changed
        • INVALID: Artifact is invalid
        • UNKNOWN: Cannot determine readiness

    IMPORTANT:
        • This readiness means only: Request projection may be constructed
        • It does NOT mean: Concrete execution request is ready
    """

    status: str = "NOT_READY"
    """Execution request readiness status."""


# =============================================================================
# SELECTED ACTION EXECUTION REQUEST READINESS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionRequestReadiness:
    """
    Execution request readiness assessment of a SelectedAction.

    PROPERTIES:
        • status: Current readiness status
        • blocking_issues: Issues preventing readiness
        • execution_review_passed: Whether execution review passed
        • conditions_pending: Conditions not yet resolved

    IMPORTANT:
        • Action Selection may prepare projections, but Execution owns concrete requests
    """

    status: str = "NOT_READY"
    """Current readiness status."""

    blocking_issues: Tuple[str, ...] = field(default_factory=tuple)
    """Issues preventing readiness."""

    execution_review_passed: bool | None = None
    """Whether execution review passed (if known)."""

    conditions_pending: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions not yet resolved."""


# =============================================================================
# SELECTED ACTION EXPIRATION TRIGGER
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExpirationTrigger:
    """
    What triggers expiration of a SelectedAction.

    TRIGGERS:
        • ACTION_SELECTION_REQUEST_REVISION_CHANGED: Parent request revision changed
        • ARBITRATION_RESULT_REVISION_CHANGED: Source arbitration result revision changed
        • FRONTIER_REVISION_CHANGED: Selection frontier revision changed
        • CANDIDATE_REVISION_CHANGED: Selected candidate revision changed
        • ACTION_REVISION_CHANGED: Action revision changed
        • DECISION_REVISION_CHANGED: Decision revision changed
        • DECISION_SUSPENDED: Decision suspended or terminated
        • DECISION_REPLACED: Decision replaced by newer one
        • DECISION_TERMINATED: Decision permanently terminated
        • PLAN_CHANGED: Plan was modified
        • TARGET_REVISION_CHANGED: Target state revision changed
        • POLICY_CHANGED: Policy status changed
        • SECURITY_CHANGED: Security authorization status changed
        • AUTHORITY_CHANGED: Authority status changed
        • CAPABILITY_CHANGED: Required capability unavailable
        • RESOURCE_CONDITION_CHANGED: Resource availability changed
        • PRECONDITION_INVALIDATED: Precondition no longer holds
        • SELECTION_CONDITION_INVALIDATED: Selection condition invalidated
        • ACTION_EXPIRED: Action itself expired
        • SELECTION_EXPIRED: Selection time window passed

    IMPORTANT:
        • No internal timers or wall-clock acquisition in semantic package
        • Expiration is based on external state changes
    """

    trigger: str = "GENERAL"
    """Expiration trigger kind."""


# =============================================================================
# SELECTED ACTION EXPIRATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExpiration:
    """
    Expiration information for a SelectedAction.

    PROPERTIES:
        • trigger: What triggers expiration (not a timer!)
        • deadline: Expiration time or condition (ISO format string, not wall-clock)
        • expired: Whether currently expired
        • semantic_time_reference: External semantic time reference

    IMPORTANT:
        • No internal timers created in semantic package
        • Expiration is based on external state changes
    """

    trigger: str = "GENERAL"
    """What triggers expiration."""

    deadline: str = ""
    """Expiration time or condition (semantic time reference, not wall-clock)."""

    expired: bool = False
    """Whether currently expired."""

    semantic_time_reference: str = ""
    """External semantic time reference."""


# =============================================================================
# SELECTED ACTION INVALIDATION REASON
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionInvalidationReason:
    """
    Reasons a SelectedAction can be invalidated.

    REASONS:
        • ACTION_SELECTION_REQUEST_CHANGED: Request changed revision
        • FINAL_SELECTION_REQUEST_CHANGED: Final selection request changed
        • ARBITRATION_RESULT_CHANGED: Source arbitration result changed
        • SELECTION_FRONTIER_CHANGED: Frontier was rebuilt with new candidates
        • ACTION_SELECTION_OUTCOME_CHANGED: Selection outcome changed
        • CANDIDATE_CHANGED: Selected candidate changed revision
        • ACTION_CHANGED: Action representation changed revision
        • DECISION_CHANGED: Decision revision changed
        • DECISION_SUSPENDED: Decision suspended or terminated
        • DECISION_REPLACED: Decision replaced by newer one
        • DECISION_TERMINATED: Decision permanently terminated
        • COMMITMENT_CHANGED: Active commitment changed
        • PLAN_CHANGED: Plan was modified
        • TARGET_CHANGED: Target state changed revision
        • TARGET_REVISION_CHANGED: Target revision mismatch
        • POLICY_CHANGED: Policy status changed
        • SECURITY_CHANGED: Security authorization status changed
        • AUTHORITY_CHANGED: Authority status changed
        • CAPABILITY_CHANGED: Required capability unavailable
        • RESOURCE_PROJECTION_CHANGED: Resource availability changed
        • PRECONDITION_INVALIDATED: Precondition no longer holds
        • CONDITION_INVALIDATED: Selection condition invalidated
        • ROLLBACK_UNAVAILABLE: Rollback mechanism no longer available
        • COMPENSATION_UNAVAILABLE: Compensation mechanism no longer available
        • MONITORING_UNAVAILABLE: Monitoring no longer available
        • PRIVACY_SCOPE_CHANGED: Privacy constraints changed
        • EXPIRED: Semantic expiration reached
        • SUPERSEDED: Replaced by newer valid selection
        • CANCELLED: Cancelled externally
        • UNKNOWN: Reason cannot be determined

    IMPORTANT:
        • Invalidated selections are not mutated in place - new revisions or deltas created
        • History must preserve all invalidations for auditability
    """

    reason: str = "GENERAL"
    """Invalidation reason kind."""


# =============================================================================
# SELECTED ACTION INVALIDATION REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionInvalidationReference:
    """
    Reference to an invalidation event.

    PROPERTIES:
        • identity: Invalidation event identity (if any)
        • invalidated_revision: Which revision was invalidated
        • invalidation_time: When invalidation occurred (semantic time)
        • source: What caused the invalidation

    IMPORTANT:
        • Invalidations are immutable historical records
    """

    identity: str = ""
    """Invalidation event identity."""

    invalidated_revision: int = 1
    """Which revision was invalidated."""

    invalidation_time: str = ""
    """When invalidation occurred (semantic time)."""

    source: str = ""
    """What caused the invalidation."""


# =============================================================================
# SELECTED ACTION INVALIDATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionInvalidation:
    """
    A record of when a SelectedAction was invalidated.

    PROPERTIES:
        • reason: Why the action was invalidated
        • timestamp: When invalidation occurred (semantic time)
        • authority: Authority that performed invalidation
        • new_selection_reference: If replaced, reference to new selection
        • downstream_invalidations: Which downstream artifacts are now stale

    IMPORTANT:
        • Invalidated selections are not mutated in place - new revisions created
        • History must preserve all invalidations for auditability
    """

    reason: str = "GENERAL"
    """Why the action was invalidated."""

    timestamp: str = ""
    """When invalidation occurred (semantic time, not wall-clock)."""

    authority: str = ""
    """Authority that performed invalidation."""

    new_selection_reference: str | None = None
    """If replaced, reference to the new selection."""

    downstream_invalidations: Tuple[str, ...] = field(default_factory=tuple)
    """Which downstream artifacts are now stale."""


# =============================================================================
# SELECTED ACTION DOWNSTREAM INVALIDATION TARGET
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionDownstreamInvalidationTarget:
    """
    A downstream artifact that becomes stale due to invalidation.

    PROPERTIES:
        • artifact_type: Type of downstream artifact (e.g., 'execution_request')
        • artifact_reference: Reference to the specific artifact
        • invalidated_by_selection_revision: Which revision's change caused this

    IMPORTANT:
        • Downstream ownership retains authority over application of invalidation
    """

    artifact_type: str = "EXECUTION_REQUEST"
    """Type of downstream artifact."""

    artifact_reference: str = ""
    """Reference to the specific artifact."""

    invalidated_by_selection_revision: int = 1
    """Which revision's change caused this."""


# =============================================================================
# SELECTED ACTION SUSPENSION REASON
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionSuspensionReason:
    """
    Reasons a SelectedAction can be suspended.

    REASONS:
        • AUTHORIZATION_PENDING: Awaiting authorization review
        • POLICY_REVIEW_PENDING: Policy review pending
        • SECURITY_REVIEW_PENDING: Security review pending
        • TARGET_STALE: Target revision mismatch
        • CAPABILITY_UNAVAILABLE: Required capability unavailable
        • RESOURCE_UNAVAILABLE: Resources not available
        • PRECONDITION_UNSATISFIED: Preconditions not satisfied
        • CONDITION_PENDING: Selection conditions not yet resolved
        • EXECUTION_ENVIRONMENT_UNAVAILABLE: Environment not ready
        • MONITORING_UNAVAILABLE: Monitoring not available
        • DECISION_SUSPENDED: Governing decision suspended
        • USER_REQUEST: User-requested suspension
        • HIGHER_AUTHORITY_REQUEST: Higher authority requested suspension

    IMPORTANT:
        • Suspension preserves history and restoration semantics
    """

    reason: str = "GENERAL"
    """Suspension reason kind."""


# =============================================================================
# SELECTED ACTION SUSPENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionSuspension:
    """
    A record of when a SelectedAction was suspended.

    PROPERTIES:
        • reason: Why the action was suspended
        • suspension_time: When suspension occurred (semantic time)
        • authority: Authority that performed suspension
        • unresolved_obligations: What remains to be resolved
        • restoration_conditions: Conditions for restoration

    IMPORTANT:
        • Suspension preserves history - artifact is not deleted
    """

    reason: str = "GENERAL"
    """Why the action was suspended."""

    suspension_time: str = ""
    """When suspension occurred (semantic time)."""

    authority: str = ""
    """Authority that performed suspension."""

    unresolved_obligations: Tuple[str, ...] = field(default_factory=tuple)
    """What remains to be resolved."""

    restoration_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions for restoration."""


# =============================================================================
# SELECTED ACTION RESTORATION REVIEW
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionRestorationReview:
    """
    Review required before restoring a suspended SelectedAction.

    PROPERTIES:
        • current_selection_revision: Current revision being restored
        • current_action_revision: Current referenced action revision
        • current_candidate_revision: Current candidate revision
        • current_decision_commitment: Current governing decision/commitment status
        • current_target: Current target state
        • current_policy_status: Current policy approval status
        • current_security_status: Current security authorization status
        • current_authority: Current authority status
        • current_capability_status: Current capability availability
        • current_resource_context: Current resource availability
        • expiration_check: Whether still within expiration window

    IMPORTANT:
        • Restoration requires current-state review, not stale projections reused
    """

    selection_revision_current: int = 1
    """Current revision being restored."""

    action_revision_current: int = 1
    """Current referenced action revision."""

    candidate_revision_current: int = 1
    """Current candidate revision."""

    decision_commitment_status: str = ""
    """Current governing decision/commitment status."""

    target_current: str = ""
    """Current target state reference."""

    policy_status: str = ""
    """Current policy approval status."""

    security_status: str = ""
    """Current security authorization status."""

    authority_status: str = ""
    """Current authority status."""

    capability_status: str = ""
    """Current capability availability status."""

    resource_context_current: str = ""
    """Current resource availability context."""

    expiration_check_passed: bool | None = None
    """Whether still within expiration window (if known)."""


# =============================================================================
# SELECTED ACTION REPLACEMENT REASON
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionReplacementReason:
    """
    Reasons a SelectedAction can be replaced.

    REASONS:
        • NEW_CANDIDATE_SELECTED: New candidate was selected instead
        • ACTION_REVISION_REQUIRES_RESELECTION: Action revision changed requires new selection
        • TARGET_CHANGED: Target state changed materially
        • POLICY_CHANGED: Policy status changed
        • SECURITY_CHANGED: Security authorization status changed
        • AUTHORITY_CHANGED: Authority scope or status changed
        • CAPABILITY_CHANGED: Required capability availability changed
        • RESOURCE_CHANGED: Resource availability changed materially
        • PRIMARY_ACTION_INVALIDATED: Primary action invalidated
        • FALLBACK_SELECTED: Fallback action activated
        • EXECUTION_REVIEW_REJECTED: Execution review rejected the selection
        • USER_CHANGED_SELECTION: User requested different selection
        • EXECUTIVE_CHANGED_SELECTION: Executive decision selected different action

    IMPORTANT:
        • Replacement creates a new immutable artifact - old one is not mutated
        • Prior history preserved for auditability
    """

    reason: str = "FRONTIER_REBUILD"
    """Replacement reason kind."""


# =============================================================================
# SELECTED ACTION REPLACEMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionReplacement:
    """
    A record of one selected action being replaced by another.

    PROPERTIES:
        • prior_selection_reference: Reference to the old selection
        • new_selection_reference: Reference to the new selection
        • reason: Why replacement occurred
        • authority: Authority that performed replacement
        • candidate_evaluation_changed: Whether candidate evaluation changed
        • arbitration_changed: Whether arbitration result changed
        • new_final_selection_occurred: Whether this was a re-selection

    IMPORTANT:
        • Old selection is not mutated; new immutable artifact created
        • Replacement preserves history for auditability
    """

    prior_selection_reference: str = ""
    """Reference to the old selection."""

    new_selection_reference: str = ""
    """Reference to the new selection."""

    reason: str = "FRONTIER_REBUILD"
    """Why replacement occurred."""

    authority: str = ""
    """Authority that performed replacement."""

    candidate_evaluation_changed: bool | None = None
    """Whether candidate evaluation changed (if known)."""

    arbitration_changed: bool | None = None
    """Whether arbitration result changed (if known)."""

    new_final_selection_occurred: bool = False
    """Whether this was a re-selection with new final action selection."""


# =============================================================================
# SELECTED ACTION SUPERSESION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionSupersession:
    """
    A record of one selected action being superseded by another.

    SUPERSESION CAUSES:
        • NEWER_VALID_SELECTION: Newer valid selection exists
        • REQUEST_REVISION_CHANGED: Request revision changed
        • FRONTIER_REVISION_CHANGED: Frontier was rebuilt
        • AUTHORITY_SELECTS_ANOTHER: Authority selected different candidate
        • EXPIRED: Prior selection expired
        • POLICY_CHANGED: Policy or security changed
        • INVALIDATED_BY_EXTERNAL_EVENT: External event invalidated prior

    IMPORTANT:
        • Supersession does NOT cancel execution of prior
        • That's a separate concern (execution layer)
    """

    prior_selection_reference: str = ""
    """Reference to the superseded selection."""

    new_selection_reference: str = ""
    """Reference to the new selection."""

    reason: str = "FRONTIER_REBUILD"
    """Why supersession occurred."""

    supersession_time: str = ""
    """When supersession occurred (semantic time)."""

    authority: str = ""
    """Authority that performed supersession."""


# =============================================================================
# SELECTED ACTION CANCELLATION REASON
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionCancellationReason:
    """
    Reasons a SelectedAction can be cancelled.

    REASONS:
        • USER_CANCELLED: User requested cancellation
        • EXECUTIVE_CANCELLED: Executive decision cancelled selection
        • AUTHORITY_REVOKED: Authority revoked authorization
        • DECISION_TERMINATED: Governing decision terminated
        • REQUEST_CANCELLED: Source request was cancelled
        • SELECTION_WITHDRAWN: Selection was withdrawn
        • POLICY_PROHIBITED: Policy now prohibits the action
        • SECURITY_PROHIBITED: Security no longer authorizes the action
        • TARGET_REMOVED: Target no longer exists
        • CONTEXT_INVALID: Selection context is no longer valid

    IMPORTANT:
        • Cancellation means selection is no longer intended for downstream review
        • It does NOT cancel an already running Execution Attempt
    """

    reason: str = "USER_CANCELLED"
    """Cancellation reason kind."""


# =============================================================================
# SELECTED ACTION CANCELLATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionCancellation:
    """
    A record of when a SelectedAction was cancelled.

    PROPERTIES:
        • reason: Why the action was cancelled
        • cancellation_time: When cancellation occurred (semantic time)
        • authority: Authority that performed cancellation

    IMPORTANT:
        • Cancellation of selection does not cancel active Execution Attempt
        • That requires separate execution cancellation contract
    """

    reason: str = "USER_CANCELLED"
    """Why the action was cancelled."""

    cancellation_time: str = ""
    """When cancellation occurred (semantic time)."""

    authority: str = ""
    """Authority that performed cancellation."""


# =============================================================================
# SELECTED ACTION TERMINATION REASON
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionTerminationReason:
    """
    Reasons a SelectedAction can be terminated.

    REASONS:
        • REPLACED: Replaced by newer selection
        • SUPERSEDED: Superseded by newer selection
        • EXPIRED: Semantic expiration reached
        • CANCELLED: Cancelled externally
        • INVALIDATED: Explicitly invalidated
        • DECISION_TERMINATED: Governing decision terminated
        • REQUEST_TERMINATED: Source request terminated
        • NO_LONGER_REQUIRED: No longer needed

    IMPORTANT:
        • Termination is semantic lifecycle end, not execution outcome
    """

    reason: str = "REPLACED"
    """Termination reason kind."""


# =============================================================================
# SELECTED ACTION TERMINATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionTermination:
    """
    A record of when a SelectedAction was terminated.

    PROPERTIES:
        • reason: Why the action was terminated
        • termination_time: When termination occurred (semantic time)
        • authority: Authority that performed termination

    IMPORTANT:
        • Termination is distinct from Execution success or failure
    """

    reason: str = "REPLACED"
    """Why the action was terminated."""

    termination_time: str = ""
    """When termination occurred (semantic time)."""

    authority: str = ""
    """Authority that performed termination."""


# =============================================================================
# SELECTED ACTION DELTA KIND
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionDeltaKind:
    """
    Kinds of deltas for a SelectedAction.

    DELTA KINDS:
        • CREATE: Initial selection created
        • REVISE: Revision with semantic changes
        • ADD_AUTHORIZATION_REVIEW: Authorization review added
        • UPDATE_AUTHORIZATION_STATUS: Authorization status changed
        • ADD_POLICY_REVIEW: Policy review added
        • ADD_SECURITY_REVIEW: Security review added
        • ADD_TARGET_REVIEW: Target review added
        • ADD_CAPABILITY_REVIEW: Capability review added
        • ADD_RESOURCE_REVIEW: Resource review added
        • ADD_PRECONDITION_REVIEW: Precondition review added
        • ADD_CONDITION: New condition added
        • REVISE_CONDITION: Condition modified
        • ADD_EXECUTION_REVIEW_REQUIREMENT: Execution review requirement added
        • UPDATE_EXECUTION_REVIEW_READINESS: Execution review readiness changed
        • UPDATE_EXECUTION_REQUEST_READINESS: Execution request readiness changed
        • SUSPEND: Action suspended
        • RESTORE: Action restored from suspension
        • INVALIDATE: Action invalidated
        • REPLACE: Action replaced by new selection
        • SUPERSEDE: Action superseded
        • CANCEL: Selection cancelled
        • TERMINATE: Lifecycle terminated

    IMPORTANT:
        • Deltas are declarative and immutable
        • Each delta creates a new revision, not mutates in place
    """

    kind: str = "CREATE"
    """Delta kind."""


# =============================================================================
# SELECTED ACTION DELTA
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionDelta:
    """
    A declarative change record for a SelectedAction.

    PROPERTIES:
        • delta_kind: What type of change occurred
        • revision_before: Revision before the change
        • revision_after: Revision after the change
        • changed_fields: Which fields were affected
        • reason: Why the change occurred
        • authority: Authority that performed the change

    IMPORTANT:
        • Deltas are immutable historical records for audit and replay
        • No runtime objects embedded in deltas
    """

    delta_kind: str = "CREATE"
    """Delta kind."""

    revision_before: int = 0
    """Revision before the change."""

    revision_after: int = 1
    """Revision after the change."""

    changed_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Which fields were affected."""

    reason: str = ""
    """Why the change occurred."""

    authority: str = ""
    """Authority that performed the change."""


# =============================================================================
# SELECTED ACTION TRANSITION KIND
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionTransitionKind:
    """
    Kinds of transitions for a SelectedAction lifecycle.

    TRANSITIONS:
        • CREATED: Initial creation
        • VALIDATION_STARTED: Validation process started
        • VALIDATED: Validation completed successfully
        • VALIDATED_WITH_CONDITIONS: Validated with conditions
        • AUTHORIZATION_REQUESTED: Authorization review requested
        • AUTHORIZED: Authorization granted
        • AUTHORIZED_WITH_CONDITIONS: Authorized with conditions
        • AUTHORIZATION_DENIED: Authorization denied
        • POLICY_REVIEW_REQUESTED: Policy review requested
        • POLICY_APPROVED: Policy approved
        • POLICY_PROHIBITED: Policy prohibits action
        • SECURITY_REVIEW_REQUESTED: Security review requested
        • SECURITY_APPROVED: Security authorized
        • SECURITY_DENIED: Security denied authorization
        • TARGET_REVIEWED: Target review completed
        • CAPABILITY_REVIEWED: Capability review completed
        • RESOURCE_REVIEWED: Resource review completed
        • PRECONDITIONS_REVIEWED: Precondition review completed
        • READY_FOR_EXECUTION_REVIEW: Ready for execution review
        • READY_FOR_EXECUTION_REQUEST_PROJECTION: Ready for request projection
        • SUSPENDED: Action suspended
        • RESTORED: Action restored from suspension
        • INVALIDATED: Action invalidated
        • REPLACED: Action replaced
        • SUPERSEDED: Action superseded
        • EXPIRED: Semantic expiration reached
        • CANCELLED: Selection cancelled
        • TERMINATED: Lifecycle terminated

    IMPORTANT:
        • Transitions exclude Execution runtime states (EXECUTING, SUCCEEDED, etc.)
    """

    kind: str = "CREATED"
    """Transition kind."""


# =============================================================================
# SELECTED ACTION TRANSITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionTransition:
    """
    A lifecycle transition for a SelectedAction.

    PROPERTIES:
        • from_state: State before the transition
        • to_state: State after the transition
        • transition_kind: What kind of transition occurred
        • timestamp: When transition occurred (semantic time)
        • authority: Authority that performed the transition

    IMPORTANT:
        • Transitions are immutable historical records
        • No runtime execution states included
    """

    from_state: str = "CREATED"
    """State before the transition."""

    to_state: str = "VALIDATION_PENDING"
    """State after the transition."""

    transition_kind: str = "VALIDATION_STARTED"
    """What kind of transition occurred."""

    timestamp: str = ""
    """When transition occurred (semantic time)."""

    authority: str = ""
    """Authority that performed the transition."""


# =============================================================================
# SELECTED ACTION CONTINUATION KIND
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionContinuationKind:
    """
    Advisory continuation kinds for a SelectedAction.

    CONTINUATIONS (advisory, not executable!):
        • COMPLETE: No further action needed from this subsystem
        • VALIDATE_SELECTION: Validate selection state
        • REQUEST_ACTION_AUTHORIZATION: Request authorization review
        • REQUEST_POLICY_REVIEW: Policy review required
        • REQUEST_SECURITY_REVIEW: Security review required
        • REQUEST_TARGET_REVIEW: Target review required
        • REQUEST_CAPABILITY_REVIEW: Capability review required
        • REQUEST_RESOURCE_REVIEW: Resource review required
        • REQUEST_PRECONDITION_REVIEW: Precondition review required
        • REQUEST_EXECUTION_ENVIRONMENT_REVIEW: Environment review required
        • REQUEST_USER_CONFIRMATION: User confirmation needed (external)
        • REQUEST_EXECUTIVE_REVIEW: Executive review needed
        • REQUEST_HIGHER_AUTHORITY: Higher authority needed
        • REQUEST_MONITORING_PREPARATION: Monitoring setup needed
        • REQUEST_ROLLBACK_PREPARATION: Rollback setup needed
        • REQUEST_COMPENSATION_PREPARATION: Compensation setup needed
        • PROCEED_TO_EXECUTION_REVIEW: Ready for execution review
        • PRODUCE_EXECUTION_REQUEST_PROJECTION: Produce request projection
        • SUSPEND: Suspend until conditions resolved
        • RESTORE: Attempt restoration from suspension
        • RESELECT_ACTION: Select different candidate
        • REEVALUATE_ACTIONS: Re-evaluate all candidates
        • REARBITRATE: Run arbitration again
        • REVISE_ACTION_SELECTION_REQUEST: Request needs revision
        • WAIT: Wait for external input
        • CANCEL: Cancel this selection
        • FAIL: Selection failed and cannot proceed

    IMPORTANT:
        • Continuation performs no scheduling or invocation
        • Later execution layer decides when and how to act on continuation
    """

    kind: str = "PROCEED_TO_EXECUTION_REVIEW"
    """Continuation kind."""


# =============================================================================
# SELECTED ACTION CONTINUATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionContinuation:
    """
    Advisory continuation information for a SelectedAction.

    PROPERTIES:
        • kind: What should happen next (advisory only)
        • delay_reason: Why waiting is needed (if applicable)
        • required_input: What input would enable proceeding

    IMPORTANT:
        • Continuation performs no scheduling or invocation
        • Later execution layer decides when and how to act on continuation
    """

    kind: str = "PROCEED_TO_EXECUTION_REVIEW"
    """What should happen next (advisory only)."""

    delay_reason: str = ""
    """Why waiting is needed (if applicable)."""

    required_input: Tuple[str, ...] = field(default_factory=tuple)
    """What input would enable proceeding to next step."""


# =============================================================================
# SELECTED ACTION STATE REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionStateReference:
    """
    Reference to a SelectedAction's current state.

    PROPERTIES:
        • identity: Selected Action Identity
        • revision: Current revision number
        • lifecycle_state: Current lifecycle state
        • validity_status: Current validity status
        • completeness_level: Current completeness level
        • freshness_status: Current freshness status

    IMPORTANT:
        • State reference is subordinate to Action Selection State
    """

    identity: str = ""
    """Selected Action Identity."""

    revision: int = 1
    """Current revision number."""

    lifecycle_state: str = "CREATED"
    """Current lifecycle state."""

    validity_status: str = "UNKNOWN"
    """Current validity status."""

    completeness_level: str = "UNKNOWN"
    """Current completeness level."""

    freshness_status: str = "UNKNOWN"
    """Current freshness status."""


# =============================================================================
# SELECTED ACTION STATE SUMMARY
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionStateSummary:
    """
    A non-authoritative summary of a SelectedAction's state.

    PROPERTIES:
        • identity_and_revision: Current identity and revision
        • underlying_action_reference: Referenced Action
        • candidate_reference: Referenced Candidate
        • lifecycle_state: Current lifecycle state
        • current_blockers: Issues blocking progression
        • authorization_summary: Authorization status summary
        • policy_and_security_summary: Policy and Security summary
        • readiness_summary: Readiness assessment summary
        • freshness_summary: Freshness status summary
        • invalidation_summary: Any invalidations
        • continuation: What should happen next (advisory)
        • provenance: Provenance information

    IMPORTANT:
        • Summary is non-authoritative - always reference the canonical state
    """

    identity_and_revision: str = ""
    """Current identity and revision."""

    underlying_action_reference: str = ""
    """Referenced Action."""

    candidate_reference: str = ""
    """Referenced Candidate."""

    lifecycle_state: str = "CREATED"
    """Current lifecycle state."""

    current_blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Issues blocking progression."""

    authorization_summary: str = ""
    """Authorization status summary."""

    policy_and_security_summary: str = ""
    """Policy and Security summary."""

    readiness_summary: str = ""
    """Readiness assessment summary."""

    freshness_summary: str = ""
    """Freshness status summary."""

    invalidation_summary: Tuple[str, ...] = field(default_factory=tuple)
    """Any invalidations."""

    continuation: str = "WAIT"
    """What should happen next (advisory)."""

    provenance: str = ""
    """Provenance information."""


# =============================================================================
# SELECTED ACTION HISTORY ENTRY
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionHistoryEntry:
    """
    One entry in the history of a SelectedAction.

    EVENTS:
        • CREATE: Initial selection created
        • SELECTION: Action selected from frontier
        • REVISION: Revision occurred
        • AUTHORIZATION_REVIEW: Authorization review performed
        • POLICY_REVIEW: Policy review performed
        • SECURITY_REVIEW: Security review performed
        • TARGET_REVIEW: Target review performed
        • CAPABILITY_REVIEW: Capability review performed
        • RESOURCE_REVIEW: Resource review performed
        • PRECONDITION_REVIEW: Precondition review performed
        • READINESS_CHANGE: Readiness status changed
        • SUSPENSION: Action suspended
        • RESTORATION: Action restored from suspension
        • INVALIDATION: Action invalidated
        • REPLACEMENT: Selection replaced
        • SUPERSESION: Selection superseded
        • CANCELLATION: Selection cancelled
        • TERMINATION: Lifecycle terminated

    IMPORTANT:
        • History is append-only and bounded
    """

    event_kind: str = "CREATE"
    """Type of history entry."""

    timestamp: str = ""
    """When event occurred (semantic time)."""

    authority: str = ""
    """Authority that performed the event."""

    details: Tuple[str, ...] = field(default_factory=tuple)
    """Event-specific details."""


# =============================================================================
# SELECTED ACTION HISTORY
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionHistory:
    """
    Bounded history of a SelectedAction.

    PROPERTIES:
        • entries: History entries in chronological order
        • max_entries: Maximum number of entries (for boundedness)

    IMPORTANT:
        • History is append-only - never mutates past entries
        • Bounded to prevent unbounded memory consumption
    """

    entries: Tuple[SelectedActionHistoryEntry, ...] = field(default_factory=tuple)
    """History entries in chronological order."""

    max_entries: int = 100
    """Maximum number of entries (for boundedness)."""

    @property
    def is_full(self) -> bool:
        """Whether the history has reached its maximum size."""
        return len(self.entries) >= self.max_entries


# =============================================================================
# SELECTED ACTION LINEAGE RELATION KIND
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionLineageRelationKind:
    """
    Kinds of lineage relations for a SelectedAction.

    RELATIONS:
        • SELECTED_FROM_CANDIDATE: This action was selected from the candidate pool
        • REFERENCES_ACTION: References an Action artifact
        • DERIVED_FROM_SELECTION_OUTCOME: Derived from selection outcome
        • GOVERNED_BY_DECISION: Governed by an Executive Decision
        • GOVERNED_BY_COMMITMENT: Governed by an active Commitment
        • REVISION_OF: This is a revision of a prior SelectedAction
        • REPLACED_BY: Replaced by another action
        • REPLACES: Replaced this action
        • SUPERSEDED_BY: Superseded by another action
        • SUPERSEDES: Superseded this action
        • SUSPENDED_FROM: Suspended from prior state
        • RESTORED_FROM: Restored from prior suspended state
        • INVALIDATED_BY: Invalidated by external event or authority

    IMPORTANT:
        • Lineage preserves cross-subsystem references without changing ownership
    """

    kind: str = "SELECTED_FROM_CANDIDATE"
    """Lineage relation kind."""


# =============================================================================
# SELECTED ACTION LINEAGE RELATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionLineageRelation:
    """
    A lineage relation for a SelectedAction.

    PROPERTIES:
        • relation_kind: Kind of relation
        • related_identity: Identity of the related artifact
        • related_revision: Revision of the related artifact (if known)

    IMPORTANT:
        • Lineage is semantic - no runtime objects embedded
    """

    relation_kind: str = "SELECTED_FROM_CANDIDATE"
    """Kind of lineage relation."""

    related_identity: str = ""
    """Identity of the related artifact."""

    related_revision: int | None = None
    """Revision of the related artifact (if known)."""


# =============================================================================
# SELECTED ACTION LINEAGE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionLineage:
    """
    Lineage information for a SelectedAction.

    PROPERTIES:
        • relations: All lineage relations
        • history_reference: Reference to full history (if separate)

    IMPORTANT:
        • Lineage preserves cross-subsystem references without changing ownership
    """

    relations: Tuple[SelectedActionLineageRelation, ...] = field(default_factory=tuple)
    """All lineage relations."""

    history_reference: str | None = None
    """Reference to full history (if stored separately)."""


# =============================================================================
# SELECTED ACTION EXECUTION REVIEW PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionReviewProjection:
    """
    An execution review projection for a SelectedAction.

    This projection requests Execution-owned review of the SelectedAction.

    IMPORTANT:
        • Projection must not contain executable commands or callbacks
        • Runtime objects are forbidden in projections

    PROPERTIES:
        • projection_identity: Unique identifier for this projection
        • projection_revision: Revision number
        • selected_action_reference: Reference to the selected action
        • action_reference: Referenced Action artifact
        • candidate_reference: Referenced Candidate artifact
        • selection_outcome_reference: Source selection outcome reference
        • decision_reference: Governing Decision reference (if any)
        • commitment_reference: Active Commitment reference (if any)
        • context: Semantic context references
        • scope: Bounded scope of the action
        • target_reference: Target being operated on
        • Preconditions: Required preconditions
        • constraints: Hard constraints that must hold
        • authority_requirements: Authority requirements
        • policy_review: Policy review references (not interpretation)
        • security_review: Security review references (not execution)
        • capability_requirements: Required capabilities
        • resource_requirements: Resource requirements
        • environment_requirements: Environment requirements
        • reversibility: Reversibility assessment
        • rollback: Rollback review references
        • compensation: Compensation review references
        • idempotency: Idempotency assessment
        • retryability: Retryability assessment
        • monitoring_requirements: What must be monitored
        • expiration: When this projection expires (semantic time)
        • privacy: Privacy scope constraints

    IMPORTANT:
        • This is a semantic projection, not an executable request
    """

    projection_identity: str = ""
    """Unique identifier for this projection."""

    projection_revision: int = 1
    """Projection revision number."""

    selected_action_reference: str = ""
    """Reference to the selected action."""

    action_reference: str = ""
    """Referenced Action artifact."""

    candidate_reference: str = ""
    """Referenced Candidate artifact."""

    selection_outcome_reference: str = ""
    """Source selection outcome reference."""

    decision_reference: str = ""
    """Governing Decision reference (if any)."""

    commitment_reference: str = ""
    """Active Commitment reference (if any)."""

    context: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic context references."""

    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of the action."""

    target_reference: str = ""
    """Target being operated on."""

    preconditions: Tuple[str, ...] = field(default_factory=tuple)
    """Required Preconditions."""

    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Hard constraints that must hold."""

    authority_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Authority requirements."""

    policy_review: str = ""
    """Policy review reference (not interpretation)."""

    security_review: str = ""
    """Security review reference (not execution)."""

    capability_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Required capabilities."""

    resource_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Resource requirements."""

    environment_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Environment requirements."""

    reversibility: str = ""
    """Reversibility assessment."""

    rollback: str = ""
    """Rollback review reference."""

    compensation: str = ""
    """Compensation review reference."""

    idempotency: str = ""
    """Idempotency assessment."""

    retryability: str = ""
    """Retryability assessment."""

    monitoring_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """What must be monitored."""

    expiration: str = ""
    """When this projection expires (semantic time)."""

    privacy: str = ""
    """Privacy scope constraints."""


# =============================================================================
# SELECTED ACTION EXECUTION REQUEST PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionRequestProjection:
    """
    An execution-request projection for a SelectedAction.

    This is the terminal Action Selection product - a complete semantic projection
    containing all information required for Execution to decide whether and how to
    construct its own concrete ExecutionRequest.

    IMPORTANT:
        • This is NOT a concrete ExecutionRequest
        • It must not contain runtime callbacks or tool invocations
        • Runtime objects are strictly forbidden

    PROPERTIES:
        • selected_action_reference: Exact Selected Action reference
        • action_reference: Exact Action artifact reference
        • candidate_reference: Exact Candidate artifact reference
        • selection_outcome_reference: Exact Selection Outcome reference
        • validated_execution_review_results: All validated review results
        • execution_authority_requirements: Execution authority requirements
        • unresolved_execution_conditions: Any conditions that remain
        • target: Target being operated on (semantic, not runtime handle)
        • scope: Action scope
        • Preconditions: Required preconditions
        • expected_effects: Intended effects of the action
        • unacceptable_effects: Effects that must not occur
        • policy_review: Policy review references (not interpretation)
        • security_review: Security review references (not execution)
        • capability_requirements: Required capabilities
        • resource_requirements: Resource requirements
        • execution_environment_requirements: Environment requirements
        • reversibility: Reversibility assessment
        • rollback: Rollback review references
        • compensation: Compensation review references
        • idempotency: Idempotency assessment
        • retryability: Retryability assessment
        • monitoring_requirements: What must be monitored
        • privacy: Privacy scope constraints
        • semantic_time: Semantic time reference for this projection
        • expiration: When this projection expires (semantic time)
        • provenance: Provenance information

    IMPORTANT:
        • Action Selection owns the projection
        • Execution owns construction and acceptance of concrete ExecutionRequests
    """

    selected_action_reference: str = ""
    """Exact Selected Action reference."""

    action_reference: str = ""
    """Exact Action artifact reference."""

    candidate_reference: str = ""
    """Exact Candidate artifact reference."""

    selection_outcome_reference: str = ""
    """Exact Selection Outcome reference."""

    validated_execution_review_results: Tuple[str, ...] = field(default_factory=tuple)
    """All validated review results."""

    execution_authority_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Execution authority requirements."""

    unresolved_execution_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Any conditions that remain unresolved."""

    target: str = ""
    """Target being operated on (semantic reference, not runtime handle)."""

    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Action scope."""

    preconditions: Tuple[str, ...] = field(default_factory=tuple)
    """Required Preconditions."""

    expected_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Intended effects of the action."""

    unacceptable_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Effects that must not occur."""

    policy_review: str = ""
    """Policy review reference (not interpretation)."""

    security_review: str = ""
    """Security review reference (not execution)."""

    capability_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Required capabilities."""

    resource_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Resource requirements."""

    execution_environment_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Execution environment requirements."""

    reversibility: str = ""
    """Reversibility assessment."""

    rollback: str = ""
    """Rollback review reference."""

    compensation: str = ""
    """Compensation review reference."""

    idempotency: str = ""
    """Idempotency assessment."""

    retryability: str = ""
    """Retryability assessment."""

    monitoring_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """What must be monitored."""

    privacy: str = ""
    """Privacy scope constraints."""

    semantic_time: str = ""
    """Semantic time reference (external, not wall-clock)."""

    expiration: str = ""
    """When this projection expires (semantic time)."""

    provenance: str = ""
    """Provenance information."""


# =============================================================================
# SELECTED ACTION EXECUTION PROJECTION RESPONSE STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionExecutionProjectionResponseStatus:
    """
    Response status for execution projection acceptance.

    STATUSES:
        • ACCEPTED_FOR_EXECUTION_REVIEW: Accepted for downstream review
        • ACCEPTED_WITH_CONDITIONS: Accepted with explicit conditions
        • EXECUTION_REQUEST_CREATED: Concrete ExecutionRequest was created
        • MORE_INFORMATION_REQUIRED: Additional information needed
        • AUTHORITY_REQUIRED: Authorization authority needed
        • POLICY_REVIEW_REQUIRED: Policy review needed first
        • SECURITY_REVIEW_REQUIRED: Security review needed first
        • TARGET_REVIEW_REQUIRED: Target review needed first
        • CAPABILITY_UNAVAILABLE: Required capability unavailable
        • RESOURCE_UNAVAILABLE: Required resources unavailable
        • ENVIRONMENT_UNAVAILABLE: Environment not ready
        • PRECONDITION_FAILED: Precondition not satisfied
        • PROJECTION_STALE: Projection is stale
        • SELECTED_ACTION_STALE: Selected Action is stale
        • REJECTED: Execution rejected the projection
        • DEFERRED: Review deferred to later mechanism
        • UNKNOWN: Cannot determine response status

    IMPORTANT:
        • This response remains externally owned by Execution
        • Action Selection consumes it as a semantic artifact
    """

    status: str = "ACCEPTED_FOR_EXECUTION_REVIEW"
    """Response status kind."""


# =============================================================================
# SELECTED ACTION VALIDATION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedActionValidationResult:
    """
    Result of validating a SelectedAction.

    RESULTS:
        • VALID: Passed all validation checks
        • VALID_WITH_WARNINGS: Valid but with warnings
        • VALID_WITH_CONDITIONS: Valid but with conditions
        • VALID_WITH_LIMITATIONS: Valid but with limitations
        • INCOMPLETE: Missing required information
        • STALE: External state is stale
        • AUTHORIZATION_REQUIRED: Authorization needed
        • POLICY_REVIEW_REQUIRED: Policy review needed
        • SECURITY_REVIEW_REQUIRED: Security review needed
        • TARGET_REVIEW_REQUIRED: Target review needed
        • CAPABILITY_REVIEW_REQUIRED: Capability review needed
        • RESOURCE_REVIEW_REQUIRED: Resource review needed
        • PRECONDITION_REVIEW_REQUIRED: Precondition review needed
        • EXECUTION_REVIEW_REQUIRED: Execution review required first
        • SUSPENDED: Currently suspended
        • INVALIDATED: Explicitly invalidated
        • EXPIRED: Semantic expiration reached
        • INVALID: Failed validation checks
        • UNKNOWN: Cannot determine validity

    IMPORTANT:
        • Validation is side-effect-free - it doesn't modify the artifact
    """

    result: str = "VALID"
    """Validation result status."""

    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Specific validation findings."""


# =============================================================================
# CANONICAL SELECTED ACTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SelectedAction:
    """
    An immutable semantic artifact representing one accepted Action Candidate.

    A SelectedAction is:
        - NOT an executing Action (execution is separate phase)
        - NOT an ExecutionRequest (that's downstream)
        - NOT a tool invocation (implementation detail)
        - NOT a runtime command (runtime belongs elsewhere)

    PROPERTIES:
        • identity: Unique identifier for this selected action
        • revision: Monotonically increasing revision number
        • schema_version: Schema version for serialization compatibility
        • candidate_reference: Reference to exact accepted Action Candidate
        • action_reference: Reference to exact Action representation

        • context: Semantic context references (bounded)
        • scope: Bounded scope of the action

        • selection_policy_reference: Which policy governed the selection
        • selection_mode: How selection was made
        • selection_authority: Selection authority reference

        • conditions: Explicit conditions for validity
        • constraints: Hard constraints that must be satisfied
        • requirements: Execution requirements

        • preconditions: Required Preconditions
        • authorization: Authorization state and review
        • policy_review: Policy review references (not interpretation)
        • security_review: Security review references (not execution)

        • target_review: Target review reference (not live inspection)
        • capability_review: Capability review reference (not implementation)
        • resource_review: Resource review reference (no allocation)

        • reversibility_review: Reversibility assessment
        • rollback_review: Rollback review reference (no execution)
        • compensation_review: Compensation review reference (no execution)
        • idempotency_review: Idempotency assessment
        • retryability_review: Retryability assessment

        • monitoring_requirements: Monitoring requirements declared
        • execution_review_requirements: Execution review requirements
        • privacy: Privacy scope constraints

        • validity: Validity assessment
        • completeness: Completeness assessment
        • freshness: Freshness assessment (revision-specific)
        • lifecycle: Lifecycle state (before execution runtime)
        • state: State reference

        • expiration: When this selection expires (not a timer!)
        • invalidations: Records of any invalidation events

        • execution_review_readiness: Ready for downstream review?
        • execution_request_readiness: Ready for request projection?

        • justification: Why this candidate was selected
        • limitations: Known limitations in the selection

    IMPORTANT LAWS:
        • SELECTED-ACTION-LAW-001: Selected Action is semantic and never executes itself.
        • SELECTED-ACTION-LAW-002: Identity is distinct from Action, Candidate,
          ExecutionRequest, and ExecutionAttempt Identity.
        • SELECTED-ACTION-LAW-003: Every SelectedAction references one exact Candidate
          revision and one exact Action revision.
        • SELECTED-ACTION-LAW-004: Selection does not imply Action authorization.
        • SELECTED-ACTION-LAW-005: Authorization does not imply Execution authority.
        • SELECTED-ACTION-LAW-006: Policy and Security remain externally authoritative.
        • SELECTED-ACTION-LAW-007: Every readiness status is declarative.
        • SELECTED-ACTION-LAW-008: Execution-review readiness is distinct from
          execution-request readiness.
        • SELECTED-ACTION-LAW-009: Execution-request readiness is distinct from
          Execution authorization.
        • SELECTED-ACTION-LAW-010: Selected Action revisions never overwrite history.

    IMPORT SAFETY:
        - No Policy engine invocation
        - No Security engine invocation
        - No target access
        - No capability implementation call
        - No resource allocation
        - No concrete ExecutionRequest construction
    """

    # Identity
    identity: str = ""
    """Unique identifier for this selected action."""

    revision: int = 1
    """Monotonically increasing revision number."""

    schema_version: str = "4.5.8"
    """Schema version for serialization compatibility."""

    # References to accepted artifacts
    candidate_reference: str = ""
    """Reference to exact accepted Action Candidate."""

    action_reference: str = ""
    """Reference to exact Action representation."""

    # Context and scope
    context: SelectedActionContext | None = None
    """Semantic context references (bounded)."""

    scope: SelectedActionScope | None = None
    """Bounded scope of the action."""

    # Selection metadata
    selection_policy_reference: str = ""
    """Which policy governed the selection."""

    selection_mode: str = "DETERMINISTIC"
    """How selection was made."""

    selection_authority: str = ""
    """Selection authority reference."""

    # Conditions and constraints
    conditions: Tuple[SelectedActionCondition, ...] = field(default_factory=tuple)
    """Explicit conditions that must hold for validity."""

    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Hard constraints that must be satisfied."""

    requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Execution requirements."""

    # Precondition review
    preconditions: Tuple[SelectedActionPreconditionReview, ...] = field(
        default_factory=tuple
    )
    """Required Preconditions and their review status."""

    # Authorization state
    authorization: SelectedActionAuthorizationState | None = None
    """Authorization state and review."""

    # Policy and Security reviews (references only, no interpretation)
    policy_review: SelectedActionPolicyReview | None = None
    """Policy review references (not interpretation)."""

    security_review: SelectedActionSecurityReview | None = None
    """Security review references (not execution)."""

    # Operational reviews (references only)
    target_review: SelectedActionTargetReview | None = None
    """Target review reference (not live inspection)."""

    capability_review: SelectedActionCapabilityReview | None = None
    """Capability review reference (not implementation)."""

    resource_review: SelectedActionResourceReview | None = None
    """Resource review reference (no allocation)."""

    # Reversibility and recovery reviews
    reversibility_review: SelectedActionReversibilityReview | None = None
    """Reversibility assessment."""

    rollback_review: SelectedActionRollbackReview | None = None
    """Rollback review reference (no execution)."""

    compensation_review: SelectedActionCompensationReview | None = None
    """Compensation review reference (no execution)."""

    idempotency_review: SelectedActionIdempotencyReview | None = None
    """Idempotency assessment."""

    retryability_review: SelectedActionRetryabilityReview | None = None
    """Retryability assessment."""

    # Monitoring and requirements
    monitoring_requirements: Tuple[SelectedActionMonitoringRequirement, ...] = field(
        default_factory=tuple
    )
    """Monitoring requirements declared (not performed)."""

    execution_review_requirements: Tuple[
        SelectedActionExecutionReviewRequirement, ...
    ] = field(default_factory=tuple)
    """Execution review requirements."""

    privacy: str = "PUBLIC"
    """Privacy scope constraints."""

    # Assessment states
    validity: SelectedActionValidity | None = None
    """Validity assessment."""

    completeness: SelectedActionCompleteness | None = None
    """Completeness assessment."""

    freshness: SelectedActionFreshness | None = None
    """Freshness assessment (revision-specific)."""

    lifecycle: str = "CREATED"
    """Lifecycle state (before execution runtime)."""

    state_reference: str = ""
    """State reference for external tracking."""

    # Lifecycle management
    expiration: SelectedActionExpiration | None = None
    """When this selection expires (not a timer!)."""

    invalidations: Tuple[SelectedActionInvalidationReference, ...] = field(
        default_factory=tuple
    )
    """Records of any invalidation events."""

    # Readiness assessments
    execution_review_readiness: str = "NOT_READY"
    """Ready for downstream review? (declarative)."""

    execution_request_readiness: str = "NOT_READY"
    """Ready for request projection? (declarative)."""

    # Justification and assessment
    justification: str = ""
    """Why this candidate was selected."""

    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations in the selection."""

    def is_ready_for_execution_review(self) -> bool:
        """
        Check if this SelectedAction is ready for execution review.

        Returns True only when all required reviews have passed and readiness
        status indicates readiness. This does NOT mean execution may begin -
        it means execution may begin its OWN review process.
        """
        # Must be in a ready state
        if self.execution_review_readiness != "READY_FOR_EXECUTION_REVIEW":
            return False

        # Must have authorization if required
        if (
            self.authorization is not None
            and self.authorization.status not in ("AUTHORIZED", "AUTHORIZED_WITH_CONDITIONS")
        ):
            return False

        # Policy must be compliant (not prohibited)
        if (
            self.policy_review is not None
            and self.policy_review.status == "PROHIBITED"
        ):
            return False

        # Security must authorize (if review performed)
        if (
            self.security_review is not None
            and self.security_review.status not in ("AUTHORIZED", "AUTHORIZED_WITH_CONDITIONS")
        ):
            return False

        return True

    def is_ready_for_execution_request_projection(self) -> bool:
        """
        Check if this SelectedAction is ready for execution request projection.

        This means: Execution may construct a concrete ExecutionRequest.
        Note: This still doesn't mean execution will occur - that's up to
        the Execution subsystem's own review and authorization.
        """
        # Must pass execution review readiness check first
        if not self.is_ready_for_execution_review():
            return False

        # Request projection requires higher confidence
        if self.execution_request_readiness != "READY_FOR_REQUEST_PROJECTION":
            return False

        # Freshness must be current (stale selections cannot proceed)
        if self.freshness is not None and self.freshness.status != "CURRENT":
            return False

        # No unresolved invalidations
        if len(self.invalidations) > 0:
            return False

        return True


# =============================================================================
# END PHASE 4.5.8 SELECTED ACTION ARCHITECTURE
# =============================================================================

__all__ = [
    # Identity types
    "SelectedActionIdentity",
    "SelectedActionRevision",
    "SelectedActionSchemaVersion",

    # Reference types
    "SelectedActionReference",
    "SelectedActionRevisionReference",
    "SelectedActionRevisionMetadata",

    # Context and scope
    "SelectedActionContext",
    "SelectedActionScope",

    # Lifecycle
    "SelectedActionLifecycleState",

    # Assessment types
    "SelectedActionValidity",
    "SelectedActionCompleteness",
    "SelectedActionFreshnessDimension",
    "SelectedActionFreshness",

    # Authorization
    "SelectedActionAuthorizationStatus",
    "SelectedActionAuthorizationState",
    "SelectedActionAuthorizationReview",
    "SelectedActionAuthorizationCondition",

    # Policy review (reference only)
    "SelectedActionPolicyReviewStatus",
    "SelectedActionPolicyReview",

    # Security review (reference only)
    "SelectedActionSecurityReviewStatus",
    "SelectedActionSecurityReview",

    # Target review (reference only)
    "SelectedActionTargetReviewStatus",
    "SelectedActionTargetReview",

    # Precondition review
    "SelectedActionPreconditionReview",

    # Operational reviews
    "SelectedActionCapabilityReviewStatus",
    "SelectedActionCapabilityReview",
    "SelectedActionResourceReviewStatus",
    "SelectedActionResourceReview",

    # Reversibility and recovery reviews
    "SelectedActionReversibilityReview",
    "SelectedActionRollbackReview",
    "SelectedActionCompensationReview",
    "SelectedActionIdempotencyReview",
    "SelectedActionRetryabilityReview",

    # Monitoring requirements
    "SelectedActionMonitoringRequirementKind",
    "SelectedActionMonitoringRequirement",

    # Privacy and environment requirements
    "SelectedActionPrivacyReview",
    "SelectedActionExecutionEnvironmentRequirement",

    # Execution review requirements
    "SelectedActionExecutionReviewRequirementKind",
    "SelectedActionExecutionReviewRequirement",

    # Readiness assessments
    "SelectedActionExecutionReviewReadinessStatus",
    "SelectedActionExecutionReviewReadiness",
    "SelectedActionExecutionRequestReadinessStatus",
    "SelectedActionExecutionRequestReadiness",

    # Expiration and invalidation
    "SelectedActionExpirationTrigger",
    "SelectedActionExpiration",
    "SelectedActionInvalidationReason",
    "SelectedActionInvalidationReference",
    "SelectedActionInvalidation",
    "SelectedActionDownstreamInvalidationTarget",

    # Suspension and restoration
    "SelectedActionSuspensionReason",
    "SelectedActionSuspension",
    "SelectedActionRestorationReview",

    # Replacement, supersession, cancellation, termination
    "SelectedActionReplacementReason",
    "SelectedActionReplacement",
    "SelectedActionSupersession",
    "SelectedActionCancellationReason",
    "SelectedActionCancellation",
    "SelectedActionTerminationReason",
    "SelectedActionTermination",

    # State management
    "SelectedActionDeltaKind",
    "SelectedActionDelta",
    "SelectedActionTransitionKind",
    "SelectedActionTransition",
    "SelectedActionContinuationKind",
    "SelectedActionContinuation",
    "SelectedActionStateReference",
    "SelectedActionStateSummary",
    "SelectedActionHistoryEntry",
    "SelectedActionHistory",
    "SelectedActionLineageRelationKind",
    "SelectedActionLineageRelation",
    "SelectedActionLineage",

    # Execution boundary projections
    "SelectedActionExecutionReviewProjection",
    "SelectedActionExecutionRequestProjection",
    "SelectedActionExecutionProjectionResponseStatus",

    # Validation
    "SelectedActionValidationResult",

    # Canonical model
    "SelectedAction",
]