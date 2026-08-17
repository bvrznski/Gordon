# Gordon Phase 5.7.6-I: Perspective Engine - Snapshots
# ===============================================================================
"""
Canonical perspective snapshot system for the Perspective Engine.

Snapshots provide immutable publications of perspective state at specific points
in time, enabling replay, debugging, and historical analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Optional


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# =============================================================================
# PERSPECTIVE SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class PerspectiveSnapshot:
    """
    Immutable snapshot of perspective state at a point in time.
    
    Each snapshot captures the complete observer-relative organization
    of conscious content from a specific reference frame. Snapshots are
    immutable and can be safely shared across systems.
    
    Snapshot properties:
        - Immutable: Once published, never modified
        - Deterministic: Same inputs produce identical snapshots
        - Complete: All relevant perspective information included
        - Bounded: Size-limited for practical use
    
    NOT included (owned by external systems):
        - Full conscious content payloads
        - Runtime thread state
        - Internal processing queues
        - External system references
    """
    
    # Identity and revisioning
    snapshot_id: str = field(default_factory=lambda: f"perspective-{_generate_uuid()}")
    """Unique identifier for this snapshot."""
    
    generation: int = 0
    """Context generation when this snapshot was created."""
    
    previous_generation: Optional[int] = None
    """Previous generation (for lineage tracking)."""
    
    schema_version: str = "5.7.6"
    """Schema version for compatibility tracking."""
    
    # Timestamps
    created_at_utc: float = field(default_factory=lambda: 0.0)
    """When this snapshot was created."""
    
    valid_from_utc: float = 0.0
    """Time from which this snapshot becomes valid."""
    
    valid_until_utc: Optional[float] = None
    """Optional expiration time for this snapshot."""
    
    # Perspective state
    reference_frame_ref: str = "frame-unknown"
    """Reference to current reference frame."""
    
    observer_id: str = "observer-001"
    """Current observer instance ID."""
    
    self_reference_ref: Optional[str] = None
    """Reference to self-reference state (if tracked)."""
    
    perspective_type: str = "self"
    """Active perspective type."""
    
    # State metadata
    provenance: Optional[str] = None
    """Source that produced this snapshot."""
    
    trust_level: str = "medium"
    """Trust level for this snapshot's accuracy."""
    
    privacy_level: str = "internal"
    """Privacy classification of this snapshot."""
    
    # Summary information (bounded)
    active_items_count: int = 0
    """Number of actively conscious items."""
    
    fading_items_count: int = 0
    """Number of fading items."""
    
    source_summary: Tuple[str, ...] = field(default_factory=tuple)
    """Summary of contributing sources."""
    
    @classmethod
    def initial(cls) -> "PerspectiveSnapshot":
        """
        Create an initial perspective snapshot.
        
        This creates a clean starting point for the first context generation.
        """
        import time
        return cls(
            snapshot_id="perspective-initial-001",
            generation=0,
            created_at_utc=time.time(),
            valid_from_utc=0.0,
            reference_frame_ref="frame-initial-001",
            observer_id="observer-001",
            perspective_type="self",
            provenance="system_initialization",
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if this snapshot has minimal content."""
        return self.active_items_count == 0 and len(self.source_summary) <= 1
    
    def with_generation(self, new_generation: int) -> "PerspectiveSnapshot":
        """Return a copy with updated generation."""
        return dataclass_replace(
            self,
            previous_generation=self.generation,
            generation=new_generation,
        )
    
    def with_reference_frame(self, frame_ref: str) -> "PerspectiveSnapshot":
        """Return a copy with updated reference frame reference."""
        return dataclass_replace(
            self,
            reference_frame_ref=frame_ref,
        )
    
    def with_perspective_type(self, new_type: str) -> "PerspectiveSnapshot":
        """Return a copy with updated perspective type."""
        return dataclass_replace(
            self,
            perspective_type=new_type,
        )


# =============================================================================
# SNAPSHOT BATCH
# =============================================================================

@dataclass
class SnapshotBatch:
    """
    Batch of perspective snapshots across generations.
    
    Allows atomic publication of multiple related snapshots and maintains
    generation lineage for replay purposes.
    """
    
    batch_id: str = field(default_factory=lambda: f"snapshot-batch-{_generate_uuid()}")
    """Unique identifier for this batch."""
    
    snapshots: list[PerspectiveSnapshot] = field(default_factory=list)
    """Snapshots in this batch (ordered by generation)."""
    
    # State tracking
    _committed_count: int = 0
    
    def __post_init__(self) -> None:
        """Initialize internal state after construction."""
        self._committed_count = 0
    
    @property
    def size(self) -> int:
        """Get number of snapshots in batch."""
        return len(self.snapshots)
    
    @property
    def is_empty(self) -> bool:
        """Check if batch has no snapshots."""
        return len(self.snapshots) == 0
    
    @property
    def current_generation(self) -> int:
        """Get highest generation in batch."""
        if not self.snapshots:
            return 0
        return max(s.generation for s in self.snapshots)
    
    def add_snapshot(self, snapshot: PerspectiveSnapshot) -> None:
        """
        Add a snapshot to the batch.
        
        Args:
            snapshot: Snapshot to add (will be added to end of list)
        """
        self.snapshots.append(snapshot)
    
    def commit_one(self) -> None:
        """Mark one snapshot as committed."""
        if self._committed_count < len(self.snapshots):
            self._committed_count += 1
    
    @property
    def is_complete(self) -> bool:
        """Check if all snapshots have been committed."""
        return self._committed_count == len(self.snapshots)
    
    def get_by_generation(self, generation: int) -> Optional[PerspectiveSnapshot]:
        """
        Get snapshot for a specific generation.
        
        Args:
            generation: Generation number to find
            
        Returns:
            Snapshot or None if not found
        """
        for s in self.snapshots:
            if s.generation == generation:
                return s
        return None
    
    def clear(self) -> None:
        """Clear the batch and reset state."""
        self.snapshots.clear()
        self._committed_count = 0


# =============================================================================
# SNAPSHOT VALIDATOR
# =============================================================================

@dataclass
class SnapshotValidator:
    """
    Validator for perspective snapshots.
    
    Ensures snapshots are well-formed, valid, and consistent before
    publication to external systems.
    """
    
    require_complete_frame_ref: bool = True
    """Whether to require complete frame reference."""
    
    max_snapshot_size_bytes: int = 65536
    """Maximum size for snapshot serialization."""
    
    def validate(
        self,
        snapshot: PerspectiveSnapshot,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a perspective snapshot.
        
        Args:
            snapshot: Snapshot to validate
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        from .constants import VALID_PERSPECTIVE_TYPES
        
        # Check generation is valid
        if snapshot.generation < 0:
            return False, "Generation cannot be negative"
        
        # Check perspective type is valid
        if snapshot.perspective_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid perspective type: {snapshot.perspective_type}"
        
        # Check frame reference required (if configured)
        if self.require_complete_frame_ref and not snapshot.reference_frame_ref:
            return False, "Reference frame reference is required"
        
        # Validate timestamp ordering
        if snapshot.created_at_utc < 0:
            return False, "Created at timestamp cannot be negative"
        if (
            snapshot.valid_from_utc > 0 and
            snapshot.valid_from_utc > snapshot.created_at_utc + 86400
        ):
            return False, "Valid from time is too far in future"
        
        # All checks passed
        return True, None
    
    def estimate_size(self, snapshot: PerspectiveSnapshot) -> int:
        """
        Estimate serialized size of a snapshot.
        
        Args:
            snapshot: Snapshot to measure
            
        Returns:
            Estimated size in bytes
        """
        # Simple estimation (in practice would use actual serialization)
        base_size = 256  # Header overhead
        frame_ref_size = len(snapshot.reference_frame_ref or "") * 2
        observer_id_size = len(snapshot.observer_id) * 2
        source_summary_size = sum(len(s) for s in snapshot.source_summary) * 2
        
        return base_size + frame_ref_size + observer_id_size + source_summary_size
    
    @classmethod
    def default(cls) -> "SnapshotValidator":
        """Return a validator with default settings."""
        return cls()
    
    @classmethod
    def strict(cls) -> "SnapshotValidator":
        """Return a strict validator for production use."""
        return cls(
            require_complete_frame_ref=True,
            max_snapshot_size_bytes=32768,  # Half the size
        )


# =============================================================================
# SNAPSHOT REPLAY ENGINE
# =============================================================================

@dataclass
class SnapshotReplayEngine:
    """
    Engine for replaying perspective snapshots.
    
    Enables deterministic reconstruction of perspective state from historical
    snapshots for debugging, testing, or restoration purposes.
    """
    
    max_history_size: int = 1000
    """Maximum number of snapshots to retain."""
    
    _snapshots: list[PerspectiveSnapshot] = field(default_factory=list)
    """Internal storage for snapshot history."""
    
    def __post_init__(self) -> None:
        """Initialize after construction."""
        self._snapshots.clear()
    
    @property
    def size(self) -> int:
        """Get number of stored snapshots."""
        return len(self._snapshots)
    
    def add_snapshot(self, snapshot: PerspectiveSnapshot) -> bool:
        """
        Add a snapshot for potential replay.
        
        Args:
            snapshot: Snapshot to store
            
        Returns:
            True if added, False if capacity exceeded
        """
        # Enforce max size by removing oldest entries if needed
        while len(self._snapshots) >= self.max_history_size:
            self._snapshots.pop(0)
        
        self._snapshots.append(snapshot)
        return True
    
    def get_at_generation(self, generation: int) -> Optional[PerspectiveSnapshot]:
        """
        Get snapshot for a specific generation.
        
        Args:
            generation: Generation number to find
            
        Returns:
            Snapshot or None if not found
        """
        for s in reversed(self._snapshots):
            if s.generation == generation:
                return s
        return None
    
    def get_latest(self) -> Optional[PerspectiveSnapshot]:
        """Get the most recent snapshot."""
        if not self._snapshots:
            return None
        return max(self._snapshots, key=lambda s: s.generation)
    
    def replay_to_generation(
        self,
        target_generation: int,
    ) -> list[PerspectiveSnapshot]:
        """
        Get snapshots up to a target generation for replay.
        
        Args:
            target_generation: Target generation (inclusive)
            
        Returns:
            List of snapshots from earliest to target
        """
        result = [
            s for s in self._snapshots
            if s.generation <= target_generation
        ]
        return sorted(result, key=lambda s: s.generation)
    
    def clear(self) -> None:
        """Clear all stored snapshots."""
        self._snapshots.clear()


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Classes
    "PerspectiveSnapshot",
    "SnapshotBatch",
    "SnapshotValidator",
    "SnapshotReplayEngine",
)