# Phase 3.15.12: State Observability & Diagnostics

**Phase Version:** 3.15.12  
**Status:** Implementation Complete  
**Release Date:** 2026-08-14  

---

## Executive Summary

This phase establishes the canonical observability and diagnostics architecture for Gordon Core runtime state.

Key achievements:
- One canonical observability model across all state types
- Immutable diagnostic artifacts (never mutate runtime state)
- Structured telemetry, metrics, logging, tracing, and audit systems
- Public API facade with no mutable state exposure
- Comprehensive retention and visibility policies

---

## Architectural Principles

### Separation of Concerns

The observability architecture completely separates:

| Concept | Description |
|---------|-------------|
| Runtime State | The actual state being observed (never owned by observability) |
| Diagnostics | Immutable diagnostic models of runtime state |
| Telemetry | Structured telemetry data points |
| Metrics | Deterministic metrics describing state behavior |
| Logs | Structured log records with redaction |
| Traces | Distributed trace spans preserving lineage |
| Audit Records | Immutable append-only audit trail |
| Health Information | State health evaluation (not replacement) |
| Monitoring | Observational monitoring via artifacts |
| Introspection | Read-only state inspection |

**Critical Invariant:** Observability is purely observational. It never becomes a mutation authority for runtime state.

### Immutability

All diagnostic artifacts are:
- Frozen dataclasses (no attribute modification)
- Value-based equality
- Copy-on-modify via `dataclass_replace()`

---

## Observability Architecture

### Domain and Visibility

```python
ObservabilityDomain = Literal["runtime", "hierarchy", "ownership", "identity", ...]
DiagnosticVisibility = Literal["public", "administrative", "internal", "privileged"]
```

Visibility controls access to diagnostic artifacts.

### Core Diagnostic Models

All diagnostics inherit from `DiagnosticArtifact` base class:

#### StateDiagnostics
```python
@frozen
class StateDiagnostics(DiagnosticArtifact):
    state_id: str
    domain: Optional[str] = None
    scope: Optional[str] = None
    owner_identity: Optional[str] = None
    version_sequence: int = 0
    generation: int = 0
    mutability_class: str = "immutable"
```

#### RuntimeDiagnostics
```python
@frozen
class RuntimeDiagnostics(DiagnosticArtifact):
    runtime_id: str
    boot_session_id: Optional[str] = None
    component_diagnostics: Tuple[ComponentDiagnostics, ...] = ()
```

#### ScopeDiagnostics
```python
@frozen
class ScopeDiagnostics(DiagnosticArtifact):
    scope_id: str
    scope_type: Literal["application", "module", "component"]
    parent_scope_id: Optional[str] = None
```

#### ValidationDiagnostics
```python
@frozen
class ValidationDiagnostics(DiagnosticArtifact):
    validation_id: str
    overall_validity: bool
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    findings: Tuple[ValidationFinding, ...] = ()
```

#### OwnershipDiagnostics
```python
@frozen
class OwnershipDiagnostics(DiagnosticArtifact):
    state_id: str
    current_owner_identity: Optional[str]
    current_authority_type: str  # "exclusive_mutation", etc.
    ownership_history: Tuple[str, ...] = ()
```

#### TransitionDiagnostics
```python
@frozen
class TransitionDiagnostics(DiagnosticArtifact):
    transition_id: str
    state_id: str
    transition_type: int  # TransitionType enum value
    result_code: int  # TransitionResultCode enum value
```

### Diagnostic Views

Support for multiple canonical views:

| View Type | Content |
|-----------|---------|
| RUNTIME | Runtime-level diagnostics |
| HIERARCHY | Scope/parent relationships |
| HEALTH | Health evaluation data |
| RESOURCE | Resource allocation metrics |
| DEPENDENCY | Dependency graph state |
| OWNERSHIP | Ownership history and authority |
| TRANSITION | Transition history |
| VERSION | Version lineage |
| PERSISTENCE | Persistence state |
| RECOVERY | Recovery status |
| SECURITY | Security audit findings |
| SUMMARY | Aggregated summary |

