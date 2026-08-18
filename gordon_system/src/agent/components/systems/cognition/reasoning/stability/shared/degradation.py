# Degradation Analysis - Phase 7.26
# ==================================

"""
Canonical Degradation Analysis.

Degradation determines performance decay, resource exhaustion,
reasoning instability, behavior oscillation, configuration drift,
and failure propagation.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class DegradationType(Enum):
    """Types of degradation that can occur."""
    
    PERFORMANCE_DECAY = "performance_decay"      # Slowing execution
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # Running out of resources
    REASONING_INSTABILITY = "reasoning_instability"  # Unstable reasoning
    BEHAVIOR_OSCILLATION = "behavior_oscillation"  # Oscillating behavior
    CONFIGURATION_DRIFT = "configuration_drift"   # Config changing over time
    FAILURE_PROPAGATION = "failure_propagation"  # Failures spreading


@dataclass(frozen=True)
class DegradationMetric:
    """A single degradation metric."""
    
    metric_id: str
    metric_name: str               # Human-readable name
    current_value: float           # Current measured value
    baseline_value: Optional[float] = None  # Historical baseline (None = no baseline)
    threshold: Optional[float] = None       # When this is exceeded, degradation is significant
    
    @property
    def decay_rate(self) -> float:
        """Calculate decay rate from baseline."""
        if self.baseline_value is None or self.baseline_value == 0:
            return 0.0
        return (self.baseline_value - self.current_value) / abs(self.baseline_value)
    
    @property
    def is_degraded(self) -> bool:
        """Check if this metric shows significant degradation."""
        if self.threshold is None:
            return False
        return self.current_value > self.threshold


@dataclass(frozen=True)
class DegradationModel:
    """
    Model defining how degradation propagates.
    
    Defines relationships between subsystems and how failures
    in one can affect others.
    """
    
    model_id: str
    model_name: str
    
    # Subsystem dependencies (which subsystem depends on which)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    
    # Propagation factors (how much failure propagates)
    propagation_factors: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class DegradationAnalysis:
    """
    Degradation analysis determines stability issues.
    
    Analyzes:
        - Performance decay over time
        - Resource exhaustion indicators
        - Reasoning instability patterns
        - Behavior oscillation detection
        - Configuration drift measurement
        - Failure propagation paths
    
    Degradation remains explicit and inspectable.
    """
    
    analysis_id: str
    degradation_identity: str
    
    # Monitored metrics
    monitored_metrics: List[DegradationMetric] = field(default_factory=list)
    
    # Degradation model
    degradation_model: Optional[DegradationModel] = None
    
    # Severity assessment
    severity: float = 0.0  # 0.0 to 1.0, where 1.0 is critical
    severity_reason: str = "unknown"
    
    # Predicted effects if not stabilized
    predicted_effects: List[str] = field(default_factory=list)
    
    # Provenance
    provenance: str = "unknown"
    
    # Timing
    analyzed_at_utc: float = field(default_factory=time.time)
    
    @property
    def has_degradation(self) -> bool:
        """Check if any degradation is detected."""
        return any(m.is_degraded for m in self.monitored_metrics)
    
    @property
    def max_decay_rate(self) -> float:
        """Get the maximum decay rate across all metrics."""
        if not self.monitored_metrics:
            return 0.0
        return max(m.decay_rate for m in self.monitored_metrics)
    
    def get_affected_subsystems(self) -> List[str]:
        """Get list of subsystems showing degradation."""
        return [m.metric_name for m in self.monitored_metrics if m.is_degraded]
    
    @classmethod
    def create(
        cls,
        degradation_identity: str,
        monitored_metrics: List[DegradationMetric],
        degradation_model: Optional[DegradationModel] = None,
        provenance: str = "unknown",
    ) -> DegradationAnalysis:
        """Create a new degradation analysis."""
        
        # Calculate severity based on max decay rate and number of degraded metrics
        if not monitored_metrics:
            severity = 0.0
        else:
            degraded_count = sum(1 for m in monitored_metrics if m.is_degraded)
            max_decay = max(m.decay_rate for m in monitored_metrics)
            
            # Severity based on both decay rate and count of affected metrics
            severity = min(1.0, (max_decay * 0.7) + ((degraded_count / len(monitored_metrics)) * 0.3))
        
        return cls(
            analysis_id=f"degr:{uuid.uuid4().hex[:16]}",
            degradation_identity=degradation_identity,
            monitored_metrics=monitored_metrics,
            degradation_model=degradation_model,
            severity=severity,
            severity_reason="Automatic calculation based on metrics",
            predicted_effects=[f"Potential failure in {m.metric_name}" for m in monitored_metrics if m.is_degraded],
            provenance=provenance,
        )


__all__ = [
    "DegradationAnalysis",
    "DegradationMetric",
    "DegradationModel",
    "DegradationType",
]