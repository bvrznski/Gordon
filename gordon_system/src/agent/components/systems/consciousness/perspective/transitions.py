# Gordon Phase 5.7.6-I: Perspective Engine - Transitions
# ===============================================================================
"""
Canonical transition system for the Perspective Engine.

Transitions represent immutable records of perspective state changes,
including initialization, viewpoint shifts, observer updates, and lifecycle events.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Optional


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# =============================================================================
# TRANSITION KINDS
# =============================================================================

TRANSITION_KIND_INITIALIZATION = "initialization"
"""Perspective initialization."""

TRANSITION_KIND_VIEWPOINT_SHIFT = "viewpoint_shift"
"""Viewpoint or perspective type change."""

TRANSITION_KIND_OBSERVER_UPDATE = "observer_update"
"""Observer state update without full transition."""

TRANSITION_KIND_INTERRUPTION = "interruption"
"""Temporary interruption of current perspective."""

TRANSITION_KIND_RESUME = "resume"
"""Resume from interruption."""

TRANSITION_KIND_DEGRADATION = "degradation"
"""Perspective degradation mode activation."""


# =============================================================================
# TRANSITION STATE
# =============================================================================

@dataclass(frozen=True)
class TransitionState:
    """
    Immutable transition state record.
    
    Each transition captures the complete context of a perspective change,
    enabling replay, audit, and debugging.
    """
    
    transition_id: str = field(default_factory=lambda: f"transition-{_generate_uuid()}")
    """Unique identifier for this transition."""
    
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    """When the transition occurred."""
    
    # State before
    from_frame_ref: Optional[str] = None
    """Reference to previous reference frame."""
    
    from_observer_id: Optional[str] = None
    """Observer ID before transition."""
    
    from_perspective_type: str = "self"
    """Perspective type before transition."""
    
    # State after
    to_frame_ref: Optional[str] = None
    """Reference to new reference frame."""
    
    to_observer_id: Optional[str] = None
    """Observer ID after transition."""
    
    to_perspective_type: str = "self"
    """Perspective type after transition."""
    
    # Metadata
    kind: str = TRANSITION_KIND_INITIALIZATION
    """Kind of transition."""
    
    generation: int = 0
    """Context generation when transition occurred."""
    
    provenance: Optional[str] = None
    """Source that triggered this transition."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    @classmethod
    def initial(cls, frame_ref: str) -> "TransitionState":
        """
        Create an initial perspective transition.
        
        Args:
            frame_ref: Reference to the initial reference frame
        """
        import time
        return cls(
            kind=TRANSITION_KIND_INITIALIZATION,
            timestamp_utc=time.time(),
            from_frame_ref=None,
            to_frame_ref=frame_ref,
            generation=0,
        )
    
    @classmethod
    def viewpoint_shift(
        cls,
        from_type: str,
        to_type: str,
        prev_frame: Optional[str] = None,
        next_frame: Optional[str] = None,
        generation: int = 1,
    ) -> "TransitionState":
        """
        Create a viewpoint shift transition.
        
        Args:
            from_type: Previous perspective type
            to_type: New perspective type
            prev_frame: Reference to previous frame (optional)
            next_frame: Reference to new frame (optional)
            generation: Context generation
        """
        import time
        return cls(
            kind=TRANSITION_KIND_VIEWPOINT_SHIFT,
            timestamp_utc=time.time(),
            from_perspective_type=from_type,
            to_perspective_type=to_type,
            from_frame_ref=prev_frame,
            to_frame_ref=next_frame,
            generation=generation,
        )
    
    @property
    def is_self_transition(self) -> bool:
        """Check if this is a self-transition (no effective change)."""
        return self.from_perspective_type == self.to_perspective_type and (
            self.kind in (TRANSITION_KIND_INITIALIZATION, TRANSITION_KIND_RESUME)
        )


# =============================================================================
# TRANSITION BATCH
# =============================================================================

@dataclass
class TransitionBatch:
    """
    Batch of perspective transitions.
    
    Allows grouping multiple transitions that should be applied together
    as an atomic unit.
    """
    
    batch_id: str = field(default_factory=lambda: f"batch-{_generate_uuid()}")
    """Unique identifier for this batch."""
    
    transitions: list[TransitionState] = field(default_factory=list)
    """List of transitions in this batch."""
    
    # State tracking
    _pending_count: int = 0
    _committed_count: int = 0
    
    def __post_init__(self) -> None:
        """Initialize internal state after construction."""
        self._pending_count = len(self.transitions)
    
    @property
    def size(self) -> int:
        """Get number of transitions in batch."""
        return len(self.transitions)
    
    @property
    def is_empty(self) -> bool:
        """Check if batch has no transitions."""
        return len(self.transitions) == 0
    
    def add_transition(self, transition: TransitionState) -> None:
        """
        Add a transition to the batch.
        
        Args:
            transition: Transition to add
        """
        self.transitions.append(transition)
        self._pending_count += 1
    
    def commit_one(self) -> None:
        """Mark one transition as committed."""
        if self._committed_count < len(self.transitions):
            self._committed_count += 1
            self._pending_count -= 1
    
    @property
    def is_complete(self) -> bool:
        """Check if all transitions have been committed."""
        return self._committed_count == len(self.transitions)
    
    def clear(self) -> None:
        """Clear the batch and reset state."""
        self.transitions.clear()
        self._pending_count = 0
        self._committed_count = 0


