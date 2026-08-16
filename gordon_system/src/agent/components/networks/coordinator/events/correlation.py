# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Correlation Models - Grouping Related Events by Context

This module defines how events can be correlated based on shared context,
even if they don't have causal relationships.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EventCorrelationIdentity:
    """
    Unique identity for an event correlation.
    """
    
    _identity: str
    _originating_context: str
    
    @property
    def identity(self) -> str:
        """Get the correlation identity."""
        return self._identity
    
    @property
    def originating_context(self) -> str:
        """Get the originating context."""
        return self._originating_context


@dataclass(frozen=True)
class EventCorrelation:
    """
    Correlation between related events.
    
    Correlations group events that share semantic relationships without
    implying causation. Correlated events may be from different sources
    but are semantically linked.
    
    CORRELATION LAWS (CORR-LAW)
    ---------------------------
    CORR-LAW-001: Related events share correlation identities
    CORR-LAW-002: Correlation never implies causation
    CORR-LAW-003: Correlation groups are immutable
    """
    
    # Correlation identity
    _correlation_identity: str
    
    # Participating event identities
    _participating_events: tuple[str, ...] = field(default_factory=tuple)
    
    # Originating context that produced this correlation
    _originating_context: str = "default"
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate correlation components."""
        if not self._correlation_identity:
            raise ValueError("Correlation identity cannot be empty")
        
        if not self._originating_context:
            raise ValueError("Originating context cannot be empty")
    
    @property
    def correlation_identity(self) -> str:
        """Get the correlation's unique identity."""
        return self._correlation_identity
    
    @property
    def participating_events(self) -> tuple[str, ...]:
        """Get events in this correlation."""
        return self._participating_events
    
    @property
    def originating_context(self) -> str:
        """Get the originating context."""
        return self._originating_context
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def event_count(self) -> int:
        """Get the number of correlated events."""
        return len(self._participating_events)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "correlation_identity": self._correlation_identity,
            "participating_events": list(self._participating_events),
            "originating_context": self._originating_context,
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventCorrelation":
        """
        Create a correlation from a dictionary.
        
        Args:
            data: Dictionary with correlation data
            
        Returns:
            New EventCorrelation instance
        """
        return cls(
            _correlation_identity=data["correlation_identity"],
            _participating_events=tuple(data.get("participating_events", [])),
            _originating_context=data.get("originating_context", "default"),
            _provenance=dict(data.get("provenance", {})),
        )