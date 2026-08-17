# Temporal Descriptor - Phase 7.8
# =================================

"""
Canonical Temporal Descriptor.

A descriptor exposes temporal reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class TemporalMode(Enum):
    """Modes of temporal reasoning."""
    
    CHRONOLOGICAL_ORDERING = "chronological_ordering"      # Order events chronologically
    INTERVAL_REASONING = "interval_reasoning"              # Reason about durations
    TEMPORAL_CONSTRAINTS = "temporal_constraints"          # Apply and propagate constraints
    CONCURRENCY_ANALYSIS = "concurrency_analysis"          # Analyze parallel events
    CHRONOLOGY_CONSTRUCTION = "chronology_construction"    # Build chronology graphs
    DEPENDENCY_ANALYSIS = "dependency_analysis"            # Analyze temporal dependencies
    VALIDATION_ONLY = "validation_only"                    # Only validate existing structure


class TemporalLifecycle(Enum):
    """Temporal session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    EVENT_COLLECTION = "event_collection"
    TEMPORAL_NORMALIZATION = "temporal_normalization"
    CHRONOLOGY_CONSTRUCTION = "chronology_construction"
    INTERVAL_ANALYSIS = "interval_analysis"
    CONSTRAINT_PROPAGATION = "constraint_propagation"
    CONCURRENCY_ANALYSIS = "concurrency_analysis"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class TemporalDescriptor:
    """
    Descriptor exposing temporal reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Temporal mode and constraints
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what temporal reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                       # What are we trying to determine?
    
    # Temporal mode and constraints
    temporal_mode: TemporalMode               # What kind of temporal reasoning?
    reference_frame: Optional[str] = None     # Reference frame for temporal ordering
    
    # Lifecycle state
    lifecycle_state: TemporalLifecycle = TemporalLifecycle.CREATED
    
    # Temporal scope
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range of interest
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did temporal reasoning originate?
    
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
        """Check if temporal reasoning completed."""
        return self.lifecycle_state == TemporalLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if temporal reasoning failed."""
        return self.lifecycle_state == TemporalLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if temporal reasoning is archived."""
        return self.lifecycle_state == TemporalLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        temporal_mode: TemporalMode = TemporalMode.CHRONOLOGICAL_ORDERING,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        reference_frame: Optional[str] = None,
    ) -> TemporalDescriptor:
        """Create a new temporal descriptor."""
        return cls(
            descriptor_id=f"temporal:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            temporal_mode=temporal_mode,
            reference_frame=reference_frame,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: TemporalLifecycle) -> TemporalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == TemporalLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class TemporalSessionIdentity:
    """
    Immutable identity for a temporal session.
    
    Allows replay and verification of temporal reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> TemporalSessionIdentity:
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
    "TemporalDescriptor",
    "TemporalSessionIdentity",
    "TemporalMode",
    "TemporalLifecycle",
]