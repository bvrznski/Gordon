# Cross-Domain Interaction Contracts - Phase 3.14.10
# ==================================================
#
# Canonical architectural contracts governing all cross-domain interactions
# in Gordon.
#
# This module establishes immutable rules for how canonical domains:
#   Execution, Streams, Networks, Capabilities, Systems, Core, Entrypoints
# interact through explicit Interaction contracts while preserving
# domain boundaries, ownership, and authority.

"""
Canonical Cross-Domain Interaction Contracts for Gordon Phase 3.14.10

This module establishes immutable architectural contracts governing all
cross-domain interactions. Every cross-domain collaboration shall occur
exclusively through canonical Interaction contracts that preserve:

    - Domain independence
    - Ownership preservation
    - Authority preservation
    - Deterministic routing
    - Observability
    - Replay compatibility

ARCHITECTURAL PRINCIPLES:
=========================

Domains cooperate. Domains do not merge.
Domains communicate. Domains preserve independence.

Every cross-domain interaction shall preserve architectural separation.

DOMAIN BOUNDARIES:
==================

Every domain defines:

    * Responsibilities
    * Ownership (of its state, lifecycle, implementation)
    * Public contracts (only these may cross boundaries)
    * Lifecycle (internal progression)
    * Authority (within its domain)
    * Visibility (public interfaces only)

Internal implementation shall remain private. Only public architectural
contracts may cross boundaries.

CANONICAL DOMAINS:
==================

    Execution       - Coordinates scheduling, admission, ordering
    Streams         - Transport interactions with ordering/provenance
    Networks        - Cognitive coordination through interactions
    Capabilities    - Perform computation (execute work)
    Systems         - Own persistent state
    Core            - Fundamental infrastructure and utilities
    Entrypoints     - External interface entry points

CANONICAL INTERACTION FLOW:
===========================

    Domain A
        │
        ▼
    Interaction (typed, categorized)
        │
        ▼
    Domain Boundary
        │
        ▼
    Domain B
        │
        ▼
    Result / Event (published back to streams)

Ownership never crosses boundaries.
Authority never crosses boundaries.

INTEGRATION PRINCIPLES:
=======================

Execution Coordinates:
    - Schedules cross-domain interactions
    - Determines admission and ordering
    - Never bypasses domain ownership or authority
    
Streams Transport:
    - Carry canonical Interactions
    - Preserve ordering, provenance, identity
    - Never modify interaction semantics or domain ownership
    
Networks Participate:
    - May initiate, receive, or coordinate interactions
    - Never own interactions
    - Always preserve architectural boundaries
    
Capabilities Execute:
    - Perform computation per authority verification
    - Never mutate System state directly
    - Results cross boundaries through Interactions
    
Systems Own State:
    - Expose public contracts for access/mutation requests
    - Authorize all state transitions
    - Never allow direct mutation by external components

REPLAY COMPATIBILITY:
=====================

Replay shall preserve:

    * Domain boundaries
    * Interaction ordering
    * Provenance
    * Authority decisions
    * Execution context

Replay shall never bypass architectural contracts.

OBSERVABILITY REQUIREMENTS:
===========================

Every cross-domain interaction shall expose immutable metadata:

    * Source domain
    * Destination domain
    * Interaction identifier
    * Execution context
    * Timestamps (creation, admission, completion)
    * Authority decision
    * Outcome

Cross-domain communication shall remain fully traceable.

FAILURE SEMANTICS:
==================

Failures shall be explicit. Examples include:

    * Boundary violation (domain accessed directly)
    * Dependency violation (implicit dependencies)
    * Routing failure (no valid path between domains)
    * Admission failure (not permitted to interact)
    * Authorization failure (authority denied)
    * Lifecycle incompatibility (wrong state for interaction)
    * Contract violation (interaction type mismatch)

Every failure shall preserve immutable diagnostic metadata.

ARCHITECTURAL INVARIANTS:
=========================

No domain shall:

    * Directly invoke another domain's internals
    * Assume another domain's authority
    * Mutate another domain's state
    * Redefine another domain's lifecycle
    * Bypass canonical Interaction contracts

Every cross-domain collaboration shall remain explicit, observable,
and architecturally verifiable.

FUTURE COMPATIBILITY:
=====================

Future architectural domains shall integrate through these contracts.
New domains may extend the interaction graph but shall never redefine
the principles established by this phase.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    FrozenSet,
    Any,
    Protocol,
    runtime_checkable,
)
import uuid
import time


# =============================================================================
# DOMAIN IDENTIFIERS
# =============================================================================


class DomainId:
    """
    Unique identifier for an architectural domain.

    Every canonical domain has a stable, immutable identity.
    """

    value: str

    def __init__(self, domain_name: str):
        """Create a domain ID from a domain name."""
        self.value = f"domain_{domain_name.lower().replace(' ', '_')}"

    @classmethod
    def execution(cls) -> "DomainId":
        return cls("execution")

    @classmethod
    def streams(cls) -> "DomainId":
        return cls("streams")

    @classmethod
    def networks(cls) -> "DomainId":
        return cls("networks")

    @classmethod
    def capabilities(cls) -> "DomainId":
        return cls("capabilities")

    @classmethod
    def systems(cls) -> "DomainId":
        return cls("systems")

    @classmethod
    def core(cls) -> "DomainId":
        return cls("core")

    @classmethod
    def entrypoints(cls) -> "DomainId":
        return cls("entrypoints")

    def __str__(self) -> str:
        return self.value


# =============================================================================
# CANONICAL DOMAIN ENUMERATION
# =============================================================================


class CanonicalDomain(Enum):
    """
    Canonical architectural domains in Gordon.

    Every cross-domain interaction shall be between exactly two canonical
    domains (source and destination).

    DOMAINS:
        EXECUTION       - Coordinates scheduling, admission, ordering
        STREAMS         - Transport interactions with ordering/provenance
        NETWORKS        - Cognitive coordination through interactions
        CAPABILITIES    - Perform computation (execute work)
        SYSTEMS         - Own persistent state
        CORE            - Fundamental infrastructure and utilities
        ENTRYPOINTS     - External interface entry points

    INVARIANTS:
        DOM-001: Every domain has exactly one canonical identity
        DOM-002: Domain identity is immutable
        DOM-003: Domain boundaries shall never be crossed by direct access
        DOM-004: All inter-domain communication uses canonical Interactions
    """

    EXECUTION = "execution"       # Coordinates scheduling, admission, ordering
    STREAMS = "streams"           # Transport interactions with ordering/provenance
    NETWORKS = "networks"         # Cognitive coordination through interactions
    CAPABILITIES = "capabilities"  # Perform computation (execute work)
    SYSTEMS = "systems"           # Own persistent state
    CORE = "core"                 # Fundamental infrastructure and utilities
    ENTRYPOINTS = "entrypoints"   # External interface entry points


# =============================================================================
# CROSS-DOMAIN INTERACTION TYPE
# =============================================================================


class CrossDomainInteractionCategory(Enum):
    """
    Categories of cross-domain interactions.

    Each category defines the expected semantics when an interaction
    crosses from one domain to another.

    CATEGORIES:
        EXECUTE_REQUEST     - Request execution scheduling (to Execution)
        EXECUTE_RESPONSE    - Response to execution scheduling (from Execution)
        TRANSPORT_REQUEST   - Request stream transport (to Streams)
        TRANSPORT_RESULT    - Result via stream transport (from Streams)
        COORDINATE_REQUEST  - Request coordination (to Networks)
        COORDINATE_RESULT   - Result of coordination (from Networks)
        COMPUTE_REQUEST     - Request computation (to Capabilities)
        COMPUTE_RESULT      - Result of computation (from Capabilities)
        STATE_ACCESS        - Access system state (to Systems)
        STATE_MUTATION      - Request state mutation (to Systems)
        CORE_OPERATION      - Core infrastructure operation
        ENTRYPOINT_IN       - Entry point incoming interaction
        ENTRYPOINT_OUT      - Entry point outgoing interaction

    INVARIANTS:
        CAT-001: Category defines semantic intent when crossing domains
        CAT-002: Category is immutable once set
        CAT-003: Category determines authority requirements
    """

    # Execution interactions
    EXECUTE_REQUEST = "execute_request"      # Request execution scheduling (to Execution)
    EXECUTE_RESPONSE = "execute_response"    # Response to execution scheduling (from Execution)

    # Streams interactions
    TRANSPORT_REQUEST = "transport_request"  # Request stream transport (to Streams)
    TRANSPORT_RESULT = "transport_result"    # Result via stream transport (from Streams)

    # Networks interactions
    COORDINATE_REQUEST = "coordinate_request"  # Request coordination (to Networks)
    COORDINATE_RESULT = "coordinate_result"    # Result of coordination (from Networks)

    # Capabilities interactions
    COMPUTE_REQUEST = "compute_request"      # Request computation (to Capabilities)
    COMPUTE_RESULT = "compute_result"        # Result of computation (from Capabilities)

    # Systems interactions
    STATE_ACCESS = "state_access"            # Access system state (to Systems)
    STATE_MUTATION = "state_mutation"        # Request state mutation (to Systems)

    # Core interactions
    CORE_OPERATION = "core_operation"        # Core infrastructure operation

    # Entrypoint interactions
    ENTRYPOINT_IN = "entrypoint_in"          # Entry point incoming interaction
    ENTRYPOINT_OUT = "entrypoint_out"        # Entry point outgoing interaction


# =============================================================================
# CROSS-DOMAIN INTERACTION IDENTITY
# =============================================================================


@dataclass(frozen=True, slots=True)
class CrossDomainInteractionId:
    """
    Unique identifier for one cross-domain interaction.

    Identity INVARIANTS:
        CDI-001: Every cross-domain interaction has exactly one unique identity
        CDI-002: Identity is immutable once created
        CDI-003: No two interactions share the same identity
    """

    value: str = field(default_factory=lambda: f"cdi_{uuid.uuid4().hex[:24]}")

    @classmethod
    def generate(cls) -> "CrossDomainInteractionId":
        """Generate a new unique cross-domain interaction ID."""
        return cls(value=f"cdi_{uuid.uuid4().hex[:24]}")


@dataclass(frozen=True, slots=True)
class CrossDomainCorrelation:
    """
    Correlation context for tracing cross-domain interactions.

    Enables tracing across architectural boundaries.
    """

    correlation_id: str  # Coordinator advancement context
    causation_id: Optional[str] = None  # Direct cause


# =============================================================================
# CROSS-DOMAIN INTERACTION RECORD
# =============================================================================


@dataclass(frozen=True, slots=True)
class CrossDomainInteractionRecord:
    """
    Canonical record of a cross-domain interaction.

    This record represents the intersection of two architectural domains.
    It preserves all domain-specific properties while adding cross-domain
    metadata for observability and routing.

    STRUCTURE:
        Source Domain       - Where interaction originates
        Destination Domain  - Where interaction is delivered
        Interaction         - The typed interaction being transported
        Context             - Cross-domain execution context
        Timestamps          - When each domain processed the interaction

    INVARIANTS:
        RECORD-001: Source and destination domains are immutable
        RECORD-002: Interaction properties are preserved exactly
        RECORD-003: Domain ownership is never transferred
        RECORD-004: Authority verification remains external
    """

    # Identity (required)
    interaction_id: CrossDomainInteractionId

    # Domain routing
    source_domain: CanonicalDomain
    destination_domain: CanonicalDomain

    # Interaction being transported across domains
    interaction_category: CrossDomainInteractionCategory
    interaction_payload: Dict[str, Any]

    # Timestamps
    created_at_utc: float  # When interaction was first created
    source_processed_at_utc: float  # When source domain processed it
    destination_processed_at_utc: Optional[float] = None  # When dest processed

    # Context for routing and observability
    routing_context: Dict[str, Any] = field(default_factory=dict)
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])

    # Authority context (for verification)
    authority_verified: bool = False
    authorization_source: Optional[str] = None

    @classmethod
    def create(
        cls,
        source_domain: CanonicalDomain,
        destination_domain: CanonicalDomain,
        category: CrossDomainInteractionCategory,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> "CrossDomainInteractionRecord":
        """Create a new cross-domain interaction record."""
        now = time.monotonic()
        return cls(
            interaction_id=CrossDomainInteractionId.generate(),
            source_domain=source_domain,
            destination_domain=destination_domain,
            interaction_category=category,
            interaction_payload=payload,
            created_at_utc=now,
            source_processed_at_utc=now,
            correlation_id=correlation_id or uuid.uuid4().hex[:16],
        )

    def with_destination_processed(self, result: "CrossDomainResult") -> "CrossDomainInteractionRecord":
        """Update record with destination processing completed."""
        return dataclass_replace(
            self,
            destination_processed_at_utc=time.monotonic(),
            authority_verified=result.is_success() or result.is_deferred(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "interaction_id": self.interaction_id.value,
            "source_domain": self.source_domain.value,
            "destination_domain": self.destination_domain.value,
            "interaction_category": self.interaction_category.value,
            "interaction_payload": dict(self.interaction_payload),
            "created_at_utc": self.created_at_utc,
            "source_processed_at_utc": self.source_processed_at_utc,
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrossDomainInteractionRecord":
        """Reconstruct record from dictionary."""
        return cls(
            interaction_id=CrossDomainInteractionId(value=data["interaction_id"]),
            source_domain=CanonicalDomain(data["source_domain"]),
            destination_domain=CanonicalDomain(data["destination_domain"]),
            interaction_category=CrossDomainInteractionCategory(data["interaction_category"]),
            interaction_payload=dict(data.get("interaction_payload", {})),
            created_at_utc=data["created_at_utc"],
            source_processed_at_utc=data["source_processed_at_utc"],
            correlation_id=data.get("correlation_id", ""),
        )


# =============================================================================
# CROSS-DOMAIN RESULT TYPES
# =============================================================================


class CrossDomainResultType(Enum):
    """
    Categories of cross-domain interaction results.

    RESULTS:
        SUCCESS         - Interaction processed successfully
        FAILURE         - Interaction failed
        DEFERRED        - Processing deferred to later time
        REJECTED        - Interaction rejected (e.g., invalid, unauthorized)
        CANCELLED       - Interaction cancelled

    INVARIANTS:
        RES-001: All results are explicit
        RES-002: Results preserve provenance
        RES-003: Results enable debugging and replay
    """

    SUCCESS = "success"           # Interaction processed successfully
    FAILURE = "failure"           # Interaction failed
    DEFERRED = "deferred"         # Processing deferred to later time
    REJECTED = "rejected"         # Interaction rejected (e.g., invalid, unauthorized)
    CANCELLED = "cancelled"       # Interaction cancelled


@dataclass(frozen=True, slots=True)
class CrossDomainResult:
    """
    Result of a cross-domain interaction.

    Every completed cross-domain interaction shall produce an explicit result.
    """

    # Identity
    interaction_id: str  # Which interaction this is the result for

    # Result type
    result_type: CrossDomainResultType

    # Outcome message
    message: Optional[str] = None

    # Timing
    created_at_utc: float
    completed_at_utc: Optional[float] = None

    # Context for debugging
    source_domain: Optional[str] = None
    destination_domain: Optional[str] = None

    def is_success(self) -> bool:
        return self.result_type == CrossDomainResultType.SUCCESS

    def is_failure(self) -> bool:
        return self.result_type == CrossDomainResultType.FAILURE

    def is_deferred(self) -> bool:
        return self.result_type == CrossDomainResultType.DEFERRED

    def is_rejected(self) -> bool:
        return self.result_type == CrossDomainResultType.REJECTED

    def is_cancelled(self) -> bool:
        return self.result_type == CrossDomainResultType.CANCELLED


# =============================================================================
# CROSS-DOMAIN ROUTING
# =============================================================================


@dataclass(frozen=True, slots=True)
class CrossDomainRoute:
    """
    Route definition for cross-domain interactions.

    Defines how interactions flow from source domain to destination domain.
    """

    route_id: str = field(default_factory=lambda: f"route_{uuid.uuid4().hex[:16]}")

    # Routing path
    source_domain: CanonicalDomain
    destination_domain: CanonicalDomain

    # Route criteria (when this route is applicable)
    category_match: Tuple[CrossDomainInteractionCategory, ...] = field(
        default_factory=tuple  # Empty tuple means all categories match
    )
    context_match: Dict[str, Any] = field(default_factory=dict)

    # Route action
    transport_strategy: str = "direct"  # direct, buffered, filtered, etc.

    created_at_utc: float = field(default_factory=time.monotonic)

    @classmethod
    def create(
        cls,
        source_domain: CanonicalDomain,
        destination_domain: CanonicalDomain,
        categories: Optional[Tuple[CrossDomainInteractionCategory, ...]] = None,
    ) -> "CrossDomainRoute":
        """Create a new routing rule."""
        return cls(
            source_domain=source_domain,
            destination_domain=destination_domain,
            category_match=categories or tuple(),
        )

    def matches(self, record: CrossDomainInteractionRecord) -> bool:
        """Check if this route matches the given interaction record."""
        # Check domain match
        if record.source_domain != self.source_domain:
            return False
        if record.destination_domain != self.destination_domain:
            return False

        # Check category match (if categories specified)
        if self.category_match and record.interaction_category not in self.category_match:
            return False

        return True


# =============================================================================
# DOMAIN VISIBILITY RULES
# =============================================================================


class DomainVisibility(Enum):
    """
    Visibility level of domain public interfaces.

    Each domain may expose public contracts at different visibility levels:

        PUBLIC      - Available to all domains (most visible)
        RESTRICTED  - Available only to specific domains
        INTERNAL    - Not exposed to other domains

    INVARIANTS:
        VIS-001: Visibility is explicit and declared
        VIS-002: Domain may never expose private implementation
        VIS-003: All cross-domain access uses public interfaces
    """

    PUBLIC = "public"      # Available to all domains
    RESTRICTED = "restricted"  # Available only to specific domains
    INTERNAL = "internal"  # Not exposed to other domains


@dataclass(frozen=True, slots=True)
class DomainPublicInterface:
    """
    Public interface exposed by a domain for cross-domain access.

    INVARIANTS:
        IFACE-001: Interface is immutable once declared
        IFACE-002: Interface never exposes private implementation
        IFACE-003: All cross-domain calls use these interfaces
    """

    interface_id: str = field(default_factory=lambda: f"iface_{uuid.uuid4().hex[:16]}")
    domain: CanonicalDomain
    name: str  # Interface name (e.g., "execute", "transport", "coordinate")
    visibility: DomainVisibility = DomainVisibility.PUBLIC

    # Method signatures for this interface
    methods: Tuple[str, ...] = field(default_factory=tuple)

    created_at_utc: float = field(default_factory=time.monotonic)


# =============================================================================
# DOMAIN OWNERSHIP PRESERVATION
# =============================================================================


@dataclass(frozen=True, slots=True)
class DomainOwnership:
    """
    Ownership record for a domain's responsibilities.

    Ownership shall never transfer across domain boundaries.

    OWNERSHIP BY DOMAIN:
        EXECUTION     - Owns scheduling and admission decisions
        STREAMS       - Owns transport mechanism and ordering
        NETWORKS      - Owns coordination logic and routing
        CAPABILITIES  - Owns computation logic
        SYSTEMS       - Owns persistent state
        CORE          - Owns infrastructure utilities
        ENTRYPOINTS   - Owns external interface handling

    INVARIANTS:
        OWN-001: Domain ownership is immutable
        OWN-002: Ownership never transfers through interactions
        OWN-003: External components may request but may not command
    """

    domain: CanonicalDomain
    owned_assets: Tuple[str, ...]  # What this domain owns (state, resources, etc.)
    owned_lifecycle: bool = True   # Owns lifecycle transitions

    @classmethod
    def execution(cls) -> "DomainOwnership":
        return cls(
            domain=CanonicalDomain.EXECUTION,
            owned_assets=("scheduling", "admission", "ordering"),
        )

    @classmethod
    def streams(cls) -> "DomainOwnership":
        return cls(
            domain=CanonicalDomain.STREAMS,
            owned_assets=("transport", "ordering", "provenance"),
        )

    @classmethod
    def systems(cls) -> "DomainOwnership":
        return cls(
            domain=CanonicalDomain.SYSTEMS,
            owned_assets=("persistent_state", "state_transitions", "persistence_policies"),
        )


# =============================================================================
# DOMAIN AUTHORITY PRESERVATION
# =============================================================================


@dataclass(frozen=True, slots=True)
class DomainAuthority:
    """
    Authority record for a domain's decision-making power.

    Authority remains local to the owning domain.

    AUTHORITY BY DOMAIN:
        EXECUTION     - Authority over scheduling and admission
        STREAMS       - Authority over transport semantics
        NETWORKS      - Authority over coordination logic
        CAPABILITIES  - Authority over computation results
        SYSTEMS       - Authority over state transitions
        CORE          - Authority over infrastructure decisions
        ENTRYPOINTS   - Authority over external interface handling

    INVARIANTS:
        AUTH-001: Authority is local to owning domain
        AUTH-002: Cross-domain interactions communicate intent, not authority
        AUTH-003: Receiving domains independently evaluate admission and authorization
    """

    domain: CanonicalDomain
    granted_authority: Tuple[str, ...]  # What decisions this domain can make

    @classmethod
    def execution(cls) -> "DomainAuthority":
        return cls(
            domain=CanonicalDomain.EXECUTION,
            granted_authority=("schedule", "admit", "order", "cancel"),
        )

    @classmethod
    def systems(cls) -> "DomainAuthority":
        return cls(
            domain=CanonicalDomain.SYSTEMS,
            granted_authority=("authorize_state_transition",),
        )


# =============================================================================
# OBSERVABILITY METADATA
# =============================================================================


@dataclass(frozen=True, slots=True)
class CrossDomainObservabilityMetadata:
    """
    Diagnostic metadata for cross-domain interactions.

    Every cross-domain interaction shall expose this immutable diagnostic
    information for observability purposes.

    REQUIRED FIELDS:
        - source_domain: Which domain sent the interaction
        - destination_domain: Which domain received it
        - interaction_id: Unique identifier
        - category: Type of cross-domain interaction
        - timestamps: Creation and routing times

    INVARIANTS:
        OBS-001: Metadata is always present and immutable
        OBS-002: Metadata never reveals private implementation details
        OBS-003: Metadata enables tracing across architectural layers
    """

    # Identification
    interaction_id: str
    source_domain: CanonicalDomain
    destination_domain: CanonicalDomain

    # Timestamps
    created_at_utc: float
    routed_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None

    # Routing information
    route_taken: Tuple[str, ...] = field(default_factory=tuple)
    retry_count: int = 0

    # Outcome
    outcome: str = "pending"  # pending, success, failure, deferred, rejected, cancelled

    @classmethod
    def create(cls, record: CrossDomainInteractionRecord) -> "CrossDomainObservabilityMetadata":
        """Create observability metadata from an interaction record."""
        return cls(
            interaction_id=record.interaction_id.value,
            source_domain=record.source_domain,
            destination_domain=record.destination_domain,
            created_at_utc=record.created_at_utc,
            outcome="pending",
        )

    def with_routing_hop(self, hop: str) -> "CrossDomainObservabilityMetadata":
        """Add a routing hop to the path."""
        return dataclass_replace(
            self,
            route_taken=self.route_taken + (hop,),
        )

    def mark_completed(self, result_type: CrossDomainResultType) -> "CrossDomainObservabilityMetadata":
        """Mark this interaction as completed with given result type."""
        return dataclass_replace(
            self,
            outcome=result_type.value,
            completed_at_utc=time.monotonic(),
        )


# =============================================================================
# CROSS-DOMAIN INTERACTION PROTOCOL
# =============================================================================


@runtime_checkable
class CrossDomainInteractionProtocol(Protocol):
    """
    Protocol for cross-domain interaction handling.

    Domains implement this protocol to participate in cross-domain interactions.

    INVARIANTS:
        PROC-001: Implementations must preserve domain ownership
        PROC-002: Implementations must verify external authority
        PROC-003: Implementations must produce observable results
    """

    @property
    def domain_id(self) -> CanonicalDomain:
        """Return the canonical domain ID for this implementation."""
        ...

    async def receive_interaction(
        self,
        record: CrossDomainInteractionRecord,
    ) -> Tuple[bool, Optional[CrossDomainResult]]:
        """
        Receive and process a cross-domain interaction.

        Args:
            record: The cross-domain interaction record to process

        Returns:
            Tuple of (success: bool, result: Optional[CrossDomainResult])
            - success: True if processed successfully
            - result: Result of processing (may be None for async)

        INVARIANTS:
            PROC-RCV-001: Must preserve domain ownership
            PROC-RCV-002: Must verify external authority
            PROC-RCV-003: Must return explicit result
        """
        ...

    async def send_interaction(
        self,
        record: CrossDomainInteractionRecord,
    ) -> Tuple[bool, Optional[CrossDomainResult]]:
        """
        Send a cross-domain interaction.

        Args:
            record: The interaction record to send

        Returns:
            Tuple of (success: bool, result: Optional[CrossDomainResult])
        """
        ...


# =============================================================================
# FAILURE TYPES
# =============================================================================


class CrossDomainFailureType(Enum):
    """
    Categories of cross-domain failures.

    FAILURES:
        BOUNDARY_VIOLATION  - Direct access to domain internals
        AUTHORITY_VIOLATION - Assuming authority not granted
        DEPENDENCY_VIOLATION - Implicit dependencies detected
        ROUTING_FAILURE     - No valid path between domains
        ADMISSION_FAILED    - Not admitted by destination domain
        AUTHORIZATION_FAILED - Authority verification failed
        LIFECYCLE_INCOMPATIBLE - Wrong state for interaction
        CONTRACT_VIOLATION  - Interaction type mismatch

    INVARIANTS:
        FAIL-001: All failures are explicit (never silent)
        FAIL-002: Failures preserve diagnostic metadata
        FAIL-003: Failures never corrupt interaction semantics
    """

    BOUNDARY_VIOLATION = "boundary_violation"     # Direct access to domain internals
    AUTHORITY_VIOLATION = "authority_violation"   # Assuming authority not granted
    DEPENDENCY_VIOLATION = "dependency_violation" # Implicit dependencies detected
    ROUTING_FAILURE = "routing_failure"           # No valid path between domains
    ADMISSION_FAILED = "admission_failed"         # Not admitted by destination domain
    AUTHORIZATION_FAILED = "authorization_failed" # Authority verification failed
    LIFECYCLE_INCOMPATIBLE = "lifecycle_incompatible"  # Wrong state for interaction
    CONTRACT_VIOLATION = "contract_violation"     # Interaction type mismatch


@dataclass(frozen=True, slots=True)
class CrossDomainFailure:
    """
    Record of a cross-domain failure.

    Failures shall be explicit and preserve immutable diagnostic information.
    """

    # Failure identity
    failure_id: str = field(default_factory=lambda: f"fail_{uuid.uuid4().hex[:16]}")

    # Context
    interaction_id: Optional[str] = None
    source_domain: Optional[CanonicalDomain] = None
    destination_domain: Optional[CanonicalDomain] = None

    # Failure details
    failure_type: CrossDomainFailureType
    timestamp_utc: float = field(default_factory=time.monotonic)

    # Diagnostic information
    error_message: str
    stack_trace: Optional[str] = None
    cause: Optional[str] = None

    # Recovery context
    can_recover: bool = False
    recovery_action: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert failure record to dictionary."""
        return {
            "failure_id": self.failure_id,
            "interaction_id": self.interaction_id,
            "source_domain": self.source_domain.value if self.source_domain else None,
            "destination_domain": self.destination_domain.value if self.destination_domain else None,
            "failure_type": self.failure_type.value,
            "timestamp_utc": self.timestamp_utc,
            "error_message": self.error_message,
            "can_recover": self.can_recover,
        }


