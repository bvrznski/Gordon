# Predictive Descriptor - Phase 7.40
# ===================================

"""
Canonical Predictive Descriptor.

A descriptor exposes predictive reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PredictiveMode(Enum):
    """Modes of predictive reasoning."""
    
    FORECAST_GENERATION = "forecast_generation"           # Generate forecasts from current state
    TRAJECTORY_ESTIMATION = "trajectory_estimation"       # Estimate future trajectories
    TREND_EXTRAPOLATION = "trend_extrapolation"          # Extrapolate trends into future
    EVENT_ANTICIPATION = "event_anticipation"            # Anticipate specific events
    UNCERTAINTY_ESTIMATION = "uncertainty_estimation"    # Estimate forecast uncertainty
    CONSISTENCY_ANALYSIS = "consistency_analysis"        # Analyze forecast consistency


class PredictiveLifecycle(Enum):
    """Predictive session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVATION_ANALYSIS = "observation_analysis"
    TREND_EXTRACTION = "trend_extraction"
    TRAJECTORY_ESTIMATION = "trajectory_estimation"
    FORECAST_GENERATION = "forecast_generation"
    UNCERTAINTY_ESTIMATION = "uncertainty_estimation"
    CONSISTENCY_ANALYSIS = "consistency_analysis"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class PredictiveDescriptor:
    """
    Descriptor exposing predictive reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Prediction goal
        - Forecasting mode and assumptions
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what predictive reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Prediction goal
    prediction_goal: str                      # What are we trying to predict?
    
    # Forecasting mode and assumptions
    predictive_mode: PredictiveMode           # What kind of predictive reasoning?
    assumptions: Tuple[str, ...] = ()         # Explicit forecasting assumptions
    
    # Lifecycle state
    lifecycle_state: PredictiveLifecycle = PredictiveLifecycle.CREATED
    
    # Constraints
    forecast_horizon: float = 1.0             # Prediction horizon (in time units)
    confidence_threshold: float = 0.5         # Minimum confidence for accepting forecasts
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did predictive reasoning originate?
    
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
        """Check if predictive reasoning completed."""
        return self.lifecycle_state == PredictiveLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if predictive reasoning failed."""
        return self.lifecycle_state == PredictiveLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if predictive reasoning is archived."""
        return self.lifecycle_state == PredictiveLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        prediction_goal: str,
        predictive_mode: PredictiveMode = PredictiveMode.FORECAST_GENERATION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        assumptions: Tuple[str, ...] = (),
        forecast_horizon: float = 1.0,
        confidence_threshold: float = 0.5,
    ) -> PredictiveDescriptor:
        """Create a new predictive descriptor."""
        return cls(
            descriptor_id=f"predictive:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            prediction_goal=prediction_goal,
            predictive_mode=predictive_mode,
            assumptions=assumptions,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            forecast_horizon=forecast_horizon,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: PredictiveLifecycle) -> PredictiveDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == PredictiveLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class PredictiveSessionIdentity:
    """
    Immutable identity for a predictive session.
    
    Allows replay and verification of predictive reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> PredictiveSessionIdentity:
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
    "PredictiveDescriptor",
    "PredictiveSessionIdentity",
    "PredictiveMode",
    "PredictiveLifecycle",
]