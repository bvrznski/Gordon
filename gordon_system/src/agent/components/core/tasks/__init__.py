# Import from canonical core location instead of execution layer
# Note: TaskPriority, TaskId, and TaskState are defined in this module (core.tasks)
# RetryPolicy is now imported from core.execution which is the canonical source
# Core Task Models and Lifecycle Control
# ======================================

"""
Core task model and lifecycle controller for Phase 3.7.7-I.

Provides:
- Canonical immutable task artifact (Task, TaskId, TaskState)
- Single authority for task state transitions (TaskLifecycleController)
- Deterministic task lifecycle state machine
- Explicit task ownership tracking
- Terminal state enforcement

Architecture:
    Task - Immutable canonical task artifact
        ↓
    TaskLifecycleController - State transition authority
        ↓
    TaskResult - Execution outcome evidence
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, FrozenSet
from enum import Enum, auto
import uuid
import time


# =============================================================================
# TASK IDENTITY
# =============================================================================

@dataclass(frozen=True)
class TaskId:
    """
    Unique identifier for a task.
    
    This is the canonical identity - all references to this task must use
    this exact instance or an equal value.
    """
    value: str
    
    @classmethod
    def generate(cls) -> "TaskId":
        """Generate a new unique task ID."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# TASK STATE MACHINE
# =============================================================================

class TaskState(Enum):
    """
    Canonical task lifecycle states.
    
    State Flow (canonical path):
        CREATED → SUBMITTED → ADMITTED → QUEUED → BLOCKED/ELIGIBLE → 
        SELECTED → DISPATCHING → DISPATCHED → EXECUTING → [TERMINAL]
        
    Terminal States (immutable):
        COMPLETED, FAILED, CANCELLED, TIMED_OUT, RETIRED
        
    Non-Terminal States (can transition to other states):
        CREATED, SUBMITTED, ADMITTED, QUEUED, BLOCKED, ELIGIBLE,
        SELECTED, DISPATCHING, DISPATCHED, EXECUTING
    """
    
    # Initial states
    CREATED = "created"           # Task artifact exists
    SUBMITTED = "submitted"       # Submitted to runtime
    ADMITTED = "admitted"         # Passed admission gates
    
    # Scheduling states
    QUEUED = "queued"             # In queue, waiting for scheduling
    BLOCKED = "blocked"           # Blocked on dependencies/resource
    ELIGIBLE = "eligible"         # Ready for scheduling consideration
    
    # Execution states
    SELECTED = "selected"         # Selected by scheduler
    DISPATCHING = "dispatching"   # Preparing dispatch to executor
    DISPATCHED = "dispatched"     # Dispatched to executor
    EXECUTING = "executing"       # Currently executing
    
    # Terminal states (immutable - no outgoing transitions)
    COMPLETED = "completed"       # Execution succeeded
    FAILED = "failed"             # Execution failed
    CANCELLED = "cancelled"       # Cancelled before/during execution
    TIMED_OUT = "timed_out"       # Execution exceeded timeout
    RETIRED = "retired"           # Removed from active structures


# Valid transitions: source_state -> set of allowed target states
VALID_TASK_TRANSITIONS: Dict[TaskState, FrozenSet[TaskState]] = {
    TaskState.CREATED: frozenset({TaskState.SUBMITTED}),
    TaskState.SUBMITTED: frozenset({TaskState.ADMITTED, TaskState.FAILED}),
    TaskState.ADMITTED: frozenset({TaskState.QUEUED, TaskState.BLOCKED}),
    TaskState.QUEUED: frozenset({
        TaskState.BLOCKED, TaskState.ELIGIBLE, 
        TaskState.SELECTED, TaskState.CANCELLED
    }),
    TaskState.BLOCKED: frozenset({
        TaskState.QUEUED, TaskState.ELIGIBLE,
        TaskState.CANCELLED
    }),
    TaskState.ELIGIBLE: frozenset({
        TaskState.QUEUED, TaskState.SELECTED, 
        TaskState.CANCELLED
    }),
    TaskState.SELECTED: frozenset({
        TaskState.DISPATCHING, TaskState.QUEUED,
        TaskState.BLOCKED, TaskState.CANCELLED
    }),
    TaskState.DISPATCHING: frozenset({
        TaskState.DISPATCHED, TaskState.ELIGIBLE,
        TaskState.FAILED
    }),
    TaskState.DISPATCHED: frozenset({TaskState.EXECUTING}),
    TaskState.EXECUTING: frozenset({
        TaskState.COMPLETED, TaskState.FAILED,
        TaskState.CANCELLED, TaskState.TIMED_OUT
    }),
    # Terminal states have no valid transitions
    TaskState.COMPLETED: frozenset(),
    TaskState.FAILED: frozenset(),
    TaskState.CANCELLED: frozenset(),
    TaskState.TIMED_OUT: frozenset(),
    TaskState.RETIRED: frozenset(),
}


