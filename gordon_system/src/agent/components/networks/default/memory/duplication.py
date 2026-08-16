# Memory Duplicate Models
# =======================

"""
Immutable duplicate-related models for memory records.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY DUPLICATE CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryDuplicateCandidate:
    """
    Immutable candidate record for potential duplicate detection.
    
    A duplicate candidate represents records that may be the same or very similar.
    
    PROPERTIES:
        • candidate_id: Unique identifier for this duplicate pair/group
        • record_refs_a: First set of record references
        • record_refs_b: Second set of record references
        • evidence: Evidence suggesting duplication
        • overlap_score: Similarity score (0.0 to 1.0)
        • is_definitive_duplicate: Is this definitely a duplicate?
        • potential_merge_target: Which record should be kept if merging
        • provenance: Provenance reference
        
    IS NOT:
        - Permission to delete or merge (authority decides)
        - A merged record (just a candidate for merging)
    """
    
    # Identity
    candidate_id: str
    """Unique identifier for this duplicate candidate."""
    
    # Record references
    record_refs_a: Tuple[str, ...] = field(default_factory=tuple)
    """First set of record references."""
    
    record_refs_b: Tuple[str, ...] = field(default_factory=tuple)
    """Second set of record references."""
    
    # Evidence for duplication
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting duplicate classification."""
    
    overlap_score: float = 0.5
    """Similarity score (0.0 to 1.0)."""
    
    # Classification
    is_definitive_duplicate: bool = False
    """Is this definitely a duplicate?"""
    
    potential_merge_target: Optional[str] = None
    """Which record should be kept if merging."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        record_refs_a: Tuple[str, ...],
        record_refs_b: Tuple[str, ...],
        overlap_score: float = 0.5,
    ) -> MemoryDuplicateCandidate:
        """Create a new duplicate candidate."""
        return cls(
            candidate_id=f"dup_{id(cls)}",
            record_refs_a=record_refs_a,
            record_refs_b=record_refs_b,
            overlap_score=overlap_score,
        )
    
    def is_high_confidence_duplicate(self) -> bool:
        """Check if this is a high-confidence duplicate."""
        return self.is_definitive_duplicate or self.overlap_score >= 0.8
    
    def has_strong_evidence(self) -> bool:
        """Check if there's strong evidence for duplication."""
        return len(self.evidence) >= 2 and self.overlap_score >= 0.6