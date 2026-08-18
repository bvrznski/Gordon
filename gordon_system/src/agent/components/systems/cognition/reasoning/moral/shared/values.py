# Value Management - Phase 7.49
# =============================

"""
Value analysis and management for moral reasoning.

MORAL-LAW-003: Every ethical conclusion shall reference explicit stakeholders, principles and supporting facts
VALUE-LAW-001: Every Moral Value shall possess one explicit identity
VALUE-LAW-002: Value conflicts shall remain explicit
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MoralValue(Enum):
    """Core moral values in ethical reasoning."""
    
    JUSTICE = "justice"
    FAIRNESS = "fairness"
    AUTONOMY = "autonomy"
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"
    TRUTHFULNESS = "truthfulness"
    RESPECT = "respect"
    HONESTY = "honesty"


@dataclass(frozen=True)
class ValueConflict:
    """
    Conflict between moral values.
    
    VALUE-LAW-003: Value prioritization shall remain explicit
    """
    
    # Identity
    conflict_id: str
    
    # Involved values
    value_a: MoralValue
    value_b: MoralValue
    
    # Nature of conflict
    conflict_type: str  # e.g., "mutually_exclusive"
    explanation: str


@dataclass(frozen=True)
class ValueAnalysis:
    """
    Analysis of moral values in a situation.
    
    VALUE-LAW-004: Value provenance shall remain complete
    """
    
    # Identity
    analysis_id: str
    
    # Values at play
    values: List[MoralValue]
    
    # Conflicts
    conflicts: Tuple[ValueConflict, ...] = field(default_factory=tuple)
    
    # Priority (ranked list of value IDs by importance)
    priority_order: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ValueSet:
    """
    Complete set of values for moral reasoning.
    
    MORAL-LAW-003: Every ethical conclusion shall reference explicit stakeholders, 
    principles and supporting facts including values.
    """
    
    # Identity
    set_id: str
    
    # Values (tuple for immutability)
    analyses: Tuple[ValueAnalysis, ...]
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        analyses: Optional[List[ValueAnalysis]] = None,
    ) -> ValueSet:
        """Create a new value set."""
        return cls(
            set_id=f"value_set:{uuid.uuid4().hex[:16]}",
            analyses=tuple(analyses or []),
            created_at_utc=time.time(),
        )


__all__ = [
    "MoralValue",
    "ValueConflict",
    "ValueAnalysis",
    "ValueSet",
]