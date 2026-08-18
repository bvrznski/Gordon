# Strategic Health - Phase 7.18
# ===========================

"""
Canonical Strategic Health for Phase 7.18.

Health metrics include strategies generated, objective coverage, policy consistency,
adaptation success, trade-off quality, validation success, and diagnostics.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicHealth:
    """
    Health metrics for the strategic reasoning subsystem.
    
    Metrics include:
        - Strategies generated (total and by type)
        - Objective coverage (% of objectives with strategies)
        - Policy consistency (no conflicts detected)
        - Adaptation success rate
        - Trade-off quality (satisfactory outcomes)
        - Validation success rate
        - Diagnostics (system health indicators)
    """
    
    # Identity
    health_id: str                          # Unique health identifier
    
    # Metrics
    strategies_generated: int = 0           # Total strategies created
    objective_coverage: float = 0.0         # Coverage % (0-1)
    policy_consistency_score: float = 1.0   # Consistency score (0-1, 1 = perfect)
    adaptation_success_rate: float = 1.0    # Success rate of adaptations (0-1)
    tradeoff_quality_score: float = 1.0     # Trade-off satisfaction (0-1)
    validation_success_rate: float = 1.0    # Pass rate for validations (0-1)
    
    # Diagnostics
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)  # health indicators
    
    # Overall health status
    overall_health_status: str = "healthy"  # healthy, warning, critical
    
    # Timing
    measured_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class HealthMetricsSnapshot:
    """
    Snapshot of health metrics at a point in time.
    """
    
    # Identity
    snapshot_id: str
    
    # Health data
    health_data: Dict[str, Any]             # All metrics
    
    # Status indicators
    status_indicators: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamp
    recorded_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class HealthAlert:
    """
    Alert generated when health metrics fall below thresholds.
    """
    
    # Identity
    alert_id: str
    
    # Metric that triggered alert
    metric_name: str                        # e.g., "policy_consistency_score"
    
    # Current value vs threshold
    current_value: float                    # Actual measured value
    threshold_value: float                  # Threshold that was exceeded
    
    # Alert type
    alert_type: str = "warning"             # warning, critical
    
    # Description
    description: str                        # What does this mean?
    
    # Timing
    triggered_at_utc: float = field(default_factory=time.time)


__all__ = [
    "StrategicHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
]