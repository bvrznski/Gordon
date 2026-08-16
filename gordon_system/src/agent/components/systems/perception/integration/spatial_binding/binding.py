# Spatial Binding - Phase 5.2.3
# ============================

"""
Core spatial binding logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class SpatialBinding:
    """
    A spatial binding of artifacts into a coherent structure.
    
    Fields:
        binding_identity: Unique identifier
        bound_artifacts: Which artifacts are bound together?
        reference_frame: Spatial reference frame used
        spatial_relations: Relations between artifacts
        topology: Topological relationships
        geometry: Geometric constraints
        hierarchy: Hierarchical structure (if any)
        occlusion: Occlusion information
    """
    
    binding_identity: str
    
    bound_artifacts: Tuple[str, ...]
    
    reference_frame: Dict[str, Any] = field(default_factory=dict)  # frame definition
    spatial_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    topology: Tuple[str, ...] = field(default_factory=tuple)
    geometry: Dict[str, Any] = field(default_factory=dict)
    hierarchy: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    occlusion: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


class SpatialRelation:
    """Spatial relations between artifacts."""
    
    CONTAINS = "contains"
    INSIDE = "inside"
    OVERLAPS = "overlaps"
    ADJACENT_TO = "adjacent_to"
    ABOVE = "above"
    BELOW = "below"
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"
    IN_FRONT_OF = "in_front_of"
    BEHIND = "behind"
    CONNECTED_TO = "connected_to"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    MEMBER_OF = "member_of"
    OCCLUDES = "occludes"
    COLOCATED_WITHIN_TOLERANCE = "colocated_within_tolerance"


@dataclass(frozen=True)
class Occlusion:
    """
    An occlusion relationship between artifacts.
    
    Fields:
        occlusion_identity: Unique identifier
        occluding_artifact: Which artifact is occluding?
        occluded_artifact: Which artifact is occluded?
        affected_region: Where is the occlusion?
        affected_interval: When does it occur?
        visibility_fraction: How visible remains? (0.0-1.0)
    """
    
    occlusion_identity: str
    
    occluding_artifact: str
    occluded_artifact: str
    
    affected_region: Dict[str, Any] = field(default_factory=dict)  # spatial region
    affected_interval: Dict[str, float] = field(default_factory=dict)  # time range
    
    visibility_fraction: float = 0.5  # 0.0-1.0
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)