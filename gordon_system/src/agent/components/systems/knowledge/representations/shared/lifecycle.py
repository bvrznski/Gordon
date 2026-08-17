# Knowledge Representation Lifecycle - Phase 6.2
# ==============================================

"""
Lifecycle management for knowledge representations.

This module tracks state transitions and history for representations,
enabling proper version management without changing semantic identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REPRESENTATION LIFECYCLE STATES
# =============================================================================


class RepresentationLifecycleState(Enum):
    """
    Lifecycle states for representations.
    
    States represent how a representation evolves:
        CREATED      -> Initial creation (not yet validated)
        ACTIVE       -> Published and in use
        STALE        -> Needs regeneration (model/ontology changed)
        REGENERATING -> Currently being regenerated
        SUPERSEDED   -> Replaced by newer version
        DEPRECATED   -> Marked as outdated but still referenced
        ARCHIVED     -> Preserved for historical purposes
        INVALID      -> Failed validation, not for use
    """
    
    CREATED = "created"
    ACTIVE = "active"
    STALE = "stale"
    REGENERATING = "regenerating"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    INVALID = "invalid"


# =============================================================================
# LIFECYCLE TRANSITION - State change record
# =============================================================================


@dataclass(frozen=True)
class RepresentationLifecycleTransition:
    """
    Record of a lifecycle state transition.
    
    Tracks when and why a representation changed states.
    
    Fields:
        transition_identity: Unique identifier for this transition
        representation_id:   ID of representation that changed states
        from_state:          Previous lifecycle state
        to_state:            New lifecycle state
        reason:              Why the transition occurred
        timestamp_utc:       When transition occurred
        actor_type:          Type of actor (system, user, reasoning)
        actor_id:            ID of actor performing transition
    """
    
    # Identity and metadata
    transition_identity: str               # Unique transition ID
    
    representation_id: str                 # Representation that changed
    
    from_state: RepresentationLifecycleState  # Previous state
    to_state: RepresentationLifecycleState      # New state
    
    reason: Optional[str] = None           # Transition reason
    timestamp_utc: float = field(default_factory=time.time)
    
    actor_type: str = "system"             # e.g., "system", "user", "reasoning"
    actor_id: str = ""                     # Actor identifier
    
    @property
    def is_valid(self) -> bool:
        """Check if transition has valid data."""
        return (
            len(self.transition_identity) > 0 and
            len(self.representation_id) > 0 and
            self.from_state != RepresentationLifecycleState.INVALID and
            self.to_state != RepresentationLifecycleState.INVALID
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition to dictionary for serialization."""
        return {
            "transition_identity": self.transition_identity,
            "representation_id": self.representation_id,
            "from_state": self.from_state.value if hasattr(
                self.from_state, 'value'
            ) else str(self.from_state),
            "to_state": self.to_state.value if hasattr(
                self.to_state, 'value'
            ) else str(self.to_state),
            "reason": self.reason,
            "timestamp_utc": self.timestamp_utc,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationLifecycleTransition":
        """Create transition from dictionary."""
        return cls(
            transition_identity=data.get("transition_identity", str(uuid.uuid4())),
            representation_id=data.get("representation_id", ""),
            from_state=RepresentationLifecycleState(data.get("from_state", "created")),
            to_state=RepresentationLifecycleState(data.get("to_state", "created")),
            reason=data.get("reason"),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            actor_type=data.get("actor_type", "system"),
            actor_id=data.get("actor_id", ""),
        )


# =============================================================================
# LIFECYCLE HISTORY - Complete progression chain
# =============================================================================


@dataclass(frozen=True)
class RepresentationLifecycle:
    """
    Complete lifecycle history for a representation.
    
    Maintains the full sequence of state transitions from initial creation to current state.
    
    Fields:
        lifecycle_identity:  Unique identifier for this lifecycle record
        representation_id:   ID of the represented artifact
        origin_event:        The first state transition (creation) in history
        transitions:         All state transitions in chronological order
    """
    
    # Identity and metadata
    lifecycle_identity: str                # Unique lifecycle ID
    
    representation_id: str                 # Representation identity
    
    origin_event: RepresentationLifecycleTransition  # Original creation
    transitions: Tuple[RepresentationLifecycleTransition, ...] = field(default_factory=tuple)
    
    @property
    def current_state(self) -> RepresentationLifecycleState:
        """Get the current lifecycle state."""
        if self.transitions:
            return self.transitions[-1].to_state
        return self.origin_event.to_state
    
    @property
    def transition_count(self) -> int:
        """Get total number of transitions in history."""
        return len(self.transitions)
    
    @classmethod
    def create_initial(
        cls,
        representation_id: str,
        actor_type: str = "system",
        actor_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> "RepresentationLifecycle":
        """
        Create initial lifecycle history with creation transition.
        
        Args:
            representation_id: ID of representation
            actor_type: Type of actor creating the representation
            actor_id: ID of actor
            context: Creation context (optional)
            
        Returns:
            New RepresentationLifecycle with single creation transition
        """
        origin_event = RepresentationLifecycleTransition(
            transition_identity=f"transition:{uuid.uuid4().hex[:16]}",
            representation_id=representation_id,
            from_state=RepresentationLifecycleState.CREATED,
            to_state=RepresentationLifecycleState.ACTIVE,  # Initial state after creation
            reason="Initial representation creation",
            timestamp_utc=time.time(),
            actor_type=actor_type,
            actor_id=actor_id,
        )
        
        return cls(
            lifecycle_identity=f"lifecycle:{uuid.uuid4().hex[:16]}",
            representation_id=representation_id,
            origin_event=origin_event,
            transitions=tuple([origin_event]),
        )
    
    def append_transition(
        self,
        to_state: RepresentationLifecycleState,
        reason: Optional[str] = None,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> "RepresentationLifecycle":
        """
        Create a new history with an additional transition appended.
        
        Args:
            to_state: Target lifecycle state
            reason: Transition reason (optional)
            actor_type: Type of actor (optional, defaults to last)
            actor_id: ID of actor (optional, defaults to last)
            
        Returns:
            New RepresentationLifecycle with added transition
        """
        new_transition = RepresentationLifecycleTransition(
            transition_identity=f"transition:{uuid.uuid4().hex[:16]}",
            representation_id=self.representation_id,
            from_state=self.current_state,
            to_state=to_state,
            reason=reason,
            timestamp_utc=time.time(),
            actor_type=actor_type or (self.transitions[-1].actor_type if self.transitions else "system"),
            actor_id=actor_id or (self.transitions[-1].actor_id if self.transitions else ""),
        )
        
        return RepresentationLifecycle(
            lifecycle_identity=self.lifecycle_identity,
            representation_id=self.representation_id,
            origin_event=self.origin_event,
            transitions=self.transitions + (new_transition,),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary for serialization."""
        return {
            "lifecycle_identity": self.lifecycle_identity,
            "representation_id": self.representation_id,
            "origin_event": self.origin_event.to_dict(),
            "transitions": [t.to_dict() for t in self.transitions],
            "current_state": self.current_state.value,
            "transition_count": len(self.transitions),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationLifecycle":
        """Create history from dictionary."""
        transitions = []
        for t_data in data.get("transitions", []):
            transitions.append(RepresentationLifecycleTransition.from_dict(t_data))
        
        return cls(
            lifecycle_identity=data.get("lifecycle_identity", str(uuid.uuid4())),
            representation_id=data.get("representation_id", ""),
            origin_event=RepresentationLifecycleTransition.from_dict(data.get("origin_event", {})),
            transitions=tuple(transitions),
        )


# =============================================================================
# LIFECYCLE MANAGER - Manage state transitions
# =============================================================================


class RepresentationLifecycleManager:
    """
    Manages lifecycle state transitions for representations.
    
    Provides utilities for working with lifecycle history, including:
        - Validating allowed transitions
        - Retrieving historical states
        - Managing regeneration workflows
    
    Allowed transitions:
        CREATED -> ACTIVE (initial publication)
        
        From ACTIVE:
            -> STALE (model/ontology changed, needs regeneration)
            -> SUPERSEDED (replaced by newer representation)
            -> DEPRECATED (marked as outdated)
            -> ARCHIVED (preserved for historical purposes)
        
        From STALE:
            -> REGENERATING (currently being regenerated)
        
        From REGENERATING:
            -> ACTIVE (regeneration complete)
            -> INVALID (regeneration failed)
    """
    
    # Define allowed transitions
    ALLOWED_TRANSITIONS: Dict[RepresentationLifecycleState, List[RepresentationLifecycleState]] = {
        RepresentationLifecycleState.CREATED: [
            RepresentationLifecycleState.ACTIVE,
            RepresentationLifecycleState.INVALID,
        ],
        RepresentationLifecycleState.ACTIVE: [
            RepresentationLifecycleState.STALE,
            RepresentationLifecycleState.SUPERSEDED,
            RepresentationLifecycleState.DEPRECATED,
            RepresentationLifecycleState.INVALID,
        ],
        RepresentationLifecycleState.STALE: [RepresentationLifecycleState.REGENERATING],
        RepresentationLifecycleState.REGENERATING: [
            RepresentationLifecycleState.ACTIVE,
            RepresentationLifecycleState.INVALID,
        ],
        RepresentationLifecycleState.SUPERSEDED: [
            RepresentationLifecycleState.ARCHIVED,
            RepresentationLifecycleState.INVALID,
        ],
        RepresentationLifecycleState.DEPRECATED: [],
        RepresentationLifecycleState.ARCHIVED: [],
        RepresentationLifecycleState.INVALID: [],  # Invalid is terminal state
    }
    
    def __init__(
        self,
        validate_transitions: bool = True,
    ):
        """
        Initialize the lifecycle manager.
        
        Args:
            validate_transitions: Whether to enforce allowed transitions
        """
        self._validate_transitions = validate_transitions
    
    def can_transition(
        self,
        from_state: RepresentationLifecycleState,
        to_state: RepresentationLifecycleState,
    ) -> bool:
        """
        Check if a transition is allowed.
        
        Args:
            from_state: Current lifecycle state
            to_state: Target lifecycle state
            
        Returns:
            True if the transition is allowed
        """
        allowed = self.ALLOWED_TRANSITIONS.get(from_state, [])
        return to_state in allowed
    
    def validate_transition(
        self,
        from_state: RepresentationLifecycleState,
        to_state: RepresentationLifecycleState,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a proposed transition.
        
        Args:
            from_state: Current lifecycle state
            to_state: Target lifecycle state
            
        Returns:
            (is_valid, error_message if invalid)
        """
        if not self.can_transition(from_state, to_state):
            return False, f"Transition from {from_state.value} to {to_state.value} is not allowed"
        
        # Special case: Invalid state has no outgoing transitions
        if from_state == RepresentationLifecycleState.INVALID:
            return False, "Cannot transition from INVALID state"
        
        return True, None
    
    def get_history(self, lifecycle: RepresentationLifecycle) -> List[Dict[str, Any]]:
        """
        Get complete lifecycle history with details.
        
        Args:
            lifecycle: RepresentationLifecycle to analyze
            
        Returns:
            List of transition records with timestamps
        """
        result = []
        all_transitions = (lifecycle.origin_event,) + lifecycle.transitions
        for t in all_transitions:
            result.append({
                "transition_identity": t.transition_identity,
                "from_state": t.from_state.value,
                "to_state": t.to_state.value,
                "reason": t.reason,
                "timestamp_utc": t.timestamp_utc,
                "actor_type": t.actor_type,
            })
        return result
    
    def get_state_at_transition(
        self,
        lifecycle: RepresentationLifecycle,
        transition_index: int,
    ) -> Optional[RepresentationLifecycleState]:
        """
        Get the lifecycle state at a specific transition.
        
        Args:
            lifecycle: The lifecycle history
            transition_index: 0-indexed transition number
            
        Returns:
            State after that transition, or None if invalid
        """
        if transition_index < 0:
            return None
        
        all_transitions = (lifecycle.origin_event,) + lifecycle.transitions
        if transition_index >= len(all_transitions):
            return lifecycle.current_state
        
        return all_transitions[transition_index].to_state


__all__ = [
    # Lifecycle states
    "RepresentationLifecycleState",
    
    # Transition record
    "RepresentationLifecycleTransition",
    
    # History chain
    "RepresentationLifecycle",
    
    # Manager utilities
    "RepresentationLifecycleManager",
]