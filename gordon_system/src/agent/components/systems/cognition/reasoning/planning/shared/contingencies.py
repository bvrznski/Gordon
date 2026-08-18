# Contingency Planning - Phase 7.20
# ================================

"""
Canonical Contingency Planning contracts for Phase 7.20.

Contingency management evaluates failure recovery, alternative execution paths,
rollback strategies, resource substitution, dynamic replanning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ContingencyKind(Enum):
    """Kinds of contingencies."""
    
    FAILURE_RECOVERY = "failure_recovery"           # What to do when a task fails
    ALTERNATIVE_PATH = "alternative_path"           # Alternative way to achieve objective
    ROLLBACK_STRATEGY = "rollback_strategy"         # How to revert changes
    RESOURCE_SUBSTITUTION = "resource_substitution"  # Backup resources to use
    DYNAMIC_REPLANNING = "dynamic_replanning"       # Replan when conditions change


class ContingencyState(Enum):
    """Contingency lifecycle states."""
    
    CREATED = "created"
    TRIGGER_CONDITION_ANALYSIS = "trigger_condition_analysis"
    RECOVERY_STRATEGY_DESIGN = "recovery_strategy_design"
    FALLBACK_PLAN_CONSTRUCTION = "fallback_plan_construction"
    VALIDATED = "validated"
    ACTIVE = "active"  # Contingency is currently in effect


@dataclass(frozen=True)
class ContingencyPlan:
    """
    A plan for handling exceptional circumstances.
    
    Contingencies define:
        - Triggering conditions (when to activate)
        - Recovery strategy
        - Fallback plan(s)
        - Alternative paths
    """
    
    # Identity
    contingency_id: str                       # Unique contingency identifier
    
    # Triggering conditions
    triggering_conditions: Tuple[str, ...] = ()  # When should this activate?
    
    # Recovery strategy
    recovery_strategy: str = "default"         # How to recover?
    
    # Fallback plan
    fallback_plan_tasks: Tuple[str, ...] = ()  # Alternative tasks to execute
    
    # Kind of contingency
    contingency_kind: ContingencyKind = ContingencyKind.FAILURE_RECOVERY
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    primary_task_id: Optional[str] = None      # Which task is this contingenting?
    
    @classmethod
    def create(
        cls,
        triggering_conditions: Tuple[str, ...],
        recovery_strategy: str = "default",
        fallback_plan_tasks: Tuple[str, ...] = (),
        contingency_kind: ContingencyKind = ContingencyKind.FAILURE_RECOVERY,
    ) -> ContingencyPlan:
        """Create a new contingency plan."""
        return cls(
            contingency_id=f"contingency:{uuid.uuid4().hex[:16]}",
            triggering_conditions=triggering_conditions,
            recovery_strategy=recovery_strategy,
            fallback_plan_tasks=fallback_plan_tasks,
            contingency_kind=contingency_kind,
        )


@dataclass(frozen=True)
class ContingencyManagement:
    """
    Management of all contingencies in a plan.
    
    Evaluates:
        - Failure recovery completeness
        - Alternative execution path coverage
        - Rollback strategy adequacy
        - Resource substitution availability
        - Dynamic replanning capability
    """
    
    # Identity
    management_id: str                        # Unique management record identifier
    
    # Contingency graph
    contingency_graph: Tuple[ContingencyPlan, ...] = ()
    
    # Recovery policy
    recovery_policy: str = "automatic"         # How are recoveries triggered?
    
    # Triggering conditions (aggregated)
    all_triggering_conditions: Tuple[str, ...] = ()  # All conditions tracked
    
    # Coverage metrics
    total_contingencies: int = 0               # Total contingency plans
    covered_tasks: int = 0                     # Tasks with contingencies
    coverage_percentage: float = 0.0           # % of tasks covered
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        contingency_graph: Tuple[ContingencyPlan, ...],
        recovery_policy: str = "automatic",
    ) -> ContingencyManagement:
        """Create a new contingency management record."""
        covered = sum(1 for c in contingency_graph if c.primary_task_id)
        
        return cls(
            management_id=f"contmgmt:{uuid.uuid4().hex[:16]}",
            contingency_graph=contingency_graph,
            recovery_policy=recovery_policy,
            total_contingencies=len(contingency_graph),
            covered_tasks=covered,
            coverage_percentage=covered / max(len(contingency_graph), 1) * 100,
        )


@dataclass(frozen=True)
class RecoveryTrigger:
    """
    A specific trigger that activates recovery.
    
    When conditions match, the corresponding contingency plan is activated.
    """
    
    # Identity
    trigger_id: str                           # Unique trigger identifier
    
    # Triggering condition
    condition_description: str                # What triggers this?
    triggering_plan_id: Optional[str] = None  # Which contingency does it activate?
    
    # Activation info
    triggered_at_utc: Optional[float] = None  # When was it triggered?
    is_active: bool = False                   # Currently active?
    
    # Recovery result (if completed)
    recovery_success: Optional[bool] = None   # Did recovery succeed?
    recovery_duration_seconds: float = 0.0     # How long did it take?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        condition_description: str,
    ) -> RecoveryTrigger:
        """Create a new recovery trigger."""
        return cls(
            trigger_id=f"trigger:{uuid.uuid4().hex[:16]}",
            condition_description=condition_description,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ContingencyPlan",
    "ContingencyKind",
    "ContingencyState",
    "ContingencyManagement",
    "RecoveryTrigger",
]