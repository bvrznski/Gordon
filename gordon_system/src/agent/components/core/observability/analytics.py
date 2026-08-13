# Core Analytics Framework
# =========================

"""
Analytics pipeline for observability data.

This module provides:
- Telemetry aggregation pipelines
- Trend analysis and percentiles
- Anomaly detection hooks
- KPI computation
- Health scoring
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto
import time
import uuid
import math


# =============================================================================
# AGGREGATION TYPES
# =============================================================================

class AggregationType(Enum):
    """Types of aggregation operations."""
    
    # Basic statistics
    COUNT = "count"           # Number of events
    SUM = "sum"               # Sum of values
    AVG = "avg"               # Average value
    MIN = "min"               # Minimum value
    MAX = "max"               # Maximum value
    
    # Percentiles
    P50 = "p50"               # Median
    P90 = "p90"               # 90th percentile
    P95 = "p95"               # 95th percentile
    P99 = "p99"               # 99th percentile
    
    # Distribution
    DISTRIBUTION = "distribution"  # Full distribution histogram


@dataclass(frozen=True)
class AggregationDefinition:
    """
    Definition for an aggregation operation.
    
    Specifies how to aggregate telemetry data.
    """
    
    agg_type: AggregationType
    metric_name: str           # Metric to aggregate
    label_filter: Optional[Dict[str, str]] = None  # Filter by labels
    
    window_seconds: float = 60.0  # Aggregation window (rolling)
    bucket_count: int = 10        # Number of buckets for distribution


# =============================================================================
# KPI DEFINITIONS
# =============================================================================

class KPICategory(Enum):
    """Categories of Key Performance Indicators."""
    
    PERFORMANCE = "performance"     # Speed, latency, throughput
    RELIABILITY = "reliability"     # Error rates, success rates
    EFFICIENCY = "efficiency"       # Resource utilization
    SCALE = "scale"                 # Capacity, growth metrics
    HEALTH = "health"               # System health and status


@dataclass(frozen=True)
class KPIDefinition:
    """
    Definition for a Key Performance Indicator.
    
    Specifies how to compute and evaluate a KPI.
    """
    
    kpi_id: str                # Unique identifier
    name: str                  # Human-readable name
    
    category: KPICategory      # Category this KPI belongs to
    description: str           # What the KPI measures
    
    # Computation
    metric_names: List[str]    # Metrics used in computation
    formula: str               # Formula (Python expression with metrics)
    
    # Target/Thresholds
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    
    # Aggregation window
    window_seconds: float = 300.0  # Default 5 minutes
    
    @property
    def kpi_type(self) -> str:
        """Get KPI type name."""
        return self.name.lower().replace(" ", "_")


# =============================================================================
# ANOMALY DETECTION
# =============================================================================

class AnomalyDetectionStrategy(Enum):
    """Strategies for anomaly detection."""
    
    STATIC_THRESHOLD = "static_threshold"  # Fixed thresholds
    STD_DEVIATION = "std_deviation"        # Statistical deviation
    MOVING_AVERAGE = "moving_average"      # Deviation from trend
    ISOLATION_FOREST = "isolation_forest"  # ML-based detection


@dataclass(frozen=True)
class AnomalyDetectionConfig:
    """
    Configuration for anomaly detection.
    """
    
    strategy: AnomalyDetectionStrategy
    metric_name: str
    
    # Strategy-specific parameters
    threshold_std_dev: float = 3.0      # For std_deviation
    window_seconds: float = 300.0       # Window size
    sensitivity: float = 1.0            # Sensitivity factor (1.0 = default)


# =============================================================================
# TRENDS AND FORECASTING
# =============================================================================

@dataclass(frozen=True)
class TrendData:
    """
    Collected data for trend analysis.
    
    Maintains a rolling window of measurements for trend computation.
    """
    
    metric_name: str
    
    # Measurements (timestamp, value) pairs
    measurements: List[tuple] = field(default_factory=list)
    
    # Configuration
    max_measurements: int = 1000
    window_seconds: float = 3600.0  # Keep last hour of data


@dataclass(frozen=True)
class TrendAnalysis:
    """
    Analysis of a trend over time.
    
    Contains computed trend metrics.
    """
    
    metric_name: str
    analysis_time_utc: float
    
    # Basic stats
    count: int
    min_value: float
    max_value: float
    avg_value: float
    
    # Trend direction and rate
    trend_direction: str = "stable"  # increasing, decreasing, stable
    trend_rate_per_second: Optional[float] = None
    
    # Forecast (if applicable)
    forecast_1h: Optional[float] = None
    forecast_24h: Optional[float] = None


# =============================================================================
# HEALTH SCORING
# =============================================================================

class HealthScoreSource(Enum):
    """Sources for health score computation."""
    
    ERROR_RATE = "error_rate"           # Error rate contribution
    LATENCY_P99 = "latency_p99"         # P99 latency contribution
    CPU_USAGE = "cpu_usage"             # CPU utilization contribution
    MEMORY_USAGE = "memory_usage"       # Memory utilization contribution
    DISK_USAGE = "disk_usage"           # Disk utilization contribution
    QUEUE_DEPTH = "queue_depth"         # Queue backlog contribution


@dataclass(frozen=True)
class HealthScoreComponent:
    """
    A component contributing to overall health score.
    
    Each source contributes a weighted portion of the total score.
    """
    
    source: HealthScoreSource
    weight: float              # 0.0 - 1.0
    current_value: float       # Current measurement
    target_value: float        # Target value
    
    @property
    def component_score(self) -> float:
        """Compute this component's contribution to health score (0-1)."""
        if self.current_value <= self.target_value:
            return 1.0
        
        # Score decreases as we exceed target
        ratio = self.current_value / self.target_value
        return max(0.0, 1.0 - (ratio - 1.0))


