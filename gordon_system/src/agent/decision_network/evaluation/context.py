# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Context
# =========================

"""
Action Evaluation Context type definitions.

This module defines the context types that provide the environment for evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# ACTION EVALUATION CONTEXT ID TYPES
# =============================================================================

EvaluationContextId = str
"""Unique identifier for an evaluation context."""


# =============================================================================
# GOAL REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class GoalReference:
    """
    Reference to a goal in the evaluation context.
    
    PROPERTIES:
        • goal_id: Unique identifier for the goal
        • purpose: What this goal is trying to achieve
        • priority: Goal priority level (0.0 to 1.0)
    """
    
    goal_id: EvaluationContextId
    """Unique identifier for this goal."""
    
    purpose: str = ""
    """What this goal is trying to achieve."""
    
    priority: float = 0.5
    """Goal priority level (0.0 to 1.0)."""


# =============================================================================
# STRATEGY REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class StrategyReference:
    """
    Reference to a strategy in the evaluation context.
    
    PROPERTIES:
        • strategy_id: Unique identifier for the strategy
        • description: Description of the strategy
        • scope: What this strategy applies to
    """
    
    strategy_id: EvaluationContextId
    """Unique identifier for this strategy."""
    
    description: str = ""
    """Description of the strategy."""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """What this strategy applies to (goal IDs, action kinds, etc.)."""


# =============================================================================
# POLICY REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class PolicyReference:
    """
    Reference to a policy in the evaluation context.
    
    PROPERTIES:
        • policy_id: Unique identifier for the policy
        • kind: Kind of policy (security, compliance, etc.)
        • constraint_type: Type of constraint (must, should, may not)
    """
    
    policy_id: EvaluationContextId
    """Unique identifier for this policy."""
    
    kind: str = "general"
    """Kind of policy (security, compliance, ethics, etc.)."""
    
    constraint_type: str = "must"
    """Type of constraint (must, should, may not)."""


# =============================================================================
# WORKSPACE STATE REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceStateReference:
    """
    Reference to workspace state in the evaluation context.
    
    PROPERTIES:
        • workspace_id: Unique identifier for the workspace
        • active_goals: IDs of currently active goals
        • active_strategies: Active strategy references
        • working_memory_content: Current working memory content
    """
    
    workspace_id: EvaluationContextId
    """Unique identifier for this workspace."""
    
    active_goals: Tuple[GoalReference, ...] = field(default_factory=tuple)
    """Currently active goals."""
    
    active_strategies: Tuple[StrategyReference, ...] = field(default_factory=tuple)
    """Active strategies."""
    
    working_memory_content: Tuple[str, ...] = field(default_factory=tuple)
    """Current working memory content references."""


# =============================================================================
# ACTION EVALUATION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionEvaluationContext:
    """
    Context for evaluating Action Candidates.
    
    This provides the environment information needed to evaluate candidates:
    goals, strategies, policies, workspace state, and other contextual factors.
    
    PROPERTIES:
        • context_id: Unique identifier for this evaluation context
        • revision: Context revision number (for version tracking)
        • active_goals: Goals that must be considered in evaluation
        • active_strategies: Strategies that constrain candidate selection
        • applicable_policies: Policies that candidates must satisfy
        • workspace_state: Current workspace state information
        • environmental_constraints: External constraints on actions
        • resource_constraints: Resource availability information
    
    NOT RESPONSIBLE FOR:
        - Making evaluation decisions
        - Storing actual candidate data
        - Executing or scheduling actions
    """
    
    context_id: EvaluationContextId
    """Unique identifier for this evaluation context."""
    
    revision: int = 1
    """Monotonically increasing revision number."""
    
    active_goals: Tuple[GoalReference, ...] = field(default_factory=tuple)
    """Goals that must be considered in evaluation."""
    
    active_strategies: Tuple[StrategyReference, ...] = field(default_factory=tuple)
    """Strategies that constrain candidate selection."""
    
    applicable_policies: Tuple[PolicyReference, ...] = field(default_factory=tuple)
    """Policies that candidates must satisfy."""
    
    workspace_state: WorkspaceStateReference | None = None
    """Current workspace state information."""
    
    environmental_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """External constraints on actions (time, environment, etc.)."""
    
    resource_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Resource availability information."""

    @classmethod
    def empty(cls) -> ActionEvaluationContext:
        """
        Create an empty evaluation context.
        
        Returns:
            New ActionEvaluationContext with no constraints or goals
        """
        return cls(
            context_id="eval_context_empty",
            active_goals=(),
            active_strategies=(),
            applicable_policies=(),
        )
    
    @classmethod
    def from_workspace(
        cls,
        workspace: WorkspaceStateReference,
        context_id: EvaluationContextId = "",
    ) -> ActionEvaluationContext:
        """
        Create an evaluation context from workspace state.
        
        Args:
            workspace: Workspace state to derive context from
            context_id: Optional unique identifier for this context
            
        Returns:
            New ActionEvaluationContext based on the workspace state
        """
        return cls(
            context_id=context_id or f"eval_context_{workspace.workspace_id}",
            active_goals=tuple(workspace.active_goals),
            active_strategies=tuple(workspace.active_strategies),
            applicable_policies=(),
            workspace_state=workspace,
        )