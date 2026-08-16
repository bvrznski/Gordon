# Executive Conflict Monitoring State Types
# =========================================

"""
Types for bounded conflict monitoring state.

This state is subordinate to canonical ExecutiveState and does not create a
root executive state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictMonitoringState:
    """
    Bounded state for conflict monitoring activity.
    
    This state is subordinate to canonical ExecutiveState. It does not create
    a root executive state.
    """
    
    # Active conflicts and related state
    active_conflict_references: Tuple[str, ...] = ()
    disputed_conflict_references: Tuple[str, ...] = ()
    waiting_conflict_references: Tuple[str, ...] = ()
    
    resolved_conflict_summaries: Tuple[str, ...] = ()
    recurring_conflict_references: Tuple[str, ...] = ()
    
    # Tension and gap tracking
    active_tension_references: Tuple[str, ...] = ()
    active_gap_references: Tuple[str, ...] = ()
    
    # Demand state
    latest_demand_assessment_references: Tuple[str, ...] = ()
    prior_demand_summaries: Tuple[str, ...] = ()
    
    # Authority and external requests
    unresolved_authority_requirements: Tuple[str, ...] = ()
    prior_mitigation_references: Tuple[str, ...] = ()
    escalation_references: Tuple[str, ...] = ()
    
    # State tracking
    executive_state_revision: str = ""
    executive_context_revision: str = ""
    monitoring_state_revision: int = 0
    
    # Bounded history
    history_entries: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveConflictMonitoringState",)