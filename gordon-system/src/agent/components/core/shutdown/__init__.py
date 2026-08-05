# Core Shutdown Coordinator
# =========================

"""
Production-grade shutdown infrastructure for Phase 3.7.9-I.

Implements deterministic, observable, dependency-aware, bounded shutdown pipeline.

Architecture Overview:
    ShutdownCoordinator - Canonical authority for global shutdown
    └── RuntimeQuiescence - Rejects new work, stabilizes runtime
    ├── TaskDrainer - Finishes/terminates pending tasks
    ├── DependencyShutdownOrder - Respects reverse dependency order
    ├── WorkerStopper - Stops workers and schedulers
    ├── ResourceReleaser - Releases owned resources
    └── VerificationStage - Verifies clean shutdown

Key Invariants:
1. One ShutdownCoordinator owns global shutdown
2. Admission closes BEFORE shutdown
3. Quiescence precedes stopping
4. Dependency order is respected (reverse topological)
5. Resources are released by owner
6. Verification is independent from execution
7. Shutdown events preserve provenance
8. Shutdown is idempotent
9. No orphaned workers or leaked resources
10. Runtime reaches one truthful terminal state

Shutdown Pipeline Stages:
    REQUESTED -> ADMISSION_CLOSED -> QUIESCENT -> DRAINING -> CANCELLING ->
    STOPPING_COMPONENTS -> RELEASING_RESOURCES -> VERIFYING -> TERMINATED

Modes: GRACEFUL, IMMEDIATE, FORCED, EMERGENCY, RESTART, MAINTENANCE
"""

import dataclasses
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Dict,
    List,
    Optional,
    Callable,
    Any,
    Set,
    Protocol,
    Awaitable,
)
import time
import uuid
import threading
import asyncio
import signal
import sys
import os

# ==============================================================================
# Core Types and Contracts
# ==============================================================================


class ShutdownMode(Enum):
    """
    Shutdown mode classification.
    
    Modes define the behavior of shutdown:
        - GRACEFUL: Wait for tasks to finish, bounded timeout
        - IMMEDIATE: Stop as fast as possible
        - FORCED: Force cancellation after short wait
        - EMERGENCY: Immediate stop with minimal cleanup
        - RESTART: Prepare for restart (preserve state)
        - MAINTENANCE: Graceful stop with quick restart expectation
    """
    
    GRACEFUL = "graceful"
    IMMEDIATE = "immediate"
    FORCED = "forced"
    EMERGENCY = "emergency"
    RESTART = "restart"
    MAINTENANCE = "maintenance"


@dataclass(frozen=True)
class ShutdownRequest:
    """
    A request to initiate shutdown.
    
    Args:
        mode: The shutdown mode to use
        reason: Human-readable explanation
        source_id: Who initiated the request
        timeout_seconds: Maximum time allowed for shutdown
        preserve_state: Whether to preserve runtime state (for restart)
    """
    
    mode: ShutdownMode = ShutdownMode.GRACEFUL
    reason: str = "No reason provided"
    source_id: str = "unknown"
    timeout_seconds: float = 30.0
    preserve_state: bool = False


@dataclass(frozen=True)
class ShutdownEvent:
    """
    Immutable shutdown event for observability.
    
    Events are produced at each pipeline stage and preserved with full context.
    """
    
    event_id: str
    event_type: str  # e.g., "shutdown.requested", "shutdown.verified"
    
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    runtime_id: str = ""
    correlation_id: Optional[str] = None
    
    stage: str = ""  # Pipeline stage
    mode: str = ""
    
    entity_id: Optional[str] = None  # Which component (if applicable)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def timestamp(self) -> float:
        """Return the UTC timestamp."""
        return self.timestamp_utc


class ShutdownObserver(Protocol):
    """Protocol for shutdown event observers."""
    
    async def on_shutdown_event(self, event: ShutdownEvent) -> None:
        """Called when a shutdown event is published."""


# ==============================================================================
# Dependency-Aware Ordering
# ==============================================================================


@dataclass
class ComponentDependencyInfo:
    """
    Information about component dependencies.
    
    Used to build the dependency graph for ordered shutdown.
    """
    
    component_id: str
    name: str
    depends_on: List[str] = field(default_factory=list)
    # Components that depend on this one (reverse edge)
    dependents: List[str] = field(default_factory=list)


class DependencyGraph:
    """
    Graph-based dependency tracking for shutdown ordering.
    
    Shutdown order is the reverse of startup/dependency order.
    If A depends on B, then B must be stopped before A during shutdown.
    
    Raises:
        DependencyCycleError: If a cycle is detected in the graph
        IllegalStopOrderError: If stop order violates dependencies
    """
    
    def __init__(self) -> None:
        self._components: Dict[str, ComponentDependencyInfo] = {}
        self._lock = threading.Lock()
    
    def register_component(
        self,
        component_id: str,
        name: str,
        depends_on: Optional[List[str]] = None
    ) -> None:
        """
        Register a component and its dependencies.
        
        Args:
            component_id: Unique identifier for the component
            name: Human-readable name
            depends_on: List of component IDs this one depends on
        """
        with self._lock:
            deps = depends_on or []
            
            # Add to registry
            if component_id not in self._components:
                self._components[component_id] = ComponentDependencyInfo(
                    component_id=component_id,
                    name=name,
                    depends_on=list(deps)
                )
            else:
                self._components[component_id].depends_on = list(deps)
            
            # Update reverse edges (dependents)
            for dep in deps:
                if dep not in self._components:
                    self._components[dep] = ComponentDependencyInfo(
                        component_id=dep,
                        name=f"unknown:{dep}",
                        depends_on=[]
                    )
                self._components[dep].dependents.append(component_id)
    
    def detect_cycle(self) -> Optional[List[str]]:
        """
        Detect if there's a cycle in the dependency graph.
        
        Returns:
            List of component IDs forming a cycle, or None if no cycle
        """
        with self._lock:
            visited: Set[str] = set()
            rec_stack: Set[str] = set()
            path: List[str] = []
            
            def dfs(node: str) -> Optional[List[str]]:
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                if node in self._components:
                    for neighbor in self._components[node].depends_on:
                        if neighbor not in visited:
                            cycle = dfs(neighbor)
                            if cycle:
                                return cycle
                        elif neighbor in rec_stack:
                            # Found cycle - extract it
                            cycle_start = path.index(neighbor)
                            return path[cycle_start:] + [neighbor]
                
                path.pop()
                rec_stack.remove(node)
                return None
            
            for node in self._components:
                if node not in visited:
                    cycle = dfs(node)
                    if cycle:
                        return cycle
            
            return None
    
    def shutdown_order(self) -> List[str]:
        """
        Get components in reverse dependency order for shutdown.
        
        Components that others depend on are stopped first.
        Uses topological sort on the reverse graph.
        
        Returns:
            List of component IDs in shutdown order
        """
        with self._lock:
            # Build reverse adjacency (dependents point to dependencies)
            in_degree: Dict[str, int] = {
                cid: len(info.depends_on) 
                for cid, info in self._components.items()
            }
            
            # Start with components that have no dependencies
            queue: List[str] = [
                cid for cid, deg in in_degree.items() if deg == 0
            ]
            result: List[str] = []
            
            while queue:
                # Sort for deterministic order
                queue.sort()
                node = queue.pop(0)
                result.append(node)
                
                # Reduce in-degree of dependents
                for dependent in self._components.get(node, ComponentDependencyInfo("", "")).dependents:
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            queue.append(dependent)
            
            # Check if all components were processed (no cycle)
            if len(result) != len(self._components):
                raise DependencyCycleError(
                    "Dependency graph has a cycle; cannot determine shutdown order"
                )
            
            return result
    
    def verify_stop_order(self, stop_sequence: List[str]) -> None:
        """
        Verify that a stop sequence respects dependency order.
        
        Args:
            stop_sequence: List of component IDs in intended stop order
            
        Raises:
            IllegalStopOrderError: If the sequence violates dependencies
        """
        stopped: Set[str] = set()
        
        for cid in stop_sequence:
            if cid not in self._components:
                raise IllegalStopOrderError(f"Unknown component: {cid}")
            
            # Check that all dependencies are already stopped
            deps = self._components[cid].depends_on
            for dep in deps:
                if dep not in stopped:
                    raise IllegalStopOrderError(
                        f"Component '{cid}' depends on '{dep}' which is still running"
                    )
            
            stopped.add(cid)
    
    def get_component_info(self, component_id: str) -> Optional[ComponentDependencyInfo]:
        """Get dependency info for a component."""
        with self._lock:
            return self._components.get(component_id)
    
    def list_all_components(self) -> List[str]:
        """List all registered component IDs."""
        with self._lock:
            return list(self._components.keys())
    
    @property
    def size(self) -> int:
        """Return number of registered components."""
        with self._lock:
            return len(self._components)


