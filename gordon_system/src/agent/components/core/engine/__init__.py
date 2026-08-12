# Core Engine Infrastructure
# ==========================
"""
Core execution engine for runtime operations.

Provides:
- Task orchestration and scheduling
- Resource coordination
- Execution context management
- Error handling and recovery
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from enum import Enum
import time

T = TypeVar("T")


# =============================================================================
# Engine Status
# =============================================================================

class EngineStatus(Enum):
    """
    Runtime engine operational status.
    
    States:
        - PENDING: Created but not yet initialized
        - INITIALIZING: Setting up resources
        - READY: Ready to process tasks
        - RUNNING: Actively processing
        - PAUSED: Temporarily suspended
        - STOPPING: Graceful shutdown in progress
        - STOPPED: Fully shut down
        - FAILED: Unrecoverable error
    """
    
    PENDING = "pending"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


# =============================================================================
# Execution Context
# =============================================================================

@dataclass(frozen=True)
class EngineExecutionContext:
    """
    Context for engine execution.
    
    Provides per-execution state and configuration.
    """
    
    execution_id: str
    parent_execution_id: Optional[str] = None
    
    priority: int = 0
    timeout_seconds: Optional[float] = None
    
    tags: Dict[str, str] = field(default_factory=dict)
    
    started_at: float = field(default_factory=time.time)
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root execution (no parent)."""
        return self.parent_execution_id is None


# =============================================================================
# Engine Contract
# =============================================================================

