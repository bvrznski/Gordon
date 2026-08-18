# Introspection Reasoning Descriptor - Phase 7.29
# ================================================

"""
Introspection Session Descriptor.

A descriptor exposes introspection reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class IntrospectionMode(Enum):
    """Modes of introspection reasoning."""
    
    SESSION = "session"              # Introspect on current execution session
    ACTIVE_GOALS = "active_goals"    # Introspect on active goals and their status
    REASONING_SESSION = "reasoning_session"  # Introspect on a reasoning session
    COGNITIVE_STATE = "cognitive_state"      # Introspect on cognitive state


class IntrospectionLifecycle(Enum):
    """Introspection session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVING = "observing"
    MODELING = "modeling"
    ANALYZING = "analyzing"
    PUBLISHING = "publishing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class IntrospectionType(Enum):
    """Types of introspection outputs."""
    
    SELF_MODEL = "self_model"                     # Self model snapshot
    COGNITIVE_AWARENESS = "cognitive_awareness"   # Awareness assessment
    CONSISTENCY_ASSESSMENT = "consistency_assessment"  # Consistency evaluation
    DIAGNOSTIC_REPORT = "diagnostic_report"       # Diagnostic findings
    VALIDATION_REPORT = "validation_report"       # Validation results
    PUBLISHED_SUMMARY = "published_summary"       # Published state summary


@dataclass(frozen=True)
class IntrospectionDescriptor:
    """
    Descriptor exposing introspection reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Introspection goal and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what introspection occurred without
    needing to execute the full introspection process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Introspection classification
    introspection_mode: IntrospectionMode     # What kind of introspection?
    introspection_goal: str                   # What are we trying to understand?
    
    # Lifecycle state
    lifecycle_state: IntrospectionLifecycle = IntrospectionLifecycle.CREATED
    
    # Constraints and requirements
    min_evidence_required: int = 1            # Minimum evidence required
    max_candidates: int = 20                  # Maximum candidates to consider
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did introspection originate?
    
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
        """Check if introspection completed."""
        return self.lifecycle_state == IntrospectionLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if introspection failed."""
        return self.lifecycle_state == IntrospectionLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        introspection_goal: str,
        introspection_mode: IntrospectionMode = IntrospectionMode.SESSION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> IntrospectionDescriptor:
        """Create a new introspection descriptor."""
        return cls(
            descriptor_id=f"introspection:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            introspection_goal=introspection_goal,
            introspection_mode=introspection_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: IntrospectionLifecycle) -> IntrospectionDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == IntrospectionLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class IntrospectionSessionIdentity:
    """
    Immutable identity for an introspection session.
    
    Allows replay and verification of introspective results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> IntrospectionSessionIdentity:
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
    "IntrospectionDescriptor",
    "IntrospectionSessionIdentity",
    "IntrospectionMode",
    "IntrospectionLifecycle",
    "IntrospectionType",
]