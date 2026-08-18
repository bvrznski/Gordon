# Experimental Reasoning Descriptor - Phase 7.16 Part 1
# =======================================================

"""
Canonical Experimental Reasoning Descriptor.

A descriptor exposes experimental reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ExperimentMode(Enum):
    """Modes of experimental reasoning."""
    
    EXPLORATORY = "exploratory"              # Open-ended hypothesis exploration
    CONFIRMATORY = "confirmatory"            # Test specific hypotheses
    DIAGNOSTIC = "diagnostic"                # Identify causes of observed effects
    OPTIMIZATION = "optimization"           # Optimize parameters or configurations
    ADAPTIVE = "adaptive"                   # Continuously refine based on evidence


class LifecycleState(Enum):
    """Experimental reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    DESIGNING = "designing"
    OPTIMIZING = "optimizing"
    VALIDATING = "validating"
    READY = "ready"
    EXECUTED = "executed"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ExperimentalDescriptor:
    """
    Descriptor exposing experimental reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Experiment mode and reasoning goal
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what experimental reasoning occurred without
    needing to execute the full experiment design process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Experiment classification
    experiment_mode: ExperimentMode         # What kind of experimental reasoning?
    reasoning_goal: str                     # What are we trying to discover/test?
    
    # Lifecycle state
    lifecycle_state: LifecycleState = LifecycleState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Constraints and requirements
    confidence_threshold: float = 0.5       # Minimum confidence for experimental selection
    min_experiments_required: int = 1       # Minimum experiments to generate
    max_candidates: int = 20                # Maximum candidate experiments
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range
    resource_limits: Dict[str, float] = field(default_factory=dict)  # Resource constraints
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did experimental reasoning originate?
    
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
        """Check if experimental reasoning completed."""
        return self.lifecycle_state == LifecycleState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if experimental reasoning failed."""
        return self.lifecycle_state == LifecycleState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        experiment_mode: ExperimentMode = ExperimentMode.EXPLORATORY,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> ExperimentalDescriptor:
        """Create a new experimental reasoning descriptor."""
        return cls(
            descriptor_id=f"experimental:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            experiment_mode=experiment_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: LifecycleState) -> ExperimentalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == LifecycleState.COMPLETED else None,
        )


@dataclass(frozen=True)
class ExperimentSessionIdentity:
    """
    Immutable identity for an experiment session.
    
    Allows replay and verification of experimental reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> ExperimentSessionIdentity:
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
    "ExperimentalDescriptor",
    "ExperimentSessionIdentity",
    "ExperimentMode",
    "LifecycleState",
]