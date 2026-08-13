# Execution Types
# ===============

"""
Immutable, deterministic value types for execution components.

This module defines neutral types that can safely cross Core-Execution boundaries.
All types are immutable and use stable serialization formats.
"""

from dataclasses import dataclass, field
from typing import NewType, Tuple, Optional, Mapping, Any
from enum import Enum, auto
import uuid


# =============================================================================
# Semantic Identity Types (Section 2)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExecutionThreadId:
    """Unique semantic identity for an ExecutionThread."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "ExecutionThreadId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True, slots=True)
class ExecutionLoopId:
    """Unique semantic identity for an ExecutionLoop."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "ExecutionLoopId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True, slots=True)
class ExecutionLoopDecisionId:
    """Unique semantic identity for an ExecutionLoop decision."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "ExecutionLoopDecisionId":
        return cls(value=str(uuid.uuid4()))


# =============================================================================
# Thread Kinds (Semantic classification)
# =============================================================================

class ExecutionThreadKind(Enum):
    """
    Semantic classifications for ExecutionThreads.
    
    These do NOT require separate subclass implementations initially.
    They are semantic markers that inform policy decisions.
    """
    
    CONVERSATION = "conversation"
    TASK = "task"
    MONITORING = "monitoring"
    INTERNAL = "internal"


# =============================================================================
# Thread Lifecycle States (Semantic)
# =============================================================================

class ExecutionThreadStatus(Enum):
    """
    Semantic lifecycle states of an ExecutionThread.
    
    These describe the Thread's state from a semantic continuity perspective,
    not runtime execution state.
    
    Allowed transitions:
        CREATED -> ACTIVE | SUSPENDED | TERMINATED
        ACTIVE -> AWAITING_INPUT | SUSPENDED | DELEGATED | COMPLETED | INTERRUPTED | FAILED | TERMINATED
        AWAITING_INPUT -> ACTIVE | SUSPENDED | TERMINATED
        SUSPENDED -> ACTIVE | TERMINATED
        DELEGATED -> ACTIVE | COMPLETED | FAILED | TERMINATED
        INTERRUPTED -> ACTIVE | SUSPENDED | TERMINATED
        FAILED -> ACTIVE | SUSPENDED | TERMINATED
        
    Terminal states:
        COMPLETED, TERMINATED
    
    FAILED is recoverable unless explicitly finalized.
    """
    
    # Initial state
    CREATED = "created"
    
    # Active states
    ACTIVE = "active"
    AWAITING_INPUT = "awaiting_input"
    SUSPENDED = "suspended"
    DELEGATED = "delegated"
    
    # Terminal states
    COMPLETED = "completed"       # Semantic purpose fulfilled
    TERMINATED = "terminated"     # Terminated without completion
    
    # Failure/interruption states (recoverable)
    INTERRUPTED = "interrupted"   # Interrupted but potentially recoverable
    FAILED = "failed"             # Failed but may be recovered


def is_terminal_status(status: ExecutionThreadStatus) -> bool:
    """Check if an ExecutionThreadStatus is terminal."""
    return status in {ExecutionThreadStatus.COMPLETED, ExecutionThreadStatus.TERMINATED}


def get_allowed_transitions(status: ExecutionThreadStatus) -> Tuple[ExecutionThreadStatus, ...]:
    """
    Get the allowed transition targets for a given ExecutionThreadStatus.
    
    This encodes the state machine defined in the design document.
    """
    if status == ExecutionThreadStatus.CREATED:
        return (
            ExecutionThreadStatus.ACTIVE,
            ExecutionThreadStatus.SUSPENDED,
            ExecutionThreadStatus.TERMINATED
        )
    
    elif status == ExecutionThreadStatus.ACTIVE:
        return (
            ExecutionThreadStatus.AWAITING_INPUT,
            ExecutionThreadStatus.SUSPENDED,
            ExecutionThreadStatus.DELEGATED,
            ExecutionThreadStatus.COMPLETED,
            ExecutionThreadStatus.INTERRUPTED,
            ExecutionThreadStatus.FAILED,
            ExecutionThreadStatus.TERMINATED
        )
    
    elif status == ExecutionThreadStatus.AWAITING_INPUT:
        return (
            ExecutionThreadStatus.ACTIVE,
            ExecutionThreadStatus.SUSPENDED,
            ExecutionThreadStatus.TERMINATED
        )
    
    elif status == ExecutionThreadStatus.SUSPENDED:
        return (
            ExecutionThreadStatus.ACTIVE,
            ExecutionThreadStatus.TERMINATED
        )
    
    elif status == ExecutionThreadStatus.DELEGATED:
        return (
            ExecutionThreadStatus.ACTIVE,
            ExecutionThreadStatus.COMPLETED,
            ExecutionThreadStatus.FAILED,
            ExecutionThreadStatus.TERMINATED
        )
    
    elif status == ExecutionThreadStatus.INTERRUPTED:
        return (
            ExecutionThreadStatus.ACTIVE,
            ExecutionThreadStatus.SUSPENDED,
            ExecutionThreadStatus.TERMINATED
        )
    
    elif status == ExecutionThreadStatus.FAILED:
        return (
            ExecutionThreadStatus.ACTIVE,
            ExecutionThreadStatus.SUSPENDED,
            ExecutionThreadStatus.TERMINATED
        )
    
    # Terminal states have no transitions
    elif status in {ExecutionThreadStatus.COMPLETED, ExecutionThreadStatus.TERMINATED}:
        return tuple()
    
    else:
        raise ValueError(f"Unknown ExecutionThreadStatus: {status}")


# =============================================================================
# Lifecycle States (Runtime)
# =============================================================================

class ExecutionState(Enum):
    """
    Execution state machine states.
    
    These describe the lifecycle phase, not behavioral meaning.
    Transitions are deterministic and controlled by Core.
    """
    
    # Initial states
    CREATED = "created"         # Unit created but not yet submitted
    QUEUED = "queued"           # In ready queue, awaiting scheduling
    
    # Running states
    RUNNING = "running"         # Currently executing
    
    # Terminal states (success/failure)
    COMPLETED = "completed"     # Execution succeeded
    FAILED = "failed"           # Execution failed with error
    
    # Cancellation states
    CANCELLING = "cancelling"   # Cancellation requested, cleaning up
    CANCELLED = "cancelled"     # Cancellation completed


class LifecycleState(Enum):
    """
    Thread lifecycle state (distinct from execution state).
    
    Answers: "What is this runtime entity's lifecycle phase?"
    """
    
    NEW = "new"                 # Just created
    READY = "ready"             # Ready for first cycle
    ACTIVE = "active"           # Running cycles
    PAUSED = "paused"           # Temporarily suspended
    TERMINATING = "terminating" # Requested termination, cleaning up
    TERMINATED = "terminated"   # Terminated completely
    FAILED = "failed"           # Failed during any phase


class ExecutionCycleResult(Enum):
    """
    Result of an execution cycle.
    
    This determines what the Loop should do next:
        - COMPLETED: Cycle finished successfully, thread may terminate
        - CONTINUE: Cycle completed but should run again (same or different)
        - WAIT: Cycle cannot proceed yet, wait for external event
        - DELEGATE: Defer to another cycle/thread
        - FAIL: Cycle failed and cannot recover
    """
    
    COMPLETED = "completed"
    CONTINUE = "continue"
    WAIT = "wait"
    DELEGATE = "delegate"
    FAIL = "fail"


# =============================================================================
# Priority Levels (Neutral - no semantics)
# =============================================================================

class ExecutionPriority(Enum):
    """
    Execution priority levels.
    
    Lower numeric value = higher priority (runs first).
    These are metadata values; cognition decides which units get which priority.
    Core obeys but doesn't invent priorities.
    """
    
    CRITICAL = 0   # Must run immediately
    HIGH = 1       # High importance, short delay acceptable
    NORMAL = 2     # Standard priority
    LOW = 3        # Can be delayed if needed


# =============================================================================
# Resource Budget (Neutral - no semantics)
# =============================================================================

@dataclass(frozen=True)
class ExecutionResourceBudget:
    """
    Resource budget allocation for execution.
    
    Specifies constraints on how resources may be consumed.
    """
    
    # Time-based
    timeout_seconds: Optional[float] = None
    
    # Execution count limits
    max_cycles: Optional[int] = None
    max_iterations: Optional[int] = None
    
    # Resource consumption
    context_tokens: Optional[int] = None
    max_retries: Optional[int] = None


# =============================================================================
# Cancellation (Neutral - no semantics)
# =============================================================================

class ExecutionCancellationReason(Enum):
    """Reason for cancellation request."""
    
    TIMEOUT = "timeout"
    USER_REQUEST = "user_request"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    FAILURE = "failure"
    PARENT_CANCELLED = "parent_cancelled"
    DEADLINE_EXCEEDED = "deadline_exceeded"


@dataclass(frozen=True)
class ExecutionCancellationView:
    """
    Read-only cancellation state view.
    
    Execution units can check for cancellation requests
    and respond appropriately.
    """
    
    is_requested: bool
    reason: Optional[ExecutionCancellationReason] = None


# =============================================================================
# Thread Purpose (Semantic)
# =============================================================================

@dataclass(frozen=True)
class ExecutionThreadPurpose:
    """
    Enduring semantic purpose of an ExecutionThread.
    
    Objectives may change while purpose remains stable.
    """
    
    statement: str
    completion_criteria: Tuple[str, ...] = ()
    constraints: Tuple[str, ...] = ()


# =============================================================================
# Objective Status (Semantic)
# =============================================================================

class ExecutionObjectiveStatus(Enum):
    """
    Status of an ExecutionThread objective.
    
    These describe the lifecycle state of an individual objective within a thread.
    """
    
    PROPOSED = "proposed"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class ExecutionThreadObjective:
    """
    A semantic objective within an ExecutionThread.
    
    Objectives may be added, refined, completed, abandoned, or superseded.
    These transitions must be explicit and validated.
    """
    
    id: str
    description: str
    status: ExecutionObjectiveStatus = ExecutionObjectiveStatus.ACTIVE
    parent_id: Optional[str] = None
    completion_criteria: Tuple[str, ...] = ()


# =============================================================================
# Artifact Reference
# =============================================================================

@dataclass(frozen=True)
class ExecutionArtifactReference:
    """
    Reference to a semantic artifact produced by Thread execution.
    
    This is a pointer/reference - the artifact itself is stored elsewhere.
    """
    
    artifact_id: str
    kind: str  # e.g., "text", "code", "plan", "report"
    created_at_utc: float = 0.0


# =============================================================================
# Participant Reference (for conversation threads)
# =============================================================================

@dataclass(frozen=True)
class ExecutionParticipantReference:
    """
    Reference to a participant in a conversational Thread.
    """
    
    participant_id: str
    role: str  # e.g., "user", "assistant", "system"
    is_human: bool = False


# =============================================================================
# Plan Reference
# =============================================================================

@dataclass(frozen=True)
class ExecutionPlanReference:
    """
    Reference to an accepted plan.
    """
    
    plan_id: str
    version: int = 1


# =============================================================================
# Monitoring Target
# =============================================================================

@dataclass(frozen=True)
class ExecutionMonitoringTarget:
    """
    Target being monitored by a monitoring Thread.
    """
    
    target_id: str
    target_type: str  # e.g., "service", "metric", "resource"
    properties: Mapping[str, object] = field(default_factory=dict)


# =============================================================================
# Observation Reference
# =============================================================================

@dataclass(frozen=True)
class ExecutionObservationReference:
    """
    Reference to a monitoring observation.
    """
    
    observation_id: str
    target_id: str
    timestamp_utc: float = 0.0


# =============================================================================
# Alert Condition
# =============================================================================

@dataclass(frozen=True)
class ExecutionAlertCondition:
    """
    Condition that triggers an alert in a monitoring Thread.
    """
    
    condition_id: str
    description: str
    threshold_value: float
    operator: str  # e.g., "gt", "lt", "eq"


# =============================================================================
# Thread-specific State Types (Section 3.7)
# =============================================================================

@dataclass(frozen=True)
class ExecutionConversationThreadState:
    """
    Specialized state for conversation Threads.
    """
    
    participants: Tuple[ExecutionParticipantReference, ...] = ()
    current_topic: Optional[str] = None
    pending_user_input: bool = False
    conversational_commitments: Tuple[str, ...] = ()
    last_input_reference: Optional[str] = None
    last_response_reference: Optional[str] = None


@dataclass(frozen=True)
class ExecutionTaskThreadState:
    """
    Specialized state for task Threads.
    """
    
    plan: Optional[ExecutionPlanReference] = None
    current_step_id: Optional[str] = None
    completed_step_ids: Tuple[str, ...] = ()
    blocked_step_ids: Tuple[str, ...] = ()
    produced_artifacts: Tuple[ExecutionArtifactReference, ...] = ()
    progress: float = 0.0


@dataclass(frozen=True)
class ExecutionMonitoringThreadState:
    """
    Specialized state for monitoring Threads.
    """
    
    target: ExecutionMonitoringTarget
    baseline: Optional[ExecutionObservationReference] = None
    last_observation: Optional[ExecutionObservationReference] = None
    alert_conditions: Tuple[ExecutionAlertCondition, ...] = ()
    meaningful_change_detected: bool = False


@dataclass(frozen=True)
class ExecutionInternalThreadState:
    """
    Specialized state for internal Threads.
    """
    
    activation_reason: str
    internal_subject: str
    insight_references: Tuple[str, ...] = ()
    unresolved_contradictions: Tuple[str, ...] = ()
    maintenance_actions: Tuple[str, ...] = ()


# =============================================================================
# Generic Thread State Envelope
# =============================================================================

@dataclass(frozen=True)
class ExecutionThreadState:
    """
    Complete state envelope for a Thread.
    
    Uses specialized payload based on thread kind.
    """
    
    objectives: Tuple[ExecutionThreadObjective, ...] = ()
    accepted_context: Mapping[str, object] = field(default_factory=dict)
    unresolved_questions: Tuple[str, ...] = ()
    commitments: Tuple[str, ...] = ()
    artifacts: Tuple[ExecutionArtifactReference, ...] = ()
    last_cycle_outcome_id: Optional[str] = None
    specialized: Any = None  # ExecutionConversationThreadState, ExecutionTaskThreadState, etc.


# =============================================================================
# Thread Terminal Reason
# =============================================================================

@dataclass(frozen=True)
class ExecutionThreadTerminalReason:
    """
    Semantic reason for a Thread's terminal state.
    """
    
    reason_type: str  # e.g., "objective_completed", "failure", "terminated"
    description: str = ""
    details: Mapping[str, object] = field(default_factory=dict)


# =============================================================================
# Timestamp (Neutral - no semantics)
# =============================================================================

@dataclass(frozen=True)
class ExecutionTimestamp:
    """Monotonic timestamp for lifecycle events."""
    
    value: float  # monotonic time in seconds
    
    @classmethod
    def now(cls) -> "ExecutionTimestamp":
        """Create a timestamp from current monotonic time."""
        import time
        return cls(value=time.monotonic())
    
    def elapsed_since(self, other: "ExecutionTimestamp") -> float:
        """Return elapsed time since another timestamp."""
        return self.value - other.value


# =============================================================================
# Advancement Lease (prevents concurrent Thread advancement)
# =============================================================================
@dataclass(frozen=True, slots=True)
class AdvancementLease:
    """
    lease that grants permission to advance a specific Thread.
    
    Purpose: Prevent concurrent or reentrant advancement of the same Thread.
    
    Invariants:
        L-001: Only one active lease per Thread at any time
        L-002: Lease is released on success, failure, cancellation, or timeout
        L-003: Reentrant acquisition is rejected
        L-004: Concurrent advancement is rejected if same Thread has active lease
    """
    
    thread_id: str
    lease_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    expected_revision: int = 0  # What revision should the thread be at?
    coordinator_id: Optional[str] = None  # Which coordinator holds this lease
    acquired_at_utc: float = field(default_factory=lambda: 0.0)
    
    def is_expired(self, current_time: float, max_age_seconds: float = 300.0) -> bool:
        """Check if the lease has exceeded its maximum age."""
        return (current_time - self.acquired_at_utc) > max_age_seconds
    
    @classmethod
    def create(cls, thread_id: str, expected_revision: int = 0) -> "AdvancementLease":
        """Create a new lease for the given Thread."""
        import time
        return cls(
            thread_id=thread_id,
            acquired_at_utc=time.monotonic(),
            expected_revision=expected_revision,
        )
    
    def release(self) -> None:
        """
        Mark this lease as released.
        
        Note: Since this is a frozen dataclass, release() is informational only.
              The caller should remove the lease from their registry.
        """
        pass


@dataclass(frozen=True, slots=True)
class LeaseAcquisitionResult:
    """Result of attempting to acquire an advancement lease."""
    
    success: bool
    lease: Optional[AdvancementLease] = None
    rejection_reason: Optional[str] = None  # Why was acquisition rejected?
    existing_lease: Optional[AdvancementLease] = None  # If conflict, what exists?
    
    @classmethod
    def granted(cls, lease: AdvancementLease) -> "LeaseAcquisitionResult":
        """Create a successful acquisition result."""
        return cls(success=True, lease=lease)
    
    @classmethod
    def rejected(cls, reason: str, existing_lease: Optional[AdvancementLease] = None) -> "LeaseAcquisitionResult":
        """Create a rejection result."""
        return cls(success=False, rejection_reason=reason, existing_lease=existing_lease)


# =============================================================================
# Cancellation Model (typed, cooperative cancellation)
# =============================================================================
class CancellationSource(Enum):
    """
    Source of a cancellation request.
    
    Determines how cancellation should propagate:
        - USER: Requested by human user
        - TIMEOUT: Execution exceeded time budget
        - PARENT: Parent thread requested cancellation
        - SYSTEM: System shutdown or resource exhaustion
    """
    
    USER = "user"
    TIMEOUT = "timeout"
    PARENT = "parent"
    SYSTEM = "system"


class CancellationReason(Enum):
    """
    Semantic reason for cancellation.
    
    This is distinct from failure and preemption:
        - FAILURE: Execution encountered an error (still terminal)
        - PREEMPTION: Runtime control returned temporarily (resumable)
        - CANCELLATION: Semantic execution should stop (cooperative)
    """
    
    USER_REQUEST = "user_request"
    TIMEOUT = "timeout"
    PARENT_CANCELLED = "parent_cancelled"
    SYSTEM_SHUTDOWN = "system_shutdown"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    DEADLINE_EXCEEDED = "deadline_exceeded"


@dataclass(frozen=True, slots=True)
class CancellationRequest:
    """
    Request to cancel a Thread's execution.
    
    Cancellation is:
        - Cooperative (Thread checks and responds at safe boundaries)
        - Distinct from failure (semantic outcome may still be valid)
        - Distinct from preemption (not about runtime control return)
        - Propagatable according to explicit policy
    
    Safe cancellation points (at minimum):
        - Before Loop decision
        - Before Cycle creation  
        - Before each Stage
        - After each Stage
        - Before ThreadDelta commit
        - Before continuation application
    """
    
    target_thread_id: str
    reason: CancellationReason
    source: CancellationSource = CancellationSource.USER
    propagate_to_children: bool = False  # Should children also be cancelled?
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    requested_at_utc: float = field(default_factory=lambda: 0.0)
    
    @classmethod
    def user_request(cls, thread_id: str) -> "CancellationRequest":
        """Create a user-initiated cancellation request."""
        import time
        return cls(
            target_thread_id=thread_id,
            reason=CancellationReason.USER_REQUEST,
            source=CancellationSource.USER,
            requested_at_utc=time.monotonic(),
        )
    
    @classmethod
    def timeout(cls, thread_id: str) -> "CancellationRequest":
        """Create a timeout-initiated cancellation request."""
        import time
        return cls(
            target_thread_id=thread_id,
            reason=CancellationReason.TIMEOUT,
            source=CancellationSource.TIMEOUT,
            requested_at_utc=time.monotonic(),
        )
    
    def should_propagate(self) -> bool:
        """Check if this request should propagate to child threads."""
        return self.propagate_to_children


@dataclass(frozen=True, slots=True)
class CancellationToken:
    """
    Read-only token for checking cancellation status.
    
    This is what ExecutionStage receives - it can check but not modify state.
    """
    
    is_requested: bool
    reason: Optional[CancellationReason] = None
    request_id: Optional[str] = None
    
    def check(self) -> None:
        """Raise an exception if cancellation has been requested."""
        if self.is_requested:
            raise ExecutionCancelledError(
                f"Execution cancelled: {self.reason.value if self.reason else 'no reason given'}"
            )
    
    def check_or_raise(self, message: Optional[str] = None) -> None:
        """
        Check for cancellation and raise exception with optional custom message.
        
        Args:
            message: Optional additional context to include in the exception
        """
        if self.is_requested:
            full_msg = f"Execution cancelled"
            if message:
                full_msg += f": {message}"
            raise ExecutionCancelledError(full_msg)


class ExecutionCancelledError(Exception):
    """Raised when checking for cancellation that was requested."""
    pass


@dataclass(frozen=True, slots=True)
class CancellationOutcome:
    """
    Result of a cancellation operation.
    
    Distinguishes between:
        - NOT_REQUESTED: No cancellation was in progress
        - REQUESTED: Cancellation was accepted (not yet completed)
        - COMPLETED: Cancellation processing finished
        - ALREADY_COMPLETED: Already processed cancellation
    """
    
    outcome_type: str  # not_requested, requested, completed, already_completed
    thread_id: str
    reason: Optional[CancellationReason] = None
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    
    @classmethod
    def not_requested(cls, thread_id: str) -> "CancellationOutcome":
        return cls(outcome_type="not_requested", thread_id=thread_id)
    
    @classmethod
    def requested(cls, thread_id: str, reason: CancellationReason) -> "CancellationOutcome":
        import time
        return cls(
            outcome_type="requested",
            thread_id=thread_id,
            reason=reason,
            timestamp_utc=time.monotonic(),
        )
    
    @classmethod
    def completed(cls, thread_id: str, reason: CancellationReason) -> "CancellationOutcome":
        import time
        return cls(
            outcome_type="completed",
            thread_id=thread_id,
            reason=reason,
            timestamp_utc=time.monotonic(),
        )


# =============================================================================
# Preemption and Interruption (distinct from cancellation)
# =============================================================================
class ExecutionInterruptionType(Enum):
    """
    Types of interruption.
    
    Distinctions:
        - YIELD:自愿放弃 execution time (resumable, no state loss)
        - PREEMPTED: Runtime control returned to Core (resumable)
        - INTERRUPTED: Bounded work stopped before normal completion
        - CANCELLED: Semantic execution should stop
    """
    
    YIELD = "yield"              # Voluntarily yield execution time
    PREEMPTED = "preempted"      # Runtime control returned temporarily
    INTERRUPTED = "interrupted"  # Work stopped before normal completion


@dataclass(frozen=True, slots=True)
class InterruptionRequest:
    """Request to interrupt a Thread's current work."""
    
    target_thread_id: str
    interruption_type: ExecutionInterruptionType
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    requested_at_utc: float = field(default_factory=lambda: 0.0)
    
    @classmethod
    def preempt(cls, thread_id: str) -> "InterruptionRequest":
        """Create a preemption request."""
        import time
        return cls(
            target_thread_id=thread_id,
            interruption_type=ExecutionInterruptionType.PREEMPTED,
            requested_at_utc=time.monotonic(),
        )
    
    @classmethod
    def yield_execution(cls, thread_id: str) -> "InterruptionRequest":
        """Create a yield request."""
        import time
        return cls(
            target_thread_id=thread_id,
            interruption_type=ExecutionInterruptionType.YIELD,
            requested_at_utc=time.monotonic(),
        )


