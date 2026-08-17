# Meta-Reasoning Descriptor - Phase 7.13
# ======================================

"""
Meta-Reasoning Descriptor.

A descriptor exposes meta-reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MetaReasoningState(Enum):
    """Meta-Reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    SELECTING = "selecting"           # Strategy selection phase
    ORCHESTRATING = "orchestrating"   # Execution orchestration phase
    MONITORING = "monitoring"         # Ongoing monitoring phase
    ADAPTING = "adapting"             # Adaptive adjustment phase
    VALIDATING = "validating"         # Validation phase
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class OrchestrationMode(Enum):
    """Meta-Reasoning orchestration modes."""
    
    SINGLE_REASONER = "single_reasoner"          # Single reasoner execution
    MULTI_REASONER = "multi_reasoner"            # Parallel multi-reasoner
    HIERARCHICAL = "hierarchical"                # Hierarchical reasoning
    ITERATIVE_REFINEMENT = "iterative_refinement"  # Iterative refinement
    COMPETITIVE = "competitive"                  # Competitive reasoning
    PARALLEL = "parallel"                        # Parallel execution
    CONSENSUS = "consensus"                      # Consensus-based


@dataclass(frozen=True)
class MetaReasoningDescriptor:
    """
    Descriptor exposing meta-reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Orchestration mode and policy
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what meta-reasoning occurred without
    needing to execute the full orchestration process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                     # What is the reasoning objective?
    
    # Orchestration configuration
    orchestration_mode: OrchestrationMode = OrchestrationMode.SINGLE_REASONER
    
    # Lifecycle state
    lifecycle_state: MetaReasoningState = MetaReasoningState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did meta-reasoning originate?
    
    # Metadata
    participating_reasoners: List[str] = field(default_factory=list)
    selected_strategy: Optional[str] = None
    total_execution_time_seconds: float = 0.0
    
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
        """Check if meta-reasoning completed."""
        return self.lifecycle_state == MetaReasoningState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if meta-reasoning failed."""
        return self.lifecycle_state == MetaReasoningState.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if meta-reasoning is archived."""
        return self.lifecycle_state == MetaReasoningState.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        orchestration_mode: OrchestrationMode = OrchestrationMode.SINGLE_REASONER,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> MetaReasoningDescriptor:
        """Create a new meta-reasoning descriptor."""
        return cls(
            descriptor_id=f"meta_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            orchestration_mode=orchestration_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: MetaReasoningState) -> MetaReasoningDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == MetaReasoningState.COMPLETED else None,
        )
    
    def with_participating_reasoners(self, reasoners: List[str]) -> MetaReasoningDescriptor:
        """Return a copy with updated participating reasoners."""
        return dataclass_replace(
            self,
            participating_reasoners=reasoners,
        )
    
    def with_selected_strategy(self, strategy: str) -> MetaReasoningDescriptor:
        """Return a copy with updated selected strategy."""
        return dataclass_replace(
            self,
            selected_strategy=strategy,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningDescriptor",
    "MetaReasoningState",
    "OrchestrationMode",
]