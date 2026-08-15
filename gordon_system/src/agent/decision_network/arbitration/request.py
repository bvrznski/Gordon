# Gordon Cognitive Architecture - Phase 4.5.6
# Action Arbitration Request
# =========================

"""
Action Arbitration Request type definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# ACTION ARBITRATION REQUEST ID TYPES
# =============================================================================

ActionArbitrationRequestId = str
"""Unique identifier for an arbitration request."""

ActionArbitrationRequestRevision = int
"""Revision number for an arbitration request."""


# =============================================================================
# ACTION SELECTION REQUEST REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionRequestReference:
    """
    Reference to a parent Action Selection Request.
    
    PROPERTIES:
        • selection_request_id: Unique identifier for the selection request
        • revision: Selection request revision number
    """
    
    selection_request_id: ActionArbitrationRequestId
    """Unique identifier for the selection request."""
    
    revision: int = 1
    """Monotonically increasing revision number."""


# =============================================================================
# EVALUATED POOL REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluatedActionCandidatePoolReference:
    """
    Reference to an evaluated Action Candidate Pool.
    
    PROPERTIES:
        • pool_id: Unique identifier for the evaluated pool
        • revision: Pool revision number
    """
    
    pool_id: str = ""
    """Unique identifier for the evaluated pool."""
    
    revision: int = 1
    """Monotonically increasing revision number."""


# =============================================================================
# ACTION ARBITRATION PURPOSE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationPurpose:
    """
    The purpose of an arbitration request.
    
    PROPERTIES:
        • kind: Canonical purpose category
        • description: Human-readable purpose description
        • scope: Bounded scope for this arbitration
    
    ARBITRATION PURPOSES:
        • BUILD_SELECTION_FRONTIER: Prepare frontiers for selection
        • RESOLVE_DOMINANCE: Identify dominance relations
        • ASSESS_COMPARABILITY: Determine candidate comparability
        • ASSESS_COMPATIBILITY: Assess compatibility relationships
        • ASSESS_CONFLICT: Identify conflicts between candidates
        • ASSESS_INTERFERENCE: Assess interference patterns
        • ASSESS_EQUIVALENCE: Identify equivalent candidates
        • ASSESS_FALLBACKS: Identify fallback relationships
        • ASSESS_CONDITIONAL_ALTERNATIVES: Assess conditional alternatives
        • ASSESS_MANDATORY_ALTERNATIVES: Identify mandatory preservation
        • PREPARE_SELECTION_RECOMMENDATION: Prepare selection guidance
        • GENERAL_ARBITRATION: General arbitration without specific goal
    """
    
    kind: str = "GENERAL_ARBITRATION"
    """Canonical purpose category."""
    
    description: str = ""
    """Human-readable purpose description."""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope for this arbitration (dimension names, etc.)."""


# =============================================================================
# ACTION ARBITRATION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationContext:
    """
    Semantic context for an arbitration request.
    
    Context contains references to related artifacts without embedding them.
    
    PROPERTIES:
        • action_selection_request_reference: Parent selection context
        • evaluated_pool_reference: Candidates being arbitrated
        • executive_decision_reference: Governing decision (if any)
        • commitment_reference: Active commitments (if any)
        • strategy_reference: Strategy context (if any)
        • plan_reference: Plan context (if any)
        • semantic_time: Semantic time reference for the arbitration
        • authority_context: Authority context references
    
    CONTEXT REMAINS BOUNDED:
        • Contains only references, not full artifacts
        • No implementation callbacks
        • No runtime state
    """
    
    action_selection_request_reference: ActionSelectionRequestReference | None = None
    """Parent Action Selection Request reference."""
    
    evaluated_pool_reference: EvaluatedActionCandidatePoolReference | None = None
    """Evaluated candidate pool being arbitrated."""
    
    executive_decision_reference: str = ""
    """Governing Executive Decision reference."""
    
    commitment_reference: str = ""
    """Active Commitment reference."""
    
    strategy_reference: str = ""
    """Strategy context reference."""
    
    plan_reference: str = ""
    """Plan context reference."""
    
    semantic_time: str = ""
    """Semantic time reference for this arbitration."""
    
    authority_context: Tuple[str, ...] = field(default_factory=tuple)
    """Authority context references."""


