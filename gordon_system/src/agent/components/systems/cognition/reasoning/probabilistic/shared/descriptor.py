# Probabilistic Descriptor - Phase 7.7
# =====================================

"""
Canonical Probabilistic Descriptor.

A descriptor exposes probabilistic reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ProbabilisticMode(Enum):
    """Modes of probabilistic reasoning."""
    
    UNCERTAINTY_ESTIMATION = "uncertainty_estimation"       # Estimate uncertainty levels
    BAYESIAN_INFERENCE = "bayesian_inference"               # Bayesian posterior estimation
    EVIDENCE_FUSION = "evidence_fusion"                     # Combine multiple evidence sources
    BELIEF_PROPAGATION = "belief_propagation"               # Propagate beliefs through graph
    CALIBRATION = "calibration"                             # Calibrate confidence estimates
    UNCERTAINTY_ANALYSIS = "uncertainty_analysis"           # Decompose uncertainty sources
    MODEL_REFINEMENT = "model_refinement"                   # Refine probability models


class ProbabilisticLifecycle(Enum):
    """Probabilistic session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    PRIOR_SELECTION = "prior_selection"
    EVIDENCE_COLLECTION = "evidence_collection"
    LIKELIHOOD_ESTIMATION = "likelihood_estimation"
    BAYESIAN_UPDATE = "bayesian_update"
    UNCERTAINTY_PROPAGATION = "uncertainty_propagation"
    CALIBRATING = "calibrating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ProbabilisticDescriptor:
    """
    Descriptor exposing probabilistic reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Inference mode and assumptions
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what probabilistic reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                       # What are we trying to estimate?
    
    # Inference mode and assumptions
    inference_mode: ProbabilisticMode         # What kind of probabilistic reasoning?
    assumptions: Tuple[str, ...] = ()         # Explicit probabilistic assumptions
    
    # Lifecycle state
    lifecycle_state: ProbabilisticLifecycle = ProbabilisticLifecycle.CREATED
    
    # Constraints
    confidence_threshold: float = 0.5         # Minimum confidence for accepting conclusions
    max_propagation_depth: int = 10           # Maximum propagation depth
    evidence_weight_min: float = 0.0          # Minimum source weight threshold
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did probabilistic reasoning originate?
    
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
        """Check if probabilistic reasoning completed."""
        return self.lifecycle_state == ProbabilisticLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if probabilistic reasoning failed."""
        return self.lifecycle_state == ProbabilisticLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if probabilistic reasoning is archived."""
        return self.lifecycle_state == ProbabilisticLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        inference_mode: ProbabilisticMode = ProbabilisticMode.UNCERTAINTY_ESTIMATION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        assumptions: Tuple[str, ...] = (),
        confidence_threshold: float = 0.5,
    ) -> ProbabilisticDescriptor:
        """Create a new probabilistic descriptor."""
        return cls(
            descriptor_id=f"probabilistic:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            inference_mode=inference_mode,
            assumptions=assumptions,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: ProbabilisticLifecycle) -> ProbabilisticDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == ProbabilisticLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class ProbabilisticSessionIdentity:
    """
    Immutable identity for a probabilistic session.
    
    Allows replay and verification of probabilistic reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> ProbabilisticSessionIdentity:
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
    "ProbabilisticDescriptor",
    "ProbabilisticSessionIdentity",
    "ProbabilisticMode",
    "ProbabilisticLifecycle",
]