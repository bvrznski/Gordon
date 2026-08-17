# Induction Hypothesis Cluster - Phase 7.2
# =========================================

"""
Canonical Hypothesis Cluster Contract.

Hypothesis Clusters preserve alternative explanations with their support.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class InductiveHypothesis:
    """
    An inductive hypothesis - a candidate explanation for observations.
    
    Hypotheses remain candidates until validated.
    
    A hypothesis records:
        - The pattern(s) it explains
        - Its confidence level
        - Its uncertainty
        - Provenance tracking
    """
    
    # Identity
    hypothesis_identity: str              # Unique identifier for this hypothesis
    
    # Supporting patterns (references to PatternCandidates)
    supporting_patterns: Tuple[str, ...]  # Pattern IDs that support this hypothesis
    
    # Hypothesis content
    explanation_text: str                 # Human-readable explanation
    prediction_capabilities: Tuple[str, ...] = ()  # What can it predict?
    
    # Confidence metrics
    confidence: float = 0.5               # Confidence in this specific hypothesis (0-1)
    uncertainty: float = 0.5              # Uncertainty about the hypothesis
    
    # Evidence strength
    support_count: int = 0                # Number of observations explained
    explanatory_power: float = 0.5        # How well does it explain?
    
    # Competing hypotheses awareness
    alternatives_considered: Tuple[str, ...] = ()  # IDs of competing hypotheses
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    hypothesis_kind: str = "candidate"    # candidate, refined, rejected
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def effective_confidence(self) -> float:
        """
        Calculate effective confidence considering uncertainty and alternatives.
        
        This adjusts raw confidence based on:
            - Uncertainty (higher uncertainty = lower effective confidence)
            - Strength of alternative explanations
        """
        base = self.confidence
        
        # Reduce for high uncertainty
        uncertainty_penalty = min(0.3, self.uncertainty * 0.3)
        
        return max(0.0, min(1.0, base - uncertainty_penalty))
    
    def explains_pattern(self, pattern_id: str) -> bool:
        """Check if this hypothesis explains a specific pattern."""
        return pattern_id in self.supporting_patterns


@dataclass(frozen=True)
class HypothesisCluster:
    """
    Cluster of competing hypotheses for the same observations.
    
    A cluster preserves:
        - All alternative explanations
        - Support and confidence for each
        - Ranking by quality
        - Preferred candidate
    
    Competing hypotheses remain explicitly represented and comparable.
    """
    
    # Identity
    cluster_identity: str                 # Unique identifier for this cluster
    
    # Participating hypotheses (references)
    participating_hypotheses: Tuple[str, ...]
    
    # Ranking (hypothesis_id -> rank)
    ranking: Dict[str, int] = field(default_factory=dict)  # hypothesis_id -> rank (1=best)
    
    # Preferred candidate
    preferred_candidate: Optional[str] = None             # Best ranked hypothesis
    
    # Cluster-level metrics
    total_alternatives: int = 0           # Number of hypotheses in cluster
    consensus_confidence: float = 0.0     # Average confidence across cluster
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    clustering_method: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def ranking_size(self) -> int:
        """Number of hypotheses with assigned ranks."""
        return len(self.ranking)
    
    def get_hypothesis_rank(self, hypothesis_id: str) -> Optional[int]:
        """Get the rank of a specific hypothesis (lower is better)."""
        return self.ranking.get(hypothesis_id)
    
    def get_preferred_hypothesis(self) -> Optional[str]:
        """Get the ID of the highest-ranked hypothesis."""
        if not self.ranking:
            return None
        return min(self.ranking.keys(), key=lambda k: self.ranking[k])
    
    def has_consensus(self, threshold: float = 0.8) -> bool:
        """Check if cluster has high-confidence consensus."""
        # Consensus requires at least one hypothesis with high confidence
        # and low uncertainty across alternatives
        return self.consensus_confidence >= threshold


@dataclass(frozen=True)
class HypothesisEvaluation:
    """
    Evaluation of a hypothesis against observations.
    
    Records how well each hypothesis explains the available evidence.
    """
    
    evaluation_id: str
    
    # Evaluated hypothesis
    hypothesis_id: str
    hypothesis_text: str
    
    # Fit measures
    explanatory_fit: float = 0.0          # How well does it fit?
    predictive_accuracy: float = 0.0      # How accurate are its predictions?
    simplicity_score: float = 1.0         # Occam's razor (simpler is better)
    
    # Composite scores
    overall_score: float = 0.5            # Combined evaluation score
    
    # Evidence support
    observations_explained: Tuple[str, ...] = ()
    observations_predicted: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    evaluation_method: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class HypothesisRefinement:
    """
    Refinement of an inductive hypothesis.
    
    Hypotheses may be refined when new evidence is discovered.
    """
    
    refinement_identity: str
    base_hypothesis_id: str               # ID of original hypothesis
    
    # Changes made
    previous_explanation: str
    refined_explanation: str
    
    # Support changes
    new_supporting_patterns: Tuple[str, ...] = ()
    removed_patterns: Tuple[str, ...] = ()
    
    # Confidence updates
    previous_confidence: float = 0.5
    refined_confidence: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    reason_for_refinement: str = "new_evidence"
    provenance: Dict[str, str] = field(default_factory=dict)


__all__ = [
    "InductiveHypothesis",
    "HypothesisCluster",
    "HypothesisEvaluation",
    "HypothesisRefinement",
]