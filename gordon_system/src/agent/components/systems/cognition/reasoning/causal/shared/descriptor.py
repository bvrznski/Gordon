# Causal Descriptor - Phase 7.5
# ==============================

"""
Canonical Causal Descriptor.

A descriptor exposes causal reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class CausalMode(Enum):
    """Modes of causal reasoning."""
    
    MECHANISM_ANALYSIS = "mechanism_analysis"        # Analyze existing mechanisms
    CAUSAL_INQUIRY = "causal_inquiry"                 # Discover causes from effects
    INTERVENTION_PREDICTION = "intervention_prediction"  # Predict intervention outcomes
    COUNTERFACTUAL_ANALYSIS = "counterfactual_analysis"   # Analyze counterfactuals
    MECHANISM_INFERENCE = "mechanism_inference"       # Infer mechanisms from observations
    EFFECT_PROPAGATION = "effect_propagation"         # Trace effect propagation


class CausalLifecycle(Enum):
    """Causal session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    MECHANISM_SELECTION = "mechanism_selection"
    GRAPH_CONSTRUCTION = "graph_construction"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    INTERVENTION_ANALYSIS = "intervention_analysis"
    EFFECT_PROPAGATION = "effect_propagation"
    MODEL_REFINEMENT = "model_refinement"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class CausalDescriptor:
    """
    Descriptor exposing causal reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Causal mode and assumptions
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what causal reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                       # What are we trying to explain?
    
    # Causal mode and assumptions
    causal_mode: CausalMode                   # What kind of causal reasoning?
    assumptions: Tuple[str, ...] = ()         # Explicit causal assumptions
    
    # Lifecycle state
    lifecycle_state: CausalLifecycle = CausalLifecycle.CREATED
    
    # Constraints
    confidence_threshold: float = 0.5         # Minimum confidence for accepting conclusions
    max_propagation_depth: int = 10           # Maximum effect propagation depth
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did causal reasoning originate?
    
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
        """Check if causal reasoning completed."""
        return self.lifecycle_state == CausalLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if causal reasoning failed."""
        return self.lifecycle_state == CausalLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if causal reasoning is archived."""
        return self.lifecycle_state == CausalLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        causal_mode: CausalMode = CausalMode.MECHANISM_ANALYSIS,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        assumptions: Tuple[str, ...] = (),
        confidence_threshold: float = 0.5,
    ) -> CausalDescriptor:
        """Create a new causal descriptor."""
        return cls(
            descriptor_id=f"causal:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            causal_mode=causal_mode,
            assumptions=assumptions,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: CausalLifecycle) -> CausalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == CausalLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class CausalSessionIdentity:
    """
    Immutable identity for a causal session.
    
    Allows replay and verification of causal reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> CausalSessionIdentity:
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
    "CausalDescriptor",
    "CausalSessionIdentity",
    "CausalMode",
    "CausalLifecycle",
]