# =============================================================================
# ACTION ARBITRATION SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationScope:
    """
    Bounded scope for arbitration operations.
    
    Every arbitration must be explicitly bounded to prevent unbounded
    comparisons and resource consumption.
    
    PROPERTIES:
        • candidate_subset: Which candidates to consider (None = all)
        • comparison_dimensions: Dimensions for pairwise comparison
        • maximum_pairwise_comparisons: Upper bound on comparisons
        • maximum_frontier_size: Upper bound on frontier size
        • authority_scope: Authority context scope
        • temporal_scope: Time-bound scope
    
    BOUNDED BY DESIGN:
        • Never unbounded (uses explicit limits)
        • Capacity overflow is explicit
        • Deterministic coverage when limits reached
    """
    
    candidate_subset: Tuple[str, ...] | None = None
    """Candidate IDs to consider. None means all in evaluated pool."""
    
    comparison_dimensions: Tuple[str, ...] = field(default_factory=tuple)
    """Dimension names for pairwise comparison."""
    
    maximum_pairwise_comparisons: int = 1000
    """Maximum pairwise comparisons allowed (prevents O(n^2) explosion)."""
    
    maximum_frontier_size: int = 100
    """Maximum candidates in any frontier."""
    
    authority_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Authority IDs to consider."""
    
    temporal_scope: str = ""
    """Temporal scope (e.g., "session", "task", "immediate")."""


# =============================================================================
# ACTION ARBITRATION CRITERION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationCriterion:
    """
    An arbitration criterion for evaluating candidates.
    
    Criteria define what dimensions should be assessed during arbitration.
    
    PROPERTIES:
        • kind: Canonical criterion category
        • weight: Relative importance (0.0 to 1.0)
        • threshold: Minimum acceptable value (optional)
        • description: Human-readable description
    
    CRITERION KINDS:
        • ELIGIBILITY: Must meet eligibility requirements
        • ADMISSIBILITY: Must be admissible
        • FEASIBILITY: Can this actually work?
        • SUITABILITY: Is this appropriate?
        • ADEQUACY: Does it satisfy the purpose?
        • GOAL_ALIGNMENT: Aligns with goals?
        • COMMITMENT_ALIGNMENT: Aligns with commitments?
        • STRATEGY_ALIGNMENT: Aligns with strategy?
        • PLAN_COMPATIBILITY: Compatible with plan?
        • POLICY_COMPLIANCE: Complies with policy?
        • SECURITY_COMPLIANCE: Complies with security rules?
        • EXPECTED_BENEFIT: Expected positive outcomes
        • EXPECTED_COST: Expected resource cost
        • EXPECTED_RISK: Expected negative outcomes
        • REVERSIBILITY: Can it be reversed if needed?
        • CONFIDENCE: Assessment confidence level
    """
    
    kind: str = "GENERAL"
    """Canonical criterion category."""
    
    weight: float = 1.0
    """Relative importance (0.0 to 1.0)."""
    
    threshold: float | None = None
    """Minimum acceptable value (optional)."""
    
    description: str = ""
    """Human-readable description."""


# =============================================================================
# ACTION ARBITRATION CONSTRAINT (HARD)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationConstraint:
    """
    A hard constraint that must be satisfied.
    
    Hard constraints are prohibitions - candidates violating them cannot
    remain in the admissible selection frontier unless explicitly permitted.
    
    PROPERTIES:
        • kind: Canonical constraint category
        • source: Source of the constraint (policy, security, authority)
        • source_owner: Owner of the constraint source
        • scope: Bounded scope where constraint applies
        • description: Human-readable description
    
    CONSTRAINT KINDS:
        • POLICY_PROHIBITION: Forbidden by policy
        • SECURITY_PROHIBITION: Forbidden by security rules
        • AUTHORITY_REQUIREMENT: Requires specific authority
        • TARGET_SCOPE_REQUIREMENT: Must be within target scope
        • CAPABILITY_REQUIREMENT: Requires specific capabilities
        • PRIVACY_REQUIREMENT: Privacy constraints
        • REVERSIBILITY_REQUIREMENT: Must be reversible
        • MANDATORY_PRECONDITION: Precondition must hold
        • UNACCEPTABLE_OUTCOME: Outcome is unacceptable
        • RESOURCE_LIMIT: Resource consumption limit
        • TEMPORAL_LIMIT: Time-bound constraint
    
    IMPORTANT:
        • Hard constraints are NOT converted to score penalties
        • Violation means exclusion unless explicit exception path
        • Source authority must be preserved
    """
    
    kind: str = "GENERAL_PROHIBITION"
    """Canonical constraint category."""
    
    source: str = ""
    """Source of the constraint (policy, security, authority)."""
    
    source_owner: str = ""
    """Owner of the constraint source."""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope where constraint applies."""
    
    description: str = ""
    """Human-readable description."""


