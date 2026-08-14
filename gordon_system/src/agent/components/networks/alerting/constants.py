# Alerting Network Constants
# ============================

"""
Immutable constants for the AlertingNetwork.

All constants are bounded and validated. They define:
    - Default configuration values
    - Threshold boundaries
    - State transition rules
    - Feature normalization ranges
"""

from __future__ import annotations


# =============================================================================
# Range Constants (Normalization Bounds)
# =============================================================================

MIN_INTENSITY: float = 0.0
MAX_INTENSITY: float = 1.0

MIN_CONFIDENCE: float = 0.0
MAX_CONFIDENCE: float = 1.0

MIN_DEMAND_SCORE: float = 0.0
MAX_DEMAND_SCORE: float = 1.0


# =============================================================================
# Threshold Constants (Classification Boundaries)
# =============================================================================

NEGLIGIBLE_MAX: float = 0.1       # Below this is NEGLIGIBLE
LOW_MAX: float = 0.3              # Below this is LOW (after negligible)
MODERATE_MAX: float = 0.5         # Below this is MODERATE (after low)
HIGH_MAX: float = 0.8             # Below this is HIGH (after moderate)
CRITICAL_MIN: float = 0.8         # At or above this is CRITICAL


# =============================================================================
# State Transition Constants
# =============================================================================

DEFAULT_HABITUATION_COEFFICIENT: float = 1.0      # Start with no attenuation
MAX_HABITUATION_COEFFICIENT: float = 1.0          # Maximum possible (no suppression)
MIN_HABITUATION_COEFFICIENT: float = 0.2          # Minimum (full habituation)

DEFAULT_REFRACTORY_WINDOW_SECONDS: float = 2.0    # Refractory period duration
REFRACTORY_ATTENUATION_FACTOR: float = 0.5        # How much signals are suppressed


# =============================================================================
# Temporal Constants
# =============================================================================

DEFAULT_BASELINE_WINDOW_SIZE: int = 10            # Window for baseline computation
MIN_SIGNALS_FOR_STATISTICS: int = 2               # Minimum signals needed for stats

DEFAULT_RECOVERY_TIME_SECONDS: float = 60.0       # Time for habituation recovery


# =============================================================================
# Feature Bounds (Each feature's valid range)
# =============================================================================

FEATURE_MIN: float = 0.0
FEATURE_MAX: float = 1.0


# =============================================================================
# Confidence Thresholds
# =============================================================================

LOW_CONFIDENCE_THRESHOLD: float = 0.5       # Below this is "low" confidence
HIGH_CONFIDENCE_THRESHOLD: float = 0.8      # Above this is "high" confidence


# =============================================================================
# Signal Classification Constants
# =============================================================================

MINIMUM_DETECTION_THRESHOLD: float = 0.1    # Minimum signal to be considered valid
SIGNAL_STRENGTH_NORMALIZATION_FACTOR: float = 10.0  # Scaling factor for normalization


# =============================================================================
# Diagnostic Counters
# =============================================================================

DEFAULT_DIAGNOSTIC_COUNTER_MAX: int = 1_000_000  # Max before overflow concern


# =============================================================================
# Time-based Constants
# =============================================================================

MILLISECONDS_PER_SECOND: float = 1000.0
MICROSECONDS_PER_SECOND: float = 1_000_000.0