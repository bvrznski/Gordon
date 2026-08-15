# Internal Episode Snapshot Model
# ===============================

"""
Snapshot model for internal episode serialization.

A snapshot is an immutable, serialization-ready representation of an episode
for storage or transmission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InternalEpisodeSnapshot:
    """
    Immutable snapshot of an internal episode for serialization/storage.
    
    A snapshot preserves the essential state and content of an episode without
    live runtime references or provider implementations.
    
    PROPERTIES:
        • Must expose no mutable nested structure
        • Preserve episode revision
        • Preserve context binding
        • Preserve evidence and outcome IDs (not full items)
        • Support deterministic comparison
        • Support serialization
        • Avoid live provider references
        
    USE CASES:
        • Storage in database or cache
        • Transmission between processes/hosts
        • Historical tracking without full episodes
        • Deterministic replay of episode state
    """
    
    # Snapshot identity
    snapshot_id: str
    """Unique identifier for this snapshot."""
    
    snapshot_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Episode identity and revisioning
    episode_id: str
    """ID of the original episode."""
    
    revision: int = 1
    """Revision number of the original episode."""
    
    created_at_utc: datetime
    """When the episode was created."""
    
    updated_at_utc: datetime
    """When the episode state last changed."""
    
    # Definition
    episode_type: str
    """Type of internal cognition (InternalEpisodeType.*)."""
    
    purpose_statement: str
    """Purpose statement from the original episode."""
    
    context_id: str
    """Bound context ID."""
    
    context_revision: int = 1
    """Bound context revision number."""
    
    # Lifecycle state
    lifecycle_state: str
    """Current lifecycle state (InternalEpisodeLifecycle.*)."""
    
    lifecycle_reason: Optional[str] = None
    """Reason for current lifecycle state."""
    
    # Coordination summary
    plan_step_count: int = 0
    """Number of steps in the active plan."""
    
    completed_step_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of completed plan steps."""
    
    pending_step_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of pending plan steps."""
    
    evidence_item_count: int = 0
    """Total number of evidence items collected."""
    
    conflict_count: int = 0
    """Number of conflicts detected."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence level (0.0 to 1.0)."""
    
    completeness_status: str = "partial"
    """Completeness status (InternalOutcomeStatus.*)."""
    
    @classmethod
    def from_episode(cls, episode: "InternalEpisode") -> InternalEpisodeSnapshot:
        """
        Create a snapshot from an InternalEpisode instance.
        
        This does NOT copy evidence items or full payloads - only references
        and summaries to prevent unbounded growth.
        """
        return cls(
            snapshot_id=f"snapshot_{episode.episode_id}",
            episode_id=episode.episode_id,
            revision=episode.revision,
            created_at_utc=episode.created_at_utc,
            updated_at_utc=episode.updated_at_utc,
            episode_type=episode.episode_type,
            purpose_statement=episode.purpose,
            context_id=episode.context_id,
            context_revision=episode.context_revision,
            lifecycle_state=episode.lifecycle.state,
            lifecycle_reason=episode.lifecycle.reason,
            completed_step_ids=tuple(episode.state.completed_steps),
            pending_step_ids=tuple(episode.state.pending_steps),
            evidence_item_count=episode.state.evidence_item_count,
            conflict_count=len(episode.conflict_ids),
            confidence=episode.confidence,
            completeness_status=episode.completeness_status,
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert snapshot to fully serializable dictionary.
        
        Returns a dict that can be safely JSON-serialized without any
        live objects or references.
        """
        return {
            "snapshot_id": self.snapshot_id,
            "snapshot_version": self.snapshot_version,
            "episode_id": self.episode_id,
            "revision": self.revision,
            "created_at_utc": (
                self.created_at_utc.isoformat()
                if hasattr(self.created_at_utc, "isoformat")
                else str(self.created_at_utc)
            ),
            "updated_at_utc": (
                self.updated_at_utc.isoformat()
                if hasattr(self.updated_at_utc, "isoformat")
                else str(self.updated_at_utc)
            ),
            "episode_type": self.episode_type,
            "purpose_statement": self.purpose_statement,
            "context_id": self.context_id,
            "context_revision": self.context_revision,
            "lifecycle_state": self.lifecycle_state,
        }


@dataclass(frozen=True, slots=True)
class InternalEpisodeHistoryEntry:
    """
    History entry for a single episode state.
    
    Contains only references and summaries, NOT full episode payloads.
    """
    
    episode_id: str
    """ID of the episode."""
    
    revision: int = 1
    """Revision number at time of recording."""
    
    timestamp_utc: datetime
    """When this entry was recorded."""
    
    lifecycle_state: str
    """Lifecycle state at time of recording."""
    
    purpose_statement: str
    """Purpose statement at time of recording."""
    
    evidence_count: int = 0
    """Evidence item count at time of recording."""
    
    confidence: float = 0.5
    """Confidence score at time of recording."""
    
    snapshot_id: Optional[str] = None
    """ID of the associated snapshot (if any)."""


@dataclass(frozen=True, slots=True)
class InternalEpisodeHistory:
    """
    Bounded history of internal episodes.
    
    History stores only references and summaries - not full episode payloads.
    This prevents unbounded memory growth while still providing diagnostic info.
    
    PROPERTIES:
        • maximum_entries: Hard limit on entries stored
        • entries: Tuple of history entries (oldest first)
        
    CAPACITY MANAGEMENT:
        When history exceeds maximum capacity, oldest entries are removed.
        This is NOT persistent memory - it's coordination state.
    """
    
    # Identity
    history_id: str = "default"
    """Unique identifier for this history instance."""
    
    # Capacity constraints
    maximum_entries: int = 100
    """Maximum number of entries to keep in memory."""
    
    # History storage (bounded)
    entries: Tuple[InternalEpisodeHistoryEntry, ...] = field(default_factory=tuple)
    """Tuple of history entries (oldest first)."""
    
    @classmethod
    def create(cls, maximum_entries: int = 100) -> InternalEpisodeHistory:
        """Create a new empty history with specified capacity."""
        return cls(maximum_entries=maximum_entries)
    
    def add_entry(self, entry: InternalEpisodeHistoryEntry) -> InternalEpisodeHistory:
        """
        Add an entry to the history.
        
        Returns a new history instance with the entry added. If capacity
        is exceeded, oldest entries are removed.
        """
        new_entries = self.entries + (entry,)
        
        # Enforce capacity limit
        if len(new_entries) > self.maximum_entries:
            new_entries = new_entries[-self.maximum_entries:]
        
        return InternalEpisodeHistory(
            history_id=self.history_id,
            maximum_entries=self.maximum_entries,
            entries=new_entries,
        )
    
    def get_recent_episodes(self, count: int = 10) -> Tuple[str, ...]:
        """Get the IDs of the most recent episodes."""
        if not self.entries:
            return ()
        
        # Get last 'count' unique episode IDs (newest first)
        seen = set()
        result = []
        for entry in reversed(self.entries):
            if entry.episode_id not in seen:
                seen.add(entry.episode_id)
                result.append(entry.episode_id)
                if len(result) >= count:
                    break
        
        return tuple(result)
    
    def get_latest_entry(self) -> Optional[InternalEpisodeHistoryEntry]:
        """Get the most recent history entry."""
        if self.entries:
            return self.entries[-1]
        return None