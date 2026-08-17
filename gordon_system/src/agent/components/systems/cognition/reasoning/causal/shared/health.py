# Causal Health - Phase 7.5
# =========================

"""
Canonical Causal Health.

Health metrics describe the state and performance of causal reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class HealthMetric:
    """
    A single health metric for causal reasoning.
    """
    
    # Identity
    metric_id: str                      # Unique metric identifier
    
    # Metric name
    name: str                           # Human-readable name
    
    # Value
    value: float                        # Current value
    
    # Unit (for display)
    unit: str = ""                      # e.g., "ms", "%", "count"
    
    # Thresholds
    warning_threshold: Optional[float] = None  # Above this is warning
    critical_threshold: Optional[float] = None # Above this is critical


@dataclass(frozen=True)
class CausalHealth:
    """
    Health metrics for causal reasoning.
    
    Health remains descriptive - it never modifies causal artifacts.
    """
    
    # Identity
    health_id: str                      # Unique health identifier
    
    # Metrics
    metrics: Tuple[HealthMetric, ...]   # All health metrics
    
    # Overall status
    overall_status: str = "healthy"     # "healthy", "warning", "critical"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_healthy(self) -> bool:
        """Check if overall status is healthy."""
        return self.overall_status == "healthy"
    
    @property
    def metric_count(self) -> int:
        """Number of health metrics."""
        return len(self.metrics)


@dataclass(frozen=True)
class HealthReport:
    """
    A complete health report with all metrics.
    """
    
    # Identity
    report_id: str                      # Unique report identifier
    
    # Metrics
    metrics: Tuple[HealthMetric, ...]
    
    # Summary statistics
    healthy_count: int = 0              # Number of healthy metrics
    warning_count: int = 0              # Number with warnings
    critical_count: int = 0             # Number in critical state
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None


def make_health_report(
    metrics: List[HealthMetric],
) -> CausalHealth:
    """Create a new health report."""
    metrics_tuple = tuple(metrics)
    
    # Determine overall status
    has_critical = any(m.critical_threshold and m.value >= m.critical_threshold for m in metrics_tuple)
    has_warning = any(m.warning_threshold and m.value >= m.warning_threshold for m in metrics_tuple)
    
    if has_critical:
        status = "critical"
    elif has_warning:
        status = "warning"
    else:
        status = "healthy"
    
    return CausalHealth(
        health_id=f"health:{uuid.uuid4().hex[:16]}",
        metrics=metrics_tuple,
        overall_status=status,
    )


__all__ = [
    "HealthMetric",
    "CausalHealth",
    "HealthReport",
]