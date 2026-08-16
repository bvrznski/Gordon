# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Revision Models - Tracking Event Revisions and Lineage

This module defines how event revisions work in the Cognitive Event Model.
Revisions are new events that supersede previous ones, never mutating existing events.
"""

from dataclasses import dataclass, field
from enum import Enum, unique


@unique
class RevisionKind(Enum):
    """
    Kinds of revisions that can occur to an event.
    
    REVISION KIND LAWS (REV-KIND-LAW)
    ---------------------------------
    REV-KIND-LAW-001: Each revision has exactly one kind
    REV-KKind-LAW-002: Revisions are immutable once published
    REV-KInd-LAW-003: Revision reasons must be explicit
    """
    
    INITIAL = "initial"
    """The first version of an event."""
    
    CORRECTION = "correction"
    """Revision that corrects errors in the original event."""
    
    SUPERSESSION = "supersession"
    """Event has been fully replaced by a new version."""
    
    REVALIDATION = "revalidation"
    """Event has been revalidated with updated confidence."""
    
    RECOVERY = "recovery"
    """Event was recovered from archival or corruption."""
    
    UNKNOWN = "unknown"
    """Unknown revision kind."""


@dataclass(frozen=True)
class CognitiveEventRevision:
    """
    Model of an event revision.
    
    Revisions are immutable. When an event needs correction, a new
    revision event is created that references the parent revision.
    
    REVISION LAWS (REV-LAW)
    -----------------------
    REV-LAW-001: Published events never mutate
    REV-LAW-002: Corrections create new revisions
    REV-LAW-003: Revision lineage must be complete
    REV-LAW-004: Supersession is explicit
    REV-LAW-005: Historical revisions remain inspectable
    REV-LAW-006: Replacement reasons are explicit
    """
    
    # Identity of this revision
    _revision_identity: str
    
    # Identity of the event being revised
    _event_identity: str
    
    # Parent revision (if any)
    _parent_revision: str | None
    
    # Kind of revision
    _revision_kind: RevisionKind
    
    # Reason for replacement/correction
    _replacement_reason: str
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate revision components."""
        if not self._revision_identity:
            raise ValueError("Revision identity cannot be empty")
        
        if not self._event_identity:
            raise ValueError("Event identity cannot be empty")
        
        if not self._replacement_reason:
            raise ValueError("Replacement reason cannot be empty")
    
    @property
    def revision_identity(self) -> str:
        """Get the revision's unique identity."""
        return self._revision_identity
    
    @property
    def event_identity(self) -> str:
        """Get the event being revised."""
        return self._event_identity
    
    @property
    def parent_revision(self) -> str | None:
        """Get the parent revision, if any."""
        return self._parent_revision
    
    @property
    def revision_kind(self) -> RevisionKind:
        """Get the revision kind."""
        return self._revision_kind
    
    @property
    def replacement_reason(self) -> str:
        """Get the reason for replacement/correction."""
        return self._replacement_reason
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def is_initial(self) -> bool:
        """Check if this is an initial revision (no parent)."""
        return self._parent_revision is None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {
            "revision_identity": self._revision_identity,
            "event_identity": self._event_identity,
            "revision_kind": self._revision_kind.value,
            "replacement_reason": self._replacement_reason,
            "provenance": dict(self._provenance),
        }
        if self._parent_revision is not None:
            result["parent_revision"] = self._parent_revision
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEventRevision":
        """
        Create a revision from a dictionary.
        
        Args:
            data: Dictionary with revision data
            
        Returns:
            New CognitiveEventRevision instance
        """
        return cls(
            _revision_identity=data["revision_identity"],
            _event_identity=data["event_identity"],
            _parent_revision=data.get("parent_revision"),
            _revision_kind=RevisionKind(data.get("revision_kind", "initial")),
            _replacement_reason=data["replacement_reason"],
            _provenance=dict(data.get("provenance", {})),
        )
