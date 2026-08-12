# Thread Semantic Snapshot
# =========================

"""
Thread snapshot model for persistence and recovery.

A snapshot is an immutable view of a thread's semantic state at a point in time.
Snapshots are used for:
    - Persistence (saving thread state)
    - Recovery (restoring from checkpoint)
    - Audit trail (historical state inspection)
    - Parallel branch tracking (when architecture supports it)

Invariants:
    S-001: Snapshots are immutable
    S-002: Snapshot version matches the state it captures
    S-003: Snapshots contain all semantic information needed for recovery
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import uuid


@dataclass(frozen=True)
class ThreadSnapshot:
    """
    Immutable snapshot of a Thread's semantic state.
    
    A snapshot is a point-in-time view that can be used for:
        - Persistence to storage (checkpointing)
        - Recovery after interruption
        - Historical audit
        - Parallel branch tracking
    
    Snapshots are immutable and versioned. Each snapshot has:
        - A unique snapshot ID
        - A reference to the thread it captures
        - A semantic version matching that state
        - All information needed for recovery (without runtime data)
    """
    
    # Snapshot identification
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Thread reference
    thread_id: str = ""
    
    # Semantic version (matches the state in this snapshot)
    semantic_version: int = 0
    
    # Snapshot timestamp
    captured_at_utc: float = field(default_factory=lambda: 0.0)
    
    # Metadata
    name: Optional[str] = None
    purpose: Optional[str] = None
    kind: str = "default"
    
    # Semantic state (owned by thread, not runtime)
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # History references
    previous_snapshot_ids: Tuple[str, ...] = ()
    checkpoint_id: Optional[str] = None
    
    # Relationship state
    parent_thread_id: Optional[str] = None
    child_thread_ids: Tuple[str, ...] = ()
    
    @property
    def is_complete(self) -> bool:
        """Check if this snapshot represents a completed thread."""
        return self.context_data.get("thread_completed", False)
    
    def to_recovery_descriptor(self) -> "ThreadRecoveryDescriptor":
        """
        Convert snapshot to recovery descriptor for restoration.
        
        The descriptor contains only the information needed by Core
        to restore the thread, excluding any transient runtime data.
        """
        return ThreadRecoveryDescriptor(
            thread_id=self.thread_id,
            semantic_version=self.semantic_version,
            context_data=dict(self.context_data),
            checkpoint_id=self.checkpoint_id,
        )


@dataclass(frozen=True)
class ThreadRecoveryDescriptor:
    """
    Minimal information needed to recover a Thread from persistence.
    
    This is what Core's recovery system uses. It excludes runtime-specific
    data (like active Loop/Cycle references) that will be reconstructed.
    """
    
    thread_id: str
    semantic_version: int = 0
    
    # Semantic state (rehydrated)
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # Persistence reference
    checkpoint_id: Optional[str] = None
    
    # Recovery metadata
    recovered_at_utc: float = field(default_factory=lambda: 0.0)
    recovery_source: str = "checkpoint"  # or "snapshot", "ledger"
    
    @classmethod
    def empty(cls, thread_id: str) -> "ThreadRecoveryDescriptor":
        """Create an empty recovery descriptor for a new thread."""
        return cls(thread_id=thread_id)


@dataclass(frozen=True)
class ThreadSnapshotBuilder:
    """
    Builder for constructing thread snapshots.
    
    Use this when you need to create a snapshot of current thread state
    for persistence or audit purposes.
    """
    
    _thread_id: str = ""
    _semantic_version: int = 0
    _captured_at_utc: float = field(default_factory=lambda: 0.0)
    _name: Optional[str] = None
    _purpose: Optional[str] = None
    _kind: str = "default"
    _context_data: Dict[str, Any] = field(default_factory=dict)
    _previous_snapshot_ids: List[str] = field(default_factory=list)
    _checkpoint_id: Optional[str] = None
    _parent_thread_id: Optional[str] = None
    _child_thread_ids: List[str] = field(default_factory=list)
    
    def __init__(self, thread_id: str):
        self._thread_id = thread_id
        self._captured_at_utc = 0.0
    
    def with_version(self, version: int) -> "ThreadSnapshotBuilder":
        """Set the semantic version this snapshot represents."""
        object.__setattr__(self, "_semantic_version", version)
        return self
    
    def with_metadata(
        self,
        name: Optional[str] = None,
        purpose: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> "ThreadSnapshotBuilder":
        """Set thread metadata."""
        if name is not None:
            object.__setattr__(self, "_name", name)
        if purpose is not None:
            object.__setattr__(self, "_purpose", purpose)
        if kind is not None:
            object.__setattr__(self, "_kind", kind)
        return self
    
    def with_context_data(self, data: Dict[str, Any]) -> "ThreadSnapshotBuilder":
        """Set the context data for this snapshot."""
        object.__setattr__(self, "_context_data", dict(data))
        return self
    
    def with_checkpoint_id(self, checkpoint_id: str) -> "ThreadSnapshotBuilder":
        """Associate a checkpoint ID with this snapshot."""
        object.__setattr__(self, "_checkpoint_id", checkpoint_id)
        return self
    
    def add_previous_snapshot(self, snapshot_id: str) -> "ThreadSnapshotBuilder":
        """Add a previous snapshot ID to the history chain."""
        ids = list(self._previous_snapshot_ids)
        if snapshot_id not in ids:
            ids.append(snapshot_id)
        object.__setattr__(self, "_previous_snapshot_ids", ids)
        return self
    
    def with_parent_child(
        self,
        parent_thread_id: Optional[str] = None,
        child_thread_ids: Optional[List[str]] = None,
    ) -> "ThreadSnapshotBuilder":
        """Set parent-child relationship information."""
        if parent_thread_id is not None:
            object.__setattr__(self, "_parent_thread_id", parent_thread_id)
        if child_thread_ids is not None:
            object.__setattr__(self, "_child_thread_ids", list(child_thread_ids))
        return self
    
    def build(self) -> ThreadSnapshot:
        """Build and return an immutable ThreadSnapshot."""
        return ThreadSnapshot(
            thread_id=self._thread_id,
            semantic_version=self._semantic_version,
            captured_at_utc=self._captured_at_utc,
            name=self._name,
            purpose=self._purpose,
            kind=self._kind,
            context_data=dict(self._context_data),
            previous_snapshot_ids=tuple(self._previous_snapshot_ids),
            checkpoint_id=self._checkpoint_id,
            parent_thread_id=self._parent_thread_id,
            child_thread_ids=tuple(self._child_thread_ids),
        )


@dataclass(frozen=True)
class ThreadSnapshotChain:
    """
    Chain of snapshots for a thread, maintaining historical state.
    
    Provides methods to traverse snapshot history and find the most recent
    state or a specific version.
    """
    
    # Snapshot ID → Snapshot mapping
    _snapshots: Dict[str, ThreadSnapshot] = field(default_factory=dict)
    
    def add_snapshot(self, snapshot: ThreadSnapshot) -> None:
        """Add a snapshot to the chain."""
        snapshots = dict(self._snapshots)
        snapshots[snapshot.snapshot_id] = snapshot
        object.__setattr__(self, "_snapshots", snapshots)
    
    def get_latest_snapshot(self) -> Optional[ThreadSnapshot]:
        """Get the most recent snapshot in the chain."""
        if not self._snapshots:
            return None
        
        latest = max(
            self._snapshots.values(),
            key=lambda s: (s.semantic_version, s.captured_at_utc)
        )
        return latest
    
    def get_snapshot_by_version(self, version: int) -> Optional[ThreadSnapshot]:
        """Get the snapshot for a specific semantic version."""
        for snapshot in self._snapshots.values():
            if snapshot.semantic_version == version:
                return snapshot
        return None
    
    def get_ancestors(self, snapshot_id: str) -> List[ThreadSnapshot]:
        """Get all ancestor snapshots of a given snapshot."""
        result = []
        
        def find_ancestor(sid: str) -> Optional[ThreadSnapshot]:
            if sid not in self._snapshots:
                return None
            snapshot = self._snapshots[sid]
            for prev_id in snapshot.previous_snapshot_ids:
                if prev_id in self._snapshots:
                    result.append(self._snapshots[prev_id])
                    find_ancestor(prev_id)
        
        find_ancestor(snapshot_id)
        return result
    
    def get_thread_history(
        self, thread_id: str
    ) -> List[Tuple[int, ThreadSnapshot]]:
        """Get all snapshots for a specific thread, ordered by version."""
        history = []
        for snapshot in self._snapshots.values():
            if snapshot.thread_id == thread_id:
                history.append((snapshot.semantic_version, snapshot))
        
        history.sort(key=lambda x: x[0])
        return history
    
    def clear(self) -> None:
        """Clear all snapshots from the chain."""
        object.__setattr__(self, "_snapshots", {})


__all__ = [
    "ThreadSnapshot",
    "ThreadRecoveryDescriptor",
    "ThreadSnapshotBuilder",
    "ThreadSnapshotChain",
]