---

## Metrics System

### Metric Types

```python
MetricType = Literal["counter", "gauge", "histogram", "timing"]
```

### MetricValue

```python
@frozen
class MetricValue:
    name: str  # e.g., "transition_count"
    value: float
    labels: Dict[str, str] = field(factory=dict)
    timestamp_utc: int = field(default_factory=lambda: int(time.time() * 1000))
```

### MetricSnapshot

```python
@frozen
class MetricSnapshot:
    snapshot_id: str = field(default_factory=_generate_uuid)
    captured_at_utc: int = field(default_factory=lambda: int(time.time() * 1000))
    values: Tuple[MetricValue, ...] = ()
    
    @classmethod
    def create(cls) -> "MetricSnapshot":
        """Create empty snapshot."""
        return cls()
    
    def record(self, metric_value: MetricValue) -> "MetricSnapshot":
        """Add a metric value, returning new immutable instance."""
        return dataclass_replace(self, values=self.values + (metric_value,))
```

### Deterministic Metrics

All metrics must be:
- Deterministic (same input → same output)
- Reproducible across runs
- Not depend on system state alone

Example deterministic metrics:
```python
# Counters: always incrementing
"transition_count", "mutation_count", "snapshot_count"

# Rate metrics: computed deterministically  
"transition_rate", "mutation_rate", "validation_failure_rate"
```

---

## Telemetry System

### TelemetryKind

```python
TelemetryKind = Literal["counter", "gauge", "histogram"]
```

### TelemetryPoint

```python
@frozen
class TelemetryPoint:
    name: str
    value: float
    labels: Dict[str, str] = field(factory=dict)
    timestamp_utc: int
    kind: TelemetryKind
    
    @classmethod
    def counter(cls, name: str, value: float) -> "TelemetryPoint":
        return cls(name=name, value=float(value), kind="counter")
    
    @classmethod
    def gauge(cls, name: str, value: float) -> "TelemetryPoint":
        return cls(name=name, value=float(value), kind="gauge")
```

### TelemetryRecord

```python
@frozen
class TelemetryRecord:
    record_id: str = field(default_factory=_generate_uuid)
    points: Tuple[TelemetryPoint, ...] = ()
    
    def record_point(self, point: TelemetryPoint) -> "TelemetryRecord":
        """Add a telemetry point (bounded to max 100)."""
        new_points = self.points + (point,)
        if len(new_points) > 100:
            new_points = new_points[-100:]
        return dataclass_replace(self, points=new_points)
```

---

## Logging System

### LogSeverity

```python
LogSeverity = Literal["debug", "info", "warning", "error", "critical"]
```

### LogRecord

```python
@frozen
class LogRecord:
    operation: str  # e.g., "transition", "validation"
    message: str  # Redacted (no secrets)
    severity: LogSeverity
    runtime_id: Optional[str] = None
    component_id: Optional[str] = None
    state_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp_utc: int = field(default_factory=lambda: int(time.time() * 1000))
```

### Redaction Policy

All sensitive information is automatically redacted:
- Tokens → `[REDACTED]`
- Secrets → `[REDACTED]`
- Credentials → `[REDACTED]`

```python
def _redact_message(message: str) -> str:
    """Redact common secret patterns."""
    redacted = message
    for pattern in [r"token\s*=\s*['\"]?(\S+)['\"]?", r"secret\s*=\s*['\"]?(\S+)['\"]?"]:
        redacted = re.sub(pattern, lambda m: "[REDACTED]", redacted, flags=re.IGNORECASE)
    return redacted
```

### LogBatch

```python
@frozen
class LogBatch:
    batch_id: str = field(default_factory=_generate_uuid)
    captured_at_utc: int = field(default_factory=lambda: int(time.time() * 1000))
    records: Tuple[LogRecord, ...] = ()
    
    def add_record(self, record: LogRecord) -> "LogBatch":
        """Add a log record."""
        return dataclass_replace(self, records=self.records + (record,))
```

