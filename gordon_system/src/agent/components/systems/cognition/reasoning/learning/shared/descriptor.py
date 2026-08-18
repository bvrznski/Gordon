# Learning Descriptor - Phase 7.24
# =================================

"""
Canonical Learning Descriptor.

A descriptor exposes learning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class LearningMode(Enum):
    """Modes of learning reasoning."""
    
    ACQUISITION = "acquisition"            # New knowledge acquisition
    GENERALIZATION = "generalization"      # Pattern to general rule
    REFINEMENT = "refinement"              # Model refinement
    INTEGRATION = "integration"            # Knowledge integration
    EVOLUTION = "evolution"                # Concept evolution


class LearningLifecycle(Enum):
    """Learning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    EXPERIENCE_COLLECTION = "experience_collection"
    ACQUIRING = "acquiring"
    GENERALIZING = "generalizing"
    REFINING = "refining"
    INTEGRATING = "integrating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class LearningDescriptor:
    """
    Descriptor exposing learning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Learning mode and goal
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what learning occurred without
    needing to execute the full process again.
    """
    
    # Identity
    descriptor_id: str                       # Unique descriptor identifier
    semantic_identity: str                   # Semantic identity (stable across runs)
    
    # Reasoning classification
    learning_mode: LearningMode              # What kind of learning?
    learning_goal: str                       # What are we trying to discover?
    
    # Lifecycle state
    lifecycle_state: LearningLifecycle = LearningLifecycle.CREATED
    
    # Constraints and requirements
    confidence_threshold: float = 0.5        # Minimum confidence for publication
    min_supporting_evidence: int = 1         # Minimum evidence required
    generalization_bounds: Dict[str, Any] = field(default_factory=dict)
    
    # Compatibility
    compatibility_revision: int = 1          # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did learning originate?
    
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
        """Check if learning completed."""
        return self.lifecycle_state == LearningLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if learning failed."""
        return self.lifecycle_state == LearningLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        learning_goal: str,
        learning_mode: LearningMode = LearningMode.ACQUISITION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> LearningDescriptor:
        """Create a new learning descriptor."""
        return cls(
            descriptor_id=f"learning:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            learning_goal=learning_goal,
            learning_mode=learning_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: LearningLifecycle) -> LearningDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == LearningLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class LearningSessionIdentity:
    """
    Immutable identity for a learning session.
    
    Allows replay and verification of learning results.
    """
    
    # Core identity
    semantic_identity: str                   # Stable identity across runs
    
    # Session context
    session_number: int = 1                  # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> LearningSessionIdentity:
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
    "LearningDescriptor",
    "LearningSessionIdentity",
    "LearningMode",
    "LearningLifecycle",
]