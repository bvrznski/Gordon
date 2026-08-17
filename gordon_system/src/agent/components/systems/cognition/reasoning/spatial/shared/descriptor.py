# Spatial Descriptor - Phase 7.9
# ==============================

"""
Canonical Spatial Descriptor.

A descriptor exposes spatial reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class SpatialMode(Enum):
    """Modes of spatial reasoning."""
    
    GEOMETRIC_ANALYSIS = "geometric_analysis"              # Analyze geometric properties
    TOPOLOGICAL_ANALYSIS = "topological_analysis"          # Analyze topological relationships
    COORDINATE_TRANSFORMATIONS = "coordinate_transformations"  # Transform between frames
    NAVIGATION_SEMANTICS = "navigation_semantics"          # Analyze navigation capabilities
    CONSISTENCY_VALIDATION = "consistency_validation"      # Validate spatial consistency
    ENTITY_MANAGEMENT = "entity_management"                # Manage spatial entities
    TRACE_RECORDING = "trace_recording"                    # Record reasoning trace
    VALIDATION_ONLY = "validation_only"                    # Only validate existing structure


class SpatialLifecycle(Enum):
    """Spatial session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    ENTITY_COLLECTION = "entity_collection"
    REFERENCE_FRAME_SELECTION = "reference_frame_selection"
    COORDINATE_NORMALIZATION = "coordinate_normalization"
    GEOMETRY_ANALYSIS = "geometry_analysis"
    TOPOLOGY_ANALYSIS = "topology_analysis"
    NAVIGATION_SEMANTICS = "navigation_semantics"
    CONSISTENCY_VALIDATION = "consistency_validation"
    TRACE_RECORDING = "trace_recording"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class SpatialDescriptor:
    """
    Descriptor exposing spatial reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Spatial mode and constraints
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what spatial reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                       # What are we trying to determine?
    
    # Spatial mode and constraints
    spatial_mode: SpatialMode                 # What kind of spatial reasoning?
    reference_frame: Optional[str] = None     # Reference frame for analysis
    
    # Lifecycle state
    lifecycle_state: SpatialLifecycle = SpatialLifecycle.CREATED
    
    # Entity set info
    entity_set_id: Optional[str] = None       # ID of participating entity set
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did spatial reasoning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if spatial reasoning completed."""
        return self.lifecycle_state == SpatialLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if spatial reasoning failed."""
        return self.lifecycle_state == SpatialLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if spatial reasoning is archived."""
        return self.lifecycle_state == SpatialLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        spatial_mode: SpatialMode = SpatialMode.GEOMETRIC_ANALYSIS,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        reference_frame: Optional[str] = None,
    ) -> SpatialDescriptor:
        """Create a new spatial descriptor."""
        return cls(
            descriptor_id=f"spatial:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            spatial_mode=spatial_mode,
            reference_frame=reference_frame,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: SpatialLifecycle) -> SpatialDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == SpatialLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class SpatialEntitySetIdentity:
    """
    Immutable identity for a spatial entity set.
    
    Allows replay and verification of spatial reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    set_number: int = 1                       # For repeated sets
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, set_number: int = 1) -> SpatialEntitySetIdentity:
        """Create a new entity set identity."""
        return cls(
            semantic_identity=semantic_identity,
            set_number=set_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialDescriptor",
    "SpatialEntitySetIdentity", 
    "SpatialMode",
    "SpatialLifecycle",
]