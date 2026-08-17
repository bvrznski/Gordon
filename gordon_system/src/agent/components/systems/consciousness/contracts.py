# Gordon Phase 5.7.1-I: Consciousness Contracts
# ===============================================================================

"""
Canonical contracts and data structures for the Consciousness capability.

This module defines immutable, typed contracts that define the interface
between Consciousness and external systems:
    - Current context snapshots (published state)
    - Context transitions (state changes)
    - Contributions (proposals from external systems)
    - Projections (exposed views from external systems)
    - Queries (consumer access patterns)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
import uuid
from typing import Tuple, Dict, Any, Optional


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    return uuid.uuid4().hex[:8]


def _get_timestamp() -> float:
    """Get current UTC timestamp."""
    import time
    return time.time()


# =============================================================================
# CURRENT CONTEXT SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class CurrentContextSnapshot:
    """
    Immutable snapshot of the current agent-relative experiential context.
    
    This is the canonical publication of Consciousness - the complete,
    bounded representation of what is currently present in the agent's
    experiential field at a point in time.
    
    Snapshot properties:
        - Immutable: Once created, never modified
        - Bounded: All collections have capacity limits
        - Deterministic: Same inputs produce identical snapshots
        - Versioned: Each snapshot has a strictly increasing generation
    
    NOT included (owned by external systems):
        - Full content of extensions (only references)
        - Runtime state (threads, queues, locks)
        - Private memory payloads
        - Hidden reasoning chains
    """
    
    # Identity and revisioning
    context_id: str = field(default_factory=lambda: f"context-{_generate_uuid()}")
    """Unique identifier for the logical context."""
    
    generation: int = 0
    """Current generation number (strictly monotonic)."""
    
    previous_generation: int = 0
    """Previous generation number (for lineage tracking)."""
    
    schema_version: str = "5.7.1"
    """Schema version for compatibility tracking."""
    
    # Timestamps
    created_at_utc: float = field(default_factory=_get_timestamp)
    """When this snapshot was created."""
    
    transition_id: Optional[str] = None
    """Transition that produced this snapshot (if any)."""
    
    # Extension references (by identity, not full content)
    field_reference: Optional[str] = None
    """Reference to experiential field snapshot (Phase 5.7.2)."""
    
    intentional_context_reference: Optional[str] = None
    """Reference to intentional context snapshot (Phase 5.7.3)."""
    
    temporal_context_reference: Optional[str] = None
    """Reference to temporal context snapshot (Phase 5.7.4)."""
    
    presence_reference: Optional[str] = None
    """Reference to presence state snapshot (Phase 5.7.5)."""
    
    awareness_reference: Optional[str] = None
    """Reference to awareness state snapshot (Phase 5.7.5)."""
    
    perspective_reference: Optional[str] = None
    """Reference to perspective state snapshot (Phase 5.7.6)."""
    
    situated_world_reference: Optional[str] = None
    """Reference to situated world snapshot (Phase 5.7.7)."""
    
    # Summary information (bounded)
    source_summary: Dict[str, str] = field(default_factory=dict)
    """Summary of registered sources."""
    
    privacy_summary: str = "internal"
    """Overall privacy classification of this context."""
    
    trust_summary: str = "medium"
    """Overall trust classification of this context."""
    
    degradation_state: Tuple[str, ...] = field(default_factory=tuple)
    """Current degradation modes (if any)."""
    
    health_state: str = "active"
    """Current health state of Consciousness capability."""
    
    provenance: Optional[str] = None
    """Provenance information for this snapshot."""
    
    @classmethod
    def initial(cls) -> "CurrentContextSnapshot":
        """
        Create an initial current context snapshot.
        
        This creates a clean starting point with minimal content and
        zero generations, suitable for first use or restart scenarios.
        """
        return cls(
            context_id="context-initial-001",
            generation=0,
            previous_generation=0,
            created_at_utc=_get_timestamp(),
            health_state="active",
            privacy_summary="internal",
            trust_summary="medium",
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if this snapshot has no extension references."""
        return all(ref is None for ref in [
            self.field_reference,
            self.intentional_context_reference,
            self.temporal_context_reference,
            self.presence_reference,
            self.awareness_reference,
            self.perspective_reference,
            self.situated_world_reference,
        ])
    
    def with_generation(self, new_generation: int) -> "CurrentContextSnapshot":
        """Return a copy with the specified generation."""
        return dataclass_replace(self, generation=new_generation)
    
    def with_transitions(
        self,
        field_ref: Optional[str] = None,
        intentional_ref: Optional[str] = None,
        temporal_ref: Optional[str] = None,
        presence_ref: Optional[str] = None,
        awareness_ref: Optional[str] = None,
        perspective_ref: Optional[str] = None,
        situated_world_ref: Optional[str] = None,
    ) -> "CurrentContextSnapshot":
        """Return a copy with updated extension references."""
        return dataclass_replace(
            self,
            field_reference=field_ref,
            intentional_context_reference=intentional_ref,
            temporal_context_reference=temporal_ref,
            presence_reference=presence_ref,
            awareness_reference=awareness_ref,
            perspective_reference=perspective_ref,
            situated_world_reference=situated_world_ref,
        )
    
    def with_degradation(self, *modes: str) -> "CurrentContextSnapshot":
        """Return a copy with degradation modes."""
        return dataclass_replace(
            self,
            degradation_state=tuple(modes),
        )


