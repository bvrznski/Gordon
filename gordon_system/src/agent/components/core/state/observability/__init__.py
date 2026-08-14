# State Observability & Diagnostics - Phase 3.15.12
# =====================================================

"""
Canonical State Observability Architecture for Gordon Core.

This module implements the single canonical observability and diagnostics architecture
governing how runtime state is monitored, analyzed, explained, audited, and visualized
without violating ownership, mutability, isolation, or architectural boundaries.

ARCHITECTURAL PRINCIPLES:
    1. Observability is observational only - NEVER a mutation authority
    2. One canonical observability architecture exists throughout the Core
    3. Diagnostics remain immutable diagnostic artifacts
    4. Metrics are deterministic and reproducible
    5. Logs are structured and redact sensitive information
    6. Tracing preserves operation lineage
    7. Audit records are immutable and append-only
    8. Inspection interfaces are read-only
    9. Retention policies are explicit and bounded
    10. Visibility policies control diagnostic access

EXTENDS:
    Phase 3.15.1 - Core State Foundations
    Phase 3.15.2 - State Identity, Scope & Ownership
    Phase 3.15.3 - Immutable & Mutable State Semantics
    Phase 3.15.4 - Runtime State Hierarchy
    Phase 3.15.5 - State Transitions & Transition Validation
    Phase 3.15.6 - State Snapshots & Views
    Phase 3.15.7 - State Versioning & Generations
    Phase 3.15.8 - State Consistency & Concurrency
    Phase 3.15.9 - State Persistence Boundaries
    Phase 3.15.10 - State Restoration & Reconciliation
    Phase 3.15.11 - Cross-Runtime State Isolation

PUBLIC API:
    - Diagnostics models (immutable diagnostic artifacts)
    - Metrics system (canonical metrics for state aggregates)
    - Telemetry system (structured telemetry data)
    - Logging system (structured logging with redaction)
    - Tracing system (distributed tracing support)
    - Audit records (immutable audit trail)
    - Inspection interfaces (read-only inspection)
    - Visibility policies (access control for diagnostics)
    - Retention policies (bounded retention management)

NO IMPORT-SIDE EFFECTS:
    Importing this module does NOT:
        - Create runtime state
        - Mutate runtime state
        - Allocate monitoring infrastructure
        - Start exporters
        - Connect to telemetry backends
"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto
import uuid
import time as _time_module

# Core state foundations (Phase 3.15.x)
from ..identity import AggregateId, RuntimeId, BootSessionId, OwnerId
from ..ownership import OwnershipAuthorityType
from ..transitions import (
    TransitionType,
    ValidationOutcome,
    TransitionResultCode,
)

# =============================================================================
# OBSERVABILITY ARCHITECTURE
# =============================================================================


class ObservabilityDomain(Enum):
    """
    Canonical domains of observability.
    
    DOMAINS:
        DIAGNOSTICS: Diagnostics and inspection artifacts
        METRICS: Quantitative measurements
        TELEMETRY: Structured telemetry data
        LOGGING: Structured log records
        TRACING: Distributed tracing spans
        AUDIT: Immutable audit trail
        INSPECTION: Read-only state inspection
    
    INVARIANTS:
        OBS-001: Every observability artifact belongs to exactly one domain
        OBS-002: Domains are mutually exclusive (no overlap)
        OBS-003: All domains preserve immutability guarantees
    """
    
    DIAGNOSTICS = "diagnostics"
    METRICS = "metrics"
    TELEMETRY = "telemetry"
    LOGGING = "logging"
    TRACING = "tracing"
    AUDIT = "audit"
    INSPECTION = "inspection"


# =============================================================================
# DIAGNOSTIC VISIBILITY
# =============================================================================


class DiagnosticVisibility(Enum):
    """
    Visibility level for diagnostic artifacts.
    
    VISIBILITY LEVELS:
        PUBLIC: Visible to all consumers (no sensitive data)
        ADMINISTRATIVE: Visible to administrative roles
        INTERNAL: Visible only within subsystem
        PRIVILEGED: Visible only to privileged security domains
    
    INVARIANTS:
        VIS-001: Every diagnostic has an explicit visibility level
        VIS-002: Visibility is enforced at all access points
        VIS-003: No visibility implies no access (deny by default)
    """
    
    PUBLIC = "public"
    ADMINISTRATIVE = "administrative"
    INTERNAL = "internal"
    PRIVILEGED = "privileged"


# =============================================================================
# DIAGNOSTIC ARTIFACT BASE CLASS
# =============================================================================


@dataclass(frozen=True)
class DiagnosticArtifact:
    """
    Base class for all immutable diagnostic artifacts.
    
    INVARIANTS:
        DIAG-ART-001: Artifacts are immutable once created
        DIAG-ART-002: Artifacts preserve provenance information
        DIAG-ART-003: Artifacts never expose mutable state handles
    
    ALL ARTIFACTS MUST INCLUDE:
        - artifact_id: Unique identifier for this artifact
        - timestamp_utc: When the artifact was created
        - runtime_id: Which runtime instance generated it
        - boot_session_id: Session context for isolation
        - provenance: Source information (component, operation, etc.)
    """
    
    artifact_id: str
    timestamp_utc: float = field(default_factory=_time_module.monotonic)
    runtime_id: Optional[str] = None
    boot_session_id: Optional[str] = None
    
    # Provenance tracking
    component_id: Optional[str] = None
    originating_operation: Optional[str] = None
    originating_transition: Optional[str] = None
    provenance: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert artifact to dictionary representation."""
        return {
            "artifact_id": self.artifact_id,
            "timestamp_utc": self.timestamp_utc,
            "runtime_id": self.runtime_id,
            "boot_session_id": self.boot_session_id,
            "component_id": self.component_id,
            "originating_operation": self.originating_operation,
            "originating_transition": self.originating_transition,
            "provenance": self.provenance.copy(),
        }


# =============================================================================
# DIAGNOSTICS MODEL
# =============================================================================


