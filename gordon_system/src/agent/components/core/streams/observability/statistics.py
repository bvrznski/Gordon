# Stream Statistics Layer - Phase 3.11.16
# =========================================

"""
Canonical Stream Statistics implementation.

Statistics are PASSIVE aggregated metrics:
- They NEVER influence execution flow
- They NEVER trigger actions or decisions
- They ONLY aggregate and analyze collected data

Supported statistics:
- AggregationType: SUM, AVG, MIN, MAX, COUNT, RATE, PCT_* (percentiles)
- MetricAggregator: Collects and aggregates metric points
- StatisticsSnapshot: Immutable snapshot of aggregated metrics
- TrendAnalysis: Historical trend analysis
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# AGGREGATION TYPES
# =============================================================================


class AggregationType(Enum):
    """
    Type of aggregation to apply.
    
    Categories:
        - COUNT: Count occurrences
        - SUM: Sum values
        - AVG: Average values
        - MIN/MAX: Find extremes
        - RATE: Calculate rate per time unit
        - PCT_*: Percentile calculations
    """
    # Basic aggregations
    COUNT = "count"                 # Number of occurrences
    SUM = "sum"                     # Sum of all values
    AVG = "avg"                     # Average value
    MIN = "min"                     # Minimum value
    MAX = "max"                     # Maximum value
    
    # Rate-based aggregations
    RATE_PER_SECOND = "rate_per_second"
    RATE_PER_MINUTE = "rate_per_minute"
    
    # Percentile-based aggregations
    P50 = "p50"                     # 50th percentile (median)
    P90 = "p90"                     # 90th percentile
    P95 = "p95"                     # 95th percentile
    P99 = "p99"                     # 99th percentile


# =============================================================================
# METRIC AGGREGATOR
# =============================================================================


@dataclass
class MetricAggregator:
    """
    Aggregates metric points into statistical summaries.
    
    This is a PASSIVE aggregator - it only calculates statistics from
    collected data. It never influences the execution flow.
    """
    
    # Configuration
    aggregation_type: AggregationType  # How to aggregate
    
    # Storage for raw values
    _values: List[float] = field(default_factory=list)
    _timestamps: List[float] = field(default_factory=list)
    
    # Time window (for rate calculations)
    _window_seconds: float = 60.0   # Default 1 minute window
    
    def add_value(self, value: float, timestamp: Optional[float] = None) -> None:
        """
        Add a value to the aggregation.
        
        This method is PASSIVE - it only stores the value for later
        statistical analysis.
        """
        self._values.append(value)
        self._timestamps.append(timestamp or time.time())
    
    def add_values(
        self,
        values: Tuple[float, ...],
        timestamps: Optional[Tuple[float, ...]] = None,
    ) -> None:
        """Add multiple values to the aggregation."""
        for i, value in enumerate(values):
            ts = timestamps[i] if timestamps and i < len(timestamps) else time.time()
            self.add_value(value, ts)
    
    def count(self) -> int:
        """Return count of values."""
        return len(self._values)
    
    def sum(self) -> float:
        """Calculate sum of all values."""
        return sum(self._values)
    
    def avg(self) -> float:
        """Calculate average of all values."""
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)
    
    def min(self) -> float:
        """Find minimum value."""
        if not self._values:
            return 0.0
        return min(self._values)
    
    def max(self) -> float:
        """Find maximum value."""
        if not self._values:
            return 0.0
        return max(self._values)
    
    def percentile(self, p: float) -> float:
        """
        Calculate the p-th percentile of values.
        
        Args:
            p: Percentile (0-100)
            
        Returns:
            Percentile value
        """
        if not self._values:
            return 0.0
        
        sorted_values = sorted(self._values)
        n = len(sorted_values)
        
        # Linear interpolation between closest ranks
        rank = (p / 100.0) * (n - 1)
        lower_idx = int(rank)
        upper_idx = min(lower_idx + 1, n - 1)
        
        fraction = rank - lower_idx
        return sorted_values[lower_idx] + fraction * (
            sorted_values[upper_idx] - sorted_values[lower_idx]
        )
    
    def rate_per_second(self) -> float:
        """Calculate average rate per second."""
        if len(self._timestamps) < 2:
            return 0.0
        
        time_span = max(1.0, self._timestamps[-1] - self._timestamps[0])
        return len(self._values) / time_span
    
    def snapshot(
        self,
        metric_name: str,
        stream_id: Optional[str] = None,
    ) -> "StatisticsSnapshot":
        """
        Create an immutable statistics snapshot.
        
        Args:
            metric_name: Name of the metric being aggregated
            stream_id: Optional stream identifier
            
        Returns:
            Immutable StatisticsSnapshot instance
        """
        return StatisticsSnapshot(
            snapshot_id=f"stat-{time.monotonic_ns()}-{hash(metric_name) % 1000:04d}",
            captured_at_utc=time.time(),
            metric_name=metric_name,
            stream_id=stream_id,
            aggregation_type=self.aggregation_type,
            count=len(self._values),
            sum_val=self.sum(),
            avg_val=self.avg(),
            min_val=self.min(),
            max_val=self.max(),
            p50=self.percentile(50),
            p90=self.percentile(90),
            p95=self.percentile(95),
            p99=self.percentile(99),
        )


# =============================================================================
# STATISTICS SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class StatisticsSnapshot:
    """
    Immutable snapshot of aggregated statistics.
    
    Contains statistical summaries for one or more metrics at a point in time.
    Used for monitoring and read-only inspection.
    """
    
    # Identity
    snapshot_id: str                # Unique ID for this snapshot
    
    # Timestamp
    captured_at_utc: float          # When snapshot was taken
    
    # Metric context
    metric_name: str                # Name of the metric
    stream_id: Optional[str] = None     # Which stream?
    
    # Aggregation configuration
    aggregation_type: AggregationType   # How values were aggregated
    
    # Basic statistics
    count: int                      # Number of values
    sum_val: float                  # Sum of all values
    avg_val: float                  # Average value
    min_val: float                  # Minimum value
    max_val: float                  # Maximum value
    
    # Percentile statistics
    p50: float                      # 50th percentile (median)
    p90: float                      # 90th percentile
    p95: float                      # 95th percentile
    p99: float                      # 99th percentile
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "captured_at_utc": self.captured_at_utc,
            "metric_name": self.metric_name,
            "stream_id": self.stream_id,
            "aggregation_type": self.aggregation_type.value,
            "count": self.count,
            "sum_val": self.sum_val,
            "avg_val": self.avg_val,
            "min_val": self.min_val,
            "max_val": self.max_val,
            "p50": self.p50,
            "p90": self.p90,
            "p95": self.p95,
            "p99": self.p99,
        }


# =============================================================================
# TREND ANALYSIS
# =============================================================================


@dataclass(frozen=True)
class TrendData:
    """
    Data for trend analysis.
    
    Contains historical data points for detecting trends over time.
    """
    
    # Timestamps and values
    timestamps: Tuple[float, ...]   # Time points (oldest to newest)
    values: Tuple[float, ...]       # Corresponding values
    
    def is_ascending(self) -> bool:
        """Check if values are generally increasing."""
        if len(self.values) < 2:
            return False
        return self.values[-1] > self.values[0]
    
    def is_descending(self) -> bool:
        """Check if values are generally decreasing."""
        if len(self.values) < 2:
            return False
        return self.values[-1] < self.values[0]
    
    def slope(self) -> float:
        """Calculate simple linear regression slope."""
        if len(self.values) < 2:
            return 0.0
        
        n = len(self.values)
        x_mean = sum(range(n)) / n
        y_mean = sum(self.values) / n
        
        numerator = sum((i - x_mean) * (y - y_mean) 
                       for i, y in enumerate(self.values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        return numerator / denominator


@dataclass(frozen=True)
class TrendAnalysis:
    """
    Analysis of trends over time.
    
    Provides statistical analysis of historical metric data to detect
    patterns and changes in behavior.
    """
    
    # Identity
    analysis_id: str                # Unique ID for this analysis
    
    # Timestamps
    period_start_utc: float         # Start of analysis period
    period_end_utc: float           # End of analysis period
    
    # Metric context
    metric_name: str                # Name of the metric
    stream_id: Optional[str] = None     # Which stream?
    
    # Trend data
    trend_data: TrendData           # Historical values and timestamps
    
    # Analysis results
    is_ascending: bool              # Are values increasing?
    is_descending: bool             # Are values decreasing?
    slope: float                    # Linear regression slope
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "analysis_id": self.analysis_id,
            "period_start_utc": self.period_start_utc,
            "period_end_utc": self.period_end_utc,
            "metric_name": self.metric_name,
            "stream_id": self.stream_id,
            "is_ascending": self.is_ascending,
            "is_descending": self.is_descending,
            "slope": self.slope,
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_metric_aggregator(
    aggregation_type: AggregationType = AggregationType.AVG,
) -> MetricAggregator:
    """Create a new metric aggregator."""
    return MetricAggregator(aggregation_type=aggregation_type)


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) 
                      for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Aggregation types
    "AggregationType",
    
    # Aggregators and snapshots
    "MetricAggregator",
    "StatisticsSnapshot",
    
    # Trend analysis
    "TrendData",
    "TrendAnalysis",
    
    # Factory functions
    "create_metric_aggregator",
    "dataclass_replace",
]