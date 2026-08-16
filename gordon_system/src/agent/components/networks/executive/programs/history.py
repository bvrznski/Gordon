# Executive Program History
# =========================

"""
Executive Program History - Immutable dataclass for bounded program history tracking.

Program history stores essential lifecycle events, not runtime traces or detailed logs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveProgramHistoryEntry:
    """
    A single entry in an ExecutiveProgram's history.
    
    History entries record significant events but NOT runtime traces or detailed logs.
    They preserve essential information for debugging and audit without unbounded growth.
    """
    
    # Identity
    entry_id: str = "exec_history_entry_initial"
    """Unique identifier for this history entry."""
    
    program_id: str = "exec_program_initial"
    """ID of the program this entry belongs to."""
    
    sequence_number: int = 0
    """Sequential position in history (starts at 1)."""
    
    # Timestamp
    occurred_at_utc: float = 0.0
    """When event occurred (seconds since epoch)."""
    
    # Event details
    event_kind: str = "state_change"
    """
    Kind of event:
        'program_created' - Program was created
        'program_activated' - Program became active
        'program_suspended' - Program suspended
        'program_resumed' - Program resumed
        'program_completed' - Program completed successfully
        'program_failed' - Program failed
        'program_abandoned' - Program abandoned
        'program_replaced' - Program replaced
        'program_merged' - Program merged
        'program_split' - Program split into children
        'revision_created' - New revision created
        'state_changed' - State changed (non-lifecycle)
        'authority_decided' - Authority decision made
    """
    
    from_state: Optional[str] = None
    """State before the event."""
    
    to_state: Optional[str] = None
    """State after the event."""
    
    # Context
    triggered_by: Optional[str] = None
    """What caused this event (e.g., 'user_request', 'system_event')."""
    
    reason: Optional[str] = None
    """Reason for the event."""
    
    priority_at_event: int = 50
    """Priority of program at time of event."""
    
    revision_at_event: int = 1
    """Program revision at time of event."""
    
    # Related IDs
    related_program_id: Optional[str] = None
    """ID of another program involved (e.g., child, parent)."""
    
    related_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of goals involved in this event."""
    
    related_commitment_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of commitments involved in this event."""
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    """Additional metadata as key-value pairs."""
    
    @classmethod
    def initial(
        cls,
        entry_id: str = "exec_history_entry_initial",
        program_id: str = "exec_program_initial",
    ) -> ExecutiveProgramHistoryEntry:
        """
        Create an initial history entry.
        
        Args:
            entry_id: Unique identifier for this entry
            program_id: ID of the program
            
        Returns:
            New history entry with default values
        """
        return cls(
            entry_id=entry_id,
            program_id=program_id,
            sequence_number=0,
            event_kind="state_change",
            priority_at_event=50,
            revision_at_event=1,
        )


@dataclass(frozen=True)
class ExecutiveProgramHistory:
    """
    Bounded history of an ExecutiveProgram's lifecycle events.
    
    History properties:
        - Immutable: No in-place modification
        - Bounded: Maximum entries to prevent unbounded growth
        - Revisioned: Each entry has a revision number
        - Semantic: Stores essential lifecycle info, not runtime traces
    
    History is NOT:
        - A complete execution trace (too large)
        - A detailed log of all operations
        - Runtime state information
    
    History IS:
        - A bounded collection of significant events
        - Revisioned for deterministic reconstruction
        - Used for debugging and auditing
    """
    
    # Identity and revisioning
    history_id: str = "exec_history_initial"
    """Unique identifier for this history."""
    
    program_id: str = "exec_program_initial"
    """ID of the program this history belongs to."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    revision: int = 1
    """Current revision number (strictly monotonic)."""
    
    # History entries - ordered from oldest to newest
    entries: Tuple[ExecutiveProgramHistoryEntry, ...] = field(default_factory=tuple)
    """Ordered history entries (oldest first)."""
    
    max_entries: int = 1000
    """Maximum entries allowed in history."""
    
    # Entry count by kind for quick analysis
    entry_count_by_kind: dict = field(default_factory=dict)
    """Map of event_kind to count of such events."""
    
    # Timeline tracking
    first_event_at_utc: Optional[float] = None
    """When the first event occurred."""
    
    last_event_at_utc: Optional[float] = None
    """When the most recent event occurred."""
    
    total_events: int = 0
    """Total number of events in history."""
    
    # Creation tracking
    created_by: str = "executive_network"
    """Who/what created this history object."""
    
    @classmethod
    def initial(
        cls,
        history_id: str = "exec_history_initial",
        program_id: str = "exec_program_initial",
    ) -> ExecutiveProgramHistory:
        """
        Create an initial empty history.
        
        Args:
            history_id: Unique identifier for this history
            program_id: ID of the program
            
        Returns:
            New history with no entries
        """
        return cls(
            history_id=history_id,
            program_id=program_id,
        )
    
    def add_entry(self, entry: ExecutiveProgramHistoryEntry) -> ExecutiveProgramHistory:
        """
        Add a new entry to the history.
        
        Args:
            entry: The history entry to add
            
        Returns:
            New history with the entry added (if capacity allows)
        """
        if self.total_events >= self.max_entries:
            return self  # At capacity - discard oldest
        
        new_entries = self.entries + (entry,)
        
        # Update counts
        kind_counts = dict(self.entry_count_by_kind)
        event_kind = entry.event_kind
        kind_counts[event_kind] = kind_counts.get(event_kind, 0) + 1
        
        return dataclass_replace(
            self,
            entries=new_entries,
            entry_count_by_kind=kind_counts,
            last_event_at_utc=entry.occurred_at_utc,
            total_events=self.total_events + 1,
            revision=self.revision + 1,
        )
    
    def get_entries_by_kind(self, kind: str) -> Tuple[ExecutiveProgramHistoryEntry, ...]:
        """
        Get all entries of a specific event kind.
        
        Args:
            kind: Event kind to filter by
            
        Returns:
            Tuple of matching entries (new tuple)
        """
        return tuple(e for e in self.entries if e.event_kind == kind)
    
    def get_last_n_entries(self, n: int) -> Tuple[ExecutiveProgramHistoryEntry, ...]:
        """
        Get the last N entries (most recent first).
        
        Args:
            n: Number of entries to retrieve
            
        Returns:
            Last n entries as new tuple
        """
        if n <= 0:
            return ()
        return self.entries[-n:] if len(self.entries) >= n else self.entries
    
    def get_entry_by_id(self, entry_id: str) -> Optional[ExecutiveProgramHistoryEntry]:
        """
        Get a specific history entry by ID.
        
        Args:
            entry_id: ID of the entry to find
            
        Returns:
            Entry if found, None otherwise
        """
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None
    
    def get_state_at(self, sequence_number: int) -> Optional[str]:
        """
        Get the program state at a specific point in history.
        
        Args:
            sequence_number: Sequence number to look up
            
        Returns:
            State value if found in history, None otherwise
        """
        for entry in self.entries[:sequence_number + 1]:
            if entry.to_state is not None:
                return entry.to_state
        return None
    
    def get_last_transition(self) -> Optional[Tuple[str, str]]:
        """
        Get the last state transition (from, to).
        
        Returns:
            Tuple of (from_state, to_state) or None
        """
        for entry in reversed(self.entries):
            if entry.from_state is not None and entry.to_state is not None:
                return (entry.from_state, entry.to_state)
        return None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def dataclass_replace(instance: object, **kwargs) -> object:
    """
    Helper to replace fields in an immutable dataclass instance.
    
    Args:
        instance: The dataclass instance to copy
        kwargs: Field names and new values
        
    Returns:
        New instance with specified fields replaced
    """
    import dataclasses
    
    if not hasattr(instance, "__dataclass_fields__"):
        raise TypeError(f"{type(instance).__name__} is not a dataclass")
    
    # Get current field values
    field_dict = {f.name: getattr(instance, f.name) for f in dataclasses.fields(instance)}
    
    # Update with new values
    field_dict.update(kwargs)
    
    # Create new instance
    return type(instance)(**field_dict)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveProgramHistoryEntry",
    "ExecutiveProgramHistory",
)