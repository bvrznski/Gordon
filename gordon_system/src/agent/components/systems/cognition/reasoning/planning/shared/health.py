# Planning Health - Phase 7.20
# ===========================

"""
Canonical Planning Health metrics for Phase 7.20.

Health metrics track:
    - Plans generated
    - Task coverage
    - Dependency correctness
    - Resource efficiency
    - Contingency completeness
    - Validation success
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PlanningHealth:
    """
    Health metrics for a planning session.
    
    Health is descriptive - it measures outcomes without modifying the plan.
    """
    
    # Identity
    health_id: str                            # Unique health identifier
    
    # Session being measured
    measured_session_id: Optional[str] = None  # Which session?
    
    # Metrics snapshot
    plans_generated: int = 0                  # Total execution plans created
    tasks_covered: int = 0                    # Tasks included in plans
    dependencies_correct: bool = True         # All dependency edges valid?
    
    # Efficiency metrics
    resource_efficiency_score: float = 1.0    # 0.0 to 1.0 (higher is better)
    total_resource_consumption: float = 0.0   # Sum of all expected usage
    
    # Completeness metrics
    contingency_completeness: float = 1.0     # % of tasks with contingencies
    validation_success_rate: float = 1.0      # % of plans passing validation
    
    # Diagnostics summary
    total_failures_encountered: int = 0       # All failures in session
    total_refinements_made: int = 0           # Plan refinements performed
    
    # Metadata
    measured_at_utc: float = field(default_factory=time.time)
    
    @property
    def overall_health_score(self) -> float:
        """Calculate an overall health score (0.0 to 1.0)."""
        base_score = (
            self.dependency_integrity_score * 0.3 +
            self.resource_efficiency_score * 0.2 +
            self.contingency_completeness * 0.2 +
            self.validation_success_rate * 0.3
        )
        # Reduce for failures (each failure reduces score slightly)
        penalty = min(0.5, self.total_failures_encountered * 0.05)
        return max(0.0, base_score - penalty)
    
    @property
    def dependency_integrity_score(self) -> float:
        """Score based on dependency correctness."""
        return 1.0 if self.dependencies_correct else 0.0
    
    @classmethod
    def create(
        cls,
        measured_session_id: Optional[str] = None,
    ) -> PlanningHealth:
        """Create a new planning health record."""
        return cls(
            health_id=f"planhealth:{uuid.uuid4().hex[:16]}",
            measured_session_id=measured_session_id,
        )


@dataclass(frozen=True)
class HealthMetricsSnapshot:
    """
    A snapshot of health metrics at a point in time.
    
    Snapshots allow historical analysis of planning health over time.
    """
    
    # Identity
    snapshot_id: str                          # Unique snapshot identifier
    
    # Session and timing
    session_id: Optional[str] = None          # Which session?
    recorded_at_utc: float = field(default_factory=time.time)
    
    # All metrics
    plans_generated: int = 0
    tasks_covered: int = 0
    dependencies_correct: bool = True
    resource_efficiency_score: float = 1.0
    contingency_completeness: float = 1.0
    validation_success_rate: float = 1.0
    
    # Summary metrics
    total_failures_encountered: int = 0
    total_refinements_made: int = 0
    
    @classmethod
    def create(
        cls,
        session_id: Optional[str] = None,
    ) -> HealthMetricsSnapshot:
        """Create a new health metrics snapshot."""
        return cls(
            snapshot_id=f"health_snapshot:{uuid.uuid4().hex[:16]}",
            session_id=session_id,
        )


@dataclass(frozen=True)
class HealthAlert:
    """
    An alert about planning health issues.
    
    Alerts trigger when health metrics fall below acceptable thresholds.
    """
    
    # Identity
    alert_id: str                             # Unique alert identifier
    
    # Alert kind
    alert_kind: str = "low_health"            # Type of alert
    
    # Health metrics at time of alert
    current_score: float = 0.0                # Current health score
    threshold: float = 0.5                    # Alert trigger threshold
    
    # Affected area
    affected_session_id: Optional[str] = None  # Which session?
    affected_component: str = "all"           # What's affected?
    
    # Description
    description: str                          # Human-readable explanation
    
    # Metadata
    triggered_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        current_score: float,
        threshold: float = 0.5,
        description: str = "",
    ) -> HealthAlert:
        """Create a new health alert."""
        return cls(
            alert_id=f"health_alert:{uuid.uuid4().hex[:16]}",
            current_score=current_score,
            threshold=threshold,
            description=description or f"Health score {current_score} below threshold {threshold}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PlanningHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
]