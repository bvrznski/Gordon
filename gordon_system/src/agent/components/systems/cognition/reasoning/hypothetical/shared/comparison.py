# Hypothesis Comparison - Phase 7.15 Part 2
# ===========================================

"""
Canonical Hypothesis Comparison Contract.

Comparison evaluates coverage, consistency, plausibility, novelty,
simplicity, and expected explanatory power.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ComparisonMetric(Enum):
    """Metrics for comparing hypotheses."""
    
    COVERAGE = "coverage"                     # How much does it explain?
    CONSISTENCY = "consistency"               # Internal and external consistency
    PLAUSIBILITY = "plausibility"             # How plausible is it?
    NOVELTY = "novelty"                       # How novel or innovative?
    SIMPLICITY = "simplicity"                 # Occam's razor - simplicity
    EXPLANATORY_POWER = "explanatory_power"   # Explanatory strength


@dataclass(frozen=True)
class HypothesisComparisonIdentity:
    """
    Immutable identity for a comparison.
    
    Allows tracking comparisons across sessions.
    """
    
    semantic_identity: str                    # Stable identity across runs
    
    @classmethod
    def create(cls, semantic_identity: str) -> HypothesisComparisonIdentity:
        """Create a new comparison identity."""
        return cls(semantic_identity=semantic_identity)


@dataclass(frozen=True)
class ComparisonResult:
    """
    Result of comparing hypotheses.
    
    Contains detailed assessment for each hypothesis across multiple metrics.
    """
    
    # Identity
    result_id: str                            # Unique identifier
    
    # Target
    compared_hypothesis_ids: Tuple[str, ...]  # Which hypotheses were compared?
    
    # Metrics scores (0.0 to 1.0)
    coverage_score: float = 0.5               # Coverage metric score
    consistency_score: float = 0.5            # Consistency metric score
    plausibility_score: float = 0.5           # Plausibility metric score
    novelty_score: float = 0.5                # Novelty metric score
    simplicity_score: float = 0.5             # Simplicity metric score
    explanatory_power_score: float = 0.5      # Explanatory power metric score
    
    # Overall assessment
    overall_score: float = 0.5                # Weighted综合 score
    ranking: int = 1                          # Rank among compared hypotheses
    
    # Metadata
    compared_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_top_ranked(self) -> bool:
        """Check if this hypothesis has the highest ranking."""
        return self.ranking == 1
    
    @classmethod
    def create(
        cls,
        compared_hypothesis_ids: List[str],
        coverage_score: float = 0.5,
        consistency_score: float = 0.5,
        plausibility_score: float = 0.5,
        novelty_score: float = 0.5,
        simplicity_score: float = 0.5,
        explanatory_power_score: float = 0.5,
        overall_score: Optional[float] = None,
        ranking: int = 1,
    ) -> ComparisonResult:
        """Create a new comparison result."""
        return cls(
            result_id=f"comparison_result:{uuid.uuid4().hex[:16]}",
            compared_hypothesis_ids=tuple(compared_hypothesis_ids),
            coverage_score=coverage_score,
            consistency_score=consistency_score,
            plausibility_score=plausibility_score,
            novelty_score=novelty_score,
            simplicity_score=simplicity_score,
            explanatory_power_score=explanatory_power_score,
            overall_score=overall_score or (coverage_score + plausibility_score) / 2,
            ranking=ranking,
        )


@dataclass(frozen=True)
class HypothesisComparison:
    """
    Record of comparing multiple hypotheses.
    
    Tracks which hypotheses were compared, their rankings, and the
    comparison rationale.
    """
    
    # Identity
    comparison_id: str                        # Unique identifier
    
    # Compared hypotheses
    compared_hypotheses: Tuple[HypothesisComparisonIdentity, ...]  # All compared
    
    # Comparison metrics
    comparison_metrics: Tuple[ComparisonMetric, ...] = (
        ComparisonMetric.COVERAGE,
        ComparisonMetric.PLACEHOLDER,
        ComparisonMetric.PLAUSIBILITY,
        ComparisonMetric.NOVELTY,
        ComparisonMetric.SIMPLICITY,
    )
    
    # Results
    results: Dict[str, ComparisonResult] = field(default_factory=dict)  # hypothesis_id -> result
    
    # Ranking (ordered list)
    ranking: Tuple[str, ...] = ()             # Ordered by score
    
    # Metadata
    compared_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_compared(self) -> int:
        """Return number of hypotheses compared."""
        return len(self.compared_hypotheses)
    
    @classmethod
    def create(
        cls,
        comparing_hypotheses: List[HypothesisComparisonIdentity],
        results: Optional[Dict[str, ComparisonResult]] = None,
        ranking: Optional[List[str]] = None,
    ) -> HypothesisComparison:
        """Create a new comparison record."""
        return cls(
            comparison_id=f"comparison:{uuid.uuid4().hex[:16]}",
            compared_hypotheses=tuple(comparing_hypotheses),
            results=results or {},
            ranking=tuple(ranking or []),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ComparisonMetric",
    "HypothesisComparisonIdentity",
    "ComparisonResult",
    "HypothesisComparison",
]