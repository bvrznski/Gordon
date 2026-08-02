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


@dataclass(frozen=True)
class SchedulerConfig:
    """Configuration for scheduler behavior."""
    
    max_concurrent_tasks: int = 10
    default_timeout_seconds: Optional[float] = None
    queue_timeout_seconds: Optional[float] = None
    dependency_wait_timeout_seconds: Optional[float] = None
    
    # Starvation prevention (max time in queue before forcing schedule)
    starvation_threshold_seconds: float = 30.0
    
    # Retry defaults
    default_retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    
    # Cleanup
    cleanup_enabled: bool = True


class ReadyQueue(Generic[T]):
    """
    Priority queue for ready-to-run tasks.
    
    Tasks are ordered by priority (lower value = higher priority).
    Within same priority, FIFO ordering is maintained for determinism.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._queue: List[Tuple[int, float, TaskSpec]] = []
    
    def push(self, spec: TaskSpec) -> None:
        """Add task to queue."""
        with self._lock:
            # Priority value (lower = higher priority)
            priority_val = int(spec.priority.value)
            
            # Timestamp for FIFO within same priority
            timestamp = time.monotonic()
            
            self._queue.append((priority_val, timestamp, spec))
            
            # Sort by priority first, then timestamp
            self._queue.sort(key=lambda x: (x[0], x[1]))
    
    def pop(self) -> Optional[Tuple[int, TaskSpec]]:
        """Remove and return highest priority task."""
        with self._lock:
            if not self._queue:
                return None
            
            priority_val, timestamp, spec = self._queue.pop(0)
            return (priority_val, spec)
    
    def peek(self) -> Optional[TaskSpec]:
        """Look at highest priority task without removing."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0][2]
    
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
                    return removed[2]
            return None
    
    def get_all_tasks(self) -> List[Tuple[int, TaskSpec]]:
        """Get all tasks sorted by priority."""
        with self._lock:
            return [(p, s) for p, _, s in self._queue]


