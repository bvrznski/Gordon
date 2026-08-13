# Core Execution Interface
# ========================

"""
Core execution interface - defines the contract for task execution.

This interface allows different execution strategies (synchronous, asynchronous,
concurrent) while providing a consistent way to execute tasks in the runtime.

ARCHITECTURAL PRINCIPLES:
- Execution is decoupled from task definition
- Multiple executor implementations possible (thread pool, event loop, etc.)
- Tasks are executed by ID/reference, not by implementation
- Execution results are returned as contracts, not concrete types
"""

from typing import Protocol, Optional, List, Any, Dict, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

T = TypeVar("T")


@dataclass(frozen=True)
class ExecutionId:
    """Unique identifier for an execution instance."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "ExecutionId":
        """Generate a new unique execution ID."""
        return cls(value=f"exec_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def from_string(cls, s: str) -> "ExecutionId":
        """Create an ExecutionId from a string."""
        return cls(value=s)


@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable context for execution.
    
    Args:
        execution_id: The unique ID of this execution instance
        parent_execution_id: ID of parent execution (for hierarchy)
        timestamp_utc: When this context was created
        metadata: Additional key-value data about the execution context
    """
    
    execution_id: str
    parent_execution_id: Optional[str] = None
    timestamp_utc: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionMode(Enum):
    """Execution strategy modes."""
    
    SYNCHRONOUS = "synchronous"     # Block until completion
    ASYNCHRONOUS = "asynchronous"   # Return immediately, deliver result later
    PARALLEL = "parallel"           # Run concurrently with other tasks
    CONCURRENT = "concurrent"       # Multiple operations in overlapping time periods


@dataclass(frozen=True)
class ExecutionResult(Generic[T]):
    """
    Result of an execution.
    
    Args:
        execution_id: Which execution produced this result
        status: Success, failure, cancelled, etc.
        value: The computed value (if successful)
        error: Error information (if failed)
        duration_ms: How long execution took in milliseconds
        timestamp_utc: When the result was produced
    """
    
    execution_id: str
    status: str  # "success", "failure", "cancelled"
    value: Optional[T] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp_utc: float = field(default_factory=time.time)
    
    def is_success(self) -> bool:
        """Check if execution succeeded."""
        return self.status == "success"
    
    def is_failure(self) -> bool:
        """Check if execution failed."""
        return self.status == "failure"
    
    def is_cancelled(self) -> bool:
        """Check if execution was cancelled."""
        return self.status == "cancelled"


class IExecutor(Protocol):
    """
    Interface for task executors.
    
    Executors are responsible for:
        - Accepting tasks for execution
        - Running them according to their mode (sync/async)
        - Returning results or errors
        - Managing execution resources
    
    This is a BEHAVIORAL contract - implementations can use threading,
    async/await, event loops, or other mechanisms as long as they conform.
    
    INVARIANTS:
        1. Execution is idempotent where appropriate (same inputs = same outputs)
        2. Cancellation is cooperative (executors provide cancellation tokens)
        3. Resources are cleaned up after execution
        4. Errors are properly propagated
    """
    
    @property
    def executor_id(self) -> str:
        """Get the unique ID of this executor."""
        ...
    
    @property
    def mode(self) -> ExecutionMode:
        """Get the execution mode of this executor."""
        ...
    
    async def execute(
        self,
        task_fn: Any,  # Callable[..., T]
        *args: Any,
        **kwargs: Any,
    ) -> ExecutionResult[T]:
        """
        Execute a task function.
        
        Args:
            task_fn: The callable to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result with status, value/error, and timing information
            
        Raises:
            ExecutorError: If executor is unavailable or misconfigured
        """
        ...
    
    async def execute_with_context(
        self,
        context: ExecutionContext,
        task_fn: Any,  # Callable[..., T]
        *args: Any,
        **kwargs: Any,
    ) -> ExecutionResult[T]:
        """
        Execute a task with explicit execution context.
        
        Args:
            context: The execution context (parent ID, metadata)
            task_fn: The callable to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result with status, value/error, and timing information
        """
        ...
    
    def cancel(self, execution_id: str) -> bool:
        """
        Attempt to cancel an in-progress execution.
        
        Args:
            execution_id: The ID of the execution to cancel
            
        Returns:
            True if cancellation was requested (not guaranteed success)
        """
        ...
    
    async def wait_for(
        self,
        execution_id: str,
        timeout_seconds: Optional[float] = None,
    ) -> ExecutionResult[Any]:
        """
        Wait for an execution to complete.
        
        Args:
            execution_id: The ID of the execution to wait for
            timeout_seconds: Maximum time to wait (None = wait forever)
            
        Returns:
            The final result when execution completes
            
        Raises:
            TimeoutError: If timeout expires before completion
        """
        ...
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get executor statistics for observability."""
        ...


class IExecutable(Protocol):
    """
    Interface for objects that can be executed.
    
    Implementations of this interface provide their own execution logic
    while conforming to the core execution contract.
    """
    
    @property
    def task_id(self) -> str:
        """Get the unique identifier for this executable task."""
        ...
    
    async def execute(
        self,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult[Any]:
        """
        Execute this task.
        
        Args:
            context: Optional execution context
            
        Returns:
            Result with status, value/error, and timing information
        """
        ...


class ExecutorError(Exception):
    """Raised when executor operations fail."""
    pass


class ExecutionTimeoutError(ExecutorError):
    """Raised when an execution times out."""
    
    def __init__(self, execution_id: str, timeout_seconds: float):
        super().__init__(
            f"Execution {execution_id} timed out after {timeout_seconds}s"
        )
        self.execution_id = execution_id
        self.timeout_seconds = timeout_seconds


class ExecutionCancelledError(ExecutorError):
    """Raised when an execution is cancelled."""
    
    def __init__(self, execution_id: str):
        super().__init__(f"Execution {execution_id} was cancelled")
        self.execution_id = execution_id


__all__ = [
    "ExecutionId",
    "ExecutionContext",
    "ExecutionMode",
    "ExecutionResult",
    "IExecutor",
    "IExecutable",
    "ExecutorError",
    "ExecutionTimeoutError",
    "ExecutionCancelledError",
]