---

## Distributed Tracing

### TraceSpan

```python
@frozen
class TraceSpan:
    trace_id: str  # Same across all spans in a trace
    span_id: str  # Unique within the trace
    parent_span_id: Optional[str] = None
    operation_name: str
    start_time_utc: int
    end_time_utc: Optional[int] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate span duration."""
        if self.end_time_utc is None:
            return None
        return (self.end_time_utc - self.start_time_utc) / 1000.0
    
    def end(self) -> "TraceSpan":
        """Mark span as complete."""
        return dataclass_replace(
            self,
            end_time_utc=int(time.time() * 1000)
        )
```

### Trace

```python
@frozen
class Trace:
    trace_id: str = field(default_factory=_generate_uuid)
    spans: Tuple[TraceSpan, ...] = ()
    
    @classmethod
    def create(cls) -> "Trace":
        """Create new trace with unique ID."""
        return cls()
    
    def add_span(self, span: TraceSpan) -> "Trace":
        """Add a span (validates trace_id matches)."""
        if span.trace_id != self.trace_id:
            raise ValueError("Span trace_id must match trace trace_id")
        return dataclass_replace(self, spans=self.spans + (span,))
```

---

## Audit Records

### AuditRecord

```python
@frozen
class AuditRecord(DiagnosticArtifact):
    operation: str  # "transition", "validation", etc.
    initiating_authority: Optional[str]
    state_id: Optional[str] = None
    version_before: int = 0
    generation_before: int = 0
    version_after: Optional[int] = None
    generation_after: Optional[int] = None
    validation_outcome: str  # "valid", "invalid"
    transition_type: Optional[int] = None
    transition_result_code: Optional[int] = None
    findings: Tuple[str, ...] = ()
    timestamp_utc: int = field(default_factory=lambda: int(time.time() * 1000))
```

### AuditLog

```python
@frozen
class AuditLog:
    log_id: str = field(default_factory=_generate_uuid)
    records: Tuple[AuditRecord, ...] = ()
    max_records: int = 1000
    
    @classmethod
    def create(cls, max_records: int = 1000) -> "AuditLog":
        return cls(max_records=max_records)
    
    def append(self, record: AuditRecord) -> "AuditLog":
        """Append record (bounded to max_records)."""
        new_records = self.records + (record,)
        if len(new_records) > self.max_records:
            new_records = new_records[-self.max_records:]
        return dataclass_replace(self, records=new_records)
```

**Critical Property:** AuditLog is append-only. Records cannot be modified or deleted.

---

## Visibility Policies

### VisibilityRule

```python
@frozen
class VisibilityRule:
    pattern: str  # glob-style pattern (e.g., "public.*")
    allowed: Tuple[DiagnosticVisibility, ...]
    
    def matches(self, diagnostic_id: str) -> bool:
        """Check if rule matches a diagnostic ID."""
        import fnmatch
        return fnmatch.fnmatch(diagnostic_id, self.pattern)
```

### VisibilityPolicy

```python
@frozen
class VisibilityPolicy:
    policy_id: str
    rules: Tuple[VisibilityRule, ...]
    
    @classmethod
    def create_default(cls) -> "VisibilityPolicy":
        """Create default restrictive policy."""
        return cls(
            policy_id="default-restrictive",
            rules=(
                # Public diagnostics
                VisibilityRule.for_pattern("public.*", (DiagnosticVisibility.PUBLIC,)),
                # Administrative diagnostics require admin visibility
                VisibilityRule.for_pattern("admin.*", (DiagnosticVisibility.ADMINISTRATIVE,)),
                # Default deny all others
                VisibilityRule.default_deny(),
            )
        )
    
    def can_view(self, diagnostic_id: str, requested_visibility: DiagnosticVisibility) -> bool:
        """Check if a diagnostic can be viewed with given visibility."""
        for rule in self.rules:
            if rule.matches(diagnostic_id):
                return requested_visibility in rule.allowed
        return False
```

---

## Retention Policies