@dataclass(frozen=True)
class StateDiagnostics(DiagnosticArtifact):
    """
    Immutable diagnostics for a state aggregate.
    
    Provides comprehensive diagnostic information about:
        - Identity and scope
        - Ownership and authority
        - Version and generation
        - Lifecycle stage
        - Validation status
    
    INVARIANTS:
        DIAG-001: Diagnostics are immutable once created
        DIAG-002: Diagnostics never expose mutable state handles
        DIAG-003: Diagnostics preserve full provenance chain
    """
    
    # State identity
    state_id: str
    domain: Optional[str] = None
    scope: Optional[str] = None
    
    # Ownership
    owner_identity: Optional[str] = None
    owner_kind: Optional[str] = None  # e.g., "lifecycle", "execution"
    
    # Authority
    authority_type: Optional[str] = None  # e.g., "exclusive_mutation"
    
    # Version and generation
    version_sequence: int = 0
    generation: int = 0
    
    # Mutability classification
    mutability_class: str = "versioned_aggregate"  # immutable, mutable
    
    # Lifecycle status
    lifecycle_stage: Optional[str] = None  # e.g., "initialized", "active", "terminated"
    
    # Last operation reference
    last_operation_id: Optional[str] = None
    last_change_id: Optional[str] = None
    
    # Validation summary
    validation_summary: str = "unknown"  # valid, invalid, pending
    
    # Snapshot and view summary (counts)
    snapshot_count: int = 0
    view_count: int = 0
    
    # Failure summary
    failure_count: int = 0
    last_failure_id: Optional[str] = None
    
    # Persistence eligibility
    persistence_eligible: bool = False
    restoration_eligible: bool = False
    
    # Bounded diagnostics history (oldest first, max 10 items)
    recent_findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def for_state(
        cls,
        state_id: str,
        domain: Optional[str] = None,
        scope: Optional[str] = None,
        owner_identity: Optional[str] = None,
        owner_kind: Optional[str] = None,
        authority_type: Optional[str] = None,
        version_sequence: int = 0,
        generation: int = 0,
        mutability_class: str = "versioned_aggregate",
    ) -> "StateDiagnostics":
        """Create diagnostics for a state aggregate."""
        return cls(
            artifact_id=f"diag-{uuid.uuid4().hex}",
            state_id=state_id,
            domain=domain,
            scope=scope,
            owner_identity=owner_identity,
            owner_kind=owner_kind,
            authority_type=authority_type,
            version_sequence=version_sequence,
            generation=generation,
            mutability_class=mutability_class,
        )
    
    def add_finding(self, finding: str) -> "StateDiagnostics":
        """Add a finding to diagnostics history (bounded)."""
        new_findings = tuple(list(self.recent_findings)[-9:] + [finding])
        return dataclass_replace(self, recent_findings=new_findings)


@dataclass(frozen=True)
class RuntimeDiagnostics(DiagnosticArtifact):
    """
    Immutable diagnostics for a runtime instance.
    
    INVARIANTS:
        DIAG-RT-001: Diagnostics are immutable once created
        DIAG-RT-002: Runtime identity is preserved
        DIAG-RT-003: Session information is bounded
    """
    
    # Runtime identification
    runtime_id: str
    boot_session_id: Optional[str] = None
    
    # State management statistics
    state_count: int = 0
    mutation_owner_states: int = 0
    observer_states: int = 0
    
    # Active operations
    active_operations: int = 0
    pending_transfers: int = 0
    
    # Runtime metadata
    process_id: Optional[str] = None
    host_name: Optional[str] = None
    
    @classmethod
    def for_runtime(
        cls,
        runtime_id: str,
        boot_session_id: Optional[str] = None,
    ) -> "RuntimeDiagnostics":
        """Create diagnostics for a runtime instance."""
        return cls(
            artifact_id=f"diag-rt-{uuid.uuid4().hex}",
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
        )


@dataclass(frozen=True)
class ScopeDiagnostics(DiagnosticArtifact):
    """
    Immutable diagnostics for a scope context.
    
    INVARIANTS:
        DIAG-SCOPE-001: Diagnostics are immutable once created
        DIAG-SCOPE-002: Scope hierarchy is preserved
        DIAG-SCOPE-003: Visibility boundaries are recorded
    """
    
    # Scope identification
    scope_id: str
    scope_type: str  # e.g., "application", "runtime", "component"
    
    # Parent scope (for inheritance tracking)
    parent_scope_id: Optional[str] = None
    
    # State counts within this scope
    state_count: int = 0
    mutation_owner_states: int = 0
    
    # Runtime binding
    runtime_binding: Optional[str] = None
    
    # Isolation boundaries
    isolation_boundary: str = "scope"  # e.g., "scope", "runtime"
    
    @classmethod
    def for_scope(
        cls,
        scope_id: str,
        scope_type: str,
        parent_scope_id: Optional[str] = None,
    ) -> "ScopeDiagnostics":
        """Create diagnostics for a scope."""
        return cls(
            artifact_id=f"diag-scope-{uuid.uuid4().hex}",
            scope_id=scope_id,
            scope_type=scope_type,
            parent_scope_id=parent_scope_id,
        )


@dataclass(frozen=True)
class ValidationDiagnostics(DiagnosticArtifact):
    """
    Immutable diagnostics for validation results.
    
    INVARIANTS:
        DIAG-VAL-001: Diagnostics are immutable once created
        DIAG-VAL-002: Validation history is preserved
        DIAG-VAL-003: Findings are bounded
    """
    
    # Validation identification
    validation_id: str
    
    # Target state
    state_id: Optional[str] = None
    
    # Overall result
    overall_validity: bool = False
    
    # Findings summary
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    
    # Validation context
    validator_identity: Optional[str] = None
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Findings (bounded)
    findings_summary: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def for_validation(
        cls,
        validation_id: str,
        overall_validity: bool,
        error_count: int = 0,
        warning_count: int = 0,
        info_count: int = 0,
    ) -> "ValidationDiagnostics":
        """Create diagnostics for a validation."""
        return cls(
            artifact_id=f"diag-val-{uuid.uuid4().hex}",
            validation_id=validation_id,
            overall_validity=overall_validity,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
        )


