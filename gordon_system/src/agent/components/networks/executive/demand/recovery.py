# Executive Recovery Demand Types
# ===============================

"""
Types for assessing recovery demand.

Detailed recovery coordination may be handled by later executive mechanisms
or Execution RecoveryLoop. This phase estimates the demand.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveRecoveryDemand:
    """
    Assessment of demand for executive recovery activities.
    
    Detailed recovery coordination may be handled by later executive mechanisms
    or Execution RecoveryLoop. This phase estimates the demand.
    """
    
    contributors: Tuple[str, ...] = ()
    failed_strategy_class: str = "unknown"
    invalid_task_set_class: str = "unknown"
    unsatisfied_dependency_class: str = "unknown"
    repeated_action_failure_class: str = "unknown"
    commitment_breach_risk_class: str = "unknown"
    lost_context_class: str = "unknown"
    excessive_tension_class: str = "unknown"
    unresolved_escalation_class: str = "unknown"
    control_saturation_class: str = "unknown"
    
    recommendations: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveRecoveryDemand",)