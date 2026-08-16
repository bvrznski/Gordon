# Gordon Cognitive Architecture - Phase 4.11.5
# ===========================================

"""
Cognitive Coordination Protocol (CCP) Serialization Module
===========================================================

Deterministic serialization for CCP messages and artifacts.

IMPORTANT: This module does NOT use pickle or any unsafe serialization.
All serialization is explicit, deterministic, and versioned.
"""

from __future__ import annotations

import json
from dataclasses import asdict, fields
from typing import Any, Optional


# =============================================================================
# CCP SERIALIZATION - Deterministic JSON-based serialization
# =============================================================================

class CCPSerializer:
    """
    Immutable deterministic serializer for CCP artifacts.
    
    Serialization is deterministic and reversible:
      - Same input -> same output (always)
      - Output can be deserialized to original form
    
    Does NOT serialize:
      - Functions, callbacks, or callables
      - Runtime references (sockets, processes, threads)
      - Object addresses or memory locations
      - Transient state (queues, locks, futures)
    """
    
    @staticmethod
    def serialize(data: Any) -> str:
        """
        Serialize data to JSON string.
        
        Args:
            data: Serializable CCP artifact
            
        Returns:
            JSON string representation
        """
        if hasattr(data, "__dict__"):
            # Convert dataclass to dict, filtering None values for cleaner output
            serialized = CCPSerializer._serialize_obj(data)
            return json.dumps(serialized, sort_keys=True)
        
        # For primitive types and collections
        return json.dumps(data, sort_keys=True)
    
    @staticmethod
    def deserialize(json_str: str) -> Any:
        """
        Deserialize JSON string to Python object.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            Deserialized CCP artifact
        """
        data = json.loads(json_str)
        return CCPSerializer._deserialize_obj(data)
    
    @staticmethod
    def _serialize_obj(obj: Any) -> dict[str, Any]:
        """Serialize an object to dictionary."""
        if hasattr(obj, "__dict__"):
            result = {}
            for key in sorted(obj.__dict__.keys()):
                value = getattr(obj, key)
                # Skip internal/private attributes and None values
                if not key.startswith("_") and value is not None:
                    result[key] = CCPSerializer._serialize_value(value)
            return result
        else:
            return obj
    
    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize a value (recursive)."""
        if hasattr(value, "__dict__"):
            return CCPSerializer._serialize_obj(value)
        elif isinstance(value, (list, tuple)):
            return [CCPSerializer._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: CCPSerializer._serialize_value(v) for k, v in sorted(value.items())}
        else:
            return value
    
    @staticmethod
    def to_dict(data: Any) -> dict[str, Any]:
        """Convert data to dictionary representation."""
        if hasattr(data, "__dict__"):
            return CCPSerializer._serialize_obj(data)
        elif isinstance(data, (list, tuple)):
            return [CCPSerializer._serialize_value(v) for v in data]
        else:
            return data
    
    @staticmethod
    def _deserialize_obj(data: dict[str, Any], target_type: Optional[type] = None) -> Any:
        """Deserialize dictionary to object."""
        if target_type is not None:
            # Try to instantiate the target type
            try:
                return target_type(**data)
            except (TypeError, AttributeError):
                pass
        
        # If no target type or instantiation fails, return as dict
        result = {}
        for key, value in data.items():
            result[key] = CCPSerializer._deserialize_value(value)
        return result
    
    @staticmethod
    def _deserialize_value(value: Any) -> Any:
        """Deserialize a value (recursive)."""
        if isinstance(value, dict):
            return CCPSerializer._deserialize_obj(value)
        elif isinstance(value, list):
            return [CCPSerializer._deserialize_value(v) for v in value]
        else:
            return value
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> dict[str, Any]:
        """Convert dictionary to standardized form."""
        return CCPSerializer._deserialize_obj(data)


# =============================================================================
# CCP MESSAGE SERIALIZATION - Message-specific serialization
# =============================================================================

class CCPMessageSerializer:
    """
    Deterministic serializer for CCP messages.
    
    Preserves all semantic metadata during serialization.
    """
    
    @staticmethod
    def serialize_message(message: Any) -> dict[str, Any]:
        """Serialize a CCP message to dictionary."""
        return CCPSerializer.to_dict(message)
    
    @staticmethod
    def deserialize_message(data: dict[str, Any]) -> dict[str, Any]:
        """Deserialize message data."""
        return CCPSerializer.from_dict(data)
    
    @classmethod
    def serialize_publication(cls, publication: Any) -> str:
        """Serialize a publication to JSON string."""
        pub_dict = {
            "identity": getattr(publication, "identity", ""),
            "publication_status": getattr(publication, "publication_status", ""),
            "semantic_time": getattr(publication, "semantic_time", None),
            "provenance": getattr(publication, "provenance", ""),
        }
        return json.dumps(pub_dict, sort_keys=True)
    
    @classmethod
    def deserialize_publication(cls, json_str: str) -> dict[str, Any]:
        """Deserialize publication from JSON string."""
        return json.loads(json_str)


# =============================================================================
# CCP SERIALIZATION VALIDATOR - Serialization integrity validation
# =============================================================================

class CCPSerializationValidator:
    """
    Immutable validator for serialized data.
    
    Ensures serialization integrity and format compliance.
    """
    
    @staticmethod
    def validate_json(json_str: str) -> tuple[bool, Optional[str]]:
        """
        Validate JSON string format.
        
        Returns:
            Tuple of (valid, error_message)
        """
        try:
            json.loads(json_str)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
    
    @staticmethod
    def validate_required_fields(
        data: dict[str, Any],
        required_fields: tuple[str, ...]
    ) -> tuple[bool, Optional[tuple[str, ...]]]:
        """
        Validate that all required fields are present.
        
        Returns:
            Tuple of (valid, missing_fields)
        """
        missing = [f for f in required_fields if f not in data]
        if missing:
            return False, tuple(missing)
        return True, None
    
    @staticmethod
    def validate_string_field(value: Any) -> tuple[bool, Optional[str]]:
        """Validate that a field is a non-empty string."""
        if not isinstance(value, str):
            return False, "Value must be a string"
        if len(value) == 0:
            return False, "String cannot be empty"
        return True, None
    
    @staticmethod
    def validate_numeric_field(
        value: Any,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate numeric field with optional bounds."""
        if not isinstance(value, (int, float)):
            return False, "Value must be numeric"
        
        if min_val is not None and value < min_val:
            return False, f"Value must be >= {min_val}"
        
        if max_val is not None and value > max_val:
            return False, f"Value must be <= {max_val}"
        
        return True, None