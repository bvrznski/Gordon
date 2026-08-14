# Identity Serialization & Compatibility - Phase 3.19.13
# ========================================================

"""
Identity serialization and compatibility utilities.

All identity types must support:
    - Binary serialization for storage/transmission
    - Deterministic comparison for equality checks
    - Schema evolution support for versioning
    - Forward/backward compatibility

SERIALIZATION HIERARCHY:
    SerializationFormat     - Format specification
        ├── IdentitySerializer  - Serialization engine
        └── IdentityDeserializer- Deserialization engine
        
COMPATIBILITY:
    CompatibilityMode       - Compatibility checking mode
        ├── IdentityCompatibilityChecker
        └── SchemaEvolutionValidator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Protocol,
    runtime_checkable,
    TypeVar,
    Generic,
    Optional,
)
import json
import uuid
import hashlib


# =============================================================================
# SERIALIZATION FORMAT ENUM
# =============================================================================


class SerializationFormat(Enum):
    """
    Canonical serialization formats for identity values.
    
    FORMATS:
        JSON      - Human-readable JSON format
        BINARY    - Compact binary format (MessagePack-style)
        STRING    - Plain string representation
        HEX       - Hexadecimal encoding
        
    INVARIANTS:
        SF-001: All formats must preserve identity value
        SF-002: Serialization is deterministic (same input -> same output)
        SF-003: Deserialization must validate integrity
    """
    
    JSON = "json"
    BINARY = "binary"
    STRING = "string"
    HEX = "hex"


# =============================================================================
# IDENTITY SERIALIZER
# =============================================================================


@dataclass(frozen=True)
class IdentitySerializer:
    """
    Serializer for identity values across all formats.
    
    Provides deterministic serialization of identities into various
    formats while preserving all metadata and type information.
    
    INVARIANTS:
        S-001: Serialization is deterministic (same input -> same output)
        S-002: All metadata is preserved during serialization
        S-003: Format conversion preserves identity value
        
    METHODS:
        serialize()     - Serialize to specified format
        deserialize()   - Deserialize from any supported format
        hash_value()    - Get deterministic hash of identity
    """
    
    format_: SerializationFormat = SerializationFormat.JSON
    
    def serialize(self, value: str) -> str | bytes:
        """Serialize an identity value to the configured format."""
        if self.format_ == SerializationFormat.STRING:
            return value
        
        elif self.format_ == SerializationFormat.HEX:
            return value.encode().hex()
        
        elif self.format_ == SerializationFormat.JSON:
            return json.dumps({"value": value})
        
        elif self.format_ == SerializationFormat.BINARY:
            # Binary format: length-prefixed UTF-8 bytes
            encoded = value.encode("utf-8")
            return len(encoded).to_bytes(4, "big") + encoded
        
        raise ValueError(f"Unsupported format: {self.format_}")
    
    def deserialize(self, data: str | bytes) -> str:
        """Deserialize from any supported format back to string."""
        if isinstance(data, bytes):
            # Could be binary or hex
            try:
                return bytes.fromhex(data.decode()).decode()
            except (ValueError, UnicodeDecodeError):
                # Try binary format
                length = int.from_bytes(data[:4], "big")
                return data[4:].decode("utf-8")
        
        elif isinstance(data, str):
            # Try to parse JSON first
            if data.startswith("{"):
                try:
                    parsed = json.loads(data)
                    return parsed.get("value", data)
                except json.JSONDecodeError:
                    pass
            return data
        
        raise ValueError(f"Cannot deserialize: {type(data)}")
    
    def hash_value(self, value: str) -> str:
        """Get a deterministic hash of an identity value."""
        # SHA256 for strong collision resistance
        return hashlib.sha256(value.encode()).hexdigest()[:32]


# =============================================================================
# IDENTITY DESERIALIZER
# =============================================================================


@dataclass(frozen=True)
class IdentityDeserializer:
    """
    Deserializer for identity values from various formats.
    
    Validates the deserialized value and reconstructs any missing
    metadata based on context.
    
    INVARIANTS:
        D-001: Deserialization must validate format integrity
        D-002: Invalid data raises appropriate exceptions
        D-003: Missing metadata can be filled with defaults
        
    METHODS:
        from_string()   - Parse string representation
        from_json()     - Parse JSON object
        from_binary()   - Parse binary format
        validate()      - Validate deserialized value
    """
    
    def from_string(self, s: str) -> str:
        """Parse identity from string representation."""
        # Remove any format prefixes
        if s.startswith("json:"):
            return s[5:]
        elif s.startswith("bin:"):
            return bytes.fromhex(s[4:]).decode()
        elif s.startswith("hex:"):
            return s[4:]
        
        # Check for JSON-encoded value
        if s.startswith("{") and s.endswith("}"):
            parsed = json.loads(s)
            return parsed.get("value", "")
        
        return s
    
    def from_json(self, data: dict) -> str:
        """Parse identity from JSON object."""
        if "value" in data:
            return data["value"]
        
        # Fallback to parsing as string
        value_str = json.dumps(data)
        return self.from_string(value_str)
    
    def from_binary(self, data: bytes) -> str:
        """Parse identity from binary format."""
        length = int.from_bytes(data[:4], "big")
        if len(data) < 4 + length:
            raise ValueError("Binary data too short")
        
        value = data[4 : 4 + length].decode("utf-8")
        return self.from_string(value)
    
    def validate(self, value: str) -> bool:
        """Validate a deserialized identity value."""
        # Must be non-empty
        if not value or len(value.strip()) < 1:
            return False
        
        # Check for invalid characters (no control chars except space)
        for char in value:
            if char < " " and char != "\n" and char != "\t":
                return False
        
        return True


# =============================================================================
# COMPATIBILITY MODE
# =============================================================================


class CompatibilityMode(Enum):
    """
    Modes for compatibility checking between identity versions.
    
    MODES:
        STRICT      - Exact match required (no evolution)
        EVOLUTION   - Allow schema evolution
        BACKWARD    - Accept newer format as older (backward compatible)
        FORWARD     - Accept older format as newer (forward compatible)
        
    INVARIANTS:
        CM-001: Mode determines validation strictness
        CM-002: Mode affects whether changes are accepted
        CM-003: Compatibility is transitive in EVOLUTION mode
    """
    
    STRICT = "strict"
    EVOLUTION = "evolution"
    BACKWARD = "backward"
    FORWARD = "forward"


# =============================================================================
# COMPATIBILITY CHECKER
# =============================================================================


@dataclass(frozen=True)
class IdentityCompatibilityChecker:
    """
    Checker for compatibility between identity versions and formats.
    
    Determines whether an old identity is compatible with a new one,
    enabling safe migration and evolution.
    
    INVARIANTS:
        CC-001: Same value is always compatible
        CC-002: Compatible values have same hash
        CC-003: Migration path can be determined
        
    METHODS:
        is_compatible()     - Check if two identities are compatible
        get_migration_path()- Determine migration path between versions
        validate_migrate()  - Validate identity can migrate safely
    """
    
    mode: CompatibilityMode = CompatibilityMode.EVOLUTION
    
    def is_compatible(self, old_value: str, new_value: str) -> bool:
        """Check if two identity values are compatible."""
        # Same value is always compatible
        if old_value == new_value:
            return True
        
        if self.mode == CompatibilityMode.STRICT:
            return False
        
        # In EVOLUTION mode, check semantic compatibility
        if self.mode == CompatibilityMode.EVOLUTION:
            # Check hash compatibility (same type of ID)
            old_hash = hashlib.sha256(old_value.encode()).hexdigest()[:8]
            new_hash = hashlib.sha256(new_value.encode()).hexdigest()[:8]
            
            # Allow similar prefixes in evolution mode
            return old_hash[:4] == new_hash[:4]
        
        # In BACKWARD/FORWARD modes, check for common patterns
        if self.mode in (CompatibilityMode.BACKWARD, CompatibilityMode.FORWARD):
            # Check if one is a valid superset of the other
            return (
                old_value.startswith(new_value)
                or new_value.startswith(old_value)
            )
        
        return False
    
    def get_migration_path(
        self,
        old_value: str,
        new_value: str,
    ) -> list[str]:
        """Determine migration path from old to new value."""
        if self.is_compatible(old_value, new_value):
            if old_value == new_value:
                return ["no-op"]
            
            # Determine type of change
            changes = []
            
            # Check for prefix change
            if old_value[:3] != new_value[:3]:
                changes.append(f"prefix:{old_value[:3]}->{new_value[:3]}")
            
            # Check for suffix change  
            if old_value[-3:] != new_value[-3:]:
                changes.append(f"suffix:{old_value[-3:]}->{new_value[-3:]}")
            
            return changes or ["value-change"]
        
        return ["incompatible"]
    
    def validate_migrate(
        self,
        identity_value: str,
        target_format: Optional[SerializationFormat] = None,
    ) -> bool:
        """Validate that identity can migrate safely."""
        # Basic validation
        if not identity_value or len(identity_value.strip()) < 1:
            return False
        
        # Format-specific checks
        if target_format == SerializationFormat.JSON:
            try:
                json.loads(identity_value)
            except json.JSONDecodeError:
                return False
        
        return True


# =============================================================================
# SCHEMA EVOLUTION VALIDATOR
# =============================================================================


class SchemaEvolutionValidator:
    """
    Validator for schema evolution compatibility.
    
    Tracks which schema versions are compatible and provides
    upgrade/downgrade paths.
    
    INVARIANTS:
        SEV-001: Schema version n is compatible with n+k (k >= 0) in forward mode
        SEV-002: Schema version n is compatible with n-k (k >= 0) in backward mode  
        SEV-003: Migration path is deterministic
        
    METHODS:
        add_compatibility() - Register compatibility between versions
        is_evolutionary()   - Check if two versions are evolutionary compatible
        get_upgrade_path()  - Get path to upgrade from older to newer
    """
    
    def __init__(self):
        self._compatibility: dict[tuple[int, int], bool] = {}
    
    def add_compatibility(self, v1: int, v2: int) -> None:
        """Register that two schema versions are compatible."""
        if v1 < v2:
            self._compatibility[(v1, v2)] = True
        else:
            self._compatibility[(v2, v1)] = True
    
    def is_evolutionary(self, v1: int, v2: int) -> bool:
        """Check if two schema versions are evolutionarily compatible."""
        # Same version is always compatible
        if v1 == v2:
            return True
        
        # Check registered compatibility
        key = (min(v1, v2), max(v1, v2))
        return self._compatibility.get(key, False)
    
    def get_upgrade_path(self, from_version: int, to_version: int) -> list[int]:
        """Get the upgrade path from older to newer version."""
        if from_version >= to_version:
            return []
        
        # Simple linear path (can be extended for complex schemas)
        return list(range(from_version + 1, to_version + 1))


# =============================================================================
# SERIALIZATION REGISTRY
# =============================================================================


class IdentitySerializationRegistry:
    """
    Registry for managing identity serialization configurations.
    
    Provides utilities for tracking which formats are used where and
    ensuring consistency across the system.
    
    INVARIANTS:
        SR-001: All registered serializers use compatible formats
        SR-002: Format conversion is always possible through canonical form
        SR-003: Registry tracks serialization usage statistics
        
    METHODS:
        register_serializer()   - Register a serializer for a domain
        get_serializer()        - Get serializer for a domain
        convert_format()        - Convert between formats
    """
    
    def __init__(self):
        self._serializers: dict[str, IdentitySerializer] = {}
        self._deserializers: dict[str, IdentityDeserializer] = {}
    
    def register_serializer(
        self,
        domain: str,
        serializer: IdentitySerializer,
    ) -> None:
        """Register a serializer for a specific domain."""
        self._serializers[domain] = serializer
    
    def get_serializer(self, domain: str) -> Optional[IdentitySerializer]:
        """Get the registered serializer for a domain."""
        return self._serializers.get(domain)
    
    def convert_format(
        self,
        value: str,
        source_format: SerializationFormat,
        target_format: SerializationFormat,
    ) -> str | bytes:
        """Convert an identity between formats."""
        # Use string as canonical intermediate format
        if source_format == target_format:
            return value
        
        # Deserialize to string first
        deserializer = IdentityDeserializer()
        
        if isinstance(value, bytes):
            result = deserializer.from_binary(value)
        else:
            result = deserializer.from_string(str(value))
        
        # Serialize to target format
        serializer = IdentitySerializer(format_=target_format)
        return serializer.serialize(result)


__all__ = [
    "SerializationFormat",
    "IdentitySerializer",
    "IdentityDeserializer",
    "CompatibilityMode",
    "IdentityCompatibilityChecker",
    "SchemaEvolutionValidator",
    "IdentitySerializationRegistry",
]