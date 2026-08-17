# Spatial Entity Set - Phase 7.9
# ==============================

"""
Canonical Spatial Entity Set.

Spatial reasoning operates over explicit Spatial Entity Sets.
Entity Sets define participating entities, reference frames, and constraints.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EntityKind(Enum):
    """Kinds of spatial entities."""
    
    OBJECT = "object"                    # Physical or abstract object
    REGION = "region"                   # Volume in space
    BOUNDARY = "boundary"               # Surface separating regions
    SURFACE = "surface"                 # 2D manifold in space
    PATH = "path"                       # 1D curve through space
    VOLUME = "volume"                   # 3D extent in space
    POINT = "point"                     # Zero-dimensional location
    RELATION = "relation"               # Spatial relationship


class GeometryType(Enum):
    """Types of geometric representations."""
    
    POLYGON = "polygon"                 # 2D polygonal shape
    POLYHEDRON = "polyhedron"          # 3D polyhedral volume
    CIRCLE = "circle"                  # Circular region
    SPHERE = "sphere"                  # Spherical volume
    ELLIPSOID = "ellipsoid"            # Ellipsoidal volume
    LINE = "line"                      # Line segment
    POINT_CLOUD = "point_cloud"        # Set of discrete points
    MESH = "mesh"                      # Triangulated surface or volume
    COMPOSITE = "composite"            # Composite of multiple types


@dataclass(frozen=True)
class SpatialEntity:
    """
    Explicit spatial entity participating in reasoning.
    
    Entities remain explicit and never possess implicit spatial extents.
    """
    
    # Identity
    entity_id: str                      # Unique entity identifier
    
    # Entity kind
    kind: EntityKind                    # What kind of entity is this?
    
    # Geometry - explicit representation
    geometry_type: Optional[GeometryType] = None  # Type of geometric representation
    vertices: Tuple[Tuple[float, float, float], ...] = ()  # Vertices for polygonal forms
    faces: Tuple[Tuple[int, ...], ...] = ()  # Face connectivity
    edges: Tuple[Tuple[int, int], ...] = ()  # Edge connectivity
    
    # Reference frame - explicit
    reference_frame: Optional[str] = None   # Frame this entity is defined in
    origin_offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Offset from frame origin
    rotation_quaternion: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)  # w,x,y,z
    
    # Spatial extent - explicit measurements
    bounds_min: Tuple[float, float, float] = (float('inf'), float('inf'), float('inf'))
    bounds_max: Tuple[float, float, float] = (float('-inf'), float('-inf'), float('-inf'))
    bounding_radius: float = 0.0
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from reasoning
    origin_context: str = "unknown"              # Where did entity originate?
    
    @property
    def center(self) -> Tuple[float, float, float]:
        """Return center point of bounding box."""
        cx = (self.bounds_min[0] + self.bounds_max[0]) / 2.0
        cy = (self.bounds_min[1] + self.bounds_max[1]) / 2.0
        cz = (self.bounds_min[2] + self.bounds_max[2]) / 2.0
        return (cx, cy, cz)
    
    @property
    def is_valid(self) -> bool:
        """Check if entity has valid geometry."""
        if self.geometry_type is None:
            return False
        if self.reference_frame is None:
            return False
        if self.bounds_min[0] >= self.bounds_max[0]:
            return False
        return True


@dataclass(frozen=True)
class SpatialEntitySet:
    """
    Immutable set of spatial entities and constraints.
    
    Entity Sets remain immutable during reasoning.
    """
    
    # Identity
    entity_set_id: str                      # Unique identifier
    
    # Participating entities
    participating_entities: Tuple[SpatialEntity, ...] = ()   # All entities in set
    
    # Reference frames - all frames used
    reference_frames: Tuple[str, ...] = ()                   # Frame names used
    
    # Constraints on reasoning
    constraints: Tuple[str, ...] = ()                        # Reasoning constraints
    maximum_distance: Optional[float] = None                 # Max distance for relation analysis
    minimum_separation: Optional[float] = None               # Min separation for distinctness
    
    # Environment boundaries
    world_bounds_min: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    world_bounds_max: Tuple[float, float, float] = (100.0, 100.0, 100.0)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from another set
    
    @property
    def entity_count(self) -> int:
        """Return number of participating entities."""
        return len(self.participating_entities)
    
    @property
    def frame_count(self) -> int:
        """Return number of reference frames used."""
        return len(self.reference_frames)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        entities: List[SpatialEntity],
        constraints: Optional[List[str]] = None,
        reference_frames: Optional[List[str]] = None,
    ) -> SpatialEntitySet:
        """Create a new spatial entity set."""
        return cls(
            entity_set_id=f"entity_set:{uuid.uuid4().hex[:16]}",
            participating_entities=tuple(entities),
            constraints=tuple(constraints or []),
            reference_frames=tuple(reference_frames or []),
            created_at_utc=time.time(),
        )
    
    def get_entity_by_id(self, entity_id: str) -> Optional[SpatialEntity]:
        """Find entity by its identifier."""
        for entity in self.participating_entities:
            if entity.entity_id == entity_id:
                return entity
        return None
    
    def filter_by_kind(self, kind: EntityKind) -> Tuple[SpatialEntity, ...]:
        """Return entities of a specific kind."""
        return tuple(e for e in self.participating_entities if e.kind == kind)
    
    def update_entity(
        self,
        updated_entity: SpatialEntity
    ) -> SpatialEntitySet:
        """Return new set with one entity replaced."""
        new_entities = []
        found = False
        for e in self.participating_entities:
            if e.entity_id == updated_entity.entity_id:
                new_entities.append(updated_entity)
                found = True
            else:
                new_entities.append(e)
        if not found:
            new_entities.append(updated_entity)
        
        return dataclass_replace(
            self,
            participating_entities=tuple(new_entities),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialEntity",
    "SpatialEntitySet", 
    "EntityKind",
    "GeometryType",
]