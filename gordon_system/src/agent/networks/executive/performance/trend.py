# Executive Performance Trend
# ===========================

"""
Canonical immutable ExecutivePerformanceTrend definitions.

Performance trend represents how performance is changing over time.
"""

from __future__ import annotations

from typing import Tuple


class ExecutivePerformanceTrend:
    """
    Typed taxonomy of executive performance trends.

    Each trend classifies the direction and nature of performance change.
    """

    IMPROVING = "IMPROVING"
    """Performance is improving."""

    STABLE = "STABLE"
    """Performance is stable (no significant change)."""

    VOLATILE = "VOLATILE"
    """Performance is volatile (unpredictable changes)."""

    DECLINING = "DECLINING"
    """Performance is declining."""

    STAGNANT = "STAGNANT"
    """Performance is stagnant (no progress, no decline)."""

    REGRESSING = "REGRESSING"
    """Performance is regressing (getting worse)."""

    RECOVERING = "RECOVERING"
    """Performance is recovering from a failure or setback."""

    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    """Insufficient history to determine trend."""

    UNKNOWN = "UNKNOWN"
    """Unknown or unclassified trend."""

    @classmethod
    def all_trends(cls) -> Tuple[str, ...]:
        """Return all valid trends as a tuple."""
        return (
            cls.IMPROVING,
            cls.STABLE,
            cls.VOLATILE,
            cls.DECLINING,
            cls.STAGNANT,
            cls.REGRESSING,
            cls.RECOVERING,
            cls.INSUFFICIENT_HISTORY,
            cls.UNKNOWN,
        )


__all__: Tuple[str, ...] = ("ExecutivePerformanceTrend",)