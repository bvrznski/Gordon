# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Query Models - Semantic Event Queries and Results

This module defines how events can be queried by various criteria.
"""

from dataclasses import dataclass, field
from enum import Enum, unique


@unique
class CognitiveEventQueryKind(Enum):
    """
    Kinds of event queries supported by the CEM.
    
    QUERY KIND LAWS (QUERY-KIND-LAW)
    --------------------------------
    QUERY-KIND-LAW-001: Each query has exactly one kind
    QUERY-KIND-LAW-002: Query kinds are deterministic from parameters
    """
    
    EVENT_LOOKUP = "event_lookup"
    """Look up a single event by identity."""
    
    EVENTS_BY_KIND = "events_by_kind"
    """Get all events of a specific kind."""
    
    EVENTS_BY_NETWORK = "events_by_network"
    """Get all events from a specific network."""
    
    EVENTS_BY_GOAL = "events_by_goal"
    """Get all events related to a specific goal."""
    
    EVENTS_BY_TASK = "events_by_task"
    """Get all events related to a specific task."""
    
    EVENTS_BY_EPISODE = "events_by_episode"
    """Get all events in a specific episode."""
    
    EVENTS_BY_DOMAIN = "events_by_domain"
    """Get all events from a specific domain."""
    
    EVENTS_BY_TIMELINE = "events_by_timeline"
    """Get all events from a timeline."""
    
    EVENTS_BY_CORRELATION = "events_by_correlation"
    """Get all correlated events."""
    
    EVENTS_BY_CAUSATION = "events_by_causation"
    """Get all events in a causation chain."""
    
    EVENTS_DURING_INTERVAL = "events_during_interval"
    """Get events during a semantic time interval."""
    
    RELATED_EVENTS = "related_events"
    """Get events related to a given event."""


@dataclass(frozen=True)
class CognitiveEventQuery:
    """
    Query for cognitive events.
    
    Queries are read-only operations that return matching events without
    modifying any state.
    
    QUERY LAWS (QUERY-LAW)
    ----------------------
    QUERY-LAW-001: Queries remain read-only
    QUERY-LAW-002: Query scope is explicit
    QUERY-LAW-003: Queries preserve findings and limitations
    """
    
    # Query kind
    _query_kind: CognitiveEventQueryKind
    
    # Query parameters (filters, ranges, etc.)
    _parameters: dict = field(default_factory=dict)
    
    # Limit on result count
    _limit: int | None = None
    
    # Offset for pagination
    _offset: int = 0
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    @property
    def query_kind(self) -> CognitiveEventQueryKind:
        """Get the query kind."""
        return self._query_kind
    
    @property
    def parameters(self) -> dict:
        """Get the query parameters."""
        return self._parameters
    
    @property
    def limit(self) -> int | None:
        """Get the result limit, if any."""
        return self._limit
    
    @property
    def offset(self) -> int:
        """Get the pagination offset."""
        return self._offset
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {
            "query_kind": self._query_kind.value,
            "parameters": dict(self._parameters),
            "offset": self._offset,
            "provenance": dict(self._provenance),
        }
        if self._limit is not None:
            result["limit"] = self._limit
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEventQuery":
        """
        Create a query from a dictionary.
        
        Args:
            data: Dictionary with query data
            
        Returns:
            New CognitiveEventQuery instance
        """
        kind_value = data.get("query_kind", "event_lookup")
        try:
            query_kind = CognitiveEventQueryKind(kind_value)
        except ValueError:
            query_kind = CognitiveEventQueryKind.EVENT_LOOKUP
        
        return cls(
            _query_kind=query_kind,
            _parameters=dict(data.get("parameters", {})),
            _limit=data.get("limit"),
            _offset=data.get("offset", 0),
            _provenance=dict(data.get("provenance", {})),
        )


@dataclass(frozen=True)
class CognitiveEventQueryResult:
    """
    Result of an event query.
    
    QUERY RESULT LAWS (QUERY-RESULT-LAW)
    ------------------------------------
    QUERY-RESULT-LAW-001: Query results preserve findings
    QUERY-RESULT-LAW-002: Query results preserve limitations
    QUERY-RESULT-LAW-003: Results are derived from query execution
    """
    
    # Reference to the original query
    _query_reference: str
    
    # Matched event identities
    _matched_events: tuple[str, ...] = field(default_factory=tuple)
    
    # Matched timeline identities
    _matched_timelines: tuple[str, ...] = field(default_factory=tuple)
    
    # Matched episode identities  
    _matched_episodes: tuple[str, ...] = field(default_factory=tuple)
    
    # Findings from the query
    _findings: dict = field(default_factory=dict)
    
    # Limitations of the query results
    _limitations: dict = field(default_factory=dict)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    @property
    def query_reference(self) -> str:
        """Get the reference to the original query."""
        return self._query_reference
    
    @property
    def matched_events(self) -> tuple[str, ...]:
        """Get the matched event identities."""
        return self._matched_events
    
    @property
    def matched_timelines(self) -> tuple[str, ...]:
        """Get the matched timeline identities."""
        return self._matched_timelines
    
    @property
    def matched_episodes(self) -> tuple[str, ...]:
        """Get the matched episode identities."""
        return self._matched_episodes
    
    @property
    def findings(self) -> dict:
        """Get the findings from the query."""
        return self._findings
    
    @property
    def limitations(self) -> dict:
        """Get the limitations of the results."""
        return self._limitations
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def event_count(self) -> int:
        """Get the number of matched events."""
        return len(self._matched_events)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "query_reference": self._query_reference,
            "matched_events": list(self._matched_events),
            "matched_timelines": list(self._matched_timelines),
            "matched_episodes": list(self._matched_episodes),
            "findings": dict(self._findings),
            "limitations": dict(self._limitations),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEventQueryResult":
        """
        Create a query result from a dictionary.
        
        Args:
            data: Dictionary with query result data
            
        Returns:
            New CognitiveEventQueryResult instance
        """
        return cls(
            _query_reference=data["query_reference"],
            _matched_events=tuple(data.get("matched_events", [])),
            _matched_timelines=tuple(data.get("matched_timelines", [])),
            _matched_episodes=tuple(data.get("matched_episodes", [])),
            _findings=dict(data.get("findings", {})),
            _limitations=dict(data.get("limitations", {})),
            _provenance=dict(data.get("provenance", {})),
        )