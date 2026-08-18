# System Descriptor - Phase 7.38
# ===============================

"""
Canonical System Descriptor.

A system descriptor exposes systems reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class SystemReasoningMode(Enum):
    """Modes of systems reasoning."""
    
    DECOMPOSITION = "decomposition"           # Break down system into components
    TOPOLOGY_ANALYSIS = "topology_analysis"   # Analyze component organization
    INTERACTION_ANALYSIS = "interaction_analysis"  # Analyze interactions
    EMERGENCE_ANALYSIS = "emergence_analysis"  # Analyze emergent behavior
    FEEDBACK_ANALYSIS = "feedback_analysis"   # Analyze feedback loops
    STABILITY_ANALYSIS = "stability_analysis"  # Analyze system stability
    HIERARCHY_ANALYSIS = "hierarchy_analysis"  # Analyze hierarchical structure


class SystemLifecycle(Enum):
    """System session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    DECOMPOSING = "decomposing"
    TOPOLOGY_CONSTRUCTING = "topology_constructing"
    INTERACTION_ANALYZING = "interaction_analyzing"
    EMERGENCE_ANALYZING = "emergence_analyzing"
    FEEDBACK_ANALYZING = "feedback_analyzing"
    STABILITY_ANALYZING = "stability_analyzing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class SystemDescriptor:
    """
    Descriptor exposing systems reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Systems reasoning mode and goal
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what systems reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                          # Unique descriptor identifier
    semantic_identity: str                      # Semantic identity (stable across runs)
    
    # Reasoning classification
    reasoning_mode: SystemReasoningMode         # What kind of systems reasoning?
    reasoning_goal: str                         # What are we analyzing?
    
    # Lifecycle state
    lifecycle_state: SystemLifecycle = SystemLifecycle.CREATED
    
    # Constraints and requirements
    analysis_depth: int = 3                     # How deep to analyze (layers)
    include_interactions: bool = True           # Include interaction analysis?
    detect_emergence: bool = True               # Detect emergent behavior?
    
    # Compatibility
    compatibility_revision: int = 1             # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did systems reasoning originate?
    
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
        """Check if systems reasoning completed."""
        return self.lifecycle_state == SystemLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if systems reasoning failed."""
        return self.lifecycle_state == SystemLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        reasoning_mode: SystemReasoningMode = SystemReasoningMode.DECOMPOSITION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        analysis_depth: int = 3,
    ) -> SystemDescriptor:
        """Create a new system descriptor."""
        return cls(
            descriptor_id=f"system:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            reasoning_mode=reasoning_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            analysis_depth=analysis_depth,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: SystemLifecycle) -> SystemDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == SystemLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class SystemSessionIdentity:
    """
    Immutable identity for a system session.
    
    Allows replay and verification of systems reasoning results.
    """
    
    # Core identity
    semantic_identity: str                      # Stable identity across runs
    
    # Session context
    session_number: int = 1                     # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> SystemSessionIdentity:
        """Create a new session identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SystemDescriptor",
    "SystemSessionIdentity",
    "SystemReasoningMode",
    "SystemLifecycle",
]