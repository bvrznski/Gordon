# Core Observability Models
# =========================

"""
Immutable data models for observability.

This module provides the canonical telemetry taxonomy for Gordon Core:

TELEMETRY TAXONOMY:
1. LOGGING MODELS
   - LogRecord: Structured log entries with full context
   - LogLevel: Severity levels for logs
   - LogContext: Contextual information attached to logs
   - LogMetadata: Metadata about the logging operation

2. TELEMETRY EVENT MODELS
   - TelemetryEvent: Machine-oriented telemetry data
   - TelemetryEnvelope: Container for batched events
   - RuntimeEvent: Event envelope with correlation tracking

3. METRIC MODELS  
   - MetricPoint: Single metric observation
   - MetricSnapshot: Point-in-time snapshot of all metrics
   - MetricType: Counter, Gauge, Histogram, Timer types

4. TRACING MODELS
   - TraceId: Unique identifier for distributed traces
   - SpanId: Unique identifier for spans within a trace
   - SpanRecord: Immutable span record (in tracing.py)

5. CORRELATION MODELS
   - CorrelationContext: Runtime correlation state
   - CorrelationSnapshot: Snapshot of active correlations

6. DIAGNOSTIC MODELS
   - DiagnosticRecord: Structured diagnostic records
   - DiagnosticReport: Collection of diagnostic findings

7. AUDIT MODELS  
   - AuditRecord: Immutable audit trail entries

All models are immutable (frozen dataclasses) and hashable.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum, auto
import uuid
import time


# =============================================================================
# LOGGING MODELS
# =============================================================================

class LogLevel(Enum):
    """
    Log severity levels for structured logging.
    
    Level ordering (lowest to highest):
        TRACE < DEBUG < INFO < NOTICE < WARNING < ERROR < CRITICAL
    
    Usage:
        # Use enum directly
        level = LogLevel.INFO
        
        # Check level properties
        if level >= LogLevel.WARNING:
            # High-priority logging path
            pass
        
        # Convert to string
        str(level)  # "INFO"
    """
    
    TRACE = auto()      # Verbose debugging details (rarely enabled)
    DEBUG = auto()      # Detailed diagnostic information
    INFO = auto()       # General operational information
    NOTICE = auto()     # Notable events requiring attention
    WARNING = auto()    # Potential issues or unexpected states
    ERROR = auto()      # Recoverable failures
    CRITICAL = auto()   # System-impacting conditions requiring immediate action
    
    @property
    def is_error(self) -> bool:
        """Check if this level represents an error condition."""
        return self in (LogLevel.ERROR, LogLevel.CRITICAL)
    
    @property
    def is_warning(self) -> bool:
        """Check if this level represents a warning or higher."""
        return self >= LogLevel.WARNING
    
    @property
    def priority(self) -> int:
        """Return numeric priority for comparison (higher = more severe)."""
        priorities = {
            LogLevel.TRACE: 0,
            LogLevel.DEBUG: 1,
            LogLevel.INFO: 2,
            LogLevel.NOTICE: 3,
            LogLevel.WARNING: 4,
            LogLevel.ERROR: 5,
            LogLevel.CRITICAL: 6,
        }
        return priorities[self]
    
    @classmethod
    def from_string(cls, value: str) -> "LogLevel":
        """Parse a string into a LogLevel."""
        try:
            return cls[value.upper()]
        except KeyError:
            return LogLevel.INFO


@dataclass(frozen=True)
class LogContext:
    """
    Contextual information attached to log records.
    
    Provides runtime and execution context that helps correlate logs
    across subsystem boundaries.
    
    Usage:
        ctx = LogContext(
            runtime_id="runtime_123",
            correlation_id="req_abc",
            entity_id="task_xyz"
        )
        
        # Create a log with this context
        log = LogRecord(
            level=LogLevel.INFO,
            message="Task completed",
            context=ctx
        )
    """
    
    runtime_id: str  # Unique runtime instance identifier
    
    # Correlation identifiers for traceability
    correlation_id: Optional[str] = None   # Groups related operations (e.g., request ID)
    causation_id: Optional[str] = None     # Identifies the causing event
    session_id: Optional[str] = None       # User/session context
    request_id: Optional[str] = None       # External request identifier
    
    # Execution context
    entity_id: Optional[str] = None        # Entity being operated on
    task_id: Optional[str] = None          # Task execution context
    parent_task_id: Optional[str] = None   # Parent task for hierarchy
    
    # Tracing identifiers
    trace_id: Optional[str] = None         # Distributed trace ID
    span_id: Optional[str] = None          # Span within the trace
    parent_span_id: Optional[str] = None   # Parent span for nesting


@dataclass(frozen=True)
class LogMetadata:
    """
    Metadata about a log record's generation.
    
    Provides system-level information about how and when the log was created.
    """
    
    source_module: str                    # Module that generated the log
    source_function: Optional[str] = None  # Function/method name
    source_file: Optional[str] = None      # Source file path
    source_line: Optional[int] = None      # Line number in source file
    
    thread_id: Optional[int] = None        # Thread that generated the log
    process_id: Optional[int] = None       # Process ID
    
    timestamp_utc: float = field(default_factory=time.time)  # Wall-clock time
    monotonic_time: float = field(default_factory=time.monotonic)  # Monotonic time for ordering
    
    # Log format version (for backward compatibility)
    format_version: int = 1


@dataclass(frozen=True)
class LogRecord:
    """
    Immutable structured log record.
    
    A complete log entry with all contextual information attached.
    Logs are immutable - once created, they cannot be modified.
    
    Usage:
        # Create a log directly
        log = LogRecord(
            level=LogLevel.INFO,
            message="Task completed successfully",
            context=context,
            metadata=metadata,
            payload={"task_id": "abc", "duration_ms": 123}
        )
        
        # Or use the factory function
        log = create_log(
            LogLevel.INFO,
            "Task completed",
            task_id="abc",
            duration_ms=123
        )
    """
    
    # Core log data
    level: LogLevel                        # Severity level
    message: str                          # Human-readable message
    
    # Context and metadata
    context: LogContext                   # Runtime context
    metadata: LogMetadata                 # Log generation metadata
    
    # Payload with domain-specific data (bounded for safety)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Redaction tracking
    redacted_fields: Set[str] = field(default_factory=set)  # Fields that were redacted
    is_redacted: bool = False              # Whether sensitive data was removed
    
    def __hash__(self) -> int:
        """Hash by event_id for set/dict operations."""
        return hash(self.context.runtime_id + self.metadata.timestamp_utc.__str__())
    
    @property
    def event_id(self) -> str:
        """Get a unique event identifier."""
        # Generate stable but unique ID from log properties
        return f"log_{self.context.runtime_id}_{self.metadata.monotonic_time:.6f}"
    
    def with_payload(self, key: str, value: Any) -> "LogRecord":
        """Return a copy with an additional payload entry."""
        new_payload = dict(self.payload)
        new_payload[key] = value
        return LogRecord(
            level=self.level,
            message=self.message,
            context=self.context,
            metadata=self.metadata,
            payload=new_payload,
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def with_severity(self, level: LogLevel) -> "LogRecord":
        """Return a copy with updated severity."""
        return LogRecord(
            level=level,
            message=self.message,
            context=self.context,
            metadata=self.metadata,
            payload=dict(self.payload),
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert log record to JSON-serializable dictionary.
        
        Preserves all data for external transport/storage.
        """
        return {
            "event_id": self.event_id,
            "level": self.level.name if hasattr(self.level, 'name') else str(self.level),
            "message": self.message,
            "context": {
                "runtime_id": self.context.runtime_id,
                "correlation_id": self.context.correlation_id,
                "causation_id": self.context.causation_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "entity_id": self.context.entity_id,
                "task_id": self.context.task_id,
                "parent_task_id": self.context.parent_task_id,
                "trace_id": self.context.trace_id,
                "span_id": self.context.span_id,
                "parent_span_id": self.context.parent_span_id,
            },
            "metadata": {
                "source_module": self.metadata.source_module,
                "source_function": self.metadata.source_function,
                "source_file": self.metadata.source_file,
                "source_line": self.metadata.source_line,
                "thread_id": self.metadata.thread_id,
                "process_id": self.metadata.process_id,
                "timestamp_utc": self.metadata.timestamp_utc,
                "monotonic_time": self.metadata.monotonic_time,
            },
            "payload": self.payload,
            "redacted_fields": list(self.redacted_fields),
            "is_redacted": self.is_redacted
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogRecord":
        """Create a log record from a dictionary."""
        # Parse level string to enum if needed
        level_value = data.get("level", LogLevel.INFO.name)
        if isinstance(level_value, str):
            try:
                level = LogLevel[level_value]
            except KeyError:
                level = LogLevel.INFO
        else:
            level = level_value
        
        context_data = data.get("context", {})
        metadata_data = data.get("metadata", {})
        
        return cls(
            level=level,
            message=data.get("message", ""),
            context=LogContext(
                runtime_id=context_data.get("runtime_id", ""),
                correlation_id=context_data.get("correlation_id"),
                causation_id=context_data.get("causation_id"),
                session_id=context_data.get("session_id"),
                request_id=context_data.get("request_id"),
                entity_id=context_data.get("entity_id"),
                task_id=context_data.get("task_id"),
                parent_task_id=context_data.get("parent_task_id"),
                trace_id=context_data.get("trace_id"),
                span_id=context_data.get("span_id"),
                parent_span_id=context_data.get("parent_span_id")
            ),
            metadata=LogMetadata(
                source_module=metadata_data.get("source_module", "unknown"),
                source_function=metadata_data.get("source_function"),
                source_file=metadata_data.get("source_file"),
                source_line=metadata_data.get("source_line"),
                thread_id=metadata_data.get("thread_id"),
                process_id=metadata_data.get("process_id"),
                timestamp_utc=metadata_data.get("timestamp_utc", time.time()),
                monotonic_time=metadata_data.get("monotonic_time", time.monotonic())
            ),
            payload=data.get("payload", {}),
            redacted_fields=set(data.get("redacted_fields", [])),
            is_redacted=data.get("is_redacted", False)
        )


# =============================================================================
# FACTORY FUNCTIONS FOR LOGS
# =============================================================================

def create_log(
    level: LogLevel,
    message: str,
    runtime_id: str = "",
    correlation_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    parent_task_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    **payload
) -> LogRecord:
    """
    Create a structured log record with common defaults.
    
    Args:
        level: Severity level for this log
        message: Human-readable summary
        runtime_id: Runtime instance identifier
        correlation_id: Groups related operations (e.g., request ID)
        entity_id: Entity being operated on
        task_id: Task execution context
        parent_task_id: Parent task for hierarchy
        trace_id: Distributed trace identifier
        span_id: Span within the trace
        **payload: Domain-specific data
        
    Returns:
        A new LogRecord instance
    """
    # Generate identifiers if not provided
    if runtime_id == "":
        runtime_id = str(uuid.uuid4())
    
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    now_monotonic = time.monotonic()
    now_wallclock = time.time()
    
    context = LogContext(
        runtime_id=runtime_id,
        correlation_id=correlation_id,
        entity_id=entity_id,
        task_id=task_id,
        parent_task_id=parent_task_id,
        trace_id=trace_id,
        span_id=span_id
    )
    
    metadata = LogMetadata(
        source_module="unknown",
        timestamp_utc=now_wallclock,
        monotonic_time=now_monotonic
    )
    
    return LogRecord(
        level=level,
        message=message,
        context=context,
        metadata=metadata,
        payload=payload
    )


def create_debug_log(
    message: str,
    **kwargs
) -> LogRecord:
    """Create a DEBUG-level log record."""
    return create_log(LogLevel.DEBUG, message, **kwargs)


def create_info_log(
    message: str,
    **kwargs
) -> LogRecord:
    """Create an INFO-level log record."""
    return create_log(LogLevel.INFO, message, **kwargs)


def create_notice_log(
    message: str,
    **kwargs
) -> LogRecord:
    """Create a NOTICE-level log record."""
    return create_log(LogLevel.NOTICE, message, **kwargs)


def create_warning_log(
    message: str,
    **kwargs
) -> LogRecord:
    """Create a WARNING-level log record."""
    return create_log(LogLevel.WARNING, message, **kwargs)


def create_error_log(
    message: str,
    exception: Optional[Exception] = None,
    **kwargs
) -> LogRecord:
    """Create an ERROR-level log record with optional exception context."""
    payload = dict(kwargs.pop("payload", {}))
    
    if exception is not None:
        payload["exception_type"] = type(exception).__name__
        payload["exception_message"] = str(exception)
    
    return create_log(LogLevel.ERROR, message, payload=payload, **kwargs)


def create_critical_log(
    message: str,
    **kwargs
) -> LogRecord:
    """Create a CRITICAL-level log record."""
    return create_log(LogLevel.CRITICAL, message, **kwargs)


# =============================================================================
# TELEMETRY MODELS
# =============================================================================

@dataclass(frozen=True)
class TelemetryEvent:
    """
    Immutable telemetry event for machine-oriented metrics.
    
    Telemetry events are distinct from logs - they're optimized for
    programmatic consumption and metric aggregation.
    
    Usage:
        # Create a simple event
        event = TelemetryEvent(
            name="task.duration",
            value=123.45,
            unit="milliseconds"
        )
        
        # With tags for filtering
        event = TelemetryEvent(
            name="api.request.count",
            value=1,
            tags={"endpoint": "/users", "method": "POST"}
        )
    """
    
    # Event identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""  # e.g., "metric", "log", "trace", "span"
    
    # Timestamps
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Context (same as logs for correlation)
    runtime_id: str = ""
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Tracing identifiers
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # Event content
    name: str = ""  # Metric/event name (e.g., "task.duration", "api.requests")
    
    # Value(s) - can be a single value or multiple
    value: Optional[float] = None
    values: Dict[str, float] = field(default_factory=dict)
    
    # Tags for filtering and grouping
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Unit information (for metrics)
    unit: Optional[str] = None  # e.g., "milliseconds", "bytes", "count"
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp_utc": self.timestamp_utc,
            "runtime_id": self.runtime_id,
            "correlation_id": self.correlation_id,
            "name": self.name,
            "value": self.value,
            "values": self.values,
            "tags": self.tags,
            "unit": self.unit
        }