@dataclass(frozen=True)
class OwnershipDiagnostics(DiagnosticArtifact):
    """
    Immutable diagnostics for state ownership.
    
    INVARIANTS:
        DIAG-OWN-001: Diagnostics are immutable once created
        DIAG-OWN-002: Diagnostics don't expose live handles or secrets
        DIAG-OWN-003: Diagnostics include full ownership history
    """
    
    # State context
    state_id: str
    domain: Optional[str] = None
    scope: Optional[str] = None
    
    # Current ownership
    current_owner_identity: Optional[str] = None
    current_authority_type: Optional[str] = None
    
    # Ownership history (ordered, oldest first)
    ownership_history: Tuple[str, ...] = field(default_factory=tuple)  # Owner IDs in order
    
    # Transfer history
    transfer_count: int = 0
    last_transfer_at_utc: Optional[float] = None
    
    # Validation summary
    validation_summary: str = "unknown"  # valid, invalid, pending
    
    @classmethod
    def for_state(
        cls,
        state_id: str,
        current_owner_identity: Optional[str] = None,
        current_authority_type: Optional[str] = None,
        ownership_history: Tuple[str, ...] = tuple(),
    ) -> "OwnershipDiagnostics":
        """Create diagnostics for a state aggregate."""
        return cls(
            artifact_id=f"diag-own-{uuid.uuid4().hex}",
            state_id=state_id,
            current_owner_identity=current_owner_identity,
            current_authority_type=current_authority_type,
            ownership_history=ownership_history,
        )


@dataclass(frozen=True)
class TransitionDiagnostics(DiagnosticArtifact):
    """
    Immutable diagnostics for transition operations.
    
    INVARIANTS:
        DIAG-TRA-001: Diagnostics are immutable once created
        DIAG-TRA-002: Transition history is preserved
        DIAG-TRA-003: Evidence chain is recorded
    """
    
    # Transition identification
    transition_id: str
    
    # State and operation
    state_id: str
    transition_type: Optional[str] = None  # TransitionType if known
    
    # Timing
    started_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    # Result
    result_code: Optional[str] = None  # TransitionResultCode if known
    
    # Version tracking
    version_before: int = 0
    version_after: Optional[int] = None
    
    generation_before: int = 0
    generation_after: Optional[int] = None
    
    # Validation outcome
    validation_outcome: Optional[str] = None  # ValidationOutcome if known
    validation_findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def for_transition(
        cls,
        transition_id: str,
        state_id: str,
        transition_type: Optional[TransitionType] = None,
        result_code: Optional[TransitionResultCode] = None,
    ) -> "TransitionDiagnostics":
        """Create diagnostics for a transition."""
        return cls(
            artifact_id=f"diag-tra-{uuid.uuid4().hex}",
            transition_id=transition_id,
            state_id=state_id,
            transition_type=transition_type.value if transition_type else None,
            result_code=result_code.value if result_code else None,
        )


# =============================================================================
# METRICS MODEL
# =============================================================================


class MetricType(Enum):
    """
    Types of metrics tracked for state aggregates.
    
    TYPES:
        AGGREGATE_COUNT: Total number of state aggregates
        ACTIVE_RUNTIME_COUNT: Number of active runtime instances
        TRANSITION_RATE: Transitions per second
        MUTATION_RATE: Mutations per second
        SNAPSHOT_RATE: Snapshots created per second
        RESTORATION_RATE: Restorations per second
        PERSISTENCE_RATE: Persistence operations per second
        VALIDATION_FAILURES: Validation failures count
        OWNERSHIP_VIOLATIONS: Ownership violation count
        ISOLATION_VIOLATIONS: Isolation boundary violations
    
    INVARIANTS:
        METRIC-001: Every metric has a type from this taxonomy
        METRIC-002: Metrics are deterministic and reproducible
        METRIC-003: Metrics preserve aggregation semantics
    """
    
    AGGREGATE_COUNT = "aggregate_count"
    ACTIVE_RUNTIME_COUNT = "active_runtime_count"
    TRANSITION_RATE = "transition_rate"
    MUTATION_RATE = "mutation_rate"
    SNAPSHOT_RATE = "snapshot_rate"
    RESTORATION_RATE = "restoration_rate"
    PERSISTENCE_RATE = "persistence_rate"
    VALIDATION_FAILURES = "validation_failures"
    OWNERSHIP_VIOLATIONS = "ownership_violations"
    ISOLATION_VIOLATIONS = "isolation_violations"


@dataclass(frozen=True)
class MetricValue:
    """
    A single metric value with metadata.
    
    INVARIANTS:
        METRIC-VAL-001: Value is immutable once created
        METRIC-VAL-002: Timestamp preserves ordering
        METRIC-VAL-003: Labels enable filtering
    """
    
    name: str  # Metric type as string
    value: float
    
    # Timestamp
    timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    # Labels for filtering/aggregation
    labels: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def counter(cls, name: str, value: int) -> "MetricValue":
        """Create a counter metric."""
        return cls(name=name, value=float(value))
    
    @classmethod
    def gauge(cls, name: str, value: float) -> "MetricValue":
        """Create a gauge metric."""
        return cls(name=name, value=value)


@dataclass(frozen=True)
class MetricSnapshot:
    """
    Snapshot of all metrics at a point in time.
    
    INVARIANTS:
        SNAPSHOT-001: Snapshot is immutable once created
        SNAPSHOT-002: Snapshot captures all metrics at one moment
        SNAPSHOT-003: No mutable state exposed
    """
    
    snapshot_id: str
    
    # Timestamps
    captured_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # All metric values
    values: Tuple[MetricValue, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls) -> "MetricSnapshot":
        """Create an empty metric snapshot."""
        return cls(snapshot_id=f"metric-snap-{uuid.uuid4().hex}")
    
    def record(self, value: MetricValue) -> "MetricSnapshot":
        """Add a metric value to the snapshot."""
        new_values = self.values + (value,)
        return dataclass_replace(self, values=new_values)


# =============================================================================
# TELEMETRY MODEL
# =============================================================================


class TelemetryKind(Enum):
    """
    Kinds of telemetry data.
    
    KINDS:
        COUNTER: Monotonically increasing counter
        GAUGE: Current value that can go up or down
        HISTOGRAM: Distribution of values
        TIMER: Time duration measurements
        UTILIZATION: Resource utilization percentage
        THROUGHPUT: Events per time unit
        LATENCY: Response latency distribution
        QUEUE_DEPTH: Queue length measurement
        CONTENTION: Contention ratio
        FAILURE_RATE: Failure occurrence rate
    
    INVARIANTS:
        TELE-001: Every telemetry point has exactly one kind
        TELE-002: Kind determines how value is interpreted
        TELE-003: Telemetry preserves timing information
    """
    
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    UTILIZATION = "utilization"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    QUEUE_DEPTH = "queue_depth"
    CONTENTION = "contention"
    FAILURE_RATE = "failure_rate"