class TaskTransitionError(Exception):
    """Raised when an invalid task state transition is attempted."""
    
    def __init__(
        self,
        from_state: TaskState,
        to_state: TaskState,
        reason: str = ""
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        super().__init__(f"Invalid transition {from_state.value} → {to_state.value}: {reason}")


# =============================================================================
# TASK PRIORITY
# =============================================================================

class TaskPriority(Enum):
    """
    Task priority levels.
    
    Lower numeric value = higher priority (runs first).
    These are metadata values - scheduler obeys but doesn't invent priorities.
    """
    EMERGENCY = 0      # Must run immediately, bypass normal constraints
    CONTROL = 1        # Control plane operations
    RECOVERY = 2       # Recovery operations
    CRITICAL = 3       # High importance, short delay acceptable
    INTERACTIVE = 4    # User-facing operations
    STANDARD = 5       # Default priority
    BACKGROUND = 6     # Low-priority background work
    MAINTENANCE = 7    # Maintenance tasks
    BEST_EFFORT = 8    # No guarantees


# =============================================================================
# TASK DEPENDENCY
# =============================================================================

class TaskDependencyKind(Enum):
    """Type of dependency relationship."""
    HARD = "hard"      # Must complete before dependent task runs
    SOFT = "soft"      # Preferred but not required


@dataclass(frozen=True)
class TaskDependency:
    """
    A dependency requirement for a task.
    
    Tasks may depend on other tasks completing before they can run.
    """
    depended_task_id: TaskId       # The task we depend on
    kind: TaskDependencyKind = TaskDependencyKind.HARD
    
    def __hash__(self) -> int:
        return hash(self.depended_task_id)


# =============================================================================
# RESOURCE REQUIREMENTS
# =============================================================================

@dataclass(frozen=True)
class ResourceRequirements:
    """
    Resource requirements for task execution.
    
    These are constraints that must be satisfied before execution begins.
    """
    cpu_slots: int = 1              # Number of CPU cores/threads needed
    memory_mb: int = 256            # Memory in megabytes
    gpu_count: int = 0              # Number of GPUs required
    vram_mb: int = 0                # GPU VRAM in MB (if GPU required)
    execution_slots: int = 1        # Concurrent execution slots needed


from ..execution import RetryPolicy


# =============================================================================
# CANCELLATION POLICY
# =============================================================================

class CancellationPolicy(Enum):
    """How cancellation is handled for a task."""
    IMMEDIATE = "immediate"           # Stop immediately on cancellation request
    COOPERATIVE = "cooperative"       # Check token periodically
    DEFERRED = "deferred"             # Complete current operation before stopping


# =============================================================================
# TASK ARTIFACT (CANONICAL, DEEPLY IMMUTABLE)
# =============================================================================

@dataclass(frozen=True)
class Task:
    """
    Immutable canonical task artifact.
    
    This is THE source of truth for task identity and metadata. All
    execution and lifecycle operations reference tasks by this immutable
    artifact or its TaskId.
    
    Immutability guarantees:
        - All fields are frozen (cannot be modified after creation)
        - Nested objects are also immutable
        - No runtime object references in public state
        - Stable identity via generated task_id
        
    Usage:
        # Create a new task
        task = Task(
            task_id=TaskId.generate(),
            operation_id="op_123",
            payload_reference="payload://...",
            priority=TaskPriority.STANDARD,
            dependencies=(TaskDependency(other_task_id),),
        )
        
        # All state transitions go through TaskLifecycleController
    """
    
    # Identity (no defaults - must come first)
    task_id: TaskId                    # Canonical unique identifier
    
    # Runtime identity (runtime-scoped isolation)
    runtime_id: str                    # Which runtime instance owns this task
    
    # Operation context
    operation_id: str                  # What operation is being performed
    correlation_id: Optional[str] = None   # User/request correlation ID
    causation_id: Optional[str] = None     # Root cause task ID (for chaining)
    
    # Task classification
    task_kind: str = "normal"          # e.g., "normal", "control", "recovery"
    
    # Work to be done
    payload_reference: str             # Reference to payload (not inline data!)
    
    # Scheduling metadata
    priority: TaskPriority = TaskPriority.STANDARD
    deadline_utc: Optional[float] = None  # Absolute deadline (Unix timestamp)
    
    # Dependencies
    dependencies: Tuple[TaskDependency, ...] = field(default_factory=tuple)
    
    # Resource requirements
    resource_requirements: ResourceRequirements = field(
        default_factory=ResourceRequirements
    )
    
    # Ownership and provenance
    owner_id: str = ""                 # Who submitted this task
    origin: str = "unknown"            # e.g., "api", "scheduler", "trigger"
    submitted_at: float = field(default_factory=time.time)
    
    # Execution configuration
    idempotency_key: Optional[str] = None  # For deduplication
    retry_policy: "RetryPolicy" = field(default_factory=lambda: RetryPolicy(max_attempts=1))
    cancellation_policy: CancellationPolicy = CancellationPolicy.COOPERATIVE
    
    # Metadata (bounded size, no runtime references)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    # Provenance tracking
    provenance: Tuple[str, ...] = field(default_factory=tuple)  # Chain of custody
    
    def __post_init__(self) -> None:
        """Validate task artifact structure."""
        if not self.task_id.value:
            raise ValueError("TaskId cannot be empty")
        
        if not self.runtime_id:
            raise ValueError("Runtime ID is required")
        
        if self.payload_reference.startswith("payload://"):
            # Would validate payload reference format in production
            pass
    
    @property
    def is_terminal(self) -> bool:
        """Check if this task is in a terminal state."""
        return False  # Task artifact itself has no state - lifecycle has state
    
    def with_priority(self, priority: TaskPriority) -> "Task":
        """Return a new Task with updated priority (immutable update)."""
        return dataclass_replace(self, priority=priority)
    
    def with_metadata(self, key: str, value: str) -> "Task":
        """Return a new Task with added/updated metadata."""
        new_metadata = dict(self.metadata)
        new_metadata[key] = value
        return dataclass_replace(self, metadata=new_metadata)


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# TASK LIFECYCLE CONTROLLER (CANONICAL AUTHORITY)
# =============================================================================

class TaskLifecycleController:
    """
    Canonical authority for task state transitions.
    
    This is THE ONE source of truth for what state each task is in.
    All task state mutations MUST go through this controller.
    
    Invariants enforced:
        1. Only one canonical task state exists
        2. State transitions must be valid (per VALID_TASK_TRANSITIONS)
        3. Terminal states are immutable (no outgoing transitions)
        4. No direct state assignment - all transitions go through here
        5. History preserves provenance for each transition
    
    Usage:
        controller = TaskLifecycleController()
        
        # Submit a task artifact
        task = Task(task_id=TaskId.generate(), ...)
        controller.register_task(task)
        
        # Transition states (must be valid!)
        controller.transition(task.task_id, TaskState.SUBMITTED, "user submitted")
        controller.transition(task.task_id, TaskState.ADMITTED, "admission passed")
    """
    
    def __init__(self) -> None:
        """Initialize the lifecycle controller."""
        self._lock = __import__("threading").RLock()
        
        # State storage: task_id -> (current_state, timestamp)
        self._task_states: Dict[TaskId, Tuple[TaskState, float]] = {}
        
        # History: list of (task_id, from_state, to_state, reason, timestamp)
        self._transition_history: List[
            Tuple[TaskId, TaskState, TaskState, str, float]
        ] = []
        
        # Terminal state tracking
        self._terminal_tasks: set = set()
    
    def register_task(self, task: Task) -> None:
        """
        Register a new task artifact with initial CREATED state.
        
        Args:
            task: The immutable task artifact to track
            
        Raises:
            ValueError: If task already registered or has invalid state
        """
        with self._lock:
            if task.task_id in self._task_states:
                raise ValueError(f"Task {task.task_id} already registered")
            
            # Start in CREATED state
            now = time.monotonic()
            self._task_states[task.task_id] = (TaskState.CREATED, now)
    
    def transition(
        self,
        task_id: TaskId,
        target_state: TaskState,
        reason: str = "",
        timestamp: Optional[float] = None
    ) -> Tuple[bool, TaskTransitionError]:
        """
        Request a state transition for a task.
        
        Args:
            task_id: The task to transition
            target_state: The desired target state
            reason: Human-readable explanation (for audit)
            timestamp: Optional monotonic timestamp (defaults to now)
            
        Returns:
            Tuple of (success, error_or_None)
            
        Raises:
            TaskTransitionError: If transition is invalid
        """
        with self._lock:
            if task_id not in self._task_states:
                return False, TaskTransitionError(
                    TaskState.CREATED, target_state,
                    f"Task {task_id} not registered"
                )
            
            current_state, _ = self._task_states[task_id]
            
            # Idempotent: same state is always valid
            if current_state == target_state:
                return True, None
            
            # Check if target is terminal (terminal states have no outgoing)
            valid_transitions = VALID_TASK_TRANSITIONS.get(current_state, frozenset())
            
            if target_state not in valid_transitions:
                error = TaskTransitionError(
                    current_state, target_state,
                    f"Invalid transition. Valid: {[s.value for s in valid_transitions]}"
                )
                return False, error
            
            # Update state
            ts = timestamp or time.monotonic()
            self._task_states[task_id] = (target_state, ts)
            
            # Record history
            self._transition_history.append((
                task_id, current_state, target_state, reason, ts
            ))
            
            # Track terminal states
            if target_state in (
                TaskState.COMPLETED, TaskState.FAILED,
                TaskState.CANCELLED, TaskState.TIMED_OUT, TaskState.RETIRED
            ):
                self._terminal_tasks.add(task_id)
            
            return True, None
    
    def get_state(self, task_id: TaskId) -> Optional[TaskState]:
        """
        Get current state of a task.
        
        Args:
            task_id: The task to query
            
        Returns:
            Current state, or None if not registered
        """
        with self._lock:
            state_tuple = self._task_states.get(task_id)
            return state_tuple[0] if state_tuple else None
    
    def is_terminal(self, task_id: TaskId) -> bool:
        """Check if a task is in a terminal state."""
        with self._lock:
            return task_id in self._terminal_tasks
    
    def get_history(
        self,
        task_id: Optional[TaskId] = None
    ) -> List[Tuple[TaskId, TaskState, TaskState, str, float]]:
        """
        Get transition history.
        
        Args:
            task_id: If provided, only return history for this task
            
        Returns:
            List of (task_id, from_state, to_state, reason, timestamp) tuples
        """
        with self._lock:
            if task_id is None:
                return list(self._transition_history)
            
            return [
                h for h in self._transition_history
                if h[0] == task_id
            ]
    
    def get_snapshot(self) -> "TaskLifecycleSnapshot":
        """Get an immutable snapshot of current state."""
        with self._lock:
            return TaskLifecycleSnapshot(
                states=dict(self._task_states),
                terminal_count=len(self._terminal_tasks),
                history_length=len(self._transition_history)
            )


@dataclass(frozen=True)
class TaskLifecycleSnapshot:
    """
    Immutable snapshot of task lifecycle state.
    
    Used for observability and diagnostics without exposing mutable state.
    """
    states: Dict[TaskId, Tuple[TaskState, float]]
    terminal_count: int
    history_length: int


# =============================================================================
# TASK RESULT (EXECUTION OUTCOME EVIDENCE)
# =============================================================================

class TaskCompletionStatus(Enum):
    """How task execution completed."""
    SUCCESS = "success"           # Completed successfully
    FAILURE = "failure"           # Failed with error
    CANCELLED = "cancelled"       # Cancelled before completion
    TIMED_OUT = "timed_out"       # Exceeded timeout


@dataclass(frozen=True)
class TaskResult:
    """
    Immutable evidence of task execution outcome.
    
    This is produced after execution completes - it's the proof of what
    happened, not a request for action.
    """
    # Identity (no defaults first)
    task_id: TaskId
    runtime_id: str
    
    # Execution outcome
    status: TaskCompletionStatus
    
    # Timing
    submitted_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Value or error (exclusive - only one set)
    value: Any = None              # Success result (if any)
    error: Optional[Exception] = None  # Failure exception (if any)
    
    # Cancellation/timeout info
    cancelled: bool = False
    cancellation_reason: Optional[str] = None
    timed_out: bool = False
    
    # Retry information
    attempt_number: int = 1
    retry_delay_used: float = 0.0
    
    # Diagnostics
    diagnostics: Dict[str, str] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def queue_wait_seconds(self) -> Optional[float]:
        """Calculate time spent in queue (queued to started)."""
        # Would need queued_at field for accurate calculation
        return None
    
    def is_success(self) -> bool:
        """Check if execution succeeded."""
        return self.status == TaskCompletionStatus.SUCCESS
    
    def is_failure(self) -> bool:
        """Check if execution failed (for any reason)."""
        return self.status in (
            TaskCompletionStatus.FAILURE,
            TaskCompletionStatus.CANCELLED,
            TaskCompletionStatus.TIMED_OUT
        )


# =============================================================================
# TASK SUBMISSION REQUEST/RESULT
# =============================================================================

@dataclass(frozen=True)
class TaskSubmissionRequest:
    """
    Request to submit a new task.
    
    This is the INPUT contract - everything needed to create and admit a task.
    """
    runtime_id: str                    # Which runtime
    task_spec: Any                     # Task specification (payload reference, etc.)
    owner_id: str                      # Who is submitting
    priority: TaskPriority = TaskPriority.STANDARD
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


@dataclass(frozen=True)
class TaskSubmissionResult:
    """
    Result of a task submission attempt.
    
    This is the OUTPUT - typed, complete, and immutable.
    """
    success: bool
    runtime_id: str
    
    # Task info (if successful)
    task_id: Optional[TaskId] = None
    state: Optional[TaskState] = None
    
    # Admission info (if failed)
    rejection_reason: Optional[str] = None
    admission_decision: Optional[Any] = None  # From AdmissionDecisionRecord
    
    # Timing
    submitted_at: float = field(default_factory=time.time)
    
    def is_success(self) -> bool:
        """Check if submission succeeded."""
        return self.success


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Task identity
    "TaskId",
    
    # State machine
    "TaskState",
    "VALID_TASK_TRANSITIONS",
    "TaskTransitionError",
    
    # Scheduling metadata
    "TaskPriority",
    
    # Dependencies
    "TaskDependencyKind",
    "TaskDependency",
    
    # Resources
    "ResourceRequirements",
    
    "CancellationPolicy",
    
    # Core types
    "Task",
    "dataclass_replace",
    
    # Lifecycle authority
    "TaskLifecycleController",
    "TaskLifecycleSnapshot",
    
    # Results
    "TaskCompletionStatus",
    "TaskResult",
    
    # Submission
    "TaskSubmissionRequest",
    "TaskSubmissionResult",
]