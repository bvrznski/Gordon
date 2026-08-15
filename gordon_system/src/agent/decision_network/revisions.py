# Gordon Cognitive Architecture - Phase 4.5.1
# ===========================================

"""
Action Revision Model

An ActionRevision represents a semantic update to an Action Identity. It never
overwrites prior revisions; it extends them.

ACTION-SEM-INV-006: Revisions are immutable.
ACTION-SEM-INV-007: Revision lineage is acyclic.
ACTION-SEM-INV-008: In-place Action revision is prohibited.
ACTION-SEM-INV-009: Conceptually different operations require different Action identities.
ACTION-SEM-INV-010: Terminated or permanently invalidated Actions do not receive ordinary new revisions.

A valid Action Revision may change:

    - Bounded scope
    - Target revision (if target mutability matters)
    - Preconditions
    - Non-authoritative preferences
    - Expected effects
    - Predicted side effects
    - Resource estimates
    - Capability requirements
    - Evidence
    - Justification
    - Expiry
    - Validation metadata

A new Action Identity is required when:

    - The primary operation changes fundamentally
    - The principal target changes materially
    - The intended effect changes fundamentally
    - The authority class changes fundamentally
    - The risk class changes fundamentally
    - The Action changes from observational to mutating
    - The Action changes from reversible to fundamentally irreversible
    - Conceptual continuity is lost

REVISION RULES:

    1. Reference exactly one Action Identity
    2. Reference its parent revision where applicable
    3. Preserve immutable history
    4. Expose changed fields
    5. Expose retained fields where required
    6. Preserve authority lineage
    7. Preserve ownership
    8. Preserve provenance
    9. Preserve semantic continuity
    10. Remain deeply immutable

Forbidden:
    action.target = new_target
    action.revision += 1

Required conceptual pattern:

    ActionRevisionProposal → validated ActionRevision → new immutable Action artifact
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ActionRevisionReference:
    """
    Reference to a specific revision of an Action.
    
    This is a lightweight reference used when you need to point to a revision
    without embedding the full revision data.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # The action identity being referenced
    identity_id: str = field(default="")
    """The ActionIdentity that this revision belongs to."""
    
    # Revision number (1 for initial, increments for subsequent)
    revision_number: int = 1
    """Sequential revision number within the identity's history."""
    
    @property
    def id(self) -> str:
        """Return fully qualified revision identifier."""
        return f"{self.identity_id}:v{self.revision_number}"
    
    def __str__(self) -> str:
        return self.id
    
    def __repr__(self) -> str:
        return f"ActionRevisionReference(id='{self.id}')"


@dataclass(frozen=True)
class ActionRevisionMetadata:
    """
    Metadata about an Action Revision.
    
    This contains administrative information about the revision, such as
    who proposed it, when, and why. It does NOT contain semantic content.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Revision identification
    identity_id: str = field(default="")
    """ActionIdentity this revision belongs to."""
    
    revision_number: int = 1
    """Sequential number within the identity's history."""
    
    parent_revision_id: Optional[str] = None
    """Parent revision if this is not the initial revision."""
    
    # Revision tracking
    created_at_semantic_time: float = field(default=0.0)
    """Semantic time when revision was created (externally supplied)."""
    
    revision_kind: str = field(default="standard")
    """Kind of revision (standard, correction, refinement, etc.)."""
    
    # Provenance
    proposed_by: Optional[str] = None
    """Entity or process that proposed this revision."""
    
    validated_by: Optional[str] = None
    """Entity that validated the revision."""
    
    @property
    def revision_id(self) -> str:
        """Return the unique revision identifier."""
        return f"{self.identity_id}:v{self.revision_number}"
    
    def is_initial_revision(self) -> bool:
        """Check if this is the first revision of an action."""
        return self.parent_revision_id is None
    
    def has_parent(self, other_revision: "ActionRevisionMetadata") -> bool:
        """
        Check if this revision follows another in history.
        
        Args:
            other_revision: The potential parent revision
            
        Returns:
            True if this revision's parent matches the other revision
        """
        return self.parent_revision_id == other_revision.revision_id


__all__ = [
    "ActionRevisionReference",
    "ActionRevisionMetadata",
]
