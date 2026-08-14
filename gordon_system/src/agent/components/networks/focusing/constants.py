# Focusing Network Constants
# ===========================

"""
Default values and bounds for the FocusingNetwork.

All constants are immutable and used throughout the network for:
    - Bounding computational ranges
    - Setting default behaviors
    - Defining thresholds
"""

from typing import Final

# ============================================================================
# BOUNDS
# ============================================================================

MIN_PRIORITY: Final[float] = 0.0
"""Minimum priority score (no focus needed)."""

MAX_PRIORITY: Final[float] = 1.0
"""Maximum priority score (critical attention demand)."""

MIN_PRECISION: Final[float] = 0.0
"""Minimum precision score (coarsest focus)."""

MAX_PRECISION: Final[float] = 1.0
"""Maximum precision score (sharpest focus)."""

MIN_PERSISTENCE: Final[float] = 0.0
"""Minimum persistence score (no maintenance needed)."""

MAX_PERSISTENCE: Final[float] = 1.0
"""Maximum persistence score (locked focus)."""

MIN_RELEVANCE: Final[float] = 0.0
"""Minimum relevance score (irrelevant to objectives)."""

MAX_RELEVANCE: Final[float] = 1.0
"""Maximum relevance score (highly relevant to objectives)."""

# ============================================================================
# DEFAULT VALUES
# ============================================================================

DEFAULT_DECAY_RATE: Final[float] = 0.95
"""
Default focus decay rate per assessment cycle.
Values closer to 1.0 mean slower decay (more persistent focus).
"""

DEFAULT_PERSISTENCE_THRESHOLD: Final[float] = 0.7
"""
Threshold above which focus is considered "maintained".
Below this, suppression or shift may be recommended.
"""

DEFAULT_PRECISION: Final[float] = 0.5
"""Default precision when not otherwise specified."""

DEFAULT_BUDGET_ALLOCATION: Final[float] = 1.0
"""
Default resource budget allocation factor.
Multiplies available resources for focus computation.
"""

# ============================================================================
# THRESHOLDS
# ============================================================================

SUPPRESSION_THRESHOLD: Final[float] = 0.3
"""
Priority below which suppression is recommended.

Targets with priority < SUPPRESSION_THRESHOLD may be suppressed to free
resources for higher-priority targets.
"""

COMPETITION_THRESHOLD: Final[float] = 0.6
"""
Priority above which competition becomes significant.

Multiple targets above this threshold compete for attention resources.
"""

PERSISTENCE_INCREASE_THRESHOLD: Final[float] = 0.75
"""
Persistence increase threshold.

When current focus exceeds this, maintenance is recommended over shift.
"""

SHIFT_ALLOWANCE_THRESHOLD: Final[float] = 0.2
"""
Allowance factor for attention shifts.

Determines how much priority change justifies a focus shift.
"""

# ============================================================================
# HISTORICAL BOUNDS
# ============================================================================

MAX_HISTORY_LENGTH: Final[int] = 100
"""Maximum number of history entries to retain."""

MAX_RECENT_WINDOW: Final[int] = 20
"""Size of recent window for rolling statistics."""

# ============================================================================
# CONFIGURATION VERSIONS
# ============================================================================

CONFIG_VERSION: Final[str] = "1.0.0"
"""Current configuration schema version."""