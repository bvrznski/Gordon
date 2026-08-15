# Executive Conflict Deduplication Types
# ======================================

"""
Types for assessing whether conflicts are duplicates or related.

Deduplication is important to prevent redundant conflict records and
overestimation of executive load.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictDuplicateAssessment:
    """
    Assessment of whether a conflict is distinct, duplicate, or related
    to existing conflicts.
    """
    
    classification: str = "distinct"
    compared_conflict_ids: Tuple[str, ...] = ()
    similarity_score: float = 0.0
    reason: str = ""


__all__: Tuple[str, ...] = (
    "ExecutiveConflictDuplicateAssessment",
)