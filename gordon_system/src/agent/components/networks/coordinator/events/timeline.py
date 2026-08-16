# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Cognitive Timeline Models - Temporal Organization of Events

This module defines how events are organized into timelines for semantic
ordering and querying.
"""

from dataclasses import dataclass, field
from enum import Enum, unique


@unique
class CognitiveTimelineScope(Enum):
    """
    Scopes for organizing event timelines.
    
    TIMELINE SCOPE LAWS (SCOPE-LAW)
    -------------------------------
    SCOPE-LAW-001: Every timeline has exactly one scope
    SCOPE-LAW-002: Events may belong to multiple timelines
    SCOPE-LAW-003: Scope is determined by semantic content
    """
    
    GLOBAL = "global"
    """All events across all networks."""
    
    NETWORK = "network"
    """Events from a specific network."""
    
    GOAL = "goal"
    """Events related to a specific goal."""
    
    TASK = "task"
    """Events related to a specific task."""
    
    EPISODE = "episode"
    """Events forming a coherent cognitive episode."""
    
    DOMAIN = "domain"
    """Domain-specific events."""
    
    REFLECTION = "reflection"
    """Reflection session events."""
    
    LEARNING = "learning"
    """Learning episode events."""


@dataclass(frozen=True)
class CognitiveTimelineIdentity:
    """
    Unique identity for a timeline.
    """
    
    _identity: str
    _scope: str
    
    @property
    def identity(self) -> str:
        """Get the timeline identity."""
        return self._identity
    
    @property
    def scope(self) -> str:
        """Get the timeline scope."""
        return self._scope


@dataclass(frozen=True)
class CognitiveTimeline:
    """
    Timeline of events organized by semantic ordering.
    
    Timelines organize events into a coherent temporal sequence without
    owning the events themselves. Events can belong to multiple timelines.
    
    TIMELINE LAWS (TIMELINE-LAW)
    ----------------------------
    TIMELINE-LAW-001: Timelines organize without owning events
    TIMELINE-LAW-002: Events may belong to multiple timelines
    TIMELINE-LAW-003: Timeline scope is explicit
    TIMELINE-LAW-004: Ordering preserves semantic time
    """
    
    # Timeline identity
    _timeline_identity: str
    
    # Scope of this timeline
    _timeline_scope: str
    
    # Ordered list of event identities (sorted by semantic time)
    _ordered_events: tuple[str, ...] = field(default_factory=tuple)
    
    # Interval events with their start/end references
    _interval_events: dict[str, tuple[str, str]] = field(default_factory=dict)
    
    # Active/open intervals (ongoing without known end)
    _active_intervals: set[str] = field(default_factory=set)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate timeline components."""
        if not self._timeline_identity:
            raise ValueError("Timeline identity cannot be empty")
        
        if not self._timeline_scope:
            raise ValueError("Timeline scope cannot be empty")
    
    @property
    def timeline_identity(self) -> str:
        """Get the timeline's unique identity."""
        return self._timeline_identity
    
    @property
    def timeline_scope(self) -> str:
        """Get the timeline scope."""
        return self._timeline_scope
    
    @property
    def ordered_events(self) -> tuple[str, ...]:
        """Get the ordered list of event identities."""
        return self._ordered_events
    
    @property
    def interval_events(self) -> dict[str, tuple[str, str]]:
        """Get interval events with their start/end references."""
        return self._interval_events
    
    @property
    def active_intervals(self) -> set[str]:
        """Get active/open intervals."""
        return self._active_intervals
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def event_count(self) -> int:
        """Get the number of events in this timeline."""
        return len(self._ordered_events)
    
    def is_empty(self) -> bool:
        """Check if this timeline has no events."""
        return len(self._ordered_events) == 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "timeline_identity": self._timeline_identity,
            "timeline_scope": self._timeline_scope,
            "ordered_events": list(self._ordered_events),
            "interval_events": dict(self._interval_events),
            "active_intervals": list(self._active_intervals),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveTimeline":
        """
        Create a timeline from a dictionary.
        
        Args:
            data: Dictionary with timeline data
            
        Returns:
            New CognitiveTimeline instance
        """
        return cls(
            _timeline_identity=data["timeline_identity"],
            _timeline_scope=data["timeline_scope"],
            _ordered_events=tuple(data.get("ordered_events", [])),
            _interval_events=dict(data.get("interval_events", {})),
            _active_intervals=set(data.get("active_intervals", [])),
            _provenance=dict(data.get("provenance", {})),
        )