# Core Executor Infrastructure
# ============================
"""
Core runtime executor for tasks and workflows.

Provides:
- Task execution abstraction
- Worker pool management
- Execution policy enforcement
- Resource coordination
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, List, Dict, TypeVar, Generic
from enum import Enum
import time

T = TypeVar("T")


# =============================================================================
# Executor Status
# =============================================================================

class ExecutorStatus(Enum):
    """
    Executor operational status.
    
    States:
        - PENDING: Created but not yet initialized
        - READY: Initialized and ready for tasks
        - RUNNING: Actively executing tasks
        - PAUSED: Temporarily stopped (can resume)
        - STOPPING: Graceful shutdown in progress
        - STOPPED: Fully shut down
        - FAILED: Unrecoverable error
    """
    
    PENDING = "pending"           # Not yet initialized
    READY = "ready"               # Initialized and waiting for tasks
    RUNNING = "running"           # Actively executing tasks
    PAUSED = "paused"             # Temporarily stopped
    STOPPING = "stopping"         # Graceful shutdown in progress
    STOPPED = "stopped"           # Fully shut down
    FAILED = "failed"             # Unrecoverable error


# =============================================================================
# Task Execution Result
# =============================================================================

@dataclass(frozen=True)
class ExecutorTaskResult(Generic[T]):
    """
    Result of a task executed by the executor.
    
    Provides structured evidence of execution outcome.
    """
    
    task_id: str  # Unique task identifier
    status: ExecutorStatus
    
    # Execution results
    value: Optional[T] = None
    error: Optional[Exception] = None
    
    # Timing
    submitted_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Worker info
    worker_id: Optional[str] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def queue_wait_seconds(self) -> Optional[float]:
        """Calculate time spent in queue."""
        if self.submitted_at and self.started_at:
            return self.started_at - self.submitted_at
        return None
    
    def is_success(self) -> bool:
        """Check if execution succeeded."""
        return self.status == ExecutorStatus.STOPPED and self.error is None
    
    def is_failure(self) -> bool:
        """Check if execution failed (for any reason)."""
        return self.error is not None or self.status == ExecutorStatus.FAILED


# =============================================================================
# Executor Protocol
# =============================================================================

class ExecutorProtocol(Generic[T]):
    """
    Protocol for executor implementations.
    
    All executor implementations must support these core operations:
        - submit: Queue a task for execution
        - execute: Execute a task synchronously (for synchronous executors)
        - shutdown: Graceful shutdown with timeout
        - cancel: Cancel pending or running tasks
    
    Usage:
        class MyExecutor(ExecutorProtocol[MyTaskType]):
            async def submit(self, task_fn: Callable[..., Any], *args, **kwargs) -> str:
                # Queue the task and return its ID
                pass
            
            async def execute(self, task_fn: Callable[..., T], *args, **kwargs) -> ExecutorTaskResult[T]:
                # Execute synchronously and return result
                pass
        
        executor = MyExecutor()
    """
    
    @property
    def status(self) -> ExecutorStatus:
        """Return current executor status."""
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        """Return unique executor name."""
        raise NotImplementedError
    
    async def submit(
        self,
        task_fn: Callable[..., Any],
        *args,
        priority: int = 0,
        **kwargs
    ) -> str:
        """
        Submit a task for asynchronous execution.
        
        Args:
            task_fn: The callable to execute
            *args: Positional arguments for the task
            priority: Execution priority (higher = more urgent)
            **kwargs: Keyword arguments for the task
            
        Returns:
            Task ID for tracking
        
        Raises:
            ExecutorNotReadyError: If executor is not ready
            ExecutorShutdownError: If executor is shutting down
        """
        raise NotImplementedError
    
    async def execute(
        self,
        task_fn: Callable[..., T],
        *args,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ) -> ExecutorTaskResult[T]:
        """
        Execute a task synchronously (for synchronous executors).
        
        This is for immediate execution without queuing.
        
        Args:
            task_fn: The callable to execute
            *args: Positional arguments for the task
            timeout_seconds: Maximum execution time
            **kwargs: Keyword arguments for the task
            
        Returns:
            Result with value or error
        """
        raise NotImplementedError
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> List[str]:
        """
        Initiate graceful shutdown.
        
        Waits for in-progress tasks to complete before stopping.
        
        Args:
            timeout_seconds: Maximum time to wait for pending tasks
            
        Returns:
            List of task IDs that were cancelled (if any)
        """
        raise NotImplementedError
    
    async def cancel(self, task_id: str) -> bool:
        """
        Cancel a pending or running task.
        
        Args:
            task_id: The ID of the task to cancel
            
        Returns:
            True if cancellation was initiated
        """
        raise NotImplementedError
    
    @property
    def active_tasks(self) -> int:
        """Return number of currently active tasks."""
        return 0
    
    @property
    def queued_tasks(self) -> int:
        """Return number of pending tasks in queue."""
        return 0
    
    async def health_check(self) -> bool:
        """
        Check if executor is healthy and operational.
        
        Returns:
            True if executor can accept tasks
        """
        return self.status == ExecutorStatus.RUNNING


# =============================================================================
# Worker Pool Management
# =============================================================================

@dataclass(frozen=True)
class WorkerInfo:
    """
    Information about an executor worker.
    
    Used for monitoring and load balancing.
    """
    
    worker_id: str
    current_task_id: Optional[str]
    status: ExecutorStatus
    
    started_at: float = field(default_factory=time.time)
    tasks_completed: int = 0
    
    @property
    def uptime_seconds(self) -> float:
        """Calculate worker uptime."""
        return time.monotonic() - self.started_at


class WorkerPool:
    """
    Managed pool of executor workers.
    
    Provides:
        - Dynamic worker scaling
        - Load balancing
        - Health monitoring
        - Graceful worker retirement
    
    Usage:
        pool = WorkerPool(max_workers=10)
        
        async with pool.worker() as worker_id:
            # Execute task on this worker
            pass
    """
    
    def __init__(self, max_workers: int = 8) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        
        self._max_workers = max_workers
        self._workers: Dict[str, WorkerInfo] = {}
        self._lock = __import__("threading").Lock()
    
    @property
    def max_workers(self) -> int:
        """Return maximum worker capacity."""
        return self._max_workers
    
    @property
    def active_workers(self) -> int:
        """Return number of currently active workers."""
        with self._lock:
            return len([w for w in self._workers.values() if w.status == ExecutorStatus.RUNNING])
    
    def _generate_worker_id(self) -> str:
        """Generate unique worker ID."""
        import uuid
        return f"worker_{uuid.uuid4().hex[:8]}"
    
    def acquire_worker(self) -> Optional[str]:
        """
        Acquire a worker from the pool.
        
        Returns:
            Worker ID if available, None if pool is exhausted
        """
        with self._lock:
            if len(self._workers) >= self._max_workers:
                return None
            
            worker_id = self._generate_worker_id()
            self._workers[worker_id] = WorkerInfo(
                worker_id=worker_id,
                current_task_id=None,
                status=ExecutorStatus.READY
            )
            
            return worker_id
    
    def release_worker(self, worker_id: str) -> None:
        """
        Release a worker back to the pool.
        
        Args:
            worker_id: The worker to release
        """
        with self._lock:
            if worker_id in self._workers:
                self._workers[worker_id] = WorkerInfo(
                    worker_id=worker_id,
                    current_task_id=None,
                    status=ExecutorStatus.READY,
                    started_at=self._workers[worker_id].started_at,
                    tasks_completed=self._workers[worker_id].tasks_completed + 1
                )
    
    def get_worker(self, worker_id: str) -> Optional[WorkerInfo]:
        """Get info about a specific worker."""
        with self._lock:
            return self._workers.get(worker_id)
    
    def list_workers(self) -> List[WorkerInfo]:
        """List all workers in the pool."""
        with self._lock:
            return list(self._workers.values())


# =============================================================================
# Priority Task Queue
# =============================================================================

@dataclass(frozen=True)
class QueuedTask(Generic[T]):
    """
    A task queued for execution.
    
    Includes priority metadata for scheduling decisions.
    """
    
    task_id: str
    task_fn: Callable[..., T]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0
    
    submitted_at: float = field(default_factory=time.time)
    
    # Execution tracking
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


class PriorityTaskQueue(Generic[T]):
    """
    Priority queue for task scheduling.
    
    Tasks are ordered by priority (lower value = higher priority).
    Supports insertion with priority, retrieval in order, and cancellation.
    
    Usage:
        queue = PriorityTaskQueue[str]()
        
        queue.enqueue(
            task_id="task_1",
            task_fn=my_function,
            priority=1  # High priority
        )
        
        next_task = queue.dequeue()
    """
    
    def __init__(self) -> None:
        self._tasks: List[QueuedTask[T]] = []
        self._lock = __import__("threading").Lock()
    
    @property
    def size(self) -> int:
        """Return number of tasks in queue."""
        with self._lock:
            return len(self._tasks)
    
    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        with self._lock:
            return len(self._tasks) == 0
    
    def enqueue(self, task: QueuedTask[T]) -> None:
        """
        Add a task to the queue.
        
        Tasks are inserted in priority order (lowest first).
        
        Args:
            task: The task to add
        """
        with self._lock:
            # Find insertion point based on priority (ascending = higher priority)
            insert_idx = 0
            for i, existing in enumerate(self._tasks):
                if task.priority >= existing.priority:
                    insert_idx = i + 1
                else:
                    break
            
            self._tasks.insert(insert_idx, task)
    
    def dequeue(self) -> Optional[QueuedTask[T]]:
        """
        Remove and return highest priority task.
        
        Returns:
            The highest priority task, or None if empty
        """
        with self._lock:
            if not self._tasks:
                return None
            
            # Pop from front (highest priority)
            return self._tasks.pop(0)
    
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a task in the queue.
        
        Args:
            task_id: The ID of the task to cancel
            
        Returns:
            True if cancelled
        """
        with self._lock:
            for i, task in enumerate(self._tasks):
                if task.task_id == task_id:
                    del self._tasks[i]
                    return True
            return False
    
    def peek(self) -> Optional[QueuedTask[T]]:
        """Return highest priority task without removing."""
        with self._lock:
            if not self._tasks:
                return None
            return self._tasks[0]


