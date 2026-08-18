# Strategic Reasoning Descriptor - Phase 7.18
# =============================================

"""
Canonical Strategic Descriptor for Phase 7.18.

A descriptor exposes strategic reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class StrategicState(Enum):
    """Strategic Reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    MISSION_ANALYSIS = "mission_analysis"
    OBJECTIVE_DECOMPOSITION = "objective_decomposition"
    CONSTRAINT_ANALYSIS = "constraint_analysis"
    STRATEGY_FORMATION = "strategy_formation"
    POLICY_CONSTRUCTION = "policy_construction"
    TRADEOFF_ANALYSIS = "tradeoff_analysis"
    PRIORITIZATION = "prioritization"
    VALIDATING = "validating"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class StrategicDescriptor:
    """
    Descriptor exposing strategic reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Strategy mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what strategic reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                     # What are we trying to achieve?
    
    # Strategy mode
    strategy_mode: str = "strategic"        # e.g., "strategic", "hierarchical"
    
    # Lifecycle state
    lifecycle_state: StrategicState = StrategicState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did strategy originate?
    
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
        """Check if strategic reasoning completed."""
        return self.lifecycle_state == StrategicState.PUBLISHED
    
    @property
    def is_failed(self) -> bool:
        """Check if strategic reasoning failed."""
        # Will be tracked via other mechanisms in this implementation
        return False
    
    @property
    def is_archived(self) -> bool:
        """Check if strategy is archived."""
        return self.lifecycle_state == StrategicState.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> StrategicDescriptor:
        """Create a new strategic descriptor."""
        return cls(
            descriptor_id=f"strategic_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: StrategicState) -> StrategicDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == StrategicState.PUBLISHED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StrategicDescriptor",
    "StrategicState",
]