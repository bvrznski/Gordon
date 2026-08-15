# Gordon Executive Decision Revision - Phase 4.4.10A
# =====================================================

"""
Decision Revision System.

This module defines revision management for Executive Decisions.
Revisions represent updated semantic understanding of the same decision identity.


ARCHITECTURAL LAWS
==================

E-007: Identity survives revisions.
E-008: Revisions never overwrite history.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionRevision:
    """
    Record of a revision within an Executive Decision's lifecycle.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - identity_id: The decision identity this revision belongs to
        - revision_number: Sequential number for ordering
        - timestamp_utc: When this revision was created
        
    Example:
        >>> revision = DecisionRevision(
        ...     identity_id="decision_abc123",
        ...     revision_number=1,
        ... )
    """
    
    identity_id: str = field(default="")
    """The decision identity this revision belongs to."""
    
    revision_number: int = 1
    """Sequential number for ordering revisions."""
    
    timestamp_utc: float = 0.0
    """Timestamp when this revision was created."""
    
    @property
    def is_revision(self) -> bool:
        """Return True for all revision records."""
        return True
    
    @classmethod
    def initial(cls, identity_id: str) -> "DecisionRevision":
        """Create an initial revision for a decision identity."""
        return cls(identity_id=identity_id, revision_number=1)