@dataclass(frozen=True)
class HealthScoreReport:
    """
    Complete health score report.
    
    Contains all component scores and the aggregate.
    """
    
    runtime_id: str
    report_time_utc: float
    
    # Component scores
    components: Dict[HealthScoreSource, HealthScoreComponent]
    
    @property
    def total_score(self) -> float:
        """Compute weighted average of all components."""
        if not self.components:
            return 1.0
        
        total_weight = sum(c.weight for c in self.components.values())
        if total_weight <= 0:
            return 1.0
        
        weighted_sum = sum(
            c.component_score * c.weight
            for c in self.components.values()
        )
        
        return weighted_sum / total_weight
    
    @property
    def health_status(self) -> str:
        """Get overall health status."""
        score = self.total_score
        
        if score >= 0.95:
            return "healthy"
        elif score >= 0.80:
            return "degraded"
        elif score >= 0.60:
            return "busy"
        elif score >= 0.40:
            return "recovering"
        else:
            return "failed"


# =============================================================================
# ANALYTICS PIPELINE
# =============================================================================

class AnalyticsPipeline(ABC):
    """
    Abstract base class for analytics pipelines.
    
    Pipelines consume telemetry data and produce analytical results.
    """
    
    @abstractmethod
    def process_event(self, event: Dict[str, Any]) -> None:
        """Process a single telemetry event."""
        ...
    
    @abstractmethod
    def process_batch(self, events: List[Dict[str, Any]]) -> None:
        """Process a batch of events."""
        ...
    
    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        """Get current analytics results."""
        ...


# =============================================================================
# AGGREGATION PIPELINE
# =============================================================================

