# Focusing Network Configuration Contracts
# ========================================

"""
Configuration contracts for the FocusingNetwork Phase 4.2.8.

These define stable interfaces for configuration without exposing implementation
details. The FocusingNetwork reads from these contracts but never owns or modifies
configuration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
from datetime import datetime


# =============================================================================
# CONFIGURATION VIEW - Immutable configuration snapshot
# =============================================================================

@dataclass(frozen=True)
class ConfigurationView:
    """
    Immutable snapshot of configuration at a point in time.
    
    Contains all configuration values without exposing how they're loaded or
    managed. Only the final configuration state, not the loading process.
    
    PROPERTIES:
        • Immutable once created
        • Versioned for compatibility tracking
        • Complete snapshot at creation time
    """
    
    # Configuration identity
    view_id: str = field(default_factory=lambda: f"config_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this configuration view."""
    
    # Priority thresholds
    suppression_threshold: float = 0.3
    """Priority below which suppression is recommended."""
    
    competition_threshold: float = 0.6
    """Priority above which competition becomes significant."""
    
    priority_boost_threshold: float = 0.5
    """Above this, current focus receives boost in next assessment."""
    
    # Persistence configuration
    default_decay_rate: float = 0.95
    """Focus decay rate per cycle when not maintained."""
    
    persistence_threshold: float = 0.7
    """Above this, focus is considered 'maintained'."""
    
    persistence_increase_threshold: float = 0.75
    """When current exceeds this, maintenance is recommended."""
    
    # Precision configuration
    default_precision: float = 0.5
    """Default precision when not otherwise specified."""
    
    min_precision: float = 0.1
    """Minimum allowed precision (broadest focus)."""
    
    max_precision: float = 0.95
    """Maximum allowed precision (sharpest focus)."""
    
    # Budget and allocation
    default_budget_allocation: float = 1.0
    """Default resource budget multiplier."""
    
    min_resource_allocation: float = 0.1
    """Minimum resources to allocate to any active target."""
    
    max_active_targets: int = 3
    """Maximum concurrent focus targets."""
    
    # Historical bounds
    max_history_length: int = 100
    """Maximum history entries to retain."""
    
    recent_window_size: int = 20
    """Window size for rolling statistics."""
    
    # Bias configuration weights (must sum to approximately 1.0)
    goal_weight: float = 0.4
    """Weight for goal-based relevance."""
    
    task_weight: float = 0.3
    """Weight for task-based relevance."""
    
    memory_weight: float = 0.2
    """Weight for memory-based relevance."""
    
    temporal_weight: float = 0.1
    """Weight for temporal/anticipation relevance."""
    
    def is_valid(self) -> bool:
        """
        Check if configuration values are within valid ranges.
        
        Returns:
            True if all values are valid, False otherwise
        """
        # Thresholds must be in [0.0, 1.0]
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
        
        # Decay rate must be in [0.0, 1.0]
        if not (0.0 <= self.default_decay_rate <= 1.0):
            return False
        
        # Max targets must be positive
        if self.max_active_targets <= 0:
            return False
        
        # Window size must be positive
        if self.recent_window_size <= 0:
            return False
        
        # Precision bounds must be valid
        if not (self.min_precision <= self.default_precision <= self.max_precision):
            return False
        
        # Weights should sum to approximately 1.0
        weight_sum = (
            self.goal_weight + self.task_weight +
            self.memory_weight + self.temporal_weight
        )
        if abs(weight_sum - 1.0) > 0.01:
            return False
        
        return True


# =============================================================================
# CONFIGURATION SNAPSHOT - Point-in-time configuration capture
# =============================================================================

