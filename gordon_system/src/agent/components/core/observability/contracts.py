# Core Observability Contracts
# =============================

"""
Canonical telemetry contracts for Gordon Core.

This module defines the interfaces and contracts that all observability
implementations must follow to ensure consistency across subsystems.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Protocol,
    Callable,
    runtime_checkable,
)
from enum import Enum, auto
import time
import uuid


# =============================================================================
# TELEMETRY VERSIONING
# =============================================================================

class TelemetryVersion(Enum):
    """
    Canonical telemetry contract versions.
    
    Each telemetry type has its own version number. Breaking changes require
    incrementing the major version.
    """
    
    V1_0_0 = "1.0.0"  # Initial stable release
    
    @property
    def major(self) -> int:
        """Return major version number."""
        return int(self.value.split(".")[0])
    
    @property
    def minor(self) -> int:
        """Return minor version number."""
        return int(self.value.split(".")[1])
    
    @property
    def patch(self) -> int:
        """Return patch version number."""
        return int(self.value.split(".")[2])


# =============================================================================
# CORRELATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class CorrelationContract:
    """
    Contract for correlation ID propagation across subsystems.
    
    ALL telemetry MUST include these correlation identifiers to enable
    end-to-end traceability.
    """
    
    version: str = "1.0.0"
    
    # Core correlation identifiers (all must be present if available)
    trace_id: Optional[str] = None      # Distributed trace ID
    span_id: Optional[str] = None       # Current span within trace
    correlation_id: Optional[str] = None  # Request/group correlation
    
    # Contextual identifiers
    session_id: Optional[str] = None    # User/session context
    request_id: Optional[str] = None    # External request identifier
    task_id: Optional[str] = None       # Task execution context
    
    def is_complete(self) -> bool:
        """Check if all required correlation IDs are present."""
        return self.correlation_id is not None and self.trace_id is not None
    
    def to_headers(self) -> Dict[str, str]:
        """
        Convert correlation contract to header format for propagation.
        
        Returns:
            Dictionary suitable for HTTP/header-based propagation
        """
        result: Dict[str, str] = {}
        
        if self.trace_id:
            result["X-Trace-ID"] = self.trace_id
        if self.span_id:
            result["X-Span-ID"] = self.span_id
        if self.correlation_id:
            result["X-Correlation-ID"] = self.correlation_id
        if self.session_id:
            result["X-Session-ID"] = self.session_id
        if self.request_id:
            result["X-Request-ID"] = self.request_id
        if self.task_id:
            result["X-Task-ID"] = self.task_id
        
        return result
    
    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> "CorrelationContract":
        """
        Create correlation contract from header dictionary.
        
        Args:
            headers: Dictionary of header values
            
        Returns:
            CorrelationContract with values extracted from headers
        """
        return cls(
            trace_id=headers.get("X-Trace-ID"),
            span_id=headers.get("X-Span-ID"),
            correlation_id=headers.get("X-Correlation-ID"),
            session_id=headers.get("X-Session-ID"),
            request_id=headers.get("X-Request-ID"),
            task_id=headers.get("X-Task-ID"),
        )


# =============================================================================
# TIMESTAMP CONTRACT
# =============================================================================

@dataclass(frozen=True)
class TimestampContract:
    """
    Contract for timestamp formatting in all telemetry.
    
    All observability data must include timestamps in canonical format
    to enable accurate ordering and correlation.
    """
    
    # Wall-clock time (UTC) - required field (no default)
    timestamp_utc: float  # Unix epoch seconds with sub-second precision
    
    # Optional fields with defaults
    version: str = "1.0.0"  # Contract version
    
    # Monotonic time (for ordering within this process)
    monotonic_time: float = field(default_factory=time.monotonic)  # Process monotonic timestamp
    
    # Timezone information (ISO 8601 format, e.g., "+00:00")
    timezone_offset: str = "Z"  # UTC by default
    
    @property
    def timestamp_iso(self) -> str:
        """Return ISO 8601 formatted timestamp."""
        import datetime
        dt = datetime.datetime.fromtimestamp(self.timestamp_utc, tz=datetime.timezone.utc)
        return dt.isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "timestamp_utc": self.timestamp_utc,
            "monotonic_time": self.monotonic_time,
            "timezone_offset": self.timezone_offset,
            "timestamp_iso": self.timestamp_iso,
        }


# =============================================================================
# METADATA CONTRACT
# =============================================================================

@dataclass(frozen=True)
class MetadataContract:
    """
    Contract for structured metadata in all telemetry.
    
    Every telemetry event must include this metadata for proper
    categorization and filtering.
    """
    
    # Required fields (no defaults) - must come first
    source_component: str  # Component generating the telemetry
    runtime_id: str  # Runtime instance identifier
    
    # Optional fields with defaults - must come after required fields
    version: str = "1.0.0"  # Contract version
    source_instance: Optional[str] = None  # Specific instance ID
    timestamps: TimestampContract = field(default_factory=TimestampContract)  # Canonical timestamp contract
    correlation_context: CorrelationContract = field(default_factory=CorrelationContract)  # Correlation IDs
    tags: Dict[str, str] = field(default_factory=dict)  # Tags for filtering/grouping
    telemetry_version: TelemetryVersion = TelemetryVersion.V1_0_0  # Version info
    
    @classmethod
    def create(
        cls,
        source_component: str,
        runtime_id: str,
        correlation_context: Optional[CorrelationContract] = None,
        **tags
    ) -> "MetadataContract":
        """
        Create metadata contract with common defaults.
        
        Args:
            source_component: Name of the component generating telemetry
            runtime_id: Runtime instance identifier
            correlation_context: Correlation IDs (generated if not provided)
            **tags: Additional tags for filtering
            
        Returns:
            New MetadataContract instance
        """
        return cls(
            version="1.0.0",
            source_component=source_component,
            runtime_id=runtime_id,
            correlation_context=correlation_context or CorrelationContract(),
            timestamps=TimestampContract(timestamp_utc=time.time()),
            tags=dict(tags),
        )


# =============================================================================
# TELEMETRY EVENT CONTRACT
# =============================================================================

@dataclass(frozen=True)
class TelemetryEventContract:
    """
    Contract for telemetry event structure.
    
    This is the canonical format that all observability data must follow
    to ensure backend independence and consistent processing.
    """
    
    # Required fields (no defaults) - must come first
    event_type: str  # e.g., "log", "metric", "span", "diagnostic"
    timestamps: TimestampContract  # Canonical timestamp contract
    metadata: MetadataContract  # Canonical metadata contract
    payload: Dict[str, Any]  # Event-specific payload
    
    # Optional fields with defaults - must come after required fields
    version: str = "1.0.0"  # Contract version
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Event identifier
    severity: Optional[str] = None  # e.g., "debug", "info", "warning", "error"
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert to JSON-serializable dictionary.
        
        This is the canonical export format for all telemetry data.
        """
        return {
            "version": self.version,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamps": self.timestamps.to_dict(),
            "metadata": {
                "version": self.metadata.version,
                "source_component": self.metadata.source_component,
                "runtime_id": self.metadata.runtime_id,
                "correlation_context": {
                    "trace_id": self.metadata.correlation_context.trace_id,
                    "span_id": self.metadata.correlation_context.span_id,
                    "correlation_id": self.metadata.correlation_context.correlation_id,
                },
                "tags": dict(self.metadata.tags),
            },
            "payload": self.payload,
            "severity": self.severity,
        }


