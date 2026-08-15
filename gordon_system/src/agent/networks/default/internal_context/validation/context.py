# Internal Context Validation Model
# =================================

"""
Validation models for internal context.

Provides strict validation of contexts and projections without runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """
    Report of validation results for a context or projection.
    
    PROPERTIES:
        • is_valid: Whether all checks passed
        • errors: List of error messages (empty if valid)
        • warnings: List of warning messages
        • checks_performed: Number of validation checks that ran
    """
    
    is_valid: bool = True
    """Whether the context/projection passed all validation checks."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation error messages."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation warning messages."""
    
    checks_performed: int = 0
    """Number of validation checks that were executed."""
    
    @classmethod
    def valid(cls) -> ValidationReport:
        """Create a valid report."""
        return cls(is_valid=True, checks_performed=1)
    
    @classmethod
    def with_error(cls, error: str) -> ValidationReport:
        """Create a report with one error."""
        return cls(
            is_valid=False,
            errors=(error,),
            checks_performed=1,
        )
    
    @classmethod
    def with_errors(cls, errors: Tuple[str, ...]) -> ValidationReport:
        """Create a report with multiple errors."""
        return cls(
            is_valid=False,
            errors=errors,
            checks_performed=len(errors),
        )
    
    @classmethod
    def from_checks(
        cls,
        results: Tuple[bool, str],  # (passed, message)
    ) -> ValidationReport:
        """Create a report from individual check results."""
        errors = tuple(msg for passed, msg in results if not passed)
        return cls(
            is_valid=len(errors) == 0,
            errors=errors,
            checks_performed=len(results),
        )
    
    def merge(self, other: ValidationReport) -> ValidationReport:
        """Merge another report into this one."""
        return ValidationReport(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            checks_performed=self.checks_performed + other.checks_performed,
        )


@dataclass(frozen=True, slots=True)
class InternalContextValidator:
    """
    Validator for internal context instances.
    
    Validates without runtime behavior - only structural and semantic checks.
    """
    
    strict_mode: bool = False
    """Whether to fail on any validation issue."""
    
    @classmethod
    def create(cls, strict_mode: bool = False) -> InternalContextValidator:
        """Create a new validator instance."""
        return cls(strict_mode=strict_mode)
    
    def validate_context(self, context: "InternalContext") -> ValidationReport:
        """
        Validate an InternalContext instance.
        
        Returns a report of validation results. Does NOT mutate the context
        or perform any runtime operations.
        """
        checks = []
        
        # Check context_id is not empty
        if not context.context_id:
            checks.append((False, "context_id must not be empty"))
        else:
            checks.append((True, "context_id present"))
        
        # Check revision is non-negative
        if context.revision < 0:
            checks.append((False, "revision must be non-negative"))
        else:
            checks.append((True, "revision valid"))
        
        # Check created_at_utc is present
        if not context.created_at_utc:
            checks.append((False, "created_at_utc must be present"))
        else:
            checks.append((True, "created_at_utc present"))
        
        # Check purpose is valid (not empty)
        if not context.purpose:
            checks.append((False, "purpose must not be empty"))
        else:
            checks.append((True, "purpose present"))
        
        # Validate confidence score
        conf = context.confidence.overall_confidence
        if not (0.0 <= conf <= 1.0):
            checks.append((False, f"confidence {conf} out of range [0.0, 1.0]"))
        else:
            checks.append((True, "confidence in valid range"))
        
        # Validate completeness status
        comp_status = context.completeness.status
        valid_statuses = ("complete", "sufficient", "partial", "insufficient", "invalid")
        if comp_status not in valid_statuses:
            checks.append((False, f"completeness status '{comp_status}' is invalid"))
        else:
            checks.append((True, "completeness status valid"))
        
        # Validate freshness status
        fresh_status = context.freshness.status
        valid_fresh = ("fresh", "recent", "stale", "expired")
        if fresh_status not in valid_fresh:
            checks.append((False, f"freshness status '{fresh_status}' is invalid"))
        else:
            checks.append((True, "freshness status valid"))
        
        return ValidationReport.from_checks(tuple(checks))
    
    def validate_request(self, request: "InternalContextRequest") -> ValidationReport:
        """Validate an InternalContextRequest instance."""
        checks = []
        
        # Check purpose is not empty
        if not request.purpose:
            checks.append((False, "purpose must not be empty"))
        else:
            checks.append((True, "purpose present"))
        
        # Validate minimum confidence
        min_conf = request.minimum_confidence
        if not (0.0 <= min_conf <= 1.0):
            checks.append((False, f"minimum_confidence {min_conf} out of range"))
        else:
            checks.append((True, "minimum_confidence valid"))
        
        # Check maximum_total_items is positive
        if request.maximum_total_items <= 0:
            checks.append((False, "maximum_total_items must be positive"))
        else:
            checks.append((True, "maximum_total_items valid"))
        
        return ValidationReport.from_checks(tuple(checks))


def validate_internal_context(context: "InternalContext") -> bool:
    """Convenience function to validate a context (returns boolean)."""
    validator = InternalContextValidator()
    report = validator.validate_context(context)
    return report.is_valid