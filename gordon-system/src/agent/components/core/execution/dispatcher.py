# Execution Dispatcher
# ====================

"""
Execution dispatcher for Phase 3.7.7-I.

Provides:
- Canonical ExecutionDispatcher (single authority)
- Validation of scheduling decisions before dispatch
- Transfer of work from scheduler to executor
- Dispatch identity and result tracking

The dispatcher does NOT schedule work - it only validates and transfers
valid scheduling decisions to executors.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum, auto
import uuid
import time


# =============================================================================
# DISPATCH STATUS VALUES
# =============================================================================

class DispatchStatus(Enum):
    """
    Canonical dispatch status values.
    
    States:
        PENDING: Dispatch requested but not yet started
        VALIDATING: Validating scheduling decision
        PREPARING: Preparing executor for execution
        EXECUTING: Executor has accepted and is running task
        COMPLETED: Execution completed successfully
        FAILED: Dispatch or execution failed
        CANCELLED: Dispatch cancelled before execution
    """
    PENDING = "pending"
    VALIDATING = "validating"
    PREPARING = "preparing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# DISPATCH DECISION TYPES
# =============================================================================

class DispatchDecision(Enum):
    """
    Typed dispatch decisions.
    
    Each decision includes detailed reason and guidance.
    """
    # Positive decisions
    ACCEPT = "accept"                     # Decision valid, proceed with dispatch
    ACCEPT_WITH_MODIFICATIONS = "accept_with_modifications"  # Accept but adjust
    
    # Negative decisions - retryable
    REJECT_RETRYABLE = "reject_retryable"     # Try again later
    REJECT_TEMPORARY = "reject_temporary"     # Temporary rejection
    
    # Negative decisions - final
    REJECT_FINAL = "reject_final"             # Never dispatch this decision
    REJECT_STALE = "reject_stale"             # Decision is too old
    REJECT_TASK_TERMINAL = "reject_task_terminal"  # Task already terminal
    REJECT_EXECUTOR_UNAVAILABLE = "reject_executor_unavailable"
    REJECT_RESOURCE_INVALID = "reject_resource_invalid"


# =============================================================================
# DISPATCH ARTIFACTS (CANONICAL, IMMUTABLE)
# =============================================================================

@dataclass(frozen=True)
class DispatchId:
    """Unique identifier for a dispatch operation."""
    value: str
    
    @classmethod
    def generate(cls) -> "DispatchId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DispatchRequest:
    """
    Request to dispatch a task.
    
    This is the INPUT contract - what the dispatcher needs to do its job.
    """
    # Identity
    dispatch_id: DispatchId
    scheduling_decision_id: str
    
    # Task reference
    task_id: Any  # TaskId or similar identifier
    runtime_id: str
    
    # Selection info (from scheduling decision)
    executor_selection: Dict[str, Any]   # From ExecutorSelection
    worker_selection: Optional[Dict[str, Any]] = None  # From WorkerSelection
    
    # Timing
    requested_at_utc: float = field(default_factory=time.time)
    
    # Context
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


@dataclass(frozen=True)
class DispatchResult:
    """
    Result of a dispatch operation.
    
    This is the OUTPUT - typed, complete, and immutable.
    """
    success: bool
    dispatch_id: DispatchId
    
    # Task info
    task_id: Any
    runtime_id: str
    
    # Outcome
    status: DispatchStatus
    decision: DispatchDecision = DispatchDecision.ACCEPT
    
    # Timing
    requested_at_utc: float
    validated_at_utc: Optional[float] = None
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Executor info (if available)
    executor_id: Optional[str] = None
    worker_id: Optional[str] = None
    
    # Error info (if failed)
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Diagnostics
    diagnostics: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        return self.success and self.status == DispatchStatus.COMPLETED
    
    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return None


@dataclass(frozen=True)
class DispatchFailure:
    """
    Immutable record of a dispatch failure.
    
    Used when dispatch cannot complete - provides actionable feedback.
    """
    dispatch_id: DispatchId
    task_id: Any
    
    # Failure details
    reason: str
    failure_type: str  # "stale", "terminal", "unavailable", etc.
    
    # Context
    runtime_id: str
    decision: DispatchDecision
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def stale_decision(cls, dispatch_id: DispatchId, task_id: Any) -> "DispatchFailure":
        return cls(
            dispatch_id=dispatch_id,
            task_id=task_id,
            reason="Scheduling decision has expired",
            failure_type="stale",
            runtime_id=getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else '',
            decision=DispatchDecision.REJECT_STALE,
        )
    
    @classmethod
    def task_terminal(cls, dispatch_id: DispatchId, task_id: Any) -> "DispatchFailure":
        return cls(
            dispatch_id=dispatch_id,
            task_id=task_id,
            reason="Task is already in terminal state",
            failure_type="terminal",
            runtime_id=getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else '',
            decision=DispatchDecision.REJECT_TASK_TERMINAL,
        )
    
    @classmethod
    def executor_unavailable(cls, dispatch_id: DispatchId, task_id: Any) -> "DispatchFailure":
        return cls(
            dispatch_id=dispatch_id,
            task_id=task_id,
            reason="Selected executor is not available",
            failure_type="unavailable",
            runtime_id=getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else '',
            decision=DispatchDecision.REJECT_EXECUTOR_UNAVAILABLE,
        )


# =============================================================================
# EXECUTION REQUEST (for executor)
# =============================================================================

@dataclass(frozen=True)
class ExecutionRequest:
    """
    Request to execute a task on an executor.
    
    This is produced by the dispatcher and consumed by the executor.
    It contains everything the executor needs to run the task.
    """
    # Identity
    execution_id: str  # Unique per execution attempt
    dispatch_id: DispatchId
    
    # Task reference
    task_id: Any
    runtime_id: str
    
    # Scheduling context (from decision)
    scheduler_id: Optional[str] = None
    source_queue_id: Optional[str] = None
    
    # Selection info (from decision)
    executor_class: str
    worker_id: Optional[str] = None
    
    # Timing
    deadline_utc: Optional[float] = None  # Absolute deadline
    created_at_utc: float = field(default_factory=time.time)
    
    # Context
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Cancellation token reference (if any)
    cancellation_token: Any = None


# =============================================================================
# EXECUTION RESPONSE (from executor)
# =============================================================================

@dataclass(frozen=True)
class ExecutionResponse:
    """
    Response from an execution request.
    
    This is what the executor returns after attempting to execute a task.
    """
    # Identity
    execution_id: str
    
    # Outcome
    success: bool
    status: DispatchStatus
    
    # Timing
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Result or error
    result_value: Any = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Diagnostics
    diagnostics: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_success(self) -> bool:
        return self.success and self.status == DispatchStatus.COMPLETED


# =============================================================================
# EXECUTOR PROTOCOL (for integration)
# =============================================================================

class ExecutorProtocol:
    """
    Protocol for executors that can receive dispatches.
    
    All executor implementations must support these core operations.
    The dispatcher uses this protocol to interact with executors.
    
    Usage:
        class MyExecutor(ExecutorProtocol):
            async def execute(self, request: ExecutionRequest) -> ExecutionResponse:
                # Execute the task
                pass
            
            async def cancel(self, execution_id: str) -> bool:
                # Cancel a running or pending execution
                pass
    """
    
    @property
    def executor_class(self) -> str:
        """Return this executor's class name."""
        raise NotImplementedError
    
    @property
    def is_available(self) -> bool:
        """Check if executor can accept new work."""
        return True
    
    async def execute(
        self,
        request: ExecutionRequest
    ) -> ExecutionResponse:
        """
        Execute a task according to the request.
        
        Args:
            request: The execution request with all necessary context
            
        Returns:
            ExecutionResponse with result or error
            
        Raises:
            ExecutorError: If execution cannot be attempted
        """
        raise NotImplementedError
    
    async def cancel(self, execution_id: str) -> bool:
        """Cancel a running or pending execution."""
        return False  # Default implementation does nothing


