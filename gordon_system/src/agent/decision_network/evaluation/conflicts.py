# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Conflicts
# ===========================

"""
Action Conflict Analysis type definitions.

This module defines the types used to detect and represent conflicts between
Action Candidates during evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


# =============================================================================
# CONFLICT TYPE ENUMERATION
# =============================================================================

class ConflictType(Enum):
    """
    Kinds of conflicts that can be detected between Action Candidates.
    
    PROPERTIES:
        • GOAL: Conflicts with active goals
        • POLICY: Violates policy rules
        • SECURITY: Violates security requirements
        • COMMITMENT: Conflicts with commitments
        • ACTION: Direct conflict with another action
        • TARGET: Conflicting target specifications
        • RESOURCE: Resource allocation conflicts
        • AUTHORITY: Authority requirement conflicts
        • TEMPORAL: Timing conflicts
        • CONTEXT: Contextual incompatibility
    """
    
    GOAL = "goal"
    """Conflicts with active goals."""
    
    POLICY = "policy"
    """Violates policy rules."""
    
    SECURITY = "security"
    """Violates security requirements."""
    
    COMMITMENT = "commitment"
    """Conflicts with commitments."""
    
    ACTION = "action"
    """Direct conflict with another action."""
    
    TARGET = "target"
    """Conflicting target specifications."""
    
    RESOURCE = "resource"
    """Resource allocation conflicts."""
    
    AUTHORITY = "authority"
    """Authority requirement conflicts."""
    
    TEMPORAL = "temporal"
    """Timing conflicts."""
    
    CONTEXT = "context"
    """Contextual incompatibility."""


# =============================================================================
# CONFLICT RECORD
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConflictRecord:
    """
    Record of a detected conflict.
    
    A conflict record documents that two or more candidates have incompatible
    requirements or effects. Conflicts do not indicate which is "right" - they
    simply document incompatibility.
    
    PROPERTIES:
        • conflict_id: Unique identifier for this conflict record
        • conflict_type: Type of conflict detected
        • affected_candidates: IDs of candidates involved in the conflict
        • nature_of_conflict: Description of how candidates conflict
        • severity: How severe the conflict is (0.0 to 1.0)
    
    NOT RESPONSIBLE FOR:
        - Resolving conflicts
        - Selecting which candidate to keep
        - Modifying affected candidates
    """
    
    conflict_id: str
    """Unique identifier for this conflict record."""
    
    conflict_type: ConflictType
    """Type of conflict detected (ConflictType.*)."""
    
    affected_candidates: Tuple[str, ...]
    """IDs of candidates involved in the conflict."""
    
    nature_of_conflict: str = ""
    """Description of how candidates conflict."""
    
    severity: float = 0.5
    """How severe the conflict is (0.0 to 1.0)."""
    
    @classmethod
    def goal_conflict(
        cls,
        candidate_a_id: str,
        candidate_b_id: str,
        description: str = "",
    ) -> ConflictRecord:
        """Create a goal conflict record."""
        return cls(
            conflict_id=f"conflict_{candidate_a_id}_{candidate_b_id}_goal",
            conflict_type=ConflictType.GOAL,
            affected_candidates=(candidate_a_id, candidate_b_id),
            nature_of_conflict=description or "Candidates have incompatible goals.",
            severity=0.7,
        )
    
    @classmethod
    def policy_conflict(
        cls,
        candidate_id: str,
        policy_violated: str,
        description: str = "",
    ) -> ConflictRecord:
        """Create a policy conflict record."""
        return cls(
            conflict_id=f"conflict_{candidate_id}_policy_{policy_violated}",
            conflict_type=ConflictType.POLICY,
            affected_candidates=(candidate_id,),
            nature_of_conflict=description or f"Candidate violates {policy_violated}.",
            severity=0.85,
        )
    
    @classmethod
    def action_conflict(
        cls,
        candidate_a_id: str,
        candidate_b_id: str,
        description: str = "",
    ) -> ConflictRecord:
        """Create an action conflict record."""
        return cls(
            conflict_id=f"conflict_{candidate_a_id}_{candidate_b_id}_action",
            conflict_type=ConflictType.ACTION,
            affected_candidates=(candidate_a_id, candidate_b_id),
            nature_of_conflict=description or "Candidates produce incompatible effects.",
            severity=0.65,
        )


# =============================================================================
# CONFLICT ANALYSIS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConflictAnalysis:
    """
    Summary of conflict analysis for an evaluation.
    
    PROPERTIES:
        • total_conflicts: Number of conflicts detected
        • conflict_records: Detailed records of each conflict
        • highest_severity_conflict: Severity of the most severe conflict
        • conflict_categories: Set of conflict types that occurred
    """
    
    total_conflicts: int = 0
    """Number of conflicts detected."""
    
    conflict_records: Tuple[ConflictRecord, ...] = field(default_factory=tuple)
    """Detailed records of each conflict."""
    
    highest_severity_conflict: float = 0.0
    """Severity of the most severe conflict (0.0 to 1.0)."""
    
    conflict_categories: Tuple[str, ...] = field(default_factory=tuple)
    """Set of conflict types that occurred."""

    @classmethod
    def no_conflicts(cls) -> ConflictAnalysis:
        """Create a conflict analysis with no conflicts."""
        return cls(
            total_conflicts=0,
            conflict_records=(),
            highest_severity_conflict=0.0,
            conflict_categories=(),
        )
    
    @classmethod
    def from_conflicts(
        cls, records: Tuple[ConflictRecord, ...]
    ) -> ConflictAnalysis:
        """Create a conflict analysis from conflict records."""
        if not records:
            return cls.no_conflicts()
        
        categories = tuple(set(str(r.conflict_type.value) for r in records))
        max_severity = max((r.severity for r in records), default=0.0)
        
        return cls(
            total_conflicts=len(records),
            conflict_records=records,
            highest_severity_conflict=max_severity,
            conflict_categories=categories,
        )
    
    def is_clean(self) -> bool:
        """Check if there are no conflicts."""
        return self.total_conflicts == 0