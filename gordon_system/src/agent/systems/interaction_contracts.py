# System Interaction Contracts - Phase 3.14.9
# ============================================
#
# Canonical architectural contracts governing all interactions involving Systems.
#
# This module establishes immutable contracts for:
#   - System admission semantics
#   - State access rules and interfaces
#   - State mutation rules and interfaces
#   - Transaction boundaries
#   - Ownership preservation
#   - Authority preservation
#   - Execution integration
#   - Stream integration
#   - Network integration
#   - Capability integration
#   - Replay compatibility
#   - Observability requirements
#   - Failure semantics
#   - Security requirements

"""
Canonical System Interaction Contracts for Gordon Phase 3.14.9.

This module establishes the immutable contracts governing all interactions
involving Systems. Systems are the authoritative owners of persistent state.
All other architectural components interact with Systems through explicit,
typed contracts that preserve ownership, authority, and integrity.

ARCHITECTURAL PRINCIPLES:
========================

Execution schedules work.
Interactions communicate intent.
Streams transport information.
Networks perform cognitive coordination.
Capabilities perform computation.
Systems own state.

Ownership Model:
- Systems exclusively own persistent state
- Systems determine whether their state changes
- External components may never directly modify System state
- Ownership remains unchanged through all interactions

Authority Model:
- Only Systems authorize state transitions
- External participants may request, propose, or recommend mutations
- No external component may bypass System validation
- Authority is never delegated through Interactions or Streams

Canonical Interaction Flow:
    Execution
        │
        ▼
    Interaction
        │
        ▼
    System Admission
        │
        ▼
    State Transition Decision
        │
        ▼
    Commit (System-only)
        │
        ▼
    Publication (to Streams)

STATE OWNERSHIP INVARIANTS:
==========================

SI-OWN-001: Systems exclusively own persistent state
SI-OWN-002: Only Systems determine whether their state changes
SI-OWN-003: External components may request, propose, or recommend mutations
SI-OWN-004: External components may never directly modify System state
SI-OWN-005: State ownership is never transferred through interactions

STATE MUTATION INVARIANTS:
===========================

SI-MUT-001: Only Systems may commit state transitions
SI-MUT-002: Mutations must be explicitly authorized by owning System
SI-MUT-003: External components may never bypass System validation
SI-MUT-004: Every mutation produces immutable transition metadata

LIFECYCLE INVARIANTS:
=====================

SI-LC-001: Every System interaction has explicit lifecycle state
SI-LC-002: Lifecycle transitions are deterministic and observable
SI-LC-003: Terminal states never transition to non-terminal states
SI-LC-004: Invalid transitions shall be rejected

AUTHORITY INVARIANTS:
=====================

SI-AUTH-001: Authority to mutate state belongs exclusively to owning System
SI-AUTH-002: Interactions may request but may not command
SI-AUTH-003: Capabilities may compute but may not commit
SI-AUTH-004: Networks may recommend but may not authorize

TRANSACTION INVARIANTS:
=======================

SI-TX-001: Systems define transactional boundaries
SI-TX-002: External components may participate but never own transactions
SI-TX-003: Transactions shall not span multiple System owners without coordination protocol
SI-TX-004: Transaction commits are atomic per System

REPLAY INVARIANTS:
==================

SI-RPLY-001: Replay shall preserve interaction ordering
SI-RPLY-002: Replay shall preserve state transition ordering
SI-RPLY-003: Replay shall never fabricate committed state transitions
SI-RPLY-004: Replay shall never bypass System validation

OBSERVABILITY INVARIANTS:
=========================

SI-OBS-001: Every System interaction exposes immutable diagnostic metadata
SI-OBS-002: Private System implementation details remain protected
SI-OBS-003: All lifecycle transitions are observable
SI-OBS-004: Outcome publication preserves provenance
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto
import time
import uuid


# =============================================================================
# IDENTITY TYPES - System Interaction
# =============================================================================


@dataclass(frozen=True, slots=True)
class SystemInteractionId:
    """Unique semantic identity for one system interaction."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def generate(cls) -> "SystemInteractionId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True, slots=True)
class SystemAdmissionId:
    """Unique semantic identity for one system admission decision."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def generate(cls) -> "SystemAdmissionId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True, slots=True)
class SystemTransitionId:
    """Unique semantic identity for one system state transition."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def generate(cls) -> "SystemTransitionId":
        return cls(value=str(uuid.uuid4()))


