# Salience Network Competition Policy
# ====================================

"""
Canonical policy definitions for competition (Phase 4.8.6).

Policies configure:
    - Dominance threshold for determining winner
    - Hysteresis to prevent ranking oscillation
    - Tie handling strategies
    - Ranking algorithms and preferences
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DominanceThresholdPolicy:
    """
    Policy for dominance determination thresholds.
    
    DOMINANCE THRESHOLD INVARIANTS:
        COMPETITION-DOMINANCE-THRESHOLD-INV-001: Threshold must be > 0.5
        COMPETITION-DOMINANCE-THRESHOLD-INV-002: Equal candidates remain equivalent
    """
    
    # Minimum confidence difference for dominance
    minimum_confidence_difference: float = field(default=0.1)
    """Minimum confidence gap to declare dominance."""
    
    # Priority difference threshold (from intensity rank)
    minimum_priority_difference: int = field(default=1)
    """Minimum priority level gap for dominance."""
    
    # Evidence strength ratio required
    minimum_evidence_ratio: float = field(default=1.5)
    """Ratio of evidence supporting dominant over subordinate."""
    
    @property
    def is_strict(self) -> bool:
        """Check if policy uses strict thresholds."""
        return self.minimum_confidence_difference >= 0.2
    
    @property
    def is_relaxed(self) -> bool:
        """Check if policy uses relaxed thresholds."""
        return self.minimum_confidence_difference < 0.1


@dataclass(frozen=True)
class HysteresisPolicy:
    """
    Policy for hysteresis to prevent ranking oscillation.
    
    HYSTERESIS INVARIANTS:
        COMPETITION-HYSTERESIS-INV-001: Thresholds must be >= 0
        COMPETITION-HYSTERESIS-INV-002: Prevents A>B>A>B oscillation
    """
    
    # Minimum rank change required to reorder candidates
    minimum_rank_change: int = field(default=2)
    """Candidates must change by this many positions to trigger reorder."""
    
    # Stability threshold for priority changes
    stability_threshold: float = field(default=0.15)
    """Priority confidence difference must exceed this to reorder."""
    
    # Maximum oscillation cycles before forcing convergence
    max_oscillation_cycles: int = field(default=3)
    """Stop cycling after this many rank exchanges."""
    
    @property
    def is_strict(self) -> bool:
        """Check if hysteresis is strict (high threshold)."""
        return self.stability_threshold >= 0.2
    
    @property
    def is_relaxed(self) -> bool:
        """Check if hysteresis is relaxed (low threshold)."""
        return self.stability_threshold < 0.1


@dataclass(frozen=True)
class RankingPolicy:
    """
    Policy for ranking algorithm configuration.
    
    RANKING POLICY INVARIANTS:
        COMPETITION-RANKING-POLICY-INV-001: Policies are immutable
        COMPETITION-RANKING-POLICY-INV-002: No runtime callbacks in policy
    """
    
    # Dominance preference (higher priority wins)
    prefer_dominant: bool = field(default=True)
    """Whether dominant candidates get higher priority."""
    
    # Inhibition weight (0.0 to 1.0)
    inhibition_weight: float = field(default=0.3)
    """Weight for inhibition relationships in ranking."""
    
    # Facilitation weight (0.0 to 1.0)
    facilitation_weight: float = field(default=0.2)
    """Weight for facilitation relationships in ranking."""
    
    # Stability preference
    prefer_stable_ordering: bool = field(default=True)
    """Whether to prefer maintaining previous rank when uncertain."""
    
    @property
    def total_weight(self) -> float:
        """Sum of all relationship weights."""
        return self.inhibition_weight + self.facilitation_weight


@dataclass(frozen=True)
class TieHandlingPolicy:
    """
    Policy for handling equivalent candidates.
    
    TIE HANDLING INVARIANTS:
        COMPETITION-TIE-HANDLING-INV-001: Ties are preserved, not broken
        COMPETITION-TIE-HANDLING-INV-002: No arbitrary ordering of ties
    """
    
    # How to represent tied candidates in ranking
    tied_representation: str = field(default="shared_rank")
    """Options: shared_rank, parallel_recommendation, deferred_comparison"""
    
    # Maximum number of tied candidates before forcing comparison
    max_tied_candidates: int = field(default=5)
    """Force pairwise comparison if more than this many ties."""
    
    # Strategy for tie-breaking when necessary
    break_tie_strategy: str = field(default="external_arbitration")
    """Options: external_arbitration, defer_comparison, random_shuffle"""
    
    @property
    def is_strict(self) -> bool:
        """Check if policy strictly preserves ties."""
        return self.break_tie_strategy == "external_arbitration"