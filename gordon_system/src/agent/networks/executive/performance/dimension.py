# Executive Performance Dimension
# ===============================

"""
Canonical immutable ExecutivePerformanceDimension definitions.

Performance dimensions are axes along which performance is assessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutivePerformanceDimensionAssessment:
    """
    Assessment of performance along a single dimension.
    """

    dimension: str
    """The dimension being assessed."""

    status: str = "unknown"
    """Status in this dimension."""

    confidence_class: str = "unknown"
    """Confidence classification."""

    completeness_class: str = "partial"
    """Completeness classification."""

    evidence: Tuple[str, ...] = ()
    """Evidence items supporting this assessment."""


class ExecutivePerformanceDimension:
    """
    Typed taxonomy of executive performance dimensions.
    """

    PROGRESS = "PROGRESS"
    """Progress toward objectives."""

    COMPLETION = "COMPLETION"
    """Completion state."""

    CORRECTNESS = "CORRECTNESS"
    """Result correctness."""

    QUALITY = "QUALITY"
    """Outcome quality."""

    EFFICIENCY = "EFFICIENCY"
    """Efficiency of effort."""

    EFFECTIVENESS = "EFFECTIVENESS"
    """Effectiveness in achieving objectives."""

    TIMELINESS = "TIMELINESS"
    """Timeliness of results."""

    RELIABILITY = "RELIABILITY"
    """Reliability and consistency."""

    CONSISTENCY = "CONSISTENCY"
    """Consistency with criteria."""

    COHERENCE = "COHERENCE"
    """Coherence of reasoning and action."""

    SAFETY = "SAFETY"
    """Safety and risk."""

    POLICY_COMPLIANCE = "POLICY_COMPLIANCE"
    """Policy compliance."""

    SECURITY_COMPLIANCE = "SECURITY_COMPLIANCE"
    """Security compliance."""

    REVERSIBILITY = "REVERSIBILITY"
    """Reversibility of outcomes."""

    UNCERTAINTY_REDUCTION = "UNCERTAINTY_REDUCTION"
    """Uncertainty reduction."""

    RISK_REDUCTION = "RISK_REDUCTION"
    """Risk reduction."""

    EFFORT_PROPORTIONALITY = "EFFORT_PROPORTIONALITY"
    """Effort proportionality."""

    RECOVERY_EFFECTIVENESS = "RECOVERY_EFFECTIVENESS"
    """Recovery effectiveness."""

    DECISION_QUALITY = "DECISION_QUALITY"
    """Decision quality."""

    ACTION_EFFECTIVENESS = "ACTION_EFFECTIVENESS"
    """Action effectiveness."""

    STRATEGY_EFFECTIVENESS = "STRATEGY_EFFECTIVENESS"
    """Strategy effectiveness."""

    TASK_SET_EFFECTIVENESS = "TASK_SET_EFFECTIVENESS"
    """Task set effectiveness."""

    CONTROL_EFFECTIVENESS = "CONTROL_EFFECTIVENESS"
    """Control effectiveness."""

    COMMITMENT_FULFILLMENT = "COMMITMENT_FULFILLMENT"
    """Commitment fulfillment."""

    GOAL_SATISFACTION = "GOAL_SATISFACTION"
    """Goal satisfaction."""

    SIDE_EFFECT_CONTAINMENT = "SIDE_EFFECT_CONTAINMENT"
    """Side effect containment."""

    UNKNOWN = "UNKNOWN"
    """Unknown or unclassified dimension."""

    @classmethod
    def all_dimensions(cls) -> Tuple[str, ...]:
        """Return all valid dimensions as a tuple."""
        return (
            cls.PROGRESS,
            cls.COMPLETION,
            cls.CORRECTNESS,
            cls.QUALITY,
            cls.EFFICIENCY,
            cls.EFFECTIVENESS,
            cls.TIMELINESS,
            cls.RELIABILITY,
            cls.CONSISTENCY,
            cls.COHERENCE,
            cls.SAFETY,
            cls.POLICY_COMPLIANCE,
            cls.SECURITY_COMPLIANCE,
            cls.REVERSIBILITY,
            cls.UNCERTAINTY_REDUCTION,
            cls.RISK_REDUCTION,
            cls.EFFORT_PROPORTIONALITY,
            cls.RECOVERY_EFFECTIVENESS,
            cls.DECISION_QUALITY,
            cls.ACTION_EFFECTIVENESS,
            cls.STRATEGY_EFFECTIVENESS,
            cls.TASK_SET_EFFECTIVENESS,
            cls.CONTROL_EFFECTIVENESS,
            cls.COMMITMENT_FULFILLMENT,
            cls.GOAL_SATISFACTION,
            cls.SIDE_EFFECT_CONTAINMENT,
            cls.UNKNOWN,
        )


__all__: Tuple[str, ...] = (
    "ExecutivePerformanceDimensionAssessment",
    "ExecutivePerformanceDimension",
)