# =============================================================================
# CURRENT CONTEXT REFERENCE
# =============================================================================

@dataclass(frozen=True)
class CurrentContextReference:
    """
    Lightweight reference to the current context without full payload.
    
    Used for quick queries and checks where the full snapshot is not needed.
    """
    
    context_id: str
    generation: int
    
    # Health information (bounded)
    health_state: str = "active"
    last_transition_id: Optional[str] = None


# =============================================================================
# CONTRIBUTION ENVELOPE
# =============================================================================

@dataclass(frozen=True)
class ContributionEnvelope:
    """
    Immutable envelope for contribution submissions.
    
    Contributions are proposals submitted by external systems to be
    considered for admission to the current context. They do not
    guarantee admission, awareness, truth, or persistence.
    
    Envelope properties:
        - Immutable: Once created, never modified
        - Self-contained: All required information included
        - Typed: Explicit kind and classification
        - Validated: Can be checked for validity before processing
    
    NOT guaranteed by contribution:
        - Admission to current context
        - Awareness in experiential field
        - Truth or validity of content
        - Persistence across generations
        - Trust status
        - Action authority
    """
    
    # Identity
    contribution_id: str = field(default_factory=lambda: f"contrib-{_generate_uuid()}")
    """Unique identifier for this contribution."""
    
    source_generation: int = 0
    """Generation of the source at time of submission."""
    
    source_id: str = ""
    """Source submitting the contribution."""
    
    # Classification
    contribution_kind: str = "generic"
    """Type of contribution (workspace, perceptual, cognitive, etc.)."""
    
    privacy_classification: str = "internal"
    """Privacy classification of this contribution."""
    
    trust_classification: str = "untrusted"
    """Trust classification of this contribution."""
    
    # Payload reference
    payload_reference: Optional[str] = None
    """Reference to full payload (not embedded)."""
    
    # Target extension (if applicable)
    target_extension: Optional[str] = None
    """Target extension for this contribution (if any)."""
    
    # Timing and validity
    freshness_utc: float = field(default_factory=_get_timestamp)
    """When this contribution was created."""
    
    expiration_utc: Optional[float] = None
    """When this contribution expires (if any)."""
    
    # Tracking
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID for tracking chain."""
    
    submitted_at_utc: float = field(default_factory=_get_timestamp)
    """When this contribution was submitted to Consciousness."""
    
    def is_expired(self, current_time_utc: Optional[float] = None) -> bool:
        """Check if this contribution has expired."""
        if self.expiration_utc is None:
            return False
        if current_time_utc is None:
            current_time_utc = _get_timestamp()
        return current_time_utc > self.expiration_utc
    
    def with_correlation(self, correlation_id: str) -> "ContributionEnvelope":
        """Return a copy with correlation ID set."""
        return dataclass_replace(self, correlation_id=correlation_id)


# =============================================================================
# PROJECTION ENVELOPE
# =============================================================================

@dataclass(frozen=True)
class ProjectionEnvelope:
    """
    Immutable envelope for projection submissions from external systems.
    
    Projections expose bounded views from canonical external owners to be
    considered as inputs to the current context. They do not mutate
    Consciousness state directly.
    
    Envelope properties:
        - Immutable: Once created, never modified
        - Bounded view: Only exposes necessary information
        - Typed: Explicit kind and classification
        - Versioned: Supports versioned projections
    
    Projections from canonical owners:
        - Perception: Integrated perceptual results
        - Working Memory: Active task items
        - Workspace: Globally available candidates
        - Personality: Durable preferences
        - Motivation: Active goals and drives
        - Cognition: Interpretation proposals
    """
    
    # Identity (required fields first)
    source_id: str
    """Source generating the projection."""
    
    projection_id: str = field(default_factory=lambda: f"proj-{_generate_uuid()}")
    """Unique identifier for this projection."""
    
    source_generation: int = 0
    """Generation of the source at time of projection."""
    
    # Classification
    projection_kind: str = "generic"
    """Type of projection (perceptual, cognitive, personality, etc.)."""
    
    privacy_classification: str = "internal"
    """Privacy classification of this projection."""
    
    trust_classification: str = "medium"
    """Trust classification of this projection."""
    
    # Validity window
    valid_from_utc: float = field(default_factory=_get_timestamp)
    """When this projection becomes valid."""
    
    expires_at_utc: Optional[float] = None
    """When this projection expires (if any)."""
    
    # Payload reference
    payload_reference: Optional[str] = None
    """Reference to full payload (not embedded)."""
    
    compatibility_version: str = "5.7.1"
    """Compatibility version for this projection type."""
    
    provenance: Optional[str] = None
    """Provenance information for this projection."""
    
    def is_expired(self, current_time_utc: Optional[float] = None) -> bool:
        """Check if this projection has expired."""
        if self.expires_at_utc is None:
            return False
        if current_time_utc is None:
            current_time_utc = _get_timestamp()
        return current_time_utc > self.expires_at_utc
    
    def with_validity_window(
        self,
        valid_from: Optional[float] = None,
        expires_at: Optional[float] = None,
    ) -> "ProjectionEnvelope":
        """Return a copy with updated validity window."""
        return dataclass_replace(
            self,
            valid_from_utc=valid_from if valid_from is not None else self.valid_from_utc,
            expires_at_utc=expires_at if expires_at is not None else self.expires_at_utc,
        )


# =============================================================================
# CONTEXT TRANSITION
# =============================================================================

@dataclass(frozen=True)
class ContextTransition:
    """
    Immutable record of a context transition commit.
    
    Transitions represent the atomic commitment of a new current-context
    generation. They preserve all relevant information for audit and
    recovery while maintaining atomic publication guarantees.
    
    Transition properties:
        - Immutable: Once committed, never modified
        - Atomic: Either fully committed or not at all
        - Deterministic: Same inputs produce same outputs
        - Bounded: All collections have capacity limits
    
    A failed transition must preserve the previous valid snapshot and never
    expose partially updated state.
    """
    
    # Identity (required fields first - no defaults before defaults)
    context_id: str
    """Context ID being transitioned."""
    
    previous_generation: int
    """Generation before this transition."""
    
    new_generation: int
    """New generation after this transition."""
    
    transition_id: str = field(default_factory=lambda: f"transition-{_generate_uuid()}")
    """Unique identifier for this transition."""
    
    # Timing
    started_at_utc: float = field(default_factory=_get_timestamp)
    """When transition was initiated."""
    
    committed_at_utc: float = field(default_factory=_get_timestamp)
    """When transition was committed."""
    
    # Trigger and metadata
    trigger: str = "internal"
    """What triggered this transition (internal, external, manual)."""
    
    extension_transition_refs: Dict[str, str] = field(default_factory=dict)
    """Extension snapshot references included in this transition."""
    
    updated_extension_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Extensions that were updated."""
    
    unchanged_extension_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Extensions that remained unchanged."""
    
    degradation_changes: Tuple[str, ...] = field(default_factory=tuple)
    """Changes to degradation state."""
    
    # Summary classifications
    privacy_summary: str = "internal"
    """Privacy classification of new context."""
    
    trust_summary: str = "medium"
    """Trust classification of new context."""
    
    validation_warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any warnings during validation."""
    
    provenance: Optional[str] = None
    """Provenance information for this transition."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID for tracking chain."""
    
    status: str = "completed"
    """Transition status (pending, validating, committing, completed, rolled_back)."""
    
    @classmethod
    def initial(cls, context_id: str) -> "ContextTransition":
        """
        Create an initial transition for the first context generation.
        
        This creates a transition from generation 0 to generation 1
        for a new context.
        """
        return cls(
            context_id=context_id,
            previous_generation=0,
            new_generation=1,
            started_at_utc=_get_timestamp(),
            committed_at_utc=_get_timestamp(),
            status="completed",
        )


