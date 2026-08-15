# Audit Constants - Gordon Executive Network Audit Subsystem
# ============================================================

"""
Standard constants for the Executive Audit subsystem.
"""

from typing import Tuple, Literal

# =============================================================================
# VERSION AND IDENTIFIERS
# =============================================================================

AUDIT_VERSION: str = "4.4.11"
"""Current audit subsystem version."""

AUDIT_PACKAGE_NAME: str = "executive.audit"
"""Canonical package name for audit subsystem."""

# =============================================================================
# BOUNDS AND LIMITS
# =============================================================================

MAX_FINDINGS_PER_SESSION: int = 100
"""Maximum findings per audit session."""

MAX_REPORTS_PER_HISTORY: int = 1000
"""Maximum reports to retain in history."""

MAX_EVIDENCE_PER_SESSION: int = 1000
"""Maximum evidence items per audit session."""

DEFAULT_AUDIT_INTERVAL_SECONDS: float = 60.0
"""Default interval between automated audits (60 seconds)."""

MINIMUM_AUDIT_INTERVAL_SECONDS: float = 1.0
"""Minimum allowed interval between audits (for testing)."""

MAXIMUM_AUDIT_INTERVAL_SECONDS: float = 86400.0
"""Maximum allowed interval between audits (24 hours)."""

# =============================================================================
# SEVERITY LEVELS
# =============================================================================

AUDIT_SEVERITY_LEVELS: Tuple[str, ...] = (
    "critical",
    "high",
    "medium",
    "low",
    "info",
)
"""All valid severity levels in order of increasing severity."""

SEVERITY_SCORES: dict = {
    "critical": 1.0,
    "high": 0.85,
    "medium": 0.60,
    "low": 0.35,
    "info": 0.15,
}
"""Default severity scores (0-1)."""

SEVERITY_COLORS: dict = {
    "critical": "red",
    "high": "orange",
    "medium": "yellow",
    "low": "green",
    "info": "blue",
}
"""Colors for severity levels in reports."""

# =============================================================================
# RISK LEVELS
# =============================================================================

AUDIT_RISK_LEVELS: Tuple[str, ...] = (
    "negligible",
    "low",
    "medium",
    "high",
)
"""All valid risk levels in order of increasing risk."""

RISK_SCORE_RANGES: dict = {
    "negligible": (0, 25),
    "low": (26, 49),
    "medium": (50, 79),
    "high": (80, 100),
}
"""Score ranges for risk levels."""

RISK_COLORS: dict = {
    "negligible": "green",
    "low": "yellow",
    "medium": "orange",
    "high": "red",
}
"""Colors for risk levels in reports."""

# =============================================================================
# AUDIT STATUS VALUES
# =============================================================================

AUDIT_STATUS_PENDING: str = "pending"
AUDIT_STATUS_RUNNING: str = "running"
AUDIT_STATUS_COMPLETED: str = "completed"
AUDIT_STATUS_FAILED: str = "failed"
AUDIT_STATUS_DEGRADED: str = "degraded"

AUDIT_STATUSES: Tuple[str, ...] = (
    AUDIT_STATUS_PENDING,
    AUDIT_STATUS_RUNNING,
    AUDIT_STATUS_COMPLETED,
    AUDIT_STATUS_FAILED,
    AUDIT_STATUS_DEGRADED,
)
"""All valid audit status values."""

# =============================================================================
# AUDIT TYPE VALUES
# =============================================================================

AUDIT_TYPE_ON_DEMAND: str = "on_demand"
AUDIT_TYPE_SCHEDULED: str = "scheduled"
AUDIT_TYPE_CONTINUOUS: str = "continuous"
AUDIT_TYPE_INTEGRITY_CHECK: str = "integrity_check"
AUDIT_TYPE_POST_MORTEM: str = "post_mortem"

AUDIT_TYPES: Tuple[str, ...] = (
    AUDIT_TYPE_ON_DEMAND,
    AUDIT_TYPE_SCHEDULED,
    AUDIT_TYPE_CONTINUOUS,
    AUDIT_TYPE_INTEGRITY_CHECK,
    AUDIT_TYPE_POST_MORTEM,
)
"""All valid audit types."""

# =============================================================================
# EVIDENCE SOURCE CATEGORIES
# =============================================================================

EVIDENCE_SOURCE_STATE: str = "state"
EVIDENCE_SOURCE_CONTEXT: str = "context"
EVIDENCE_SOURCE_PROGRAMS: str = "programs"
EVIDENCE_SOURCE_GOALS: str = "goals"
EVIDENCE_SOURCE_COMMITMENTS: str = "commitments"
EVIDENCE_SOURCE_CONFLICTS: str = "conflicts"
EVIDENCE_SOURCE_DEMAND: str = "demand"
EVIDENCE_SOURCE_PERFORMANCE: str = "performance"
EVIDENCE_SOURCE_POLICY: str = "policy"
EVIDENCE_SOURCE_DECISIONS: str = "decisions"

EVIDENCE_SOURCES: Tuple[str, ...] = (
    EVIDENCE_SOURCE_STATE,
    EVIDENCE_SOURCE_CONTEXT,
    EVIDENCE_SOURCE_PROGRAMS,
    EVIDENCE_SOURCE_GOALS,
    EVIDENCE_SOURCE_COMMITMENTS,
    EVIDENCE_SOURCE_CONFLICTS,
    EVIDENCE_SOURCE_DEMAND,
    EVIDENCE_SOURCE_PERFORMANCE,
    EVIDENCE_SOURCE_POLICY,
    EVIDENCE_SOURCE_DECISIONS,
)
"""All evidence source categories."""

# =============================================================================
# INTEGRITY CHECK CONSTANTS
# =============================================================================

INTEGRITY_CHECK_VERSION: str = "1.0"
"""Version of integrity check specification."""

EXPECTED_ENGINE_COUNT: int = 1
"""Expected count of canonical audit engines (exactly one)."""

MAX_HISTORY_SIZE_BYTES: int = 10_000_000
"""Maximum total history size in bytes before eviction."""

MIN_RETENTION_PERIOD_SECONDS: float = 3600.0
"""Minimum retention period for historical data (1 hour)."""

# =============================================================================
# DEGRADATION MODES
# =============================================================================

DEGRADED_MODE_NONE: str = "none"
DEGRADED_MODE_PARTIAL: str = "partial"
DEGRADED_MODE_CRITICAL: str = "critical"

DEGRADED_MODES: Tuple[str, ...] = (
    DEGRADED_MODE_NONE,
    DEGRADED_MODE_PARTIAL,
    DEGRADED_MODE_CRITICAL,
)
"""All degradation modes."""

# =============================================================================
# REPORTING CONSTANTS
# =============================================================================

DEFAULT_REPORT_FORMAT: str = "json"
"""Default report output format."""

MAX_REPORT_FIELD_LENGTH: int = 10_000
"""Maximum length of text fields in reports before truncation."""

INCLUDE_PROVENANCE_DEFAULT: bool = True
"""Whether to include provenance by default in reports."""

# =============================================================================
# TIMEOUT CONSTANTS
# =============================================================================

DEFAULT_TIMEOUT_SECONDS: float = 30.0
"""Default timeout for audit operations."""

MAX_TIMEOUT_SECONDS: float = 3600.0
"""Maximum allowed timeout (1 hour)."""

MIN_TIMEOUT_SECONDS: float = 0.1
"""Minimum allowed timeout (100ms for testing)."""