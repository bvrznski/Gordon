# Core Observability Package
# ==========================

"""
Core observability infrastructure for Gordon agent.

This package provides:
- Structured runtime event model (events.py)
- Correlation and tracing context (correlation.py, correlation_manager.py)
- Event sinks with bounded buffers (sinks.py, logging_manager.py)
- Redaction support for sensitive data
- Structured logging (logging_manager.py)
- Metrics collection (metrics_manager.py)
- Telemetry collection and export (telemetry_manager.py)
- Diagnostics generation (diagnostics_manager.py)
- Observability orchestration (observability_manager.py)

All observability is OBSERVATIONAL - it never changes runtime behavior.
"""

# ==============================================================================
# EXISTING LEGACY EXPORTS (MAINTAINED FOR BACKWARD COMPATIBILITY)
# ==============================================================================

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
    SpanStatus as LegacySpanStatus,
    SpanRecord as LegacySpanRecord,
    SpanEvent as LegacySpanEvent,
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

# ==============================================================================
# NEW PRODUCTION ARCHITECTURE EXPORTS
# ==============================================================================

# Models - Immutable data structures
from .models import (
    # Logging models
    LogLevel,
    LogContext,
    LogMetadata,
    LogRecord,
    create_log,
    create_debug_log,
    create_info_log,
    create_notice_log,
    create_warning_log,
    create_error_log,
    create_critical_log,
    
    # Telemetry models
    TelemetryEvent,
    TelemetryEnvelope,
    
    # Tracing identifiers
    TraceId,
    SpanId,
    
    # Metric models
    MetricType,
    MetricPoint,
    MetricSnapshot,
    
    # Correlation models
    CorrelationContext,
    CorrelationSnapshot,
    
    # Health models (canonical)
    HealthStatus,
    HealthReport,
    
    # Export models
    ExportBatch,
)

# Logging manager - structured logging infrastructure (canonical authority)
from .logging_manager import (
    SamplingPolicy,
    SamplingConfig,
    LogSink,
    LogFormatter,
    PlainTextFormatter,
    JsonFormatter,
    LoggingManager,
    ConsoleSink,
    MemorySink,
    FakeSink,
)

# Correlation manager - runtime correlation state management (canonical authority)
from .correlation_manager import (
    CorrelationScope,
    CorrelationState,
    CorrelationManager,
)

# Metrics manager - metric collection and aggregation (canonical authority)
from .metrics_manager import (
    MetricConfig,
    Metric,
    Counter,
    Gauge,
    Histogram,
    Timer,
    MetricsManager,
)

# Telemetry manager - telemetry event collection and export (canonical authority)
from .telemetry_manager import (
    ExporterStatus,
    TelemetryExporter,
    TelemetryManager,
    FakeExporter,
    NoOpExporter,
)

# Diagnostics manager - diagnostic findings and reports (canonical authority)
from .diagnostics_manager import (
    DiagnosticSeverity,
    DiagnosticFinding,
    DiagnosticReport,
    DiagnosticsManager,
    ResourceDiagnostics,
    SystemDiagnostics,
)

# Tracing manager - distributed tracing with span hierarchy (canonical authority)
# Exactly one TraceManager per runtime
from .tracing import (
    SpanRecord,      # Canonical span record (immutable)
    SpanStatus,
    SpanEvent,
    TraceSnapshot,
    SpanContextManager,
    TraceManager,    # Canonical trace manager - exactly one per runtime
)

# Observability manager - unified orchestration of all observability subsystems
from .observability_manager import (
    ObservabilityConfig,
    ObservabilityManager,
    RuntimeObservability,
)

__all__ = [
    # LEGACY exports (backward compatibility)
    "RuntimeEvent",
    "EventSeverity",
    "EventCategory",
    "create_event",
    "create_lifecycle_event",
    "create_error_event",
    "create_warning_event",
    "create_critical_event",
    
    "TraceContext",      # Legacy context
    "LegacySpanStatus",  # Legacy span status
    "LegacySpanRecord",  # Legacy span record
    "LegacySpanEvent",   # Legacy span event
    "Span",              # Legacy span
    "Tracer",            # Legacy tracer
    
    "SinkStatus",
    "EvictionPolicy",
    "BoundedBufferConfig",
    "EventSink",
    "NoOpSink",
    "InMemorySink",
    "RedactingSink",
    "FanOutSink",
    
    # NEW PRODUCTION ARCHITECTURE
    
    # Models
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
    
    "TelemetryEvent",
    "TelemetryEnvelope",
    
    "TraceId",
    "SpanId",
    
    "MetricType",
    "MetricPoint",
    "MetricSnapshot",
    
    "CorrelationContext",
    "CorrelationSnapshot",
    
    # Health models (canonical)
    "HealthStatus",
    "HealthReport",
    
    "ExportBatch",
    
    # Logging (canonical authority)
    "SamplingPolicy",
    "SamplingConfig",
    "LogSink",
    "LogFormatter",
    "PlainTextFormatter",
    "JsonFormatter",
    "LoggingManager",   # Canonical logging manager - exactly one per runtime
    
    # Correlation (canonical authority)
    "CorrelationScope",
    "CorrelationState",
    "CorrelationManager",  # Canonical correlation manager - exactly one per runtime
    
    # Metrics (canonical authority)
    "MetricConfig",
    "Metric",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "MetricsManager",   # Canonical metrics manager - exactly one per runtime
    
    # Telemetry (canonical authority)
    "ExporterStatus",
    "TelemetryExporter",
    "TelemetryManager",  # Canonical telemetry manager - exactly one per runtime
    "FakeExporter",
    "NoOpExporter",
    
    # Diagnostics (canonical authority)
    "DiagnosticSeverity",
    "DiagnosticFinding",
    "DiagnosticReport",
    "DiagnosticsManager",  # Canonical diagnostics manager - exactly one per runtime
    "ResourceDiagnostics",
    "SystemDiagnostics",
    
    # Tracing (canonical authority)
    "SpanRecord",
    "SpanStatus",
    "SpanEvent",
    "TraceSnapshot",
    "SpanContextManager",
    "TraceManager",   # Canonical trace manager - exactly one per runtime
    
    # Orchestration
    "ObservabilityConfig",
    "ObservabilityManager",  # Canonical observability orchestrator - exactly one per runtime
    "RuntimeObservability",
]