# =============================================================================
# Exception Types
# =============================================================================

class ExecutorError(Exception):
    """Base exception for executor errors."""
    pass


class ExecutorNotReadyError(ExecutorError):
    """Raised when executor is not ready to accept tasks."""
    
    def __init__(self, message: str = "Executor is not ready"):
        super().__init__(message)


class ExecutorShutdownError(ExecutorError):
    """Raised when operations are rejected due to shutdown."""
    
    def __init__(self, message: str = "Executor is shutting down"):
        super().__init__(message)


# =============================================================================
# Default Executor Implementation
# =============================================================================

class ThreadedExecutor:
    """
    Simple executor using thread pool for parallel execution.
    
    This provides a reference implementation of ExecutorProtocol.
    For production use, consider integrating with asyncio event loop.
    
    Usage:
        executor = ThreadedExecutor(max_workers=4)
        
        # Asynchronous submission
        task_id = await executor.submit(my_function, arg1, arg2)
        
        # Synchronous execution
        result = await executor.execute(my_function, arg1)
        
        # Cleanup
        cancelled = await executor.shutdown()
    """
    
    def __init__(self, max_workers: int = 8) -> None:
        self._max_workers = max_workers
        self._status = ExecutorStatus.PENDING
        
        self._queue = PriorityTaskQueue[Any]()
        self._worker_pool = WorkerPool(max_workers)
        
        import threading
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._running = False
    
    @property
    def status(self) -> ExecutorStatus:
        return self._status
    
    @property
    def name(self) -> str:
        return f"ThreadedExecutor_{id(self)}"
    
    async def submit(
        self,
        task_fn: Callable[..., Any],
        *args,
        priority: int = 0,
        **kwargs
    ) -> str:
        if self._status != ExecutorStatus.RUNNING:
            raise ExecutorNotReadyError("Executor is not running")
        
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task = QueuedTask(
            task_id=task_id,
            task_fn=task_fn,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        self._queue.enqueue(task)
        
        # Start worker if not already running
        if not self._running:
            await self._start_worker()
        
        return task_id
    
    async def execute(
        self,
        task_fn: Callable[..., T],
        *args,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ) -> ExecutorTaskResult[T]:
        import threading
        
        result_container: Dict[str, Any] = {"result": None, "error": None}
        
        def worker():
            try:
                value = task_fn(*args, **kwargs)
                result_container["result"] = value
            except Exception as e:
                result_container["error"] = e
        
        thread = threading.Thread(target=worker)
        started_at = time.time()
        
        thread.start()
        thread.join(timeout=timeout_seconds)
        
        if thread.is_alive():
            # Timeout occurred
            return ExecutorTaskResult(
                task_id=f"task_{time.monotonic_ns()}",
                status=ExecutorStatus.FAILED,
                error=TimeoutError(f"Execution exceeded {timeout_seconds}s timeout")
            )
        
        completed_at = time.time()
        
        if result_container["error"]:
            return ExecutorTaskResult(
                task_id=f"task_{time.monotonic_ns()}",
                status=ExecutorStatus.STOPPED,
                value=None,
                error=result_container["error"],
                started_at=started_at,
                completed_at=completed_at
            )
        
        return ExecutorTaskResult(
            task_id=f"task_{time.monotonic_ns()}",
            status=ExecutorStatus.STOPPED,
            value=result_container["result"],
            started_at=started_at,
            completed_at=completed_at
        )
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> List[str]:
        """Initiate graceful shutdown."""
        with self._lock:
            if self._status in (ExecutorStatus.STOPPING, ExecutorStatus.STOPPED):
                return []
            
            self._status = ExecutorStatus.STOPPING
        
        cancelled_tasks = []
        
        # Cancel all queued tasks
        while not self._queue.is_empty:
            task = self._queue.dequeue()
            if task:
                cancelled_tasks.append(task.task_id)
        
        with self._lock:
            self._status = ExecutorStatus.STOPPED
        
        return cancelled_tasks
    
    async def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        return self._queue.cancel(task_id)
    
    @property
    def active_tasks(self) -> int:
        # This is a simplified implementation
        return 0
    
    @property
    def queued_tasks(self) -> int:
        return self._queue.size
    
    async def health_check(self) -> bool:
        """Check executor health."""
        return self._status == ExecutorStatus.RUNNING
    
    async def _start_worker(self) -> None:
        """Start background worker thread (placeholder)."""
        pass


__all__ = [
    # Status
    "ExecutorStatus",
    
    # Results
    "ExecutorTaskResult",
    
    # Protocol
    "ExecutorProtocol",
    
    # Worker management
    "WorkerInfo",
    "WorkerPool",
    
    # Priority queue
    "QueuedTask",
    "PriorityTaskQueue",
    
    # Exceptions
    "ExecutorError",
    "ExecutorNotReadyError",
    "ExecutorShutdownError",
    
    # Implementation
    "ThreadedExecutor",
]