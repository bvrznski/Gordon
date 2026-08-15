# Executive Overload Assessment Types
# ====================================

"""
Types for assessing executive overload.

Overload describes semantic executive organization exceeding safe bounded
coordination capacity. Does not suspend Programs automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveOverloadAssessment:
    """
    Assessment of executive overload in the organization.
    
    Overload describes semantic executive organization exceeding safe bounded
    coordination capacity. Does not suspend Programs automatically.
    """
    
    program_count_class: str = "unknown"
    task_set_competition_class: str = "unknown"
    unresolved_conflict_count_class: str = "unknown"
    decision_requirements_count_class: str = "unknown"
    commitments_count_class: str = "unknown"
    context_complexity_class: str = "unknown"
    authority_dependencies_class: str = "unknown"
    switching_frequency_class: str = "unknown"
    inhibition_requirements_class: str = "unknown"
    monitoring_requirements_class: str = "unknown"
    evidence_gaps_count_class: str = "unknown"
    
    recommendations: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveOverloadAssessment",)