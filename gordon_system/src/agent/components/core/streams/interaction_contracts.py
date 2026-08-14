# Stream Interaction Contracts - Phase 3.14.6
# ============================================
#
# Canonical relationship between Interactions and Semantic Streams.
#
# This module establishes immutable contracts governing how Interactions are
# published to, transported by, observed from, and replayed through Streams.
#

"""
Canonical Stream-Interaction Contracts for Gordon Phase 3.14.6

This module establishes immutable rules governing the relationship between
Interactions and Semantic Streams throughout the repository.

Core Principles:

* Streams transport.
* Interactions communicate.
* Execution schedules.

Streams and Interactions are orthogonal architectural concepts.

Streams never redefine Interaction semantics.
Interactions never redefine Stream semantics.

Both concepts preserve ownership, authority, and integrity.

Canonical Model:
    Execution → Interaction → Publication → Stream → Subscribers

Each step preserves the semantic meaning of the previous step.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, FrozenSet, Type, Union
from enum import Enum, auto
import uuid
import time

# Re-export interaction types for convenience
try:
    from ...architecture.interaction.taxonomy import (
        Interaction,
        Request,
        Response,
        Command,
        Event,
        Signal,
        Notification,
        Proposal,
        Observation,
        Query,
        Publication as TaxonomyPublication,
        Subscription as TaxonomySubscription,
        Checkpoint,
        Heartbeat,
        Synchronization,
        Transaction,
        Recovery,
        InteractionCategory,
        InteractionId,
        InteractionCorrelation,
        InteractionTrait,
    )
except ModuleNotFoundError:
    from gordon_system.src.agent.architecture.interaction.taxonomy import (
        Interaction,
        Request,
        Response,
        Command,
        Event,
        Signal,
        Notification,
        Proposal,
        Observation,
        Query,
        Publication as TaxonomyPublication,
        Subscription as TaxonomySubscription,
        Checkpoint,
        Heartbeat,
        Synchronization,
        Transaction,
        Recovery,
        InteractionCategory,
        InteractionId,
        InteractionCorrelation,
        InteractionTrait,
    )

try:
    from ...architecture.interaction.semantics import (
        RequestState,
        ResponseState,
        CommandState,
        Outcome,
        DiagnosticMetadata,
    )
except ModuleNotFoundError:
    from gordon_system.src.agent.architecture.interaction.semantics import (
        RequestState,
        ResponseState,
        CommandState,
        Outcome,
        DiagnosticMetadata,
    )


# =============================================================================
# STREAM TRANSPORT ROLE
# =============================================================================

class StreamTransportRole(Enum):
    """
    Role of a stream in interaction transport.
    
    Every stream has exactly one primary role:
        - PASSTHROUGH: Simply transports interactions without modification
        - BUFFERED: Caches interactions for delivery to subscribers
        - FILTERED: Routes interactions based on subscription criteria
        - ENRICHED: Adds transport metadata while preserving semantics
        - OBSERVATION: Specialized stream for diagnostic observation
    
    Invariants:
        - STREAM-ROLE-001: Stream role is immutable after creation
        - STREAM-ROLE-002: Role defines allowed operations, not semantic meaning
        - STREAM-ROLE-003: All roles preserve interaction semantics
    """
    
    PASSTHROUGH = "passthrough"  # Direct transport, no buffering
    BUFFERED = "buffered"        # Cached delivery to subscribers
    FILTERED = "filtered"        # Subscription-based routing
    ENRICHED = "enriched"        # Adds transport metadata
    OBSERVATION = "observation"  # Diagnostic-only stream


# =============================================================================
# STREAM TRANSPORT CONTRACT
# =============================================================================

class StreamTransportConstraint(Enum):
    """
    Immutable constraints on what streams may do with interactions.
    
    These are NOT permissions - they are absolute architectural boundaries:
        - NEVER_AUTHORIZE: Stream cannot authorize execution
        - NEVER_MUTATE_SEMANTICS: Stream cannot change interaction meaning
        - NEVER_REDEFINE_IDENTITY: Stream cannot alter interaction identity
        - NEVER_OWN_TRANSPORT: Stream does not own the interaction
        - NEVER_DEFINE_LIFECYCLE: Stream lifecycle is independent
    
    Invariants:
        - STREAM-CONSTRAINT-001: All constraints are absolute (never optional)
        - STREAM-CONSTRAINT-002: Constraints apply to all stream implementations
        - STREAM-CONSTRAINT-003: Violating a constraint is an architectural error
    """
    
    NEVER_AUTHORIZE = "never_authorize"       # Stream never grants authority
    NEVER_MUTATE_SEMANTICS = "never_mutate_semantics"  # Preserve interaction semantics
    NEVER_REDEFINE_IDENTITY = "never_redefine_identity"  # Preserve identity
    NEVER_OWN_TRANSPORT = "never_own_transport"  # Stream doesn't own interaction
    NEVER_DEFINE_LIFECYCLE = "never_define_lifecycle"  # Independent lifecycle


# =============================================================================
# PUBLICATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class PublicationContract:
    """
    Immutable contract for publishing interactions to streams.
    
    When an interaction is published to a stream, the following are guaranteed:
        - IDENTITY_PRESERVED: Interaction ID remains unchanged
        - CATEGORY_PRESERVED: Semantic category is preserved
        - PROVENANCE_PRESERVED: Origin information is maintained
        - ORDERING_PRESERVED: Position in stream ordering is recorded
        - TIMESTAMP_PRESERVED: Original timestamp is retained (not replaced)
        - CONTEXT_PRESERVED: Execution context remains accessible
        - METADATA_UNCHANGED: Interaction metadata is not modified
    
    Publication shall never alter:
        - The interaction's semantic meaning
        - The interaction's identity or correlation IDs
        - Timestamps except to add stream-specific timing
        - Payload content (unless encryption/encoding for transport)
    
    Invariants:
        - PUB-001: Every publication creates a new stream record
        - PUB-002: Stream record references original interaction
        - PUB-003: Publication timestamp is distinct from interaction timestamp
        - PUB-004: Provenance chain is preserved in stream context
    """
    
    # Identity preservation
    preserve_interaction_id: bool = True
    
    # Category preservation  
    preserve_category: bool = True
    
    # Timestamp handling (original vs publication)
    preserve_original_timestamps: bool = True
    
    # Context preservation
    preserve_execution_context: bool = True
    
    # Provenance
    track_stream_path: bool = True  # Record which streams were traversed
    
    # Ordering
    record_stream_position: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert publication contract to dictionary."""
        return {
            "preserve_interaction_id": self.preserve_interaction_id,
            "preserve_category": self.preserve_category,
            "preserve_original_timestamps": self.preserve_original_timestamps,
            "preserve_execution_context": self.preserve_execution_context,
            "track_stream_path": self.track_stream_path,
            "record_stream_position": self.record_stream_position,
        }
    
    @classmethod
    def strict(cls) -> "PublicationContract":
        """Create a strict publication contract with all preservation enabled."""
        return cls(
            preserve_interaction_id=True,
            preserve_category=True,
            preserve_original_timestamps=True,
            preserve_execution_context=True,
            track_stream_path=True,
            record_stream_position=True,
        )
    
    @classmethod
    def permissive(cls) -> "PublicationContract":
        """
        Create a permissive publication contract.
        
        Note: Even in permissive mode, identity and category are always preserved.
        """
        return cls(
            preserve_interaction_id=True,  # Always required
            preserve_category=True,       # Always required
            preserve_original_timestamps=False,
            preserve_execution_context=False,
            track_stream_path=False,
            record_stream_position=False,
        )


