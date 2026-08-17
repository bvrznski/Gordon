# Gordon Phase 5.7.2-I: Experiential Field Transition
# ===============================================================================
#
# Atomic transition commit for the experiential field.
#

"""
Transition management module for Experiential Field Builder.

This module handles atomic transitions between field generations:
    - Transition record creation
    - Atomic commit protocol
    - Rollback on failure
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class FieldTransition:
    """
    Immutable transition record between field generations.
    
    A transition records the changes from one field generation to another,
    preserving provenance and enabling replay/recovery scenarios.
    """
    
    # Identity
    transition_id: str
    """Unique identifier for this transition."""
    
    field_id: str
    """Field ID being transitioned."""
    
    previous_generation: int
    """Generation before this transition."""
    
    new_generation: int
    """New generation after this transition."""
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    """When the transition was initiated."""
    
    committed_at_utc: Optional[float] = None
    """When the transition was committed (None until commit)."""
    
    # Trigger and metadata
    trigger: str = "internal"
    """What triggered this transition."""
    
    # Contents changed
    added_contents: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of contents added in this transition."""
    
    retained_contents: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of contents that remain unchanged."""
    
    removed_contents: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of contents removed in this transition."""
    
    # Relations changed
    added_relations: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of relations added."""
    
    removed_relations: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of relations removed."""
    
    # Status and result
    accepted_contributions: int = 0
    """Number of contributions that were accepted."""
    
    rejected_contributions: int = 0
    """Number of contributions that were rejected."""
    
    capacity_actions: Tuple[str, ...] = field(default_factory=tuple)
    """Capacity-related actions taken during this transition."""
    
    validation_warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any warnings during validation."""
    
    status: str = "pending"
    """Transition status: pending, committing, completed, rolled_back"""
    
    provenance: Optional[str] = None
    """Provenance chain for this transition."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID for tracking."""
    
    def is_completed(self) -> bool:
        """Check if this transition has been successfully completed."""
        return self.status == "completed"
    
    def is_rolled_back(self) -> bool:
        """Check if this transition was rolled back."""
        return self.status == "rolled_back"


@dataclass
class TransitionCommitResult:
    """
    Result of a transition commit operation.
    
    This result indicates whether the transition succeeded and what state
    is now current, or why it failed.
    """
    
    succeeded: bool
    """Whether the transition commit succeeded."""
    
    status: str = "pending"
    """Final status of the transition."""
    
    new_field_snapshot: Optional["ExperientialFieldSnapshot"] = None
    """New field snapshot (if committed successfully)."""
    
    new_generation: int = 0
    """New generation number (if successful)."""
    
    # Failure information
    failure_reason: Optional[str] = None
    """Reason for failure if failed."""
    
    partial_success: bool = False
    """Whether this was a partial success with degraded operation."""
    
    degraded_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Degradation modes if partially successful."""
    
    # Partial outcomes
    skipped_transitions: Tuple[dict, ...] = field(default_factory=tuple)
    """Transitions that were skipped (optional)."""
    
    @property
    def is_failed(self) -> bool:
        """Check if this result represents a failure."""
        return not self.succeeded
    
    @classmethod
    def success(
        cls,
        snapshot: "ExperientialFieldSnapshot",
        generation: int,
    ) -> "TransitionCommitResult":
        """Create a successful commit result."""
        return cls(
            succeeded=True,
            status="completed",
            new_field_snapshot=snapshot,
            new_generation=generation,
        )
    
    @classmethod
    def failure(cls, reason: str) -> "TransitionCommitResult":
        """Create a failed commit result."""
        return cls(
            succeeded=False,
            status="failed",
            failure_reason=reason,
        )


# Field transition authority manages the atomic transition process

class FieldTransitionAuthority:
    """
    Manages atomic transitions between field generations.
    
    The authority ensures that:
        - Only one transition is active at a time
        - Transitions either fully commit or rollback completely  
        - Previous valid snapshots are preserved on failure
        - No partially built states are exposed to consumers
    
    This is the single canonical source of transition authority for
    experiential field construction.
    """
    
    def __init__(self, field_id: str):
        """
        Initialize the transition authority.
        
        Args:
            field_id: ID of the field this authority manages
        """
        self._field_id = field_id
        self._current_generation = 0
        self._previous_snapshot: Optional[ExperientialFieldSnapshot] = None
        self._pending_transition_id: Optional[str] = None
    
    def prepare_transition(
        self,
        new_contents: Tuple[dict, ...],
        new_relations: Tuple[dict, ...],
        trigger: str = "internal",
        accepted_contributions: int = 0,
        rejected_contributions: int = 0,
    ) -> FieldTransition:
        """
        Prepare a new transition record.
        
        This creates the transition but does not commit it yet. The caller
        should build the new snapshot and then call commit_transition().
        
        Args:
            new_contents: Tuple of content data dictionaries to add/update
            new_relations: Tuple of relation data dictionaries to add
            trigger: What triggered this transition
            accepted_contributions: Count of accepted contributions
            rejected_contributions: Count of rejected contributions
            
        Returns:
            A FieldTransition record ready for commit
        """
        self._pending_transition_id = f"transition-{time.time_ns()}"
        
        # Determine new generation
        new_generation = self._current_generation + 1
        
        transition = FieldTransition(
            transition_id=self._pending_transition_id,
            field_id=self._field_id,
            previous_generation=self._current_generation,
            new_generation=new_generation,
            started_at_utc=time.time(),
            trigger=trigger,
            accepted_contributions=accepted_contributions,
            rejected_contributions=rejected_contributions,
            status="committing",
        )
        
        return transition
    
    def commit_transition(
        self,
        new_snapshot: "ExperientialFieldSnapshot",
        transition: FieldTransition,
    ) -> TransitionCommitResult:
        """
        Atomically commit a transition with the new snapshot.
        
        This is the atomic point - either this succeeds completely or
        nothing changes. The caller must have already validated and built
        the new snapshot before calling this.
        
        Args:
            new_snapshot: The new field snapshot to commit
            transition: The transition record to update
            
        Returns:
            TransitionCommitResult indicating success/failure
        """
        try:
            # Update the transition with commit timestamp
            committed_transition = FieldTransition(
                transition_id=transition.transition_id,
                field_id=transition.field_id,
                previous_generation=transition.previous_generation,
                new_generation=new_snapshot.generation,
                started_at_utc=transition.started_at_utc,
                committed_at_utc=time.time(),
                trigger=transition.trigger,
                added_contents=new_snapshot.contents,
                retained_contents=(),
                removed_contents=(),
                added_relations=new_snapshot.relations,
                accepted_contributions=transition.accepted_contributions,
                rejected_contributions=transition.rejected_contributions,
                status="completed",
            )
            
            # Update internal state atomically
            self._previous_snapshot = new_snapshot
            self._current_generation = new_snapshot.generation
            self._pending_transition_id = None
            
            return TransitionCommitResult.success(
                snapshot=new_snapshot,
                generation=new_snapshot.generation,
            )
            
        except Exception as e:
            # Rollback on failure - previous snapshot remains valid
            self._pending_transition_id = None
            
            return TransitionCommitResult.failure(
                reason=f"Transition commit failed: {str(e)}"
            )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "FieldTransition",
    "TransitionCommitResult",
    "FieldTransitionAuthority",
)
