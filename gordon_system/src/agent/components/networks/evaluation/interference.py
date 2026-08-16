# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Interference
# ==============================

"""
Action Interference Analysis type definitions.

This module defines the types used to assess whether one Action Candidate
degrades another during evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


# =============================================================================
# INTERFERENCE KIND ENUMERATION
# =============================================================================

class InterferenceKind(Enum):
    """
    Kinds of interference between Action Candidates.
    
    PROPERTIES:
        • MUTUAL_EXCLUSION: Candidates cannot both be selected
        • REDUNDANCY: One candidate makes another unnecessary
        • OBSTRUCTION: One candidate blocks the other's success
        • INHIBITION: One candidate reduces the effectiveness of another
        • DEPENDENCY: One candidate requires the other first
        • SYNERGY: Candidates work better together than separately
    """
    
    MUTUAL_EXCLUSION = "mutual_exclusion"
    """Candidates cannot both be selected."""
    
    REDUNDANCY = "redundancy"
    """One candidate makes another unnecessary."""
    
    OBSTRUCTION = "obstruction"
    """One candidate blocks the other's success."""
    
    INHIBITION = "inhibition"
    """One candidate reduces the effectiveness of another."""
    
    DEPENDENCY = "dependency"
    """One candidate requires the other first."""
    
    SYNERGY = "synergy"
    """Candidates work better together than separately."""


# =============================================================================
# INTERFERENCE RECORD
# =============================================================================

@dataclass(frozen=True, slots=True)
class InterferenceRecord:
    """
    Record of interference between two Action Candidates.
    
    An interference record documents how one candidate affects another. This is
    distinct from conflict analysis - interference can be positive or negative.
    
    PROPERTIES:
        • interference_id: Unique identifier for this record
        • kind: Kind of interference
        • source_candidate_id: ID of the interfering candidate
        • affected_candidate_id: ID of the affected candidate
        • strength: How strong the interference is (0.0 to 1.0)
        • direction: Direction of the interference
    
    NOT RESPONSIBLE FOR:
        - Resolving interference
        - Selecting candidates based on interference
    """
    
    interference_id: str
    """Unique identifier for this interference record."""
    
    kind: InterferenceKind
    """Kind of interference (InterferenceKind.*)."""
    
    source_candidate_id: str
    """ID of the interfering candidate."""
    
    affected_candidate_id: str
    """ID of the affected candidate."""
    
    strength: float = 0.5
    """How strong the interference is (0.0 to 1.0)."""
    
    direction: str = "forward"
    """Direction of the interference ('forward' or 'backward')."""
    
    @classmethod
    def mutual_exclusion(
        cls,
        candidate_a_id: str,
        candidate_b_id: str,
    ) -> InterferenceRecord:
        """Create a mutual exclusion record."""
        return cls(
            interference_id=f"interfere_{candidate_a_id}_{candidate_b_id}_mutual",
            kind=InterferenceKind.MUTUAL_EXCLUSION,
            source_candidate_id=candidate_a_id,
            affected_candidate_id=candidate_b_id,
            strength=1.0,
            direction="both",
        )
    
    @classmethod
    def redundancy(
        cls,
        redundant_candidate_id: str,
        essential_candidate_id: str,
    ) -> InterferenceRecord:
        """Create a redundancy record."""
        return cls(
            interference_id=f"interfere_{redundant_candidate_id}_{essential_candidate_id}_red",
            kind=InterferenceKind.REDUNDANCY,
            source_candidate_id=redundant_candidate_id,
            affected_candidate_id=essential_candidate_id,
            strength=0.8,
            direction="forward",
        )
    
    @classmethod
    def synergy(
        cls,
        candidate_a_id: str,
        candidate_b_id: str,
    ) -> InterferenceRecord:
        """Create a synergy record."""
        return cls(
            interference_id=f"interfere_{candidate_a_id}_{candidate_b_id}_syn",
            kind=InterferenceKind.SYNERGY,
            source_candidate_id=candidate_a_id,
            affected_candidate_id=candidate_b_id,
            strength=0.7,
            direction="both",
        )


# =============================================================================
# INTERFERENCE ANALYSIS
# =============================================================================

@dataclass(frozen=True, slots=True)
class InterferenceAnalysis:
    """
    Summary of interference analysis for an evaluation.
    
    PROPERTIES:
        • total_interferences: Number of interferences detected
        • interference_records: Detailed records of each interference
        • negative_interference_score: Score for negative interferences (0.0 to 1.0)
        • positive_interference_score: Score for positive interferences (0.0 to 1.0)
    """
    
    total_interferences: int = 0
    """Number of interferences detected."""
    
    interference_records: Tuple[InterferenceRecord, ...] = field(default_factory=tuple)
    """Detailed records of each interference."""
    
    negative_interference_score: float = 0.0
    """Score for negative interferences (0.0 to 1.0)."""
    
    positive_interference_score: float = 0.0
    """Score for positive interferences (0.0 to 1.0)."""
    
    @classmethod
    def no_interference(cls) -> InterferenceAnalysis:
        """Create an interference analysis with no interferences."""
        return cls(
            total_interferences=0,
            interference_records=(),
            negative_interference_score=0.0,
            positive_interference_score=0.0,
        )
    
    @classmethod
    def from_interferences(
        cls, records: Tuple[InterferenceRecord, ...]
    ) -> InterferenceAnalysis:
        """Create an interference analysis from interference records."""
        if not records:
            return cls.no_interference()
        
        negative = sum(
            (r.strength for r in records if r.kind != InterferenceKind.SYNERGY),
            0.0,
        )
        positive = sum(
            (r.strength for r in records if r.kind == InterferenceKind.SYNERGY),
            0.0,
        )
        
        return cls(
            total_interferences=len(records),
            interference_records=records,
            negative_interference_score=min(negative, 1.0),
            positive_interference_score=min(positive, 1.0),
        )


# =============================================================================
# INTERFERENCE MATRIX
# =============================================================================

@dataclass(frozen=True, slots=True)
class InterferenceMatrix:
    """
    Pairwise interference assessment between candidates.
    
    A matrix representation of interference where each cell represents the
    interference from one candidate to another.
    
    PROPERTIES:
        • candidate_ids: Ordered list of candidate IDs
        • matrix: Dictionary mapping (from_id, to_id) to interference strength
    """
    
    candidate_ids: Tuple[str, ...]
    """Ordered list of candidate IDs."""
    
    matrix: Tuple[Tuple[str, str, float], ...]
    """Dictionary mapping (from_id, to_id) to interference strength."""

    @classmethod
    def empty(cls, candidate_ids: Tuple[str, ...]) -> InterferenceMatrix:
        """Create an empty interference matrix."""
        matrix = tuple(
            (a, b, 0.0) for a in candidate_ids for b in candidate_ids if a != b
        )
        return cls(candidate_ids=candidate_ids, matrix=matrix)
