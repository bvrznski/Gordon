# Motivational Projection Network - Projection Hierarchy (Phase 4.10.6)
# ====================================================================

"""
ProjectionHierarchy model for Phase 4.10.6.

This module defines the hierarchical structure of projections across
different levels: actions, tasks, goals, strategies, and missions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict


@dataclass(frozen=True)
class ProjectionHierarchy:
    """
    A hierarchical mapping of projections across different levels.

    HIERARCHY-LAW-001: Projections remain explicit across hierarchy levels.
    HIERARCHY-LAW-002: Cross-level mappings are preserved.
    HIERARCHY-LAW-003: Hierarchy is immutable once constructed.
    
    LEVELS (bottom to top):
        • action: Individual actions
        • task: Sequences of related actions
        • goal: Desired states achieved by tasks
        • strategy: High-level approaches to goals
        • mission: Long-term objectives and values
    """
    
    hierarchy_id: str = "projection_hierarchy"
    """Unique identifier for this hierarchy."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Mapping from projection ID to hierarchy level
    projection_levels: Dict[str, str] = field(default_factory=dict)
    """Maps projection IDs to their hierarchy levels."""
    
    # Parent-child relationships (child -> parents)
    parent_map: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    """Maps child projections to their parent projections."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.hierarchy_id}@v{self.revision}"
    
    def get_level(self, projection_id: str) -> str:
        """Get the hierarchy level for a projection."""
        return self.projection_levels.get(projection_id, "unknown")
    
    def get_parents(self, projection_id: str) -> Tuple[str, ...]:
        """Get parent projections for a given projection."""
        return self.parent_map.get(projection_id, ())
    
    def is_action_level(self, projection_id: str) -> bool:
        """Check if projection is at action level."""
        return self.get_level(projection_id) == "action"
    
    def is_task_level(self, projection_id: str) -> bool:
        """Check if projection is at task level."""
        return self.get_level(projection_id) == "task"
    
    def is_goal_level(self, projection_id: str) -> bool:
        """Check if projection is at goal level."""
        return self.get_level(projection_id) == "goal"
    
    def is_strategy_level(self, projection_id: str) -> bool:
        """Check if projection is at strategy level."""
        return self.get_level(projection_id) == "strategy"
    
    def is_mission_level(self, projection_id: str) -> bool:
        """Check if projection is at mission level."""
        return self.get_level(projection_id) == "mission"
    
    def get_all_projections_at_level(self, level: str) -> Tuple[str, ...]:
        """Get all projections at a specific hierarchy level."""
        return tuple(
            pid for pid, lvl in self.projection_levels.items() 
            if lvl == level
        )
    
    def to_dict(self) -> dict:
        """Convert hierarchy to dictionary representation."""
        return {
            "hierarchy_id": self.hierarchy_id,
            "revision": self.revision,
            "projection_levels": self.projection_levels.copy(),
            "parent_map": {k: list(v) for k, v in self.parent_map.items()},
        }
    
    @classmethod
    def create_empty(cls, hierarchy_id: str = "projection_hierarchy") -> ProjectionHierarchy:
        """Create an empty projection hierarchy."""
        return cls(hierarchy_id=hierarchy_id)
    
    @classmethod
    def from_levels(
        cls,
        projection_levels: Dict[str, str],
        parent_map: Dict[str, Tuple[str, ...]] = None,
        hierarchy_id: str = "projection_hierarchy",
    ) -> ProjectionHierarchy:
        """Create a hierarchy from projection levels and parent map."""
        return cls(
            hierarchy_id=hierarchy_id,
            revision=0,
            projection_levels=dict(projection_levels),
            parent_map=dict(parent_map) if parent_map else {},
        )


__all__ = ["ProjectionHierarchy"]