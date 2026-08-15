# Executive Conflict Recurrence Model
# ====================================

"""
Types for assessing conflict recurrence patterns.

Recurrence tracks repeated occurrences of the same or similar conflicts,
which may indicate deeper issues with task sets, strategies, or authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictRecurrenceClass:
    """
    Recurrence classes for executive conflicts.
    """
    
    NONE = "none"
    FIRST_RECURRENCE = "first_recurrence"
    SECOND_RECURRENCE = "second_recurrence"
    RECURRING = "recurring"
    CHRONIC = "chronic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveConflictRecurrence:
    """
    Structured assessment of executive conflict recurrence.
    """
    
    recurrence_class: str
    recurrence_count: int = 1
    prior_conflict_ids: Tuple[str, ...] = ()
    similarity_classification: str = "identical"
    average_interval_cycles: float = 0.0
    previous_mitigations: Tuple[str, ...] = ()
    previous_outcomes: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = (
    "ExecutiveConflictRecurrenceClass",
    "ExecutiveConflictRecurrence",
)