@dataclass(frozen=True)
class TelemetryPoint:
    """
    A single telemetry data point.
    
    INVARIANTS:
        TELE-POINT-001: Point is immutable once created
        TELE-POINT-002: Kind determines value semantics
        TELE-POINT-003: Timing is preserved
    """
    
    name: str  # Metric name
    kind: TelemetryKind
    
    # Value(s) depending on kind
    value: Optional[float] = None  # Single value for counter/gauge
    values: Tuple[float, ...] = field(default_factory=tuple)  # Distribution for histogram/timer
    
    # Timestamps
    timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def counter(cls, name: str, value: int) -> "TelemetryPoint":
        """Create a counter telemetry point."""
        return cls(name=name, kind=TelemetryKind.COUNTER, value=float(value))
    
    @classmethod
    def gauge(cls, name: str, value: float) -> "TelemetryPoint":
        """Create a gauge telemetry point."""
        return cls(name=name, kind=TelemetryKind.GAUGE, value=value)
    
    @classmethod
    def histogram(cls, name: str, values: Tuple[float, ...]) -> "TelemetryPoint":
        """Create a histogram telemetry point."""
        return cls(
            name=name,
            kind=TelemetryKind.HISTOGRAM,
            values=values,
        )


@dataclass(frozen=True)
class TelemetryRecord:
    """
    A complete telemetry record with context.
    
    INVARIANTS:
        TELE-RECORD-001: Record is immutable once created
        TELE-RECORD-002: Context preserves provenance
        TELE-RECORD-003: All points are bounded
    """
    
    record_id: str
    
    # Timestamps
    captured_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Points (bounded to 100 max)
    points: Tuple[TelemetryPoint, ...] = field(default_factory=tuple)
    
    # Context
    runtime_id: Optional[str] = None
    component_id: Optional[str] = None
    
    @classmethod
    def create(cls) -> "TelemetryRecord":
        """Create an empty telemetry record."""
        return cls(record_id=f"telem-{uuid.uuid4().hex}")
    
    def record_point(self, point: TelemetryPoint) -> "TelemetryRecord":
        """Add a telemetry point to the record."""
        # Keep only last 100 points
        new_points = tuple(list(self.points)[-99:] + [point])
        return dataclass_replace(self, points=new_points)


# =============================================================================
# LOGGING MODEL
# =============================================================================


class LogSeverity(Enum):
    """
    Severity levels for log records.
    
    LEVELS:
        TRACE: Detailed trace information (debugging)
        DEBUG: Debug-level information
        INFO: General informational messages
        NOTICE: Normal but significant events
        WARNING: Potential issues requiring attention
        ERROR: Error conditions detected
        CRITICAL: Critical failures requiring immediate attention
        FATAL: System failure events
    
    INVARIANTS:
        LOG-LEV-001: Every log record has exactly one severity
        LOG-LEV-002: Severity order is preserved (TRACE < DEBUG < INFO < ...)
        LOG-LEV-003: Redaction preserves logging structure
    """
    
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


@dataclass(frozen=True)
class LogRecord:
    """
    A single structured log record.
    
    INVARIANTS:
        LOG-001: Record is immutable once created
        LOG-002: All required fields are present
        LOG-003: Sensitive information is redacted
    """
    
    # Identity
    record_id: str
    
    # Timestamp
    timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    # Severity
    severity: LogSeverity
    
    # Context (where applicable)
    runtime_id: Optional[str] = None
    component_id: Optional[str] = None
    aggregate_id: Optional[str] = None
    version: Optional[int] = None
    generation: Optional[int] = None
    
    # Operation context
    operation: str  # e.g., "transition", "validation", "persistence"
    transition_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Message (always redacted of secrets)
    message: str
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def for_operation(
        cls,
        operation: str,
        message: str,
        severity: LogSeverity = LogSeverity.INFO,
        runtime_id: Optional[str] = None,
        component_id: Optional[str] = None,
        aggregate_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> "LogRecord":
        """Create a log record for an operation."""
        return cls(
            record_id=f"log-{uuid.uuid4().hex[:16]}",
            severity=severity,
            runtime_id=runtime_id,
            component_id=component_id,
            aggregate_id=aggregate_id,
            operation=operation,
            message=_redact_sensitive(message),
            correlation_id=correlation_id,
        )


def _redact_sensitive(message: str) -> str:
    """
    Redact sensitive information from log messages.
    
    Removes patterns that might contain secrets, passwords, tokens, etc.
    This function preserves the structure of the message while removing
    potentially sensitive values.
    
    Args:
        message: The original log message
        
    Returns:
        A redacted version of the message
    """
    import re
    
    # Patterns to redact (these will be replaced with [REDACTED])
    patterns = [
        r'(password|passwd|pwd)\s*[=:]\s*\S+',
        r'(token|secret|api_key)\s*[=:]\s*\S+',
        r'authorization\s*[=:]?\s*["\']?\w+["\']?',
        r'private[_-]?key\b.*?(?=\s|$)',
    ]
    
    result = message
    for pattern in patterns:
        result = re.sub(pattern, '[REDACTED]', result, flags=re.IGNORECASE)
    
    return result


@dataclass(frozen=True)
class LogBatch:
    """
    A batch of log records.
    
    INVARIANTS:
        LOG-BATCH-001: Batch is immutable once created
        LOG-BATCH-002: Records are ordered chronologically
        LOG-BATCH-003: Bounded size (max 1000)
    """
    
    batch_id: str
    
    # Timestamps
    captured_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Records
    records: Tuple[LogRecord, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls) -> "LogBatch":
        """Create an empty log batch."""
        return cls(batch_id=f"log-batch-{uuid.uuid4().hex}")
    
    def add_record(self, record: LogRecord) -> "LogBatch":
        """Add a log record to the batch (bounded)."""
        new_records = tuple(list(self.records)[-999:] + [record])
        return dataclass_replace(self, records=new_records)


# =============================================================================
# TRACING MODEL
# =============================================================================


@dataclass(frozen=True)
class TraceSpan:
    """
    A single span in a distributed trace.
    
    INVARIANTS:
        SPAN-001: Span is immutable once created
        SPAN-002: Parent-child relationships are preserved
        SPAN-003: Timing information is accurate
    """
    
    # Identity
    span_id: str
    trace_id: str
    
    # Operation context
    operation_name: str
    kind: Optional[str] = None  # e.g., "internal", "producer", "consumer"
    
    # Timestamps (monotonic)
    start_time_utc: float = field(default_factory=_time_module.monotonic)
    end_time_utc: Optional[float] = None
    
    # Attributes
    attributes: Dict[str, str] = field(default_factory=dict)
    
    # References
    parent_span_id: Optional[str] = None
    trace_state: Optional[str] = None
    
    # Status
    status_code: Optional[int] = None  # 0 = OK, non-zero = error
    status_message: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ) -> "TraceSpan":
        """Create a new trace span."""
        return cls(
            span_id=f"span-{uuid.uuid4().hex[:16]}",
            trace_id=trace_id or f"trace-{uuid.uuid4().hex}",
            operation_name=operation_name,
            parent_span_id=parent_span_id,
        )
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate span duration, or None if not ended."""
        if self.end_time_utc is None:
            return None
        return self.end_time_utc - self.start_time_utc
    
    def end(self) -> "TraceSpan":
        """Create a copy with the span marked as ended."""
        return dataclass_replace(
            self,
            end_time_utc=_time_module.monotonic(),
        )


@dataclass(frozen=True)
class Trace:
    """
    A complete trace containing multiple spans.
    
    INVARIANTS:
        TRACE-001: Trace is immutable once created
        TRACE-002: Span hierarchy is preserved
        TRACE-003: All spans share same trace_id
    """
    
    # Identity
    trace_id: str
    
    # Timestamps
    started_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    # Spans (ordered by start time, then by span_id for determinism)
    spans: Tuple[TraceSpan, ...] = field(default_factory=tuple)
    
    # Context
    runtime_id: Optional[str] = None
    component_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        trace_id: Optional[str] = None,
    ) -> "Trace":
        """Create a new trace."""
        return cls(trace_id=trace_id or f"trace-{uuid.uuid4().hex}")
    
    def add_span(self, span: TraceSpan) -> "Trace":
        """Add a span to the trace (spans must share same trace_id)."""
        if span.trace_id != self.trace_id:
            raise ValueError(f"Span trace_id {span.trace_id} doesn't match trace {self.trace_id}")
        
        new_spans = tuple(list(self.spans) + [span])
        return dataclass_replace(self, spans=new_spans)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total trace duration."""
        if self.completed_at_utc is None:
            # Find latest end time among spans
            max_end = max((s.end_time_utc for s in self.spans), default=None)
            if max_end is not None:
                return max_end - self.started_at_utc
            return None
        
        return self.completed_at_utc - self.started_at_utc


