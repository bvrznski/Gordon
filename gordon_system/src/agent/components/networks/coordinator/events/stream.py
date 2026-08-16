# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Stream Models - Event Streams and Global Stream Aggregation

This module defines how events are organized into streams per network,
and how all streams combine to form the global event timeline.
"""

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class CognitiveEventStreamIdentity:
    """
    Unique identity for an event stream.
    
    Each cognitive network has its own event stream. Streams are
    identified by their producing network and semantic scope.
    """
    
    _identity: str
    _producing_network: str
    _semantic_scope: str = "default"
    
    @property
    def identity(self) -> str:
        """Get the stream identity."""
        return self._identity
    
    @property
    def producing_network(self) -> str:
        """Get the network that produces this stream."""
        return self._producing_network
    
    @property
    def semantic_scope(self) -> str:
        """Get the semantic scope."""
        return self._semantic_scope


@dataclass(frozen=True)
class CognitiveEventStream:
    """
    Immutable collection of events from a single cognitive network.
    
    Every network has exactly one logical Event Stream. Streams preserve
    event ordering and are immutable - new events create new streams,
    not modified versions.
    
    STREAM LAWS (STREAM-LAW)
    ------------------------
    STREAM-LAW-001: Each network has one logical Event Stream
    STREAM-LAW-002: Streams preserve event ordering
    STREAM-LAW-003: Streams are immutable
    STREAM-LAW-004: Stream revisions preserve lineage
    STREAM-LAW-005: Streams preserve provenance
    """
    
    # Stream identity
    _stream_identity: str
    
    # Network that produces events in this stream
    _producing_network: str
    
    # Ordered collection of events (tuple for immutability)
    _events: tuple[str, ...] = field(default_factory=tuple)
    
    # Current revision number
    _current_revision: int = 1
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate stream components."""
        if not self._stream_identity:
            raise ValueError("Stream identity cannot be empty")
        
        if not self._producing_network:
            raise ValueError("Producing network cannot be empty")
    
    @property
    def stream_identity(self) -> str:
        """Get the stream's unique identity."""
        return self._stream_identity
    
    @property
    def producing_network(self) -> str:
        """Get the network that produces events in this stream."""
        return self._producing_network
    
    @property
    def events(self) -> tuple[str, ...]:
        """Get the ordered collection of event identities."""
        return self._events
    
    @property
    def current_revision(self) -> int:
        """Get the current revision number."""
        return self._current_revision
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def event_count(self) -> int:
        """Get the number of events in this stream."""
        return len(self._events)
    
    def is_empty(self) -> bool:
        """Check if this stream has no events."""
        return len(self._events) == 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "stream_identity": self._stream_identity,
            "producing_network": self._producing_network,
            "events": list(self._events),
            "current_revision": self._current_revision,
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEventStream":
        """
        Create a stream from a dictionary.
        
        Args:
            data: Dictionary with stream data
            
        Returns:
            New CognitiveEventStream instance
        """
        return cls(
            _stream_identity=data["stream_identity"],
            _producing_network=data["producing_network"],
            _events=tuple(data.get("events", [])),
            _current_revision=data.get("current_revision", 1),
            _provenance=dict(data.get("provenance", {})),
        )
    
    def with_events(self, new_events: Iterable[str]) -> "CognitiveEventStream":
        """
        Create a new stream with additional events.
        
        This is the immutable way to add events - creates a new stream
        instance rather than modifying the existing one.
        
        Args:
            new_events: Collection of event identities to add
            
        Returns:
            New CognitiveEventStream with combined events
        """
        all_events = tuple(self._events) + tuple(new_events)
        return CognitiveEventStream(
            _stream_identity=self._stream_identity,
            _producing_network=self._producing_network,
            _events=all_events,
            _current_revision=self._current_revision + 1,
            _provenance=self._provenance.copy(),
        )


@dataclass(frozen=True)
class GlobalCognitiveEventStream:
    """
    Aggregate of all event streams from all networks.
    
    The global stream merges all network-specific streams by semantic
    ordering to create a complete timeline of cognition.
    
    GLOBAL STREAM LAWS (GLOBAL-STREAM-LAW)
    --------------------------------------
    GLOBAL-STREAM-LAW-001: Global stream combines all network streams
    GLOBAL-STREAM-LAW-002: Merging preserves semantic ordering
    GLOBAL-STREAM-LAW-003: Global stream is immutable
    GLOBAL-STREAM-LAW-004: Historical global streams remain queryable
    """
    
    # Stream identity (global)
    _stream_identity: str = "global_cognitive_stream"
    
    # Map of network names to their streams
    _network_streams: dict[str, CognitiveEventStream] = field(
        default_factory=dict
    )
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def stream_count(self) -> int:
        """Get the number of network streams in this global stream."""
        return len(self._network_streams)
    
    def event_count(self) -> int:
        """Get the total number of events across all streams."""
        return sum(stream.event_count() for stream in self._network_streams.values())
    
    def get_network_stream(self, network: str) -> CognitiveEventStream | None:
        """
        Get the event stream for a specific network.
        
        Args:
            network: Network identifier
            
        Returns:
            The stream for that network, or None if not found
        """
        return self._network_streams.get(network)
    
    def add_network_stream(
        self, stream: CognitiveEventStream
    ) -> "GlobalCognitiveEventStream":
        """
        Create a new global stream with an additional network stream.
        
        Args:
            stream: Network stream to add
            
        Returns:
            New GlobalCognitiveEventStream with added stream
        """
        new_streams = dict(self._network_streams)
        new_streams[stream.producing_network] = stream
        return GlobalCognitiveEventStream(
            _stream_identity=self._stream_identity,
            _network_streams=new_streams,
            _provenance=self._provenance.copy(),
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "stream_identity": self._stream_identity,
            "network_streams": {
                network: stream.to_dict()
                for network, stream in self._network_streams.items()
            },
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GlobalCognitiveEventStream":
        """
        Create a global stream from a dictionary.
        
        Args:
            data: Dictionary with global stream data
            
        Returns:
            New GlobalCognitiveEventStream instance
        """
        network_streams = {}
        for network, stream_data in data.get("network_streams", {}).items():
            network_streams[network] = CognitiveEventStream.from_dict(stream_data)
        
        return cls(
            _stream_identity=data.get("stream_identity", "global_cognitive_stream"),
            _network_streams=network_streams,
            _provenance=dict(data.get("provenance", {})),
        )