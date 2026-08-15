# Executive Effort Demand Types
# =============================

"""
Types for assessing effort demand.

Effort demand is semantic and must not allocate runtime resources like CPU,
GPU, tokens, memory, or workers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveEffortDemand:
    """
    Assessment of semantic effort demand for executive activities.
    
    Effort Demand is semantic - it must not allocate CPU, GPU, tokens,
    memory, or workers.
    """
    
    contributors: Tuple[str, ...] = ()
    complexity_class: str = "unknown"
    constraint_count_class: str = "unknown"
    unresolved_conflict_count_class: str = "unknown"
    evidence_diversity_class: str = "unknown"
    working_memory_demand_class: str = "unknown"
    decision_difficulty_class: str = "unknown"
    switching_cost_class: str = "unknown"
    reasoning_depth_class: str = "unknown"
    monitoring_burden_class: str = "unknown"
    recovery_complexity_class: str = "unknown"
    capability_limitation_class: str = "unknown"
    
    recommendations: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveEffortDemand",)