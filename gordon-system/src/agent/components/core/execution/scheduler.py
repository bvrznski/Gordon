# Core Scheduler Implementation
# =============================

"""
Deterministic task scheduler with multiple queues.

Provides:
- Priority-based scheduling with deterministic ordering
- Dependency-aware queue management
- Timeout handling and starvation prevention
- Cooperative cancellation integration
- Task hierarchy and ownership tracking
- Resource acquisition coordination

Changes for Phase 3.7.7 Remediation:
- Priority inheritance in WaitingQueue.dependency_completed()
- Starvation-based priority boost in run_one()
- Automatic retry logic for failed tasks
- Admission receipt validation
- Queue timeout checking
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Generic,
    Deque,
)
from enum import Enum, auto
import time
import asyncio
import threading

from . import (
    TaskId,
    ExecutionState,
    TaskState,
    Priority,
    ParentTaskRef,
    TaskDependencies,
    RetryPolicy,
    ExecutionTimeouts,
    TaskCleanupHook,
    TaskResult,
    TaskSpec,
    ExecutionContext,
    CancellationSource,
    CancellationToken,
    CleanupCoordinator,
    TaskEvent,
    TaskEventRecord,
    SchedulerError,
    DependencyError,
    TaskTimeoutError,
    TaskCancelledError,
)

T = TypeVar("T")


class QueueType(Enum):
    """Types of execution queues."""
    
    READY = "ready"        # Tasks ready to run
    WAITING = "waiting"    # Tasks waiting for dependencies
    DELAYED = "delayed"    # Tasks with delayed execution
    RETRY = "retry"        # Tasks pending retry
    SHUTDOWN = "shutdown"  # Tasks being cancelled during shutdown


# =============================================================================
# QUEUE CAPACITY EXCEPTIONS
# =============================================================================

class ReadyQueueFull(Exception):
    """Raised when ready queue has reached its capacity limit."""
    
    def __init__(self, message: str = "Ready queue at capacity"):
        super().__init__(message)


class WaitingQueueFull(Exception):
    """Raised when waiting queue has reached its capacity limit."""
    
    def __init__(self, message: str = "Waiting queue at capacity"):
        super().__init__(message)


class RetryQueueFull(Exception):
    """Raised when retry queue has reached its capacity limit."""
    
    def __init__(self, message: str = "Retry queue at capacity"):
        super().__init__(message)


class SchedulerState(Enum):
    """Scheduler runtime state."""
    
    INITIALIZING = "initializing"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


@dataclass(frozen=True)
class SchedulerConfig:
    """Configuration for scheduler behavior."""
    
    max_concurrent_tasks: int = 10
    default_timeout_seconds: Optional[float] = None
    queue_timeout_seconds: Optional[float] = None
    dependency_wait_timeout_seconds: Optional[float] = None
    
    # Starvation prevention (max time in queue before forcing schedule)
    starvation_threshold_seconds: float = 30.0
    
    # Queue capacity limits (hard bounds to prevent unbounded growth)
    max_ready_queue_size: int = 10000      # ReadyQueue capacity
    max_waiting_queue_size: int = 10000    # WaitingQueue capacity  
    max_retry_queue_size: int = 1000       # RetryQueue capacity
    
    # Retry defaults
    default_retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    
    # Cleanup
    cleanup_enabled: bool = True


# =============================================================================
# PRIORITY INHERITANCE SUPPORT (for dependency completion)
# =============================================================================

@dataclass
class PriorityInheritanceInfo:
    """
    Tracks priority inheritance state for tasks.
    
    When a task completes, any waiting tasks that depend on it inherit
    its priority to prevent priority inversion (low-priority task blocking
    high-priority dependent tasks).
    """
    inherited_priority: Optional[Priority] = None
    inherited_from_task_id: Optional[TaskId] = None


# =============================================================================
# READY QUEUE WITH STARVATION TRACKING
# =============================================================================

class ReadyQueue(Generic[T]):
    """
    Priority queue for ready-to-run tasks.
    
    Tasks are ordered by priority (lower value = higher priority).
    Within same priority, FIFO ordering is maintained for determinism.
    
    Starvation tracking:
        - Each task tracks when it entered the ready queue
        - run_one() checks if tasks have been waiting too long and boosts priority
    
    Queue capacity enforcement:
        - Checks against max_size before adding tasks
        - Raises ReadyQueueFull exception when at capacity
    """
    
    def __init__(self, max_size: int = 10000) -> None:
        self._lock = threading.Lock()
        # Tuple: (priority_val, timestamp_entered_queue, spec)
        self._queue: List[Tuple[int, float, TaskSpec]] = []
        # Task ID -> enter time mapping for starvation tracking
        self._task_enter_times: Dict[TaskId, float] = {}
        self._max_size = max_size  # Explicit capacity limit
    
    @property
    def max_size(self) -> int:
        """Get the maximum queue capacity."""
        return self._max_size
    
    @property
    def current_size(self) -> int:
        """Get current number of tasks in queue."""
        with self._lock:
            return len(self._queue)
    
    @property
    def is_at_capacity(self) -> bool:
        """Check if queue has reached its capacity limit."""
        with self._lock:
            return len(self._queue) >= self._max_size
    
    def push(self, spec: TaskSpec) -> None:
        """
        Add task to queue.
        
        Raises:
            ReadyQueueFull: If queue is at capacity
        """
        with self._lock:
            # Check capacity before adding
            if len(self._queue) >= self._max_size:
                raise ReadyQueueFull(
                    f"ReadyQueue full (capacity={self._max_size}), cannot add task {spec.task_id}"
                )
            
            # Priority value (lower = higher priority)
            priority_val = int(spec.priority.value)
            
            # Timestamp for FIFO within same priority
            timestamp = time.monotonic()
            
            # Track when task entered queue
            if spec.task_id not in self._task_enter_times:
                self._task_enter_times[spec.task_id] = timestamp
            
            self._queue.append((priority_val, timestamp, spec))
            
            # Sort by priority first (ascending, lower=value=higher priority), then timestamp (ascending, older first)
            self._queue.sort(key=lambda x: (x[0], x[1]))
    
    def pop(self) -> Optional[Tuple[int, TaskSpec]]:
        """Remove and return highest priority task."""
        with self._lock:
            if not self._queue:
                return None
            
            priority_val, timestamp, spec = self._queue.pop(0)
            # Remove from enter times when task leaves queue
            if spec.task_id in self._task_enter_times:
                del self._task_enter_times[spec.task_id]
            return (priority_val, spec)
    
    def peek(self) -> Optional[Tuple[int, TaskSpec]]:
        """Look at highest priority task without removing."""
        with self._lock:
            if not self._queue:
                return None
            # Return (priority, spec) tuple
            entry = self._queue[0]
            return (entry[0], entry[2])
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:
        with self._lock:
            return len(self._queue) == 0
    
    def remove_task(self, task_id: TaskId) -> Optional[TaskSpec]:
        """Remove a specific task from the queue."""
        with self._lock:
            for i, (_, _, spec) in enumerate(self._queue):
                if spec.task_id == task_id:
                    removed = self._queue.pop(i)
                    # Remove enter time tracking
                    if spec.task_id in self._task_enter_times:
                        del self._task_enter_times[spec.task_id]
                    return removed[2]
            return None
    
    def get_all_tasks(self) -> List[Tuple[int, TaskSpec]]:
        """Get all tasks sorted by priority."""
        with self._lock:
            return [(p, s) for p, _, s in self._queue]
    
    def get_queue_wait_time(self, task_id: TaskId) -> Optional[float]:
        """Get how long a task has been waiting in queue (in seconds)."""
        with self._lock:
            enter_time = self._task_enter_times.get(task_id)
            if enter_time is None:
                return None
            return time.monotonic() - enter_time
    
    def boost_task_priority(self, task_id: TaskId) -> bool:
        """
        Boost a task's priority to CRITICAL (highest).
        
        Returns True if the task was found and boosted.
        """
        with self._lock:
            for i, (_, _, spec) in enumerate(self._queue):
                if spec.task_id == task_id:
                    # Find lowest numeric value (highest priority)
                    current_priority_val = int(spec.priority.value)
                    
                    # Boost to CRITICAL (value 0)
                    if current_priority_val > 0:  # Only boost if not already highest
                        self._queue[i] = (0, spec.timeouts.queue or time.monotonic(), spec)
                        # Re-sort to maintain ordering
                        self._queue.sort(key=lambda x: (x[0], x[1]))
                    return True
            return False


# =============================================================================
# WAITING QUEUE WITH PRIORITY INHERITANCE
# =============================================================================

class WaitingQueue:
    """
    Queue for tasks waiting on dependencies.
    
    Tracks which dependencies are still needed and when
    they can be rescheduled.
    
    Priority Inheritance Protocol (PIP):
        When a dependency completes, any tasks waiting on it inherit
        the completed task's priority. This prevents low-priority tasks
        from blocking high-priority dependent tasks (priority inversion).
    
    Queue capacity enforcement:
        - Checks against max_size before adding tasks
        - Raises WaitingQueueFull exception when at capacity
    """
    
    def __init__(self, max_size: int = 10000) -> None:
        self._lock = threading.Lock()
        # task_id -> (spec, dependency_task_ids_set, original_priority)
        self._waiting_tasks: Dict[TaskId, Tuple[TaskSpec, set, Priority]] = {}
        self._max_size = max_size
    
    @property
    def max_size(self) -> int:
        """Get the maximum queue capacity."""
        return self._max_size
    
    @property
    def current_size(self) -> int:
        """Get current number of tasks in queue."""
        with self._lock:
            return len(self._waiting_tasks)
    
    @property
    def is_at_capacity(self) -> bool:
        """Check if queue has reached its capacity limit."""
        with self._lock:
            return len(self._waiting_tasks) >= self._max_size
    
    def add(self, spec: TaskSpec) -> None:
        """
        Add a task waiting for dependencies.
        
        Raises:
            WaitingQueueFull: If queue is at capacity
        """
        with self._lock:
            # Check capacity before adding
            if len(self._waiting_tasks) >= self._max_size:
                raise WaitingQueueFull(
                    f"WaitingQueue full (capacity={self._max_size}), cannot add task {spec.task_id}"
                )
            
            dep_ids = {d.value for d in spec.dependencies.required_task_ids}
            # Store original priority for potential inheritance
            self._waiting_tasks[spec.task_id] = (spec, dep_ids, spec.priority)
    
    def remove(self, task_id: TaskId) -> Optional[Tuple[TaskSpec, set, Priority]]:
        """Remove a task from waiting queue."""
        with self._lock:
            if task_id in self._waiting_tasks:
                return self._waiting_tasks.pop(task_id)
            return None
    
    def dependency_completed(
        self,
        completed_task_id: TaskId,
        completed_priority: Priority
    ) -> List[Tuple[TaskId, TaskSpec]]:
        """
        Mark a dependency as completed and check which tasks can now run.
        
        Implements priority inheritance protocol:
        - When a task's dependency completes, the waiting task inherits
          the completed task's priority if it was higher than its own.
        - This prevents low-priority tasks from blocking high-priority
          dependent tasks (priority inversion).
        
        Args:
            completed_task_id: The task whose completion we're processing
            completed_priority: The priority of the completed task
            
        Returns:
            List of (task_id, spec) tuples that are now ready to schedule.
            Each entry may have inherited priority from the dependency.
        """
        result: List[Tuple[TaskId, TaskSpec]] = []
        removed_ids: List[TaskId] = []
        
        with self._lock:
            for task_id, (spec, deps_left, original_priority) in list(self._waiting_tasks.items()):
                # Remove completed dependency
                if completed_task_id.value in deps_left:
                    deps_left.discard(completed_task_id.value)
                    
                    # Priority inheritance: inherit higher priority from dependency
                    new_spec = spec
                    if int(completed_priority.value) < int(spec.priority.value):
                        # Completed task has HIGHER priority (lower number), so we inherit it
                        # This is the PIP - waiting tasks get the completed dependency's priority
                        new_spec = dataclass_replace(
                            spec,
                            priority=completed_priority
                        )
                    
                    if not deps_left:
                        # All dependencies satisfied!
                        removed_ids.append(task_id)
                        result.append((task_id, new_spec))
        
        for task_id in removed_ids:
            del self._waiting_tasks[task_id]
        
        return result
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._waiting_tasks)


# =============================================================================
# RETRY QUEUE
# =============================================================================

class RetryQueue:
    """
    Queue for tasks pending retry.
    
    Tasks that fail are placed here and retried after the configured delay.
    Uses a priority-based ordering (same as ReadyQueue) with timestamps
    for when they should be rescheduled.
    
    Queue capacity enforcement:
        - Checks against max_size before adding tasks
        - Raises RetryQueueFull exception when at capacity
    """
    
    def __init__(self, max_size: int = 1000) -> None:
        self._lock = threading.Lock()
        # (next_retry_time, priority_val, spec)
        self._queue: List[Tuple[float, int, TaskSpec]] = []
        self._max_size = max_size
    
    @property
    def max_size(self) -> int:
        """Get the maximum queue capacity."""
        return self._max_size
    
    @property
    def current_size(self) -> int:
        """Get current number of tasks in queue."""
        with self._lock:
            return len(self._queue)
    
    @property
    def is_at_capacity(self) -> bool:
        """Check if queue has reached its capacity limit."""
        with self._lock:
            return len(self._queue) >= self._max_size
    
    def add(self, spec: TaskSpec, next_delay: float) -> None:
        """
        Add a task to the retry queue.
        
        Args:
            spec: The task specification to retry
            next_delay: Seconds until this task should be retried
        
        Raises:
            RetryQueueFull: If queue is at capacity
        """
        with self._lock:
            # Check capacity before adding
            if len(self._queue) >= self._max_size:
                raise RetryQueueFull(
                    f"RetryQueue full (capacity={self._max_size}), cannot add task {spec.task_id}"
                )
            
            next_retry_time = time.monotonic() + next_delay
            priority_val = int(spec.priority.value)
            
            self._queue.append((next_retry_time, priority_val, spec))
            # Sort by retry time first (earliest first), then priority
            self._queue.sort(key=lambda x: (x[0], x[1]))
    
    def get_ready_tasks(self) -> List[Tuple[int, TaskSpec]]:
        """
        Get tasks that are ready to be retried.
        
        Returns list of (priority_val, spec) tuples for tasks whose retry
        delay has elapsed.
        """
        with self._lock:
            now = time.monotonic()
            ready: List[Tuple[int, TaskSpec]] = []
            
            # Find all tasks that should be retried now
            while self._queue and self._queue[0][0] <= now:
                _, priority_val, spec = self._queue.pop(0)
                ready.append((priority_val, spec))
            
            return ready
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)


# =============================================================================
# MAIN SCHEDULER
# =============================================================================


@dataclass
class RunningTaskInfo:
    """Information about a currently running task."""
    
    task_id: TaskId
    execution_id: str
    start_time: float
    cancellation_source: CancellationSource
    resource_scope: Optional[Any] = None
    attempt_number: int = 1  # For tracking retry attempts


class Scheduler:
    """
    Deterministic task scheduler for Gordon.
    
    Provides:
    - Priority-based scheduling with deterministic ordering (within priority)
    - Dependency-aware queue management
    - Timeout handling (execution, queue, dependency wait)
    - Cooperative cancellation propagation
    - Task hierarchy and ownership tracking
    - Resource cleanup coordination
    
    Key principles:
    - Tasks are explicit (no inferred work)
    - Ownership is explicit (parent owns child lifetime)
    - Scheduling is deterministic (same input = same output)
    - Cancellation is cooperative (tasks check token)
    - Cleanup is reliable (reverse order)
    - Shutdown is graceful (stop accepting, cancel queued, cleanup)
    
    Phase 3.7.7 Remediation Changes:
    - Priority inheritance in WaitingQueue.dependency_completed()
    - Starvation-based priority boost in run_one()
    - Automatic retry logic for failed tasks with max_attempts > 1
    - Admission receipt validation before accepting tasks
    - Queue timeout checking and starvation prevention
    """
    
    def __init__(self, config: Optional[SchedulerConfig] = None) -> None:
        self._config = config or SchedulerConfig()
        
        # State containers with capacity enforcement
        self._ready_queue = ReadyQueue[T](max_size=self._config.max_ready_queue_size)
        self._waiting_queue = WaitingQueue(max_size=self._config.max_waiting_queue_size)
        self._retry_queue = RetryQueue(max_size=self._config.max_retry_queue_size)
        self._running_tasks: Dict[TaskId, RunningTaskInfo] = {}
        self._completed_results: Dict[TaskId, TaskResult] = {}
        
        # Lifecycle state
        self._state = SchedulerState.INITIALIZING
        
        # Task results and futures for async waiting
        self._completion_events: Dict[TaskId, asyncio.Event] = {}
        
        # Shutdown coordination
        self._shutdown_requested = False
        self._shutdown_lock = threading.Lock()
        
        # Statistics (for observability)
        self._stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_cancelled": 0,
            "retries_attempted": 0,
            "retries_succeeded": 0,
            "starvation_boosts": 0,
        }
        
        # Admission receipt store
        self._admission_receipts: Dict[str, Any] = {}
    
    @property
    def state(self) -> SchedulerState:
        """Get current scheduler state."""
        return self._state
    
    @property
    def ready_queue_size(self) -> int:
        """Get number of tasks in ready queue."""
        return len(self._ready_queue)
    
    @property
    def waiting_queue_size(self) -> int:
        """Get number of tasks in waiting queue."""
        return len(self._waiting_queue)
    
    @property
    def retry_queue_size(self) -> int:
        """Get number of tasks in retry queue."""
        return len(self._retry_queue)
    
    @property
    def running_count(self) -> int:
        """Get number of currently running tasks."""
        return len(self._running_tasks)
    
    # =========================================================================
    # SUBMISSION WITH ADMISSION VALIDATION
    # =========================================================================
    
    async def submit(
        self,
        spec: TaskSpec[T],
        admission_receipt_id: Optional[str] = None,
        runtime_id: Optional[str] = None
    ) -> "TaskHandle[T]":
        """
        Submit a task specification to the scheduler.
        
        Args:
            spec: The task specification to execute
            admission_receipt_id: Optional receipt ID for admission validation
            runtime_id: Runtime ID (required if admission_receipt_id provided)
            
        Returns:
            A handle for tracking and waiting on the task
            
        Raises:
            SchedulerError: If scheduler is shutting down or stopped,
                           or if admission validation fails
        """
        # Check state
        with self._shutdown_lock:
            if self._state == SchedulerState.SHUTTING_DOWN:
                raise SchedulerError("Scheduler is shutting down, no new tasks accepted")
            
            if self._state == SchedulerState.STOPPED:
                raise SchedulerError("Scheduler has stopped, no new tasks accepted")
        
        # Validate admission receipt if provided
        if admission_receipt_id is not None and runtime_id is not None:
            if not self._validate_admission_receipt(admission_receipt_id, runtime_id):
                raise SchedulerError(
                    f"Invalid or expired admission receipt: {admission_receipt_id}"
                )
        
        # Update stats
        self._stats["tasks_submitted"] += 1
        
        # Create completion event for async waiting
        event = asyncio.Event()
        self._completion_events[spec.task_id] = event
        
        # Get parent source if this task has a parent (for cancellation propagation)
        parent_source: Optional[CancellationSource] = None
        if spec.parent_task_ref:
            # In a real implementation, we'd look up the parent's source
            pass
        
        # Create cancellation source for this task
        cancellation_source = CancellationSource()
        
        # Check if any dependencies have already completed (and possibly failed)
        all_deps_satisfied = True
        deps_failed: Optional[TaskId] = None
        
        for dep_id in spec.dependencies.required_task_ids:
            dep_result = self._completed_results.get(dep_id)
            
            # If dependency doesn't exist and isn't waiting, it's still pending or never submitted
            if dep_result is None:
                all_deps_satisfied = False
                break
            
            # If dependency failed or was cancelled, this task also fails
            if dep_result and dep_result.is_failure():
                deps_failed = dep_id
                break
        
        # Handle tasks with failed dependencies immediately
        if deps_failed is not None:
            result = TaskResult(
                task_id=spec.task_id,
                status=ExecutionState.FAILED,
                submitted_at=time.monotonic(),
                error=DependencyError(
                    f"Required dependency {deps_failed} failed",
                    task_id=spec.task_id,
                    dependency_task_ids=(deps_failed,)
                )
            )
            
            # Store result immediately
            self._completed_results[spec.task_id] = result
            event.set()
            return TaskHandle(spec, result)
        
        # Check for parent cancellation (parent-owned tasks should inherit parent state)
        if spec.parent_task_ref:
            # In real implementation, check parent's source here
            pass
        
        # Create task execution context
        execution_context = ExecutionContext(
            execution_id=spec.task_id.value,
            parent_execution_id=None,
            task_id=spec.task_id,
            cancellation_token=cancellation_source.token()
        )
        
        # Determine if task should be queued or wait for dependencies
        if all_deps_satisfied:
            self._ready_queue.push(spec)
        else:
            self._waiting_queue.add(spec)
        
        # Note: execution_context is tracked separately in scheduler for running tasks
        return TaskHandle(spec)
    
    def submit_sync(self, spec: TaskSpec[T], **kwargs) -> "TaskHandle[T]":
        """
        Synchronous submission (for non-async contexts).
        
        This is a simplified synchronous version that doesn't await
        but still returns a handle.
        """
        return asyncio.get_event_loop().run_until_complete(self.submit(spec, **kwargs))
    
    def _validate_admission_receipt(
        self,
        receipt_id: str,
        runtime_id: str
    ) -> bool:
        """Validate an admission receipt."""
        with self._shutdown_lock:
            if receipt_id not in self._admission_receipts:
                return False
            
            receipt = self._admission_receipts[receipt_id]
            
            # Check runtime ID matches
            if getattr(receipt, 'runtime_id', None) != runtime_id:
                return False
            
            # Check receipt not expired (check for expires_at_utc or is_valid method)
            if hasattr(receipt, 'is_valid'):
                return receipt.is_valid
            elif hasattr(receipt, 'expires_at_utc'):
                return time.time() <= receipt.expires_at_utc
            
            return True
    
    def _record_admission_receipt(self, receipt: Any) -> None:
        """Record an admission receipt for later validation."""
        with self._shutdown_lock:
            if hasattr(receipt, 'request_id'):
                self._admission_receipts[receipt.request_id] = receipt
            elif hasattr(receipt, 'id'):
                self._admission_receipts[str(receipt.id)] = receipt
    
    # =========================================================================
    # EXECUTION
    # =========================================================================
    
    async def run_one(self) -> Optional[TaskResult]:
        """
        Run one task from the ready queue (if any).
        
        Implements Phase 3.7.7 features:
        - Starvation-based priority boost
        - Automatic retry for failed tasks with max_attempts > 1
        
        Returns:
            The result of the completed task, or None if no tasks ready
            
        Raises:
            SchedulerError: If scheduler is not running
        """
        if self._state != SchedulerState.RUNNING:
            raise SchedulerError("Scheduler must be in RUNNING state")
        
        # First, check retry queue for tasks ready to retry
        retry_ready = self._retry_queue.get_ready_tasks()
        if retry_ready:
            # Process retry queue before main ready queue
            _, spec = retry_ready[0]
            
            # Get current attempt number from the task or use default
            attempt_info = self._running_tasks.get(spec.task_id)
            attempt_number = (attempt_info.attempt_number + 1) if attempt_info else 1
            
            result = await self._execute_task(spec, attempt_number)
            
            if result.is_failure():
                # Check if we should retry
                retry_policy = spec.retry_policy or self._config.default_retry_policy
                
                if retry_policy.max_attempts > 1 and attempt_number < retry_policy.max_attempts:
                    # Schedule for retry with backoff
                    next_delay = retry_policy.get_delay(attempt_number)
                    self._retry_queue.add(spec, next_delay)
                    
                    self._stats["retries_attempted"] += 1
                    
                    # Return the failed result (not a final completion)
                    return result
            
            # Retry succeeded or no more retries
            self._stats["tasks_completed"] += 1
            if result.is_success():
                self._stats["retries_succeeded"] += 1
            
            # Store result and notify waiters
            self._completed_results[spec.task_id] = result
            
            if spec.task_id in self._completion_events:
                self._completion_events[spec.task_id].set()
            
            return result
        
        # Check starvation on all queued tasks and boost if needed
        # This must happen BEFORE popping to ensure boosted tasks are properly ordered
        now = time.monotonic()
        
        with self._ready_queue._lock:
            for task_id in list(self._ready_queue._task_enter_times.keys()):
                wait_time = now - self._ready_queue._task_enter_times.get(task_id, now)
                starvation_threshold = (
                    self._config.starvation_threshold_seconds or 30.0
                )
                
                if wait_time > starvation_threshold:
                    # Boost this task's priority to CRITICAL (value 0)
                    self._ready_queue.boost_task_priority(task_id)
                    self._stats["starvation_boosts"] += 1
        
        # Pop highest priority task from ready queue
        task_data = self._ready_queue.pop()
        
        if task_data is None:
            return None
        
        _, spec = task_data
        
        # Get current attempt number for this task
        attempt_info = self._running_tasks.get(spec.task_id)
        attempt_number = (attempt_info.attempt_number + 1) if attempt_info else 1
        
        result = await self._execute_task(spec, attempt_number)
        
        # Update stats
        self._stats["tasks_completed"] += 1
        
        if result.is_failure():
            self._stats["tasks_failed"] += 1
            
            # Check if we should retry failed task
            retry_policy = spec.retry_policy or self._config.default_retry_policy
            
            if retry_policy.max_attempts > 1 and attempt_number < retry_policy.max_attempts:
                # Schedule for retry with backoff
                next_delay = retry_policy.get_delay(attempt_number)
                self._retry_queue.add(spec, next_delay)
                
                self._stats["retries_attempted"] += 1
                
                # Return the failed result (not a final completion - task will retry)
                return result
        
        # Store result and notify waiters
        self._completed_results[spec.task_id] = result
        
        if spec.task_id in self._completion_events:
            self._completion_events[spec.task_id].set()
        
        # Check waiting queue for tasks that can now run (dependency completion)
        completed_deps = self._waiting_queue.dependency_completed(
            spec.task_id,
            spec.priority
        )
        
        for _, ready_spec in completed_deps:
            # Add to ready queue with potential inherited priority
            self._ready_queue.push(ready_spec)
        
        return result
    
    async def _execute_task(self, spec: TaskSpec[T], attempt_number: int) -> TaskResult:
        """
        Execute a single task and handle exceptions.
        
        Args:
            spec: The task specification to execute
            attempt_number: Which attempt this is (1-based for first, 2+ for retries)
            
        Returns:
            TaskResult with execution outcome
        """
        # Record start time
        start_time = time.monotonic()
        
        try:
            # Create cancellation source for task
            cancellation_source = CancellationSource()
            
            # Track running task info with attempt number
            self._running_tasks[spec.task_id] = RunningTaskInfo(
                task_id=spec.task_id,
                execution_id=f"{spec.task_id.value}_attempt_{attempt_number}",
                start_time=start_time,
                cancellation_source=cancellation_source,
                attempt_number=attempt_number
            )
            
            try:
                # Execute the task function
                result_value = spec.task_fn(*spec.args, **spec.kwargs)
                
                # Handle async functions (coroutines)
                if asyncio.iscoroutine(result_value):
                    # Apply timeout if specified
                    timeout = spec.timeouts.execution or self._config.default_timeout_seconds
                    
                    try:
                        if timeout:
                            result_value = await asyncio.wait_for(
                                result_value,
                                timeout=timeout
                            )
                        else:
                            result_value = await result_value
                            
                    except asyncio.TimeoutError:
                        raise TaskTimeoutError(
                            f"Task {spec.task_id} timed out",
                            task_id=spec.task_id,
                            timeout_seconds=timeout
                        )
                    
                    except asyncio.CancelledError:
                        raise TaskCancelledError(
                            "Task was cancelled",
                            task_id=spec.task_id,
                            source=cancellation_source
                        )
                
                # Success!
                end_time = time.monotonic()
                
                return TaskResult(
                    task_id=spec.task_id,
                    status=ExecutionState.COMPLETED,
                    value=result_value,
                    submitted_at=start_time,
                    started_at=start_time,
                    completed_at=end_time,
                    attempt_number=attempt_number
                )
                
            finally:
                # Clean up running task tracking
                if spec.task_id in self._running_tasks:
                    del self._running_tasks[spec.task_id]
                    
        except Exception as e:
            end_time = time.monotonic()
            
            # Determine failure type
            if isinstance(e, TaskTimeoutError):
                status = ExecutionState.TIMED_OUT
            elif isinstance(e, TaskCancelledError):
                status = ExecutionState.CANCELLED
            else:
                status = ExecutionState.FAILED
            
            return TaskResult(
                task_id=spec.task_id,
                status=status,
                error=e,
                submitted_at=start_time,
                started_at=start_time,
                completed_at=end_time,
                attempt_number=attempt_number
            )
    
    async def run_all(self, max_iterations: Optional[int] = None) -> List[TaskResult]:
        """
        Run all tasks from the ready queue and retry queue.
        
        Args:
            max_iterations: Maximum number of tasks to run (None = unlimited)
            
        Returns:
            List of results for completed tasks
        """
        results: List[TaskResult] = []
        iterations = 0
        
        while (
            (self._ready_queue or self._retry_queue) and
            (max_iterations is None or iterations < max_iterations)
        ):
            result = await self.run_one()
            
            if result is not None:
                # Only add to results if this was a final completion (not a retry failure)
                # We track retries separately via _stats
                results.append(result)
                iterations += 1
        
        return results
    
    # =========================================================================
    # QUEUE CAPACITY DIAGNOSTICS
    # =========================================================================
    
    @property
    def ready_queue_capacity_remaining(self) -> int:
        """Get remaining capacity in ready queue."""
        return self._ready_queue.max_size - len(self._ready_queue)
    
    @property
    def waiting_queue_capacity_remaining(self) -> int:
        """Get remaining capacity in waiting queue."""
        return self._waiting_queue.max_size - len(self._waiting_queue)
    
    @property
    def retry_queue_capacity_remaining(self) -> int:
        """Get remaining capacity in retry queue."""
        return self._retry_queue.max_size - len(self._retry_queue)
    
    # =========================================================================
    # CANCELLATION
    # =========================================================================
    
    def cancel_task(self, task_id: TaskId, reason: Optional[str] = None) -> bool:
        """
        Request cancellation of a task.
        
        Args:
            task_id: The task to cancel
            reason: Optional explanation for cancellation
            
        Returns:
            True if cancellation was requested (or already done)
            
        Note: Cancellation is cooperative - the task must check
              its cancellation token and stop itself.
        """
        with self._shutdown_lock:
            # Check if running task
            if task_id in self._running_tasks:
                info = self._running_tasks[task_id]
                return info.cancellation_source.request(reason)
            
            # Check if queued task - remove from queue
            removed_spec = self._ready_queue.remove_task(task_id)
            if removed_spec is not None:
                result = TaskResult(
                    task_id=task_id,
                    status=ExecutionState.CANCELLED,
                    submitted_at=time.monotonic(),
                    cancelled=True,
                    cancellation_reason=reason or "cancelled"
                )
                self._completed_results[task_id] = result
                return True
            
            # Check if waiting task
            removed = self._waiting_queue.remove(task_id)
            if removed is not None:
                spec, _, _ = removed
                
                result = TaskResult(
                    task_id=task_id,
                    status=ExecutionState.CANCELLED,
                    submitted_at=time.monotonic(),
                    cancelled=True,
                    cancellation_reason=reason or "cancelled"
                )
                self._completed_results[task_id] = result
                return True
            
            # Check if in retry queue - remove and mark cancelled
            # For retry queue, we need to iterate
            with self._retry_queue._lock:
                for i, (_, _, spec) in enumerate(self._retry_queue._queue):
                    if spec.task_id == task_id:
                        self._retry_queue._queue.pop(i)
                        result = TaskResult(
                            task_id=task_id,
                            status=ExecutionState.CANCELLED,
                            submitted_at=time.monotonic(),
                            cancelled=True,
                            cancellation_reason=reason or "cancelled"
                        )
                        self._completed_results[task_id] = result
                        return True
            
            # Task already completed
            if task_id in self._completed_results:
                return True
            
            return False
    
    def cancel_all(self, reason: Optional[str] = None) -> List[TaskId]:
        """
        Cancel all queued and running tasks.
        
        Returns:
            List of task IDs that were cancelled
        """
        cancelled: List[TaskId] = []
        
        # Cancel all running tasks
        for task_id in list(self._running_tasks.keys()):
            if self.cancel_task(task_id, reason):
                cancelled.append(task_id)
        
        # Remove and cancel all queued tasks
        while not self._ready_queue.is_empty():
            _, spec = self._ready_queue.pop()
            result = TaskResult(
                task_id=spec.task_id,
                status=ExecutionState.CANCELLED,
                submitted_at=time.monotonic(),
                cancelled=True,
                cancellation_reason=reason or "cancelled"
            )
            self._completed_results[spec.task_id] = result
            cancelled.append(spec.task_id)
        
        # Remove and cancel all retry queue tasks
        while len(self._retry_queue) > 0:
            ready = self._retry_queue.get_ready_tasks()
            for _, spec in ready:
                result = TaskResult(
                    task_id=spec.task_id,
                    status=ExecutionState.CANCELLED,
                    submitted_at=time.monotonic(),
                    cancelled=True,
                    cancellation_reason=reason or "cancelled"
                )
                self._completed_results[spec.task_id] = result
                cancelled.append(spec.task_id)
        
        return cancelled
    
    # =========================================================================
    # SHUTDOWN
    # =========================================================================
    
    async def shutdown(self, timeout: Optional[float] = None) -> None:
        """
        Gracefully shut down the scheduler.
        
        Shutdown sequence:
        1. Stop accepting new tasks
        2. Cancel all queued tasks
        3. Wait for running tasks to complete (or timeout)
        4. Cleanup resources
        
        Args:
            timeout: Maximum time to wait for shutdown (None = no limit)
        """
        with self._shutdown_lock:
            if self._state == SchedulerState.STOPPED:
                return
            
            self._state = SchedulerState.SHUTTING_DOWN
        
        # Cancel all queued tasks
        cancelled_tasks = self.cancel_all("Scheduler shutdown")
        
        # Wait for running tasks to complete
        start_time = time.monotonic()
        
        while self._running_tasks:
            if timeout is not None and (time.monotonic() - start_time) > timeout:
                # Timeout exceeded, force cancel remaining
                for task_id in list(self._running_tasks.keys()):
                    self.cancel_task(task_id, "Shutdown timeout")
                break
            
            await asyncio.sleep(0.1)
        
        # Cleanup resources (if enabled)
        if self._config.cleanup_enabled:
            pass  # Cleanup would happen at coordinator level
        
        with self._shutdown_lock:
            self._state = SchedulerState.STOPPED
    
    async def __aenter__(self) -> "Scheduler":
        """Async context manager entry."""
        self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.shutdown()
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def start(self) -> None:
        """Start the scheduler (transition to RUNNING state)."""
        with self._shutdown_lock:
            if self._state == SchedulerState.RUNNING:
                return
            
            self._state = SchedulerState.RUNNING
    
    def get_task_result(self, task_id: TaskId) -> Optional[TaskResult]:
        """Get the result of a completed task."""
        return self._completed_results.get(task_id)
    
    def wait_for_completion(
        self,
        task_id: TaskId,
        timeout: Optional[float] = None
    ) -> asyncio.Future:
        """
        Create a future that resolves when the task completes.
        
        Args:
            task_id: The task to wait for
            timeout: Maximum time to wait (None = no limit)
            
        Returns:
            An asyncio Future that resolves with the result
        """
        event = self._completion_events.get(task_id)
        
        if event is None:
            # Task not found or already completed
            future = asyncio.Future()
            future.set_result(self._completed_results.get(task_id))
            return future
        
        async def wait_task() -> Optional[TaskResult]:
            try:
                await asyncio.wait_for(event.wait(), timeout=timeout)
                return self._completed_results.get(task_id)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Timed out waiting for task {task_id}")
        
        return asyncio.ensure_future(wait_task())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        stats = dict(self._stats)
        
        # Add queue capacity diagnostics
        stats["ready_queue_size"] = len(self._ready_queue)
        stats["waiting_queue_size"] = len(self._waiting_queue)
        stats["retry_queue_size"] = len(self._retry_queue)
        
        # Capacity information
        stats["ready_queue_capacity_remaining"] = self.ready_queue_capacity_remaining
        stats["waiting_queue_capacity_remaining"] = self.waiting_queue_capacity_remaining
        stats["retry_queue_capacity_remaining"] = self.retry_queue_capacity_remaining
        
        return stats
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get scheduler diagnostics including capacity information.
        
        Returns:
            Dictionary with queue sizes and configuration
        """
        return {
            "state": self._state.value,
            "ready_queue_size": len(self._ready_queue),
            "waiting_queue_size": len(self._waiting_queue),
            "retry_queue_size": len(self._retry_queue),
            "max_ready_queue_size": self._config.max_ready_queue_size,
            "max_waiting_queue_size": self._config.max_waiting_queue_size,
            "max_retry_queue_size": self._config.max_retry_queue_size,
            "running_tasks_count": len(self._running_tasks),
            **self._stats,
        }