@dataclass(frozen=True)
class TelemetryEnvelope:
    """
    Container for telemetry events with metadata.
    
    Used for batch processing, export, and transport of telemetry data.
    """
    
    # Envelope identification
    envelope_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: float = field(default_factory=time.time)
    
    # Source information
    source_component: str = ""  # Component that generated this envelope
    
    # Events contained in this envelope
    events: List[TelemetryEvent] = field(default_factory=list)
    
    # Envelope-level metadata
    tags: Dict[str, str] = field(default_factory=dict)
    
    @property
    def count(self) -> int:
        """Return number of events in this envelope."""
        return len(self.events)


# =============================================================================
# TRACING IDENTIFIERS
# =============================================================================

class TraceId(str):
    """
    Unique identifier for a distributed trace.
    
    A trace represents an end-to-end operation that may span multiple
    services and components. All spans within the same trace share
    the same TraceId.
    
    Usage:
        trace_id = TraceId.generate()
        span1_context = SpanContext(trace_id=trace_id, span_id=SpanId.generate())
    """
    
    @classmethod
    def generate(cls) -> "TraceId":
        """Generate a new random trace ID."""
        return cls(str(uuid.uuid4()))


class SpanId(str):
    """
    Unique identifier for a single span within a trace.
    
    Each operation within a trace has its own SpanId, and spans
    can be nested using parent_span_id relationships.
    
    Usage:
        span_id = SpanId.generate()
        # Create span with this ID
    """
    
    @classmethod
    def generate(cls) -> "SpanId":
        """Generate a new random span ID."""
        return cls(str(uuid.uuid4()))


