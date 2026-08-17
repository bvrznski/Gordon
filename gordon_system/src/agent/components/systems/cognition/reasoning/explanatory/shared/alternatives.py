# Alternative Explanation Analysis - Phase 7.14
# ===============================================

"""
Alternative explanation analysis for explanatory reasoning.

Evaluates:
    - Coverage
    - Parsimony
    - Predictive power
    - Consistency
    - Supporting evidence
    - Conflicting evidence
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AlternativeIdentity:
    """
    Immutable identity for an alternative explanation.
    """
    
    semantic_identity: str                    # Stable identity across runs
    alternative_number: int = 1               # For repeated evaluations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, alternative_number: int = 1) -> AlternativeIdentity:
        """Create a new alternative identity."""
        return cls(
            semantic_identity=semantic_identity,
            alternative_number=alternative_number,
        )


@dataclass(frozen=True)
class CandidateExplanation:
    """
    A candidate explanation that competes with others.
    
    Each has:
        - Content (what it explains)
        - Evidence support
        - Parsimony score
        - Coverage metrics
    """
    
    # Identity
    alternative_id: str                       # Unique identifier
    
    # Content
    explanation_content: Dict[str, Any]       # The explanation itself
    
    # Evaluation metrics
    evidence_support_score: float = 0.5       # How well supported?
    parsimony_score: float = 1.0              # Simpler is better (1.0 = simplest)
    coverage_score: float = 0.5               # How much does it explain?
    
    @property
    def overall_score(self) -> float:
        """Calculate overall score."""
        return (
            self.evidence_support_score * 0.4 +
            self.parsimony_score * 0.3 +
            self.coverage_score * 0.3
        )


@dataclass(frozen=True)
class AlternativeExplanationAnalysis:
    """
    Analysis of alternative explanations.
    
    Evaluates competing hypotheses to select the best explanation.
    """
    
    # Identity
    analysis_id: str                          # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Candidate alternatives
    candidate_explanations: Tuple[CandidateExplanation, ...]
    
    # Comparative metrics
    preferred_explanation_id: str             # Which is best?
    comparative_metrics: Dict[str, float]     # Comparison details
    
    # Quality
    discrimination_power: float = 0.5         # How well do alternatives distinguish?
    confidence_in_selection: float = 0.5      # Confidence in the choice
    
    @classmethod
    def create(
        cls,
        candidates: List[CandidateExplanation],
        semantic_identity: str,
        preferred_explanation_id: Optional[str] = None,
    ) -> "AlternativeExplanationAnalysis":
        """Create a new alternative analysis."""
        candidate_tuple = tuple(candidates)
        
        # Find best by overall score
        if not preferred_explanation_id and candidate_tuple:
            best = max(candidate_tuple, key=lambda c: c.overall_score)
            preferred_explanation_id = best.alternative_id
        
        return cls(
            analysis_id=f"alt_analysis:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            candidate_explanations=candidate_tuple,
            preferred_explanation_id=preferred_explanation_id or "",
            comparative_metrics={"best_score": 0.5},
            confidence_in_selection=0.5,
        )
    
    def get_preferred(self) -> Optional[CandidateExplanation]:
        """Get the preferred explanation."""
        for c in self.candidate_explanations:
            if c.alternative_id == self.preferred_explanation_id:
                return c
        if self.candidate_explanations:
            return max(self.candidate_explanations, key=lambda c: c.overall_score)
        return None


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AlternativeIdentity",
    "CandidateExplanation",
    "AlternativeExplanationAnalysis",
]