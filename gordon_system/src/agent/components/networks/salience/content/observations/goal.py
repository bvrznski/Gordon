# Salience Goal Observation
# =========================
#
# Canonical implementation of goal observations (Phase 4.8.3).
#

"""
Goal observation for the Salience Network.

GOAL OBSERVATION:
    Represents raw semantic information about goals without interpretation.
    
SEMANTIC HIERARCHY:
    BaseSalienceContent → BaseObservation → GoalObservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import FrozenSet, Tuple

from gordon_system.src.agent.networks.salience.content.observations.base import BaseObservation


@dataclass(frozen=True)
class GoalObservation(BaseObservation):
    """
    Observation of raw goal-related information without interpretation.
    
    GOAL TYPES:
        - primary: Primary objectives
        - secondary: Supporting objectives
        - terminal: End states
        - instrumental: Means to achieve ends
    
    SEMANTIC HIERARCHY:
        BaseObservation → GoalObservation
    """
    
    goal_type: str = field(default="primary")
    """Type of goal (primary, secondary, terminal, instrumental)."""
    
    goal_id: str = field(default="")
    """Identifier for the target goal."""
    
    priority: float = field(default=0.5)
    """Priority level (0.0 to 1.0)."""
    
    @property
    def is_goal(self) -> bool:
        """Indicates whether this is a goal observation."""
        return True
    
    @property
    def canonical_type(self) -> str:
        """Return the canonical type identifier for this goal observation."""
        return f"salience.goal.{self.goal_type}"
    
    def validate_goal_compliance(self) -> bool:
        """
        Validate that this goal observation satisfies Salience Network laws.
        
        Returns:
            True if compliance is valid, False otherwise.
        """
        return (
            super().validate_observation_compliance() and
            self._validate_goal_type()
        )
    
    def _validate_goal_type(self) -> bool:
        """Validate that goal type is explicit and recognized."""
        recognized_types = {"primary", "secondary", "terminal", "instrumental"}
        return self.goal_type in recognized_types