# =============================================================================
# TRANSITION RESULT
# =============================================================================

@dataclass(frozen=True)
class TransitionResult:
    """
    Result of a transition operation.
    
    This represents the outcome of attempting to commit a new context
    generation. It includes success/failure information and partial
    outcomes where applicable.
    """
    
    # Identity
    transition_id: str
    
    # Outcome
    succeeded: bool = False
    """Whether the transition succeeded."""
    
    status: str = "pending"
    """Final status of the transition."""
    
    # New state (if successful)
    new_context_snapshot: Optional[CurrentContextSnapshot] = None
    """New current context snapshot (if committed)."""
    
    new_generation: int = 0
    """New generation number (if successful)."""
    
    # Partial outcomes
    partial_success: bool = False
    """Whether this was a partial success."""
    
    degraded_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Degradation modes if partially successful."""
    
    skipped_extensions: Tuple[str, ...] = field(default_factory=tuple)
    """Extensions that were skipped (optional)."""
    
    # Failure information
    failure_reason: Optional[str] = None
    """Reason for failure (if failed)."""
    
    @property
    def is_failed(self) -> bool:
        """Check if this result represents a failure."""
        return not self.succeeded
    
    @property
    def is_degraded(self) -> bool:
        """Check if this result represents degraded operation."""
        return self.partial_success


# =============================================================================
# QUERY REQUEST
# =============================================================================

@dataclass(frozen=True)
class QueryRequest:
    """
    Request for current context information.
    
    Queries are read-only operations that never mutate state. They may
    be filtered by consumer policy for privacy and trust boundaries.
    """
    
    # Identity
    query_id: str = field(default_factory=lambda: f"query-{_generate_uuid()}")
    """Unique identifier for this query."""
    
    # Mode
    mode: str = "current_composite_snapshot"
    """Query mode (reference, snapshot, health_only, diagnostics_only)."""
    
    # Filters
    consumer_id: Optional[str] = None
    """Consumer requesting the query (for filtering)."""
    
    min_generation: int = 0
    """Minimum acceptable generation."""
    
    exclude_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Sources to exclude from results."""
    
    # Timing
    request_time_utc: float = field(default_factory=_get_timestamp)
    """When this query was issued."""
    
    timeout_seconds: Optional[float] = None
    """Optional timeout for this query."""
    
    def with_min_generation(self, generation: int) -> "QueryRequest":
        """Return a copy with minimum generation set."""
        return dataclass_replace(self, min_generation=generation)
    
    def with_consumer(self, consumer_id: str) -> "QueryRequest":
        """Return a copy with consumer ID set."""
        return dataclass_replace(self, consumer_id=consumer_id)