# =============================================================================
# TELEMETRY EXPORTER CONTRACT
# =============================================================================

@runtime_checkable
class TelemetryExporterContract(Protocol):
    """
    Contract for telemetry exporters.
    
    All exporter implementations must support these methods to ensure
    backend independence and replaceability.
    """
    
    @property
    def name(self) -> str:
        """Return exporter name."""
        ...
    
    @property
    def version(self) -> str:
        """Return exporter version."""
        ...
    
    async def export(self, events: List[TelemetryEventContract]) -> bool:
        """
        Export a batch of telemetry events.
        
        Args:
            events: List of telemetry events to export
            
        Returns:
            True if export succeeded, False otherwise
        """
        ...
    
    async def close(self) -> None:
        """Close the exporter and release resources."""
        ...
    
    @property
    def status(self) -> str:
        """Return current exporter status."""
        ...


# =============================================================================
# METRIC EXPORTER CONTRACT
# =============================================================================

@dataclass(frozen=True)
class MetricContract:
    """
    Contract for metric data structure.
    
    All metrics must follow this contract to ensure consistent processing
    across different backend systems.
    """
    
    # Required fields (no defaults) - must come first
    metric_name: str  # e.g., "http.requests.total", "cpu.usage"
    metric_type: str  # "counter", "gauge", "histogram", "summary"
    value: float  # Current/observed value
    
    # Optional fields with defaults - must come after required fields
    version: str = "1.0.0"  # Contract version
    labels: Dict[str, str] = field(default_factory=dict)  # Labels for dimensionality (prometheus-style)
    timestamp_utc: float = field(default_factory=time.time)  # Timestamp
    histogram_bucket: Optional[Dict[str, int]] = None  # For histograms
    histogram_sum: Optional[float] = None
    histogram_count: Optional[int] = None
    
    def to_prometheus_format(self) -> str:
        """
        Convert to Prometheus exposition format.
        
        Returns:
            String in Prometheus text format
        """
        label_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        base_name = self.metric_name.replace(".", "_")
        
        if self.histogram_bucket:
            # Histogram format
            lines = []
            for bucket, count in sorted(self.histogram_bucket.items()):
                lines.append(
                    f"{base_name}_bucket{{{label_str},le=\"{bucket}\"}} {count}"
                )
            if self.histogram_sum is not None and self.histogram_count is not None:
                lines.append(f"{base_name}_sum{{{label_str}}} {self.histogram_sum}")
                lines.append(f"{base_name}_count{{{label_str}}} {self.histogram_count}")
            return "\n".join(lines)
        else:
            # Simple metric format
            if self.labels:
                return f"{base_name}{{{label_str}}} {self.value}"
            return f"{base_name} {self.value}"


