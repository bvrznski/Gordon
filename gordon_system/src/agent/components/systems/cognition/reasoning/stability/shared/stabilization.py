# Stabilization Management - Phase 7.26
# =====================================

"""
Canonical Stabilization Management.

Stabilization determines safe configuration, behavior throttling,
adaptation rollback, resource redistribution, execution limits,
and operational continuity.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class StabilizationAction(Enum):
    """Actions that can be taken for stabilization."""
    
    BEHAVIOR_FREEZE = "behavior_freeze"         # Stop behavior changes temporarily
    ADAPTATION_ROLLBACK = "adaptation_rollback"  # Revert recent adaptations
    RESOURCE_REDISTRIBUTION = "resource_redistribution"  # Move resources to critical areas
    EXECUTION_LIMIT = "execution_limit"          # Limit execution rate or scope
    CONFIG_FREEZE = "config_freeze"              # Freeze configuration changes
    PRIORITY_REDUCTION = "priority_reduction"    # Lower priority of non-critical tasks


@dataclass(frozen=True)
class StabilizationActionPlan:
    """A plan for a specific stabilization action."""
    
    action_id: str
    action_type: StabilizationAction
    target_component: str           # Which component to stabilize
    expected_effect: str            # What this should achieve
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_reversible(self) -> bool:
        """Check if this action can be reversed."""
        return self.action_type in [
            StabilizationAction.BEHAVIOR_FREEZE,
            StabilizationAction.ADAPTATION_ROLLBACK,
            StabilizationAction.RESOURCE_REDISTRIBUTION,
            StabilizationAction.PRIORITY_REDUCTION,
        ]


@dataclass(frozen=True)
class ExitCondition:
    """A condition that, when met, exits the stabilized state."""
    
    condition_id: str
    condition_name: str
    condition_type: str             # e.g., "metric_below", "time_elapsed"
    target_value: Any               # Target value for the condition
    current_value: Optional[Any] = None


@dataclass(frozen=True)
class RollbackStrategy:
    """Strategy for rolling back to a previous state."""
    
    strategy_id: str
    rollback_point: str             # Identifier of state to roll back to
    components_affected: List[str]
    verification_needed: bool       # Whether to verify after rollback


@dataclass(frozen=True)
class StabilizationManagement:
    """
    Stabilization management evaluates stabilization strategies.
    
    Evaluates:
        - Safe configuration states
        - Behavior throttling needs
        - Adaptation rollback requirements
        - Resource redistribution opportunities
        - Execution limits required
        - Operational continuity保障
    
    Stabilization remains explicit and inspectable.
    """
    
    stabilization_id: str
    stabilization_identity: str
    
    # Stabilization strategy
    stabilization_strategy: Optional[str] = None
    
    # Stabilization actions to take
    stabilization_actions: List[StabilizationActionPlan] = field(default_factory=list)
    
    # Exit conditions (when to stop stabilizing)
    exit_conditions: List[ExitCondition] = field(default_factory=list)
    
    # Rollback strategy if stabilization fails
    rollback_strategy: Optional[RollbackStrategy] = None
    
    # Provenance
    provenance: str = "unknown"
    
    # Timing
    planned_at_utc: float = field(default_factory=time.time)
    
    @property
    def action_count(self) -> int:
        """Get the number of stabilization actions."""
        return len(self.stabilization_actions)
    
    @property
    def is_reversible(self) -> bool:
        """Check if all actions are reversible."""
        return all(action.is_reversible for action in self.stabilization_actions)
    
    def get_action_for_component(self, component: str) -> Optional[StabilizationActionPlan]:
        """Get the stabilization action for a specific component."""
        for action in self.stabilization_actions:
            if action.target_component == component:
                return action
        return None
    
    @classmethod
    def create(
        cls,
        stabilization_identity: str,
        stabilization_strategy: Optional[str] = None,
        stabilization_actions: List[StabilizationActionPlan] = None,
        provenance: str = "unknown",
    ) -> StabilizationManagement:
        """Create a new stabilization management instance."""
        if stabilization_actions is None:
            stabilization_actions = []
        
        return cls(
            stabilization_id=f"stab:{uuid.uuid4().hex[:16]}",
            stabilization_identity=stabilization_identity,
            stabilization_strategy=stabilization_strategy,
            stabilization_actions=stabilization_actions,
            provenance=provenance,
        )


__all__ = [
    "StabilizationManagement",
    "StabilizationActionPlan",
    "ExitCondition",
    "RollbackStrategy",
    "StabilizationAction",
]