# Capability Invocation Contracts
# ================================
#
# PHASE 3.14.8 - Canonical Capability Invocation Architecture
#
# This module establishes the immutable contracts governing:
#   - Capability admission semantics
#   - Invocation lifecycle
#   - Execution semantics
#   - Completion semantics
#   - Cancellation semantics
#   - Result publication rules
#   - Ownership preservation
#   - Authority preservation
#   - Replay compatibility
#   - Observability

"""
Canonical Capability Invocation Contracts for Gordon Phase 3.14.8.

This module defines the architectural contracts that govern how Capabilities
are invoked, executed, and produce results while preserving ownership,
authority, determinism, and architectural integrity.

ARCHITECTURAL PRINCIPLES:
=========================

Execution schedules work.
Interactions request work.
Capabilities perform work.
Streams transport interaction records.
Systems own persistent state.

OWNERSHIP MODEL:
================

Capabilities own computation.
Execution owns scheduling.
Interactions own communication semantics.
Streams own transport.
Systems own persistent state.

These ownership rights are immutable throughout invocation lifecycle.


INVOCATION FLOW:
================

Execution
    │
    ▼
Interaction
    │
    ▼
Capability Admission
    │
    ▼
Capability Invocation
    │
    ▼
Capability Execution
    │
    ▼
Capability Result
    │
    ▼
Interaction Publication


INVOCATION LIFECYCLE:
=====================

Created → Validated → Admitted → Scheduled → Executing
    │                              ├─► Cancelled
    │                              ├─► Failed
    ▼
Completed → Published


AUTHORITY MODEL:
================

Capabilities never self-authorize.
Capability invocation is always subject to external authority verification.
Authority remains external to computation.

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
# IDENTITY TYPES - Capability Invocation
# =============================================================================


@dataclass(frozen=True, slots=True)
class CapabilityInvocationId:
    """Unique semantic identity for one capability invocation."""
    
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "CapabilityInvocationId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True, slots=True)
class CapabilityAdmissionId:
    """Unique semantic identity for one capability admission decision."""
    
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "CapabilityAdmissionId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True, slots=True)
class CapabilityExecutionId:
    """Unique semantic identity for one capability execution instance."""
    
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "CapabilityExecutionId":
        return cls(value=str(uuid.uuid4()))


# =============================================================================
# LIFECYCLE STATE ENUMERATION
# =============================================================================


class CapabilityLifecycleState(Enum):
    """
    Canonical lifecycle states for Capability invocation.
    
    Transitions:
        CREATED → VALIDATED → ADMIITTED → SCHEDULED → EXECUTING
            ├─► CANCELLED (before/during execution)
            └─► FAILED (at any point before completion)
        
        EXECUTING → COMPLETED → PUBLISHED
        
        Terminal states: COMPLETED, CANCELLED, FAILED
    
    Invariants:
        LC-001: Lifecycle progression shall remain deterministic
        LC-002: Invalid transitions shall be rejected
        LC-003: Each transition shall produce observable event
        LC-004: Terminal states never transition to non-terminal states
    """
    
    # Initial state
    CREATED = "created"           # Invocation created, not yet validated
    
    # Pre-execution states
    VALIDATED = "validated"       # Inputs validated, ready for admission
    ADMIITTED = "admitted"        # Passed admission checks, scheduled
    
    # Execution states
    SCHEDULED = "scheduled"       # Scheduled for execution
    EXECUTING = "executing"       # Currently executing
    
    # Terminal states
    COMPLETED = "completed"       # Execution completed successfully
    CANCELLED = "cancelled"       # Invocation cancelled
    FAILED = "failed"             # Execution failed


def is_terminal_state(state: CapabilityLifecycleState) -> bool:
    """Check if a lifecycle state is terminal."""
    return state in {
        CapabilityLifecycleState.COMPLETED,
        CapabilityLifecycleState.CANCELLED,
        CapabilityLifecycleState.FAILED,
    }


def get_allowed_transitions(from_state: CapabilityLifecycleState) -> Tuple[CapabilityLifecycleState, ...]:
    """
    Get allowed transitions from a given lifecycle state.
    
    Invariants:
        LC-005: Only explicitly declared transitions are valid
        LC-006: Terminal states have no outgoing transitions
    """
    transitions = {
        CapabilityLifecycleState.CREATED: (
            CapabilityLifecycleState.VALIDATED,
            CapabilityLifecycleState.CANCELLED,  # Can be cancelled immediately
            CapabilityLifecycleState.FAILED,     # Validation may fail
        ),
        
        CapabilityLifecycleState.VALIDATED: (
            CapabilityLifecycleState.ADMIITTED,
            CapabilityLifecycleState.CANCELLED,
            CapabilityLifecycleState.FAILED,
        ),
        
        CapabilityLifecycleState.ADMIITTED: (
            CapabilityLifecycleState.SCHEDULED,
            CapabilityLifecycleState.CANCELLED,
            CapabilityLifecycleState.FAILED,     # Scheduling may fail
        ),
        
        CapabilityLifecycleState.SCHEDULED: (
            CapabilityLifecycleState.EXECUTING,
            CapabilityLifecycleState.CANCELLED,
            CapabilityLifecycleState.FAILED,
        ),
        
        CapabilityLifecycleState.EXECUTING: (
            CapabilityLifecycleState.COMPLETED,
            CapabilityLifecycleState.CANCELLED,
            CapabilityLifecycleState.FAILED,
        ),
        
        CapabilityLifecycleState.COMPLETED: (),  # Terminal
        CapabilityLifecycleState.CANCELLED: (),  # Terminal
        CapabilityLifecycleState.FAILED: (),     # Terminal
    }
    
    return transitions.get(from_state, ())


# =============================================================================
# INVOCATION CONTEXT
# =============================================================================


@dataclass(frozen=True, slots=True)
class InvocationContext:
    """
    Immutable invocation context provided to Capabilities.
    
    This is NOT a service locator - it contains only invocation-specific data.
    
    Invariants:
        IC-001: InvocationContext shall be invocation-scoped
        IC-002: InvocationContext shall not become an unrestricted service locator
        IC-003: InvocationContext contents shall be explicitly declared and typed
    """
    
    # Identity (required - no defaults)
    invocation_id: CapabilityInvocationId
    interaction_id: str  # Interaction that triggered this invocation
    capability_id: str   # Which capability is being invoked
    
    # Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)  # e.g., user_id, session_id
    
    # Scheduling context
    scheduling_context: Dict[str, Any] = field(default_factory=dict)  # e.g., priority, deadline
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Lifecycle state tracking
    lifecycle_state: CapabilityLifecycleState = CapabilityLifecycleState.CREATED
    
    # Initiator (who requested this invocation)
    initiator_id: str = "unknown"
    initiator_type: str = "system"  # e.g., "user", "system", "scheduled"
    
    # Cancellation view
    cancellation_requested: bool = False
    cancellation_reason: Optional[str] = None
    
    def with_state(self, new_state: CapabilityLifecycleState) -> "InvocationContext":
        """Create a copy with updated lifecycle state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            started_at_utc=self.started_at_utc if new_state != CapabilityLifecycleState.CREATED else time.time()
        )
    
    def with_result(self, result: "CapabilityResult") -> "InvocationContext":
        """Create a copy with updated lifecycle state and timestamps."""
        return dataclass_replace(
            self,
            lifecycle_state=CapabilityLifecycleState.COMPLETED,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace that works with frozen dataclasses."""
    import dataclasses
    if hasattr(instance, '__dataclass_fields__'):
        return type(instance)(
            **{**dataclasses.asdict(instance), **kwargs}
        )
    # Fallback for non-dataclasses (using __dict__)
    new_instance = object.__new__(type(instance))
    new_instance.__dict__.update(instance.__dict__)
    new_instance.__dict__.update(kwargs)
    return new_instance


# =============================================================================
# ADMISSION CONTEXT
# =============================================================================


@dataclass(frozen=True, slots=True)
class AdmissionContext:
    """
    Context for capability admission evaluation.
    
    Contains all information needed to decide whether a capability may execute.
    
    Invariants:
        AC-001: Admission shall never imply authority
        AC-002: Implicit admission is prohibited - explicit outcome required
        AC-003: Every admission decision shall be observable
    """
    
    # Identity
    admission_id: CapabilityAdmissionId
    
    # Invocation context being admitted
    invocation_context: InvocationContext
    
    # Admission criteria to verify
    capability_available: bool = True          # Is the capability implementation available?
    execution_context_valid: bool = True       # Are required execution contexts present?
    dependencies_ready: bool = True            # Are all dependencies satisfied?
    
    # Authority verification (external to computation)
    authority_verified: bool = False           # Has external authority verified this invocation?
    scheduling_compatible: bool = True         # Does this fit within scheduling constraints?
    resource_available: bool = True            # Are required resources available?
    
    # Policy verification
    security_policy_passed: bool = True        # Does invocation pass security policy?
    privacy_policy_passed: bool = True         # Does invocation pass privacy policy?
    
    # Admission outcome
    decision: "AdmissionDecision" = field(default_factory=lambda: AdmissionDecision.ADMIT)
    rejection_reason: Optional[str] = None
    
    evaluated_at_utc: float = field(default_factory=time.time)


class AdmissionDecision(Enum):
    """Result of capability admission evaluation."""
    
    ADMIT = "admit"                     # Capability may proceed
    WAIT = "wait"                       # Wait for dependencies/resources
    REJECT = "reject"                   # Permanent rejection (e.g., policy violation)
    CANCEL = "cancel"                   # Cancel due to external request


# =============================================================================
# CAPABILITY EXECUTION CONTEXT
# =============================================================================


@dataclass(frozen=True, slots=True)
class ExecutionExecutionContext:
    """
    Context provided during actual capability execution.
    
    This is the runtime context that Capabilities receive when executing.
    
    Invariants:
        EXE-001: ExecutionContext shall never imply authority
        EXE-002: ExecutionContext shall not expose concrete implementations
        EXE-003: ExecutionContext shall preserve provenance information
    """
    
    # Invocation identity
    invocation_id: str
    execution_id: CapabilityExecutionId
    
    # Input context (what the capability should process)
    inputs: Dict[str, Any]
    
    # Execution metadata
    execution_context: Dict[str, Any] = field(default_factory=dict)
    provenance: Optional[str] = None  # How did we get here?
    
    # Resource budget (constraints under which to execute)
    timeout_seconds: Optional[float] = None
    resource_budget: Dict[str, int] = field(default_factory=dict)
    
    # Cancellation support
    cancellation_token: "ExecutionContextCancellationView" = field(
        default_factory=lambda: ExecutionContextCancellationView(is_requested=False)
    )
    
    # Observability hooks (for emitting diagnostic data)
    observability_port: Optional["ExecutionObservabilityPort"] = None
    
    def with_timeout(self, timeout_seconds: float) -> "ExecutionExecutionContext":
        """Create copy with updated timeout."""
        return dataclass_replace(self, timeout_seconds=timeout_seconds)


@dataclass(frozen=True, slots=True)
class ExecutionContextCancellationView:
    """
    Read-only view of cancellation state for execution context.
    
    Invariants:
        EXE-CAN-001: Cancellation check is cooperative
        EXE-CAN-002: Cancellation does not guarantee immediate termination
    """
    
    is_requested: bool
    reason: Optional[str] = None
    
    def check(self) -> None:
        """Raise exception if cancellation has been requested."""
        if self.is_requested:
            raise ExecutionCancelledError(
                f"Execution cancelled: {self.reason or 'no reason given'}"
            )
    
    async def wait_for_cancellation(self) -> str:
        """Wait until cancellation is requested. Returns the reason."""
        return self.reason or "cancellation requested"


class ExecutionCancelledError(Exception):
    """Raised when execution detects cancellation has been requested."""


@runtime_checkable
class ExecutionObservabilityPort(Protocol):
    """
    Port for emitting observability data during execution.
    
    Invariants:
        OBS-001: Observability failure shall not silently alter semantic results
        OBS-002: Every lifecycle transition shall produce observability data
    """
    
    async def emit_trace(self, record: "TraceRecord") -> None:
        """Emit a trace record for tracing."""
        ...
    
    async def record_audit(self, record: "AuditRecord") -> None:
        """Record an audit record."""
        ...


@dataclass(frozen=True, slots=True)
class TraceRecord:
    """Structured trace record for observability."""
    
    invocation_id: str
    event_type: str  # e.g., "execution_start", "output_produced"
    timestamp_utc: float = field(default_factory=time.time)
    message: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """Structured audit record for compliance and debugging."""
    
    invocation_id: str
    event_type: str
    timestamp_utc: float = field(default_factory=time.time)
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None


# =============================================================================
# CAPABILITY EXECUTION PROTOCOL
# =============================================================================


@runtime_checkable
class CapabilityExecutor(Protocol):
    """
    Protocol for capability execution.
    
    Capabilities implement this protocol to be executable by the system.
    
    Invariants:
        EXEC-001: Execute shall consume declared inputs
        EXEC-002: Execute shall produce explicit outputs
        EXEC-003: Execute shall preserve execution context
        EXEC-004: Execute shall never mutate System state directly
    """
    
    @property
    def capability_id(self) -> str:
        """Return stable capability identifier."""
        ...
    
    async def execute(
        self,
        context: ExecutionExecutionContext,
        inputs: Dict[str, Any]
    ) -> "CapabilityExecutionResult":
        """
        Execute the capability with given context and inputs.
        
        Args:
            context: Runtime execution context
            inputs: Input data for this invocation
            
        Returns:
            Capability execution result with outputs and status
            
        Invariants:
            EXEC-005: Execution shall never bypass authority verification
            EXEC-006: Execution shall preserve provenance
            EXEC-007: Execution shall be deterministic where applicable
        """
        ...


@dataclass(frozen=True, slots=True)
class CapabilityExecutionResult:
    """
    Result of capability execution.
    
    Invariants:
        RES-001: Successful invocation shall produce explicit result
        RES-002: Result shall preserve invocation identity
        RES-003: Results shall remain immutable once published
    """
    
    # Identity (required)
    invocation_id: str
    execution_id: str
    
    # Execution status
    status: "ExecutionStatus"
    
    # Outputs (if successful)
    outputs: Dict[str, Any] = field(default_factory=dict)
    
    # Output metadata
    output_schema_version: int = 1
    provenance: Optional[str] = None
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Diagnostics
    execution_time_seconds: Optional[float] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.COMPLETED
    
    def to_publication_result(self, result_id: str) -> "PublishedResult":
        """Convert to published result format."""
        return PublishedResult(
            result_id=result_id,
            invocation_id=self.invocation_id,
            execution_id=self.execution_id,
            outputs=self.outputs,
            status=self.status.value,
            created_at_utc=self.completed_at_utc or self.started_at_utc,
        )


class ExecutionStatus(Enum):
    """Possible execution statuses."""
    
    COMPLETED = "completed"
    YIELDED = "yielded"           # Returned to core for rescheduling
    WAITING = "waiting"           # Waiting for external event
    DELEGATED = "delegated"       # Delegated to another executor
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


# =============================================================================
# CAPABILITY RESULT FOR PUBLICATION
# =============================================================================


@dataclass(frozen=True, slots=True)
class PublishedResult:
    """
    Result published to streams after successful invocation.
    
    Invariants:
        PUB-001: Results shall remain immutable once published
        PUB-002: Publication shall preserve provenance
        PUB-003: Integrity metadata shall be included
    """
    
    result_id: str
    
    # Invocation identity (for tracing)
    invocation_id: str
    execution_id: str
    
    # Semantic outputs
    outputs: Dict[str, Any]
    
    # Status
    status: str  # One of ExecutionStatus values
    
    # Timestamps
    created_at_utc: float
    
    # Provenance
    provenance: Optional[str] = None
    author_id: Optional[str] = None
    
    # Integrity metadata
    integrity_hash: Optional[str] = None
    signature: Optional[str] = None
    
    def get_integrity_data(self) -> str:
        """Get data that should be hashed for integrity verification."""
        import json
        return json.dumps({
            "invocation_id": self.invocation_id,
            "execution_id": self.execution_id,
            "outputs": self.outputs,
            "created_at_utc": self.created_at_utc,
        }, sort_keys=True)


# =============================================================================
# CAPABILITY METADATA (for determinism, type checking, etc.)
# =============================================================================


@dataclass(frozen=True, slots=True)
class CapabilityMetadata:
    """
    Static metadata about a capability.
    
    This is used for admission decisions and should not change during execution.
    
    Invariants:
        META-001: Metadata shall include determinism declaration
        META-002: Metadata shall be immutable once registered
        META-003: Metadata shall include required input/output schemas
    """
    
    # Identity
    capability_id: str
    
    # Type information
    capability_type: str  # e.g., "cognitive", "computational", "transformation"
    
    # Determinism
    is_deterministic: bool = False
    determinism_class: Optional[str] = None  # e.g., "strict", "idempotent"
    
    # Inputs and outputs (schema references)
    input_schema_uri: Optional[str] = None
    output_schema_uri: Optional[str] = None
    
    # Resource requirements
    resource_requirements: Dict[str, int] = field(default_factory=dict)
    
    # Authority requirements
    requires_authority_verification: bool = True
    requires_dependency_check: bool = True
    
    # Lifecycle properties
    supports_cancellation: bool = True
    supports_replay: bool = False  # Can this capability be replayed?
    
    # Observability
    exposes_diagnostics: bool = True


# =============================================================================
# INVOCATION REQUEST (from Interaction to Execution)
# =============================================================================


@dataclass(frozen=True, slots=True)
class CapabilityInvocationRequest:
    """
    Request from an Interaction for a Capability invocation.
    
    This is the canonical way Interactions request Capability work.
    
    Invariants:
        REQ-001: Submission is a request, not a command
        REQ-002: Execution may accept, defer, or reject according to policy
        REQ-003: Requester shall not infer successful scheduling merely because submitted
    """
    
    # Identity
    request_id: str  # Unique request identifier
    invocation_id: CapabilityInvocationId
    
    # Which capability
    capability_id: str
    
    # Input data
    inputs: Dict[str, Any]
    
    # Context
    interaction_id: str  # The Interaction that requested this
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    # Constraints
    priority: int = 0  # Lower = higher priority
    deadline_seconds: Optional[float] = None
    
    # Resource budget
    resource_budget: Dict[str, int] = field(default_factory=dict)
    
    # Requester
    requester_id: str = "unknown"
    
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True, slots=True)
class CapabilityInvocationHandle:
    """
    Handle for tracking an invocation request.
    
    Provides ability to await results or cancel execution.
    """
    
    request_id: str
    invocation_id: str
    status: str  # One of ExecutionStatus values
    lifecycle_state: str  # One of CapabilityLifecycleState values


# =============================================================================
# CANCELLATION REQUESTS
# =============================================================================


@dataclass(frozen=True, slots=True)
class InvocationCancellationRequest:
    """
    Request to cancel an invocation.
    
    Invariants:
        CAN-REQ-001: Cancellation shall be explicit
        CAN-REQ-002: Cancellation may occur before or during execution
        CAN-REQ-003: Partial execution shall remain observable
    """
    
    # Identity
    cancellation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    invocation_id: str
    
    # Reason
    reason: str  # Human-readable reason for cancellation
    
    # Source
    source: "CancellationSource"
    requested_at_utc: float = field(default_factory=time.time)
    
    # Type of cancellation
    is_immediate: bool = False  # Should execution stop immediately?
    preserve_partial_results: bool = True  # Keep partial results if any?


class CancellationSource(Enum):
    """Source of a cancellation request."""
    
    USER = "user"
    TIMEOUT = "timeout"
    PARENT = "parent"         # Parent invocation cancelled
    SYSTEM = "system"         # System shutdown or resource exhaustion
    DEADLINE_EXCEEDED = "deadline_exceeded"


# =============================================================================
# FAILURE TYPES (for capability execution failures)
# =============================================================================


class CapabilityFailureCategory(Enum):
    """Categories of capability failure."""
    
    # Admission failures
    ADMISSION_FAILED = "admission_failed"
    
    # Dependency failures
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    DEPENDENCY_TIMEOUT = "dependency_timeout"
    
    # Execution failures
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_TIMED_OUT = "execution_timed_out"
    
    # Interruption failures
    INTERUPTED = "interrupted"
    
    # Resource failures
    RESOURCE_EXHAUSTED = "resource_exhausted"
    
    # Internal failures
    INTERNAL_ERROR = "internal_error"


@dataclass(frozen=True, slots=True)
class CapabilityFailure:
    """
    Structured failure information for capability invocation.
    
    Invariants:
        FAIL-001: Failures shall be explicit
        FAIL-002: Failures shall preserve provenance
        FAIL-003: Failures shall never corrupt invocation identity
    """
    
    # Identity (required)
    invocation_id: str
    
    # Classification
    category: CapabilityFailureCategory
    code: str  # Machine-readable failure code
    
    # Message
    message: str  # Human-readable explanation
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_layer: Optional[str] = None
    causal_chain: Tuple[str, ...] = field(default_factory=tuple)
    
    # Recovery information
    retryable: bool = False
    recovery_hint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert failure to dictionary for serialization."""
        return {
            "invocation_id": self.invocation_id,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "code": self.code,
            "message": self.message,
            "occurred_at_utc": self.occurred_at_utc,
            "source_layer": self.source_layer,
            "retryable": self.retryable,
            "recovery_hint": self.recovery_hint,
        }


# =============================================================================
# RESULT PUBLICATION
# =============================================================================


@dataclass(frozen=True, slots=True)
class ResultPublication:
    """
    Request to publish a Capability result.
    
    This is how successful invocations produce published outputs.
    
    Invariants:
        PUB-REQ-001: Publication shall preserve invocation identity
        PUB-REQ-002: Publication shall be atomic
        PUB-REQ-003: Published results shall be immutable
    """
    
    # Identity
    publication_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    invocation_id: str
    
    # Result to publish
    result: PublishedResult
    
    # Target streams (where to publish)
    target_stream_ids: List[str] = field(default_factory=list)
    
    # Routing metadata
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Timestamps
    requested_at_utc: float = field(default_factory=time.time)
    published_at_utc: Optional[float] = None
    
    # Status (forward reference using string)
    status: str = "pending"


class PublicationStatus(Enum):
    """Status of a result publication."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# STREAM INTEGRATION TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class CapabilityStreamIntegration:
    """
    Integration points between capability invocation and streams.
    
    Defines how capabilities interact with streams during execution.
    
    Invariants:
        STRM-INT-001: Streams transport Capability Interactions and published results
        STRM-INT-002: Streams never execute Capabilities
        STRM-INT-003: Transport remains independent of execution
    """
    
    # Input streams (what the capability reads from)
    input_stream_ids: List[str]
    
    # Output streams (where results are published)
    output_stream_ids: List[str]
    
    # Read position tracking
    read_positions: Dict[str, int] = field(default_factory=dict)  # stream_id -> position
    
    # Write positions
    write_positions: Dict[str, int] = field(default_factory=dict)  # stream_id -> position
    
    # Replay safety
    is_replay: bool = False
    
    # Integrity verification
    verify_integrity: bool = True


# =============================================================================
# OWNERSHIP AND AUTHORITY PROTOCOLS
# =============================================================================


@runtime_checkable
class OwnershipPreservationProtocol(Protocol):
    """
    Protocol for verifying ownership preservation during invocation.
    
    Invariants:
        OWN-001: Capabilities own computation
        OWN-002: Execution owns scheduling
        OWN-003: Interactions own communication semantics
        OWN-004: Streams own transport
        OWN-005: Systems own persistent state
        OWN-006: Ownership shall remain immutable throughout invocation
    """
    
    def verify_ownership(self, action_type: str) -> Tuple[bool, Optional[str]]:
        """
        Verify that ownership is preserved for given action.
        
        Returns:
            (is_valid, violation_message)
        """
        ...


@runtime_checkable
class AuthorityPreservationProtocol(Protocol):
    """
    Protocol for verifying authority preservation during invocation.
    
    Invariants:
        AUTH-001: Capabilities shall never self-authorize
        AUTH-002: Capability invocation shall always remain subject to external authority verification
        AUTH-003: Capability execution shall never elevate architectural privileges
        AUTH-004: Authority remains external to computation
    """
    
    def verify_authority(self, invocation_context: InvocationContext) -> Tuple[bool, Optional[str]]:
        """
        Verify that authority is preserved for given invocation.
        
        Returns:
            (is_valid, violation_message)
        """
        ...


# =============================================================================
# REPLAY SUPPORT TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class ReplayMetadata:
    """
    Metadata required for replaying an invocation.
    
    Invariants:
        REPL-001: Replay shall preserve invocation ordering
        REPL-002: Replay shall preserve lifecycle progression
        REPL-003: Replay shall never fabricate Capability executions
    """
    
    # Original invocation identity
    original_invocation_id: str
    
    # Timestamps for deterministic ordering
    original_created_at_utc: float
    original_completed_at_utc: Optional[float] = None
    
    # Execution context (for replaying with same inputs)
    execution_context_hash: str  # Hash of original execution context
    
    # Inputs hash (to verify same inputs are provided)
    inputs_hash: str
    
    # Lifecycle state trace (for verifying replay fidelity)
    lifecycle_trace: List[str] = field(default_factory=list)


# =============================================================================
# OBSERVABILITY TYPES
# =============================================================================


@dataclass(frozen=True, slots=True)
class InvocationObservabilityMetadata:
    """
    Immutable diagnostic metadata for Capability invocation observability.
    
    Invariants:
        OBS-INV-001: Every invocation shall expose immutable diagnostic metadata
        OBS-INV-002: Metadata shall include all required fields
        OBS-INV-003: Internal implementation details remain private
    """
    
    # Identity (required)
    invocation_id: str
    capability_id: str
    
    # Context
    interaction_id: str
    execution_context_hash: Optional[str] = None
    
    # Lifecycle tracking
    lifecycle_state: CapabilityLifecycleState
    created_at_utc: float
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Outcome
    execution_status: ExecutionStatus = ExecutionStatus.COMPLETED
    failure_category: Optional[CapabilityFailureCategory] = None
    
    # Timing
    total_duration_seconds: Optional[float] = None
    
    # Integrity
    integrity_verified: bool = True
    
    def get_summary(self) -> str:
        """Get human-readable summary of invocation."""
        return (
            f"Invocation {self.invocation_id}: "
            f"{self.capability_id} in state {self.lifecycle_state.value}, "
            f"status={self.execution_status.value}"
        )


# =============================================================================
# CAPABILITY PROTOCOL
# =============================================================================


@runtime_checkable
class Capability(Protocol):
    """
    Protocol for all Capabilities in Gordon.
    
    This is the canonical interface that all Capabilities must implement.
    
    Invariants:
        CAP-001: Every Capability shall execute only through canonical invocation
        CAP-002: Every Capability shall preserve architectural ownership and authority
        CAP-003: Execution remains the sole authority for Capability scheduling
        CAP-004: Systems remain the sole authority for persistent state mutation
    """
    
    @property
    def capability_id(self) -> str:
        """Return stable capability identifier."""
        ...
    
    @property
    def metadata(self) -> CapabilityMetadata:
        """Return static metadata about this capability."""
        ...
    
    async def execute(
        self,
        context: InvocationContext,
        inputs: Dict[str, Any]
    ) -> CapabilityExecutionResult:
        """
        Execute the capability.
        
        This is the canonical entry point for Capability invocation.
        
        Invariants:
            CAP-005: Execution shall only occur through this method
            CAP-006: Execution shall preserve determinism where declared
            CAP-007: Execution shall never mutate System state directly
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "CapabilityInvocationId",
    "CapabilityAdmissionId",
    "CapabilityExecutionId",
    
    # Lifecycle states
    "CapabilityLifecycleState",
    "is_terminal_state",
    "get_allowed_transitions",
    
    # Context types
    "InvocationContext",
    "AdmissionContext",
    "ExecutionExecutionContext",
    "ExecutionContextCancellationView",
    
    # Protocol types
    "ExecutionObservabilityPort",
    "TraceRecord",
    "AuditRecord",
    "CapabilityExecutor",
    
    # Result types
    "CapabilityExecutionResult",
    "ExecutionStatus",
    "PublishedResult",
    
    # Metadata
    "CapabilityMetadata",
    
    # Request/Handle types
    "CapabilityInvocationRequest",
    "CapabilityInvocationHandle",
    
    # Cancellation types
    "InvocationCancellationRequest",
    "CancellationSource",
    
    # Failure types
    "CapabilityFailureCategory",
    "CapabilityFailure",
    
    # Publication types
    "ResultPublication",
    "PublicationStatus",
    
    # Stream integration
    "CapabilityStreamIntegration",
    
    # Protocol types for verification
    "OwnershipPreservationProtocol",
    "AuthorityPreservationProtocol",
    
    # Replay types
    "ReplayMetadata",
    
    # Observability types
    "InvocationObservabilityMetadata",
    
    # Base protocol
    "Capability",
]