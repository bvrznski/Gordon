# Workspace State Delta Module
# ============================

"""
Canonical WorkspaceStateDelta and related types.

WorkspaceStateDelta represents an immutable record of semantic changes between
workspace state revisions. Deltas are append-only and never mutate in place.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


WorkspaceStateDeltaIdentity = str
"""
Unique identifier for a WorkspaceStateDelta instance.

Characteristics:
- Globally unique across all time
- Never changes once assigned
- External or deterministically derived (never internally generated)
"""


@dataclass(frozen=True)
class StateDeltaOperation:
    """
    A single atomic operation in a state delta.
    
    Operations are the smallest units of state change. Each operation represents
    exactly one semantic modification to the workspace state.
    """
    
    # Operation kind
    kind: str = "add"  # add, replace, remove, supersede, invalidate, restore
    
    """Type of operation performed."""
    
    # Target identification
    target_id: str = ""
    """ID of the target entity being modified."""
    
    # Content (for add/replace operations)
    new_content: dict = field(default_factory=dict)
    """New content being added or replacing existing content."""
    
    # Evidence (for removal/invalidation operations)
    justification: str = ""
    """Justification for the operation."""
    
    @property
    def is_add(self) -> bool:
        return self.kind == "add"
    
    @property
    def is_replace(self) -> bool:
        return self.kind == "replace"
    
    @property
    def is_remove(self) -> bool:
        return self.kind == "remove"
    
    @property
    def is_supersede(self) -> bool:
        return self.kind == "supersede"
    
    @property
    def is_invalidate(self) -> bool:
        return self.kind == "invalidate"
    
    @property
    def is_restore(self) -> bool:
        return self.kind == "restore"


@dataclass(frozen=True)
class WorkspaceStateDelta:
    """
    Immutable record of semantic changes between workspace state revisions.
    
    Delta semantics:
    - Append-only: no in-place mutation allowed
    - Atomic: each delta represents exactly one revision transition
    - Complete: captures all changes in the transition
    - Deterministic: same inputs produce identical deltas
    
    Supported operations:
        - add: Introduce new content into the workspace
        - replace: Replace existing content with updated content
        - remove: Remove content from active state (history preserved)
        - supersede: Mark content as superseded by newer revision
        - invalidate: Mark content as semantically invalid
        - restore: Restore previously removed/suspended content
    
    ARCHITECTURAL INVARIANT: Every delta belongs to exactly one revision chain.
    """
    
    # Identity and Revisioning
    delta_id: WorkspaceStateDeltaIdentity = "delta_initial"
    """Unique identifier for this delta instance."""
    
    revision: int = 0
    """Revision number that this delta produces."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # State references
    previous_state_id: str = ""
    """ID of the state before this delta was applied."""
    
    next_state_id: str = ""
    """ID of the state after this delta is applied."""
    
    # Operations (ordered sequence)
    operations: Tuple[StateDeltaOperation, ...] = field(default_factory=tuple)
    """Ordered list of atomic operations in this delta."""
    
    # Delta metadata
    applied_at_utc: float = 0.0
    """When delta was applied (seconds since epoch)."""
    
    applied_by: str = "workspace_delta"
    """Who/what applied this delta."""
    
    # Validation
    validity_class: str = "valid"
    """Classification of delta validity."""
    
    consistency_class: str = "unknown"
    """Classification of consistency after application."""
    
    @classmethod
    def create_initial(cls) -> WorkspaceStateDelta:
        """
        Create an initial (empty) delta.
        
        This represents the delta that produces the initial state from nothing.
        """
        return cls(
            delta_id="delta_initial",
            revision=0,
            previous_state_id="",
            next_state_id="workspace_state_initial",
            validity_class="valid",
        )
    
    def with_operation(self, operation: StateDeltaOperation) -> WorkspaceStateDelta:
        """Return a new delta with the given operation appended."""
        return WorkspaceStateDelta(
            delta_id=self.delta_id,
            revision=self.revision,
            schema_version=self.schema_version,
            previous_state_id=self.previous_state_id,
            next_state_id=self.next_state_id,
            operations=self.operations + (operation,),
            applied_at_utc=operation.justification if hasattr(operation, 'justification') else self.applied_at_utc,
            applied_by=self.applied_by,
            validity_class=self.validity_class,
            consistency_class=self.consistency_class,
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if this delta contains no operations."""
        return len(self.operations) == 0
    
    @property
    def operation_count(self) -> int:
        """Return the number of operations in this delta."""
        return len(self.operations)


@dataclass(frozen=True)
class DeltaApplicationResult:
    """
    Result of applying a state delta to a workspace state.
    
    Captures whether the application succeeded and what state was produced.
    """
    
    success: bool = False
    """Whether the delta was successfully applied."""
    
    new_state_id: str = ""
    """ID of the resulting state (if successful)."""
    
    new_revision: int = 0
    """Revision number of the resulting state."""
    
    error_message: str = ""
    """Error description if application failed."""
    
    validation_errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation errors if any occurred."""
    
    @classmethod
    def success_result(cls, state_id: str, revision: int) -> DeltaApplicationResult:
        return cls(
            success=True,
            new_state_id=state_id,
            new_revision=revision,
        )
    
    @classmethod
    def failure_result(cls, error_message: str) -> DeltaApplicationResult:
        return cls(
            success=False,
            error_message=error_message,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "WorkspaceStateDeltaIdentity",
    "StateDeltaOperation",
    "WorkspaceStateDelta",
    "DeltaApplicationResult",
)