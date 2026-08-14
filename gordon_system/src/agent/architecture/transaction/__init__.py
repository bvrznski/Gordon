# Transaction & Consistency Architecture - Phase 3.14.15
# =========================================================
#
# Canonical model for transactions and consistency throughout Gordon.
#
# This module establishes immutable contracts governing:
#   - Transaction lifecycle states and transitions
#   - Consistency verification before commitment
#   - Atomic commitment semantics
#   - Rollback semantics
#   - Isolation guarantees
#   - Durability semantics
#   - Ownership preservation (transactions never redefine ownership)
#   - Authority preservation (transactions never redefine authority)
#
# Transaction Lifecycle Axis:
#   CREATED → VALIDATED → ADMITTED → EXECUTING → VERIFYING → COMMITTED → CERTIFIED → CLOSED
#                    │                              └── ROLLED BACK (terminal)
#                    └─────────────── FAILED (terminal)

"""
Transaction & Consistency Architecture - Phase 3.14.15

Canonical model for transactions and consistency throughout Gordon.

This module establishes immutable contracts governing transactional execution,
consistency verification, commitment, rollback, recovery, and certification
across Execution, Streams, Networks, Capabilities, Systems, and future
architectural domains.

Transaction Principles:
    - Transactions coordinate multiple architectural operations into a single
      consistent unit of work.
    - Transactions preserve architectural integrity.
    - Transactions never redefine ownership.
    - Transactions never redefine authority.
    - Every Transaction shall possess exactly one owner (System).
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

# =============================================================================
# TRANSACTION LIFECYCLE STATES
# =============================================================================


class TransactionLifecycleState(Enum):
    """
    Canonical transaction lifecycle states.
    
    State Flow:
        CREATED → VALIDATED → ADMITTED → EXECUTING → VERIFYING → COMMITTED → CERTIFIED → CLOSED
        
    Terminal States (may be reached from any intermediate state):
        - FAILED: Execution failed, no recovery attempted
        - ABORTED: Explicitly aborted by owner or authority
        - CANCELLED: Requested cancellation before execution completed
        - ROLLED_BACK: Rollback completed successfully
    
    Valid Transitions:
        CREATED → VALIDATED       (Validation passed)
        VALIDATED → ADMITTED      (Admission control granted)
        ADMITTED → EXECUTING      (Execution started)
        EXECUTING → VERIFYING     (Execution completed, verification required)
        VERIFYING → COMMITTED     (Consistency verified, commit approved)
        COMMITTED → CERTIFIED     (Commit durable, certification complete)
        CERTIFIED → CLOSED        (Final state)
        
    Failure Transitions:
        Any State → FAILED          (Irrecoverable failure)
        Any State → ABORTED         (Explicit abort by authority)
        Any State → CANCELLED       (External cancellation request)
        VERIFYING → ROLLED_BACK     (Rollback completed)
    """
    
    # Initial states - transaction definition
    CREATED = "created"             # Transaction defined, not yet validated
    VALIDATED = "validated"         # Validation passed, ready for admission
    
    # Admission states
    ADMITTED = "admitted"           # Admission control granted, may execute
    
    # Execution states
    EXECUTING = "executing"         # Active execution in progress
    VERIFYING = "verifying"         # Post-execution consistency verification
    
    # Commitment states
    COMMITTED = "committed"         # Consistency verified, committed to state
    CERTIFIED = "certified"         # Durable, certified complete
    
    # Closed (final) state
    CLOSED = "closed"               # Transaction lifecycle complete
    
    # Alternative terminal states
    FAILED = "failed"               # Terminal failure state
    ABORTED = "aborted"             # Explicitly aborted
    CANCELLED = "cancelled"         # Cancelled before completion
    ROLLED_BACK = "rolled_back"     # Rollback completed


# =============================================================================
# TRANSACTION IDENTITY AND OWNERSHIP
# =============================================================================


class TransactionKind(Enum):
    """
    Semantic kind of transaction for routing and policy.
    
    Kinds determine:
        - Which authority may commit the transaction
        - Which persistence policies apply
        - Which isolation semantics are enforced
        - Which recovery mechanisms are available
    """
    
    # Execution-level transactions
    EXECUTION = "execution"                 # Standard execution coordination
    EXECUTION_BATCH = "execution_batch"     # Batch of related executions
    
    # Stream transactions
    STREAM_PUBLISH = "stream_publish"       # Publish to stream (atomic batch)
    STREAM_CONSUME = "stream_consume"       # Consume from stream (atomic batch)
    
    # Network transactions
    NETWORK_COMMIT = "network_commit"       # Network configuration commit
    NETWORK_RECOVERY = "network_recovery"   # Network recovery operation
    
    # System-level transactions
    SYSTEM_STATE = "system_state"           # Persistent system state change
    SYSTEM_CONFIG = "system_config"         # Configuration change
    SYSTEM_RECOVERY = "system_recovery"     # Recovery operation
    
    # Capability transactions
    CAPABILITY_INVOKE = "capability_invoke" # Single capability invocation
    CAPABILITY_CHAIN = "capability_chain"   # Chained capability execution


@dataclass(frozen=True)
class TransactionOwner:
    """
    Immutable descriptor for transaction ownership.
    
    Every transaction shall possess exactly one owner.
    The owner is responsible for lifecycle management, coordination,
    consistency verification, commitment, and rollback.
    
    Ownership does NOT grant authority over the components involved
    in the transaction. Authority remains external to the transaction.
    """
    
    # Owner identity
    system_id: str                      # Which System owns this?
    scope: str                          # "global", "user", "session", etc.
    
    # Authority bindings (external to transaction)
    commit_authority_id: Optional[str] = None   # Who may commit?
    rollback_authority_id: Optional[str] = None  # Who may rollback?
    cancel_authority_id: Optional[str] = None     # Who may cancel?
    
    # Scope context
    scope_context: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def for_system(cls, system_id: str) -> "TransactionOwner":
        """Create owner for a system-scoped transaction."""
        return cls(
            system_id=system_id,
            scope="global",
            commit_authority_id=system_id,
            rollback_authority_id=system_id,
        )
    
    @classmethod
    def for_session(cls, system_id: str, session_id: str) -> "TransactionOwner":
        """Create owner for a session-scoped transaction."""
        return cls(
            system_id=system_id,
            scope="session",
            scope_context={"session_id": session_id},
            commit_authority_id=f"{system_id}:session:{session_id}",
            rollback_authority_id=f"{system_id}:session:{session_id}",
        )
    
    def can_commit(self, authority_id: str) -> bool:
        """Check if given authority may commit this transaction."""
        return self.commit_authority_id is None or self.commit_authority_id == authority_id
    
    def can_rollback(self, authority_id: str) -> bool:
        """Check if given authority may rollback this transaction."""
        return self.rollback_authority_id is None or self.rollback_authority_id == authority_id
    
    def can_cancel(self, authority_id: str) -> bool:
        """Check if given authority may cancel this transaction."""
        return self.cancel_authority_id is None or self.cancel_authority_id == authority_id


# =============================================================================
# TRANSACTION DEFINITION
# =============================================================================


@dataclass(frozen=True)
class TransactionDefinition:
    """
    Immutable definition of a Transaction.
    
    Every Transaction shall define:
        - Transaction identifier (unique across system lifetime)
        - Transaction owner (exactly one)
        - Transaction scope (what components participate)
        - Execution context (how to execute)
        - Participating components (what is affected)
        - Consistency policy (how consistency is verified)
        
    This definition is never modified during transaction lifecycle.
    """
    
    # Identity
    transaction_id: str                 # UUID string, unique globally
    
    # Owner
    owner: TransactionOwner             # Exactly one owner
    
    # Scope and purpose
    kind: TransactionKind               # Semantic kind of transaction
    scope: FrozenSet[str] = field(default_factory=frozenset)  # Components involved
    description: Optional[str] = None   # Human-readable description
    
    # Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    # Consistency policy (default to EXECUTION_ONLY via class method)
    consistency_policy: "ConsistencyPolicy" = field(
        default_factory=lambda: ConsistencyPolicy.for_execution()
    )
    
    # Timeout constraints
    timeout_seconds: Optional[float] = None
    
    # Participating components (external references, not owned)
    participant_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    requested_by: Optional[str] = None  # Who initiated?
    correlation_id: Optional[str] = None  # Cross-transaction trace
    
    @classmethod
    def new(
        cls,
        owner: TransactionOwner,
        kind: TransactionKind,
        scope: Optional[FrozenSet[str]] = None,
        description: Optional[str] = None,
        consistency_policy: Optional["ConsistencyPolicy"] = None,
    ) -> "TransactionDefinition":
        """Create a new transaction definition."""
        return cls(
            transaction_id=f"txn-{uuid.uuid4().hex[:16]}",
            owner=owner,
            kind=kind,
            scope=scope or frozenset(),
            description=description,
            consistency_policy=consistency_policy or ConsistencyPolicy.for_execution(),
        )
    
    def with_participant(self, ref: str) -> "TransactionDefinition":
        """Return new definition with additional participant reference."""
        return dataclass_replace(
            self,
            participant_refs=self.participant_refs + (ref,)
        )
    
    def with_timeout(self, timeout_seconds: float) -> "TransactionDefinition":
        """Return new definition with timeout."""
        return dataclass_replace(self, timeout_seconds=timeout_seconds)
    
    def with_correlation_id(self, correlation_id: str) -> "TransactionDefinition":
        """Return new definition with correlation ID for tracing."""
        return dataclass_replace(self, correlation_id=correlation_id)


# =============================================================================
# CONSISTENCY POLICY
# =============================================================================


@dataclass(frozen=True)
class ConsistencyPolicy:
    """
    Policy defining consistency verification requirements.
    
    Policies determine how consistency is verified and what constraints
    must be satisfied before commitment.
    """
    
    class VerificationLevel(Enum):
        """Consistency verification strength."""
        NONE = "none"                     # No verification (unsafe, for testing only)
        EXECUTION_ONLY = "execution_only"  # Execution completed successfully
        INTEGRITY = "integrity"           # Integrity constraints satisfied
        OWNERSHIP = "ownership"           # Ownership integrity verified
        AUTHORITY = "authority"           # Authority boundaries verified
        FULL = "full"                     # All checks (execution, integrity, ownership, authority)
    
    class IsolationLevel(Enum):
        """Isolation semantics."""
        READ_UNCOMMITTED = "read_uncommitted"  # No isolation (unsafe)
        READ_COMMITTED = "read_committed"      # Reads see committed state only
        REPEATABLE_READ = "repeatable_read"    # Repeated reads see same snapshot
        SERIALIZABLE = "serializable"          # Complete isolation, no interference
    
    verification_level: VerificationLevel = VerificationLevel.EXECUTION_ONLY
    isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE
    verify_ownership_integrity: bool = True
    verify_authority_integrity: bool = True
    verify_dependency_integrity: bool = False  # May be expensive, opt-in
    
    @classmethod
    def for_strict(cls) -> "ConsistencyPolicy":
        """Create strict policy with full verification."""
        return cls(
            verification_level=cls.VerificationLevel.FULL,
            isolation_level=cls.IsolationLevel.SERIALIZABLE,
            verify_ownership_integrity=True,
            verify_authority_integrity=True,
            verify_dependency_integrity=True,
        )
    
    @classmethod
    def for_execution(cls) -> "ConsistencyPolicy":
        """Create policy for execution-only verification."""
        return cls(
            verification_level=cls.VerificationLevel.EXECUTION_ONLY,
            isolation_level=cls.IsolationLevel.SERIALIZABLE,
            verify_ownership_integrity=True,
            verify_authority_integrity=True,
        )
    
    @classmethod
    def for_testing(cls) -> "ConsistencyPolicy":
        """Create policy for testing (minimal verification)."""
        return cls(
            verification_level=cls.VerificationLevel.NONE,
            isolation_level=cls.IsolationLevel.READ_UNCOMMITTED,
            verify_ownership_integrity=False,
            verify_authority_integrity=False,
        )
    
    # Aliases for backwards compatibility
    EXECUTION_ONLY = VerificationLevel.EXECUTION_ONLY


# =============================================================================
# TRANSACTION STATE
# =============================================================================


@dataclass(frozen=True)
class TransactionState:
    """
    Immutable state of a Transaction at a point in time.
    
    This captures the complete state for persistence, recovery, and
    observability. Contains only bounded data - no live objects.
    """
    
    # Identity (immutable after creation)
    transaction_id: str
    lifecycle_state: TransactionLifecycleState
    
    # Owner reference (not owner object to avoid serialization issues)
    system_owner_id: str
    scope: str
    
    # Lifecycle timing
    created_at_utc: float
    validated_at_utc: Optional[float] = None
    admitted_at_utc: Optional[float] = None
    started_executing_at_utc: Optional[float] = None
    completed_execution_at_utc: Optional[float] = None
    verified_at_utc: Optional[float] = None
    committed_at_utc: Optional[float] = None
    certified_at_utc: Optional[float] = None
    closed_at_utc: Optional[float] = None
    
    # Terminal state indicators
    is_failed: bool = False
    failure_reason: Optional[str] = None  # Machine-readable code
    failure_message: Optional[str] = None  # Human-readable explanation
    
    is_rolled_back: bool = False
    rollback_at_utc: Optional[float] = None
    
    # Execution results (if applicable)
    execution_results: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Verification status
    verification_passed: bool = True
    consistency_violations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Commitment status
    commit_authority_approved: Optional[str] = None  # Who approved?
    commitment_durable: bool = False
    
    # Provenance
    correlation_id: Optional[str] = None
    participants_observed: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def initial(cls, definition: TransactionDefinition) -> "TransactionState":
        """Create initial state for a new transaction."""
        return cls(
            transaction_id=definition.transaction_id,
            lifecycle_state=TransactionLifecycleState.CREATED,
            system_owner_id=definition.owner.system_id,
            scope=definition.owner.scope,
            created_at_utc=definition.created_at_utc,
            correlation_id=definition.correlation_id,
            participants_observed=definition.participant_refs,
        )
    
    def with_state(self, new_state: TransactionLifecycleState) -> "TransactionState":
        """Return state with updated lifecycle state."""
        return dataclass_replace(self, lifecycle_state=new_state)
    
    def with_timestamp(self, timestamp_name: str, value: float) -> "TransactionState":
        """Set a timestamp field and return new state."""
        return dataclass_replace(self, **{timestamp_name: value})
    
    def mark_failed(
        self,
        reason: str,
        message: Optional[str] = None,
    ) -> "TransactionState":
        """Mark transaction as failed with diagnostic info."""
        return dataclass_replace(
            self,
            is_failed=True,
            failure_reason=reason,
            failure_message=message,
        )
    
    def mark_rolled_back(self, at_utc: Optional[float] = None) -> "TransactionState":
        """Mark transaction as rolled back."""
        return dataclass_replace(
            self,
            is_rolled_back=True,
            rollback_at_utc=at_utc or time.time(),
        )
    
    def with_verification_result(
        self,
        passed: bool,
        violations: Tuple[str, ...] = tuple(),
    ) -> "TransactionState":
        """Update verification status."""
        return dataclass_replace(
            self,
            verification_passed=passed,
            consistency_violations=violations,
        )
    
    def mark_committed(self, authority_id: str, durable: bool) -> "TransactionState":
        """Mark transaction as committed."""
        return dataclass_replace(
            self,
            commit_authority_approved=authority_id,
            commitment_durable=durable,
        )


# =============================================================================
# TRANSACTION LIFECYCLE EVENT
# =============================================================================


class LifecycleEvent(Enum):
    """
    Lifecycle transition events that may be observed.
    
    These events are published to streams for observability and replay.
    """
    
    # Creation and validation
    CREATED = "created"
    VALIDATED = "validated"
    
    # Admission
    ADMITTED = "admitted"
    
    # Execution phases
    EXECUTION_STARTED = "execution_started"
    EXECUTION_STEP_COMPLETED = "execution_step_completed"
    EXECUTION_COMPLETED = "execution_completed"
    
    # Verification and commitment
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_PASSED = "verification_passed"
    VERIFICATION_FAILED = "verification_failed"
    COMMITTED = "committed"
    CERTIFIED = "certified"
    
    # Terminal states
    FAILED = "failed"
    ABORTED = "aborted"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"
    CLOSED = "closed"


@dataclass(frozen=True)
class TransactionLifecycleEvent:
    """
    Immutable event representing a lifecycle transition.
    
    Events are published to streams for observability, replay, and
    cross-system coordination.
    """
    
    # Identity
    event_id: str                       # UUID string
    transaction_id: str                 # Which transaction?
    
    # Timestamp
    occurred_at_utc: float
    
    # Event details
    previous_state: TransactionLifecycleState
    new_state: TransactionLifecycleState
    event_type: LifecycleEvent
    
    # Author
    triggered_by: Optional[str] = None  # Who/what triggered this?
    
    # Context (additional data)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostic info (for failures, rollbacks, etc.)
    failure_reason: Optional[str] = None
    rollback_attribution: Optional[str] = None
    
    @classmethod
    def from_state_transition(
        cls,
        transaction_id: str,
        previous_state: TransactionLifecycleState,
        new_state: TransactionLifecycleState,
        event_type: LifecycleEvent,
        triggered_by: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "TransactionLifecycleEvent":
        """Create lifecycle event from state transition."""
        return cls(
            event_id=f"evt-{uuid.uuid4().hex[:16]}",
            transaction_id=transaction_id,
            occurred_at_utc=time.time(),
            previous_state=previous_state,
            new_state=new_state,
            event_type=event_type,
            triggered_by=triggered_by,
            context=context or {},
        )
    
    @classmethod
    def failed(
        cls,
        transaction_id: str,
        state_before_failure: TransactionLifecycleState,
        failure_reason: str,
        message: Optional[str] = None,
        triggered_by: Optional[str] = None,
    ) -> "TransactionLifecycleEvent":
        """Create a failure event."""
        context: Dict[str, Any] = {"failure_message": message} if message else {}
        return cls(
            event_id=f"evt-{uuid.uuid4().hex[:16]}",
            transaction_id=transaction_id,
            occurred_at_utc=time.time(),
            previous_state=state_before_failure,
            new_state=TransactionLifecycleState.FAILED,
            event_type=LifecycleEvent.FAILED,
            triggered_by=triggered_by,
            context=context,
            failure_reason=failure_reason,
        )


# =============================================================================
# CONSISTENCY VERIFICATION
# =============================================================================


class ConsistencyCheck(Enum):
    """
    Types of consistency checks that may be performed.
    
    Checks are performed in order (earlier checks are prerequisites for later).
    A transaction failing any check shall never commit.
    """
    
    # Prerequisite checks
    EXECUTION_COMPLETE = "execution_complete"  # All work completed
    NO_PENDING_OPERATIONS = "no_pending_operations"  # No async work remaining
    
    # Integrity checks
    OWNERSHIP_INTEGRITY = "ownership_integrity"  # Ownership boundaries preserved
    AUTHORITY_INTEGRITY = "authority_integrity"  # Authority boundaries preserved
    DEPENDENCY_INTEGRITY = "dependency_integrity"  # Dependencies satisfied
    
    # State checks
    ARCHITECTURAL_INVARIANT = "architectural_invariant"  # Core invariants hold


@dataclass(frozen=True)
class ConsistencyVerificationResult:
    """
    Result of consistency verification for a Transaction.
    
    A transaction failing consistency verification shall never commit.
    """
    
    is_consistent: bool
    checks_passed: Tuple[ConsistencyCheck, ...]
    checks_failed: Tuple[ConsistencyCheck, ...]
    
    # Failure details (if not consistent)
    failure_reason: Optional[str] = None
    violation_details: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def passed(cls) -> "ConsistencyVerificationResult":
        """Create a passing result."""
        return cls(
            is_consistent=True,
            checks_passed=tuple(ConsistencyCheck),
            checks_failed=tuple(),
        )
    
    @classmethod
    def failed(cls, reason: str, *violations: str) -> "ConsistencyVerificationResult":
        """Create a failing result."""
        return cls(
            is_consistent=False,
            checks_passed=tuple(),
            checks_failed=tuple(ConsistencyCheck),
            failure_reason=reason,
            violation_details=violations,
        )
    
    @classmethod
    def with_failures(cls, failed: Tuple[ConsistencyCheck, ...], reason: str) -> "ConsistencyVerificationResult":
        """Create result with specific failures."""
        return cls(
            is_consistent=False,
            checks_passed=tuple(),
            checks_failed=failed,
            failure_reason=reason,
            violation_details=tuple(f"check={c.value}, reason={reason}" for c in failed),
        )


class CommitmentAuthority(Enum):
    """
    Canonical authorities that may commit transactions.
    
    Only the owning System may finalize persistent architectural state.
    Transactions may propose commitment, but final authority rests with
    the system that owns the state being modified.
    """
    
    SYSTEM_OWNER = "system_owner"       # The owning System (canonical)
    EXECUTION_COORDINATOR = "execution_coordinator"  # For execution coordination
    STREAM_MANAGER = "stream_manager"   # For stream operations
    
    @classmethod
    def for_system(cls, system_id: str) -> str:
        """Return the canonical commit authority ID for a system."""
        return f"{cls.SYSTEM_OWNER.value}:{system_id}"


@dataclass(frozen=True)
class CommitmentDecision:
    """
    Decision about committing a Transaction.
    
    Commitment shall occur only after:
        - Successful validation
        - Successful execution
        - Successful consistency verification
        - Successful authority verification
    
    Partial commitment is prohibited.
    """
    
    # Required fields first (must come before any defaults)
    transaction_state: TransactionState  # Must be first - no default value
    
    # Optional fields with defaults
    should_commit: bool = True
    committing_authority_id: str = ""
    consistency_result: Optional[ConsistencyVerificationResult] = None
    ownership_verified: bool = True
    authority_verified: bool = True
    committed_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def approved(
        cls,
        committing_authority_id: str,
        transaction_state: TransactionState,
        consistency_result: ConsistencyVerificationResult,
    ) -> "CommitmentDecision":
        """Create an approval decision."""
        return cls(
            should_commit=True,
            committed_at_utc=time.time(),
            committing_authority_id=committing_authority_id,
            transaction_state=transaction_state,
            consistency_result=consistency_result,
            ownership_verified=True,
            authority_verified=True,
        )
    
    @classmethod
    def rejected(
        cls,
        transaction_state: TransactionState,
        reason: str,
    ) -> "CommitmentDecision":
        """Create a rejection decision."""
        return cls(
            should_commit=False,
            committed_at_utc=time.time(),
            committing_authority_id=transaction_state.system_owner_id,
            transaction_state=transaction_state,
            consistency_result=None,
            ownership_verified=True,  # Still verified, just rejected for other reasons
            authority_verified=True,
        )
    
    @property
    def rejection_reason(self) -> Optional[str]:
        """Return rejection reason if not approved."""
        return None if self.should_commit else "Unknown rejection"


@dataclass(frozen=True)
class RollbackDecision:
    """
    Decision about rolling back a Transaction.
    
    Rollback shall restore the last architecturally consistent state.
    Rollback shall preserve ownership, provenance, timestamps, transaction
    identity, and execution history.
    
    Rollback shall never fabricate successful execution.
    Rollback shall remain observable.
    """
    
    # Required fields first (must come before any defaults)
    transaction_state: Optional[TransactionState]  # Must be first - no default value
    
    # Optional fields with defaults
    should_rollback: bool = False  # Default for convenience
    rollback_authority_id: str = ""
    restore_to_state: Optional[TransactionState] = None  # Previous consistent state
    rolled_back_at_utc: float = field(default_factory=time.time)
    """
    Decision about rolling back a Transaction.
    
    Rollback shall restore the last architecturally consistent state.
    Rollback shall preserve ownership, provenance, timestamps, transaction
    identity, and execution history.
    
    Rollback shall never fabricate successful execution.
    Rollback shall remain observable.
    """
    
    # Required fields first (must come before any defaults)
    should_rollback: bool = False  # Default for convenience
    transaction_state: Optional[TransactionState]  # type: ignore[assignment]
    
    # Optional fields with defaults
    rollback_authority_id: str = ""
    restore_to_state: Optional[TransactionState] = None  # Previous consistent state
    rolled_back_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def approved(
        cls,
        rollback_authority_id: str,
        transaction_state: TransactionState,
    ) -> "RollbackDecision":
        """Create a rollback approval decision."""
        return cls(
            should_rollback=True,
            rolled_back_at_utc=time.time(),
            rollback_authority_id=rollback_authority_id,
            transaction_state=transaction_state,
        )
    
    @classmethod
    def rejected(cls, reason: str) -> "RollbackDecision":
        """Create a rollback rejection decision."""
        return cls(
            should_rollback=False,
            rolled_back_at_utc=time.time(),
            rollback_authority_id="unknown",
            transaction_state=None,  # type: ignore[assignment]
        )
    
    @property
    def rollback_rejection_reason(self) -> Optional[str]:
        """Return rejection reason if not approved."""
        return None if self.should_rollback else "Unknown rejection"


# =============================================================================
# DURABILITY SEMANTICS
# =============================================================================


class DurabilityLevel(Enum):
    """
    Durability guarantees for committed transactions.
    
    Durability shall be guaranteed according to the owning System's
    persistence policy. Replay shall never compromise durability guarantees.
    """
    
    MEMORY_ONLY = "memory_only"         # Not durable, for testing only
    VOLATILE_PERSISTENCE = "volatile_persistence"  # May survive restarts but not crash
    PERSISTENT = "persistent"           # Survives crashes and restarts
    ARCHIVAL = "archival"               # Immutable, permanent storage
    
    @classmethod
    def for_system(cls, system_id: str) -> "DurabilityLevel":
        """Get default durability level for a system."""
        # In practice, this would be configured per-system
        return cls.PERSISTENT


@dataclass(frozen=True)
class DurabilityDescriptor:
    """
    Descriptor for transaction durability semantics.
    
    Every committed Transaction shall remain durable according to the owning
    System's persistence policy.
    """
    
    level: DurabilityLevel = DurabilityLevel.PERSISTENT
    
    # Storage configuration
    storage_backend: str = "default"  # Backend identifier
    replication_factor: int = 1       # Number of replicas
    
    # Timing constraints
    durability_timeout_seconds: Optional[float] = None
    
    @classmethod
    def for_persistent(cls) -> "DurabilityDescriptor":
        """Create descriptor with persistent durability."""
        return cls(level=DurabilityLevel.PERSISTENT)
    
    @classmethod
    def for_archival(cls) -> "DurabilityDescriptor":
        """Create descriptor with archival durability."""
        return cls(
            level=DurabilityLevel.ARCHIVAL,
            replication_factor=3,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


def validate_transaction_definition(definition: TransactionDefinition) -> Tuple[bool, Optional[str]]:
    """
    Validate a transaction definition before creating state.
    
    Returns:
        (is_valid, error_message) tuple
    """
    if not definition.transaction_id:
        return False, "transaction_id is required"
    
    if not definition.owner:
        return False, "owner is required"
    
    # Verify exactly one owner
    # (TransactionOwner is dataclass-frozen so we just check it's set)
    
    if not definition.kind:
        return False, "kind is required"
    
    return True, None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Lifecycle states
    "TransactionLifecycleState",
    
    # Transaction definition
    "TransactionKind",
    "TransactionOwner",
    "TransactionDefinition",
    "ConsistencyPolicy",
    
    # Transaction state
    "TransactionState",
    
    # Events and lifecycle
    "LifecycleEvent",
    "TransactionLifecycleEvent",
    
    # Consistency
    "ConsistencyCheck",
    "ConsistencyVerificationResult",
    "CommitmentAuthority",
    "CommitmentDecision",
    
    # Rollback
    "RollbackDecision",
    
    # Durability
    "DurabilityLevel",
    "DurabilityDescriptor",
    
    # Utilities
    "dataclass_replace",
    "validate_transaction_definition",
]