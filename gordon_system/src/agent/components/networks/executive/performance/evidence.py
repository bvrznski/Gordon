# Executive Performance Evidence
# ==============================

"""
Canonical immutable ExecutivePerformanceEvidence definitions.

Performance evidence is what supports performance assessments - action results,
observations, evaluations, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutivePerformanceEvidence:
    """
    Immutable reference to a piece of performance evidence.

    Each evidence item must preserve source, revision, factuality, confidence,
    completeness, temporal validity, privacy, and provenance.
    """

    evidence_id: str
    """Unique identifier for this evidence."""

    kind: str  # ExecutivePerformanceEvidenceKind value
    """The semantic category of the evidence."""

    source: str = "unknown"
    """Source system or component that provided this evidence."""

    revision: int = 1
    """Revision number of the source evidence."""

    factuality_class: str = "observed"
    """Classification of factuality (observed, reported, inferred, etc.)."""

    confidence_class: str = "unknown"
    """Confidence classification."""

    completeness_class: str = "partial"
    """Completeness classification."""

    temporal_validity_seconds: float = 0.0
    """Temporal validity window in seconds (0 = no time bound)."""

    privacy_classification: str = "internal"
    """Privacy classification of this evidence."""

    provenance_created_by: str = "unknown"
    """Who/what created this evidence reference."""

    provenance_created_at_utc: float = 0.0
    """When this evidence was created (seconds since epoch)."""

    @classmethod
    def for_action_result(cls, action_id: str) -> ExecutivePerformanceEvidence:
        """Create evidence referencing an action result."""
        return cls(
            evidence_id=f"action_{action_id}",
            kind="ACTION_RESULT",
            source="action_execution",
        )

    @classmethod
    def for_observation(cls, observation_id: str) -> ExecutivePerformanceEvidence:
        """Create evidence referencing an observation."""
        return cls(
            evidence_id=observation_id,
            kind="OBSERVATION",
            source="monitoring",
        )


class ExecutivePerformanceEvidenceKind:
    """
    Typed taxonomy of executive performance evidence kinds.
    """

    ACTION_RESULT = "ACTION_RESULT"
    """Result from action execution."""

    ACTION_OUTCOME = "ACTION_OUTCOME"
    """Outcome from action execution."""

    OBSERVATION = "OBSERVATION"
    """Observation from monitoring systems."""

    MONITORING_RESULT = "MONITORING_RESULT"
    """Result from monitoring evaluation."""

    EVALUATION_RESULT = "EVALUATION_RESULT"
    """Result from evaluation capability assessment."""

    GOAL_SATISFACTION_ASSESSMENT = "GOAL_SATISFACTION_ASSESSMENT"
    """Goal satisfaction assessment."""

    COMMITMENT_FULFILLMENT_ASSESSMENT = "COMMITMENT_FULFILLMENT_ASSESSMENT"
    """Commitment fulfillment assessment."""

    PLAN_PROGRESS = "PLAN_PROGRESS"
    """Plan progress information."""

    REASONING_RESULT = "REASONING_RESULT"
    """Result from reasoning process."""

    DECISION_RESULT = "DECISION_RESULT"
    """Result from decision computation."""

    PREDICTION = "PREDICTION"
    """Prediction from predictive network."""

    PREDICTION_ERROR = "PREDICTION_ERROR"
    """Prediction error from predictive network."""

    USER_FEEDBACK = "USER_FEEDBACK"
    """Feedback from user."""

    EXTERNAL_AUTHORITY_DECISION = "EXTERNAL_AUTHORITY_DECISION"
    """Decision from external authority."""

    ARTIFACT_ACCEPTANCE = "ARTIFACT_ACCEPTANCE"
    """Artifact acceptance information."""

    ARTIFACT_REJECTION = "ARTIFACT_REJECTION"
    """Artifact rejection information."""

    POLICY_DECISION = "POLICY_DECISION"
    """Policy authority decision."""

    SECURITY_DECISION = "SECURITY_DECISION"
    """Security authority decision."""

    WORKING_MEMORY_PROJECTION = "WORKING_MEMORY_PROJECTION"
    """Working memory state projection."""

    WORKSPACE_FEEDBACK = "WORKSPACE_FEEDBACK"
    """Workspace feedback information."""

    RUNTIME_TELEMETRY_PROJECTION = "RUNTIME_TELEMETRY_PROJECTION"
    """Runtime telemetry projection (when semantically relevant)."""

    OTHER = "OTHER"
    """Other evidence type."""

    UNKNOWN = "UNKNOWN"
    """Unknown or unclassified evidence kind."""

    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid evidence kinds as a tuple."""
        return (
            cls.ACTION_RESULT,
            cls.ACTION_OUTCOME,
            cls.OBSERVATION,
            cls.MONITORING_RESULT,
            cls.EVALUATION_RESULT,
            cls.GOAL_SATISFACTION_ASSESSMENT,
            cls.COMMITMENT_FULFILLMENT_ASSESSMENT,
            cls.PLAN_PROGRESS,
            cls.REASONING_RESULT,
            cls.DECISION_RESULT,
            cls.PREDICTION,
            cls.PREDICTION_ERROR,
            cls.USER_FEEDBACK,
            cls.EXTERNAL_AUTHORITY_DECISION,
            cls.ARTIFACT_ACCEPTANCE,
            cls.ARTIFACT_REJECTION,
            cls.POLICY_DECISION,
            cls.SECURITY_DECISION,
            cls.WORKING_MEMORY_PROJECTION,
            cls.WORKSPACE_FEEDBACK,
            cls.RUNTIME_TELEMETRY_PROJECTION,
            cls.OTHER,
            cls.UNKNOWN,
        )


__all__: Tuple[str, ...] = (
    "ExecutivePerformanceEvidence",
    "ExecutivePerformanceEvidenceKind",
)