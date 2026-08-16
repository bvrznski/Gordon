# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Serialization Models - Deterministic Event Serialization

This module defines how cognitive events are serialized to/from dictionaries
for storage, transmission, and replay.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CognitiveEventSerializer:
    """
    Serializer for cognitive events and related models.
    
    SERIALIZATION LAWS (SER-LAW)
    ----------------------------
    SER-LAW-001: Serialization is deterministic
    SER-LAW-002: Deserialization produces equivalent objects
    SER-LAW-003: No runtime information leaks into serialized form
    """
    
    def serialize_event(self, event_data: dict) -> str:
        """
        Serialize an event to a JSON-compatible string.
        
        Args:
            event_data: Dictionary with event data
            
        Returns:
            JSON string representation
        """
        import json
        
        return json.dumps(event_data, sort_keys=True, default=str)
    
    def deserialize_event(self, serialized: str) -> dict:
        """
        Deserialize an event from a JSON string.
        
        Args:
            serialized: JSON string with event data
            
        Returns:
            Dictionary with deserialized event data
        """
        import json
        
        return json.loads(serialized)
    
    def serialize_to_dict(
        self, obj_data: dict, include_provenance: bool = True
    ) -> dict:
        """
        Convert an object to a dictionary representation.
        
        Args:
            obj_data: Object data to serialize
            include_provenance: Whether to include provenance metadata
            
        Returns:
            Dictionary ready for JSON serialization
        """
        result = dict(obj_data)
        
        if not include_provenance:
            result.pop("provenance", None)
        
        return result
    
    def deserialize_from_dict(
        self, data: dict, expected_type: str | None = None
    ) -> dict:
        """
        Convert a dictionary to the appropriate object representation.
        
        Args:
            data: Dictionary with serialized data
            expected_type: Expected type of object (for validation)
            
        Returns:
            Dictionary ready for object construction
        """
        if expected_type is not None and "type" in data:
            if data["type"] != expected_type:
                raise ValueError(
                    f"Expected type '{expected_type}', got '{data['type']}'"
                )
        
        return dict(data)
    
    def roundtrip_serialize(self, obj_data: dict) -> dict:
        """
        Perform a complete serialization/deserialization cycle.
        
        This verifies that serialization is lossless and deterministic.
        
        Args:
            obj_data: Object data to serialize
            
        Returns:
            Deserialized object data
        """
        import json
        
        # Serialize to string
        serialized = self.serialize_event(obj_data)
        
        # Deserialize back to dict
        deserialized = self.deserialize_event(serialized)
        
        return deserialized
    
    def is_deterministic(self, obj1: dict, obj2: dict) -> bool:
        """
        Check if two objects would serialize identically.
        
        Args:
            obj1: First object data
            obj2: Second object data
            
        Returns:
            True if serialization would produce identical output
        """
        serialized1 = self.serialize_event(obj1)
        serialized2 = self.serialize_event(obj2)
        
        return serialized1 == serialized2