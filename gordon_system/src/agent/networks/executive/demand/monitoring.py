# Executive Monitoring Demand Types
# ==================================

"""
Types for assessing monitoring demand.

Monitoring demand may produce a MonitoringProposal but must not create
a MonitoringThread or runtime schedule.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveMonitoringDemand:
    """
    Assessment of demand for executive monitoring activities.
    
    Monitoring Demand may produce a MonitoringProposal but must not create
    a MonitoringThread or runtime schedule.
    """
    
    reasons: Tuple[str, ...] = ()
    unresolved_conflict_class: str = "unknown"
    changing_condition_class: str = "unknown"
    commitment_breach_risk_class: str = "unknown"
    uncertain_prediction_class: str = "unknown"
    temporary_blockage_class: str = "unknown"
    deferred_authority_class: str = "unknown"
    fragile_mitigation_class: str = "unknown"
    recovery_progress_class: str = "unknown"
    strategy_performance_class: str = "unknown"
    
    proposals: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveMonitoringDemand",)