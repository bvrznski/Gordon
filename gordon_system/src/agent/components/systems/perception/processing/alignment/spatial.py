# Spatial Alignment - Phase 5.2.2
# ===============================

"""
Spatial Alignment: Maps evidence between coordinate systems.

Spatial alignment establishes relationships between different spatial reference
frames, enabling cross-modality spatial reasoning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# SPATIAL ALIGNMENT - Spatial coordinate mapping
# =============================================================================


@dataclass(frozen=True)
class SpatialAlignment:
    """
    Alignment of spatial references between different reference frames.
    
    Fields:
        alignment_identity:      Unique identifier for this alignment
        source_artifacts:        Which artifacts are being aligned?
        source_frames:           Source reference frame(s)
        target_frame:            Target reference frame
        transformations:         Transformations applied to map coordinates
        residual_error:          Residual error after transformation (meters or pixels)
        occlusion:               Any occlusion information
        boundary_conditions:     Boundary conditions for the alignment
        confidence:              Confidence in the alignment
        uncertainty:             Known limitations of this alignment
    """
    
    alignment_identity: str             # Unique ID
    
    source_artifacts: Tuple[str, ...]  # Artifact IDs being aligned
    
    source_frames: Tuple[str, ...]     # e.g., "camera_local", "screen", "window"
    target_frame: str = ""             # e.g., "world", "desktop", "body_relative"
    
    transformations: Dict[str, Any] = field(default_factory=dict)  # transformation_type -> params
    
    residual_error: float = 0.0        # Meters or pixels of error
    occlusion: Optional[str] = None    # e.g., "partial", "complete"
    
    boundary_conditions: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 0.5           # Alignment confidence (0.0-1.0)
    uncertainty: float = 0.3          # Alignment uncertainty (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Alignment history
    
    @property
    def is_valid(self) -> bool:
        """Check if spatial alignment is valid."""
        return self.target_frame and self.residual_error >= 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alignment to dictionary."""
        return {
            "alignment_identity": self.alignment_identity,
            "source_artifacts": list(self.source_artifacts),
            "source_frames": list(self.source_frames),
            "target_frame": self.target_frame,
            "transformations": dict(self.transformations),
            "residual_error": self.residual_error,
            "occlusion": self.occlusion,
            "boundary_conditions": list(self.boundary_conditions),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        source_frames: List[str],
        target_frame: str = "",
        transformations: Optional[Dict[str, Any]] = None,
    ) -> "SpatialAlignment":
        """Create a new spatial alignment."""
        return cls(
            alignment_identity=f"spatial:{uuid.uuid4().hex[:16]}",
            source_artifacts=tuple(artifact_ids),
            source_frames=tuple(source_frames),
            target_frame=target_frame or "world",
            transformations=transformations or {},
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpatialAlignment":
        """Create alignment from dictionary."""
        return cls(
            alignment_identity=data.get("alignment_identity", str(uuid.uuid4())),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            source_frames=tuple(data.get("source_frames", [])),
            target_frame=data.get("target_frame", ""),
            transformations=dict(data.get("transformations", {})),
            residual_error=float(data.get("residual_error", 0.0)),
            occlusion=data.get("occlusion"),
            boundary_conditions=tuple(data.get("boundary_conditions", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.3)),
        )