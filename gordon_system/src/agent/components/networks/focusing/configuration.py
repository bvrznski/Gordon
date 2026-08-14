# Focusing Network Configuration
# ===============================

"""
Immutable configuration for the FocusingNetwork.

The configuration defines:
    - Default thresholds and bounds
    - Behavioral policies
    - Algorithm parameters
    - Resource constraints

All configuration is immutable. Changes require creating a new config instance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class FocusingNetworkConfig:
    """
    Immutable configuration for the FocusingNetwork.

    This configuration defines all behavioral parameters for the network.
    Once instantiated, it cannot be modified - new configuration requires
    creating a new instance.

    All thresholds are clamped to [0.0, 1.0] and must be valid probabilities.
    """

    # Priority computation thresholds
    suppression_threshold: float = field(default=0.3)
    """Priority below which suppression is recommended."""

    competition_threshold: float = field(default=0.6)
    """Priority above which competition becomes significant."""

    priority_boost_threshold: float = field(default=0.5)
    """Above this, current focus receives boost in next assessment."""

    # Persistence configuration
    default_decay_rate: float = field(default=0.95)
    """Focus decay rate per cycle when not maintained."""

    persistence_threshold: float = field(default=0.7)
    """Above this, focus is considered 'maintained'."""

    persistence_increase_threshold: float = field(default=0.75)
    """When current exceeds this, maintenance is recommended."""

    # Precision configuration
    default_precision: float = field(default=0.5)
    """Default precision when not otherwise specified."""

    min_precision: float = field(default=0.1)
    """Minimum allowed precision (broadest focus)."""

    max_precision: float = field(default=0.95)
    """Maximum allowed precision (sharpest focus)."""

    # Budget and allocation
    default_budget_allocation: float = field(default=1.0)
    """Default resource budget multiplier."""

    min_resource_allocation: float = field(default=0.05)
    """Minimum resources to allocate to any active target."""

    max_active_targets: int = field(default=3)
    """Maximum concurrent focus targets."""

    # Historical bounds
    max_history_length: int = field(default=100)
    """Maximum history entries to retain."""

    recent_window_size: int = field(default=20)
    """Window size for rolling statistics."""

    # Bias configuration
    goal_weight: float = field(default=0.4)
    """Weight for goal-based relevance."""

    task_weight: float = field(default=0.3)
    """Weight for task-based relevance."""

    memory_weight: float = field(default=0.2)
    """Weight for memory-based relevance."""

    temporal_weight: float = field(default=0.1)
    """Weight for temporal/anticipation relevance."""

    @classmethod
    def default(cls) -> "FocusingNetworkConfig":
        """
        Return the default configuration.

        This is the canonical starting point for most use cases.
        For specialized configurations, create a new instance with desired values.
        """
        return cls()

    @property
    def is_valid(self) -> bool:
        """
        Validate that all configuration values are within acceptable ranges.
        """
        thresholds = [
            self.suppression_threshold,
            self.competition_threshold,
            self.priority_boost_threshold,
            self.persistence_threshold,
            self.persistence_increase_threshold,
            self.min_precision,
            self.max_precision,
            self.default_budget_allocation,
            self.min_resource_allocation,
        ]

        if not all(0.0 <= t <= 1.0 for t in thresholds):
            return False

        if self.default_decay_rate < 0.0 or self.default_decay_rate > 1.0:
            return False

        if self.max_active_targets <= 0:
            return False

        if self.recent_window_size <= 0:
            return False

        if not (self.min_precision <= self.default_precision <= self.max_precision):
            return False

        # Weights must sum to approximately 1.0
        weight_sum = (
            self.goal_weight + self.task_weight +
            self.memory_weight + self.temporal_weight
        )
        if abs(weight_sum - 1.0) > 0.01:
            return False

        return True

    def clamp_priority(self, value: float) -> float:
        """Clamp a priority score to valid range [0.0, 1.0]."""
        return max(0.0, min(1.0, value))

    def clamp_precision(self, value: float) -> float:
        """Clamp a precision score to valid range [min, max]."""
        return max(self.min_precision, min(self.max_precision, value))


def validate_config(config: FocusingNetworkConfig) -> Tuple[bool, str]:
    """
    Validate configuration and return (is_valid, error_message).

    Returns:
        Tuple of (True, "") if config is valid
        Tuple of (False, "error message") if validation fails
    """
    if not isinstance(config, FocusingNetworkConfig):
        return False, "Configuration must be a FocusingNetworkConfig instance"

    if not config.is_valid:
        return False, "Configuration has invalid threshold values"

    return True, ""