class AggregationPipeline(AnalyticsPipeline):
    """
    Pipeline that aggregates telemetry metrics.
    
    Maintains rolling windows and computes statistics over time.
    """
    
    def __init__(
        self,
        runtime_id: str,
        aggregation_definitions: Optional[List[AggregationDefinition]] = None,
        max_data_points_per_metric: int = 10000,
    ) -> None:
        self.runtime_id = runtime_id
        self._max_points = max_data_points_per_metric
        
        # Aggregation definitions by metric name
        self._definitions: Dict[str, List[AggregationDefinition]] = {}
        for defn in aggregation_definitions or []:
            if defn.metric_name not in self._definitions:
                self._definitions[defn.metric_name] = []
            self._definitions[defn.metric_name].append(defn)
        
        # Collected data
        self._data: Dict[str, List[float]] = {}
    
    def process_event(self, event: Dict[str, Any]) -> None:
        """Process a telemetry event."""
        metric_name = event.get("metric_name", "")
        value = event.get("value")
        
        if value is not None and isinstance(value, (int, float)):
            if metric_name not in self._data:
                self._data[metric_name] = []
            
            # Enforce max points
            while len(self._data[metric_name]) >= self._max_points:
                self._data[metric_name].pop(0)
            
            self._data[metric_name].append(float(value))
    
    def process_batch(self, events: List[Dict[str, Any]]) -> None:
        """Process a batch of events."""
        for event in events:
            self.process_event(event)
    
    def get_results(self) -> Dict[str, Any]:
        """Get aggregated results."""
        results = {}
        
        for metric_name, values in self._data.items():
            if not values:
                continue
            
            # Compute basic stats
            count = len(values)
            total = sum(values)
            
            results[metric_name] = {
                "count": count,
                "sum": total,
                "avg": total / count if count > 0 else 0.0,
                "min": min(values),
                "max": max(values),
            }
            
            # Compute percentiles
            sorted_values = sorted(values)
            for pct in [50, 90, 95, 99]:
                idx = int(len(sorted_values) * pct / 100)
                if idx < len(sorted_values):
                    results[metric_name][f"p{pct}"] = sorted_values[idx]
        
        return {
            "runtime_id": self.runtime_id,
            "timestamp_utc": time.time(),
            "metrics": results,
        }


# =============================================================================
# KPI COMPUTATION PIPELINE
# =============================================================================

class KPICalculationPipeline(AnalyticsPipeline):
    """
    Pipeline that computes Key Performance Indicators.
    
    Evaluates KPI definitions against collected metrics.
    """
    
    def __init__(
        self,
        runtime_id: str,
        kpi_definitions: Optional[List[KPIDefinition]] = None,
    ) -> None:
        self.runtime_id = runtime_id
        self._kpi_defs = {d.kpi_id: d for d in kpi_definitions or []}
        
        # Metric values by name (rolling window)
        self._metric_values: Dict[str, List[float]] = {}
    
    def process_event(self, event: Dict[str, Any]) -> None:
        """Process a telemetry event."""
        metric_name = event.get("metric_name", "")
        value = event.get("value")
        
        if value is not None and isinstance(value, (int, float)):
            if metric_name not in self._metric_values:
                self._metric_values[metric_name] = []
            
            # Keep last 1000 values per metric
            while len(self._metric_values[metric_name]) >= 1000:
                self._metric_values[metric_name].pop(0)
            
            self._metric_values[metric_name].append(float(value))
    
    def process_batch(self, events: List[Dict[str, Any]]) -> None:
        """Process a batch of events."""
        for event in events:
            self.process_event(event)
    
    def compute_kpi_value(self, kpi_def: KPIDefinition) -> float:
        """
        Compute a single KPI value from its metric dependencies.
        
        Args:
            kpi_def: The KPI definition to compute
            
        Returns:
            Computed KPI value
        """
        # Build metrics dictionary for formula evaluation
        metrics = {}
        for name in kpi_def.metric_names:
            values = self._metric_values.get(name, [])
            if values:
                metrics[name] = sum(values) / len(values)  # Average
        
        try:
            # Evaluate the formula (simplified - would need proper parser)
            if not kpi_def.formula:
                return 0.0
            
            # For now, return first metric as placeholder
            primary_metric = kpi_def.metric_names[0] if kpi_def.metric_names else ""
            return metrics.get(primary_metric, 0.0)
            
        except Exception:
            return 0.0
    
    def get_results(self) -> Dict[str, Any]:
        """Get computed KPI results."""
        results = {}
        
        for kpi_id, kpi_def in self._kpi_defs.items():
            value = self.compute_kpi_value(kpi_def)
            
            # Determine status
            status = "unknown"
            if kpi_def.critical_threshold and value >= kpi_def.critical_threshold:
                status = "critical"
            elif kpi_def.warning_threshold and value >= kpi_def.warning_threshold:
                status = "warning"
            elif kpi_def.target_value is not None:
                if abs(value - kpi_def.target_value) <= 0.1 * kpi_def.target_value:
                    status = "on_target"
                else:
                    status = "偏离目标"
            
            results[kpi_id] = {
                "name": kpi_def.name,
                "value": value,
                "status": status,
                "timestamp_utc": time.time(),
            }
        
        return {
            "runtime_id": self.runtime_id,
            "timestamp_utc": time.time(),
            "kpis": results,
        }


