# Executive Performance Confidence
# ===============================

"""
Canonical immutable ExecutivePerformanceConfidence definitions.

Performance confidence represents certainty in the assessment.
"""

from __future__ import annotations

from typing import Tuple


class ExecutivePerformanceConfidence:
    """
    Typed taxonomy of executive performance confidence levels.

    Each class represents a level of certainty in the performance assessment.
    """

    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    """High confidence (e.g., >0.8)."""

    MODERATE_CONFIDENCE = "MODERATE_CONFIDENCE"
    """Moderate confidence (e.g., 0.5-0.8)."""

    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    """Low confidence (<0.5)."""

    UNKNOWN = "UNKNOWN"
    """Confidence is unknown or unassessed."""

    @classmethod
    def all_confidences(cls) -> Tuple[str, ...]:
        """Return all valid confidence levels as a tuple."""
        return (
            cls.HIGH_CONFIDENCE,
            cls.MODERATE_CONFIDENCE,
            cls.LOW_CONFIDENCE,
            cls.UNKNOWN,
        )


__all__: Tuple[str, ...] = ("ExecutivePerformanceConfidence",)