# =============================================================================
# SUBSCRIPTION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class SubscriptionContract:
    """
    Immutable contract for subscribing to streams and consuming interactions.
    
    When a subscriber consumes an interaction from a stream, the following are
    guaranteed:
        - OBSERVE_AS_PUBLISHED: Interaction is observed exactly as published
        - NO_FILTERING_SEMANTICS: Filtering never modifies semantics
        - ORDERING_ACCURATE: Position in stream ordering is accurate
        - TIMESTAMPS_ACCURATE: Original timestamps are preserved
    
    Subscriptions express interest but do not grant authority.
    
    Invariants:
        - SUB-001: Every subscription observes interactions exactly as published
        - SUB-002: Subscription filtering cannot alter interaction semantics
        - SUB-003: Stream position is tracked per-subscriber
        - SUB-004: No implicit subscriptions (explicit only)
    """
    
    # Observation guarantees
    observe_as_published: bool = True
    
    # Filtering behavior
    filter_preserves_semantics: bool = True  # Filtered interactions retain semantics
    
    # Ordering
    preserve_ordering: bool = True
    
    # Position tracking
    track_subscription_position: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription contract to dictionary."""
        return {
            "observe_as_published": self.observe_as_published,
            "filter_preserves_semantics": self.filter_preserves_semantics,
            "preserve_ordering": self.preserve_ordering,
            "track_subscription_position": self.track_subscription_position,
        }
    
    @classmethod
    def strict(cls) -> "SubscriptionContract":
        """Create a strict subscription contract."""
        return cls(
            observe_as_published=True,
            filter_preserves_semantics=True,
            preserve_ordering=True,
            track_subscription_position=True,
        )


# =============================================================================
# ROUTING CONTRACT
# =============================================================================

@dataclass(frozen=True)
class RoutingContract:
    """
    Immutable contract for routing interactions through streams.
    
    Routing decisions shall be deterministic and based only on explicit criteria:
        - Stream identity (which stream)
        - Interaction category (what type)
        - Interaction metadata (payload, traits, etc.)
        - Execution context (thread, loop, etc.)
        - Subscription policy (explicit subscription criteria)
    
    Routing shall NEVER depend upon:
        - Mutable architectural state
        - Runtime performance considerations
        - Load balancing decisions
        - Implementation details
    
    Deterministic routing means the same input always produces the same output.
    
    Invariants:
        - ROUTE-001: Routing is deterministic (same input → same output)
        - ROUTE-002: Routing criteria are explicit and inspectable
        - ROUTE-003: No implicit cross-stream routing
        - ROUTE-004: Routing preserves interaction semantics
    """
    
    # Determinism guarantee
    deterministic_routing: bool = True
    
    # Explicit criteria only
    use_only_explicit_criteria: bool = True
    
    # Isolation
    preserve_stream_isolation: bool = True  # Don't implicitly route across streams
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert routing contract to dictionary."""
        return {
            "deterministic_routing": self.deterministic_routing,
            "use_only_explicit_criteria": self.use_only_explicit_criteria,
            "preserve_stream_isolation": self.preserve_stream_isolation,
        }
    
    @classmethod
    def strict(cls) -> "RoutingContract":
        """Create a strict routing contract."""
        return cls(
            deterministic_routing=True,
            use_only_explicit_criteria=True,
            preserve_stream_isolation=True,
        )


