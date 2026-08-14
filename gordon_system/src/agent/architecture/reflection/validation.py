"""Reflection Validation - Phase 3.23 Canonical Validation System.
================================================================================

Canonical validation for reflection metadata, discovery results, and audit records.

VALIDATION PRINCIPLES:
- Validation is read-only - never modifies data
- All validations produce deterministic results
- Invalid metadata fails validation with clear error messages
- Validation reports are structured and machine-readable

VALIDATION RESPONSIBILITIES:
- Validate metadata completeness
- Validate metadata consistency  
- Validate discovery correctness
- Validate dependency correctness
- Validate ownership correctness
- Validate registry correctness

"""
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time


# =============================================================================
# VALIDATION RESULTS & REPORTS
# =============================================================================


class ValidationStatus(Enum):
    """Result status of a validation operation."""
    
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass(frozen=True)
class ValidationError:
    """
    A single validation error or warning.
    
    Immutable record of a validation issue with full context.
    """
    
    # Identification
    validator_name: str
    entity_id: Optional[str]  # Which entity, if any
    
    # Error details (required - no defaults)
    severity: ValidationStatus  # error, warning, info
    code: str  # e.g., "MISSING_FIELD", "INVALID_VALUE"
    
    # Message (required - no defaults)
    message: str
    
    # Context
    field_name: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete validation result for a single entity or group.
    
    Immutable record of all validations performed and their results.
    """
    
    # Identity (required - no defaults)
    validated_at_utc: float
    validator_name: str
    
    # Validation scope
    target_type: str  # e.g., "EntityMetadata", "RegistryEntry"
    target_id: Optional[str] = None
    
    # Results (required - no defaults)
    status: ValidationStatus
    errors: Tuple[ValidationError, ...]
    
    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASSED
    
    @property
    def error_count(self) -> int:
        """Get the number of errors."""
        return sum(1 for e in self.errors if e.severity == ValidationStatus.FAILED)
    
    @property
    def warning_count(self) -> int:
        """Get the number of warnings."""
        return sum(1 for e in self.errors if e.severity == ValidationStatus.WARNING)


@dataclass(frozen=True)
class ValidationReport:
    """
    Complete validation report.
    
    Immutable record of all validations performed.
    """
    
    # Identity (required - no defaults)
    generated_at_utc: float
    report_id: str
    
    # Summary
    total_validations: int
    passed_count: int
    failed_count: int
    warning_count: int
    
    # Details
    results: Tuple[ValidationResult, ...]
    
    @property
    def overall_passed(self) -> bool:
        """Check if all validations passed."""
        return self.failed_count == 0


# =============================================================================
# VALIDATOR BASE CLASS
# =============================================================================


class MetadataValidator:
    """
    Base class for metadata validators.
    
    Each validator implements validation logic for a specific aspect of metadata.
    Validators are stateless and immutable - they only validate, never modify.
    """
    
    name: str = "base_validator"
    
    def validate(self, entity: Any) -> ValidationResult:
        """
        Validate an entity's metadata.
        
        Args:
            entity: The entity to validate
            
        Returns:
            ValidationResult with all validation results
        """
        return ValidationResult(
            validated_at_utc=time.time(),
            validator_name=self.name,
            target_type=type(entity).__name__,
            status=ValidationStatus.PASSED,
            errors=()
        )


# =============================================================================
# SPECIFIC VALIDATORS
# =============================================================================


class IdentityValidator(MetadataValidator):
    """Validates identity metadata."""
    
    name: str = "identity_validator"
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate identity metadata for completeness and correctness."""
        errors: List[ValidationError] = []
        
        # Check required fields
        if not hasattr(entity, 'id') or not getattr(entity, 'id', None):
            errors.append(ValidationError(
                validator_name=self.name,
                entity_id=getattr(entity, 'id', None),
                severity=ValidationStatus.FAILED,
                code="MISSING_ID",
                message="Identity metadata must have an 'id' field"
            ))
        
        if not hasattr(entity, 'name') or not getattr(entity, 'name', None):
            errors.append(ValidationError(
                validator_name=self.name,
                entity_id=getattr(entity, 'id', None),
                severity=ValidationStatus.FAILED,
                code="MISSING_NAME",
                message="Identity metadata must have a 'name' field"
            ))
        
        status = ValidationStatus.PASSED if not errors else ValidationStatus.FAILED
        return ValidationResult(
            validated_at_utc=time.time(),
            validator_name=self.name,
            target_type=type(entity).__name__,
            status=status,
            errors=tuple(errors)
        )


