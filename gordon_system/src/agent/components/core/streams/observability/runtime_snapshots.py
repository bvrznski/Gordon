# Stream Runtime Snapshots Layer - Phase 3.11.16
# ===============================================

"""
Canonical Stream Runtime Snapshots implementation.

Runtime Snapshots are PASSIVE immutable state capture:
- They NEVER modify stream behavior or data
- They NEVER influence execution flow
- They ONLY provide read-only snapshots of runtime state

Supported snapshot types:
- Stream metadata: Stream configuration and status
- Subscriber metadata: Subscription state
- Cursor metadata: Consumer progress tracking
- Checkpoint metadata: Recovery points
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# RUNTIME STREAM SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class RuntimeStreamSnapshot:
    """
    Immutable snapshot of a stream's runtime state.
    
    Contains only bounded metadata - no live objects, locks, or callbacks.
    """
    
    # Identity
    snapshot_id: str                # Unique ID for this snapshot
    
    # Timestamps
    captured_at_utc: float          # When snapshot was taken
    
    # Stream identity
    stream_id: str                  # Which stream?
    
    # Configuration context (versioned references, not objects)
    configuration_generation: int = 1   # Config generation number
    ownership_version: int = 1          # Ownership version
    
    # Lifecycle state
    lifecycle_state: str = "active"     # e.g., "active", "paused"
    
    # Operational status
    admission_status: str = "open"      # open, paused, draining, closed
    degradation_state: str = "healthy"  # healthy, degraded, recovering
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    last_activity_utc: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "captured_at_utc": self.captured_at_utc,
            "stream_id": self.stream_id,
            "configuration_generation": self.configuration_generation,
            "ownership_version": self.ownership_version,
            "lifecycle_state": self.lifecycle_state,
            "admission_status": self.admission_status,
            "degradation_state": self.degradation_state,
            "created_at_utc": self.created_at_utc,
            "last_activity_utc": self.last_activity_utc,
        }


# =============================================================================
# SUBSCRIBER SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class SubscriberSnapshot:
    """
    Immutable snapshot of a subscriber's state.
    
    Contains only bounded metadata - no live objects or callbacks.
    """
    
    # Identity
    snapshot_id: str                # Unique ID for this snapshot
    
    # Timestamps
    captured_at_utc: float          # When snapshot was taken
    
    # Subscriber identity
    subscriber_id: str              # Which subscriber?
    
    # Stream context
    stream_id: str                  # Which stream?
    subscription_id: Optional[str] = None  # Subscription ID (if available)
    
    # State
    subscription_state: str = "active"    # e.g., "active", "paused"
    
    # Progress tracking
    current_cursor_position: int = 0      # Current position
    last_checkpoint_position: Optional[int] = None
    
    # Statistics
    records_delivered: int = 0            # Total delivered
    records_acknowledged: int = 0         # Total acknowledged
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "captured_at_utc": self.captured_at_utc,
            "subscriber_id": self.subscriber_id,
            "stream_id": self.stream_id,
            "subscription_id": self.subscription_id,
            "subscription_state": self.subscription_state,
            "current_cursor_position": self.current_cursor_position,
            "last_checkpoint_position": self.last_checkpoint_position,
            "records_delivered": self.records_delivered,
            "records_acknowledged": self.records_acknowledged,
        }


# =============================================================================
# CURSOR SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class CursorSnapshot:
    """
    Immutable snapshot of a cursor's state.
    
    Contains only bounded metadata - no live objects or runtime references.
    """
    
    # Identity
    snapshot_id: str                # Unique ID for this snapshot
    
    # Timestamps
    captured_at_utc: float          # When snapshot was taken
    
    # Cursor identity
    cursor_id: str                  # Which cursor?
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # Position
    position: int = 0               # Current position in stream
    
    # Statistics
    records_delivered: int = 0      # Total delivered to this cursor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "captured_at_utc": self.captured_at_utc,
            "cursor_id": self.cursor_id,
            "stream_id": self.stream_id,
            "position": self.position,
            "records_delivered": self.records_delivered,
        }


# =============================================================================
# CHECKPOINT SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class CheckpointSnapshot:
    """
    Immutable snapshot of a checkpoint's state.
    
    Contains only bounded metadata - no live objects or runtime references.
    """
    
    # Identity
    snapshot_id: str                # Unique ID for this snapshot
    
    # Timestamps
    captured_at_utc: float          # When snapshot was taken
    
    # Checkpoint identity
    checkpoint_id: str              # Which checkpoint?
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # Position at checkpoint time
    position: int = 0               # Cursor position at checkpoint
    
    # Metadata
    version: int = 1                # Checkpoint version
    created_by: Optional[str] = None  # Who/what created it?
    
    # Status
    status: str = "committed"       # e.g., "proposed", "validated", "committed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "captured_at_utc": self.captured_at_utc,
            "checkpoint_id": self.checkpoint_id,
            "stream_id": self.stream_id,
            "position": self.position,
            "version": self.version,
            "created_by": self.created_by,
            "status": self.status,
        }


# =============================================================================
# FULL RUNTIME SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class FullRuntimeSnapshot:
    """
    Immutable complete runtime snapshot of all stream components.
    
    Contains only bounded metadata - no live objects, locks, or callbacks.
    Used for debugging and read-only inspection of system state.
    """
    
    # Timestamps
    captured_at_utc: float = field(default_factory=time.time)
    
    # Snapshots by component type
    stream_snapshots: Dict[str, RuntimeStreamSnapshot] = field(
        default_factory=dict  # stream_id -> snapshot
    )
    subscriber_snapshots: Dict[str, SubscriberSnapshot] = field(
        default_factory=dict  # subscriber_id -> snapshot
    )
    cursor_snapshots: Dict[str, CursorSnapshot] = field(
        default_factory=dict  # cursor_id -> snapshot
    )
    checkpoint_snapshots: Dict[str, CheckpointSnapshot] = field(
        default_factory=dict  # checkpoint_id -> snapshot
    )
    
    # Summary statistics
    total_streams: int = 0
    total_subscribers: int = 0
    total_cursors: int = 0
    total_checkpoints: int = 0
    
    def __post_init__(self):
        """Post-initialization to set computed fields."""
        object.__setattr__(self, 'total_streams', len(self.stream_snapshots))
        object.__setattr__(self, 'total_subscribers', len(self.subscriber_snapshots))
        object.__setattr__(self, 'total_cursors', len(self.cursor_snapshots))
        object.__setattr__(self, 'total_checkpoints', len(self.checkpoint_snapshots))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "captured_at_utc": self.captured_at_utc,
            "stream_snapshots": {sid: s.to_dict() for sid, s in self.stream_snapshots.items()},
            "subscriber_snapshots": {sid: s.to_dict() for sid, s in self.subscriber_snapshots.items()},
            "cursor_snapshots": {sid: s.to_dict() for sid, s in self.cursor_snapshots.items()},
            "checkpoint_snapshots": {cid: c.to_dict() for cid, c in self.checkpoint_snapshots.items()},
            "total_streams": self.total_streams,
            "total_subscribers": self.total_subscribers,
            "total_cursors": self.total_cursors,
            "total_checkpoints": self.total_checkpoints,
        }

    @classmethod
    def create_empty(cls) -> "FullRuntimeSnapshot":
        """Create an empty snapshot."""
        return cls()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) 
                      for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Snapshot types
    "RuntimeStreamSnapshot",
    "SubscriberSnapshot",
    "CursorSnapshot",
    "CheckpointSnapshot",
    "FullRuntimeSnapshot",
    
    # Factory functions
    "dataclass_replace",
]