# =============================================================================
# CONSUMER VIEW FILTER
# =============================================================================

@dataclass(frozen=True)
class ConsumerViewFilter:
    """
    Filter for consumer-specific context views.
    
    Consumer views may filter private content, restricted sources,
    untrusted material, and security-sensitive state according to
    policy-defined rules.
    """
    
    # Identity (required fields first)
    consumer_id: str
    """Consumer requesting the filtered view."""
    
    view_id: str = field(default_factory=lambda: f"view-{_generate_uuid()}")
    """Unique identifier for this consumer view."""
    
    # Filter criteria
    privacy_threshold: str = "internal"
    """Maximum privacy level to include (e.g., public, internal)."""
    
    trust_minimum: str = "untrusted"
    """Minimum trust level to include (e.g., untrusted, medium)."""
    
    exclude_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Source IDs to always exclude."""
    
    # Policy flags
    filter_private_content: bool = True
    """Whether to filter private content."""
    
    filter_untrusted: bool = False
    """Whether to filter untrusted content."""
    
    # Output control
    max_items: int = 100
    """Maximum items in filtered view."""
    
    include_provenance: bool = False
    """Whether to include provenance metadata."""
    
    def with_view_id(self, view_id: str) -> "ConsumerViewFilter":
        """Return a copy with view ID set."""
        return dataclass_replace(self, view_id=view_id)


# =============================================================================
# DIAGNOSTICS SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class DiagnosticsSnapshot:
    """
    Bounded diagnostics information for Consciousness capability.
    
    Diagnostics provide operational insights without exposing private
    or sensitive context content. They are safe for observability and
    monitoring systems.
    """
    
    # Identity
    capability_id: str = "consciousness-001"
    """Consciousness capability identity."""
    
    context_id: Optional[str] = None
    """Current context ID (if available)."""
    
    generation: int = 0
    """Current context generation."""
    
    age_seconds: float = 0.0
    """How long since last update."""
    
    # Registration counts
    registered_source_count: int = 0
    """Total registered sources."""
    
    active_source_count: int = 0
    """Sources currently active."""
    
    registered_extension_count: int = 0
    """Total registered extensions."""
    
    ready_extension_count: int = 0
    """Extensions currently ready."""
    
    # Transition history
    last_transition_id: Optional[str] = None
    """Last transition that completed."""
    
    last_transition_duration_seconds: float = 0.0
    """Duration of last transition."""
    
    last_transition_status: str = "completed"
    """Status of last transition."""
    
    pending_contribution_count: int = 0
    """Pending contributions waiting for processing."""
    
    # Health indicators
    degradation_state: Tuple[str, ...] = field(default_factory=tuple)
    """Current degradation modes."""
    
    privacy_summary: str = "internal"
    """Privacy classification of current context."""
    
    trust_summary: str = "medium"
    """Trust classification of current context."""
    
    lifecycle_state: str = "active"
    """Lifecycle state of Consciousness capability."""
    
    # Performance metrics
    query_count_1m: int = 0
    """Queries in last minute."""
    
    transition_count_1m: int = 0
    """Transitions in last minute."""
    
    error_count_1m: int = 0
    """Errors in last minute."""


# =============================================================================
# HEALTH SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class HealthSnapshot:
    """
    Bounded health information for Consciousness capability.
    
    Health reflects operational readiness, not context population.
    A populated context is not automatically healthy.
    An empty context may be valid during initialization or controlled operation.
    """
    
    # Identity
    capability_id: str = "consciousness-001"
    """Consciousness capability identity."""
    
    state: str = "active"
    """Current health state (ready, active, degraded, failed)."""
    
    last_update_utc: float = field(default_factory=_get_timestamp)
    """When this health snapshot was generated."""
    
    # Readiness indicators
    initialized: bool = False
    """Whether capability is initialized."""
    
    ready: bool = False
    """Whether capability is ready for operations."""
    
    active: bool = False
    """Whether capability is actively processing."""
    
    # Dependency status
    required_sources_ready: Tuple[str, ...] = field(default_factory=tuple)
    """Required sources that are ready."""
    
    optional_sources_available: Tuple[str, ...] = field(default_factory=tuple)
    """Optional sources that are available."""
    
    required_extensions_ready: Tuple[str, ...] = field(default_factory=tuple)
    """Required extensions that are ready."""
    
    # Failure information
    last_failure_category: Optional[str] = None
    """Category of last failure (if any)."""
    
    last_failure_timestamp: Optional[float] = None
    """Timestamp of last failure (if any)."""
    
    recovery_status: str = "none"
    """Current recovery status."""
    
    # Capacity
    pending_operations: int = 0
    """Number of pending operations."""
    
    max_capacity_reached: bool = False
    """Whether capacity limits have been reached."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "CurrentContextSnapshot",
    "CurrentContextReference",
    "ContributionEnvelope",
    "ProjectionEnvelope",
    "ContextTransition",
    "TransitionResult",
    "QueryRequest",
    "ConsumerViewFilter",
    "DiagnosticsSnapshot",
    "HealthSnapshot",
)