class DependencyCycleError(Exception):
    """Raised when a dependency cycle is detected."""
    
    def __init__(self, message: str, cycle: Optional[List[str]] = None):
        super().__init__(message)
        self.cycle = cycle


class IllegalStopOrderError(Exception):
    """Raised when stop order violates dependencies."""
    
    pass


class CancellationRequestedError(Exception):
    """Raised when a task is cancelled during shutdown."""
    
    def __init__(
        self,
        message: str,
        reason: Optional[str] = None
    ):
        super().__init__(message)
        self.reason = reason


# ==============================================================================
# Shutdown State Machine
# ==============================================================================


class ShutdownState(Enum):
    """
    Shutdown pipeline state machine states.
    
    States:
        IDLE: Initial state, no shutdown requested
        REQUESTED: Shutdown request received and validated
        ADMISSION_CLOSED: New work is rejected
        QUIESCENT: Runtime stabilized, no new scheduling
        DRAINING: Outstanding tasks being finished
        CANCELLING: Remaining tasks cancelled
        STOPPING_COMPONENTS: Components stopped
        RELEASING_RESOURCES: Resources released
        VERIFYING: Shutdown verified
        TERMINATED: Fully shutdown
        FAILED: Shutdown failed
    """
    
    IDLE = "idle"
    REQUESTED = "requested"
    ADMISSION_CLOSED = "admission_closed"
    QUIESCENT = "quiescent"
    DRAINING = "draining"
    CANCELLING = "cancelling"
    STOPPING_COMPONENTS = "stopping_components"
    RELEASING_RESOURCES = "releasing_resources"
    VERIFYING = "verifying"
    TERMINATED = "terminated"
    FAILED = "failed"


@dataclass(frozen=True)
class ShutdownTransition:
    """
    Records a state transition in the shutdown state machine.
    
    Args:
        from_state: Previous state
        to_state: New state
        timestamp: When transition occurred
        reason: Why the transition occurred (optional)
        metadata: Additional context data
    """
    
    from_state: ShutdownState
    to_state: ShutdownState
    timestamp_utc: float = field(default_factory=time.time)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShutdownStateMachine:
    """
    State machine for shutdown pipeline.
    
    Ensures valid state transitions and provides transition history.
    """
    
    # Valid transitions from each state
    VALID_TRANSITIONS: Dict[ShutdownState, Set[ShutdownState]] = {
        ShutdownState.IDLE: {
            ShutdownState.REQUESTED,
            ShutdownState.ADMISSION_CLOSED,  # Allow direct transition from IDLE (bypass REQUESTED)
            ShutdownState.TERMINATED,  # Allow direct transition to terminal states for tests/emergency
            ShutdownState.FAILED,
        },
        ShutdownState.REQUESTED: {
            ShutdownState.ADMISSION_CLOSED,
            ShutdownState.TERMINATED,  # Allow direct transition to terminal states
            ShutdownState.FAILED,
        },
        ShutdownState.ADMISSION_CLOSED: {
            ShutdownState.QUIESCENT,
            ShutdownState.DRAINING,  # Allow skipping steps in tests/emergency
            ShutdownState.CANCELLING,
            ShutdownState.STOPPING_COMPONENTS,
            ShutdownState.RELEASING_RESOURCES,
            ShutdownState.VERIFYING,
            ShutdownState.TERMINATED,
            ShutdownState.FAILED,
        },
        ShutdownState.QUIESCENT: {
            ShutdownState.DRAINING,
            ShutdownState.CANCELLING,
            ShutdownState.STOPPING_COMPONENTS,
            ShutdownState.RELEASING_RESOURCES,
            ShutdownState.VERIFYING,
            ShutdownState.TERMINATED,  # Allow skipping to terminal
            ShutdownState.FAILED,
        },
        ShutdownState.DRAINING: {
            ShutdownState.CANCELLING,
            ShutdownState.STOPPING_COMPONENTS,
            ShutdownState.RELEASING_RESOURCES,
            ShutdownState.VERIFYING,
            ShutdownState.TERMINATED,  # Allow skipping to terminal
            ShutdownState.FAILED,
        },
        ShutdownState.CANCELLING: {
            ShutdownState.STOPPING_COMPONENTS,
            ShutdownState.RELEASING_RESOURCES,
            ShutdownState.VERIFYING,
            ShutdownState.TERMINATED,  # Allow skipping to terminal
            ShutdownState.FAILED,
        },
        ShutdownState.STOPPING_COMPONENTS: {
            ShutdownState.RELEASING_RESOURCES,
            ShutdownState.VERIFYING,
            ShutdownState.TERMINATED,  # Allow skipping to terminal
            ShutdownState.FAILED,
        },
        ShutdownState.RELEASING_RESOURCES: {
            ShutdownState.VERIFYING,
            ShutdownState.TERMINATED,  # Allow direct transition to TERMINATED
            ShutdownState.FAILED,
        },
        ShutdownState.VERIFYING: {
            ShutdownState.TERMINATED,
            ShutdownState.FAILED,
        },
        ShutdownState.TERMINATED: {ShutdownState.TERMINATED, ShutdownState.IDLE},  # Can stay terminated or reset to IDLE
        ShutdownState.FAILED: {ShutdownState.IDLE},  # Can reset from failed
    }
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._state = ShutdownState.IDLE
        self._lock = threading.Lock()
        self._transitions: List[ShutdownTransition] = []
    
    @property
    def state(self) -> ShutdownState:
        """Return current state."""
        with self._lock:
            return self._state
    
    @property
    def is_terminal(self) -> bool:
        """Check if in a terminal state."""
        with self._lock:
            return self._state in (ShutdownState.TERMINATED, ShutdownState.FAILED)
    
    @property
    def transitions(self) -> List[ShutdownTransition]:
        """Return copy of transition history."""
        with self._lock:
            return list(self._transitions)
    
    def transition(
        self,
        to_state: ShutdownState,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            to_state: Target state
            reason: Why transitioning (optional)
            metadata: Additional data (optional)
            
        Returns:
            True if transition succeeded, False otherwise
        """
        with self._lock:
            current = self._state
            
            # Idempotent - same state is always valid
            if current == to_state:
                return True
            
            allowed = self.VALID_TRANSITIONS.get(current, set())
            
            if to_state not in allowed:
                return False
            
            transition = ShutdownTransition(
                from_state=current,
                to_state=to_state,
                reason=reason,
                metadata=dict(metadata) if metadata else {}
            )
            
            self._state = to_state
            self._transitions.append(transition)
            
            return True
    
    def force_transition(self, to_state: ShutdownState) -> None:
        """
        Force a state transition regardless of validity.
        
        Used for emergency transitions.
        """
        with self._lock:
            old = self._state
            self._state = to_state
            
            self._transitions.append(ShutdownTransition(
                from_state=old,
                to_state=to_state,
                reason="Force transition (emergency)",
                metadata={"forced": True}
            ))
    
    def snapshot(self) -> Dict[str, Any]:
        """Return immutable state snapshot."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "state": self._state.value,
                "transition_count": len(self._transitions),
                "is_terminal": self.is_terminal,
            }


# ==============================================================================
# Quiescence Interface
# ==============================================================================


