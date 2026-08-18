# Duty Management - Phase 7.49
# ============================

"""
Duty analysis and management for moral reasoning.

MORAL-LAW-003: Every ethical conclusion shall reference explicit stakeholders, principles and supporting facts
DUTY-LAW-001: Every Duty shall possess one explicit identity
DUTY-LAW-002: Duty applicability shall remain explicit
DUTY-LAW-003: Duty priority shall remain explicit
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DutyType(Enum):
    """Types of duties in moral reasoning."""
    
    OBLIGATION = "obligation"
    PROFESSIONAL = "professional"
    FIDUCIARY = "fiduciary"
    PROMISE = "promise"
    SPECIAL_RESPONSIBILITY = "special_responsibility"


class DutyStatus(Enum):
    """Status of duty application."""
    
    IDENTIFIED = "identified"
    APPLICABLE = "applicable"
    CONFLICTING = "conflicting"
    SATISFIED = "satisfied"
    VIOLATED = "violated"


@dataclass(frozen=True)
class DutyAnalysis:
    """
    Analysis of an applicable duty in moral reasoning.
    
    DUTY-LAW-004: Duty provenance shall remain complete
    DUTY-LAW-005: Duty revisions shall preserve history
    DUTY-LAW-006: Conflicting duties shall never remain unresolved without explicit annotation
    
    A duty analysis includes:
        - The duty itself (what is required)
        - Its applicability to the current situation
        - Priority relative to other duties
        - Sources of the duty (ethical framework, role, etc.)
    """
    
    # Identity
    analysis_id: str
    semantic_identity: str
    
    # Duty info
    duty_id: str
    duty_type: DutyType
    description: str
    
    # Application
    applicability_score: float = 1.0  # How well does this duty apply?
    priority: int = 0  # Higher = more important to satisfy
    
    # Context
    applicable_stakeholders: List[str] = field(default_factory=list)
    
    # Provenance
    source_framework: Optional[str] = None
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_applicable(self) -> bool:
        """Check if duty applies."""
        return self.applicability_score > 0.5


@dataclass(frozen=True)
class DutyConflict:
    """
    Conflict between duties in moral reasoning.
    
    MORAL-LAW-003 requires explicit resolution of such conflicts.
    """
    
    # Identity
    conflict_id: str
    
    # Involved duties
    duty_a_id: str
    duty_b_id: str
    
    # Nature of conflict
    conflict_type: str  # e.g., "impossible_to_satisfy_both"
    explanation: str
    
    # Resolution status
    resolved: bool = False
    resolution_note: Optional[str] = None


@dataclass(frozen=True)
class DutySet:
    """
    Complete set of duties for moral reasoning.
    
    MORAL-LAW-003: Every ethical conclusion shall reference explicit stakeholders, 
    principles and supporting facts including duties.
    """
    
    # Identity
    set_id: str
    
    # Duties (tuple for immutability)
    analyses: Tuple[DutyAnalysis, ...]
    
    # Conflicts
    conflicts: Tuple[DutyConflict, ...] = field(default_factory=tuple)
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def count(self) -> int:
        """Number of duty analyses."""
        return len(self.analyses)
    
    @property
    def applicable_duties(self) -> List[DutyAnalysis]:
        """Get duties that apply to current situation."""
        return [d for d in self.analyses if d.is_applicable]
    
    @classmethod
    def create(
        cls,
        analyses: Optional[List[DutyAnalysis]] = None,
        conflicts: Optional[List[DutyConflict]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> DutySet:
        """Create a new duty set."""
        return cls(
            set_id=f"duty_set:{uuid.uuid4().hex[:16]}",
            analyses=tuple(analyses or []),
            conflicts=tuple(conflicts or []),
            source_descriptor_id=source_descriptor_id,
            created_at_utc=time.time(),
        )
    
    def add_analysis(self, analysis: DutyAnalysis) -> DutySet:
        """Add a duty analysis."""
        return dataclass_replace(
            self,
            analyses=self.analyses + (analysis,),
        )
    
    def add_conflict(self, conflict: DutyConflict) -> DutySet:
        """Add a duty conflict."""
        return dataclass_replace(
            self,
            conflicts=self.conflicts + (conflict,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DutyType",
    "DutyStatus",
    "DutyAnalysis",
    "DutyConflict",
    "DutySet",
]