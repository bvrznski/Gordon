# Stability Descriptor - Phase 7.26
# ==================================

"""
Canonical Stability Descriptor.

A descriptor exposes stability metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class StabilityKind(Enum):
    """Categories of stability operations."""
    
    HOMEOSTASIS = "homeostasis"       # Cognitive homeostasis
    DEGRADATION_ANALYSIS = "degradation_analysis"  # Degradation evaluation
    CONTAINMENT = "containment"       # Failure containment
    STABILIZATION = "stabilization"   # Stabilization planning
    VALIDATION = "validation"         # Stability validation


class StabilityState(Enum):
    """Stability session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    MONITORING = "monitoring"
    ANALYZING = "analyzing"
    CONTAINING = "containing"
    STABILIZING = "stabilizing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class StabilityDescriptor:
    """
    Descriptor exposing stability metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Stability kind and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what stability operations occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Stability classification
    stability_kind: StabilityKind           # What kind of stability operation?
    stability_mode: Optional[str] = None    # Mode-specific details
    
    # Lifecycle state
    lifecycle_state: StabilityState = StabilityState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did stability originate?
    
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
        """Check if stability operation completed."""
        return self.lifecycle_state == StabilityState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if stability operation failed."""
        return self.lifecycle_state == StabilityState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        stability_kind: StabilityKind,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> StabilityDescriptor:
        """Create a new stability descriptor."""
        return cls(
            descriptor_id=f"stability:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            stability_kind=stability_kind,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: StabilityState) -> StabilityDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == StabilityState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StabilityDescriptor",
    "StabilityKind",
    "StabilityState",
]