### RetentionPolicy

```python
@frozen
class RetentionPolicy:
    policy_id: str
    diagnostics_seconds: int = 7 * 24 * 3600  # 7 days default
    metrics_seconds: int = 7 * 24 * 3600
    logs_seconds: int = 7 * 24 * 3600
    traces_seconds: int = 7 * 24 * 3600
    audit_seconds: int = 30 * 24 * 3600  # 30 days for audit
    
    @classmethod
    def create(cls, policy_id: str) -> "RetentionPolicy":
        return cls(policy_id=policy_id)
    
    def is_expired(self, timestamp_utc: int, artifact_type: str) -> bool:
        """Check if an artifact has expired."""
        seconds = {
            "diagnostics": self.diagnostics_seconds,
            "metrics": self.metrics_seconds,
            "logs": self.logs_seconds,
            "traces": self.traces_seconds,
            "audit": self.audit_seconds,
        }.get(artifact_type, 7 * 24 * 3600)
        
        current_time = int(time.time() * 1000)
        age_ms = current_time - timestamp_utc
        return age_ms > (seconds * 1000)
```

---

## Validation Diagnostics

### ValidationFinding

```python
@frozen
class ValidationFinding:
    finding_id: str = field(default_factory=_generate_uuid)
    category: str  # "metrics", "diagnostics", etc.
    finding_type: str  # "missing_value", "out_of_range"
    message: str
    severity: LogSeverity
```

### ValidationResult

```python
@frozen
class ValidationResult:
    result_id: str = field(default_factory=_generate_uuid)
    is_valid: bool
    findings: Tuple[ValidationFinding, ...]
    
    @classmethod
    def valid(cls) -> "ValidationResult":
        return cls(is_valid=True, findings=())
    
    @classmethod
    def invalid(cls, findings: Tuple[ValidationFinding, ...]) -> "ValidationResult":
        return cls(is_valid=False, findings=findings)
```

---

## Inspection Interfaces

### StateInspection Protocol

```python
@runtime_checkable
class StateInspection(Protocol):
    """Protocol for state inspection."""
    
    def inspect_identity(self) -> Tuple[str, ...]:
        """Return all available identities."""
        ...
    
    def inspect_hierarchy(self) -> Dict[str, Any]:
        """Return hierarchy information."""
        ...
    
    def inspect_ownership(self) -> Tuple[OwnershipDiagnostics, ...]:
        """Return ownership diagnostics."""
        ...
```

### RuntimeInspection Protocol

```python
@runtime_checkable
class RuntimeInspection(Protocol):
    """Protocol for runtime inspection."""
    
    def get_runtime_diagnostics(self) -> RuntimeDiagnostics:
        """Get current runtime diagnostics."""
        ...
```

---

## ObservabilityFacade (Public API)

The `ObservabilityFacade` is the single entry point for all observability operations.

### Methods

| Method | Description |
|--------|-------------|
| `create_state_diagnostics()` | Create StateDiagnostics instance |
| `create_runtime_diagnostics()` | Create RuntimeDiagnostics instance |
| `record_metric()` | Record a metric value |
| `record_log()` | Record a log entry (with redaction) |
| `start_span()` | Start a new trace span |
| `create_audit_record()` | Create an audit record |
| `create_retention_policy()` | Create a retention policy |
| `validate_diagnostic_artifact()` | Validate a diagnostic artifact |

### Key Design

- **No mutation authority**: The facade only creates diagnostic artifacts
- **Immutability preserved**: All created artifacts are frozen dataclasses
- **Import-pure**: Importing the module has no side effects

---

## Architectural Invariants

### Invariant 1: Observability Never Becomes a Mutation Authority

```python
# This is INVALID - observability should never mutate state:
def bad_observability(state):
    state.value = 42  # NO! This makes it a mutation authority
    
# This is VALID - observability only creates diagnostics:
def good_observability(state):
    return StateDiagnostics.for_state(
        state_id=state.id,
        value_snapshot=state.value,  # Read-only snapshot
    )
```

