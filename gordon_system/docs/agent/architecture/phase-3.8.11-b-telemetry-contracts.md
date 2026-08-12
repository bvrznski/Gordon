# GORDON OBSERVABILITY, TELEMETRY & ANALYTICS INFRASTRUCTURE
## PHASE 3.8.11 - TELEMETRY CONTRACTS SPECIFICATION

**Version:** 3.8.11  
**Date:** 2026-08-06  
**Author:** Cline AI Assistant  
**Status:** DRAFT  

---

## 1. OVERVIEW

This document specifies the canonical telemetry contracts for Phase 3.8.11 (Observability, Telemetry & Analytics Infrastructure). These contracts define the interface between all observability subsystems and ensure deterministic, backend-independent telemetry collection.

### Contract Principles

| Principle | Description |
|-----------|-------------|
| **Deterministic** | Same inputs always produce same outputs |
| **Immutable** | Once created, data structures cannot be modified |
| **Backend-Independent** | Contracts do not depend on specific export backends |
| **Versioned** | All contracts include version information |
| **Extensible** | New fields can be added without breaking compatibility |

---

## 2. CORE TELEMETRY CONTRACTS

### 2.1 Log Record Contract

```python
@dataclass(frozen=True)
class LogRecord:
    """
    Immutable structured log record.
    
    All observability data flows through canonical contracts.
    """
    
    # Core fields (always present)
    level: LogLevel                        # Severity level
    message: str                          # Human-readable message
    
    # Context and metadata
    context: LogContext                   # Runtime context
    metadata: LogMetadata                 # Log generation metadata
    
    # Payload with domain-specific data (bounded for safety)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Redaction tracking
    redacted_fields: Set[str] = field(default_factory=set)
    is_redacted: bool = False
```

**Contract Requirements:**
- ✅ All observability must produce LogRecord instances
- ✅ Context must include correlation_id for traceability
- ✅ Metadata must include source_module and timestamp

### 2.2 Metric Record Contract

```python
@dataclass(frozen=True)
class MetricPoint:
    """
    Single metric observation with optional labels.
    
    All metrics must conform to this contract.
    """
    
    name: str                           # Metric name (use dots for hierarchy)
    value: float                        # Observed value
    
    timestamp_utc: float = field(default_factory=time.time)
    
    # Labels for multi-dimensional metrics
    labels: Dict[str, str] = field(default_factory=dict)
    
    metric_type: MetricType = MetricType.GAUGE  # Counter, Gauge, Histogram, Timer
```

**Contract Requirements:**
- ✅ All metrics must use MetricPoint instances
- ✅ Metric types must be specified in the contract

### 2.3 Telemetry Event Contract

```python
@dataclass(frozen=True)
class TelemetryEvent:
    """
    Immutable telemetry event for machine-oriented metrics.
    
    Telemetry events are distinct from logs - optimized for programmatic consumption.
    """
    
    # Event identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""  # e.g., "metric", "log", "trace"
    
    # Timestamps
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Context (same as logs for correlation)
    runtime_id: str = ""
    correlation_id: Optional[str] = None
    
    # Tracing identifiers
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # Event content
    name: str = ""  # Metric/event name
    value: Optional[float] = None
    values: Dict[str, float] = field(default_factory=dict)
    
    # Tags for filtering and grouping
    tags: Dict[str, str] = field(default_factory=dict)
    
    unit: Optional[str] = None  # e.g., "milliseconds", "bytes", "count"
```

**Contract Requirements:**
- ✅ All telemetry data must use TelemetryEvent instances
- ✅ Events must include correlation_id for traceability

### 2.4 Span Record Contract

```python
@dataclass(frozen=True)
class SpanRecord:
    """
    Immutable record of a single span.
    
    Spans are the atomic unit of distributed tracing.
    """
    
    span_id: str
    trace_id: str
    name: str
    
    status: "SpanStatus" = field(default="running")
    
    start_time: float = field(default_factory=time.monotonic)
    end_time: Optional[float] = None
    
    parent_span_id: Optional[str] = None
    child_span_ids: List[str] = field(default_factory=list)
    
    attributes: Dict[str, str] = field(default_factory=dict)
    events: List["SpanEvent"] = field(default_factory=list)
    
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
```

**Contract Requirements:**
- ✅ All tracing must produce SpanRecord instances
- ✅ Spans must have valid trace_id and span_id

---

## 3. EXPORTER CONTRACTS

