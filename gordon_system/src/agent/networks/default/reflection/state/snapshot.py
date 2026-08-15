# Reflection State Snapshots
# ==========================

"""
Immutable state snapshots for reflection coordination.

ARCHITECTURAL PRINCIPLES:
    - Snapshots preserve full state at a point in time
    - No runtime references or live objects
    - Immutable and serializable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class ReflectionSnapshot:
    """
    Immutable complete snapshot of reflection coordination state.
    
    A snapshot is a point-in-time view of all active reflections and
    their states. Snapshots are used for recovery, auditing, and
    deterministic replay.
    """
    
    timestamp_utc: str = ""
    """When this snapshot was taken (ISO format)."""
    
    state_revision: int = 1
    """Revision number of the state."""
    
    active_episode_snapshots: Tuple[str, ...] = field(default_factory=tuple)
    """Active episode snapshots (references only)."""
    
    ready_episode_snapshots: Tuple[str, ...] = field(default_factory=tuple)
    """Ready episode snapshots (references only)."""
    
    waiting_episode_snapshots: Tuple[str, ...] = field(default_factory=tuple)
    """Waiting episode snapshots (references only)."""
    
    recent_outcomes: Tuple[str, ...] = field(default_factory=tuple)
    """Recent outcome summaries."""
    
    unresolved_conflict_count: int = 0
    """Count of unresolved contradictions."""
    
    @classmethod
    def from_state(cls, coordination_state) -> ReflectionSnapshot:
        """
        Create a snapshot from a coordination state.
        
        Args:
            coordination_state: The state to snapshot
            
        Returns:
            New ReflectionSnapshot instance
        """
        return cls(
            timestamp_utc="",
            state_revision=coordination_state.state_revision if hasattr(coordination_state, 'state_revision') else 1,
            active_episode_snapshots=getattr(coordination_state, 'active_episode_refs', ()),
            ready_episode_snapshots=getattr(coordination_state, 'ready_episode_refs', ()),
            waiting_episode_snapshots=getattr(coordination_state, 'waiting_references', ()),
            recent_outcomes=(),
            unresolved_conflict_count=getattr(coordination_state, 'unresolved_conflict_count', 0),
        )