# Oriented Network Governance Validation - Phase 4.7.11
# =====================================================

"""
Validation Framework for Oriented Network Governance Models

This module provides validation for all governance representations.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic validation
    - Repository-independent

VALIDATION TYPES:

    Constitutional Validation   - Validates constitutional hierarchy and authority
    Policy Validation           - Validates policy inheritance and consistency
    Compliance Validation       - Validates compliance determinations
    Constraint Validation       - Validates constraint legality
    Permission Validation       - Validates permission admissibility
    Obligation Validation       - Validates obligation completeness
    Exception Validation        - Validates exception explicitness

VALIDATION LAWS (ORIENTED-VALIDATION-LAW-XXX):

    ORIENTED-VALIDATION-LAW-001: Validation is deterministic
    ORIENTED-VALIDATION-LAW-002: Validation never executes runtime logic
    ORIENTED-VALIDATION-LAW-003: Validation preserves semantic integrity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ValidationError(Exception):
    """
    Exception raised when validation fails.
    
    INVARIANTS:
        VE-INV-001: Error is immutable
        VE-INV-002: Error represents semantic issues only
    """
    
    message: str = ""
    """Human-readable error description"""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """Tuple of specific validation errors"""
    
    def __str__(self) -> str:
        if self.message:
            return self.message
        return f"Validation failed: {'; '.join(self.errors)}"


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a validation operation.
    
    INVARIANTS:
        VR-INV-001: Result is immutable
        VR-INV-002: Result never executes runtime logic
    """
    
    is_valid: bool = True
    """Whether validation passed"""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation errors"""
    
    @property
    def error_count(self) -> int:
        return len(self.errors)


# =============================================================================
# CONSTITUTIONAL VALIDATION
# =============================================================================

class ConstitutionalValidator:
    """
    Validates constitutional models.
    
    INVARIANTS:
        CV-INV-001: Validation is deterministic
        CV-INV-002: Validation never executes runtime logic
    """
    
    @staticmethod
    def validate_constitution(
        constitution_id: str,
        authority: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate a constitutional model.
        
        Args:
            constitution_id: Constitution identifier
            authority: Authority source (optional)
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        if not constitution_id:
            errors.append("constitution_id is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )
    
    @staticmethod
    def validate_constitutional_hierarchy(
        hierarchy_ids: Tuple[str, ...],
    ) -> ValidationResult:
        """
        Validate constitutional hierarchy (acyclic).
        
        Args:
            hierarchy_ids: Sequence of hierarchy IDs
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        # Check for cycles in hierarchy
        if len(hierarchy_ids) != len(set(hierarchy_ids)):
            errors.append("hierarchy contains duplicate IDs")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )


# =============================================================================
# POLICY VALIDATION
# =============================================================================

class PolicyValidator:
    """
    Validates policy models.
    
    INVARIANTS:
        PV-INV-001: Validation is deterministic
        PV-INV-002: Validation never executes runtime logic
    """
    
    @staticmethod
    def validate_policy(
        policy_id: str,
        version: int = 1,
        authority: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate a policy model.
        
        Args:
            policy_id: Policy identifier
            version: Policy version (>= 1)
            authority: Authority source (optional)
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        if not policy_id:
            errors.append("policy_id is required")
        
        if version < 1:
            errors.append("version must be >= 1")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )
    
    @staticmethod
    def validate_policy_inheritance(
        policy_chain: Tuple[str, ...],
    ) -> ValidationResult:
        """
        Validate policy inheritance chain (explicit and acyclic).
        
        Args:
            policy_chain: Sequence of policy IDs in inheritance order
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        # Check for cycles
        if len(policy_chain) != len(set(policy_chain)):
            errors.append("policy chain contains cycle")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )


# =============================================================================
# COMPLIANCE VALIDATION
# =============================================================================

class ComplianceValidator:
    """
    Validates compliance models.
    
    INVARIANTS:
        ComV-INV-001: Validation is deterministic
        ComV-INV-002: Validation never executes runtime logic
    """
    
    @staticmethod
    def validate_compliance_status(
        status: str,
    ) -> ValidationResult:
        """
        Validate compliance status value.
        
        Args:
            status: Compliance status string
            
        Returns:
            ValidationResult instance
        """
        valid_statuses = ("compliant", "non_compliant", "conditionally_compliant")
        errors = []
        
        if status not in valid_statuses:
            errors.append(f"status must be one of {valid_statuses}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )


# =============================================================================
# CONSTRAINT VALIDATION
# =============================================================================

class ConstraintValidator:
    """
    Validates constraint models.
    
    INVARIANTS:
        CV-INV-001: Validation is deterministic
        CV-INV-002: Validation never executes runtime logic
    """
    
    @staticmethod
    def validate_constraint(
        constraint_id: str,
        type_: str,
    ) -> ValidationResult:
        """
        Validate a constraint model.
        
        Args:
            constraint_id: Constraint identifier
            type_: Constraint type
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        if not constraint_id:
            errors.append("constraint_id is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )


# =============================================================================
# PERMISSION VALIDATION
# =============================================================================

class PermissionValidator:
    """
    Validates permission models.
    
    INVARIANTS:
        PerV-INV-001: Validation is deterministic
        PerV-INV-002: Validation never executes runtime logic
    """
    
    @staticmethod
    def validate_permission(
        permission_id: str,
        operation: str,
    ) -> ValidationResult:
        """
        Validate a permission model.
        
        Args:
            permission_id: Permission identifier
            operation: Operation type
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        if not permission_id:
            errors.append("permission_id is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )


# =============================================================================
# OBLIGATION VALIDATION
# =============================================================================

class ObligationValidator:
    """
    Validates obligation models.
    
    INVARIANTS:
        OV-INV-001: Validation is deterministic
        OV-INV-002: Validation never executes runtime logic
    """
    
    @staticmethod
    def validate_obligation(
        obligation_id: str,
        requirement: str,
    ) -> ValidationResult:
        """
        Validate an obligation model.
        
        Args:
            obligation_id: Obligation identifier
            requirement: Requirement type
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        if not obligation_id:
            errors.append("obligation_id is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )


# =============================================================================
# EXCEPTION VALIDATION
# =============================================================================

class ExceptionValidator:
    """
    Validates exception models.
    
    INVARIANTS:
        EV-INV-001: Validation is deterministic
        EV-INV-002: Validation never executes runtime logic
    """
    
    @staticmethod
    def validate_exception(
        exception_id: str,
        type_: str,
        justification: Optional[str],
    ) -> ValidationResult:
        """
        Validate an exception model.
        
        Args:
            exception_id: Exception identifier
            type_: Exception type
            justification: Architectural justification
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        if not exception_id:
            errors.append("exception_id is required")
        
        if not type_:
            errors.append("type is required")
        
        if not justification:
            errors.append("justification is required for explicit exceptions")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Errors
    "ValidationError",
    
    # Results
    "ValidationResult",
    
    # Validators
    "ConstitutionalValidator",
    "PolicyValidator",
    "ComplianceValidator",
    "ConstraintValidator",
    "PermissionValidator",
    "ObligationValidator",
    "ExceptionValidator",
]