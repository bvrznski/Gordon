# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Causation Models - Explicit Causal Relationships Between Events

This module defines how events can have explicit causal relationships,
with all causation being explicitly recorded rather than inferred.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EventCausation:
    """
    Explicit causal relationship between events.
    
    Every causal link is represented as an EventCausation with clear
    references to the causing and caused events.
    
    CAUSATION LAWS (CAUS-LAW)
    -------------------------
    CAUS-LAW-001: Causation always references explicit events
    CAUS-LAW-002: Implicit causation is prohibited
    CAUS-LAW-003: Causation preserves semantic direction
    """
    
    # Identity of the causing event
    _causing_event: str
    
    # Identity of the caused event
    _caused_event: str
    
    # Kind of causal relationship
    _relationship_kind: str = "direct"
    
    # Confidence in this causation (0.0 - 1.0)
    _confidence: float = 1.0
    
    # Uncertainty in this causation (0.0 - 1.0)
    _uncertainty: float = 0.0
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate causation components."""
        if not self._causing_event:
            raise ValueError("Causing event identity cannot be empty")
        
        if not self._caused_event:
            raise ValueError("Caused event identity cannot be empty")
        
        if self._causing_event == self._caused_event:
            raise ValueError(
                "Event cannot cause itself "
                f"(got {self._causing_event})"
            )
        
        if not (0.0 <= self._confidence <= 1.0):
            raise ValueError(f"Confidence must be 0.0-1.0, got {self._confidence}")
        
        if not (0.0 <= self._uncertainty <= 1.0):
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {self._uncertainty}")
    
    @property
    def causing_event(self) -> str:
        """Get the identity of the causing event."""
        return self._causing_event
    
    @property
    def caused_event(self) -> str:
        """Get the identity of the caused event."""
        return self._caused_event
    
    @property
    def relationship_kind(self) -> str:
        """Get the kind of causal relationship."""
        return self._relationship_kind
    
    @property
    def confidence(self) -> float:
        """Get confidence in this causation (0.0 - 1.0)."""
        return self._confidence
    
    @property
    def uncertainty(self) -> float:
        """Get uncertainty in this causation (0.0 - 1.0)."""
        return self._uncertainty
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "causing_event": self._causing_event,
            "caused_event": self._caused_event,
            "relationship_kind": self._relationship_kind,
            "confidence": self._confidence,
            "uncertainty": self._uncertainty,
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventCausation":
        """
        Create a causation from a dictionary.
        
        Args:
            data: Dictionary with causation data
            
        Returns:
            New EventCausation instance
        """
        return cls(
            _causing_event=data["causing_event"],
            _caused_event=data["caused_event"],
            _relationship_kind=data.get("relationship_kind", "direct"),
            _confidence=float(data.get("confidence", 1.0)),
            _uncertainty=float(data.get("uncertainty", 0.0)),
            _provenance=dict(data.get("provenance", {})),
        )


class CausationChain:
    """
    Chain of causal relationships between events.
    
    A causation chain represents a sequence of cause-effect relationships
    that link multiple events together.
    """
    
    def __init__(self):
        """Initialize an empty causation chain."""
        self._causations: list[EventCausation] = []
    
    @property
    def causations(self) -> tuple[EventCausation, ...]:
        """Get all causations in this chain."""
        return tuple(self._causations)
    
    def add_causation(self, causation: EventCausation) -> None:
        """
        Add a causation to the chain.
        
        Args:
            causation: The EventCausation to add
        """
        self._causations.append(causation)
    
    def get_events_in_chain(self) -> list[str]:
        """
        Get all unique event identities in this causation chain.
        
        Returns:
            List of event identities, in order from first cause to final effect
        """
        events: list[str] = []
        seen: set[str] = set()
        
        for c in self._causations:
            if c.causing_event not in seen:
                events.append(c.causing_event)
                seen.add(c.causing_event)
            if c.caused_event not in seen:
                events.append(c.caused_event)
                seen.add(c.caused_event)
        
        return events
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "causations": [c.to_dict() for c in self._causations],
        }