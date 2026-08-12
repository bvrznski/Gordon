# Execution Contracts
# =================

"""
Core contracts for execution components.

These define stable boundaries between Execution and Core.
Execution may depend on these contracts but NOT on concrete Core implementations.
"""

from typing import Protocol, Any, Optional, Dict, List, Tuple, Type
from dataclasses import dataclass, field
import abc


# =============================================================================
# Executable Unit Contract (Core → Execution)
# =============================================================================

class ExecutableUnit(Protocol):
    """
    Protocol for executable units that Core can invoke without knowing their type.
    
    This is how Core executes execution units generically:
        - Core does NOT import ConversationCycle, ReasoningLoop, etc.
        - Core calls unit.execute(context) through this protocol
        - The unit returns a standardized outcome
    
    Invariants:
        EXU-001: Every executable unit shall expose a stable execution identifier.
        EXU-002: Execution shall begin only through the declared executable contract.
        EXU-003: The executable shall return a declared outcome rather than mutate Core runtime state directly.
        EXU-004: Core shall not inspect concrete execution implementation types to determine runtime behaviour.
    """
    
    @property
    def execution_id(self) -> str:
        """Return stable execution identifier."""
        ...
    
    async def execute(self, context: "RuntimeExecutionContext") -> "ExecutionOutcome":
        """Execute the unit with given context. Return standardized outcome."""
        ...


# =============================================================================
# Runtime Execution Context (Core → Execution)
# =============================================================================

@dataclass(frozen=True)
class RuntimeExecutionContext:
    """
    Invocation-scoped execution context provided by Core to units.
    
    This is NOT a service locator - it contains only invocation-specific data.
    
    Invariants:
        CTX-001: ExecutionContext shall be invocation-scoped.
        CTX-002: ExecutionContext shall not become an unrestricted service locator.
        CTX-003: ExecutionContext shall not expose concrete runtime implementations.
        CTX-004: ExecutionContext contents shall be explicitly declared and typed.
    """
    
    # Identity (required - no defaults)
    execution_id: str
    started_at: float  # monotonic timestamp
    
    # Optional fields with defaults
    parent_execution_id: Optional[str] = None
    cancellation_view: Optional["CancellationView"] = None
    deadline_seconds: Optional[float] = None
    resource_lease: Optional[Any] = None
    correlation_id: Optional[str] = None
    observability_port: Optional[Any] = None


# =============================================================================
# Execution Outcome (Execution → Core)
# =============================================================================

class ExecutionStatus:
    """Possible execution status values."""
    
    COMPLETED = "completed"
    YIELDED = "yielded"        # Returned to core for rescheduling later
    WAITING = "waiting"        # Waiting for external event
    DELEGATED = "delegated"    # Delegated to another unit
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True)
class ExecutionOutcome:
    """
    Result of execution returned from ExecutableUnit.execute().
    
    This is how units communicate results back to Core without mutating state directly.
    
    Invariants:
        OUT-001: A returned outcome shall not directly mutate Core runtime state.
        OUT-002: Semantic completion and runtime completion shall remain distinguishable.
        OUT-003: Continuation is a request subject to Core admission.
        OUT-004: Failure outcomes shall contain structured failure classification.
    """
    
    # Status (required)
    status: str  # One of ExecutionStatus.* values
    
    # Semantic result
    semantic_result: Optional[Any] = None  # The actual meaningful result
    
    # Lifecycle intent (what should happen next?)
    lifecycle_intent: Optional[str] = None  # e.g., "request_completion", "request_pause"
    
    # Continuation request
    continuation: Optional["ContinuationRequest"] = None
    
    # Delegation request
    delegation: Optional["DelegationRequest"] = None
    
    # Failure information
    failure: Optional["ContractFailure"] = None
    
    # Checkpoint hint (should Core create a checkpoint?)
    checkpoint_hint: Optional[str] = None  # "create", "skip", "on_error"
    
    # Events emitted during execution
    emitted_events: Tuple[Any, ...] = field(default_factory=tuple)


# =============================================================================
# Continuation Requests
# =============================================================================

@dataclass(frozen=True)
class ContinuationRequest:
    """
    Request for Core to continue execution.
    
    This is a request, not a command. Core decides when and whether to act on it.
    """
    
    delay_seconds: Optional[float] = None  # Delay before next cycle
    priority_hint: Optional[int] = None    # Priority hint (lower = higher priority)
    deadline_hint: Optional[float] = None  # Deadline for continuation


@dataclass(frozen=True)
class DelegationRequest:
    """
    Request to delegate execution to another unit.
    
    Core will create and schedule the new unit, passing appropriate context.
    """
    
    target_type: str  # Type identifier of target unit
    transfer_context: bool = True  # Whether to transfer current context


