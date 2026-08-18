# Adaptation Descriptor - Phase 7.25
# ==================================

"""
Canonical Adaptation Descriptor.

A descriptor exposes adaptation metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AdaptationMode(Enum):
    """Adaptation operational modes."""
    
    BEHAVIOR = "behavior"           # Behavioral modifications
    CONFIGURATION = "configuration" # Configuration updates
    PARAMETER_TUNING = "parameter_tuning"
    CONTEXT = "context"             # Context-specific policies
    RESOURCE_POLICY = "resource_policy"


class AdaptationState(Enum):
    """Adaptation session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    ADAPTING = "adapting"
    CONFIGURING = "configuring"
    INTEGRATING = "integrating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class AdaptationDescriptor:
    """
    Descriptor exposing adaptation metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Adaptation mode and scope
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what adaptations occurred without
    needing to execute the full adaptation process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Adaptation classification
    adaptation_mode: AdaptationMode         # What kind of adaptation?
    adaptation_scope: Optional[str] = None  # Scope-specific details
    
    # Lifecycle state
    lifecycle_state: AdaptationState = AdaptationState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did adaptation originate?
    
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
        """Check if adaptation completed."""
        return self.lifecycle_state == AdaptationState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if adaptation failed."""
        return self.lifecycle_state == AdaptationState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        adaptation_mode: AdaptationMode,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> AdaptationDescriptor:
        """Create a new adaptation descriptor."""
        return cls(
            descriptor_id=f"adaptation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            adaptation_mode=adaptation_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: AdaptationState) -> AdaptationDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == AdaptationState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationDescriptor",
    "AdaptationMode",
    "AdaptationState",
]