# =============================================================================
# SYSTEM IDENTIFIERS AND LIFECYCLE STATE
# =============================================================================


class SystemLifecycleState(Enum):
    """
    Canonical lifecycle states for Systems.

    Transitions:
        CREATED → READY → ACTIVE
            ├─► MAINTENANCE (maintenance requested)
            └─► TERMINATED (shutdown initiated)

        MAINTENANCE → TERMINATED

    Terminal states: TERMINATED, FAILED

    Invariants:
        LC-001: Lifecycle progression shall remain deterministic
        LC-002: Invalid transitions shall be rejected
        LC-003: Each transition shall produce observable event
        LC-004: Terminal states never transition to non-terminal states
    """

    CREATED = "created"           # System initialized but not yet ready
    READY = "ready"               # System is ready to receive interactions
    ACTIVE = "active"             # System is actively processing interactions
    MAINTENANCE = "maintenance"   # Maintenance mode (read-only or limited)
    TERMINATED = "terminated"     # System shutdown complete
    FAILED = "failed"             # System entered error state


def is_system_terminal_state(state: SystemLifecycleState) -> bool:
    """Check if a system lifecycle state is terminal."""
    return state in {
        SystemLifecycleState.TERMINATED,
        SystemLifecycleState.FAILED,
    }


# =============================================================================
# SYSTEM INTERACTION CATEGORIES
# =============================================================================


class SystemInteractionCategory(Enum):
    """
    Categories of interactions with Systems.

    Each category defines the expected behavior and authority requirements:

    STATE_ACCESS: Read operations on system state (may or may not require write)
    STATE_MUTATION: Write operations that change system state
    TRANSACTION_MANAGEMENT: Operations managing transaction boundaries
    QUERY: Ad-hoc queries against system state (not part of normal workflow)
    CONTROL: System control operations (start, stop, configure)

    Invariants:
        CAT-001: Category determines authority requirements
        CAT-002: Category determines allowed transitions
        CAT-003: Category never implies ownership or authority
    """

    STATE_ACCESS = "state_access"           # Read system state
    STATE_MUTATION = "state_mutation"       # Write/modify system state
    TRANSACTION_MANAGEMENT = "transaction_management"  # Transaction boundaries
    QUERY = "query"                         # Ad-hoc query operations
    CONTROL = "control"                     # System control operations


# =============================================================================
# SYSTEM INTERACTION CONTEXT
# =============================================================================


