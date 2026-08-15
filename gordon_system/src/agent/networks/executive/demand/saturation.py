# Control Saturation Assessment Types
# ====================================

"""
Types for assessing control saturation.

This is not a runtime resource metric - it's an assessment of semantic
executive organization exceeding safe bounded coordination capacity.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ControlSaturationAssessment:
    """
    Assessment of control saturation in executive organization.
    
    This is not a runtime resource metric - it's an assessment of semantic
    executive organization exceeding safe bounded coordination capacity.
    """
    
    evidence: Tuple[str, ...] = ()
    status_class: str = "unknown"
    active_high_demand_targets_count_class: str = "unknown"
    persistent_critical_conflicts_class: str = "unknown"
    repeated_control_escalation_class: str = "unknown"
    excessive_programs_class: str = "unknown"
    incompatible_mandatory_requirements_class: str = "unknown"
    working_memory_insufficiency_class: str = "unknown"
    action_selection_overload_class: str = "unknown"
    authority_deadlock_class: str = "unknown"
    unbounded_recurrence_pressure_class: str = "unknown"


__all__: Tuple[str, ...] = ("ControlSaturationAssessment",)