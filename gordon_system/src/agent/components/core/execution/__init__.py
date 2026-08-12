# Core Execution Primitives
# =========================

"""
Core runtime execution mechanics.

Provides comprehensive execution substrate for Gordon:
- Task lifecycle model with explicit states
- Deterministic scheduler with multiple queues
- Cooperative cancellation with propagation
- Multiple timeout policies (execution, queue, dependency wait)
- Task hierarchy with parent-child ownership
- Temporary execution context per task
- Cleanup coordination in reverse order
- Graceful shutdown sequence
- Structured observability events

This implements Phase 3.4: Execution, Scheduling, Cancellation, and Task Ownership.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Generic, Set
from enum import Enum, auto
import uuid
import time

# Re-export types for convenience
from ..types import (
    EntityId,
    ExecutionId,
    SchedulingId,
    Timestamp,
)

T = TypeVar("T")


class ExecutionState(Enum):
    """
    Task execution state machine states.
    
    These describe what the task is currently doing, not its lifecycle phase.
    Transitions are deterministic and controlled by the scheduler.
    
    State Flow:
        CREATED -> QUEUED -> WAITING -> READY -> RUNNING -> [COMPLETED|FAILED]
                            ^              |
                            |              v
                         CANCELLING     TIMED_OUT
                            |
                         CANCELLED
    
    Note: SUSPENDED is not implemented to keep state machine simple.
          Suspension can be modeled as stop/restart with same priority.
    """
    
    # Initial states
    CREATED = "created"           # Task created but not yet in scheduler
    QUEUED = "queued"             # In ready queue, waiting for scheduling
    
    # Dependency-related states
    WAITING = "waiting"           # Waiting for dependencies to complete
    READY = "ready"               # Dependencies satisfied, ready to run
    
    # Running state
    RUNNING = "running"           # Currently executing
    
    # Terminal states (success/failure)
    COMPLETED = "completed"       # Execution succeeded
    FAILED = "failed"             # Execution failed with error
    
    # Timeout states
    TIMED_OUT = "timed_out"       # Execution exceeded timeout
    
    # Cancellation states
    CANCELLING = "cancelling"     # Cancellation requested, cleaning up
    CANCELLED = "cancelled"       # Cancellation completed


class TaskState(Enum):
    """
    Task lifecycle state (distinct from execution state).
    
    Lifecycle answers "What is this runtime entity?"
    Execution answers "What is this task currently doing?"
    
    State Flow:
        INITIALIZING -> READY -> STARTING -> RUNNING -> STOPPING -> STOPPED
          |              |         |          |
          v              v         v          v
        FAILED         FAILED    FAILED     FAILED
    """
    
    INITIALIZING = "initializing"  # Being prepared
    READY = "ready"               # Ready for execution
    STARTING = "starting"         # About to begin execution
    RUNNING = "running"           # Currently executing
    STOPPING = "stopping"         # Stopping requested
    STOPPED = "stopped"           # Stopped completely
    FAILED = "failed"             # Failed during any phase


# ============================================================================
# PRIORITY LEVELS
# ============================================================================


class Priority(Enum):
    """
    Task execution priority levels.
    
    Lower numeric value = higher priority (runs first).
    These are metadata values; cognition decides which tasks get which priority.
    Scheduler obeys but doesn't invent priorities.
    """
    
    CRITICAL = 0    # Must run immediately
    HIGH = 1        # High importance, short delay acceptable
    NORMAL = 2      # Standard priority
    LOW = 3         # Can be delayed if needed


# ============================================================================
# TASK MODEL
# ============================================================================


@dataclass(frozen=True)
class TaskId:
    """Unique identifier for a task (wraps EntityId)."""
    
    value: EntityId
    
    @classmethod
    def generate(cls) -> "TaskId":
        """Generate a new unique task ID."""
        return cls(value=EntityId(str(uuid.uuid4())))
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, TaskId):
            return self.value == other.value
        if isinstance(other, EntityId):
            return self.value == other
        return False


@dataclass(frozen=True)
class ParentTaskRef:
    """
    Reference to a parent task in the hierarchy.
    
    Provides ownership information for propagation and cleanup.
    """
    
    task_id: TaskId
    owner_scope: str  # Scope identifier for resource cleanup


@dataclass(frozen=True)
class TaskDependencies:
    """
    Task dependency specifications.
    
    Tasks can depend on other tasks completing before they can run.
    """
    
    required_task_ids: Tuple[TaskId, ...] = field(default_factory=tuple)
    optional_task_ids: Tuple[TaskId, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RetryPolicy:
    """
    Retry policy for failed tasks.
    
    Explicit retry configuration - no automatic retries without this.
    
    Fields:
        max_attempts: Maximum number of attempts (including initial)
        initial_delay_seconds: Delay before first retry
        backoff_multiplier: Multiplier for exponential backoff
        max_delay_seconds: Maximum delay cap
    
    Backward-compatible aliases:
        backoff_seconds -> initial_delay_seconds
        max_backoff_seconds -> max_delay_seconds
    """
    
    max_attempts: int = 1
    initial_delay_seconds: float = 0.0
    backoff_multiplier: float = 1.0
    max_delay_seconds: float = 60.0
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        if attempt <= 0 or attempt >= self.max_attempts:
            return 0.0
        delay = self.initial_delay_seconds * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay_seconds)
    
    # Backward-compatible property aliases for existing code
    @property
    def backoff_seconds(self) -> float:
        """Backward compatible alias for initial_delay_seconds."""
        return self.initial_delay_seconds
    
    @property
    def max_backoff_seconds(self) -> float:
        """Backward compatible alias for max_delay_seconds."""
        return self.max_delay_seconds


@dataclass(frozen=True)
class ExecutionTimeouts:
    """
    Multiple timeout policies for different phases.
    
    Different timeouts for different purposes prevent one misconfigured
    timeout from affecting unrelated phases.
    """
    
    # Execution timeout - how long the task can run
    execution: Optional[float] = None
    
    # Queue timeout - max time in queue before scheduling (prevents starvation)
    queue: Optional[float] = None
    
    # Dependency wait timeout - max time waiting for dependencies
    dependency_wait: Optional[float] = None
    
    # Resource acquisition timeout - max time waiting for resources
    resource_acquire: Optional[float] = None


@dataclass(frozen=True)
class TaskCleanupHook:
    """
    Hook called during task cleanup.
    
    Provides deterministic cleanup in reverse ownership order.
    """
    
    name: str  # Description of what this hook cleans up
    cleanup_fn: Callable[[], Any]  # Function to call for cleanup
    is_critical: bool = False  # If True, failure stops the task result


@dataclass(frozen=True)
class TaskResult:
    """
    Result of a completed task.
    
    Provides structured evidence of what happened during execution.
    """
    
    # Timing information (must come first - no defaults)
    submitted_at: float
    
    # Identity
    task_id: TaskId
    status: ExecutionState
    
    # Value or error (exclusive - only one set)
    value: Any = None
    error: Optional[Exception] = None
    
    queued_at: Optional[float] = None
    scheduled_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Cancellation/timeout info
    cancelled: bool = False
    cancellation_reason: Optional[str] = None
    timed_out: bool = False
    
    # Retry information
    attempt_number: int = 1
    retry_delay_used: float = 0.0
    
    # Diagnostic data
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Return total execution duration if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def queue_wait_seconds(self) -> Optional[float]:
        """Return time spent in queue if queued."""
        if self.queued_at and self.scheduled_at:
            return self.scheduled_at - self.queued_at
        return None
    
    def is_success(self) -> bool:
        """Check if execution succeeded."""
        return self.status == ExecutionState.COMPLETED
    
    def is_failure(self) -> bool:
        """Check if execution failed (for any reason)."""
        return self.status in (
            ExecutionState.FAILED,
            ExecutionState.CANCELLED,
            ExecutionState.TIMED_OUT
        )


# ============================================================================
# EXECUTION REQUEST
# ============================================================================


@dataclass(frozen=True)
class TaskSpec(Generic[T]):
    """
    Specification for a task to be executed.
    
    This is the input to the scheduler - what work should be done.
    It's immutable and never mutated during processing.
    
    Usage:
        spec = TaskSpec(
            task_id=TaskId.generate(),
            task_fn=my_async_function,
            priority=Priority.NORMAL
        )
        
        # Submit to scheduler
        result = await scheduler.submit(spec)
    """
    
    # Identity (no defaults first)
    task_id: TaskId
    
    # The work to be done
    task_fn: Callable[..., Any]  # Sync or async callable (required, no default)
    
    # Optional fields with defaults
    parent_task_ref: Optional[ParentTaskRef] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    
    # Priority and scheduling
    priority: Priority = Priority.NORMAL
    
    # Dependencies
    dependencies: TaskDependencies = field(default_factory=TaskDependencies)
    
    # Timeouts
    timeouts: ExecutionTimeouts = field(default_factory=ExecutionTimeouts)
    
    # Retry configuration
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    
    # Cleanup hooks (called in reverse order during cleanup)
    cleanup_hooks: Tuple[TaskCleanupHook, ...] = field(default_factory=tuple)
    
    # Execution context metadata
    execution_scope: str = "default"
    trace_id: Optional[str] = None
    
    # Owner information
    owner: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate task spec structure."""
        if self.retry_policy.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        
        if self.priority == Priority.CRITICAL and not self.parent_task_ref:
            # Critical tasks without parent should be flagged
            pass  # Not an error, just informational


