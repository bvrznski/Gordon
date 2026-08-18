# Scientific Reasoning Descriptor - Phase 7.34
# =====================================================

"""
Scientific Reasoning Descriptor.

A descriptor exposes scientific reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ScientificMode(Enum):
    """Scientific reasoning modes."""
    
    HYPOTHESIS_GENERATION = "hypothesis_generation"      # Generate candidate hypotheses
    EVIDENCE_INTEGRATION = "evidence_integration"        # Integrate observations
    EXPERIMENTAL_DESIGN = "experimental_design"          # Design experiments
    MODEL_REVISION = "model_revision"                    # Revise scientific models
    PREDICTION_GENERATION = "prediction_generation"      # Generate predictions


class ScientificState(Enum):
    """Scientific session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    FORMULATING = "formulating"
    EVALUATING = "evaluating"
    EXPERIMENTING = "experimenting"
    REVISING = "revising"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ScientificDescriptor:
    """
    Descriptor exposing scientific reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Scientific mode and objective
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what scientific reasoning occurred without
    needing to execute the full process again.
    """
    
    # Identity
    descriptor_id: str                       # Unique descriptor identifier
    semantic_identity: str                   # Semantic identity (stable across runs)
    
    # Scientific classification
    scientific_mode: ScientificMode          # What kind of scientific reasoning?
    scientific_goal: Optional[str] = None    # Goal description
    
    # Lifecycle state
    lifecycle_state: ScientificState = ScientificState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1          # For schema evolution tracking
    
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
        """Check if reasoning completed."""
        return self.lifecycle_state == ScientificState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == ScientificState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        scientific_mode: ScientificMode,
        scientific_goal: Optional[str] = None,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> ScientificDescriptor:
        """Create a new scientific descriptor."""
        return cls(
            descriptor_id=f"descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            scientific_mode=scientific_mode,
            scientific_goal=scientific_goal,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: ScientificState) -> ScientificDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == ScientificState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ScientificDescriptor",
    "ScientificMode",
    "ScientificState",
]