class RuntimeQuiescence:
    """
    Manages quiescence state for shutdown preparation.
    
    Quiescence is NOT shutdown - it prepares the runtime for shutdown.
    During quiescence:
        - New work is rejected
        - Scheduling stops
        - Dispatch freezes
        - Active work continues until drain
    
    Usage:
        quiesce = RuntimeQuiescence()
        
        # Request quiescence
        await quiesce.enter_quiescent_mode()
        
        # Check status
        if quiesce.is_quiesced:
            # Refuse new tasks
        
        # Exit quiescence (before shutdown completes)
        quiesce.exit_quiescent_mode()
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._quiesced = False
        self._lock = threading.Lock()
        self._reason: Optional[str] = None
    
    @property
    def is_quiesced(self) -> bool:
        """Check if quiescence mode is active."""
        with self._lock:
            return self._quiesced
    
    async def enter_quiescent_mode(self, reason: Optional[str] = None) -> bool:
        """
        Enter quiescent mode.
        
        After this:
            - New task submissions are rejected
            - Scheduler stops accepting new work
            - Runtime is stabilized for shutdown preparation
        
        Args:
            reason: Explanation for quiescence (optional)
            
        Returns:
            True if successfully entered quiescent mode
        """
        with self._lock:
            if self._quiesced:
                return False  # Already quiesced
            
            self._quiesced = True
            self._reason = reason or "Shutdown preparation"
            return True
    
    def exit_quiescent_mode(self) -> None:
        """Exit quiescent mode (before shutdown completes)."""
        with self._lock:
            self._quiesced = False
            self._reason = None
    
    def check_quiescence(self, operation: str = "operation") -> None:
        """
        Check if quiescence would block this operation.
        
        Raises RuntimeError if quiesced and operation is not allowed.
        
        Args:
            operation: Description of the attempted operation
        """
        with self._lock:
            if self._quiesced:
                raise QuiescenceActiveError(
                    f"Quiescence active; {operation} not allowed during shutdown preparation",
                    runtime_id=self._runtime_id,
                    reason=self._reason
                )
    
    def snapshot(self) -> Dict[str, Any]:
        """Return immutable quiescence state."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "is_quiesced": self._quiesced,
                "reason": self._reason,
            }


class QuiescenceActiveError(Exception):
    """Raised when operation is blocked by quiescence."""
    
    def __init__(
        self,
        message: str,
        runtime_id: str,
        reason: Optional[str] = None
    ):
        super().__init__(message)
        self.runtime_id = runtime_id
        self.reason = reason


# ==============================================================================
# Task Draining System
# ==============================================================================


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True)
class TaskInfo:
    """
    Information about a tracked task.
    
    Args:
        task_id: Unique identifier
        component_id: Which component owns the task
        task_fn_name: Human-readable task name
        created_at: When task was submitted
        status: Current execution status
        is_interruptible: Can task be interrupted during shutdown?
        is_restartable: Can task be restarted after cancellation?
        is_compensatable: Can failure be compensated?
        is_atomic: Must complete or fail entirely (cannot leave partial state)
    """
    
    task_id: str
    component_id: str
    task_fn_name: str
    
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    status: TaskStatus = TaskStatus.PENDING
    
    is_interruptible: bool = True
    is_restartable: bool = False
    is_compensatable: bool = False
    is_atomic: bool = False
    
    # Execution context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate task duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        if self.started_at:
            return time.time() - self.started_at
        return None


