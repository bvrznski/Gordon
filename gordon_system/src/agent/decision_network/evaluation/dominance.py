# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Dominance Analysis
# ====================================

"""
Dominance Analysis types for comparing Action Candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


# =============================================================================
# DOMINANCE KIND ENUMERATION
# =============================================================================

class DominanceKind(Enum):
    """
    Kinds of dominance relationships between candidates.
    
    PROPERTIES:
        • STRICT: One candidate strictly dominates another (better in all dimensions)
        • WEAK: One candidate weakly dominates (at least as good in all, better in some)
        • INCOMPARABLE: Neither candidate dominates the other
        • EQUIVALENT: Candidates are equivalent across all evaluated dimensions
    """
    
    STRICT = "strict"
    """One candidate strictly dominates another."""
    
    WEAK = "weak"
    """One candidate weakly dominates another."""
    
    INCOMPARABLE = "incomparable"
    """Neither candidate dominates the other."""
    
    EQUIVALENT = "equivalent"
    """Candidates are equivalent across all dimensions."""


# =============================================================================
# PAIRWISE COMPARISON
# =============================================================================

@dataclass(frozen=True, slots=True)
class PairwiseComparison:
    """
    Comparison result between two Action Candidates.
    
    PROPERTIES:
        • candidate_a_id: First candidate's identifier
        • candidate_b_id: Second candidate's identifier
        • dominance_kind: What kind of dominance exists (if any)
        • dimension_results: Per-dimension comparison results
        • evidence: Why this comparison was made
    """
    
    candidate_a_id: str
    """First candidate's identifier."""
    
    candidate_b_id: str
    """Second candidate's identifier."""
    
    dominance_kind: DominanceKind = DominanceKind.INCOMPARABLE
    """What kind of dominance exists (if any)."""
    
    dimension_results: Tuple[Tuple[str, float], ...] = field(default_factory=tuple)
    """Per-dimension comparison results as (dimension_name, a_vs_b_score) tuples."""
    
    evidence: str = ""
    """Why this comparison was made."""

    @classmethod
    def from_dominance(
        cls,
        candidate_a_id: str,
        candidate_b_id: str,
        dominance_kind: DominanceKind,
    ) -> PairwiseComparison:
        """Create a pairwise comparison with explicit dominance kind."""
        return cls(
            candidate_a_id=candidate_a_id,
            candidate_b_id=candidate_b_id,
            dominance_kind=dominance_kind,
        )


# =============================================================================
# DOMINANCE RELATIONSHIP
# =============================================================================

@dataclass(frozen=True, slots=True)
class DominanceRelation:
    """
    Summary of dominance relationships in an evaluation.
    
    PROPERTIES:
        • strict_dominances: List of (winner_id, loser_id) pairs
        • weak_dominances: List of weak dominance pairs
        • incomparable_pairs: Pairs that are incomparable
        • equivalence_classes: Groups of equivalent candidates
    """
    
    strict_dominances: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """List of (winner_id, loser_id) pairs for strict dominance."""
    
    weak_dominances: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """List of (dominator_id, dominated_id) pairs for weak dominance."""
    
    incomparable_pairs: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Pairs that are incomparable."""
    
    equivalence_classes: Tuple[Tuple[str, ...], ...] = field(default_factory=tuple)
    """Groups of equivalent candidates."""

    @classmethod
    def empty(cls) -> DominanceRelation:
        """Create a dominance relation with no comparisons."""
        return cls(
            strict_dominances=(),
            weak_dominances=(),
            incomparable_pairs=(),
            equivalence_classes=(),
        )