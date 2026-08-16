# Oriented Network Governance Serialization - Phase 4.7.11
# =======================================================

"""
Serialization Framework for Oriented Network Governance Models

This module provides deterministic serialization for all governance representations.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic serialization
    - Repository-independent

SERIALIZATION TYPES:

    Identity
        → Unique identifier
    Authority  
        → Source of governance authority
    Owner
        → Architectural owner
    Relationships
        → Semantic relationships between elements
    Dependencies
        → Explicit dependencies
    Revision
        → Version tracking
    SchemaVersion
        → Serialization schema version

NO SERIALIZATION:
    - Runtime permissions (never serialized)
    - Authentication state (never serialized)
    - Authorization tokens (never serialized)
    - Security credentials (never serialized)
    - Execution context (never serialized)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, fields
from typing import Any, Dict, Tuple


# =============================================================================
# SERIALIZATION CONSTANTS
# =============================================================================

SCHEMA_VERSION: str = "1.0.0"
"""Serialization schema version"""


# =============================================================================
# SERIALIZATION FUNCTIONS
# =============================================================================

def serialize_governance_object(obj: Any) -> Dict[str, Any]:
    """
    Serialize a governance object to dictionary format.
    
    Args:
        obj: Governance dataclass instance
        
    Returns:
        Dictionary representation of the object
    """
    return asdict(obj)


def deserialize_governance_object(
    data: Dict[str, Any],
    target_type: type,
) -> Any:
    """
    Deserialize a governance object from dictionary format.
    
    Args:
        data: Dictionary representation
        target_type: Target class type
        
    Returns:
        Instance of target type
    """
    return target_type(**data)


def serialize_to_json(obj: Any) -> str:
    """
    Serialize a governance object to JSON string.
    
    Args:
        obj: Governance dataclass instance
        
    Returns:
        JSON string representation
    """
    return json.dumps(serialize_governance_object(obj), indent=2)


def deserialize_from_json(
    json_str: str,
    target_type: type,
) -> Any:
    """
    Deserialize a governance object from JSON string.
    
    Args:
        json_str: JSON string representation
        target_type: Target class type
        
    Returns:
        Instance of target type
    """
    data = json.loads(json_str)
    return deserialize_governance_object(data, target_type)


# =============================================================================
# SERIALIZATION VALIDATION
# =============================================================================

def validate_serialization_schema(
    data: Dict[str, Any],
    expected_keys: Tuple[str, ...] = (),
) -> Tuple[bool, Tuple[str, ...]]:
    """
    Validate that serialized data has the expected structure.
    
    Args:
        data: Serialized data dictionary
        expected_keys: Expected keys in the data
        
    Returns:
        (is_valid, errors) tuple
    """
    errors = []
    
    # Check schema version if present
    if "schema_version" in data and data["schema_version"] != SCHEMA_VERSION:
        errors.append(f"schema_version mismatch: expected {SCHEMA_VERSION}, got {data.get('schema_version')}")
    
    # Check for required keys
    missing_keys = set(expected_keys) - set(data.keys())
    if missing_keys:
        errors.append(f"missing required keys: {', '.join(missing_keys)}")
    
    return len(errors) == 0, tuple(errors)


# =============================================================================
# DETERMINISTIC HASH
# =============================================================================

def get_deterministic_hash(obj: Any) -> str:
    """
    Get a deterministic hash for a governance object.
    
    Args:
        obj: Governance dataclass instance
        
    Returns:
        Hex string hash
    """
    import hashlib
    
    # Convert to sorted JSON string for determinism
    data = serialize_governance_object(obj)
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


# =============================================================================
# SERIALIZATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class SerializationContract:
    """
    Contract defining serialization requirements.
    
    INVARIANTS:
        SC-INV-001: Serialization is deterministic
        SC-INV-002: Serialization never includes runtime data
        SC-INV-003: Deserialization preserves semantic meaning
    """
    
    contract_id: str = "serialization-contract"
    """Unique contract identifier"""
    
    schema_version: str = SCHEMA_VERSION
    """Serialization schema version"""
    
    required_fields: Tuple[str, ...] = (
        "identity",
        "authority",
        "owner",
        "relationships",
        "dependencies",
        "revision",
        "schema_version",
    )
    """Required fields in serialized representation"""
    
    forbidden_fields: Tuple[str, ...] = (
        "runtime_permissions",
        "authentication_state",
        "authorization_tokens",
        "security_credentials",
        "execution_context",
    )
    """Fields that must never be serialized"""
    
    @property
    def is_valid(self) -> bool:
        return True
    
    def validate_serialized_data(
        self,
        data: Dict[str, Any],
    ) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate that serialized data complies with contract.
        
        Args:
            data: Serialized data dictionary
            
        Returns:
            (is_valid, errors) tuple
        """
        errors = []
        
        # Check required fields
        for field_name in self.required_fields:
            if field_name not in data:
                errors.append(f"missing required field: {field_name}")
        
        # Check forbidden fields are not present
        for field_name in self.forbidden_fields:
            if field_name in data:
                errors.append(f"forbidden field present: {field_name}")
        
        return len(errors) == 0, tuple(errors)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "SCHEMA_VERSION",
    
    # Serialization functions
    "serialize_governance_object",
    "deserialize_governance_object",
    "serialize_to_json",
    "deserialize_from_json",
    
    # Validation
    "validate_serialization_schema",
    
    # Hashing
    "get_deterministic_hash",
    
    # Contract
    "SerializationContract",
]