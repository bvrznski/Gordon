# Executive Switching Demand Types
# ==================================

"""
Types for assessing switching demand.

Detailed switching behavior belongs to Phase 4.4.8.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveSwitchingDemand:
    """
    Assessment of demand for program or task-set switching.
    
    Detailed switching behavior belongs to Phase 4.4.8.
    """
    
    contributor_class: str = "unknown"
    current_strategy_failure_class: str = "unknown"
    focus_misalignment_class: str = "unknown"
    task_set_invalidity_class: str = "unknown"
    changing_priority_class: str = "unknown"
    new_critical_goal_class: str = "unknown"
    repeated_outcome_mismatch_class: str = "unknown"
    opportunity_expiration_class: str = "unknown"
    low_progress_class: str = "unknown"
    control_saturation_class: str = "unknown"
    
    outputs: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveSwitchingDemand",)