@dataclass(frozen=True, slots=True)
class InterruptionOutcome:
    """Result of an interruption operation."""
    
    outcome_type: str  # not_interrupted, interrupted, resumed, already_resumed
    thread_id: str
    interruption_type: Optional[ExecutionInterruptionType] = None
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    
    @classmethod
    def not_interrupted(cls, thread_id: str) -> "InterruptionOutcome":
        return cls(outcome_type="not_interrupted", thread_id=thread_id)
    
    @classmethod
    def interrupted(cls, thread_id: str, interruption_type: ExecutionInterruptionType) -> "InterruptionOutcome":
        import time
        return cls(
            outcome_type="interrupted",
            thread_id=thread_id,
            interruption_type=interruption_type,
            timestamp_utc=time.monotonic(),
        )
    
    @classmethod
    def resumed(cls, thread_id: str) -> "InterruptionOutcome":
        import time
        return cls(
            outcome_type="resumed",
            thread_id=thread_id,
            timestamp_utc=time.monotonic(),
        )


# =============================================================================
# Additional Semantic Identity Types - Cycle and Stage IDs only
# (LoopId already defined above in Section 2)
# =============================================================================

@dataclass(frozen=True)
class ExecutionCycleId:
    """Unique semantic identity for an ExecutionCycle."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "ExecutionCycleId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class ExecutionStageId:
    """Unique semantic identity for an ExecutionStage."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "ExecutionStageId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class ExecutionCheckpointId:
    """Unique semantic identity for a checkpoint."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "ExecutionCheckpointId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class ExecutionCorrelationId:
    """Unique semantic identity for correlation tracking."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "ExecutionCorrelationId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class ExecutionIdentifier:
    """Wrapper for various execution identifiers."""
    value: str


