# Abduction Descriptor - Phase 7.3
# =================================

"""
Canonical Abduction Descriptor.

A descriptor exposes abductive reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AbductionMode(Enum):
    """Modes of abductive reasoning."""
    
    DIAGNOSTIC = "diagnostic"               # Identify causes from effects
    EXPLANATORY = "explanatory"             # Explain observations
    CAUSAL_INFER = "causal_infer"           # Infer causal mechanisms
    ANALOGICAL = "analogical"              # Reason by similarity
    MODEL_COMPARISON = "model_comparison"   # Compare explanatory models


class AbductionLifecycle(Enum):
    """Abduction session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    EVIDENCE_COLLECTION = "evidence_collection"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPLANATION_COMPARISON = "explanation_comparison"
    INFORMATION_ACQUISITION = "information_acquisition"
    CAUSAL_ANALYSIS = "causal_analysis"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class AbductionDescriptor:
    """
    Descriptor exposing abductive reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Abduction mode and goal
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what abduction occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning classification
    abduction_mode: AbductionMode             # What kind of abductive reasoning?
    reasoning_goal: str                       # What are we trying to explain?
    
    # Lifecycle state
    lifecycle_state: AbductionLifecycle = AbductionLifecycle.CREATED
    
    # Constraints and requirements
    confidence_threshold: float = 0.5         # Minimum confidence for accepting explanation
    min_evidence_required: int = 1            # Minimum evidence required
    max_hypotheses: int = 10                  # Maximum hypotheses to consider
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did abduction originate?
    
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
        """Check if abduction completed."""
        return self.lifecycle_state == AbductionLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if abduction failed."""
        return self.lifecycle_state == AbductionLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        abduction_mode: AbductionMode = AbductionMode.DIAGNOSTIC,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> AbductionDescriptor:
        """Create a new abduction descriptor."""
        return cls(
            descriptor_id=f"abduction:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            abduction_mode=abduction_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: AbductionLifecycle) -> AbductionDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == AbductionLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class AbductionSessionIdentity:
    """
    Immutable identity for an abduction session.
    
    Allows replay and verification of abductive results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> AbductionSessionIdentity:
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
    "AbductionDescriptor",
    "AbductionSessionIdentity",
    "AbductionMode",
    "AbductionLifecycle",
]