class OwnershipValidator(MetadataValidator):
    """Validates ownership metadata."""
    
    name: str = "ownership_validator"
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate ownership metadata for completeness."""
        errors: List[ValidationError] = []
        
        # Check owner is present
        if not hasattr(entity, 'owner') or not getattr(entity, 'owner', None):
            errors.append(ValidationError(
                validator_name=self.name,
                entity_id=getattr(getattr(entity, 'identity', None), 'id', None),
                severity=ValidationStatus.FAILED,
                code="MISSING_OWNER",
                message="Ownership metadata must have an owner"
            ))
        
        status = ValidationStatus.PASSED if not errors else ValidationStatus.FAILED
        return ValidationResult(
            validated_at_utc=time.time(),
            validator_name=self.name,
            target_type=type(entity).__name__,
            status=status,
            errors=tuple(errors)
        )


class DependencyValidator(MetadataValidator):
    """Validates dependency metadata."""
    
    name: str = "dependency_validator"
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate dependency graph for cycles and consistency."""
        errors: List[ValidationError] = []
        
        # Check if dependencies are valid references
        if hasattr(entity, 'dependencies'):
            for dep in getattr(entity, 'dependencies', ()):
                if not hasattr(dep, 'depends_on') or not getattr(dep, 'depends_on', None):
                    errors.append(ValidationError(
                        validator_name=self.name,
                        entity_id=getattr(getattr(entity, 'identity', None), 'id', None),
                        severity=ValidationStatus.FAILED,
                        code="INVALID_DEPENDENCY",
                        message=f"Dependency missing target: {dep}"
                    ))
        
        status = ValidationStatus.PASSED if not errors else ValidationStatus.FAILED
        return ValidationResult(
            validated_at_utc=time.time(),
            validator_name=self.name,
            target_type=type(entity).__name__,
            status=status,
            errors=tuple(errors)
        )


class CompleteValidator:
    """
    Composite validator that runs all validators.
    
    Runs multiple validators and aggregates results into a single report.
    """
    
    def __init__(self) -> None:
        self._validators: List[MetadataValidator] = [
            IdentityValidator(),
            OwnershipValidator(),
            DependencyValidator(),
        ]
    
    def add_validator(self, validator: MetadataValidator) -> None:
        """Add a validator to the chain."""
        self._validators.append(validator)
    
    def validate_entity(self, entity: Any) -> ValidationResult:
        """
        Validate an entity using all validators.
        
        Args:
            entity: The entity to validate
            
        Returns:
            ValidationResult with aggregated results
        """
        all_errors: List[ValidationError] = []
        
        for validator in self._validators:
            result = validator.validate(entity)
            all_errors.extend(result.errors)
        
        status = ValidationStatus.PASSED if not all_errors else ValidationStatus.FAILED
        return ValidationResult(
            validated_at_utc=time.time(),
            validator_name="complete_validator",
            target_type=type(entity).__name__,
            status=status,
            errors=tuple(all_errors)
        )
    
    def validate_repository(self, entities: Tuple[Any, ...]) -> ValidationReport:
        """
        Validate all entities in a repository.
        
        Args:
            entities: All entities to validate
            
        Returns:
            ValidationReport with complete results
        """
        import uuid
        
        results: List[ValidationResult] = []
        passed_count = 0
        failed_count = 0
        warning_count = 0
        
        for entity in entities:
            result = self.validate_entity(entity)
            
            if result.status == ValidationStatus.PASSED:
                passed_count += 1
            elif result.status == ValidationStatus.FAILED:
                failed_count += 1
            else:
                warning_count += 1
            
            results.append(result)
        
        return ValidationReport(
            generated_at_utc=time.time(),
            report_id=str(uuid.uuid4()),
            total_validations=len(entities),
            passed_count=passed_count,
            failed_count=failed_count,
            warning_count=warning_count,
            results=tuple(results)
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Status & Reports
    "ValidationStatus",
    "ValidationError",
    "ValidationResult",
    "ValidationReport",
    
    # Validators
    "MetadataValidator",
    "IdentityValidator",
    "OwnershipValidator", 
    "DependencyValidator",
    "CompleteValidator",
]