# =============================================================================
# Export all types
# =============================================================================

__all__ = [
    # Identifiers
    "ExecutionThreadId",
    "ExecutionLoopId",
    "ExecutionCycleId",
    "ExecutionStageId",
    "ExecutionLoopDecisionId",
    "ExecutionCheckpointId",
    "ExecutionCorrelationId",
    "ExecutionIdentifier",
    
    # Thread classifications
    "ExecutionThreadKind",
    
    # Lifecycle states (semantic)
    "ExecutionThreadStatus",
    "is_terminal_status",
    "get_allowed_transitions",
    
    # Lifecycle states (runtime)
    "ExecutionState",
    "LifecycleState",
    "ExecutionCycleResult",
    
    # Priority and resources
    "ExecutionPriority",
    "ExecutionResourceBudget",
    
    # Cancellation
    "ExecutionCancellationReason",
    "ExecutionCancellationView",
    
    # Thread semantic types
    "ExecutionThreadPurpose",
    "ExecutionObjectiveStatus",
    "ExecutionThreadObjective",
    "ExecutionArtifactReference",
    "ExecutionParticipantReference",
    "ExecutionPlanReference",
    "ExecutionMonitoringTarget",
    "ExecutionObservationReference",
    "ExecutionAlertCondition",
    "ExecutionConversationThreadState",
    "ExecutionTaskThreadState",
    "ExecutionMonitoringThreadState",
    "ExecutionInternalThreadState",
    "ExecutionThreadState",
    "ExecutionThreadTerminalReason",
    
    # Time
    "ExecutionTimestamp",
    
    # Advancement Lease (Enforcement 1)
    "AdvancementLease",
    "LeaseAcquisitionResult",
    
    # Cancellation Model (Enhancement 2)
    "CancellationSource",
    "CancellationReason",
    "CancellationRequest",
    "CancellationToken",
    "ExecutionCancelledError",
    "CancellationOutcome",
    
    # Preemption and Interruption (Enhancement 3)
    "ExecutionInterruptionType",
    "InterruptionRequest",
    "InterruptionOutcome",
]