@dataclass(frozen=True)
class ConfigurationSnapshot:
    """
    Immutable snapshot of configuration at a specific point in time.
    
    Used for replay, diagnostics, and historical analysis. Contains the complete
    configuration state at creation time.
    
    PROPERTIES:
        • Immutable once created
        • Captures complete configuration state
        • Timestamped for historical tracking
    """
    
    # Snapshot identity
    snapshot_id: str = field(default_factory=lambda: f"config_snap_{id(datetime.utcnow()):x}")
    """Unique identifier for this snapshot."""
    
    # Configuration at time of snapshot
    config: ConfigurationView = field(default_factory=ConfigurationView)
    """Configuration view at snapshot time."""
    
    # Timestamp information
    captured_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When the snapshot was taken."""
    
    revision: int = 1
    """Snapshot revision number."""
    
    # Source information (for diagnostics)
    source_system: str = "unknown"
    """System that created this snapshot."""
    
    @classmethod
    def capture(cls, config: Optional[ConfigurationView] = None) -> "ConfigurationSnapshot":
        """
        Capture current configuration as a snapshot.
        
        Args:
            config: Configuration to snapshot. Uses default if None.
            
        Returns:
            New ConfigurationSnapshot with the given or default configuration
        """
        return cls(config=config or ConfigurationView())
    
    def get_threshold(self, threshold_name: str) -> Optional[float]:
        """
        Get a specific threshold value from the configuration.
        
        Args:
            threshold_name: Name of the threshold (e.g., 'suppression', 'competition')
            
        Returns:
            Threshold value or None if not found
        """
        threshold_map = {
            "suppression": self.config.suppression_threshold,
            "competition": self.config.competition_threshold,
            "priority_boost": self.config.priority_boost_threshold,
            "persistence": self.config.persistence_threshold,
            "persistence_increase": self.config.persistence_increase_threshold,
            "min_precision": self.config.min_precision,
            "max_precision": self.config.max_precision,
        }
        return threshold_map.get(threshold_name)


# =============================================================================
# CONFIGURATION VALIDATOR - Defines validation rules without implementation
# =============================================================================

@dataclass(frozen=True)
class ConfigurationValidator:
    """
    Defines validation expectations for configuration.
    
    Specifies what makes a valid configuration but doesn't implement the
    validation logic. The FocusingNetwork uses these rules but doesn't define them.
    
    PROPERTIES:
        • Rules are defined, not implemented here
        • Versioned for compatibility tracking
        • External implementation responsibility
    """
    
    # Validator identity
    validator_id: str = field(default_factory=lambda: f"config_validator_{id(datetime.utcnow()):x}")
    """Unique identifier for this validator."""
    
    # Validation rules (descriptive, not implementational)
    required_fields: Tuple[str, ...] = (
        "suppression_threshold",
        "competition_threshold",
        "max_active_targets",
        "default_precision",
    )
    """Required configuration fields."""
    
    range_rules: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Rules defining value ranges."""
    
    constraint_rules: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Rules defining cross-field constraints."""
    
    def __post_init__(self):
        # Initialize default range rules if empty
        if not self.range_rules:
            object.__setattr__(
                self,
                "range_rules",
                (
                    {"field": "suppression_threshold", "min": 0.0, "max": 1.0},
                    {"field": "competition_threshold", "min": 0.0, "max": 1.0},
                    {"field": "priority_boost_threshold", "min": 0.0, "max": 1.0},
                )
            )


# =============================================================================
# CONFIGURATION VERSION - Version information for configuration
# =============================================================================

@dataclass(frozen=True)
class ConfigurationVersion:
    """
    Version information for configuration compatibility.
    
    Contains version metadata that external systems can use to ensure
    configuration compatibility.
    
    PROPERTIES:
        • Immutable once created
        • Compatibility policy defined
        • Deprecation tracking
    """
    
    # Version identity
    version_id: str = field(default_factory=lambda: f"config_version_{id(datetime.utcnow()):x}")
    """Unique identifier for this version."""
    
    # Semantic versioning
    semantic_version: str = "1.0.0"
    """Semantic version string (MAJOR.MINOR.PATCH)."""
    
    compatibility_policy: str = "backward"
    """Compatibility policy: 'strict', 'backward', 'forward', or 'full'."""
    
    deprecation_policy: str = "three_releases"
    """Deprecation policy description."""
    
    extension_strategy: str = "additive_only"
    """Extension strategy: how new features are added."""
    
    # Version history
    created_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When this version was created."""
    
    valid_until_utc: Optional[datetime] = None
    """When this version becomes deprecated (if known)."""
    
    @property
    def is_deprecated(self) -> bool:
        """Check if this version is deprecated based on deprecation policy."""
        if self.deprecation_policy == "three_releases":
            # Version is not deprecated in three_releases policy until 3 releases later
            return False
        return False
    
    @property
    def supports_forward_compatibility(self) -> bool:
        """Check if this version supports forward compatibility."""
        return self.compatibility_policy in ("forward", "full")
    
    @property
    def supports_backward_compatibility(self) -> bool:
        """Check if this version supports backward compatibility."""
        return self.compatibility_policy in ("backward", "full")


# =============================================================================
# FOCUS CONFIGURATION PROVIDER - Protocol for external configuration sources
# =============================================================================

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FocusConfigurationProvider(Protocol):
    """
    Protocol for providing configuration to the FocusingNetwork.
    
    Allows external systems to supply configuration without coupling to
    the FocusingNetwork implementation. Configuration is read-only once loaded.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new config sections via nested objects)
    
    OWNERSHIP:
        - Configuration is owned by the Provider system
        - Network only reads configuration
        - No runtime modification capability
    
    USE BY:
        - FocusingNetwork reads thresholds during assessment
        - Configuration affects classification, feature weights,
          state bounds, and limits
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def get_configuration_view(self) -> ConfigurationView:
        """
        Get current configuration as an immutable view.
        
        Returns:
            ConfigurationView with all configuration values
        """
        ...
    
    @abstractmethod
    def get_threshold(self, threshold_name: str) -> Optional[float]:
        """
        Get a specific threshold value.
        
        Args:
            threshold_name: Name of the threshold (e.g., 'suppression', 'competition')
            
        Returns:
            Threshold value or None if not found
        """
        ...
    
    @abstractmethod
    def get_max_targets(self) -> int:
        """Get maximum number of active focus targets."""
        ...
    
    @abstractmethod
    def is_config_valid(self) -> bool:
        """Check if current configuration is valid."""
        ...
    
    @abstractmethod
    def get_version(self) -> ConfigurationVersion:
        """Get version information for this configuration."""
        ...


__all__ = [
    # Configuration view (immutable snapshot)
    "ConfigurationView",
    # Configuration snapshot (point-in-time capture)
    "ConfigurationSnapshot",
    # Validation rules (not implementation)
    "ConfigurationValidator",
    # Versioning information
    "ConfigurationVersion",
    # External provider interface
    "FocusConfigurationProvider",
]