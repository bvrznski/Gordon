# Configuration Parser Module
# ===========================
"""
Configuration value parsing and type conversion.

Provides:
- Typed parsing from source representations
- Strict validation of parsed values
- Source location tracking in errors

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    Tuple,
)
import re
import time


# =============================================================================
# Parsing Errors
# =============================================================================

@dataclass(frozen=True)
class ParseError:
    """A configuration parsing error."""
    path: str  # Field path (dot-notation)
    value: Any
    expected_type: type
    message: str
    source_id: Optional[str] = None
    parsed_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class ParseResult:
    """Result of parsing a configuration value."""
    success: bool
    value: Any = None
    errors: Tuple[ParseError, ...] = field(default_factory=tuple)
    raw_value: Optional[Any] = None


# =============================================================================
# Parsed Value
# =============================================================================

@dataclass(frozen=True)
class ParsedValue:
    """
    A parsed configuration value.
    
    Contains both the original raw value and the parsed typed value.
    """
    raw: Any  # Raw source value (string from env, etc.)
    parsed: Any  # Parsed value with correct type
    path: str  # Field path


# =============================================================================
# Type Parsers
# =============================================================================

class BooleanParser:
    """Strict boolean parser."""
    
    TRUE_VALUES = frozenset({'true', 'yes', 'on', '1'})
    FALSE_VALUES = frozenset({'false', 'no', 'off', '0'})
    
    @classmethod
    def parse(cls, value: Any) -> ParseResult:
        """
        Parse a boolean value.
        
        Accepts: true/yes/on/1 for True, false/no/off/0 for False
        
        Args:
            value: Raw value to parse (string or already typed)
            
        Returns:
            ParseResult with success flag and parsed value
        """
        if isinstance(value, bool):
            return ParseResult(success=True, value=value)
        
        if isinstance(value, str):
            lower = value.lower().strip()
            if lower in cls.TRUE_VALUES:
                return ParseResult(success=True, value=True)
            if lower in cls.FALSE_VALUES:
                return ParseResult(success=True, value=False)
        
        return ParseResult(
            success=False,
            errors=(ParseError(
                path="",
                value=value,
                expected_type=bool,
                message=f"Cannot parse {value!r} as boolean"
            ),)
        )


class IntegerParser:
    """Strict integer parser."""
    
    @classmethod
    def parse(cls, value: Any) -> ParseResult:
        """
        Parse an integer value.
        
        Args:
            value: Raw value to parse (string or number)
            
        Returns:
            ParseResult with success flag and parsed value
        """
        if isinstance(value, int) and not isinstance(value, bool):
            return ParseResult(success=True, value=value)
        
        if isinstance(value, str):
            try:
                # Only accept pure integer strings, no floats
                stripped = value.strip()
                if '.' in stripped or 'e' in stripped.lower():
                    raise ValueError("Not an integer")
                return ParseResult(success=True, value=int(stripped))
            except (ValueError, OverflowError) as e:
                return ParseResult(
                    success=False,
                    errors=(ParseError(
                        path="",
                        value=value,
                        expected_type=int,
                        message=str(e)
                    ),)
                )
        
        if isinstance(value, float):
            if value.is_integer():
                return ParseResult(success=True, value=int(value))
        
        return ParseResult(
            success=False,
            errors=(ParseError(
                path="",
                value=value,
                expected_type=int,
                message=f"Cannot parse {value!r} as integer"
            ),)
        )


class FloatParser:
    """Strict float parser."""
    
    @classmethod
    def parse(cls, value: Any) -> ParseResult:
        """
        Parse a float value.
        
        Args:
            value: Raw value to parse (string or number)
            
        Returns:
            ParseResult with success flag and parsed value
        """
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return ParseResult(success=True, value=float(value))
        
        if isinstance(value, str):
            try:
                return ParseResult(success=True, value=float(value.strip()))
            except (ValueError, OverflowError) as e:
                return ParseResult(
                    success=False,
                    errors=(ParseError(
                        path="",
                        value=value,
                        expected_type=float,
                        message=str(e)
                    ),)
                )
        
        return ParseResult(
            success=False,
            errors=(ParseError(
                path="",
                value=value,
                expected_type=float,
                message=f"Cannot parse {value!r} as float"
            ),)
        )


class StringParser:
    """String parser (identity function)."""
    
    @classmethod
    def parse(cls, value: Any) -> ParseResult:
        """
        Parse a string value.
        
        Args:
            value: Raw value to parse
            
        Returns:
            ParseResult with success flag and parsed value
        """
        if isinstance(value, str):
            return ParseResult(success=True, value=value)
        
        # Convert other types to string
        try:
            return ParseResult(success=True, value=str(value))
        except Exception as e:
            return ParseResult(
                success=False,
                errors=(ParseError(
                    path="",
                    value=value,
                    expected_type=str,
                    message=f"Cannot convert {value!r} to string: {e}"
                ),)
            )


class ListParser:
    """List parser."""
    
    def __init__(self, element_parser):
        """
        Initialize list parser with element parser.
        
        Args:
            element_parser: Parser for individual list elements
        """
        self._element_parser = element_parser
    
    def parse(self, value: Any) -> ParseResult:
        """
        Parse a list value.
        
        Args:
            value: Raw value to parse (should be a list)
            
        Returns:
            ParseResult with success flag and parsed value
        """
        if not isinstance(value, list):
            return ParseResult(
                success=False,
                errors=(ParseError(
                    path="",
                    value=value,
                    expected_type=list,
                    message=f"Expected list, got {type(value).__name__}"
                ),)
            )
        
        # Parse each element
        parsed_list = []
        errors = []
        
        for i, elem in enumerate(value):
            result = self._element_parser.parse(elem)
            if result.success:
                parsed_list.append(result.value)
            else:
                # Collect errors with path prefix
                for err in result.errors:
                    new_error = ParseError(
                        path=f"[{i}].{err.path}",
                        value=elem,
                        expected_type=self._element_parser.__class__.__name__,
                        message=err.message
                    )
                    errors.append(new_error)
        
        if errors:
            return ParseResult(success=False, errors=tuple(errors))
        
        return ParseResult(success=True, value=parsed_list)


class DictParser:
    """Dict parser."""
    
    def __init__(self, field_parsers: Dict[str, Any]):
        """
        Initialize dict parser with field-specific parsers.
        
        Args:
            field_parsers: Mapping of field name to parser instance
        """
        self._field_parsers = field_parsers
    
    def parse(self, value: Any) -> ParseResult:
        """
        Parse a dict value.
        
        Args:
            value: Raw value to parse (should be a dict)
            
        Returns:
            ParseResult with success flag and parsed value
        """
        if not isinstance(value, dict):
            return ParseResult(
                success=False,
                errors=(ParseError(
                    path="",
                    value=value,
                    expected_type=dict,
                    message=f"Expected dict, got {type(value).__name__}"
                ),)
            )
        
        # Parse each field
        parsed_dict = {}
        errors = []
        
        for key, val in value.items():
            if key in self._field_parsers:
                parser = self._field_parsers[key]
                result = parser.parse(val)
                
                if result.success:
                    parsed_dict[key] = result.value
                else:
                    for err in result.errors:
                        new_error = ParseError(
                            path=f"{key}.{err.path}",
                            value=val,
                            expected_type=type(err.value),
                            message=err.message
                        )
                        errors.append(new_error)
            else:
                # Unknown fields - include them as-is
                parsed_dict[key] = val
        
        if errors:
            return ParseResult(success=False, errors=tuple(errors))
        
        return ParseResult(success=True, value=parsed_dict)


class DurationParser:
    """Duration/time parser (e.g., '5s', '1m30s', '2h')."""
    
    # Pattern: number followed by unit
    _PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*(ms|s|m|h|d|w|y)$')
    
    @classmethod
    def parse(cls, value: Any) -> ParseResult:
        """
        Parse a duration string.
        
        Units: ms (milliseconds), s (seconds), m (minutes), h (hours),
               d (days), w (weeks), y (years)
        
        Args:
            value: Duration string to parse
            
        Returns:
            ParseResult with success flag and parsed seconds as float
        """
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return ParseResult(success=True, value=float(value))
        
        if isinstance(value, str):
            match = cls._PATTERN.match(value.strip().lower())
            if match:
                amount = float(match.group(1))
                unit = match.group(2)
                
                multipliers = {
                    'ms': 0.001,
                    's': 1,
                    'm': 60,
                    'h': 3600,
                    'd': 86400,
                    'w': 604800,
                    'y': 31536000,
                }
                
                seconds = amount * multipliers.get(unit, 1)
                return ParseResult(success=True, value=seconds)
        
        return ParseResult(
            success=False,
            errors=(ParseError(
                path="",
                value=value,
                expected_type=str,
                message=f"Invalid duration format: {value!r}. Use '5s', '1m30s', etc."
            ),)
        )


class SizeParser:
    """Size parser (e.g., '1GB', '512MB', '2KB')."""
    
    _PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s*(b|kb|mb|gb|tb)$')
    
    @classmethod
    def parse(cls, value: Any) -> ParseResult:
        """
        Parse a size string.
        
        Units: b (bytes), kb (kilobytes), mb (megabytes),
               gb (gigabytes), tb (terabytes)
        
        Args:
            value: Size string to parse
            
        Returns:
            ParseResult with success flag and parsed bytes as int
        """
        if isinstance(value, int) and not isinstance(value, bool):
            return ParseResult(success=True, value=value)
        
        if isinstance(value, str):
            match = cls._PATTERN.match(value.strip().lower())
            if match:
                amount = float(match.group(1))
                unit = match.group(2)
                
                multipliers = {
                    'b': 1,
                    'kb': 1024,
                    'mb': 1024 ** 2,
                    'gb': 1024 ** 3,
                    'tb': 1024 ** 4,
                }
                
                bytes_count = int(amount * multipliers.get(unit, 1))
                return ParseResult(success=True, value=bytes_count)
        
        return ParseResult(
            success=False,
            errors=(ParseError(
                path="",
                value=value,
                expected_type=str,
                message=f"Invalid size format: {value!r}. Use '1GB', '512MB', etc."
            ),)
        )


# =============================================================================
# Parser Chain
# =============================================================================

class ConfigurationParser:
    """
    Main parser for configuration values.
    
    Provides typed parsing for all supported value types with
    proper error handling and source location tracking.
    """
    
    def __init__(self):
        self._parsers = {
            bool: BooleanParser(),
            int: IntegerParser(),
            float: FloatParser(),
            str: StringParser(),
        }
    
    def parse_value(self, value: Any, expected_type: type) -> ParseResult:
        """
        Parse a value to the expected type.
        
        Args:
            value: Raw value to parse
            expected_type: Target type (bool, int, float, str)
            
        Returns:
            ParseResult with parsed value or errors
        """
        parser = self._parsers.get(expected_type)
        if parser is None:
            return ParseResult(
                success=False,
                errors=(ParseError(
                    path="",
                    value=value,
                    expected_type=expected_type,
                    message=f"Unsupported type: {expected_type.__name__}"
                ),)
            )
        
        return parser.parse(value)


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Errors
    "ParseError",
    "ParseResult",
    
    # Parsed Value
    "ParsedValue",
    
    # Type Parsers
    "BooleanParser",
    "IntegerParser",
    "FloatParser",
    "StringParser",
    "ListParser",
    "DictParser",
    "DurationParser",
    "SizeParser",
    
    # Main Parser
    "ConfigurationParser",
]