@dataclass(frozen=True)
class ExecutionRequest(Generic[T]):
    """
    Request to execute a unit of work (simpler form for backward compatibility).
    
    This is a simplified version of TaskSpec for backward compatibility.
    New code should use TaskSpec directly.
    """
    
    task: Callable[[], Any]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    timeout_seconds: Optional[float] = None
    priority: int = 0
    
    def to_task_spec(self, task_id: Optional[TaskId] = None) -> TaskSpec[T]:
        """Convert to a full TaskSpec."""
        return TaskSpec(
            task_id=task_id or TaskId.generate(),
            task_fn=self.task,
            args=self.args,
            kwargs=self.kwargs,
            priority=Priority(self.priority if self.priority < 4 else Priority.NORMAL),
            timeouts=ExecutionTimeouts(execution=self.timeout_seconds)
        )
    
    @classmethod
    def from_task_spec(cls, spec: TaskSpec[T]) -> "ExecutionRequest[T]":
        """Create ExecutionRequest from TaskSpec."""
        return cls(
            task=lambda: spec.task_fn(*spec.args, **spec.kwargs),
            timeout_seconds=spec.timeouts.execution,
            priority=int(spec.priority.value)
        )


# ============================================================================
# EXECUTION CONTEXT (TEMPORARY, TASK-SCOPED)
# ============================================================================


