# Executive Decision Demand Types
# ================================

"""
Types for assessing decision demand.

Detailed decision architecture belongs to Phase 4.4.10.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveDecisionDemand:
    """
    Assessment of demand for executive decision-making.
    
    Detailed decision architecture belongs to Phase 4.4.10.
    """
    
    decision_status_class: str = "unknown"
    alternative_count: int = 0
    priority_equivalence_class: str = "unknown"
    evidence_conflict_class: str = "unknown"
    authority_requirement_class: str = "unknown"
    commitment_conflict_class: str = "unknown"
    goal_conflict_class: str = "unknown"
    consequence_class: str = "unknown"
    irreversibility_class: str = "unknown"
    evaluation_completeness_class: str = "unknown"
    temporal_pressure_class: str = "unknown"
    
    recommendations: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveDecisionDemand",)