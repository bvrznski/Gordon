# Interaction Observability & Diagnostics Architecture - Phase 3.14.16
# ================================================================================
#
# Canonical architectural model for observability and diagnostics of every
# interaction within Gordon.
#
# This module establishes immutable contracts governing:
#   - Diagnostic record structure (immutable, traceable, correlated)
#   - Observation layer (never influences execution semantics)
#   - Correlation system (repository-wide relationship tracing)
#   - Provenance tracking (preserves origin and lineage)
#   - Diagnostic lifecycle (Created → Published → Correlated → Analyzed → Archived)
#   - Architectural metrics (observational, never modifies behavior)
#   - Traceability (complete reconstruction of interaction history)
#   - Replay diagnostics (exact reproduction of observed execution)
#   - Certification diagnostics (verification of diagnostic integrity)

"""
Interaction Observability & Diagnostics Architecture - Phase 3.14.16

Canonical model for observability and diagnostics of every interaction
within Gordon.

Observability Principles:
    - Every Interaction shall be fully observable
    - Observation shall never influence execution semantics
    - Diagnostic Records are immutable
    - Correlation identifiers remain immutable
    - Provenance is preserved throughout lifecycle
    - Integrity verification is deterministic

Architectural Model:

    Interaction
            │
            ▼
    Observation
            │
            ▼
    Diagnostic Record
            │
            ▼
    Correlation
            │
            ▼
    Analysis
            │
            ▼
    Certification

Observation produces Diagnostics.
Diagnostics enable Analysis.
Analysis enables Certification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    FrozenSet,
    Callable,
)
from enum import Enum, auto
import uuid
import time
import hashlib


# =============================================================================
# DIAGNOSTIC IDENTITY - Immutable Unique Identifiers
# =============================================================================


class DiagnosticIdType(Enum):
    """Categories of diagnostic identifiers."""
    DIAGNOSTIC = "diagnostic"
    OBSERVATION = "observation"
    CORRELATION = "correlation"
    PROVENANCE = "provenance"
    CERTIFICATION = "certification"


@dataclass(frozen=True, slots=True)
class DiagnosticId:
    """
    Immutable unique identifier for a diagnostic record.
    
    Identity Invariants:
        - D-001: Every diagnostic has exactly one unique identity
        - D-002: Identity is immutable once created
        - D-003: No two diagnostics share the same identity
        - D-004: Identity does not change during lifecycle transitions
    """
    
    value: str  # Unique identifier string (UUID-based)
    
    @classmethod
    def generate(cls) -> "DiagnosticId":
        """Generate a new unique diagnostic ID."""
        return cls(value=f"diag_{uuid.uuid4().hex[:24]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ObservationId:
    """
    Immutable identifier for an observation event.
    
    Every observation shall have a unique ID that traces back to
    its source interaction and diagnostic record.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "ObservationId":
        """Generate a new unique observation ID."""
        return cls(value=f"obs_{uuid.uuid4().hex[:24]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CorrelationId:
    """
    Immutable correlation identifier for tracking relationships.
    
    Correlation identifiers shall remain immutable throughout their lifecycle.
    They enable repository-wide tracing of diagnostic relationships.
    """
    
    value: str
    kind: DiagnosticIdType = DiagnosticIdType.CORRELATION
    
    @classmethod
    def generate(cls) -> "CorrelationId":
        """Generate a new unique correlation ID."""
        return cls(value=f"corr_{uuid.uuid4().hex[:24]}", kind=DiagnosticIdType.CORRELATION)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# DIAGNOSTIC RECORD - Immutable Diagnostic Container
# =============================================================================


class DiagnosticSeverity(Enum):
    """
    Canonical severity levels for diagnostic records.
    
    Severity is observational only and shall never influence execution semantics.
    """
    
    TRACE = "trace"         # Detailed low-level information
    DEBUG = "debug"         # Debugging information
    INFO = "info"           # General informational message
    NOTICE = "notice"       # Normal but significant condition
    WARNING = "warning"     # Warning conditions
    ERROR = "error"         # Error events that may allow continuation
    CRITICAL = "critical"   # Critical errors causing termination
    FATAL = "fatal"         # Fatal errors requiring immediate shutdown


class DiagnosticCategory(Enum):
    """
    Canonical categories for diagnostic classification.
    
    Categories define the type of diagnostic without influencing execution.
    """
    
    # Interaction lifecycle
    INTERACTION_CREATED = "interaction_created"
    INTERACTION_STARTED = "interaction_started"
    INTERACTION_COMPLETED = "interaction_completed"
    INTERACTION_TERMINATED = "interaction_terminated"
    
    # Execution lifecycle
    EXECUTION_REQUESTED = "execution_requested"
    EXECUTION_SCHEDULED = "execution_scheduled"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_RESUMED = "execution_resumed"
    EXECUTION_SUSPENDED = "execution_suspended"
    EXECUTION_COMPLETED = "execution_completed"
    
    # Stream lifecycle
    STREAM_PUBLISHED = "stream_published"
    STREAM_CONSUMED = "stream_consumed"
    STREAM_REPLAYED = "stream_replayed"
    STREAM_COMMITTED = "stream_committed"
    STREAM_ROLLED_BACK = "stream_rolled_back"
    
    # Network lifecycle
    NETWORK_ACTIVATED = "network_activated"
    NETWORK_DEACTIVATED = "network_deactivated"
    NETWORK_ERROR = "network_error"
    
    # Capability lifecycle
    CAPABILITY_INVOKED = "capability_invoked"
    CAPABILITY_COMPLETED = "capability_completed"
    CAPABILITY_FAILED = "capability_failed"
    
    # System state changes
    SYSTEM_STATE_CHANGED = "system_state_changed"
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    SYSTEM_ERROR = "system_error"


@dataclass(frozen=True, slots=True)
class DiagnosticRecord:
    """
    Immutable diagnostic record containing all observable information.
    
    Every Diagnostic Record shall define:
        - diagnostic identifier (unique, immutable)
        - interaction identifier (source of this diagnostic)
        - execution identifier (execution context)
        - stream identifier (stream context, if applicable)
        - network identifier (network context, if applicable)
        - capability identifier (capability context, if applicable)
        - system identifier (owning system)
        - timestamps (creation and lifecycle events)
        - lifecycle snapshot (state at time of observation)
        - integrity status (verification state)
        - severity (impact level)
        - outcome (result classification)
    
    Diagnostic Records are immutable.
    Updates shall create new Records rather than modifying existing ones.
    """
    
    # Identity fields
    diagnostic_id: str                      # Unique diagnostic identifier
    interaction_id: Optional[str] = None    # Source interaction ID
    execution_id: Optional[str] = None      # Execution context ID
    stream_id: Optional[str] = None         # Stream context ID
    network_id: Optional[str] = None        # Network context ID
    capability_id: Optional[str] = None     # Capability context ID
    system_id: str = ""                     # Owning system ID
    
    # Timestamps (all UTC epoch seconds) - defaults after non-default fields
    created_at_utc: float = field(default_factory=time.monotonic)  # When diagnostic was first recorded
    observed_at_utc: Optional[float] = None  # When observation occurred
    published_at_utc: Optional[float] = None  # When published to streams
    correlated_at_utc: Optional[float] = None  # When correlation completed
    archived_at_utc: Optional[float] = None   # When archived
    
    # Lifecycle snapshot (state at time of observation) - defaults after all timestamp fields
    lifecycle_state: str = "unknown"        # Current lifecycle state name
    lifecycle_snapshot: Dict[str, Any] = field(default_factory=dict)  # Full state snapshot as dict
    
    # Integrity and verification - defaults for fields after timestamp fields
    integrity_hash: str = ""                # SHA256 hash of record content (empty = computed in __post_init__)
    integrity_status: str = "verified"      # Verification status
    
    # Diagnostic metadata
    severity: DiagnosticSeverity = DiagnosticSeverity.INFO
    category: DiagnosticCategory = DiagnosticCategory.INTERACTION_CREATED
    
    # Outcome classification
    outcome: str = "success"                # success, failure, error, timeout, etc.
    
    # Metadata for analysis
    tags: Tuple[str, ...] = field(default_factory=tuple)  # Classification tags
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    # Correlation chain (immutable lineage)
    correlation_chain: Tuple[str, ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Compute integrity hash after initialization."""
        if not self.integrity_hash:
            object.__setattr__(
                self,
                "integrity_hash",
                self._compute_integrity_hash()
            )
    
    @classmethod
    def create(
        cls,
        interaction_id: Optional[str],
        system_id: str,
        lifecycle_state: str,
        lifecycle_snapshot: Dict[str, Any],
        severity: DiagnosticSeverity = DiagnosticSeverity.INFO,
        category: DiagnosticCategory = DiagnosticCategory.INTERACTION_CREATED,
        outcome: str = "success",
        context: Optional[Dict[str, Any]] = None,
    ) -> "DiagnosticRecord":
        """
        Create a new diagnostic record.
        
        This is the canonical factory method for creating diagnostic records.
        All fields are populated with appropriate defaults and computed values.
        """
        created_at = time.time()
        # Capture the interaction_id for hash computation (use provided or None)
        hash_interaction_id = interaction_id
        
        content_for_hash = cls._content_for_hash(
            interaction_id=hash_interaction_id,
            system_id=system_id,
            lifecycle_state=lifecycle_state,
            lifecycle_snapshot=lifecycle_snapshot,
            severity=severity.value,
            category=category.value,
            outcome=outcome,
            context=context or {},
        )
        
        return cls(
            diagnostic_id=DiagnosticId.generate().value,
            interaction_id=interaction_id,
            system_id=system_id,
            created_at_utc=created_at,
            observed_at_utc=created_at,
            lifecycle_state=lifecycle_state,
            lifecycle_snapshot=lifecycle_snapshot,
            integrity_hash=hashlib.sha256(content_for_hash.encode()).hexdigest(),
            severity=severity,
            category=category,
            outcome=outcome,
            context=context or {},
        )
    
    @staticmethod
    def _content_for_hash(
        interaction_id: Optional[str],
        system_id: str,
        lifecycle_state: str,
        lifecycle_snapshot: Dict[str, Any],
        severity: str,
        category: str,
        outcome: str,
        context: Dict[str, Any],
    ) -> str:
        """Generate content string for hash computation."""
        snapshot_str = str(sorted(lifecycle_snapshot.items()))
        return (
            f"{interaction_id}|{system_id}|{lifecycle_state}|"
            f"{snapshot_str}|{severity}|{category}|{outcome}|{sorted(context.items())}"
        )
    
    def with_lifecycle_transition(self, new_state: str) -> "DiagnosticRecord":
        """
        Create a new record with updated lifecycle state.
        
        This creates a NEW diagnostic record rather than modifying the existing one,
        preserving immutability and enabling replay of the full lifecycle.
        """
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            published_at_utc=time.time(),
        )
    
    def mark_published(self) -> "DiagnosticRecord":
        """Mark this diagnostic as published to streams."""
        return dataclass_replace(
            self,
            published_at_utc=time.time(),
        )
    
    def mark_correlated(self, correlation_chain: Tuple[str, ...]) -> "DiagnosticRecord":
        """
        Mark this diagnostic as correlated with correlation chain.
        
        The correlation chain is immutable and preserves the lineage of
        correlation relationships.
        """
        return dataclass_replace(
            self,
            correlated_at_utc=time.time(),
            correlation_chain=correlation_chain,
        )
    
    def mark_archived(self) -> "DiagnosticRecord":
        """Mark this diagnostic as archived."""
        return dataclass_replace(
            self,
            archived_at_utc=time.time(),
        )
    
    def with_tag(self, tag: str) -> "DiagnosticRecord":
        """Create a new record with an additional tag."""
        return dataclass_replace(
            self,
            tags=self.tags + (tag,)
        )
    
    def verify_integrity(self) -> bool:
        """
        Verify the integrity of this diagnostic record.
        
        Returns True if the current hash matches the computed hash,
        indicating the record has not been modified.
        """
        expected_hash = self._compute_integrity_hash()
        return self.integrity_hash == expected_hash
    
    def _compute_integrity_hash(self) -> str:
        """Compute integrity hash from record content."""
        content = self._content_for_hash(
            interaction_id=self.interaction_id,
            system_id=self.system_id,
            lifecycle_state=self.lifecycle_state,
            lifecycle_snapshot=dict(self.lifecycle_snapshot),
            severity=self.severity.value,
            category=self.category.value,
            outcome=self.outcome,
            context=dict(self.context),
        )
        return hashlib.sha256(content.encode()).hexdigest()


# =============================================================================
# OBSERVATION LAYER - Non-intrusive Observation Interface
# =============================================================================


class ObservationMode(Enum):
    """
    Modes of observation for interactions.
    
    Observation mode determines the depth and type of observability applied,
    but never influences execution semantics.
    """
    
    NONE = "none"              # No observation (for performance testing)
    LIGHT = "light"            # Minimal observation (IDs only)
    STANDARD = "standard"      # Standard observation (full lifecycle)
    VERBOSE = "verbose"        # Verbose observation (all details)
    FULL = "full"              # Full observation (complete state snapshots)


@dataclass(frozen=True, slots=True)
class ObservationContext:
    """
    Context for an observation event.
    
    Observation context captures metadata about the observation itself,
    separate from the observed interaction.
    """
    
    observer_id: str                        # Which observer made this?
    mode: ObservationMode                   # Observation mode used
    timestamp_utc: float                    # When observation occurred
    duration_ms: Optional[float] = None     # Observation duration (if measured)
    sample_rate: float = 1.0                # Sample rate (for probabilistic sampling)


@dataclass(frozen=True, slots=True)
class Observation:
    """
    Immutable observation of an interaction.
    
    Every architectural Interaction shall be observable.
    Observation shall preserve:
        - identity
        - provenance
        - timestamps
        - execution context
        - interaction category
        - lifecycle state
        - ownership
        - authority decisions
    
    Observation shall never alter execution.
    """
    
    observation_id: str                     # Unique observation identifier
    diagnostic_record: DiagnosticRecord     # The diagnostic being observed
    observation_context: ObservationContext # Context of the observation itself
    
    @classmethod
    def from_diagnostic(
        cls,
        diagnostic: DiagnosticRecord,
        observer_id: str,
        mode: ObservationMode = ObservationMode.STANDARD,
    ) -> "Observation":
        """Create an observation from a diagnostic record."""
        return cls(
            observation_id=ObservationId.generate().value,
            diagnostic_record=diagnostic,
            observation_context=ObservationContext(
                observer_id=observer_id,
                mode=mode,
                timestamp_utc=time.time(),
            ),
        )


# =============================================================================
# CORRELATION SYSTEM - Repository-wide Relationship Tracing
# =============================================================================


class CorrelationType(Enum):
    """
    Types of correlation relationships between diagnostics.
    
    Correlation types define the semantic relationship between diagnostic records.
    """
    
    # Identity-based correlations
    SAME_INTERACTION = "same_interaction"       # Same interaction, different states
    SAME_EXECUTION = "same_execution"           # Same execution context
    
    # Causal correlations
    DIRECTLY_CAUSES = "directly_causes"         # Direct causal relationship
    INDIRECTLY_CAUSES = "indirectly_causes"     # Indirect causal relationship
    
    # Temporal correlations
    BEFORE = "before"                           # Occurred before
    AFTER = "after"                             # Occurred after
    CONCURRENT_WITH = "concurrent_with"         # Occurred concurrently
    
    # Hierarchical correlations
    PARENT_OF = "parent_of"                     # Parent-child relationship
    CHILD_OF = "child_of"                       # Child-parent relationship
    SUBPROCESS_OF = "subprocess_of"             # Subprocess relationship


@dataclass(frozen=True, slots=True)
class CorrelationEdge:
    """
    Immutable correlation relationship between two diagnostic records.
    
    Correlation edges enable tracing of relationships across the repository.
    """
    
    source_diagnostic_id: str               # From which diagnostic?
    target_diagnostic_id: str               # To which diagnostic?
    correlation_type: CorrelationType       # What kind of relationship?
    created_at_utc: float                   # When correlation established
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info


@dataclass(frozen=True, slots=True)
class CorrelationGraph:
    """
    Immutable graph of diagnostic correlations.
    
    Enables repository-wide correlation of diagnostics across all interactions.
    """
    
    graph_id: str                           # Unique graph identifier
    edges: Tuple[CorrelationEdge, ...]      # All correlation edges
    created_at_utc: float                   # When graph was created
    
    @classmethod
    def create_empty(cls) -> "CorrelationGraph":
        """Create an empty correlation graph."""
        return cls(
            graph_id=f"corr_graph_{uuid.uuid4().hex[:16]}",
            edges=tuple(),
            created_at_utc=time.time(),
        )
    
    def add_edge(
        self,
        source_diagnostic_id: str,
        target_diagnostic_id: str,
        correlation_type: CorrelationType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "CorrelationGraph":
        """Create a new graph with the added correlation edge."""
        edge = CorrelationEdge(
            source_diagnostic_id=source_diagnostic_id,
            target_diagnostic_id=target_diagnostic_id,
            correlation_type=correlation_type,
            created_at_utc=time.time(),
            metadata=metadata or {},
        )
        return dataclass_replace(
            self,
            edges=self.edges + (edge,),
        )
    
    def get_correlations(self, diagnostic_id: str) -> Tuple[CorrelationEdge, ...]:
        """Get all correlations involving a specific diagnostic."""
        return tuple(
            e for e in self.edges
            if e.source_diagnostic_id == diagnostic_id or e.target_diagnostic_id == diagnostic_id
        )
    
    def get_successors(self, diagnostic_id: str) -> Tuple[CorrelationEdge, ...]:
        """Get correlations where this diagnostic is the source."""
        return tuple(e for e in self.edges if e.source_diagnostic_id == diagnostic_id)
    
    def get_predecessors(self, diagnostic_id: str) -> Tuple[CorrelationEdge, ...]:
        """Get correlations where this diagnostic is the target."""
        return tuple(e for e in self.edges if e.target_diagnostic_id == diagnostic_id)


# =============================================================================
# PROVENANCE TRACKING - Origin and Lineage Preservation
# =============================================================================


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """
    Immutable provenance record preserving origin information.
    
    Every Diagnostic Record shall preserve provenance.
    Provenance shall include:
        - originating component
        - originating Interaction
        - execution context
        - architectural domain
        - creation timestamp
    
    Diagnostic provenance shall never be discarded.
    """
    
    # Origin information
    originating_component: str = ""         # Which component created this?
    originating_interaction_id: Optional[str] = None  # Source interaction (if any)
    originating_execution_id: Optional[str] = None    # Source execution (if any)
    
    # Context information - must have defaults after non-default fields
    architectural_domain: str = "unknown"   # e.g., "execution", "streams", "networks"
    timestamp_utc: float = field(default_factory=time.monotonic)  # When created
    
    # Ancestry chain
    ancestry_chain: Tuple[str, ...] = field(default_factory=tuple)  # Parent provenance IDs
    
    def with_ancestor(self, ancestor_id: str) -> "ProvenanceRecord":
        """Create a new record with an added ancestor."""
        return dataclass_replace(
            self,
            ancestry_chain=self.ancestry_chain + (ancestor_id,)
        )


@dataclass(frozen=True, slots=True)
class ProvenanceChain:
    """
    Immutable chain of provenance records.
    
    Enables full reconstruction of diagnostic origin and lineage.
    """
    
    chain_id: str                           # Unique chain identifier
    records: Tuple[ProvenanceRecord, ...]   # All provenance records in order
    
    @classmethod
    def create_root(cls, record: ProvenanceRecord) -> "ProvenanceChain":
        """Create a new provenance chain with root record."""
        return cls(
            chain_id=f"prov_{uuid.uuid4().hex[:16]}",
            records=(record,),
        )
    
    def append(self, record: ProvenanceRecord) -> "ProvenanceChain":
        """Append a record to this chain."""
        return dataclass_replace(
            self,
            records=self.records + (record.with_ancestor(self.chain_id),)
        )


# =============================================================================
# DIAGNOSTIC LIFECYCLE - Canonical State Transitions
# =============================================================================


class DiagnosticLifecycleState(Enum):
    """
    Canonical diagnostic lifecycle states.
    
    Lifecycle progression shall remain deterministic.
    
    Canonical lifecycle:
        Created → Published → Correlated → Analyzed → Archived
    """
    
    # Initial state
    CREATED = "created"                     # First recorded
    
    # Publication states
    PENDING_PUBLICATION = "pending_publication"
    PUBLISHED = "published"                 # Published to streams
    
    # Correlation states
    CORRELATING = "correlating"             # Currently being correlated
    CORRELATED = "correlated"               # Correlation complete
    
    # Analysis states
    ANALYZED = "analyzed"                   # Analysis completed
    
    # Final states
    ARCHIVED = "archived"                   # Permanently archived
    DELETED = "deleted"                     # Logically deleted (for compliance)


@dataclass(frozen=True, slots=True)
class DiagnosticLifecycleEvent:
    """
    Immutable event representing a lifecycle state transition.
    
    Lifecycle events enable complete reconstruction of diagnostic history.
    """
    
    event_id: str                           # Unique event identifier
    diagnostic_id: str                      # Which diagnostic?
    previous_state: DiagnosticLifecycleState  # State before transition
    new_state: DiagnosticLifecycleState     # State after transition
    occurred_at_utc: float                  # When transition occurred
    triggered_by: Optional[str] = None      # Who/what triggered this?
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info


@dataclass(frozen=True, slots=True)
class DiagnosticLifecycle:
    """
    Immutable lifecycle state machine for a diagnostic record.
    
    Tracks the complete progression of a diagnostic through its lifecycle.
    """
    
    diagnostic_id: str                      # Which diagnostic?
    current_state: DiagnosticLifecycleState # Current lifecycle state
    created_at_utc: float                   # When first created
    transitions: Tuple[DiagnosticLifecycleEvent, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, diagnostic_id: str) -> "DiagnosticLifecycle":
        """Create initial lifecycle state."""
        return cls(
            diagnostic_id=diagnostic_id,
            current_state=DiagnosticLifecycleState.CREATED,
            created_at_utc=time.time(),
        )
    
    def transition_to(self, new_state: DiagnosticLifecycleState, triggered_by: Optional[str] = None) -> "DiagnosticLifecycle":
        """
        Transition to a new lifecycle state.
        
        Returns a NEW lifecycle object with the transition recorded,
        preserving immutability and enabling replay.
        """
        event = DiagnosticLifecycleEvent(
            event_id=f"lifecycle_{uuid.uuid4().hex[:16]}",
            diagnostic_id=self.diagnostic_id,
            previous_state=self.current_state,
            new_state=new_state,
            occurred_at_utc=time.time(),
            triggered_by=triggered_by,
            metadata={},
        )
        
        return dataclass_replace(
            self,
            current_state=new_state,
            transitions=self.transitions + (event,),
        )
    
    def is_terminal(self) -> bool:
        """Check if this diagnostic has reached a terminal state."""
        return self.current_state in (
            DiagnosticLifecycleState.ARCHIVED,
            DiagnosticLifecycleState.DELETED,
        )


# =============================================================================
# ARCHITECTURAL METRICS - Observational Statistics
# =============================================================================


class MetricType(Enum):
    """
    Types of architectural metrics.
    
    Metrics shall remain observational.
    Metrics shall never alter execution behavior.
    """
    
    # Timing metrics (all in milliseconds)
    INTERACTION_LATENCY = "interaction_latency"
    EXECUTION_LATENCY = "execution_latency"
    SCHEDULING_LATENCY = "scheduling_latency"
    ADMISSION_LATENCY = "admission_latency"
    
    # Throughput metrics
    STREAM_THROUGHPUT = "stream_throughput"      # Events per second
    NETWORK_ACTIVATION_RATE = "network_activation_rate"  # Activations per second
    
    # Utilization metrics
    CAPABILITY_UTILIZATION = "capability_utilization"  # Fraction of time busy
    SYSTEM_REQUEST_RATE = "system_request_rate"        # Requests per second
    
    # Duration metrics (all in milliseconds)
    TRANSACTION_DURATION = "transaction_duration"
    RECOVERY_DURATION = "recovery_duration"
    
    # Counters
    FAILURE_COUNT = "failure_count"
    SUCCESS_COUNT = "success_count"


@dataclass(frozen=True, slots=True)
class MetricPoint:
    """
    Immutable single metric observation.
    
    A metric point represents a single measurement at a point in time.
    """
    
    metric_type: MetricType                 # What type of metric?
    value: float                            # Measured value
    timestamp_utc: float                    # When measured
    labels: Dict[str, str] = field(default_factory=dict)  # Dimension labels


@dataclass(frozen=True, slots=True)
class MetricAggregation:
    """
    Immutable aggregated metrics.
    
    Aggregations summarize multiple metric points for analysis.
    """
    
    metric_type: MetricType                 # What type of metric?
    count: int                              # Number of samples
    sum: float                              # Sum of all values
    min: float                              # Minimum value
    max: float                              # Maximum value
    avg: float                              # Average value
    std_dev: Optional[float] = None         # Standard deviation (optional)
    
    @classmethod
    def from_points(cls, points: Tuple[MetricPoint, ...]) -> "MetricAggregation":
        """Create an aggregation from a set of metric points."""
        if not points:
            raise ValueError("Cannot aggregate empty set of points")
        
        values = [p.value for p in points]
        sum_val = sum(values)
        count = len(values)
        avg = sum_val / count
        
        # Calculate standard deviation if we have multiple points
        std_dev: Optional[float] = None
        if count > 1:
            variance = sum((v - avg) ** 2 for v in values) / (count - 1)
            std_dev = variance ** 0.5
        
        return cls(
            metric_type=points[0].metric_type,
            count=count,
            sum=sum_val,
            min=min(values),
            max=max(values),
            avg=avg,
            std_dev=std_dev,
        )


# =============================================================================
# TRACEABILITY - Complete Interaction Reconstruction
# =============================================================================


class TraceEventType(Enum):
    """
    Types of trace events for interaction reconstruction.
    
    Trace events enable complete reconstruction of:
        - initiation
        - routing
        - scheduling
        - execution
        - completion
        - publication
        - recovery
    """
    
    # Lifecycle events
    INITIATED = "initiated"
    ROUTED = "routed"
    SCHEDULED = "scheduled"
    EXECUTING = "executing"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    COMPLETED = "completed"
    
    # Publication events
    PUBLISHED = "published"
    SUBSCRIBED = "subscribed"
    
    # Recovery events
    RECOVERING = "recovering"
    RECOVERY_COMPLETE = "recovery_complete"


@dataclass(frozen=True, slots=True)
class TraceEvent:
    """
    Immutable trace event in the execution history.
    
    Trace events enable deterministic reconstruction of interaction history.
    """
    
    trace_id: str = ""                      # Correlation-wide trace ID
    timestamp_utc: float = field(default_factory=time.monotonic)  # When event occurred
    event_type: TraceEventType = TraceEventType.INITIATED  # What kind of event?
    interaction_id: Optional[str] = None    # Which interaction? (if applicable)
    execution_id: Optional[str] = None      # Which execution? (if applicable)
    component_id: str = ""                  # Which component?
    details: Dict[str, Any] = field(default_factory=dict)  # Event-specific data


@dataclass(frozen=True, slots=True)
class ExecutionTrace:
    """
    Immutable trace of an interaction's complete execution path.
    
    Enables reconstruction of the entire execution history for any interaction.
    """
    
    trace_id: str                           # Unique trace identifier
    events: Tuple[TraceEvent, ...]          # All trace events in order
    
    @classmethod
    def create(cls, trace_id: str) -> "ExecutionTrace":
        """Create a new empty execution trace."""
        return cls(trace_id=trace_id, events=tuple())
    
    def append(self, event: TraceEvent) -> "ExecutionTrace":
        """Append an event to this trace."""
        return dataclass_replace(
            self,
            events=self.events + (event,),
        )
    
    def get_events_by_type(self, event_type: TraceEventType) -> Tuple[TraceEvent, ...]:
        """Get all events of a specific type."""
        return tuple(e for e in self.events if e.event_type == event_type)
    
    def get_interactions_traced(self) -> Tuple[str, ...]:
        """Get all interaction IDs traced in this execution trace."""
        return tuple(
            e.interaction_id
            for e in self.events
            if e.interaction_id is not None
        )


# =============================================================================
# REPLAY DIAGNOSTICS - Exact Reproduction of Execution History
# =============================================================================


@dataclass(frozen=True, slots=True)
class ReplaySource:
    """
    Source specification for replay diagnostics.
    
    Replay shall preserve:
        - diagnostic ordering
        - correlation identifiers
        - provenance
        - timestamps
        - lifecycle progression
    
    Replay diagnostics shall exactly reproduce the observed execution history.
    """
    
    source_type: str                        # e.g., "database", "stream", "archive"
    source_id: str                          # Specific source identifier
    start_timestamp_utc: Optional[float] = None  # If replaying from time
    end_timestamp_utc: Optional[float] = None    # If replaying to time


@dataclass(frozen=True, slots=True)
class ReplayConfig:
    """
    Configuration for diagnostic replay.
    
    Replay configuration enables deterministic reproduction of execution history.
    """
    
    replay_id: str                          # Unique replay identifier
    source: ReplaySource                    # Where to get diagnostics from
    preserve_ordering: bool = True          # Preserve original event ordering?
    restore_timestamps: bool = True         # Restore original timestamps?
    include_correlations: bool = True       # Include correlation relationships?
    
    @classmethod
    def create(cls, source: ReplaySource) -> "ReplayConfig":
        """Create a default replay configuration."""
        return cls(
            replay_id=f"replay_{uuid.uuid4().hex[:16]}",
            source=source,
        )


@dataclass(frozen=True, slots=True)
class ReplayResult:
    """
    Result of a diagnostic replay operation.
    
    Captures the outcome and statistics of replaying diagnostics.
    """
    
    replay_id: str                          # Which replay?
    started_at_utc: float                   # When replay started
    completed_at_utc: float                 # When replay finished
    diagnostics_replayed: int               # Number of diagnostics replayed
    correlations_restored: int              # Number of correlation relationships restored
    errors_encountered: int                 # Number of errors during replay


# =============================================================================
# CERTIFICATION DIAGNOSTICS - Verification and Validation
# =============================================================================


class CertificationStatus(Enum):
    """
    Canonical certification status values.
    
    Certification diagnostics enable verification of diagnostic integrity.
    """
    
    PENDING = "pending"                     # Waiting for certification
    VERIFIED = "verified"                   # Integrity verified
    FAILED = "failed"                       # Integrity check failed
    ARCHIVED = "archived"                   # Archived (cannot be re-certified)


@dataclass(frozen=True, slots=True)
class CertificationRecord:
    """
    Immutable certification record for a diagnostic.
    
    Every Diagnostic Record shall be integrity-verifiable.
    Verification shall detect:
        - corruption
        - truncation
        - duplication
        - forgery
        - inconsistent lineage
    
    Integrity verification shall remain deterministic.
    """
    
    diagnostic_id: str                      # Which diagnostic?
    certification_status: CertificationStatus  # Current certification state
    verified_at_utc: Optional[float] = None  # When verified (if applicable)
    verifier_id: Optional[str] = None       # Who/what verified this?
    verification_data: Dict[str, Any] = field(default_factory=dict)  # Verification details
    
    @classmethod
    def create_pending(cls, diagnostic_id: str) -> "CertificationRecord":
        """Create a pending certification record."""
        return cls(
            diagnostic_id=diagnostic_id,
            certification_status=CertificationStatus.PENDING,
        )
    
    def mark_verified(self, verifier_id: str, verification_data: Optional[Dict[str, Any]] = None) -> "CertificationRecord":
        """Mark this diagnostic as verified."""
        return dataclass_replace(
            self,
            certification_status=CertificationStatus.VERIFIED,
            verified_at_utc=time.time(),
            verifier_id=verifier_id,
            verification_data=verification_data or {},
        )
    
    def mark_failed(self, reason: str) -> "CertificationRecord":
        """Mark this diagnostic certification as failed."""
        return dataclass_replace(
            self,
            certification_status=CertificationStatus.FAILED,
            verified_at_utc=time.time(),
            verification_data={"failure_reason": reason},
        )


# =============================================================================
# DIAGNOSTIC INTEGRITY - Verification and Validation
# =============================================================================


@dataclass(frozen=True, slots=True)
class IntegrityCheckResult:
    """
    Result of an integrity check on a diagnostic record.
    
    Integrity checks detect corruption, truncation, duplication,
    forgery, and inconsistent lineage.
    """
    
    is_valid: bool                          # Does the record pass all checks?
    checked_at_utc: float                   # When check was performed
    
    # Check details
    hash_match: bool = True                 # Content hash matches stored hash?
    lineage_consistent: bool = True         # Lineage is consistent?
    timestamp_ordering_valid: bool = True   # Timestamps are in valid order?
    
    # Failure reasons (if invalid)
    failure_reasons: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def passed(cls) -> "IntegrityCheckResult":
        """Create a passing result."""
        return cls(
            is_valid=True,
            checked_at_utc=time.time(),
            hash_match=True,
            lineage_consistent=True,
            timestamp_ordering_valid=True,
        )
    
    @classmethod
    def failed(cls, *reasons: str) -> "IntegrityCheckResult":
        """Create a failing result with one or more failure reasons."""
        return cls(
            is_valid=False,
            checked_at_utc=time.time(),
            hash_match=False,
            lineage_consistent=False,
            timestamp_ordering_valid=False,
            failure_reasons=reasons,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Simple dataclass replace implementation for frozen dataclasses.
    
    This function creates a new instance with updated fields while preserving
    immutability. It is used throughout the observability architecture to
    enable state transitions without modifying existing objects.
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Cannot replace fields on non-dataclass object: {type(obj)}")


def verify_diagnostic_integrity(record: DiagnosticRecord) -> IntegrityCheckResult:
    """
    Verify the integrity of a diagnostic record.
    
    Performs all integrity checks:
        - Hash verification
        - Timestamp ordering
        - Required field presence
    
    Returns an IntegrityCheckResult indicating pass/failure status.
    """
    failures = []
    
    # Check required fields are present
    if not record.diagnostic_id:
        failures.append("missing diagnostic_id")
    
    if not record.system_id:
        failures.append("missing system_id")
    
    if not record.lifecycle_state:
        failures.append("missing lifecycle_state")
    
    # Verify hash integrity
    actual_hash = record._compute_integrity_hash()
    if actual_hash != record.integrity_hash:
        failures.append(f"hash mismatch: expected {record.integrity_hash}, got {actual_hash}")
    
    # Check timestamp ordering (created <= observed)
    if record.observed_at_utc is not None and record.observed_at_utc < record.created_at_utc:
        failures.append("observed_at_utc cannot be before created_at_utc")
    
    if failures:
        return IntegrityCheckResult.failed(*failures)
    
    return IntegrityCheckResult.passed()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "DiagnosticIdType",
    "DiagnosticId",
    "ObservationId",
    "CorrelationId",
    
    # Diagnostic record (core model)
    "DiagnosticRecord",
    "DiagnosticSeverity",
    "DiagnosticCategory",
    
    # Observation layer
    "ObservationMode",
    "ObservationContext",
    "Observation",
    
    # Correlation system
    "CorrelationType",
    "CorrelationEdge",
    "CorrelationGraph",
    
    # Provenance tracking
    "ProvenanceRecord",
    "ProvenanceChain",
    
    # Diagnostic lifecycle
    "DiagnosticLifecycleState",
    "DiagnosticLifecycleEvent",
    "DiagnosticLifecycle",
    
    # Architectural metrics
    "MetricType",
    "MetricPoint",
    "MetricAggregation",
    
    # Traceability
    "TraceEventType",
    "TraceEvent",
    "ExecutionTrace",
    
    # Replay diagnostics
    "ReplaySource",
    "ReplayConfig",
    "ReplayResult",
    
    # Certification diagnostics
    "CertificationStatus",
    "CertificationRecord",
    
    # Integrity verification
    "IntegrityCheckResult",
    "verify_diagnostic_integrity",
    
    # Utilities
    "dataclass_replace",
]