# Salience Network Competition Result
# ====================================

"""
Canonical competition result model (Phase 4.8.6).

CompetitionResult contains the complete output of the competition layer:
    - Ranked candidates with priority ordering
    - Dominance relationships between candidates
    - Inhibition and facilitation graphs
    - Stability assessment
    - Attention recommendations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class CandidateRanking:
    """
    Immutable candidate ranking result.
    
    Contains ordered candidates with semantic rationale for ordering.
    
    RANKING INVARIANTS:
        COMPETITION-RANKING-INV-001: Rank is advisory only (not execution)
        COMPETITION-RANKING-INV-002: Equivalent candidates remain equivalent
        COMPETITION-RANKING-INV-003: Incomparable candidates are explicitly marked
    """
    
    # Ordered list of candidate identities (highest to lowest priority)
    ordered_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Candidate state identities in ranked order."""
    
    # Explicit rank information per candidate
    candidate_ranks: dict[str, int] = field(default_factory=dict)
    """
    Mapping from candidate identity to numeric rank.
    Lower numbers indicate higher priority.
    """
    
    # Ties (equivalent candidates)
    tied_groups: Tuple[Tuple[str, ...], ...] = field(default_factory=tuple)
    """Groups of equivalent-rank candidates."""
    
    # Incomparables
    incomparable_pairs: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Pairs of incomparable candidates."""
    
    # Rationale for ranking
    ranking_rationale: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for the ranking decision."""
    
    # Confidence and uncertainty
    confidence: float = 0.5
    """Confidence in the ranking (0.0-1.0)."""
    
    uncertainty_basis: str = field(default="")
    """Semantic basis for uncertainty level."""