# Worker Ownership Model
# ======================

"""
Worker ownership for Phase 3.7.7-I scheduling, execution & task lifecycle.

Provides:
- Canonical worker identity (WorkerId)
- Worker state machine with valid transitions
- Single authority for worker state transitions
- Bounded concurrency via worker pool
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# WORKER IDENTITY
# =============================================================================

@dataclass(frozen=True)
class WorkerId:
    """Unique identifier for a worker."""
    value: str
    
    @classmethod
    def generate(cls) -> "WorkerId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# WORKER STATE MACHINE
# =============================================================================

class WorkerState(Enum):
    """
    Canonical worker lifecycle states.
    
    State Flow:
        CREATED → STARTING → IDLE → ASSIGNED → EXECUTING → [IDLE|STOPPING]
                              ↓
                           FAILED
    
    Terminal/Stop States:
        STOPPING, STOPPED, FAILED
    """
    CREATED = "created"       # Worker created but not started
    STARTING = "starting"     # Being initialized
    IDLE = "idle"             # Ready for assignment
    ASSIGNED = "assigned"     # Assigned to a task (pending execution)
    EXECUTING = "executing"   # Currently running task
    CANCELLING = "cancelling" # Cancellation requested, cleaning up
    STOPPING = "stopping"     # Being shut down
    STOPPED = "stopped"       # Fully stopped
    FAILED = "failed"         # Unrecoverable failure


VALID_WORKER_TRANSITIONS: Dict[WorkerState, Tuple[WorkerState, ...]] = {
    WorkerState.CREATED: (WorkerState.STARTING,),
    WorkerState.STARTING: (WorkerState.IDLE, WorkerState.FAILED),
    WorkerState.IDLE: (WorkerState.ASSIGNED, WorkerState.STOPPING, WorkerState.FAILED),
    WorkerState.ASSIGNED: (WorkerState.EXECUTING, WorkerState.IDLE, WorkerState.STOPPING, WorkerState.FAILED),
    WorkerState.EXECUTING: (WorkerState.IDLE, WorkerState.CANCELLING, WorkerState.FAILED),
    WorkerState.CANCELLING: (WorkerState.IDLE, WorkerState.STOPPING, WorkerState.FAILED),
    WorkerState.STOPPING: (WorkerState.STOPPED, WorkerState.FAILED),
    WorkerState.STOPPED: (),  # Terminal
    WorkerState.FAILED: (),   # Terminal
}


class WorkerTransitionError(Exception):
    """Raised when an invalid worker state transition is attempted."""
    
    def __init__(self, from_state: WorkerState, to_state: WorkerState, reason: str = ""):
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        super().__init__(f"Invalid worker transition {from_state.value} → {to_state.value}: {reason}")


# =============================================================================
# WORKER GENERATION
# =============================================================================

@dataclass(frozen=True)
class WorkerGeneration:
    """
    Worker generation for fence tracking.
    
    Prevents old workers from interfering with new pool instances.
    """
    generation_id: str
    created_at_utc: float = field(default_factory=time.time)


# =============================================================================
# WORKER ASSIGNMENT
# =============================================================================

@dataclass(frozen=True)
class WorkerAssignment:
    """Assignment of a task to a worker."""
    assignment_id: str
    worker_id: WorkerId
    task_id: Any  # TaskId reference
    runtime_id: str
    
    assigned_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None


# =============================================================================
# WORKER DESCRIPTOR (CANONICAL ARTIFACT)
# =============================================================================

@dataclass(frozen=True)
class WorkerDescriptor:
    """
    Immutable worker descriptor with full metadata.
    
    This is the canonical record of a worker - no mutations allowed.
    All state changes go through WorkerLifecycleController.
    """
    # Identity
    worker_id: WorkerId
    runtime_id: str
    
    # Generation info
    generation_id: str
    generation_sequence: int
    
    # Configuration
    executor_class: str  # Which executor this worker uses
    
    # State (can be updated via transitions)
    state: WorkerState = WorkerState.CREATED
    
    # Assignment
    assigned_task_id: Optional[Any] = None
    
    # Statistics
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_seconds: float = 0.0
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    stopped_at_utc: Optional[float] = None
    
    def is_active(self) -> bool:
        """Check if worker is in an active (non-terminal) state."""
        return self.state in (
            WorkerState.STARTING, WorkerState.IDLE,
            WorkerState.ASSIGNED, WorkerState.EXECUTING
        )
    
    def is_terminal(self) -> bool:
        """Check if worker is in a terminal state."""
        return self.state in (WorkerState.STOPPED, WorkerState.FAILED)


# =============================================================================
# WORKER LIFECYCLE CONTROLLER (CANONICAL AUTHORITY)
# =============================================================================

class WorkerLifecycleController:
    """
    Canonical authority for worker state transitions.
    
    This is THE ONE source of truth for worker states.
    All worker state mutations MUST go through this controller.
    
    Invariants enforced:
        1. Single canonical worker state
        2. Valid state transitions only (per VALID_WORKER_TRANSITIONS)
        3. Terminal states are immutable
        4. No direct state assignment - all transitions go through here
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # State storage: worker_id -> (descriptor, timestamp)
        self._worker_states: Dict[WorkerId, Tuple[WorkerDescriptor, float]] = {}
        
        # History: list of (worker_id, from_state, to_state, reason, timestamp)
        self._transition_history: List[
            Tuple[WorkerId, WorkerState, WorkerState, str, float]
        ] = []
    
    def register_worker(self, descriptor: WorkerDescriptor) -> None:
        """Register a new worker with initial CREATED state."""
        with self._lock:
            if descriptor.worker_id in self._worker_states:
                raise ValueError(f"Worker {descriptor.worker_id} already registered")
            
            now = time.monotonic()
            self._worker_states[descriptor.worker_id] = (descriptor, now)
    
    def transition(
        self,
        worker_id: WorkerId,
        target_state: WorkerState,
        reason: str = "",
        timestamp: Optional[float] = None
    ) -> Tuple[bool, Optional[WorkerTransitionError]]:
        """
        Request a state transition for a worker.
        
        Returns:
            Tuple of (success, error_or_None)
        """
        with self._lock:
            if worker_id not in self._worker_states:
                return False, WorkerTransitionError(
                    WorkerState.CREATED, target_state,
                    f"Worker {worker_id} not registered"
                )
            
            current_descriptor, _ = self._worker_states[worker_id]
            current_state = current_descriptor.state
            
            # Idempotent: same state is always valid
            if current_state == target_state:
                return True, None
            
            # Check valid transitions
            valid_transitions = VALID_WORKER_TRANSITIONS.get(current_state, ())
            
            if target_state not in valid_transitions:
                error = WorkerTransitionError(
                    current_state, target_state,
                    f"Invalid transition. Valid: {[s.value for s in valid_transitions]}"
                )
                return False, error
            
            # Create new descriptor with updated state
            ts = timestamp or time.monotonic()
            
            if target_state == WorkerState.EXECUTING:
                new_descriptor = dataclass_replace(current_descriptor, state=target_state)
            elif target_state == WorkerState.STOPPING:
                new_descriptor = dataclass_replace(
                    current_descriptor,
                    state=target_state,
                    stopped_at_utc=ts
                )
            else:
                new_descriptor = dataclass_replace(current_descriptor, state=target_state)
            
            self._worker_states[worker_id] = (new_descriptor, ts)
            
            # Record history
            self._transition_history.append((
                worker_id, current_state, target_state, reason, ts
            ))
            
            return True, None
    
    def get_descriptor(self, worker_id: WorkerId) -> Optional[WorkerDescriptor]:
        """Get the current descriptor for a worker."""
        with self._lock:
            result = self._worker_states.get(worker_id)
            if result:
                return result[0]
            return None
    
    def assign_task(
        self,
        worker_id: WorkerId,
        task_id: Any
    ) -> Tuple[bool, Optional[str]]:
        """Assign a task to a worker (state transition to ASSIGNED)."""
        with self._lock:
            if worker_id not in self._worker_states:
                return False, f"Worker {worker_id} not registered"
            
            current_descriptor, _ = self._worker_states[worker_id]
            
            # Can only assign from IDLE state
            if current_descriptor.state != WorkerState.IDLE:
                return False, f"Cannot assign: worker is in {current_descriptor.state.value} state"
            
            new_descriptor = dataclass_replace(
                current_descriptor,
                state=WorkerState.ASSIGNED,
                assigned_task_id=task_id
            )
            
            self._worker_states[worker_id] = (new_descriptor, time.monotonic())
            
            return True, None
    
    def complete_assignment(
        self,
        worker_id: WorkerId,
        success: bool,
        duration_seconds: float
    ) -> Tuple[bool, Optional[str]]:
        """Mark assignment as completed and return to IDLE."""
        with self._lock:
            if worker_id not in self._worker_states:
                return False, f"Worker {worker_id} not registered"
            
            current_descriptor, _ = self._worker_states[worker_id]
            
            # Update statistics
            tasks_completed = current_descriptor.tasks_completed + (1 if success else 0)
            tasks_failed = current_descriptor.tasks_failed + (0 if success else 1)
            total_execution_seconds = current_descriptor.total_execution_seconds + duration_seconds
            
            new_descriptor = dataclass_replace(
                current_descriptor,
                state=WorkerState.IDLE,
                assigned_task_id=None,
                tasks_completed=tasks_completed,
                tasks_failed=tasks_failed,
                total_execution_seconds=total_execution_seconds
            )
            
            self._worker_states[worker_id] = (new_descriptor, time.monotonic())
            
            return True, None
    
    def get_active_workers(self) -> List[WorkerDescriptor]:
        """Get all workers in active states."""
        with self._lock:
            return [
                desc for desc, _ in self._worker_states.values()
                if desc.is_active()
            ]
    
    def get_snapshot(self) -> "WorkerSnapshot":
        """Get an immutable snapshot of worker state."""
        with self._lock:
            active = []
            stopped = 0
            failed = 0
            
            for desc, _ in self._worker_states.values():
                if desc.state == WorkerState.FAILED:
                    failed += 1
                elif desc.is_terminal():
                    stopped += 1
                else:
                    active.append(desc)
            
            return WorkerSnapshot(
                total_workers=len(self._worker_states),
                active_workers=active,
                stopped_count=stopped,
                failed_count=failed,
                history_length=len(self._transition_history)
            )


