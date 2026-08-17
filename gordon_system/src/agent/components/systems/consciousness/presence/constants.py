# Gordon Phase 5.7.5-I: Presence Engine - Constants
# ===============================================================================
"""
Canonical constants for the Presence Engine.

This module defines:
    - Presence state transitions and lifecycle states
    - Admission policy constants
    - Persistence policy constants
    - Fading model constants
"""

from __future__ import annotations

from typing import Tuple


# =============================================================================
# PRESENCE LIFECYCLE STATES
# =============================================================================

PRESENCE_STATE_CANDIDATE = "candidate"
"""Content has been proposed but not yet admitted to presence."""

PRESENCE_STATE_ADMITTED = "admitted"
"""Content is admitted and awaiting activation into conscious accessibility."""

PRESENCE_STATE_ACTIVE = "active"
"""Content is consciously accessible in the current context."""

PRESENCE_STATE_WEAKENING = "weakening"
"""Transitional state as fading begins (intermediate)."""

PRESENCE_STATE_FADING = "fading"
"""Content is gradually withdrawing from presence."""

PRESENCE_STATE_SUSPENDED = "suspended"
"""Content temporarily suspended (not withdrawn, can resume)."""

PRESENCE_STATE_WITHDRAWN = "withdrawn"
"""Content is no longer consciously accessible and has been removed."""

VALID_PRESENCE_STATES: Tuple[str, ...] = (
    PRESENCE_STATE_CANDIDATE,
    PRESENCE_STATE_ADMITTED,
    PRESENCE_STATE_ACTIVE,
    PRESENCE_STATE_WEAKENING,
    PRESENCE_STATE_FADING,
    PRESENCE_STATE_SUSPENDED,
    PRESENCE_STATE_WITHDRAWN,
)


# =============================================================================
# ADMISSION POLICY CONSTANTS
# =============================================================================

ADMISSION_POLICY_SOURCE_VALIDATION = "source_validation"
"""Validate source identity before admission."""

ADMISSION_POLICY_FRESHNESS_CHECK = "freshness_check"
"""Check content freshness timestamp before admission."""

ADMISSION_POLICY_CAPACITY_LIMIT = "capacity_limit"
"""Enforce capacity limits for presence pool."""

VALID_ADMISSION_POLICIES: Tuple[str, ...] = (
    ADMISSION_POLICY_SOURCE_VALIDATION,
    ADMISSION_POLICY_FRESHNESS_CHECK,
    ADMISSION_POLICY_CAPACITY_LIMIT,
)

DEFAULT_MAX_ACTIVE_PRESENCE = 100
"""Maximum number of concurrently active presence items."""

DEFAULT_MAX_ADMITTED = 200
"""Maximum number of admitted (but not yet active) items."""


# =============================================================================
# PERSISTENCE POLICY CONSTANTS
# =============================================================================

PERSISTENCE_POLICY_EXPIRY = "expiry"
"""Content expires after configured duration."""

PERSISTENCE_POLICY_REUSE = "reuse"
"""Expired content may be re-admitted under same identity."""

VALID_PERSISTENCE_POLICIES: Tuple[str, ...] = (
    PERSISTENCE_POLICY_EXPIRY,
    PERSISTENCE_POLICY_REUSE,
)

DEFAULT_CONTENT_LIFETIME_SECONDS = 3600.0
"""Default content lifetime in seconds (1 hour)."""

DEFAULT_FADING_GRACE_PERIOD_SECONDS = 300.0
"""Grace period before fading begins (5 minutes)."""


# =============================================================================
# FADE TRANSITION CONSTANTS
# =============================================================================

FADE_TRANSITION_TYPE_MANUAL = "manual"
"""Fade triggered by explicit request."""

FADE_TRANSITION_TYPE_EXPIRY = "expiry"
"""Fade triggered by policy expiration."""

FADE_TRANSITION_TYPE_CAPACITY = "capacity"
"""Fade triggered by capacity pressure."""

VALID_FADE_TRANSITION_TYPES: Tuple[str, ...] = (
    FADE_TRANSITION_TYPE_MANUAL,
    FADE_TRANSITION_TYPE_EXPIRY,
    FADE_TRANSITION_TYPE_CAPACITY,
)

