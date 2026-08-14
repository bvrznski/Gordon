# Canonical Concurrency Architecture (Phase 3.20)
# ================================================
#
# Concurrency defines how independent execution progresses safely and deterministically.
#
# Canonical Model:
#     Execution → Concurrency → Parallelism → Coordination → Execution Continuation
#
# Concurrency PRINCIPLES:
# - Concurrency never performs computation
# - Concurrency never owns runtime state
# - Concurrency governs safe progression of independent execution
# - Concurrency preserves architectural isolation
# - Concurrency enables deterministic, reproducible execution

"""
Canonical Concurrency Architecture for Gordon Phase 3.20.

This module establishes the unified contracts governing:
- concurrency
- execution contexts
- parallelism
- coordination
- synchronization
- structured concurrency
- task groups
- execution ownership
- execution domains
- isolation
- cancellation
- backpressure
- work stealing
- visibility
- fairness
- deadlock prevention

Concurrency is a Core concern. Every subsystem shall use this canonical model.
"""

from dataclasses import dataclass, field
from typing import Protocol, Any, Optional, List, Set, Tuple, Dict, Callable
from enum import Enum, auto
import uuid
import time
import asyncio


# =============================================================================
# CONCURRENCY IDENTITY
# =============================================================================

@dataclass(frozen=True)
class ConcurrencyId:
    """Unique identifier for a concurrency scope or task group."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "ConcurrencyId":
        """Generate a new unique concurrency ID."""
        return cls(value=f"concur_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TaskGroupId:
    """Unique identifier for a task group within a concurrency scope."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "TaskGroupId":
        """Generate a new unique task group ID."""
        return cls(value=f"tg_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConcurrencyEventId:
    """Unique identifier for a concurrency event."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "ConcurrencyEventId":
        """Generate a new unique concurrency event ID."""
        return cls(value=f"concur_event_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# CONCURRENCY STATES
# =============================================================================

class ConcurrencyState(Enum):
    """
    Concurrency scope states.
    
    Every concurrency scope transitions through these states:
        PENDING → (awaiting tasks)
        ACTIVE → (tasks running)
        CANCELLING → (cancellation requested, tasks terminating)
        COMPLETED → (all tasks completed)
        FAILED → (error occurred)
        CANCELLED → (explicitly cancelled)
    """
    
    PENDING = "pending"
    ACTIVE = "active"
    CANCELLING = "cancelling"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionDomain(Enum):
    """Execution domains for canonical concurrency."""
    
    APPLICATION = "application"         # Application-level execution
    RUNTIME = "runtime"                 # Runtime infrastructure
    PROCESS = "process"                 # Process management
    SCHEDULER = "scheduler"             # Scheduler domain
    SERVICE = "service"                 # Service execution
    COMPONENT = "component"             # Component-level execution
    CAPABILITY = "capability"           # Capability invocation
    WORKER = "worker"                   # Worker pool execution
    REQUEST = "request"                 # Request-scoped execution
    TRANSACTION = "transaction"         # Transaction-bound execution
    STREAM = "stream"                   # Stream processing
    SESSION = "session"                 # Session-scoped execution
    TASK = "task"                       # Task-level execution


class CancellationMode(Enum):
    """Cancellation policies."""
    
    COOPERATIVE = "cooperative"         # Tasks check for cancellation
    CASCADE = "cascade"                 # Cancels all child scopes/tasks
    SELECTIVE = "selective"             # Cancel specific tasks/scopes only
    GRACEFUL = "graceful"               # Wait for graceful termination


# =============================================================================
# EXECUTION CONTEXT
# =============================================================================

@dataclass(frozen=True)
class ExecutionContext:
    """
    Immutable context for execution within a concurrency scope.
    
    Args:
        concurrency_id: The concurrency scope this context belongs to
        parent_context_id: ID of parent context (for hierarchy)
        task_group_id: Task group identifier if in a group
        execution_domain: Domain this execution runs in
        timestamp_utc: When this context was created
        properties: Additional key-value properties
    """
    
    concurrency_id: str
    parent_context_id: Optional[str] = None
    task_group_id: Optional[str] = None
    execution_domain: ExecutionDomain = ExecutionDomain.APPLICATION
    timestamp_utc: float = field(default_factory=time.time)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def hierarchy_path(self) -> List[str]:
        """Get the full path from root to this context."""
        path = [self.concurrency_id]
        if self.parent_context_id:
            # In real implementation, would traverse parent chain
            pass
        return path


@dataclass(frozen=True)
class ContextPropagation:
    """
    Defines how execution context propagates through hierarchy.
    
    Properties that propagate to child contexts by default:
        - ownership
        - cancellation policy
        - priority
        - tracing context
        - diagnostic metadata
    
    Some properties must be explicitly propagated (not inherited):
        - execution identity
        - start timestamp
        - specific timeouts
    """
    
    parent_context_id: str
    child_context_id: str
    propagated_properties: Set[str]
    explicit_only_properties: Set[str]


# =============================================================================
# EXECUTION SCOPE & OWNERSHIP
# =============================================================================

@dataclass(frozen=True)
class ExecutionScope:
    """
    Defines an execution scope with ownership and visibility boundaries.
    
    Every concurrent activity exists within exactly one execution scope.
    """
    
    scope_id: ConcurrencyId
    owner_id: str  # Component ID that owns this scope
    domain: ExecutionDomain
    parent_scope_id: Optional[ConcurrencyId] = None
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_root_scope(self) -> bool:
        """Check if this is a root-level execution scope."""
        return self.parent_scope_id is None
    
    @property
    def depth(self) -> int:
        """Get the nesting depth of this scope (root=0)."""
        return 0 if self.is_root_scope else 1


@dataclass(frozen=True)
class ExecutionOwnership:
    """
    Ownership record for an execution scope.
    
    Defines:
        - Who owns this scope
        - What operations are authorized
        - Visibility boundaries
        - Cancellation authority
    """
    
    owner_id: str
    scope_id: ConcurrencyId
    can_cancel: bool = True           # Can cancel scope and children
    can_spawn: bool = True            # Can create child scopes
    can_synchronize: bool = True      # Can use synchronization primitives
    can_coordination: bool = True     # Can use coordination primitives


# =============================================================================
# CANCELLATION TOKENS & PROTOCOLS
# =============================================================================

class CancellationTokenSource:
    """
    Source of cancellation tokens for cooperative cancellation.
    
    This is the canonical mechanism for:
        - Cooperative cancellation (tasks check token)
        - Cascading cancellation (token propagates to children)
        - Selective cancellation (specific tasks can be cancelled)
    
    INVARIANTS:
        - Cancellation is observable (tasks can check)
        - Cancellation is non-blocking (no forced termination)
        - Cancellation propagates hierarchically
        - Cancellation state is immutable once triggered
    """
    
    def __init__(self):
        self._is_cancelled = False
        self._observers: List[Callable[[], None]] = []
        self._timestamp_utc: Optional[float] = None
    
    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._is_cancelled
    
    @property
    def timestamp_utc(self) -> Optional[float]:
        """When cancellation was requested (None if not cancelled)."""
        return self._timestamp_utc
    
    def cancel(self) -> None:
        """Request cancellation. Cannot be undone."""
        if not self._is_cancelled:
            self._is_cancelled = True
            self._timestamp_utc = time.time()
            for observer in self._observers:
                observer()
    
    def add_callback(self, callback: Callable[[], None]) -> None:
        """Add a callback to be invoked when cancelled."""
        if self._is_cancelled:
            # Call immediately if already cancelled
            try:
                callback()
            except Exception:
                pass  # Callback failures are non-fatal
        else:
            self._observers.append(callback)
    
    def throw_if_cancelled(self) -> None:
        """Raise an exception if cancellation has been requested."""
        if self._is_cancelled:
            raise CancellationRequestedError(
                cancelled_at_utc=self._timestamp_utc
            )
    
    def register(self, token: "CancellationToken") -> None:
        """Register this source as the source for a token."""
        # In real implementation, would link tokens together
        pass


class CancellationToken:
    """
    Token representing cancellation state that can be observed.
    
    Tokens are immutable and cannot be cancelled directly.
    Only their source can request cancellation.
    """
    
    def __init__(self, source: CancellationTokenSource):
        self._source = source
    
    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._source.is_cancelled
    
    def throw_if_cancelled(self) -> None:
        """Raise an exception if cancelled."""
        self._source.throw_if_cancelled()
    
    def add_callback(self, callback: Callable[[], None]) -> None:
        """Add a callback for when cancellation occurs."""
        self._source.add_callback(callback)


class CancellationRequestedError(Exception):
    """Raised when a task detects cancellation has been requested."""
    
    def __init__(self, cancelled_at_utc: Optional[float] = None):
        super().__init__("Cancellation was requested")
        self.cancelled_at_utc = cancelled_at_utc


# =============================================================================
# TASK GROUP & STRUCTURED CONCURRENCY
# =============================================================================

@dataclass(frozen=True)
class TaskGroupConfig:
    """
    Configuration for a task group.
    
    Task groups implement structured concurrency - tasks are organized
    in parent-child hierarchies with explicit lifecycle management.
    """
    
    group_id: TaskGroupId
    parent_scope_id: Optional[ConcurrencyId] = None
    cancellation_mode: CancellationMode = CancellationMode.COOPERATIVE
    timeout_seconds: Optional[float] = None
    max_concurrent_tasks: int = 10
    allow_detached_execution: bool = False


class TaskGroup:
    """
    Task group implementing structured concurrency.
    
    Guarantees:
        - All tasks complete before scope exits (or is cancelled)
        - Parent waits for all children to complete
        - Cancellation cascades from parent to children
        - No orphaned tasks remain after scope completes
    
    USAGE PATTERN:
        async with TaskGroup.create(scope_id) as group:
            await group.spawn(task1)
            await group.spawn(task2)
            # Implicitly waits for all tasks when exiting context
    """
    
    def __init__(self, config: TaskGroupConfig):
        self._config = config
        self._task_ids: Set[str] = set()
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Dict[str, Exception] = {}
        self._state = ConcurrencyState.PENDING
        self._source = CancellationTokenSource()
        self._token = CancellationToken(self._source)
    
    @property
    def group_id(self) -> TaskGroupId:
        return self._config.group_id
    
    @property
    def state(self) -> ConcurrencyState:
        return self._state
    
    @property
    def token(self) -> CancellationToken:
        return self._token
    
    @property
    def active_task_count(self) -> int:
        """Number of tasks that haven't completed yet."""
        return len(self._task_ids) - len(self._completed_tasks)
    
    async def spawn(self, task_id: str, task_coro: Any) -> None:
        """
        Spawn a new task in this group.
        
        Args:
            task_id: Unique identifier for the task
            task_coro: Coroutine function to execute
            
        Raises:
            RuntimeError: If group is not active or has completed
        """
        if self._state != ConcurrencyState.ACTIVE:
            raise RuntimeError(f"Cannot spawn task: group state is {self._state}")
        
        if task_id in self._task_ids:
            raise ValueError(f"Task {task_id} already exists in group")
        
        self._task_ids.add(task_id)
        
        # In real implementation, would launch coroutine with cancellation support
        # This is a simplified placeholder for demonstration
    
    async def wait_for_completion(self) -> bool:
        """
        Wait for all tasks in the group to complete.
        
        Returns True if all tasks completed successfully.
        Returns False if cancelled or some tasks failed.
        """
        import asyncio
        
        self._state = ConcurrencyState.ACTIVE
        
        # Wait for timeout if specified
        if self._config.timeout_seconds:
            try:
                await asyncio.wait_for(
                    self._wait_for_tasks(),
                    timeout=self._config.timeout_seconds
                )
            except asyncio.TimeoutError:
                self.cancel()
        
        return (
            self._state == ConcurrencyState.COMPLETED or 
            len(self._failed_tasks) == 0
        )
    
    async def _wait_for_tasks(self) -> None:
        """Internal method to wait for tasks (placeholder)."""
        # In real implementation, would wait on actual task completion events
        await asyncio.sleep(0.1)
    
    def cancel(self) -> None:
        """Request cancellation of all tasks in this group."""
        self._source.cancel()
        if self._state == ConcurrencyState.ACTIVE:
            self._state = ConcurrencyState.CANCELLING
    
    async def __aenter__(self) -> "TaskGroup":
        """Context manager entry - activate the task group."""
        if self._config.parent_scope_id is not None:
            # Inherit cancellation from parent
            pass
        
        self._state = ConcurrencyState.ACTIVE
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - wait for completion or cancel."""
        if exc_type is not None and self._config.cancellation_mode in (
            CancellationMode.CASCADE,
            CancellationMode.GRACEFUL
        ):
            self.cancel()
        
        await self.wait_for_completion()


# =============================================================================
# SYNCHRONIZATION & COORDINATION INTEGRATION
# =============================================================================

@dataclass(frozen=True)
class ConcurrencySynchronizationConfig:
    """
    Configuration for synchronization within a concurrency scope.
    
    Defines how synchronization primitives interact with the concurrency model.
    """
    
    sync_timeout_seconds: Optional[float] = None
    deadlock_detection_enabled: bool = True
    starvation_prevention_enabled: bool = True
    fairness_policy: str = "fifo"  # or "priority", "random"


@dataclass(frozen=True)
class ConcurrencyCoordinationConfig:
    """
    Configuration for coordination within a concurrency scope.
    
    Defines how coordination primitives interact with the concurrency model.
    """
    
    coord_timeout_seconds: Optional[float] = None
    quorum_size: int = 1  # Number of participants needed for coordination


# =============================================================================
# FAIRNESS & RESOURCE MANAGEMENT
# =============================================================================

class FairnessPolicy(Enum):
    """Policies for fair resource allocation."""
    
    FIFO = "fifo"               # First-in, first-out
    PRIORITY = "priority"       # Higher priority first
    ROUND_ROBIN = "round_robin"  # Round-robin among participants
    WEIGHTED_FAIR = "weighted_fair"  # Weighted fair queuing


@dataclass(frozen=True)
class FairnessConfig:
    """
    Configuration for fairness guarantees.
    
    Ensures no participant suffers starvation or deadlock.
    """
    
    policy: FairnessPolicy = FairnessPolicy.FIFO
    max_wait_time_seconds: Optional[float] = None
    priority_inheritance_enabled: bool = True
    detection_enabled: bool = True


# =============================================================================
# VISIBILITY & MEMORY ORDERING
# =============================================================================

class MemoryOrder(Enum):
    """
    Memory ordering guarantees for visibility.
    
    These define what changes are visible to different execution contexts:
        - RELAXED: No ordering guarantees (fastest)
        - ACQUIRE: Synchronizes with release operations
        - RELEASE: Makes writes visible to acquire operations
        - ACQ_REL: Both acquire and release semantics
        - SEQUENTIAL_CONSISTENCY: Total order across all threads
    """
    
    RELAXED = "relaxed"
    ACQUIRE = "acquire"
    RELEASE = "release"
    ACQ_REL = "acq_rel"
    SEQUENTIAL_CONSISTENT = "sequential_consistent"


@dataclass(frozen=True)
class VisibilityContract:
    """
    Contract for visibility guarantees between execution contexts.
    
    Defines what changes are visible when and to whom.
    """
    
    sync_point_id: str
    memory_order: MemoryOrder = MemoryOrder.SEQUENTIAL_CONSISTENT
    visibility_boundary: bool = True  # Clear boundary where visibility is guaranteed


# =============================================================================
# DEADLOCK & Livelock PREVENTION
# =============================================================================

class DeadlockPrevention(Enum):
    """Strategies for deadlock prevention."""
    
    NONE = "none"                     # No prevention (unsafe)
    TIMEOUT = "timeout"               # Use timeouts on all operations
    WAIT_DIE = "wait_die"             # Wait-die wound-wait scheme
    WOUND_WAIT = "wound_wait"         # Wound-wait scheme
    DEADLOCK_DETECTION = "detection"  # Periodic detection and resolution


class LivelockPrevention(Enum):
    """Strategies for livelock prevention."""
    
    NONE = "none"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    JITTER = "jitter"
    BACKPRESSURE = "backpressure"


@dataclass(frozen=True)
class DeadlockPreventionConfig:
    """
    Configuration for deadlock prevention.
    """
    
    strategy: DeadlockPrevention = DeadlockPrevention.DETECTION
    detection_interval_seconds: float = 1.0
    max_wait_time_seconds: Optional[float] = None


@dataclass(frozen=True)
class LivelockPreventionConfig:
    """
    Configuration for livelock prevention.
    """
    
    strategy: LivelockPrevention = LivelockPrevention.EXPONENTIAL_BACKOFF
    initial_delay_seconds: float = 0.1
    max_delay_seconds: float = 60.0


# =============================================================================
# BACKPRESSURE & FLOW CONTROL
# =============================================================================

@dataclass(frozen=True)
class BackpressureConfig:
    """
    Configuration for backpressure control.
    
    Prevents producers from overwhelming consumers by regulating flow.
    """
    
    enabled: bool = True
    max_queue_size: int = 1000
    producer_throttle_threshold: float = 0.8  # 80% capacity triggers throttling
    consumer_throttle_threshold: float = 0.2  # 20% capacity signals demand


# =============================================================================
# WORKER & EXECUTOR CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class WorkerPoolConfig:
    """
    Configuration for worker pools.
    
    Defines how workers are managed and tasks are distributed.
    """
    
    pool_id: str
    min_workers: int = 1
    max_workers: int = 100
    task_queue_size: int = 1000
    allow_work_stealing: bool = True
    fair_scheduling: bool = True


class ExecutorType(Enum):
    """Types of executors in the canonical model."""
    
    COOPERATIVE = "cooperative"        # Cooperative multitasking (async/await)
    DEDICATED = "dedicated"            # Dedicated threads per task
    ISOLATED = "isolated"              # Fully isolated execution contexts
    SHARED = "shared"                  # Shared thread pool


@dataclass(frozen=True)
class ExecutorConfig:
    """
    Configuration for executors.
    """
    
    executor_id: str
    executor_type: ExecutorType = ExecutorType.COOPERATIVE
    max_concurrent_tasks: int = 10
    task_timeout_seconds: Optional[float] = None


# =============================================================================
# OBSERVABILITY & DIAGNOSTICS
# =============================================================================

@dataclass(frozen=True)
class ConcurrencyEvent:
    """
    Event in the concurrency observability stream.
    
    Every significant concurrency operation emits events for diagnostics.
    """
    
    event_id: ConcurrencyEventId
    concurrency_id: Optional[ConcurrencyId] = None
    timestamp_utc: float = field(default_factory=time.time)
    event_type: str  # "SCOPE_CREATED", "TASK_STARTED", "CANCELLED", etc.
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_replayable(self) -> bool:
        """Events are replayable if they contain deterministic data."""
        return True


@dataclass(frozen=True)
class ConcurrencyDiagnostic:
    """
    Diagnostic information about concurrency state.
    """
    
    concurrency_id: Optional[ConcurrencyId] = None
    timestamp_utc: float = field(default_factory=time.time)
    active_scope_count: int = 0
    active_task_count: int = 0
    cancelled_tasks_count: int = 0
    deadlock_detected: bool = False
    starvation_detected: bool = False


# =============================================================================
# CONCURRENCY PRIMITIVES PROTOCOLS
# =============================================================================

class ConcurrencyPrimitive(Protocol):
    """Base protocol for all concurrency primitives."""
    
    @property
    def concurrency_id(self) -> ConcurrencyId:
        ...
    
    @property
    def state(self) -> ConcurrencyState:
        ...
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        ...
    
    async def signal(self) -> None:
        ...
    
    async def cancel(self) -> None:
        ...


# =============================================================================
# FACTORY FOR CONCURRENCY PRIMITIVES
# =============================================================================

class ConcurrencyPrimitiveFactory:
    """
    Factory for creating canonical concurrency primitives.
    
    Ensures consistent primitive creation and proper ID generation.
    """
    
    def __init__(self):
        self._scopes: Dict[ConcurrencyId, "ConcurrencyScope"] = {}
    
    def create_scope(
        self,
        owner_id: str,
        domain: ExecutionDomain = ExecutionDomain.APPLICATION
    ) -> "ConcurrencyScope":
        """Create a new execution scope."""
        scope_id = ConcurrencyId.generate()
        config = ConcurrencySynchronizationConfig()
        coord_config = ConcurrencyCoordinationConfig()
        
        scope = ConcurrencyScope(
            scope_id=scope_id,
            owner_id=owner_id,
            domain=domain,
            sync_config=config,
            coord_config=coord_config
        )
        self._scopes[scope_id] = scope
        return scope
    
    def create_task_group(
        self,
        parent_scope_id: Optional[ConcurrencyId] = None,
        cancellation_mode: CancellationMode = CancellationMode.COOPERATIVE
    ) -> TaskGroup:
        """Create a new task group within a scope."""
        config = TaskGroupConfig(
            group_id=TaskGroupId.generate(),
            parent_scope_id=parent_scope_id,
            cancellation_mode=cancellation_mode
        )
        return TaskGroup(config)


# =============================================================================
# CONCURRENCY SCOPE (EXECUTION CONTEXT)
# =============================================================================

class ConcurrencyScope:
    """
    Execution scope that governs concurrent execution.
    
    Every concurrent activity belongs to exactly one concurrency scope.
    Scopes form a hierarchy with explicit parent-child relationships.
    """
    
    def __init__(
        self,
        scope_id: ConcurrencyId,
        owner_id: str,
        domain: ExecutionDomain = ExecutionDomain.APPLICATION,
        parent_scope_id: Optional[ConcurrencyId] = None,
        sync_config: Optional[ConcurrencySynchronizationConfig] = None,
        coord_config: Optional[ConcurrencyCoordinationConfig] = None
    ):
        self._scope_id = scope_id
        self._owner_id = owner_id
        self._domain = domain
        self._parent_scope_id = parent_scope_id
        self._sync_config = sync_config or ConcurrencySynchronizationConfig()
        self._coord_config = coord_config or ConcurrencyCoordinationConfig()
        
        self._task_groups: Dict[TaskGroupId, TaskGroup] = {}
        self._state = ConcurrencyState.PENDING
        self._source = CancellationTokenSource()
        self._token = CancellationToken(self._source)
        self._created_at_utc = time.time()
    
    @property
    def scope_id(self) -> ConcurrencyId:
        return self._scope_id
    
    @property
    def owner_id(self) -> str:
        return self._owner_id
    
    @property
    def domain(self) -> ExecutionDomain:
        return self._domain
    
    @property
    def state(self) -> ConcurrencyState:
        return self._state
    
    @property
    def token(self) -> CancellationToken:
        return self._token
    
    @property
    def parent_scope_id(self) -> Optional[ConcurrencyId]:
        return self._parent_scope_id
    
    async def spawn_task_group(
        self,
        cancellation_mode: CancellationMode = CancellationMode.COOPERATIVE
    ) -> TaskGroup:
        """
        Spawn a new task group within this scope.
        
        The spawned group inherits properties from its parent scope.
        """
        if self._state == ConcurrencyState.COMPLETED:
            raise RuntimeError("Cannot spawn task group: scope is completed")
        
        if self._state == ConcurrencyState.CANCELLED:
            raise RuntimeError("Cannot spawn task group: scope is cancelled")
        
        config = TaskGroupConfig(
            group_id=TaskGroupId.generate(),
            parent_scope_id=self._scope_id,
            cancellation_mode=cancellation_mode
        )
        group = TaskGroup(config)
        self._task_groups[group.group_id] = group
        
        # Propagate cancellation to new group
        if self._state == ConcurrencyState.CANCELLING:
            group.cancel()
        
        return group
    
    def cancel(self) -> None:
        """Request cancellation of this scope and all child groups."""
        self._source.cancel()
        if self._state == ConcurrencyState.ACTIVE:
            self._state = ConcurrencyState.CANCELLING
        
        # Cancel all task groups
        for group in self._task_groups.values():
            group.cancel()
    
    async def wait_for_completion(self) -> bool:
        """
        Wait for this scope and all task groups to complete.
        
        Returns True if completed successfully, False otherwise.
        """
        import asyncio
        
        if self._state == ConcurrencyState.ACTIVE:
            # Wait for any active task groups
            if self._task_groups:
                wait_tasks = [
                    group.wait_for_completion()
                    for group in self._task_groups.values()
                ]
                await asyncio.gather(*wait_tasks, return_exceptions=True)
        
        if self._state == ConcurrencyState.CANCELLING:
            self._state = ConcurrencyState.CANCELLED
        
        if len(self._task_groups) > 0 and all(
            group.state in (ConcurrencyState.COMPLETED, ConcurrencyState.CANCELLED)
            for group in self._task_groups.values()
        ):
            self._state = ConcurrencyState.COMPLETED
        elif self._state != ConcurrencyState.CANCELLED:
            self._state = ConcurrencyState.FAILED
        
        return (
            self._state == ConcurrencyState.COMPLETED and
            all(
                group.state in (ConcurrencyState.COMPLETED, ConcurrencyState.CANCELLED)
                for group in self._task_groups.values()
            )
        )
    
    async def __aenter__(self) -> "ConcurrencyScope":
        """Context manager entry - activate the scope."""
        if self._state == ConcurrencyState.PENDING:
            self._state = ConcurrencyState.ACTIVE
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - wait for completion or cancel."""
        if exc_type is not None and self._sync_config.deadlock_detection_enabled:
            # Handle exception with cancellation
            pass
        
        await self.wait_for_completion()


__all__ = [
    # Identity
    "ConcurrencyId",
    "TaskGroupId",
    "ConcurrencyEventId",
    
    # States and domains
    "ConcurrencyState",
    "ExecutionDomain",
    "CancellationMode",
    
    # Context and ownership
    "ExecutionContext",
    "ContextPropagation",
    "ExecutionScope",
    "ExecutionOwnership",
    
    # Cancellation
    "CancellationTokenSource",
    "CancellationToken",
    "CancellationRequestedError",
    
    # Structured concurrency
    "TaskGroupConfig",
    "TaskGroup",
    
    # Integration configs
    "ConcurrencySynchronizationConfig",
    "ConcurrencyCoordinationConfig",
    
    # Fairness
    "FairnessPolicy",
    "FairnessConfig",
    
    # Visibility
    "MemoryOrder",
    "VisibilityContract",
    
    # Prevention
    "DeadlockPrevention",
    "LivelockPrevention",
    "DeadlockPreventionConfig",
    "LivelockPreventionConfig",
    
    # Backpressure
    "BackpressureConfig",
    
    # Workers and executors
    "WorkerPoolConfig",
    "ExecutorType",
    "ExecutorConfig",
    
    # Observability
    "ConcurrencyEvent",
    "ConcurrencyDiagnostic",
    
    # Protocols and factories
    "ConcurrencyPrimitive",
    "ConcurrencyPrimitiveFactory",
    "ConcurrencyScope",
]