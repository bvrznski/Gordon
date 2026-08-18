# Reflection Reasoning Descriptor - Phase 7.28
# ==============================================

"""
Reflection Session Descriptor.

A descriptor exposes reflection reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ReflectionMode(Enum):
    """Modes of reflection reasoning."""
    
    SESSION = "session"              # Reflect on a completed execution session
    PLAN = "plan"                   # Reflect on a completed plan
    DECISION = "decision"           # Reflect on a decision
    STRATEGY = "strategy"           # Reflect on a strategy
    REASONING_SESSION = "reasoning_session"  # Reflect on a reasoning session


class ReflectionLifecycle(Enum):
    """Reflection session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    EXPERIENCE_COLLECTION = "experience_collection"
    SYNTHESIZING = "synthesizing"
    EXPLAINING = "explaining"
    LESSON_EXTRACTION = "lesson_extraction"
    CONSOLIDATION_PLANNING = "consolidation_planning"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ReflectionType(Enum):
    """Types of reflection outputs."""
    
    EXPERIENCE_SYNTHESIS = "experience_synthesis"
    SELF_EXPLANATION = "self_explanation"
    LESSON_EXTRACTION = "lesson_extraction"
    CONSOLIDATION_PROPOSAL = "consolidation_proposal"
    VALIDATION_REPORT = "validation_report"
    GOVERNANCE_EVALUATION = "governance_evaluation"
    DIAGNOSTIC_REPORT = "diagnostic_report"


@dataclass(frozen=True)
class ReflectionDescriptor:
    """
    Descriptor exposing reflection reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reflection goal and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what reflection occurred without
    needing to execute the full reflection process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reflection classification
    reflection_mode: ReflectionMode           # What kind of reflection?
    reflection_goal: str                      # What are we trying to understand?
    
    # Lifecycle state
    lifecycle_state: ReflectionLifecycle = ReflectionLifecycle.CREATED
    
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
    origin_context: str = "unknown"              # Where did reflection originate?
    
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
        """Check if reflection completed."""
        return self.lifecycle_state == ReflectionLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reflection failed."""
        return self.lifecycle_state == ReflectionLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reflection_goal: str,
        reflection_mode: ReflectionMode = ReflectionMode.SESSION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> ReflectionDescriptor:
        """Create a new reflection descriptor."""
        return cls(
            descriptor_id=f"reflection:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reflection_goal=reflection_goal,
            reflection_mode=reflection_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: ReflectionLifecycle) -> ReflectionDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == ReflectionLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class ReflectionSessionIdentity:
    """
    Immutable identity for a reflection session.
    
    Allows replay and verification of reflective results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> ReflectionSessionIdentity:
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
    "ReflectionDescriptor",
    "ReflectionSessionIdentity",
    "ReflectionMode",
    "ReflectionLifecycle",
    "ReflectionType",
]