# =============================================================================
# TRANSITION VALIDATOR
# =============================================================================

@dataclass
class TransitionValidator:
    """
    Validator for perspective transitions.
    
    Ensures transitions are well-formed, valid, and don't conflict with
    the current state or system constraints.
    """
    
    allow_self_transitions: bool = True
    """Whether to allow transitions that don't change perspective."""
    
    require_frame_reference: bool = False
    """Whether to require frame reference in all transitions."""
    
    def validate(
        self,
        transition: TransitionState,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a perspective transition.
        
        Args:
            transition: Transition to validate
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        from .constants import (
            VALID_PERSPECTIVE_TYPES,
            VALID_TRANSFORMATION_TYPES,
        )
        
        # Check perspective types are valid
        if transition.from_perspective_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid source perspective: {transition.from_perspective_type}"
        if transition.to_perspective_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid target perspective: {transition.to_perspective_type}"
        
        # Check generation is valid
        if transition.generation < 0:
            return False, "Generation cannot be negative"
        
        # Check self-transition allowed (if configured)
        if not self.allow_self_transitions and transition.is_self_transition:
            return False, "Self-transitions are disabled"
        
        # Check frame reference required (if configured)
        if self.require_frame_reference and transition.kind != TRANSITION_KIND_INITIALIZATION:
            if not transition.from_frame_ref or not transition.to_frame_ref:
                return False, "Frame references required for this transition type"
        
        # All checks passed
        return True, None
    
    @classmethod
    def default(cls) -> "TransitionValidator":
        """Return a validator with default settings."""
        return cls()
    
    @classmethod
    def strict(cls) -> "TransitionValidator":
        """Return a strict validator for production use."""
        return cls(
            allow_self_transitions=False,
            require_frame_reference=True,
        )


# =============================================================================
# TRANSITION LOG
# =============================================================================

@dataclass
class TransitionLog:
    """
    Log of all perspective transitions.
    
    Maintains a complete history of perspective changes for replay,
    debugging, and audit purposes.
    """
    
    max_entries: int = 10000
    """Maximum number of entries to retain."""
    
    _entries: list[TransitionState] = field(default_factory=list)
    """Internal storage for transition records."""
    
    def __post_init__(self) -> None:
        """Initialize after construction."""
        self._entries.clear()
    
    @property
    def size(self) -> int:
        """Get number of entries in log."""
        return len(self._entries)
    
    @property
    def last_entry(self) -> Optional[TransitionState]:
        """Get the most recent transition entry."""
        if not self._entries:
            return None
        return self._entries[-1]
    
    def append(self, entry: TransitionState) -> bool:
        """
        Add a transition entry to the log.
        
        Args:
            entry: Transition state to add
            
        Returns:
            True if added, False if capacity exceeded
        """
        # Enforce max size by removing oldest entries if needed
        while len(self._entries) >= self.max_entries:
            self._entries.pop(0)
        
        self._entries.append(entry)
        return True
    
    def get_by_generation(self, generation: int) -> list[TransitionState]:
        """
        Get all transitions for a specific generation.
        
        Args:
            generation: Context generation to look up
            
        Returns:
            List of matching transition entries
        """
        return [e for e in self._entries if e.generation == generation]
    
    def get_by_kind(self, kind: str) -> list[TransitionState]:
        """
        Get all transitions of a specific kind.
        
        Args:
            kind: Transition kind to filter by
            
        Returns:
            List of matching transition entries
        """
        return [e for e in self._entries if e.kind == kind]
    
    def get_by_perspective(self, perspective_type: str) -> list[TransitionState]:
        """
        Get all transitions involving a specific perspective type.
        
        Args:
            perspective_type: Perspective type to filter by
            
        Returns:
            List of matching transition entries
        """
        return [
            e for e in self._entries
            if e.from_perspective_type == perspective_type or
               e.to_perspective_type == perspective_type
        ]
    
    def clear(self) -> None:
        """Clear all entries from the log."""
        self._entries.clear()


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Kinds
    "TRANSITION_KIND_INITIALIZATION",
    "TRANSITION_KIND_VIEWPOINT_SHIFT",
    "TRANSITION_KIND_OBSERVER_UPDATE",
    "TRANSITION_KIND_INTERRUPTION",
    "TRANSITION_KIND_RESUME",
    "TRANSITION_KIND_DEGRADATION",
    # Classes
    "TransitionState",
    "TransitionBatch",
    "TransitionValidator",
    "TransitionLog",
)