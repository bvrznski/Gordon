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
- Telemetry contracts (contracts.py) - canonical interfaces
- Error handling (errors.py) - exception hierarchy

Additional modules (Phase 3.8.11):
- Instrumentation framework (instrumentation.py) - hooks and execution tracking
- Analytics pipeline (analytics.py) - aggregation, KPIs, health scoring
- Reporting framework (reporting.py) - reports, dashboards, exports
- Profiling framework (profiling.py) - CPU/memory profiling, flame graphs
- Governance layer (governance.py) - policies, orchestration, lifecycle

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

# =============================================================================
# PHASE 3.8.11 NEW MODULES
# =============================================================================

# Contracts (canonical interfaces)
from .contracts import (
    TelemetryVersion,
    CorrelationContract,
    TimestampContract,
    MetadataContract,
    TelemetryEventContract,
    TelemetryExporterContract,
    MetricContract,
    SpanContract,
    LogContract,
    TelemetryPolicyContract,
    TelemetryConsumerContract,
    TelemetryContextManagerContract,
    TelemetryManagerInterface,
)

# Errors (exception hierarchy)
from .errors import (
    ObservabilityError,
    TelemetryError,
    MetricsError,
    TraceError,
    LoggingError,
    ExportError,
    AnalyticsError,
    GovernanceError,
    InstrumentationError,
    MetricsCollectionError,
    TraceCollectionError,
    LogPipelineError,
    ExportPipelineError,
    AnalyticsPipelineError,
    GovernanceViolationError,
    TelemetryOrchestrationError,
    SamplingError,
    CorrelationError,
    DashboardError,
    ProfilingError,
    error_to_dict,
    log_error_chain,
)

# Instrumentation framework
from .instrumentation import (
    HookType,
    HookDescriptor,
    InstrumentationHook,
    LifecycleHook,
    ExecutionHook,
    ResourceHook,
    PerfHook,
    HookRegistry,
    InstrumentationContext,
    InstrumentationManager,
)

# Analytics pipeline
from .analytics import (
    AggregationType,
    AggregationDefinition,
    KPICategory,
    KPIDefinition,
    AnomalyDetectionStrategy,
    AnomalyDetectionConfig,
    TrendData,
    TrendAnalysis,
    HealthScoreSource,
    HealthScoreComponent,
    HealthScoreReport,
    AnalyticsPipeline,
    AggregationPipeline,
    KPICalculationPipeline,
    HealthScoringPipeline,
)

# Reporting framework
from .reporting import (
    ReportType,
    ReportSchedule,
    ReportDefinition,
    ReportOutputFormat,
    ReportOutput,
    ReportGenerator,
    StructuredReportGenerator,
    ReportScheduler,
    DashboardType,
    DashboardDefinition,
    DashboardWidget,
    DashboardGenerator,
    ExportFormat,
    ExportConfig,
)

# Profiling framework
from .profiling import (
    ProfileType,
    ProfileDefinition,
    ProfileSession,
    FlameGraphNode,
    FlameGraph,
    ProfileCollector,
    CpuProfiler,
    MemoryProfiler,
    ProfilingSessionManager,
    BottleneckAnalysis,
    CapacityAnalysis,
    PerformanceBaseline,
    RegressionDetector,
    ProfiledBlock,
    PerformanceProfiler,
)

# Governance layer
from .governance import (
    PolicyScope,
    TelemetryPolicy,
    GovernanceRule,
    SamplingRule,
    RetentionRule,
    RuntimeObservabilityState,
    TelemetryOrchestrator,
    LifecycleEvent,
    ObservabilityLifecycleHooks,
    ObservabilityGovernanceEngine,
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
    
    # Contracts (Phase 3.8.11)
    "TelemetryVersion",
    "CorrelationContract",
    "TimestampContract",
    "MetadataContract",
    "TelemetryEventContract",
    "TelemetryExporterContract",
    "MetricContract",
    "SpanContract",
    "LogContract",
    "TelemetryPolicyContract",
    "TelemetryConsumerContract",
    "TelemetryContextManagerContract",
    "TelemetryManagerInterface",
    
    # Errors (Phase 3.8.11)
    "ObservabilityError",
    "TelemetryError",
    "MetricsError",
    "TraceError",
    "LoggingError",
    "ExportError",
    "AnalyticsError",
    "GovernanceError",
    "InstrumentationError",
    "MetricsCollectionError",
    "TraceCollectionError",
    "LogPipelineError",
    "ExportPipelineError",
    "AnalyticsPipelineError",
    "GovernanceViolationError",
    "TelemetryOrchestrationError",
    "SamplingError",
    "CorrelationError",
    "DashboardError",
    "ProfilingError",
    "error_to_dict",
    "log_error_chain",
    
    # Instrumentation (Phase 3.8.11)
    "HookType",
    "HookDescriptor",
    "InstrumentationHook",
    "LifecycleHook",
    "ExecutionHook",
    "ResourceHook",
    "PerfHook",
    "HookRegistry",
    "InstrumentationContext",
    "InstrumentationManager",
    
    # Analytics (Phase 3.8.11)
    "AggregationType",
    "AggregationDefinition",
    "KPICategory",
    "KPIDefinition",
    "AnomalyDetectionStrategy",
    "AnomalyDetectionConfig",
    "TrendData",
    "TrendAnalysis",
    "HealthScoreSource",
    "HealthScoreComponent",
    "HealthScoreReport",
    "AnalyticsPipeline",
    "AggregationPipeline",
    "KPICalculationPipeline",
    "HealthScoringPipeline",
    
    # Reporting (Phase 3.8.11)
    "ReportType",
    "ReportSchedule",
    "ReportDefinition",
    "ReportOutputFormat",
    "ReportOutput",
    "ReportGenerator",
    "StructuredReportGenerator",
    "ReportScheduler",
    "DashboardType",
    "DashboardDefinition",
    "DashboardWidget",
    "DashboardGenerator",
    "ExportFormat",
    "ExportConfig",
    
    # Profiling (Phase 3.8.11)
    "ProfileType",
    "ProfileDefinition",
    "ProfileSession",
    "FlameGraphNode",
    "FlameGraph",
    "ProfileCollector",
    "CpuProfiler",
    "MemoryProfiler",
    "ProfilingSessionManager",
    "BottleneckAnalysis",
    "CapacityAnalysis",
    "PerformanceBaseline",
    "RegressionDetector",
    "ProfiledBlock",
    "PerformanceProfiler",
    
    # Governance (Phase 3.8.11)
    "PolicyScope",
    "TelemetryPolicy",
    "GovernanceRule",
    "SamplingRule",
    "RetentionRule",
    "RuntimeObservabilityState",
    "TelemetryOrchestrator",
    "LifecycleEvent",
    "ObservabilityLifecycleHooks",
    "ObservabilityGovernanceEngine",
]