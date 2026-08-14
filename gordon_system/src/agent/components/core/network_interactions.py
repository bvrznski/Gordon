# Phase 3.14.7 — Network Interaction Contracts
# =============================================
"""
Canonical Network Interaction Contracts for Gordon.

This module establishes the immutable contracts governing every interaction
involving Cognitive Networks. Networks participate in Interactions without
owning or redefining them.

ARCHITECTURAL PRINCIPLES
------------------------
Execution schedules.
Streams transport.
Interactions communicate.
Networks process cognition.

Interactions involving Networks shall coordinate architectural cooperation
without altering the internal semantics of any Network.

NETWORK PARTICIPATION SEMANTICS
-------------------------------
A Network may participate in an Interaction as:
- initiator
- recipient
- publisher
- subscriber
- observer
- coordinator

Participation shall be explicit.
Participation shall never imply authority.
Participation shall never imply ownership.

NETWORK ACTIVATION
------------------
Interaction shall not activate Networks directly.
Execution activates Networks.
Interactions may request participation.
Execution determines:
  - admission
  - scheduling
  - ordering
  - cancellation
  - completion

Activation remains an Execution responsibility.

NETWORK CONTRACT
----------------
Networks shall:
- receive Interactions
- evaluate Interactions
- emit Interactions
- publish Events
- emit Signals
- produce Proposals
- produce Observations

Networks shall never:
- redefine Interaction categories
- redefine ownership
- redefine authority
- mutate transport semantics
- bypass Execution
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, FrozenSet, Any
import uuid
import time


# =============================================================================
# NETWORK PARTICIPATION ROLES
# =============================================================================

class NetworkParticipationRole(Enum):
    """
    Roles a Network may assume in an Interaction.
    
    Each role defines how the Network contributes to the interaction
    while preserving its architectural independence.
    
    ROLES:
    - INITIATOR: The Network that starts the interaction
    - RECIPIENT: A Network that receives and processes the interaction
    - PUBLISHER: A Network that publishes results or observations
    - SUBSCRIBER: A Network that subscribes to related interactions
    - OBSERVER: A Network that observes without active participation
    - COORDINATOR: A Network that coordinates multiple participants
    
    SEMANTICS:
    - Roles are explicit and declared at interaction creation
    - Roles never grant authority
    - Roles never imply ownership of the interaction
    """
    
    INITIATOR = "initiator"       # The Network initiating the interaction
    RECIPIENT = "recipient"       # A Network receiving the interaction
    PUBLISHER = "publisher"       # A Network publishing results
    SUBSCRIBER = "subscriber"     # A Network subscribing to related interactions
    OBSERVER = "observer"         # A Network observing without active role
    COORDINATOR = "coordinator"   # A Network coordinating multiple participants


# =============================================================================
# NETWORK INTERACTION PARTICIPATION RECORD
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkParticipation:
    """
    Record of a Network's participation in an Interaction.
    
    Every Network that participates in an interaction shall be recorded
    with explicit role assignment and timestamped participation.
    
    PARTICIPATION INVARIANTS:
    - P-001: Every participant has exactly one primary role
    - P-002: Participation is always explicit (never implicit)
    - P-003: Role never grants authority
    - P-004: Role never implies ownership
    - P-005: Network identity is preserved
    """
    
    network_id: str  # Unique identifier for the participating network
    role: NetworkParticipationRole  # The role assumed in this interaction
    participated_at_utc: float  # When the network joined the interaction
    
    # Optional context
    capabilities_requested: Tuple[str, ...] = field(default_factory=tuple)
    capabilities_provided: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(
        cls,
        network_id: str,
        role: NetworkParticipationRole,
        capabilities_requested: Optional[Tuple[str, ...]] = None,
        capabilities_provided: Optional[Tuple[str, ...]] = None,
    ) -> "NetworkParticipation":
        """Create a new network participation record."""
        return cls(
            network_id=network_id,
            role=role,
            participated_at_utc=time.monotonic(),
            capabilities_requested=capabilities_requested or (),
            capabilities_provided=capabilities_provided or (),
        )
    
    def with_capability(self, capability: str, *, provided: bool = False) -> "NetworkParticipation":
        """Create a new participation record with an additional capability."""
        if provided:
            return dataclass_replace(
                self,
                capabilities_provided=self.capabilities_provided + (capability,)
            )
        else:
            return dataclass_replace(
                self,
                capabilities_requested=self.capabilities_requested + (capability,)
            )


# =============================================================================
# NETWORK ACTIVATION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkActivationRequest:
    """
    Request from an Interaction for a Network to participate.
    
    Activation requests are sent by Interactions to Execution.
    Execution determines admission and scheduling.
    
    INVARIANTS:
    - A-001: Request never guarantees activation
    - A-002: Request never implies authority
    - A-003: Request is always asynchronous (non-blocking)
    - A-004: Request may be cancelled by Execution
    """
    
    request_id: str  # Unique identifier for this request
    interaction_id: str  # Which interaction requested activation
    network_id: str  # Which network is being activated
    requested_at_utc: float  # When the request was made
    
    # Activation parameters
    capabilities_required: Tuple[str, ...] = field(default_factory=tuple)
    priority: int = 0  # Higher = more urgent ( Execution decides interpretation )
    
    # Lifecycle state
    state: str = "pending"  # pending, admitted, scheduled, active, completed, cancelled
    
    @classmethod
    def create(
        cls,
        interaction_id: str,
        network_id: str,
        capabilities_required: Optional[Tuple[str, ...]] = None,
        priority: int = 0,
    ) -> "NetworkActivationRequest":
        """Create a new activation request."""
        return cls(
            request_id=f"act_req_{uuid.uuid4().hex[:16]}",
            interaction_id=interaction_id,
            network_id=network_id,
            requested_at_utc=time.monotonic(),
            capabilities_required=capabilities_required or (),
            priority=priority,
            state="pending",
        )


# =============================================================================
# NETWORK ACTIVATION RESULT
# =============================================================================

class ActivationDecision(Enum):
    """Decisions that Execution may make about an activation request."""
    
    ADMIT = "admit"           # Request admitted, scheduled for execution
    REJECT = "reject"         # Request rejected (e.g., invalid, unauthorized)
    WAIT = "wait"             # Request queued, waiting for resources
    CANCEL = "cancel"         # Request cancelled by Execution


@dataclass(frozen=True, slots=True)
class NetworkActivationResult:
    """
    Result of an activation request evaluation.
    
    Generated by Execution in response to a NetworkActivationRequest.
    May be invoked by Streams as transport mechanism.
    
    RESULTS INVARIANTS:
    - R-001: Result is immutable once produced
    - R-002: Result never implies ownership
    - R-003: Result may be observed but not modified
    """
    
    request_id: str  # Which request this responds to
    decision: ActivationDecision  # The decision made by Execution
    
    # Timing information
    evaluated_at_utc: float  # When the decision was made
    requested_at_utc: float  # When the original request was made
    
    # Decision context
    reason: str  # Human-readable explanation for the decision
    admission_context: Optional[str] = None  # Contextual information (e.g., resource constraints)
    
    @classmethod
    def create_admission(
        cls,
        request_id: str,
        requested_at_utc: float,
        evaluated_at_utc: Optional[float] = None,
    ) -> "NetworkActivationResult":
        """Create an admission result."""
        return cls(
            request_id=request_id,
            decision=ActivationDecision.ADMIT,
            evaluated_at_utc=evaluated_at_utc or time.monotonic(),
            requested_at_utc=requested_at_utc,
            reason="Request admitted for execution",
        )
    
    @classmethod
    def create_rejection(
        cls,
        request_id: str,
        requested_at_utc: float,
        reason: str,
        evaluated_at_utc: Optional[float] = None,
    ) -> "NetworkActivationResult":
        """Create a rejection result."""
        return cls(
            request_id=request_id,
            decision=ActivationDecision.REJECT,
            evaluated_at_utc=evaluated_at_utc or time.monotonic(),
            requested_at_utc=requested_at_utc,
            reason=f"Request rejected: {reason}",
        )
    
    @classmethod
    def create_wait(
        cls,
        request_id: str,
        requested_at_utc: float,
        wait_reason: str = "awaiting_resources",
        evaluated_at_utc: Optional[float] = None,
    ) -> "NetworkActivationResult":
        """Create a wait result."""
        return cls(
            request_id=request_id,
            decision=ActivationDecision.WAIT,
            evaluated_at_utc=evaluated_at_utc or time.monotonic(),
            requested_at_utc=requested_at_utc,
            reason=f"Request queued: {wait_reason}",
        )
    
    @classmethod
    def create_cancel(
        cls,
        request_id: str,
        requested_at_utc: float,
        reason: str = "cancelled_by_execution",
        evaluated_at_utc: Optional[float] = None,
    ) -> "NetworkActivationResult":
        """Create a cancel result."""
        return cls(
            request_id=request_id,
            decision=ActivationDecision.CANCEL,
            evaluated_at_utc=evaluated_at_utc or time.monotonic(),
            requested_at_utc=requested_at_utc,
            reason=f"Request cancelled: {reason}",
        )
    
    def is_admitted(self) -> bool:
        """Check if activation was admitted."""
        return self.decision == ActivationDecision.ADMIT
    
    def is_rejected(self) -> bool:
        """Check if activation was rejected."""
        return self.decision == ActivationDecision.REJECT
    
    def is_wait(self) -> bool:
        """Check if activation is waiting."""
        return self.decision == ActivationDecision.WAIT
    
    def is_cancelled(self) -> bool:
        """Check if activation was cancelled."""
        return self.decision == ActivationDecision.CANCEL


# =============================================================================
# NETWORK ACTIVATION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkActivationContext:
    """
    Context information for network activation.
    
    Contains all metadata needed by Execution to schedule and manage
    the activation of a Network as part of an Interaction.
    
    CONTEXT INVARIANTS:
    - C-001: Context is immutable once created
    - C-002: Context never implies ownership
    - C-003: Context may be observed for diagnostics
    """
    
    activation_id: str  # Unique identifier for this activation instance
    
    # Interaction context
    interaction_id: str  # Which interaction triggered this activation
    network_id: str  # Which network is being activated
    
    # Timestamps (must come before default fields)
    created_at_utc: float  # When the context was created
    
    # Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)
    deadline_utc: Optional[float] = None  # Optional deadline for completion
    
    # Resource constraints
    resource_budget: Dict[str, int] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        interaction_id: str,
        network_id: str,
        execution_context: Optional[Dict[str, Any]] = None,
        deadline_utc: Optional[float] = None,
        resource_budget: Optional[Dict[str, int]] = None,
    ) -> "NetworkActivationContext":
        """Create a new activation context."""
        return cls(
            activation_id=f"act_ctx_{uuid.uuid4().hex[:16]}",
            interaction_id=interaction_id,
            network_id=network_id,
            execution_context=execution_context or {},
            created_at_utc=time.monotonic(),
            deadline_utc=deadline_utc,
            resource_budget=resource_budget or {},
        )
    
    def with_execution_context(self, context: Dict[str, Any]) -> "NetworkActivationContext":
        """Create a new context with merged execution context."""
        return dataclass_replace(
            self,
            execution_context={**self.execution_context, **context}
        )


# =============================================================================
# NETWORK INTERACTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkInteraction:
    """
    Interaction involving Cognitive Networks.
    
    Every interaction that involves Networks shall use this canonical
    structure. Networks participate without ownership or redefinition.
    
    CANONICAL MODEL:
        Execution
            │
            ▼
        Interaction
            │
            ▼
        Network Admission
            │
            ▼
        Network Processing
            │
            ▼
        Interaction Result
            │
            ▼
        Publication
    
    INVARIANTS:
    - NI-001: Networks never own interactions
    - NI-002: Networks never redefine interaction semantics
    - NI-003: Networks always preserve architectural independence
    - NI-004: Execution remains sole authority for scheduling
    """
    
    # Interaction identity (canonical)
    interaction_id: str  # Unique identifier
    category: str  # Interaction category (Request, Event, etc.)
    created_at_utc: float  # When the interaction was created
    
    # Network participation
    initiator_network_id: Optional[str] = None  # Which network initiated (if any)
    participant_networks: Tuple[NetworkParticipation, ...] = field(default_factory=tuple)
    
    # Semantic content
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        category: str,
        interaction_id: Optional[str] = None,
        initiator_network_id: Optional[str] = None,
        participants: Optional[Tuple[NetworkParticipation, ...]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> "NetworkInteraction":
        """Create a new network interaction."""
        now = time.monotonic()
        return cls(
            interaction_id=interaction_id or f"net_int_{uuid.uuid4().hex[:16]}",
            category=category,
            created_at_utc=now,
            initiator_network_id=initiator_network_id,
            participant_networks=participants or (),
            payload=payload or {},
            execution_context={"created_at": now},
        )
    
    def add_participant(
        self,
        network_id: str,
        role: NetworkParticipationRole,
    ) -> "NetworkInteraction":
        """Create a new interaction with an additional participant."""
        new_participants = self.participant_networks + (
            NetworkParticipation.create(network_id, role),
        )
        return dataclass_replace(
            self,
            participant_networks=new_participants
        )
    
    def is_initiator(self, network_id: str) -> bool:
        """Check if a network was the initiator."""
        return self.initiator_network_id == network_id
    
    def get_participant_roles(self, network_id: str) -> Tuple[NetworkParticipationRole, ...]:
        """Get all roles assumed by a network in this interaction."""
        return tuple(
            p.role for p in self.participant_networks
            if p.network_id == network_id
        )
    
    def has_network_participation(self, network_id: str) -> bool:
        """Check if a network participates in this interaction."""
        return (
            self.initiator_network_id == network_id or
            any(p.network_id == network_id for p in self.participant_networks)
        )


# =============================================================================
# NETWORK OBSERVABILITY METADATA
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkInteractionObservabilityMetadata:
    """
    Diagnostic metadata exposed by every Network Interaction.
    
    Every interaction involving Networks shall expose this immutable
    diagnostic information for observability purposes.
    
    OBSERVABILITY INVARIANTS:
    - O-001: Metadata is always present and immutable
    - O-002: Metadata never reveals private Network internals
    - O-003: Metadata enables tracing across architectural layers
    """
    
    # Identification
    interaction_id: str  # Which interaction this metadata describes
    
    # Timestamps (must come before default fields)
    interaction_created_at_utc: float
    
    network_id: Optional[str] = None  # Which network (if single-network context)
    interaction_completed_at_utc: Optional[float] = None
    
    # Participation
    participant_count: int = 0
    participant_roles: Tuple[str, ...] = field(default_factory=tuple)
    
    # Execution context
    execution_context_id: Optional[str] = None
    stream_context_id: Optional[str] = None
    
    # Outcome
    outcome: str = "pending"  # pending, success, failure, cancelled
    integrity_status: str = "verified"  # verified, unknown, compromised
    
    @classmethod
    def create(
        cls,
        interaction_id: str,
        network_id: Optional[str] = None,
        participant_roles: Optional[Tuple[str, ...]] = None,
        execution_context_id: Optional[str] = None,
        stream_context_id: Optional[str] = None,
    ) -> "NetworkInteractionObservabilityMetadata":
        """Create new observability metadata."""
        return cls(
            interaction_id=interaction_id,
            network_id=network_id,
            interaction_created_at_utc=time.monotonic(),
            participant_count=len(participant_roles or ()),
            participant_roles=participant_roles or (),
            execution_context_id=execution_context_id,
            stream_context_id=stream_context_id,
            outcome="pending",
        )
    
    def with_outcome(self, outcome: str) -> "NetworkInteractionObservabilityMetadata":
        """Create new metadata with updated outcome."""
        return dataclass_replace(
            self,
            outcome=outcome,
            interaction_completed_at_utc=time.monotonic()
        )


# =============================================================================
# NETWORK FAILURE TYPES
# =============================================================================

class NetworkActivationFailureType(Enum):
    """Categories of network activation failures."""
    
    ACTIVATION_FAILED = "activation_failed"      # Activation could not proceed
    ADMISSION_FAILED = "admission_failed"         # Not admitted by Execution
    EXECUTION_FAILED = "execution_failed"         # Execution encountered error
    ROUTING_FAILED = "routing_failed"             # Could not route to network
    DEPENDENCY_FAILED = "dependency_failed"       # Missing dependency
    INTERRUPTION = "interruption"                 # Interrupted by external factor
    CANCELLATION = "cancellation"                 # Cancelled by policy


@dataclass(frozen=True, slots=True)
class NetworkInteractionFailure:
    """
    Record of a failure in network interaction.
    
    Failures shall be explicit and preserve immutable diagnostic information.
    
    FAILURE INVARIANTS:
    - F-001: Failures are always explicit (never silent)
    - F-002: Failure records are immutable
    - F-003: Failures enable root cause analysis
    """
    
    failure_id: str  # Unique identifier for this failure record
    
    # Context
    interaction_id: str  # Which interaction failed
    
    # Failure details (must come BEFORE optional fields like network_id)
    failure_type: NetworkActivationFailureType
    timestamp_utc: float
    
    # Diagnostic information (these have no defaults and must come BEFORE network_id which has default)
    error_message: str  # Must come before optional field network_id
    
    stack_trace: Optional[str] = None
    cause: Optional[str] = None
    
    network_id: Optional[str] = None  # Which network (if applicable) - now after all required fields
    
    # Recovery context (these have defaults and can follow diagnostics)
    can_recover: bool = False
    recovery_action: Optional[str] = None
    
    @classmethod
    def create_activation_failure(
        cls,
        interaction_id: str,
        network_id: Optional[str],
        error_message: str,
        timestamp_utc: Optional[float] = None,
    ) -> "NetworkInteractionFailure":
        """Create an activation failure record."""
        return cls(
            failure_id=f"fail_{uuid.uuid4().hex[:16]}",
            interaction_id=interaction_id,
            network_id=network_id,
            failure_type=NetworkActivationFailureType.ACTIVATION_FAILED,
            timestamp_utc=timestamp_utc or time.monotonic(),
            error_message=error_message,
        )
    
    @classmethod
    def create_admission_failure(
        cls,
        interaction_id: str,
        network_id: Optional[str],
        reason: str,
        timestamp_utc: Optional[float] = None,
    ) -> "NetworkInteractionFailure":
        """Create an admission failure record."""
        return cls(
            failure_id=f"fail_{uuid.uuid4().hex[:16]}",
            interaction_id=interaction_id,
            network_id=network_id,
            failure_type=NetworkActivationFailureType.ADMISSION_FAILED,
            timestamp_utc=timestamp_utc or time.monotonic(),
            error_message=f"Admission denied: {reason}",
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# CANONICAL INTERACTION FLOW
# =============================================================================

def get_canonical_network_interaction_flow() -> Tuple[str, ...]:
    """
    Return the canonical flow of Network interactions.
    
    This defines the expected sequence of states and transitions
    for any interaction involving Networks.
    """
    return (
        "Execution_Schedules",
        "Interaction_Created",
        "Network_Admission_Pending",
        "Network_Eligibility_Determined",
        "Activation_Requested",
        "Network_Processing_Started",
        "Interaction_Result_Computed",
        "Publication_Prepared",
        "Stream_Transport",
    )


# =============================================================================
# ARCHITECTURAL CONSTRAINTS
# =============================================================================

ARCHITECTURAL_CONSTRAINTS: FrozenSet[str] = frozenset({
    # Ownership constraints
    "Networks_do_not_own_interactions",
    "Execution_owns_scheduling",
    "Streams_own_transport",
    "Interactions_own_communication_semantics",
    
    # Authority constraints
    "Network_participation_never_grants_authority",
    "Interaction_participation_never_grants_authority",
    "Authority_remains_external_to_network_participation",
    
    # Participation constraints
    "Participation_must_be_explicit",
    "Participation_never_implies_ownership",
    "Participation_never_implies_authority",
})

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Roles
    "NetworkParticipationRole",
    
    # Participation records
    "NetworkParticipation",
    "NetworkInteraction",
    
    # Activation contracts
    "NetworkActivationRequest",
    "NetworkActivationResult",
    "NetworkActivationContext",
    "ActivationDecision",
    
    # Observability
    "NetworkInteractionObservabilityMetadata",
    
    # Failures
    "NetworkActivationFailureType",
    "NetworkInteractionFailure",
    
    # Utility functions
    "dataclass_replace",
    "get_canonical_network_interaction_flow",
    "ARCHITECTURAL_CONSTRAINTS",
]