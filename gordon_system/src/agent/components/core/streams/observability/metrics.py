# Stream Metrics Layer - Phase 3.11.16
# ======================================

"""
Canonical Stream Metrics implementation.

Metrics are PASSIVE measurements of stream behavior:
- They NEVER influence execution flow
- They NEVER schedule or dispatch work
- They NEVER modify stream state
- They ONLY observe and quantify

Supported metrics:
- stream count: Total streams in system
- publication rate: Records published per second
- subscription rate: Records consumed per second  
- replay rate: Records replayed per second
- checkpoint rate: Checkpoints created per second
- backlog: Unprocessed records waiting
- queue depth: Current queue size
- throughput: Records processed over time
- latency: Time between operations
- congestion: Backpressure indicator
- rejection rate: Failed publications per second
- retry rate: Retried deliveries per second
- cursor lag: Position difference between cursors
- storage utilization: Storage usage percentage
- memory utilization: Memory usage percentage
- integrity failures: Integrity check failures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time
import uuid

# =============================================================================
# METRIC TYPES
# =============================================================================


class StreamMetricType(Enum):
    """
    Canonical stream metric types.
    
    Categories:
        - COUNTS: Event counters (publications, subscriptions)
        - RATES: Rate measurements (per second)
        - LEVELS: Current levels (backlog, queue depth)
        - TIMING: Duration measurements
        - PERCENTAGES: Ratios and utilization
    """
    # Count metrics
    STREAM_COUNT = "stream_count"                 # Total streams
    PUBLICATION_COUNT = "publication_count"       # Total publications
    SUBSCRIPTION_COUNT = "subscription_count"     # Total subscriptions
    REPLAY_COUNT = "replay_count"                 # Total replays
    CHECKPOINT_COUNT = "checkpoint_count"         # Checkpoints created
    
    # Rate metrics (per second)
    PUBLICATION_RATE = "publication_rate"
    SUBSCRIPTION_RATE = "subscription_rate"
    REPLAY_RATE = "replay_rate"
    CHECKPOINT_RATE = "checkpoint_rate"
    
    # Level metrics
    BACKLOG_SIZE = "backlog_size"                 # Unprocessed records
    QUEUE_DEPTH = "queue_depth"                   # Current queue size
    
    # Throughput metrics
    THROUGHPUT_RECORDS_PER_SECOND = "throughput_records_per_second"
    THROUGHPUT_BYTES_PER_SECOND = "throughput_bytes_per_second"
    
    # Timing metrics (milliseconds)
    PUBLICATION_LATENCY_MS = "publication_latency_ms"
    ROUTING_LATENCY_MS = "routing_latency_ms"
    SUBSCRIBER_LATENCY_MS = "subscriber_latency_ms"
    CHECKPOINT_LATENCY_MS = "checkpoint_latency_ms"
    REPLAY_LATENCY_MS = "replay_latency_ms"
    
    # Congestion metrics
    CONGESTION_LEVEL = "congestion_level"         # 0.0 to 1.0
    BACKPRESSURE_ACTIVE = "backpressure_active"   # boolean as percentage
    
    # Error/retry metrics (rates)
    REJECTION_RATE = "rejection_rate"
    RETRY_RATE = "retry_rate"
    
    # Cursor metrics
    CURSOR_LAG_RECORDS = "cursor_lag_records"     # Position difference
    
    # Resource utilization (percentage 0-100)
    STORAGE_UTILIZATION_PERCENT = "storage_utilization_percent"
    MEMORY_UTILIZATION_PERCENT = "memory_utilization_percent"
    
    # Integrity metrics
    INTEGRITY_FAILURE_COUNT = "integrity_failure_count"


@dataclass(frozen=True)
class StreamMetricPoint:
    """
    Immutable metric measurement point.
    
    A single observation of a metric at a specific time.
    """
    metric_type: StreamMetricType
    value: float
    
    # Identifiers
    stream_id: Optional[str] = None               # Which stream?
    component_id: Optional[str] = None            # Which component?
    
    # Timestamp
    recorded_at_utc: float = field(default_factory=time.time)
    
    # Labels for classification
    labels: Dict[str, str] = field(default_factory=dict)  # e.g., {"region": "us-east"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metric_type": self.metric_type.value,
            "value": self.value,
            "stream_id": self.stream_id,
            "component_id": self.component_id,
            "recorded_at_utc": self.recorded_at_utc,
            "labels": dict(self.labels),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamMetricPoint":
        """Create metric point from dictionary."""
        return cls(
            metric_type=StreamMetricType(data.get("metric_type", "")),
            value=float(data.get("value", 0.0)),
            stream_id=data.get("stream_id"),
            component_id=data.get("component_id"),
            recorded_at_utc=float(data.get("recorded_at_utc", time.time())),
            labels=dict(data.get("labels", {})),
        )


@dataclass(frozen=True)
class StreamMetricsSnapshot:
    """
    Immutable snapshot of all metrics at a point in time.
    
    Used for persistence, reporting, and read-only inspection.
    Contains only bounded data - no live objects or references.
    """
    
    # Timestamp
    captured_at_utc: float = field(default_factory=time.time)
    
    # Metrics by type
    metric_points: Tuple[StreamMetricPoint, ...] = field(default_factory=tuple)
    
    # Summary statistics
    stream_count: int = 0
    active_streams: int = 0
    total_publications: int = 0
    total_subscriptions: int = 0
    
    @classmethod
    def create_empty(cls) -> "StreamMetricsSnapshot":
        """Create an empty snapshot."""
        return cls()

    @classmethod
    def from_points(
        cls,
        points: Tuple[StreamMetricPoint, ...]
    ) -> "StreamMetricsSnapshot":
        """Create snapshot from metric points."""
        return cls(metric_points=points)

    def get_metric(self, metric_type: StreamMetricType) -> Optional[float]:
        """Get a specific metric value by type."""
        for point in self.metric_points:
            if point.metric_type == metric_type:
                return point.value
        return None

    def filter_by_stream(
        self,
        stream_id: str
    ) -> "StreamMetricsSnapshot":
        """Filter metrics to only those from a specific stream."""
        filtered = tuple(p for p in self.metric_points if p.stream_id == stream_id)
        return dataclass_replace(self, metric_points=filtered)

    def filter_by_component(
        self,
        component_id: str
    ) -> "StreamMetricsSnapshot":
        """Filter metrics to only those from a specific component."""
        filtered = tuple(p for p in self.metric_points if p.component_id == component_id)
        return dataclass_replace(self, metric_points=filtered)


# =============================================================================
# METRICS AGGREGATOR
# =============================================================================


@dataclass
class StreamMetricsAccumulator:
    """
    Accumulates and aggregates stream metrics.
    
    This is a stateful accumulator that maintains running statistics.
    It NEVER modifies the streams it observes.
    
    Thread-safe for concurrent updates from multiple sources.
    """
    
    # Storage for metric points
    _points: List[StreamMetricPoint] = field(default_factory=list)
    
    # Counters for rate calculation
    _publication_count: int = 0
    _subscription_count: int = 0
    _replay_count: int = 0
    _checkpoint_count: int = 0
    
    # Time tracking for rates
    _start_time_utc: float = field(default_factory=time.time)
    
    def record(
        self,
        metric_type: StreamMetricType,
        value: float,
        stream_id: Optional[str] = None,
        component_id: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Record a single metric observation.
        
        This method is PASSIVE - it only stores the measurement.
        It never influences execution.
        """
        point = StreamMetricPoint(
            metric_type=metric_type,
            value=value,
            stream_id=stream_id,
            component_id=component_id,
            recorded_at_utc=time.time(),
            labels=dict(labels or {}),
        )
        self._points.append(point)
    
    def increment_publication(self) -> None:
        """Record a publication event."""
        self._publication_count += 1
    
    def increment_subscription(self) -> None:
        """Record a subscription event."""
        self._subscription_count += 1
    
    def increment_replay(self) -> None:
        """Record a replay event."""
        self._replay_count += 1
    
    def increment_checkpoint(self) -> None:
        """Record a checkpoint creation."""
        self._checkpoint_count += 1
    
    def snapshot(
        self,
        stream_count: int = 0,
        active_streams: int = 0,
        total_publications: int = 0,
        total_subscriptions: int = 0,
    ) -> StreamMetricsSnapshot:
        """
        Create an immutable snapshot of current metrics.
        
        This is the PRIMARY way to access metric data for inspection.
        The snapshot contains only bounded data - no live references.
        """
        elapsed = time.time() - self._start_time_utc
        rates = []
        if elapsed > 0:
            rates = [
                StreamMetricPoint(
                    metric_type=StreamMetricType.PUBLICATION_RATE,
                    value=self._publication_count / elapsed,
                    recorded_at_utc=time.time(),
                ),
                StreamMetricPoint(
                    metric_type=StreamMetricType.SUBSCRIPTION_RATE,
                    value=self._subscription_count / elapsed,
                    recorded_at_utc=time.time(),
                ),
            ]
        
        # Add count metrics
        counts = [
            StreamMetricPoint(
                metric_type=StreamMetricType.STREAM_COUNT,
                value=float(stream_count),
                recorded_at_utc=time.time(),
            ),
            StreamMetricPoint(
                metric_type=StreamMetricType.PUBLICATION_COUNT,
                value=float(self._publication_count),
                recorded_at_utc=time.time(),
            ),
            StreamMetricPoint(
                metric_type=StreamMetricType.SUBSCRIPTION_COUNT,
                value=float(self._subscription_count),
                recorded_at_utc=time.time(),
            ),
            StreamMetricPoint(
                metric_type=StreamMetricType.REPLAY_COUNT,
                value=float(self._replay_count),
                recorded_at_utc=time.time(),
            ),
            StreamMetricPoint(
                metric_type=StreamMetricType.CHECKPOINT_COUNT,
                value=float(self._checkpoint_count),
                recorded_at_utc=time.time(),
            ),
        ]
        
        all_points = tuple(self._points + rates + counts)
        
        return StreamMetricsSnapshot(
            captured_at_utc=time.time(),
            metric_points=all_points,
            stream_count=stream_count,
            active_streams=active_streams,
            total_publications=total_publications,
            total_subscriptions=total_subscriptions,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_stream_metric_point(
    metric_type: StreamMetricType,
    value: float,
    stream_id: Optional[str] = None,
    component_id: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
) -> StreamMetricPoint:
    """
    Create a new stream metric point.
    
    This is the canonical factory for creating metric observations.
    
    Args:
        metric_type: The type of metric being recorded
        value: The measured value
        stream_id: Optional stream identifier
        component_id: Optional component identifier  
        labels: Optional label key-value pairs
        
    Returns:
        Immutable StreamMetricPoint instance
        
    Note: This function is PASSIVE - it only constructs the record.
    """
    return StreamMetricPoint(
        metric_type=metric_type,
        value=value,
        stream_id=stream_id,
        component_id=component_id,
        recorded_at_utc=time.time(),
        labels=dict(labels or {}),
    )


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
    # Types
    "StreamMetricType",
    
    # Records
    "StreamMetricPoint",
    "StreamMetricsSnapshot",
    
    # Aggregator
    "StreamMetricsAccumulator",
    
    # Factory functions
    "create_stream_metric_point",
    "dataclass_replace",
]