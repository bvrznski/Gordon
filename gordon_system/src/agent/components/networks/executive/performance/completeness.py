# Executive Performance Completeness
# ===================================

"""
Canonical immutable ExecutivePerformanceCompleteness definitions.

Performance completeness represents how complete the evidence is.
"""

from __future__ import annotations

from typing import Tuple


class ExecutivePerformanceCompleteness:
    """
    Typed taxonomy of executive performance completeness levels.
    """

    COMPLETE = "COMPLETE"
    """All relevant evidence is present."""

    SUBSTANTIALLY_COMPLETE = "SUBSTANTIALLY_COMPLETE"
    """Most relevant evidence is present, minor gaps remain."""

    PARTIAL = "PARTIAL"
    """Some evidence present, significant gaps remain."""

    MINIMAL = "MINIMAL"
    """Minimal evidence present, major gaps remain."""

    MISSING = "MISSING"
    """No relevant evidence present."""

    INVALID = "INVALID"
    """Evidence is invalid or corrupted."""

    UNKNOWN = "UNKNOWN"
    """Completeness is unknown or unassessed."""

    @classmethod
    def all_completeness(cls) -> Tuple[str, ...]:
        """Return all valid completeness levels as a tuple."""
        return (
            cls.COMPLETE,
            cls.SUBSTANTIALLY_COMPLETE,
            cls.PARTIAL,
            cls.MINIMAL,
            cls.MISSING,
            cls.INVALID,
            cls.UNKNOWN,
        )


__all__: Tuple[str, ...] = ("ExecutivePerformanceCompleteness",)