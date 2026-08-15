# Executive Performance Criteria
# ==============================

"""
Canonical immutable ExecutivePerformanceCriteria definitions.

Performance criteria are what performance is assessed against - goals,
commitments, constraints, policies, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutivePerformanceCriterion:
    """
    Immutable reference to a single performance criterion.

    A criterion defines one aspect of how performance is assessed.
    Each criterion must preserve owner, authority, applicability,
    threshold/predicate, evidence requirements, temporal validity,
    confidence requirements, and provenance.
    """

    criterion_id: str
    """Unique identifier for this criterion."""

    kind: str  # CriterionKind value
    """The semantic category of the criterion."""

    owner: str = "executive_network_internal"
    """Owner of this criterion (authority reference)."""

    authority: str = "EXECUTIVE_NETWORK_INTERNAL"
    """Authority class for this criterion."""

    threshold_or_predicate: str = "unknown"
    """Threshold or predicate that determines satisfaction."""

    evidence_requirements: Tuple[str, ...] = ()
    """Evidence required to assess this criterion."""

    temporal_validity_seconds: float = 0.0
    """Temporal validity window in seconds (0 = no time bound)."""

    confidence_requirement: float = 0.5
    """Minimum confidence required for assessment."""

    provenance_created_by: str = "unknown"
    """Who/what created this criterion reference."""

    provenance_created_at_utc: float = 0.0
    """When this criterion was defined (seconds since epoch)."""


class ExecutivePerformanceCriterionKind:
    """
    Typed taxonomy of executive performance criterion kinds.
    """

    GOAL_SATISFACTION = "GOAL_SATISFACTION"
    """Goal satisfaction condition."""

    COMMITMENT_FULFILLMENT = "COMMITMENT_FULFILLMENT"
    """Commitment fulfillment requirement."""

    OBJECTIVE_PROGRESS = "OBJECTIVE_PROGRESS"
    """Objective progress threshold."""

    COMPLETION = "COMPLETION"
    """Completion state."""

    CORRECTNESS = "CORRECTNESS"
    """Result correctness condition."""

    QUALITY = "QUALITY"
    """Quality standard."""

    CONSTRAINT_COMPLIANCE = "CONSTRAINT_COMPLIANCE"
    """Constraint compliance requirement."""

    POLICY_COMPLIANCE = "POLICY_COMPLIANCE"
    """Policy compliance requirement."""

    SECURITY_COMPLIANCE = "SECURITY_COMPLIANCE"
    """Security compliance requirement."""

    TIMELINESS = "TIMELINESS"
    """Timeliness threshold."""

    EFFICIENCY = "EFFICIENCY"
    """Efficiency threshold."""

    EFFORT_PROPORTIONALITY = "EFFORT_PROPORTIONALITY"
    """Effort proportionality condition."""

    UNCERTAINTY_REDUCTION = "UNCERTAINTY_REDUCTION"
    """Uncertainty reduction requirement."""

    RISK_REDUCTION = "RISK_REDUCTION"
    """Risk reduction requirement."""

    RECOVERY_SUCCESS = "RECOVERY_SUCCESS"
    """Recovery success requirement."""

    SIDE_EFFECT_CONTAINMENT = "SIDE_EFFECT_CONTAINMENT"
    """Side effect containment requirement."""

    REVERSIBILITY = "REVERSIBILITY"
    """Reversibility condition."""

    ARTIFACT_ACCEPTANCE = "ARTIFACT_ACCEPTANCE"
    """Artifact acceptance condition."""

    DECISION_ADEQUACY = "DECISION_ADEQUACY"
    """Decision adequacy condition."""

    ACTION_POSTCONDITION_SATISFACTION = "ACTION_POSTCONDITION_SATISFACTION"
    """Action postcondition satisfaction requirement."""

    USER_ACCEPTANCE = "USER_ACCEPTANCE"
    """User acceptance condition."""

    EXTERNAL_AUTHORITY_ACCEPTANCE = "EXTERNAL_AUTHORITY_ACCEPTANCE"
    """External authority acceptance condition."""

    UNKNOWN = "UNKNOWN"
    """Unknown or unclassified criterion kind."""

    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid criterion kinds as a tuple."""
        return (
            cls.GOAL_SATISFACTION,
            cls.COMMITMENT_FULFILLMENT,
            cls.OBJECTIVE_PROGRESS,
            cls.COMPLETION,
            cls.CORRECTNESS,
            cls.QUALITY,
            cls.CONSTRAINT_COMPLIANCE,
            cls.POLICY_COMPLIANCE,
            cls.SECURITY_COMPLIANCE,
            cls.TIMELINESS,
            cls.EFFICIENCY,
            cls.EFFORT_PROPORTIONALITY,
            cls.UNCERTAINTY_REDUCTION,
            cls.RISK_REDUCTION,
            cls.RECOVERY_SUCCESS,
            cls.SIDE_EFFECT_CONTAINMENT,
            cls.REVERSIBILITY,
            cls.ARTIFACT_ACCEPTANCE,
            cls.DECISION_ADEQUACY,
            cls.ACTION_POSTCONDITION_SATISFACTION,
            cls.USER_ACCEPTANCE,
            cls.EXTERNAL_AUTHORITY_ACCEPTANCE,
            cls.UNKNOWN,
        )


@dataclass(frozen=True)
class ExecutivePerformanceCriteria:
    """
    Immutable container for a set of performance criteria.

    A criteria set is the complete collection of criteria against which
    performance is assessed.
    """

    criteria_id: str
    """Unique identifier for this criteria set."""

    criteria: Tuple[ExecutivePerformanceCriterion, ...]
    """The criteria in this set."""

    subject_kind: str = "EXECUTIVE_PROGRAM"
    """Kind of subject these criteria apply to."""

    @classmethod
    def default(cls) -> ExecutivePerformanceCriteria:
        """Create a default criteria set with common criteria."""
        return cls(
            criteria_id="default_criteria",
            criteria=(
                ExecutivePerformanceCriterion(
                    criterion_id="goal_satisfaction",
                    kind=ExecutivePerformanceCriterionKind.GOAL_SATISFACTION,
                ),
                ExecutivePerformanceCriterion(
                    criterion_id="commitment_fulfillment",
                    kind=ExecutivePerformanceCriterionKind.COMMITMENT_FULFILLMENT,
                ),
                ExecutivePerformanceCriterion(
                    criterion_id="correctness",
                    kind=ExecutivePerformanceCriterionKind.CORRECTNESS,
                ),
            ),
        )


__all__: Tuple[str, ...] = (
    "ExecutivePerformanceCriterion",
    "ExecutivePerformanceCriterionKind",
    "ExecutivePerformanceCriteria",
)