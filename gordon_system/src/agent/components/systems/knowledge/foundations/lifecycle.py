# Knowledge Lifecycle - Phase 6.1
# ================================

"""
Semantic Lifecycle: Artifact maturity progression in Gordon's knowledge system.

The semantic lifecycle defines the states an artifact progresses through:
    CREATED     -> Initial creation (not yet validated)
    DRAFT       -> Work-in-progress state  
    VALIDATING  -> Under validation review
    CERTIFIED   -> Passed validation, ready for publication
    ACTIVE      -> Published and in use
    REVISED     -> Has been superseded by newer revision
    SUPERSEDED  -> Replaced by another artifact
    DEPRECATED  -> Marked as outdated but still referenced
    ARCHIVED    -> Preserved for historical purposes
    INVALID     -> Failed validation, not for use

Lifecycle represents semantic maturity. It does not represent persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# LIFECYCLE STATES - Artifact maturity progression
# =============================================================================


class LifecycleState(Enum):
    """
    States of semantic artifact lifecycle progression.
    
    Defines the maturity states an artifact transitions through:
        CREATED     -> Initial creation (not yet validated)
        DRAFT       -> Work-in-progress state
        VALIDATING  -> Under validation review
        CERTIFIED   -> Passed validation, ready for publication
        ACTIVE      -> Published and in use
        REVISED     -> Has been superseded by newer revision
        SUPERSEDED  -> Replaced by another artifact
        DEPRECATED  -> Marked as outdated but still referenced
        ARCHIVED    -> Preserved for historical purposes
        INVALID     -> Failed validation, not for use
    """
    
    CREATED = "created"
    DRAFT = "draft"
    VALIDATING = "validating"
    CERTIFIED = "certified"
    ACTIVE = "active"
    REVISED = "revised"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    INVALID = "invalid"


# =============================================================================
# LIFECYCLE TRANSITION - State change record
# =============================================================================


@dataclass(frozen=True)
class LifecycleTransition:
    """
    Record of a lifecycle state transition.
    
    Tracks when and why an artifact changed states, providing complete auditability.
    
    Fields:
        transition_identity: Unique identifier for this transition
        semantic_identity:   Identity of artifact that changed states
        from_state:          Previous lifecycle state
        to_state:            New lifecycle state
        reason:              Why the transition occurred
        timestamp_utc:       When transition occurred
        actor_type:          Type of actor (system, user, reasoning)
        actor_id:            ID of actor performing transition
    """
    
    # Identity and metadata (required)
    transition_identity: str              # Unique transition identifier
    
    semantic_identity: str                # Artifact identity
    
    from_state: LifecycleState            # Previous state
    to_state: LifecycleState              # New state
    
    reason: Optional[str] = None          # Transition reason
    timestamp_utc: float = field(default_factory=time.time)
    
    actor_type: str = "system"            # e.g., "system", "user", "reasoning"
    actor_id: str = ""                    # Actor identifier
    
    @property
    def is_valid(self) -> bool:
        """Check if transition has valid data."""
        return (
            len(self.transition_identity) > 0 and
            len(self.semantic_identity) > 0 and
            self.from_state != LifecycleState.INVALID and
            self.to_state != LifecycleState.INVALID
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition to dictionary for serialization."""
        return {
            "transition_identity": self.transition_identity,
            "semantic_identity": self.semantic_identity,
            "from_state": self.from_state.value if hasattr(self.from_state, 'value') else str(self.from_state),
            "to_state": self.to_state.value if hasattr(self.to_state, 'value') else str(self.to_state),
            "reason": self.reason,
            "timestamp_utc": self.timestamp_utc,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LifecycleTransition":
        """Create transition from dictionary."""
        return cls(
            transition_identity=data.get("transition_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            from_state=LifecycleState(data.get("from_state", "created")),
            to_state=LifecycleState(data.get("to_state", "created")),
            reason=data.get("reason"),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            actor_type=data.get("actor_type", "system"),
            actor_id=data.get("actor_id", ""),
        )


# =============================================================================
# LIFECYCLE HISTORY - Complete progression chain
# =============================================================================


@dataclass(frozen=True)
class LifecycleHistory:
    """
    Complete lifecycle history for an artifact.
    
    Maintains the full sequence of state transitions from initial creation to current state.
    
    Fields:
        lifecycle_identity:  Unique identifier for this lifecycle record
        origin_event:        The first state transition (creation) in the history
        transitions:         All state transitions in chronological order
        current_state:       Current lifecycle state after all transitions
    """
    
    # Identity and metadata (required)
    lifecycle_identity: str               # Unique lifecycle ID
    
    origin_event: LifecycleTransition     # The original creation transition
    transitions: Tuple[LifecycleTransition, ...] = field(default_factory=tuple)  # All transitions
    
    @property
    def current_state(self) -> LifecycleState:
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
        semantic_identity: str,
        actor_type: str = "system",
        actor_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> "LifecycleHistory":
        """
        Create initial lifecycle history with creation transition.
        
        Args:
            semantic_identity: Identity of artifact
            actor_type: Type of actor creating the artifact
            actor_id: ID of actor
            context: Creation context (optional)
            
        Returns:
            New LifecycleHistory with single creation transition
        """
        origin_event = LifecycleTransition(
            transition_identity=f"transition:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            from_state=LifecycleState.CREATED,
            to_state=LifecycleState.DRAFT,  # Initial state after creation is draft
            reason="Initial artifact creation",
            timestamp_utc=time.time(),
            actor_type=actor_type,
            actor_id=actor_id,
        )
        
        return cls(
            lifecycle_identity=f"lifecycle:{uuid.uuid4().hex[:16]}",
            origin_event=origin_event,
            transitions=tuple([origin_event]),
        )
    
    def append_transition(
        self,
        to_state: LifecycleState,
        reason: Optional[str] = None,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> "LifecycleHistory":
        """
        Create a new history with an additional transition appended.
        
        Args:
            to_state: Target lifecycle state
            reason: Transition reason (optional)
            actor_type: Type of actor (optional, defaults to last)
            actor_id: ID of actor (optional, defaults to last)
            
        Returns:
            New LifecycleHistory with added transition
        """
        new_transition = LifecycleTransition(
            transition_identity=f"transition:{uuid.uuid4().hex[:16]}",
            semantic_identity=self.origin_event.semantic_identity,
            from_state=self.current_state,
            to_state=to_state,
            reason=reason,
            timestamp_utc=time.time(),
            actor_type=actor_type or self.transitions[-1].actor_type if self.transitions else "system",
            actor_id=actor_id or self.transitions[-1].actor_id if self.transitions else "",
        )
        
        return LifecycleHistory(
            lifecycle_identity=self.lifecycle_identity,
            origin_event=self.origin_event,
            transitions=self.transitions + (new_transition,),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary for serialization."""
        return {
            "lifecycle_identity": self.lifecycle_identity,
            "origin_event": self.origin_event.to_dict(),
            "transitions": [t.to_dict() for t in self.transitions],
            "current_state": self.current_state.value,
            "transition_count": len(self.transitions),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LifecycleHistory":
        """Create history from dictionary."""
        transitions = []
        for t_data in data.get("transitions", []):
            transitions.append(LifecycleTransition.from_dict(t_data))
        
        return cls(
            lifecycle_identity=data.get("lifecycle_identity", str(uuid.uuid4())),
            origin_event=LifecycleTransition.from_dict(data.get("origin_event", {})),
            transitions=tuple(transitions),
        )


# =============================================================================
# LIFECYCLE MANAGER - Manage state transitions
# =============================================================================


class LifecycleManager:
    """
    Manages lifecycle state transitions for artifacts.
    
    Provides utilities for working with lifecycle history, including:
        - Validating allowed transitions
        - Retrieving historical states
        - Managing revision synchronization
    
    Allowed transitions:
        CREATED -> DRAFT -> VALIDATING -> CERTIFIED -> ACTIVE
        
        From ACTIVE:
            -> REVISED (new version created)
            -> SUPERSEDED (replaced by newer artifact)
            -> DEPRECATED (marked as outdated)
        
        Any state can transition to INVALID for failed validation
    """
    
    # Define allowed transitions
    ALLOWED_TRANSITIONS: Dict[LifecycleState, List[LifecycleState]] = {
        LifecycleState.CREATED: [LifecycleState.DRAFT],
        LifecycleState.DRAFT: [LifecycleState.VALIDATING],
        LifecycleState.VALIDATING: [LifecycleState.CERTIFIED, LifecycleState.INVALID],
        LifecycleState.CERTIFIED: [LifecycleState.ACTIVE, LifecycleState.INVALID],
        LifecycleState.ACTIVE: [
            LifecycleState.REVISED,
            LifecycleState.SUPERSEDED,
            LifecycleState.DEPRECATED,
            LifecycleState.INVALID,
            LifecycleState.ARCHIVED,
        ],
        LifecycleState.REVISED: [LifecycleState.INVALID],
        LifecycleState.SUPERSEDED: [LifecycleState.INVALID, LifecycleState.ARCHIVED],
        LifecycleState.DEPRECATED: [LifecycleState.INVALID, LifecycleState.ARCHIVED],
        LifecycleState.ARCHIVED: [],
        LifecycleState.INVALID: [],  # Invalid is terminal state
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
        from_state: LifecycleState,
        to_state: LifecycleState,
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
        from_state: LifecycleState,
        to_state: LifecycleState,
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
        if from_state == LifecycleState.INVALID:
            return False, "Cannot transition from INVALID state"
        
        return True, None
    
    def get_history(self, history: LifecycleHistory) -> List[Dict[str, Any]]:
        """
        Get complete lifecycle history with details.
        
        Args:
            history: LifecycleHistory to analyze
            
        Returns:
            List of transition records with timestamps
        """
        result = []
        for t in (history.origin_event,) + history.transitions:
            result.append({
                "transition_identity": t.transition_identity,
                "from_state": t.from_state.value,
                "to_state": t.to_state.value,
                "reason": t.reason,
                "timestamp_utc": t.timestamp_utc,
                "actor_type": t.actor_type,
            })
        return result
    
    def get_state_at_revision(
        self,
        history: LifecycleHistory,
        revision_number: int,
    ) -> Optional[LifecycleState]:
        """
        Get the lifecycle state at a specific revision.
        
        Args:
            history: The lifecycle history
            revision_number: 1-indexed revision number
            
        Returns:
            State at that revision, or None if invalid
        """
        if revision_number < 1:
            return None
        
        transitions = list(history.transitions)
        if revision_number - 1 >= len(transitions):
            return history.current_state
        
        return transitions[revision_number - 1].to_state


__all__ = [
    # Lifecycle states
    "LifecycleState",
    # Transition record
    "LifecycleTransition",
    # History chain
    "LifecycleHistory",
    # Manager utilities
    "LifecycleManager",
]