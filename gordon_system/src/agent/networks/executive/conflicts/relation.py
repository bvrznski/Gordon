# Executive Conflict Relation Types
# ==================================

"""
Types for representing relationships between executive conflicts.

Relationships can be directional where semantics require direction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictRelationKind:
    """
    Kinds of relationships between executive conflicts.
    """
    
    CONTRADICTS = "contradicts"
    COMPETES_WITH = "competes_with"
    BLOCKS = "blocks"
    WEAKENS = "weakens"
    INVALIDATES = "invalidates"
    REQUIRES_EXCLUSION_OF = "requires_exclusion_of"
    REQUIRES_RESOLUTION_BEFORE = "requires_resolution_before"
    AMPLIFIES = "amplifies"
    DEPENDS_ON = "depends_on"
    PROPAGATES_TO = "propagates_to"
    RESULTS_FROM = "results_from"
    OVERLAPS_WITH = "overlaps_with"
    DUPLICATES = "duplicates"
    SUPERSEDES = "supersedes"
    MITIGATES = "mitigates"
    RESOLVES = "resolves"


@dataclass(frozen=True)
class ExecutiveConflictRelation:
    """
    A relationship between two executive conflicts.
    """
    
    from_conflict_id: str
    to_conflict_id: str
    relation_kind: str


__all__: Tuple[str, ...] = (
    "ExecutiveConflictRelationKind",
    "ExecutiveConflictRelation",
)