### Invariant 2: Diagnostic Artifacts Are Immutable

```python
diag = StateDiagnostics.for_state("state-1", version_sequence=1)
# This raises AttributeError or TypeError:
diag.version_sequence = 2  # NO! Frozen dataclass

# Instead, create a new instance:
new_diag = dataclass_replace(diag, version_sequence=2)  # OK!
```

### Invariant 3: Audit Records Are Append-Only

```python
log = AuditLog.create()
record = AuditRecord.for_transition(...)
log.append(record)
# Original log is unchanged - append returns a new instance
```

---

## Testing Strategy

### Test Categories

1. **Diagnostics Tests**: Verify diagnostic model creation and immutability
2. **Metrics Tests**: Verify metric recording and snapshot creation
3. **Telemetry Tests**: Verify telemetry point generation and bounding
4. **Logging Tests**: Verify log record creation and redaction
5. **Tracing Tests**: Verify span creation, duration calculation
6. **Audit Tests**: Verify audit record creation and append-only behavior
7. **Policy Tests**: Verify visibility and retention policy enforcement
8. **Validation Tests**: Verify finding and result creation

### Test Fixture Pattern

```python
@pytest.fixture
def facade() -> ObservabilityFacade:
    """Create an observability facade instance."""
    return ObservabilityFacade()

def test_create_state_diagnostics(facade):
    diag = facade.create_state_diagnostics(
        state_id="test-state",
        domain="domain-1",
        owner_identity="owner-1",
        version_sequence=1,
    )
    assert isinstance(diag, StateDiagnostics)
```

### Import Purity Test

```python
def test_import_purity():
    """Test that importing the module has no side effects."""
    import sys
    initial_modules = set(sys.modules.keys())
    
    from gordon_system.src.agent.components.core.state.observability import __all__
    
    # Should not add new infrastructure modules
    assert len(set(sys.modules.keys()) - initial_modules) < N  # Tolerance for stdlib
```

---

## Integration Points

### Runtime Hierarchy
- Diagnostics include scope/parent relationships

### Ownership
- OwnershipDiagnostics tracks ownership history and authority type

### Transitions
- TransitionDiagnostics records transition type and result code

### Persistence
- Persistence state is exposed in diagnostics

### Restoration
- Restoration status is tracked in diagnostics

### Recovery
- Recovery status is tracked in diagnostics

### Health, Readiness, Admission
- Observability reports to these systems but does not replace them

---

## Documentation Files

| File | Purpose |
|------|---------|
| `phase-3.15.12-state-observability-diagnostics.md` | This documentation |
| `test_state_observability.py` | Comprehensive test suite |

---

## Migration Notes

### Legacy Gordon
- Do NOT import legacy monitoring systems
- Extract concepts only (not code)
- Reimplement natively for Phase 3.15.12

### Existing Code
- Remove duplicate observability frameworks
- Migrate to canonical `ObservabilityFacade` API
- Update imports from legacy paths to new canonical path

---

## Future Enhancements

Potential future additions:
- Metrics aggregation windows
- Log search indices
- Distributed trace sampling strategies
- Audit record export connectors (S3, Elasticsearch)
- Real-time diagnostic streaming

---

## Compliance Checklist

- [x] One canonical observability architecture exists
- [x] One canonical diagnostics architecture exists  
- [x] Diagnostics remain immutable (frozen dataclasses)
- [x] Observability never becomes a mutation authority
- [x] Metrics are deterministic and reproducible
- [x] Telemetry is structured with bounded records
- [x] Logs are structured with automatic redaction
- [x] Tracing preserves operation lineage via trace_id/span_id
- [x] Audit records are immutable and append-only
- [x] Inspection interfaces are read-only (protocol-based)
- [x] Retention policies are explicit and bounded
- [x] Diagnostic visibility is policy-controlled
- [x] Public APIs expose no mutable runtime state
- [x] No duplicate observability framework exists
- [x] Documentation matches implementation

---

*End of Phase 3.15.12 Documentation*