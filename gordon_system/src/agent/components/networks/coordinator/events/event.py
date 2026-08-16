# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Cognitive Event Model - Core Event Class and Construction

This module defines the canonical CognitiveEvent model that represents
a single cognitive occurrence in Gordon's semantic history.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CognitiveEvent:
    """
    Immutable representation of a cognitive event.
    
    Every meaningful cognitive occurrence produces one Cognitive Event.
    Events are immutable; revisions create new events rather than modifying
    existing ones.
    
    EVENT LAWS (EVENT-LAW)
    ----------------------
    EVENT-LAW-001: Every event has stable semantic identity
    EVENT-LAW-002: Events are independent from runtime execution
    EVENT-LAW-003: Published events are immutable
    EVENT-LAW-004: Revisions create new events (not mutations)
    EVENT-LAW-005: Historical events remain inspectable
    """
    
    # Identity of this event
    _identity: str
    
    # Revision information
    _revision: int
    
    # Event kind/type
    _event_kind: str
    
    # Reference to the payload (not the payload itself - ownership stays with source)
    _payload_reference: str
    
    # Source network that produced this event
    _source_network: str
    
    # Semantic scope of the event
    _semantic_scope: str
    
    # Importance level for downstream consumers
    _importance: str = "normal"
    
    # Duration type (instantaneous or interval)
    _duration_kind: str = "instantaneous"
    
    # Event status in its lifecycle
    _status: str = "occurred"
    
    # Confidence in the event's validity (0.0 - 1.0)
    _confidence: float = 1.0
    
    # Uncertainty measure (0.0 - 1.0, higher = more uncertain)
    _uncertainty: float = 0.0
    
    # Semantic time reference for ordering
    _semantic_time: str | None = None
    
    # Correlation identity (if any)
    _correlation: str | None = None
    
    # Causation references (list of causing event identities)
    _causation: tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate event components after initialization."""
        if not self._identity:
            raise ValueError("Event identity cannot be empty")
        
        if not self._event_kind:
            raise ValueError("Event kind cannot be empty")
        
        if not self._source_network:
            raise ValueError("Source network cannot be empty")
        
        if not self._payload_reference:
            raise ValueError("Payload reference cannot be empty")
        
        if self._revision < 1:
            raise ValueError(f"Revision must be >= 1, got {self._revision}")
        
        if not (0.0 <= self._confidence <= 1.0):
            raise ValueError(f"Confidence must be 0.0-1.0, got {self._confidence}")
        
        if not (0.0 <= self._uncertainty <= 1.0):
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {self._uncertainty}")
        
        if self._confidence + self._uncertainty > 1.0:
            raise ValueError(
                f"Confidence + uncertainty cannot exceed 1.0 "
                f"(got confidence={self._confidence}, uncertainty={self._uncertainty})"
            )
    
    @property
    def identity(self) -> str:
        """Get the event's unique identity."""
        return self._identity
    
    @property
    def revision(self) -> int:
        """Get the event revision number."""
        return self._revision
    
    @property
    def event_kind(self) -> str:
        """Get the event kind/type."""
        return self._event_kind
    
    @property
    def payload_reference(self) -> str:
        """Get a reference to the semantic payload (not the payload itself)."""
        return self._payload_reference
    
    @property
    def source_network(self) -> str:
        """Get the source network identifier."""
        return self._source_network
    
    @property
    def semantic_scope(self) -> str:
        """Get the semantic scope."""
        return self._semantic_scope
    
    @property
    def importance(self) -> str:
        """Get the event importance level."""
        return self._importance
    
    @property
    def duration_kind(self) -> str:
        """Get the duration kind."""
        return self._duration_kind
    
    @property
    def status(self) -> str:
        """Get the current event status."""
        return self._status
    
    @property
    def confidence(self) -> float:
        """Get the confidence level (0.0 - 1.0)."""
        return self._confidence
    
    @property
    def uncertainty(self) -> float:
        """Get the uncertainty measure (0.0 - 1.0)."""
        return self._uncertainty
    
    @property
    def semantic_time(self) -> str | None:
        """Get the semantic time reference."""
        return self._semantic_time
    
    @property
    def correlation(self) -> str | None:
        """Get the correlation identity, if any."""
        return self._correlation
    
    @property
    def causation(self) -> tuple[str, ...]:
        """Get the causation references (list of causing event identities)."""
        return self._causation
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def is_initial_revision(self) -> bool:
        """Check if this is an initial event (not a revision)."""
        return self._revision == 1
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "identity": self._identity,
            "revision": self._revision,
            "event_kind": self._event_kind,
            "payload_reference": self._payload_reference,
            "source_network": self._source_network,
            "semantic_scope": self._semantic_scope,
            "importance": self._importance,
            "duration_kind": self._duration_kind,
            "status": self._status,
            "confidence": self._confidence,
            "uncertainty": self._uncertainty,
            "semantic_time": self._semantic_time,
            "correlation": self._correlation,
            "causation": list(self._causation),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEvent":
        """
        Create an event from a dictionary.
        
        Args:
            data: Dictionary with event data
            
        Returns:
            New CognitiveEvent instance
        """
        return cls(
            _identity=data["identity"],
            _revision=data.get("revision", 1),
            _event_kind=data["event_kind"],
            _payload_reference=data["payload_reference"],
            _source_network=data["source_network"],
            _semantic_scope=data.get("semantic_scope", "default"),
            _importance=data.get("importance", "normal"),
            _duration_kind=data.get("duration_kind", "instantaneous"),
            _status=data.get("status", "occurred"),
            _confidence=float(data.get("confidence", 1.0)),
            _uncertainty=float(data.get("uncertainty", 0.0)),
            _semantic_time=data.get("semantic_time"),
            _correlation=data.get("correlation"),
            _causation=tuple(data.get("causation", [])),
            _provenance=dict(data.get("provenance", {})),
        )
    
    def __repr__(self) -> str:
        return (
            f"CognitiveEvent("
            f"kind={self._event_kind!r}, "
            f"id={self._identity[:16]!s}..., "
            f"network={self._source_network!r}, "
            f"status={self._status!r})"
        )


