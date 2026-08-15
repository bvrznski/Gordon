# Internal Episode Transition Model
# ================================

"""
Transition model for internal episode state evolution.

A transition is an immutable record of how an episode changed, not a mutation
of the original episode.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InternalEpisodeTransition:
    """
    Immutable record of how an episode evolved.
    
    A transition records what changed between episode versions without
    mutating the original. The original episode remains unchanged; a new
    transition record is created to document the evolution.
    
    TRANSITION CATEGORIES:
        • created: New episode was validated from request
        • step_started: Plan step began processing
        • step_completed: Plan step finished successfully
        • evidence_added: New evidence item added to collection
        • conflict_recorded: Conflict detected and recorded
        • capability_requested: Capability request issued
        • capability_result_accepted: Result accepted from capability owner
        • context_refreshed: Context binding was refreshed
        • state_changed: Lifecycle state changed
        • outcome_proposed: Outcome proposed by coordinator
        • completed: Episode produced terminal outcome
        
    PROPERTIES:
        • transition_id: Unique identifier for this transition
        • prior_episode_id: ID of the episode before change
        • result_episode_id: ID of the episode after change
        • transition_type: Category of change
        • changed_fields: List of fields that changed
        • timestamp: When transition occurred
    """
    
    # Identity
    transition_id: str
    """Unique identifier for this transition."""
    
    prior_episode_id: str
    """ID of the episode before this change."""
    
    result_episode_id: str
    """ID of the episode after this change (new if created)."""
    
    # Transition details
    transition_type: str
    """Category of change that occurred."""
    
    timestamp_utc: datetime
    """When the transition occurred."""
    
    # Change records
    changed_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that were modified."""
    
    removed_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs that were removed (if any)."""
    
    added_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs that were newly added."""
    
    # Reasoning (optional)
    reason: Optional[str] = None
    """Human-readable explanation of the change."""
    
    @classmethod
    def create(
        cls,
        prior_episode_id: str,
        result_episode_id: str,
        transition_type: str,
        timestamp_utc: datetime,
        reason: Optional[str] = None,
    ) -> InternalEpisodeTransition:
        """Create a new episode transition record."""
        return cls(
            transition_id=f"transition_{prior_episode_id}_{id(transition_type)}",
            prior_episode_id=prior_episode_id,
            result_episode_id=result_episode_id,
            transition_type=transition_type,
            timestamp_utc=timestamp_utc,
            reason=reason,
        )
    
    @classmethod
    def created_new(cls, episode_id: str, timestamp_utc: datetime) -> InternalEpisodeTransition:
        """Create a 'created' transition for a new episode."""
        return cls(
            transition_id=f"transition_created_{episode_id}",
            prior_episode_id="none",
            result_episode_id=episode_id,
            transition_type="created",
            timestamp_utc=timestamp_utc,
            reason="New episode validated from request",
        )
    
    @classmethod
    def superseded(cls, old_episode_id: str, new_episode_id: str, timestamp_utc: datetime) -> InternalEpisodeTransition:
        """Create a 'superseded' transition."""
        return cls(
            transition_id=f"transition_superseded_{old_episode_id}",
            prior_episode_id=old_episode_id,
            result_episode_id=new_episode_id,
            transition_type="superseded",
            timestamp_utc=timestamp_utc,
            reason="Episode superseded by newer version",
        )
    
    def to_dict(self) -> dict[str, str | int]:
        """Convert to serializable dictionary."""
        return {
            "transition_id": self.transition_id,
            "prior_episode_id": self.prior_episode_id,
            "result_episode_id": self.result_episode_id,
            "transition_type": self.transition_type,
            "timestamp_utc": (
                self.timestamp_utc.isoformat()
                if hasattr(self.timestamp_utc, "isoformat")
                else str(self.timestamp_utc)
            ),
            "changed_field_count": len(self.changed_fields),
        }