# =============================================================================
# Lifecycle Port (Execution → Core)
# =============================================================================

class LifecyclePort(Protocol):
    """
    Port for expressing lifecycle intent and receiving lifecycle state.
    
    Execution expresses intent, Core commits transitions.
    
    Invariants:
        LCP-001: Execution expresses lifecycle intent. Core owns committed lifecycle state.
        LCP-002: Lifecycle transitions shall be validated against an explicit transition graph.
        LCP-003: Lifecycle mutations shall be atomic.
        LCP-004: Every accepted or rejected transition shall be observable.
        LCP-005: A Thread shall not directly assign its authoritative runtime state.
    """
    
    async def request_transition(
        self,
        execution_id: str,
        from_state: str,
        to_state: str,
        reason: Optional[str] = None
    ) -> "LifecycleTransitionResult":
        """Request a lifecycle transition. Returns result with acceptance status."""
        ...
    
    async def get_state(self, execution_id: str) -> Optional[str]:
        """Get current lifecycle state for an execution unit."""
        ...
    
    async def observe_transitions(
        self,
        execution_id: str,
        handler
    ) -> None:
        """Subscribe to lifecycle transition events for an execution unit."""
        ...


@dataclass(frozen=True)
class LifecycleTransitionResult:
    """
    Result of a lifecycle transition request.
    """
    
    accepted: bool
    previous_state: Optional[str] = None
    current_state: Optional[str] = None
    rejection_reason: Optional[str] = None


# =============================================================================
# Execution Runtime Port (Execution → Core)
# =============================================================================

class ExecutionRuntimePort(Protocol):
    """
    Port for requesting execution of semantic work.
    
    Invariants:
        ERP-001: Submission is a request, not a command.
        ERP-002: Core may accept, defer, downgrade, or reject a submission according to runtime policy.
        ERP-003: Execution shall not infer successful scheduling merely because submission was requested.
        ERP-004: Execution shall not receive direct access to scheduler internals.
    """
    
    async def submit(
        self,
        request: "ExecutionRequest"
    ) -> "ExecutionHandle":
        """Submit an execution request. Returns a handle for tracking."""
        ...
    
    async def await_result(
        self,
        handle: "ExecutionHandle",
        timeout_seconds: Optional[float] = None
    ) -> ExecutionOutcome:
        """Wait for execution result with optional timeout."""
        ...
    
    async def cancel(
        self,
        handle: "ExecutionHandle",
        reason: str
    ) -> bool:
        """Request cancellation of scheduled execution. Returns True if accepted."""
        ...


@dataclass(frozen=True)
class ExecutionRequest:
    """
    Request to execute a semantic unit.
    
    This contains only runtime-neutral information. Core decides how to schedule it.
    """
    
    request_id: str
    unit: ExecutableUnit  # The executable unit (via protocol)
    priority: int = 2     # Priority hint (lower = higher priority)
    deadline_seconds: Optional[float] = None
    budget: Optional["ResourceBudget"] = None


@dataclass(frozen=True)
class ExecutionHandle:
    """
    Handle for tracking execution of a request.
    
    Provides ability to await results or cancel execution.
    """
    
    request_id: str
    execution_id: str
    status: str  # One of ExecutionStatus.* values


# =============================================================================
# Checkpoint Port (Execution → Core)
# =============================================================================

