# Executive Performance Status
# ============================

"""
Canonical immutable ExecutivePerformanceStatus definitions.

Performance status is the overall assessment of how well a subject is progressing.
"""

from __future__ import annotations

from typing import Tuple


class ExecutivePerformanceStatus:
    """
    Typed taxonomy of executive performance statuses.

    Each status represents an overall assessment of performance state.
    """

    NOT_ASSESSED = "NOT_ASSESSED"
    """Not yet assessed."""

    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    """Insufficient evidence to assess."""

    ON_TRACK = "ON_TRACK"
    """On track toward objectives."""

    AHEAD_OF_EXPECTATION = "AHEAD_OF_EXPECTATION"
    """Ahead of expected progress."""

    ACCEPTABLE = "ACCEPTABLE"
    """Acceptable performance level."""

    MARGINALLY_ACCEPTABLE = "MARGINALLY_ACCEPTABLE"
    """Marginally acceptable, with concerns."""

    BELOW_EXPECTATION = "BELOW_EXPECTATION"
    """Below expected performance."""

    DETERIORATING = "DETERIORATING"
    """Performance is deteriorating."""

    STALLED = "STALLED"
    """Progress has stalled."""

    REGRESSING = "REGRESSING"
    """Performance is regressing."""

    UNSUCCESSFUL = "UNSUCCESSFUL"
    """Unsuccessful performance."""

    FAILED = "FAILED"
    """Failed performance."""

    COMPLETED = "COMPLETED"
    """Successfully completed."""

    COMPLETED_WITH_LIMITATIONS = "COMPLETED_WITH_LIMITATIONS"
    """Completed but with limitations."""

    DISPUTED = "DISPUTED"
    """Performance is disputed."""

    INVALID = "INVALID"
    """Invalid assessment (e.g., invalid criteria)."""

    UNKNOWN = "UNKNOWN"
    """Unknown or unclassified status."""

    @classmethod
    def all_statuses(cls) -> Tuple[str, ...]:
        """Return all valid statuses as a tuple."""
        return (
            cls.NOT_ASSESSED,
            cls.INSUFFICIENT_EVIDENCE,
            cls.ON_TRACK,
            cls.AHEAD_OF_EXPECTATION,
            cls.ACCEPTABLE,
            cls.MARGINALLY_ACCEPTABLE,
            cls.BELOW_EXPECTATION,
            cls.DETERIORATING,
            cls.STALLED,
            cls.REGRESSING,
            cls.UNSUCCESSFUL,
            cls.FAILED,
            cls.COMPLETED,
            cls.COMPLETED_WITH_LIMITATIONS,
            cls.DISPUTED,
            cls.INVALID,
            cls.UNKNOWN,
        )


__all__: Tuple[str, ...] = ("ExecutivePerformanceStatus",)