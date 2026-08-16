# Internal Context History Model
# ==============================

"""
History model for internal context snapshots.

History maintains bounded records of context states without storing full
contexts indefinitely. Used for debugging and coordination state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InternalContextHistoryEntry:
    """
    History entry for a single context state.
    
    Contains only references and summaries, NOT full context payloads.
    """
    
    context_id: str
    """ID of the context."""
    
    revision: int = 1
    """Revision number at time of recording."""
    
    timestamp_utc: datetime
    """When this entry was recorded."""
    
    purpose: str
    """Purpose of the context."""
    
    completeness_status: str
    """Completeness status at time of recording."""
    
    confidence_score: float
    """Confidence score at time of recording."""
    
    transition_type: Optional[str] = None
    """How this context was reached (None if first entry)."""
    
    snapshot_id: Optional[str] = None
    """ID of the associated snapshot (if any)."""


@dataclass(frozen=True, slots=True)
class InternalContextHistory:
    """
    Bounded history of internal contexts.
    
    History stores only references and summaries - not full context payloads.
    This prevents unbounded memory growth while still providing diagnostic info.
    
    PROPERTIES:
        • maximum_entries: Hard limit on entries stored
        • entries: Tuple of history entries (oldest first)
        • recent_context_ids: List of most recent context IDs
        • diagnostics_digest: Summary for quick debugging
    
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
    entries: Tuple[InternalContextHistoryEntry, ...] = field(default_factory=tuple)
    """Tuple of history entries (oldest first)."""
    
    @classmethod
    def create(cls, maximum_entries: int = 100) -> InternalContextHistory:
        """Create a new empty history with specified capacity."""
        return cls(maximum_entries=maximum_entries)
    
    def add_entry(self, entry: InternalContextHistoryEntry) -> InternalContextHistory:
        """
        Add an entry to the history.
        
        Returns a new history instance with the entry added. If capacity
        is exceeded, oldest entries are removed.
        """
        new_entries = self.entries + (entry,)
        
        # Enforce capacity limit
        if len(new_entries) > self.maximum_entries:
            new_entries = new_entries[-self.maximum_entries:]
        
        return InternalContextHistory(
            history_id=self.history_id,
            maximum_entries=self.maximum_entries,
            entries=new_entries,
        )
    
    def get_recent_contexts(self, count: int = 10) -> Tuple[str, ...]:
        """Get the IDs of the most recent contexts."""
        if not self.entries:
            return ()
        
        # Get last 'count' unique context IDs (newest first)
        seen = set()
        result = []
        for entry in reversed(self.entries):
            if entry.context_id not in seen:
                seen.add(entry.context_id)
                result.append(entry.context_id)
                if len(result) >= count:
                    break
        
        return tuple(result)
    
    def get_latest_entry(self) -> Optional[InternalContextHistoryEntry]:
        """Get the most recent history entry."""
        if self.entries:
            return self.entries[-1]
        return None
    
    def get_diagnostics_digest(self) -> dict[str, Any]:
        """
        Get a diagnostic digest of the history.
        
        Returns summary info without exposing full context data.
        """
        total_entries = len(self.entries)
        purposes = {}
        completeness_by_purpose = {}
        
        for entry in self.entries:
            # Count by purpose
            purposes[entry.purpose] = purposes.get(entry.purpose, 0) + 1
            
            # Track completeness distribution
            comp = entry.completeness_status
            completeness_by_purpose.setdefault(entry.purpose, {})
            completeness_by_purpose[entry.purpose][comp] = (
                completeness_by_purpose[entry.purpose].get(comp, 0) + 1
            )
        
        return {
            "total_entries": total_entries,
            "purposes": purposes,
            "completeness_by_purpose": completeness_by_purpose,
        }
    
    def get_entry_count(self) -> int:
        """Return the current number of entries in history."""
        return len(self.entries)