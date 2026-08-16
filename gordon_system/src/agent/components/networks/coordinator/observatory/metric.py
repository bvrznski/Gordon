# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Metric Models for Observatory
=============================

Semantic metrics for architectural observation.
Metrics measure properties of the system without modifying it.

METRIC LAWS (from spec)
-----------------------
METRIC-LAW-001: Every metric shall measure exactly one semantic property.
METRIC-LAW-002: Metric definitions shall remain explicit.
METRIC-LAW-003: Metrics shall preserve measurement scope.
METRIC-LAW-004: Metric baselines shall remain explicit.
METRIC-LAW-005: Metric confidence shall remain explicit.
METRIC-LAW-006: Metric uncertainty shall remain explicit.
METRIC-LAW-007: Metric histories shall remain immutable.
METRIC-LAW-008: Metric evaluation shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# =============================================================================
# METRIC KINDS
# =============================================================================

class MetricKind(Enum):
    """
    Canonical kinds of observatory metrics.
    
    METRIC-LAW-001: Every metric measures exactly one semantic property.
    METRIC-LAW-002: Metric definitions remain explicit.
    """
    CYCLE_COMPLETION_RATE = "cycle_completion_rate"
    """Rate at which coordination cycles complete successfully."""
    
    GOAL_COMPLETION_RATE = "goal_completion_rate"
    """Rate at which goals are completed."""
    
    PREDICTION_CONSISTENCY = "prediction_consistency"
    """Consistency of predictive network outputs."""
    
    REWARD_STABILITY = "reward_stability"
    """Stability of reward signals."""
    
    WORKSPACE_UTILIZATION = "workspace_utilization"
    """Current utilization of workspace memory."""
    
    SYNCHRONIZATION_DELAY = "synchronization_delay"
    """Delay in synchronization between networks."""
    
    BARRIER_WAIT_TIME = "barrier_wait_time"
    """Time spent waiting at coordination barriers."""
    
    EXECUTION_EFFICIENCY = "execution_efficiency"
    """Efficiency of execution throughput."""
    
    NETWORK_UTILIZATION = "network_utilization"
    """Utilization of individual networks."""
    
    DEPENDENCY_DENSITY = "dependency_density"
    """Density of dependency relationships."""
    
    RECOVERY_SUCCESS_RATE = "recovery_success_rate"
    """Rate at which recoveries succeed."""
    
    FAILURE_RATE = "failure_rate"
    """Frequency of failures."""
    
    CONTEXT_USAGE = "context_usage"
    """Amount of context being utilized."""
    
    ATTENTION_DISTRIBUTION = "attention_distribution"
    """Distribution of attention across networks."""
    
    COORDINATION_OVERHEAD = "coordination_overhead"
    """Overhead from coordination protocol."""
    
    ORCHESTRATION_QUALITY = "orchestration_quality"
    """Quality score for orchestration decisions."""
    
    UNKNOWN = "unknown"
    """Unknown metric kind."""


# =============================================================================
# OBSERVATORY METRIC
# =============================================================================

