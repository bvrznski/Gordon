# Executive Program Serialization
# ===============================

"""
Executive Program Serialization - Functions for converting programs to/from dict representations.

Serialization enables stable storage and transmission of program state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any


@dataclass(frozen=True)
class ExecutiveProgramSerialization:
    """
    Serialization result for an ExecutiveProgram.
    
    Serialization is deterministic - same inputs always produce the same output.
    It enables stable storage and transmission of program state without runtime artifacts.
    """
    
    # Identity
    serialization_id: str = "exec_serialization_initial"
    """Unique identifier for this serialization."""
    
    schema_version: str = "1.0.0"
    """Schema version used for serialization."""
    
    # Serialization result
    success: bool = True
    """Whether serialization succeeded."""
    
    serialized_data: Dict[str, Any] = field(default_factory=dict)
    """The serialized data (JSON-serializable dict)."""
    
    serialized_size_bytes: int = 0
    """Size of serialized data in bytes."""
    
    # Timestamps
    serialized_at_utc: float = 0.0
    """When serialization was performed (seconds since epoch)."""
    
    deserialized_at_utc: Optional[float] = None
    """When deserialization was completed (if applicable)."""
    
    # Validation after deserialization
    validation_passed_after_deserialization: bool = True
    """Whether the deserialized data passed validation."""
    
    # Integrity
    integrity_digest: Optional[str] = None
    """Hash digest of serialized data for integrity verification."""
    
    @classmethod
    def initial(cls) -> ExecutiveProgramSerialization:
        """
        Create an initial serialization result.
        
        Returns:
            New serialization with default values
        """
        return cls(
            serialization_id="exec_serialization_initial",
            schema_version="1.0.0",
            success=True,
        )
    
    @classmethod
    def success_result(
        cls,
        data: Dict[str, Any],
        size_bytes: int,
        integrity_digest: Optional[str] = None,
    ) -> ExecutiveProgramSerialization:
        """
        Create a successful serialization result.
        
        Args:
            data: The serialized data dict
            size_bytes: Size of the serialized data
            integrity_digest: Optional hash digest for verification
            
        Returns:
            New serialization with success=True
        """
        return cls(
            serialization_id="exec_serialization_success",
            schema_version="1.0.0",
            success=True,
            serialized_data=data,
            serialized_size_bytes=size_bytes,
            integrity_digest=integrity_digest,
            validation_passed_after_deserialization=True,
        )
    
    @classmethod
    def error_result(cls, error_message: str) -> ExecutiveProgramSerialization:
        """
        Create a failed serialization result.
        
        Args:
            error_message: Description of the failure
            
        Returns:
            New serialization with success=False
        """
        return cls(
            serialization_id="exec_serialization_error",
            schema_version="1.0.0",
            success=False,
            serialized_data={},
            serialized_size_bytes=0,
            validation_passed_after_deserialization=True,  # N/A for errors
        )


def serialize_program_to_dict(program: object) -> Dict[str, Any]:
    """
    Serialize an ExecutiveProgram to a dictionary representation.
    
    Args:
        program: The ExecutiveProgram instance
        
    Returns:
        Dictionary with all program data (JSON-serializable)
    """
    import dataclasses
    
    if not hasattr(program, "__dataclass_fields__"):
        raise TypeError("Input must be a dataclass")
    
    result = {}
    for field_info in dataclasses.fields(program):
        value = getattr(program, field_info.name)
        
        # Convert tuples to lists for JSON compatibility
        if isinstance(value, tuple):
            result[field_info.name] = list(value)
        elif hasattr(value, "to_dict"):
            # Handle nested objects with to_dict method
            result[field_info.name] = value.to_dict()
        else:
            result[field_info.name] = value
    
    return result


def deserialize_program_from_dict(
    data: Dict[str, Any],
    program_type: type,
) -> object:
    """
    Deserialize a dictionary back into an ExecutiveProgram instance.
    
    Args:
        data: The serialized dictionary
        program_type: The ExecutiveProgram subclass type
        
    Returns:
        New instance of the specified type
    """
    import dataclasses
    
    if not hasattr(program_type, "__dataclass_fields__"):
        raise TypeError("program_type must be a dataclass")
    
    # Convert lists back to tuples where needed
    field_data = {}
    for field_info in dataclasses.fields(program_type):
        field_name = field_info.name
        value = data.get(field_name)
        
        if isinstance(value, list) and hasattr(field_info, "type"):
            # Try to convert list back to tuple
            try:
                # Handle specific field types
                if field_name in (
                    "goal_bindings",
                    "commitment_bindings",
                    "child_program_ids",
                    "dependency_objective_ids",
                    "satisfaction_criteria_met",
                ):
                    value = tuple(value or [])
                elif isinstance(field_info.default, tuple):
                    value = tuple(value or [])
            except (TypeError, ValueError):
                pass  # Keep as list if conversion fails
        
        field_data[field_name] = value
    
    return program_type(**field_data)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveProgramSerialization",
    "serialize_program_to_dict",
    "deserialize_program_from_dict",
)