# =============================================================================
# TRACE EXPORTER CONTRACT
# =============================================================================

@dataclass(frozen=True)
class SpanContract:
    """
    Contract for span data in distributed traces.
    
    All tracing implementations must follow this contract to ensure
    interoperability between different tracing backends.
    """
    
    # Required fields (no defaults) - must come first
    trace_id: str  # Trace identifier
    span_id: str  # Span identifier
    name: str  # Operation name
    
    # Optional fields with defaults - must come after required fields
    version: str = "1.0.0"  # Contract version
    parent_span_id: Optional[str] = None  # Parent span identifier (optional)
    kind: str = "internal"  # "client", "server", "producer", "consumer", "internal"
    start_time_utc: float = field(default_factory=time.time)  # Start timestamp
    end_time_utc: Optional[float] = None  # End timestamp (optional)
    status_code: str = "unset"  # "ok", "error", "unset"
    status_message: Optional[str] = None  # Status message (optional)
    attributes: Dict[str, Any] = field(default_factory=dict)  # Span attributes
    events: List[Dict[str, Any]] = field(default_factory=list)  # Events within the span
    links: List[Dict[str, str]] = field(default_factory=list)  # Links to other spans
    
    @property
    def duration_seconds(self) -> float:
        """Calculate span duration in seconds."""
        if self.end_time_utc is None:
            return time.time() - self.start_time_utc
        return self.end_time_utc - self.start_time_utc
    
    def to_opentelemetry_json(self) -> Dict[str, Any]:
        """
        Convert to OpenTelemetry JSON format.
        
        Returns:
            Dictionary in OpenTelemetry span JSON format
        """
        result = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "kind": self.kind,
            "start_time": f"{int(self.start_time_utc * 1e9)}",
            "status": {"code": self.status_code},
        }
        
        if self.parent_span_id:
            result["parent_span_id"] = self.parent_span_id
        
        if self.end_time_utc:
            result["end_time"] = f"{int(self.end_time_utc * 1e9)}"
        
        if self.attributes:
            result["attributes"] = [
                {"key": k, "value": {"string_value": str(v)}}
                for k, v in self.attributes.items()
            ]
        
        if self.events:
            result["events"] = [
                {
                    "time_unix_nano": int(e.get("timestamp_utc", 0) * 1e9),
                    "name": e.get("name", ""),
                    "attributes": [
                        {"key": k, "value": {"string_value": str(v)}}
                        for k, v in e.get("attributes", {}).items()
                    ],
                }
                for e in self.events
            ]
        
        return result


