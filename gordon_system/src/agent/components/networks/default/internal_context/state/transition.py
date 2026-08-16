# Internal Context Transition Model
# =================================

"""
Transition model for internal context evolution.

A transition is an immutable record of how a context changed, not a mutation
of the original context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


ContextTransitionId = str
"""Unique identifier for a context transition record."""


@dataclass(frozen=True, slots=True)
class InternalContextTransition:
    """
    Immutable record of how a context evolved.
    
    A transition records what changed between context versions without
    mutating the original. The original context remains unchanged; a new
    transition record is created to document the evolution.
    
    TRANSITION CATEGORIES:
        • created: New context assembled from scratch
        • refreshed: Context updated with fresh projections
        • expanded: Scope widened (more projections added)
        • reduced: Scope narrowed (projections removed due to capacity)
        • revised: Context revised based on validation or new info
        • invalidated: Context became invalid
        • superseded: Context replaced by newer version
    
    PROPERTIES:
        • transition_id: Unique identifier for this transition
        • prior_context_id: ID of the context before change
        • result_context_id: ID of the context after change
        • transition_type: Category of change
        • changed_projections: List of projection kinds that changed
        • removed_projections: List of projection kinds that were removed
        • timestamp: When transition occurred
    """
    
    # Identity
    transition_id: ContextTransitionId
    """Unique identifier for this transition."""
    
    prior_context_id: str
    """ID of the context before this change."""
    
    result_context_id: str
    """ID of the context after this change (new if created)."""
    
    # Transition details
    transition_type: str  # ContextTransitionType.*
    """Category of change that occurred."""
    
    timestamp_utc: datetime
    """When the transition occurred."""
    
    # Change records
    changed_projections: Tuple[str, ...] = field(default_factory=tuple)
    """Projection kinds that were modified."""
    
    removed_projections: Tuple[str, ...] = field(default_factory=tuple)
    """Projection kinds that were removed."""
    
    added_projections: Tuple[str, ...] = field(default_factory=tuple)
    """Projection kinds that were newly added."""
    
    # Reasoning (optional)
    reason: Optional[str] = None
    """Human-readable explanation of the change."""
    
    # Metadata
    confidence_change: Optional[float] = None
    """Change in overall confidence (-1.0 to 1.0)."""
    
    completeness_change: Optional[str] = None
    """Change in completeness status (before -> after format)."""
    
    @classmethod
    def create(
        cls,
        prior_context_id: str,
        result_context_id: str,
        transition_type: str,
        timestamp_utc: datetime,
        reason: Optional[str] = None,
    ) -> InternalContextTransition:
        """Create a new context transition record."""
        return cls(
            transition_id=f"transition_{prior_context_id}_{id(transition_type)}",
            prior_context_id=prior_context_id,
            result_context_id=result_context_id,
            transition_type=transition_type,
            timestamp_utc=timestamp_utc,
            reason=reason,
        )
    
    @classmethod
    def created_new(cls, context_id: str, timestamp_utc: datetime) -> InternalContextTransition:
        """Create a 'created' transition for a new context."""
        return cls(
            transition_id=f"transition_created_{context_id}",
            prior_context_id="none",
            result_context_id=context_id,
            transition_type="created",
            timestamp_utc=timestamp_utc,
            reason="New context assembled from projections",
        )
    
    @classmethod
    def superseded(cls, old_context_id: str, new_context_id: str, timestamp_utc: datetime) -> InternalContextTransition:
        """Create a 'superseded' transition."""
        return cls(
            transition_id=f"transition_superseded_{old_context_id}",
            prior_context_id=old_context_id,
            result_context_id=new_context_id,
            transition_type="superseded",
            timestamp_utc=timestamp_utc,
            reason="Context superseded by newer assembly",
        )
    
    def to_dict(self) -> dict[str, str | int]:
        """Convert to serializable dictionary."""
        return {
            "transition_id": self.transition_id,
            "prior_context_id": self.prior_context_id,
            "result_context_id": self.result_context_id,
            "transition_type": self.transition_type,
            "timestamp_utc": (
                self.timestamp_utc.isoformat()
                if hasattr(self.timestamp_utc, "isoformat")
                else str(self.timestamp_utc)
            ),
            "changed_projection_count": len(self.changed_projections),
        }