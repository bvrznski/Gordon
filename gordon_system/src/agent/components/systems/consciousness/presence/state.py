# Gordon Phase 5.7.5-I: Presence Engine - State Model
# ===============================================================================
"""
Canonical presence state model and lifecycle transitions.

This module defines:
    - PresenceItem: A single item in presence (with its lifecycle state)
    - PresenceState: Immutable state snapshot of all presence items
    - Lifecycle transitions between states
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


# =============================================================================
# PRESENCE ITEM LIFECYCLE STATE
# =============================================================================

@dataclass(frozen=True)
class PresenceItem:
    """
    A single item in the presence system with its lifecycle state.
    
    Each presence item represents content that is either consciously accessible
    or in the process of becoming/ceasing to be conscious.
    
    Properties:
        - Immutable: Once created, never modified
        - Versioned: Has generation tracking for replayability
        - Provenance-preserving: Links to source contribution
    """
    
    # Identity (required fields first)
    item_id: str
    """Unique identifier for this presence item."""
    
    state: str
    """Current lifecycle state (from PRESENCE_STATE_* constants)."""
    
    # Content reference (bounded - not full content embedded)
    content_reference: Optional[str] = None
    """Reference to actual content (not embedded)."""
    
    source_id: str = ""
    """Source that contributed this item."""
    
    contribution_id: Optional[str] = None
    """Contribution envelope ID (for provenance)."""
    
    # Classification
    privacy_classification: str = "internal"
    """Privacy level of this item."""
    
    trust_classification: str = "untrusted"
    """Trust level of this item (preserved, not granted by admission)."""
    
    source_generation: int = 0
    """Source generation at time of contribution."""
    
    # Timing and freshness
    created_at_utc: float = field(default_factory=time.time)
    """When this presence item was first created."""
    
    admitted_at_utc: Optional[float] = None
    """When this item became admitted (if applicable)."""
    
    active_from_utc: Optional[float] = None
    """When this item became actively conscious (if applicable)."""
    
    fading_started_utc: Optional[float] = None
    """When fading began (if applicable)."""
    
    withdrawn_at_utc: Optional[float] = None
    """When this item was withdrawn (if applicable)."""
    
    # Fading metadata
    weakening_duration_seconds: float = 60.0
    """Duration expected in weakening state."""
    
    fade_duration_seconds: float = 30.0
    """Duration expected in fading state before withdrawal."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance chain for this item."""
    
    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if self.state not in (
            "candidate", "admitted", "active", "weakening",
            "fading", "suspended", "withdrawn"
        ):
            raise ValueError(f"Invalid state: {self.state}")
    
    def is_active(self) -> bool:
        """Check if this item is consciously accessible."""
        return self.state == "active"
    
    def is_withdrawn(self) -> bool:
        """Check if this item has been removed from presence."""
        return self.state == "withdrawn"
    
    def get_age_seconds(self, now_utc: Optional[float] = None) -> float:
        """
        Get the age of this presence item in seconds.
        
        Args:
            now_utc: Current time (uses current time if not provided)
            
        Returns:
            Age in seconds
        """
        if now_utc is None:
            now_utc = time.time()
        return max(0.0, now_utc - self.created_at_utc)
    
    def get_time_in_state_seconds(self, now_utc: Optional[float] = None) -> float:
        """
        Get time spent in current state.
        
        This calculates based on when the item entered its current state,
        which is tracked implicitly through state transition timestamps.
        
        Args:
            now_utc: Current time (uses current time if not provided)
            
        Returns:
            Seconds spent in current state
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Determine when current state began based on state type
        state_start = self.created_at_utc
        if self.state == "admitted" and self.admitted_at_utc:
            state_start = self.admitted_at_utc
        elif self.state == "active" and self.active_from_utc:
            state_start = self.active_from_utc
        elif self.state in ("weakening", "fading") and self.fading_started_utc:
            state_start = self.fading_started_utc
        
        return max(0.0, now_utc - state_start)
    
    @classmethod
    def create_candidate(
        cls,
        item_id: str,
        source_id: str,
        contribution_id: Optional[str] = None,
        content_reference: Optional[str] = None,
        privacy_classification: str = "internal",
        trust_classification: str = "untrusted",
        source_generation: int = 0,
    ) -> "PresenceItem":
        """
        Create a new candidate presence item.
        
        Args:
            item_id: Unique ID for this item
            source_id: Source contributing the item
            contribution_id: ID of contribution (for provenance)
            content_reference: Reference to full content (optional)
            privacy_classification: Privacy level
            trust_classification: Trust level (preserved, not granted)
            source_generation: Source's generation at time of contribution
            
        Returns:
            New PresenceItem in "candidate" state
        """
        return cls(
            item_id=item_id,
            state="candidate",
            content_reference=content_reference,
            source_id=source_id,
            contribution_id=contribution_id,
            privacy_classification=privacy_classification,
            trust_classification=trust_classification,
            source_generation=source_generation,
        )
    
    def to_admitted(self, now_utc: Optional[float] = None) -> "PresenceItem":
        """Transition from candidate to admitted state."""
        if self.state != "candidate":
            raise ValueError(f"Cannot transition {self.state} → admitted")
        
        if now_utc is None:
            now_utc = time.time()
        
        return dataclass_replace(self, 
            state="admitted",
            admitted_at_utc=now_utc,
        )
    
    def to_active(self, now_utc: Optional[float] = None) -> "PresenceItem":
        """Transition from admitted to active state."""
        if self.state not in ("admitted", "suspended"):
            raise ValueError(f"Cannot transition {self.state} → active")
        
        if now_utc is None:
            now_utc = time.time()
        
        return dataclass_replace(self,
            state="active",
            active_from_utc=now_utc,
        )
    
    def to_weakening(self, now_utc: Optional[float] = None) -> "PresenceItem":
        """Start fading transition by entering weakening state."""
        if self.state != "active":
            raise ValueError(f"Cannot transition {self.state} → weakening")
        
        if now_utc is None:
            now_utc = time.time()
        
        return dataclass_replace(self,
            state="weakening",
            fading_started_utc=now_utc,
        )
    
    def to_fading(self, now_utc: Optional[float] = None) -> "PresenceItem":
        """Transition from weakening to fading state."""
        if self.state != "weakening":
            raise ValueError(f"Cannot transition {self.state} → fading")
        
        if now_utc is None:
            now_utc = time.time()
        
        return dataclass_replace(self,
            state="fading",
            fading_started_utc=now_utc,  # Keep original start time
        )
    
    def to_withdrawn(self, now_utc: Optional[float] = None) -> "PresenceItem":
        """Transition from fading to withdrawn state."""
        if self.state not in ("fading", "active"):
            raise ValueError(f"Cannot transition {self.state} → withdrawn")
        
        if now_utc is None:
            now_utc = time.time()
        
        return dataclass_replace(self,
            state="withdrawn",
            withdrawn_at_utc=now_utc,
        )
    
    def to_suspended(self, now_utc: Optional[float] = None) -> "PresenceItem":
        """Suspend active content (can resume later)."""
        if self.state != "active":
            raise ValueError(f"Cannot transition {self.state} → suspended")
        
        if now_utc is None:
            now_utc = time.time()
        
        return dataclass_replace(self,
            state="suspended",
        )
    
    def to_resumed(self, now_utc: Optional[float] = None) -> "PresenceItem":
        """Resume suspended content to active state."""
        if self.state != "suspended":
            raise ValueError(f"Cannot transition {self.state} → resumed")
        
        if now_utc is None:
            now_utc = time.time()
        
        return dataclass_replace(self,
            state="active",
            active_from_utc=now_utc,
        )


# Import dataclass_replace after class definition
from dataclasses import replace as dataclass_replace


# =============================================================================
# PRESENCE STATE SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class PresenceStateSnapshot:
    """
    Immutable snapshot of the complete presence state at a point in time.
    
    A snapshot captures all items currently in presence, their states,
    and relevant metadata for diagnostics and replay.
    
    Properties:
        - Immutable: Once published, never modified
        - Versioned: Has generation number for ordering
        - Provenance-preserving: Links to transition that produced it
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
    
    # Presence items by state
    candidate_items: Tuple[PresenceItem, ...] = field(default_factory=tuple)
    """Items in candidate state (proposed but not admitted)."""
    
    admitted_items: Tuple[PresenceItem, ...] = field(default_factory=tuple)
    """Items that are admitted but not yet active."""
    
    active_items: Tuple[PresenceItem, ...] = field(default_factory=tuple)
    """Items currently consciously accessible."""
    
    weakening_items: Tuple[PresenceItem, ...] = field(default_factory=tuple)
    """Items in weakening state (fade transition started)."""
    
    fading_items: Tuple[PresenceItem, ...] = field(default_factory=tuple)
    """Items in fading state (withdrawing from presence)."""
    
    suspended_items: Tuple[PresenceItem, ...] = field(default_factory=tuple)
    """Items temporarily suspended."""
    
    withdrawn_items: Tuple[PresenceItem, ...] = field(default_factory=tuple)
    """Items no longer consciously accessible."""
    
    # Summary counts
    candidate_count: int = 0
    admitted_count: int = 0
    active_count: int = 0
    weakening_count: int = 0
    fading_count: int = 0
    suspended_count: int = 0
    withdrawn_count: int = 0
    
    # Classification summaries (bounded)
    privacy_summary: str = "internal"
    """Overall privacy classification of present items."""
    
    trust_summary: str = "medium"
    """Overall trust classification of present items."""
    
    # Source summary
    source_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Set of unique source IDs in this snapshot."""
    
    provenance: Optional[str] = None
    """Provenance information for this snapshot."""
    
    def __post_init__(self) -> None:
        """Post-initialization validation and computed fields."""
        # Update counts from tuples
        object.__setattr__(self, "candidate_count", len(self.candidate_items))
        object.__setattr__(self, "admitted_count", len(self.admitted_items))
        object.__setattr__(self, "active_count", len(self.active_items))
        object.__setattr__(self, "weakening_count", len(self.weakening_items))
        object.__setattr__(self, "fading_count", len(self.fading_items))
        object.__setattr__(self, "suspended_count", len(self.suspended_items))
        object.__setattr__(self, "withdrawn_count", len(self.withdrawn_items))
        
        # Extract unique source IDs
        source_ids_set: set = set()
        for items in (self.candidate_items, self.admitted_items, self.active_items,
                      self.weakening_items, self.fading_items, self.suspended_items):
            for item in items:
                if item.source_id:
                    source_ids_set.add(item.source_id)
        
        object.__setattr__(self, "source_ids", tuple(sorted(source_ids_set)))
    
    @property
    def total_active(self) -> int:
        """Total number of actively conscious items."""
        return self.active_count + self.weakening_count
    
    @property
    def total_present(self) -> int:
        """Total number of items in presence (not withdrawn)."""
        return (self.candidate_count + self.admitted_count + self.active_count +
                self.weakening_count + self.fading_count + self.suspended_count)
    
    @classmethod
    def initial(cls, snapshot_id: Optional[str] = None) -> "PresenceStateSnapshot":
        """
        Create an initial empty presence state.
        
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
    
    def next_generation(self, transition_id: str) -> "PresenceStateSnapshot":
        """
        Create the next generation snapshot from this one.
        
        Args:
            transition_id: ID of the transition producing this generation
            
        Returns:
            New PresenceStateSnapshot with generation + 1
        """
        return PresenceStateSnapshot(
            snapshot_id=self.snapshot_id,  # Same ID for replayability
            generation=self.generation + 1,
            previous_generation=self.generation,
            transition_id=transition_id,
            created_at_utc=time.time(),
            valid_from_utc=0.0,  # Will be set by caller for replayability
            candidate_items=self.candidate_items,
            admitted_items=self.admitted_items,
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
    
    def with_active_items(self, *items: PresenceItem) -> "PresenceStateSnapshot":
        """Return a copy with updated active items."""
        return dataclass_replace(self, active_items=tuple(items))
    
    def with_withdrawn_items(self, *items: PresenceItem) -> "PresenceStateSnapshot":
        """Return a copy with updated withdrawn items."""
        return dataclass_replace(self, withdrawn_items=tuple(items))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "PresenceItem",
    "PresenceStateSnapshot",
)
