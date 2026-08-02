# Phase 3.4: Execution, Scheduling, Cancellation, and Task Ownership
# ====================================================================

"""
Metadata for Phase 3.4 execution infrastructure.

This phase establishes the execution substrate of Gordon - how work is executed,
not what work means or who performs cognition.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PhaseMetadata:
    """Phase 3.4 metadata and requirements."""
    
    phase_name: str = "EXECUTION, SCHEDULING, CANCELLATION, AND TASK OWNERSHIP"
    phase_number: float = 3.4
    status: str = "IN_PROGRESS"  # TODO: Change to COMPLETE when all gates pass
    
    # Gates that must PASS for Phase 3.4 completion
    required_gates: List[str] = field(default_factory=lambda: [
        "Execution Gate",       # One execution model exists
        "Scheduler Gate",       # One scheduler exists
        "Cancellation Gate",    # Cancellation is deterministic
        "Timeout Gate",         # Timeout policy is explicit
        "Hierarchy Gate",       # Task hierarchy is explicit
        "Cleanup Gate",         # Cleanup is deterministic
        "Shutdown Gate",        # Shutdown is graceful
        "Resource Gate",        # Resource ownership is explicit
        "Import Gate",          # All modules import correctly
        "Structural Gate",      # One authoritative model for each concept
        "Test Gate",            # Phase 3.4 tests pass, plus regressions
    ])
    
    # Core concepts implemented
    task_model: str = """
- TaskId: Unique identifier (wraps EntityId)
- TaskResult: Completed task result with timing, status
- ExecutionState: State machine (CREATED -> QUEUED -> WAITING -> READY -> RUNNING -> [COMPLETED|FAILED])
- Priority: Priority levels (CRITICAL=0, HIGH=1, NORMAL=2, LOW=3)
- ParentTaskRef: Parent-child ownership reference
- TaskDependencies: Required and optional dependency specifications
- RetryPolicy: Explicit retry configuration with exponential backoff
- ExecutionTimeouts: Multiple timeouts (execution, queue, dependency_wait, resource_acquire)
"""
    
    scheduler: str = """
- SchedulerConfig: Configuration for scheduling behavior
- ReadyQueue: Priority queue with deterministic FIFO within same priority
- WaitingQueue: Tasks waiting for dependencies to complete
- SchedulerState: Runtime state (INITIALIZING, RUNNING, SHUTTING_DOWN, STOPPED)
- Scheduler: Main scheduler class with submit/run/cancel/shutdown methods
"""
    
    cancellation: str = """
- CancellationSource: Source of cancellation requests with propagation support
- CancellationToken: Read-only token for tasks to check status
- Cooperative: Tasks must check token and stop themselves gracefully
- Propagation: Children inherit parent cancellation state
"""
    
    cleanup: str = """
- CleanupCoordinator: Coordinates cleanup in reverse ownership order
- TaskCleanupHook: Hooks called during task cleanup
- Deterministic: Reverse order ensures proper resource release
"""
    
    shutdown: str = """
- Graceful: Stop accepting -> Cancel queued -> Wait running -> Cleanup
- Timeout support for each phase
- State machine transitions (SHUTTING_DOWN -> STOPPED)
"""

from dataclasses import field

__all__ = ["PhaseMetadata"]