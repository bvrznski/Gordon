# Salience Network Evaluation Enums
# ==================================

"""
Canonical enumeration types for evaluation (Phase 4.8.5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class SalienceDimension(Enum):
    """
    Canonical salience dimension enumeration.
    
    Each dimension represents a distinct semantic axis of significance.
    """
    SIGNIFICANCE = auto()
    RELEVANCE = auto()
    NOVELTY = auto()
    URGENCY = auto()
    UNCERTAINTY = auto()
    CONFLICT = auto()
    PREDICTION_ERROR = auto()
    MOTIVATIONAL = auto()
    EMOTIONAL = auto()
    THREAT = auto()
    OPPORTUNITY = auto()
    SOCIAL = auto()
    CONTEXTUAL = auto()
    MEMORY = auto()
    GOAL = auto()
    EXECUTIVE = auto()


class SalienceEvaluationStatus(Enum):
    """
    Evaluation result status.
    
    Represents the overall outcome of evaluation.
    """
    COMPLETE = auto()
    """Successfully completed evaluation with full assessment."""
    PROVISIONAL = auto()
    """Evaluation succeeded but may have limitations or incomplete data."""
    DEGRADED = auto()
    """Evaluation produced degraded assessment due to missing input."""
    CONFLICTED = auto()
    """Evaluation detected unresolved conflicts in evidence."""
    INSUFFICIENT_EVIDENCE = auto()
    """Input lacks sufficient evidence for meaningful assessment."""
    REJECTED = auto()
    """Request was rejected due to invalid or malformed input."""
    INVALID = auto()
    """Input failed validation."""
    UNSUPPORTED = auto()
    """Request contains unsupported schema or source kinds."""


class SalienceDimensionStatus(Enum):
    """
    Dimension evaluation status.
    
    Represents the outcome for an individual dimension evaluator.
    """
    NOT_EVALUATED = auto()
    """Dimension was not evaluated (e.g., no relevant input)."""
    INSUFFICIENT_INPUT = auto()
    """Input insufficient for dimension evaluation."""
    PROVISIONAL = auto()
    """Evaluation produced provisional assessment."""
    COMPLETE = auto()
    """Successfully completed dimension evaluation."""
    CONFLICTED = auto()
    """Evidence contains unresolved conflicts."""
    DEGRADED = auto()
    """Evaluation was degraded due to missing or uncertain input."""
    INVALID = auto()
    """Input failed validation for this dimension."""
    UNSUPPORTED = auto()
    """Source kind not supported by this evaluator."""


class SalienceAggregationStatus(Enum):
    """
    Evidence aggregation result status.
    """
    COMPLETE = auto()
    """All evidence successfully aggregated."""
    PARTIAL = auto()
    """Some evidence was aggregated with limitations."""
    CONFLICTED = auto()
    """Authority conflicts detected during aggregation."""
    DEGRADED = auto()
    """Aggregation produced degraded output."""
    INSUFFICIENT = auto()
    """Insufficient evidence for meaningful aggregation."""
    INVALID = auto()
    """Input failed validation."""


class SalienceCompositionStatus(Enum):
    """
    Assessment composition result status.
    """
    COMPLETE = auto()
    """Assessment composed successfully."""
    PROVISIONAL = auto()
    """Composition produced provisional assessment."""
    DEGRADED = auto()
    """Composition was degraded due to missing dimensions."""
    CONFLICTED = auto()
    """Conflicting dimensions detected."""
    INSUFFICIENT = auto()
    """Missing required dimensions for composition."""
    INVALID = auto()
    """Input failed validation."""


@dataclass(frozen=True, slots=True)
class SalienceLevel:
    """
    Canonical qualitative salience level.
    
    Represents the semantic intensity of a salience assessment.
    """
    UNKNOWN = "unknown"
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_value(cls, value: str) -> SalienceLevel:
        """Convert string to SalienceLevel."""
        mapping = {
            "unknown": cls.UNKNOWN,
            "negligible": cls.NEGLIGIBLE,
            "low": cls.LOW,
            "moderate": cls.MODERATE,
            "high": cls.HIGH,
            "critical": cls.CRITICAL,
        }
        if value not in mapping:
            raise ValueError(f"Unknown SalienceLevel value: {value}")
        return mapping[value]

    def is_valid(self) -> bool:
        """Check if this level represents valid evaluation output."""
        return self != self.UNKNOWN

    @property
    def intensity_rank(self) -> int:
        """Return numeric rank for comparison (higher = more intense)."""
        ranks = {
            SalienceLevel.UNKNOWN: 0,
            SalienceLevel.NEGLIGIBLE: 1,
            SalienceLevel.LOW: 2,
            SalienceLevel.MODERATE: 3,
            SalienceLevel.HIGH: 4,
            SalienceLevel.CRITICAL: 5,
        }
        return ranks[self]