# Monitoring Health Contract - Phase 7.22
# ========================================

"""
Canonical Monitoring Health Metrics.

Health metrics describe the operational condition of the monitoring system.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class HealthMetrics:
    """
    Health metrics for a monitoring system component.
    """
    
    # Component identity
    component_id: str                         # Which component?
    
    # Operational status
    is_operational: bool = True               # Is the component working?
    health_status: str = "unknown"            # unknown, healthy, degraded, failed
    
    # Performance metrics
    response_time_ms: float = 0.0             # Average response time
    error_rate: float = 0.0                   # Error rate (0.0 to 1.0)
    
    # Timing
    last_heartbeat_utc: Optional[float] = None
    uptime_seconds: float = 0.0               # Time since last restart
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.is_operational and self.health_status == "healthy"


@dataclass(frozen=True)
class MonitoringHealth:
    """
    Health status for the monitoring system.
    
    Health metrics include:
        - Observations collected
        - Sampling latency
        - State consistency
        - Anomaly precision
        - Progress accuracy
        - Validation success rate
    """
    
    # Identity
    health_id: str                            # Unique health identifier
    
    # Overall status
    is_operational: bool = True               # Is monitoring system working?
    overall_status: str = "unknown"           # unknown, healthy, degraded, failed
    
    # Health metrics
    observations_collected: int = 0
    sampling_latency_ms: float = 0.0          # Average latency per sample
    state_consistency_score: float = 1.0      # Consistency score (0.0 to 1.0)
    
    anomaly_precision: float = 0.0            # Precision of anomaly detection
    anomaly_recall: float = 0.0               # Recall of anomaly detection
    
    progress_accuracy: float = 0.0            # Accuracy of progress estimates
    validation_success_rate: float = 1.0      # Success rate of validations
    
    # Component health
    component_health: List[HealthMetrics] = field(default_factory=list)
    
    # Timing
    measured_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_healthy(self) -> bool:
        """Check if monitoring system is healthy."""
        return self.is_operational and self.overall_status == "healthy"
    
    def add_component_health(self, component_id: str, status: str) -> MonitoringHealth:
        """Add or update component health status."""
        new_health = list(self.component_health)
        
        for i, h in enumerate(new_health):
            if h.component_id == component_id:
                new_health[i] = dataclass_replace(
                    h,
                    is_operational=status != "failed",
                    health_status=status,
                    last_heartbeat_utc=time.time(),
                )
                break
        else:
            # Add new component health
            new_health.append(HealthMetrics(
                component_id=component_id,
                is_operational=status != "failed",
                health_status=status,
                last_heartbeat_utc=time.time(),
            ))
        
        return dataclass_replace(
            self,
            component_health=new_health,
            # Recalculate overall status based on components
            is_operational=all(c.is_operational for c in new_health),
            overall_status=self._calculate_overall_status(new_health),
        )
    
    def _calculate_overall_status(self, components: List[HealthMetrics]) -> str:
        """Calculate overall status from component statuses."""
        if not components:
            return "unknown"
        
        # Check for any failures
        if any(not c.is_operational or c.health_status == "failed" for c in components):
            return "degraded"
        
        # Check for healthy
        if all(c.is_operational and c.health_status == "healthy" for c in components):
            return "healthy"
        
        return "unknown"
    
    @classmethod
    def create(
        cls,
    ) -> MonitoringHealth:
        """Create initial health metrics."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            measured_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MonitoringHealth",
    "HealthMetrics",
]