class CognitiveEventBuilder:
    """
    Builder pattern for constructing CognitiveEvents.
    
    Provides a fluent API for incrementally building event instances
    with validation at construction time.
    
    BUILDER LAWS
    ------------
    BUILD-LAW-001: All required fields must be set before construction
    BUILD-LAW-002: Validation occurs only at build() time
    BUILD-LAW-003: Builder is immutable during construction
    """
    
    def __init__(self):
        """Initialize a new event builder."""
        self._identity: str | None = None
        self._revision: int = 1
        self._event_kind: str | None = None
        self._payload_reference: str | None = None
        self._source_network: str | None = None
        self._semantic_scope: str = "default"
        self._importance: str = "normal"
        self._duration_kind: str = "instantaneous"
        self._status: str = "occurred"
        self._confidence: float = 1.0
        self._uncertainty: float = 0.0
        self._semantic_time: str | None = None
        self._correlation: str | None = None
        self._causation: list[str] = []
        self._provenance: dict = {}
    
    def set_identity(self, identity: str) -> "CognitiveEventBuilder":
        """Set the event identity."""
        if not identity:
            raise ValueError("Identity cannot be empty")
        self._identity = identity
        return self
    
    def set_revision(self, revision: int) -> "CognitiveEventBuilder":
        """Set the event revision number."""
        if revision < 1:
            raise ValueError(f"Revision must be >= 1, got {revision}")
        self._revision = revision
        return self
    
    def set_event_kind(self, kind: str) -> "CognitiveEventBuilder":
        """Set the event kind/type."""
        if not kind:
            raise ValueError("Event kind cannot be empty")
        self._event_kind = kind
        return self
    
    def set_payload_reference(self, ref: str) -> "CognitiveEventBuilder":
        """Set the payload reference (not the payload itself)."""
        if not ref:
            raise ValueError("Payload reference cannot be empty")
        self._payload_reference = ref
        return self
    
    def set_source_network(self, network: str) -> "CognitiveEventBuilder":
        """Set the source network identifier."""
        if not network:
            raise ValueError("Source network cannot be empty")
        self._source_network = network
        return self
    
    def set_semantic_scope(self, scope: str) -> "CognitiveEventBuilder":
        """Set the semantic scope."""
        self._semantic_scope = scope
        return self
    
    def set_importance(self, importance: str) -> "CognitiveEventBuilder":
        """Set the event importance level."""
        valid_levels = ("critical", "high", "normal", "low", "background")
        if importance not in valid_levels:
            raise ValueError(
                f"Invalid importance level '{importance}'. "
                f"Must be one of: {valid_levels}"
            )
        self._importance = importance
        return self
    
    def set_duration_kind(self, kind: str) -> "CognitiveEventBuilder":
        """Set the duration kind."""
        valid_kinds = ("instantaneous", "interval", "open_interval")
        if kind not in valid_kinds:
            raise ValueError(
                f"Invalid duration kind '{kind}'. "
                f"Must be one of: {valid_kinds}"
            )
        self._duration_kind = kind
        return self
    
    def set_status(self, status: str) -> "CognitiveEventBuilder":
        """Set the event status."""
        valid_statuses = (
            "occurred", "validated", "published",
            "superseded", "historical", "invalid", "archived"
        )
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{status}'. "
                f"Must be one of: {valid_statuses}"
            )
        self._status = status
        return self
    
    def set_confidence(self, confidence: float) -> "CognitiveEventBuilder":
        """Set the confidence level (0.0 - 1.0)."""
        if not (0.0 <= confidence <= 1.0):
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "CognitiveEventBuilder":
        """Set the uncertainty measure (0.0 - 1.0)."""
        if not (0.0 <= uncertainty <= 1.0):
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_semantic_time(self, time: str) -> "CognitiveEventBuilder":
        """Set the semantic time reference."""
        self._semantic_time = time
        return self
    
    def add_correlation(self, correlation_id: str) -> "CognitiveEventBuilder":
        """Add a correlation identity."""
        self._correlation = correlation_id
        return self
    
    def add_causation(self, causing_event_identity: str) -> "CognitiveEventBuilder":
        """Add a causation reference to a causing event."""
        if not causing_event_identity:
            raise ValueError("Causation event identity cannot be empty")
        self._causation.append(causing_event_identity)
        return self
    
    def set_provenance(self, provenance: dict) -> "CognitiveEventBuilder":
        """Set the provenance information."""
        self._provenance = provenance.copy()
        return self
    
    def build(self) -> CognitiveEvent:
        """
        Build and validate the event.
        
        Returns:
            New CognitiveEvent instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if self._identity is None:
            raise ValueError("Identity must be set")
        
        if self._event_kind is None:
            raise ValueError("Event kind must be set")
        
        if self._source_network is None:
            raise ValueError("Source network must be set")
        
        if self._payload_reference is None:
            raise ValueError("Payload reference must be set")
        
        return CognitiveEvent(
            _identity=self._identity,
            _revision=self._revision,
            _event_kind=self._event_kind,
            _payload_reference=self._payload_reference,
            _source_network=self._source_network,
            _semantic_scope=self._semantic_scope,
            _importance=self._importance,
            _duration_kind=self._duration_kind,
            _status=self._status,
            _confidence=self._confidence,
            _uncertainty=self._uncertainty,
            _semantic_time=self._semantic_time,
            _correlation=self._correlation,
            _causation=tuple(self._causation),
            _provenance=self._provenance,
        )