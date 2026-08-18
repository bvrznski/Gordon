# Planned Task - Phase 7.20
# =========================

"""
Canonical Planned Task contracts for Phase 7.20.

Task management evaluates task hierarchy, granularity, execution readiness,
dependency completeness, termination conditions, and resource requirements.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class TaskKind(Enum):
    """Kinds of planned tasks."""
    
    ATOMIC = "atomic"                 # Simplest actionable unit
    COMPOSITE = "composite"           # Container for subtasks
    DECISION = "decision"             # A decision point in the plan
    CHECKPOINT = "checkpoint"         # Verification point
    SYNCHRONIZATION = "synchronization"  # Parallel task sync point


class TaskState(Enum):
    """Task lifecycle states."""
    
    CREATED = "created"
    PRECONDITIONS_CHECKING = "preconditions_checking"
    RESOURCES_ALLOCATING = "resources_allocating"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class PlannedTask:
    """
    A task that is part of an execution plan.
    
    Each planned task contains:
        - An explicit identity
        - The objective being pursued
        - Required resources and preconditions
        - Task provenance tracking
    """
    
    # Identity
    task_id: str                              # Unique task identifier
    
    # Objective reference
    objective_reference: str                  # What does this task achieve?
    parent_task_id: Optional[str] = None      # If this is a subtask
    
    # Task properties
    task_kind: TaskKind = TaskKind.ATOMIC   # What kind of task?
    task_depth: int = 0                       # Hierarchy depth (0 = top-level)
    
    # Requirements
    required_resources: Tuple[str, ...] = ()  # Resources needed to execute
    preconditions: Tuple[str, ...] = ()       # Pre-execution conditions
    postconditions: Tuple[str, ...] = ()      # Post-execution guarantees
    
    # Completion criteria
    completion_criteria: str = "default"      # How do we know it's done?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    source_task_id: Optional[str] = None      # If this is a refinement
    
    @property
    def is_leaf(self) -> bool:
        """Check if task is a leaf (atomic or has no subtasks)."""
        return self.task_kind in (TaskKind.ATOMIC, TaskKind.CHECKPOINT)
    
    @classmethod
    def create(
        cls,
        objective_reference: str,
        task_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        task_kind: TaskKind = TaskKind.ATOMIC,
        task_depth: int = 0,
    ) -> PlannedTask:
        """Create a new planned task."""
        return cls(
            task_id=task_id or f"task:{uuid.uuid4().hex[:16]}",
            objective_reference=objective_reference,
            parent_task_id=parent_task_id,
            task_kind=task_kind,
            task_depth=task_depth,
        )
    
    def with_resources(self, resources: Tuple[str, ...]) -> PlannedTask:
        """Return a copy with added required resources."""
        return dataclass_replace(
            self,
            required_resources=resources,
            updated_at_utc=time.time(),
        )
    
    def with_conditions(
        self,
        preconditions: Tuple[str, ...],
        postconditions: Tuple[str, ...],
    ) -> PlannedTask:
        """Return a copy with added conditions."""
        return dataclass_replace(
            self,
            preconditions=preconditions,
            postconditions=postconditions,
            updated_at_utc=time.time(),
        )


@dataclass(frozen=True)
class TaskManagement:
    """
    Evaluation of task management quality.
    
    Task management evaluates:
        - Task hierarchy completeness
        - Task granularity appropriateness
        - Execution readiness metrics
        - Dependency completeness
        - Termination condition coverage
        - Resource requirement clarity
    """
    
    # Identity
    management_id: str                        # Unique management evaluation identifier
    
    # Participating tasks
    participating_tasks: Tuple[PlannedTask, ...] = ()
    
    # Decomposition strategy
    decomposition_strategy: str = "default"   # Strategy used for decomposition
    
    # Readiness metrics
    total_tasks: int = 0                      # Total task count
    leaf_tasks: int = 0                       # Leaf (atomic) tasks
    ready_tasks: int = 0                      # Ready-to-execute tasks
    dependencies_complete: bool = False       # Are all dependencies satisfied?
    
    # Quality metrics
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        participating_tasks: Tuple[PlannedTask, ...],
        decomposition_strategy: str = "default",
    ) -> TaskManagement:
        """Create a new task management evaluation."""
        leaf_count = sum(1 for t in participating_tasks if t.is_leaf)
        ready_count = sum(1 for t in participating_tasks if t.preconditions == ())
        
        return cls(
            management_id=f"taskmgmt:{uuid.uuid4().hex[:16]}",
            participating_tasks=participating_tasks,
            decomposition_strategy=decomposition_strategy,
            total_tasks=len(participating_tasks),
            leaf_tasks=leaf_count,
            ready_tasks=ready_count,
            dependencies_complete=True,  # Would be set by dependency analysis
        )


@dataclass(frozen=True)
class TaskDecomposition:
    """
    Record of how a task was decomposed.
    
    Decomposition breaks objectives into:
        - Major tasks
        - Subtasks  
        - Atomic actions
        - Dependencies between them
        - Resource assignments
    """
    
    # Identity
    decomposition_id: str                     # Unique decomposition record identifier
    
    # Original objective
    original_objective: str                   # What was being decomposed?
    
    # Decomposition result
    resulting_tasks: Tuple[PlannedTask, ...] = ()
    dependency_edges: Tuple[str, ...] = ()    # Task-to-task dependencies
    
    # Decomposition strategy
    decomposition_strategy: str = "default"
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_task_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        original_objective: str,
        resulting_tasks: Tuple[PlannedTask, ...],
        decomposition_strategy: str = "default",
    ) -> TaskDecomposition:
        """Create a new task decomposition record."""
        return cls(
            decomposition_id=f"decomposition:{uuid.uuid4().hex[:16]}",
            original_objective=original_objective,
            resulting_tasks=resulting_tasks,
            decomposition_strategy=decomposition_strategy,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PlannedTask",
    "TaskKind",
    "TaskState",
    "TaskManagement",
    "TaskDecomposition",
]