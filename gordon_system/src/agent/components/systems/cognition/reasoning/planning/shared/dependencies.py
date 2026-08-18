# Task Dependency - Phase 7.20
# ============================

"""
Canonical Task Dependency contracts for Phase 7.20.

Dependency analysis evaluates causal ordering, resource dependencies,
information flow, parallel execution opportunities, critical paths,
and deadlock potential.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DependencyKind(Enum):
    """Kinds of task dependencies."""
    
    CAUSAL = "causal"                       # Task A must complete before B starts
    RESOURCE = "resource"                   # Shared resource constraint
    INFORMATION = "information"             # Information dependency (data flow)
    SYNCHRONIZATION = "synchronization"     # Parallel task sync point
    PRIORITY = "priority"                   # Ordering by priority, not necessity


class DependencyGraphState(Enum):
    """Dependency graph lifecycle states."""
    
    CONSTRUCTING = "constructing"
    ANALYZING = "analyzing"
    CYCLE_CHECKING = "cycle_checking"
    CRITICAL_PATH_ANALYSIS = "critical_path_analysis"
    PARALLELISM_IDENTIFICATION = "parallelism_identification"
    VALIDATED = "validated"


@dataclass(frozen=True)
class TaskDependency:
    """
    A dependency between tasks in the execution plan.
    
    Dependencies define:
        - Execution order (predecessor → successor)
        - Resource dependencies
        - Causal dependencies
        - Information dependencies
        - Synchronization barriers
    """
    
    # Identity
    dependency_id: str                        # Unique dependency identifier
    
    # Dependency endpoints
    predecessor_task_id: str                  # The task that must complete first
    successor_task_id: str                    # The task that depends on predecessor
    
    # Dependency semantics
    dependency_kind: DependencyKind = DependencyKind.CAUSAL  # What kind of dependency?
    
    # Optional constraints
    delay_seconds: float = 0.0                # Optional delay after predecessor
    resource_constraint: Optional[str] = None  # Shared resource if any
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        predecessor_task_id: str,
        successor_task_id: str,
        dependency_kind: DependencyKind = DependencyKind.CAUSAL,
    ) -> TaskDependency:
        """Create a new task dependency."""
        return cls(
            dependency_id=f"dep:{uuid.uuid4().hex[:16]}",
            predecessor_task_id=predecessor_task_id,
            successor_task_id=successor_task_id,
            dependency_kind=dependency_kind,
        )


@dataclass(frozen=True)
class DependencyGraph:
    """
    A graph representing all dependencies between tasks.
    
    Dependency graphs remain explicit and are used to determine:
        - Causal ordering of tasks
        - Resource dependencies
        - Information flow patterns
        - Parallel execution opportunities
        - Critical paths through the plan
        - Deadlock potential
    """
    
    # Identity
    graph_id: str                             # Unique graph identifier
    
    # Participating tasks and edges
    participating_task_ids: Tuple[str, ...] = ()  # All task IDs in graph
    dependency_edges: Tuple[TaskDependency, ...] = ()  # All dependencies
    
    # Analysis results
    critical_path: Tuple[str, ...] = ()       # Longest path (determines duration)
    parallel_groups: Tuple[Tuple[str, ...], ...] = ()  # Independent task groups
    
    # Graph properties
    is_acyclic: bool = True                   # No circular dependencies
    has_deadlock: bool = False                # No deadlock potential
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @property
    def edge_count(self) -> int:
        """Count edges in dependency graph."""
        return len(self.dependency_edges)
    
    @classmethod
    def create(
        cls,
        participating_task_ids: Tuple[str, ...],
        dependency_edges: Tuple[TaskDependency, ...],
        originating_plan_id: Optional[str] = None,
    ) -> DependencyGraph:
        """Create a new dependency graph."""
        return cls(
            graph_id=f"depgraph:{uuid.uuid4().hex[:16]}",
            participating_task_ids=participating_task_ids,
            dependency_edges=dependency_edges,
            originating_plan_id=originating_plan_id,
            critical_path=tuple(participating_task_ids),  # Would be computed
            parallel_groups=(),  # Would be computed from independent tasks
        )


@dataclass(frozen=True)
class DependencyAnalysis:
    """
    Analysis of dependency graph properties.
    
    Evaluates:
        - Causal ordering correctness
        - Resource dependency coverage
        - Information flow completeness
        - Parallel execution opportunities
        - Critical path identification
        - Deadlock detection
    """
    
    # Identity
    analysis_id: str                          # Unique analysis identifier
    
    # Analyzed graph
    analyzed_graph_id: str                    # Which graph was analyzed?
    
    # Analysis results
    causal_ordering_valid: bool = True        # Is the ordering consistent?
    resource_dependencies_complete: bool = True  # All resources tracked?
    information_flow_complete: bool = True    # All data dependencies captured?
    parallelism_identified: Tuple[str, ...] = ()  # Independent tasks
    critical_path_found: str = ""             # Longest path task ID
    
    # Properties verified
    is_acyclic: bool = True                   # No cycles detected
    deadlock_detected: bool = False           # No deadlocks found
    blocked_tasks: Tuple[str, ...] = ()       # Tasks that can't proceed
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        analyzed_graph_id: str,
        is_acyclic: bool = True,
        deadlock_detected: bool = False,
    ) -> DependencyAnalysis:
        """Create a new dependency analysis."""
        return cls(
            analysis_id=f"depanalysis:{uuid.uuid4().hex[:16]}",
            analyzed_graph_id=analyzed_graph_id,
            is_acyclic=is_acyclic,
            deadlock_detected=deadlock_detected,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TaskDependency",
    "DependencyKind",
    "DependencyGraphState",
    "DependencyGraph",
    "DependencyAnalysis",
]