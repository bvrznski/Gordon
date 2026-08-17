# Knowledge Revision - Phase 6.1
# =============================

"""
Knowledge Revision: Change management and versioning for semantic artifacts.

Revision tracking enables the knowledge system to maintain a complete history
of changes while preserving traceability and enabling rollback when needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REVISION EVENTS - Change operations in the revision history
# =============================================================================


class RevisionEventType(Enum):
    """
    Types of revision events.
    
    Defines the kinds of changes that can occur to knowledge artifacts.
    """
    
    INITIAL = "initial"                   # Initial version (no prior state)
    UPDATE = "update"                    # Content modification
    REFINEMENT = "refinement"            # Clarification or detail addition
    CORRECTION = "correction"            # Fixing an error
    SUPERSCEEDED = "superseded"          # Replaced by newer version
    MERGE = "merge"                      # Merged with another artifact
    SPLIT = "split"                      # Split into multiple artifacts
    
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RevisionEvent:
    """
    A single revision event in the history of a knowledge artifact.
    
    Records when and how an artifact was modified, who made the change,
    and what the change entailed.
    
    Fields:
        event_identity:      Unique identifier for this event
        timestamp_utc:       When the event occurred
        revision_number:     Revision number after this event
        event_type:          Type of change performed
        actor_type:          Type of actor (system, user, reasoning)
        actor_id:            ID of the actor performing the action
        summary:             Brief description of the change
        context:             Context surrounding this revision
    """
    
    # Identity and metadata (required)
    event_identity: str                 # Unique event identifier
    
    timestamp_utc: float                # When event occurred
    revision_number: int = 1            # Revision number after this event
    
    # Change information
    event_type: RevisionEventType = RevisionEventType.UNKNOWN
    
    # Actor information
    actor_type: str = "system"          # e.g., "system", "user", "reasoning"
    actor_id: str = ""                  # Actor identifier
    
    # Change details
    summary: Optional[str] = None       # Brief description of change
    context: Dict[str, Any] = field(default_factory=dict)  # Event context
    
    @property
    def is_valid(self) -> bool:
        """Check if event has valid data."""
        return (
            len(self.event_identity) > 0 and
            self.timestamp_utc > 0.0 and
            self.revision_number >= 1 and
            self.event_type != RevisionEventType.UNKNOWN
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_identity": self.event_identity,
            "timestamp_utc": self.timestamp_utc,
            "revision_number": self.revision_number,
            "event_type": self.event_type.value if hasattr(self.event_type, 'value') else str(self.event_type),
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "summary": self.summary,
            "context": dict(self.context),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RevisionEvent":
        """Create event from dictionary."""
        return cls(
            event_identity=data.get("event_identity", ""),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            revision_number=int(data.get("revision_number", 1)),
            event_type=RevisionEventType(data.get("event_type", "unknown")),
            actor_type=data.get("actor_type", "system"),
            actor_id=data.get("actor_id", ""),
            summary=data.get("summary"),
            context=dict(data.get("context", {})),
        )


# =============================================================================
# REVISION HISTORY - Complete version history
# =============================================================================


@dataclass(frozen=True)
class RevisionHistory:
    """
    Complete revision history for a knowledge artifact.
    
    Maintains the full sequence of revisions from initial creation to current state.
    
    Fields:
        revision_identity:   Unique identifier for this revision history
        initial_event:       The first event (creation) in the history
        events:              All revision events in chronological order
        current_revision:    Current revision number
    """
    
    # Identity and metadata (required)
    revision_identity: str              # Unique ID for this revision history
    
    initial_event: RevisionEvent        # The original creation event
    events: Tuple[RevisionEvent, ...] = field(default_factory=tuple)  # All events
    
    @property
    def current_revision(self) -> int:
        """Get the current revision number."""
        if self.events:
            return self.events[-1].revision_number
        return self.initial_event.revision_number
    
    @property
    def total_revisions(self) -> int:
        """Get total number of revisions (including initial)."""
        return len(self.events) + 1
    
    @classmethod
    def create_initial(
        cls,
        actor_type: str = "system",
        actor_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> "RevisionHistory":
        """
        Create initial revision history with creation event.
        
        Args:
            actor_type: Type of actor creating the artifact
            actor_id: ID of the actor
            context: Creation context (optional)
            
        Returns:
            New RevisionHistory with single initial event
        """
        initial_event = RevisionEvent(
            event_identity=f"event:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            revision_number=1,
            event_type=RevisionEventType.INITIAL,
            actor_type=actor_type,
            actor_id=actor_id,
            context=context or {},
        )
        
        return cls(
            revision_identity=f"revision:{uuid.uuid4().hex[:16]}",
            initial_event=initial_event,
            events=tuple([initial_event]),
        )
    
    def add_revision(
        self,
        event_type: RevisionEventType = RevisionEventType.UPDATE,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        summary: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "RevisionHistory":
        """
        Create a new history with an additional revision.
        
        Args:
            event_type: Type of change
            actor_type: Type of actor (optional)
            actor_id: ID of actor (optional)
            summary: Description of change (optional)
            context: Event context (optional)
            
        Returns:
            New RevisionHistory with added event
        """
        new_event = RevisionEvent(
            event_identity=f"event:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            revision_number=self.current_revision + 1,
            event_type=event_type,
            actor_type=actor_type or self.events[-1].actor_type if self.events else "system",
            actor_id=actor_id or self.events[-1].actor_id if self.events else "",
            summary=summary,
            context=context or {},
        )
        
        return RevisionHistory(
            revision_identity=self.revision_identity,
            initial_event=self.initial_event,
            events=self.events + (new_event,),
        )
    
    def get_revision(self, revision_number: int) -> Optional[RevisionEvent]:
        """
        Get the event at a specific revision number.
        
        Args:
            revision_number: 1-indexed revision number
            
        Returns:
            Event at that revision, or None if invalid
        """
        for event in self.events:
            if event.revision_number == revision_number:
                return event
        if revision_number == 1 and len(self.events) == 0:
            return self.initial_event
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary for serialization."""
        return {
            "revision_identity": self.revision_identity,
            "initial_event": self.initial_event.to_dict(),
            "events": [e.to_dict() for e in self.events],
            "current_revision": self.current_revision,
            "total_revisions": self.total_revisions,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RevisionHistory":
        """Create history from dictionary."""
        events = []
        for event_data in data.get("events", []):
            events.append(RevisionEvent.from_dict(event_data))
        
        return cls(
            revision_identity=data.get("revision_identity", str(uuid.uuid4())),
            initial_event=RevisionEvent.from_dict(data.get("initial_event", {})),
            events=tuple(events),
        )


# =============================================================================
# REVISION MANAGER - Manage revision operations
# =============================================================================


class RevisionManager:
    """
    Manages revision operations for knowledge artifacts.
    
    Provides utilities for working with revision history, including rollback,
    comparison, and merge operations.
    """
    
    def __init__(
        self,
        auto_increment: bool = True,
    ):
        """
        Initialize the manager.
        
        Args:
            auto_increment: Whether to automatically increment revision numbers
        """
        self._auto_increment = auto_increment
    
    def compare_revisions(
        self,
        history: RevisionHistory,
        rev1: int,
        rev2: int,
    ) -> Dict[str, Any]:
        """
        Compare two revisions in a history.
        
        Args:
            history: The revision history to analyze
            rev1: First revision number
            rev2: Second revision number
            
        Returns:
            Dictionary with comparison results
        """
        event1 = history.get_revision(rev1)
        event2 = history.get_revision(rev2)
        
        if not event1 or not event2:
            return {"error": "Invalid revision numbers"}
        
        return {
            "rev1_timestamp": event1.timestamp_utc,
            "rev2_timestamp": event2.timestamp_utc,
            "rev1_type": event1.event_type.value,
            "rev2_type": event2.event_type.value,
            "time_delta_seconds": abs(event2.timestamp_utc - event1.timestamp_utc),
        }
    
    def get_rollback_point(
        self,
        history: RevisionHistory,
        target_revision: int,
    ) -> Optional[RevisionEvent]:
        """
        Get the revision to rollback to.
        
        Args:
            history: The revision history
            target_revision: Target revision number
            
        Returns:
            Event at target revision, or None if not found
        """
        return history.get_revision(target_revision)


__all__ = [
    "RevisionEventType",
    "RevisionEvent",
    "RevisionHistory",
    "RevisionManager",
]