@dataclass(frozen=True, slots=True)
class ObservatoryMetric:
    """
    Immutable semantic metric.
    
    Metrics remain evidence-based and never include runtime references.
    
    METRIC-LAW-001: Every metric measures exactly one semantic property.
    METRIC-LAW-003: Metrics preserve measurement scope.
    METRIC-LAW-004: Metric baselines remain explicit.
    """
    
    metric_identity: str
    """Unique identifier for this metric."""
    
    metric_kind: str
    """Kind of metric (from MetricKind)."""
    
    measured_scope: str
    """Scope being measured (network, cycle, goal, etc.)."""
    
    value: float = 0.0
    """Current measurement value."""
    
    baseline: Optional[float] = None
    """Baseline value for comparison."""
    
    confidence: float = 1.0
    """Confidence in the metric value (0.0 to 1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty about the metric value (0.0 to 1.0)."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this metric."""
    
    timestamp: Optional[str] = None
    """Timestamp of measurement in ISO format."""
    
    def __post_init__(self):
        """Validate metric components."""
        if not self.metric_identity:
            raise ValueError("Metric identity cannot be empty")
        
        if not self.measured_scope:
            raise ValueError("Measured scope cannot be empty")
        
        # Validate value bounds
        if self.value < 0.0:
            raise ValueError(f"Metric value cannot be negative: {self.value}")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("Uncertainty must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        metric_kind: str,
        measured_scope: str,
        value: float,
        baseline: Optional[float] = None,
        confidence: float = 1.0,
        provenance: Optional[dict[str, str]] = None,
    ) -> ObservatoryMetric:
        """
        Create a new metric.
        
        Args:
            metric_kind: Kind of metric (from MetricKind)
            measured_scope: Scope being measured
            value: Current measurement value
            baseline: Optional baseline for comparison
            confidence: Confidence in the measurement
            provenance: Optional provenance dictionary
            
        Returns:
            New ObservatoryMetric instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"{metric_kind}:{measured_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            metric_identity=f"metric:{identity_hash}",
            metric_kind=metric_kind,
            measured_scope=measured_scope,
            value=value,
            baseline=baseline,
            confidence=confidence,
            uncertainty=1.0 - confidence if confidence < 1.0 else 0.0,
            provenance=provenance or {},
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            "metric_identity": self.metric_identity,
            "metric_kind": self.metric_kind,
            "measured_scope": self.measured_scope,
            "value": self.value,
            "baseline": self.baseline,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObservatoryMetric:
        """Create metric from dictionary."""
        return cls(
            metric_identity=data["metric_identity"],
            metric_kind=data["metric_kind"],
            measured_scope=data["measured_scope"],
            value=float(data.get("value", 0.0)),
            baseline=data.get("baseline"),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# METRIC HISTORY
# =============================================================================

@dataclass(frozen=True, slots=True)
class MetricHistory:
    """
    Immutable history of a metric over time.
    
    Histories are append-only and never modify previous values.
    
    METRIC-LAW-007: Metric histories remain immutable.
    """
    
    metric_reference: str
    """Reference to the metric being tracked."""
    
    observations: tuple[ObservatoryMetric, ...] = ()
    """Sequence of observations for this metric."""
    
    trends: tuple[str, ...] = ()
    """Identified trends in the history."""
    
    baseline: Optional[float] = None
    """Computed baseline from observations."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this history."""
    
    def __post_init__(self):
        """Validate history components."""
        if not self.metric_reference:
            raise ValueError("Metric reference cannot be empty")
    
    @classmethod
    def create(cls, metric: ObservatoryMetric) -> MetricHistory:
        """
        Create a new history from an initial observation.
        
        Args:
            metric: Initial metric observation
            
        Returns:
            New MetricHistory instance with single observation
        """
        return cls(
            metric_reference=metric.metric_identity,
            observations=(metric,),
            baseline=metric.value,
            provenance=dict(metric.provenance),
        )
    
    def add_observation(self, new_metric: ObservatoryMetric) -> MetricHistory:
        """
        Add a new observation and return updated history.
        
        Args:
            new_metric: New metric observation to add
            
        Returns:
            New MetricHistory instance with additional observation
        """
        # Compute new baseline from all observations
        values = [m.value for m in self.observations] + [new_metric.value]
        new_baseline = sum(values) / len(values)
        
        return MetricHistory(
            metric_reference=self.metric_reference,
            observations=self.observations + (new_metric,),
            trends=self.trends,  # Trends would be recomputed externally
            baseline=new_baseline,
            provenance=dict(self.provenance),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert history to dictionary."""
        return {
            "metric_reference": self.metric_reference,
            "observations": [m.to_dict() for m in self.observations],
            "trends": list(self.trends),
            "baseline": self.baseline,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MetricHistory:
        """Create history from dictionary."""
        return cls(
            metric_reference=data["metric_reference"],
            observations=tuple(ObservatoryMetric.from_dict(m) for m in data.get("observations", [])),
            trends=tuple(data.get("trends", [])),
            baseline=data.get("baseline"),
            provenance=dict(data.get("provenance", {})),
        )