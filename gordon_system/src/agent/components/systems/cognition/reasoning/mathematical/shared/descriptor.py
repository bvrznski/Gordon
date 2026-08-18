# Mathematical Descriptor - Phase 7.46
# =====================================

"""
Canonical Mathematical Descriptor.

A descriptor exposes mathematical reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MathematicalMode(Enum):
    """Mathematical reasoning modes."""
    
    ALGEBRAIC = "algebraic"
    GEOMETRIC = "geometric"
    OPTIMIZATION = "optimization"
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    PROOF_CONSTRUCTION = "proof_construction"
    NUMERICAL_ANALYSIS = "numerical_analysis"
    GRAPH_REASONING = "graph_reasoning"
    SYMBOLIC_MANIPULATION = "symbolic_manipulation"


class MathematicalLifecycle(Enum):
    """Mathematical session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    FORMALIZING = "formalizing"
    SOLVING = "solving"
    PROVING = "proving"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class MathematicalDescriptor:
    """
    Descriptor exposing mathematical reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Reasoning mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what mathematical reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                     # What are we trying to solve/prove?
    
    # Reasoning mode
    reasoning_mode: MathematicalMode = MathematicalMode.ALGEBRAIC
    
    # Lifecycle state
    lifecycle_state: MathematicalLifecycle = MathematicalLifecycle.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
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
        return self.lifecycle_state == MathematicalLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == MathematicalLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if reasoning is archived."""
        return self.lifecycle_state == MathematicalLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        reasoning_mode: MathematicalMode = MathematicalMode.ALGEBRAIC,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> MathematicalDescriptor:
        """Create a new mathematical descriptor."""
        return cls(
            descriptor_id=f"mathematical_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            reasoning_mode=reasoning_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: MathematicalLifecycle) -> MathematicalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == MathematicalLifecycle.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MathematicalDescriptor",
    "MathematicalMode",
    "MathematicalLifecycle",
]