# Autobiographical Descriptor - Phase 7.31
# ==========================================

"""
Autobiographical Descriptor.

A descriptor exposes autobiographical metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AutobiographyState(Enum):
    """Autobiographical session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    COLLECTING = "collecting"
    INTEGRATING = "integrating"
    NARRATING = "narrating"
    VALIDATING = "validating"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class AutobiographicalDescriptor:
    """
    Descriptor exposing autobiographical metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Autobiographical goal
        - Autobiographical mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what autobiographical reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Autobiographical goal
    autobiographical_goal: str              # What are we trying to construct?
    
    # Autobiographical mode
    autobiographical_mode: str = "life_narrative"  # e.g., "life_narrative", "identity_continuity"
    
    # Lifecycle state
    lifecycle_state: AutobiographyState = AutobiographyState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did autobiographical reasoning originate?
    
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
        """Check if autobiographical reasoning completed."""
        return self.lifecycle_state == AutobiographyState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if autobiographical reasoning failed."""
        return self.lifecycle_state == AutobiographyState.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if autobiographical is archived."""
        return self.lifecycle_state == AutobiographyState.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        autobiographical_goal: str,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> AutobiographicalDescriptor:
        """Create a new autobiographical descriptor."""
        return cls(
            descriptor_id=f"autobiography_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            autobiographical_goal=autobiographical_goal,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: AutobiographyState) -> AutobiographicalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == AutobiographyState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AutobiographicalDescriptor",
    "AutobiographyState",
]