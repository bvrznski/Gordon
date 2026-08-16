# Executive Conflict Decomposition Types
# ======================================

"""
Types for decomposing broad conflicts into more specific sub-conflicts.

Decomposition helps analyze complex conflicts by breaking them down
into manageable components. It must be bounded to prevent explosion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictDecomposition:
    """
    A decomposition of a conflict into more specific sub-conflicts.
    """
    
    original_conflict_id: str = ""
    subconflict_kinds: Tuple[str, ...] = ()
    subconflict_ids: Tuple[str, ...] = ()
    decomposition_depth: int = 1
    max_depth_reached: bool = False
    reason: str = ""


__all__: Tuple[str, ...] = (
    "ExecutiveConflictDecomposition",
)