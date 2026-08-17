# Gordon Phase 5.7.4-I: Temporal Context Engine - Transition
# ===============================================================================
"""
Transition module for atomic temporal state changes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class TemporalTransition:
    """
    Immutable record of a single temporal transition operation.
    
    A transition represents the immutable change from one temporal state to
    another. Transitions are deterministic and must be validated before commit.
    
    Properties:
        - Deterministic: Same inputs produce identical outputs
        - Atomic: Either fully commits or rolls back on failure
        - Versioned: Has explicit generation tracking
    """
    
    transition_id: str = field(default_factory=lambda: f"tt-{time.time()}")
    """Unique identifier for this transition."""
    
    # Source and target states
    previous_generation: int = 0
    """Generation before the transition."""
    
    new_generation: int = 1
    """Generation after the transition."""
    
    # Temporal components being updated
    retention_update_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to add/update in retention."""
    
    presentation_update_ref: Optional[str] = None
    """New presentation reference (if changing)."""
    
    protention_update_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Expectations to add/update in protention."""
    
    # Metadata
    transition_kind: str = "default"
    """Kind of transition (default, resume, reset, interruption, etc.)."""
    
    trigger: str = "internal"
    """What triggered this transition."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the transition was initiated."""
    
    is_rollback: bool = False
    """Whether this transition is a rollback."""
    
    @classmethod
    def standard(
        cls,
        previous_generation: int,
        presentation_ref: str,
    ) -> "TemporalTransition":
        """
        Create a standard temporal transition (next generation).
        
        Args:
            previous_generation: Generation before the transition
            presentation_ref: New EF context reference
            
        Returns:
            New TemporalTransition for standard advancement
        """
        return cls(
            previous_generation=previous_generation,
            new_generation=previous_generation + 1,
            presentation_update_ref=presentation_ref,
        )
    
    @classmethod
    def resume(cls, generation: int) -> "TemporalTransition":
        """
        Create a resume transition (continues from paused state).
        
        Args:
            generation: Current generation
            
        Returns:
            New TemporalTransition for resuming
        """
        return cls(
            previous_generation=generation,
            new_generation=generation,
            transition_kind="resume",
        )
    
    @classmethod
    def reset(cls) -> "TemporalTransition":
        """
        Create a reset transition (new session).
        
        Returns:
            New TemporalTransition for resetting
        """
        return cls(
            previous_generation=0,
            new_generation=1,
            transition_kind="reset",
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if this transition is valid."""
        # Generation must advance by exactly 1 (unless rollback)
        if not self.is_rollback and self.new_generation != self.previous_generation + 1:
            return False
        
        # Presentation reference required for non-rollback transitions
        if not self.is_rollback and self.presentation_update_ref is None:
            return False
        
        return True


class TransitionAuthority:
    """
    Authority for managing temporal transitions.
    
    Ensures atomic commits, validates transition validity, and maintains
    proper state during the commit process.
    """
    
    def __init__(self):
        """Initialize the transition authority."""
        self._pending_transition: Optional[TemporalTransition] = None
        self._committed_transitions: Dict[str, TemporalTransition] = {}
        self._last_generation: int = 0
    
    @property
    def last_committed_generation(self) -> int:
        """Get the last committed generation number."""
        return self._last_generation
    
    def begin_transition(
        self,
        transition: TemporalTransition,
    ) -> Tuple[bool, Optional[str]]:
        """
        Begin a new transition (prepare for commit).
        
        Args:
            transition: The transition to begin
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check for concurrent transitions
        if self._pending_transition is not None:
            return False, "Transition already in progress"
        
        # Validate the transition
        if not transition.is_valid:
            return False, f"Invalid transition: generation must increment by 1"
        
        # Store pending state
        self._pending_transition = transition
        return True, None
    
    def commit_transition(
        self,
        transition_id: str,
    ) -> Tuple[bool, Optional[str], Optional[TemporalTransition]]:
        """
        Commit a pending transition.
        
        Args:
            transition_id: ID of the transition to commit
            
        Returns:
            Tuple of (success, error_message, committed transition if successful)
        """
        if self._pending_transition is None:
            return False, "No pending transition to commit", None
        
        # Final validation
        if self._pending_transition.transition_id != transition_id:
            return False, "Transition ID mismatch", None
        
        # Record the transition
        self._committed_transitions[transition_id] = self._pending_transition
        self._last_generation = self._pending_transition.new_generation
        
        committed = self._pending_transition
        self._pending_transition = None
        
        return True, None, committed
    
    def rollback_transition(
        self,
    ) -> Tuple[bool, Optional[str]]:
        """
        Rollback the current pending transition.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._pending_transition is None:
            return False, "No pending transition to rollback"
        
        # Simply discard the pending transition
        self._pending_transition = None
        return True, None
    
    def get_pending_transition(self) -> Optional[TemporalTransition]:
        """Get the current pending transition."""
        return self._pending_transition
    
    def get_committed(self, transition_id: str) -> Optional[TemporalTransition]:
        """Get a committed transition by its ID."""
        return self._committed_transitions.get(transition_id)
    
    def get_all_committed(
        self,
        after_generation: int = 0,
    ) -> Tuple[TemporalTransition, ...]:
        """
        Get all committed transitions after a given generation.
        
        Args:
            after_generation: Start from this generation (exclusive)
            
        Returns:
            Tuple of committed transitions
        """
        return tuple(
            t for t in self._committed_transitions.values()
            if t.previous_generation > after_generation
        )


@dataclass(frozen=True)
class TransitionResult:
    """
    Immutable result of a transition operation.
    
    Contains the outcome of either attempting or committing a transition,
    including any errors that may have occurred.
    """
    
    transition_id: str = ""
    """ID of the affected transition."""
    
    succeeded: bool = False
    """Whether the transition succeeded."""
    
    status: str = ""
    """Status string (completed, rolled_back, failed)."""
    
    new_context_snapshot: Optional[TemporalSnapshot] = None
    """New context snapshot if successful."""
    
    new_generation: int = 0
    """Generation number after transition."""
    
    failure_reason: Optional[str] = None
    """Human-readable reason for failure (if any)."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the result was generated."""
    
    @classmethod
    def success(
        cls,
        transition_id: str,
        snapshot: TemporalSnapshot,
        generation: int,
    ) -> "TransitionResult":
        """
        Create a successful transition result.
        
        Args:
            transition_id: ID of the completed transition
            snapshot: New context snapshot
            generation: New generation number
            
        Returns:
            TransitionResult with success status
        """
        return cls(
            transition_id=transition_id,
            succeeded=True,
            status="completed",
            new_context_snapshot=snapshot,
            new_generation=generation,
        )
    
    @classmethod
    def rollback(
        cls,
        transition_id: str,
        previous_generation: int,
    ) -> "TransitionResult":
        """
        Create a rollback transition result.
        
        Args:
            transition_id: ID of the rolled back transition
            previous_generation: Generation to roll back to
            
        Returns:
            TransitionResult with rollback status
        """
        return cls(
            transition_id=transition_id,
            succeeded=False,
            status="rolled_back",
            new_generation=previous_generation,
        )
    
    @classmethod
    def failure(
        cls,
        transition_id: str,
        reason: str,
    ) -> "TransitionResult":
        """
        Create a failed transition result.
        
        Args:
            transition_id: ID of the failed transition
            reason: Failure reason
            
        Returns:
            TransitionResult with failure status
        """
        return cls(
            transition_id=transition_id,
            succeeded=False,
            status="failed",
            failure_reason=reason,
        )


__all__: Tuple[str, ...] = (
    "TemporalTransition",
    "TransitionAuthority",
    "TransitionResult",
)