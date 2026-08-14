# Gordon Core - Validation, Verification & Certification Architecture
# ================================================================================
# Phase 3.24 Canonical Architecture
#
# VALIDATION PRINCIPLES:
#     - Validation is read-only - never modifies data
#     - All validations produce deterministic results
#     - Invalid findings are structured and actionable
#     - Evidence is preserved for all validation operations
#
# ARCHITECTURAL BOUNDARIES:
#     - Validation: Determines internal correctness (Core concern)
#     - Verification: Determines conformance to contracts (Implementation concern)
#     - Certification: Determines readiness for production (Deployment concern)
#
# RESPONSIBILITIES:
#     - One canonical validation architecture throughout repository
#     - No subsystem shall implement independent validation framework
#     - All validation results are immutable findings with evidence

"""
Canonical Validation, Verification & Certification Architecture for Gordon Core.

This module establishes the single source of truth for all validation,
verification, and certification operations across the entire repository.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import time

# =============================================================================
# VALIDATION SEVERITY ENUMERATION
# =============================================================================


class ValidationSeverity(Enum):
    """
    Canonical validation finding severities.
    
    SEVERITIES:
        ERROR       - Validation failed, operation must be rejected
        WARNING     - Operation may proceed but with caution
        INFO        - Informational finding, no action required
        NOTICE      - Notice of interest, should be reviewed
        CRITICAL    - Critical failure, system may be compromised
    """
    
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    NOTICE = "notice"
    CRITICAL = "critical"


# =============================================================================
# VALIDATION FINDING
# =============================================================================


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding with full context.
    
    FINDING PRINCIPLES:
        - Findings are immutable once created
        - Each finding has exactly one severity
        - All findings include evidence and traceability
    
    INVARIANTS:
        FND-001: Finding is immutable once created
        FND-002: Each finding has exactly one severity
        FND-003: ERROR/CRITICAL findings indicate validation failure
        FND-004: All findings include source traceability
    """
    
    # Identity - immutable
    finding_id: str = field(default_factory=lambda: f"fnd_{time.time_ns()}")
    
    # Category (what was validated)
    category: str  # e.g., "identity", "scope", "dependency", "contract"
    
    # Validation details
    check_name: str  # What specific check was performed?
    severity: ValidationSeverity = ValidationSeverity.ERROR
    
    # Result
    valid: bool = True
    message: Optional[str] = None
    
    # Context
    entity_id: Optional[str] = None  # Which entity was validated
    field_path: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    
    # Evidence & Traceability
    rule_id: Optional[str] = None  # Which rule was violated?
    timestamp_utc: float = field(default_factory=time.time)
    source_validator: str = "unknown"
    
    @property
    def is_error(self) -> bool:
        """Check if this finding represents an error or critical issue."""
        return self.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
    
    @property
    def is_warning(self) -> bool:
        """Check if this finding represents a warning."""
        return self.severity == ValidationSeverity.WARNING
    
    @property
    def is_info(self) -> bool:
        """Check if this finding is informational."""
        return self.severity in (ValidationSeverity.INFO, ValidationSeverity.NOTICE)