@dataclass(frozen=True, slots=True)
class SystemInteractionContext:
    """
    Immutable context for system interactions.

    Contains all information needed to evaluate an interaction with a System.
    This is NOT a service locator - it contains only interaction-specific data.

    Invariants:
        IC-001: Context shall be interaction-scoped
        IC-002: Context shall not become an unrestricted service locator
        IC-003: Context contents shall be explicitly declared and typed
    """

    # Identity (required - no defaults)
    interaction_id: SystemInteractionId
    system_id: str  # Which system is being interacted with

    # Lifecycle state
    lifecycle_state: SystemLifecycleState = SystemLifecycleState.CREATED

    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    evaluated_at_utc: Optional[float] = None
    decision_at_utc: Optional[float] = None

    # Initiator (who requested this interaction)
    initiator_id: str = "unknown"
    initiator_type: str = "system"  # e.g., "user", "system", "scheduled"

    # Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)

    # Category of this interaction
    category: SystemInteractionCategory = SystemInteractionCategory.STATE_ACCESS

    # Authority context (for evaluation)
    authority_verified: bool = False
    authorization_source: Optional[str] = None  # Where authority was verified

    def with_state(self, new_state: SystemLifecycleState) -> "SystemInteractionContext":
        """Create a copy with updated lifecycle state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            evaluated_at_utc=self.evaluated_at_utc if new_state != SystemLifecycleState.CREATED else time.time()
        )

    def with_decision(self, decision: "SystemAdmissionDecision") -> "SystemInteractionContext":
        """Create a copy with admission decision recorded."""
        return dataclass_replace(
            self,
            decision_at_utc=time.time(),
            authority_verified=decision.is_admitted() or decision.is_deferred(),
        )


# =============================================================================
# SYSTEM ADMISSION CONTEXT
# =============================================================================


@dataclass(frozen=True, slots=True)
class SystemAdmissionContext:
    """
    Context for system admission evaluation.

    Contains all information needed to decide whether an interaction with a
    System may proceed. Admission is explicit - implicit admission is prohibited.

    Invariants:
        AC-001: Admission shall never imply authority
        AC-002: Implicit admission is prohibited - explicit outcome required
        AC-003: Every admission decision shall be observable
    """

    # Identity
    admission_id: SystemAdmissionId

    # Interaction context being admitted
    interaction_context: SystemInteractionContext

    # Admission criteria to verify
    system_available: bool = True              # Is the system operational?
    lifecycle_compatible: bool = True          # Is lifecycle state compatible?
    ownership_compatible: bool = True          # Does ownership match?

    # Authority verification (external to computation)
    authority_verified: bool = False           # Has external authority verified?
    dependency_ready: bool = True              # Are dependencies satisfied?

    # Policy verification
    security_policy_passed: bool = True        # Security policy check passed
    privacy_policy_passed: bool = True         # Privacy policy check passed

    # Transaction context
    transaction_compatible: bool = True        # Compatible with existing transactions
    transaction_context: Optional[str] = None  # Existing transaction ID if any

    # Admission outcome
    decision: "SystemAdmissionDecision" = field(default_factory=lambda: SystemAdmissionDecision.ADMIT)
    rejection_reason: Optional[str] = None

    evaluated_at_utc: float = field(default_factory=time.time)


class SystemAdmissionDecision(Enum):
    """
    Result of system admission evaluation.

    Invariants:
        DEC-001: All decisions are explicit
        DEC-002: Decisions shall never imply ownership or authority
        DEC-003: Decisions shall be observable and traceable
    """

    ADMIT = "admit"                     # Interaction may proceed to state evaluation
    WAIT = "wait"                       # Wait for dependencies/resources/capacity
    REJECT = "reject"                   # Permanent rejection (e.g., policy violation)
    DEFER = "defer"                     # Defer until later (not cancelled, just postponed)
    CANCEL = "cancel"                   # Cancel due to external request or lifecycle


def is_admission_terminal(decision: SystemAdmissionDecision) -> bool:
    """Check if an admission decision is terminal."""
    return decision in {
        SystemAdmissionDecision.REJECT,
        SystemAdmissionDecision.CANCEL,
    }


# =============================================================================
# STATE ACCESS TYPES
# =============================================================================


class StateAccessMode(Enum):
    """
    Modes of state access.

    READ: Access state for reading only. No mutation allowed.
    SNAPSHOT: Create a point-in-time snapshot for read consistency.
    CONSENSUS: Read with consensus guarantees (may be slower).

    Invariants:
        ACCESS-001: Mode determines whether mutation is possible
        ACCESS-002: Mode never grants authority to mutate
        ACCESS-003: Mode shall be immutable once set
    """

    READ = "read"           # Read state only, no validation required
    SNAPSHOT = "snapshot"   # Create point-in-time snapshot for consistency
    CONSENSUS = "consensus" # Read with consensus guarantees


@dataclass(frozen=True, slots=True)
class StateAccessRequest:
    """
    Request to access System state.

    Invariants:
        ACCESS-REQ-001: Access request shall be explicit
        ACCESS-REQ-002: Access request shall never imply authority
        ACCESS-REQ-003: Access request shall preserve provenance
    """

    # Identity
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_id: str

    # What to access
    key_path: Tuple[str, ...]  # Dot-separated path to state entry
    access_mode: StateAccessMode = StateAccessMode.READ

    # Context
    transaction_context: Optional[str] = None  # Join existing transaction?
    consistency_level: int = 1                 # How fresh must data be? (0-5)

    # Timestamp bounds
    as_of_utc: Optional[float] = None          # Read state at specific time

    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True, slots=True)
class StateAccessResult:
    """
    Result of a state access request.

    Invariants:
        ACCESS-RES-001: Result shall preserve identity
        ACCESS-RES-002: Result shall never reveal private implementation details
        ACCESS-RES-003: Result integrity shall be verifiable
    """

    # Identity (required)
    request_id: str
    system_id: str

    # Access result
    found: bool  # Was the key found?

    # Value (if found) - should only expose public interface, not internals
    value: Optional[Dict[str, Any]] = None

    # Version information for integrity verification
    version: Optional[int] = None
    timestamp_utc: Optional[float] = None

    # Integrity metadata
    integrity_hash: Optional[str] = None  # Hash of the value for verification

    accessed_at_utc: float = field(default_factory=time.time)

    def to_public_access(self) -> "PublicStateAccess":
        """Convert to public access record."""
        return PublicStateAccess(
            system_id=self.system_id,
            key_path=list(self.key_path) if hasattr(self, 'key_path') else [],
            value=self.value,
            version=self.version,
            timestamp_utc=self.timestamp_utc,
            accessed_at_utc=self.accessed_at_utc,
        )


# =============================================================================
# STATE MUTATION TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class StateMutationRequest:
    """
    Request to mutate System state.

    External participants may REQUEST mutations but may never COMMIT them.
    Only the owning System may commit mutations.

    Invariants:
        MUT-REQ-001: Mutation request shall be explicit
        MUT-REQ-002: Mutation request shall never imply authority
        MUT-REQ-003: Mutation request shall include all required validation data
    """

    # Identity
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_id: str

    # What to mutate
    key_path: Tuple[str, ...]
    new_value: Dict[str, Any]  # Complete replacement value
    expected_version: Optional[int] = None  # For optimistic locking

    # Validation context (what the System should verify)
    validation_data: Dict[str, Any] = field(default_factory=dict)

    # Transaction context
    transaction_context: Optional[str] = None

    # Timestamps
    requested_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True, slots=True)
class StateMutationProposal:
    """
    Proposed mutation that System may evaluate.

    This is the canonical way external participants propose state changes.
    The owning System evaluates and decides whether to commit.

    Invariants:
        MUT-PROP-001: Proposal shall be explicit
        MUT-PROP-002: Proposal shall never imply authority
        MUT-PROP-003: Proposal shall be deterministically evaluable
    """

    # Identity
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_id: str

    # Mutation details
    key_path: Tuple[str, ...]
    proposed_value: Dict[str, Any]

    # Evaluation criteria (what the System should check)
    validation_criteria: Dict[str, Any] = field(default_factory=dict)

    # Requester information (for audit)
    proposer_id: str
    proposer_type: str  # e.g., "capability", "network", "external"

    proposed_at_utc: float = field(default_factory=time.time)


class MutationEvaluationResult(Enum):
    """
    Result of evaluating a state mutation proposal.

    Invariants:
        EVAL-001: All results are explicit
        EVAL-002: Results shall never imply ownership or authority transfer
    """

    ACCEPTED = "accepted"         # Proposal accepted, may be committed
    REJECTED = "rejected"         # Proposal rejected (e.g., validation failed)
    DEFERRED = "deferred"         # Deferred to later evaluation
    INVALID = "invalid"           # Request is malformed or invalid


@dataclass(frozen=True, slots=True)
class MutationEvaluation:
    """
    Evaluation of a state mutation proposal.

    Invariants:
        EVAL-RES-001: Evaluation shall be explicit
        EVAL-RES-002: Evaluation shall never modify state
        EVAL-RES-003: Evaluation result shall be observable
    """

    # Identity (required)
    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_id: str

    # What was evaluated
    proposal_id: str
    key_path: Tuple[str, ...]

    # Evaluation result
    result: MutationEvaluationResult
    rejection_reason: Optional[str] = None  # If rejected or invalid

    # Timestamps
    proposed_at_utc: float  # When proposal was created
    evaluated_at_utc: float = field(default_factory=time.time)

    def is_accepted(self) -> bool:
        return self.result == MutationEvaluationResult.ACCEPTED

    def is_rejected(self) -> bool:
        return self.result == MutationEvaluationResult.REJECTED

    def is_deferred(self) -> bool:
        return self.result == MutationEvaluationResult.DEFERRED


# =============================================================================
# STATE TRANSITION TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class StateTransitionRequest:
    """
    Request from System to commit a state transition.

    ONLY Systems may issue this request. External participants never
    directly modify state.

    Invariants:
        TXN-REQ-001: Only Systems may request transitions
        TXN-REQ-002: Request shall be explicit and typed
        TXN-REQ-003: Request shall include all required validation data
    """

    # Identity (required)
    transition_id: SystemTransitionId
    system_id: str

    # Transition details
    key_path: Tuple[str, ...]
    old_value: Optional[Dict[str, Any]]
    new_value: Dict[str, Any]

    # Version information
    old_version: int
    new_version: int

    # Timestamps
    requested_at_utc: float = field(default_factory=time.time)
    executed_at_utc: Optional[float] = None

    # Transaction context
    transaction_context: Optional[str] = None


@dataclass(frozen=True, slots=True)
class StateTransitionMetadata:
    """
    Immutable metadata produced by every state transition.

    This is the canonical record of what changed and why. It shall be
    preserved for observability, replay, and provenance tracking.

    Invariants:
        TXN-META-001: Metadata is immutable once committed
        TXN-META-002: Metadata preserves provenance
        TXN-META-003: Metadata enables replay
        TXN-META-004: Metadata never reveals private implementation details
    """

    # Transition identity
    transition_id: str
    system_id: str

    # What changed
    key_path: Tuple[str, ...]
    old_value_hash: Optional[str]  # Hash of old value
    new_value_hash: str            # Hash of new value

    # Version information
    old_version: int
    new_version: int

    # Timestamps
    transitioned_at_utc: float  # When transition was committed
    transaction_context: Optional[str] = None

    # Provenance
    requesting_component: Optional[str] = None   # Who requested?
    requesting_component_type: Optional[str] = None  # What type?
    authorization_source: Optional[str] = None   # Where authority verified?

    # Integrity verification data
    integrity_signature: Optional[str] = None

    def to_public_record(self) -> "StateTransitionRecord":
        """Convert to public transition record for observability."""
        return StateTransitionRecord(
            transition_id=self.transition_id,
            system_id=self.system_id,
            key_path=list(self.key_path),
            old_value_hash=self.old_value_hash,
            new_value_hash=self.new_value_hash,
            old_version=self.old_version,
            new_version=self.new_version,
            transitioned_at_utc=self.transitioned_at_utc,
        )


@dataclass(frozen=True, slots=True)
class StateTransitionRecord:
    """
    Public record of a state transition for observability.

    This record may be published to streams for observability purposes.
    It preserves provenance while protecting private implementation details.

    Invariants:
        TXN-REC-001: Record is immutable once committed
        TXN-REC-002: Record preserves transition ordering
        TXN-REC-003: Record enables replay of state changes
    """

    # Transition identity
    transition_id: str
    system_id: str

    # What changed (public view only)
    key_path: List[str]  # Public format (list instead of tuple)
    old_value_hash: Optional[str]
    new_value_hash: str

    # Version information
    old_version: int
    new_version: int

    # Timestamps
    transitioned_at_utc: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "transition_id": self.transition_id,
            "system_id": self.system_id,
            "key_path": self.key_path,
            "old_value_hash": self.old_value_hash,
            "new_value_hash": self.new_value_hash,
            "old_version": self.old_version,
            "new_version": self.new_version,
            "transitioned_at_utc": self.transitioned_at_utc,
        }


# =============================================================================
# TRANSACTION BOUNDARY TYPES
# =============================================================================


class TransactionBoundary(Enum):
    """
    Types of transaction boundaries Systems may define.

    SINGLE_OP: Each operation is its own transaction (no coordination)
    LOCAL: Operations grouped by system instance
    DISTRIBUTED: Operations coordinated across multiple systems

    Invariants:
        TXN-BND-001: Boundary type determines coordination requirements
        TXN-BND-002: Boundary never implies ownership transfer
    """

    SINGLE_OP = "single_op"         # No transaction context needed
    LOCAL = "local"                 # Local to system instance
    DISTRIBUTED = "distributed"     # Coordinated across systems


@dataclass(frozen=True, slots=True)
class TransactionBoundaryRequest:
    """
    Request for a new transaction boundary.

    Only Systems may initiate this. External participants may request
    participation but never define boundaries.

    Invariants:
        TXN-BND-REQ-001: Request shall be explicit
        TXN-BND-REQ-002: Request shall never imply ownership transfer
    """

    # Identity (required)
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_id: str

    # Boundary type
    boundary_type: TransactionBoundary = TransactionBoundary.LOCAL

    # Duration constraints
    timeout_seconds: Optional[float] = None  # Maximum duration

    requested_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True, slots=True)
class TransactionCommitRequest:
    """
    Request from System to commit transaction.

    Only the owning System may commit. External participants may
    participate but never own or commit transactions.

    Invariants:
        TXN-COM-REQ-001: Only Systems may commit transactions
        TXN-COM-REQ-002: Commit shall be atomic per System
        TXN-COM-REQ-003: Commit shall produce transaction record
    """

    # Identity (required)
    transaction_id: str
    system_id: str

    # State transitions to commit (as a unit)
    transition_ids: Tuple[str, ...]

    # Timestamps
    requested_at_utc: float = field(default_factory=time.time)


# =============================================================================
# PROOF OF STATE ACCESS
# =============================================================================


@dataclass(frozen=True, slots=True)
class PublicStateAccess:
    """
    Public proof of state access for observability.

    This record may be published to streams. It preserves provenance
    while protecting private implementation details.

    Invariants:
        PUB-ACCESS-001: Record is immutable once committed
        PUB-ACCESS-002: Record preserves access ordering
        PUB-ACCESS-003: Record enables replay of state reads
    """

    system_id: str
    key_path: List[str]  # Public format (list instead of tuple)
    value: Optional[Dict[str, Any]] = None  # Public view only
    version: Optional[int] = None
    timestamp_utc: Optional[float] = None

    accessed_at_utc: float = field(default_factory=time.time)


# =============================================================================
# SYSTEM INTERACTION PROTOCOL
# =============================================================================


@runtime_checkable
class SystemExecutor(Protocol):
    """
    Protocol for System execution of state transitions.

    Systems implement this protocol to participate in the canonical
    interaction flow. Execution remains within System boundaries.

    Invariants:
        EXEC-001: Execute shall consume declared inputs
        EXEC-002: Execute shall produce explicit outputs
        EXEC-003: Execute shall preserve transaction context
        EXEC-004: Execute shall never mutate state outside transaction
    """

    @property
    def system_id(self) -> str:
        """Return stable system identifier."""
        ...

    async def evaluate_state_access(
        self,
        request: StateAccessRequest,
    ) -> StateAccessResult:
        """
        Evaluate a state access request.

        Returns the result of accessing requested state.
        """
        ...

    async def propose_state_mutation(
        self,
        proposal: StateMutationProposal,
    ) -> MutationEvaluation:
        """
        Evaluate and possibly commit a state mutation proposal.

        This is where external proposals are evaluated. The System
        may accept, reject, or defer the proposal.

        Returns: Evaluation result with decision.
        """
        ...

    async def request_state_transition(
        self,
        transition_request: StateTransitionRequest,
    ) -> Optional[StateTransitionMetadata]:
        """
        Request a state transition from this System.

        Only the owning System may commit transitions. This method
        returns metadata if committed, None otherwise.

        Returns: Transition metadata if committed, None otherwise.
        """
        ...

    async def get_transaction_boundary(
        self,
        request: TransactionBoundaryRequest,
    ) -> Optional[str]:  # transaction_id or None
        """
        Request a new transaction boundary.

        Only Systems may initiate transactions. External participants
        may participate but never define boundaries.

        Returns: Transaction ID if created, None otherwise.
        """
        ...

    async def commit_transaction(
        self,
        commit_request: TransactionCommitRequest,
    ) -> bool:
        """
        Commit all transitions in a transaction as atomic unit.

        Only the owning System may commit transactions. External
        participants may participate but never own commits.

        Returns: True if committed, False if aborted.
        """
        ...


# =============================================================================
# SYSTEM RESULTS
# =============================================================================


class SystemInteractionOutcome(Enum):
    """
    Possible outcomes of System interactions.

    Invariants:
        OUTCOME-001: All outcomes are explicit
        OUTCOME-002: Outcomes preserve provenance
        OUTCOME-003: Outcomes enable replay and debugging
    """

    ACCEPTED = "accepted"         # Interaction accepted for processing
    REJECTED = "rejected"         # Interaction rejected (e.g., invalid)
    DEFERRED = "deferred"         # Deferred to later time
    COMMITTED = "committed"       # State transition committed
    CANCELLED = "cancelled"       # Interaction cancelled
    FAILED = "failed"             # Interaction failed


@dataclass(frozen=True, slots=True)
class SystemInteractionResult:
    """
    Result of a System interaction.

    Every completed System interaction shall produce an explicit outcome.

    Invariants:
        RES-001: Results shall preserve identity
        RES-002: Results shall be immutable once published
        RES-003: Results shall enable debugging and replay
    """

    # Identity (required)
    interaction_id: str
    system_id: str

    # Outcome
    outcome: SystemInteractionOutcome
    message: Optional[str] = None  # Human-readable explanation

    # Transition information (if applicable)
    transition_ids: Tuple[str, ...] = field(default_factory=tuple)

    # Timestamps
    created_at_utc: float
    completed_at_utc: Optional[float] = None

    def is_success(self) -> bool:
        return self.outcome in {
            SystemInteractionOutcome.ACCEPTED,
            SystemInteractionOutcome.COMMITTED,
        }

    def to_public_record(self) -> "PublicSystemInteractionRecord":
        """Convert to public record for observability."""
        return PublicSystemInteractionRecord(
            interaction_id=self.interaction_id,
            system_id=self.system_id,
            outcome=self.outcome.value,
            message=self.message,
            created_at_utc=self.created_at_utc,
            completed_at_utc=self.completed_at_utc or self.created_at_utc,
        )


@dataclass(frozen=True, slots=True)
class PublicSystemInteractionRecord:
    """
    Public record of System interaction for observability.

    This record may be published to streams. It preserves provenance
    while protecting private implementation details.

    Invariants:
        PUB-REC-001: Record is immutable once committed
        PUB-REC-002: Record preserves interaction ordering
        PUB-REC-003: Record enables replay of interactions
    """

    interaction_id: str
    system_id: str
    outcome: str  # One of SystemInteractionOutcome values
    message: Optional[str]
    created_at_utc: float
    completed_at_utc: float


# =============================================================================
# FAILURE TYPES
# =============================================================================


class SystemFailureCategory(Enum):
    """
    Categories of System interaction failures.

    Invariants:
        FAIL-001: Failures shall be explicit
        FAIL-002: Failures shall preserve provenance
        FAIL-003: Failures shall enable debugging and recovery
    """

    # Admission failures
    ADMISSION_FAILED = "admission_failed"           # Interaction not admitted
    AUTHORITY_FAILURE = "authority_failure"         # Authority verification failed

    # Lifecycle failures
    LIFECYCLE_INCOMPATIBLE = "lifecycle_incompatible"  # Wrong lifecycle state
    SYSTEM_UNAVAILABLE = "system_unavailable"       # System not operational

    # Transaction failures
    TRANSACTION_CONFLICT = "transaction_conflict"   # Concurrent modification
    TRANSACTION_TIMEOUT = "transaction_timeout"     # Transaction timed out

    # Validation failures
    VALIDATION_FAILED = "validation_failed"         # Input validation failed
    INTEGRITY_FAILURE = "integrity_failure"         # Integrity check failed

    # Dependency failures
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"  # Missing dependency
    DEPENDENCY_TIMEOUT = "dependency_timeout"       # Dependency timeout


@dataclass(frozen=True, slots=True)
class SystemInteractionFailure:
    """
    Record of a System interaction failure.

    Every failure shall preserve immutable diagnostic information.

    Invariants:
        FAIL-REC-001: Failures are always explicit
        FAIL-REC-002: Failure records are immutable
        FAIL-REC-003: Failures enable root cause analysis
        FAIL-REC-004: Failures never corrupt interaction identity
    """

    # Identity (required)
    failure_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    interaction_id: str

    # Classification
    category: SystemFailureCategory
    code: str  # Machine-readable failure code

    # Message
    message: str  # Human-readable explanation

    # Timestamps
    occurred_at_utc: float = field(default_factory=time.time)

    # Context
    system_id: Optional[str] = None
    key_path: Optional[Tuple[str, ...]] = None  # If applicable

    # Provenance
    source_layer: Optional[str] = None
    causal_chain: Tuple[str, ...] = field(default_factory=tuple)

    # Recovery information
    retryable: bool = False
    recovery_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert failure record to dictionary for serialization."""
        return {
            "failure_id": self.failure_id,
            "interaction_id": self.interaction_id,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "code": self.code,
            "message": self.message,
            "occurred_at_utc": self.occurred_at_utc,
            "system_id": self.system_id,
            "key_path": list(self.key_path) if self.key_path else None,
            "source_layer": self.source_layer,
            "retryable": self.retryable,
            "recovery_hint": self.recovery_hint,
        }


