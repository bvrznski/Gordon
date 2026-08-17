# Knowledge Provenance - Phase 6.1
# =================================

"""
Knowledge Provenance: Origin tracking and history for semantic artifacts.

Provenance records the complete lifecycle of a knowledge artifact, including:
    - When and where it was created or modified
    - Who or what actor performed each action
    - The context surrounding each event
    - How changes relate to one another

Provenance enables:
    - Complete auditability of semantic artifacts
    - Revision history tracking
    - Source accountability
    - Trust assessment based on origin
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PROVENANCE EVENTS - Individual history entries
# =============================================================================


class ProvenanceAction(Enum):
    """
    Actions that can be tracked in provenance.
    
    Defines the types of events that modify or reference knowledge artifacts.
    """
    
    CREATE = "create"                      # Initial creation
    UPDATE = "update"                      # Content modification
    REVISION = "revision"                  # New revision (content unchanged)
    VALIDATE = "validate"                  # Validation performed
    ASSERT = "assert"                      # Asserted as knowledge
    BELIEVE = "believe"                    # Accepted as belief
    RETRACT = "retract"                    # Retracted from belief
    MERGE = "merge"                        # Merged with other artifact
    SPLIT = "split"                        # Split into multiple artifacts
    SUPERSEDE = "supersede"                # Replaced by newer version
    DEPRECATE = "deprecate"                # Marked as deprecated
    ARCHIVE = "archive"                    # Archived for storage
    RESTORE = "restore"                    # Restored from archive
    
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProvenanceEvent:
    """
    A single event in the provenance trail.
    
    Records an action taken on a knowledge artifact with full context.
    
    Fields:
        event_identity:     Unique identifier for this event
        timestamp_utc:      When the event occurred
        actor_type:         Type of actor (system, user, reasoning)
        actor_id:           ID of the actor performing the action
        action:             Action that was performed
        context:            Context surrounding this event
    """
    
    # Identity and metadata (required)
    event_identity: str                 # Unique event identifier
    
    timestamp_utc: float                # When event occurred
    actor_type: str = "system"          # e.g., "system", "user", "reasoning"
    actor_id: str = ""                  # Actor identifier
    
    action: ProvenanceAction = ProvenanceAction.UNKNOWN  # Action performed
    context: Dict[str, Any] = field(default_factory=dict)  # Event context
    
    @property
    def is_valid(self) -> bool:
        """Check if event has valid data."""
        return (
            len(self.event_identity) > 0 and
            self.timestamp_utc > 0.0 and
            self.actor_type != "" and
            self.action != ProvenanceAction.UNKNOWN
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_identity": self.event_identity,
            "timestamp_utc": self.timestamp_utc,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "action": self.action.value if hasattr(self.action, 'value') else str(self.action),
            "context": dict(self.context),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceEvent":
        """Create event from dictionary."""
        return cls(
            event_identity=data.get("event_identity", ""),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            actor_type=data.get("actor_type", "system"),
            actor_id=data.get("actor_id", ""),
            action=ProvenanceAction(data.get("action", "unknown")),
            context=dict(data.get("context", {})),
        )


# =============================================================================
# PROVENANCE TRAIL - Complete history chain
# =============================================================================


@dataclass(frozen=True)
class ProvenanceTrail:
    """
    Complete provenance trail for a knowledge artifact.
    
    Maintains the full chronological sequence of events in an artifact's lifecycle.
    
    Fields:
        provenance_identity:  Unique identifier for this provenance record
        origin_event:         The first event (creation) in the trail
        events:               All events in chronological order
        current_state:        Current state after all events
    """
    
    # Identity and metadata (required)
    provenance_identity: str            # Unique ID for this provenance record
    
    origin_event: ProvenanceEvent       # The original creation event
    events: Tuple[ProvenanceEvent, ...] = field(default_factory=tuple)  # All events
    
    @property
    def current_state(self) -> Dict[str, Any]:
        """Get the final state after all provenance events."""
        return self.events[-1].context if self.events else {}
    
    @property
    def event_count(self) -> int:
        """Get total number of events in trail."""
        return len(self.events)
    
    @property
    def is_valid(self) -> bool:
        """Check if trail has valid data."""
        return (
            len(self.provenance_identity) > 0 and
            self.origin_event.is_valid
        )
    
    @classmethod
    def create_initial(
        cls,
        actor_type: str = "system",
        actor_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> "ProvenanceTrail":
        """
        Create initial provenance trail with creation event.
        
        Args:
            actor_type: Type of actor creating the artifact
            actor_id: ID of the actor
            context: Creation context (optional)
            
        Returns:
            New ProvenanceTrail with single creation event
        """
        origin_event = ProvenanceEvent(
            event_identity=f"event:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            actor_type=actor_type,
            actor_id=actor_id,
            action=ProvenanceAction.CREATE,
            context=context or {},
        )
        
        return cls(
            provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
            origin_event=origin_event,
            events=tuple([origin_event]),
        )
    
    def append_event(
        self,
        action: ProvenanceAction,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "ProvenanceTrail":
        """
        Create a new trail with an additional event appended.
        
        Args:
            action: Action to append
            actor_type: Type of actor (optional, defaults to last)
            actor_id: ID of actor (optional, defaults to last)
            context: Event context (optional)
            
        Returns:
            New ProvenanceTrail with added event
        """
        new_event = ProvenanceEvent(
            event_identity=f"event:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            actor_type=actor_type or self.events[-1].actor_type if self.events else "system",
            actor_id=actor_id or self.events[-1].actor_id if self.events else "",
            action=action,
            context=context or {},
        )
        
        return ProvenanceTrail(
            provenance_identity=self.provenance_identity,
            origin_event=self.origin_event,
            events=self.events + (new_event,),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trail to dictionary for serialization."""
        return {
            "provenance_identity": self.provenance_identity,
            "origin_event": self.origin_event.to_dict(),
            "events": [e.to_dict() for e in self.events],
            "event_count": len(self.events),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceTrail":
        """Create trail from dictionary."""
        events = []
        for event_data in data.get("events", []):
            events.append(ProvenanceEvent.from_dict(event_data))
        
        return cls(
            provenance_identity=data.get("provenance_identity", str(uuid.uuid4())),
            origin_event=ProvenanceEvent.from_dict(data.get("origin_event", {})),
            events=tuple(events),
        )


# =============================================================================
# PROVENANCE VALIDATOR
# =============================================================================


class ProvenanceValidator:
    """
    Validates provenance trails for integrity.
    
    Ensures that provenance records are complete, consistent, and trustworthy.
    """
    
    def __init__(
        self,
        require_origin: bool = True,
        require_actor: bool = True,
        min_events: int = 1,
    ):
        """
        Initialize the validator.
        
        Args:
            require_origin: Whether origin event is required
            require_actor: Whether actor information is required
            min_events: Minimum number of events expected
        """
        self._require_origin = require_origin
        self._require_actor = require_actor
        self._min_events = min_events
    
    def validate(self, trail: ProvenanceTrail) -> Tuple[bool, List[str]]:
        """
        Validate a provenance trail.
        
        Args:
            trail: Trail to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Rule 1: Must have valid identity
        if not trail.provenance_identity or len(trail.provenance_identity) == 0:
            issues.append("Missing provenance identity")
        
        # Rule 2: Origin event required and must be create action
        if self._require_origin:
            if trail.origin_event is None:
                issues.append("Missing origin event")
            elif trail.origin_event.action != ProvenanceAction.CREATE:
                issues.append("Origin event must be CREATE action")
        
        # Rule 3: Must have minimum events
        if len(trail.events) < self._min_events:
            issues.append(f"Insufficient events (need at least {self._min_events})")
        
        # Rule 4: Actor information required
        if self._require_actor:
            for event in trail.events:
                if not event.actor_type or event.actor_id == "":
                    issues.append(f"Missing actor info in event {event.event_identity}")
        
        # Rule 5: Events must be in chronological order
        timestamps = [e.timestamp_utc for e in trail.events]
        if timestamps != sorted(timestamps):
            issues.append("Events not in chronological order")
        
        return len(issues) == 0, issues


__all__ = [
    "ProvenanceAction",
    "ProvenanceEvent",
    "ProvenanceTrail",
    "ProvenanceValidator",
]