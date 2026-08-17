# Abduction Explanation Candidate - Phase 7.3
# ===========================================

"""
Explanation candidates and generation for abductive reasoning.

Explanations are candidate mechanisms that explain the available evidence.
They remain explicit and comparable during the abductive process.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ExplanationStrategy(Enum):
    """Strategies for explanation generation."""
    
    CAUSAL_REASONING = "causal_reasoning"      # Identify causal mechanisms
    ANALOGICAL = "analogical"                 # Reason by similarity to known cases
    MODEL_COMPARISON = "model_comparison"     # Compare against explanatory models
    HISTORICAL = "historical"                 # Use historical patterns
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"  # Find solutions satisfying constraints


@dataclass(frozen=True)
class ExplanationCandidate:
    """
    A candidate explanation in abductive reasoning.
    
    An explanation contains:
        - Identity and semantic tracking
        - Supported evidence (what it explains)
        - Assumptions made
        - Confidence level
        - Causal structure
    
    Explanations remain candidates until evaluated and ranked.
    """
    
    # Identity
    explanation_id: str                      # Unique identifier
    semantic_identity: str                   # Stable identity for comparison
    
    # Content
    explanation_text: str                    # Human-readable explanation
    explained_evidence: Tuple[str, ...]      # Which evidence items this explains
    
    # Causal structure
    causal_mechanism: Dict[str, Any] = field(default_factory=dict)  # Mechanism description
    assumptions: Tuple[str, ...] = ()        # Underlying assumptions
    boundary_conditions: Tuple[str, ...] = ()  # When does this apply?
    
    # Assessment
    confidence: float = 0.5                  # Confidence in the explanation (0.0-1.0)
    coverage: float = 0.5                    # What fraction of evidence is explained?
    simplicity: float = 0.5                  # Simplicity score (Occam's razor)
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    generation_strategy: ExplanationStrategy = ExplanationStrategy.CAUSAL_REASONING
    
    @property
    def explanatory_strength(self) -> float:
        """Calculate overall explanation strength."""
        return (
            self.confidence * 0.4 +
            self.coverage * 0.3 +
            self.simplicity * 0.2 +
            min(len(self.explained_evidence) / max(1, len(self.assumptions)), 2.0) * 0.1
        )
    
    def explains_evidence(self, evidence_id: str) -> bool:
        """Check if this explanation covers a specific piece of evidence."""
        return evidence_id in self.explained_evidence
    
    @classmethod
    def create(
        cls,
        explanation_text: str,
        explained_evidence_ids: List[str],
        semantic_identity: str,
        confidence: float = 0.5,
        coverage: float = 0.5,
        assumptions: Optional[List[str]] = None,
        strategy: ExplanationStrategy = ExplanationStrategy.CAUSAL_REASONING,
    ) -> ExplanationCandidate:
        """Create a new explanation candidate."""
        return cls(
            explanation_id=f"explanation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            explanation_text=explanation_text,
            explained_evidence=tuple(explained_evidence_ids),
            confidence=confidence,
            coverage=coverage,
            assumptions=tuple(assumptions or []),
            generation_strategy=strategy,
        )
    
    def with_assumptions(self, assumptions: List[str]) -> "ExplanationCandidate":
        """Return a copy with added assumptions."""
        return dataclass_replace(
            self,
            assumptions=tuple(assumptions),
        )
    
    def update_confidence(self, new_confidence: float) -> "ExplanationCandidate":
        """Return a copy with updated confidence."""
        return dataclass_replace(
            self,
            confidence=new_confidence,
        )


@dataclass(frozen=True)
class ExplanationGeneration:
    """
    Record of an explanation generation process.
    
    This tracks how explanations were generated, including:
        - Generation strategy used
        - All candidates produced
        - Supporting evidence for each
        - Timing information
    """
    
    # Identity
    generation_id: str                       # Unique identifier
    
    # Process info
    strategy_used: ExplanationStrategy       # Strategy employed
    reasoning_goal: str                      # What were we trying to explain?
    
    # Results
    generated_candidates: Tuple[ExplanationCandidate, ...]  # All candidates produced
    supporting_evidence_ids: Tuple[str, ...] = ()           # Evidence used in generation
    
    # Process metadata
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def candidate_count(self) -> int:
        """Number of candidates generated."""
        return len(self.generated_candidates)
    
    @property
    def best_candidate(self) -> Optional[ExplanationCandidate]:
        """Get the highest confidence candidate."""
        if not self.generated_candidates:
            return None
        return max(self.generated_candidates, key=lambda c: c.explanatory_strength)
    
    @classmethod
    def create(
        cls,
        strategy_used: ExplanationStrategy,
        reasoning_goal: str,
        candidates: List[ExplanationCandidate],
        supporting_evidence_ids: Optional[List[str]] = None,
    ) -> ExplanationGeneration:
        """Create a new generation record."""
        return cls(
            generation_id=f"generation:{uuid.uuid4().hex[:16]}",
            strategy_used=strategy_used,
            reasoning_goal=reasoning_goal,
            generated_candidates=tuple(candidates),
            supporting_evidence_ids=tuple(supporting_evidence_ids or []),
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class ComparisonMetric:
    """A single metric for comparing explanations."""
    
    metric_id: str                           # Unique identifier
    metric_name: str                         # Human-readable name
    value: float                             # Metric value (0.0-1.0)
    weight: float = 1.0                      # Importance in ranking
    
    @property
    def weighted_value(self) -> float:
        """Calculate weighted contribution to total score."""
        return self.value * self.weight


@dataclass(frozen=True)
class HypothesisComparison:
    """
    Comparison of competing hypothesis explanations.
    
    This record shows:
        - All hypotheses compared
        - Metrics used for comparison
        - Ranking results
        - Preferred explanation
    
    Comparison remains explicit and inspectable.
    """
    
    # Identity
    comparison_id: str                       # Unique identifier
    
    # Process info
    compared_candidates: Tuple[ExplanationCandidate, ...]  # All candidates compared
    metrics_used: Tuple[ComparisonMetric, ...] = ()        # Metrics for each candidate
    
    # Results
    ranking: Dict[str, int] = field(default_factory=dict)  # explanation_id -> rank (lower is better)
    preferred_candidate_id: Optional[str] = None           # Best explanation
    
    # Process metadata
    completed_at_utc: float = field(default_factory=time.time)
    
    @property
    def candidate_count(self) -> int:
        """Number of candidates compared."""
        return len(self.compared_candidates)
    
    @classmethod
    def create(
        cls,
        candidates: List[ExplanationCandidate],
        metrics: Dict[str, List[ComparisonMetric]],
        ranking: Optional[Dict[str, int]] = None,
    ) -> HypothesisComparison:
        """Create a new comparison record."""
        ranking = ranking or {}
        
        # Calculate ranks if not provided
        if not ranking and candidates:
            strengths = {c.explanation_id: c.explanatory_strength for c in candidates}
            sorted_ids = sorted(strengths.keys(), key=lambda x: -strengths[x])
            ranking = {eid: i + 1 for i, eid in enumerate(sorted_ids)}
        
        preferred = None
        if ranking:
            best_rank = min(ranking.values())
            for eid, rank in ranking.items():
                if rank == best_rank:
                    preferred = eid
                    break
        
        # Flatten metrics into tuple
        all_metrics = []
        for cid, mlist in metrics.items():
            all_metrics.extend(mlist)
        
        return cls(
            comparison_id=f"comparison:{uuid.uuid4().hex[:16]}",
            compared_candidates=tuple(candidates),
            metrics_used=tuple(all_metrics),
            ranking=ranking,
            preferred_candidate_id=preferred,
        )


@dataclass(frozen=True)
class ExplanationRanking:
    """
    Final ranking of explanations.
    
    This provides:
        - Ordered list of candidates by quality
        - Score differences for discrimination
        - Confidence in the ranking
    
    Ranking remains revisable as new evidence arrives.
    """
    
    # Identity
    ranking_id: str                          # Unique identifier
    
    # Candidates ranked
    ranked_candidates: Tuple[ExplanationCandidate, ...]  # Ordered list (best first)
    
    # Quality metrics
    score_gap_first_second: float = 0.0      # Score difference between top two
    confidence_in_ranking: float = 1.0       # Confidence in the ranking order
    
    # Context
    ranking_strategy: str = "explanatory_strength"  # Strategy used
    evidence_count: int = 0                  # Evidence considered
    
    @property
    def best_explanation(self) -> Optional[ExplanationCandidate]:
        """Get the top-ranked explanation."""
        if not self.ranked_candidates:
            return None
        return self.ranked_candidates[0]
    
    def has_clear_winner(self, min_gap: float = 0.2) -> bool:
        """Check if there's a clear best explanation."""
        return self.score_gap_first_second >= min_gap
    
    @classmethod
    def create(
        cls,
        candidates: List[ExplanationCandidate],
        evidence_count: int = 1,
        ranking_strategy: str = "explanatory_strength",
    ) -> ExplanationRanking:
        """Create a new ranking."""
        sorted_candidates = sorted(candidates, key=lambda c: -c.explanatory_strength)
        
        score_gap = 0.0
        if len(sorted_candidates) >= 2:
            score_gap = sorted_candidates[0].explanatory_strength - sorted_candidates[1].explanatory_strength
        
        return cls(
            ranking_id=f"ranking:{uuid.uuid4().hex[:16]}",
            ranked_candidates=tuple(sorted_candidates),
            score_gap_first_second=score_gap,
            confidence_in_ranking=min(1.0, 0.5 + len(candidates) * 0.1),
            ranking_strategy=ranking_strategy,
            evidence_count=evidence_count,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExplanationCandidate",
    "ExplanationGeneration",
    "ExplanationStrategy",
    "ComparisonMetric",
    "HypothesisComparison",
    "ExplanationRanking",
]