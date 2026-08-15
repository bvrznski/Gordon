# Executive Ambiguity Assessment Types
# ====================================

"""
Types for assessing ambiguity in executive conditions.

Ambiguity concerns multiple plausible interpretations or meanings.
It may create demand without constituting a confirmed conflict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveAmbiguityClass:
    """
    Ambiguity classes for executive conditions.
    """
    
    UNAMBIGUOUS = "unambiguous"
    MINOR_AMBIGUITY = "minor_amiguity"
    MATERIAL_AMBIGUITY = "material_ambiguity"
    MULTIPLE_PLAUSIBLE_INTERPRETATIONS = "multiple_plausible_interpretations"
    BLOCKING_AMBIGUITY = "blocking_amiguity"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveAmbiguityAssessment:
    """
    Structured assessment of ambiguity in executive conditions.
    """
    
    user_intent_class: str = "unambiguous"
    goal_interpretation_class: str = "unambiguous"
    task_boundary_class: str = "unambiguous"
    policy_applicability_class: str = "unambiguous"
    evidence_meaning_class: str = "unambiguous"
    plan_interpretation_class: str = "unambiguous"
    decision_criteria_class: str = "unambiguous"
    action_semantics_class: str = "unambiguous"
    commitment_scope_class: str = "unambiguous"
    completion_criteria_class: str = "unambiguous"
    overall_class: str = "unambiguous"


__all__: Tuple[str, ...] = (
    "ExecutiveAmbiguityClass",
    "ExecutiveAmbiguityAssessment",
)