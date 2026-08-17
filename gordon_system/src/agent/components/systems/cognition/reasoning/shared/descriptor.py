# Reasoning Descriptor - Phase 7.0
# =================================

"""
Canonical Reasoning Descriptor.

A descriptor exposes reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ReasoningKind(Enum):
    """Categories of reasoning operations."""
    
    DEDUCTIVE = "deductive"          # From general to specific
    INDUCTIVE = "inductive"          # From specific to general
    ABDUCTIVE = "abductive"          # Best explanation inference
    ANALOGICAL = "analogical"        # Similarity-based reasoning
    CAUSAL = "causal"                # Cause-effect analysis
    TEMPORAL = "temporal"            # Time-based reasoning
    COUNTERFACTUAL = "counterfactual"  # What-if scenarios
    META_REASONING = "meta_reasoning"  # Reasoning about reasoning


class ReasoningState(Enum):
    """Reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DELIBERATING = "deliberating"
    CONCLUDING = "concluding"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ReasoningDescriptor:
    """
    Descriptor exposing reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning kind and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoning classification
    reasoning_kind: ReasoningKind           # What kind of reasoning?
    reasoning_mode: Optional[str] = None    # Mode-specific details
    
    # Lifecycle state
    lifecycle_state: ReasoningState = ReasoningState.CREATED
    
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
        return self.lifecycle_state == ReasoningState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == ReasoningState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_kind: ReasoningKind,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> ReasoningDescriptor:
        """Create a new reasoning descriptor."""
        return cls(
            descriptor_id=f"descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_kind=reasoning_kind,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: ReasoningState) -> ReasoningDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == ReasoningState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReasoningDescriptor",
    "ReasoningKind",
    "ReasoningState",
]