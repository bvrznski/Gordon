# Executive State Histories
# =========================

"""
Bounded history types for executive state and context tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveStateHistoryEntry:
    """Single entry in state history."""
    
    revision: int = 0
    """Revision at this point."""
    
    mode: str = "uninitialized"
    """Executive mode at this revision."""
    
    timestamp_utc: float = 0.0
    """When this revision was created (seconds since epoch)."""
    
    transition_kind: Optional[str] = None
    """Transition that produced this revision."""
    
    state_id: str = "exec_state_unknown"
    """State ID at this revision."""


@dataclass(frozen=True)
class ExecutiveStateHistory:
    """
    Bounded history of executive state revisions.
    
    History stores only references and summaries, not full states.
    This prevents unbounded memory growth while providing diagnostic info.
    
    When capacity is exceeded, oldest entries are removed.
    Unresolved items are preserved (not silently evicted).
    """
    
    history_id: str = "exec_state_history_default"
    """Unique identifier for this history."""
    
    maximum_entries: int = 100
    """Maximum number of entries to keep."""
    
    entries: Tuple[ExecutiveStateHistoryEntry, ...] = field(default_factory=tuple)
    """Tuple of history entries (oldest first)."""
    
    @classmethod
    def create(cls, max_entries: int = 100) -> ExecutiveStateHistory:
        """Create a new empty history."""
        return cls(maximum_entries=max_entries)
    
    def add_entry(self, entry: ExecutiveStateHistoryEntry) -> ExecutiveStateHistory:
        """Add an entry to history, evicting oldest if at capacity."""
        new_entries = self.entries + (entry,)
        if len(new_entries) > self.maximum_entries:
            new_entries = new_entries[-self.maximum_entries:]
        return ExecutiveStateHistory(
            history_id=self.history_id,
            maximum_entries=self.maximum_entries,
            entries=new_entries,
        )
    
    def get_latest_entry(self) -> Optional[ExecutiveStateHistoryEntry]:
        """Get the most recent entry."""
        return self.entries[-1] if self.entries else None


@dataclass(frozen=True)
class ExecutiveContextHistoryEntry:
    """Single entry in context history."""
    
    context_id: str = "exec_context_unknown"
    """Context ID."""
    
    revision: int = 1
    """Context revision."""
    
    purpose: str = "general_executive_assessment"
    """Purpose of the context."""
    
    validity_class: str = "unknown"
    """Validity classification at this point."""
    
    timestamp_utc: float = 0.0
    """When context was assembled."""


@dataclass(frozen=True)
class ExecutiveContextHistory:
    """
    Bounded history of executive context revisions.
    
    History stores only references and summaries, not full contexts.
    """
    
    history_id: str = "exec_context_history_default"
    """Unique identifier for this history."""
    
    maximum_entries: int = 100
    """Maximum number of entries to keep."""
    
    entries: Tuple[ExecutiveContextHistoryEntry, ...] = field(default_factory=tuple)
    """Tuple of history entries (oldest first)."""
    
    @classmethod
    def create(cls, max_entries: int = 100) -> ExecutiveContextHistory:
        """Create a new empty context history."""
        return cls(maximum_entries=max_entries)
    
    def add_entry(self, entry: ExecutiveContextHistoryEntry) -> ExecutiveContextHistory:
        """Add an entry to context history."""
        new_entries = self.entries + (entry,)
        if len(new_entries) > self.maximum_entries:
            new_entries = new_entries[-self.maximum_entries:]
        return ExecutiveContextHistory(
            history_id=self.history_id,
            maximum_entries=self.maximum_entries,
            entries=new_entries,
        )
    
    def get_latest_entry(self) -> Optional[ExecutiveContextHistoryEntry]:
        """Get the most recent entry."""
        return self.entries[-1] if self.entries else None


__all__: Tuple[str, ...] = (
    "ExecutiveStateHistoryEntry",
    "ExecutiveStateHistory",
    "ExecutiveContextHistoryEntry",
    "ExecutiveContextHistory",
)