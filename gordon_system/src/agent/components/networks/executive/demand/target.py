# Executive Demand Target Types
# ==============================

"""
Types for representing demand targets.

A target is a semantic recommendation target, not a live subsystem object.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveDemandTarget:
    """
    Semantic recommendation targets for executive demand.
    
    A target is a semantic recommendation target - it is not a live
    subsystem object.
    """
    
    EXECUTIVE_PROGRAM = "executive_program"
    EXECUTIVE_TASK_SET = "executive_task_set"
    GOAL = "goal"
    COMMITMENT = "commitment"
    STRATEGY = "strategy"
    RULE = "rule"
    CONSTRAINT = "constraint"
    PLAN = "plan"
    REASONING_PROCESS = "reasoning_process"
    DECISION_PROCESS = "decision_process"
    ACTION_SELECTION = "action_selection"
    FOCUS_REVIEW = "focus_review"
    WORKING_MEMORY_REVIEW = "working_memory_review"
    WORKSPACE_REVIEW = "workspace_review"
    MONITORING = "monitoring"
    RECOVERY = "recovery"
    COMMUNICATION = "communication"
    POLICY_REVIEW = "policy_review"
    SECURITY_REVIEW = "security_review"
    GENERAL_EXECUTIVE_STATE = "general_executive_state"

    @classmethod
    def all_targets(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveDemandTarget",)