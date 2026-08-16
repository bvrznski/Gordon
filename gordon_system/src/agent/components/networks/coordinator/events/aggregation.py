# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Aggregation Models - Grouping Events Without Duplication

This module defines how events can be aggregated for analysis, querying,
and episode reconstruction without duplicating the underlying events.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EventAggregationIdentity:
    """
    Unique identity for an event aggregation.
    """
    
    _identity: str
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
class EventAggregation:
    """
    Aggregation of events by common criteria.
    
    Aggregations group related events without duplicating them. They serve
    as views or indexes over existing events.
    
    AGGREGATION LAWS (AGG-LAW)
    --------------------------
    AGG-LAW-001: Aggregations group existing events
    AGG-LAW-002: Aggregations never duplicate events
    AGG-LAW-003: Aggregation criteria are explicit
    """
    
    # Aggregation identity
    _aggregation_identity: str
    
    # Events in this aggregation (by reference/identity)
    _event_references: tuple[str, ...] = field(default_factory=tuple)
    
    # Aggregation criteria
    _criteria: dict = field(default_factory=dict)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate aggregation components."""
        if not self._aggregation_identity:
            raise ValueError("Aggregation identity cannot be empty")
    
    @property
    def aggregation_identity(self) -> str:
        """Get the aggregation's unique identity."""
        return self._aggregation_identity
    
    @property
    def event_references(self) -> tuple[str, ...]:
        """Get event references in this aggregation."""
        return self._event_references
    
    @property
    def criteria(self) -> dict:
        """Get the aggregation criteria."""
        return self._criteria
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def event_count(self) -> int:
        """Get the number of events in this aggregation."""
        return len(self._event_references)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "aggregation_identity": self._aggregation_identity,
            "event_references": list(self._event_references),
            "criteria": dict(self._criteria),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventAggregation":
        """
        Create an aggregation from a dictionary.
        
        Args:
            data: Dictionary with aggregation data
            
        Returns:
            New EventAggregation instance
        """
        return cls(
            _aggregation_identity=data["aggregation_identity"],
            _event_references=tuple(data.get("event_references", [])),
            _criteria=dict(data.get("criteria", {})),
            _provenance=dict(data.get("provenance", {})),
        )