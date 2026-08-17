# Navigation Semantics - Phase 7.9
# ==============================

"""
Canonical Navigation Semantics.

Navigation semantics evaluate:
    reachable regions, obstacles, visibility, clearance, accessibility, connectivity.
    
Navigation remains descriptive (never implies executable motion).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ReachableRegion:
    """
    Region that is reachable from a starting point.
    
    Represents all points accessible via continuous paths.
    """
    
    # Identity
    region_id: str                          # Unique identifier
    
    # Starting point
    start_point: Tuple[float, float, float]  # Where did we start?
    
    # Region definition (simplified as bounds for now)
    bounds_min: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounds_max: Tuple[float, float, float] = (100.0, 100.0, 100.0)
    
    # Connectivity info
    connected_components: int = 1           # Number of reachable components
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""


@dataclass(frozen=True)
class ObstacleSet:
    """
    Set of obstacles affecting navigation.
    
    Obstacles remain explicitly represented (never implicit).
    """
    
    # Identity
    set_id: str                             # Unique identifier
    
    # Obstacles
    obstacles: Tuple[Tuple[float, float, float], ...] = ()  # Positions
    obstacle_bounds: Tuple[
        Tuple[float, float, float],
        Tuple[float, float, float]
    ] = ((0.0, 0.0, 0.0), (10.0, 10.0, 10.0))  # Bounds for all obstacles
    
    # Obstacle properties
    obstacle_count: int = 0                 # Count of obstacles
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""


@dataclass(frozen=True)
class TraversabilityAnalysis:
    """
    Analysis of traversability for a path or region.
    
    Evaluates whether paths are navigable given constraints.
    """
    
    # Identity
    analysis_id: str                        # Unique identifier
    
    # Path analyzed
    path_id: Optional[str] = None           # Which path?
    
    # Traversability result
    is_traversable: bool = False            # Can this be traversed?
    traversability_score: float = 1.0       # 0.0 to 1.0
    
    # Reasons (for non-traversable)
    blocking_reasons: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""


@dataclass(frozen=True)
class NavigationSemantics:
    """
    Result of navigation semantics analysis.
    
    Evaluates reachable regions, obstacles, visibility, clearance,
    accessibility, and connectivity.
    """
    
    # Identity
    navigation_id: str                      # Unique identifier
    
    # Reachability
    reachable_regions: Tuple[ReachableRegion, ...] = ()
    
    # Obstacles
    obstacle_set: ObstacleSet               # All known obstacles
    
    # Traversability analysis
    traversability: Tuple[TraversabilityAnalysis, ...] = ()
    
    # Connectivity graph (topological)
    connectivity_graph_nodes: Tuple[str, ...] = ()  # Region IDs
    connectivity_graph_edges: Tuple[Tuple[str, str], ...] = ()  # Connections
    
    # Clearance analysis (optional)
    minimum_clearance: Optional[float] = None
    maximum_obstacle_height: Optional[float] = None
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def reachable_region_count(self) -> int:
        """Return number of reachable regions."""
        return len(self.reachable_regions)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        obstacle_set: ObstacleSet,
    ) -> NavigationSemantics:
        """Create a new navigation semantics result."""
        return cls(
            navigation_id=f"navigation:{uuid.uuid4().hex[:16]}",
            obstacle_set=obstacle_set,
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def get_region_by_point(
        self, 
        point: Tuple[float, float, float]
    ) -> Optional[ReachableRegion]:
        """Find which reachable region contains this point."""
        # For now, return first region if within bounds
        for region in self.reachable_regions:
            if (region.bounds_min[0] <= point[0] <= region.bounds_max[0] and
                region.bounds_min[1] <= point[1] <= region.bounds_max[1] and
                region.bounds_min[2] <= point[2] <= region.bounds_max[2]):
                return region
        return None


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "NavigationSemantics",
    "ReachableRegion", 
    "ObstacleSet",
    "TraversabilityAnalysis",
]