# =============================================================================
# ORDERING GUARANTEES
# =============================================================================

class OrderingType(Enum):
    """
    Types of ordering guarantees provided by streams.
    
    Orderings:
        - SEQUENTIAL: Records arrive in publication order
        - CAUSAL: Causally related records maintain causal order
        - TOTAL: All records have a global total order
        - PARTIAL: No guaranteed ordering (unordered delivery)
    """
    
    SEQUENTIAL = "sequential"  # Publication order preserved
    CAUSAL = "causal"          # Causal dependencies maintained
    TOTAL = "total"            # Global total order (strongest)
    PARTIAL = "partial"        # No guarantee (weakest)


@dataclass(frozen=True)
class OrderingGuarantees:
    """
    Immutable ordering guarantees for stream interactions.
    
    Each stream defines its own ordering semantics:
        - The type of ordering it provides
        - How replay preserves ordering
        - Whether causal dependencies are tracked
    
    Invariants:
        - ORDER-001: Every stream has explicit ordering semantics
        - ORDER-002: Ordering is preserved during replay
        - ORDER-003: Causal relationships are maintained where applicable
        - ORDER-004: No arbitrary reordering by transport
    """
    
    # Type of ordering
    ordering_type: OrderingType = OrderingType.SEQUENTIAL
    
    # Timestamps for temporal ordering
    use_timestamps_for_ordering: bool = True
    
    # Causal tracking
    track_causal_dependencies: bool = False  # Requires explicit enablement
    
    # Replay guarantees
    preserve_ordering_during_replay: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ordering guarantees to dictionary."""
        return {
            "ordering_type": self.ordering_type.value,
            "use_timestamps_for_ordering": self.use_timestamps_for_ordering,
            "track_causal_dependencies": self.track_causal_dependencies,
            "preserve_ordering_during_replay": self.preserve_ordering_during_replay,
        }
    
    @classmethod
    def sequential(cls) -> "OrderingGuarantees":
        """Create sequential ordering guarantees (publication order)."""
        return cls(
            ordering_type=OrderingType.SEQUENTIAL,
            use_timestamps_for_ordering=True,
            track_causal_dependencies=False,
            preserve_ordering_during_replay=True,
        )
    
    @classmethod
    def causal(cls) -> "OrderingGuarantees":
        """Create causal ordering guarantees (dependencies preserved)."""
        return cls(
            ordering_type=OrderingType.CAUSAL,
            use_timestamps_for_ordering=True,
            track_causal_dependencies=True,
            preserve_ordering_during_replay=True,
        )
    
    @classmethod
    def total(cls) -> "OrderingGuarantees":
        """Create total ordering guarantees (global order)."""
        return cls(
            ordering_type=OrderingType.TOTAL,
            use_timestamps_for_ordering=True,
            track_causal_dependencies=True,
            preserve_ordering_during_replay=True,
        )
    
    @classmethod
    def unordered(cls) -> "OrderingGuarantees":
        """Create unordered guarantees (no ordering guarantee)."""
        return cls(
            ordering_type=OrderingType.PARTIAL,
            use_timestamps_for_ordering=False,
            track_causal_dependencies=False,
            preserve_ordering_during_replay=False,  # Unordered replay
        )


# =============================================================================
# REPLAY CONTRACT
# =============================================================================

@dataclass(frozen=True)
class ReplayContract:
    """
    Immutable contract for replaying interactions from streams.
    
    Replay shall preserve:
        - ORDERING: Same sequence as original publication
        - PROVENANCE: Origin information is maintained
        - IDENTITY: Interaction IDs remain unchanged
        - PUBLICATION_SEQUENCE: Publication order is preserved
        - TIMESTAMPS: Original timestamps are retained (not replay time)
        - STREAM_IDENTITY: Which stream the interaction was published to
    
    Replay shall NEVER:
        - Fabricate transport history
        - Alter semantic meaning
        - Change identity or correlation IDs
        - Replace original timestamps with replay time
    
    Invariants:
        - REPLAY-001: Replay is deterministic (same input → same output)
        - REPLAY-002: No fabricated history (only actual records are replayed)
        - REPLAY-003: Provenance chain is preserved
        - REPLAY-004: Timestamps remain original values
    """
    
    # Preservation guarantees
    preserve_ordering: bool = True
    
    preserve_provenance: bool = True
    
    preserve_identity: bool = True
    
    preserve_timestamps: bool = True
    
    preserve_stream_id: bool = True
    
    # Replay constraints
    allow_fabrication: bool = False  # Never fabricate history
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert replay contract to dictionary."""
        return {
            "preserve_ordering": self.preserve_ordering,
            "preserve_provenance": self.preserve_provenance,
            "preserve_identity": self.preserve_identity,
            "preserve_timestamps": self.preserve_timestamps,
            "preserve_stream_id": self.preserve_stream_id,
            "allow_fabrication": self.allow_fabrication,
        }
    
    @classmethod
    def strict(cls) -> "ReplayContract":
        """Create a strict replay contract."""
        return cls(
            preserve_ordering=True,
            preserve_provenance=True,
            preserve_identity=True,
            preserve_timestamps=True,
            preserve_stream_id=True,
            allow_fabrication=False,  # Never fabricate
        )


