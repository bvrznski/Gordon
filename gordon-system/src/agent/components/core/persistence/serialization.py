# Serialization Manager
# =====================

"""
Serialization authority and codec management.

This module provides:
- SerializationManager: Canonical serialization authority
- Codec registry for format-specific encoding/decoding
- Deterministic serialization requirements
- Type safety and rejection of unsafe types

Key principle: Serialization only transforms data - it does NOT determine
persistence eligibility. A value being serializable does not make it safe
to persist.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type, List
from enum import Enum
import json
import uuid
import threading
import asyncio


# =============================================================================
# Schema Identity and Versioning
# =============================================================================

@dataclass(frozen=True)
class SchemaId:
    """Unique identifier for a schema."""
    
    domain: str
    version: int
    
    def __str__(self) -> str:
        return f"{self.domain}:v{self.version}"


@dataclass(frozen=True)
class SchemaInfo:
    """Information about a schema."""
    
    schema_id: SchemaId
    fields: Dict[str, Any]
    required_fields: List[str] = field(default_factory=list)
    optional_fields: Dict[str, Any] = field(default_factory=dict)
    defaults: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Serialization Error Types
# =============================================================================

class SerializationError(Exception):
    """Base exception for serialization errors."""
    pass


class UnsafeTypeError(SerializationError):
    """Attempt to serialize an unsafe type (live handle, callable, etc.)."""
    pass


class UnsupportedTypeError(SerializationError):
    """Type not supported by the selected codec."""
    pass


class DecodingError(SerializationError):
    """Error during deserialization."""
    pass


# =============================================================================
# Serialization Format Definitions
# =============================================================================

class SerializationFormat(Enum):
    """Supported serialization formats."""
    
    CANONICAL_JSON = "canonical_json"
    MESSAGEPACK = "messagepack"
    PROTOBUF = "protobuf"
    CBOR = "cbor"


@dataclass(frozen=True)
class CodecInfo:
    """Information about a registered codec."""
    
    format: SerializationFormat
    name: str
    version: str
    deterministic: bool  # Does equivalent state produce same bytes?
    supports_encryption: bool
    default_compression: Optional[str] = None


# =============================================================================
# Type Model - What Can Be Serialized
# =============================================================================

class SerializableType(Enum):
    """Categories of serializable types."""
    
    SCALAR = "scalar"
    ENUM = "enum"
    IMMUTABLE_RECORD = "immutable_record"
    TUPLE = "tuple"
    IMMUTABLE_MAPPING = "immutable_mapping"
    BOUNDED_SEQUENCE = "bounded_sequence"
    STABLE_IDENTIFIER = "stable_identifier"
    TYPE_REFERENCE = "type_reference"
    UNION = "union"
    VERSIONED_PAYLOAD = "versioned_payload"


# =============================================================================
# Serialization Limits
# =============================================================================

@dataclass(frozen=True)
class SerializationLimits:
    """Safety limits for serialization."""
    
    max_depth: int = 100
    max_collection_size: int = 10_000
    max_string_length: int = 100_000
    max_binary_size: int = 1_000_000
    
    max_record_fields: int = 1_000
    max_schema_version: int = 1000
    
    max_total_payload_size: int = 10_000_000


# =============================================================================
# Unsafe Type Detection
# =============================================================================

def is_unsafe_type(value: Any) -> bool:
    """
    Check if a value contains unsafe types that should not be serialized.
    
    Returns:
        True if value contains unsafe types
    """
    import _thread
    
    # File-like objects
    if hasattr(value, 'read') or hasattr(value, 'write'):
        return True
    
    # Threading primitives - use actual types from the module
    try:
        lock_type = type(_thread.allocate_lock())
        if isinstance(value, lock_type):
            return True
        
        rlock_type = type(threading.RLock())
        if isinstance(value, rlock_type):
            return True
        
        semaphore_type = type(threading.Semaphore())
        if isinstance(value, semaphore_type):
            return True
        
        event_type = type(threading.Event())
        if isinstance(value, event_type):
            return True
    except Exception:
        pass
    
    # Async primitives
    try:
        asyncio_lock_type = type(asyncio.Lock())
        if isinstance(value, asyncio_lock_type):
            return True
        
        condition_type = type(asyncio.Condition())
        if isinstance(value, condition_type):
            return True
        
        semaphore_type = type(asyncio.Semaphore())
        if isinstance(value, semaphore_type):
            return True
        
        event_type = type(asyncio.Event())
        if isinstance(value, event_type):
            return True
    except Exception:
        pass
    
    # Callables - reject functions and methods but not all callables
    import inspect
    if callable(value):
        if inspect.isfunction(value) or inspect.ismethod(value):
            return True
        
        if getattr(value, '__name__', '').startswith('<lambda>'):
            return True
    
    return False


def check_unsafe_types_recursive(
    value: Any,
    path: str = "root",
    limits: SerializationLimits = None
) -> List[str]:
    """
    Recursively check for unsafe types in nested structures.
    
    Returns:
        List of paths where unsafe types were found (empty if clean)
    """
    if limits is None:
        limits = SerializationLimits()
    
    issues = []
    
    # Check direct type
    if is_unsafe_type(value):
        issues.append(f"{path}: contains unsafe type")
        return issues
    
    # Recurse into collections
    if isinstance(value, dict) and len(value) <= limits.max_collection_size:
        for k, v in value.items():
            issues.extend(check_unsafe_types_recursive(v, f"{path}.dict[{k}]", limits))
    
    elif isinstance(value, (list, tuple)) and len(value) <= limits.max_collection_size:
        for i, item in enumerate(value):
            issues.extend(check_unsafe_types_recursive(item, f"{path}.seq[{i}]", limits))
    
    # Check dataclass attributes
    if hasattr(value, '__dataclass_fields__'):
        for field_name in value.__dataclass_fields__:
            try:
                field_value = getattr(value, field_name)
                issues.extend(check_unsafe_types_recursive(
                    field_value, f"{path}.{field_name}", limits
                ))
            except AttributeError:
                pass
    
    return issues


# =============================================================================
# Codec Protocol
# =============================================================================

class SerializationCodec(ABC):
    """Protocol for a serialization codec."""
    
    @property
    @abstractmethod
    def format(self) -> SerializationFormat:
        """Return the format this codec handles."""
        pass
    
    @abstractmethod
    def encode(self, value: Any, context: Dict[str, Any] = None) -> bytes:
        """
        Encode a value to bytes.
        
        Args:
            value: The value to encode (must be serializable)
            context: Optional encoding context
            
        Returns:
            Encoded bytes
            
        Raises:
            UnsafeTypeError: If value contains unsafe types
            UnsupportedTypeError: If type not supported
        """
        pass
    
    @abstractmethod
    def decode(self, data: bytes, expected_type: Type[Any] = None) -> Any:
        """
        Decode bytes to a value.
        
        Args:
            data: Bytes to decode
            expected_type: Optional type hint for validation
            
        Returns:
            Decoded value
            
        Raises:
            DecodingError: If decoding fails
        """
        pass
    
    @abstractmethod
    def is_deterministic(self) -> bool:
        """Return True if this codec produces deterministic output."""
        pass


# =============================================================================
# Canonical JSON Codec (Reference Implementation)
# =============================================================================

class CanonicalJsonCodec(SerializationCodec):
    """
    Deterministic JSON codec with strict type requirements.
    """
    
    def __init__(self) -> None:
        self._format = SerializationFormat.CANONICAL_JSON
    
    @property
    def format(self) -> SerializationFormat:
        return self._format
    
    def is_deterministic(self) -> bool:
        return True
    
    def encode(self, value: Any, context: Dict[str, Any] = None) -> bytes:
        """Encode to canonical JSON."""
        issues = check_unsafe_types_recursive(value)
        if issues:
            raise UnsafeTypeError(f"Unsafe types found: {', '.join(issues)}")
        
        canonical = self._to_canonical(value)
        return json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode('utf-8')
    
    def decode(self, data: bytes, expected_type: Type[Any] = None) -> Any:
        """Decode from canonical JSON."""
        try:
            value = json.loads(data.decode('utf-8'))
            
            if expected_type and not self._type_check(value, expected_type):
                raise DecodingError(f"Decoded type {type(value)} not compatible with {expected_type}")
            
            return value
        except json.JSONDecodeError as e:
            raise DecodingError(f"Invalid JSON: {e}") from e
    
    def _to_canonical(self, value: Any) -> Any:
        """Convert to canonical form for deterministic serialization."""
        if isinstance(value, dict):
            return {k: self._to_canonical(v) for k, v in sorted(value.items())}
        elif isinstance(value, (list, tuple)):
            return [self._to_canonical(item) for item in value]
        elif isinstance(value, float):
            if value != value:
                return "NaN"
            elif value == float('inf'):
                return "Infinity"
            elif value == float('-inf'):
                return "-Infinity"
            else:
                return round(value, 10)
        elif isinstance(value, (int, str, bool)) or value is None:
            return value
        else:
            raise UnsupportedTypeError(f"Cannot serialize {type(value)}")
    
    def _type_check(self, value: Any, expected_type: Type[Any]) -> bool:
        """Check if decoded value matches expected type."""
        origin = getattr(expected_type, '__origin__', None)
        
        if origin is dict:
            key_t, val_t = getattr(expected_type, '__args__', (Any, Any))
            return isinstance(value, dict) and all(
                self._type_check(k, key_t) and self._type_check(v, val_t)
                for k, v in value.items()
            )
        elif origin is list:
            item_t = getattr(expected_type, '__args__', (Any,))[0]
            return isinstance(value, list) and all(
                self._type_check(item, item_t) for item in value
            )
        
        return isinstance(value, expected_type)


# =============================================================================
# Serialization Manager
# =============================================================================

class SerializationManager:
    """
    Canonical serialization authority.
    
    Manages:
        - Codec registration and selection
        - Deterministic encoding/decoding
        - Unsafe type rejection
        - Size limits enforcement
    """
    
    def __init__(self) -> None:
        self._codecs: Dict[SerializationFormat, SerializationCodec] = {}
        self._limits = SerializationLimits()
    
    def register_codec(self, codec: SerializationCodec) -> None:
        """Register a codec for its format."""
        if codec.format in self._codecs:
            raise ValueError(f"Codec for {codec.format} already registered")
        self._codecs[codec.format] = codec
    
    def get_codec(self, fmt: SerializationFormat) -> Optional[SerializationCodec]:
        """Get the codec for a format."""
        return self._codecs.get(fmt)
    
    async def serialize(
        self,
        value: Any,
        format: SerializationFormat = SerializationFormat.CANONICAL_JSON
    ) -> bytes:
        """
        Serialize a value to bytes.
        
        Args:
            value: The value to serialize (must be serializable)
            format: Target serialization format
            
        Returns:
            Serialized bytes
            
        Raises:
            UnsafeTypeError: If value contains unsafe types
            UnsupportedTypeError: If no codec for format or type not supported
        """
        codec = self._codecs.get(format)
        if not codec:
            raise UnsupportedTypeError(f"No codec registered for {format}")
        
        issues = check_unsafe_types_recursive(value, limits=self._limits)
        if issues:
            raise UnsafeTypeError(f"Unsafe types in value: {', '.join(issues)}")
        
        return codec.encode(value)
    
    async def deserialize(
        self,
        data: bytes,
        expected_type: Type[Any] = None
    ) -> Any:
        """
        Deserialize bytes to a value.
        
        Args:
            data: Bytes to decode
            expected_type: Optional type for validation
            
        Returns:
            Decoded value
            
        Raises:
            DecodingError: If decoding fails
        """
        for codec in self._codecs.values():
            try:
                return codec.decode(data, expected_type)
            except DecodingError:
                continue
        
        raise DecodingError("Failed to decode data with any registered codec")
    
    def is_deterministic(self) -> bool:
        """Check if all registered codecs are deterministic."""
        return all(c.is_deterministic() for c in self._codecs.values())
    
    @property
    def limits(self) -> SerializationLimits:
        """Get serialization limits."""
        return self._limits


__all__ = [
    # Exceptions
    "SerializationError",
    "UnsafeTypeError",
    "UnsupportedTypeError",
    "DecodingError",
    
    # Schema
    "SchemaId",
    "SchemaInfo",
    
    # Formats and info
    "SerializationFormat",
    "CodecInfo",
    
    # Limits
    "SerializationLimits",
    
    # Safety
    "is_unsafe_type",
    "check_unsafe_types_recursive",
    
    # Codec protocol and implementations
    "SerializationCodec",
    "CanonicalJsonCodec",
    
    # Manager
    "SerializationManager",
]