# =============================================================================
# METRIC MODELS
# =============================================================================

class MetricType(Enum):
    """Types of metrics supported by MetricsManager."""
    
    COUNTER = "counter"      # Monotonically increasing count
    GAUGE = "gauge"          # Current value that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values (percentiles)
    TIMER = "timer"          # Duration measurements (specialized histogram)


@dataclass(frozen=True)
class MetricPoint:
    """
    Single metric observation with optional labels.
    
    Used for point-in-time metric snapshots and aggregation.
    """
    
    name: str                           # Metric name
    value: float                        # Observed value
    
    timestamp_utc: float = field(default_factory=time.time)
    
    # Labels for multi-dimensional metrics (prometheus-style)
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Metric type (for proper interpretation)
    metric_type: MetricType = MetricType.GAUGE


@dataclass(frozen=True)
class MetricSnapshot:
    """
    Snapshot of all metrics at a point in time.
    
    Provides a complete view of all registered metrics for
    reporting, export, and debugging purposes.
    """
    
    runtime_id: str
    timestamp_utc: float = field(default_factory=time.time)
    
    # All metric points by name
    metrics: Dict[str, List[MetricPoint]] = field(default_factory=dict)
    
    @property
    def count(self) -> int:
        """Return total number of metric points."""
        return sum(len(points) for points in self.metrics.values())
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert snapshot to JSON-serializable dictionary.
        
        Preserves all data for external transport/storage.
        """
        metrics_data: Dict[str, List[Dict[str, Any]]] = {}
        for name, points in self.metrics.items():
            metrics_data[name] = [
                {
                    "name": p.name,
                    "value": p.value,
                    "timestamp_utc": p.timestamp_utc,
                    "labels": dict(p.labels),
                    "metric_type": p.metric_type.name if hasattr(p.metric_type, 'name') else str(p.metric_type)
                }
                for p in points
            ]
        
        return {
            "runtime_id": self.runtime_id,
            "timestamp_utc": self.timestamp_utc,
            "count": self.count,
            "metrics": metrics_data
        }


# =============================================================================
# CORRELATION MODELS
# =============================================================================

@dataclass(frozen=True)
class CorrelationSnapshot:
    """
    Snapshot of runtime correlation state at a point in time.
    
    Captures all active correlation IDs and their relationships
    for debugging and trace reconstruction.
    """
    
    runtime_id: str
    timestamp_utc: float = field(default_factory=time.time)
    
    # Active correlation groups
    correlation_groups: Dict[str, List[str]] = field(default_factory=dict)  # correlation_id -> related_ids
    
    # Active traces
    active_traces: Dict[str, int] = field(default_factory=dict)  # trace_id -> span_count
    
    # Session tracking
    active_sessions: Dict[str, float] = field(default_factory=dict)  # session_id -> last_activity


@dataclass(frozen=True)
class CorrelationContext:
    """
    Runtime correlation context for a single operation.
    
    Used to propagate correlation state across subsystem boundaries
    without relying on thread-local storage.
    """
    
    runtime_id: str
    correlation_id: str
    causation_id: Optional[str] = None
    
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    task_id: Optional[str] = None
    parent_task_id: Optional[str] = None


# =============================================================================
# HEALTH MODEL (Canonical Health States)
# =============================================================================

class HealthStatus(Enum):
    """
    Canonical health states for runtime entities.
    
    State ordering and transitions are observable through telemetry contracts.
    
    States:
        - UNKNOWN: Not yet evaluated
        - INITIALIZING: Startup in progress
        - HEALTHY: Fully operational
        - DEGRADED: Operational with reduced capability
        - BUSY: Under heavy load, degraded performance
        - RECOVERING: Attempting to recover from failure
        - FAILED: Failed and not recoverable
        - OFFLINE: Intentionally stopped
    """
    
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BUSY = "busy"
    RECOVERING = "recovering"
    FAILED = "failed"
    OFFLINE = "offline"


@dataclass(frozen=True)
class HealthReport:
    """
    A collection of health states for entities at a point in time.
    
    Provides observability into runtime entity health transitions.
    """
    
    # Report identification
    report_id: str  # Unique identifier for this report
    
    # Report context
    subject: str                    # What these health states are about
    timestamp_utc: float = field(default_factory=time.time)  # When generated
    
    # Health states by entity
    states: Dict[str, HealthStatus] = field(default_factory=dict)
    
    # Aggregate state (determined from individual states)
    aggregate_state: HealthStatus = HealthStatus.UNKNOWN
    
    @property
    def count(self) -> int:
        """Return total number of health states."""
        return len(self.states)
    
    @property
    def has_issues(self) -> bool:
        """Check if any entities have issues (not healthy/offline)."""
        issue_states = (
            HealthStatus.UNKNOWN,
            HealthStatus.INITIALIZING,
            HealthStatus.DEGRADED,
            HealthStatus.BUSY,
            HealthStatus.RECOVERING,
            HealthStatus.FAILED
        )
        return any(s in issue_states for s in self.states.values())
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert report to JSON-serializable dictionary."""
        return {
            "report_id": self.report_id,
            "subject": self.subject,
            "timestamp_utc": self.timestamp_utc,
            "count": len(self.states),
            "aggregate_state": self.aggregate_state.value if hasattr(self.aggregate_state, 'value') else str(self.aggregate_state),
            "states": {k: (v.value if hasattr(v, 'value') else str(v)) for k, v in self.states.items()}
        }


