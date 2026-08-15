# Control Insufficiency Assessment Types
# =======================================

"""
Types for assessing control insufficiency.

It assesses whether the current accepted executive organization appears
insufficient for current conditions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ControlInsufficiencyAssessment:
    """
    Assessment of whether current executive control is insufficient.
    
    It assesses whether the current accepted executive organization appears
    insufficient for current conditions. Does not allocate runtime resources.
    """
    
    evidence: Tuple[str, ...] = ()
    status_class: str = "unknown"
    conflicting_strategies_class: str = "unknown"
    missing_rules_class: str = "unknown"
    repeated_strategy_failure_class: str = "unknown"
    focus_misalignment_class: str = "unknown"
    missing_evidence_class: str = "unknown"
    inadequate_inhibition_class: str = "unknown"
    competing_programs_class: str = "unknown"
    unconstrained_decisions_class: str = "unknown"
    missing_critical_target_class: str = "unknown"


__all__: Tuple[str, ...] = ("ControlInsufficiencyAssessment",)