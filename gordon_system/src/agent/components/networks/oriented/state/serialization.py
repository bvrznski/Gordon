# Oriented Network State Serialization - Phase 4.7.4
# ====================================================

"""
Serialization framework for Oriented Network State types.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic serialization
    - Repository-independent

SERIALIZATION TYPES:
    - StateSerializer: Serializes state to dict/JSON
    - StateDeserializer: Deserializes from dict/JSON
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Type


@dataclass(frozen=True)
class StateSerializer:
    """
    Serializer for Oriented Network State types.
    
    SEMANTIC ROLE:
        - Converts state to dictionary representation
        - Never includes runtime data
        
    SERIALIZATION INVARIANTS:
        S-INV-001: Deterministic (same input = same output)
        S-INV-002: Semantic data only
        S-INV-003: No runtime references
    """
    
    @staticmethod
    def serialize(state: Any) -> Dict[str, Any]:
        """
        Serialize a state to a dictionary.
        
        Args:
            state: State instance to serialize
            
        Returns:
            Dictionary representation of the state
            
        INVARIANT: Deserialization must be able to reconstruct the original state
        """
        if hasattr(state, "to_dict"):
            return state.to_dict()
        raise TypeError(f"Cannot serialize {type(state)} - missing to_dict() method")
    
    @classmethod
    def serialize_to_json(cls, state: Any) -> str:
        """
        Serialize a state to JSON string.
        
        Args:
            state: State instance to serialize
            
        Returns:
            JSON string representation
        """
        data = cls.serialize(state)
        return json.dumps(data)


@dataclass(frozen=True)
class StateDeserializer:
    """
    Deserializer for Oriented Network State types.
    
    SEMANTIC ROLE:
        - Reconstructs state from dictionary representation
        - Never executes runtime logic
        
    DESERIALIZATION INVARIANTS:
        D-INV-001: Deterministic (same input = same output)
        D-INV-002: Semantic data only
        D-INV-003: No runtime dependencies
    """
    
    @staticmethod
    def deserialize(data: Dict[str, Any], state_type: Type[Any]) -> Any:
        """
        Deserialize a dictionary to a state instance.
        
        Args:
            data: Dictionary representation of the state
            state_type: State class to instantiate
            
        Returns:
            New state instance
            
        INVARIANT: from_dict(to_dict(x)) == x for valid inputs
        """
        if hasattr(state_type, "from_dict"):
            return state_type.from_dict(data)
        raise TypeError(f"Cannot deserialize to {state_type} - missing from_dict() method")
    
    @classmethod
    def deserialize_from_json(cls, json_str: str, state_type: Type[Any]) -> Any:
        """
        Deserialize a JSON string to a state instance.
        
        Args:
            json_str: JSON string representation
            state_type: State class to instantiate
            
        Returns:
            New state instance
        """
        data = json.loads(json_str)
        return cls.deserialize(data, state_type)


def serialize_state(state: Any) -> Dict[str, Any]:
    """
    Serialize a state to a dictionary.
    
    Args:
        state: State instance to serialize
        
    Returns:
        Dictionary representation of the state
    """
    return StateSerializer.serialize(state)


def deserialize_state(data: Dict[str, Any], state_type: Type[Any]) -> Any:
    """
    Deserialize a dictionary to a state instance.
    
    Args:
        data: Dictionary representation of the state
        state_type: State class to instantiate
        
    Returns:
        New state instance
    """
    return StateDeserializer.deserialize(data, state_type)


__all__ = [
    "StateSerializer",
    "StateDeserializer",
    "serialize_state",
    "deserialize_state",
]