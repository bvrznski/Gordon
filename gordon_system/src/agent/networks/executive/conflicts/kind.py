# Executive Conflict Kind Types
# ==============================

"""
Types for classifying executive conflicts into semantic categories.

Each conflict kind represents a distinct category that may require different
assessment or resolution approaches.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveConflictKind:
    """
    Typed taxonomy of executive conflict kinds.
    
    Each kind represents a distinct semantic category of conflict.
    """
    
    # Goal and commitment conflicts
    GOAL_GOAL_CONFLICT = "goal_goal_conflict"
    COMMITMENT_COMMITMENT_CONFLICT = "commitment_commitment_conflict"
    GOAL_COMMITMENT_CONFLICT = "goal_commitment_conflict"
    
    # Program and task-set conflicts
    PROGRAM_PROGRAM_CONFLICT = "program_program_conflict"
    TASK_SET_TASK_SET_CONFLICT = "task_set_task_set_conflict"
    PROGRAM_TASK_SET_CONFLICT = "program_task_set_conflict"
    
    # Priority and strategy conflicts
    PRIORITY_CONFLICT = "priority_conflict"
    STRATEGY_CONFLICT = "strategy_conflict"
    
    # Rule, constraint, policy, security conflicts
    RULE_CONFLICT = "rule_conflict"
    CONSTRAINT_CONFLICT = "constraint_conflict"
    POLICY_CONFLICT = "policy_conflict"
    SECURITY_CONFLICT = "security_conflict"
    
    # Authority and source conflicts
    AUTHORITY_CONFLICT = "authority_conflict"
    
    # Plan, reasoning, evidence conflicts
    PLAN_CONFLICT = "plan_conflict"
    REASONING_CONFLICT = "reasoning_conflict"
    EVIDENCE_CONFLICT = "evidence_conflict"
    INTERPRETATION_CONFLICT = "interpretation_conflict"
    
    # Prediction and outcome conflicts
    PREDICTION_OBSERVATION_CONFLICT = "prediction_observation_conflict"
    EXPECTATION_OUTCOME_CONFLICT = "expectation_outcome_conflict"
    
    # Decision and action conflicts
    DECISION_CANDIDATE_CONFLICT = "decision_candidate_conflict"
    ACTION_CANDIDATE_CONFLICT = "action_candidate_conflict"
    
    # Focus and attention conflicts
    FOCUS_TASK_SET_CONFLICT = "focus_task_set_conflict"
    
    # Motivation and resource conflicts
    MOTIVATION_COMMITMENT_CONFLICT = "motivation_commitment_conflict"
    WORKING_MEMORY_REQUIREMENT_CONFLICT = "working_memory_requirement_conflict"
    WORKSPACE_CONTENT_CONFLICT = "workspace_content_conflict"
    CAPABILITY_REQUIREMENT_CONFLICT = "capability_requirement_conflict"
    RESOURCE_CONSTRAINT_CONFLICT = "resource_constraint_conflict"
    
    # Temporal and dependency conflicts
    TEMPORAL_CONFLICT = "temporal_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    
    # Completion and recovery conflicts
    COMPLETION_CRITERIA_CONFLICT = "completion_criteria_conflict"
    RECOVERY_CONFLICT = "recovery_conflict"
    
    # Communication and general conflicts
    COMMUNICATION_CONFLICT = "communication_conflict"
    GENERAL_EXECUTIVE_CONFLICT = "general_executive_conflict"
    UNKNOWN = "unknown"

    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveConflictKind",)