class CheckpointPort(Protocol):
    """
    Port for checkpoint save/load operations.
    
    Execution provides snapshot content, Core handles storage and retrieval.
    
    Invariants:
        CPP-001: Execution shall not write directly to checkpoint storage.
        CPP-002: A snapshot shall be self-identifying through schema name and version.
        CPP-003: Checkpoint creation shall not imply successful semantic restoration.
        CPP-004: Core stores snapshots but does not reinterpret their semantic meaning.
    """
    
    async def save(
        self,
        snapshot: "SemanticSnapshot"
    ) -> "CheckpointReference":
        """Save a semantic snapshot. Returns reference for retrieval."""
        ...
    
    async def load(
        self,
        execution_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional["SemanticSnapshot"]:
        """Load a semantic snapshot for given execution unit."""
        ...
    
    async def list_references(
        self,
        execution_id: str
    ) -> Tuple["CheckpointReference", ...]:
        """List all checkpoint references for an execution unit."""
        ...


@dataclass(frozen=True)
class SemanticSnapshot:
    """
    Semantic state snapshot to be persisted.
    
    Contains only semantic information, not runtime internals.
    """
    
    schema_name: str  # e.g., "conversation_thread"
    schema_version: int
    execution_id: str
    
    # Serializable semantic state (no concrete types that Core doesn't know)
    semantic_state: Dict[str, Any]
    
    # Continuation descriptor (where to resume from)
    continuation: Optional["ContinuationDescriptor"] = None


@dataclass(frozen=True)
class ContinuationDescriptor:
    """
    Information about where and how to continue execution.
    """
    
    next_cycle_type: str  # Type identifier of the next cycle
    context_snapshot: Dict[str, Any]  # Context needed for continuation


@dataclass(frozen=True)
class CheckpointReference:
    """
    Reference to a saved checkpoint for retrieval.
    """
    
    checkpoint_id: str
    created_at: float  # monotonic timestamp
    schema_name: str
    schema_version: int


# =============================================================================
# Cancellation View (Execution → Core)
# =============================================================================

@dataclass(frozen=True)
class CancellationView:
    """
    Read-only view of cancellation state.
    
    Execution units can check for cancellation and respond appropriately.
    
    Invariants:
        CAN-001: Cancellation request and cancellation completion are distinct events.
        CAN-002: Execution shall acknowledge cancellation only after reaching a declared safe boundary.
        CAN-003: A non-interruptible stage shall be bounded.
        CAN-004: Core may escalate cancellation according to runtime policy, but escalation shall remain observable.
    """
    
    is_requested: bool
    reason: Optional[str] = None
    
    async def wait_for_cancellation(self) -> str:
        """Wait until cancellation is requested. Returns the reason."""
        ...
    
    def check(self) -> None:
        """Raise an exception if cancellation has been requested."""
        if self.is_requested:
            raise ExecutionCancelledError(
                f"Execution cancelled: {self.reason or 'no reason given'}"
            )


class ExecutionCancelledError(Exception):
    """Raised when checking for cancellation that was requested."""
    pass


# =============================================================================
# Observability Port (Execution → Core)
# =============================================================================

@dataclass(frozen=True)
class TraceRecord:
    """Structured trace record for observability."""
    
    execution_id: str
    event_type: str  # e.g., "cycle_start", "lifecycle_transition"
    timestamp: float
    message: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditRecord:
    """Structured audit record for compliance and debugging."""
    
    execution_id: str
    event_type: str
    timestamp: float
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None


class ObservabilityPort(Protocol):
    """
    Port for emitting structured observability data.
    
    Execution emits records, Core handles transport and storage.
    
    Invariants:
        OBS-001: Every lifecycle transition shall produce a structured audit record.
        OBS-002: Every Cycle shall expose start, completion, interruption, and failure events.
        OBS-003: Observability failure shall not silently alter semantic results unless the contract explicitly declares observability as mandatory for that operation.
        OBS-004: Sensitive semantic state shall not be emitted without an explicit redaction policy.
    """
    
    def emit_trace(self, record: TraceRecord) -> None:
        """Emit a trace record for tracing/backtrace purposes."""
        ...
    
    def record_audit(self, record: AuditRecord) -> None:
        """Record an audit record for compliance/debugging."""
        ...


# =============================================================================
# Execution Factory Port (Composition Root → Core)
# =============================================================================

class ExecutionFactoryPort(Protocol):
    """
    Factory for creating and restoring execution units.
    
    This allows Core to instantiate execution units without importing their concrete classes.
    Concrete implementations are constructed at the composition root, not in Core.
    """
    
    def create(
        self,
        unit_type: str,
        execution_id: Optional[str] = None,
        **kwargs
    ) -> ExecutableUnit:
        """Create a new execution unit of given type."""
        ...
    
    def restore(
        self,
        snapshot: SemanticSnapshot
    ) -> ExecutableUnit:
        """Restore an execution unit from a saved snapshot."""
        ...


__all__ = [
    # Protocol types
    "ExecutableUnit",
    "LifecyclePort",
    "ExecutionRuntimePort",
    "CheckpointPort",
    "ObservabilityPort",
    "ExecutionFactoryPort",
    
    # Context and outcome
    "RuntimeExecutionContext",
    "ExecutionOutcome",
    "ExecutionStatus",
    
    # Requests and handles
    "ExecutionRequest",
    "ExecutionHandle",
    "ContinuationRequest",
    "DelegationRequest",
    
    # Checkpoint types
    "SemanticSnapshot",
    "ContinuationDescriptor",
    "CheckpointReference",
    
    # Cancellation
    "CancellationView",
    "ExecutionCancelledError",
    
    # Observability
    "TraceRecord",
    "AuditRecord",
    
    # Lifecycle result
    "LifecycleTransitionResult",
]