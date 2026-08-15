# Internal Episode History Model
# =============================

"""
History model for internal episode snapshots.

History maintains bounded records of episode states without storing full
episodes indefinitely. Used for debugging and coordination state tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


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
    
    def get_diagnostics_digest(self) -> dict[str, any]:
        """
        Get a diagnostic digest of the history.
        
        Returns summary info without exposing full episode data.
        """
        total_entries = len(self.entries)
        states = {}
        
        for entry in self.entries:
            state = entry.lifecycle_state
            states[state] = states.get(state, 0) + 1
        
        return {
            "total_entries": total_entries,
            "lifecycle_states": states,
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
    
    purpose_statement: Optional[str] = None
    """Purpose statement (if available)."""
    
    evidence_count: int = 0
    """Evidence item count at time of recording."""
    
    confidence: float = 0.5
    """Confidence score at time of recording."""
    
    snapshot_id: Optional[str] = None
    """ID of the associated snapshot (if any)."""