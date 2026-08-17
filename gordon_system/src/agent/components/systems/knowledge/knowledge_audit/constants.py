# Knowledge Audit Constants - Phase 6.10
# ======================================

"""
Constants for the Knowledge Audit subsystem.
"""

from __future__ import annotations


# =============================================================================
# AUDIT THRESHOLDS
# =============================================================================

DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5
"""Minimum acceptable confidence level for knowledge to be considered supported."""

DEFAULT_UNCERTAINTY_THRESHOLD: float = 0.5
"""Maximum acceptable uncertainty level for knowledge to be considered well-defined."""

DEFAULT_COVERAGE_THRESHOLD: float = 0.7
"""Minimum coverage ratio (evidence count / expected evidence) required for acceptance."""

MIN_EVIDENCE_COUNT: int = 1
"""Minimum number of evidence references required for a knowledge artifact."""

MAX_CONTRADICTION_RATIO: float = 0.2
"""Maximum ratio of contradicting evidence before marking as contradicted."""


# =============================================================================
# AUDIT TIME WINDOWS (seconds)
# =============================================================================

FRESHNESS_RECENT_THRESHOLD: float = 86400.0  # 24 hours
"""Time window for considering knowledge as "recent"."""

FRESHNESS_WARNING_THRESHOLD: float = 604800.0  # 7 days
"""Time window after which freshness warnings are issued."""

FRESHNESS_OBSOLETE_THRESHOLD: float = 2592000.0  # 30 days
"""Time window after which knowledge may be considered potentially obsolete."""


# =============================================================================
# HEALTH METRIC BOUNDS
# =============================================================================

MIN_HEALTH_SCORE: float = 0.0
MAX_HEALTH_SCORE: float = 1.0

MIN_COVERAGE_SCORE: float = 0.0
MAX_COVERAGE_SCORE: float = 1.0

MIN_CONSISTENCY_SCORE: float = 0.0
MAX_CONSISTENCY_SCORE: float = 1.0


# =============================================================================
# AUDIT SESSION CONFIGURATION
# =============================================================================

DEFAULT_SESSION_TIMEOUT_SECONDS: int = 3600  # 1 hour
"""Default timeout for audit sessions."""

MAX_AUDIT_TARGETS_PER_REQUEST: int = 1000
"""Maximum number of targets that can be audited in a single request."""


# =============================================================================
# RECOMMENDATION WEIGHTS
# =============================================================================

RECOMMENDATION_WEIGHT_VERIFY: float = 1.0
RECOMMENDATION_WEIGHT_REVALIDATE: float = 2.0
RECOMMENDATION_WEIGHT_RELEARN: float = 3.0
RECOMMENDATION_WEIGHT_CONSOLIDATE: float = 4.0
RECOMMENDATION_WEIGHT_REMOVE: float = 5.0
RECOMMENDATION_WEIGHT_REQUEST_HUMAN_REVIEW: float = 10.0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "DEFAULT_UNCERTAINTY_THRESHOLD",
    "DEFAULT_COVERAGE_THRESHOLD",
    "MIN_EVIDENCE_COUNT",
    "MAX_CONTRADICTION_RATIO",
    "FRESHNESS_RECENT_THRESHOLD",
    "FRESHNESS_WARNING_THRESHOLD",
    "FRESHNESS_OBSOLETE_THRESHOLD",
    "MIN_HEALTH_SCORE",
    "MAX_HEALTH_SCORE",
    "MIN_COVERAGE_SCORE",
    "MAX_COVERAGE_SCORE",
    "MIN_CONSISTENCY_SCORE",
    "MAX_CONSISTENCY_SCORE",
    "DEFAULT_SESSION_TIMEOUT_SECONDS",
    "MAX_AUDIT_TARGETS_PER_REQUEST",
    "RECOMMENDATION_WEIGHT_VERIFY",
    "RECOMMENDATION_WEIGHT_REVALIDATE",
    "RECOMMENDATION_WEIGHT_RELEARN",
    "RECOMMENDATION_WEIGHT_CONSOLIDATE",
    "RECOMMENDATION_WEIGHT_REMOVE",
    "RECOMMENDATION_WEIGHT_REQUEST_HUMAN_REVIEW",
]