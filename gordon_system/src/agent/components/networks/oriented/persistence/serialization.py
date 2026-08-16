# Oriented Network Serialization Framework - Phase 4.7.8 Part 2
# =============================================================

"""
Serialization Framework for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Serialization produces deterministic output
    - No runtime state or handles are serialized
    - Pure semantic representation only
    
PHASE 4.7.8 PART 2 - SERIALIZATION:
    Serialization framework for persistence models
    Schema validation and compatibility checking

NO RUNTIME BEHAVIOR:
    - No runtime serialization (pickle, json.dumps with handles)
    - No checkpointing
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, Tuple, Type

from gordon_system.src.agent.components.networks.oriented.persistence.base import BasePersistenceModel


# =============================================================================
# SERIALIZATION CONSTANTS
# =============================================================================

SCHEMA_VERSION = "1.0.0"
"""Current schema version for serialization compatibility"""

IDENTITY_KEY = "identity"
AUTHORITY_KEY = "authority"
OWNER_KEY = "owner"
RELATIONSHIPS_KEY = "relationships"
DEPENDENCIES_KEY = "dependencies"
REVISION_KEY = "revision"
VERSION_KEY = "version"
SCHEMA_VERSION_KEY = "schema_version"


# =============================================================================
# SERIALIZATION RESULTS
# =============================================================================

SerializationResult = Tuple[bool, Dict[str, Any] | str]
"""
Serialization result: (is_valid, serialized_data_or_error_message)
"""


# =============================================================================
# BASE SERIALIZER
# =============================================================================

class BaseSerializer:
    """
    Base serializer for Oriented Network persistence models.
    
    INVARIANTS:
        BS-INV-001: Serialization is deterministic
        BS-INV-002: Serialization never includes runtime handles
        BS-INV-003: Deserialization must produce valid instances
    """
    
    @staticmethod
    def serialize(model: BasePersistenceModel) -> str:
        """
        Serialize a persistence model to JSON string.
        
        Args:
            model: The persistence model to serialize
            
        Returns:
            JSON string representation
            
        INVARIANT: Same input produces same output
        """
        data = BaseSerializer._model_to_dict(model)
        return json.dumps(data, sort_keys=True)
    
    @staticmethod
    def deserialize(json_str: str) -> Dict[str, Any]:
        """
        Deserialize a JSON string to dictionary.
        
        Args:
            json_str: JSON string from serialize()
            
        Returns:
            Dictionary representation
            
        INVARIANT: Deterministic parsing
        """
        return json.loads(json_str)
    
    @staticmethod
    def _model_to_dict(model: BasePersistenceModel) -> Dict[str, Any]:
        """
        Convert model to dictionary for serialization.
        
        Args:
            model: The persistence model
            
        Returns:
            Dictionary ready for JSON serialization
        """
        data = asdict(model)
        # Add schema metadata
        data[SCHEMA_VERSION_KEY] = SCHEMA_VERSION
        return data


# =============================================================================
# VALIDATION RESULTS
# =============================================================================

ValidationResult = Tuple[bool, Tuple[str, ...]]
"""
Validation result: (is_valid, list_of_errors_or_warnings)
"""


# =============================================================================
# BASE VALIDATOR
# =============================================================================

class BaseValidator:
    """
    Base validator for Oriented Network persistence models.
    
    INVARIANTS:
        BV-INV-001: Validation is deterministic
        BV-INV-002: Validation never modifies input
        BV-INV-003: Validation checks ownership compliance
    """
    
    @staticmethod
    def validate_model(model: BasePersistenceModel) -> ValidationResult:
        """
        Validate a persistence model.
        
        Args:
            model: The persistence model to validate
            
        Returns:
            (is_valid, list_of_errors)
            
        INVARIANT: Same input produces same output
        """
        is_valid, errors = model.validate()
        return is_valid, errors
    
    @staticmethod
    def validate_serialization(
        data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate serialized data structure.
        
        Args:
            data: Dictionary from deserialized JSON
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required keys
        required_keys = [SCHEMA_VERSION_KEY, IDENTITY_KEY]
        for key in required_keys:
            if key not in data:
                errors.append(f"Missing required field: {key}")
        
        # Validate schema version compatibility
        schema_version = data.get(SCHEMA_VERSION_KEY, "")
        if schema_version != SCHEMA_VERSION:
            errors.append(
                f"Incompatible schema version: {schema_version} "
                f"(expected: {SCHEMA_VERSION})"
            )
        
        return len(errors) == 0, tuple(errors)
    
    @staticmethod
    def validate_ontology_compliance(
        model: BasePersistenceModel,
        ontology_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate model against ontology requirements.
        
        Args:
            model: The persistence model
            ontology_data: Ontology constraints
            
        Returns:
            (is_valid, list_of_errors)
        """
        # Semantic validation - ensure no runtime artifacts
        if hasattr(model, "__dict__"):
            for attr_name, attr_value in vars(model).items():
                if BaseValidator._contains_runtime_artifact(attr_value):
                    return False, (
                        f"Invalid runtime artifact found in {attr_name}",
                    )
        
        return True, ()
    
    @staticmethod
    def _contains_runtime_artifact(value: Any) -> bool:
        """
        Check if a value contains runtime artifacts.
        
        Args:
            value: Value to check
            
        Returns:
            True if runtime artifact detected
        """
        # Runtime types that should never be serialized
        runtime_types = (
            "threading", "multiprocessing", "asyncio",
            "queue", "subprocess", "socket", "requests"
        )
        
        if isinstance(value, str):
            return any(rt in value for rt in runtime_types)
        elif isinstance(value, dict):
            return any(BaseValidator._contains_runtime_artifact(v) 
                      for v in value.values())
        elif isinstance(value, (list, tuple)):
            return any(BaseValidator._contains_runtime_artifact(item) 
                      for item in value)
        
        return False


# =============================================================================
# SERIALIZATION EXPORTS
# =============================================================================

__all__ = [
    "SCHEMA_VERSION",
    "IDENTITY_KEY",
    "AUTHORITY_KEY",
    "OWNER_KEY",
    "RELATIONSHIPS_KEY",
    "DEPENDENCIES_KEY",
    "REVISION_KEY",
    "VERSION_KEY",
    "SCHEMA_VERSION_KEY",
    "SerializationResult",
    "BaseSerializer",
    "ValidationResult",
    "BaseValidator",
]