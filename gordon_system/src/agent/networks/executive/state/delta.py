# Executive State Deltas
# =======================

"""
Immutable delta types for executive state changes.

Deltas represent proposed or applied changes to state without mutating
the original state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# EXECUTIVE STATE DELTA
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateDelta:
    """
    Immutable delta for executive state changes.
    
    A delta identifies what changed between two state revisions without
    exposing mutation callbacks or full object copies.
    
    Properties:
        - Immutable: Cannot be modified after creation
        - Bounded: All collections have capacity limits
        - Deterministic: Same inputs produce same deltas
    
    Delta properties:
        - Base revision (what was changed FROM)
        - Resulting revision (what it should change TO)
        - Changed fields (what actually changed)
        - Added references (new items referenced)
        - Removed references (items removed)
        - Preserved fields (unchanged items)
        - Reason for change
        - Authority that approved the change
    """
    
    base_state_id: str = "exec_state_unknown"
    """State ID at base revision."""
    
    base_revision: int = 0
    """Revision being changed FROM."""
    
    resulting_revision: int = 1
    """Revision after delta is applied."""
    
    # Fields that were modified (changed values)
    modified_fields: Tuple[str, ...] = field(default_factory=tuple)
    """List of fields whose values were modified."""
    
    # References that were added
    added_task_set_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Task set IDs that were added."""
    
    added_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Goal IDs that were added."""
    
    added_commitment_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Commitment IDs that were added."""
    
    added_proposal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Proposal IDs that were added."""
    
    # References that were removed
    removed_task_set_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Task set IDs that were removed."""
    
    removed_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Goal IDs that were removed."""
    
    removed_commitment_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Commitment IDs that were removed."""
    
    # Fields preserved unchanged
    preserved_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that remain unchanged."""
    
    # Delta metadata
    reason: str = "unknown"
    """Reason for this delta (e.g., 'task_set_activated', 'goal_added')."""
    
    authority_approved: bool = False
    """Whether an external authority approved this change."""
    
    confidence_score: float = 1.0
    """Confidence in the delta correctness (0.0 to 1.0)."""
    
    semantic_time_utc: float = 0.0
    """Semantic time when delta was created (seconds since epoch)."""
    
    provenance_id: Optional[str] = None
    """ID of provenance record for this delta."""
    
    @classmethod
    def from_changes(
        cls,
        base_state_id: str,
        base_revision: int,
        resulting_revision: int,
        reason: str,
    ) -> ExecutiveStateDelta:
        """
        Create a delta from change information.
        
        Args:
            base_state_id: State ID at the base revision
            base_revision: Revision being changed FROM
            resulting_revision: Revision after delta is applied
            reason: Human-readable reason for the change
        
        Returns:
            A new ExecutiveStateDelta instance
        """
        return cls(
            base_state_id=base_state_id,
            base_revision=base_revision,
            resulting_revision=resulting_revision,
            reason=reason,
        )


# =============================================================================
# EXECUTIVE CONTEXT DELTA
# =============================================================================


@dataclass(frozen=True)
class ExecutiveContextDelta:
    """
    Immutable delta for executive context changes.
    
    Context deltas are proposals or assembly inputs - they don't mutate
    source systems, just describe what would change in a new context.
    
    Delta operations:
        ADD_PROJECTION: Add a new projection to the context
        REPLACE_PROJECTION: Replace an existing projection with a newer one
        REMOVE_EXPIRED_PROJECTION: Remove a projection that has expired
        MARK_STALE: Mark projections as stale without removing them
        ADD_CONFLICT: Record a conflict between projections
        ADD_OMISSION: Record an omitted projection due to bounds
        UPDATE_VALIDITY: Update validity classification
        UPDATE_CONFIDENCE: Update confidence score
        UPDATE_COMPLETENESS: Update completeness classification
    """
    
    class Operation:
        """Context delta operation types."""
        ADD_PROJECTION = "add_projection"
        REPLACE_PROJECTION = "replace_projection"
        REMOVE_EXPIRED_PROJECTION = "remove_expired_projection"
        MARK_STALE = "mark_stale"
        ADD_CONFLICT = "add_conflict"
        ADD_OMISSION = "add_omission"
        UPDATE_VALIDITY = "update_validity"
        UPDATE_CONFIDENCE = "update_confidence"
        UPDATE_COMPLETENESS = "update_completeness"
    
    base_context_id: str = "exec_context_unknown"
    """Context ID at base revision."""
    
    base_revision: int = 1
    """Revision being changed FROM."""
    
    resulting_revision: int = 2
    """Revision after delta is applied."""
    
    operation: str = Operation.ADD_PROJECTION
    """Type of operation performed."""
    
    affected_source_id: Optional[str] = None
    """Source ID affected by this change (if applicable)."""
    
    projection_type: Optional[str] = None
    """Type of projection being modified."""
    
    reason: str = "unknown"
    """Reason for the delta (e.g., 'source_expired', 'projection_replaced')."""
    
    source_owner: Optional[str] = None
    """Owner of the affected source system."""
    
    source_revision_lag: int = 0
    """How many revisions behind the latest source is."""
    
    @classmethod
    def add_projection(
        cls,
        context_id: str,
        revision: int,
        source_id: str,
        projection_type: str,
    ) -> ExecutiveContextDelta:
        """
        Create a delta to add a new projection.
        
        Args:
            context_id: Context ID being updated
            revision: Current revision before update
            source_id: Source system providing the projection
            projection_type: Type of projection (e.g., 'goal', 'task')
        
        Returns:
            A new ExecutiveContextDelta instance
        """
        return cls(
            base_context_id=context_id,
            base_revision=revision,
            resulting_revision=revision + 1,
            operation=cls.Operation.ADD_PROJECTION,
            affected_source_id=source_id,
            projection_type=projection_type,
            reason="new_projection_assembled",
        )
    
    @classmethod
    def replace_projection(
        cls,
        context_id: str,
        revision: int,
        source_id: str,
        projection_type: str,
    ) -> ExecutiveContextDelta:
        """
        Create a delta to replace an existing projection.
        
        Args:
            context_id: Context ID being updated
            revision: Current revision before update
            source_id: Source system providing the new projection
            projection_type: Type of projection
        
        Returns:
            A new ExecutiveContextDelta instance
        """
        return cls(
            base_context_id=context_id,
            base_revision=revision,
            resulting_revision=revision + 1,
            operation=cls.Operation.REPLACE_PROJECTION,
            affected_source_id=source_id,
            projection_type=projection_type,
            reason="projection_replaced",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveStateDelta",
    "ExecutiveContextDelta",
)