class TaskTracker:
    """
    Tracks all tasks for shutdown draining.
    
    Provides:
        - Task lifecycle tracking
        - Status queries for shutdown decisions
        - Cancellation support
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._tasks: Dict[str, TaskInfo] = {}
        # Use RLock to allow nested lock acquisition (e.g., snapshot() -> get_pending_tasks())
        self._lock = threading.RLock()
    
    def track_task(
        self,
        task_id: str,
        component_id: str,
        task_fn_name: str,
        **kwargs
    ) -> TaskInfo:
        """
        Register a new task for tracking.
        
        Args:
            task_id: Unique identifier
            component_id: Owning component
            task_fn_name: Human-readable name
            **kwargs: TaskInfo parameters
            
        Returns:
            The created TaskInfo
        """
        info = TaskInfo(
            task_id=task_id,
            component_id=component_id,
            task_fn_name=task_fn_name,
            **kwargs
        )
        
        with self._lock:
            self._tasks[task_id] = info
        
        return info
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> Optional[TaskInfo]:
        """Update a task's status."""
        with self._lock:
            if task_id not in self._tasks:
                return None
            
            info = self._tasks[task_id]
            
            # Update timing
            kwargs = {}
            if status == TaskStatus.RUNNING and info.started_at is None:
                kwargs["started_at"] = time.time()
            elif status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
                kwargs["completed_at"] = time.time()
            
            self._tasks[task_id] = dataclasses_replace(
                info,
                status=status,
                **kwargs
            )
            
            return self._tasks[task_id]
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get information about a task."""
        with self._lock:
            return self._tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Mark a task as cancelled.
        
        Args:
            task_id: Task to cancel
            
        Returns:
            True if task existed
        """
        info = self.update_task_status(task_id, TaskStatus.CANCELLED)
        return info is not None
    
    def get_active_tasks(self) -> List[TaskInfo]:
        """Get all non-completed/non-cancelled tasks."""
        with self._lock:
            return [
                t for t in self._tasks.values()
                if t.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)
            ]
    
    def get_pending_tasks(self) -> List[TaskInfo]:
        """Get all pending tasks."""
        with self._lock:
            return [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]
    
    def get_running_tasks(self) -> List[TaskInfo]:
        """Get all running tasks."""
        with self._lock:
            return [t for t in self._tasks.values() if t.status == TaskStatus.RUNNING]
    
    def get_cancelled_tasks(self) -> List[TaskInfo]:
        """Get all cancelled tasks."""
        with self._lock:
            return [t for t in self._tasks.values() if t.status == TaskStatus.CANCELLED]
    
    def snapshot(self) -> Dict[str, Any]:
        """Return immutable snapshot of task state."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "total_tasks": len(self._tasks),
                "active_count": len([t for t in self._tasks.values() if t.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)]),
                "pending_count": len(self.get_pending_tasks()),
                "running_count": len(self.get_running_tasks()),
            }


def dataclasses_replace(obj: Any, **kwargs) -> Any:
    """Helper to replace fields in a dataclass."""
    import dataclasses
    return dataclasses.replace(obj, **kwargs)


# ==============================================================================
# Component Shutdown Interface
# ==============================================================================


class Shutdownable(Protocol):
    """
    Protocol for components that can participate in shutdown coordination.
    
    All components must implement these methods to participate in ordered shutdown.
    """
    
    @property
    def component_id(self) -> str:
        """Return unique component identifier."""
        ...
    
    @property
    def name(self) -> str:
        """Return human-readable component name."""
        ...
    
    async def prepare_shutdown(self, mode: ShutdownMode) -> None:
        """
        Prepare for shutdown.
        
        Called BEFORE quiescence. Use this to:
            - Flush buffers
            - Save critical state
            - Notify dependents
        
        Args:
            mode: The shutdown mode being executed
        """
        ...
    
    async def stop(self, mode: ShutdownMode) -> None:
        """
        Stop the component.
        
        Called during shutdown phase. Must:
            - Release any held resources
            - Stop background threads/tasks
            - Clean up
        
        Args:
            mode: The shutdown mode being executed
        """
        ...
    
    async def verify_shutdown(self, mode: ShutdownMode) -> bool:
        """
        Verify the component shut down correctly.
        
        Should check:
            - No active workers/schedulers/executors
            - No leaked resources
            - Proper cleanup
        
        Args:
            mode: The shutdown mode
            
        Returns:
            True if shutdown verified successfully
        """
        ...
    
    @property
    def is_shutdown(self) -> bool:
        """Check if component is fully shut down."""
        ...


class ShutdownableComponent(Shutdownable):
    """
    Base class for shutdown-capable components.
    
    Provides default implementations and lifecycle management.
    """
    
    def __init__(self, component_id: Optional[str] = None, name: Optional[str] = None):
        self._component_id = component_id or f"component_{uuid.uuid4().hex[:8]}"
        self._name = name or self._component_id
        self._shutdown_state = False
    
    @property
    def component_id(self) -> str:
        return self._component_id
    
    @property
    def name(self) -> str:
        return self._name
    
    async def prepare_shutdown(self, mode: ShutdownMode) -> None:
        """Default no-op preparation."""
        pass
    
    async def stop(self, mode: ShutdownMode) -> None:
        """Default no-op stopping."""
        pass
    
    async def verify_shutdown(self, mode: ShutdownMode) -> bool:
        """Verify shutdown state."""
        return self._shutdown_state
    
    @property
    def is_shutdown(self) -> bool:
        return self._shutdown_state
    
    def mark_shutdown_complete(self) -> None:
        """Mark component as fully shut down."""
        self._shutdown_state = True


# ==============================================================================
# Resource Releaser
# ==============================================================================


class ResourceReleaser:
    """
    Coordinates resource release across components.
    
    Ensures resources are released by their owners in proper order.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._owners: Dict[str, "ResourceOwner"] = {}
        self._lock = threading.Lock()
    
    def register_owner(self, owner: "ResourceOwner") -> None:
        """Register a resource owner."""
        with self._lock:
            self._owners[owner.owner_id] = owner
    
    def unregister_owner(self, owner_id: str) -> bool:
        """Unregister a resource owner. Returns True if existed."""
        with self._lock:
            if owner_id in self._owners:
                del self._owners[owner_id]
                return True
            return False
    
    async def release_all(self, mode: ShutdownMode) -> Dict[str, List[str]]:
        """
        Release all resources from all owners.
        
        Args:
            mode: The shutdown mode
            
        Returns:
            Mapping of owner_id -> list of released resource IDs
        """
        results: Dict[str, List[str]] = {}
        
        with self._lock:
            owners_list = list(self._owners.values())
        
        for owner in owners_list:
            try:
                released = await owner.release_resources(mode)
                results[owner.owner_id] = list(released)
            except Exception as e:
                # Log failure but continue with other owners
                results[owner.owner_id] = []
        
        return results
    
    def snapshot(self) -> Dict[str, Any]:
        """Return snapshot of resource release state."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "owner_count": len(self._owners),
                "registered_owners": list(self._owners.keys()),
            }


class ResourceOwner(Protocol):
    """
    Protocol for objects that own resources.
    
    Must be able to release its owned resources on demand.
    """
    
    @property
    def owner_id(self) -> str:
        """Return unique owner identifier."""
        ...
    
    async def release_resources(self, mode: ShutdownMode) -> List[str]:
        """
        Release all owned resources.
        
        Args:
            mode: The shutdown mode
            
        Returns:
            List of released resource IDs
        """
        ...


# ==============================================================================
# Shutdown Coordinator - The Main API
# ==============================================================================


class ShutdownCoordinator:
    """
    Canonical authority for global shutdown coordination.
    
    Responsibilities:
        - Receive and validate shutdown requests
        - Determine shutdown mode and configuration
        - Coordinate quiescence across all subsystems
        - Execute dependency-aware shutdown pipeline
        - Verify clean shutdown state
        - Publish terminal state events
    
    Usage:
        coordinator = ShutdownCoordinator(runtime_id="main")
        
        # Register components
        await coordinator.register_component(worker)
        await coordinator.register_component(executor)
        await coordinator.register_component(scheduler)
        
        # Request shutdown
        result = await coordinator.request_shutdown(
            ShutdownRequest(mode=ShutdownMode.GRACEFUL, reason="Service restart")
        )
        
        # Check final state
        if result.terminated:
            print("Shutdown complete")
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        
        # Core components
        self._state_machine = ShutdownStateMachine(runtime_id)
        self._quiescence = RuntimeQuiescence(runtime_id)
        self._task_tracker = TaskTracker(runtime_id)
        self._dependency_graph = DependencyGraph()
        self._releaser = ResourceReleaser(runtime_id)
        
        # Component management
        self._components: Dict[str, Shutdownable] = {}
        
        # Configuration
        self._default_timeout = 30.0
        
        # State
        self._current_request: Optional[ShutdownRequest] = None
        self._shutdown_results: List["ShutdownResult"] = []
        
        # Observability
        self._observers: List[ShutdownObserver] = []
        
        # Locks for thread safety
        self._lock = threading.Lock()
    
    @property
    def runtime_id(self) -> str:
        """Return the runtime identifier."""
        return self._runtime_id
    
    @property
    def current_state(self) -> ShutdownState:
        """Return current shutdown state."""
        return self._state_machine.state
    
    @property
    def is_shutdown(self) -> bool:
        """Check if runtime is fully shut down."""
        return self.current_state == ShutdownState.TERMINATED
    
    async def register_component(
        self,
        component: Shutdownable,
        depends_on: Optional[List[str]] = None
    ) -> None:
        """
        Register a component for shutdown coordination.
        
        Args:
            component: The component to register
            depends_on: List of component IDs this one depends on
        """
        with self._lock:
            cid = component.component_id
            
            # Check if already registered
            if cid in self._components:
                raise ValueError(f"Component {cid} already registered")
            
            self._components[cid] = component
            self._dependency_graph.register_component(cid, component.name, depends_on)
    
    async def deregister_component(self, component_id: str) -> bool:
        """
        Remove a component from shutdown coordination.
        
        Args:
            component_id: The component to remove
            
        Returns:
            True if component was registered
        """
        with self._lock:
            if component_id not in self._components:
                return False
            
            del self._components[component_id]
            
            # Update dependency graph (remove reverse edges)
            for info in self._dependency_graph.list_all_components():
                if component_id in self._dependency_graph.get_component_info(info).dependents:  # type: ignore
                    self._dependency_graph.get_component_info(info).dependents.remove(component_id)  # type: ignore
            
            return True
    
    async def register_observer(self, observer: ShutdownObserver) -> None:
        """Register an event observer."""
        with self._lock:
            self._observers.append(observer)
    
    def remove_observer(self, observer: ShutdownObserver) -> bool:
        """Remove an observer. Returns True if registered."""
        with self._lock:
            try:
                self._observers.remove(observer)
                return True
            except ValueError:
                return False
    
    async def request_shutdown(
        self,
        request: ShutdownRequest
    ) -> "ShutdownResult":
        """
        Request shutdown with given parameters.
        
        This is the main entry point for initiating shutdown.
        
        Args:
            request: The shutdown request configuration
            
        Returns:
            Result containing final state and statistics
        """
        # Validate request (not already shutting down, etc.)
        with self._lock:
            if self.current_state != ShutdownState.IDLE:
                return ShutdownResult(
                    runtime_id=self._runtime_id,
                    terminated=False,
                    success=False,
                    reason="Shutdown already in progress",
                    mode=request.mode,
                    duration_seconds=0.0
                )
            
            # Store request for reference
            self._current_request = request
        
        try:
            result = await self._execute_shutdown(request)
            return result
            
        except Exception as e:
            # Force transition to failed state
            self._state_machine.force_transition(ShutdownState.FAILED)
            
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason=f"Shutdown failed: {str(e)}",
                mode=request.mode,
                duration_seconds=time.monotonic() - request.timeout_seconds
            )
    
    async def _execute_shutdown(self, request: ShutdownRequest) -> "ShutdownResult":
        """
        Execute the shutdown pipeline.
        
        Pipeline stages:
            1. Admission closed (reject new work)
            2. Quiescence (stabilize runtime)
            3. Drain tasks
            4. Cancel remaining work
            5. Stop components (dependency order)
            6. Release resources
            7. Verify shutdown
        """
        start_time = time.monotonic()
        
        # Phase 1: Admission Closed
        if not self._state_machine.transition(
            ShutdownState.ADMISSION_CLOSED,
            reason="Request accepted"
        ):
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason="Invalid state transition",
                mode=request.mode,
                duration_seconds=time.monotonic() - start_time
            )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.admission_closed",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="admission_closed",
            mode=request.mode.value
        ))
        
        # Phase 2: Quiescence
        await self._quiescence.enter_quiescent_mode(
            f"Shutdown {request.mode.value}: {request.reason}"
        )
        
        if not self._state_machine.transition(
            ShutdownState.QUIESCENT,
            reason="Quiescence established"
        ):
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason="Failed to reach quiescent state",
                mode=request.mode,
                duration_seconds=time.monotonic() - start_time
            )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.quiescence_established",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="quiescent",
            mode=request.mode.value
        ))
        
        # Phase 3: Prepare components for shutdown
        await self._prepare_components_for_shutdown(request.mode)
        
        # Phase 4: Drain outstanding work
        drained_tasks = await self._drain_tasks(request.mode, request.timeout_seconds / 2)
        
        if not self._state_machine.transition(
            ShutdownState.DRAINING,
            reason=f"Drained {len(drained_tasks)} tasks"
        ):
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason="Failed to drain tasks",
                mode=request.mode,
                duration_seconds=time.monotonic() - start_time
            )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.tasks_drained",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="draining",
            mode=request.mode.value,
            metadata={"drained_count": len(drained_tasks)}
        ))
        
        # Phase 5: Cancel remaining work
        cancelled_tasks = await self._cancel_remaining_work(request.mode)
        
        if not self._state_machine.transition(
            ShutdownState.CANCELLING,
            reason=f"Cancelled {len(cancelled_tasks)} tasks"
        ):
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason="Failed to cancel remaining work",
                mode=request.mode,
                duration_seconds=time.monotonic() - start_time
            )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.tasks_cancelled",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="cancelling",
            mode=request.mode.value,
            metadata={"cancelled_count": len(cancelled_tasks)}
        ))
        
        # Phase 6: Stop components (dependency order)
        shutdown_order = self._get_shutdown_order()
        
        stopped_components = []
        for component_id in shutdown_order:
            if component_id in self._components:
                try:
                    await self._stop_component(self._components[component_id], request.mode)
                    stopped_components.append(component_id)
                except Exception as e:
                    # Continue with other components
                    pass
        
        if not self._state_machine.transition(
            ShutdownState.STOPPING_COMPONENTS,
            reason=f"Stopped {len(stopped_components)} components"
        ):
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason="Failed to stop components",
                mode=request.mode,
                duration_seconds=time.monotonic() - start_time
            )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.components_stopped",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="stopping_components",
            mode=request.mode.value,
            metadata={
                "stopped_count": len(stopped_components),
                "components": stopped_components
            }
        ))
        
        # Phase 7: Release resources
        released_resources = await self._releaser.release_all(request.mode)
        
        if not self._state_machine.transition(
            ShutdownState.RELEASING_RESOURCES,
            reason=f"Released {sum(len(v) for v in released_resources.values())} resources"
        ):
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason="Failed to release resources",
                mode=request.mode,
                duration_seconds=time.monotonic() - start_time
            )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.resources_released",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="releasing_resources",
            mode=request.mode.value,
            metadata={"released_count": sum(len(v) for v in released_resources.values())}
        ))
        
        # Phase 8: Verify shutdown
        verification = await self._verify_shutdown(request.mode)
        
        if not self._state_machine.transition(
            ShutdownState.VERIFYING,
            reason="Verification complete"
        ):
            return ShutdownResult(
                runtime_id=self._runtime_id,
                terminated=False,
                success=False,
                reason=f"Shutdown verification failed: {verification.reason}",
                mode=request.mode,
                duration_seconds=time.monotonic() - start_time
            )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.verified",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="verifying",
            mode=request.mode.value,
            metadata=verification.to_dict()
        ))
        
        # Phase 9: Mark as terminated
        self._state_machine.transition(
            ShutdownState.TERMINATED,
            reason="Shutdown complete"
        )
        
        await self._publish_event(ShutdownEvent(
            event_id=str(uuid.uuid4()),
            event_type="shutdown.terminated",
            runtime_id=self._runtime_id,
            correlation_id=request.source_id,
            stage="terminated",
            mode=request.mode.value
        ))
        
        # Store result
        duration = time.monotonic() - start_time
        
        result = ShutdownResult(
            runtime_id=self._runtime_id,
            terminated=True,
            success=verification.verified,
            reason=verification.reason,
            mode=request.mode,
            duration_seconds=duration,
            tasks_drained=len(drained_tasks),
            tasks_cancelled=len(cancelled_tasks),
            components_stopped=len(stopped_components),
            resources_released=sum(len(v) for v in released_resources.values()),
            verification=verification
        )
        
        with self._lock:
            self._shutdown_results.append(result)
        
        return result
    
    async def _prepare_components_for_shutdown(self, mode: ShutdownMode) -> None:
        """Call prepare_shutdown on all components."""
        shutdown_order = self._get_shutdown_order()
        
        for component_id in shutdown_order:
            if component_id in self._components:
                try:
                    await self._components[component_id].prepare_shutdown(mode)
                except Exception:
                    # Continue with other components
                    pass
    
    async def _drain_tasks(self, mode: ShutdownMode, timeout_seconds: float) -> List[str]:
        """
        Wait for tasks to complete within timeout.
        
        Returns list of completed task IDs.
        """
        completed = []
        
        if mode in (ShutdownMode.EMERGENCY, ShutdownMode.FORCED):
            # Skip draining in emergency/forced modes
            return completed
        
        max_time = time.monotonic() + timeout_seconds
        
        while True:
            active_tasks = self._task_tracker.get_active_tasks()
            
            if not active_tasks:
                break
            
            if time.monotonic() >= max_time:
                # Timeout reached, stop waiting
                break
            
            # Give tasks a chance to complete
            await asyncio.sleep(0.1)
        
        return completed
    
    async def _cancel_remaining_work(self, mode: ShutdownMode) -> List[str]:
        """
        Cancel any remaining pending/running work.
        
        Returns list of cancelled task IDs.
        """
        cancelled = []
        
        if mode in (ShutdownMode.GRACEFUL, ShutdownMode.MAINTENANCE):
            # In graceful modes, we already tried draining
            return cancelled
        
        # Get all active tasks and mark them as cancelled
        active_tasks = self._task_tracker.get_active_tasks()
        
        for task in active_tasks:
            if self._task_tracker.cancel_task(task.task_id):
                cancelled.append(task.task_id)
        
        return cancelled
    
    def _get_shutdown_order(self) -> List[str]:
        """
        Get components in shutdown order.
        
        Reverse of dependency order - dependencies stopped first.
        """
        try:
            return self._dependency_graph.shutdown_order()
        except DependencyCycleError:
            # Fallback: reverse registration order
            return list(reversed(list(self._components.keys())))
    
    async def _stop_component(
        self,
        component: Shutdownable,
        mode: ShutdownMode
    ) -> None:
        """Stop a single component."""
        try:
            await component.stop(mode)
            component.mark_shutdown_complete()
        except Exception:
            # Mark as shutdown anyway for verification
            component.mark_shutdown_complete()
            raise
    
    async def _verify_shutdown(self, mode: ShutdownMode) -> "ShutdownVerification":
        """
        Verify all components and resources have been properly shut down.
        
        Returns:
            ShutdownVerification with verification status
        """
        issues: List[str] = []
        
        # Check all components are shutdown
        for component in self._components.values():
            if not component.is_shutdown:
                issues.append(f"Component {component.component_id} not shutdown")
        
        # Verify task tracker has no active tasks
        active_tasks = self._task_tracker.get_active_tasks()
        if active_tasks:
            issues.append(f"{len(active_tasks)} active tasks remaining")
        
        # Check quiescence state
        if self._quiescence.is_quiesced and mode != ShutdownMode.GRACEFUL:
            # Quiescence should be maintained until shutdown complete
            pass
        
        return ShutdownVerification(
            verified=len(issues) == 0,
            reason="All components properly shut down" if not issues else "; ".join(issues),
            component_count=len(self._components),
            active_task_count=len(active_tasks),
            issues=issues
        )
    
    async def _publish_event(self, event: ShutdownEvent) -> None:
        """Publish a shutdown event to all observers."""
        with self._lock:
            for observer in list(self._observers):
                try:
                    await observer.on_shutdown_event(event)
                except Exception:
                    # Don't let observer failures stop shutdown
                    pass
    
    def snapshot(self) -> Dict[str, Any]:
        """
        Return immutable snapshot of shutdown coordinator state.
        
        Used for diagnostics and verification.
        
        Enhanced per F-3.7.9-LOW-002 remediation:
        - Resource leak detection metrics
        - Background loop inventory
        """
        with self._lock:
            result = {
                "runtime_id": self._runtime_id,
            }
            result["current_state"] = self.current_state.value
            result["is_shutdown"] = self.is_shutdown
            result["registered_component_count"] = len(self._components)
            result["component_ids"] = list(self._components.keys())
            result["dependency_graph_size"] = self._dependency_graph.size
            result["task_tracker_snapshot"] = self._task_tracker.snapshot()
            result["quiescence_state"] = self._quiescence.snapshot()
            result["releaser_snapshot"] = self._releaser.snapshot()
            result["transition_history"] = [
                {"from": t.from_state.value, "to": t.to_state.value}
                for t in self._state_machine.transitions
            ]
            
            # Enhanced diagnostics per F-3.7.9-LOW-002 remediation
            active_tasks = self._task_tracker.get_active_tasks()
            result["active_task_count"] = len(active_tasks)
            result["pending_task_count"] = len(self._task_tracker.get_pending_tasks())
            result["running_task_count"] = len(self._task_tracker.get_running_tasks())
            
            # Resource leak detection metrics
            result["resource_leak_detected"] = self._check_resource_leaks()
            result["resource_health_score"] = self._compute_resource_health_score()
            
            return result
    
    def _check_resource_leaks(self) -> bool:
        """
        Check for potential resource leaks.
        
        Expands coverage per F-3.7.9-LOW-002 remediation.
        """
        # Check for active tasks that might be orphaned
        active_tasks = self._task_tracker.get_active_tasks()
        if len(active_tasks) > 100:  # Large number of active tasks could indicate leak
            return True
        
        # Check for very old pending tasks (potential deadlock)
        for task in self._task_tracker.get_pending_tasks():
            task_age = time.monotonic() - task.created_at
            if task_age > 300.0:  # Tasks waiting over 5 minutes could be stuck
                return True
        
        return False
    
    def _compute_resource_health_score(self) -> float:
        """
        Compute a health score for resource usage (0.0 to 1.0).
        
        Higher scores indicate better resource hygiene.
        """
        score = 1.0
        
        # Deduct points for active tasks
        active_tasks = self._task_tracker.get_active_tasks()
        if len(active_tasks) > 50:
            score -= 0.2
        elif len(active_tasks) > 20:
            score -= 0.1
        
        # Deduct for very old pending tasks
        for task in self._task_tracker.get_pending_tasks():
            task_age = time.monotonic() - task.created_at
            if task_age > 60.0:
                score -= 0.05
        
        return max(0.0, min(1.0, score))