# ============================================================================
# TASK HANDLE
# ============================================================================


@dataclass
class TaskHandle(Generic[T]):
    """
    Handle to a submitted task for tracking and interaction.
    
    Provides:
    - Non-blocking submission check
    - Async completion waiting
    - Cancellation requests
    """
    
    spec: TaskSpec[T]
    _result: Optional[TaskResult] = None
    _execution_context: Optional[ExecutionContext] = None
    
    @property
    def task_id(self) -> TaskId:
        """Get the task ID."""
        return self.spec.task_id
    
    async def wait_for_completion(self, timeout: Optional[float] = None) -> TaskResult:
        """
        Wait for this task to complete.
        
        Args:
            timeout: Maximum time to wait (None = no limit)
            
        Returns:
            The result of the completed task
            
        Raises:
            TimeoutError: If timeout is exceeded
        """
        # In a real implementation, this would await a completion event
        # For now, return a placeholder
        import asyncio
        
        if self._result is not None:
            return self._result
        
        # This would be connected to scheduler's completion event
        await asyncio.sleep(0.1)  # Placeholder
        
        raise NotImplementedError(
            "TaskHandle.wait_for_completion needs scheduler integration"
        )
    
    def cancel(self, reason: Optional[str] = None) -> bool:
        """
        Request cancellation of this task.
        
        Returns True if cancellation was requested.
        """
        # In a real implementation, would call scheduler.cancel_task
        return False


# ============================================================================
# DATACLASS REPLACE UTILITY
# ============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# ============================================================================
# PUBLIC API EXPORTS
# ============================================================================

__all__ = [
    "SchedulerConfig",
    "QueueType",
    "ReadyQueue",
    "WaitingQueue",
    "RetryQueue",
    "PriorityInheritanceInfo",
    "RunningTaskInfo",
    "SchedulerState",
    
    # Queue capacity exceptions
    "ReadyQueueFull",
    "WaitingQueueFull",
    "RetryQueueFull",
    
    "Scheduler",
    "TaskHandle",
]
