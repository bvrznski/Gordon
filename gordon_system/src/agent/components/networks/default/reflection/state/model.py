# Reflection Coordination State
# =============================

"""
Immutable coordination state snapshot for reflection.

ARCHITECTURAL PRINCIPLES:
    - State is bounded (no unbounded growth)
    - No runtime references or live objects
    - Immutable snapshot of coordination status
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class ReflectionCoordinationState:
    """
    Immutable complete state snapshot for reflection coordination.
    
    This is a bounded record of what the DefaultNetwork knows about
    active and ready reflections. It does NOT contain full episode copies
    but rather references and summaries.
    """
    
    # Active reflections (by reference, not full copy)
    active_episode_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    ready_episode_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    waiting_references: Tuple[str, ...] = field(default_factory=tuple)
    
    # Recent activity summaries (bounded history)
    recent_purposes: Tuple[str, ...] = field(default_factory=tuple)
    
    recent_subjects: Tuple[str, ...] = field(default_factory=tuple)
    
    recent_product_digests: Tuple[str, ...] = field(default_factory=tuple)
    
    # Metrics
    unresolved_conflict_count: int = 0
    
    no_result_count: int = 0
    
    state_revision: int = 1
    
    last_state_change_utc: str = ""
    
    @classmethod
    def empty(cls) -> ReflectionCoordinationState:
        """Create an empty coordination state."""
        return cls(
            active_episode_refs=(),
            ready_episode_refs=(),
            waiting_references=(),
            recent_purposes=(),
            recent_subjects=(),
            recent_product_digests=(),
            unresolved_conflict_count=0,
            no_result_count=0,
        )
    
    def can_accept_more_active(self, max_active: int = 5) -> bool:
        """Check if more active reflections can be accepted."""
        return len(self.active_episode_refs) < max_active
    
    def add_recent_purpose(self, purpose_summary: str, max_history: int = 25) -> Tuple[str, ...]:
        """Add a purpose summary to recent history (bounded)."""
        new_history = (purpose_summary,) + self.recent_purposes
        return new_history[:max_history]
    
    def record_no_result(self) -> ReflectionCoordinationState:
        """Record a no-result reflection for attenuation tracking."""
        return ReflectionCoordinationState(
            active_episode_refs=self.active_episode_refs,
            ready_episode_refs=self.ready_episode_refs,
            waiting_references=self.waiting_references,
            recent_purposes=self.recent_purposes,
            recent_subjects=self.recent_subjects,
            recent_product_digests=self.recent_product_digests,
            unresolved_conflict_count=self.unresolved_conflict_count,
            no_result_count=self.no_result_count + 1,
            state_revision=self.state_revision + 1,
        )
    
    def clear_no_result_count(self) -> ReflectionCoordinationState:
        """Reset no-result count (after meaningful result)."""
        return ReflectionCoordinationState(
            active_episode_refs=self.active_episode_refs,
            ready_episode_refs=self.ready_episode_refs,
            waiting_references=self.waiting_references,
            recent_purposes=self.recent_purposes,
            recent_subjects=self.recent_subjects,
            recent_product_digests=self.recent_product_digests,
            unresolved_conflict_count=self.unresolved_conflict_count,
            no_result_count=0,
            state_revision=self.state_revision + 1,
        )