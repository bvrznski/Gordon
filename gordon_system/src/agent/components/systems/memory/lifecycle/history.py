# Memory Lifecycle History - Phase 5.1.4 Immutable Transition Tracking
# ====================================================================
"""
Memory Lifecycle History: The immutable record of all state transitions.

This module implements the history tracking system that preserves:

    - Every state transition record
    - All validation results
    - Diagnostic information
    - Provenance of each transition

History Laws:
    HISTORY-LAW-001: History is immutable once recorded
    HISTORY-LAW-002: History includes all transitions in order
    HISTORY-LAW-003: History preserves diagnostic context
    HISTORY-LAW-004: History is independently queryable
    HISTORY-LAW-005: History is never deleted

The history system maintains a complete audit trail of every artifact's
lifecycle journey, enabling:

    - Full provenance inspection
    - Failure analysis and debugging
    - Compliance verification
    - Historical state reconstruction
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Iterator
from enum import Enum, auto
import time


# =============================================================================
# HISTORY ENTRIES - Each entry is a single historical record
# =============================================================================


@dataclass(frozen=True)
class HistoryEntry:
    """
    A single history entry in the lifecycle timeline.
    
    Every transition produces exactly one history entry. Entries are
    immutable and form a complete timeline of an artifact's lifecycle.
    
    Fields:
        entry_id:            Unique ID for this history entry
        artifact_id:         Which artifact is this about?
        
        # Transition details
        timestamp_utc:       When did this happen?
        previous_state:      State before transition
        next_state:          State after transition
        
        # Metadata
        trigger:             What triggered the transition?
        type_:               Type of transition
        
        # Validation
        validation_passed:   Was validation successful?
        validation_result:   Details if validation failed
        
        # Provenance
        provenance:          Where did this record come from?
        
        # Diagnostics
        diagnostics:         Any diagnostic information
        recovery_info:       If recovery, details of what was repaired
    """
    
    entry_id: str                             # Unique ID for this entry
    artifact_id: str                          # Artifact being tracked
    
    timestamp_utc: float                      # When it happened
    previous_state: str                       # State before
    next_state: str                           # State after
    
    trigger: str = "unknown"                  # What triggered it?
    type_: str = "unknown"                    # Type of transition
    
    validation_passed: bool = True            # Validation status
    validation_result: Optional[str] = None   # If failed
    
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    recovery_info: Optional[Dict[str, Any]] = None  # If recovery


# =============================================================================
# HISTORY SNAPSHOT - Point-in-time view of history
# =============================================================================


@dataclass(frozen=True)
class HistorySnapshot:
    """
    A point-in-time snapshot of an artifact's history.
    
    Snapshots preserve the complete state for historical inspection or
    recovery purposes. They can never modify the actual history.
    
    Fields:
        snapshot_id:         Unique ID for this snapshot
        artifact_id:         Which artifact?
        
        # State at time of snapshot
        current_state:       State when snapshot was taken
        
        # History at time of snapshot (subset)
        entries_before:      Entry IDs before this point
        
        # Timestamps
        captured_at_utc:     When was the snapshot taken?
    """
    
    snapshot_id: str                          # Unique ID for this snapshot
    artifact_id: str                          # Artifact being snapshotted
    
    current_state: str                        # State when snapshotted
    
    entries_before: Tuple[str, ...] = field(default_factory=tuple)
    
    captured_at_utc: float = field(default_factory=time.time)


# =============================================================================
# LIFECYCLE HISTORY - The immutable history log
# =============================================================================


class LifecycleHistory:
    """
    Immutable history log for a single artifact's lifecycle.
    
    This class maintains the complete timeline of an artifact's lifecycle,
    including all state transitions, validation results, and diagnostics.
    
    History Laws:
        HISTORY-LAW-001: History is immutable once recorded
        HISTORY-LAW-002: History includes all transitions in order
        HISTORY-LAW-003: History preserves diagnostic context
        HISTORY-LAW-004: History is independently queryable
        HISTORY-LAW-005: History is never deleted
    
    Operations:
        - append_entry: Add a new history entry (immutable update)
        - get_entries: Get all entries (returns copy, not reference)
        - get_latest_entry: Get the most recent entry
        - find_state_changes: Find all transitions to/from a state
        - take_snapshot: Create a point-in-time snapshot
    
    The history is stored as a list of HistoryEntry objects. Each append
    operation returns a new LifecycleHistory instance, preserving immutability.
    """
    
    def __init__(
        self,
        artifact_id: Optional[str] = None,
        initial_state: str = "candidate",
        initial_provenance: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the history log for an artifact.
        
        Args:
            artifact_id: ID of the artifact (optional)
            initial_state: Starting state (default: candidate)
            initial_provenance: Initial provenance info
        """
        self._artifact_id = artifact_id or ""
        self._entries: List[HistoryEntry] = []
        
        # Create initial entry for the starting state
        if initial_provenance is None:
            initial_provenance = {"origin": "lifecycle_system", "initial_state": initial_state}
        
        initial_entry = HistoryEntry(
            entry_id=f"init:{time.time():.6f}",
            artifact_id=self._artifact_id,
            timestamp_utc=time.time(),
            previous_state="none",
            next_state=initial_state,
            trigger="system_initialization",
            type_="admission",
            provenance=dict(initial_provenance),
        )
        
        self._entries.append(initial_entry)
    
    def append_entry(
        self,
        next_state: str,
        trigger: str = "unknown",
        type_: str = "transition",
        validation_passed: bool = True,
        validation_result: Optional[str] = None,
        diagnostics: Tuple[str, ...] = (),
        recovery_info: Optional[Dict[str, Any]] = None,
    ) -> "LifecycleHistory":
        """
        Create a new history entry and return updated history.
        
        This does NOT modify the current instance - it returns a new one.
        
        Args:
            next_state: State after transition
            trigger: What triggered the transition?
            type_: Type of transition
            validation_passed: Was validation successful?
            validation_result: Details if validation failed
            diagnostics: Any diagnostic information
            recovery_info: If recovery, details of what was repaired
            
        Returns:
            New LifecycleHistory with the entry appended
        """
        # Get previous state from latest entry (or use current if empty)
        previous_state = self._entries[-1].next_state if self._entries else "unknown"
        
        new_entry = HistoryEntry(
            entry_id=f"entry:{time.time():.6f}:{len(self._entries)}",
            artifact_id=self._artifact_id,
            timestamp_utc=time.time(),
            previous_state=previous_state,
            next_state=next_state,
            trigger=trigger,
            type_=type_,
            validation_passed=validation_passed,
            validation_result=validation_result,
            provenance={"origin": "lifecycle_history", "timestamp_utc": time.time()},
            diagnostics=diagnostics,
            recovery_info=recovery_info,
        )
        
        # Return new instance with appended entry (immutable)
        new_instance = LifecycleHistory.__new__(LifecycleHistory)
        new_instance._artifact_id = self._artifact_id
        new_instance._entries = list(self._entries) + [new_entry]
        
        return new_instance
    
    def get_entries(self) -> Tuple[HistoryEntry, ...]:
        """
        Get all history entries.
        
        Returns a copy to preserve immutability.
        
        Returns:
            Tuple of HistoryEntry objects in chronological order
        """
        return tuple(self._entries)
    
    def get_latest_entry(self) -> Optional[HistoryEntry]:
        """
        Get the most recent history entry.
        
        Returns:
            Latest HistoryEntry or None if empty
        """
        return self._entries[-1] if self._entries else None
    
    @property
    def artifact_id(self) -> str:
        """Get the artifact ID."""
        return self._artifact_id
    
    @property
    def current_state(self) -> str:
        """Get the current state from the latest entry."""
        return self._entries[-1].next_state if self._entries else "unknown"
    
    @property
    def entry_count(self) -> int:
        """Total number of history entries."""
        return len(self._entries)
    
    def find_state_changes(
        self,
        state: str,
        include_from: bool = True,
        include_to: bool = True,
    ) -> Tuple[HistoryEntry, ...]:
        """
        Find all transitions involving a specific state.
        
        Args:
            state: State to search for
            include_from: Include entries where this was the previous state?
            include_to: Include entries where this was the next state?
            
        Returns:
            Tuple of matching history entries
        """
        result = []
        for entry in self._entries:
            if include_from and entry.previous_state == state:
                result.append(entry)
            elif include_to and entry.next_state == state:
                result.append(entry)
        
        return tuple(result)
    
    def find_transitions_between(
        self,
        from_state: str,
        to_state: str,
    ) -> Tuple[HistoryEntry, ...]:
        """
        Find all transitions directly from one state to another.
        
        Args:
            from_state: Source state
            to_state: Target state
            
        Returns:
            Tuple of matching history entries
        """
        return tuple(
            e for e in self._entries
            if e.previous_state == from_state and e.next_state == to_state
        )
    
    def take_snapshot(self) -> HistorySnapshot:
        """
        Create a point-in-time snapshot of the current history.
        
        Returns:
            New HistorySnapshot
        """
        return HistorySnapshot(
            snapshot_id=f"snapshot:{time.time():.6f}",
            artifact_id=self._artifact_id,
            current_state=self.current_state,
            entries_before=tuple(e.entry_id for e in self._entries),
            captured_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert history to a dictionary representation.
        
        Returns:
            Dictionary with all history data
        """
        return {
            "artifact_id": self._artifact_id,
            "current_state": self.current_state,
            "entry_count": len(self._entries),
            "entries": [
                {
                    "entry_id": e.entry_id,
                    "timestamp_utc": e.timestamp_utc,
                    "previous_state": e.previous_state,
                    "next_state": e.next_state,
                    "trigger": e.trigger,
                    "type_": e.type_,
                    "validation_passed": e.validation_passed,
                    "validation_result": e.validation_result,
                    "provenance": dict(e.provenance),
                    "diagnostics": list(e.diagnostics),
                    "recovery_info": e.recovery_info,
                }
                for e in self._entries
            ],
        }


# =============================================================================
# HISTORY STORE - Stores histories for multiple artifacts
# =============================================================================


class LifecycleHistoryStore:
    """
    Store for managing lifecycle histories of multiple artifacts.
    
    This provides a central repository for all artifact histories, enabling:
        - Centralized history management
        - Cross-artifact analysis
        - Bulk operations on histories
    
    Operations:
        - get_history: Get or create history for an artifact
        - append_entry: Add entry to specific artifact's history
        - get_all_entries: Get all entries from all artifacts
        - find_artifacts_by_state: Find all artifacts in a particular state
    """
    
    def __init__(self):
        """Initialize the history store."""
        self._histories: Dict[str, LifecycleHistory] = {}
        self._creation_count = 0
    
    def get_history(
        self,
        artifact_id: str,
        create_if_missing: bool = True,
        initial_state: str = "candidate",
    ) -> LifecycleHistory:
        """
        Get or create history for an artifact.
        
        Args:
            artifact_id: ID of the artifact
            create_if_missing: Create new history if not found?
            initial_state: Starting state if creating new
            
        Returns:
            LifecycleHistory for this artifact
        """
        if artifact_id in self._histories:
            return self._histories[artifact_id]
        
        if create_if_missing:
            history = LifecycleHistory(
                artifact_id=artifact_id,
                initial_state=initial_state,
            )
            self._histories[artifact_id] = history
            self._creation_count += 1
            return history
        
        raise KeyError(f"No history found for artifact: {artifact_id}")
    
    def append_entry(
        self,
        artifact_id: str,
        next_state: str,
        trigger: str = "unknown",
        type_: str = "transition",
        validation_passed: bool = True,
        validation_result: Optional[str] = None,
        diagnostics: Tuple[str, ...] = (),
        recovery_info: Optional[Dict[str, Any]] = None,
    ) -> LifecycleHistory:
        """
        Append an entry to an artifact's history.
        
        Args:
            artifact_id: ID of the artifact
            next_state: State after transition
            trigger: What triggered the transition?
            type_: Type of transition
            validation_passed: Was validation successful?
            validation_result: Details if validation failed
            diagnostics: Any diagnostic information
            recovery_info: If recovery, details of what was repaired
            
        Returns:
            Updated LifecycleHistory (immutable)
            
        Raises:
            KeyError: If artifact history doesn't exist
        """
        history = self.get_history(artifact_id)
        
        updated_history = history.append_entry(
            next_state=next_state,
            trigger=trigger,
            type_=type_,
            validation_passed=validation_passed,
            validation_result=validation_result,
            diagnostics=diagnostics,
            recovery_info=recovery_info,
        )
        
        # Update the store
        self._histories[artifact_id] = updated_history
        
        return updated_history
    
    def get_all_entries(self) -> Dict[str, Tuple[HistoryEntry, ...]]:
        """
        Get all entries from all artifacts.
        
        Returns:
            Dictionary mapping artifact_id to its tuple of entries
        """
        return {
            aid: h.get_entries()
            for aid, h in self._histories.items()
        }
    
    def find_artifacts_by_state(
        self,
        state: str,
    ) -> Tuple[str, ...]:
        """
        Find all artifacts currently in a particular state.
        
        Args:
            state: State to search for
            
        Returns:
            Tuple of artifact IDs
        """
        result = []
        for artifact_id, history in self._histories.items():
            if history.current_state == state:
                result.append(artifact_id)
        
        return tuple(result)
    
    def get_current_states(self) -> Dict[str, str]:
        """
        Get current states for all tracked artifacts.
        
        Returns:
            Dictionary mapping artifact_id to its current state
        """
        return {
            aid: history.current_state
            for aid, history in self._histories.items()
        }
    
    @property
    def artifact_count(self) -> int:
        """Number of artifacts with recorded histories."""
        return len(self._histories)
    
    @property
    def total_entry_count(self) -> int:
        """Total number of history entries across all artifacts."""
        return sum(len(h.get_entries()) for h in self._histories.values())


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_history_entry(
    artifact_id: str,
    previous_state: str,
    next_state: str,
    trigger: str = "unknown",
    type_: str = "transition",
    validation_passed: bool = True,
    validation_result: Optional[str] = None,
    diagnostics: Tuple[str, ...] = (),
) -> HistoryEntry:
    """
    Convenience function to create a history entry.
    
    Args:
        artifact_id: ID of the artifact
        previous_state: State before transition
        next_state: State after transition
        trigger: What triggered the transition?
        type_: Type of transition
        validation_passed: Was validation successful?
        validation_result: Details if validation failed
        diagnostics: Any diagnostic information
        
    Returns:
        New HistoryEntry
    """
    return HistoryEntry(
        entry_id=f"entry:{time.time():.6f}",
        artifact_id=artifact_id,
        timestamp_utc=time.time(),
        previous_state=previous_state,
        next_state=next_state,
        trigger=trigger,
        type_=type_,
        validation_passed=validation_passed,
        validation_result=validation_result,
        provenance={"origin": "lifecycle_history"},
        diagnostics=diagnostics,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # History entry
    "HistoryEntry",
    
    # Snapshot
    "HistorySnapshot",
    
    # History log
    "LifecycleHistory",
    
    # History store
    "LifecycleHistoryStore",
    
    # Utilities
    "create_history_entry",
]