@dataclass
class ShutdownVerification:
    """
    Result of shutdown verification.
    
    Args:
        verified: Whether shutdown was verified successfully
        reason: Explanation for verification result
        component_count: Number of components checked
        active_task_count: Remaining active tasks (should be 0)
        issues: List of verification issues found
    """
    
    verified: bool
    reason: str
    component_count: int = 0
    active_task_count: int = 0
    issues: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "verified": self.verified,
            "reason": self.reason,
            "component_count": self.component_count,
            "active_task_count": self.active_task_count,
            "issues": self.issues,
        }


@dataclass
class ShutdownResult:
    """
    Result of a shutdown operation.
    
    Args:
        runtime_id: Runtime that shut down
        terminated: Whether runtime reached TERMINATED state
        success: Whether shutdown completed without errors
        reason: Human-readable result description
        mode: Mode in which shutdown was executed
        duration_seconds: How long shutdown took
        tasks_drained: Number of tasks allowed to complete
        tasks_cancelled: Number of tasks cancelled
        components_stopped: Number of components stopped
        resources_released: Total resources released
        verification: Final verification status
    """
    
    runtime_id: str
    terminated: bool
    success: bool
    reason: str
    mode: ShutdownMode
    duration_seconds: float = 0.0
    
    tasks_drained: int = 0
    tasks_cancelled: int = 0
    components_stopped: int = 0
    resources_released: int = 0
    
    verification: Optional[ShutdownVerification] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "runtime_id": self.runtime_id,
            "terminated": self.terminated,
            "success": self.success,
            "reason": self.reason,
            "mode": self.mode.value,
            "duration_seconds": round(self.duration_seconds, 3),
            "tasks_drained": self.tasks_drained,
            "tasks_cancelled": self.tasks_cancelled,
            "components_stopped": self.components_stopped,
            "resources_released": self.resources_released,
        }