# =============================================================================
# LOG EXPORTER CONTRACT
# =============================================================================

@dataclass(frozen=True)
class LogContract:
    """
    Contract for log record structure.
    
    All logging must follow this contract to ensure consistent processing
    across different log aggregation systems.
    """
    
    # Required fields (no defaults) - must come first
    timestamps: TimestampContract  # Canonical timestamp contract
    severity_text: str  # e.g., "DEBUG", "INFO", "WARNING", "ERROR"
    severity_number: int  # Numeric level for sorting
    
    # Optional fields with defaults - must come after required fields
    version: str = "1.0.0"  # Contract version
    resource: Dict[str, Any] = field(default_factory=dict)  # Resource attributes
    scope: Dict[str, Any] = field(default_factory=dict)     # Scope attributes
    body: Optional[str] = None  # Log body content
    body_type: str = "string"  # "string", "json", etc.
    attributes: Dict[str, Any] = field(default_factory=dict)  # Structured log data
    trace_id: Optional[str] = None  # Trace context
    span_id: Optional[str] = None   # Span context
    
    def to_structured_logging_json(self) -> Dict[str, Any]:
        """
        Convert to structured logging JSON format.
        
        Returns:
            Dictionary in structured logging format
        """
        return {
            "timestamp": self.timestamps.timestamp_iso,
            "severity": self.severity_text,
            "body": self.body,
            "attributes": self.attributes,
            "trace_context": {
                "trace_id": self.trace_id,
                "span_id": self.span_id,
            } if self.trace_id and self.span_id else {},
        }


# =============================================================================
# TELEMETRY POLICY CONTRACT
# =============================================================================

@dataclass(frozen=True)
class TelemetryPolicyContract:
    """
    Contract for telemetry policy configuration.
    
    Defines rules for sampling, retention, export, and other telemetry policies.
    """
    
    # Required fields (no defaults) - must come first
    name: str  # Human-readable policy name
    scope: str  # e.g., "runtime", "service:x", "component:y"
    
    # Optional fields with defaults - must come after required fields
    version: str = "1.0.0"  # Contract version
    policy_id: str = field(default_factory=lambda: f"policy_{uuid.uuid4().hex[:8]}")  # Policy identifier
    sample_rate: float = 1.0  # 0.0 - 1.0
    sampling_policy: str = "always"  # "always", "never", "probabilistic"
    retention_seconds: int = 3600  # Default 1 hour
    export_enabled: bool = True
    export_batch_size: int = 1000
    export_interval_seconds: float = 5.0  # Export interval in seconds
    min_severity: str = "TRACE"  # Minimum severity to collect
    
    def is_sampled(self, random_value: Optional[float] = None) -> bool:
        """
        Check if an event should be sampled according to this policy.
        
        Args:
            random_value: Random value between 0 and 1 (generated if not provided)
            
        Returns:
            True if the event should be included
        """
        import random
        
        if self.sampling_policy == "never":
            return False
        
        if self.sampling_policy == "always":
            return True
        
        # Probabilistic sampling
        rand = random_value if random_value is not None else random.random()
        return rand < self.sample_rate


