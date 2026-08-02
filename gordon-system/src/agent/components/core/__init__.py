# Core Runtime Infrastructure
# ============================

"""
Core runtime infrastructure for Gordon agent.

This package provides the foundational runtime substrate including:
- Lifecycle management
- Registry and dependency resolution
- Configuration handling
- Context management
- State management
- Synchronization primitives
- Execution and scheduling
- Observability and integrity validation
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import submodules for type checking
    from core import contracts, types, exceptions, lifecycle
    from core import registry, dependency, configuration, context
    from core import state, synchronization, execution, scheduling
    from core import observability, integrity, kernel, runtime
    from core import testing, health, failures, recovery, diagnostics

# Runtime imports for execution submodule
from .execution import (
    ExecutionState,
    TaskState,
    Priority,
    TaskId,
    TaskResult,
    ParentTaskRef,
    TaskDependencies,
    RetryPolicy,
    ExecutionTimeouts,
    TaskCleanupHook,
    TaskSpec,
    ExecutionContext,
    CancellationSource,
    CancellationToken,
    CleanupCoordinator,
    TaskEvent,
    TaskEventRecord,
    SchedulerError,
    DependencyError,
    TaskTimeoutError,
    TaskCancelledError,
)

from .execution.scheduler import (
    Scheduler,
    SchedulerConfig,
    ReadyQueue,
    WaitingQueue,
    SchedulerState,
)

# Phase 3.5 - New exports for observability, integrity, health, recovery
from .observability import RuntimeEvent, EventSeverity, EventCategory

__all__ = [
    "contracts",
    "types", 
    "exceptions",
    "lifecycle",
    "registry",
    "dependency",
    "configuration",
    "context",
    "state",
    "synchronization",
    "execution",
    "scheduling",
    "observability",
    "integrity",
    "kernel",
    "runtime",
    "testing",
    # Phase 3.5 - Observability, Integrity, Health, Recovery
    "health",
    "failures",
    "recovery",
    "diagnostics",
    # New exports for Phase 3.5
    "RuntimeEvent", "EventSeverity", "EventCategory",
    # Missing exception exports from execution module
    "DependencyError", "TaskTimeoutError", "TaskCancelledError",
]
