# Creative Session Descriptor - Phase 7.33
# =========================================

"""
Canonical Creative Session Descriptor.

A descriptor exposes creative metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class CreativeState(Enum):
    """Creative session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    SYNTHESIZING = "synthesizing"
    EXPLORING = "exploring"
    INVENTING = "inventing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class CreativeDescriptor:
    """
    Descriptor exposing creative metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Creative goal and scope
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what creative reasoning occurred without
    needing to execute the full creative process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Creative goal
    creative_goal: str                      # What are we trying to create?
    
    # Creative scope
    creative_scope: str = "general"         # e.g., "architecture", "design", "strategy"
    
    # Lifecycle state
    lifecycle_state: CreativeState = CreativeState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did creative reasoning originate?
    
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
        """Check if creative session completed."""
        return self.lifecycle_state == CreativeState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if creative session failed."""
        return self.lifecycle_state == CreativeState.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if creative session is archived."""
        return self.lifecycle_state == CreativeState.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        creative_goal: str,
        creative_scope: str = "general",
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> CreativeDescriptor:
        """Create a new creative descriptor."""
        return cls(
            descriptor_id=f"creative_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            creative_goal=creative_goal,
            creative_scope=creative_scope,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: CreativeState) -> CreativeDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == CreativeState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeDescriptor",
    "CreativeState",
]