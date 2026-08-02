# Core Execution Primitives
# =========================

"""
Core runtime execution mechanics.

Provides generic execution with:
- Execution requests and results
- Cancellation handling
- Timeout handling
- Executor contract
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar, Generic
from enum import Enum


T = TypeVar("T")


class ExecutionStatus(Enum):
    """Execution result status."""
    
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class ExecutionRequest(Generic[T]):
    """
    Request to execute a unit of work.
    
    Args:
        task: Callable to execute
        args: Positional arguments for the callable
        kwargs: Keyword arguments for the callable
        timeout_seconds: Optional timeout in seconds
        priority: Execution priority (lower = higher priority)
    """
    
    task: Callable[[], Any]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    timeout_seconds: Optional[float] = None
    priority: int = 0
    
    def bind(self, *args: Any, **kwargs: Any) -> "ExecutionRequest[T]":
        """Return a new request with additional arguments."""
        return ExecutionRequest(
            task=self.task,
            args=self.args + args,
            kwargs={**self.kwargs, **kwargs},
            timeout_seconds=self.timeout_seconds,
            priority=self.priority
        )


@dataclass(frozen=True)
class ExecutionResult(Generic[T]):
    """
    Result of an execution.
    
    Args:
        status: Execution status
        value: Return value (if successful)
        error: Exception if failed (preserved cause chain)
        started_at: Timestamp when execution started
        completed_at: Timestamp when execution ended
        cancelled: Whether cancellation was requested
        timed_out: Whether timeout occurred
    """
    
    status: ExecutionStatus
    value: Optional[T] = None
    error: Optional[Exception] = None
    started_at: float = field(default_factory=lambda: 0.0)
    completed_at: float = field(default_factory=lambda: 0.0)
    cancelled: bool = False
    timed_out: bool = False
    
    @property
    def duration(self) -> float:
        """Return execution duration in seconds."""
        return self.completed_at - self.started_at
    
    def is_success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS
    
    def is_failure(self) -> bool:
        return self.status in (ExecutionStatus.FAILURE, ExecutionStatus.CANCELLED, ExecutionStatus.TIMEOUT)
    
    def unwrap(self) -> T:
        """Return the value or raise exception."""
        if self.error:
            raise self.error
        return self.value  # type: ignore


@dataclass(frozen=True)
class ExecutionContext:
    """
    Context for an execution.
    
    Args:
        execution_id: Unique identifier
        parent_execution_id: Parent if part of a chain
        timeout_seconds: Execution timeout
        priority: Priority level
        created_at: Timestamp
    """
    
    execution_id: str
    parent_execution_id: Optional[str] = None
    timeout_seconds: Optional[float] = None
    priority: int = 0
    created_at: float = field(default_factory=lambda: 0.0)


class Executor( Generic[T]):
    """
    Contract for execution engines.
    
    Provides async task execution with:
    - Cancellation support
    - Timeout support
    - Result capture
    
    Usage:
        executor = LocalExecutor()
        
        result = await executor.execute(
            ExecutionRequest(task=my_async_func)
        )
    """
    
    def __init__(self) -> None:
        self._tasks: dict = {}
    
    async def execute(self, request: ExecutionRequest[T]) -> ExecutionResult[T]:
        """
        Execute a request and return the result.
        
        Args:
            request: The execution request
            
        Returns:
            ExecutionResult with status, value or error
        """
        import time
        
        start_time = time.monotonic()
        
        try:
            # Create the task
            coro = request.task(*request.args, **request.kwargs)
            
            # Apply timeout if specified
            if request.timeout_seconds is not None:
                result = await asyncio.wait_for(coro, timeout=request.timeout_seconds)
            else:
                result = await coro
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                value=result,
                started_at=start_time,
                completed_at=time.monotonic()
            )
            
        except asyncio.CancelledError:
            return ExecutionResult(
                status=ExecutionStatus.CANCELLED,
                started_at=start_time,
                completed_at=time.monotonic(),
                cancelled=True
            )
            
        except asyncio.TimeoutError:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                started_at=start_time,
                completed_at=time.monotonic(),
                timed_out=True
            )
            
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILURE,
                error=e,
                started_at=start_time,
                completed_at=time.monotonic()
            )


class LocalExecutor(Executor[T]):
    """
    Simple local executor using asyncio.
    
    Executes tasks in the current event loop.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self._cancelled: set = set()
    
    async def execute(self, request: ExecutionRequest[T]) -> ExecutionResult[T]:
        """Execute request in local event loop."""
        return await super().execute(request)


def run_sync(coro):
    """
    Run a coroutine synchronously.
    
    Should only be used when asyncio.run() isn't available
    (e.g., inside existing event loops).
    
    Args:
        coro: Coroutine to execute
        
    Returns:
        Result of the coroutine
    """
    import asyncio
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    
    # Inside an existing loop - use run_until_complete
    return loop.run_until_complete(coro)


__all__ = [
    "ExecutionStatus",
    "ExecutionRequest",
    "ExecutionResult",
    "ExecutionContext",
    "Executor",
    "LocalExecutor",
    "run_sync",
]
