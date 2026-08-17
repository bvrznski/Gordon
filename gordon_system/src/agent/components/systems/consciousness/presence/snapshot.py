# Gordon Phase 5.7.5-I: Presence Engine - Snapshot Model
# ===============================================================================
"""
Immutable snapshot model for presence state publications.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class PresenceSnapshot:
    """
    Immutable publication of the complete presence state at a point in time.
    
    A snapshot captures all items currently in presence (active, fading, etc.),
    their states, and relevant metadata for diagnostics and replay.
    
    Properties:
        - Immutable: Once published, never modified
        - Versioned: Has generation number for ordering
        - Provenance-preserving: Links to transition that produced it
        - Replayable: Can reconstruct from history
    """
    
    # Identity and versioning (required fields first)
    snapshot_id: str = field(default_factory=lambda: f"ps-{_generate_uuid()}")
    """Unique identifier for this snapshot."""
    
    generation: int = 0
    """Snapshot generation number."""
    
    previous_generation: Optional[int] = None
    """Previous generation for lineage tracking."""
    
    transition_id: Optional[str] = None
    """Transition that produced this snapshot (if any)."""
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    """When this snapshot was published."""
    
    valid_from_utc: float = 0.0
    """Timestamp when this snapshot became valid (for replay)."""
    
    # Presence items by state (bounded)
    active_items: Tuple[str, ...] = field(default_factory=tuple)
    """Active items (currently conscious)."""
    
    weakening_items: Tuple[str, ...] = field(default_factory=tuple)
    """Weakening items (fade in progress)."""
    
    fading_items: Tuple[str, ...] = field(default_factory=tuple)
    """Fading items (withdrawal in progress)."""
    
    suspended_items: Tuple[str, ...] = field(default_factory=tuple)
    """Suspended items (temporarily inactive)."""
    
    withdrawn_items: Tuple[str, ...] = field(default_factory=tuple)
    """Withdrawn items (no longer conscious)."""
    
    # Summary counts
    active_count: int = 0
    weakening_count: int = 0
    fading_count: int = 0
    suspended_count: int = 0
    withdrawn_count: int = 0
    
    # Classification summaries (bounded)
    privacy_summary: str = "internal"
    """Overall privacy classification."""
    
    trust_summary: str = "medium"
    """Overall trust classification."""
    
    # Source summary
    source_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Set of unique source IDs in this snapshot."""
    
    provenance: Optional[str] = None
    """Provenance information for this snapshot."""
    
    def __post_init__(self) -> None:
        """Post-initialization validation and computed fields."""
        object.__setattr__(self, "active_count", len(self.active_items))
        object.__setattr__(self, "weakening_count", len(self.weakening_items))
        object.__setattr__(self, "fading_count", len(self.fading_items))
        object.__setattr__(self, "suspended_count", len(self.suspended_items))
        object.__setattr__(self, "withdrawn_count", len(self.withdrawn_items))
        
        # Extract unique source IDs
        object.__setattr__(self, "source_ids", tuple(sorted(set(
            self._extract_source_ids()
        ))))
    
    def _extract_source_ids(self) -> Tuple[str, ...]:
        """Extract unique source IDs from items."""
        return tuple()
    
    @property
    def total_active(self) -> int:
        """Total actively conscious items (active + weakening)."""
        return self.active_count + self.weakening_count
    
    @property
    def total_present(self) -> int:
        """Total items in presence (not withdrawn)."""
        return (self.active_count + self.weakening_count + self.fading_count +
                self.suspended_count)
    
    @classmethod
    def initial(cls, snapshot_id: Optional[str] = None) -> "PresenceSnapshot":
        """
        Create an initial empty presence snapshot.
        
        Args:
            snapshot_id: Optional ID (generated if not provided)
            
        Returns:
            Initial snapshot at generation 0
        """
        return cls(
            snapshot_id=snapshot_id or f"ps-{_generate_uuid()}",
            generation=0,
            created_at_utc=time.time(),
            valid_from_utc=0.0,
        )
    
    def next_generation(self, transition_id: str) -> "PresenceSnapshot":
        """
        Create the next generation snapshot from this one.
        
        Args:
            transition_id: ID of the transition producing this generation
            
        Returns:
            New PresenceSnapshot with generation + 1
        """
        return PresenceSnapshot(
            snapshot_id=self.snapshot_id,  # Same ID for replayability
            generation=self.generation + 1,
            previous_generation=self.generation,
            transition_id=transition_id,
            created_at_utc=time.time(),
            valid_from_utc=0.0,  # Will be set by caller
            active_items=self.active_items,
            weakening_items=self.weakening_items,
            fading_items=self.fading_items,
            suspended_items=self.suspended_items,
            withdrawn_items=self.withdrawn_items,
            privacy_summary=self.privacy_summary,
            trust_summary=self.trust_summary,
            source_ids=self.source_ids,
            provenance=self.provenance,
        )
    
    def with_active(self, *items: str) -> "PresenceSnapshot":
        """Return a copy with updated active items."""
        return dataclass_replace(self, active_items=tuple(items))
    
    def with_withdrawn(self, *items: str) -> "PresenceSnapshot":
        """Return a copy with updated withdrawn items."""
        return dataclass_replace(self, withdrawn_items=tuple(items))


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# Import dataclass_replace after class definition
from dataclasses import replace as dataclass_replace


__all__: Tuple[str, ...] = (
    "PresenceSnapshot",
)