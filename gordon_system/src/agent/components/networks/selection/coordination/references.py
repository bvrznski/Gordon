# Gordon Cognitive Architecture - Phase 4.5.10
# ===========================================

"""
Coordination References module.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ActionSelectionCoordinationResponseIdentity:
    """
    Unique identifier for a coordination response.
    
    Each external subsystem response has one stable identity that can be referenced
    by acknowledgement and integration records.
    """
    
    value: str = ""
    """Unique response identifier."""
    
    @classmethod
    def from_value(cls, value: str) -> ActionSelectionCoordinationResponseIdentity:
        """Create a response identity from an explicit string value."""
        return cls(value=value)


@dataclass(frozen=True)
class ActionSelectionCoordinationResponseRevision:
    """
    Revision number for a coordination response artifact.
    
    Monotonically increasing revision tracking preserves history while allowing
    updates to responses.
    """
    
    value: int = 1
    """Monotonically increasing revision number."""
    
    @classmethod
    def initial(cls) -> ActionSelectionCoordinationResponseRevision:
        """Create the initial (first) coordination response revision."""
        return cls(value=1)
    
    @classmethod
    def next(cls, current: ActionSelectionCoordinationResponseRevision) -> ActionSelectionCoordinationResponseRevision:
        """Get the next revision number."""
        return cls(value=current.value + 1)


# =============================================================================
# COORDINATION REFERENCES
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionCoordinationReference:
    """
    Reference to a specific coordination artifact revision.
    
    Combines identity and revision to reference an exact coordination artifact.
    """
    
    identity: str = ""
    """The coordination identity being referenced."""
    
    revision: int = 1
    """The revision of that identity."""
    
    @classmethod
    def from_values(cls, identity: str, revision: int) -> ActionSelectionCoordinationReference:
        """Create a reference from explicit values."""
        return cls(identity=identity, revision=revision)