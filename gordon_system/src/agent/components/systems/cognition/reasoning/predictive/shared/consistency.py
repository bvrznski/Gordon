# Predictive Consistency Model - Phase 7.40
# ==========================================

"""
Predictive consistency model evaluates forecast agreement across horizons and models.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ConsistencyIdentity:
    """Unique identity for a consistency analysis."""
    
    consistency_id: str
    semantic_identity: str
    
    @classmethod
    def create(cls) -> ConsistencyIdentity:
        """Create a new consistency identity."""
        return cls(
            consistency_id=f"consist:{uuid.uuid4().hex[:16]}",
            semantic_identity="consistency-identity",
        )


@dataclass(frozen=True)
class CrossHorizonConsistency:
    """Consistency analysis across different prediction horizons."""
    
    horizon_consistency_score: float  # How consistent are forecasts at different horizons?
    temporal_coherence: float  # Do later predictions follow from earlier ones?
    horizon_agreement: Dict[str, float]  # forecast_id -> agreement score
    
    @classmethod
    def create(
        cls,
        horizon_consistency_score: float = 0.8,
        temporal_coherence: float = 0.75,
        horizon_agreements: Dict[str, float] = None,
    ) -> CrossHorizonConsistency:
        """Create cross-horizon consistency."""
        return cls(
            horizon_consistency_score=horizon_consistency_score,
            temporal_coherence=temporal_coherence,
            horizon_agreement=horizon_agreements or {},
        )


@dataclass(frozen=True)
class CrossModelConsistency:
    """Consistency analysis across different forecasting models."""
    
    model_agreement: float  # How do different models agree?
    model_conflict_count: int
    most_agreed_predictions: List[str]
    conflicting_predictions: List[str]
    
    @classmethod
    def create(
        cls,
        model_agreement: float = 0.7,
        conflict_count: int = 0,
        agreed_predictions: List[str] = None,
        conflicting: List[str] = None,
    ) -> CrossModelConsistency:
        """Create cross-model consistency."""
        return cls(
            model_agreement=model_agreement,
            model_conflict_count=conflict_count,
            most_agreed_predictions=agreed_predictions or [],
            conflicting_predictions=conflicting or [],
        )


@dataclass(frozen=True)
class ConsistencyScore:
    """Overall consistency score combining all metrics."""
    
    overall_score: float
    cross_horizon_component: float
    cross_model_component: float
    internal_consistency: float
    
    @classmethod
    def create(
        cls,
        overall_score: float = 0.8,
        cross_horizon: float = 0.9,
        cross_model: float = 0.75,
        internal: float = 0.85,
    ) -> ConsistencyScore:
        """Create consistency score."""
        return cls(
            overall_score=overall_score,
            cross_horizon_component=cross_horizon,
            cross_model_component=cross_model,
            internal_consistency=internal,
        )


@dataclass(frozen=True)
class PredictiveConsistency:
    """
    Comprehensive predictive consistency model.
    
    Evaluates forecast coherence across multiple dimensions:
    - Cross-horizon agreement
    - Cross-model agreement
    - Internal consistency
    - Temporal stability
    """
    
    # Identity
    consistency_identity: str
    
    # Consistency metrics
    cross_horizon_consistency: CrossHorizonConsistency
    cross_model_consistency: CrossModelConsistency
    overall_score: float
    
    # Analysis details
    time_window_start_utc: float
    forecast_ids_analyzed: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    based_on_forecasts: List[str] = field(default_factory=list)  # Forecast IDs analyzed
    
    @classmethod
    def create(
        cls,
        cross_horizon_consistency: CrossHorizonConsistency,
        cross_model_consistency: CrossModelConsistency,
        forecast_ids_analyzed: List[str] = None,
        based_on_forecasts: List[str] = None,
    ) -> PredictiveConsistency:
        """Create a new predictive consistency model."""
        # Overall score is the minimum of components (conservative)
        overall_score = min(
            cross_horizon_consistency.horizon_consistency_score,
            cross_model_consistency.model_agreement,
            0.8,  # Default internal consistency
        )
        
        return cls(
            consistency_identity=f"consist:{uuid.uuid4().hex[:16]}",
            cross_horizon_consistency=cross_horizon_consistency,
            cross_model_consistency=cross_model_consistency,
            overall_score=overall_score,
            time_window_start_utc=time.time(),
            forecast_ids_analyzed=forecast_ids_analyzed or [],
            based_on_forecasts=based_on_forecasts or [],
        )


__all__ = [
    "PredictiveConsistency",
    "ConsistencyIdentity",
    "CrossHorizonConsistency",
    "CrossModelConsistency",
    "ConsistencyScore",
]