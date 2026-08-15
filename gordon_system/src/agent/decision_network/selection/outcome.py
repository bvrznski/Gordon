# Gordon Cognitive Architecture - Phase 4.5.7
# ===========================================
#
"""
ActionSelectionOutcome types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# OUTCOME ID TYPES
# =============================================================================

ActionSelectionOutcomeIdentity = str
"""Unique identifier for an action selection outcome."""

ActionSelectionOutcomeRevision = int
"""Monotonically increasing revision number for an outcome."""


# =============================================================================
# ACTION SELECTION OUTCOME KIND
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionOutcomeKind:
    """
    The kind of outcome produced by final action selection.
    
    OUTCOME KINDS:
        • ACTION_SELECTED: One candidate was selected as SelectedAction
        • ACTION_SELECTED_WITH_CONDITIONS: Selection has explicit conditions
        • CONDITIONAL_ACTION_SELECTED: Conditional action accepted
        • FALLBACK_ACTION_SELECTED: Fallback action activated
        • USER_CHOICE_APPLIED: User choice determined the selection
        • EXECUTIVE_CHOICE_APPLIED: Executive decision determined the selection
        • AUTHORITY_CHOICE_APPLIED: Authority's explicit choice was applied
        • REPLAY_SELECTION_APPLIED: Prior selection replayed from record
        • NO_SELECTION: No candidate was selected (valid semantic outcome)
        • SELECTION_DEFERRED: Selection deferred to later mechanism
        • USER_CHOICE_REQUIRED: User choice required but not provided
        • EXECUTIVE_REVIEW_REQUIRED: Executive review needed before proceeding
        • AUTHORITY_REQUIRED: Selection authority needed but not provided
        • POLICY_REVIEW_REQUIRED: Policy review pending before selection
        • SECURITY_REVIEW_REQUIRED: Security review pending before selection
        • MORE_EVIDENCE_REQUIRED: Insufficient evidence to make selection
        • REQUEST_STALE: Request revision is stale
        • FRONTIER_STALE: Frontier revision is stale
        • NO_ELIGIBLE_CANDIDATES: No candidates meet eligibility criteria
        • NO_ADMISSIBLE_CANDIDATES: No candidates are admissible
        • SELECTION_BLOCKED: Selection blocked by hard constraint
        • SELECTION_CANCELLED: Selection cancelled externally
        • FAILED: Selection failed due to system error
    
    IMPORTANT:
        • Each kind must be explicit, not implicit
        • NO_SELECTION is NOT an error - it's a valid semantic outcome
        • Outcome kind determines downstream continuation
    """
    
    kind: str = "ACTION_SELECTED"
    """Canonical outcome kind."""


# =============================================================================
# ACTION SELECTION OUTCOME STATUS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionOutcomeStatus:
    """
    The overall status of a selection outcome.
    
    STATUSES:
        • COMPLETE: Selection completed successfully
        • COMPLETE_WITH_CONDITIONS: Selection complete but with conditions
        • COMPLETE_WITH_LIMITATIONS: Selection has known limitations
        • DEFERRED: Selection deferred to later mechanism
        • BLOCKED: Hard constraints block selection
        • NO_SELECTION: No candidate was selected (valid outcome)
        • STALE: Request or frontier is stale
        • EXPIRED: Selection time window passed
        • INVALID: Outcome structure is invalid
        • FAILED: Selection failed due to system error
        • UNKNOWN: Status cannot be determined
    
    IMPORTANT:
        • Status is distinct from kind
        • COMPLETE_WITH_CONDITIONS != COMPLETE (conditions matter downstream)
        • NO_SELECTION != FAILED (no-selection is valid)
    """
    
    status: str = "COMPLETE"
    """Overall outcome status."""


# =============================================================================
# ACTION SELECTION COMPLETENESS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionCompleteness:
    """
    Assessment of how complete the selection was.
    
    COMPLETENESS LEVELS:
        • COMPLETE: All candidates assessed and disposition assigned
        • SUBSTANTIALLY_COMPLETE: Most candidates assessed with minor gaps
        • PARTIAL: Only some candidates were assessed
        • FRONTIER_LIMITED: Frontier size limited assessment coverage
        • EVALUATION_LIMITED: Evaluation depth was insufficient
        • ARBITRATION_LIMITED: Arbitration did not cover all pairs
        • EVIDENCE_LIMITED: Insufficient evidence for thorough assessment
        • AUTHORITY_LIMITED: Authority review was partial
        • POLICY_LIMITED: Policy review was incomplete
        • SECURITY_LIMITED: Security review was incomplete
        • CONTEXT_LIMITED: Context information was insufficient
        • NO_SELECTION: No selection made (completeness not applicable)
        • INVALID: Outcome structure is invalid
    
    IMPORTANT:
        • Lower completeness means lower confidence in selection
        • Downstream systems should consider completeness when acting
    """
    
    level: str = "COMPLETE"
    """Completeness level."""
    
    candidates_assessed: int = 0
    """Number of frontier candidates that received a disposition."""
    
    candidates_total: int = 0
    """Total number of candidates in frontier."""


# =============================================================================
# ACTION SELECTION CONTINUATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionContinuation:
    """
    Advisory information about what should happen next after selection.
    
    CONTINUATIONS (advisory, not executable!):
        • COMPLETE: No further action needed from this subsystem
        • PROCEED_TO_EXECUTION_REVIEW: Ready for downstream execution review
        • REQUEST_EXECUTION_AUTHORIZATION: Need execution authorization
        • REQUEST_USER_CHOICE: User choice required (external user system)
        • REQUEST_EXECUTIVE_REVIEW: Executive review needed
        • REQUEST_AUTHORITY: Selection authority needed
        • REQUEST_POLICY_REVIEW: Policy review pending before proceeding
        • REQUEST_SECURITY_REVIEW: Security review pending before proceeding
        • REQUEST_MORE_EVIDENCE: More evidence needed to proceed
        • REQUEST_CONTEXT_REFRESH: Context information needs updating
        • REQUEST_TARGET_REFRESH: Target state needs refresh
        • REQUEST_CAPABILITY_REVIEW: Capability availability check needed
        • REQUEST_RESOURCE_REVIEW: Resource availability check needed
        • REVISE_SELECTION_POLICY: Selection policy may need adjustment
        • REVISE_ACTION_SELECTION_REQUEST: Request needs revision
        • REGENERATE_CANDIDATES: New candidates should be generated
        • REEVALUATE_CANDIDATES: Candidates should be reevaluated
        • REARBITRATE: Arbitration should be run again
        • WAIT: Nothing to do, wait for external input
        • DEFER: Defer to later mechanism
        • CANCEL: Cancel the selection request
        • FAIL: Selection failed and cannot proceed
    
    IMPORTANT:
        • Continuation performs no scheduling or invocation
        • Later execution layer decides when and how to act on continuation
    """
    
    continuation: str = "PROCEED_TO_EXECUTION_REVIEW"
    """What should happen next (advisory only)."""
    
    delay_reason: str = ""
    """If waiting, why the delay is needed."""
    
    required_input: Tuple[str, ...] = field(default_factory=tuple)
    """What input would enable proceeding to next step."""


# =============================================================================
# ACTION SELECTION CONFIDENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionConfidence:
    """
    Assessment of confidence in the selection.
    
    PROPERTIES:
        • level: Numerical confidence (0.0 to 1.0)
        • basis: What supports this confidence
    
    IMPORTANT:
        • Confidence does NOT imply authorization
        • Confidence does NOT guarantee success
        • Low confidence may require higher review threshold
    """
    
    level: float = 0.5
    """Confidence level (0.0 to 1.0)."""
    
    basis: str = "SELECTION_POLICY_APPLIED"
    """What supports the confidence assessment."""


# =============================================================================
# ACTION SELECTION UNCERTAINTY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionUncertaintySource:
    """
    A source of uncertainty in the selection process.
    
    UNCERTAINTY SOURCES:
        • FRONTIER_INCOMPLETE: Frontier may be missing candidates
        • PAIRWISE_COMPARISON_LIMITED: Not all candidate pairs compared
        • EVIDENCE_INCOMPLETE: Insufficient evidence for assessment
        • TARGET_STATE_UNCERTAIN: Target state not well understood
        • POLICY_INTERPRETATION_PENDING: Policy meaning unclear
        • SECURITY_STATUS_UNCERTAIN: Security authorization status unclear
        • AUTHORITY_SCOPE_UNCERTAIN: Authority scope boundaries unclear
        • OUTCOME_UNCERTAIN: Expected outcomes uncertain
        • RESOURCE_STATE_UNCERTAIN: Resource availability unclear
        • CAPABILITY_STATE_UNCERTAIN: Capability availability unclear
        • USER_PREFERENCE_UNCERTAIN: User preferences not well known
        • UNKNOWN: Uncertainty source cannot be determined
    
    IMPORTANT:
        • Uncertainty sources must remain explicit in outcome
        • High uncertainty may block selection or require deferral
    """
    
    source: str = "PAIRWISE_COMPARISON_LIMITED"
    """Source of uncertainty."""
    
    severity: float = 0.0
    """How severe this uncertainty is (0.0 to 1.0)."""


# =============================================================================
# ACTION SELECTION LIMITATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionLimitation:
    """
    A known limitation in the selection process.
    
    LIMITATIONS:
        • CAPACITY_LIMITED_FRONTIER: Frontier size limited by capacity
        • PARTIAL_EVALUATION: Evaluation was partial not complete
        • PARTIAL_ARBITRATION: Arbitration coverage was incomplete
        • UNRESOLVED_NON_BLOCKING_TIE: Tied but tie-breaker wasn't applied
        • EXTERNAL_REFERENCE_UNRESOLVED: External reference couldn't be resolved
        • CONDITIONAL_AUTHORIZATION: Authorization has conditions
        • CONDITIONAL_POLICY_APPROVAL: Policy approval is conditional
        • CONDITIONAL_SECURITY_APPROVAL: Security approval is conditional
        • TARGET_FRESHNESS_LIMIT: Target may not be current
        • TEMPORAL_LIMIT: Selection based on time-bound information
        • PRIVACY_LIMIT: Privacy constraints limited assessment
        • GENERAL: General limitation without specific category
    
    IMPORTANT:
        • Limitations must remain visible downstream
        • Downstream systems should consider limitations when acting
    """
    
    kind: str = "GENERAL"
    """Limitation kind."""
    
    description: str = ""
    """Description of the limitation."""
    
    impact: float = 0.0
    """Impact on selection confidence (0.0 to 1.0)."""


# =============================================================================
# FINAL ACTION SELECTION DISPOSITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class FinalActionSelectionDisposition:
    """
    The final-selection disposition for one frontier candidate.
    
    Every frontier candidate must receive a disposition - none may disappear silently!
    
    DISPOSITIONS:
        • SELECTED: This candidate was selected as SelectedAction
        • NOT_SELECTED: Candidate considered but not selected
        • NOT_SELECTED_DOMINATED: Not selected due to dominance by other candidates
        • NOT_SELECTED_POLICY: Policy prohibited this candidate
        • NOT_SELECTED_SECURITY: Security prohibited this candidate
        • NOT_SELECTED_AUTHORITY: Authority requirements not met
        • NOT_SELECTED_CONSTRAINT: Hard constraint violation
        • NOT_SELECTED_TIE: Candidate lost in unresolved tie
        • NOT_SELECTED_USER_CHOICE: User choice selected another
        • NOT_SELECTED_EXECUTIVE_CHOICE: Executive choice selected another
        • RETAINED_AS_FALLBACK: Retained as fallback option
        • RETAINED_AS_CONDITIONAL: Retained as conditional alternative
        • MANDATORY_BUT_NOT_SELECTED: Mandatory but not selected (per semantics)
        • STALE: Candidate is stale
        • EXPIRED: Candidate has expired
        • INVALIDATED: Candidate has been invalidated
        • DEFERRED: Selection deferred for this candidate
    
    IMPORTANT:
        • Disposition is per-candidate, not just for the winner
        • Every frontier candidate must have a disposition
        • Dispositions enable auditability and replay
    """
    
    candidate_id: str = ""
    """The candidate this disposition applies to."""
    
    disposition: str = "NOT_SELECTED"
    """Final selection disposition for this candidate."""
    
    reason: str = ""
    """Why this candidate received this disposition."""


# =============================================================================
# ACTION SELECTION OUTCOME
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionOutcome:
    """
    The complete semantic result of final action selection.
    
    PROPERTIES:
        • identity: Unique identifier for this outcome instance
        • revision: Monotonically increasing revision number
        • kind: What type of outcome this is
        • status: Overall status of the outcome
    
    REFERENCE CONTEXT:
        • request_reference: Which selection request produced this outcome
        • frontier_reference: Which frontier was consumed
        • arbitration_result_reference: Source of frontier
    
    SELECTION RESULT:
        • selected_action_reference: SelectedAction if one was created (else None)
        • no_selection: NoSelection if no selection made (else None)
    
    CANDIDATE ASSESSMENT:
        • candidate_dispositions: Disposition for every frontier candidate
    
    JUSTIFICATION AND ASSESSMENT:
        • justification: Why this outcome was produced
        • confidence: How confident we are in the outcome
        • uncertainty: Sources of uncertainty in the outcome
        • completeness: How complete the assessment was
    
    CONTINUATION:
        • continuation: What should happen next (advisory)
    
    IMPORTANT LAWS:
        • ACTION-SEL-LAW-019: Equivalent semantic inputs produce equivalent selection artifacts.
        • ACTION-SEL-LAW-020: Package import performs no selection work.
    """
    
    identity: ActionSelectionOutcomeIdentity = ""
    """Unique identifier for this outcome."""
    
    revision: int = 1
    """Monotonically increasing revision number."""
    
    # Kind and status
    kind: str = "ACTION_SELECTED"
    """What type of outcome this is."""
    
    status: str = "COMPLETE"
    """Overall status of the outcome."""
    
    # References
    request_reference: str = ""
    """Which selection request produced this outcome."""
    
    frontier_reference: str = ""
    """Which frontier was consumed."""
    
    arbitration_result_reference: str = ""
    """Source of frontier (arbitration result)."""
    
    # Selection result
    selected_action_reference: str | None = None
    """SelectedAction reference if one was created."""
    
    no_selection: ActionNoSelection | None = None
    """NoSelection if no selection made."""
    
    # Candidate assessment
    candidate_dispositions: Tuple[FinalActionSelectionDisposition, ...] = field(
        default_factory=tuple
    )
    """Disposition for every frontier candidate."""
    
    # Justification and assessment
    justification: str = ""
    """Why this outcome was produced."""
    
    confidence: ActionSelectionConfidence | None = None
    """How confident we are in the outcome."""
    
    uncertainty: Tuple[ActionSelectionUncertaintySource, ...] = field(
        default_factory=tuple
    )
    """Sources of uncertainty in the outcome."""
    
    completeness: ActionSelectionCompleteness | None = None
    """How complete the assessment was."""
    
    # Continuation
    continuation: str = "PROCEED_TO_EXECUTION_REVIEW"
    """What should happen next (advisory)."""