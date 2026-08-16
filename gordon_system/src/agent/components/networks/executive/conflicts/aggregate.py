# Executive Conflict Aggregation Types
# =====================================

"""
Types for grouping related conflicts into aggregates.

Aggregation is a higher-level view that preserves references to
constituent conflicts while providing summary assessment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictAggregate:
    """
    An aggregate of related executive conflicts.
    """
    
    aggregate_id: str = ""
    grouping_criterion: str = "executive_program"
    group_value: str = ""
    constituent_conflict_ids: Tuple[str, ...] = ()
    summary_severity_class: str = "unknown"
    summary_count: int = 0
    related_by_causal_chain: bool = False
    related_by_shared_subject: bool = False


__all__: Tuple[str, ...] = (
    "ExecutiveConflictAggregate",
)