# =============================================================================
# ACTION ARBITRATION PREFERENCE (SOFT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationPreference:
    """
    A soft preference for ranking candidates.
    
    Preferences are not prohibitions - they guide selection but do not
    grant authority. They may be overridden by hard constraints or vetoes.
    
    PROPERTIES:
        • kind: Canonical preference category
        • strength: How strongly to prefer (weak, moderate, strong, lexicographic)
        • description: Human-readable description
    
    PREFERENCE KINDS:
        • PREFER_REVERSIBLE: Prefer reversible options
        • PREFER_READ_ONLY: Prefer read-only operations
        • PREFER_LOWER_COST: Prefer lower resource cost
        • PREFER_LOWER_RISK: Prefer lower risk
        • PREFER_HIGHER_INFORMATION_GAIN: Prefer more information
        • PREFER_SHORTER_HORIZON: Prefer shorter time horizon
        • PREFER_GREATER_MONITORABILITY: Prefer observable actions
        • PREFER_EXISTING_CAPABILITY: Prefer existing capabilities
        • PREFER_NO_EXTERNAL_DEPENDENCY: Avoid external dependencies
        • PREFER_PLAN_ALIGNMENT: Align with plan
    
    PREFERENCE STRENGTHS:
        • WEAK: Slight preference
        • MODERATE: Noticeable preference
        • STRONG: Strong preference
        • VERY_STRONG: Very strong preference
        • LEXICOGRAPHIC: Hard priority over other dimensions
    """
    
    kind: str = "GENERAL_PREFERENCE"
    """Canonical preference category."""
    
    strength: str = "MODERATE"
    """How strongly to prefer (WEAK, MODERATE, STRONG, VERY_STRONG, LEXICOGRAPHIC)."""
    
    description: str = ""
    """Human-readable description."""


