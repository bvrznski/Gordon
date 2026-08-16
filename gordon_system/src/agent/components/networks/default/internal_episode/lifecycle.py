# Internal Episode Lifecycle Model
# ================================

"""
Lifecycle model for internal episode state transitions.

A lifecycle is an immutable record of how an episode's coordination state changed,
not a mutation of the original episode.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


LifecycleTransitionId = str
"""Unique identifier for a lifecycle transition record."""


@dataclass(frozen=True, slots=True)
class InternalEpisodeLifecycle:
    """
    Immutable record of episode coordination state.
    
    The lifecycle represents semantic coordination state, not runtime execution state.
    Core and Execution handle actual runtime mechanics.
    
    TRANSITION PATHS:
        PROPOSED -> VALIDATED -> READY -> ACTIVE
        ACTIVE -> WAITING_FOR_INPUT, WAITING_FOR_CAPABILITY, SUSPENDED, COMPLETING
        ACTIVE -> FAILED, CANCELLED, EXPIRED
        COMPLETING -> COMPLETED
        
    TERMINAL STATES:
        COMPLETED, FAILED, CANCELLED, EXPIRED, SUPERSEDED
    """
    
    state: str  # InternalEpisodeLifecycle.*
    """Current lifecycle state."""
    
    transition_id: Optional[TransitionRecord] = None
    """Record of the most recent transition (if any)."""
    
    @classmethod
    def proposed(cls) -> InternalEpisodeLifecycle:
        """Create a PROPOSED lifecycle state."""
        return cls(
            state="proposed",
            transition_id=None,
        )
    
    @classmethod
    def validated(
        cls,
        transition_id: LifecycleTransitionId,
        reason: Optional[str] = None,
    ) -> InternalEpisodeLifecycle:
        """Create a VALIDATED lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="proposed",
            target_state="validated",
            timestamp_utc=datetime.utcnow(),
            reason=reason or "Request, purpose, scope, and context binding are valid",
        )
        return cls(state="validated", transition_id=record)
    
    @classmethod
    def ready(cls, transition_id: LifecycleTransitionId) -> InternalEpisodeLifecycle:
        """Create a READY lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="validated",
            target_state="ready",
            timestamp_utc=datetime.utcnow(),
            reason="Episode may be processed when Execution and Core permit",
        )
        return cls(state="ready", transition_id=record)
    
    @classmethod
    def active(cls, transition_id: LifecycleTransitionId) -> InternalEpisodeLifecycle:
        """Create an ACTIVE lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="ready",
            target_state="active",
            timestamp_utc=datetime.utcnow(),
            reason="Bounded episode progression is currently being coordinated",
        )
        return cls(state="active", transition_id=record)
    
    @classmethod
    def completing(cls, transition_id: LifecycleTransitionId) -> InternalEpisodeLifecycle:
        """Create a COMPLETING lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="active",
            target_state="completing",
            timestamp_utc=datetime.utcnow(),
            reason="Outcome composition or final validation in progress",
        )
        return cls(state="completing", transition_id=record)
    
    @classmethod
    def completed(cls, transition_id: LifecycleTransitionId) -> InternalEpisodeLifecycle:
        """Create a COMPLETED lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="completing",
            target_state="completed",
            timestamp_utc=datetime.utcnow(),
            reason="Valid terminal outcome produced",
        )
        return cls(state="completed", transition_id=record)
    
    @classmethod
    def failed(
        cls,
        transition_id: LifecycleTransitionId,
        reason: Optional[str] = None,
    ) -> InternalEpisodeLifecycle:
        """Create a FAILED lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="active",
            target_state="failed",
            timestamp_utc=datetime.utcnow(),
            reason=reason or "Terminated without valid successful outcome",
        )
        return cls(state="failed", transition_id=record)
    
    @classmethod
    def cancelled(cls, transition_id: LifecycleTransitionId) -> InternalEpisodeLifecycle:
        """Create a CANCELLED lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="active",
            target_state="cancelled",
            timestamp_utc=datetime.utcnow(),
            reason="Terminated by authority before normal completion",
        )
        return cls(state="cancelled", transition_id=record)
    
    @classmethod
    def expired(cls, transition_id: LifecycleTransitionId) -> InternalEpisodeLifecycle:
        """Create an EXPIRED lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="active",
            target_state="expired",
            timestamp_utc=datetime.utcnow(),
            reason="Context, scope, or deadline expired",
        )
        return cls(state="expired", transition_id=record)
    
    @classmethod
    def superseded(cls, transition_id: LifecycleTransitionId) -> InternalEpisodeLifecycle:
        """Create a SUPERSEDED lifecycle state."""
        record = TransitionRecord(
            transition_id=transition_id,
            source_state="active",
            target_state="superseded",
            timestamp_utc=datetime.utcnow(),
            reason="Newer episode replaced this episode's purpose or authority",
        )
        return cls(state="superseded", transition_id=record)
    
    def is_terminal(self) -> bool:
        """Check if this lifecycle state is terminal."""
        return self.state in {
            "completed",
            "failed",
            "cancelled",
            "expired",
            "superseded",
        }
    
    def can_transition_to(self, target_state: str) -> bool:
        """
        Check if a transition to the target state is permitted.
        
        Args:
            target_state: The desired target lifecycle state
            
        Returns:
            True if the transition is valid
        """
        # Permitted transitions from each source state
        permitted = {
            "proposed": {"validated"},
            "validated": {"ready"},
            "ready": {"active"},
            "active": {
                "waiting_for_input",
                "waiting_for_capability",
                "suspended",
                "completing",
                "failed",
                "cancelled",
                "expired",
            },
            "waiting_for_input": {"active", "suspended", "failed", "cancelled", "expired"},
            "waiting_for_capability": {"active", "suspended", "failed", "cancelled", "expired"},
            "suspended": {"ready", "failed", "cancelled", "expired"},
            "completing": {"completed", "failed", "cancelled", "expired"},
        }
        
        return target_state in permitted.get(self.state, set())


@dataclass(frozen=True, slots=True)
class TransitionRecord:
    """
    Immutable record of a lifecycle state transition.
    
    Every state change creates a new transition record rather than
    mutating the original episode's lifecycle.
    """
    
    transition_id: LifecycleTransitionId
    """Unique identifier for this transition."""
    
    source_state: str  # InternalEpisodeLifecycle.*
    """The state before the transition."""
    
    target_state: str  # InternalEpisodeLifecycle.*
    """The state after the transition."""
    
    timestamp_utc: datetime
    """When the transition occurred."""
    
    reason: Optional[str] = None
    """Human-readable explanation of the change."""
    
    initiator: Optional[str] = None
    """Who/what caused the transition (optional)."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence references related to this transition."""
    
    @classmethod
    def create(
        cls,
        source_state: str,
        target_state: str,
        reason: Optional[str] = None,
        initiator: Optional[str] = None,
    ) -> TransitionRecord:
        """
        Create a new transition record.
        
        Args:
            source_state: The state before the transition
            target_state: The state after the transition
            reason: Human-readable explanation of the change
            initiator: Who/what caused the transition
            
        Returns:
            New TransitionRecord instance
        """
        return cls(
            transition_id=f"transition_{source_state}_{target_state}_{id(cls)}",
            source_state=source_state,
            target_state=target_state,
            timestamp_utc=datetime.utcnow(),
            reason=reason,
            initiator=initiator,
        )