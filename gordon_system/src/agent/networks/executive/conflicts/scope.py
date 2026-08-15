# Executive Conflict Scope Types
# ===============================

"""
Types for defining the scope of executive conflicts.

Scope defines which parts of the executive organization are affected by
a conflict, without automatically elevating local issues to global ones.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictScope:
    """
    Bounded scope definition for an executive conflict.
    
    A local conflict must not automatically be promoted to a global conflict.
    """
    
    # Scope dimensions
    program_scope: str = "single_program"
    task_set_scope: str = "single_task_set"
    thread_scope: str = "single_thread"
    decision_scope: str = "single_decision"
    action_selection_scope: str = "single_action_selection"
    
    # Subject scope (which executive structures are involved)
    affected_program_ids: Tuple[str, ...] = ()
    affected_task_set_ids: Tuple[str, ...] = ()
    affected_thread_ids: Tuple[str, ...] = ()
    affected_decision_ids: Tuple[str, ...] = ()
    
    # Temporal and authority scope
    temporal_scope: str = "current_cycle"
    authority_scope: str = "executive_network_internal"


__all__: Tuple[str, ...] = ("ExecutiveConflictScope",)