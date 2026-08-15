# Workspace State Identity Module
# ================================

"""
Canonical WorkspaceStateIdentity and WorkspaceStateRevision types.

These represent the immutable semantic identity and revision of workspace states.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NewType


# =============================================================================
# WORKSPACE STATE IDENTITY
# =============================================================================

WorkspaceStateIdentity = NewType("WorkspaceStateIdentity", str)
"""
Unique identifier for a WorkspaceState instance.

Characteristics:
- Globally unique across all time
- Never changes once assigned
- External or deterministically derived (never internally generated)
- Preserved through state transitions via lineage
"""


@dataclass(frozen=True)
class WorkspaceStateRevision:
    """
    Monotonically increasing revision identifier for a WorkspaceState.
    
    Revision semantics:
    - Revision 0 represents the initial state
    - Each transition produces exactly one new revision
    - Revisions are never reused
    - Revisions are strictly monotonic (n+1 > n)
    
    ARCHITECTURAL INVARIANT: Every state has exactly one revision number.
    """
    
    value: int = field(default=0, metadata={"description": "The revision number"})
    
    def next(self) -> WorkspaceStateRevision:
        """Return the next revision in the sequence."""
        return WorkspaceStateRevision(value=self.value + 1)
    
    @property
    def is_initial(self) -> bool:
        """Check if this is the initial (revision 0) state."""
        return self.value == 0
    
    def __str__(self) -> str:
        return f"v{self.value}"
    
    def __repr__(self) -> str:
        return f"WorkspaceStateRevision(value={self.value})"


@dataclass(frozen=True)
class WorkspaceStateReference:
    """
    Reference to a workspace state by identity and revision.
    
    Used for linking states without embedding full state objects.
    Preserves traceability while maintaining bounds.
    """
    
    state_id: WorkspaceStateIdentity
    """Unique identifier of the referenced state."""
    
    revision: int = field(default=1, metadata={"description": "Revision at reference time"})
    """Revision number at the time of reference."""
    
    @classmethod
    def for_initial(cls) -> WorkspaceStateReference:
        """Create a reference to an initial state (revision 0)."""
        return cls(state_id=WorkspaceStateIdentity("initial"), revision=0)
    
    def __str__(self) -> str:
        return f"{self.state_id}@v{self.revision}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "WorkspaceStateIdentity",
    "WorkspaceStateRevision",
    "WorkspaceStateReference",
)