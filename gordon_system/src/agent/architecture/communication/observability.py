# Gordon Core - Communication Observability & Diagnostics (Phase 3.21.13)
# ========================================================================
#
# Canonical observability for message tracing, metrics, and diagnostics
#
# Every communication event is traced and measured to provide comprehensive
# visibility into system behavior.

"""
Canonical Communication Observability for Gordon Phase 3.21.13

OBSERVABILITY TYPES:
--------------------
1. Tracing: Distributed tracing of messages across the system
2. Metrics: Quantitative measurements (latency, throughput, errors)
3. Diagnostics: Qualitative analysis of communication issues
4. Health: Endpoint and system health status

TRACE HIERARCHY:
----------------
- TraceId: Unique identifier for an entire trace
- SpanId: Individual operations within a trace
- Links: References between spans
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum, auto
import time
import uuid


# =============================================================================
# TRACE IDENTIFIERS
# =============================================================================

@dataclass(frozen=True)
class TraceId:
    """
    Unique identifier for a trace.
    
    Invariants:
        - TRC-ID-001: Every trace has exactly one unique identity
        - TRC-ID-002: All spans in same trace share the same trace ID
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "TraceId":
        """Generate a new unique trace ID."""
        return cls(value=f"trace_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SpanId:
    """
    Unique identifier for a span within a trace.
    
    Invariants:
        - SPN-ID-001: Every span has exactly one unique identity
        - SPN-ID-002: Spans are linked via parent-child relationships
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "SpanId":
        """Generate a new unique span ID."""
        return cls(value=f"span_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# SPAN STATUS
# =============================================================================

class SpanStatus(Enum):
    """
    Canonical span status values.
    """
    
    UNSET = "unset"           # Status not yet determined
    OK = "ok"                 # Operation completed successfully
    ERROR = "error"           # Operation encountered an error


# =============================================================================
# MESSAGE SPAN
# =============================================================================

@dataclass(frozen=True, slots=True)
class MessageSpan:
    """
    Immutable span representing a single message operation.
    
    Args:
        trace_id: The trace this span belongs to
        span_id: Unique identifier for this span
        parent_span_id: Parent span (if any)
        
        # Operation details
        name: Human-readable name of the operation
        kind: Span type (producer, consumer, internal)
        status: Current status
        
        # Timing
        start_timestamp_utc: When the operation started
        end_timestamp_utc: When the operation completed (optional)
        
        # Context
        source_endpoint_id: Endpoint that initiated this span
        target_endpoint_id: Endpoint being communicated with
        message_type: Type of message being sent/received
        
        # Attributes
        attributes: Additional key-value attributes
    """
    
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    
    name: str = "unknown"
    kind: str = "internal"  # producer, consumer, internal
    status: SpanStatus = SpanStatus.UNSET
    
    start_timestamp_utc: float = field(default_factory=time.time)
    end_timestamp_utc: Optional[float] = None
    
    source_endpoint_id: str = ""
    target_endpoint_id: str = ""
    message_type: str = "unknown"
    
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if self.end_timestamp_utc is None:
            return 0.0
        return (self.end_timestamp_utc - self.start_timestamp_utc) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "kind": self.kind,
            "status": self.status.value,
            "start_timestamp_utc": self.start_timestamp_utc,
            "end_timestamp_utc": self.end_timestamp_utc,
            "duration_ms": self.duration_ms,
            "source_endpoint_id": self.source_endpoint_id,
            "target_endpoint_id": self.target_endpoint_id,
            "message_type": self.message_type,
            "attributes": dict(self.attributes),
        }


# =============================================================================
# MESSAGE TRACE
# =============================================================================

@dataclass(slots=True)
class MessageTrace:
    """
    Mutable trace container for message operations.
    
    Collects spans belonging to a single logical operation.
    """
    
    _trace_id: str = field(default_factory=lambda: TraceId.generate().value)
    _spans: Dict[str, MessageSpan] = field(default_factory=dict)
    
    def create_span(
        self,
        name: str,
        kind: str = "internal",
        parent_span_id: Optional[str] = None,
    ) -> MessageSpan:
        """Create a new span in this trace."""
        span_id = SpanId.generate().value
        span = MessageSpan(
            trace_id=self._trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            name=name,
            kind=kind,
            start_timestamp_utc=time.time(),
        )
        self._spans[span_id] = span
        return span
    
    def complete_span(self, span_id: str) -> None:
        """Mark a span as completed."""
        if span_id in self._spans:
            self._spans[span_id].end_timestamp_utc = time.time()
    
    def get_spans(self) -> Tuple[MessageSpan, ...]:
        """Get all spans in this trace."""
        return tuple(self._spans.values())
    
    def get_root_span(self) -> Optional[MessageSpan]:
        """Get the root span (no parent)."""
        for span in self._spans.values():
            if span.parent_span_id is None:
                return span
        # If no explicit root, return first span
        if self._spans:
            return tuple(self._spans.values())[0]
        return None


# =============================================================================
# DELIVERY METRICS
# =============================================================================

@dataclass(frozen=True)
class DeliveryMetric:
    """
    Immutable delivery metrics record.
    
    Args:
        timestamp_utc: When this metric was recorded
        message_type: Type of message
        source_endpoint_id: Originating endpoint
        target_endpoint_id: Target endpoint
        
        # Timing
        send_latency_ms: Time to send message (ms)
        delivery_latency_ms: Total time to deliver (ms)
        
        # Status
        status: Delivery status (delivered, failed, expired)
        attempts: Number of delivery attempts
    """
    
    timestamp_utc: float = field(default_factory=time.time)
    message_type: str = ""
    source_endpoint_id: str = ""
    target_endpoint_id: str = ""
    
    send_latency_ms: float = 0.0
    delivery_latency_ms: float = 0.0
    
    status: str = "delivered"  # delivered, failed, expired, dropped
    attempts: int = 1


# =============================================================================
# ENDPOINT HEALTH
# =============================================================================

class EndpointHealthStatus(Enum):
    """
    Canonical endpoint health statuses.
    """
    
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"     # Working but with issues
    UNHEALTHY = "unhealthy"   # Not working properly


@dataclass(frozen=True, slots=True)
class EndpointHealth:
    """
    Immutable health record for an endpoint.
    
    Args:
        endpoint_id: The endpoint being measured
        timestamp_utc: When this measurement was taken
        
        # Health indicators
        status: Overall health status
        last_activity_utc: When endpoint was last active
        messages_processed_count: Total messages processed
        error_rate: Error rate (0.0 to 1.0)
        
        # Performance
        avg_latency_ms: Average message processing latency
        queue_depth: Current number of queued messages
        
        # Diagnostics
        diagnostic_messages: List of diagnostic messages
    """
    
    endpoint_id: str
    timestamp_utc: float = field(default_factory=time.time)
    
    status: EndpointHealthStatus = EndpointHealthStatus.UNKNOWN
    last_activity_utc: Optional[float] = None
    messages_processed_count: int = 0
    error_rate: float = 0.0
    
    avg_latency_ms: float = 0.0
    queue_depth: int = 0
    
    diagnostic_messages: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# DIAGNOSTIC EVENT
# =============================================================================

class DiagnosticEventType(Enum):
    """
    Canonical diagnostic event types.
    """
    
    # Lifecycle events
    ENDPOINT_REGISTERED = "endpoint_registered"
    ENDPOINT_UNREGISTERED = "endpoint_unregistered"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_EXPIRED = "message_expired"
    
    # Error events
    MESSAGE_FAILED = "message_failed"
    AUTHORIZATION_DENIED = "authorization_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DELIVERY_TIMEOUT = "delivery_timeout"
    
    # State change events
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_DELETED = "subscription_deleted"
    ROUTE_CHANGED = "route_changed"


@dataclass(frozen=True, slots=True)
class DiagnosticEvent:
    """
    Immutable diagnostic event record.
    
    Args:
        event_type: Type of event that occurred
        timestamp_utc: When it occurred
        
        # Context
        endpoint_id: Endpoint where event occurred
        message_id: Related message (if any)
        
        # Details
        severity: Event severity level
        description: Human-readable description
        metadata: Additional event-specific data
    """
    
    event_type: DiagnosticEventType
    timestamp_utc: float = field(default_factory=time.time)
    
    endpoint_id: str = ""
    message_id: Optional[str] = None
    
    severity: str = "info"  # debug, info, warn, error, critical
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# OBSERVABILITY STATE
# =============================================================================

@dataclass(slots=True)
class ObservabilityState:
    """
    Mutable state for observability data collection.
    
    Collects and aggregates metrics for reporting and analysis.
    """
    
    _spans: Dict[str, MessageSpan] = field(default_factory=dict)
    _traces: Dict[str, Tuple[MessageSpan, ...]] = field(default_factory=dict)
    _metrics: list = field(default_factory=list)
    _health_records: Dict[str, EndpointHealth] = field(default_factory=dict)
    
    def record_span(self, span: MessageSpan) -> None:
        """Record a message span."""
        self._spans[span.span_id] = span
        
        # Group by trace
        if span.trace_id not in self._traces:
            self._traces[span.trace_id] = []
        self._traces[span.trace_id].append(span)
    
    def record_metric(self, metric: DeliveryMetric) -> None:
        """Record a delivery metric."""
        self._metrics.append(metric)
    
    def update_health(self, health: EndpointHealth) -> None:
        """Update endpoint health record."""
        self._health_records[health.endpoint_id] = health
    
    def get_trace(self, trace_id: str) -> Optional[Tuple[MessageSpan, ...]]:
        """Get all spans for a trace."""
        return self._traces.get(trace_id)
    
    def get_all_metrics(self) -> Tuple[DeliveryMetric, ...]:
        """Get all recorded metrics."""
        return tuple(self._metrics)


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Trace identifiers
    "TraceId",
    "SpanId",
    
    # Span types
    "SpanStatus",
    "MessageSpan",
    "MessageTrace",
    
    # Metrics
    "DeliveryMetric",
    
    # Health
    "EndpointHealthStatus",
    "EndpointHealth",
    
    # Diagnostics
    "DiagnosticEventType",
    "DiagnosticEvent",
    
    # State collection
    "ObservabilityState",
]