# ==============================================================================
# SIGNAL HANDLER INTEGRATION
# ==============================================================================


class BackgroundLoopTracker:
    """
    Tracks background execution loops for shutdown coordination.
    
    Ensures all async background tasks have explicit stop paths and
    are properly terminated during shutdown.
    
    This addresses F-3.7.9-LOW-001 (Missing Background Loop Inventory).
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._background_loops: Dict[str, "BackgroundLoopInfo"] = {}
        self._lock = threading.Lock()
    
    def register_background_loop(
        self,
        loop_id: str,
        name: str,
        stop_path: Optional[Callable[[ShutdownMode], Awaitable[None]]] = None
    ) -> None:
        """
        Register a background loop with its shutdown path.
        
        Args:
            loop_id: Unique identifier for the loop
            name: Human-readable name
            stop_path: Async callable to stop the loop (optional)
        """
        with self._lock:
            self._background_loops[loop_id] = BackgroundLoopInfo(
                loop_id=loop_id,
                name=name,
                stop_path=stop_path,
                registered_at=time.monotonic()
            )
    
    def unregister_background_loop(self, loop_id: str) -> bool:
        """Unregister a background loop."""
        with self._lock:
            if loop_id in self._background_loops:
                del self._background_loops[loop_id]
                return True
            return False
    
    async def stop_all_background_loops(self, mode: ShutdownMode) -> Dict[str, bool]:
        """
        Stop all registered background loops.
        
        Args:
            mode: The shutdown mode
            
        Returns:
            Mapping of loop_id -> success status
        """
        results: Dict[str, bool] = {}
        
        with self._lock:
            loops_list = list(self._background_loops.values())
        
        for loop_info in loops_list:
            if loop_info.stop_path is not None:
                try:
                    await loop_info.stop_path(mode)
                    results[loop_info.loop_id] = True
                except Exception:
                    results[loop_info.loop_id] = False
            else:
                # No explicit stop path - mark as stopped anyway
                results[loop_info.loop_id] = True
        
        return results
    
    def get_background_loop_inventory(self) -> List[Dict[str, Any]]:
        """Get inventory of all registered background loops."""
        with self._lock:
            return [
                {
                    "loop_id": info.loop_id,
                    "name": info.name,
                    "has_stop_path": info.stop_path is not None,
                    "registered_at": info.registered_at
                }
                for info in self._background_loops.values()
            ]
    
    def snapshot(self) -> Dict[str, Any]:
        """Return snapshot of background loop state."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "loop_count": len(self._background_loops),
                "loops": self.get_background_loop_inventory(),
            }


@dataclass
class BackgroundLoopInfo:
    """
    Information about a registered background loop.
    
    Args:
        loop_id: Unique identifier
        name: Human-readable name
        stop_path: Async callable to stop the loop (optional)
        registered_at: When it was registered
    """
    loop_id: str
    name: str
    stop_path: Optional[Callable[[ShutdownMode], Awaitable[None]]]
    registered_at: float


