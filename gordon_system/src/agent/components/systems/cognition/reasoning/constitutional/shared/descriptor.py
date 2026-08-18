# Constitutional Descriptor - Phase 7.36
# =======================================

"""
Constitutional Reasoning Descriptor.

A descriptor exposes constitutional session metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ConstitutionalState(Enum):
    """Constitutional session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    INTERPRETING = "interpreting"
    DELIBERATING = "deliberating"
    VALIDATING = "validating"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ConstitutionalMode(Enum):
    """Constitutional reasoning modes."""
    
    INTERPRETATION = "interpretation"
    LEGITIMACY_ASSESSMENT = "legitimacy_assessment"
    AMENDMENT_ANALYSIS = "amendment_analysis"
    PRECEDENCE_EVALUATION = "precedence_evaluation"
    EVOLUTION_REVIEW = "evolution_review"


@dataclass(frozen=True)
class ConstitutionalDescriptor:
    """
    Descriptor exposing constitutional metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Constitutional goal and scope
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what constitutional reasoning occurred without
    needing to execute the full session again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Constitutional classification
    constitutional_mode: ConstitutionalMode  # What mode of constitutional reasoning?
    constitutional_goal: str                 # The objective of this session
    
    # Scope
    constitutional_scope: str               # What is being evaluated?
    
    # Lifecycle state
    lifecycle_state: ConstitutionalState = ConstitutionalState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
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
        return self.lifecycle_state == ConstitutionalState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == ConstitutionalState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        constitutional_mode: ConstitutionalMode,
        constitutional_goal: str,
        constitutional_scope: str = "",
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> ConstitutionalDescriptor:
        """Create a new constitutional descriptor."""
        return cls(
            descriptor_id=f"constitutional:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            constitutional_mode=constitutional_mode,
            constitutional_goal=constitutional_goal,
            constitutional_scope=constitutional_scope,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: ConstitutionalState) -> ConstitutionalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == ConstitutionalState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConstitutionalDescriptor",
    "ConstitutionalState",
    "ConstitutionalMode",
]