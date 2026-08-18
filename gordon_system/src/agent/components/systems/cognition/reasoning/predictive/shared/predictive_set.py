# Predictive Set - Phase 7.40
# ===========================

"""
Canonical Predictive Set.

A predictive set defines the current observations and constraints for
predictive reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PredictionHorizon:
    """
    Explicit prediction horizon definition.
    
    Defines the temporal scope of predictions.
    """
    
    # Time bounds
    start_offset: float = 0.0           # Start offset from current time (seconds)
    end_offset: float = 1.0             # End offset from current time (seconds)
    
    # Horizon type
    horizon_type: str = "relative"      # relative or absolute
    
    # Resolution
    resolution_seconds: float = 1.0     # Time step resolution
    
    @property
    def duration(self) -> float:
        """Calculate total duration of the horizon."""
        return self.end_offset - self.start_offset
    
    @classmethod
    def create_relative(
        cls,
        start_offset: float,
        end_offset: float,
        resolution_seconds: float = 1.0,
    ) -> PredictionHorizon:
        """Create a relative prediction horizon."""
        return cls(
            start_offset=start_offset,
            end_offset=end_offset,
            horizon_type="relative",
            resolution_seconds=resolution_seconds,
        )
    
    @classmethod
    def create_absolute(
        cls,
        start_timestamp: float,
        end_timestamp: float,
        resolution_seconds: float = 1.0,
    ) -> PredictionHorizon:
        """Create an absolute prediction horizon."""
        return cls(
            start_offset=start_timestamp,
            end_offset=end_timestamp,
            horizon_type="absolute",
            resolution_seconds=resolution_seconds,
        )


@dataclass(frozen=True)
class ForecastingConstraints:
    """
    Explicit constraints on forecasting.
    
    Defines boundaries for valid forecasts.
    """
    
    # Minimum confidence required
    minimum_confidence: float = 0.5
    
    # Maximum forecast uncertainty allowed
    maximum_uncertainty: float = 1.0
    
    # Valid outcome space
    outcome_space: Tuple[str, ...] = ("all",)
    
    # Temporal constraints
    max_prediction_horizon: float = float('inf')
    
    # Domain-specific constraints
    domain_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PredictiveSet:
    """
    Canonical predictive set for a prediction session.
    
    A predictive set contains:
        - Current observed state
        - Prediction horizon
        - Forecasting constraints
        - Environmental assumptions
    
    The predictive set remains immutable during reasoning, ensuring
    reproducible and verifiable predictions.
    """
    
    # Identity
    predictive_set_identity: str            # Unique identifier for the set
    
    # Observations
    observed_state: Dict[str, Any]          # Current state observations
    observation_timestamp_utc: float        # When were observations made?
    
    # Prediction scope
    prediction_horizon: PredictionHorizon   # Temporal scope of predictions
    
    # Constraints
    forecasting_constraints: ForecastingConstraints  # Forecasting boundaries
    
    # Assumptions
    environmental_assumptions: Tuple[str, ...] = ()  # Background assumptions
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        observed_state: Dict[str, Any],
        prediction_horizon: PredictionHorizon,
        forecasting_constraints: ForecastingConstraints = None,
        environmental_assumptions: Tuple[str, ...] = (),
    ) -> PredictiveSet:
        """Create a new predictive set."""
        return cls(
            predictive_set_identity=f"predictive-set:{uuid.uuid4().hex[:16]}",
            observed_state=observed_state,
            observation_timestamp_utc=time.time(),
            prediction_horizon=prediction_horizon,
            forecasting_constraints=forecasting_constraints or ForecastingConstraints(),
            environmental_assumptions=environmental_assumptions,
        )


__all__ = [
    "PredictiveSet",
    "PredictionHorizon",
    "ForecastingConstraints",
]