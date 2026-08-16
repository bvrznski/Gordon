# Salience Network Competition Layer
# ===================================
#
# Canonical implementation of multi-candidate competition (Phase 4.8.6).
#

"""
Canonical competition layer for the Salience Network.

Competition evaluates relationships between multiple Candidate States to determine:

    * Which candidate is relatively more salient?
    * Which candidates should receive cognitive priority?
    * What semantic relationships exist between candidates?

Competition does NOT:
    
    * Allocate Attention (owned by Attention Network)
    * Select Executives (owned by Executive Network)
    * Schedule Actions (owned by Scheduler)
    * Modify Candidates (preserves immutability)

ARCHITECTURAL INVARIANTS:

    - COMPETITION-INV-001: Competition operates exclusively on validated Candidate States
    - COMPETITION-INV-002: Competition is deterministic and immutable
    - COMPETITION-INV-003: Competition never modifies input Candidates
    - COMPETITION-INV-004: All outputs are deeply frozen dataclasses
    - COMPETITION-INV-005: No runtime dependencies (no threads, no I/O, no scheduling)

ARCHITECTURAL PRINCIPLES:

    1. Pure comparison (stateless evaluators)
    2. Immutable outputs (frozen dataclasses)
    3. External time providers (never datetime.now internally)
    4. External identity providers (no internal UUID generation)
    5. Typed policies (explicit contracts, no callbacks)
    6. Complete traceability (structural rationale only)

PACKAGE CONTENTS:

    request.py      Competition request model
    result.py       Competition result model  
    policy.py       Policy definitions for ranking, hysteresis
    comparator.py   Pairwise comparison engine
    dominance.py    Dominance relationship evaluation
    inhibition.py   Inhibition relationship evaluation
    facilitation.py Facilitation relationship evaluation
    graph.py        Competition graph construction and validation
    ranking.py      Ranking algorithm implementation
    stability.py    Stability estimation
    hysteresis.py   Hysteresis policy enforcement
    recommendation.py  Attention recommendation generation
    trace.py        Structural trace generation
    validation.py   Request and graph validation

TESTING REQUIREMENTS:

    - Unit tests for each module
    - Property-based tests for determinism
    - Metamorphic tests for ranking consistency
    - Negative tests for invalid input handling
"""

from __future__ import annotations

# =============================================================================
# CANONICAL METADATA (Phase 4.8.6)
# =============================================================================

from . import _meta as __meta__

__version__ = __meta__.__version__
PACKAGE_NAME = __meta__.PACKAGE_NAME
DISPLAY_NAME = __meta__.DISPLAY_NAME
ARCHITECTURAL_LAYER = __meta__.ARCHITECTURAL_LAYER
PACKAGE_STATUS = __meta__.PACKAGE_STATUS
IMPLEMENTATION_PHASE = __meta__.IMPLEMENTATION_PHASE
CANONICAL = __meta__.CANONICAL

# =============================================================================
# PHASE 4.8.6: Core Models
# =============================================================================

from ._enums import (
    DominanceRelation,
    InhibitionStrength,
    FacilitationStrength,
    StabilityKind,
    PersistenceKind,
    RecommendationLevel,
)

from ._request import CompetitionRequest
from ._result import CompetitionResult, CandidateRanking, AttentionRecommendation

# =============================================================================
# PHASE 4.8.6: Policy Models
# =============================================================================

from ._policy import (
    DominanceThresholdPolicy,
    HysteresisPolicy,
    RankingPolicy,
    TieHandlingPolicy,
)

# =============================================================================
# PHASE 4.8.6: Evaluator Interfaces (Protocols)
# =============================================================================

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ._enums import SalienceLevel
    from ._request import CompetitionRequest
    from ._result import CandidateRanking


class CompetitionComparator(Protocol):
    """Canonical interface for pairwise candidate comparison."""

    def compare(self, candidate_a: dict, candidate_b: dict) -> "ComparisonResult":
        """Compare two candidates and return relationship."""
        ...


class DominanceEvaluator(Protocol):
    """Interface for dominance evaluation."""

    def evaluate_dominance(
        self, 
        dominant_candidate: dict,
        subordinate_candidate: dict,
        policy: "DominanceThresholdPolicy"
    ) -> bool:
        """Determine if dominant_candidate dominates subordinate_candidate."""
        ...


class InhibitionEvaluator(Protocol):
    """Interface for inhibition relationship evaluation."""

    def evaluate_inhibition(
        self, 
        inhibitor: dict,
        target: dict
    ) -> tuple[InhibitionStrength, tuple[str, ...]]:
        """
        Evaluate if inhibitor inhibits target.
        
        Returns:
            Tuple of (strength, semantic_basis)
        """
        ...


class FacilitationEvaluator(Protocol):
    """Interface for facilitation relationship evaluation."""

    def evaluate_facilitation(
        self,
        facilitator_a: dict,
        facilitator_b: dict
    ) -> tuple[FacilitationStrength, tuple[str, ...]]:
        """
        Evaluate if two candidates facilitate each other.
        
        Returns:
            Tuple of (strength, semantic_basis)
        """
        ...


class StabilityEvaluator(Protocol):
    """Interface for stability estimation."""

    def evaluate_stability(
        self,
        current_ranking: "CandidateRanking",
        previous_ranking: "CandidateRanking" | None,
        policy: "HysteresisPolicy"
    ) -> tuple[StabilityKind, tuple[str, ...]]:
        """
        Estimate stability of ranking across evaluation cycles.
        
        Returns:
            Tuple of (stability_kind, findings)
        """
        ...


class RankingEngine(Protocol):
    """Interface for ranking candidates."""

    def generate_ranking(
        self,
        candidates: tuple[dict, ...],
        dominance_matrix: dict,
        inhibition_graph: dict,
        facilitation_graph: dict,
        policy: "RankingPolicy"
    ) -> "CandidateRanking":
        """
        Generate ranked ordering of candidates.
        
        Returns:
            CandidateRanking with ordered candidates and rationale
        """
        ...

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Metadata
    "__version__",
    "PACKAGE_NAME",
    "DISPLAY_NAME",
    "ARCHITECTURAL_LAYER",
    "PACKAGE_STATUS",
    "IMPLEMENTATION_PHASE",
    "CANONICAL",
    
    # Enums
    "DominanceRelation",
    "InhibitionStrength",
    "FacilitationStrength",
    "StabilityKind",
    "PersistenceKind",
    "RecommendationLevel",
    
    # Core Models
    "CompetitionRequest",
    "CompetitionResult",
    "CandidateRanking",
    "AttentionRecommendation",
    
    # Policy Models
    "DominanceThresholdPolicy",
    "HysteresisPolicy",
    "RankingPolicy",
    "TieHandlingPolicy",
    
    # Protocol Interfaces (for type hints)
    "CompetitionComparator",
    "DominanceEvaluator",
    "InhibitionEvaluator",
    "FacilitationEvaluator",
    "StabilityEvaluator",
    "RankingEngine",
]