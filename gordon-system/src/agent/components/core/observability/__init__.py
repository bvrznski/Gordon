# Core Observability Package
# ==========================

"""
Core observability infrastructure for Gordon agent.

This package provides:
- Structured runtime event model
- Correlation and tracing context
- Event sinks with bounded buffers
- Redaction support for sensitive data
"""

from .events import (
    RuntimeEvent,
    EventSeverity,
    EventCategory,
    create_event,
    create_lifecycle_event,
    create_error_event,
    create_warning_event,
    create_critical_event,
)

from .correlation import (
    TraceContext,
    SpanStatus,
    SpanRecord,
    SpanEvent,
    Span,
    Tracer,
)

from .sinks import (
    SinkStatus,
    EvictionPolicy,
    BoundedBufferConfig,
    EventSink,
    NoOpSink,
    InMemorySink,
    RedactingSink,
    FanOutSink,
)

__all__ = [
    # Events
    "RuntimeEvent",
    "EventSeverity",
    "EventCategory",
    "create_event",
    "create_lifecycle_event",
    "create_error_event",
    "create_warning_event",
    "create_critical_event",
    
    # Correlation and tracing
    "TraceContext",
    "SpanStatus",
    "SpanRecord",
    "SpanEvent",
    "Span",
    "Tracer",
    
    # Sinks
    "SinkStatus",
    "EvictionPolicy",
    "BoundedBufferConfig",
    "EventSink",
    "NoOpSink",
    "InMemorySink",
    "RedactingSink",
    "FanOutSink",
]