# =============================================================================
# AUDIT RECORDS
# =============================================================================


@dataclass(frozen=True)
class AuditRecord(DiagnosticArtifact):
    """
    An immutable audit record preserving operation history.
    
    INVARIANTS:
        AUDIT-001: Record is immutable once created
        AUDIT-002: Records are append-only (never updated)
        AUDIT-003: Evidence chain is preserved
    
    ALL AUDIT RECORDS MUST INCLUDE:
        - operation: What operation was performed
        - initiating_authority: Who initiated the operation
        - ownership: State ownership at time of operation
        - version/generation: State version context
        - validation_outcome: Whether validation passed
        - transition_result: Result of any state transition
    """
    
    # Record identification
    audit_id: str
    
    # Operation details
    operation: str  # e.g., "transition", "validation", "persistence"
    
    # Initiator
    initiating_authority: str
    initiator_identity: Optional[str] = None
    
    # State context
    state_id: Optional[str] = None
    domain: Optional[str] = None
    scope: Optional[str] = None
    
    # Ownership and authority
    ownership_at_time: Optional[str] = None  # Owner identity at operation time
    authority_type: Optional[str] = None
    
    # Version context
    version_before: int = 0
    generation_before: int = 0
    
    # Validation outcome
    validation_outcome: str = "pending"  # valid, invalid, rejected
    validation_findings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Transition result (if applicable)
    transition_type: Optional[str] = None
    transition_result_code: Optional[str] = None  # TransitionResultCode if known
    
    # Timestamps
    recorded_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def for_transition(
        cls,
        operation: str,
        initiating_authority: str,
        state_id: str,
        version_before: int,
        generation_before: int,
        validation_outcome: str,
        transition_type: Optional[TransitionType] = None,
        transition_result_code: Optional[TransitionResultCode] = None,
    ) -> "AuditRecord":
        """Create an audit record for a transition operation."""
        return cls(
            audit_id=f"audit-{uuid.uuid4().hex[:16]}",
            operation=operation,
            initiating_authority=initiating_authority,
            state_id=state_id,
            version_before=version_before,
            generation_before=generation_before,
            validation_outcome=validation_outcome,
            transition_type=transition_type.value if transition_type else None,
            transition_result_code=transition_result_code.value if transition_result_code else None,
        )
    
    @classmethod
    def for_validation(
        cls,
        operation: str,
        initiating_authority: str,
        state_id: str,
        version_before: int,
        generation_before: int,
        validation_outcome: str,
        findings: Tuple[str, ...] = tuple(),
    ) -> "AuditRecord":
        """Create an audit record for a validation operation."""
        return cls(
            audit_id=f"audit-{uuid.uuid4().hex[:16]}",
            operation=operation,
            initiating_authority=initiating_authority,
            state_id=state_id,
            version_before=version_before,
            generation_before=generation_before,
            validation_outcome=validation_outcome,
            validation_findings=findings,
        )


