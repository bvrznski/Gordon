# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Duration Enumeration and Models - Temporal Characteristics of Events

This module defines how events span semantic time, from instantaneous points
to extended intervals.
"""

from enum import Enum, unique


@unique
class EventDurationKind(Enum):
    """
    Canonical enumeration of event duration types.
    
    Events can be:
    - INSTANTANEOUS: Single point in semantic time (most events)
    - INTERVAL: Has defined start and end events
    - OPEN_INTERVAL: Ongoing interval without known endpoint
    
    DURATION LAWS
    -------------
    DUR-LAW-001: Every event has exactly one duration kind
    DUR-LAW-002: Duration is determined by semantic content
    DUR-LAW-003: Interval events have explicit start/end references
    DUR-LAW-004: Duration does not affect event validity
    """
    
    INSTANTANEOUS = "instantaneous"
    """Event occurs at a single point in semantic time.
    Examples:
    - DECISION_SELECTED
    - REWARD_OBSERVED
    - GOAL_COMPLETED
    - OBSERVATION_RECORDED"""
    
    INTERVAL = "interval"
    """Event spans an interval with defined start and end events.
    Examples:
    - PLANNING_STARTED/COMPLETED pair
    - REFLECTION_STARTED/COMPLETED pair
    - TASK_CREATED/COMPLETED pair"""
    
    OPEN_INTERVAL = "open_interval"
    """Event is an ongoing interval without known endpoint.
    Examples:
    - Current goal (not yet completed)
    - Active task (not yet finished)
    - Ongoing learning episode"""


@unique
class SemanticTimeReference(Enum):
    """
    Reference points for semantic time ordering.
    
    Semantic time is the canonical temporal ordering in CEM, independent
    of wall-clock time. It represents the logical order of cognitive events.
    """
    
    COGNITIVE_CYCLE_START = "cognitive_cycle_start"
    """Start of a cognitive processing cycle."""
    
    COGNITIVE_CYCLE_END = "cognitive_cycle_end"
    """End of a cognitive processing cycle."""
    
    GOAL_CREATION = "goal_creation"
    """Point when the current goal was established."""
    
    DECISION_MADE = "decision_made"
    """Point when the current decision was selected."""
    
    OBSERVATION_RECEIVED = "observation_received"
    """Point when external observation was registered."""
    
    REFLECTION_COMPLETE = "reflection_complete"
    """Point when current reflection session completed."""


class EventIntervalReference:
    """
    Reference to an interval event's start and end points.
    
    Interval events are defined by their boundaries in semantic time.
    This model stores the references needed to reconstruct the interval.
    
    INTERVAL LAWS
    -------------
    INT-LAW-001: Intervals have explicit start and end references
    INT-LAW-002: Start must precede end in semantic ordering
    INT-LAW-003: Interval duration is deterministic from boundaries
    """
    
    def __init__(
        self,
        start_event_identity: str,
        end_event_identity: str,
        interval_id: str | None = None,
    ):
        """
        Initialize an event interval reference.
        
        Args:
            start_event_identity: Identity of the start event
            end_event_identity: Identity of the end event  
            interval_id: Optional identifier for this interval
            
        Raises:
            ValueError: If start and end are identical (invalid interval)
        """
        if start_event_identity == end_event_identity:
            raise ValueError(
                "Start and end event identities must be different "
                f"(got same identity: {start_event_identity})"
            )
        
        self._start_event_identity = start_event_identity
        self._end_event_identity = end_event_identity
        self._interval_id = interval_id
    
    @property
    def start_event_identity(self) -> str:
        """Get the identity of the start event."""
        return self._start_event_identity
    
    @property
    def end_event_identity(self) -> str:
        """Get the identity of the end event."""
        return self._end_event_identity
    
    @property
    def interval_id(self) -> str | None:
        """Get the interval identifier, if any."""
        return self._interval_id
    
    def is_valid_interval(self) -> bool:
        """
        Check if this represents a valid interval.
        
        Returns:
            True if start != end and both identities are present
        """
        return (
            self._start_event_identity
            and self._end_event_identity
            and self._start_event_identity != self._end_event_identity
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {
            "start_event_identity": self._start_event_identity,
            "end_event_identity": self._end_event_identity,
        }
        if self._interval_id is not None:
            result["interval_id"] = self._interval_id
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventIntervalReference":
        """
        Create an EventIntervalReference from a dictionary.
        
        Args:
            data: Dictionary with interval reference data
            
        Returns:
            New EventIntervalReference instance
        """
        return cls(
            start_event_identity=data["start_event_identity"],
            end_event_identity=data["end_event_identity"],
            interval_id=data.get("interval_id"),
        )
    
    def __repr__(self) -> str:
        return (
            f"EventIntervalReference(start={self._start_event_identity!r}, "
            f"end={self._end_event_identity!r}, id={self._interval_id!r})"
        )


class EventDuration:
    """
    Complete model for an event's temporal characteristics.
    
    Events can be instantaneous points or interval-spanning events.
    This model captures all duration-related information.
    
    DURATION MODEL LAWS
    -------------------
    DUR-MODEL-LAW-001: Duration is immutable once set
    DUR-MODEL-LAW-002: Interval duration has explicit start/end
    DUR-MODEL-LAW-003: Instantaneous events have no interval data
    """
    
    def __init__(
        self,
        duration_kind: EventDurationKind,
        semantic_time: str | None = None,
        interval_reference: EventIntervalReference | None = None,
    ):
        """
        Initialize event duration model.
        
        Args:
            duration_kind: The kind of duration (instantaneous or interval)
            semantic_time: Semantic time reference for instantaneous events
            interval_reference: Interval boundaries for interval events
            
        Raises:
            ValueError: If parameters are inconsistent
        """
        if duration_kind == EventDurationKind.INSTANTANEOUS:
            if interval_reference is not None:
                raise ValueError(
                    "Instantaneous events cannot have interval references"
                )
        elif duration_kind in (
            EventDurationKind.INTERVAL,
            EventDurationKind.OPEN_INTERVAL,
        ):
            if interval_reference is None:
                raise ValueError(
                    f"Interval event kind requires interval reference, got {duration_kind}"
                )
        
        self._duration_kind = duration_kind
        self._semantic_time = semantic_time
        self._interval_reference = interval_reference
    
    @property
    def duration_kind(self) -> EventDurationKind:
        """Get the duration kind."""
        return self._duration_kind
    
    @property
    def semantic_time(self) -> str | None:
        """Get the semantic time reference for instantaneous events."""
        return self._semantic_time
    
    @property
    def interval_reference(self) -> EventIntervalReference | None:
        """Get the interval reference for interval events."""
        return self._interval_reference
    
    def is_instantaneous(self) -> bool:
        """Check if this event is instantaneous."""
        return self._duration_kind == EventDurationKind.INSTANTANEOUS
    
    def is_interval(self) -> bool:
        """Check if this event spans an interval."""
        return self._duration_kind in (
            EventDurationKind.INTERVAL,
            EventDurationKind.OPEN_INTERVAL,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {
            "duration_kind": self._duration_kind.value,
        }
        if self._semantic_time is not None:
            result["semantic_time"] = self._semantic_time
        if self._interval_reference is not None:
            result["interval_reference"] = self._interval_reference.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventDuration":
        """
        Create an EventDuration from a dictionary.
        
        Args:
            data: Dictionary with duration data
            
        Returns:
            New EventDuration instance
        """
        duration_kind = EventDurationKind(data.get("duration_kind", "instantaneous"))
        
        interval_ref = None
        if "interval_reference" in data:
            interval_ref = EventIntervalReference.from_dict(
                data["interval_reference"]
            )
        
        return cls(
            duration_kind=duration_kind,
            semantic_time=data.get("semantic_time"),
            interval_reference=interval_ref,
        )
    
    def __repr__(self) -> str:
        return (
            f"EventDuration(kind={self._duration_kind.value}, "
            f"time={self._semantic_time!r}, interval={self._interval_reference!r})"
        )