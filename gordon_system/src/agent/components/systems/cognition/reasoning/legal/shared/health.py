# Legal Health - Phase 7.47 Part 1
# =================================

"""
Health Contract.

Legal health metrics:
    - jurisdiction accuracy
    - source completeness
    - interpretation consistency
    - compliance accuracy
    - validation success
    - diagnostics
    
Health remains descriptive.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class HealthStatus:
    """
    Health status for a legal reasoning component.
    
    Includes:
        - Component identity and type
        - Health score (0.0 to 1.0)
        - Contributing metrics
        - Diagnostics
    
    Health remains descriptive (never prescriptive).
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Target
    target_type: str                          # e.g., "session", "interpretation"
    target_id: str                            # ID of component assessed
    
    # Score
    health_score: float = 1.0                 # 0.0 (critical) to 1.0 (healthy)
    
    # Contributing metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics
    diagnostics: Tuple[Dict[str, Any], ...] = ()  # Health-related issues
    
    # Status
    health_status: Optional[str] = None       # e.g., "healthy", "degraded", "critical"
    
    # Timing
    assessed_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        target_type: str,
        target_id: str,
    ) -> HealthStatus:
        """Create a new health status."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            target_type=target_type,
            target_id=target_id,
        )
    
    def with_metrics(self, metrics: Dict[str, Any]) -> HealthStatus:
        """Add metrics to the health assessment."""
        return dataclass_replace(
            self,
            metrics={**self.metrics, **metrics},
        )


@dataclass(frozen=True)
class HealthMonitor:
    """
    Monitor for legal reasoning component health.
    
    Tracks health over time and provides health history.
    """
    
    monitor_id: str                           # Unique identifier
    
    # Health status per target
    statuses: Dict[str, HealthStatus] = field(default_factory=dict)  # ID -> status
    
    # History (latest N assessments)
    history: Tuple[HealthStatus, ...] = ()    # Recent health status snapshots
    
    # Summary statistics
    average_health_score: float = 1.0         # Current average score
    critical_count: int = 0                   # Count of critical components
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
    ) -> HealthMonitor:
        """Create a new health monitor."""
        return cls(
            monitor_id=f"health_monitor:{uuid.uuid4().hex[:16]}",
        )
    
    def update_status(self, status: HealthStatus) -> HealthMonitor:
        """Update the health status of a component."""
        # Update average
        scores = [s.health_score for s in self.statuses.values()]
        if scores:
            avg = sum(scores) / len(scores)
        else:
            avg = 1.0
        
        new_critical_count = sum(1 for s in self.statuses.values() if s.health_status == "critical")
        
        return dataclass_replace(
            self,
            statuses={**self.statuses, status.target_id: status},
            history=self.history + (status,),
            average_health_score=avg,
            critical_count=new_critical_count,
        )
    
    def get_target_health(
        self,
        target_id: str,
    ) -> Optional[HealthStatus]:
        """Get the health status of a specific component."""
        return self.statuses.get(target_id)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HealthStatus",
    "HealthMonitor",
]