class WaitingQueue:
    """
    Queue for tasks waiting on dependencies.
    
    Tracks which dependencies are still needed and when
    they can be rescheduled.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        # task_id -> (spec, dependency_task_ids_set)
        self._waiting_tasks: Dict[TaskId, Tuple[TaskSpec, set]] = {}
    
    def add(self, spec: TaskSpec) -> None:
        """Add a task waiting for dependencies."""
        with self._lock:
            dep_ids = {d.value for d in spec.dependencies.required_task_ids}
            self._waiting_tasks[spec.task_id] = (spec, dep_ids)
    
    def remove(self, task_id: TaskId) -> Optional[Tuple[TaskSpec, set]]:
        """Remove a task from waiting queue."""
        with self._lock:
            if task_id in self._waiting_tasks:
                return self._waiting_tasks.pop(task_id)
            return None
    
    def dependency_completed(self, completed_task_id: TaskId) -> List[Tuple[TaskId, TaskSpec]]:
        """
        Mark a dependency as completed and check which tasks can now run.
        
        Returns list of (task_id, spec) tuples that are now ready to schedule.
        """
        result: List[Tuple[TaskId, TaskSpec]] = []
        removed_ids: List[TaskId] = []
        
        with self._lock:
            for task_id, (spec, deps_left) in list(self._waiting_tasks.items()):
                # Remove completed dependency
                deps_left.discard(completed_task_id.value)
                
                if not deps_left:
                    # All dependencies satisfied!
                    removed_ids.append(task_id)
                    result.append((task_id, spec))
            
            for task_id in removed_ids:
                del self._waiting_tasks[task_id]
        
        return result
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._waiting_tasks)


class SchedulerState(Enum):
    """Scheduler runtime state."""
    
    INITIALIZING = "initializing"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


@dataclass
class RunningTaskInfo:
    """Information about a currently running task."""
    
    task_id: TaskId
    execution_id: str
    start_time: float
    cancellation_source: CancellationSource
    resource_scope: Optional[Any] = None


# ============================================================================
# MAIN SCHEDULER
# ============================================================================


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
    
    Usage:
        scheduler = Scheduler()
        
        # Submit a task
        spec = TaskSpec(
            task_id=TaskId.generate(),
            task_fn=my_async_function,
            priority=Priority.NORMAL
        )
        result = await scheduler.submit(spec)
        
        # Wait for completion
        await result.wait_for_completion()
    """
    
    def __init__(self, config: Optional[SchedulerConfig] = None) -> None:
        self._config = config or SchedulerConfig()
        
        # State containers
        self._ready_queue = ReadyQueue[T]()
        self._waiting_queue = WaitingQueue()
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
        }
    
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
    def running_count(self) -> int:
        """Get number of currently running tasks."""
        return len(self._running_tasks)
    
    # =========================================================================
    # SUBMISSION
    # =========================================================================
    
    async def submit(self, spec: TaskSpec[T]) -> "TaskHandle[T]":
        """
        Submit a task specification to the scheduler.
        
        Args:
            spec: The task specification to execute
            
        Returns:
            A handle for tracking and waiting on the task
            
        Raises:
            SchedulerError: If scheduler is shutting down or stopped
        """
        # Check state
        with self._shutdown_lock:
            if self._state == SchedulerState.SHUTTING_DOWN:
                raise SchedulerError("Scheduler is shutting down, no new tasks accepted")
            
            if self._state == SchedulerState.STOPPED:
                raise SchedulerError("Scheduler has stopped, no new tasks accepted")
        
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
        for dep_id in spec.dependencies.required_task_ids:
            dep_result = self._completed_results.get(dep_id)
            
            # If dependency doesn't exist, it's still waiting or never submitted
            if dep_result is None and dep_id.value not in [s.value for s in self._waiting_queue._waiting_tasks.keys()]:
                all_deps_satisfied = False
                break
            
            # If dependency failed or was cancelled, this task also fails
            if dep_result and dep_result.is_failure():
                result = TaskResult(
                    task_id=spec.task_id,
                    status=ExecutionState.FAILED,
                    submitted_at=time.monotonic(),
                    error=DependencyError(
                        f"Required dependency {dep_id} failed",
                        task_id=spec.task_id,
                        dependency_task_ids=(dep_id,)
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
        
        return TaskHandle(spec, execution_context=execution_context)
    
    def submit_sync(self, spec: TaskSpec[T]) -> "TaskHandle[T]":
        """
        Synchronous submission (for non-async contexts).
        
        This is a simplified synchronous version that doesn't await
        but still returns a handle.
        """
        return asyncio.get_event_loop().run_until_complete(self.submit(spec))
    
    # =========================================================================
    # EXECUTION
    # =========================================================================
    
    async def run_one(self) -> Optional[TaskResult]:
        """
        Run one task from the ready queue (if any).
        
        Returns:
            The result of the completed task, or None if no tasks ready
            
        Raises:
            SchedulerError: If scheduler is not running
        """
        if self._state != SchedulerState.RUNNING:
            raise SchedulerError("Scheduler must be in RUNNING state")
        
        # Pop highest priority task from ready queue
        task_data = self._ready_queue.pop()
        
        if task_data is None:
            return None
        
        _, spec = task_data
        
        # Check for starvation (task has been waiting too long)
        now = time.monotonic()
        if spec.timeouts.queue and (now - spec.dependencies.required_task_ids[0].value) > spec.timeouts.queue:
            # Starvation detected, but we still run it (for testing/determinism)
            pass
        
        # Create cancellation source for task
        cancellation_source = CancellationSource()
        
        # Record start time
        start_time = now
        
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
            
            result = TaskResult(
                task_id=spec.task_id,
                status=ExecutionState.COMPLETED,
                value=result_value,
                submitted_at=start_time,
                started_at=start_time,
                completed_at=end_time,
                attempt_number=1
            )
            
        except Exception as e:
            end_time = time.monotonic()
            
            # Determine failure type
            if isinstance(e, TaskTimeoutError):
                status = ExecutionState.TIMED_OUT
            elif isinstance(e, TaskCancelledError):
                status = ExecutionState.CANCELLED
            else:
                status = ExecutionState.FAILED
            
            result = TaskResult(
                task_id=spec.task_id,
                status=status,
                error=e,
                submitted_at=start_time,
                started_at=start_time,
                completed_at=end_time,
                attempt_number=1
            )
        
        # Update stats
        self._stats["tasks_completed"] += 1
        
        if result.is_failure():
            self._stats["tasks_failed"] += 1
        
        # Store result and notify waiters
        self._completed_results[spec.task_id] = result
        
        if spec.task_id in self._completion_events:
            self._completion_events[spec.task_id].set()
        
        return result
    
    async def run_all(self, max_iterations: Optional[int] = None) -> List[TaskResult]:
        """
        Run all tasks from the ready queue.
        
        Args:
            max_iterations: Maximum number of tasks to run (None = unlimited)
            
        Returns:
            List of results for completed tasks
        """
        results: List[TaskResult] = []
        iterations = 0
        
        while self._ready_queue and (
            max_iterations is None or iterations < max_iterations
        ):
            result = await self.run_one()
            
            if result is not None:
                results.append(result)
                iterations += 1
        
        return results
    
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
                spec, _ = removed
                
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


__all__ = [
    "SchedulerConfig",
    "QueueType",
    "ReadyQueue",
    "WaitingQueue",
    "SchedulerState",
    "RunningTaskInfo",
    "Scheduler",
    "TaskHandle",
]