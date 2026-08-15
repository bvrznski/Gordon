# Executive Conflict Monitoring Scope Types
# ==========================================

"""
Types for defining the bounded scope of conflict monitoring activities.

Scope limits ensure that monitoring remains bounded and does not perform
unbounded pairwise comparisons.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictMonitoringScope:
    """
    Bounded scope for conflict monitoring activity.
    
    Scope limits ensure that monitoring remains bounded and does not perform
    unbounded pairwise comparisons without explicit prefiltering.
    """
    
    max_programs: int = 100
    max_task_sets: int = 100
    max_goals: int = 100
    max_commitments: int = 100
    max_constraints: int = 100
    max_source_projections: int = 100
    max_conflict_candidates: int = 1000
    max_confirmed_conflicts: int = 100
    max_relations: int = 1000
    max_evidence_items: int = 1000
    max_pairwise_comparisons: int = 5000
    max_aggregates: int = 100
    max_decomposition_depth: int = 3
    max_recurrence_history: int = 100
    max_mitigation_references: int = 100
    max_demand_targets: int = 100
    max_proposals: int = 100
    
    # Temporal and other scope
    temporal_scope_from: str = ""
    temporal_scope_to: str = ""
    
    # Thread, task, participant, authority scope
    thread_scope: Tuple[str, ...] = ()
    task_scope: Tuple[str, ...] = ()
    participant_scope: Tuple[str, ...] = ()
    authority_scope: Tuple[str, ...] = ()
    
    # Privacy and factuality restrictions
    privacy_restrictions: Tuple[str, ...] = ()
    factuality_restrictions: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveConflictMonitoringScope",)