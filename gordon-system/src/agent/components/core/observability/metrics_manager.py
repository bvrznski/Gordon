# Core Metrics Manager
# ====================

"""
Metrics collection and aggregation for Gordon runtime.

This module provides:
- MetricsManager: Canonical authority for metric collection
- Counter, Gauge, Histogram, Timer metric types
- Metric aggregation with labels
- Sampling policies

Metrics are OBSERVATIONAL - they never change runtime behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto
import threading
import time
import uuid
import math

from .models import (
    MetricType,
    MetricPoint,
    MetricSnapshot,
)


# =============================================================================
# METRIC TYPES
# =============================================================================

class MetricConfig:
    """Configuration for a metric."""
    
    def __init__(
        self,
        name: str,
        metric_type: MetricType = MetricType.GAUGE,
        help_text: str = "",
        labels: Optional[List[str]] = None,
    ) -> None:
        self.name = name
        self.metric_type = metric_type
        self.help_text = help_text
        self.labels = labels or []


# =============================================================================
# METRIC IMPLEMENTATIONS
# =============================================================================

class Metric(ABC):
    """Base class for all metric types."""
    
    def __init__(self, config: MetricConfig) -> None:
        self.config = config
        self._lock = threading.RLock()
    
    @abstractmethod
    def collect(self) -> List[MetricPoint]:
        """Collect current metric values."""
        ...
    
    def name(self) -> str:
        """Return metric name."""
        return self.config.name
    
    @abstractmethod
    def to_snapshot(self, timestamp: float) -> Dict[str, List[MetricPoint]]:
        """Convert to snapshot format."""
        ...


class Counter(Metric):
    """
    Monotonically increasing counter.
    
    Use for counting events that only go up:
        - Task completions
        - Errors
        - Requests processed
    
    Usage:
        counter = Counter(MetricConfig("tasks.completed"))
        
        # Increment by 1
        counter.inc()
        
        # Increment by arbitrary amount
        counter.inc_by(5)
        
        # Get current value
        count = counter.get()
    """
    
    def __init__(self, config: MetricConfig) -> None:
        super().__init__(config)
        self._value: float = 0.0
    
    def inc(self) -> "Counter":
        """Increment by 1."""
        with self._lock:
            self._value += 1
        return self
    
    def inc_by(self, amount: float) -> "Counter":
        """Increment by arbitrary amount (must be >= 0)."""
        if amount < 0:
            raise ValueError("Counter increment must be non-negative")
        with self._lock:
            self._value += amount
        return self
    
    def get(self) -> float:
        """Get current value."""
        with self._lock:
            return self._value
    
    def collect(self) -> List[MetricPoint]:
        """Collect metric point."""
        with self._lock:
            return [MetricPoint(
                name=self.config.name,
                value=self._value,
                timestamp_utc=time.time(),
                metric_type=MetricType.COUNTER
            )]
    
    def to_snapshot(self, timestamp: float) -> Dict[str, List[MetricPoint]]:
        """Convert to snapshot format."""
        with self._lock:
            return {self.config.name: [MetricPoint(
                name=self.config.name,
                value=self._value,
                timestamp_utc=timestamp,
                metric_type=MetricType.COUNTER
            )]}


class Gauge(Metric):
    """
    Gauge metric that can go up or down.
    
    Use for values that fluctuate:
        - Memory usage
        - Queue depth
        - Active connections
    
    Usage:
        gauge = Gauge(MetricConfig("queue.depth"))
        
        # Set to value
        gauge.set(10)
        
        # Increment/decrement
        gauge.inc()
        gauge.dec()
        
        # Get current value
        depth = gauge.get()
    """
    
    def __init__(self, config: MetricConfig) -> None:
        super().__init__(config)
        self._value: float = 0.0
    
    def set(self, value: float) -> "Gauge":
        """Set to specific value."""
        with self._lock:
            self._value = value
        return self
    
    def inc(self) -> "Gauge":
        """Increment by 1."""
        with self._lock:
            self._value += 1
        return self
    
    def dec(self) -> "Gauge":
        """Decrement by 1."""
        with self._lock:
            self._value -= 1
        return self
    
    def add(self, amount: float) -> "Gauge":
        """Add arbitrary amount."""
        with self._lock:
            self._value += amount
        return self
    
    def sub(self, amount: float) -> "Gauge":
        """Subtract arbitrary amount."""
        with self._lock:
            self._value -= amount
        return self
    
    def get(self) -> float:
        """Get current value."""
        with self._lock:
            return self._value
    
    def collect(self) -> List[MetricPoint]:
        """Collect metric point."""
        with self._lock:
            return [MetricPoint(
                name=self.config.name,
                value=self._value,
                timestamp_utc=time.time(),
                metric_type=MetricType.GAUGE
            )]
    
    def to_snapshot(self, timestamp: float) -> Dict[str, List[MetricPoint]]:
        """Convert to snapshot format."""
        with self._lock:
            return {self.config.name: [MetricPoint(
                name=self.config.name,
                value=self._value,
                timestamp_utc=timestamp,
                metric_type=MetricType.GAUGE
            )]}


class Histogram(Metric):
    """
    Histogram for value distribution (percentiles).
    
    Tracks the distribution of values over time:
        - Request latency
        - Response sizes
        - Processing times
    
    Usage:
        histogram = Histogram(MetricConfig("request.duration"))
        
        # Observe a value
        histogram.observe(0.123)  # seconds
        
        # Get statistics
        count = histogram.count()
        sum_val = histogram.sum()
        percentiles = histogram.percentiles([50, 95, 99])
    """
    
    def __init__(
        self,
        config: MetricConfig,
        max_age_seconds: float = 60.0,
        bucket_count: int = 20,
    ) -> None:
        super().__init__(config)
        self._max_age = max_age_seconds
        self._bucket_count = bucket_count
        
        # Storage for observations
        self._values: List[float] = []
        self._timestamps: List[float] = []
        
        self._count: int = 0
        self._sum: float = 0.0
    
    def observe(self, value: float) -> "Histogram":
        """Record an observed value."""
        now = time.time()
        
        with self._lock:
            # Clean old entries
            cutoff = now - self._max_age
            while self._timestamps and self._timestamps[0] < cutoff:
                self._timestamps.pop(0)
                if self._values:
                    self._values.pop(0)
            
            self._values.append(value)
            self._timestamps.append(now)
            
            self._count += 1
            self._sum += value
        
        return self
    
    def count(self) -> int:
        """Get number of observations in window."""
        with self._lock:
            return len(self._values)
    
    def sum(self) -> float:
        """Get sum of all observed values."""
        with self._lock:
            return self._sum
    
    def avg(self) -> float:
        """Get average value."""
        with self._lock:
            if not self._values:
                return 0.0
            return self._sum / len(self._values)
    
    def min(self) -> float:
        """Get minimum observed value."""
        with self._lock:
            if not self._values:
                return 0.0
            return min(self._values)
    
    def max(self) -> float:
        """Get maximum observed value."""
        with self._lock:
            if not self._values:
                return 0.0
            return max(self._values)
    
    def percentiles(self, percentile_list: List[float]) -> Dict[float, float]:
        """
        Calculate percentiles.
        
        Args:
            percentile_list: List of percentile values (0-100)
            
        Returns:
            Dictionary mapping percentile to value
        """
        with self._lock:
            if not self._values:
                return {p: 0.0 for p in percentile_list}
            
            sorted_values = sorted(self._values)
            n = len(sorted_values)
            
            result = {}
            for p in percentile_list:
                # Linear interpolation
                k = (n - 1) * (p / 100.0)
                f = math.floor(k)
                c = math.ceil(k)
                
                if f == c:
                    result[p] = sorted_values[int(k)]
                else:
                    result[p] = sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)
            
            return result
    
    def collect(self) -> List[MetricPoint]:
        """Collect metric points (one per percentile)."""
        with self._lock:
            if not self._values:
                return []
            
            p50, p95, p99 = 0.0, 0.0, 0.0
            if len(self._values) >= 2:
                sorted_vals = sorted(self._values)
                n = len(sorted_vals)
                
                # P50
                k = (n - 1) * 0.5
                f, c = int(k), int(k) + 1
                p50 = sorted_vals[f] if f < n else sorted_vals[-1]
                if c < n:
                    p50 += (sorted_vals[c] - sorted_vals[f]) * (k - f)
                
                # P95
                k = (n - 1) * 0.95
                f, c = int(k), int(k) + 1
                p95 = sorted_vals[f] if f < n else sorted_vals[-1]
                if c < n:
                    p95 += (sorted_vals[c] - sorted_vals[f]) * (k - f)
                
                # P99
                k = (n - 1) * 0.99
                f, c = int(k), int(k) + 1
                p99 = sorted_vals[f] if f < n else sorted_vals[-1]
                if c < n:
                    p99 += (sorted_vals[c] - sorted_vals[f]) * (k - f)
            
            points = [
                MetricPoint(
                    name=f"{self.config.name}_p50",
                    value=p50,
                    timestamp_utc=time.time(),
                    metric_type=MetricType.HISTOGRAM
                ),
                MetricPoint(
                    name=f"{self.config.name}_p95",
                    value=p95,
                    timestamp_utc=time.time(),
                    metric_type=MetricType.HISTOGRAM
                ),
                MetricPoint(
                    name=f"{self.config.name}_p99",
                    value=p99,
                    timestamp_utc=time.time(),
                    metric_type=MetricType.HISTOGRAM
                ),
                MetricPoint(
                    name=f"{self.config.name}_count",
                    value=float(self._count),
                    timestamp_utc=time.time(),
                    metric_type=MetricType.COUNTER
                ),
                MetricPoint(
                    name=f"{self.config.name}_sum",
                    value=self._sum,
                    timestamp_utc=time.time(),
                    metric_type=MetricType.HISTOGRAM
                ),
            ]
            
            return points
    
    def to_snapshot(self, timestamp: float) -> Dict[str, List[MetricPoint]]:
        """Convert to snapshot format."""
        with self._lock:
            if not self._values:
                return {}
            
            sorted_vals = sorted(self._values)
            n = len(sorted_vals)
            
            # Calculate percentiles
            def percentile(pct: float) -> float:
                k = (n - 1) * pct
                f, c = int(k), int(k) + 1
                if f >= n:
                    return sorted_vals[-1]
                if c >= n:
                    return sorted_vals[f]
                return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)
            
            p50 = percentile(0.5)
            p95 = percentile(0.95)
            p99 = percentile(0.99)
            
            return {
                f"{self.config.name}_p50": [MetricPoint(
                    name=f"{self.config.name}_p50",
                    value=p50,
                    timestamp_utc=timestamp,
                    metric_type=MetricType.HISTOGRAM
                )],
                f"{self.config.name}_p95": [MetricPoint(
                    name=f"{self.config.name}_p95",
                    value=p95,
                    timestamp_utc=timestamp,
                    metric_type=MetricType.HISTOGRAM
                )],
                f"{self.config.name}_p99": [MetricPoint(
                    name=f"{self.config.name}_p99",
                    value=p99,
                    timestamp_utc=timestamp,
                    metric_type=MetricType.HISTOGRAM
                )],
                f"{self.config.name}_count": [MetricPoint(
                    name=f"{self.config.name}_count",
                    value=float(self._count),
                    timestamp_utc=timestamp,
                    metric_type=MetricType.COUNTER
                )],
                f"{self.config.name}_sum": [MetricPoint(
                    name=f"{self.config.name}_sum",
                    value=self._sum,
                    timestamp_utc=timestamp,
                    metric_type=MetricType.HISTOGRAM
                )],
            }


class Timer:
    """
    Context manager for timing operations.
    
    Records duration as a histogram observation.
    
    Usage:
        timer = Timer(MetricConfig("operation.duration"))
        
        with timer:
            # Do some work
            time.sleep(0.1)
        
        # Duration automatically recorded
    """
    
    def __init__(
        self,
        histogram: Histogram,
    ) -> None:
        self._histogram = histogram
    
    def __enter__(self) -> "Timer":
        self._start = time.monotonic()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        duration = time.monotonic() - self._start
        # Convert to seconds for standard metric unit
        self._histogram.observe(duration)


# =============================================================================
# METRICS MANAGER
# =============================================================================

class MetricsManager:
    """
    Canonical authority for metrics collection.
    
    Provides:
        - Metric registration and management
        - Automatic aggregation
        - Snapshot generation
    
    INVAR: Exactly one MetricsManager exists per runtime.
    INVAR: Metrics are observational - never change runtime behavior.
    
    Usage:
        # Create manager (runtime-scoped)
        manager = MetricsManager(runtime_id="runtime_123")
        
        # Register metrics
        counter = manager.create_counter("tasks.completed", help_text="Tasks completed")
        gauge = manager.create_gauge("queue.depth", help_text="Current queue depth")
        histogram = manager.create_histogram("request.duration", help_text="Request duration")
        
        # Use metrics
        counter.inc()
        gauge.set(10)
        with Timer(histogram):
            do_work()
        
        # Get snapshot for export
        snapshot = manager.get_snapshot()
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        self._lock = threading.RLock()
        
        # Registered metrics by name
        self._metrics: Dict[str, Metric] = {}
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    # ------------------------------------------------------------------
    # Metric Creation
    # ------------------------------------------------------------------
    
    def create_counter(
        self,
        name: str,
        help_text: str = "",
        labels: Optional[List[str]] = None,
    ) -> Counter:
        """
        Create or retrieve a counter metric.
        
        Args:
            name: Metric name (use dots for hierarchy)
            help_text: Human-readable description
            labels: List of label names for multi-dimensional metrics
            
        Returns:
            New Counter instance
        """
        with self._lock:
            if name not in self._metrics:
                config = MetricConfig(
                    name=name,
                    metric_type=MetricType.COUNTER,
                    help_text=help_text,
                    labels=labels or []
                )
                self._metrics[name] = Counter(config)
            
            return self._metrics[name]  # type: ignore
    
    def create_gauge(
        self,
        name: str,
        help_text: str = "",
        labels: Optional[List[str]] = None,
    ) -> Gauge:
        """
        Create or retrieve a gauge metric.
        
        Args:
            name: Metric name
            help_text: Human-readable description
            labels: List of label names
            
        Returns:
            New Gauge instance
        """
        with self._lock:
            if name not in self._metrics:
                config = MetricConfig(
                    name=name,
                    metric_type=MetricType.GAUGE,
                    help_text=help_text,
                    labels=labels or []
                )
                self._metrics[name] = Gauge(config)
            
            return self._metrics[name]  # type: ignore
    
    def create_histogram(
        self,
        name: str,
        help_text: str = "",
        labels: Optional[List[str]] = None,
        max_age_seconds: float = 60.0,
        bucket_count: int = 20,
    ) -> Histogram:
        """
        Create or retrieve a histogram metric.
        
        Args:
            name: Metric name
            help_text: Human-readable description
            labels: List of label names
            max_age_seconds: How long to keep observations
            bucket_count: Number of buckets for distribution
            
        Returns:
            New Histogram instance
        """
        with self._lock:
            if name not in self._metrics:
                config = MetricConfig(
                    name=name,
                    metric_type=MetricType.HISTOGRAM,
                    help_text=help_text,
                    labels=labels or []
                )
                self._metrics[name] = Histogram(
                    config,
                    max_age_seconds=max_age_seconds,
                    bucket_count=bucket_count
                )
            
            return self._metrics[name]  # type: ignore
    
    def create_timer(self, name: str) -> Timer:
        """
        Create a timer for an operation.
        
        Args:
            name: Histogram metric name
            
        Returns:
            Timer context manager
        """
        histogram = self.create_histogram(name)
        return Timer(histogram)
    
    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a registered metric by name."""
        with self._lock:
            return self._metrics.get(name)
    
    def get_snapshot(self) -> MetricSnapshot:
        """
        Get a snapshot of all metrics at current time.
        
        Returns:
            MetricSnapshot containing all metrics
        """
        with self._lock:
            timestamp = time.time()
            
            result: Dict[str, List[MetricPoint]] = {}
            for name, metric in self._metrics.items():
                try:
                    snapshot_dict = metric.to_snapshot(timestamp)
                    for k, v in snapshot_dict.items():
                        result[k] = v
                except Exception:
                    # Don't let a single metric failure affect the whole snapshot
                    continue
            
            return MetricSnapshot(
                runtime_id=self._runtime_id,
                timestamp_utc=timestamp,
                metrics=result
            )
    
    def get_all_metrics(self) -> List[Metric]:
        """Get all registered metrics."""
        with self._lock:
            return list(self._metrics.values())
    
    # ------------------------------------------------------------------
    # Convenience Methods (for direct use without creating metric first)
    # ------------------------------------------------------------------
    
    def record_counter(
        self,
        name: str,
        amount: float = 1.0,
    ) -> None:
        """
        Record a counter value directly.
        
        Creates the metric if it doesn't exist.
        
        Args:
            name: Metric name
            amount: Amount to increment by (default 1)
        """
        metric = self.create_counter(name)
        metric.inc_by(amount)
    
    def set_gauge(
        self,
        name: str,
        value: float,
    ) -> None:
        """
        Set a gauge value directly.
        
        Creates the metric if it doesn't exist.
        
        Args:
            name: Metric name
            value: Value to set
        """
        metric = self.create_gauge(name)
        metric.set(value)
    
    def observe_histogram(
        self,
        name: str,
        value: float,
    ) -> None:
        """
        Record an observation in a histogram.
        
        Creates the metric if it doesn't exist.
        
        Args:
            name: Metric name
            value: Value to record
        """
        metric = self.create_histogram(name)
        metric.observe(value)


__all__ = [
    "MetricConfig",
    "Metric",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "MetricsManager",
]