# =============================================================================
# ISOLATION RULES
# =============================================================================

@dataclass(frozen=True)
class IsolationRules:
    """
    Immutable isolation rules for stream interactions.
    
    Streams shall remain isolated:
        - STREAM_ISOLATED: Publishing to one stream doesn't implicitly publish to another
        - CROSS_STREAM_EXPLICIT: Cross-stream propagation requires explicit routing
        - NO_SHARED_STATE: Streams don't share interaction state
    
    Invariants:
        - ISO-001: Every stream is independent
        - ISO-002: No implicit cross-stream propagation
        - ISO-003: Cross-stream routing is explicit and observable
        - ISO-004: Isolation preserves ownership boundaries
    """
    
    # Stream isolation
    preserve_stream_isolation: bool = True
    
    require_explicit_cross_stream_routing: bool = True
    
    no_shared_state_between_streams: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert isolation rules to dictionary."""
        return {
            "preserve_stream_isolation": self.preserve_stream_isolation,
            "require_explicit_cross_stream_routing": self.require_explicit_cross_stream_routing,
            "no_shared_state_between_streams": self.no_shared_state_between_streams,
        }
    
    @classmethod
    def strict(cls) -> "IsolationRules":
        """Create strict isolation rules."""
        return cls(
            preserve_stream_isolation=True,
            require_explicit_cross_stream_routing=True,
            no_shared_state_between_streams=True,
        )


# =============================================================================
# OWNERSHIP PRESERVATION
# =============================================================================

@dataclass(frozen=True)
class OwnershipPreservation:
    """
    Immutable ownership preservation rules for stream-interaction relationships.
    
    Ownership boundaries:
        - STREAM_OWN_TRANSPORT: Streams own the transport mechanism
        - INTERACTION_OWNS_SEMANTICS: Interactions own communication semantics
        - EXECUTION_OWNS_SCHEDULING: Execution owns scheduling decisions
        - SYSTEM_OWNS_STATE: Systems own their state (unchanged by interactions)
    
    Ownership boundaries shall NEVER be crossed through transport.
    
    Invariants:
        - OWN-001: Stream ownership ≠ Interaction ownership
        - OWN-002: Transport ownership ≠ Semantic ownership
        - OWN-003: Scheduling authority ≠ Ownership authority
        - OWN-004: State ownership is never transferred by interactions
    """
    
    # Ownership assignments
    stream_owns_transport: bool = True
    
    interaction_owns_semantics: bool = True
    
    execution_owns_scheduling: bool = True
    
    system_owns_state: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ownership preservation to dictionary."""
        return {
            "stream_owns_transport": self.stream_owns_transport,
            "interaction_owns_semantics": self.interaction_owns_semantics,
            "execution_owns_scheduling": self.execution_owns_scheduling,
            "system_owns_state": self.system_owns_state,
        }
    
    @classmethod
    def strict(cls) -> "OwnershipPreservation":
        """Create strict ownership preservation."""
        return cls(
            stream_owns_transport=True,
            interaction_owns_semantics=True,
            execution_owns_scheduling=True,
            system_owns_state=True,
        )