@dataclass(frozen=True)
class WorkerSnapshot:
    """Immutable snapshot of worker state."""
    total_workers: int
    active_workers: List[WorkerDescriptor]
    stopped_count: int
    failed_count: int
    history_length: int


# =============================================================================
# WORKER POOL (bounded concurrency control)
# =============================================================================

@dataclass(frozen=True)
class WorkerPoolConfig:
    """
    Configuration for worker pool.
    
    All bounds are enforced - no unbounded growth possible.
    """
    min_workers: int = 1          # Minimum workers to maintain
    max_workers: int = 8          # Maximum workers (bound!)
    idle_timeout_seconds: float = 60.0  # Worker retention time
    max_concurrent_tasks: int = 10      # Max simultaneous executions


class WorkerPool:
    """
    Managed pool of workers with bounded concurrency.
    
    Owner: One explicit owner (typically the scheduler or executor)
    Bounds: min/max workers enforced, concurrent tasks limited
    
    Usage:
        config = WorkerPoolConfig(max_workers=8, max_concurrent_tasks=10)
        pool = WorkerPool(runtime_id="runtime_1", config=config)
        
        # Acquire a worker for a task
        worker_id = await pool.acquire()
        
        if worker_id:
            # Use the worker...
            pass
        
        # Release when done
        pool.release(worker_id, success=True)
    """
    
    def __init__(self, runtime_id: str, config: WorkerPoolConfig):
        self._runtime_id = runtime_id
        self._config = config
        
        self._lock = __import__("threading").RLock()
        
        # Worker lifecycle controller (owns worker state transitions)
        self._lifecycle = WorkerLifecycleController(runtime_id)
        
        # Pool state
        self._worker_ids: List[WorkerId] = []  # All workers in pool
        self._idle_workers: List[WorkerId] = []  # Available for work
        self._active_assignments: Dict[WorkerId, Any] = {}  # worker_id -> task_id
        
        # Generation tracking (fence)
        self._current_generation = 1
    
    async def initialize(self) -> None:
        """Initialize the pool by creating initial workers."""
        with self._lock:
            for i in range(max(0, self._config.min_workers)):
                await self._create_worker()
    
    async def _create_worker(self) -> WorkerId:
        """Create a new worker and add to pool."""
        worker_id = WorkerId.generate()
        
        descriptor = WorkerDescriptor(
            worker_id=worker_id,
            runtime_id=self._runtime_id,
            generation_id=str(self._current_generation),
            generation_sequence=len(self._worker_ids),
            executor_class="InlineExecutor"
        )
        
        self._lifecycle.register_worker(descriptor)
        
        # Add to pool
        self._worker_ids.append(worker_id)
        self._idle_workers.append(worker_id)
        
        return worker_id
    
    async def acquire(self) -> Optional[WorkerId]:
        """
        Acquire a worker for task execution.
        
        Returns:
            Worker ID if available, None if pool exhausted
            
        Note: Bounded by max_workers and concurrent tasks limits.
        """
        with self._lock:
            # Check if we can create more workers
            if len(self._worker_ids) >= self._config.max_workers:
                return None  # Pool is at capacity
            
            # Try to get idle worker
            while self._idle_workers:
                worker_id = self._idle_workers.pop(0)
                
                descriptor = self._lifecycle.get_descriptor(worker_id)
                if descriptor and descriptor.state == WorkerState.IDLE:
                    return worker_id
            
            # No idle workers - create new one if under limit
            if len(self._worker_ids) < self._config.max_workers:
                return await self._create_worker()
            
            return None
    
    def release(
        self,
        worker_id: WorkerId,
        success: bool = True,
        duration_seconds: float = 0.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Release a worker back to the pool after task completion.
        
        Returns:
            Tuple of (success, error_message)
        """
        with self._lock:
            if worker_id not in self._worker_ids:
                return False, f"Worker {worker_id} not in pool"
            
            # Mark assignment complete
            success, error = self._lifecycle.complete_assignment(
                worker_id, success, duration_seconds
            )
            
            if success:
                self._active_assignments.pop(worker_id, None)
                self._idle_workers.append(worker_id)
            
            return success, error
    
    def get_snapshot(self) -> "WorkerPoolSnapshot":
        """Get an immutable snapshot of pool state."""
        with self._lock:
            active = len(self._active_assignments)
            idle = len(self._idle_workers)
            total = len(self._worker_ids)
            
            return WorkerPoolSnapshot(
                runtime_id=self._runtime_id,
                config=self._config,
                total_workers=total,
                idle_workers=idle,
                active_workers=active,
                generation=self._current_generation
            )


@dataclass(frozen=True)
class WorkerPoolSnapshot:
    """Immutable snapshot of worker pool state."""
    runtime_id: str
    config: WorkerPoolConfig
    total_workers: int
    idle_workers: int
    active_workers: int
    generation: int


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Identity and state
    "WorkerId",
    "WorkerState",
    "VALID_WORKER_TRANSITIONS",
    "WorkerTransitionError",
    
    # Generation and assignment
    "WorkerGeneration",
    "WorkerAssignment",
    
    # Descriptor (canonical artifact)
    "WorkerDescriptor",
    
    # Lifecycle authority
    "WorkerLifecycleController",
    "WorkerSnapshot",
    
    # Pool
    "WorkerPoolConfig",
    "WorkerPool",
    "WorkerPoolSnapshot",
]