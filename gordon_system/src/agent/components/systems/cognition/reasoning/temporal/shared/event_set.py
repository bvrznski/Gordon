# Event Set - Phase 7.8
# ======================

"""
Canonical Event Set.

An event set defines participating events, temporal scope, reference clocks,
granularity, and constraints for temporal reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, FrozenSet
from enum import Enum, auto


class EventKind(Enum):
    """Kinds of events."""
    
    PERCEPTION = "perception"               # Events from sensory input
    MEMORY = "memory"                       # Events from memory retrieval
    EXECUTION = "execution"                 # Events from action execution
    PLANNING = "planning"                   # Events from planning processes
    EXTERNAL_OBSERVATION = "external_observation"  # Events from external sources
    SIMULATION = "simulation"               # Events from simulation
    ABSTRACT = "abstract"                   # Abstract conceptual events


class TemporalScope(Enum):
    """Temporal scope classifications."""
    
    INSTANTANEOUS = "instantaneous"         # Point events (no duration)
    BRIEF = "brief"                         # Short duration events
    DETAILED = "detailed"                   # Detailed temporal coverage
    EXTENDED = "extended"                   # Extended time periods
    LONG_TERM = "long_term"                 # Long-term event patterns


@dataclass(frozen=True)
class TemporalEvent:
    """
    Event in the temporal reasoning system.
    
    Events remain explicit - they are not inferred or derived.
    
    Every event possesses:
        - Explicit identity (immutable, persistent)
        - Timestamp (when it occurred)
        - Duration (how long it lasted)
        - Type (what kind of event)
        - Provenance (where it came from)
    """
    
    # Identity
    event_id: str                           # Unique event identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Temporal properties
    timestamp_utc: float                    # When did the event occur?
    duration_seconds: Optional[float] = None  # How long did it last? (None for instantaneous)
    
    # Event classification
    event_kind: EventKind = EventKind.ABSTRACT
    
    # Content and metadata
    event_name: str = "unknown"             # Human-readable name
    event_description: str = ""             # Detailed description
    event_context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    # Provenance
    source_event_id: Optional[str] = None   # If derived from another event
    origin_system: str = "unknown"          # Where did the event originate?
    
    @property
    def end_timestamp(self) -> float:
        """Calculate end timestamp if duration is known."""
        return self.timestamp_utc + (self.duration_seconds or 0.0)
    
    @property
    def is_instantaneous(self) -> bool:
        """Check if this is an instantaneous event."""
        return self.duration_seconds is None or self.duration_seconds == 0.0
    
    def contains_timepoint(self, timepoint: float) -> bool:
        """Check if a timepoint falls within this event's interval."""
        if self.is_instantaneous:
            # For instantaneous events, check within small tolerance
            return abs(timepoint - self.timestamp_utc) < 0.001
        return self.timestamp_utc <= timepoint <= self.end_timestamp
    
    def overlaps_with(self, other: TemporalEvent) -> bool:
        """Check if this event overlaps with another."""
        return not (self.end_timestamp <= other.timestamp_utc or 
                    other.end_timestamp <= self.timestamp_utc)
    
    def strictly_before(self, other: TemporalEvent) -> bool:
        """Check if this event strictly precedes another."""
        return self.end_timestamp < other.timestamp_utc
    
    def strictly_after(self, other: TemporalEvent) -> bool:
        """Check if this event strictly follows another."""
        return other.strictly_before(self)
    
    def starts_at_or_before(self, other: TemporalEvent) -> bool:
        """Check if this event starts at or before the other."""
        return self.timestamp_utc <= other.timestamp_utc
    
    def finishes_at_or_after(self, other: TemporalEvent) -> bool:
        """Check if this event finishes at or after the other."""
        return self.end_timestamp >= other.end_timestamp


