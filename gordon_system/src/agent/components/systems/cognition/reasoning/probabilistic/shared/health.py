# Probabilistic Health - Phase 7.7
# ================================

"""
Canonical health metrics for probabilistic reasoning.

Health remains descriptive - it never modifies artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class HealthStatus(Enum):
    """Health status of probabilistic reasoning."""
    
    HEALTHY = "healthy"                   # All metrics within normal bounds
    DEGRADED = "degraded"                 # Some metrics outside bounds
    CRITICAL = "critical"                 # Critical failure, cannot continue


@dataclass(frozen=True)
class HealthMetric:
    """
    A single health metric for probabilistic reasoning.
    
    Represents one aspect of system health.
    """
    
    # Identity
    metric_id: str                          # Unique identifier
    
    # Metric details
    metric_name: str                        # e.g., "average_uncertainty", "calibration_score"
    metric_value: float                     # Current value
    
    # Thresholds
    optimal_min: float = 0.0                # Best case minimum
    optimal_max: float = 1.0                # Best case maximum
    acceptable_min: float = -float('inf')   # Minimum to be healthy
    acceptable_max: float = float('inf')    # Maximum to be healthy
    
    # Metadata
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def status(self) -> str:
        """Determine if metric is within bounds."""
        if self.acceptable_min <= self.metric_value <= self.acceptable_max:
            return "healthy"
        return "degraded"


@dataclass(frozen=True)
class ProbabilisticHealth:
    """
    Health assessment for a probabilistic reasoning session.
    
    Metrics include:
        - Posterior updates (how many times beliefs changed?)
        - Average uncertainty
        - Calibration score
        - Prediction reliability
        - Fusion accuracy
        - Validation success
    
    Health remains descriptive - it never modifies artifacts directly.
    """
    
    # Identity
    health_id: str                          # Unique identifier
    
    # Session identity
    assessed_session_identity: str          # Which session was assessed?
    
    # Metrics
    metrics: Tuple[HealthMetric, ...] = ()  # All health metrics
    
    # Overall status
    overall_status: HealthStatus = HealthStatus.HEALTHY
    
    # Summary statistics
    metric_count: int = 0                   # How many metrics tracked?
    degraded_count: int = 0                 # How many are degraded?
    
    # Timestamps
    assessed_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_healthy(self) -> bool:
        """Check if overall health is healthy."""
        return self.overall_status == HealthStatus.HEALTHY
    
    @classmethod
    def create_empty(cls, session_id: str) -> ProbabilisticHealth:
        """Create a health record with no metrics."""
        return cls(
            health_id=f"prob_health:{uuid.uuid4().hex[:16]}",
            assessed_session_identity=session_id,
        )
    
    @classmethod
    def create_from_metrics(
        cls,
        session_id: str,
        metrics: List[HealthMetric],
    ) -> ProbabilisticHealth:
        """Create a health record from individual metrics."""
        degraded = sum(1 for m in metrics if m.status != "healthy")
        
        status = (
            HealthStatus.HEALTHY if degraded == 0 else
            HealthStatus.DEGRADED if degraded < len(metrics) / 2 else
            HealthStatus.CRITICAL
        )
        
        return cls(
            health_id=f"prob_health:{uuid.uuid4().hex[:16]}",
            assessed_session_identity=session_id,
            metrics=tuple(metrics),
            overall_status=status,
            metric_count=len(metrics),
            degraded_count=degraded,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ProbabilisticHealth",
    "HealthMetric", 
    "HealthStatus",
]