# =============================================================================
# CONSUMER CONTRACT
# =============================================================================

@runtime_checkable
class TelemetryConsumerContract(Protocol):
    """
    Contract for telemetry consumers.
    
    Components that consume telemetry data must implement these methods
    to ensure consistent integration.
    """
    
    @property
    def name(self) -> str:
        """Return consumer name."""
        ...
    
    async def on_event(self, event: TelemetryEventContract) -> None:
        """
        Handle a single telemetry event.
        
        Args:
            event: The telemetry event to process
        """
        ...
    
    async def on_batch(self, events: List[TelemetryEventContract]) -> None:
        """
        Handle a batch of telemetry events.
        
        This is called for batch processing optimizations.
        
        Args:
            events: List of telemetry events to process
        """
        ...
    
    async def close(self) -> None:
        """Close the consumer and release resources."""
        ...


# =============================================================================
# OBSERVABILITY CONTEXT MANAGER CONTRACT
# =============================================================================

class TelemetryContextManagerContract(ABC):
    """
    Contract for telemetry context managers.
    
    Context managers that propagate telemetry state must follow this contract.
    """
    
    @abstractmethod
    def __enter__(self) -> "TelemetryContextManagerContract":
        """Enter the context and establish telemetry state."""
        ...
    
    @abstractmethod
    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any]
    ) -> bool:
        """
        Exit the context and restore previous telemetry state.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception instance if an exception was raised
            exc_tb: Traceback if an exception was raised
            
        Returns:
            True to suppress exception, False otherwise
        """
        ...
    
    @property
    @abstractmethod
    def correlation_context(self) -> CorrelationContract:
        """Get the correlation context for this context."""
        ...


# =============================================================================
# TELEMETRY MANAGER CONTRACT
# =============================================================================

@runtime_checkable
class TelemetryManagerInterface(Protocol):
    """
    Contract for telemetry manager implementations.
    
    This defines the public interface that all telemetry managers must support.
    """
    
    @property
    def runtime_id(self) -> str:
        """Return the runtime identifier."""
        ...
    
    @abstractmethod
    async def emit_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        **context
    ) -> TelemetryEventContract:
        """
        Emit a telemetry event.
        
        Args:
            event_type: Type of event (e.g., "log", "metric")
            payload: Event-specific data
            **context: Additional context (correlation IDs, etc.)
            
        Returns:
            The emitted event contract
        """
        ...
    
    @abstractmethod
    async def export_events(
        self,
        events: List[TelemetryEventContract]
    ) -> int:
        """
        Export a batch of events to registered exporters.
        
        Args:
            events: Events to export
            
        Returns:
            Number of successfully exported events
        """
        ...
    
    @abstractmethod
    async def add_exporter(self, exporter: TelemetryExporterContract) -> None:
        """Add an exporter to receive telemetry data."""
        ...
    
    @abstractmethod
    async def remove_exporter(self, exporter: TelemetryExporterContract) -> None:
        """Remove a registered exporter."""
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the manager and flush all pending data."""
        ...


__all__ = [
    # Versioning
    "TelemetryVersion",
    
    # Contracts
    "CorrelationContract",
    "TimestampContract",
    "MetadataContract",
    "TelemetryEventContract",
    
    # Exporter contracts
    "TelemetryExporterContract",
    "MetricContract",
    "SpanContract",
    "LogContract",
    
    # Policy and governance
    "TelemetryPolicyContract",
    "TelemetryConsumerContract",
    "TelemetryContextManagerContract",
    "TelemetryManagerInterface",
]