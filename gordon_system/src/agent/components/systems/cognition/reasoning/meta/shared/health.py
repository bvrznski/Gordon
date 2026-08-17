# Meta Reasoning Health - Phase 7.13
# ===================================

"""
Canonical Meta-Reasoning Health definition.

Health metrics provide descriptive statistics about meta-reasoning execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class HealthStatus(Enum):
    """Meta-reasoning health status."""
    
    UNKNOWN = "unknown"                       # Not yet evaluated
    HEALTHY = "healthy"                       # All metrics within normal range
    DEGRADED = "degraded"                     # Some issues detected
    CRITICAL = "critical"                     # Critical failure detected


@dataclass(frozen=True)
class HealthMetrics:
    """
    Metrics describing meta-reasoning health.
    
    Health metrics are descriptive, not prescriptive.
    """
    
    # Identity
    metric_id: str                          # Unique metric identifier
    
    # Metric details
    name: str                               # Human-readable name
    value: float                            # Current value
    
    # Thresholds
    warning_threshold: Optional[float] = None   # Warning if above/below
    critical_threshold: Optional[float] = None  # Critical if above/below
    
    # Unit
    unit: Optional[str] = None              # Measurement unit
    
    # Timing
    measured_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class MetaReasoningHealth:
    """
    Health assessment of meta-reasoning execution.
    
    A health assessment contains:
        - Identity and provenance
        - Collected metrics
        - Overall status
        - Descriptive statistics
    
    Health remains descriptive (does not modify artifacts).
    """
    
    # Identity
    health_id: str                          # Unique health identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Metrics
    collected_metrics: List[HealthMetrics] = field(default_factory=list)
    
    # Status
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Statistics
    total_sessions_evaluated: int = 0       # Sessions evaluated
    parallel_utilization: float = 0.0       # Parallel execution % (0-1)
    average_latency_seconds: float = 0.0    # Average session duration
    resource_efficiency: float = 0.0        # Resource utilization % (0-1)
    
    # Timing
    assessed_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_healthy(self) -> bool:
        """Check if health status is healthy."""
        return self.overall_status == HealthStatus.HEALTHY
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> MetaReasoningHealth:
        """Create a new health assessment."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
        )
    
    def record_metric(
        self,
        name: str,
        value: float,
        unit: Optional[str] = None,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None,
    ) -> MetaReasoningHealth:
        """Record a metric and return updated health."""
        return dataclass_replace(
            self,
            collected_metrics=self.collected_metrics + [HealthMetrics(
                metric_id=f"health_metric:{uuid.uuid4().hex[:16]}",
                name=name,
                value=value,
                unit=unit,
                warning_threshold=warning_threshold,
                critical_threshold=critical_threshold,
            )]
        )
    
    def update_status(self, status: HealthStatus) -> MetaReasoningHealth:
        """Update overall health status."""
        return dataclass_replace(
            self,
            overall_status=status,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningHealth",
    "HealthMetrics",
    "HealthStatus",
]