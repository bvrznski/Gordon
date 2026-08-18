# Evaluation Reasoning Descriptor - Phase 7.23
# ===============================================

"""
Evaluation Session Descriptor.

A descriptor exposes evaluation metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EvaluationMode(Enum):
    """Modes of evaluation reasoning."""
    
    SESSION = "session"              # Evaluate an execution session
    PLAN = "plan"                   # Evaluate a plan
    DECISION = "decision"           # Evaluate a decision
    STRATEGY = "strategy"           # Evaluate a strategy
    REASONING_SESSION = "reasoning_session"  # Evaluate a reasoning session


class EvaluationLifecycle(Enum):
    """Evaluation session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    MEASURING = "measuring"
    ASSESSING = "assessing"
    VERIFYING = "verifying"
    APPRAISING = "appraising"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class EvaluationDescriptor:
    """
    Descriptor exposing evaluation metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Evaluation mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what evaluation occurred without
    needing to execute the full evaluation process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Evaluation classification
    evaluation_mode: EvaluationMode         # What kind of evaluation?
    evaluation_scope: Optional[str] = None  # Scope-specific details
    
    # Lifecycle state
    lifecycle_state: EvaluationLifecycle = EvaluationLifecycle.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did evaluation originate?
    
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
        """Check if evaluation completed."""
        return self.lifecycle_state == EvaluationLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if evaluation failed."""
        return self.lifecycle_state == EvaluationLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluation_mode: EvaluationMode,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> EvaluationDescriptor:
        """Create a new evaluation descriptor."""
        return cls(
            descriptor_id=f"eval:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluation_mode=evaluation_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: EvaluationLifecycle) -> EvaluationDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == EvaluationLifecycle.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EvaluationDescriptor",
    "EvaluationMode",
    "EvaluationLifecycle",
]