# =============================================================================
# HEALTH SCORING PIPELINE
# =============================================================================

class HealthScoringPipeline(AnalyticsPipeline):
    """
    Pipeline that computes overall system health score.
    
    Aggregates multiple health components into a single score.
    """
    
    def __init__(
        self,
        runtime_id: str,
        component_weights: Optional[Dict[HealthScoreSource, float]] = None,
    ) -> None:
        self.runtime_id = runtime_id
        
        # Default weights
        default_weights = {
            HealthScoreSource.ERROR_RATE: 0.25,
            HealthScoreSource.LATENCY_P99: 0.20,
            HealthScoreSource.CPU_USAGE: 0.15,
            HealthScoreSource.MEMORY_USAGE: 0.15,
            HealthScoreSource.DISK_USAGE: 0.10,
            HealthScoreSource.QUEUE_DEPTH: 0.15,
        }
        
        self._weights = component_weights or default_weights
        
        # Current measurements
        self._measurements: Dict[HealthScoreSource, float] = {}
    
    def process_event(self, event: Dict[str, Any]) -> None:
        """Process a telemetry event."""
        source_str = event.get("health_source", "")
        value = event.get("value")
        
        if value is not None and isinstance(value, (int, float)):
            try:
                source = HealthScoreSource(source_str)
                self._measurements[source] = float(value)
            except ValueError:
                pass  # Unknown source, ignore
    
    def process_batch(self, events: List[Dict[str, Any]]) -> None:
        """Process a batch of events."""
        for event in events:
            self.process_event(event)
    
    def get_results(self) -> Dict[str, Any]:
        """Get health score report."""
        components = {}
        
        for source, weight in self._weights.items():
            measurement = self._measurements.get(source, 0.0)
            
            # Set target values based on source type
            if source == HealthScoreSource.ERROR_RATE:
                target = 0.01  # 1% max error rate
            elif source == HealthScoreSource.CPU_USAGE:
                target = 0.70  # 70% max CPU
            elif source == HealthScoreSource.MEMORY_USAGE:
                target = 0.80  # 80% max memory
            else:
                target = 1.0  # Generic targets
            
            components[source] = HealthScoreComponent(
                source=source,
                weight=weight,
                current_value=measurement,
                target_value=target,
            )
        
        report = HealthScoreReport(
            runtime_id=self.runtime_id,
            report_time_utc=time.time(),
            components=components,
        )
        
        return {
            "runtime_id": self.runtime_id,
            "timestamp_utc": time.time(),
            "health_score": report.total_score,
            "status": report.health_status,
            "component_scores": {
                k.value: v.component_score for k, v in components.items()
            },
        }


__all__ = [
    # Aggregation
    "AggregationType",
    "AggregationDefinition",
    
    # KPIs
    "KPICategory",
    "KPIDefinition",
    
    # Anomaly detection
    "AnomalyDetectionStrategy",
    "AnomalyDetectionConfig",
    
    # Trends and forecasting
    "TrendData",
    "TrendAnalysis",
    
    # Health scoring
    "HealthScoreSource",
    "HealthScoreComponent",
    "HealthScoreReport",
    
    # Pipelines
    "AnalyticsPipeline",
    "AggregationPipeline",
    "KPICalculationPipeline",
    "HealthScoringPipeline",
]