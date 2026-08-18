# Decision Reasoning Descriptor - Phase 7.19
# ===========================================

"""
Canonical Decision Descriptor.

A decision descriptor exposes decision metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DecisionKind(Enum):
    """Categories of decision operations."""
    
    STRATEGIC = "strategic"           # Long-term strategic choices
    OPERATIONAL = "operational"       # Short-term operational decisions
    TACTICAL = "tactical"             # Medium-term tactical choices
    POLICY = "policy"                 # Policy formation and modification
    ALLOCATION = "allocation"         # Resource allocation decisions


class DecisionState(Enum):
    """Decision session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OPTION_GENERATION = "option_generation"
    EVALUATING = "evaluating"
    COMMITTING = "committing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class DecisionDescriptor:
    """
    Descriptor exposing decision metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Decision kind and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what decisions occurred without
    needing to execute the full decision process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Decision classification
    decision_kind: DecisionKind             # What kind of decision?
    decision_mode: Optional[str] = None     # Mode-specific details
    
    # Lifecycle state
    lifecycle_state: DecisionState = DecisionState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did decision originate?
    
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
        """Check if decision completed."""
        return self.lifecycle_state == DecisionState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if decision failed."""
        return self.lifecycle_state == DecisionState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        decision_kind: DecisionKind,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> DecisionDescriptor:
        """Create a new decision descriptor."""
        return cls(
            descriptor_id=f"decision_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            decision_kind=decision_kind,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: DecisionState) -> DecisionDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == DecisionState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionDescriptor",
    "DecisionKind",
    "DecisionState",
]