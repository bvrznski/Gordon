# Planning Plan Set - Phase 7.20
# ==============================

"""
Canonical Plan Set for Phase 7.20.

Plan Sets define the complete set of execution plans for a planning session,
including dependencies, resources, and contingencies.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExecutionPlan:
    """
    An executable plan for achieving a specific objective.
    
    Each execution plan contains:
        - A unique identity
        - The objective being pursued
        - The task graph defining how to achieve the objective
        - Completion criteria
        - Provenance tracking
    """
    
    # Identity
    plan_id: str                              # Unique plan identifier
    
    # Objective reference
    objective_reference: str                  # What is this plan trying to achieve?
    originating_decision: str                 # Which decision created this plan?
    
    # Task graph
    task_graph: Tuple[str, ...] = ()          # Tasks in the execution graph
    dependencies: Tuple[str, ...] = ()        # Dependencies between tasks
    
    # Completion criteria
    completion_criteria: Tuple[str, ...] = () # What defines successful completion?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_plan_id: Optional[str] = None      # If this is a refinement
    parent_task_id: Optional[str] = None      # If this is a sub-plan
    
    @property
    def task_count(self) -> int:
        """Count tasks in the plan."""
        return len(self.task_graph)
    
    @classmethod
    def create(
        cls,
        objective_reference: str,
        originating_decision: str,
        plan_id: Optional[str] = None,
    ) -> ExecutionPlan:
        """Create a new execution plan."""
        return cls(
            plan_id=plan_id or f"plan:{uuid.uuid4().hex[:16]}",
            objective_reference=objective_reference,
            originating_decision=originating_decision,
        )
    
    def with_tasks(self, tasks: Tuple[str, ...]) -> ExecutionPlan:
        """Return a copy with added tasks."""
        return dataclass_replace(
            self,
            task_graph=tasks,
            updated_at_utc=time.time(),
        )
    
    def with_dependencies(self, dependencies: Tuple[str, ...]) -> ExecutionPlan:
        """Return a copy with added dependencies."""
        return dataclass_replace(
            self,
            dependencies=dependencies,
            updated_at_utc=time.time(),
        )


@dataclass(frozen=True)
class PlanSet:
    """
    A complete set of execution plans for a planning session.
    
    Plan Sets are immutable during construction and contain:
        - All participating execution plans
        - Execution scope definition
        - Planning constraints
        - Provenance tracking
    """
    
    # Identity
    plan_set_id: str                          # Unique plan set identifier
    
    # Participating plans
    executing_plans: Tuple[ExecutionPlan, ...] = ()
    
    # Execution scope
    execution_scope: str = "default"          # Context of this plan set
    planning_constraints: Tuple[str, ...] = ()  # Constraints on execution
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_plan_set_id: Optional[str] = None
    originating_decision: str = "unknown"
    
    @property
    def plan_count(self) -> int:
        """Count plans in the set."""
        return len(self.executing_plans)
    
    @classmethod
    def create(
        cls,
        executing_plans: Tuple[ExecutionPlan, ...],
        execution_scope: str = "default",
        originating_decision: str = "unknown",
    ) -> PlanSet:
        """Create a new plan set."""
        return cls(
            plan_set_id=f"planset:{uuid.uuid4().hex[:16]}",
            executing_plans=executing_plans,
            execution_scope=execution_scope,
            originating_decision=originating_decision,
        )
    
    def with_constraints(self, constraints: Tuple[str, ...]) -> PlanSet:
        """Return a copy with added constraints."""
        return dataclass_replace(
            self,
            planning_constraints=constraints,
            updated_at_utc=time.time(),
        )


@dataclass(frozen=True)
class PlanConstruction:
    """
    Record of how a plan was constructed.
    
    Plan construction follows a deterministic pipeline:
        Decision Analysis → Objective Decomposition → Task Construction
        ↓
        Dependency Analysis → Resource Allocation → Contingency Planning
        ↓
        Validation → Publication
    """
    
    # Identity
    construction_id: str                      # Unique construction record identifier
    
    # Construction inputs
    planning_strategy: str                    # Strategy used for construction
    result_plan: ExecutionPlan                # The resulting execution plan
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()         # Diagnostic information
    construction_steps: Tuple[str, ...] = ()  # Steps taken during construction
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        planning_strategy: str,
        result_plan: ExecutionPlan,
        construction_steps: Tuple[str, ...] = (),
        diagnostics: Tuple[str, ...] = (),
    ) -> PlanConstruction:
        """Create a new plan construction record."""
        return cls(
            construction_id=f"construction:{uuid.uuid4().hex[:16]}",
            planning_strategy=planning_strategy,
            result_plan=result_plan,
            construction_steps=construction_steps,
            diagnostics=diagnostics,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionPlan",
    "PlanSet",
    "PlanConstruction",
]