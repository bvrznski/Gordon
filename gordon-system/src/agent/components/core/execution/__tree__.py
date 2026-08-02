# Core Execution Package Tree
# ============================

"""
Tree structure for core execution package.

This module documents the hierarchy of execution-related components.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ModuleNode:
    """A node in the package tree."""
    
    name: str
    description: str
    children: List["ModuleNode"] = field(default_factory=list)


# Main execution module
root = ModuleNode(
    name="core/execution/",
    description="Execution substrate for Gordon agent system"
)

# Task model
task_model = ModuleNode(
    name="task-model/",
    description="Task representation and lifecycle states"
)

tasks = [
    ModuleNode("TaskId", "Unique task identifier"),
    ModuleNode("ParentTaskRef", "Parent-child ownership reference"),
    ModuleNode("TaskDependencies", "Required and optional dependencies"),
    ModuleNode("RetryPolicy", "Explicit retry configuration"),
    ModuleNode("ExecutionTimeouts", "Multiple timeout policies"),
    ModuleNode("TaskCleanupHook", "Cleanup hooks for deterministic release"),
    ModuleNode("TaskResult", "Completed task result with timing info"),
]

# Execution states
execution_states = ModuleNode(
    name="execution-states/",
    description="State machine for task execution"
)

states = [
    ModuleNode("ExecutionState", """
CREATED -> QUEUED -> WAITING -> READY -> RUNNING -> [COMPLETED|FAILED]
                                ^              |
                                |              v
                             CANCELLING     TIMED_OUT
                                |
                             CANCELLED"""),
    ModuleNode("TaskState", "Lifecycle state (separate from execution state)"),
]

# Priority levels
priority = ModuleNode(
    name="priority/",
    description="Execution priority levels"
)

priorities = [
    ModuleNode("Priority.CRITICAL", "0 - Must run immediately"),
    ModuleNode("Priority.HIGH", "1 - High importance, short delay acceptable"),
    ModuleNode("Priority.NORMAL", "2 - Standard priority"),
    ModuleNode("Priority.LOW", "3 - Can be delayed if needed"),
]

# Scheduler
scheduler = ModuleNode(
    name="scheduler/",
    description="Deterministic task scheduler"
)

scheduler_components = [
    ModuleNode("SchedulerConfig", "Configuration for scheduling behavior"),
    ModuleNode("ReadyQueue", "Priority queue with deterministic FIFO"),
    ModuleNode("WaitingQueue", "Tasks waiting for dependencies"),
    ModuleNode("SchedulerState", "Runtime state (INITIALIZING, RUNNING, etc.)"),
    ModuleNode("RunningTaskInfo", "Currently running task information"),
    ModuleNode("Scheduler", "Main scheduler class with submit/run/cancel/shutdown"),
    ModuleNode("TaskHandle", "Handle to submitted task for tracking"),
]

# Cancellation
cancellation = ModuleNode(
    name="cancellation/",
    description="Cooperative cancellation system"
)

cancellation_components = [
    ModuleNode("CancellationSource", "Source of cancellation with propagation"),
    ModuleNode("CancellationToken", "Read-only token for tasks"),
    ModuleNode("TaskCancelledError", "Raised when task is cancelled"),
]

# Timeout handling
timeout = ModuleNode(
    name="timeouts/",
    description="Multiple timeout policies"
)

timeout_components = [
    ModuleNode("ExecutionTimeouts.execution", "How long the task can run"),
    ModuleNode("ExecutionTimeouts.queue", "Max time in queue before scheduling"),
    ModuleNode("ExecutionTimeouts.dependency_wait", "Max time waiting for dependencies"),
    ModuleNode("TaskTimeoutError", "Raised when execution exceeds timeout"),
]

# Cleanup
cleanup = ModuleNode(
    name="cleanup/",
    description="Deterministic cleanup coordination"
)

cleanup_components = [
    ModuleNode("CleanupCoordinator", "Coordinates reverse-order cleanup"),
    ModuleNode("TaskCleanupHook", "Hooks called during task cleanup"),
]

# Shutdown
shutdown = ModuleNode(
    name="shutdown/",
    description="Graceful shutdown sequence"
)

shutdown_components = [
    ModuleNode("ShutdownSequence", """
1. Stop accepting new tasks
2. Cancel all queued tasks
3. Wait for running tasks to complete (or timeout)
4. Cleanup resources"""),
]

# Context
context = ModuleNode(
    name="context/",
    description="Temporary, task-scoped execution context"
)

context_components = [
    ModuleNode("ExecutionContext", "Task-scoped context with cancellation token"),
]

# Observability
observability = ModuleNode(
    name="observability/",
    description="Structured event records"
)

observability_components = [
    ModuleNode("TaskEvent", "Types of execution events"),
    ModuleNode("TaskEventRecord", "Event record with timing and state info"),
]

# Build tree structure
task_model.children = tasks
execution_states.children = states
scheduler.children = scheduler_components
cancellation.children = cancellation_components
timeout.children = timeout_components
cleanup.children = cleanup_components
shutdown.children = shutdown_components
context.children = context_components
observability.children = observability_components

root.children = [
    task_model,
    execution_states,
    priority,
    scheduler,
    cancellation,
    timeout,
    cleanup,
    shutdown,
    context,
    observability,
]

__all__ = ["ModuleNode", "root", "task_model", "scheduler", "cancellation"]