class EngineProtocol(Generic[T]):
    """
    Protocol for execution engine implementations.
    
    All engines must support:
        - Task submission and scheduling
        - Resource allocation/deallocation
        - Context management
        - Error handling and recovery
    
    Usage:
        class MyEngine(EngineProtocol[MyResultType]):
            async def submit(self, task_fn: Callable[..., T], *args, **kwargs) -> str:
                # Submit task and return ID
                pass
            
            async def execute(self, execution_id: str) -> EngineExecutionResult[T]:
                # Execute a specific task by ID
                pass
        
        engine = MyEngine()
    """
    
    @property
    def status(self) -> EngineStatus:
        """Return current engine status."""
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        """Return unique engine identifier."""
        raise NotImplementedError
    
    async def submit(
        self,
        task_fn: Callable[..., Any],
        *args,
        priority: int = 0,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Submit a task to the engine.
        
        Args:
            task_fn: The callable to execute
            *args: Positional arguments for the task
            priority: Execution priority (lower = more urgent)
            timeout_seconds: Maximum execution time
            **kwargs: Keyword arguments for the task
            
        Returns:
            Task/execution ID
            
        Raises:
            EngineNotReadyError: If engine is not ready
            EngineShutdownError: If engine is shutting down
        """
        raise NotImplementedError
    
    async def execute(self, execution_id: str) -> "EngineExecutionResult[T]":
        """
        Execute a specific task by ID.
        
        Args:
            execution_id: The ID of the task to execute
            
        Returns:
            Result with value or error
        """
        raise NotImplementedError
    
    async def cancel(self, execution_id: str) -> bool:
        """Cancel an executing or pending task."""
        raise NotImplementedError
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> List[str]:
        """
        Initiate graceful shutdown.
        
        Returns list of cancelled task IDs.
        """
        raise NotImplementedError
    
    @property
    def active_tasks(self) -> int:
        """Return count of currently executing tasks."""
        return 0
    
    @property
    def queued_tasks(self) -> int:
        """Return count of pending tasks."""
        return 0
    
    async def health_check(self) -> bool:
        """Check if engine is healthy."""
        return self.status == EngineStatus.RUNNING


# =============================================================================
# Execution Result
# =============================================================================

@dataclass(frozen=True)
class EngineExecutionResult(Generic[T]):
    """
    Result of an engine execution.
    
    Provides structured evidence of what happened during execution.
    """
    
    execution_id: str
    
    status: EngineStatus
    success: bool
    
    value: Optional[T] = None
    error: Optional[Exception] = None
    
    # Timing
    submitted_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Worker info
    worker_id: Optional[str] = None
    thread_id: Optional[int] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def queue_wait_seconds(self) -> Optional[float]:
        """Calculate time spent in queue."""
        if self.submitted_at and self.started_at:
            return self.started_at - self.submitted_at
        return None


# =============================================================================
# Engine Context Manager
# =============================================================================

class EngineContextManager:
    """
    Manages execution contexts for engine operations.
    
    Provides:
        - Context isolation per task
        - Context propagation for nested tasks
        - Cleanup on context exit
    
    Usage:
        manager = EngineContextManager()
        
        async with manager.context(execution_id="task_123") as ctx:
            # Execute within this context
            result = await execute_task(ctx)
    """
    
    def __init__(self) -> None:
        self._contexts: Dict[str, EngineExecutionContext] = {}
        self._lock = __import__("threading").Lock()
    
    async def create_context(
        self,
        execution_id: str,
        parent_execution_id: Optional[str] = None,
        priority: int = 0,
        timeout_seconds: Optional[float] = None,
        **tags
    ) -> EngineExecutionContext:
        """
        Create a new execution context.
        
        Args:
            execution_id: Unique ID for this execution
            parent_execution_id: Parent if nested, None for root
            priority: Execution priority
            timeout_seconds: Maximum duration
            **tags: String tags for categorization
            
        Returns:
            The created context
        """
        import uuid
        
        ctx = EngineExecutionContext(
            execution_id=execution_id,
            parent_execution_id=parent_execution_id,
            priority=priority,
            timeout_seconds=timeout_seconds,
            tags=dict(tags)
        )
        
        with self._lock:
            self._contexts[execution_id] = ctx
        
        return ctx
    
    async def get_context(self, execution_id: str) -> Optional[EngineExecutionContext]:
        """Get an existing context."""
        with self._lock:
            return self._contexts.get(execution_id)
    
    async def remove_context(self, execution_id: str) -> bool:
        """Remove a context."""
        with self._lock:
            if execution_id in self._contexts:
                del self._contexts[execution_id]
                return True
            return False
    
    @property
    def active_contexts(self) -> int:
        """Return count of active contexts."""
        with self._lock:
            return len(self._contexts)


# =============================================================================
# Resource Manager (for Engine)
# =============================================================================

@dataclass(frozen=True)
class ResourceManagerConfig:
    """
    Configuration for resource management.
    
    Defines limits and policies for resource allocation.
    """
    
    max_memory_mb: int = 1024
    max_threads: int = 8
    timeout_seconds: float = 30.0
    
    can_reuse_resources: bool = True


class ResourceManager:
    """
    Manages resources for engine execution.
    
    Provides:
        - Memory allocation tracking
        - Thread pool management
        - Timeout enforcement
    
    Usage:
        config = ResourceManagerConfig(max_memory_mb=512, max_threads=4)
        manager = ResourceManager(config)
        
        async with manager.acquire(task_id="task_1") as resources:
            # Execute with allocated resources
            pass
    """
    
    def __init__(self, config: Optional[ResourceManagerConfig] = None) -> None:
        self._config = config or ResourceManagerConfig()
        self._allocated_memory_mb: int = 0
        self._active_threads: int = 0
        self._lock = __import__("threading").Lock()
    
    @property
    def memory_remaining(self) -> int:
        """Return available memory in MB."""
        with self._lock:
            return max(0, self._config.max_memory_mb - self._allocated_memory_mb)
    
    @property
    def threads_available(self) -> int:
        """Return number of available threads."""
        with self._lock:
            return max(0, self._config.max_threads - self._active_threads)
    
    async def acquire(self, task_id: str, memory_mb: int = 128, threads: int = 1):
        """
        Acquire resources for a task.
        
        Args:
            task_id: The task requesting resources
            memory_mb: Memory in MB to allocate
            threads: Number of threads to reserve
            
        Returns:
            Context manager for resource release
        """
        import asyncio
        
        async def acquire_resources():
            with self._lock:
                if (memory_mb > self.memory_remaining or 
                    threads > self.threads_available):
                    raise ResourceError(f"Insufficient resources: need {memory_mb}MB, {threads} threads")
                
                self._allocated_memory_mb += memory_mb
                self._active_threads += threads
        
        await acquire_resources()
        
        return ResourceManagerAcquisition(self, task_id, memory_mb, threads)


class ResourceManagerAcquisition:
    """Resource acquisition context."""
    
    def __init__(
        self,
        manager: ResourceManager,
        task_id: str,
        memory_mb: int,
        threads: int
    ) -> None:
        self._manager = manager
        self._task_id = task_id
        self._memory_mb = memory_mb
        self._threads = threads
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        with self._manager._lock:
            self._manager._allocated_memory_mb -= self._memory_mb
            self._manager._active_threads -= self._threads


# =============================================================================
# Exception Types
# =============================================================================

class EngineError(Exception):
    """Base exception for engine errors."""
    pass


class EngineNotReadyError(EngineError):
    """Raised when engine is not ready to accept tasks."""
    
    def __init__(self, message: str = "Engine is not ready"):
        super().__init__(message)


class EngineShutdownError(EngineError):
    """Raised when operations are rejected due to shutdown."""
    
    def __init__(self, message: str = "Engine is shutting down"):
        super().__init__(message)


class ResourceError(EngineError):
    """Raised when resource allocation fails."""
    
    def __init__(self, message: str):
        super().__init__(message)


# =============================================================================
# Default Engine Implementation
# =============================================================================

class ThreadedExecutionEngine:
    """
    Reference engine implementation using thread pool.
    
    Provides a working implementation of EngineProtocol.
    
    Usage:
        engine = ThreadedExecutionEngine(max_workers=4)
        
        task_id = await engine.submit(my_task_fn, arg1, arg2)
        result = await engine.execute(task_id)
        
        cancelled = await engine.shutdown()
    """
    
    def __init__(self, max_workers: int = 8) -> None:
        self._max_workers = max_workers
        self._status = EngineStatus.PENDING
        
        import threading
        self._lock = threading.Lock()
        self._tasks: Dict[str, Any] = {}
        
        self._context_manager = EngineContextManager()
        self._resource_manager = ResourceManager(ResourceManagerConfig(
            max_memory_mb=1024,
            max_threads=max_workers
        ))
    
    @property
    def status(self) -> EngineStatus:
        return self._status
    
    @property
    def name(self) -> str:
        return f"ThreadedExecutionEngine_{id(self)}"
    
    async def submit(
        self,
        task_fn: Callable[..., Any],
        *args,
        priority: int = 0,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ) -> str:
        if self._status != EngineStatus.RUNNING:
            raise EngineNotReadyError("Engine is not running")
        
        import uuid
        
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            self._tasks[execution_id] = {
                "task_fn": task_fn,
                "args": args,
                "kwargs": kwargs,
                "priority": priority,
                "timeout_seconds": timeout_seconds,
                "status": EngineStatus.READY
            }
        
        return execution_id
    
    async def execute(self, execution_id: str) -> EngineExecutionResult[Any]:
        import threading
        
        with self._lock:
            task_info = self._tasks.get(execution_id)
            if task_info is None:
                raise EngineError(f"Unknown execution ID: {execution_id}")
            
            # Mark as executing
            self._tasks[execution_id]["status"] = EngineStatus.RUNNING
        
        result_container: Dict[str, Any] = {
            "value": None,
            "error": None
        }
        
        def worker():
            try:
                value = task_info["task_fn"](*task_info["args"], **task_info["kwargs"])
                result_container["value"] = value
            except Exception as e:
                result_container["error"] = e
        
        started_at = time.time()
        
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=task_info.get("timeout_seconds"))
        
        completed_at = time.time()
        
        with self._lock:
            if thread.is_alive():
                # Timeout
                self._tasks[execution_id]["status"] = EngineStatus.FAILED
                
                return EngineExecutionResult(
                    execution_id=execution_id,
                    status=EngineStatus.FAILED,
                    success=False,
                    error=TimeoutError(f"Execution exceeded timeout"),
                    started_at=started_at,
                    completed_at=completed_at
                )
            
            self._tasks[execution_id]["status"] = (
                EngineStatus.STOPPED if result_container["error"] is None else 
                EngineStatus.FAILED
            )
        
        return EngineExecutionResult(
            execution_id=execution_id,
            status=self._tasks[execution_id]["status"],
            success=result_container["error"] is None,
            value=result_container["value"],
            error=result_container["error"],
            started_at=started_at,
            completed_at=completed_at
        )
    
    async def cancel(self, execution_id: str) -> bool:
        with self._lock:
            if execution_id not in self._tasks:
                return False
            
            task_status = self._tasks[execution_id]["status"]
            
            # Can only cancel pending/ready tasks
            if task_status in (EngineStatus.READY, EngineStatus.RUNNING):
                self._tasks[execution_id]["status"] = EngineStatus.STOPPED
                return True
            
            return False
    
    async def shutdown(self, timeout_seconds: float = 30.0) -> List[str]:
        with self._lock:
            cancelled = []
            
            for exec_id, task_info in list(self._tasks.items()):
                if task_info["status"] in (EngineStatus.READY, EngineStatus.RUNNING):
                    task_info["status"] = EngineStatus.STOPPED
                    cancelled.append(exec_id)
            
            self._status = EngineStatus.STOPPED
        
        return cancelled
    
    async def start(self) -> None:
        """Start the engine."""
        with self._lock:
            if self._status == EngineStatus.PENDING:
                self._status = EngineStatus.INITIALIZING
            self._status = EngineStatus.RUNNING
    
    @property
    def active_tasks(self) -> int:
        with self._lock:
            count = 0
            for t in self._tasks.values():
                if t["status"] == EngineStatus.RUNNING:
                    count += 1
            return count
    
    @property
    def queued_tasks(self) -> int:
        with self._lock:
            count = 0
            for t in self._tasks.values():
                if t["status"] == EngineStatus.READY:
                    count += 1
            return count
    
    async def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING


__all__ = [
    # Status
    "EngineStatus",
    
    # Context
    "EngineExecutionContext",
    "EngineContextManager",
    
    # Result
    "EngineExecutionResult",
    
    # Protocol
    "EngineProtocol",
    
    # Resources
    "ResourceManagerConfig",
    "ResourceManager",
    "ResourceManagerAcquisition",
    
    # Exceptions
    "EngineError",
    "EngineNotReadyError",
    "EngineShutdownError",
    "ResourceError",
    
    # Implementation
    "ThreadedExecutionEngine",
]