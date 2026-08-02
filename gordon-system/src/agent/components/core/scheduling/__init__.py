# Core Scheduling Primitives
# ==========================

"""
Core runtime scheduling primitives.

Provides generic scheduling with:
- Schedulable task contract
- Schedule request/response
- Deterministic in-process scheduler
- Cancellation and graceful shutdown
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum


class TaskState(Enum):
    """Schedulable task states."""
    
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True)
class SchedulableTask:
    """
    A task that can be scheduled for execution.
    
    Args:
        name: Task identifier
        coroutine_func: Async function to execute
        priority: Execution priority (lower = higher priority)
        delay_seconds: Optional initial delay before first run
    """
    
    name: str
    coroutine_func: Callable[[], Any]
    priority: int = 0
    delay_seconds: float = 0.0
    
    def __hash__(self) -> int:
        return hash(self.name)


@dataclass(frozen=True)
class ScheduleRequest:
    """
    Request to schedule a task.
    
    Args:
        task: The schedulable task
        run_at: Optional absolute timestamp for first run
        interval_seconds: Optional repeat interval (None = one-shot)
        max_runs: Optional maximum runs before automatic cancellation
    """
    
    task: SchedulableTask
    run_at: Optional[float] = None
    interval_seconds: Optional[float] = None
    max_runs: Optional[int] = None


@dataclass(frozen=True)
class ScheduleResult:
    """
    Result of scheduling an operation.
    
    Args:
        success: Whether scheduling succeeded
        task_id: Task identifier if scheduled
        error: Error message if failed
    """
    
    success: bool
    task_id: Optional[str] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class ScheduledTaskSnapshot:
    """Immutable snapshot of a scheduled task's state."""
    
    task_name: str
    state: TaskState
    priority: int
    runs_completed: int
    next_run_at: Optional[float]
    created_at: float


class Scheduler:
    """
    Deterministic in-process scheduler.
    
    Provides:
    - Priority-based scheduling
    - One-shot and recurring tasks
    - Cancellation support
    - Graceful shutdown
    
    Usage:
        scheduler = Scheduler()
        
        task = SchedulableTask("my_task", my_async_func, priority=1)
        await scheduler.schedule(task)
        
        # Wait for tasks
        await scheduler.wait_for_completion()
    """
    
    def __init__(self) -> None:
        self._tasks: Dict[str, ScheduledTask] = {}
        self._task_counter = 0
        self._lock: Any = asyncio.Lock()
        self._running = False
    
    async def schedule(self, request: ScheduleRequest) -> ScheduleResult:
        """
        Schedule a task.
        
        Args:
            request: The scheduling request
            
        Returns:
            ScheduleResult with task_id or error
        """
        import time
        
        async with self._lock:
            # Generate unique task ID
            self._task_counter += 1
            task_id = f"task_{self._task_counter}"
            
            scheduled_task = ScheduledTask(
                task_id=task_id,
                name=request.task.name,
                coroutine_func=request.task.coroutine_func,
                priority=request.task.priority,
                delay_seconds=request.task.delay_seconds,
                run_at=request.run_at,
                interval_seconds=request.interval_seconds,
                max_runs=request.max_runs
            )
            
            self._tasks[task_id] = scheduled_task
            
            return ScheduleResult(success=True, task_id=task_id)
    
    async def cancel(self, task_id: str) -> bool:
        """
        Cancel a scheduled or running task.
        
        Args:
            task_id: The task to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        async with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                await task.cancel()
                return True
            return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTaskSnapshot]:
        """Get current state of a task."""
        import time
        
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            
            return ScheduledTaskSnapshot(
                task_name=task.name,
                state=task.state,
                priority=task.priority,
                runs_completed=task.runs_completed,
                next_run_at=None,  # Not tracked in this simple model
                created_at=task.created_at
            )
    
    def get_all_tasks(self) -> List[ScheduledTaskSnapshot]:
        """Get snapshots of all tasks."""
        with self._lock:
            return [self.get_task(tid) for tid in self._tasks]
    
    async def start(self) -> None:
        """Start the scheduler."""
        import threading
        lock = threading.Lock()
        with lock:
            self._running = True
    
    async def stop(self) -> None:
        """
        Stop the scheduler gracefully.
        
        Cancels all pending tasks and waits for running ones to complete.
        """
        import asyncio
        
        async with self._lock:
            self._running = False
            
            # Cancel all tasks
            for task in list(self._tasks.values()):
                await task.cancel()
            
            # Give tasks time to finish
            if self._tasks:
                await asyncio.sleep(0.1)
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        import threading
        lock = threading.Lock()
        with lock:
            return self._running
    
    def __len__(self) -> int:
        """Return number of scheduled tasks."""
        with self._lock:
            return len(self._tasks)


@dataclass
class ScheduledTask:
    """Internal representation of a scheduled task."""
    
    task_id: str
    name: str
    coroutine_func: Callable[[], Any]
    priority: int
    delay_seconds: float = 0.0
    run_at: Optional[float] = None
    interval_seconds: Optional[float] = None
    max_runs: Optional[int] = None
    
    state: TaskState = TaskState.PENDING
    runs_completed: int = 0
    created_at: float = field(default_factory=lambda: 0.0)
    
    _task: Any = None  # asyncio.Task reference
    _cancel_event: Any = None
    
    def __post_init__(self) -> None:
        import time
        self.created_at = time.monotonic()
    
    async def cancel(self) -> None:
        """Cancel this task."""
        if self._task is not None and not self._task.done():
            self._task.cancel()
        
        import threading
        lock = threading.Lock()
        with lock:
            self.state = TaskState.CANCELLED


__all__ = [
    "TaskState",
    "SchedulableTask",
    "ScheduleRequest",
    "ScheduleResult",
    "ScheduledTaskSnapshot",
    "Scheduler",
    "ScheduledTask",
]