# =============================================================================
# CANONICAL DOMAIN INTERACTION MATRIX
# =============================================================================

# Matrix of allowed cross-domain interactions:
# Key: (source_domain, destination_domain)
# Value: List of allowed interaction categories
ALLOWED_CROSS_DOMAIN_INTERACTIONS: Dict[
    Tuple[CanonicalDomain, CanonicalDomain],
    Tuple[CrossDomainInteractionCategory, ...]
] = {
    # Execution -> Execution (internal scheduling)
    (CanonicalDomain.EXECUTION, CanonicalDomain.EXECUTION): (
        CrossDomainInteractionCategory.EXECUTE_REQUEST,
        CrossDomainInteractionCategory.EXECUTE_RESPONSE,
    ),

    # Entrypoints -> Execution
    (CanonicalDomain.ENTRYPOINTS, CanonicalDomain.EXECUTION): (
        CrossDomainInteractionCategory.EXECUTE_REQUEST,
    ),

    # Core -> Execution
    (CanonicalDomain.CORE, CanonicalDomain.EXECUTION): (
        CrossDomainInteractionCategory.EXECUTE_REQUEST,
    ),

    # Execution -> Streams (publish results)
    (CanonicalDomain.EXECUTION, CanonicalDomain.STREAMS): (
        CrossDomainInteractionCategory.TRANSPORT_RESULT,
    ),

    # Networks -> Execution
    (CanonicalDomain.NETWORKS, CanonicalDomain.EXECUTION): (
        CrossDomainInteractionCategory.EXECUTE_REQUEST,
    ),

    # Capabilities -> Execution (report completion)
    (CanonicalDomain.CAPABILITIES, CanonicalDomain.EXECUTION): (
        CrossDomainInteractionCategory.EXECUTE_RESPONSE,
    ),

    # Systems -> Execution (request state transition publication)
    (CanonicalDomain.SYSTEMS, CanonicalDomain.EXECUTION): (
        CrossDomainInteractionCategory.EXECUTE_RESPONSE,
    ),
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


def is_cross_domain_allowed(source: CanonicalDomain, dest: CanonicalDomain) -> bool:
    """
    Check if cross-domain interaction from source to destination is allowed.

    Args:
        source: Source domain
        dest: Destination domain

    Returns:
        True if the cross-domain interaction is allowed by architectural rules
    """
    return (source, dest) in ALLOWED_CROSS_DOMAIN_INTERACTIONS


def get_allowed_categories(source: CanonicalDomain, dest: CanonicalDomain) -> Tuple[CrossDomainInteractionCategory, ...]:
    """
    Get allowed interaction categories between two domains.

    Args:
        source: Source domain
        dest: Destination domain

    Returns:
        Tuple of allowed interaction categories (empty if not allowed)
    """
    key = (source, dest)
    return ALLOWED_CROSS_DOMAIN_INTERACTIONS.get(key, ())


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Domain identifiers
    "DomainId",
    "CanonicalDomain",

    # Cross-domain interaction types
    "CrossDomainInteractionCategory",
    "CrossDomainInteractionId",
    "CrossDomainCorrelation",

    # Interaction records
    "CrossDomainInteractionRecord",

    # Results
    "CrossDomainResultType",
    "CrossDomainResult",

    # Routing
    "CrossDomainRoute",

    # Visibility rules
    "DomainVisibility",
    "DomainPublicInterface",

    # Ownership and Authority
    "DomainOwnership",
    "DomainAuthority",

    # Observability
    "CrossDomainObservabilityMetadata",

    # Protocol
    "CrossDomainInteractionProtocol",

    # Failures
    "CrossDomainFailureType",
    "CrossDomainFailure",

    # Matrix
    "ALLOWED_CROSS_DOMAIN_INTERACTIONS",

    # Utility functions
    "dataclass_replace",
    "is_cross_domain_allowed",
    "get_allowed_categories",
]