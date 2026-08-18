# Forecast Model - Phase 7.40
# ===========================

"""
Forecast model represents explicit future expectations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ForecastIdentity:
    """Unique identity for a forecast."""
    
    forecast_id: str
    semantic_identity: str  # Stable across revisions
    
    @classmethod
    def create(cls) -> ForecastIdentity:
        """Create a new forecast identity."""
        return cls(
            forecast_id=f"forecast:{uuid.uuid4().hex[:16]}",
            semantic_identity="forecast-identity",
        )


@dataclass(frozen=True)
class PredictedEvent:
    """A predicted event with its characteristics."""
    
    event_id: str
    event_name: str
    predicted_time: float
    probability: float
    confidence: float
    
    @classmethod
    def create(
        cls,
        event_name: str,
        predicted_time: float,
        probability: float = 0.5,
        confidence: float = 0.5,
    ) -> PredictedEvent:
        """Create a predicted event."""
        return cls(
            event_id=f"event:{uuid.uuid4().hex[:16]}",
            event_name=event_name,
            predicted_time=predicted_time,
            probability=probability,
            confidence=confidence,
        )


@dataclass(frozen=True)
class ForecastQuality:
    """Quality assessment of a forecast."""
    
    quality_score: float
    data_reliability: float
    model_accuracy: float
    assumption_solidity: float
    
    @classmethod
    def create(
        cls,
        forecast_confidence: float = 0.5,
    ) -> ForecastQuality:
        """Create forecast quality assessment."""
        return cls(
            quality_score=forecast_confidence,
            data_reliability=0.8,
            model_accuracy=0.7,
            assumption_solidity=0.6,
        )


@dataclass(frozen=True)
class ConfidenceDistribution:
    """Confidence distribution for forecast uncertainty."""
    
    distribution_type: str  # e.g., "normal", "uniform", "beta"
    mean: float
    std_dev: float
    min_value: float = 0.0
    max_value: float = 1.0
    
    @classmethod
    def create_beta(cls, alpha: float, beta_val: float) -> ConfidenceDistribution:
        """Create a Beta distribution."""
        return cls(
            distribution_type="beta",
            mean=alpha / (alpha + beta_val),
            std_dev=(alpha * beta_val / ((alpha + beta_val) ** 2 * (alpha + beta_val + 1))) ** 0.5,
            min_value=0.0,
            max_value=1.0,
        )


@dataclass(frozen=True)
class ForecastModel:
    """
    Explicit forecast model.
    
    A forecast model contains:
        - Forecast identity
        - Predicted state
        - Forecast horizon
        - Confidence estimates
        - Supporting assumptions
    """
    
    # Identity
    forecast_identity: str
    
    # Prediction content
    predicted_state: Dict[str, Any]
    time_steps: List[float]
    
    # Horizon
    forecast_horizon_start: float
    forecast_horizon_end: float
    
    # Confidence
    confidence: float = 0.5
    confidence_distribution: Optional[ConfidenceDistribution] = None
    
    # Supporting information
    assumptions: Tuple[str, ...] = ()
    supporting_evidence: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    observation_reference: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        predicted_state: Dict[str, Any],
        time_steps: List[float],
        forecast_horizon_start: float,
        forecast_horizon_end: float,
        confidence: float = 0.5,
        assumptions: Tuple[str, ...] = (),
        observation_reference: Optional[str] = None,
    ) -> ForecastModel:
        """Create a new forecast model."""
        return cls(
            forecast_identity=f"forecast:{uuid.uuid4().hex[:16]}",
            predicted_state=predicted_state,
            time_steps=time_steps,
            forecast_horizon_start=forecast_horizon_start,
            forecast_horizon_end=forecast_horizon_end,
            confidence=confidence,
            assumptions=assumptions,
            observation_reference=observation_reference,
        )


__all__ = [
    "ForecastModel",
    "ForecastIdentity",
    "PredictedEvent",
    "ForecastQuality",
    "ConfidenceDistribution",
]