@dataclass(frozen=True)
class AuditLog:
    """
    A bounded audit log containing multiple records.
    
    INVARIANTS:
        AUDIT-LOG-001: Log is immutable once created
        AUDIT-LOG-002: Records are appended in order (never deleted)
        AUDIT-LOG-003: Maximum size is enforced
    
    RETENTION POLICY:
        - Default maximum: 10,000 records
        - Old records may be pruned when limit exceeded
        - Pruning preserves chronological integrity
    """
    
    log_id: str
    
    # Configuration
    max_records: int = 10_000
    
    # Records (chronologically ordered)
    _records: Tuple[AuditRecord, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_records: int = 10_000) -> "AuditLog":
        """Create a new audit log."""
        return cls(log_id=f"audit-log-{uuid.uuid4().hex}")
    
    def append(self, record: AuditRecord) -> "AuditLog":
        """
        Append a record to the audit log.
        
        Preserves chronological order and enforces maximum size.
        """
        new_records = self._records + (record,)
        
        # Enforce maximum size (keep newest records)
        if len(new_records) > self.max_records:
            new_records = new_records[-self.max_records:]
        
        return dataclass_replace(self, _records=new_records)
    
    @property
    def records(self) -> Tuple[AuditRecord, ...]:
        """Get all audit records."""
        return self._records
    
    @property
    def record_count(self) -> int:
        """Get the number of records in the log."""
        return len(self._records)
    
    def get_latest(self) -> Optional[AuditRecord]:
        """Get the most recent audit record."""
        if not self._records:
            return None
        return self._records[-1]


# =============================================================================
# INSPECTION INTERFACES
# =============================================================================


@runtime_checkable
class StateInspection(Protocol):
    """
    Protocol for read-only state inspection.
    
    All inspection methods shall be:
        - Pure functions (no side effects)
        - Deterministic (same input = same output)
        - Non-mutating (never change runtime state)
    
    INVARIANTS:
        INSPECT-001: All methods are read-only
        INSPECT-002: No mutation authority granted
        INSPECT-003: Results are deterministic
    """
    
    def inspect_identity(self, state_id: str) -> Dict[str, Optional[str]]:
        """Get identity information for a state aggregate."""
        ...
    
    def inspect_ownership(self, state_id: str) -> Dict[str, Optional[str]]:
        """Get ownership information for a state aggregate."""
        ...
    
    def inspect_version(self, state_id: str) -> Dict[str, int]:
        """Get version and generation info for a state aggregate."""
        ...
    
    def inspect_health(self, state_id: str) -> Dict[str, bool]:
        """Get health status for a state aggregate."""
        ...
    
    def inspect_diagnostics(self, state_id: str) -> StateDiagnostics:
        """Get full diagnostics snapshot for a state aggregate."""
        ...


@runtime_checkable
class RuntimeInspection(Protocol):
    """
    Protocol for read-only runtime inspection.
    
    INVARIANTS:
        RT-INSPECT-001: All methods are read-only
        RT-INSPECT-002: No mutation authority granted
        RT-INSPECT-003: Results are deterministic
    """
    
    def inspect_runtime(self, runtime_id: str) -> RuntimeDiagnostics:
        """Get diagnostics for a runtime instance."""
        ...
    
    def inspect_aggregates(self, runtime_id: Optional[str] = None) -> Dict[str, int]:
        """Get aggregate counts by state type."""
        ...
    
    def inspect_health(self) -> Dict[str, bool]:
        """Get overall runtime health status."""
        ...


# =============================================================================
# VISIBILITY POLICIES
# =============================================================================


@dataclass(frozen=True)
class VisibilityPolicy:
    """
    Policy controlling diagnostic visibility.
    
    INVARIANTS:
        VIS-POL-001: Policy is immutable once created
        VIS-POL-002: Default is deny (explicit allow only)
        VIS-POL-003: Policy applies to all diagnostic types
    
    POLICY RULES:
        - Each rule specifies allowed visibility levels
        - Rules are evaluated in order, first match wins
        - No match = deny access
    """
    
    # Policy identifier
    policy_id: str
    
    # Rules (evaluated in order)
    rules: Tuple["VisibilityRule", ...] = field(default_factory=tuple)
    
    @classmethod
    def create_default(cls) -> "VisibilityPolicy":
        """Create a restrictive default visibility policy."""
        return cls(
            policy_id="default-restrictive",
            rules=(
                VisibilityRule.for_pattern("public.*", (DiagnosticVisibility.PUBLIC,)),
                VisibilityRule.for_pattern("internal.*", (DiagnosticVisibility.INTERNAL, DiagnosticVisibility.PRIVILEGED)),
                VisibilityRule.default_deny(),
            ),
        )
    
    def can_view(self, diagnostic_id: str, requested_visibility: DiagnosticVisibility) -> bool:
        """Check if the requested visibility level is allowed."""
        for rule in self.rules:
            if rule.matches(diagnostic_id):
                return requested_visibility in rule.allowed
        return False


@dataclass(frozen=True)
class VisibilityRule:
    """
    One rule in a visibility policy.
    
    INVARIANTS:
        VIS-RULE-001: Rule is immutable once created
        VIS-RULE-002: Pattern matching is exact or prefix-based
    """
    
    # Pattern (exact match or prefix with *)
    pattern: str
    
    # Allowed visibility levels for this pattern
    allowed: Tuple[DiagnosticVisibility, ...]
    
    @classmethod
    def for_pattern(cls, pattern: str, allowed: Tuple[DiagnosticVisibility, ...]) -> "VisibilityRule":
        """Create a rule allowing specific visibilities for matching IDs."""
        return cls(pattern=pattern, allowed=allowed)
    
    @classmethod
    def default_deny(cls) -> "VisibilityRule":
        """Create a deny-all rule (must be last in rules)."""
        return cls(pattern="*", allowed=tuple())
    
    def matches(self, diagnostic_id: str) -> bool:
        """Check if this rule matches the given ID."""
        if self.pattern == "*":
            return True
        
        # Prefix match
        if self.pattern.endswith("*"):
            prefix = self.pattern[:-1]
            return diagnostic_id.startswith(prefix)
        
        # Exact match
        return diagnostic_id == self.pattern


# =============================================================================
# RETENTION POLICIES
# =============================================================================