### 3.1 Telemetry Exporter Interface

```python
class TelemetryExporter(ABC):
    """
    Interface for telemetry exporters.
    
    Exporters transport telemetry data to external systems.
    """
    
    @abstractmethod
    async def export(self, batch: ExportBatch) -> bool:
        """Export a batch of telemetry data."""
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the exporter and release resources."""
        ...
    
    @property
    @abstractmethod
    def status(self) -> ExporterStatus:
        """Return current exporter status."""
        ...
```

**Contract Requirements:**
- ✅ All exporters must implement this interface
- ✅ Export must be async for non-blocking behavior

### 3.2 Log Sink Interface

```python
class LogSink(ABC):
    """
    Interface for log sinks.
    
    Sinks receive formatted logs and deliver them to their destination.
    """
    
    @abstractmethod
    def emit(self, record: LogRecord) -> bool:
        """Emit a log record to this sink."""
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the sink and release resources."""
        ...
    
    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """Check if sink is closed."""
        ...
```

**Contract Requirements:**
- ✅ All log sinks must implement this interface
- ✅ Emit must be thread-safe

---

## 4. HEALTH STATUS CONTRACTS

### 4.1 Canonical Health States

```python
class HealthStatus(Enum):
    """
    Canonical health states for runtime entities.
    
    State ordering and transitions are observable through telemetry contracts.
    """
    
    UNKNOWN = "unknown"
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BUSY = "busy"
    RECOVERING = "recovering"
    FAILED = "failed"
    OFFLINE = "offline"
```

**Contract Requirements:**
- ✅ All health reporting must use these canonical states
- ✅ Health transitions must be recorded via LogRecord

---

## 5. CORRELATION CONTRACTS

### 5.1 Correlation Context Contract

```python
@dataclass(frozen=True)
class CorrelationContext:
    """
    Runtime correlation context for a single operation.
    
    Used to propagate correlation state across subsystem boundaries.
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
```

**Contract Requirements:**
- ✅ All observability data must include correlation context
- ✅ Correlation IDs must propagate across subsystem boundaries

---

## 6. FAILURE CONTRACTS

### 6.1 Telemetry Error Hierarchy

```python
class TelemetryError(RuntimeError):
    """Base exception for telemetry errors."""
    pass

class MetricsError(TelemetryError):
    """Exception during metric collection."""
    pass

class TraceError(TelemetryError):
    """Exception during tracing operations."""
    pass

class LoggingError(TelemetryError):
    """Exception during logging operations."""
    pass

class ExportError(TelemetryError):
    """Exception during export operations."""
    pass
```

**Contract Requirements:**
- ✅ All telemetry exceptions must inherit from TelemetryError
- ✅ Errors must include context for debugging

---

## 7. OBSERVABILITY CONTRACTS SUMMARY

| Contract | Purpose | Status |
|----------|---------|--------|
| LogRecord | Structured log entries | ✅ Canonical |
| MetricPoint | Single metric observation | ✅ Canonical |
| TelemetryEvent | Machine-oriented telemetry data | ✅ Canonical |
| SpanRecord | Distributed tracing spans | ✅ Canonical |
| ExportBatch | Batch data for export | ✅ Canonical |
| CorrelationContext | Runtime correlation state | ✅ Canonical |
| HealthStatus | Health states (canonical) | ✅ Canonical |

---

## 8. IMPLEMENTATION REQUIREMENTS

### 8.1 All Observability Code Must:

- Use canonical contracts for all data exchange
- Produce immutable data structures
- Include full context in every observation
- Propagate correlation IDs across boundaries

### 8.2 No Direct Telemetry Bypass

```
❌ WRONG: Subsystem emits directly to external backend
✅ RIGHT: Subsystem produces LogRecord/MetricPoint/TelemetryEvent → Manager → Exporter
```

### 8.3 Backend Independence

```
The observability contracts must NOT depend on:
- Prometheus client libraries
- OpenTelemetry SDKs
- Specific database drivers
- Cloud provider SDKs
```

---

## 9. CONFORMANCE TESTING

All implementations must pass conformance tests:

1. **Contract Validation Tests** - Verify data structures match contracts
2. **Integration Tests** - Verify end-to-end telemetry flow
3. **Backend Independence Tests** - Verify no backend dependencies in contracts

---

*Specification generated by Cline AI Assistant*
*Phase 3.8.11 - Telemetry Contracts*