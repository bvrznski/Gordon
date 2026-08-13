# Stream Observability & Diagnostics Architecture - Phase 3.11.16
# ===============================================================

"""
Canonical Stream Observability and Diagnostics architecture for Gordon.

This module implements passive observability for semantic streams:
- Metrics: Counters, gauges, histograms for stream behavior
- Telemetry: Structured event collection and export
- Diagnostics: Read-only inspection of stream state
- Tracing: Deterministic record flow tracking
- Health: Stream health state reporting
- Logging: Structured log records
- Statistics: Aggregated metrics and trends
- Profiling: Performance measurement
- Event Inspection: Record-level visibility
- Runtime Snapshots: Immutable runtime state

CRITICAL PRINCIPLE:
Observability MUST NEVER influence execution.
Metrics observe but never schedule.
Diagnostics read but never modify.
Tracing tracks but never alters.
Health reports but never controls.

Architecture Layers:

    Stream Runtime (execution)
           │
           ▼
    ┌─────────────────────────────────────┐
    │   OBSERVABILITY LAYERS             │
    ├─────────────────────────────────────┤
    │ • Metrics - Counters, gauges,      │
    │   histograms for quantification    │
    │ • Telemetry - Structured events    │
    │ • Diagnostics - Read-only inspection│
    │ • Tracing - Deterministic flow     │
    │ • Health - State reporting         │
    │ • Logging - Structured records     │
    │ • Statistics - Aggregations        │
    │ • Profiling - Performance metrics  │
    │ • Event Inspection - Record view   │
    │ • Runtime Snapshots - Immutable    │
    └─────────────────────────────────────┘
           │
           ▼
    Stream Storage (data)

All components are passive observers. They never alter stream behavior.
"""

# =============================================================================
# CORE OBSERVABILITY TYPES
# =============================================================================

from .metrics import (
    StreamMetricType,
    StreamCounter,
    StreamGauge,
    StreamHistogram,
    StreamTimer,
    StreamMetricsSnapshot,
    create_stream_metric_point,
)

from .telemetry import (
    StreamTelemetryEvent,
    StreamTelemetryEnvelope,
    TelemetryRecord,
    TelemetryExportBatch,
)

from .diagnostics import (
    DiagnosticSeverity,
    DiagnosticFinding,
    DiagnosticReport,
    StreamDiagnostics,
    HealthDiagnostic,
)

from .tracing import (
    TracedRecord,
    TraceSpan,
    TraceContext,
    DeterministicTraceManager,
    RecordFlowTrace,
)

from .health import (
    StreamHealthStatus,
    StreamHealthState,
    StreamHealthReport,
    StreamHealthSnapshot,
)

from .logging import (
    StreamLogRecord,
    StreamLogger,
    LogSeverity,
    StructuredLogEntry,
)

from .statistics import (
    AggregationType,
    MetricAggregator,
    StatisticsSnapshot,
    TrendAnalysis,
)

from .profiling import (
    ProfileMeasurement,
    ProfilingResult,
    CPUProfile,
    MemoryProfile,
)

from .event_inspection import (
    RecordInspectionContext,
    InspectionResult,
    RecordInspector,
    StreamEventInspector,
)

from .runtime_snapshots import (
    RuntimeStreamSnapshot,
    SubscriberSnapshot,
    CursorSnapshot,
    CheckpointSnapshot,
    FullRuntimeSnapshot,
)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Metrics - quantifiable stream behavior
    "StreamMetricType",
    "StreamCounter",
    "StreamGauge",
    "StreamHistogram",
    "StreamTimer",
    "StreamMetricsSnapshot",
    "create_stream_metric_point",
    
    # Telemetry - structured events
    "StreamTelemetryEvent",
    "StreamTelemetryEnvelope",
    "TelemetryRecord",
    "TelemetryExportBatch",
    
    # Diagnostics - read-only inspection
    "DiagnosticSeverity",
    "DiagnosticFinding",
    "DiagnosticReport",
    "StreamDiagnostics",
    "HealthDiagnostic",
    
    # Tracing - deterministic flow tracking
    "TracedRecord",
    "TraceSpan",
    "TraceContext",
    "DeterministicTraceManager",
    "RecordFlowTrace",
    
    # Health - state reporting
    "StreamHealthStatus",
    "StreamHealthState",
    "StreamHealthReport",
    "StreamHealthSnapshot",
    
    # Logging - structured records
    "StreamLogRecord",
    "StreamLogger",
    "LogSeverity",
    "StructuredLogEntry",
    
    # Statistics - aggregations and trends
    "AggregationType",
    "MetricAggregator",
    "StatisticsSnapshot",
    "TrendAnalysis",
    
    # Profiling - performance measurement
    "ProfileMeasurement",
    "ProfilingResult",
    "CPUProfile",
    "MemoryProfile",
    
    # Event Inspection - record-level visibility
    "RecordInspectionContext",
    "InspectionResult",
    "RecordInspector",
    "StreamEventInspector",
    
    # Runtime Snapshots - immutable state capture
    "RuntimeStreamSnapshot",
    "SubscriberSnapshot",
    "CursorSnapshot",
    "CheckpointSnapshot",
    "FullRuntimeSnapshot",
]