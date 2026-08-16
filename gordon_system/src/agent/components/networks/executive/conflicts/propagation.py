# Executive Conflict Propagation Model
# =====================================

"""
Types for assessing how conflicts may propagate through the executive
organization.

Propagation assessment helps identify secondary effects and cascading
impact that may require additional attention.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictPropagationTarget:
    """
    Possible targets for conflict propagation.
    """
    
    PARENT_PROGRAM = "parent_program"
    CHILD_PROGRAM = "child_program"
    SIBLING_PROGRAM = "sibling_program"
    TASK_SET = "task_set"
    GOAL_HIERARCHY = "goal_hierarchy"
    COMMITMENT_SET = "commitment_set"
    DECISION_PROCESS = "decision_process"
    ACTION_SELECTION = "action_selection"
    WORKING_MEMORY_REQUIREMENTS = "working_memory_requirements"
    FOCUS_REQUIREMENTS = "focus_requirements"
    WORKSPACE_REVIEW = "workspace_review"
    MONITORING_REQUIREMENTS = "monitoring_requirements"
    COMMUNICATION_REQUIREMENTS = "communication_requirements"


@dataclass(frozen=True)
class ExecutiveConflictPropagation:
    """
    Structured assessment of how an executive conflict may propagate.
    """
    
    target_ids: Tuple[str, ...] = ()
    impact_class: str = "moderate"
    certainty_class: str = "unknown"
    cascading_risk_class: str = "low"
    timing_estimate_cycles: int = 0
    mitigation_targets: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = (
    "ExecutiveConflictPropagationTarget",
    "ExecutiveConflictPropagation",
)