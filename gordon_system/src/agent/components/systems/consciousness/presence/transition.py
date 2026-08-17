# Gordon Phase 5.7.5-I: Presence Engine - Transition Model
# ===============================================================================
"""
Immutable transition model for presence state changes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class PresenceTransition:
    """
    Immutable record of a presence state change.
    
    Transitions track when and why items changed state, enabling replay
    and audit without exposing mutable runtime state.
    """
    
    item_id: str
    """ID of the item being transitioned."""
    
    from_state: str
    """Previous state (from)."""
    
    to_state: str
    """New state (to)."""
    
    kind: str = "default"
    """Transition kind (admission, withdrawal, fade_start, resume, interrupt)."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the transition occurred."""
    
    reason: Optional[str] = None
    """Reason for this transition (policy violation, expiration, etc.)."""
    
    source_id: str = ""
    """Source that proposed the item (if known)."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing across systems."""
    
    causation_id: Optional[str] = None
    """Causation ID for tracking decision chains."""
    
    transition_id: str = field(default_factory=lambda: f"pt-{_generate_uuid()}")
    """Unique identifier for this transition."""
    
    @property
    def is_admission(self) -> bool:
        """Check if this is an admission transition."""
        return self.kind == "admission"
    
    @property
    def is_withdrawal(self) -> bool:
        """Check if this is a withdrawal transition."""
        return self.kind == "withdrawal"
    
    @property
    def is_fade_start(self) -> bool:
        """Check if this starts the fading process."""
        return self.kind == "fade_start"
    
    @classmethod
    def admission(
        cls,
        item_id: str,
        source_id: str = "",
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> "PresenceTransition":
        """Create an admission transition."""
        return cls(
            item_id=item_id,
            from_state="candidate",
            to_state="admitted",
            kind="admission",
            source_id=source_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
    
    @classmethod
    def fade_start(
        cls,
        item_id: str,
        reason: Optional[str] = None,
        source_id: str = "",
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> "PresenceTransition":
        """Create a fade-start transition (active → weakening)."""
        return cls(
            item_id=item_id,
            from_state="active",
            to_state="weakening",
            kind="fade_start",
            reason=reason,
            source_id=source_id,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
    
    @classmethod
    def fade_advance(
        cls,
        item_id: str,
        from_state: str,
        to_state: str,
        reason: Optional[str] = None,
    ) -> "PresenceTransition":
        """Create a fade-advance transition (weakening → fading or fading → withdrawn)."""
        return cls(
            item_id=item_id,
            from_state=from_state,
            to_state=to_state,
            kind="fade_advance",
            reason=reason,
        )
    
    @classmethod
    def resume(
        cls,
        item_id: str,
        source_id: str = "",
    ) -> "PresenceTransition":
        """Create a resume transition (suspended → active)."""
        return cls(
            item_id=item_id,
            from_state="suspended",
            to_state="active",
            kind="resume",
            source_id=source_id,
        )
    
    @classmethod
    def interrupt(
        cls,
        item_id: str,
        reason: Optional[str] = None,
    ) -> "PresenceTransition":
        """Create an interrupt transition (active → suspended)."""
        return cls(
            item_id=item_id,
            from_state="active",
            to_state="suspended",
            kind="interrupt",
            reason=reason,
        )


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class TransitionBatch:
    """
    Immutable record of multiple transitions.
    
    Used for batch operations and replay scenarios where all transitions
    need to be tracked together.
    """
    
    batch_id: str = field(default_factory=lambda: f"tb-{_generate_uuid()}")
    """Unique identifier for this transition batch."""
    
    generation: int = 0
    """Generation when these transitions occurred."""
    
    transitions: Tuple[PresenceTransition, ...] = field(default_factory=tuple)
    """List of transitions in this batch."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the batch was committed."""
    
    @property
    def transition_count(self) -> int:
        """Number of transitions in this batch."""
        return len(self.transitions)
    
    @classmethod
    def from_transitions(
        cls,
        *transitions: PresenceTransition,
        generation: int = 0,
    ) -> "TransitionBatch":
        """Create a transition batch from individual transitions."""
        return cls(
            generation=generation,
            transitions=tuple(transitions),
        )