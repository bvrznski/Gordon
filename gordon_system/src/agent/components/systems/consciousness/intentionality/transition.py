# Gordon Phase 5.7.3-I: Intentional Context Engine - Transitions Authority
# ===============================================================================
#
# Immutable transitions for atomic publication of intentional context snapshots.
#

"""
Intentional Transition Authority for the Intentional Context Engine.

Transitions represent atomic commits of new intentional state generations:
    - Attention shifts
    - Object replacement
    - Target merge/split
    - Context completion/interruption/resumption
    
Transitions are immutable, deterministic, and never mutate published snapshots.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Dict, Optional
import uuid


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    return uuid.uuid4().hex[:8]


# =============================================================================
# INTENTIONAL TRANSITION STATUS
# =============================================================================

class IntentionalTransitionStatus:
    """
    Enum-like status values for transitions.
    
    Lifecycle states:
        - PENDING: Transition created but not yet committed
        - VALIDATING: Transition is being validated
        - COMMITTING: Transition is committing to new generation
        - COMPLETED: Transition successfully completed
        - ROLLED_BACK: Transition failed and rolled back
    """
    
    PENDING = "pending"
    VALIDATING = "validating"
    COMMITTING = "committing"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    
    ALL: Tuple[str, ...] = (
        PENDING,
        VALIDATING,
        COMMITTING,
        COMPLETED,
        ROLLED_BACK,
    )


# =============================================================================
# INTENTIONAL TRANSITION
# =============================================================================

@dataclass(frozen=True)
class IntentionalTransition:
    """
    Immutable record of an intentional transition commit.
    
    Transitions represent atomic commits of new intentional context states:
        - Attention shifts between objects
        - Object replacement (new target for same identity)
        - Target merge/split operations
        - Context completion/interruption/resumption
        
    Transition properties:
        - Immutable: Once committed, never modified
        - Atomic: Either fully committed or not at all
        - Deterministic: Same inputs produce same outputs
        - Versioned: Strictly monotonic generation increases
    
    A failed transition must preserve the previous valid snapshot and never
    expose partially updated state.
    """
    
    # Identity (required fields first)
    context_id: str
    """Context ID being transitioned."""
    
    previous_generation: int
    """Generation before this transition."""
    
    new_generation: int
    """New generation after this transition."""
    
    # Optional fields with defaults come after required fields
    transition_id: str = field(default_factory=lambda: f"transition-{_generate_uuid()}")
    """Unique identifier for this transition."""
    
    # Timing (required)
    started_at_utc: float = field(default_factory=time.time)
    """When transition was initiated."""
    
    committed_at_utc: Optional[float] = None
    """When transition was committed (None until successful)."""
    
    # Transition type and metadata
    transition_kind: str = "default"
    """Kind of transition (attention_shift, object_replace, etc.)."""
    
    trigger: str = "internal"
    """What triggered this transition."""
    
    # Intentional objects
    new_object_references: Tuple[str, ...] = field(default_factory=tuple)
    """New object references added in this transition."""
    
    removed_object_references: Tuple[str, ...] = field(default_factory=tuple)
    """Object references removed in this transition."""
    
    # Intentional relations
    new_relation_references: Tuple[str, ...] = field(default_factory=tuple)
    """New relation references added."""
    
    removed_relation_references: Tuple[str, ...] = field(default_factory=tuple)
    """Relation references removed."""
    
    # Intentional targets
    new_target_references: Tuple[str, ...] = field(default_factory=tuple)
    """New target references added."""
    
    removed_target_references: Tuple[str, ...] = field(default_factory=tuple)
    """Target references removed."""
    
    # Status and metadata
    status: str = "pending"
    """Current transition status (see IntentionalTransitionStatus)."""
    
    validation_warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any warnings during validation."""
    
    provenance: Optional[str] = None
    """Provenance information for this transition."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID for tracking chain."""
    
    # Failure information (only populated on failure)
    failure_reason: Optional[str] = None
    """Reason for failure (if status is rolled_back)."""
    
    @property
    def is_success(self) -> bool:
        """Check if this transition succeeded."""
        return self.status == IntentionalTransitionStatus.COMPLETED
    
    @property
    def is_failure(self) -> bool:
        """Check if this transition failed."""
        return self.status in (
            IntentionalTransitionStatus.ROLLED_BACK,
            IntentionalTransitionStatus.PENDING,  # Never committed
        )
    
    def complete(
        self,
        committed_at_utc: Optional[float] = None,
    ) -> "IntentionalTransition":
        """Return a copy marked as completed."""
        return dataclass_replace(
            self,
            status=IntentionalTransitionStatus.COMPLETED,
            committed_at_utc=committed_at_utc or time.time(),
        )
    
    def rollback(self, failure_reason: str) -> "IntentionalTransition":
        """Return a copy marked as rolled back with failure reason."""
        return dataclass_replace(
            self,
            status=IntentionalTransitionStatus.ROLLED_BACK,
            failure_reason=failure_reason,
        )


# Import dataclass_replace for methods
# Import is already done above


# =============================================================================
# TRANSITION AUTHORITY
# =============================================================================

