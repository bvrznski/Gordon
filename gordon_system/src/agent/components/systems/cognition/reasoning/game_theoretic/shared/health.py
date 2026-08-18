# Game Health - Phase 7.43
# ======================

"""
Canonical Game Health metrics.

Health is descriptive and never prescriptive.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class HealthMetrics:
    """Metrics describing game health."""
    
    strategy_coverage: float = 0.0          # Fraction of strategies covered
    equilibrium_stability: float = 0.0      # Average equilibrium stability
    payoff_calibration: float = 0.0         # How well payoffs match expectations
    incentive_consistency: float = 0.0      # Incentive alignment score
    game_completeness: float = 0.0          # Completeness of game definition
    validation_success: float = 0.0         # Validation pass rate


@dataclass(frozen=True)
class GameHealth:
    """
    Health metrics for a game session.
    
    Health remains descriptive and never prescriptive.
    """
    
    # Identity
    health_identity: str                    # Unique identifier
    
    # Metrics
    metrics: HealthMetrics = field(default_factory=HealthMetrics)
    
    # Status
    status: str = "unknown"                 # unknown, healthy, warning, critical
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_session_id: Optional[str] = None
    
    @property
    def overall_score(self) -> float:
        """Compute overall health score."""
        return (
            self.metrics.strategy_coverage * 0.15 +
            self.metrics.equilibrium_stability * 0.25 +
            self.metrics.payoff_calibration * 0.20 +
            self.metrics.incentive_consistency * 0.20 +
            self.metrics.game_completeness * 0.15 +
            self.metrics.validation_success * 0.05
        )
    
    @classmethod
    def create(
        cls,
        source_session_id: Optional[str] = None,
    ) -> GameHealth:
        """Create new game health."""
        return cls(
            health_identity=f"health:{uuid.uuid4().hex[:16]}",
            source_session_id=source_session_id,
        )
    
    def with_metrics(self, metrics: HealthMetrics) -> GameHealth:
        """Update health with new metrics."""
        # Determine status based on overall score
        score = self.metrics.strategy_coverage * 0.15 + \
                metrics.equilibrium_stability * 0.25 + \
                metrics.payoff_calibration * 0.20 + \
                metrics.incentive_consistency * 0.20 + \
                metrics.game_completeness * 0.15 + \
                metrics.validation_success * 0.05
        
        if score >= 0.8:
            status = "healthy"
        elif score >= 0.5:
            status = "warning"
        else:
            status = "critical"
        
        return dataclass_replace(self, metrics=metrics, status=status)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HealthMetrics",
    "GameHealth",
]
