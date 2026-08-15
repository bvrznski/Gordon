# Executive State Integrity Types
# ================================

"""
Integrity types for executive state and context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveStateIntegrityAssessment:
    """
    Assessment of executive state integrity.
    
    Validates that the state is well-formed, consistent, and safe to use.
    """
    
    valid: bool = True
    """Whether the state passes all integrity checks."""
    
    identity_valid: bool = True
    """Whether state ID is valid."""
    
    schema_valid: bool = True
    """Whether schema version is recognized."""
    
    revision_valid: bool = True
    """Whether revision number is valid (non-negative, monotonic in history)."""
    
    nested_immutability: bool = True
    """Whether all nested structures are immutable."""
    
    reference_validity: bool = True
    """Whether all references point to valid entities."""
    
    transition_lineage: bool = True
    """Whether transition lineage is intact."""
    
    authority_metadata: bool = True
    """Whether authority metadata is present and valid."""
    
    factuality_preserved: bool = True
    """Whether factuality markers are preserved."""
    
    privacy_preserved: bool = True
    """Whether privacy classifications are preserved."""
    
    provenance_complete: bool = True
    """Whether provenance information is complete."""
    
    boundedness_valid: bool = True
    """Whether bounded collections don't overflow."""
    
    no_runtime_objects: bool = True
    """Whether no live runtime objects are present."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of integrity errors."""
    
    @classmethod
    def valid(cls) -> ExecutiveStateIntegrityAssessment:
        return cls(valid=True)
    
    @classmethod
    def invalid(cls, errors: Tuple[str, ...]) -> ExecutiveStateIntegrityAssessment:
        return cls(valid=False, errors=errors)


@dataclass(frozen=True)
class ExecutiveContextIntegrityAssessment:
    """
    Assessment of executive context integrity.
    """
    
    valid: bool = True
    """Whether the context passes all integrity checks."""
    
    identity_valid: bool = True
    """Whether context ID is valid."""
    
    schema_valid: bool = True
    """Whether schema version is recognized."""
    
    revision_valid: bool = True
    """Whether revision number is valid."""
    
    source_references_valid: bool = True
    """Whether all source references are valid."""
    
    projections_valid: bool = True
    """Whether all projections are valid."""
    
    privacy_preserved: bool = True
    """Whether privacy classifications are preserved."""
    
    provenance_complete: bool = True
    """Whether provenance information is complete."""
    
    boundedness_valid: bool = True
    """Whether bounded collections don't overflow."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of integrity errors."""
    
    @classmethod
    def valid(cls) -> ExecutiveContextIntegrityAssessment:
        return cls(valid=True)
    
    @classmethod
    def invalid(cls, errors: Tuple[str, ...]) -> ExecutiveContextIntegrityAssessment:
        return cls(valid=False, errors=errors)


__all__: Tuple[str, ...] = (
    "ExecutiveStateIntegrityAssessment",
    "ExecutiveContextIntegrityAssessment",
)