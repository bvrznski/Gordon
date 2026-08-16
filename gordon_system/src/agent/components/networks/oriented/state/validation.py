# Oriented Network State Validation - Phase 4.7.4
# ================================================

"""
Validation framework for Oriented Network State types.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic validation
    - Repository-independent

VALIDATION TYPES:
    - StateValidator: Main validator class
    - Validation functions for each state type
    - ValidationError: Exception type for validation failures
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


@dataclass(frozen=True)
class StateValidationError(Exception):
    """
    Exception raised when state validation fails.
    
    SEMANTIC ROLE:
        - Represents semantic validation failure
        - Never contains runtime error details
        
    INVARIANTS:
        SV-INV-001: Error is immutable
        SV-INV-002: Error represents semantic issues only
    """
    
    message: str = ""
    """Human-readable error description"""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """Tuple of specific validation errors"""
    
    state_id: Optional[str] = None
    """State ID being validated (if known)"""
    
    def __str__(self) -> str:
        if self.message:
            return self.message
        return f"Validation failed: {'; '.join(self.errors)}"


class StateValidator:
    """
    Validator for Oriented Network State types.
    
    SEMANTIC ROLE:
        - Validates state structure and constraints
        - Never executes runtime logic
        
    VALIDATION INVARIANTS:
        V-INV-001: Deterministic (same input = same output)
        V-INV-002: Semantic validation only
        V-INV-003: No runtime dependencies
    """
    
    @staticmethod
    def validate_state_structure(data: Dict[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate basic state structure.
        
        Args:
            data: State data to validate
            
        Returns:
            (is_valid, errors) tuple
        """
        errors = []
        
        # Check required fields
        if "state_id" not in data or not data["state_id"]:
            errors.append("state_id is required")
        
        # Validate revision
        if "revision" in data and data["revision"] < 1:
            errors.append("revision must be >= 1")
        
        # Validate version
        if "version" in data and data["version"] < 1:
            errors.append("version must be >= 1")
        
        return len(errors) == 0, tuple(errors)
    
    @staticmethod
    def validate_state_composition(
        state_id: str,
        composition_ids: Tuple[str, ...],
    ) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate state composition structure.
        
        Args:
            state_id: State ID being validated
            composition_ids: IDs of composed elements
            
        Returns:
            (is_valid, errors) tuple
        """
        errors = []
        
        # Check for duplicate IDs in composition
        if len(composition_ids) != len(set(composition_ids)):
            errors.append("duplicate IDs in composition")
        
        return len(errors) == 0, tuple(errors)
    
    @staticmethod
    def validate_state_lineage(
        state_id: str,
        lineage: Tuple[str, ...],
    ) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate state lineage structure.
        
        Args:
            state_id: State ID being validated
            lineage: Lineage tuple
            
        Returns:
            (is_valid, errors) tuple
        """
        errors = []
        
        # Check for cycles in lineage
        if state_id in lineage:
            errors.append("lineage contains cycle")
        
        return len(errors) == 0, tuple(errors)
    
    @staticmethod
    def validate_state_provenance(
        provenance: Dict[str, Any],
    ) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate state provenance structure.
        
        Args:
            provenance: Provenance data
            
        Returns:
            (is_valid, errors) tuple
        """
        errors = []
        
        # Check that derived_from is a tuple of strings
        if "derived_from" in provenance:
            if not isinstance(provenance["derived_from"], (tuple, list)):
                errors.append("derived_from must be a tuple or list")
        
        return len(errors) == 0, tuple(errors)


def validate_state_structure(data: Dict[str, Any]) -> Tuple[bool, Tuple[str, ...]]:
    """
    Validate basic state structure.
    
    Args:
        data: State data to validate
        
    Returns:
        (is_valid, errors) tuple
    """
    return StateValidator.validate_state_structure(data)


def validate_state_composition(
    state_id: str,
    composition_ids: Tuple[str, ...],
) -> Tuple[bool, Tuple[str, ...]]:
    """
    Validate state composition structure.
    
    Args:
        state_id: State ID being validated
        composition_ids: IDs of composed elements
        
    Returns:
        (is_valid, errors) tuple
    """
    return StateValidator.validate_state_composition(state_id, composition_ids)


def validate_state_lineage(
    state_id: str,
    lineage: Tuple[str, ...],
) -> Tuple[bool, Tuple[str, ...]]:
    """
    Validate state lineage structure.
    
    Args:
        state_id: State ID being validated
        lineage: Lineage tuple
        
    Returns:
        (is_valid, errors) tuple
    """
    return StateValidator.validate_state_lineage(state_id, lineage)


def validate_state_provenance(
    provenance: Dict[str, Any],
) -> Tuple[bool, Tuple[str, ...]]:
    """
    Validate state provenance structure.
    
    Args:
        provenance: Provenance data
        
    Returns:
        (is_valid, errors) tuple
    """
    return StateValidator.validate_state_provenance(provenance)


__all__ = [
    "StateValidationError",
    "StateValidator",
    "validate_state_structure",
    "validate_state_composition",
    "validate_state_lineage",
    "validate_state_provenance",
]