# =============================================================================
# SECURITY REQUIREMENTS
# =============================================================================


@dataclass(frozen=True, slots=True)
class SecurityVerification:
    """
    Security verification for System interactions.

    Every interaction shall pass security verification before any state
    mutation or access is permitted.

    Invariants:
        SEC-001: Verification shall precede all operations
        SEC-002: Verification shall never be bypassed
        SEC-003: Verification results are immutable
    """

    # Identity (required)
    verification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_id: str

    # What was verified
    interaction_category: SystemInteractionCategory
    key_path: Optional[Tuple[str, ...]] = None  # If applicable

    # Verification results
    authentication_passed: bool = False
    authorization_passed: bool = False
    integrity_passed: bool = False
    audit_trail_recorded: bool = False

    # Timestamps
    verified_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None  # When verification expires

    def is_complete(self) -> bool:
        """Check if all security verifications passed."""
        return (
            self.authentication_passed and
            self.authorization_passed and
            self.integrity_passed and
            self.audit_trail_recorded
        )

    def to_public_record(self) -> "PublicSecurityRecord":
        """Convert to public record for observability."""
        return PublicSecurityRecord(
            verification_id=self.verification_id,
            system_id=self.system_id,
            category=self.interaction_category.value,
            passed=self.is_complete(),
            verified_at_utc=self.verified_at_utc,
        )


