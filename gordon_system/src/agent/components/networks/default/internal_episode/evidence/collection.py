# Internal Episode Evidence Collection
# ====================================

"""
Evidence collection model for episode coordination.

A bounded, immutable collection of evidence items with duplicate detection
and conflict preservation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class InternalEpisodeEvidenceCollection:
    """
    Immutable bounded collection of evidence items for an episode.
    
    The collection enforces bounds to prevent unbounded growth while preserving
    all relevant information including conflicts.
    
    PROPERTIES:
        • evidence_items: Bounded tuple of evidence items (oldest first)
        • evidence_ids: Set-like view of evidence IDs for lookup
        
    REQUIREMENTS:
        • bounded: Maximum size enforced
        • deterministic ordering: Stable ordering where applicable
        • duplicate detection: Same ID = same item
        • conflict preservation: Conflicts never silently discarded
        • source grouping: Items grouped by source for debugging
        
    NOT RESPONSIBLE FOR:
        • Evaluating evidence truth or validity
        • Resolving conflicts (that's done separately)
        • Mutating the collection after publication
    
    CAPACITY MANAGEMENT:
        When capacity is exceeded, overflow behavior is explicit:
            - TRUNCATED: Oldest items removed with records
            - PARTIAL: Collection marked as partial
            - REJECTED: Entire collection rejected
            - DEGRADED: Proceeds with degraded quality
    """
    
    # Identity
    collection_id: str = "default"
    """Unique identifier for this collection."""
    
    # Capacity constraints
    maximum_items: int = 500
    """Maximum number of evidence items allowed."""
    
    overflow_behavior: str = "truncated"  # OverflowBehavior.*
    """What happens when capacity is exceeded."""
    
    # Evidence storage (bounded)
    evidence_items: Tuple[InternalEpisodeEvidence, ...] = field(default_factory=tuple)
    """Tuple of evidence items (oldest first)."""
    
    @classmethod
    def create(cls, maximum_items: int = 500) -> InternalEpisodeEvidenceCollection:
        """Create a new empty evidence collection."""
        return cls(maximum_items=maximum_items)
    
    def add_evidence(
        self,
        item: InternalEpisodeEvidence,
    ) -> InternalEpisodeEvidenceCollection:
        """
        Add an evidence item to the collection.
        
        Returns a new collection instance with the item added. If capacity
        is exceeded, behavior follows overflow_behavior setting.
        
        Duplicate detection: Same evidence_id = same item (no duplicates).
        """
        # Check for duplicates
        for existing in self.evidence_items:
            if existing.evidence_id == item.evidence_id:
                return self  # Already exists
        
        new_items = self.evidence_items + (item,)
        
        # Enforce capacity limit based on overflow behavior
        if len(new_items) > self.maximum_items:
            if self.overflow_behavior in {"rejected", "truncated"}:
                new_items = new_items[-self.maximum_items:]
        
        return InternalEpisodeEvidenceCollection(
            collection_id=self.collection_id,
            maximum_items=self.maximum_items,
            overflow_behavior=self.overflow_behavior,
            evidence_items=new_items,
        )
    
    def get_item_by_id(self, evidence_id: str) -> Optional[InternalEpisodeEvidence]:
        """Get an evidence item by its ID."""
        for item in self.evidence_items:
            if item.evidence_id == evidence_id:
                return item
        return None
    
    def get_conflicting_ids(self) -> Tuple[str, ...]:
        """Get IDs of items that have conflicts recorded."""
        result = []
        for item in self.evidence_items:
            if item.contradicts_ids:
                result.append(item.evidence_id)
        return tuple(result)
    
    def get_by_source(self, source: str) -> Tuple[InternalEpisodeEvidence, ...]:
        """Get all evidence items from a specific source."""
        return tuple(item for item in self.evidence_items if item.source == source)
    
    def get_summary(self) -> dict[str, any]:
        """
        Get a summary of the collection without exposing full payloads.
        
        Returns:
            Summary dict with counts and categories
        """
        total = len(self.evidence_items)
        category_counts = {}
        source_counts = {}
        conflict_count = 0
        
        for item in self.evidence_items:
            # Count by category
            cat = item.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Count by source
            src = item.source
            source_counts[src] = source_counts.get(src, 0) + 1
            
            # Track conflicts
            if item.contradicts_ids:
                conflict_count += 1
        
        return {
            "total_items": total,
            "maximum_items": self.maximum_items,
            "category_counts": category_counts,
            "source_counts": source_counts,
            "conflict_count": conflict_count,
            "overflow_behavior": self.overflow_behavior,
        }


@dataclass(frozen=True, slots=True)
class InternalEpisodeEvidenceConflict:
    """
    Record of a detected conflict between evidence items.
    
    Conflicts are NEVER silently resolved. They are recorded and may influence
    confidence or completeness assessment.
    """
    
    # Identity
    conflict_id: str
    """Unique identifier for this conflict."""
    
    category: str  # ContextConflictCategory.*
    """Type of conflict detected."""
    
    description: str
    """Human-readable description of the conflict."""
    
    severity: str = "non-blocking"  # "blocking" or "non-blocking"
    """How critical this conflict is."""
    
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of evidence items involved in this conflict."""
    
    resolution_status: str = "unresolved"  # "unresolved", "acknowledged", "deferred"
    """Current state of conflict resolution."""