# Core Configuration Infrastructure
# ==================================

"""
Core runtime configuration management.

Provides validated, immutable configuration objects with source tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TypeVar, Generic, List, Tuple
from enum import Enum


T = TypeVar("T")


@dataclass(frozen=True)
class ConfigSource:
    """Represents a single configuration source."""
    
    name: str  # e.g., "env", "file", "default"
    data: Dict[str, Any]
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get value for key from this source."""
        return self.data.get(key, default)
    
    def contains(self, key: str) -> bool:
        """Check if key exists in this source."""
        return key in self.data


@dataclass(frozen=True)
class ConfigValidationError:
    """A configuration validation error."""
    
    key: str
    message: str
    value: Any = None
    severity: str = "error"  # "error" or "warning"
    
    def is_error(self) -> bool:
        return self.severity == "error"


@dataclass(frozen=True)
class Configuration:
    """
    Immutable configuration with source tracking.
    
    Supports multiple sources with deterministic precedence:
    default < file < env
    """
    
    _sources: Tuple[ConfigSource, ...] = field(default_factory=tuple)
    _resolved: Dict[str, Any] = field(default_factory=dict)
    _errors: List[ConfigValidationError] = field(default_factory=list)
    
    @classmethod
    def create(cls, *sources: ConfigSource) -> "Configuration":
        """Create a configuration from sources in precedence order."""
        resolved: Dict[str, Any] = {}
        
        # Merge sources (later sources override earlier ones)
        for source in reversed(sources):
            for key, value in source.data.items():
                if not isinstance(key, str):
                    raise ValueError(f"Configuration keys must be strings, got {type(key)}")
                resolved[key] = value
        
        return cls(_sources=sources, _resolved=resolved)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Configuration":
        """Create a configuration from a single dict (treated as default source)."""
        source = ConfigSource(name="default", data=dict(data))
        return cls.create(source)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation: "a.b.c")
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        # Support dot notation for nested access
        keys = key.split(".")
        value = self._resolved
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a string configuration value."""
        value = self.get(key, default)
        if value is not None and not isinstance(value, str):
            raise TypeError(f"Expected string for {key}, got {type(value)}")
        return value
    
    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """Get an integer configuration value."""
        value = self.get(key, default)
        if value is not None and not isinstance(value, int):
            raise TypeError(f"Expected int for {key}, got {type(value)}")
        return value
    
    def get_float(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """Get a float configuration value."""
        value = self.get(key, default)
        if value is not None and not isinstance(value, (int, float)):
            raise TypeError(f"Expected float for {key}, got {type(value)}")
        return value
    
    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """Get a boolean configuration value."""
        value = self.get(key, default)
        if value is not None and not isinstance(value, bool):
            raise TypeError(f"Expected bool for {key}, got {type(value)}")
        return value
    
    def get_dict(self, key: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Get a dictionary configuration value."""
        value = self.get(key, default)
        if value is not None and not isinstance(value, dict):
            raise TypeError(f"Expected dict for {key}, got {type(value)}")
        return value
    
    def has_key(self, key: str) -> bool:
        """Check if a key exists in the configuration."""
        try:
            self.get(key)
            return True
        except (KeyError, TypeError):
            return False
    
    @property
    def sources(self) -> Tuple[ConfigSource, ...]:
        """Return all configuration sources in precedence order."""
        return self._sources
    
    @property
    def keys(self) -> List[str]:
        """Return all top-level configuration keys."""
        return list(self._resolved.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary."""
        return dict(self._resolved)
    
    def validate(self, required: List[str], types: Optional[Dict[str, type]] = None) -> List[ConfigValidationError]:
        """
        Validate the configuration.
        
        Args:
            required: List of required keys
            types: Optional mapping of key to expected type
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors: List[ConfigValidationError] = []
        
        # Check required keys
        for key in required:
            if not self.has_key(key):
                errors.append(ConfigValidationError(
                    key=key,
                    message=f"Required configuration key missing",
                    severity="error"
                ))
        
        # Check types
        if types:
            for key, expected_type in types.items():
                if self.has_key(key):
                    value = self._resolved.get(key)
                    if value is not None and not isinstance(value, expected_type):
                        errors.append(ConfigValidationError(
                            key=key,
                            message=f"Expected {expected_type.__name__}, got {type(value).__name__}",
                            value=value,
                            severity="error"
                        ))
        
        return errors
    
    def without_secrets(self) -> "Configuration":
        """Return a copy of configuration with common secret keys filtered."""
        secret_patterns = ["password", "secret", "token", "key", "credential"]
        filtered_data = {}
        
        for key, value in self._resolved.items():
            if any(pattern in key.lower() for pattern in secret_patterns):
                filtered_data[key] = "***FILTERED***"
            else:
                filtered_data[key] = value
        
        return Configuration(
            _sources=self._sources,
            _resolved=filtered_data,
            _errors=self._errors
        )


__all__ = [
    "ConfigSource",
    "ConfigValidationError",
    "Configuration",
]
