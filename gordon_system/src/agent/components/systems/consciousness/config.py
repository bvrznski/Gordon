# Gordon Phase 5.7.1-I: Consciousness Configuration
# ===============================================================================

"""
Configuration for the Consciousness capability.

This module defines validated configuration types that ensure:
    - Immutable configuration after creation
    - Validated constraints on all parameters
    - Deterministic behavior from configuration values
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Optional
import re


@dataclass(frozen=True)
class ConsciousnessConfiguration:
    """
    Immutable validated configuration for the Consciousness capability.
    
    Configuration properties:
        - Immutable: Once created, never modified
        - Validated: All values pass validation checks
        - Complete: All required parameters must be specified
    
    The configuration is set once at initialization and cannot be changed
    during runtime. This ensures deterministic behavior and prevents
    configuration drift during operation.
    """
    
    # Source limits
    maximum_sources: int = 100
    """Maximum number of registered sources."""
    
    maximum_pending_contributions: int = 1000
    """Maximum pending contributions before backpressure."""
    
    # Extension limits
    maximum_extensions: int = 25
    """Maximum number of registered extensions."""
    
    maximum_transition_history: int = 100
    """Maximum transition records retained."""
    
    # Timing constraints
    maximum_snapshot_age_seconds: float = 60.0
    """Maximum age of current snapshot before considered stale."""
    
    transition_timeout_seconds: float = 30.0
    """Timeout for transition operations."""
    
    source_timeout_seconds: float = 5.0
    """Timeout for source registration."""
    
    extension_timeout_seconds: float = 10.0
    """Timeout for extension registration."""
    
    query_timeout_seconds: float = 5.0
    """Timeout for query operations."""
    
    # Extension requirements
    required_extensions: Tuple[str, ...] = field(default_factory=tuple)
    """Extensions that must be ready before capability is considered healthy."""
    
    optional_extensions: Tuple[str, ...] = field(default_factory=tuple)
    """Extensions that may be unavailable without degrading health."""
    
    # Operational modes
    allow_degraded_start: bool = False
    """Whether to start in degraded mode if requirements are unmet."""
    
    diagnostic_detail_level: str = "standard"
    """Detail level for diagnostics (minimal, standard, verbose)."""
    
    privacy_mode: str = "conservative"
    """Privacy enforcement mode (permissive, conservative, strict)."""
    
    trust_policy_reference: Optional[str] = None
    """Reference to external trust policy configuration."""
    
    def __post_init__(self):
        """Validate configuration values after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate all configuration values."""
        # Validate numeric constraints
        if self.maximum_sources < 1 or self.maximum_sources > 1000:
            raise ValueError("maximum_sources must be between 1 and 1000")
        
        if self.maximum_extensions < 1 or self.maximum_extensions > 50:
            raise ValueError("maximum_extensions must be between 1 and 50")
        
        if self.maximum_pending_contributions < 1 or self.maximum_pending_contributions > 10000:
            raise ValueError("maximum_pending_contributions must be between 1 and 10000")
        
        if self.maximum_transition_history < 1 or self.maximum_transition_history > 500:
            raise ValueError("maximum_transition_history must be between 1 and 500")
        
        # Validate timing constraints
        if self.maximum_snapshot_age_seconds < 1.0 or self.maximum_snapshot_age_seconds > 3600.0:
            raise ValueError("maximum_snapshot_age_seconds must be between 1 and 3600")
        
        if self.transition_timeout_seconds < 1.0 or self.transition_timeout_seconds > 120.0:
            raise ValueError("transition_timeout_seconds must be between 1 and 120")
        
        if self.source_timeout_seconds < 0.1 or self.source_timeout_seconds > 30.0:
            raise ValueError("source_timeout_seconds must be between 0.1 and 30")
        
        if self.extension_timeout_seconds < 0.5 or self.extension_timeout_seconds > 60.0:
            raise ValueError("extension_timeout_seconds must be between 0.5 and 60")
        
        if self.query_timeout_seconds < 0.1 or self.query_timeout_seconds > 30.0:
            raise ValueError("query_timeout_seconds must be between 0.1 and 30")
        
        # Validate mode values
        valid_diagnostic_levels = ("minimal", "standard", "verbose")
        if self.diagnostic_detail_level not in valid_diagnostic_levels:
            raise ValueError(
                f"diagnostic_detail_level must be one of {valid_diagnostic_levels}"
            )
        
        valid_privacy_modes = ("permissive", "conservative", "strict")
        if self.privacy_mode not in valid_privacy_modes:
            raise ValueError(f"privacy_mode must be one of {valid_privacy_modes}")
    
    @classmethod
    def default(cls) -> "ConsciousnessConfiguration":
        """Return the default configuration."""
        return cls()
    
    @classmethod
    def minimal(cls) -> "ConsciousnessConfiguration":
        """Return a minimal configuration for testing."""
        return cls(
            maximum_sources=10,
            maximum_extensions=5,
            maximum_pending_contributions=100,
            maximum_transition_history=10,
        )
    
    @classmethod
    def strict(cls) -> "ConsciousnessConfiguration":
        """Return a strict configuration with conservative limits."""
        return cls(
            maximum_sources=20,
            maximum_extensions=5,
            maximum_pending_contributions=100,
            maximum_transition_history=25,
            allow_degraded_start=False,
            diagnostic_detail_level="verbose",
            privacy_mode="strict",
        )
    
    def with_source_limit(self, limit: int) -> "ConsciousnessConfiguration":
        """Return a copy with updated source limit."""
        return dataclass_replace(self, maximum_sources=limit)
    
    def with_extension_limit(self, limit: int) -> "ConsciousnessConfiguration":
        """Return a copy with updated extension limit."""
        return dataclass_replace(self, maximum_extensions=limit)


# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_configuration(config_dict: dict) -> tuple[bool, list[str]]:
    """
    Validate a configuration dictionary.
    
    Args:
        config_dict: Dictionary containing configuration values
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    required_fields = [
        "maximum_sources",
        "maximum_extensions",
        "transition_timeout_seconds",
    ]
    
    for field in required_fields:
        if field not in config_dict:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Validate numeric ranges
    try:
        sources = config_dict.get("maximum_sources", 0)
        extensions = config_dict.get("maximum_extensions", 0)
        
        if not isinstance(sources, int) or sources < 1 or sources > 1000:
            errors.append("maximum_sources must be an integer between 1 and 1000")
        
        if not isinstance(extensions, int) or extensions < 1 or extensions > 50:
            errors.append("maximum_extensions must be an integer between 1 and 50")
            
    except Exception as e:
        errors.append(f"Error validating numeric fields: {str(e)}")
    
    return len(errors) == 0, errors


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "ConsciousnessConfiguration",
    "validate_configuration",
)