# =============================================================================
# ACTION ARBITRATION VETO
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationVeto:
    """
    A veto that blocks a candidate from selection.
    
    Vetoes are hard prohibitions with explicit authority. They may have
    exception paths for special circumstances.
    
    PROPERTIES:
        • kind: Canonical veto category
        • status: Current veto status (active, pending review, resolved, etc.)
        • source: Source of the veto
        • source_owner: Owner of the veto source
        • reviewed_candidate_id: Exact candidate ID that triggered veto
        • conditions: Conditions for exception paths
        • expiration: Optional expiration time
        • provenance: Veto origin information
    
    VETO KINDS:
        • POLICY_VETO: Forbidden by policy
        • SECURITY_VETO: Forbidden by security rules
        • AUTHORITY_VETO: Missing required authority
        • PRIVACY_VETO: Privacy constraint violation
        • TARGET_STATE_VETO: Target state not acceptable
        • DECISION_STATE_VETO: Decision state incompatible
        • COMMITMENT_VETO: Commitment conflict
        • UNACCEPTABLE_OUTCOME_VETO: Outcome is unacceptable
        • IRREVERSIBILITY_VETO: Irreversible action not permitted
    
    VETO STATUS:
        • ACTIVE: Currently blocking
        • ACTIVE_WITH_EXCEPTION_PATH: May be overridden under conditions
        • PENDING_REVIEW: Under review
        • RESOLVED: Resolved through exception or review
        • SUPERSEDED: Superseded by newer veto
        • STALE: No longer applicable
    """
    
    kind: str = "GENERAL_VETO"
    """Canonical veto category."""
    
    status: str = "ACTIVE"
    """Current veto status (ACTIVE, ACTIVE_WITH_EXCEPTION_PATH, PENDING_REVIEW, etc.)."""
    
    source: str = ""
    """Source of the veto."""
    
    source_owner: str = ""
    """Owner of the veto source."""
    
    reviewed_candidate_id: str = ""
    """Exact candidate ID that triggered this veto."""
    
    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions for exception paths (empty if no exceptions)."""
    
    expiration: str = ""
    """Optional expiration timestamp or condition."""
    
    provenance: str = ""
    """Veto origin information."""


# =============================================================================
# ACTION MANDATORY CANDIDATE REQUIREMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionMandatoryCandidateRequirement:
    """
    Requirement to preserve a candidate in the selection frontier.
    
    Some candidates must be preserved regardless of other considerations,
    though they may not be preferred or selected.
    
    PROPERTIES:
        • kind: Canonical mandatory type
        • candidate_id: ID of the required candidate
        • reason: Why it must be preserved
        • priority: Relative importance
    
    MANDATORY KINDS:
        • USER_REQUIRED: Explicitly requested by user
        • POLICY_REQUIRED: Required by policy
        • SECURITY_REQUIRED: Required for security escalation
        • ROLLBACK_REQUIRED: Required rollback action
        • COMPENSATION_REQUIRED: Required compensation action
        • NO_OP_REQUIRED: Required no-operation alternative
        • WAIT_REQUIRED: Required wait alternative
        • AUTHORITY_REQUEST_REQUIRED: Required authority request
        • SAFETY_CHECK_REQUIRED: Required safety check
    
    IMPORTANT:
        • Mandatory preservation does NOT imply final selection
        • Still subject to hard constraints and vetoes
        • May be placed on special frontiers (fallback, safety)
    """
    
    kind: str = "GENERAL"
    """Canonical mandatory type."""
    
    candidate_id: str = ""
    """ID of the required candidate."""
    
    reason: str = ""
    """Why it must be preserved."""
    
    priority: int = 0
    """Relative importance (-100 to 100)."""


# =============================================================================
# ACTION ARBITRATION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationRequest:
    """
    Request to perform arbitration on evaluated Action Candidates.
    
    This request specifies what candidates to arbitrate, under what context,
    and with what rules. It does NOT contain the candidate data itself - that
    comes from external sources or evaluation context.
    
    PROPERTIES:
        • request_id: Unique identifier for this arbitration request
        • revision: Request revision number (for tracking updates)
        • action_selection_request_reference: Parent selection request
        • evaluated_pool_reference: Candidates to arbitrate
        • purpose: What we're trying to achieve
        • scope: Bounded scope for this arbitration
        • context: Semantic context references
        • criteria: Arbitration criteria (what to assess)
        • hard_constraints: Hard prohibitions (what is forbidden)
        • preferences: Soft preferences (ranking guidance)
        • vetoes: Hard vetoes (blocking rules)
        • mandatory_requirements: Candidates that must be preserved
        • required_frontier_kinds: Which frontiers to produce
        • completion_requirements: How complete the arbitration must be
    
    NOT RESPONSIBLE FOR:
        - Storing actual candidate data
        - Performing evaluation (evaluation is separate phase)
        - Making final selection (deferred to Phase 4.5.7)
        - Allocating resources
        - Executing actions
    
    IMPORTANT LAWS:
        • ACTION-ARB-LAW-013: Recommendations are advisory
        • ACTION-ARB-LAW-014: Continuation performs no scheduling
        • ACTION-ARB-LAW-015: Equivalent inputs produce equivalent outputs
        • ACTION-ARB-LAW-016: Capacity limitations are explicit
    """
    
    request_id: ActionArbitrationRequestId
    """Unique identifier for this arbitration request."""
    
    revision: int = 1
    """Monotonically increasing revision number."""
    
    action_selection_request_reference: ActionSelectionRequestReference | None = None
    """Parent Action Selection Request reference."""
    
    evaluated_pool_reference: EvaluatedActionCandidatePoolReference | None = None
    """Evaluated candidate pool to arbitrate."""
    
    purpose: ActionArbitrationPurpose = field(default_factory=ActionArbitrationPurpose)
    """What we're trying to achieve through arbitration."""
    
    scope: ActionArbitrationScope = field(default_factory=ActionArbitrationScope)
    """Bounded scope for this arbitration."""
    
    context: ActionArbitrationContext = field(default_factory=ActionArbitrationContext)
    """Semantic context references."""
    
    criteria: Tuple[ActionArbitrationCriterion, ...] = field(default_factory=tuple)
    """ Arbitration criteria (what dimensions to assess)."""
    
    hard_constraints: Tuple[ActionArbitrationConstraint, ...] = field(
        default_factory=tuple
    )
    """Hard prohibitions that must be satisfied."""
    
    preferences: Tuple[ActionArbitrationPreference, ...] = field(default_factory=tuple)
    """Soft preferences for ranking guidance."""
    
    vetoes: Tuple[ActionArbitrationVeto, ...] = field(default_factory=tuple)
    """Hard vetoes that block candidates."""
    
    mandatory_requirements: Tuple[ActionMandatoryCandidateRequirement, ...] = field(
        default_factory=tuple
    )
    """Candidates that must be preserved regardless of other considerations."""
    
    required_frontier_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Frontier kinds to produce (general, safety, Pareto, etc.)."""
    
    @classmethod
    def from_pool(
        cls,
        evaluated_pool_reference: EvaluatedActionCandidatePoolReference,
        request_id: ActionArbitrationRequestId = "",
    ) -> ActionArbitrationRequest:
        """
        Create an arbitration request from an evaluated pool reference.
        
        Args:
            evaluated_pool_reference: Reference to candidates to arbitrate
            request_id: Optional unique identifier for this request
            
        Returns:
            New ActionArbitrationRequest with default settings
        """
        return cls(
            request_id=request_id or "arbitration_request_default",
            evaluated_pool_reference=evaluated_pool_reference,
        )