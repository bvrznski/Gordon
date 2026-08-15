# Default Network Policy
# =====================

"""
Semantic policy decisions for the DefaultNetwork.

Policy determines semantic choices such as which internally generated candidates
are worth proposing, how competing internal candidates are ranked, and when to
emit proposals. Policy does NOT decide runtime scheduling or execution.

PHASE 4.3.1: Semantic Policy Only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# POLICY DECISIONS (semantic choices)
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultPolicy:
    """
    Policy decisions for the DefaultNetwork.
    
    These are semantic policy choices - they do NOT command runtime behavior.
    
    Policy may determine:
        - Whether internally generated candidates are worth proposing
        - Which categories of internally oriented processing are applicable
        - How many candidates may be emitted
        - How competing internal candidates are ranked
        - When an internally oriented proposal is too weak to emit
        - When uncertainty requires additional capability invocation
    """
    
    # Proposal emission threshold (minimum confidence)
    minimum_confidence_threshold: float = 0.5
    
    # Maximum candidates to emit per assessment
    max_candidates_per_assessment: int = 10
    
    # Priority ranking mode
    priority_ranking_mode: str = "descending"  # "ascending", "descending"
    
    # Categories to activate (if empty, all are eligible)
    active_categories: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """
    A single policy decision made during assessment.
    
    Records which candidates passed policy checks and why.
    """
    
    # Decision identity
    decision_id: str
    
    # Candidate that was evaluated
    candidate_ref: str
    
    # Whether it passed the policy check
    passed: bool
    
    # Reason for the decision
    reason: str
    
    # Timestamp of decision (not processed)
    timestamp_utc: str


# =============================================================================
# POLICY RULES (semantic constraints)
# =============================================================================

class PolicyRule:
    """
    Semantic policy rules that govern proposal generation.
    
    These are constraint definitions, NOT runtime enforcement mechanisms.
    """
    
    # Confidence must meet minimum threshold
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    
    # Proposals must have valid category
    VALID_CATEGORY = "valid_category"
    
    # Maximum count per assessment
    MAX_COUNT_PER_ASSESSMENT = "max_count_per_assessment"
    
    # Priority ranking must be consistent
    CONSISTENT_RANKING = "consistent_ranking"


# =============================================================================
# POLICY STATES (for bounded tracking)
# =============================================================================

class PolicyState:
    """
    Bounded policy state for tracking.
    
    Used for explainability, not runtime state mutation.
    """
    
    # Candidate evaluation state
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED_CONFIDENCE = "rejected_confidence"
    REJECTED_CATEGORY = "rejected_category"
    REJECTED_COUNT = "rejected_count"


# =============================================================================
# POLICY DECISION TYPES
# =============================================================================

class PolicyDecisionType:
    """
    Bounded policy decision type classifications.
    
    Describes what kind of policy check was performed.
    """
    
    CONFIDENCE_CHECK = "confidence_check"
    CATEGORY_CHECK = "category_check"
    COUNT_CHECK = "count_check"
    RANKING_CHECK = "ranking_check"


# =============================================================================
# POLICY CONFIGURATION
# =============================================================================

class PolicyConfiguration:
    """
    Semantic policy configuration parameters.
    
    These are configuration values, NOT runtime resource assignments.
    """
    
    # Minimum confidence for proposal emission (0.0 to 1.0)
    MIN_CONFIDENCE_THRESHOLD: float = 0.3
    
    # Maximum proposals per assessment (bounded)
    MAX_PROPOSALS_PER_ASSESSMENT: int = 20
    
    # Priority adjustment bounds
    MIN_PRIORITY_ADJUSTMENT: float = -1.0
    MAX_PRIORITY_ADJUSTMENT: float = 1.0


# =============================================================================
# POLICY VALIDATION HELPERS
# =============================================================================

def validate_confidence_threshold(threshold: float) -> bool:
    """
    Validate that a confidence threshold is in valid range.
    
    Args:
        threshold: The threshold to validate (should be 0.0 to 1.0)
        
    Returns:
        True if valid, False otherwise
    """
    return 0.0 <= threshold <= 1.0


def validate_candidate_count(count: int) -> bool:
    """
    Validate that candidate count is within policy bounds.
    
    Args:
        count: Number of candidates
        
    Returns:
        True if within bounds, False otherwise
    """
    return 0 <= count <= PolicyConfiguration.MAX_PROPOSALS_PER_ASSESSMENT


def validate_priority_adjustment(adjustment: float) -> bool:
    """
    Validate that a priority adjustment is in valid range.
    
    Args:
        adjustment: The adjustment value
        
    Returns:
        True if within bounds, False otherwise
    """
    return (PolicyConfiguration.MIN_PRIORITY_ADJUSTMENT <= 
            adjustment <= 
            PolicyConfiguration.MAX_PRIORITY_ADJUSTMENT)