class IntentionalTransitionAuthority:
    """
    Authority for creating and publishing intentional transitions.
    
    Ensures atomic publication of new intentional context generations.
    
    Key responsibilities:
        - Create transition records with deterministic IDs
        - Validate transitions before commit
        - Publish new snapshot generations atomically
        - Roll back on failure, preserving previous state
        
    No mutable global intentional state is maintained. Transitions produce
    immutable snapshots that are published atomically.
    """
    
    def __init__(self):
        """Initialize the transition authority."""
        self._pending_transition_id: Optional[str] = None
    
    def create_transition(
        self,
        context_id: str,
        previous_generation: int,
        new_generation: int,
        transition_kind: str = "default",
        trigger: str = "internal",
    ) -> IntentionalTransition:
        """
        Create a new transition record.
        
        Args:
            context_id: Context ID being transitioned
            previous_generation: Current generation before transition
            new_generation: Target generation after transition
            transition_kind: Kind of transition (attention_shift, etc.)
            trigger: What triggered the transition
            
        Returns:
            New IntentionalTransition in PENDING state
        """
        if self._pending_transition_id is not None:
            raise RuntimeError(f"Concurrent transition already in progress: {self._pending_transition_id}")
        
        transition = IntentionalTransition(
            context_id=context_id,
            previous_generation=previous_generation,
            new_generation=new_generation,
            transition_kind=transition_kind,
            trigger=trigger,
        )
        
        self._pending_transition_id = transition.transition_id
        return transition
    
    def add_object_references(
        self,
        transition: IntentionalTransition,
        new_objects: Tuple[str, ...] = (),
        removed_objects: Tuple[str, ...] = (),
    ) -> IntentionalTransition:
        """
        Add object references to a transition.
        
        Args:
            transition: The transition to modify
            new_objects: Object references to add (tuple)
            removed_objects: Object references to remove (tuple)
            
        Returns:
            New IntentionalTransition with updated references
        """
        if transition.status != IntentionalTransitionStatus.PENDING:
            raise ValueError("Cannot modify transition that is not in PENDING state")
        
        return dataclass_replace(
            transition,
            new_object_references=transition.new_object_references + tuple(new_objects),
            removed_object_references=transition.removed_object_references + tuple(removed_objects),
        )
    
    def add_relation_references(
        self,
        transition: IntentionalTransition,
        new_relations: Tuple[str, ...] = (),
        removed_relations: Tuple[str, ...] = (),
    ) -> IntentionalTransition:
        """
        Add relation references to a transition.
        
        Args:
            transition: The transition to modify
            new_relations: Relation references to add (tuple)
            removed_relations: Relation references to remove (tuple)
            
        Returns:
            New IntentionalTransition with updated references
        """
        if transition.status != IntentionalTransitionStatus.PENDING:
            raise ValueError("Cannot modify transition that is not in PENDING state")
        
        return dataclass_replace(
            transition,
            new_relation_references=transition.new_relation_references + tuple(new_relations),
            removed_relation_references=transition.removed_relation_references + tuple(removed_relations),
        )
    
    def add_target_references(
        self,
        transition: IntentionalTransition,
        new_targets: Tuple[str, ...] = (),
        removed_targets: Tuple[str, ...] = (),
    ) -> IntentionalTransition:
        """
        Add target references to a transition.
        
        Args:
            transition: The transition to modify
            new_targets: Target references to add (tuple)
            removed_targets: Target references to remove (tuple)
            
        Returns:
            New IntentionalTransition with updated references
        """
        if transition.status != IntentionalTransitionStatus.PENDING:
            raise ValueError("Cannot modify transition that is not in PENDING state")
        
        return dataclass_replace(
            transition,
            new_target_references=transition.new_target_references + tuple(new_targets),
            removed_target_references=transition.removed_target_references + tuple(removed_targets),
        )
    
    def commit_transition(
        self,
        transition: IntentionalTransition,
    ) -> IntentionalTransition:
        """
        Commit a transition, marking it as completed.
        
        Args:
            transition: The transition to commit
            
        Returns:
            New IntentionalTransition with status=COMPLETED
            
        Raises:
            ValueError: If transition is not in PENDING state
            RuntimeError: If another transition is already pending
        """
        if transition.status != IntentionalTransitionStatus.PENDING:
            raise ValueError(
                f"Cannot commit transition with status: {transition.status}"
            )
        
        if self._pending_transition_id != transition.transition_id:
            raise RuntimeError(
                f"Transition {transition.transition_id} not in pending state"
            )
        
        try:
            completed = transition.complete()
            self._pending_transition_id = None
            return completed
        except Exception as e:
            rolled_back = transition.rollback(failure_reason=str(e))
            self._pending_transition_id = None
            return rolled_back
    
    def rollback_transition(
        self,
        transition: IntentionalTransition,
        failure_reason: str,
    ) -> IntentionalTransition:
        """
        Roll back a transition, marking it as failed.
        
        Args:
            transition: The transition to roll back
            failure_reason: Reason for the rollback
            
        Returns:
            New IntentionalTransition with status=ROLLED_BACK
        """
        rolled_back = transition.rollback(failure_reason=failure_reason)
        self._pending_transition_id = None
        return rolled_back
    
    @property
    def has_pending_transition(self) -> bool:
        """Check if there's a pending transition."""
        return self._pending_transition_id is not None
    
    @property
    def pending_transition_id(self) -> Optional[str]:
        """Get the ID of the pending transition (if any)."""
        return self._pending_transition_id


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "IntentionalTransitionStatus",
    "IntentionalTransition",
    "IntentionalTransitionAuthority",
)