# Competition Module - Focusing Network
# ======================================

"""
Competition analysis for focus candidates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass(frozen=True)
class CompetitionAssessment:
    """Competition assessment for a candidate."""
    
    candidate_id: str
    competition_count: int
    max_competition_intensity: float
    dominant_candidate: bool
    
    @classmethod
    def create_empty(cls, candidate_id: str) -> "CompetitionAssessment":
        """Create an empty assessment."""
        return cls(
            candidate_id=candidate_id,
            competition_count=0,
            max_competition_intensity=0.0,
            dominant_candidate=False,
        )


@dataclass(frozen=True)
class SuppressionAssessment:
    """Suppression recommendation for a candidate."""
    
    candidate_id: str
    should_suppress: bool
    suppression_confidence: float
    suppression_reasons: Tuple[str, ...]
    
    @classmethod
    def create_no_suppression(cls, candidate_id: str) -> "SuppressionAssessment":
        """Create an assessment with no suppression."""
        return cls(
            candidate_id=candidate_id,
            should_suppress=False,
            suppression_confidence=0.0,
            suppression_reasons=tuple(),
        )