# =============================================================================
# AUTHORITY PRESERVATION
# =============================================================================

@dataclass(frozen=True)
class AuthorityPreservation:
    """
    Immutable authority preservation rules for streams.
    
    Streams never:
        - Grant authority
        - Evaluate authority
        - Deny authority
    
    Authority verification remains external to transport.
    
    Invariants:
        - AUTH-001: Streams do not grant authority
        - AUTH-002: Streams do not evaluate authority
        - AUTH-003: Streams do not deny authority
        - AUTH-004: Authority is verified externally (not in transport layer)
    """
    
    # Stream constraints
    streams_never_grant_authority: bool = True
    
    streams_never_evaluate_authority: bool = True
    
    streams_never_deny_authority: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert authority preservation to dictionary."""
        return {
            "streams_never_grant_authority": self.streams_never_grant_authority,
            "streams_never_evaluate_authority": self.streams_never_evaluate_authority,
            "streams_never_deny_authority": self.streams_never_deny_authority,
        }
    
    @classmethod
    def strict(cls) -> "AuthorityPreservation":
        """Create strict authority preservation."""
        return cls(
            streams_never_grant_authority=True,
            streams_never_evaluate_authority=True,
            streams_never_deny_authority=True,
        )


# =============================================================================
# OBSERVABILITY METADATA
# =============================================================================

@dataclass(frozen=True)
class StreamObservabilityMetadata:
    """
    Diagnostic metadata for stream interaction transport.
    
    This metadata is附加 to interactions during transport through streams.
    It records the transport journey without modifying the original interaction.
    
    Required fields for every observable interaction transport:
        - stream_id: Which stream was used
        - interaction_id: The original interaction being transported
        - publication_timestamp: When publication occurred
        - routing_info: How it was routed
        - subscriber_info: Who received it (for subscriptions)
        - replay_metadata: If this is a replay
    
    Transport diagnostics shall remain independent of Interaction diagnostics.
    
    Invariants:
        - OBS-STREAM-001: All required fields are present during transport
        - OBS-STREAM-002: Timestamps record both original and stream times
        - OBS-STREAM-003: Routing information is traceable
        - OBS-STREAM-004: Subscriber information is recorded per-delivery
    """
    
    # Transport identity
    stream_id: str
    
    interaction_id: str
    
    # Timing
    publication_timestamp_utc: float  # When published to stream
    original_interaction_timestamp_utc: float  # Original timestamp (unchanged)
    
    # Routing
    routing_path: Tuple[str, ...] = field(default_factory=tuple)  # Which streams/routers traversed
    
    # Subscriber tracking
    subscriber_id: Optional[str] = None  # If delivered to subscriber
    delivery_timestamp_utc: Optional[float] = None
    
    # Replay information
    is_replay: bool = False
    replay_source: Optional[str] = None  # Where replay came from (archive, etc.)
    
    def with_routing_hop(self, hop_id: str) -> "StreamObservabilityMetadata":
        """Add a routing hop to the path."""
        return dataclass_replace(
            self,
            routing_path=self.routing_path + (hop_id,)
        )
    
    def as_delivered_to(self, subscriber_id: str) -> "StreamObservabilityMetadata":
        """Mark this interaction as delivered to a subscriber."""
        return dataclass_replace(
            self,
            subscriber_id=subscriber_id,
            delivery_timestamp_utc=time.time()
        )
    
    def mark_as_replay(self, replay_source: Optional[str] = None) -> "StreamObservabilityMetadata":
        """Mark this transport as part of a replay operation."""
        return dataclass_replace(
            self,
            is_replay=True,
            replay_source=replay_source
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert observability metadata to dictionary for serialization."""
        result = {
            "stream_id": self.stream_id,
            "interaction_id": self.interaction_id,
            "publication_timestamp_utc": self.publication_timestamp_utc,
            "original_interaction_timestamp_utc": self.original_interaction_timestamp_utc,
            "routing_path": list(self.routing_path),
        }
        
        if self.subscriber_id:
            result["subscriber_id"] = self.subscriber_id
        
        if self.delivery_timestamp_utc:
            result["delivery_timestamp_utc"] = self.delivery_timestamp_utc
        
        if self.is_replay:
            result["is_replay"] = True
            if self.replay_source:
                result["replay_source"] = self.replay_source
        
        return result