@dataclass
class ExecutionContext:
    """
    Temporary context for a single task execution.
    
    This is NOT the RuntimeContext. It exists only during task execution
    and is destroyed after completion/cancellation.
    
    Key principles:
        - Task-scoped (one per task)
        - Not process-global
        - Destroyed after execution completes
        - Contains temporary runtime data
    """
    
    # Identity (no defaults first)
    execution_id: ExecutionId
    
    # Task information (required fields before optional)
    task_id: TaskId
    
    # Optional fields with defaults
    parent_execution_id: Optional[ExecutionId] = None
    task_spec: Optional[TaskSpec] = None  # Available during scheduling
    
    cancellation_token: Optional["CancellationSource"] = None
    deadline_seconds: Optional[float] = None
    deadline_timestamp: Optional[float] = None
    
    execution_budget: Dict[str, Any] = field(default_factory=dict)
    
    trace_id: Optional[str] = None
    
    scheduler_handle: Optional[Any] = None
    
    resource_scope: Optional[Any] = None
    
    # Timing (last - with defaults)
    created_at: float = field(default_factory=time.monotonic)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if execution context has exceeded its deadline."""
        if self.deadline_timestamp is None:
            return False
        return time.monotonic() > self.deadline_timestamp
    
    def mark_started(self) -> None:
        """Mark the execution as started."""
        self.started_at = time.monotonic()
    
    def mark_completed(self) -> None:
        """Mark the execution as completed."""
        self.completed_at = time.monotonic()


# ============================================================================
# CANCELLATION SOURCE
# ============================================================================


class CancellationSource:
    """
    Source of cancellation requests with propagation support.
    
    Provides cooperative cancellation where tasks check for requests
    and stop themselves gracefully.
    
    Usage:
        # Create a source
        source = CancellationSource()
        
        # Get a token to pass to task execution context
        token = source.token
        
        # In task, periodically check:
        if token.is_requested:
            raise CancelledError("Task cancelled")
        
        # Request cancellation (e.g., from parent or timeout)
        source.request(reason="Timeout exceeded")
    """
    
    def __init__(self) -> None:
        import threading
        self._lock = threading.Lock()
        self._is_requested = False
        self._reason: Optional[str] = None
        self._timestamp: float = 0.0
        self._children: List["CancellationSource"] = []
        self._request_callbacks: List[Callable[[str], Any]] = []
    
    @property
    def is_requested(self) -> bool:
        """Check if cancellation has been requested."""
        with self._lock:
            return self._is_requested
    
    @property
    def reason(self) -> Optional[str]:
        """Get the cancellation reason."""
        with self._lock:
            return self._reason
    
    @property
    def timestamp(self) -> float:
        """Get when cancellation was requested."""
        with self._lock:
            return self._timestamp
    
    def token(self) -> "CancellationToken":
        """Get a cancellation token for passing to tasks."""
        return CancellationToken(self)
    
    def request(self, reason: Optional[str] = None) -> bool:
        """
        Request cancellation.
        
        Returns True if this was the first request (not idempotent).
        """
        with self._lock:
            if self._is_requested:
                return False
            
            self._is_requested = True
            self._reason = reason or "cancelled"
            self._timestamp = time.monotonic()
            
            # Notify callbacks
            for callback in list(self._request_callbacks):
                try:
                    callback(self._reason)
                except Exception:
                    pass  # Don't let callback failures stop propagation
            
            # Propagate to children (downward propagation)
            for child in list(self._children):
                child.request(f"Parent cancelled: {self._reason}")
        
        return True
    
    def register_callback(self, callback: Callable[[str], Any]) -> None:
        """Register a callback to be called when cancellation is requested."""
        with self._lock:
            if not self._is_requested:
                self._request_callbacks.append(callback)
    
    def create_child(self) -> "CancellationSource":
        """Create a child source that inherits parent state."""
        child = CancellationSource()
        with self._lock:
            self._children.append(child)
            
            # If parent is already cancelled, propagate immediately
            if self._is_requested:
                child.request(f"Inherited: {self._reason}")
        
        return child


class CancellationToken:
    """
    Read-only token for checking cancellation status.
    
    Passed to tasks so they can check for cancellation requests.
    Tasks cannot request cancellation themselves (that requires source).
    """
    
    def __init__(self, source: CancellationSource) -> None:
        self._source = source
    
    @property
    def is_requested(self) -> bool:
        """Check if cancellation has been requested."""
        return self._source.is_requested
    
    @property
    def reason(self) -> Optional[str]:
        """Get the cancellation reason."""
        return self._source.reason
    
    def check(self) -> None:
        """Raise an exception if cancellation is requested."""
        if self.is_requested:
            from ..exceptions import TaskCancelledError
            raise TaskCancelledError(
                f"Task cancelled: {self.reason}",
                source=self._source
            )


# ============================================================================
# EXCEPTIONS
# ============================================================================


class TaskError(Exception):
    """Base exception for task-related errors."""
    
    def __init__(self, message: str, task_id: Optional[TaskId] = None):
        self.task_id = task_id
        super().__init__(message)


class TaskCancelledError(TaskError):
    """Raised when a task is cancelled."""
    
    def __init__(
        self,
        message: str,
        task_id: Optional[TaskId] = None,
        source: Optional[CancellationSource] = None
    ):
        self.source = source
        super().__init__(message, task_id)


class TaskTimeoutError(TaskError):
    """Raised when a task exceeds its execution timeout."""
    
    def __init__(
        self,
        message: str,
        task_id: Optional[TaskId] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.timeout_seconds = timeout_seconds
        super().__init__(message, task_id)


class DependencyError(TaskError):
    """Raised when a dependency fails or is cancelled."""
    
    def __init__(
        self,
        message: str,
        task_id: Optional[TaskId] = None,
        dependency_task_ids: Tuple[TaskId, ...] = tuple()
    ):
        self.dependency_task_ids = dependency_task_ids
        super().__init__(message, task_id)


class SchedulerError(Exception):
    """Raised when scheduler operations fail."""
    
    pass


# ============================================================================
# CLEANUP COORDINATOR
# ============================================================================


class CleanupCoordinator:
    """
    Coordinates cleanup in deterministic reverse ownership order.
    
    Ensures that resources are released in the correct order and that
    cleanup failures don't overwrite task execution results.
    """
    
    def __init__(self) -> None:
        self._hooks: List[TaskCleanupHook] = []
        self._results: Dict[str, Tuple[bool, Optional[str]]] = {}
    
    def register_hook(self, hook: TaskCleanupHook) -> None:
        """Register a cleanup hook (hooks are called in reverse order)."""
        self._hooks.append(hook)
    
    async def execute_cleanup(self) -> Dict[str, Any]:
        """
        Execute all cleanup hooks in reverse ownership order.
        
        Returns results mapping hook name to (success, error_message).
        Cleanup failures don't overwrite task results.
        """
        results: Dict[str, Tuple[bool, Optional[str]]] = {}
        
        for hook in reversed(self._hooks):
            try:
                hook.cleanup_fn()
                results[hook.name] = (True, None)
            except Exception as e:
                results[hook.name] = (False, str(e))
                
                # Critical hooks fail the overall cleanup
                if hook.is_critical:
                    results["_critical_failure"] = (
                        False,
                        f"Critical cleanup failed: {hook.name}"
                    )
        
        self._results = results
        return {
            "cleanup_order": list(reversed([h.name for h in self._hooks])),
            "results": dict(results),
            "success": all(r[0] for r in results.values())
        }
    
    def get_result(self, hook_name: str) -> Optional[Tuple[bool, Optional[str]]]:
        """Get the result of a specific cleanup hook."""
        return self._results.get(hook_name)
    
    def was_successful(self) -> bool:
        """Check if all non-critical cleanup completed successfully."""
        return self._results.get("_success", True)


# ============================================================================
# OBSERVABILITY EVENTS
# ============================================================================


class TaskEvent(Enum):
    """Types of task execution events for observability."""
    
    TASK_SUBMITTED = "task_submitted"
    TASK_QUEUED = "task_queued"
    TASK_DEP_WAIT = "task_dep_wait"
    TASK_READY = "task_ready"
    TASK_SCHEDULED = "task_scheduled"
    TASK_STARTED = "task_started"
    TASK_CANCELLED = "task_cancelled"
    TASK_FAILED = "task_failed"
    TASK_COMPLETED = "task_completed"
    CLEANUP_STARTED = "cleanup_started"
    CLEANUP_COMPLETED = "cleanup_completed"


@dataclass(frozen=True)
class TaskEventRecord:
    """
    Structured execution event record.
    
    Provides observability without implementing a telemetry backend.
    Event consumers can forward these to logging, tracing systems, etc.
    """
    
    event_type: TaskEvent
    timestamp: float
    task_id: TaskId
    execution_id: Optional[ExecutionId] = None
    
    # Contextual data
    priority: Optional[int] = None
    state_before: Optional[str] = None
    state_after: Optional[str] = None
    reason: Optional[str] = None
    
    # Timing information (where applicable)
    queue_wait_seconds: Optional[float] = None
    execution_duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event record to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "task_id": str(self.task_id),
            "execution_id": str(self.execution_id) if self.execution_id else None,
            "priority": self.priority,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "reason": self.reason,
            "queue_wait_seconds": self.queue_wait_seconds,
            "execution_duration_seconds": self.execution_duration_seconds
        }


# ============================================================================
# SUBMODULES EXPORT
# ============================================================================

from .scheduler import (
    Scheduler,
    SchedulerConfig,
    SchedulerState,
    ReadyQueue,
    WaitingQueue,
    RetryQueue,
    PriorityInheritanceInfo,
    RunningTaskInfo,
    TaskHandle,
    
    # Queue capacity exceptions (Phase 3.7.18-R)
    ReadyQueueFull,
    WaitingQueueFull,
    RetryQueueFull,
)

# Re-export lifecycle state machines from core.lifecycle
from ..lifecycle import (
    ThreadLifecycleState as ThreadLifecycleState,
    CycleState as CycleState,
    StateTransition as StateTransition,
    ThreadLifecycleTransitionGraph as ThreadLifecycleTransitionGraph,
    CycleTransitionGraph as CycleTransitionGraph,
    LifecycleTransitionRequest as LifecycleTransitionRequest,
    LifecycleTransitionResult as LifecycleTransitionResult,
    ThreadLifecycleSnapshot as ThreadLifecycleSnapshot,
    CycleLifecycleSnapshot as CycleLifecycleSnapshot,
)

__all__ = [
    # Execution states
    "ExecutionState",
    "TaskState",
    
    # Priority levels
    "Priority",
    
    # Task model
    "TaskId",
    "ParentTaskRef",
    "TaskDependencies",
    "RetryPolicy",
    "ExecutionTimeouts",
    "TaskCleanupHook",
    "TaskResult",
    
    # Execution request
    "TaskSpec",
    "ExecutionRequest",
    
    # Execution context (temporary, task-scoped)
    "ExecutionContext",
    
    # Cancellation
    "CancellationSource",
    "CancellationToken",
    "TaskCancelledError",
    
    # Timeouts and errors
    "TaskTimeoutError",
    "DependencyError",
    "SchedulerError",
    
    # Queue capacity exceptions (Phase 3.7.18-R)
    "ReadyQueueFull",
    "WaitingQueueFull",
    "RetryQueueFull",
    
    # Cleanup
    "CleanupCoordinator",
    
    # Observability
    "TaskEvent",
    "TaskEventRecord",
    
    # Scheduler (imported from submodules)
    "Scheduler",
    "SchedulerConfig",
    "SchedulerState",
    "ReadyQueue",
    "WaitingQueue",
    "RetryQueue",
    "PriorityInheritanceInfo",
    "RunningTaskInfo",
    "TaskHandle",
]