# =============================================================================
# VALIDATION RESULT
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete validation result for a target.
    
    Validation produces structured findings, not just Boolean results.
    
    INVARIANTS:
        VAL-001: Validation has exactly one overall validity outcome
        VAL-002: Findings include all validation details
        VAL-003: ERROR/CRITICAL findings indicate validation failure
        VAL-004: All validation results are immutable
    """
    
    # Identity - immutable
    result_id: str = field(default_factory=lambda: f"val_{time.time_ns()}")
    target_type: str  # e.g., "Package", "Module", "Component"
    target_id: Optional[str] = None
    
    # Validation scope
    validation_scope: str = "default"  # e.g., "runtime", "architecture", "contract"
    
    # Overall result - computed from findings
    overall_validity: bool = False  # True only if no ERROR/CRITICAL findings
    
    # Findings (all individual checks)
    findings: Tuple[ValidationFinding, ...] = field(default_factory=tuple)
    
    # Validation context
    validated_at_utc: float = field(default_factory=time.time)
    validator_name: str = "unknown"
    
    @classmethod
    def valid(
        cls,
        target_type: str,
        target_id: Optional[str] = None,
        validation_scope: str = "default",
        findings: Optional[Tuple[ValidationFinding, ...]] = None,
        validator_name: str = "unknown",
    ) -> "ValidationResult":
        """Create a valid validation result."""
        return cls(
            target_type=target_type,
            target_id=target_id,
            validation_scope=validation_scope,
            overall_validity=True,
            findings=findings or tuple(),
            validated_at_utc=time.time(),
            validator_name=validator_name,
        )
    
    @classmethod
    def invalid(
        cls,
        target_type: str,
        target_id: Optional[str] = None,
        validation_scope: str = "default",
        primary_failure: str = "Validation failed",
        secondary_findings: Optional[Tuple[ValidationFinding, ...]] = None,
    ) -> "ValidationResult":
        """Create an invalid validation result."""
        return cls(
            target_type=target_type,
            target_id=target_id,
            validation_scope=validation_scope,
            overall_validity=False,
            findings=tuple([
                ValidationFinding(
                    finding_id="primary",
                    category="validation",
                    check_name="overall_validation",
                    severity=ValidationSeverity.ERROR,
                    valid=False,
                    message=primary_failure,
                    timestamp_utc=time.time(),
                ),
            ]) + (secondary_findings or tuple()),
        )
    
    @property
    def error_count(self) -> int:
        """Get the number of ERROR/CRITICAL findings."""
        return sum(1 for f in self.findings if f.is_error)
    
    @property
    def warning_count(self) -> bool:
        """Get the number of WARNING findings."""
        return sum(1 for f in self.findings if f.is_warning)
    
    @property
    def info_count(self) -> int:
        """Get the number of INFO/NOTICE findings."""
        return sum(1 for f in self.findings if f.is_info)
    
    @classmethod
    def warning_result(
        cls,
        target_type: str,
        target_id: Optional[str] = None,
        validation_scope: str = "default",
        message: Optional[str] = None,
    ) -> "ValidationResult":
        """Create a warning validation result."""
        return cls(
            target_type=target_type,
            target_id=target_id,
            validation_scope=validation_scope,
            overall_validity=True,
            findings=tuple([
                ValidationFinding(
                    finding_id="warning",
                    category="validation",
                    check_name="overall_validation",
                    severity=ValidationSeverity.WARNING,
                    valid=True,
                    message=message or "Warning issued",
                    timestamp_utc=time.time(),
                ),
            ]),
            validated_at_utc=time.time(),
            validator_name="unknown",
        )


# =============================================================================
# VALIDATION REPORT
# =============================================================================


@dataclass(frozen=True)
class ValidationReport:
    """
    Complete validation report with aggregated results.
    
    INVARIANTS:
        REP-001: Report is immutable once generated
        REP-002: All sub-results are included
        REP-003: Summary statistics are accurate
    """
    
    # Identity - immutable
    report_id: str = field(default_factory=lambda: f"rpt_{time.time_ns()}")
    generated_at_utc: float = field(default_factory=time.time)
    
    # Scope
    report_type: str  # e.g., "repository", "package", "module"
    validated_entity_count: int
    
    # Summary statistics
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    
    # Results
    results: Tuple[ValidationResult, ...] = field(default_factory=tuple)
    
    @property
    def overall_passed(self) -> bool:
        """Check if all validations passed."""
        return self.failed_count == 0
    
    @property
    def total_findings(self) -> int:
        """Get the total number of findings across all results."""
        return sum(len(r.findings) for r in self.results)
    
    @property
    def error_findings(self) -> List[ValidationFinding]:
        """Get all ERROR/CRITICAL findings."""
        errors = []
        for result in self.results:
            errors.extend(f for f in result.findings if f.is_error)
        return errors
    
    @property
    def warning_findings(self) -> List[ValidationFinding]:
        """Get all WARNING findings."""
        warnings = []
        for result in self.results:
            warnings.extend(f for f in result.findings if f.is_warning)
        return warnings


# =============================================================================
# VALIDATOR BASE CLASS
# =============================================================================


class ValidatorBase:
    """
    Base class for all validators.
    
    VALIDATOR PRINCIPLES:
        - Validators are stateless (except configuration)
        - All validation is read-only
        - Results are deterministic and reproducible
    """
    
    name: str = "validator_base"
    description: str = "Base validator class"
    
    def validate(self, target: Any) -> ValidationResult:
        """
        Validate a target entity.
        
        Args:
            target: The entity to validate
            
        Returns:
            ValidationResult with all validation results
        """
        return ValidationResult.valid(
            target_type=type(target).__name__,
            validator_name=self.name,
        )
    
    def validate_batch(self, targets: Tuple[Any, ...]) -> ValidationReport:
        """
        Validate multiple targets.
        
        Args:
            targets: All entities to validate
            
        Returns:
            ValidationReport with aggregated results
        """
        results = []
        passed = 0
        failed = 0
        
        for target in targets:
            result = self.validate(target)
            if result.overall_validity:
                passed += 1
            else:
                failed += 1
            results.append(result)
        
        return ValidationReport(
            report_type=self.name,
            validated_entity_count=len(targets),
            passed_count=passed,
            failed_count=failed,
            results=tuple(results),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Severity enum
    "ValidationSeverity",
    
    # Result types
    "ValidationFinding",
    "ValidationResult",
    "ValidationReport",
    
    # Base classes
    "ValidatorBase",
]