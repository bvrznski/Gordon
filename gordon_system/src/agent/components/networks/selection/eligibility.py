# Gordon Cognitive Architecture - Phase 4.5.7
# ===========================================
#
"""
Eligibility assessment types for frontier candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# ID TYPES
# =============================================================================

ActionSelectionFrontierEligibilityAssessment = str
"""Status of a frontier's eligibility for selection."""

FinalActionCandidateEligibilityAssessment = str
"""Status of an individual candidate's eligibility for final selection."""


# =============================================================================
# FRONTIER ELIGIBILITY ASSESSMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionFrontierEligibility:
    """
    Assessment of a frontier's eligibility for final selection.
    
    PROPERTIES:
        • status: Frontier eligibility status
        • reasons: List of reasons affecting eligibility
        • expired_candidates: Count of expired candidates in frontier
    
    ELIGIBILITY STATUSES:
        • ELIGIBLE: Frontier is ready for selection
        • ELIGIBLE_WITH_CONDITIONS: Frontier eligible but with conditions
        • PARTIALLY_ELIGIBLE: Some candidates eligible, some not
        • AUTHORITY_REQUIRED: Selection authority needed to proceed
        • POLICY_REVIEW_REQUIRED: Policy review needed before selection
        • SECURITY_REVIEW_REQUIRED: Security review needed before selection
        • TIE_UNRESOLVED: Unresolved ties prevent selection
        • CONFLICT_UNRESOLVED: Conflicts between candidates unresolved
        • STALE: Frontier revision is stale
        • EXPIRED: Frontier has expired
        • NO_SELECTABLE_CANDIDATES: No eligible candidates in frontier
        • INVALID: Frontier structure is invalid
        • UNKNOWN: Eligibility cannot be determined
    """
    
    status: str = "ELIGIBLE"
    """Frontier eligibility status."""
    
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    """List of reasons affecting eligibility."""
    
    expired_candidates: int = 0
    """Count of expired candidates in frontier."""


# =============================================================================
# CANDIDATE FINAL ELIGIBILITY ASSESSMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class FinalActionCandidateEligibility:
    """
    Assessment of whether a candidate may participate in final selection.
    
    PROPERTIES:
        • status: Candidate eligibility status
        • reasons: List of eligibility factors (positive and negative)
        • conditions: Conditions that must hold for selection
    
    ELIGIBILITY STATUSES:
        • ELIGIBLE: Candidate is eligible for final selection
        • ELIGIBLE_WITH_CONDITIONS: Eligible but with external conditions
        • PARTIALLY_ELIGIBLE: Only some aspects are eligible
        • AUTHORITY_REQUIRED: Selection authority needed
        • POLICY_REVIEW_REQUIRED: Policy review pending
        • SECURITY_REVIEW_REQUIRED: Security review pending
        • VETOED: Candidate has active veto
        • INVALIDATED: Candidate has been invalidated
        • EXPIRED: Candidate has expired
        • OUT_OF_SCOPE: Not in permitted selection scope
        • STALE: Candidate revision is stale
        • UNKNOWN: Eligibility cannot be determined
    
    IMPORTANT:
        • This is final boundary validation, not reevaluation
        • Must confirm candidate appears on frontier
        • Must confirm revision is current
        • Must verify no vetoes or invalidations
    """
    
    status: str = "ELIGIBLE"
    """Candidate eligibility status."""
    
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    """List of factors affecting eligibility (positive and negative)."""
    
    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """External conditions that must hold before selection."""