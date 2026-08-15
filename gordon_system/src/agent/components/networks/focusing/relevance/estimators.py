# Relevance Estimators - Focusing Network
# ========================================

"""
Estimators for goal-directed relevance and priority aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass(frozen=True)
class GoalRelevanceAssessment:
    """Goal-directed relevance assessment for a candidate."""
    
    candidate_id: str
    goal_relevance_score: float
    context_relevance_score: float
    combined_relevance: float
    
    @classmethod
    def create_empty(cls, candidate_id: str) -> "GoalRelevanceAssessment":
        """Create an empty assessment."""
        return cls(
            candidate_id=candidate_id,
            goal_relevance_score=0.0,
            context_relevance_score=0.0,
            combined_relevance=0.0,
        )


@dataclass(frozen=True)
class RelevanceAssessment:
    """Complete relevance assessment for a set of candidates."""
    
    assessments: Tuple[GoalRelevanceAssessment, ...]
    average_relevance: float
    max_relevance: float
    
    @classmethod
    def create_empty(cls) -> "RelevanceAssessment":
        """Create an empty assessment."""
        return cls(
            assessments=tuple(),
            average_relevance=0.0,
            max_relevance=0.0,
        )