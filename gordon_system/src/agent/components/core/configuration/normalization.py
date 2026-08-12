# Configuration Normalization Module
# ===================================
"""
Configuration value normalization to canonical forms.

Provides:
- Path normalization (absolute paths, canonical form)
- Duration and size parsing
- Enum value normalization
- Case normalization
- Empty value handling

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    Tuple,
)
from enum import Enum
import os
import re
import time


# =============================================================================
# Normalization Results
# =============================================================================

@dataclass(frozen=True)
class NormalizationResult:
    """Result of normalizing a value."""
    original: Any
    normalized: Any
    path: str
    changes_made: bool = False
    warnings: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NormalizationReport:
    """
    Complete normalization report.
    
    Tracks all normalizations performed on a configuration.
    """
    normalized_values: Dict[str, NormalizationResult]
    total_changed: int
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    normalized_at: float = field(default_factory=time.monotonic)


# =============================================================================
# Path Normalizer
# =============================================================================

class PathNormalizer:
    """Normalizes file and directory paths."""
    
    def normalize(self, value: Any, path: str) -> NormalizationResult:
        """
        Normalize a path to its canonical form.
        
        Args:
            value: The path value (string or None)
            path: Field path for tracking
            
        Returns:
            NormalizationResult with normalized path
        """
        if not isinstance(value, str):
            return NormalizationResult(
                original=value,
                normalized=value,
                path=path,
                changes_made=False
            )
        
        if not value:
            return NormalizationResult(
                original=value,
                normalized=value,
                path=path,
                changes_made=False
            )
        
        # Normalize the path
        try:
            normalized = os.path.normpath(os.path.abspath(value))
            
            return NormalizationResult(
                original=value,
                normalized=normalized,
                path=path,
                changes_made=(value != normalized)
            )
        except Exception as e:
            return NormalizationResult(
                original=value,
                normalized=value,
                path=path,
                changes_made=False,
                warnings=(f"Path normalization failed: {e}",)
            )


# =============================================================================
# Duration Normalizer
# =============================================================================

class DurationNormalizer:
    """Normalizes duration values to seconds (float)."""
    
    # Pattern: number followed by unit
    _PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*(ms|s|m|h|d|w|y)$')
    _MULTIPLIERS = {
        'ms': 0.001,
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800,
        'y': 31536000,
    }
    
    def normalize(self, value: Any, path: str) -> NormalizationResult:
        """
        Normalize duration to seconds.
        
        Accepts numeric values (already in seconds) or string durations
        like '5s', '1m30s', '2h'.
        
        Args:
            value: Duration value (number or string)
            path: Field path for tracking
            
        Returns:
            NormalizationResult with duration in seconds
        """
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return NormalizationResult(
                original=value,
                normalized=float(value),
                path=path,
                changes_made=False  # Already numeric
            )
        
        if isinstance(value, str):
            match = self._PATTERN.match(value.strip().lower())
            if match:
                amount = float(match.group(1))
                unit = match.group(2)
                
                seconds = amount * self._MULTIPLIERS.get(unit, 1)
                
                return NormalizationResult(
                    original=value,
                    normalized=seconds,
                    path=path,
                    changes_made=True
                )
        
        # Return as-is if not recognized
        return NormalizationResult(
            original=value,
            normalized=value,
            path=path,
            changes_made=False,
            warnings=(f"Unknown duration format: {value!r}",)
        )


# =============================================================================
# Size Normalizer
# =============================================================================

class SizeNormalizer:
    """Normalizes size values to bytes (int)."""
    
    _PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*(b|kb|mb|gb|tb)$')
    _MULTIPLIERS = {
        'b': 1,
        'kb': 1024,
        'mb': 1024 ** 2,
        'gb': 1024 ** 3,
        'tb': 1024 ** 4,
    }
    
    def normalize(self, value: Any, path: str) -> NormalizationResult:
        """
        Normalize size to bytes.
        
        Accepts numeric values (already in bytes) or string sizes
        like '1GB', '512MB', '2KB'.
        
        Args:
            value: Size value (number or string)
            path: Field path for tracking
            
        Returns:
            NormalizationResult with size in bytes
        """
        if isinstance(value, int) and not isinstance(value, bool):
            return NormalizationResult(
                original=value,
                normalized=int(value),
                path=path,
                changes_made=False
            )
        
        if isinstance(value, str):
            match = self._PATTERN.match(value.strip().lower())
            if match:
                amount = float(match.group(1))
                unit = match.group(2)
                
                bytes_count = int(amount * self._MULTIPLIERS.get(unit, 1))
                
                return NormalizationResult(
                    original=value,
                    normalized=bytes_count,
                    path=path,
                    changes_made=True
                )
        
        # Return as-is if not recognized
        return NormalizationResult(
            original=value,
            normalized=value,
            path=path,
            changes_made=False,
            warnings=(f"Unknown size format: {value!r}",)
        )


# =============================================================================
# Enum Normalizer
# =============================================================================

class EnumNormalizer:
    """Normalizes enum values to canonical form."""
    
    def __init__(self, allowed_values: Tuple[str, ...]):
        """
        Initialize with allowed enum values.
        
        Args:
            allowed_values: Tuple of valid enum string values
        """
        self._allowed = {v.lower(): v for v in allowed_values}
    
    def normalize(self, value: Any, path: str) -> NormalizationResult:
        """
        Normalize an enum value to canonical form.
        
        Args:
            value: The enum value (string or already typed)
            path: Field path for tracking
            
        Returns:
            NormalizationResult with normalized enum
        """
        if isinstance(value, str):
            lower = value.lower()
            
            if lower in self._allowed:
                canonical = self._allowed[lower]
                
                return NormalizationResult(
                    original=value,
                    normalized=canonical,
                    path=path,
                    changes_made=(value != canonical)
                )
        
        # Return as-is
        return NormalizationResult(
            original=value,
            normalized=value,
            path=path,
            changes_made=False
        )


# =============================================================================
# Case Normalizer
# =============================================================================

class CaseNormalizer:
    """Normalizes string case."""
    
    class Mode(Enum):
        LOWER = "lower"
        UPPER = "upper"
        CAMEL_TO_SNAKE = "camel_to_snake"
        SNAKE_TO_CAMEL = "snake_to_camel"
    
    def __init__(self, mode: str = "lower"):
        self._mode = CaseNormalizer.Mode(mode)
    
    def normalize(self, value: Any, path: str) -> NormalizationResult:
        """
        Normalize string case.
        
        Args:
            value: The string value
            path: Field path for tracking
            
        Returns:
            NormalizationResult with normalized string
        """
        if not isinstance(value, str):
            return NormalizationResult(
                original=value,
                normalized=value,
                path=path,
                changes_made=False
            )
        
        if self._mode == CaseNormalizer.Mode.LOWER:
            normalized = value.lower()
        
        elif self._mode == CaseNormalizer.Mode.UPPER:
            normalized = value.upper()
        
        else:
            normalized = value
        
        return NormalizationResult(
            original=value,
            normalized=normalized,
            path=path,
            changes_made=(value != normalized)
        )


# =============================================================================
# Empty Value Handler
# =============================================================================

class EmptyValueHandler:
    """Normalizes empty/None values to configured defaults."""
    
    def __init__(self, default_value: Any = None):
        """
        Initialize with default value.
        
        Args:
            default_value: Default value for empty slots
        """
        self._default = default_value
    
    def normalize(self, value: Any, path: str) -> NormalizationResult:
        """
        Normalize empty/None values to default.
        
        Args:
            value: The value to check
            path: Field path for tracking
            
        Returns:
            NormalizationResult with normalized value
        """
        is_empty = value is None or (isinstance(value, str) and not value.strip())
        
        if is_empty:
            return NormalizationResult(
                original=value,
                normalized=self._default,
                path=path,
                changes_made=True,
                warnings=("Empty value replaced with default",)
            )
        
        return NormalizationResult(
            original=value,
            normalized=value,
            path=path,
            changes_made=False
        )


# =============================================================================
# Full Normalizer Pipeline
# =============================================================================

@dataclass(frozen=True)
class NormalizationRule:
    """A normalization rule for a specific field."""
    path: str  # Field path (dot-notation)
    normalizers: Tuple[Any, ...]  # List of normalizer instances


class ConfigurationNormalizer:
    """
    Complete configuration normalization pipeline.
    
    Runs all normalizers on configuration values and produces
    canonical forms suitable for validation and application.
    """
    
    def __init__(
        self,
        rules: Optional[Tuple[NormalizationRule, ...]] = None
    ):
        """
        Initialize with normalization rules.
        
        Args:
            rules: Tuple of NormalizationRule instances
        """
        self._rules = rules or ()
    
    def normalize(
        self,
        data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], NormalizationReport]:
        """
        Normalize all values in configuration data.
        
        Args:
            data: Raw configuration data
            
        Returns:
            Tuple of (normalized_data, normalization_report)
        """
        normalized = dict(data)
        results = {}
        
        for rule in self._rules:
            if rule.path not in normalized:
                continue
            
            value = normalized[rule.path]
            
            # Apply each normalizer in order
            current_value = value
            warnings = []
            
            for normalizer in rule.normalizers:
                result = normalizer.normalize(current_value, rule.path)
                
                if result.changes_made:
                    current_value = result.normalized
                
                warnings.extend(result.warnings)
            
            results[rule.path] = NormalizationResult(
                original=value,
                normalized=current_value,
                path=rule.path,
                changes_made=(value != current_value),
                warnings=tuple(warnings)
            )
        
        # Apply changes to data
        for path, result in results.items():
            if result.changes_made:
                self._set_nested_value(normalized, path, result.normalized)
        
        total_changed = sum(1 for r in results.values() if r.changes_made)
        
        report = NormalizationReport(
            normalized_values=results,
            total_changed=total_changed,
            warnings=tuple(w for r in results.values() for w in r.warnings),
            normalized_at=time.monotonic()
        )
        
        return normalized, report
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested value using dot-notation path."""
        keys = path.split('.')
        
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        
        data[keys[-1]] = value


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Results
    "NormalizationResult",
    "NormalizationReport",
    
    # Normalizers
    "PathNormalizer",
    "DurationNormalizer",
    "SizeNormalizer",
    "EnumNormalizer",
    "CaseNormalizer",
    "EmptyValueHandler",
    
    # Pipeline
    "NormalizationRule",
    "ConfigurationNormalizer",
]