DEFAULT_WEAKENING_DURATION_SECONDS = 60.0
"""Duration in weakening state before full fading (1 minute)."""

DEFAULT_FADE_DURATION_SECONDS = 30.0
"""Duration in fading state before withdrawal (30 seconds)."""


# =============================================================================
# TRANSITION KINDS
# =============================================================================

TRANSITION_KIND_ADMISSION = "admission"
"""Content admitted to presence."""

TRANSITION_KIND_WITHDRAWAL = "withdrawal"
"""Content withdrawn from presence."""

TRANSITION_KIND_FADE_START = "fade_start"
"""Fade transition initiated (candidate → weakening)."""

TRANSITION_KIND_RESUME = "resume"
"""Suspended content resumed to active."""

TRANSITION_KIND_INTERRUPT = "interrupt"
"""Active content interrupted (active → suspended)."""

VALID_TRANSITION_KINDS: Tuple[str, ...] = (
    TRANSITION_KIND_ADMISSION,
    TRANSITION_KIND_WITHDRAWAL,
    TRANSITION_KIND_FADE_START,
    TRANSITION_KIND_RESUME,
    TRANSITION_KIND_INTERRUPT,
)


# =============================================================================
# DIAGNOSTICS METRICS
# =============================================================================

METRIC_ADMITTED_TOTAL = "admitted_total"
"""Total items admitted since initialization."""

METRIC_WITHDRAWN_TOTAL = "withdrawn_total"
"""Total items withdrawn since initialization."""

METRIC_ACTIVE_COUNT = "active_count"
"""Current number of active presence items."""

METRIC_FADE_COUNT = "fade_count"
"""Current number of fading presence items."""

METRIC_ADMISSION_FAILURES = "admission_failures"
"""Total admission failures (policy violations)."""

VALID_METRICS: Tuple[str, ...] = (
    METRIC_ADMITTED_TOTAL,
    METRIC_WITHDRAWN_TOTAL,
    METRIC_ACTIVE_COUNT,
    METRIC_FADE_COUNT,
    METRIC_ADMISSION_FAILURES,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # State constants
    "PRESENCE_STATE_CANDIDATE",
    "PRESENCE_STATE_ADMITTED",
    "PRESENCE_STATE_ACTIVE",
    "PRESENCE_STATE_WEAKENING",
    "PRESENCE_STATE_FADING",
    "PRESENCE_STATE_SUSPENDED",
    "PRESENCE_STATE_WITHDRAWN",
    "VALID_PRESENCE_STATES",
    # Admission policy constants
    "ADMISSION_POLICY_SOURCE_VALIDATION",
    "ADMISSION_POLICY_FRESHNESS_CHECK",
    "ADMISSION_POLICY_CAPACITY_LIMIT",
    "VALID_ADMISSION_POLICIES",
    "DEFAULT_MAX_ACTIVE_PRESENCE",
    "DEFAULT_MAX_ADMITTED",
    # Persistence policy constants
    "PERSISTENCE_POLICY_EXPIRY",
    "PERSISTENCE_POLICY_REUSE",
    "VALID_PERSISTENCE_POLICIES",
    "DEFAULT_CONTENT_LIFETIME_SECONDS",
    "DEFAULT_FADING_GRACE_PERIOD_SECONDS",
    # Fade transition constants
    "FADE_TRANSITION_TYPE_MANUAL",
    "FADE_TRANSITION_TYPE_EXPIRY",
    "FADE_TRANSITION_TYPE_CAPACITY",
    "VALID_FADE_TRANSITION_TYPES",
    "DEFAULT_WEAKENING_DURATION_SECONDS",
    "DEFAULT_FADE_DURATION_SECONDS",
    # Transition kinds
    "TRANSITION_KIND_ADMISSION",
    "TRANSITION_KIND_WITHDRAWAL",
    "TRANSITION_KIND_FADE_START",
    "TRANSITION_KIND_RESUME",
    "TRANSITION_KIND_INTERRUPT",
    "VALID_TRANSITION_KINDS",
    # Diagnostics metrics
    "METRIC_ADMITTED_TOTAL",
    "METRIC_WITHDRAWN_TOTAL",
    "METRIC_ACTIVE_COUNT",
    "METRIC_FADE_COUNT",
    "METRIC_ADMISSION_FAILURES",
    "VALID_METRICS",
)