@dataclass(frozen=True)
class EventSet:
    """
    Set of events for temporal reasoning.
    
    An event set defines:
        - Participating events
        - Temporal scope
        - Reference frame
        - Granularity
        - Constraints
    
    Event Sets remain immutable during reasoning.
    """
    
    # Identity
    event_set_id: str                       # Unique event set identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Participating events
    participating_events: Tuple[TemporalEvent, ...]
    
    # Temporal scope
    temporal_scope: TemporalScope = TemporalScope.DETAILED
    
    # Reference frame for ordering
    reference_frame: Optional[str] = None   # e.g., "wall_clock", "monotonic_system_time"
    
    # Constraints on events
    event_constraints: Tuple[str, ...] = ()  # Explicit constraints on participating events
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_event_set_id: Optional[str] = None   # If derived from another set
    origin_context: str = "unknown"             # Where did the event set originate?
    
    @property
    def event_count(self) -> int:
        """Return the number of events in this set."""
        return len(self.participating_events)
    
    @property
    def has_events(self) -> bool:
        """Check if the event set is non-empty."""
        return len(self.participating_events) > 0
    
    @property
    def earliest_timestamp(self) -> Optional[float]:
        """Return the earliest timestamp in this set, or None if empty."""
        if not self.participating_events:
            return None
        return min(e.timestamp_utc for e in self.participating_events)
    
    @property
    def latest_timestamp(self) -> Optional[float]:
        """Return the latest timestamp in this set, or None if empty."""
        if not self.participating_events:
            return None
        return max(e.end_timestamp for e in self.participating_events)
    
    @property
    def time_span_seconds(self) -> float:
        """Return the total time span of events in seconds."""
        earliest = self.earliest_timestamp
        latest = self.latest_timestamp
        if earliest is None or latest is None:
            return 0.0
        return latest - earliest
    
    @property
    def event_ids(self) -> Tuple[str, ...]:
        """Return tuple of all event IDs in this set."""
        return tuple(e.event_id for e in self.participating_events)
    
    def get_event_by_id(self, event_id: str) -> Optional[TemporalEvent]:
        """Get an event by its ID."""
        for event in self.participating_events:
            if event.event_id == event_id:
                return event
        return None
    
    def filter_by_kind(self, kind: EventKind) -> Tuple[TemporalEvent, ...]:
        """Filter events by kind."""
        return tuple(e for e in self.participating_events if e.event_kind == kind)
    
    def filter_by_timepoint(self, timepoint: float) -> Tuple[TemporalEvent, ...]:
        """Get events that contain a given timepoint."""
        return tuple(e for e in self.participating_events if e.contains_timepoint(timepoint))
    
    def get_ordered_events(self) -> Tuple[TemporalEvent, ...]:
        """Return events ordered by start timestamp."""
        return tuple(sorted(self.participating_events, key=lambda e: e.timestamp_utc))
    
    def find_conflicts(self, tolerance_seconds: float = 0.001) -> List[Tuple[str, str]]:
        """
        Find pairs of events that conflict in their temporal ordering.
        
        Returns list of (event_id_1, event_id_2) tuples representing conflicting pairs.
        """
        conflicts = []
        ordered = self.get_ordered_events()
        
        for i, event1 in enumerate(ordered):
            for event2 in ordered[i+1:]:
                if not event1.overlaps_with(event2):
                    # Check for ordering constraints
                    if event1.duration_seconds and event2.duration_seconds:
                        if (event1.timestamp_utc == event2.timestamp_utc and 
                            abs(event1.duration_seconds - event2.duration_seconds) < tolerance_seconds):
                            conflicts.append((event1.event_id, event2.event_id))
        
        return conflicts
    
    def to_interval(self) -> Optional[TemporalEvent]:
        """Create an interval that encompasses all events in this set."""
        if not self.participating_events:
            return None
        
        earliest = min(e.timestamp_utc for e in self.participating_events)
        latest = max(e.end_timestamp for e in self.participating_events)
        
        return TemporalEvent(
            event_id=f"interval:{uuid.uuid4().hex[:16]}",
            semantic_identity=self.semantic_identity,
            timestamp_utc=earliest,
            duration_seconds=latest - earliest,
            event_kind=EventKind.ABSTRACT,
            event_name="event_set_interval",
            event_description="Interval encompassing all events in this set",
        )


@dataclass(frozen=True)
class EventSetIdentity:
    """
    Immutable identity for an event set.
    
    Allows replay and verification of temporal reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Set context
    set_number: int = 1                       # For repeated sets
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, set_number: int = 1) -> EventSetIdentity:
        """Create a new event set identity."""
        return cls(
            semantic_identity=semantic_identity,
            set_number=set_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalEvent",
    "EventSet",
    "EventSetIdentity",
    "EventKind",
    "TemporalScope",
]