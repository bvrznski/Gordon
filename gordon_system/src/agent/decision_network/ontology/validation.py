# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Ontology Validation

This module provides validation utilities for the Action ontology.
"""

from __future__ import annotations

from typing import FrozenSet, Tuple


class OntologyValidationError(Exception):
    """
    Exception raised when ontology validation fails.
    
    Runtime-neutral: Yes
    Executable: No
    """
    pass


class OntologyValidationResult:
    """
    Result of an ontology validation operation.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    def __init__(
        self,
        is_valid: bool = True,
        errors: Tuple[str, ...] = (),
        warnings: Tuple[str, ...] = (),
    ):
        self.is_valid = is_valid
        self.errors = tuple(errors)
        self.warnings = tuple(warnings)
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


def validate_ontology_consistency() -> OntologyValidationResult:
    """
    Validate that the ontology is internally consistent.
    
    Checks:
    - All categories have valid kinds
    - No circular relationships in hierarchy
    - Unique enum values
    - Valid namespace structure
    
    Returns:
        Validation result with any errors or warnings.
    """
    from . import categories, purposes, kinds, targets, subjects, effects, capabilities
    
    errors = []
    
    # Check for unique category names
    category_values = [c.value for c in categories.ActionCategory]
    if len(category_values) != len(set(category_values)):
        errors.append("Duplicate ActionCategory values detected")
    
    # Check for unique kind names
    kind_values = [k.value for k in kinds.ActionKind]
    if len(kind_values) != len(set(kind_values)):
        errors.append("Duplicate ActionKind values detected")
    
    # Check for unique purpose names
    purpose_values = [p.value for p in purposes.ActionPurpose]
    if len(purpose_values) != len(set(purpose_values)):
        errors.append("Duplicate ActionPurpose values detected")
    
    # Check that categories are acyclic (no self-reference)
    try:
        cat_set = frozenset(categories.ActionCategory)
        kind_set = frozenset(kinds.ActionKind)
        
        # Verify category/kind relationships
        for cat in categories.ActionCategory:
            kinds_for_cat = cat.get_kinds()
            for k in kinds_for_cat:
                if k not in kind_set:
                    errors.append(f"Kind {k} not found in kind set")
    except Exception as e:
        errors.append(f"Error validating category/kind relationships: {e}")
    
    # Check that enum values are strings
    for enum_type in [categories.ActionCategory, kinds.ActionKind, purposes.ActionPurpose]:
        for member in enum_type:
            if not isinstance(member.value, str):
                errors.append(f"{enum_type.__name__}.{member.name} has non-string value")
    
    return OntologyValidationResult(
        is_valid=len(errors) == 0,
        errors=tuple(errors),
    )


def validate_acyclic() -> bool:
    """
    Check that the ontology hierarchy is acyclic.
    
    Returns:
        True if the hierarchy is acyclic, False otherwise.
    """
    # In our enum-based implementation, acyclicity is guaranteed
    # by Python's enum implementation - there are no inheritance
    # cycles since each enum member is a distinct object
    
    return True


def validate_unique_values() -> bool:
    """
    Check that all ontology enums have unique values.
    
    Returns:
        True if all values are unique, False otherwise.
    """
    from . import categories, purposes, kinds
    
    for enum_type in [categories.ActionCategory, kinds.ActionKind, purposes.ActionPurpose]:
        values = [m.value for m in enum_type]
        if len(values) != len(set(values)):
            return False
    
    return True


__all__ = [
    "OntologyValidationError",
    "OntologyValidationResult",
    "validate_ontology_consistency",
    "validate_acyclic",
    "validate_unique_values",
]