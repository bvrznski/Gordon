# Coordinate Transformations - Phase 7.9
# ======================================

"""
Canonical Coordinate Transformations.

Coordinate transformations convert representations between reference frames.
Supported examples:
    camera -> world, body -> world, world -> map, object -> local
Transformations remain explicit and reconstructable.
"""

from __future__ import annotations

import time
import uuid
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class TransformMatrix:
    """
    Explicit transformation matrix between frames.
    
    Matrices remain reconstructable and preserve mathematical consistency.
    """
    
    # Identity
    transform_id: str                       # Unique identifier
    
    # Source and target frames
    source_frame: str                       # Frame we're transforming from
    target_frame: str                       # Frame we're transforming to
    
    # Matrix representation (4x4 homogeneous)
    matrix_4x4: Tuple[
        Tuple[float, float, float, float],
        Tuple[float, float, float, float],
        Tuple[float, float, float, float],
        Tuple[float, float, float, float]
    ] = (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    
    # Uncertainty - explicit representation
    uncertainty_matrix: Optional[
        Tuple[
            Tuple[float, float, float],
            Tuple[float, float, float],
            Tuple[float, float, float]
        ]
    ] = None
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    def apply(self, point: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Apply transformation to a 3D point (returns new point)."""
        x, y, z = point
        # Convert to homogeneous coordinates
        px, py, pz, pw = x, y, z, 1.0
        
        # Matrix multiplication
        m = self.matrix_4x4
        rx = m[0][0]*px + m[0][1]*py + m[0][2]*pz + m[0][3]*pw
        ry = m[1][0]*px + m[1][1]*py + m[1][2]*pz + m[1][3]*pw
        rz = m[2][0]*px + m[2][1]*py + m[2][2]*pz + m[2][3]*pw
        
        # Convert back from homogeneous (divide by w)
        if abs(pw) > 1e-10:
            rw = m[3][0]*px + m[3][1]*py + m[3][2]*pz + m[3][3]*pw
            return (rx/rw, ry/rw, rz/rw)
        else:
            return (rx, ry, rz)
    
    def inverse(self) -> TransformMatrix:
        """Return the inverse transformation."""
        # For now, just swap source/target and use identity
        # A full implementation would compute the matrix inverse
        m = self.matrix_4x4
        inv_matrix = (
            (m[0][0], m[1][0], m[2][0], -m[0][3]),
            (m[0][1], m[1][1], m[2][1], -m[1][3]),
            (m[0][2], m[1][2], m[2][2], -m[2][3]),
            (0.0, 0.0, 0.0, 1.0),
        )
        
        # Swap source and target
        return dataclass_replace(
            self,
            matrix_4x4=inv_matrix,
            source_frame=self.target_frame,
            target_frame=self.source_frame,
        )


class FrameType(Enum):
    """Kinds of reference frames."""
    
    WORLD = "world"                         # Global world coordinates
    BODY = "body"                         # Robot/body-centered coordinates
    CAMERA = "camera"                     # Camera-centered coordinates
    OBJECT = "object"                     # Object-centered coordinates
    MAP = "map"                           # Map-fixed coordinates
    LOCAL = "local"                       # Local region coordinates
    SENSOR = "sensor"                     # Sensor-specific coordinates


@dataclass(frozen=True)
class ReferenceFrame:
    """
    Explicit reference frame definition.
    
    Frames remain independently inspectable and never substituted implicitly.
    """
    
    # Identity
    frame_id: str                           # Unique identifier
    
    # Frame kind
    frame_type: FrameType                   # What type of frame?
    
    # Position and orientation
    origin: Tuple[float, float, float]      # Position in parent frame
    rotation_quaternion: Tuple[
        float, float, float, float
    ] = (1.0, 0.0, 0.0, 0.0)               # w, x, y, z
    
    # Parent frame (None if root)
    parent_frame_id: Optional[str] = None
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    def get_transform_to(self, target_frame: ReferenceFrame) -> TransformMatrix:
        """Compute transform from this frame to another."""
        # For now, return identity with proper source/target
        return TransformMatrix(
            transform_id=f"transform:{uuid.uuid4().hex[:16]}",
            source_frame=self.frame_id,
            target_frame=target_frame.frame_id,
        )


@dataclass(frozen=True)
class CoordinateTransformation:
    """
    Result of coordinate transformation between frames.
    
    Transforms remain explicit and deterministic.
    """
    
    # Identity
    transformation_id: str                  # Unique identifier
    
    # Source and target frames
    source_frame: str                       # Frame we're transforming from
    target_frame: str                       # Frame we're transforming to
    
    # Transformation matrix
    transform_matrix: TransformMatrix       # The computed transformation
    
    # Applied to entities (which were transformed)
    applied_to_entity_ids: Tuple[str, ...] = ()
    
    # Reverse transformation available?
    has_inverse: bool = True                # Can compute inverse?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        source_frame: str,
        target_frame: str,
        transform_matrix: TransformMatrix,
        entity_ids: Optional[List[str]] = None,
    ) -> CoordinateTransformation:
        """Create a new coordinate transformation result."""
        return cls(
            transformation_id=f"transform:{uuid.uuid4().hex[:16]}",
            source_frame=source_frame,
            target_frame=target_frame,
            transform_matrix=transform_matrix,
            applied_to_entity_ids=tuple(entity_ids or []),
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def apply_to_point(
        self, 
        point: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """Apply transformation to a 3D point."""
        return self.transform_matrix.apply(point)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CoordinateTransformation",
    "TransformMatrix", 
    "ReferenceFrame",
    "FrameType",
]