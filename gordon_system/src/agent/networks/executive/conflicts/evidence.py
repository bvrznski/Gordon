# Executive Conflict Evidence Types
# ==================================

"""
Types for representing evidence that supports or characterizes executive conflicts.

Evidence is the foundation of any meaningful conflict assessment - without evidence,
a conflict is just an assertion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveConflictEvidenceKind:
    """
    Kinds of evidence that may support executive conflicts.
    
    Each kind represents a different type of supporting or contradicting
    information that contributes to conflict assessment.
    """
    
    CONTRADICTORY_CLAIM = "contradictory_claim"
    MUTUAL_EXCLUSION = "mutual_exclusion"
    DEPENDENCY_FAILURE = "dependency_failure"
    COMPETING_REQUIREMENT = "competing_requirement"
    UNSATISFIED_CONSTRAINT = "unsatisfied_constraint"
    AUTHORITY_DISAGREEMENT = "authority_disagreement"
    POLICY_PROHIBITION = "policy_prohibition"
    SECURITY_PROHIBITION = "security_prohibition"
    GOAL_OBSTRUCTION = "goal_obstruction"
    COMMITMENT_BREACH_RISK = "commitment_breach_risk"
    OUTCOME_MISMATCH = "outcome_mismatch"
    PREDICTION_ERROR = "prediction_error"
    PLAN_INCONSISTENCY = "plan_inconsistency"
    REASONING_DISAGREEMENT = "reasoning_disagreement"
    ACTION_COMPETITION = "action_compition"
    FOCUS_MISALIGNMENT = "focus_misalignment"
    MOTIVATIONAL_MISALIGNMENT = "motivational_misalignment"
    WORKING_MEMORY_DEFICIT = "working_memory_deficit"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    RESOURCE_PROJECTION_SHORTFALL = "resource_projection_shortfall"
    TEMPORAL_OVERLAP = "temporal_overlap"
    AMBIGUITY = "ambiguity"
    UNCERTAINTY = "uncertainty"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REPEATED_FAILURE = "repeated_failure"
    PERSEVERATION = "perseveration"
    OTHER = "other"


@dataclass(frozen=True)
class ExecutiveConflictEvidence:
    """
    Evidence item supporting or characterizing an executive conflict.
    """
    
    kind: str
    description: str
    source_id: Optional[str] = None
    source_revision: int = 1
    factuality_class: str = "factual"
    confidence_class: str = "unknown"
    applicability_class: str = "direct"
    temporal_valid_from_utc: Optional[float] = None
    temporal_valid_until_utc: Optional[float] = None
    privacy_classification: str = "internal"
    provenance_gathered_by: str = "executive_conflict_monitor"
    provenance_gathered_at_utc: float = 0.0


__all__: Tuple[str, ...] = (
    "ExecutiveConflictEvidenceKind",
    "ExecutiveConflictEvidence",
)