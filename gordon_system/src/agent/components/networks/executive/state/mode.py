# Executive State Modes
# =====================

"""
Semantic executive modes for the Executive Network.

Executive modes are cognitive states, NOT runtime process or scheduler states.
They represent how the executive is currently organizing and evaluating cognition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Literal
from enum import Enum, auto


# =============================================================================
# EXECUTIVE MODE ENUM
# =============================================================================


class ExecutiveMode(Enum):
    """
    Semantic executive modes.
    
    These are cognitive modes, NOT runtime process states:
        - UNINITIALIZED: State has not been initialized yet
        - ORIENTING: Initial orientation and context gathering
        - TASK_SET_FORMATION: Forming or revising task sets
        - GOAL_MAINTENANCE: Maintaining active goals and commitments
        - TASK_EXECUTION_SUPPORT: Supporting ongoing task execution
        - CONFLICT_REVIEW: Reviewing conflicts and their resolution
        - CONTROL_ALLOCATION: Allocating control resources
        - PERFORMANCE_REVIEW: Reviewing performance metrics
        - STRATEGY_REVIEW: Evaluating and revising strategy
        - DECISION_PREPARATION: Preparing for decision points
        - SWITCH_REVIEW: Assessing need for task/strategy switching
        - RECOVERY: Recovering from errors or failures
        - WAITING: Waiting for external results or decisions
        - SUSPENDED: Temporarily suspended (external decision)
        - IDLE_EXECUTIVE_MAINTENANCE: Idle-time maintenance tasks
        - COMPLETED: Executive evaluation completed successfully
        - FAILED: Executive evaluation failed
    
    These modes are NOT:
        * Process states
        * Scheduler states
        * Thread states
        * Runtime activation flags
    """
    
    UNINITIALIZED = "uninitialized"
    """State has not been initialized yet."""
    
    ORIENTING = "orienting"
    """Initial orientation and context gathering."""
    
    TASK_SET_FORMATION = "task_set_formation"
    """Forming or revising task sets."""
    
    GOAL_MAINTENANCE = "goal_maintenance"
    """Maintaining active goals and commitments."""
    
    TASK_EXECUTION_SUPPORT = "task_execution_support"
    """Supporting ongoing task execution."""
    
    CONFLICT_REVIEW = "conflict_review"
    """Reviewing conflicts and their resolution."""
    
    CONTROL_ALLOCATION = "control_allocation"
    """Allocating control resources."""
    
    PERFORMANCE_REVIEW = "performance_review"
    """Reviewing performance metrics."""
    
    STRATEGY_REVIEW = "strategy_review"
    """Evaluating and revising strategy."""
    
    DECISION_PREPARATION = "decision_preparation"
    """Preparing for decision points."""
    
    SWITCH_REVIEW = "switch_review"
    """Assessing need for task/strategy switching."""
    
    RECOVERY = "recovery"
    """Recovering from errors or failures."""
    
    WAITING = "waiting"
    """Waiting for external results or decisions."""
    
    SUSPENDED = "suspended"
    """Temporarily suspended (external decision)."""
    
    IDLE_EXECUTIVE_MAINTENANCE = "idle_executive_maintenance"
    """Idle-time maintenance tasks."""
    
    COMPLETED = "completed"
    """Executive evaluation completed successfully."""
    
    FAILED = "failed"
    """Executive evaluation failed."""
    
    @property
    def is_terminal(self) -> bool:
        """Check if this mode is terminal (no further transitions)."""
        return self in (
            ExecutiveMode.COMPLETED,
            ExecutiveMode.FAILED,
        )
    
    @property
    def is_suspended(self) -> bool:
        """Check if the executive is suspended."""
        return self == ExecutiveMode.SUSPENDED
    
    @property
    def is_waiting(self) -> bool:
        """Check if the executive is waiting for external results."""
        return self == ExecutiveMode.WAITING


# =============================================================================
# MODE TRANSITION VALIDATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveModeTransitionRule:
    """
    Rule defining valid mode transitions.
    
    Each rule specifies which source modes can transition to which target modes,
    under what conditions, and with what authority requirements.
    """
    
    from_modes: Tuple[ExecutiveMode, ...]
    """Source modes that may transition."""
    
    to_mode: ExecutiveMode
    """Target mode for the transition."""
    
    condition: Literal["always", "on_external_result", "on_authority", "on_failure"] = "always"
    """Condition required for the transition."""
    
    authority_required: bool = False
    """Whether explicit authority is required."""
    
    @property
    def description(self) -> str:
        """Get a human-readable description of the rule."""
        return f"{', '.join(m.value for m in self.from_modes)} -> {self.to_mode.value}"


# =============================================================================
# VALID TRANSITION MAP
# =============================================================================


EXECUTIVE_MODE_TRANSITIONS: Tuple[ExecutiveModeTransitionRule, ...] = (
    # Initial states
    ExecutiveModeTransitionRule(
        from_modes=(ExecutiveMode.UNINITIALIZED,),
        to_mode=ExecutiveMode.ORIENTING,
        condition="always",
        authority_required=False,
    ),
    
    # Orienting can lead to task formation
    ExecutiveModeTransitionRule(
        from_modes=(ExecutiveMode.ORIENTING,),
        to_mode=ExecutiveMode.TASK_SET_FORMATION,
        condition="always",
        authority_required=False,
    ),
    
    # Task formation leads to goal maintenance or execution support
    ExecutiveModeTransitionRule(
        from_modes=(ExecutiveMode.TASK_SET_FORMATION,),
        to_mode=ExecutiveMode.GOAL_MAINTENANCE,
        condition="always",
        authority_required=False,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(ExecutiveMode.TASK_SET_FORMATION,),
        to_mode=ExecutiveMode.TASK_EXECUTION_SUPPORT,
        condition="on_external_result",
        authority_required=False,
    ),
    
    # Goal maintenance can lead to various assessments
    ExecutiveModeTransitionRule(
        from_modes=(
            ExecutiveMode.GOAL_MAINTENANCE,
            ExecutiveMode.TASK_EXECUTION_SUPPORT,
        ),
        to_mode=ExecutiveMode.CONFLICT_REVIEW,
        condition="on_failure",
        authority_required=False,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(
            ExecutiveMode.GOAL_MAINTENANCE,
            ExecutiveMode.TASK_EXECUTION_SUPPORT,
        ),
        to_mode=ExecutiveMode.CONTROL_ALLOCATION,
        condition="always",
        authority_required=True,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(
            ExecutiveMode.GOAL_MAINTENANCE,
            ExecutiveMode.TASK_EXECUTION_SUPPORT,
        ),
        to_mode=ExecutiveMode.PERFORMANCE_REVIEW,
        condition="always",
        authority_required=False,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(
            ExecutiveMode.GOAL_MAINTENANCE,
            ExecutiveMode.TASK_EXECUTION_SUPPORT,
        ),
        to_mode=ExecutiveMode.STRATEGY_REVIEW,
        condition="on_failure",
        authority_required=True,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(
            ExecutiveMode.GOAL_MAINTENANCE,
            ExecutiveMode.TASK_EXECUTION_SUPPORT,
        ),
        to_mode=ExecutiveMode.DECISION_PREPARATION,
        condition="always",
        authority_required=False,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(
            ExecutiveMode.GOAL_MAINTENANCE,
            ExecutiveMode.TASK_EXECUTION_SUPPORT,
        ),
        to_mode=ExecutiveMode.SWITCH_REVIEW,
        condition="on_failure",
        authority_required=True,
    ),
    
    # Waiting states
    ExecutiveModeTransitionRule(
        from_modes=tuple(m for m in ExecutiveMode if not m.is_terminal),
        to_mode=ExecutiveMode.WAITING,
        condition="always",
        authority_required=False,
    ),
    
    # Resumption from waiting
    ExecutiveModeTransitionRule(
        from_modes=(ExecutiveMode.WAITING,),
        to_mode=ExecutiveMode.GOAL_MAINTENANCE,
        condition="on_external_result",
        authority_required=False,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(ExecutiveMode.WAITING,),
        to_mode=ExecutiveMode.CONFLICT_REVIEW,
        condition="on_failure",
        authority_required=False,
    ),
    
    # Suspension
    ExecutiveModeTransitionRule(
        from_modes=tuple(m for m in ExecutiveMode if not m.is_terminal),
        to_mode=ExecutiveMode.SUSPENDED,
        condition="always",
        authority_required=True,
    ),
    ExecutiveModeTransitionRule(
        from_modes=(ExecutiveMode.SUSPENDED,),
        to_mode=ExecutiveMode.GOAL_MAINTENANCE,
        condition="on_authority",
        authority_required=True,
    ),
    
    # Completion and failure
    ExecutiveModeTransitionRule(
        from_modes=tuple(m for m in ExecutiveMode if not m.is_terminal),
        to_mode=ExecutiveMode.COMPLETED,
        condition="always",
        authority_required=False,
    ),
    ExecutiveModeTransitionRule(
        from_modes=tuple(m for m in ExecutiveMode if not m.is_terminal),
        to_mode=ExecutiveMode.FAILED,
        condition="on_failure",
        authority_required=False,
    ),
)


def get_valid_transitions(mode: ExecutiveMode) -> Tuple[ExecutiveMode, ...]:
    """
    Get all valid target modes from the given source mode.
    
    Args:
        mode: The current executive mode
        
    Returns:
        Tuple of valid target modes
    """
    result = []
    for rule in EXECUTIVE_MODE_TRANSITIONS:
        if mode in rule.from_modes:
            result.append(rule.to_mode)
    return tuple(result)


def is_transition_valid(from_mode: ExecutiveMode, to_mode: ExecutiveMode) -> bool:
    """
    Check if a mode transition is valid.
    
    Args:
        from_mode: Source mode
        to_mode: Target mode
        
    Returns:
        True if the transition is allowed
    """
    return to_mode in get_valid_transitions(from_mode)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveMode",
    "ExecutiveModeTransitionRule",
    "EXECUTIVE_MODE_TRANSITIONS",
    "get_valid_transitions",
    "is_transition_valid",
)