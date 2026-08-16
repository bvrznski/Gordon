# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Lineage Models - Tracking Revision History

This module defines how event revisions form lineage chains, tracking
the complete history of all revisions for an event.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EventLineage:
    """
    Complete revision lineage for a single event.
    
    Lineage tracks the entire history of revisions, including the original
    event and all subsequent corrections and supersessions.
    
    LINEAGE LAWS (LINEAGE-LAW)
    --------------------------
    LINEAGE-LAW-001: Lineage contains complete revision chain
    LINEAGE-LAW-002: Supersession chain is explicit
    LINEAGE-LAW-003: Replacement reasons are preserved
    """
    
    # Base event identity (first version)
    _base_event_identity: str
    
    # Ordered revision history (oldest first, newest last)
    _revision_history: tuple[str, ...] = field(default_factory=tuple)
    
    # Supersession relationships (newer -> older for each supersession)
    _supersession_chain: dict[str, str] = field(default_factory=dict)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate lineage components."""
        if not self._base_event_identity:
            raise ValueError("Base event identity cannot be empty")
    
    @property
    def base_event_identity(self) -> str:
        """Get the base (first) event identity."""
        return self._base_event_identity
    
    @property
    def revision_history(self) -> tuple[str, ...]:
        """Get the ordered revision history."""
        return self._revision_history
    
    @property
    def supersession_chain(self) -> dict[str, str]:
        """Get the supersession chain (newer -> older)."""
        return self._supersession_chain
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def revision_count(self) -> int:
        """Get the total number of revisions in this lineage."""
        return len(self._revision_history)
    
    def is_active(self, event_identity: str) -> bool:
        """
        Check if an event is still active (not superseded).
        
        Args:
            event_identity: Event identity to check
            
        Returns:
            True if not superseded, False otherwise
        """
        return event_identity not in self._supersession_chain
    
    def get_current_revision(self) -> str | None:
        """Get the current/latest revision."""
        if self._revision_history:
            return self._revision_history[-1]
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "base_event_identity": self._base_event_identity,
            "revision_history": list(self._revision_history),
            "supersession_chain": dict(self._supersession_chain),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventLineage":
        """
        Create a lineage from a dictionary.
        
        Args:
            data: Dictionary with lineage data
            
        Returns:
            New EventLineage instance
        """
        return cls(
            _base_event_identity=data["base_event_identity"],
            _revision_history=tuple(data.get("revision_history", [])),
            _supersession_chain=dict(data.get("supersession_chain", {})),
            _provenance=dict(data.get("provenance", {})),
        )