# =============================================================================
# EXPORT MODELS
# =============================================================================

@dataclass(frozen=True)
class ExportBatch:
    """
    Batch of telemetry data prepared for export.
    
    Used by exporters to transport data to external systems
    (e.g., Prometheus, OpenTelemetry collectors).
    """
    
    # Required fields without defaults
    batch_id: str  # Generated in __post_init__
    
    # Data type and format
    export_format: str  # e.g., "json", "protobuf", "opentelemetry"
    data_type: str      # e.g., "logs", "metrics", "traces"
    
    # Payload
    payload: bytes
    
    # Optional fields with defaults (must come after required fields)
    timestamp_utc: float = field(default_factory=time.time)
    source_component: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    @property
    def size_bytes(self) -> int:
        """Return size of payload in bytes."""
        return len(self.payload)


__all__ = [
    # Logging models
    "LogLevel",
    "LogContext",
    "LogMetadata",
    "LogRecord",
    "create_log",
    "create_debug_log",
    "create_info_log",
    "create_notice_log",
    "create_warning_log",
    "create_error_log",
    "create_critical_log",
    
    # Telemetry models
    "TelemetryEvent",
    "TelemetryEnvelope",
    
    # Tracing identifiers
    "TraceId",
    "SpanId",
    
    # Metric models
    "MetricType",
    "MetricPoint",
    "MetricSnapshot",
    
    # Correlation models
    "CorrelationSnapshot",
    "CorrelationContext",
    
    # Health models (canonical)
    "HealthStatus",
    "HealthReport",
    
    # Export models
    "ExportBatch",
]