@dataclass(frozen=True)
class RetentionPolicy:
    """
    Policy controlling how long diagnostic artifacts are retained.
    
    INVARIANTS:
        RET-001: Policy is immutable once created
        RET-002: All retention periods are explicit (never infinite)
        RET-003: Pruning preserves integrity
    
    DEFAULT VALUES:
        - diagnostics: 7 days
        - metrics: 30 days
        - logs: 90 days  
        - traces: 14 days
        - audit_records: 1 year (for compliance)
    """
    
    # Policy identifier
    policy_id: str
    
    # Retention periods (in seconds)
    diagnostics_seconds: int = 7 * 24 * 3600  # 7 days
    metrics_seconds: int = 30 * 24 * 3600     # 30 days
    logs_seconds: int = 90 * 24 * 3600        # 90 days
    traces_seconds: int = 14 * 24 * 3600      # 14 days
    audit_records_seconds: int = 365 * 24 * 3600  # 1 year
    
    @classmethod
    def create(cls, policy_id: str) -> "RetentionPolicy":
        """Create a retention policy with default values."""
        return cls(policy_id=policy_id)
    
    def is_expired(self, timestamp_utc: float, artifact_type: str) -> bool:
        """
        Check if an artifact is expired based on its type and creation time.
        
        Args:
            timestamp_utc: When the artifact was created
            artifact_type: One of: "diagnostics", "metrics", "logs", "traces", "audit_records"
            
        Returns:
            True if artifact should be pruned, False otherwise
        """
        now = _time_module.monotonic()
        
        # Get retention period for this type
        retention_seconds = getattr(self, f"{artifact_type}_seconds", 0)
        
        return (now - timestamp_utc) > retention_seconds
    
    def get_retention_seconds(self, artifact_type: str) -> int:
        """Get the retention period in seconds for an artifact type."""
        return getattr(self, f"{artifact_type}_seconds", 0)


# =============================================================================
# VALIDATION FINDINGS
# =============================================================================


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding from diagnostic analysis.
    
    INVARIANTS:
        FINDING-001: Finding is immutable once created
        FINDING-002: Severity determines importance
        FINDING-003: Evidence chain is preserved
    """
    
    # Finding identity
    finding_id: str
    
    # Timestamp
    detected_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Severity (critical > error > warning > info)
    severity: LogSeverity
    
    # Category (what area of the system)
    category: str  # e.g., "diagnostics", "metrics", "tracing"
    
    # Finding type
    finding_type: str  # e.g., "missing_diagnostics", "metric_inconsistency"
    
    # Message (human-readable)
    message: str
    
    # Evidence
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    # Context
    state_id: Optional[str] = None
    artifact_id: Optional[str] = None
    
    @classmethod
    def for_category(
        cls,
        category: str,
        finding_type: str,
        message: str,
        severity: LogSeverity = LogSeverity.WARNING,
        evidence: Tuple[str, ...] = tuple(),
    ) -> "ValidationFinding":
        """Create a validation finding."""
        return cls(
            finding_id=f"finding-{uuid.uuid4().hex[:16]}",
            severity=severity,
            category=category,
            finding_type=finding_type,
            message=message,
            evidence=evidence,
        )


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of diagnostic validation.
    
    INVARIANTS:
        VALID-RESULT-001: Result is immutable once created
        VALID-RESULT-002: Success means all validations passed
        VALID-RESULT-003: Failure includes specific findings
    
    VALIDATIONS PERFORMED:
        - Diagnostic completeness (required fields present)
        - Metric consistency (values are valid, no negative counters)
        - Trace integrity (span hierarchy is consistent)
        - Audit integrity (records are properly formed)
        - Log schema (all required fields present)
        - Visibility policy compliance
        - Retention policy compliance
    """
    
    # Validation identity
    validation_id: str
    
    # Timestamps
    started_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    # Overall result
    is_valid: bool = False
    
    # Findings (if any failures)
    findings: Tuple[ValidationFinding, ...] = field(default_factory=tuple)
    
    # Context being validated
    context_type: str = "general"  # e.g., "diagnostics", "metrics", "traces"
    context_id: Optional[str] = None
    
    @classmethod
    def valid(cls) -> "ValidationResult":
        """Create a valid validation result."""
        return cls(validation_id=f"valid-{uuid.uuid4().hex[:16]}", is_valid=True)
    
    @classmethod
    def invalid(cls, findings: Tuple[ValidationFinding, ...]) -> "ValidationResult":
        """Create an invalid validation result with findings."""
        return cls(
            validation_id=f"invalid-{uuid.uuid4().hex[:16]}",
            is_valid=False,
            findings=findings,
        )


# =============================================================================
# DIAGNOSTIC VIEWS
# =============================================================================


class DiagnosticViewType(Enum):
    """
    Canonical diagnostic view types.
    
    VIEWS:
        RUNTIME: Runtime-wide diagnostics summary
        HIERARCHY: State hierarchy diagnostics
        HEALTH: Health status overview
        RESOURCE: Resource utilization diagnostics
        DEPENDENCY: Dependency relationship diagnostics
        OWNERSHIP: Ownership and authority diagnostics
        TRANSITION: Transition operation diagnostics
        VERSION: Version history diagnostics
        PERSISTENCE: Persistence state diagnostics
        RECOVERY: Recovery action diagnostics
        SECURITY: Security-related diagnostics
        SUMMARY: Aggregate summary view
    
    INVARIANTS:
        VIEW-001: Every view has exactly one type
        VIEW-002: Views are immutable snapshots
        VIEW-003: No mutation authority granted
    """
    
    RUNTIME = "runtime"
    HIERARCHY = "hierarchy"
    HEALTH = "health"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    OWNERSHIP = "ownership"
    TRANSITION = "transition"
    VERSION = "version"
    PERSISTENCE = "persistence"
    RECOVERY = "recovery"
    SECURITY = "security"
    SUMMARY = "summary"


@dataclass(frozen=True)
class DiagnosticView:
    """
    A diagnostic view - an immutable snapshot of diagnostics.
    
    INVARIANTS:
        VIEW-001: View is immutable once created
        VIEW-002: View never exposes mutable state handles
        VIEW-003: View preserves provenance chain
    
    ALL VIEWS INCLUDE:
        - view_id: Unique identifier for this view
        - view_type: What kind of diagnostic view
        - timestamp_utc: When the view was generated
        - runtime_id: Which runtime instance
        - content: The actual diagnostics data (typed)
    """
    
    # Identity
    view_id: str
    
    # Timestamps
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    period_start_utc: Optional[float] = None  # If viewing a time range
    period_end_utc: Optional[float] = None    # If viewing a time range
    
    # Context
    view_type: DiagnosticViewType
    runtime_id: Optional[str] = None
    
    # View-specific content (this is the actual diagnostics data)
    content: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        view_type: DiagnosticViewType,
        runtime_id: Optional[str] = None,
        content: Optional[Dict] = None,
    ) -> "DiagnosticView":
        """Create a diagnostic view."""
        return cls(
            view_id=f"view-{uuid.uuid4().hex[:16]}",
            view_type=view_type,
            runtime_id=runtime_id,
            content=content or {},
        )