@dataclass(frozen=True, slots=True)
class PublicSecurityRecord:
    """
    Public security record for observability.

    This record may be published to streams for audit and compliance
    purposes. It preserves provenance while protecting sensitive details.

    Invariants:
        PUB-SEC-001: Record is immutable once committed
        PUB-SEC-002: Record enables audit trail reconstruction
    """

    verification_id: str
    system_id: str
    category: str  # One of SystemInteractionCategory values
    passed: bool
    verified_at_utc: float


# =============================================================================
# CANONICAL INTERACTION FLOW
# =============================================================================


def get_canonical_system_interaction_flow() -> Tuple[str, ...]:
    """
    Return the canonical flow of System interactions.

    This defines the expected sequence of states and transitions
    for any interaction involving Systems.
    """
    return (
        "Execution_Schedules",
        "Interaction_Created",
        "System_Admission_Pending",
        "Admission_Evaluation",
        "State_Evaluation",
        "Transaction_Boundary_Determined",
        "State_Transition_Committed_Only_By_System",
        "Publication_Prepared",
        "Result_Published",
    )


# =============================================================================
# ARCHITECTURAL CONSTRAINTS
# =============================================================================


ARCHITECTURAL_CONSTRAINTS: Tuple[str, ...] = (
    # Ownership constraints
    "Systems_exclusively_own_persistent_state",
    "Only_systems_determine_whether_their_state_changes",
    "External_components_never_directly_modify_System_state",
    "Ownership_remains_unchanged_through_all_interactions",

    # Authority constraints
    "Authority_to_mutate_belongs_exclusively_to_owning_System",
    "Interactions_may_request_but_may_not_command",
    "Capabilities_may_compute_but_may_not_commit",
    "Networks_may_recommend_but_may_not_authorize",
    "No_component_bypasses_system_validation",

    # Lifecycle constraints
    "Every_interaction_has_explicit_lifecycle_state",
    "Lifecycle_transitions_are_deterministic_and_observable",
    "Invalid_transitions_shall_be_rejected",

    # Transaction constraints
    "Systems_define_transactional_boundaries",
    "External_components_may_participate_but_never_own_transactions",
    "Transaction_commits_are_atomic_per_System",

    # Replay constraints
    "Replay_preserves_state_transition_ordering",
    "Replay_shall_never_fabricate_committed_transitions",
    "Replay_shall_never_bypass_system_validation",

    # Security constraints
    "Security_verification_shall_precede_all_operations",
    "Authentication_and_authorization_required_for_mutations",
    "Integrity_checks_required_for_state_access",
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
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "SystemInteractionId",
    "SystemAdmissionId",
    "SystemTransitionId",

    # Lifecycle state
    "SystemLifecycleState",
    "is_system_terminal_state",

    # Interaction categories
    "SystemInteractionCategory",

    # Context types
    "SystemInteractionContext",
    "SystemAdmissionContext",

    # Admission decision
    "SystemAdmissionDecision",
    "is_admission_terminal",

    # State access
    "StateAccessMode",
    "StateAccessRequest",
    "StateAccessResult",

    # State mutation
    "StateMutationRequest",
    "StateMutationProposal",
    "MutationEvaluationResult",
    "MutationEvaluation",

    # State transitions
    "StateTransitionRequest",
    "StateTransitionMetadata",
    "StateTransitionRecord",

    # Transaction boundaries
    "TransactionBoundary",
    "TransactionBoundaryRequest",
    "TransactionCommitRequest",

    # Public records
    "PublicStateAccess",
    "PublicSystemInteractionRecord",

    # Protocol
    "SystemExecutor",

    # Results
    "SystemInteractionOutcome",
    "SystemInteractionResult",

    # Failures
    "SystemFailureCategory",
    "SystemInteractionFailure",

    # Security
    "SecurityVerification",
    "PublicSecurityRecord",

    # Utility functions
    "dataclass_replace",
    "get_canonical_system_interaction_flow",
    "ARCHITECTURAL_CONSTRAINTS",
]