# Executive Inhibition Demand Types
# ==================================

"""
Types for assessing inhibition demand.

This phase estimates inhibition demand. It must not apply inhibition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveInhibitionDemand:
    """
    Assessment of demand for action or response inhibition.
    
    This phase estimates inhibition demand but must not apply it directly.
    """
    
    targets: Tuple[str, ...] = ()
    action_candidate_class: str = "unknown"
    response_candidate_class: str = "unknown"
    strategy_class: str = "unknown"
    goal_activation_class: str = "unknown"
    task_set_activation_class: str = "unknown"
    communication_class: str = "unknown"
    memory_retrieval_class: str = "unknown"
    focus_switch_class: str = "unknown"
    decision_commitment_class: str = "unknown"
    
    classes: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveInhibitionDemand",)