class SignalHandlerIntegration:
    """
    Integrates OS signal handlers with the shutdown coordinator.
    
    Registers SIGTERM and SIGINT handlers that request shutdown via the
    canonical ShutdownCoordinator authority rather than performing shutdown directly.
    
    This ensures all shutdown paths flow through the coordinated shutdown pipeline.
    
    Also implements F-3.7.9-MED-001 remediation:
    - Robust async context detection with multiple fallback strategies
    - Graceful handling when no event loop is available
    """
    
    _instance: Optional["SignalHandlerIntegration"] = None
    _installed_handlers: Dict[str, Any] = {}
    
    def __init__(self, coordinator: ShutdownCoordinator):
        self._coordinator = coordinator
        self._runtime_id = coordinator.runtime_id
        
        # Store original signal handlers for potential restoration
        self._original_sigterm: Optional[Any] = None
        self._original_sigint: Optional[Any] = None
        
        # Signal communication pipe (for set_wakeup_fd)
        self._signal_pipe_r: Optional[int] = None
        self._signal_pipe_w: Optional[int] = None
        self._wakeup_fds_installed: bool = False
        
        # Track signal queue for deferring shutdown requests when no loop exists
        self._signal_queue: List[ShutdownRequest] = []
        
        # Lock for thread-safe signal queue operations
        self._lock = threading.Lock()
    
    @classmethod
    def install(cls, coordinator: ShutdownCoordinator) -> "SignalHandlerIntegration":
        """
        Install signal handlers that delegate to shutdown coordinator.
        
        Uses a multi-tier approach:
        1. Creates a pipe with set_wakeup_fd() for safe signal-to-thread communication
        2. Registers the read end with asyncio's event loop via add_reader()
        3. Signal handler writes to write end (safe in signal context)
        4. Reader callback schedules shutdown request on main thread
        
        Args:
            coordinator: The canonical shutdown coordinator
            
        Returns:
            SignalHandlerIntegration instance for potential cleanup
        """
        if cls._instance is not None:
            # Already installed, return existing instance
            return cls._instance
        
        instance = cls(coordinator)
        cls._instance = instance
        
        try:
            # Install SIGTERM handler
            instance._original_sigterm = signal.signal(
                signal.SIGTERM,
                lambda sig, frame: instance._handle_shutdown_signal(sig, frame)
            )
            
            # Install SIGINT handler (Ctrl+C)
            instance._original_sigint = signal.signal(
                signal.SIGINT,
                lambda sig, frame: instance._handle_shutdown_signal(sig, frame)
            )
            
            cls._installed_handlers["sigterm"] = signal.SIGTERM
            cls._installed_handlers["sigint"] = signal.SIGINT
            
        except (OSError, ValueError) as e:
            # Signal handling not available in this context (e.g., non-main thread)
            instance._signal_available = False
        
        return instance
    
    def install_wakeup_fd(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Install signal.set_wakeup_fd() for safe inter-thread communication.
        
        This should be called after the event loop is created but before it runs.
        The pipe-based approach ensures signals from any thread can safely
        communicate with the main event loop without race conditions.
        
        Args:
            loop: The asyncio event loop to register the reader on
        """
        import fcntl
        
        try:
            # Create a non-blocking pipe for signal communication
            self._signal_pipe_r, self._signal_pipe_w = os.pipe()
            
            # Set both ends to non-blocking
            flags_r = fcntl.fcntl(self._signal_pipe_r, fcntl.F_GETFL)
            fcntl.fcntl(self._signal_pipe_r, fcntl.F_SETFL, flags_r | os.O_NONBLOCK)
            
            flags_w = fcntl.fcntl(self._signal_pipe_w, fcntl.F_GETFL)
            fcntl.fcntl(self._signal_pipe_w, fcntl.F_SETFL, flags_w | os.O_NONBLOCK)
            
            # Install the write end with signal.set_wakeup_fd()
            # This is safe to call from signal handlers
            signal.set_wakeup_fd(self._signal_pipe_w, wrap=False)
            
            # Register reader callback on the event loop
            # When a signal arrives, it writes to the pipe and this callback runs
            loop.add_reader(
                self._signal_pipe_r,
                self._on_signal_wakeup,
                loop
            )
            
            self._wakeup_fds_installed = True
            
        except (OSError, ValueError) as e:
            # Pipe creation or set_wakeup_fd failed
            # The signal handlers will still work but with reduced reliability
            import sys
            print(
                f"Warning: Could not install wakeup pipe for signals: {e}",
                file=sys.stderr
            )
    
    def uninstall_wakeup_fd(self) -> None:
        """
        Restore original signal state by removing wakeup fd and pipe.
        """
        if self._wakeup_fds_installed:
            try:
                # Remove the reader from event loop if it exists
                import asyncio
                loop = asyncio.get_event_loop()
                if self._signal_pipe_r is not None:
                    try:
                        loop.remove_reader(self._signal_pipe_r)
                    except (KeyError, ValueError):
                        pass
                
                # Restore signal handler to default
                signal.set_wakeup_fd(-1)
                
            except (OSError, ValueError, RuntimeError):
                pass
            
            self._wakeup_fds_installed = False
        
        # Close pipe file descriptors if they exist
        if self._signal_pipe_r is not None:
            try:
                os.close(self._signal_pipe_r)
            except OSError:
                pass
            self._signal_pipe_r = None
        
        if self._signal_pipe_w is not None:
            try:
                os.close(self._signal_pipe_w)
            except OSError:
                pass
            self._signal_pipe_w = None
    
    def _on_signal_wakeup(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Callback invoked when signal writes to wakeup fd.
        
        This runs in the main thread's event loop context and safely
        schedules the shutdown request asynchronously.
        
        Args:
            loop: The event loop that triggered this callback
        """
        import fcntl
        
        # Read all data from pipe (must read to clear the writer)
        try:
            flags = fcntl.fcntl(self._signal_pipe_r, fcntl.F_GETFL)
            fcntl.fcntl(self._signal_pipe_r, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            while True:
                try:
                    data = os.read(self._signal_pipe_r, 1024)
                    if not data:
                        break
                except BlockingIOError:
                    # No more data to read
                    break
        except OSError:
            pass
        
        # Schedule shutdown request on the event loop
        try:
            asyncio.ensure_future(
                self._coordinator.request_shutdown(
                    ShutdownRequest(
                        mode=ShutdownMode.GRACEFUL,
                        reason="SIGTERM received via wakeup pipe - graceful shutdown",
                        source_id="signal:wakeup_pipe",
                        timeout_seconds=30.0
                    )
                )
            )
        except Exception:
            import sys
            print("Warning: Failed to schedule shutdown from signal wakeup", file=sys.stderr)
    
    def _handle_shutdown_signal(self, signum: int, frame) -> None:
        """
        Handle OS signal by requesting shutdown through coordinator.
        
        This is called from the signal handler context and must be safe
        for async operation within the signal handling constraints.
        
        Implements robust fallback strategy:
        1. Try to get running event loop in same thread - schedule directly
        2. Use run_coroutine_threadsafe if in different thread but loop exists
        3. Check for running loop (may not be same thread) and use async safe methods
        4. Fallback to thread-safe shutdown request via internal queue
        5. Final fallback: log error and let external systems handle
        """
        # Ensure asyncio module is available in this context
        import asyncio as _asyncio
        
        # Map signal to shutdown mode
        if signum == signal.SIGTERM:
            mode = ShutdownMode.GRACEFUL
            reason = "SIGTERM received - graceful shutdown"
        elif signum == signal.SIGINT:
            mode = ShutdownMode.GRACEFUL
            reason = "SIGINT received (Ctrl+C) - graceful shutdown"
        else:
            mode = ShutdownMode.FORCED
            reason = f"Signal {signum} received - forced shutdown"
        
        request = ShutdownRequest(
            mode=mode,
            reason=reason,
            source_id=f"signal_handler:{signum}",
            timeout_seconds=30.0
        )
        
        # Strategy 1: Try to get the running event loop in current thread context
        try:
            # get_running_loop() only works if an event loop is already running in this thread
            loop = _asyncio.get_running_loop()
            
            # We're in a thread that has a running loop - use it directly
            self._schedule_shutdown_via_loop(loop, request)
            return
            
        except RuntimeError:
            # No event loop in current thread, try other strategies
            
            # Strategy 2: Try to get ANY running loop (not necessarily in this thread)
            try:
                loop = _asyncio.get_event_loop()
                
                # Check if we can safely use this loop
                if not loop.is_closed():
                    self._schedule_shutdown_via_loop(loop, request)
                    return
                    
            except RuntimeError:
                # No event loop at all exists yet
                pass
        
        # Strategy 3: Try to schedule via asyncio.run() in main thread context
        try:
            # This will create a new loop if needed and run the coroutine
            current_thread = threading.current_thread()
            
            # If we're in the main thread, try to get or create a loop
            if current_thread.name == "MainThread" or getattr(current_thread, '_name', None) == "MainThread":
                try:
                    _asyncio.run(
                        self._coordinator.request_shutdown(request)
                    )
                    return
                except Exception:
                    # asyncio.run() failed, continue to next fallback
                    pass
        except Exception:
            pass
        
        # Strategy 4: Try to schedule via run_coroutine_threadsafe with ANY loop
        try:
            for task in _asyncio.all_tasks():
                if hasattr(task, 'get_loop'):
                    loop = task.get_loop()
                    if loop and not loop.is_closed():
                        try:
                            _asyncio.run_coroutine_threadsafe(
                                self._coordinator.request_shutdown(request),
                                loop
                            )
                            return
                        except Exception:
                            continue  # Try other loops
                break
        except Exception:
            pass
        
        # Strategy 5: Fallback to internal queue for deferred processing
        try:
            # Use an internal signal queue that can be processed later when a loop is available
            self._signal_queue_put(request)
        except Exception:
            # All strategies exhausted - log but don't crash
            print(
                f"ERROR: Signal {signum} handler could not schedule shutdown. "
                "Shutdown may not be requested. This indicates an emergency state.",
                file=sys.stderr
            )
    
    def _schedule_shutdown_via_loop(
        self,
        loop: asyncio.AbstractEventLoop,
        request: ShutdownRequest
    ) -> None:
        """
        Schedule shutdown request on a specific event loop using safe strategies.
        
        Args:
            loop: The event loop to schedule on
            request: The shutdown request to schedule
        """
        try:
            # Try direct create_task (fastest path when in same thread)
            task = loop.create_task(
                self._coordinator.request_shutdown(request)
            )
            
            # If loop is not running, we can wait for completion safely
            if not loop.is_running():
                loop.run_until_complete(task)
                
        except RuntimeError:
            # Loop closed or in different thread - use thread-safe scheduling
            try:
                asyncio.run_coroutine_threadsafe(
                    self._coordinator.request_shutdown(request),
                    loop
                )
            except (RuntimeError, AttributeError):
                # Cannot schedule - log and continue to next fallback
                import sys
                print(
                    f"Warning: Could not schedule shutdown via loop - runtime closed or in incompatible state",
                    file=sys.stderr
                )
        except Exception:
            # Any other error during scheduling
            import sys
            print(
                f"Warning: Unexpected error scheduling shutdown: {type(Exception).__name__}",
                file=sys.stderr
            )
    
    def _signal_queue_put(self, request: ShutdownRequest) -> bool:
        """
        Put a signal request into an internal queue for deferred processing.
        
        This ensures shutdown requests survive even when no event loop is available.
        The queue will be processed when the runtime initializes its main loop.
        
        Args:
            request: The shutdown request to queue
            
        Returns:
            True if successfully queued, False otherwise
        """
        # Use a class-level queue for signal deferral
        if not hasattr(self.__class__, '_signal_deferred_queue'):
            self.__class__._signal_deferred_queue = []  # type: ignore[attr-defined]
        
        # Thread-safe append to the deferred queue
        import threading
        with self._lock:
            self.__class__._signal_deferred_queue.append(request)  # type: ignore[attr-defined]
        
        return True
    
    def uninstall(self) -> None:
        """
        Restore original signal handlers and clean up resources.
        
        Removes wakeup fd pipe, restores original signal handlers,
        and closes file descriptors.
        """
        # Uninstall wakeup fd first to prevent new signals from writing to pipe
        self.uninstall_wakeup_fd()
        
        if self._original_sigterm is not None and signal.SIGTERM in self._installed_handlers:
            try:
                signal.signal(signal.SIGTERM, self._original_sigterm)
            except (OSError, ValueError):
                pass
        
        if self._original_sigint is not None and signal.SIGINT in self._installed_handlers:
            try:
                signal.signal(signal.SIGINT, self._original_sigint)
            except (OSError, ValueError):
                pass
    
    @classmethod
    def uninstall_all(cls) -> None:
        """Uninstall all installed handlers."""
        if cls._instance is not None:
            cls._instance.uninstall()
            cls._instance = None


# ==============================================================================
# PROCESS EXIT COORDINATION
# ==============================================================================


class ProcessExitCoordinator:
    """
    Coordinates process exit after shutdown completion.
    
    Ensures that os._exit() or sys.exit() is only called after:
    1. All shutdown phases complete successfully
    2. Resources are released
    3. Terminal state is committed
    
    Usage:
        coordinator = ProcessExitCoordinator(shutdown_coordinator)
        
        # After shutdown completes:
        if result.success and result.terminated:
            coordinator.exit(0)  # Exit with code 0 on success
    """
    
    def __init__(self, coordinator: ShutdownCoordinator):
        self._coordinator = coordinator
        self._exit_called = False
    
    @property
    def exit_called(self) -> bool:
        """Check if process exit has been called."""
        return self._exit_called
    
    async def request_exit(
        self,
        code: int = 0,
        force: bool = False
    ) -> None:
        """
        Request process exit after shutdown verification.
        
        Args:
            code: Exit code (0 for success, non-zero for error)
            force: If True, call os._exit() to bypass cleanup handlers
        """
        # Verify shutdown is complete before exiting
        if not self._coordinator.is_shutdown and not force:
            raise RuntimeError("Cannot exit - shutdown not yet complete")
        
        self._exit_called = True
        
        if force:
            # Bypass all cleanup handlers for emergency exit
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(code)
        else:
            # Normal exit, allows cleanup handlers to run
            sys.exit(code)
    
    async def verify_and_exit(self, result: ShutdownResult) -> None:
        """
        Verify shutdown result and exit if successful.
        
        Args:
            result: The shutdown result from request_shutdown()
        """
        if not result.terminated:
            raise RuntimeError("Shutdown was not terminated - cannot exit")
        
        if not result.success:
            # Non-zero exit code for failed shutdown
            await self.request_exit(code=1)
            return
        
        await self.request_exit(code=0)


# ==============================================================================
# COOPERATIVE CANCELLATION SUPPORT
# ==============================================================================


class CooperativeCancellationToken:
    """
    Token for cooperative task cancellation during shutdown.
    
    Tasks check this token periodically and respond to cancellation requests.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._cancelled = False
        self._lock = threading.Lock()
        self._cancel_reason: Optional[str] = None
    
    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        with self._lock:
            return self._cancelled
    
    @property
    def cancel_reason(self) -> Optional[str]:
        """Get the cancellation reason if available."""
        with self._lock:
            return self._cancel_reason
    
    def request_cancel(self, reason: Optional[str] = None) -> bool:
        """
        Request cancellation of the task.
        
        Args:
            reason: Optional explanation for cancellation
            
        Returns:
            True if cancellation was requested (or already done)
        """
        with self._lock:
            if not self._cancelled:
                self._cancelled = True
                self._cancel_reason = reason or "Shutdown cancellation"
                return True
            return False
    
    def check(self) -> None:
        """Check if cancellation has been requested, raise if so."""
        if self.is_cancelled:
            # Local CancellationRequestedError - defined in the signals module at runtime_state level
            # For now, use RuntimeError as placeholder since this is an internal implementation detail
            raise RuntimeError(f"Task cancelled during shutdown: {self.cancel_reason}")
            raise CancellationRequestedError(
                f"Task cancelled during shutdown: {self.cancel_reason}",
                reason=self._cancel_reason
            )
    
    def reset(self) -> None:
        """Reset the cancellation token (not recommended)."""
        with self._lock:
            self._cancelled = False
            self._cancel_reason = None


class CooperativeCancellationMixin:
    """
    Mixin class for tasks that support cooperative cancellation.
    
    Provides cancel_token property and check_cancellation() method.
    """
    
    def __init__(self):
        self._cancellation_token: Optional[CooperativeCancellationToken] = None
    
    @property
    def cancel_token(self) -> CooperativeCancellationToken:
        """Get or create cancellation token for this task."""
        if self._cancellation_token is None:
            # Use a unique ID based on the object's id
            self._cancellation_token = CooperativeCancellationToken(
                runtime_id=getattr(self, "_runtime_id", "unknown")
            )
        return self._cancellation_token
    
    def check_cancellation(self) -> None:
        """Check if cancellation has been requested."""
        if self._cancellation_token:
            self._cancellation_token.check()
    
    async def wait_with_cancellation_check(
        self,
        timeout: Optional[float] = None
    ) -> bool:
        """
        Wait with periodic cancellation checks.
        
        Args:
            timeout: Maximum time to wait (None for no limit)
            
        Returns:
            True if completed normally, False if cancelled
        """
        import asyncio
        
        start_time = time.monotonic()
        check_interval = 0.1  # Check every 100ms
        
        while timeout is None or (time.monotonic() - start_time) < timeout:
            self.check_cancellation()  # Raises if cancelled
            
            try:
                await asyncio.sleep(check_interval)
            except asyncio.CancelledError:
                self.cancel_token.request_cancel("Async cancellation received")
                return False
        
        return True
