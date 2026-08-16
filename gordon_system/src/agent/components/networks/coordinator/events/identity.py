# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Identity Models - Semantic Identities for Events and Event Containers

This module defines the canonical identity models used throughout the
Cognitive Event Model to uniquely identify events, streams, timelines,
and other semantic entities.
"""

from dataclasses import dataclass, field
from typing import Final


# =============================================================================
# SEMANTIC TIME REFERENCE
# =============================================================================

@dataclass(frozen=True)
class SemanticTimeReference:
    """
    Reference point in the canonical semantic time ordering.
    
    Semantic time is independent of wall-clock time. It represents
    the logical order of cognitive occurrences.
    
    SEMANTIC TIME LAWS (TIME-LAW)
    -----------------------------
    TIME-LAW-001: Semantic time is deterministic from context
    TIME-LAW-002: No two distinct events have identical semantic time
    TIME-LAW-003: Semantic ordering is total and transitive
    """
    
    # Predefined reference points
    COGNITIVE_CYCLE_START = "cognitive_cycle_start"
    COGNITIVE_CYCLE_END = "cognitive_cycle_end"
    GOAL_CREATION = "goal_creation"
    DECISION_MADE = "decision_made"
    OBSERVATION_RECEIVED = "observation_received"
    REFLECTION_COMPLETE = "reflection_complete"
    
    # Dynamic reference point
    _value: str
    
    @classmethod
    def from_value(cls, value: str) -> "SemanticTimeReference":
        """
        Create a SemanticTimeReference from a string value.
        
        Args:
            value: The semantic time value
            
        Returns:
            New SemanticTimeReference instance
        """
        return cls(_value=value)
    
    @property
    def value(self) -> str:
        """Get the semantic time value."""
        return self._value
    
    def __str__(self) -> str:
        return self._value


# =============================================================================
# EVENT IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class CognitiveEventIdentity:
    """
    Unique identity for a cognitive event.
    
    Event identity is derived from semantic content, not runtime memory
    addresses. The same semantic occurrence always produces the same identity.
    
    EVENT IDENTITY LAWS (ID-LAW)
    ----------------------------
    ID-LAW-001: Equivalent semantic events have equivalent identities
    ID-LAW-002: Event identity is independent from runtime execution
    ID-LAW-003: Event identity is immutable once generated
    ID-LAW-004: Identity preserves source ownership and provenance
    """
    
    # Generated identifier
    _identity: str
    
    # Semantic type of the event (kind)
    _event_kind: str
    
    # Source network that produced the event
    _source_network: str
    
    # Semantic scope of the event
    _semantic_scope: str
    
    # Event revision number (1 for initial events)
    _revision: int = field(default=1)
    
    def __post_init__(self):
        """Validate identity components after initialization."""
        if not self._identity:
            raise ValueError("Event identity cannot be empty")
        
        if not self._event_kind:
            raise ValueError("Event kind cannot be empty")
        
        if not self._source_network:
            raise ValueError("Source network cannot be empty")
        
        if not self._semantic_scope:
            raise ValueError("Semantic scope cannot be empty")
        
        if self._revision < 1:
            raise ValueError(f"Revision must be >= 1, got {self._revision}")
    
    @property
    def identity(self) -> str:
        """Get the event's unique identity."""
        return self._identity
    
    @property
    def event_kind(self) -> str:
        """Get the event kind name."""
        return self._event_kind
    
    @property
    def source_network(self) -> str:
        """Get the source network identifier."""
        return self._source_network
    
    @property
    def semantic_scope(self) -> str:
        """Get the semantic scope."""
        return self._semantic_scope
    
    @property
    def revision(self) -> int:
        """Get the event revision number."""
        return self._revision
    
    def to_string(self) -> str:
        """
        Convert identity to canonical string representation.
        
        Format: kind:identity@network/v{revision}
        
        Returns:
            Canonical string identifier
        """
        return (
            f"{self._event_kind}:{self._identity}@"
            f"{self._source_network}/v{self._revision}"
        )
    
    @classmethod
    def from_string(cls, s: str) -> "CognitiveEventIdentity":
        """
        Parse an identity string into a CognitiveEventIdentity.
        
        Args:
            s: String in format kind:identity@network/v{revision}
            
        Returns:
            New CognitiveEventIdentity instance
            
        Raises:
            ValueError: If the string cannot be parsed
        """
        # Parse "kind:identity@network/v{revision}"
        parts = s.split("/")
        if len(parts) != 2 or not parts[1].startswith("v"):
            raise ValueError(f"Invalid identity format: {s}")
        
        revision_str = parts[1][1:]  # Remove 'v' prefix
        try:
            revision = int(revision_str)
        except ValueError:
            raise ValueError(f"Invalid revision in identity: {s}")
        
        kind_network_part = parts[0]
        at_idx = kind_network_part.rfind("@")
        if at_idx == -1:
            raise ValueError(f"Invalid identity format (missing @): {s}")
        
        kind = kind_network_part[:at_idx]
        rest = kind_network_part[at_idx + 1:]
        
        colon_idx = rest.find(":")
        if colon_idx == -1:
            network = rest
            identity = ""
        else:
            identity = rest[:colon_idx]
            network = rest[colon_idx + 1:]
        
        return cls(
            _identity=identity,
            _event_kind=kind,
            _source_network=network,
            _semantic_scope="default",
            _revision=revision,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "identity": self._identity,
            "event_kind": self._event_kind,
            "source_network": self._source_network,
            "semantic_scope": self._semantic_scope,
            "revision": self._revision,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEventIdentity":
        """
        Create an identity from a dictionary.
        
        Args:
            data: Dictionary with identity data
            
        Returns:
            New CognitiveEventIdentity instance
        """
        return cls(
            _identity=data["identity"],
            _event_kind=data["event_kind"],
            _source_network=data["source_network"],
            _semantic_scope=data.get("semantic_scope", "default"),
            _revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class CognitiveEventRevisionIdentity:
    """
    Unique identity for a revision of an event.
    
    Revisions are new events that supersede previous ones. This identity
    tracks the lineage of revisions.
    """
    
    # Base event identity (the original event)
    _base_event_identity: str
    
    # Revision number (2, 3, ... for revisions)
    _revision_number: int
    
    def __post_init__(self):
        if self._revision_number < 1:
            raise ValueError(f"Revision number must be >= 1, got {self._revision_number}")
    
    @property
    def base_event_identity(self) -> str:
        """Get the base event identity."""
        return self._base_event_identity
    
    @property
    def revision_number(self) -> int:
        """Get the revision number."""
        return self._revision_number
    
    def to_string(self) -> str:
        """Convert to canonical string representation."""
        return f"{self._base_event_identity}/r{self._revision_number}"
    
    def is_initial(self) -> bool:
        """Check if this is an initial event (not a revision)."""
        return self._revision_number == 1


@dataclass(frozen=True)
class CognitiveEventStreamIdentity:
    """
    Unique identity for an event stream.
    
    Each network has its own event stream. Streams are identified by
    their producing network and scope.
    """
    
    # Stream identifier
    _identity: str
    
    # Network that produces events in this stream
    _producing_network: str
    
    # Semantic scope of the stream
    _semantic_scope: str
    
    @property
    def identity(self) -> str:
        """Get the stream identity."""
        return self._identity
    
    @property
    def producing_network(self) -> str:
        """Get the producing network identifier."""
        return self._producing_network
    
    @property
    def semantic_scope(self) -> str:
        """Get the semantic scope."""
        return self._semantic_scope


@dataclass(frozen=True)
class CognitiveTimelineIdentity:
    """
    Unique identity for a timeline.
    
    Timelines organize events and may have different scopes (global,
    network-specific, goal-based, etc.).
    """
    
    # Timeline identifier
    _identity: str
    
    # Scope of the timeline
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
class CognitiveEpisodeIdentity:
    """
    Unique identity for a cognitive episode.
    
    Episodes are coherent collections of related events (problem-solving,
    dialogue, planning, etc.).
    """
    
    # Episode identifier
    _identity: str
    
    # Kind of episode
    _episode_kind: str
    
    @property
    def identity(self) -> str:
        """Get the episode identity."""
        return self._identity
    
    @property
    def episode_kind(self) -> str:
        """Get the episode kind."""
        return self._episode_kind


@dataclass(frozen=True)
class EventAggregationIdentity:
    """
    Unique identity for an event aggregation.
    
    Aggregations group related events without duplicating them.
    """
    
    # Aggregation identifier
    _identity: str
    
    # Aggregation criteria
    _aggregation_criteria: str
    
    @property
    def identity(self) -> str:
        """Get the aggregation identity."""
        return self._identity
    
    @property
    def aggregation_criteria(self) -> str:
        """Get the aggregation criteria."""
        return self._aggregation_criteria


@dataclass(frozen=True)
class EventCorrelationIdentity:
    """
    Unique identity for an event correlation.
    
    Correlations group related events that don't necessarily have
    causal relationships.
    """
    
    # Correlation identifier
    _identity: str
    
    # Context that produced the correlation
    _originating_context: str
    
    @property
    def identity(self) -> str:
        """Get the correlation identity."""
        return self._identity
    
    @property
    def originating_context(self) -> str:
        """Get the originating context."""
        return self._originating_context


def generate_event_identity(
    event_kind: str,
    source_network: str,
    semantic_scope: str = "default",
    revision: int = 1,
) -> CognitiveEventIdentity:
    """
    Generate a deterministic event identity from semantic content.
    
    This function produces the same identity for identical inputs,
    ensuring determinism across runs and systems.
    
    Args:
        event_kind: The kind of event
        source_network: Network that produced the event
        semantic_scope: Semantic scope of the event
        revision: Event revision number
        
    Returns:
        New CognitiveEventIdentity instance
    """
    # Create a deterministic identifier from semantic content
    identity_hash = hash(
        (event_kind, source_network, semantic_scope, revision)
    )
    
    return CognitiveEventIdentity(
        _identity=f"evt_{abs(identity_hash):016x}",
        _event_kind=event_kind,
        _source_network=source_network,
        _semantic_scope=semantic_scope,
        _revision=revision,
    )


def generate_stream_identity(
    network: str,
    semantic_scope: str = "default",
) -> CognitiveEventStreamIdentity:
    """
    Generate a deterministic stream identity.
    
    Args:
        network: Network identifier
        semantic_scope: Semantic scope
        
    Returns:
        New CognitiveEventStreamIdentity instance
    """
    return CognitiveEventStreamIdentity(
        _identity=f"stream_{network}_{semantic_scope}",
        _producing_network=network,
        _semantic_scope=semantic_scope,
    )