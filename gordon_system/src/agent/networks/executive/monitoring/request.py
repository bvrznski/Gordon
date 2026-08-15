# Executive Conflict Monitoring Request Types
# ============================================

"""
Types for requesting conflict monitoring activities.

A monitoring request is declarative and does not perform any work by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictMonitoringRequest:
    """
    Declarative request for conflict monitoring activity.
    
    A monitoring request specifies what to monitor, but does not perform the
    monitoring itself. The execution of this request belongs to Phase 4.4.6.
    """
    
    request_id: str = ""
    purpose_class: str = "unknown"
    
    # References to state elements to be monitored
    executive_state_reference: str = ""
    executive_context_reference: str = ""
    program_references: Tuple[str, ...] = ()
    task_set_references: Tuple[str, ...] = ()
    goal_references: Tuple[str, ...] = ()
    commitment_references: Tuple[str, ...] = ()
    decision_references: Tuple[str, ...] = ()
    action_candidate_references: Tuple[str, ...] = ()
    existing_conflict_references: Tuple[str, ...] = ()
    prior_demand_references: Tuple[str, ...] = ()
    
    # Scope
    scope_max_programs: int = 100
    scope_max_task_sets: int = 100
    scope_max_goals: int = 100
    scope_max_commitments: int = 100
    
    # Expected products
    expected_products: Tuple[str, ...] = ()
    
    # Completion requirements
    completion_requirements: str = "unknown"
    
    # Correlation and causation
    correlation_id: str = ""
    causation_source: str = ""


__all__: Tuple[str, ...] = ("ExecutiveConflictMonitoringRequest",)