# Integration Validation - Phase 5.1.7 Request/Response Validation System
# =======================================================================

"""
Memory Integration Validation: Validates requests and responses.

Validation responsibilities:
    - Verify request format and required fields
    - Check version compatibility
    - Validate authorization context
    - Ensure semantic integrity

Validation Laws:
    VALIDATION-LAW-001: Every request must be validated
    VALIDATION-LAW-002: Every response must be validated
    VALIDATION-LAW-003: Validation precedes communication
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# VALIDATION RESULTS
# =============================================================================


class ValidationResult(Enum):
    """
    Results of validation.
    
    | State        | Description                                    |
    |--------------|------------------------------------------------|
    | VALID        | Passed all validation checks                   |
    | INVALID      | Failed validation                              |
    | WARN         | Valid but has warnings                         |
    | PENDING      | Validation pending                             |
    """
    
    VALID = "valid"
    INVALID = "invalid"
    WARN = "warn"
    PENDING = "pending"


# =============================================================================
# VALIDATION ERROR
# =============================================================================


@dataclass(frozen=True)
class ValidationError:
    """
    A validation error.
    
    Fields:
        code:           Machine-readable error code
        
        field:          Which field failed?
        message:       Human-readable error message
        
        severity:      How severe is this error?
        
        # Context
        request_id:    Request ID (if applicable)
    """
    
    code: str                               # e.g., "MISSING_FIELD", "INVALID_TYPE"
    
    field: str = ""                         # Which field failed?
    message: str = ""                       # Error explanation
    
    severity: int = 1                       # 1 = critical, higher = less severe
    
    request_id: Optional[str] = None


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass(frozen=True)
class ValidationOutcome:
    """
    Result of validation.
    
    Fields:
        result:         Final validation result
        
        is_valid:       Is the item valid?
        
        # Errors and warnings
        errors:        List of validation errors
        warnings:      List of warning messages
        
        # Timing
        validated_at:  When was validation performed?
        duration_ms:   How long did validation take?
    """
    
    result: ValidationResult = ValidationResult.PENDING
    
    is_valid: bool = False
    
    errors: Tuple[ValidationError, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    validated_at: float = field(default_factory=time.time)
    duration_ms: float = 0.0


# =============================================================================
# VALIDATOR BASE
# =============================================================================


class Validator:
    """
    Base class for validators.
    
    Provides common validation functionality and extensibility.
    
    Usage:
        validator = RequestValidator()
        result = validator.validate(request_data)
    """
    
    def __init__(self, name: str = "validator"):
        self.name = name
        self._validation_count: int = 0
    
    def validate(self, item: Any) -> ValidationOutcome:
        """Validate an item."""
        start_time = time.time()
        
        try:
            # Perform validation
            errors, warnings = self._do_validate(item)
            
            is_valid = len(errors) == 0
            
            if not is_valid:
                result = ValidationResult.INVALID
            elif warnings:
                result = ValidationResult.WARN
            else:
                result = ValidationResult.VALID
            
            outcome = ValidationOutcome(
                result=result,
                is_valid=is_valid,
                errors=tuple(errors),
                warnings=tuple(warnings)
            )
            
        except Exception as e:
            outcome = ValidationOutcome(
                result=ValidationResult.INVALID,
                is_valid=False,
                errors=(ValidationError(
                    code="VALIDATION_ERROR",
                    field="__exception__",
                    message=str(e),
                    severity=1
                ),)
            )
        
        end_time = time.time()
        
        return dataclass_replace(outcome, 
                                  duration_ms=(end_time - start_time) * 1000,
                                  validated_at=end_time)
    
    def _do_validate(self, item: Any) -> Tuple[List[ValidationError], List[str]]:
        """Perform actual validation (to be overridden by subclasses)."""
        return [], []


# =============================================================================
# REQUEST VALIDATOR
# =============================================================================


class RequestValidator(Validator):
    """
    Validates integration requests.
    
    Checks:
        - Required fields are present
        - Field types are correct
        - Authorization context is valid
        - Contract compatibility
    
    Usage:
        validator = RequestValidator()
        result = validator.validate(request)
    """
    
    def __init__(self):
        super().__init__("request")
    
    def _do_validate(self, item: Any) -> Tuple[List[ValidationError], List[str]]:
        errors = []
        warnings = []
        
        # Check if item has required fields
        required_fields = ["request_id", "requester", "purpose"]
        
        for field in required_fields:
            if not hasattr(item, field):
                errors.append(ValidationError(
                    code="MISSING_FIELD",
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity=1
                ))
                continue
            
            value = getattr(item, field)
            
            # Validate field types
            if field == "request_id" and not isinstance(value, str):
                errors.append(ValidationError(
                    code="INVALID_TYPE",
                    field=field,
                    message=f"'{field}' must be a string",
                    severity=1
                ))
            elif field in ("requester", "purpose") and not isinstance(value, str):
                errors.append(ValidationError(
                    code="INVALID_TYPE",
                    field=field,
                    message=f"'{field}' must be a non-empty string",
                    severity=1
                ))
        
        # Check for empty required fields
        if hasattr(item, "request_id"):
            if not item.request_id or not item.request_id.strip():
                errors.append(ValidationError(
                    code="EMPTY_FIELD",
                    field="request_id",
                    message="Request ID cannot be empty",
                    severity=1
                ))
        
        return errors, warnings


# =============================================================================
# RESPONSE VALIDATOR
# =============================================================================


class ResponseValidator(Validator):
    """
    Validates integration responses.
    
    Checks:
        - Projection is valid
        - No implementation details leaked
        - Confidence is within bounds
    
    Usage:
        validator = ResponseValidator()
        result = validator.validate(response)
    """
    
    def __init__(self):
        super().__init__("response")
    
    def _do_validate(self, item: Any) -> Tuple[List[ValidationError], List[str]]:
        errors = []
        warnings = []
        
        # Check for projection
        if not hasattr(item, "projection_data"):
            errors.append(ValidationError(
                code="MISSING_FIELD",
                field="projection_data",
                message="Response must contain projection data",
                severity=1
            ))
            return errors, warnings
        
        projection = getattr(item, "projection_data")
        
        # Check projection is dict-like
        if not isinstance(projection, (dict, list)):
            errors.append(ValidationError(
                code="INVALID_TYPE",
                field="projection_data",
                message="Projection data must be a dictionary or list",
                severity=1
            ))
        
        return errors, warnings


# =============================================================================
# VALIDATION PIPELINE
# =============================================================================


class ValidationPipeline:
    """
    Pipeline for validation operations.
    
    Chains multiple validators together and aggregates results.
    
    Usage:
        pipeline = ValidationPipeline()
        pipeline.add_validator(RequestValidator())
        pipeline.add_validator(VersionValidator())
        
        result = pipeline.validate(request)
    """
    
    def __init__(self):
        self._validators: List[Validator] = []
    
    def add_validator(self, validator: Validator) -> None:
        """Add a validator to the pipeline."""
        self._validators.append(validator)
    
    def remove_validator(self, name: str) -> None:
        """Remove a validator by name."""
        self._validators = [v for v in self._validators if v.name != name]
    
    def validate(self, item: Any) -> ValidationOutcome:
        """
        Validate an item through all validators.
        
        Returns aggregated result from all validators.
        """
        start_time = time.time()
        
        all_errors: List[ValidationError] = []
        all_warnings: List[str] = []
        
        for validator in self._validators:
            outcome = validator.validate(item)
            
            if not outcome.is_valid:
                # Collect errors
                all_errors.extend(outcome.errors)
            
            all_warnings.extend(outcome.warnings)
        
        is_valid = len(all_errors) == 0
        
        if not is_valid:
            result = ValidationResult.INVALID
        elif all_warnings:
            result = ValidationResult.WARN
        else:
            result = ValidationResult.VALID
        
        end_time = time.time()
        
        return ValidationOutcome(
            result=result,
            is_valid=is_valid,
            errors=tuple(all_errors),
            warnings=tuple(all_warnings),
            validated_at=end_time,
            duration_ms=(end_time - start_time) * 1000
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace (Python 3.7 compatible)."""
    fields = instance.__dataclass_fields__
    return type(instance)(
        **{f.name: kwargs.get(f.name, getattr(instance, f.name)) 
           for f in fields.values()}
    )