# =============================================================================
# FAILURE SEMANTICS
# =============================================================================

class StreamFailureType(Enum):
    """
    Categories of stream transport failure.
    
    Transport failures shall be explicit and never corrupt interaction identity.
    
    Failure Types:
        - PUBLICATION: Cannot publish to stream (buffer full, closed, etc.)
        - ROUTING: Cannot route to intended destination
        - SUBSCRIBER: Subscriber failed to receive or process
        - CAPACITY: Stream capacity exceeded
        - REPLAY: Replay operation failed
        - CHECKPOINT: Checkpoint operation failed
    """
    
    PUBLICATION_FAILURE = "publication_failure"      # Cannot publish to stream
    ROUTING_FAILURE = "routing_failure"              # Cannot route correctly
    SUBSCRIBER_FAILURE = "subscriber_failure"        # Subscriber cannot receive
    CAPACITY_EXHAUSTION = "capacity_exhaustion"      # Resource exhausted
    REPLAY_FAILURE = "replay_failure"                # Replay failed
    CHECKPOINT_FAILURE = "checkpoint_failure"        # Checkpoint operation failed


@dataclass(frozen=True)
class StreamTransportFailure:
    """
    Immutable record of a stream transport failure.
    
    Every transport failure shall preserve immutable diagnostic information.
    
    Failure semantics:
        - FAILURE-001: Transport failures are explicit (never silent)
        - FAILURE-002: Interaction identity is preserved in failure records
        - FAILURE-003: Failures never corrupt interaction semantics
        - FAILURE-004: Failure records include full context
    
    Invariants:
        - FAIL-STREAM-001: All failures record the interaction being transported
        - FAIL-STREAM-002: Timestamps are recorded at failure time
        - FAIL-STREAM-003: Context includes stream, routing, and subscriber info
        - FAIL-STREAM-004: Failures are traceable to their source
    """
    
    # Failure identity
    failure_id: str
    
    # Failure category
    failure_type: StreamFailureType
    
    # Interaction context (what was being transported)
    interaction_id: Optional[str] = None
    
    interaction_category: Optional[str] = None  # Category name as string
    
    # Stream context
    stream_id: Optional[str] = None
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    original_interaction_timestamp_utc: Optional[float] = None
    
    # Additional context
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retryable: bool = False
    retry_after_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert failure record to dictionary."""
        result = {
            "failure_id": self.failure_id,
            "failure_type": self.failure_type.value,
            "timestamp_utc": self.timestamp_utc,
        }
        
        if self.interaction_id:
            result["interaction_id"] = self.interaction_id
        
        if self.interaction_category:
            result["interaction_category"] = self.interaction_category
        
        if self.stream_id:
            result["stream_id"] = self.stream_id
        
        if self.original_interaction_timestamp_utc:
            result["original_interaction_timestamp_utc"] = self.original_interaction_timestamp_utc
        
        if self.error_message:
            result["error_message"] = self.error_message
        
        if self.error_code:
            result["error_code"] = self.error_code
        
        result["retryable"] = self.retryable
        
        if self.retry_after_seconds is not None:
            result["retry_after_seconds"] = self.retry_after_seconds
        
        return result


# =============================================================================
# CANONICAL INTERACTION STREAM RECORD
# =============================================================================

@dataclass(frozen=True)
class InteractionStreamRecord:
    """
    Canonical record of an interaction published to a stream.
    
    This record represents the intersection of interaction semantics and
    stream transport. It preserves all interaction properties while adding
    stream-specific metadata for observability and ordering.
    
    Structure:
        - Interaction: The original interaction (identity, category, payload)
        - StreamContext: Transport metadata added by streams
        - OrderingInfo: Position in stream ordering
        - Timestamps: Both original and stream timestamps
    
    Invariants:
        - RECORD-001: Interaction properties are immutable
        - RECORD-002: Stream context cannot alter interaction semantics
        - RECORD-003: Ordering is preserved from stream position
        - RECORD-004: All timestamps remain accessible for observability
    """
    
    # Original interaction (preserved exactly as published)
    interaction_id: str
    category: str  # Category name as string (InteractionCategory would need import)
    interaction_data: Dict[str, Any] = field(default_factory=dict)
    
    # Stream context (added by stream at publication time)
    stream_id: str
    sequence_number: int
    generation_id: Optional[str] = None
    
    # Timestamps
    original_timestamp_utc: float  # When interaction was created
    published_to_stream_utc: float  # When it was published to stream
    
    # Routing information (for observability)
    routing_path: Tuple[str, ...] = field(default_factory=tuple)
    
    # Metadata for diagnostics
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def with_routing_hop(self, hop_id: str) -> "InteractionStreamRecord":
        """Create a new record with an additional routing hop."""
        return dataclass_replace(
            self,
            routing_path=self.routing_path + (hop_id,)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stream record to dictionary for serialization."""
        result = {
            "interaction_id": self.interaction_id,
            "category": self.category,
            "stream_id": self.stream_id,
            "sequence_number": self.sequence_number,
            "original_timestamp_utc": self.original_timestamp_utc,
            "published_to_stream_utc": self.published_to_stream_utc,
            "routing_path": list(self.routing_path),
        }
        
        if self.generation_id:
            result["generation_id"] = self.generation_id
        
        # Include interaction data (payload, participants, etc.)
        result["interaction_data"] = dict(self.interaction_data)
        
        # Add metadata
        result["metadata"] = dict(self.metadata)
        
        return result


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    if hasattr(obj, "__dataclass_fields__"):
        import dataclasses
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Stream transport role and constraints
    "StreamTransportRole",
    "StreamTransportConstraint",
    
    # Contracts
    "PublicationContract",
    "SubscriptionContract",
    "RoutingContract",
    
    # Ordering
    "OrderingType",
    "OrderingGuarantees",
    
    # Replay
    "ReplayContract",
    
    # Isolation
    "IsolationRules",
    
    # Ownership and Authority
    "OwnershipPreservation",
    "AuthorityPreservation",
    
    # Observability
    "StreamObservabilityMetadata",
    
    # Failures
    "StreamFailureType",
    "StreamTransportFailure",
    
    # Canonical record
    "InteractionStreamRecord",
    
    # Utilities
    "dataclass_replace",
]