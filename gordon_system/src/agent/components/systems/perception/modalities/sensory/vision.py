# Vision Modality - Phase 5.2 Visual Perception
# ============================================

"""
Vision Modality: Observes images, video, motion, depth, geometry, and appearance.

Canonical inputs:
    camera frames
    screenshots  
    video streams
    rendered scenes

Canonical outputs:
    visual Observations
    visual Signals
    visual Features
    object Percepts
    visual Scenes
    visual Events

Vision does not own:
    semantic knowledge
    object permanence
    identity recognition authority
    world-state truth
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# VISUAL OBSERVATION - Raw visual evidence
# =============================================================================


@dataclass(frozen=True)
class VisualObservation:
    """
    Raw visual evidence from a camera or display capture.
    
    Fields:
        identity:            Unique identifier for this observation
        
        timestamp_utc:       When captured
        
        source_type:         Camera, screenshot, rendered_scene, etc.
        
        width_px:            Image width in pixels
        height_px:           Image height in pixels
        depth_channels:      Number of color channels (e.g., 3 for RGB)
        
        pixel_data:          Raw pixel bytes (PNG/JPEG encoded or raw buffer)
        
        quality:             Quality score 0.0-1.0
        
        calibration_offset_ms: Time offset from calibration reference
        
        provenance:          Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique observation ID
    
    timestamp_utc: float                # When captured
    
    source_type: str = "camera"         # Camera, screenshot, rendered_scene, etc.
    
    # Image dimensions
    width_px: int = 0                   # Image width in pixels
    height_px: int = 0                  # Image height in pixels
    depth_channels: int = 3             # Color channels (RGB)
    
    # Image data
    pixel_data: bytes = b""             # Raw image bytes
    
    quality: float = 1.0                # Quality score 0.0-1.0
    
    calibration_offset_ms: float = 0.0  # Time offset from reference
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if observation has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.timestamp_utc > 0.0 and
            self.width_px > 0 and
            self.height_px > 0
        )
    
    @classmethod
    def from_image_data(
        cls,
        pixel_data: bytes,
        width_px: int,
        height_px: int,
        depth_channels: int = 3,
        source_type: str = "camera",
        timestamp_utc: Optional[float] = None,
        quality: float = 1.0,
    ) -> "VisualObservation":
        """
        Create a VisualObservation from image data.
        
        Args:
            pixel_data: Image bytes (PNG, JPEG, or raw)
            width_px: Width in pixels
            height_px: Height in pixels
            depth_channels: Number of color channels
            source_type: Source type string
            timestamp_utc: Capture timestamp (default: now)
            quality: Quality score 0.0-1.0
            
        Returns:
            New VisualObservation instance
        """
        return cls(
            identity=f"vis_obs:{time.time_ns()}",
            timestamp_utc=timestamp_utc or time.time(),
            source_type=source_type,
            width_px=width_px,
            height_px=height_px,
            depth_channels=depth_channels,
            pixel_data=pixel_data,
            quality=quality,
        )


# =============================================================================
# VISUAL FEATURE - Visual feature extracted from image
# =============================================================================