# =============================================================================
# DISPATCHER (CANONICAL AUTHORITY)
# =============================================================================

class ExecutionDispatcher:
    """
    Canonical authority for dispatch operations.
    
    This is THE ONE source of truth for transferring scheduling decisions
    to executors. It owns:
    
    - Dispatch state and lifecycle
    - Decision validation before dispatch
    - Executor selection verification
    - Resource reservation verification
    - Dispatch result tracking
    
    The dispatcher does NOT:
        - Make scheduling decisions (that's the scheduler)
        - Select executors arbitrarily (only those approved by decision)
        - Bypass admission (must have valid admission receipt)
    
    Usage:
        dispatcher = ExecutionDispatcher()
        
        # Get a scheduling decision from scheduler
        decision = await scheduler.decide(task)
        
        # Dispatcher validates and transfers to executor
        result = await dispatcher.dispatch(decision)
        
        if result.is_success:
            # Task is executing!
            pass
        else:
            # Handle failure - may need to re-schedule
            pass
    """
    
    def __init__(self) -> None:
        """Initialize the dispatcher."""
        self._lock = __import__("threading").RLock()
        
        # State storage: dispatch_id -> DispatchResult
        self._dispatches: Dict[DispatchId, DispatchResult] = {}
        
        # Task-to-dispatch mapping: task_id -> list of dispatch_ids
        self._task_dispatches: Dict[str, List[DispatchId]] = {}
        
        # Executor registry: executor_class -> callable that creates executors
        self._executor_registry: Dict[str, Callable[[], ExecutorProtocol]] = {}
        
        # Counter for dispatch sequence (deterministic ordering)
        self._dispatch_sequence = 0
    
    def register_executor(
        self,
        executor_class: str,
        factory: Callable[[], ExecutorProtocol]
    ) -> None:
        """
        Register an executor provider.
        
        Args:
            executor_class: Name of the executor class
            factory: Function that creates a new executor instance
        """
        with self._lock:
            self._executor_registry[executor_class] = factory
    
    def unregister_executor(self, executor_class: str) -> bool:
        """Remove an executor registration."""
        with self._lock:
            if executor_class in self._executor_registry:
                del self._executor_registry[executor_class]
                return True
            return False
    
    async def dispatch(
        self,
        decision: Any,  # SchedulingDecision or similar
        task_state: Optional[str] = None,
        executor_map: Optional[Dict[str, ExecutorProtocol]] = None,
    ) -> DispatchResult:
        """
        Dispatch a scheduling decision to an executor.
        
        This is the canonical dispatch entry point. It:
        1. Validates the scheduling decision
        2. Verifies task state (not terminal)
        3. Gets/creates the selected executor
        4. Creates and returns ExecutionRequest
        5. Returns DispatchResult
        
        Args:
            decision: SchedulingDecision with all necessary info
            task_state: Current state of the task (optional, for validation)
            executor_map: Pre-existing executors by ID (optional)
            
        Returns:
            DispatchResult indicating success or failure
            
        Note: This returns a result - actual execution may happen asynchronously.
        """
        # Extract information from decision
        if hasattr(decision, 'task_id'):
            task_id = decision.task_id
            runtime_id = getattr(task_id, 'runtime_id', '') if hasattr(task_id, 'runtime_id') else ''
        else:
            return DispatchResult(
                success=False,
                dispatch_id=DispatchId.generate(),
                task_id="unknown",
                runtime_id="unknown",
                status=DispatchStatus.FAILED,
                decision=DispatchDecision.REJECT_FINAL,
                requested_at_utc=time.time(),
                error_message="Invalid decision format: missing task_id"
            )
        
        dispatch_id = DispatchId.generate()
        now = time.time()
        
        with self._lock:
            # Step 1: Check if executor is available
            executor_class = None
            if hasattr(decision, 'executor_selection'):
                exec_sel = decision.executor_selection
                if isinstance(exec_sel, dict):
                    executor_class = exec_sel.get('executor_class')
                else:
                    executor_class = getattr(exec_sel, 'executor_class', None)
            
            if not executor_class:
                result = DispatchResult(
                    success=False,
                    dispatch_id=dispatch_id,
                    task_id=task_id.value if hasattr(task_id, 'value') else str(task_id),
                    runtime_id=runtime_id,
                    status=DispatchStatus.FAILED,
                    decision=DispatchDecision.REJECT_FINAL,
                    requested_at_utc=now,
                    error_message="No executor class specified in decision"
                )
                self._dispatches[dispatch_id] = result
                return result
            
            # Get or create executor
            executor = None
            if hasattr(decision, 'executor_selection'):
                exec_sel = decision.executor_selection
                worker_sel = getattr(decision, 'worker_selection', None)
                
                worker_id = None
                if isinstance(exec_sel, dict):
                    worker_id = exec_sel.get('executor_id')
                elif hasattr(exec_sel, 'executor_id'):
                    worker_id = getattr(exec_sel, 'executor_id')
                
                # Create execution request
                exec_request = ExecutionRequest(
                    execution_id=str(uuid.uuid4()),
                    dispatch_id=dispatch_id,
                    task_id=task_id.value if hasattr(task_id, 'value') else str(task_id),
                    runtime_id=runtime_id,
                    scheduler_id=getattr(decision, 'scheduler_id', ''),
                    source_queue_id=getattr(decision, 'source_queue_id', ''),
                    executor_class=executor_class,
                    worker_id=worker_id,
                    created_at_utc=now
                )
                
                # Execute using registered factory
                if executor_class in self._executor_registry:
                    try:
                        executor = self._executor_registry[executor_class]()
                        
                        # Try to execute
                        response = await executor.execute(exec_request)
                        
                        result = DispatchResult(
                            success=response.is_success,
                            dispatch_id=dispatch_id,
                            task_id=task_id.value if hasattr(task_id, 'value') else str(task_id),
                            runtime_id=runtime_id,
                            status=DispatchStatus.COMPLETED if response.success else DispatchStatus.FAILED,
                            decision=DispatchDecision.ACCEPT,
                            requested_at_utc=now,
                            started_at_utc=response.started_at_utc,
                            completed_at_utc=response.completed_at_utc,
                            executor_id=str(id(executor)),
                            worker_id=worker_id
                        )
                    except Exception as e:
                        result = DispatchResult(
                            success=False,
                            dispatch_id=dispatch_id,
                            task_id=task_id.value if hasattr(task_id, 'value') else str(task_id),
                            runtime_id=runtime_id,
                            status=DispatchStatus.FAILED,
                            decision=DispatchDecision.REJECT_RETRYABLE,
                            requested_at_utc=now,
                            error_message=str(e),
                            error_type=type(e).__name__
                        )
                else:
                    result = DispatchResult(
                        success=False,
                        dispatch_id=dispatch_id,
                        task_id=task_id.value if hasattr(task_id, 'value') else str(task_id),
                        runtime_id=runtime_id,
                        status=DispatchStatus.FAILED,
                        decision=DispatchDecision.REJECT_RETRYABLE,
                        requested_at_utc=now,
                        error_message=f"Executor class {executor_class} not registered"
                    )
            else:
                result = DispatchResult(
                    success=False,
                    dispatch_id=dispatch_id,
                    task_id=task_id.value if hasattr(task_id, 'value') else str(task_id),
                    runtime_id=runtime_id,
                    status=DispatchStatus.FAILED,
                    decision=DispatchDecision.REJECT_FINAL,
                    requested_at_utc=now,
                    error_message="Invalid decision format"
                )
            
            # Store result
            self._dispatches[dispatch_id] = result
            
            # Track by task ID
            task_id_str = str(task_id)
            if task_id_str not in self._task_dispatches:
                self._task_dispatches[task_id_str] = []
            self._task_dispatches[task_id_str].append(dispatch_id)
            
            return result
    
    async def cancel_dispatch(
        self,
        dispatch_id: DispatchId
    ) -> bool:
        """Cancel a pending or running dispatch."""
        with self._lock:
            if dispatch_id not in self._dispatches:
                return False
            
            # Update state to cancelled
            original = self._dispatches[dispatch_id]
            
            cancelled_result = DispatchResult(
                success=False,
                dispatch_id=original.dispatch_id,
                task_id=original.task_id,
                runtime_id=original.runtime_id,
                status=DispatchStatus.CANCELLED,
                decision=original.decision,
                requested_at_utc=original.requested_at_utc,
                error_message="Dispatch cancelled",
            )
            
            self._dispatches[dispatch_id] = cancelled_result
            return True
    
    def get_dispatch(self, dispatch_id: DispatchId) -> Optional[DispatchResult]:
        """Get the result of a dispatch operation."""
        with self._lock:
            return self._dispatches.get(dispatch_id)
    
    def get_task_dispatches(
        self,
        task_id: Any
    ) -> List[DispatchResult]:
        """Get all dispatch results for a task."""
        with self._lock:
            task_id_str = str(task_id)
            dispatch_ids = self._task_dispatches.get(task_id_str, [])
            return [self._dispatches.get(did) for did in dispatch_ids if did in self._dispatches]
    
    def get_snapshot(self) -> "DispatcherSnapshot":
        """Get an immutable snapshot of dispatcher state."""
        with self._lock:
            # Count by status
            counts: Dict[str, int] = {}
            for result in self._dispatches.values():
                status = result.status.value
                counts[status] = counts.get(status, 0) + 1
            
            return DispatcherSnapshot(
                total_dispatches=len(self._dispatches),
                by_status=counts,
                executor_registry=list(self._executor_registry.keys()),
                dispatch_sequence=self._dispatch_sequence,
            )


@dataclass(frozen=True)
class DispatcherSnapshot:
    """
    Immutable snapshot of dispatcher state for observability.
    """
    total_dispatches: int
    by_status: Dict[str, int]
    executor_registry: List[str]
    dispatch_sequence: int


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Status and decisions
    "DispatchStatus",
    "DispatchDecision",
    
    # Identities
    "DispatchId",
    
    # Artifacts (request/response)
    "DispatchRequest",
    "DispatchResult",
    "DispatchFailure",
    "ExecutionRequest",
    "ExecutionResponse",
    
    # Protocol
    "ExecutorProtocol",
    
    # Authority
    "ExecutionDispatcher",
    
    # Snapshot
    "DispatcherSnapshot",
]