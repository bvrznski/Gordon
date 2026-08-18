# Experimental Reasoning - Health Metrics
# =======================================

"""
Canonical Health metrics for Experimental Reasoning.

Health remains descriptive - it does not modify experiments directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class HealthMetric(Enum):
    """Metrics for experimental health assessment."""
    
    EXPERIMENTS_DESIGNED = "experiments_designed"        # Number of experiments designed
    MEASUREMENT_QUALITY = "measurement_quality"          # Quality of measurement plans
    CONTROL_COMPLETENESS = "control_completeness"       # Completeness of control conditions
    INFORMATION_GAIN = "information_gain"                # Information gain achieved
    RESOURCE_EFFICIENCY = "resource_efficiency"         # Resource usage efficiency
    VALIDATION_SUCCESS = "validation_success"           # Validation pass rate


@dataclass(frozen=True)
class ExperimentalHealth:
    """
    Health status of experimental reasoning.
    
    Health remains descriptive - it does not modify experiments directly.
    Metrics include:
        - Experiments designed
        - Measurement quality
        - Control completeness
        - Information gain
        - Resource efficiency
        - Validation success
        - Diagnostics
    
    Health status is purely observational and descriptive.
    """
    
    # Identity
    health_id: str                              # Unique identifier
    
    # Metric values (0-1 scale, higher is better)
    experiments_designed: float = 0.0           # Experiments designed / target
    measurement_quality: float = 0.0            # Quality score
    control_completeness: float = 0.0           # Control coverage
    information_gain: float = 0.0               # Total information gain
    resource_efficiency: float = 0.0            # Resource efficiency ratio
    validation_success: float = 0.0             # Pass rate
    
    # Overall health assessment
    overall_health_score: float = 0.0           # Weighted average
    
    # Status
    status: str = "unknown"                     # "healthy", "warning", "critical"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @classmethod
    def create(
        cls,
        origin_context: str = "unknown",
    ) -> ExperimentalHealth:
        """Create a new experimental health record."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            origin_context=origin_context,
        )
    
    @classmethod
    def calculate_health(
        cls,
        experiments_designed: float = 0.0,
        measurement_quality: float = 0.0,
        control_completeness: float = 0.0,
        information_gain: float = 0.0,
        resource_efficiency: float = 0.0,
        validation_success: float = 0.0,
    ) -> ExperimentalHealth:
        """Calculate health score from individual metrics."""
        weights = {
            "experiments_designed": 0.15,
            "measurement_quality": 0.2,
            "control_completeness": 0.2,
            "information_gain": 0.2,
            "resource_efficiency": 0.15,
            "validation_success": 0.1,
        }
        
        overall = (
            experiments_designed * weights["experiments_designed"] +
            measurement_quality * weights["measurement_quality"] +
            control_completeness * weights["control_completeness"] +
            information_gain * weights["information_gain"] +
            resource_efficiency * weights["resource_efficiency"] +
            validation_success * weights["validation_success"]
        )
        
        if overall >= 0.8:
            status = "healthy"
        elif overall >= 0.5:
            status = "warning"
        else:
            status = "critical"
        
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            experiments_designed=experiments_designed,
            measurement_quality=measurement_quality,
            control_completeness=control_completeness,
            information_gain=information_gain,
            resource_efficiency=resource_efficiency,
            validation_success=validation_success,
            overall_health_score=overall,
            status=status,
        )
    
    @property
    def is_healthy(self) -> bool:
        """Check if experimental reasoning is healthy."""
        return self.status == "healthy"
    
    @property
    def has_issues(self) -> bool:
        """Check if there are health issues (warning or critical)."""
        return self.status in ("warning", "critical")


@dataclass(frozen=True)
class HealthSummary:
    """
    Summary of health metrics over a period.
    
    Includes trend analysis and historical comparison.
    """
    
    # Identity
    summary_id: str                             # Unique identifier
    
    # Time window
    start_time_utc: float                       # Start of period
    end_time_utc: float = field(default_factory=time.time)  # End of period
    
    # Metrics over time
    metrics_history: Dict[HealthMetric, List[float]] = field(default_factory=dict)
    
    @property
    def average_score(self) -> float:
        """Calculate average health score."""
        if not self.metrics_history:
            return 0.0
        
        all_values = []
        for values in self.metrics_history.values():
            all_values.extend(values)
        
        return sum(all_values) / len(all_values) if all_values else 0.0
    
    @property
    def is_improving(self) -> bool:
        """Check if health is improving over time."""
        if not self.metrics_history:
            return False
        
        for values in self.metrics_history.values():
            if len(values) >= 2 and values[-1] > values[0]:
                return True
        return False


__all__ = [
    "HealthMetric",
    "ExperimentalHealth",
    "HealthSummary",
]