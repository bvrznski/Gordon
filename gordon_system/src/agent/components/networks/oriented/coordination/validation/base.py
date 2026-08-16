# Oriented Network Coordination Validation Base Interface
# =======================================================

"""
Base interface for coordination validation (Phase 4.7.5)

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-028 through 039: Validation and consistency laws
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


# =============================================================================
# VALIDATION RESULT TYPES
# =============================================================================

class ValidationResult(str):
    """Validation result status."""
    
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    PENDING = "pending"


# =============================================================================
# BASE VALIDATOR INTERFACE
# =============================================================================

class BaseValidator(ABC):
    """
    Abstract base class for coordination validation.
    
    ARCHITECTURAL PRINCIPLES:
        V-INV-001: Validation is deterministic (same input = same output)
        V-INV-002: Validation never mutates the validated object
        V-INV-003: Validation produces explicit error messages
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-029: Every coordination contract shall be validatable.
        ORIENTED-COORDINATION-LAW-039: Coordination shall remain independent from runtime implementation.
    """
    
    @abstractmethod
    def validate(self, obj: Any) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate the given object against coordination rules.
        
        Args:
            obj: Object to validate (coordination contract or lifecycle state)
            
        Returns:
            (is_valid, list_of_errors) tuple
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_errors(self, obj: Any) -> Tuple[str, ...]:
        """
        Get validation errors without boolean result.
        
        Args:
            obj: Object to validate
            
        Returns:
            Tuple of error messages (empty if valid)
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def rules_applied(self) -> Tuple[str, ...]:
        """Return names of validation rules applied."""
        raise NotImplementedError


# =============================================================================
# HIERARCHY VALIDATOR
# =============================================================================

class HierarchyValidator(BaseValidator):
    """
    Validates intentional hierarchy structure.
    
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-014: Hierarchy shall remain acyclic.
        
    HIERARCHY STRUCTURE:
        Purpose (level 0)
            ↓
        Mission (level 1)
            ↓  
        Goal (level 2)
            ↓
        Objective (level 3)
            ↓
        Task (level 4)
    """
    
    @abstractmethod
    def validate_acyclic(self, hierarchy: Dict[str, Any]) -> bool:
        """Validate that the hierarchy is acyclic."""
        raise NotImplementedError
    
    @abstractmethod
    def validate_level_consistency(
        self, 
        concept_type: str, 
        level: int
    ) -> bool:
        """Validate that a concept type appears at its expected level."""


# =============================================================================
# OWNERSHIP VALIDATOR  
# =============================================================================

class OwnershipValidator(BaseValidator):
    """
    Validates ownership contracts.
    
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-010: Ownership shall never overlap.
        
    OWNERSHIP RULES:
        - Every coordinated concept has exactly one owner
        - Owner references must be explicit and unambiguous
        - No circular ownership relationships
    """
    
    @abstractmethod
    def validate_unique_owner(self, concept_id: str) -> bool:
        """Validate that a concept has exactly one owner."""
        raise NotImplementedError
    
    @abstractmethod  
    def validate_no_overlap(self, owners: Dict[str, Any]) -> Tuple[bool, ...]:
        """Validate that ownership domains don't overlap."""


# =============================================================================
# REFERENCE VALIDATOR
# =============================================================================

class ReferenceValidator(BaseValidator):
    """
    Validates reference relationships.
    
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-013: Every reference shall be explicit.
        
    REFERENCE RULES:
        - All references must be syntactically valid identifiers
        - Referenced targets must exist in external systems
        - References must preserve semantic compatibility
    """
    
    @abstractmethod
    def validate_reference_syntax(self, ref_id: str) -> bool:
        """Validate reference ID syntax."""
        raise NotImplementedError
    
    @abstractmethod
    def validate_reference_compatibility(
        self, 
        source_type: str, 
        target_type: str
    ) -> bool:
        """Validate that reference is semantically compatible."""


# =============================================================================
# SERIALIZATION VALIDATOR
# =============================================================================

class SerializationValidator(BaseValidator):
    """
    Validates serialization format.
    
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-028: Every coordination contract shall be serializable.
        
    SERIALIZATION RULES:
        - Deterministic output (same input = same output)
        - All required fields present
        - No runtime-specific data included
    """
    
    @abstractmethod
    def validate_to_dict(self, obj: Any) -> bool:
        """Validate serialization to dictionary."""
        raise NotImplementedError
    
    @abstractmethod
    def validate_from_dict(self, data: Dict[str, Any]) -> bool:
        """Validate deserialization from dictionary."""
        raise NotImplementedError


# =============================================================================
# CONSISTENCY VALIDATOR
# =============================================================================

class ConsistencyValidator(BaseValidator):
    """
    Validates semantic consistency across coordination concepts.
    
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-029: Every coordination contract shall be validatable.
        
    CONSISTENCY RULES:
        - All lifecycle states are consistent with coordination status
        - Hierarchy relationships are preserved
        - References point to existing external concepts
    """
    
    @abstractmethod
    def validate_lifecycle_consistency(
        self, 
        state: Any, 
        status: Any
    ) -> bool:
        """Validate consistency between lifecycle state and coordination status."""
        raise NotImplementedError
    
    @abstractmethod
    def validate_hierarchy_preservation(
        self, 
        hierarchy: Dict[str, Any]
    ) -> bool:
        """Validate that hierarchy relationships are preserved."""
        raise NotImplementedError


__all__ = [
    # Result types
    "ValidationResult",
    # Base interface
    "BaseValidator",
    # Specialized validators
    "HierarchyValidator",
    "OwnershipValidator", 
    "ReferenceValidator",
    "SerializationValidator",
    "ConsistencyValidator",
]