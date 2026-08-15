# Executive Demand Profile Types
# ===============================

"""
Types for representing the profile or shape of executive demand.

A profile describes the functional form that demand takes, not a runtime
execution plan.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveDemandProfile:
    """
    Profiles describing the functional shape of executive demand.
    
    A profile describes the functional shape of demand - it is not a runtime
    execution plan.
    """
    
    MAINTENANCE = "maintenance"
    STABILIZATION = "stabilization"
    DISAMBIGUATION = "disambiguation"
    EVIDENCE_ACQUISITION = "evidence_acquisition"
    CONFLICT_RESOLUTION = "conflict_resolution"
    DECISION_PREPARATION = "decision_preparation"
    INHIBITION = "inhibition"
    SWITCHING = "switching"
    RECOVERY = "recovery"
    MONITORING = "monitoring"
    STRATEGY_REVIEW = "strategy_review"
    TASK_SET_REVIEW = "task_set_review"
    PROGRAM_REVIEW = "program_review"
    AUTHORITY_REVIEW = "authority_review"
    DEESCALATION = "deescalation"
    CONTROL_RELEASE = "control_release"
    COMPOSITE = "composite"
    UNKNOWN = "unknown"

    @classmethod
    def all_profiles(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveDemandProfile",)