# Gordon Phase 5.7.6-I: Perspective Engine - Reference Frame
# ===============================================================================
"""
Canonical reference frame representation for the Perspective Engine.

A reference frame establishes the computational origin, orientation, and
coordinate system for conscious content organization.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Optional


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# =============================================================================
# ORIENTATION DATA
# =============================================================================

@dataclass(frozen=True)
class Orientation:
    """
    Immutable orientation data for a reference frame.
    
    Orientation determines how the reference frame is aligned relative to
    the world coordinate system and other frames.
    """
    
    yaw: float = 0.0
    """Rotation around vertical axis (radians)."""
    
    pitch: float = 0.0
    """Rotation around horizontal axis (radians)."""
    
    roll: float = 0.0
    """Rotation around forward axis (radians)."""
    
    @classmethod
    def from_euler(cls, yaw: float, pitch: float, roll: float) -> "Orientation":
        """Create an Orientation from Euler angles."""
        return cls(yaw=yaw, pitch=pitch, roll=roll)
    
    def with_yaw(self, new_yaw: float) -> "Orientation":
        """Return a copy with updated yaw."""
        return dataclass_replace(self, yaw=new_yaw)
    
    def with_pitch(self, new_pitch: float) -> "Orientation":
        """Return a copy with updated pitch."""
        return dataclass_replace(self, pitch=new_pitch)
    
    def with_roll(self, new_roll: float) -> "Orientation":
        """Return a copy with updated roll."""
        return dataclass_replace(self, roll=new_roll)


# =============================================================================
# REFERENCE FRAME
# =============================================================================

@dataclass(frozen=True)
class ReferenceFrame:
    """
    Immutable reference frame for perspective organization.
    
    A reference frame establishes the computational origin, orientation,
    and coordinate system used to organize conscious contents from a first-
    person perspective.
    
    Reference frame properties:
        - Immutable: Once created, never modified
        - Complete: All required coordinates specified
        - Deterministic: Same inputs produce identical frames
        - Canonical: Single source of truth for perspective coordination
    
    NOT included (owned by external systems):
        - World coordinate system definition
        - Physical sensor calibration
        - External reference frame mappings
    """
    
    # Identity (required fields first)
    frame_id: str = field(default_factory=lambda: f"frame-{_generate_uuid()}")
    """Unique identifier for this reference frame."""
    
    origin: Tuple[float, float, float] = field(
        default_factory=lambda: (0.0, 0.0, 0.0)
    )
    """Reference point coordinates (x, y, z)."""
    
    orientation: Orientation = field(default_factory=Orientation)
    """Frame orientation in 3D space."""
    
    # Frame properties
    frame_type: str = "self"
    """Type of reference frame (self, external_observer, etc.)."""
    
    orientation_type: str = "default"
    """Orientation mode for this frame."""
    
    # Metadata
    generated_at_utc: float = field(default_factory=lambda: 0.0)
    """When this frame was created."""
    
    provenance: Optional[str] = None
    """Source that produced this frame (if any)."""
    
    trust_level: str = "medium"
    """Trust level for this frame's coordinates."""
    
    privacy_level: str = "internal"
    """Privacy classification of this frame."""
    
    # Coordinate bounds (for validation)
    coordinate_bounds: Tuple[Tuple[float, float], ...] = field(
        default_factory=lambda: ((-1000.0, 1000.0), (-1000.0, 1000.0), (-1000.0, 1000.0))
    )
    """Valid ranges for x, y, z coordinates."""
    
    @classmethod
    def initial(cls) -> "ReferenceFrame":
        """
        Create an initial reference frame.
        
        This creates a clean starting point at the origin with default
        orientation, suitable for first use or restart scenarios.
        """
        import time
        return cls(
            frame_id="frame-initial-001",
            origin=(0.0, 0.0, 0.0),
            generated_at_utc=time.time(),
            frame_type="self",
            orientation_type="default",
            trust_level="medium",
            privacy_level="internal",
        )
    
    @classmethod
    def external_observer(
        cls,
        observer_position: Tuple[float, float, float] = (1.0, 1.5, -2.0),
    ) -> "ReferenceFrame":
        """
        Create an external observer reference frame.
        
        Args:
            observer_position: Position of the external observer
        """
        import time
        return cls(
            frame_id=f"frame-external-{_generate_uuid()}",
            origin=observer_position,
            generated_at_utc=time.time(),
            frame_type="external_observer",
            orientation_type="aligned",
            trust_level="high",
            privacy_level="internal",
        )
    
    def with_origin(self, new_origin: Tuple[float, float, float]) -> "ReferenceFrame":
        """Return a copy with updated origin."""
        return dataclass_replace(self, origin=new_origin)
    
    def with_orientation(self, new_orientation: Orientation) -> "ReferenceFrame":
        """Return a copy with updated orientation."""
        return dataclass_replace(self, orientation=new_orientation)
    
    def with_frame_type(self, new_type: str) -> "ReferenceFrame":
        """Return a copy with updated frame type."""
        return dataclass_replace(self, frame_type=new_type)
    
    def is_valid_coordinate(self, coordinate: Tuple[float, float, float]) -> bool:
        """
        Check if a coordinate is within valid bounds.
        
        Args:
            coordinate: (x, y, z) coordinates to check
            
        Returns:
            True if all coordinates are within bounds
        """
        for i, (coord, (min_val, max_val)) in enumerate(zip(coordinate, self.coordinate_bounds)):
            if not (min_val <= coord <= max_val):
                return False
        return True
    
    def transform_to(self, target_frame: "ReferenceFrame") -> Optional["Transformation"]:
        """
        Create a transformation to the target frame.
        
        This creates a deterministic transformation from this frame to
        another reference frame. The actual computation is done by
        the transformations module.
        
        Args:
            target_frame: Destination reference frame
            
        Returns:
            Transformation object, or None if incompatible
        """
        # Check compatibility
        if self.frame_type == target_frame.frame_type:
            return None  # Same frame, no transformation needed
        
        from gordon.agent.components.systems.consciousnesstransformations import Transformation
        
        return Transformation(
            source_frame=self,
            target_frame=target_frame,
            transform_type="canonical",
        )


# =============================================================================
# TRANSFORMATION (lightweight record)
# =============================================================================

@dataclass(frozen=True)
class Transformation:
    """
    Immutable record of a reference frame transformation.
    
    Transformations represent the computation to convert coordinates
    between different reference frames. They are deterministic and
    reproducible.
    """
    
    source_frame: ReferenceFrame
    """Source reference frame."""
    
    target_frame: ReferenceFrame
    """Target reference frame."""
    
    transform_type: str = "canonical"
    """Type of transformation performed."""
    
    transformation_matrix: Optional[Tuple[Tuple[float, ...], ...]] = None
    """Optional pre-computed transformation matrix."""
    
    @property
    def is_self_transform(self) -> bool:
        """Check if this is a self-transformation (no change)."""
        return self.source_frame.frame_id == self.target_frame.frame_id


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "Orientation",
    "ReferenceFrame",
    "Transformation",
)