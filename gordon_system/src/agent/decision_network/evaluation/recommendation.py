# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Recommendations
# ================================

"""
Recommendation types for Action Evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


# =============================================================================
# RECOMMENDATION KIND ENUMERATION
# =============================================================================

class RecommendationKind(Enum):
    """
    Kinds of recommendations that can be made about Action Candidates.
    
    PROPERTIES:
        • STRONGLY_RECOMMEND: Action should be strongly considered for selection
        • RECOMMEND: Action is acceptable and recommended
        • ACCEPTABLE: Action is acceptable but not optimal
        • MARGINAL: Action has significant concerns
        • DISCOURAGE: Action should generally be avoided
        • REJECT: Action should be rejected
        • UNKNOWN: Insufficient information to recommend
    """
    
    STRONGLY_RECOMMEND = "strongly_recommend"
    """Action should be strongly considered for selection."""
    
    RECOMMEND = "recommend"
    """Action is acceptable and recommended."""
    
    ACCEPTABLE = "acceptable"
    """Action is acceptable but not optimal."""
    
    MARGINAL = "marginal"
    """Action has significant concerns."""
    
    DISCOURAGE = "discourage"
    """Action should generally be avoided."""
    
    REJECT = "reject"
    """Action should be rejected."""
    
    UNKNOWN = "unknown"
    """Insufficient information to recommend."""


# =============================================================================
# ACTION RECOMMENDATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionRecommendation:
    """
    Recommendation about an Action Candidate.
    
    Recommendations are advisory. They do not determine whether an action will
    be selected - only whether it is worth considering.
    
    PROPERTIES:
        • recommendation_kind: Kind of recommendation
        • confidence: Confidence in the recommendation (0.0 to 1.0)
        • uncertainty: Uncertainty about the recommendation (0.0 to 1.0)
        • summary: Human-readable summary of reasoning
        • concerns: List of specific concerns (if any)
    """
    
    recommendation_kind: RecommendationKind = RecommendationKind.UNKNOWN
    """Kind of recommendation."""
    
    confidence: float = 0.5
    """Confidence in the recommendation (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about the recommendation (0.0 to 1.0)."""
    
    summary: str = ""
    """Human-readable summary of reasoning."""
    
    concerns: Tuple[str, ...] = field(default_factory=tuple)
    """List of specific concerns (if any)."""
    
    @classmethod
    def strongly_recommended(cls) -> ActionRecommendation:
        """Create a strongly recommended recommendation."""
        return cls(
            recommendation_kind=RecommendationKind.STRONGLY_RECOMMEND,
            confidence=0.85,
            uncertainty=0.15,
            summary="This action is highly recommended based on evaluation.",
            concerns=(),
        )
    
    @classmethod
    def recommended(cls) -> ActionRecommendation:
        """Create a recommended recommendation."""
        return cls(
            recommendation_kind=RecommendationKind.RECOMMEND,
            confidence=0.75,
            uncertainty=0.25,
            summary="This action is acceptable and recommended.",
            concerns=(),
        )
    
    @classmethod
    def acceptable(cls) -> ActionRecommendation:
        """Create an acceptable recommendation."""
        return cls(
            recommendation_kind=RecommendationKind.ACCEPTABLE,
            confidence=0.6,
            uncertainty=0.35,
            summary="This action is acceptable but has some concerns.",
            concerns=(),
        )
    
    @classmethod
    def marginal(cls, concerns: Tuple[str, ...]) -> ActionRecommendation:
        """Create a marginal recommendation."""
        return cls(
            recommendation_kind=RecommendationKind.MARGINAL,
            confidence=0.35,
            uncertainty=0.45,
            summary="This action has significant concerns.",
            concerns=concerns,
        )
    
    @classmethod
    def discouraged(cls, concerns: Tuple[str, ...]) -> ActionRecommendation:
        """Create a discourage recommendation."""
        return cls(
            recommendation_kind=RecommendationKind.DISCOURAGE,
            confidence=0.5,
            uncertainty=0.3,
            summary="This action should generally be avoided.",
            concerns=concerns,
        )
    
    @classmethod
    def rejected(cls, reasons: Tuple[str, ...]) -> ActionRecommendation:
        """Create a reject recommendation."""
        return cls(
            recommendation_kind=RecommendationKind.REJECT,
            confidence=0.8,
            uncertainty=0.2,
            summary="This action should be rejected.",
            concerns=reasons,
        )
    
    @classmethod
    def unknown(cls) -> ActionRecommendation:
        """Create an unknown recommendation."""
        return cls(
            recommendation_kind=RecommendationKind.UNKNOWN,
            confidence=0.1,
            uncertainty=0.8,
            summary="Insufficient information to make a recommendation.",
            concerns=(),
        )


# =============================================================================
# EVALUATION SUMMARY
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    """
    Summary of evaluation for an Action Candidate.
    
    PROPERTIES:
        • candidate_id: Identifier of the evaluated candidate
        • overall_assessment: Overall assessment score (0.0 to 1.0)
        • recommendation: Recommendation about the candidate
        • confidence: Overall confidence in assessment
        • uncertainty: Overall uncertainty about assessment
        • evaluation_dimensions: Results for each dimension
    """
    
    candidate_id: str
    """Identifier of the evaluated candidate."""
    
    overall_assessment: float = 0.5
    """Overall assessment score (0.0 to 1.0)."""
    
    recommendation: ActionRecommendation = field(default_factory=ActionRecommendation)
    """Recommendation about the candidate."""
    
    confidence: float = 0.5
    """Overall confidence in assessment (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Overall uncertainty about assessment (0.0 to 1.0)."""
    
    evaluation_dimensions: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    """Results for each dimension as (dimension_name, score) tuples."""

    @classmethod
    def from_candidate(
        cls,
        candidate_id: str,
        overall_assessment: float = 0.5,
    ) -> EvaluationSummary:
        """Create an evaluation summary for a candidate."""
        return cls(
            candidate_id=candidate_id,
            overall_assessment=overall_assessment,
        )