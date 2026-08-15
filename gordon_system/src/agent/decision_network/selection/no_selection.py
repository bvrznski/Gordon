# Gordon Cognitive Architecture - Phase 4.5.7
# ===========================================
#
"""
No-selection and deferral types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# NO-SELECTION REASON
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionNoSelectionReason:
    """
    Reason for producing a no-selection outcome.
    
    IMPORTANT: No-selection is a valid semantic outcome, not an error.
    
    REASONS:
        • NO_ELIGIBLE_CANDIDATES: All candidates filtered out
        • NO_ADMISSIBLE_CANDIDATES: All candidates vetoed or constrained
        • FRONTIER_EMPTY: Frontier contains no candidates
        • FRONTIER_STALE: Frontier revision is stale
        • REQUEST_STALE: Request revision is stale
        • DECISION_INACTIVE: Governing decision is no longer active
        • COMMITMENT_INACTIVE: Governing commitment is no longer active
        • AUTHORITY_REQUIRED: Selection authority needed but not provided
        • POLICY_REVIEW_REQUIRED: Policy review pending before selection
        • SECURITY_REVIEW_REQUIRED: Security review pending before selection
        • UNRESOLVED_TIE: Tied candidates and no tie-breaker policy
        • INCOMPARABLE_CANDIDATES: Candidates incomparable without higher-order policy
        • CONFLICTING_CONSTRAINTS: Hard constraints cannot be satisfied simultaneously
        • MORE_EVIDENCE_REQUIRED: Insufficient evidence to make selection
        • USER_CHOICE_REQUIRED: User choice required but not provided
        • EXECUTIVE_REVIEW_REQUIRED: Executive review needed
        • TARGET_STATE_STALE: Target state no longer matches requirements
        • CAPABILITY_UNAVAILABLE: Required capability no longer available
        • SELECTION_POLICY_INVALID: Selection policy is invalid or expired
        • SELECTION_DEFERRED: Selection deferred to another mechanism
        • SELECTION_CANCELLED: Selection cancelled by external request
        • UNKNOWN: Reason cannot be determined
    
    IMPORTANT:
        • Each reason must be explicit, not implicit
        • No-selection preserves frontier and candidate references
        • Deferral may specify what input is needed for future selection
    """
    
    kind: str = "NO_ELIGIBLE_CANDIDATES"
    """Canonical no-selection reason."""
    
    description: str = ""
    """Human-readable explanation of the no-selection reason."""
    
    required_future_input: Tuple[str, ...] = field(default_factory=tuple)
    """What additional input would enable future selection."""


# =============================================================================
# ACTION NO-SELECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionNoSelection:
    """
    An explicit no-selection outcome.
    
    A no-selection is a valid semantic result when:
        - No candidates are eligible or admissible
        - All candidates are vetoed or constrained
        - Frontiers cannot be meaningfully selected from
    
    PROPERTIES:
        • reasons: Why selection did not occur
        • deferral: If applicable, what should happen instead
        •候选人_remaining: Number of candidates in frontier (for context)
    
    IMPORTANT:
        • This is NOT None or absence of result
        • This IS an explicit semantic outcome
        • Downstream systems must handle this outcome
        • No-selection may trigger re-arbitration or new candidate generation
    """
    
    reasons: Tuple[ActionNoSelectionReason, ...] = field(default_factory=tuple)
    """Explicit reasons why no selection was made."""
    
    deferral: str | None = None
    """If applicable, reference to deferred selection mechanism."""
    
    candidates_remaining: int = 0
    """Number of candidates remaining in frontier (for context)."""


# =============================================================================
# SELECTION DEFERRAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionDeferral:
    """
    A request to defer selection until later conditions are met.
    
    PROPERTIES:
        • reason: Why deferral is needed
        • required_future_input: What input would enable future selection
        • blockers: Current obstacles preventing selection
        • authority: Authority that can resolve the deferral
        • review_conditions: Conditions that must be satisfied before retry
        • expiration: When deferred selection expires
    
    IMPORTANT:
        • Deferral does NOT schedule re-selection
        • Deferral is advisory, not executable
        • Later execution layer decides when to retry
    """
    
    reason: str = "PENDING_EVIDENCE"
    """Why deferral was necessary."""
    
    required_future_input: Tuple[str, ...] = field(default_factory=tuple)
    """What future input would enable selection."""
    
    blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Current obstacles preventing selection."""
    
    authority: str = ""
    """Authority that can resolve the deferral."""
    
    review_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be satisfied before retry."""
    
    expiration: str = ""
    """When deferred selection expires (ISO format or relative time)."""