@dataclass(frozen=True)
class VisualFeature:
    """
    Structured visual feature extracted from an observation.
    
    Examples: edges, corners, contours, motion vectors, depth values
    
    Fields:
        identity:         Unique identifier
        
        modality:         "vision"
        
        location:         (x, y) pixel position
        scale:            Feature scale/size in pixels
        
        confidence:       Detection confidence 0.0-1.0
        
        descriptor:       Feature descriptor (vector or string)
        
        supporting_observation_id: Source observation reference
        
        provenance:       Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique feature ID
    
    modality: str = "vision"            # Modality identifier
    
    location: Tuple[float, float] = field(default=(0.0, 0.0))  # (x, y) pixels
    scale: float = 1.0                  # Feature size in pixels
    
    confidence: float = 1.0             # Detection confidence 0.0-1.0
    
    descriptor: str = ""                # Feature descriptor (vector as string)
    
    supporting_observation_id: Optional[str] = None  # Source reference
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if feature has minimal required data."""
        return (
            len(self.identity) > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    @classmethod
    def from_location_descriptor(
        cls,
        x: float,
        y: float,
        descriptor: str,
        confidence: float = 1.0,
        scale: float = 1.0,
        observation_id: Optional[str] = None,
    ) -> "VisualFeature":
        """
        Create a VisualFeature from location and descriptor.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            descriptor: Feature descriptor string
            confidence: Detection confidence 0.0-1.0
            scale: Feature size in pixels
            observation_id: Source observation reference
            
        Returns:
            New VisualFeature instance
        """
        return cls(
            identity=f"vis_feat:{time.time_ns()}",
            location=(x, y),
            scale=scale,
            confidence=confidence,
            descriptor=descriptor,
            supporting_observation_id=observation_id,
        )


# =============================================================================
# VISUAL PERCEPT - Modality-independent visual representation
# =============================================================================


@dataclass(frozen=True)
class VisualPercept:
    """
    Modality-independent visual representation derived from features.
    
    Examples: objects, scenes, events
    
    Fields:
        identity:          Unique identifier
        
        modality:          "vision"
        
        percept_type:      object, scene, event, motion, etc.
        
        location:          Spatial extent or position
        confidence:        0.0-1.0
        
        visual_features:   References to contributing features
        
        provenance:        Origin tracking
    """
    
    # Core identity (required)
    identity: str                       # Unique percept ID
    
    modality: str = "vision"            # Modality identifier
    
    percept_type: str = "object"        # object, scene, event, etc.
    
    location: Tuple[float, float] = field(default=(0.0, 0.0))
    confidence: float = 1.0             # Detection confidence
    
    visual_features: Tuple[str, ...] = field(default_factory=tuple)  # Feature refs
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if percept has minimal required data."""
        return (
            len(self.identity) > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    @classmethod
    def create(
        cls,
        percept_type: str = "object",
        features: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> "VisualPercept":
        """
        Create a VisualPercept.
        
        Args:
            percept_type: Type of percept
            features: Feature references
            confidence: Confidence score
            
        Returns:
            New VisualPercept instance
        """
        return cls(
            identity=f"vis_percept:{time.time_ns()}",
            percept_type=percept_type,
            confidence=confidence,
            visual_features=features,
        )


# =============================================================================
# VISION MODALITY - Vision modality implementation
# =============================================================================


@dataclass(frozen=True)
class VisionModality:
    """
    Vision Modality implementation.
    
    Implements the canonical perception contract for visual observation.
    
    Fields:
        identity:           Unique modality identifier
        
        capabilities:       Supported capability identifiers
        
        permissions:        Effective permission set
        
        sandbox_profile:    Active sandbox profile
        
        calibration_state:  Current calibration state
        
        health:             Operational health status
    """
    
    # Core identity (required)
    identity: str                       # Modality unique ID
    
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    
    permissions: Tuple[str, ...] = field(default_factory=tuple)
    
    sandbox_profile: str = "NONE"
    
    calibration_state: str = "uncalibrated"
    
    health: Dict[str, Any] = field(default_factory=dict)  # Health metrics
    
    @property
    def is_active(self) -> bool:
        """Check if modality is active."""
        return self.health.get("is_available", False)
    
    @classmethod
    def create(
        cls,
        identity: Optional[str] = None,
        capabilities: Tuple[str, ...] = ("capture_image", "capture_video"),
        permissions: Tuple[str, ...] = (),
        sandbox_profile: str = "NONE",
        calibration_state: str = "uncalibrated",
    ) -> "VisionModality":
        """
        Create a new VisionModality instance.
        
        Args:
            identity: Unique identifier (auto-generated if None)
            capabilities: Supported capability identifiers
            permissions: Effective permission set
            sandbox_profile: Active sandbox profile
            calibration_state: Calibration state
            
        Returns:
            New VisionModality instance
        """
        return cls(
            identity=identity or f"vision:{time.time_ns()}",
            capabilities=capabilities,
            permissions=permissions,
            sandbox_profile=sandbox_profile,
            calibration_state=calibration_state,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Dataclasses
    "VisualObservation",
    "VisualFeature", 
    "VisualPercept",
    
    # Modality class
    "VisionModality",
]