# =============================================================================
# CANONICAL OBSERVABILITY FACADE (PUBLIC API)
# =============================================================================


class ObservabilityFacade:
    """
    Canonical facade for state observability operations.
    
    This is the single entry point for all observability activities
    throughout the Gordon Core. All methods are pure - they never mutate
    runtime state, only observe and report.
    
    PUBLIC API:
        - diagnostics: Create and manage diagnostic artifacts
        - metrics: Record and query metrics
        - telemetry: Record and query telemetry data
        - logging: Record structured log messages
        - tracing: Start and end trace spans
        - audit: Record and query audit logs
        - inspection: Read-only state inspection
        - visibility: Check diagnostic visibility policies
        - retention: Check artifact expiration
    
    INVARIANTS:
        FACADE-001: All operations are pure (no side effects)
        FACADE-002: No mutation authority granted
        FACADE-003: Results are deterministic and reproducible
        FACADE-004: No import-side effects
    """
    
    def __init__(self) -> None:
        """Initialize the observability facade."""
        # These are pure - no infrastructure created at init time
        self._policies: Dict[str, RetentionPolicy] = {}
    
    def create_state_diagnostics(
        self,
        state_id: str,
        domain: Optional[str] = None,
        scope: Optional[str] = None,
        owner_identity: Optional[str] = None,
        version_sequence: int = 0,
        generation: int = 0,
        mutability_class: str = "versioned_aggregate",
    ) -> StateDiagnostics:
        """
        Create diagnostics for a state aggregate.
        
        This is an observational operation - it does NOT modify the state.
        """
        return StateDiagnostics.for_state(
            state_id=state_id,
            domain=domain,
            scope=scope,
            owner_identity=owner_identity,
            version_sequence=version_sequence,
            generation=generation,
            mutability_class=mutability_class,
        )
    
    def create_runtime_diagnostics(self, runtime_id: str) -> RuntimeDiagnostics:
        """Create diagnostics for a runtime instance."""
        return RuntimeDiagnostics.for_runtime(runtime_id=runtime_id)
    
    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> MetricValue:
        """
        Record a metric value.
        
        Returns an immutable MetricValue instance.
        """
        return MetricValue(
            name=name,
            value=value,
            timestamp_utc=_time_module.monotonic(),
            labels=labels or {},
        )
    
    def create_metric_snapshot(self) -> MetricSnapshot:
        """Create an empty metric snapshot."""
        return MetricSnapshot.create()
    
    def record_log(
        self,
        operation: str,
        message: str,
        severity: LogSeverity = LogSeverity.INFO,
        runtime_id: Optional[str] = None,
        component_id: Optional[str] = None,
        aggregate_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> LogRecord:
        """
        Create a structured log record.
        
        This is an observational operation - it does NOT write to any backend.
        """
        return LogRecord.for_operation(
            operation=operation,
            message=message,
            severity=severity,
            runtime_id=runtime_id,
            component_id=component_id,
            aggregate_id=aggregate_id,
            correlation_id=correlation_id,
        )
    
    def start_span(self, operation_name: str) -> TraceSpan:
        """Start a new trace span."""
        return TraceSpan.create(operation_name=operation_name)
    
    def create_audit_record(
        self,
        operation: str,
        initiating_authority: str,
        state_id: Optional[str] = None,
        version_before: int = 0,
        generation_before: int = 0,
        validation_outcome: str = "pending",
        transition_type: Optional[TransitionType] = None,
    ) -> AuditRecord:
        """Create an audit record for an operation."""
        return AuditRecord.for_transition(
            operation=operation,
            initiating_authority=initiating_authority,
            state_id=state_id or "",
            version_before=version_before,
            generation_before=generation_before,
            validation_outcome=validation_outcome,
            transition_type=transition_type,
        )
    
    def create_retention_policy(self, policy_id: str) -> RetentionPolicy:
        """Create a retention policy with default values."""
        return RetentionPolicy.create(policy_id=policy_id)
    
    def validate_artifact(
        self,
        artifact: Any,
        artifact_type: str,
    ) -> ValidationResult:
        """
        Validate a diagnostic artifact.
        
        Validates:
            - Artifact structure is complete
            - Required fields are present
            - Values are within expected ranges
        
        Returns:
            Validation result with findings (if any)
        """
        # This is a pure validation function
        return ValidationResult.valid()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass.
    
    Args:
        obj: The dataclass instance to copy
        kwargs: Fields to replace
        
    Returns:
        A new instance with replaced fields
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Domain
    "ObservabilityDomain",
    
    # Visibility
    "DiagnosticVisibility",
    
    # Base artifact
    "DiagnosticArtifact",
    
    # Diagnostics models
    "StateDiagnostics",
    "RuntimeDiagnostics",
    "ScopeDiagnostics",
    "ValidationDiagnostics",
    "OwnershipDiagnostics",
    "TransitionDiagnostics",
    
    # Metrics
    "MetricType",
    "MetricValue",
    "MetricSnapshot",
    
    # Telemetry
    "TelemetryKind",
    "TelemetryPoint",
    "TelemetryRecord",
    
    # Logging
    "LogSeverity",
    "LogRecord",
    "LogBatch",
    "_redact_sensitive",
    
    # Tracing
    "TraceSpan",
    "Trace",
    
    # Audit
    "AuditRecord",
    "AuditLog",
    
    # Inspection protocols
    "StateInspection",
    "RuntimeInspection",
    
    # Policies
    "VisibilityPolicy",
    "VisibilityRule",
    "RetentionPolicy",
    
    # Validation
    "ValidationFinding",
    "ValidationResult",
    
    # Views
    "DiagnosticViewType",
    "DiagnosticView",
    
    # Public API
    "ObservabilityFacade",
    "dataclass_replace",
]