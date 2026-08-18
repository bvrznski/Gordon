# World-Model Reasoning Descriptor - Phase 7.44
# =================================

"""
Canonical World-Model Descriptor.

A descriptor exposes world-model reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class WorldKind(Enum):
    """Categories of world-model reasoning operations."""
    
    WORLD_MODEL = "world_model"              # Environment representation and evolution
    ENTITY_MANAGEMENT = "entity_management"  # Entity tracking and analysis
    SCENE_MANAGEMENT = "scene_management"    # Scene analysis and construction
    DYNAMICS_MANAGEMENT = "dynamics_management"  # World dynamics and transitions
    CONSISTENCY_MANAGEMENT = "consistency_management"  # Consistency verification


class WorldState(Enum):
    """World-Model reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVING = "observing"
    INTEGRATING = "integrating"
    MODELING = "modeling"
    UPDATING = "updating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class WorldDescriptor:
    """
    Descriptor exposing world-model reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - World kind and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what world-model reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # World classification
    world_kind: WorldKind                   # What kind of world-model reasoning?
    world_mode: Optional[str] = None        # Mode-specific details
    
    # Lifecycle state
    lifecycle_state: WorldState = WorldState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did reasoning originate?
    
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
        """Check if world-model reasoning completed."""
        return self.lifecycle_state == WorldState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if world-model reasoning failed."""
        return self.lifecycle_state == WorldState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        world_kind: WorldKind,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> WorldDescriptor:
        """Create a new world-model descriptor."""
        return cls(
            descriptor_id=f"descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            world_kind=world_kind,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: WorldState) -> WorldDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == WorldState.COMPLETED else None,
        )


@dataclass(frozen=True)
class WorldSet:
    """
    World Set defines the scope of world-model reasoning.
    
    A world set contains:
        - Active observations
        - Known entities
        - Environment boundaries
        - Physical assumptions
        - World constraints
    
    World sets remain immutable during reasoning.
    """
    
    world_set_identity: str                 # Unique identity for this world set
    observed_environment: str               # Description of the environment being modeled
    physical_constraints: List[str]         # Explicit physical constraints
    environmental_scope: Dict[str, Any]     # Scope definition (spatial, temporal, etc.)
    provenance: Optional[str] = None        # Where did this world set come from?
    
    @classmethod
    def create(
        cls,
        world_set_identity: str,
        observed_environment: str,
        physical_constraints: Optional[List[str]] = None,
        environmental_scope: Optional[Dict[str, Any]] = None,
        provenance: Optional[str] = None,
    ) -> WorldSet:
        """Create a new world set."""
        return cls(
            world_set_identity=world_set_identity,
            observed_environment=observed_environment,
            physical_constraints=physical_constraints or [],
            environmental_scope=environmental_scope or {},
            provenance=provenance,
        )


@dataclass(frozen=True)
class WorldPipeline:
    """
    Pipeline contract for world-model reasoning.
    
    A pipeline defines:
        - Pipeline identity
        - World strategy employed
        - Resulting world model
        - Diagnostics
        - Provenance tracking
    """
    
    pipeline_identity: str                  # Unique pipeline identifier
    world_strategy: str                     # Strategy used (e.g., "persistent_graph", "evolutionary")
    resulting_world_model: Dict[str, Any]   # Result from pipeline execution
    diagnostics: List[Dict[str, Any]]       # Diagnostic information
    provenance: Optional[str] = None        # Provenance tracking
    
    @classmethod
    def create(
        cls,
        pipeline_identity: str,
        world_strategy: str,
        provenance: Optional[str] = None,
    ) -> WorldPipeline:
        """Create a new world pipeline."""
        return cls(
            pipeline_identity=pipeline_identity,
            world_strategy=world_strategy,
            resulting_world_model={},
            diagnostics=[],
            provenance=provenance,
        )


# Helper function for dataclass replacement
def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "WorldDescriptor",
    "WorldKind",
    "WorldState",
    "WorldSet",
    "WorldPipeline",
]