# =============================================================================
# INTENTIONAL CONTEXT REFERENCES (Phase 5.7.3-I)
# =============================================================================

@dataclass(frozen=True)
class IntentionalContextReference:
    """
    Reference to an intentional context from Consciousness contracts.
    
    External systems can reference intentional contexts using this contract
    without accessing the full internal state.
    """
    
    context_id: str
    """Intentional context ID."""
    
    generation: int = 0
    """Current generation of the intentional context."""
    
    timestamp_utc: float = field(default_factory=_get_timestamp)
    """Timestamp when reference was created."""


@dataclass(frozen=True)
class IntentionalContextTransitionRequest:
    """
    Request to transition an intentional context.
    
    External systems (perception, memory, reasoning) propose transitions
    by submitting these requests. Only the canonical Intentional Context
    Engine validates and publishes them.
    """
    
    context_id: str
    """Intentional context ID being transitioned."""
    
    previous_generation: int
    """Previous generation before transition."""
    
    new_object_references: Tuple[str, ...] = field(default_factory=tuple)
    """New object references to add."""
    
    removed_object_references: Tuple[str, ...] = field(default_factory=tuple)
    """Object references to remove."""
    
    new_relation_references: Tuple[str, ...] = field(default_factory=tuple)
    """New relation references to add."""
    
    removed_relation_references: Tuple[str, ...] = field(default_factory=tuple)
    """Relation references to remove."""
    
    new_target_references: Tuple[str, ...] = field(default_factory=tuple)
    """New target references to add."""
    
    removed_target_references: Tuple[str, ...] = field(default_factory=tuple)
    """Target references to remove."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID for tracking chain."""
    
    trigger: str = "external"
    """What triggered this transition."""


@dataclass(frozen=True)
class IntentionalContextQuery:
    """
    Query for intentional context state.
    
    External systems can query intentional context using these contracts
    without accessing the full internal state.
    """
    
    context_id: Optional[str] = None
    """Intentional context ID (None = all contexts)."""
    
    object_filter: Tuple[str, ...] = field(default_factory=tuple)
    """Object IDs to filter for."""
    
    relation_filter: Tuple[str, ...] = field(default_factory=tuple)
    """Relation kinds to filter for."""
    
    target_status_filter: Tuple[str, ...] = field(default_factory=tuple)
    """Target status values to filter for."""
    
    max_results: int = 100
    """Maximum number of results to return."""


__all__: tuple[str, ...] = (
    "CurrentContextSnapshot",
    "ContextTransition",
    "ContributionProposal",
    "ProjectionRequest",
    "ConsumerViewFilter",
    "QueryRequest",
    "IntentionalContextReference",
    "IntentionalContextTransitionRequest",
    "IntentionalContextQuery",
)
