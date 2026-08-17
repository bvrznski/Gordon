# Knowledge Model Validation - Phase 6.7
# ======================================

"""
Model Validation: Observational evaluation of model quality and consistency.

Validation evaluates models for internal consistency, coverage, prediction quality,
assumption consistency, and constraint satisfaction without modifying models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# VALIDATION RESULT - Overall validation outcome
# =============================================================================


class ValidationResult(Enum):
    """
    Results of model validation.
    
    Represents the overall quality assessment of a model.
    """
    
    PASSED = "passed"               # All checks passed
    WARNINGS = "warnings"           # Passed but with warnings
    FAILED = "failed"               # Critical issues found


# =============================================================================
# VALIDATION FINDING - Individual check result
# =============================================================================


@dataclass(frozen=True)
class ValidationFinding:
    """
    Record of an individual validation check.
    
    Each finding represents the result of evaluating one aspect of a model.
    
    Fields:
        finding_identity:      Unique identifier for this finding
        check_name:            Name of the validation check performed
        passed:                Whether the check passed
        severity:              Issue severity level
        message:               Description of the issue (if any)
        affected_component:    Reference to affected model component (optional)
    """
    
    # Identity and check info
    finding_identity: str               # Unique ID for this finding
    
    check_name: str                     # Name of the validation check
    
    passed: bool                        # Whether the check passed
    
    severity: str = "info"              # "info", "warning", or "error"
    
    message: str = ""                   # Issue description (if failed)
    
    affected_component: Optional[str] = None  # Affected component ID (optional)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary for serialization."""
        return {
            "finding_identity": self.finding_identity,
            "check_name": self.check_name,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
            "affected_component": self.affected_component,
        }


# =============================================================================
# MODEL VALIDATION - Canonical validation structure
# =============================================================================


@dataclass(frozen=True)
class ModelValidation:
    """
    Canonical representation of model validation in Gordon's knowledge system.
    
    Validation is observational - it never modifies models, only reports on them.
    
    Fields:
        validation_identity:   Unique identifier for this validation session
        evaluated_model:       ID of the model being validated
        performed_checks:      List of checks that were performed
        findings:              Results of all validation checks
        warnings:              Warnings found during validation
        overall_result:        Overall validation outcome
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    validation_identity: str            # Unique ID for this validation session
    
    # Evaluated model reference (required)
    evaluated_model: str                # ID of the validated model
    
    # Validation results (required)
    performed_checks: Tuple[str, ...]   # Names of checks performed
    findings: Tuple[ValidationFinding, ...]  # Individual check results
    
    # Warnings
    warnings: Tuple[str, ...] = field(default_factory=tuple)  # Non-critical issues
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def overall_result(self) -> ValidationResult:
        """Determine the overall validation result."""
        if len(self.findings) == 0:
            return ValidationResult.PASSED
        
        has_errors = any(not f.passed and f.severity == "error" for f in self.findings)
        
        if has_errors:
            return ValidationResult.FAILED
        elif self.warnings or any(not f.passed for f in self.findings):
            return ValidationResult.WARNINGS
        else:
            return ValidationResult.PASSED
    
    @property
    def is_valid(self) -> bool:
        """Check if the model passed validation."""
        return self.overall_result == ValidationResult.PASSED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation to dictionary for serialization."""
        return {
            "validation_identity": self.validation_identity,
            "evaluated_model": self.evaluated_model,
            "performed_checks": list(self.performed_checks),
            "findings": [f.to_dict() for f in self.findings],
            "warnings": list(self.warnings),
            "overall_result": self.overall_result.value if self.overall_result else None,
            "provenance": dict(getattr(self, 'provenance', {})),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelValidation":
        """Create validation from dictionary."""
        findings_data = data.get("findings", [])
        findings = tuple(
            ValidationFinding(
                finding_identity=f.get("finding_identity", str(uuid.uuid4())),
                check_name=f.get("check_name", ""),
                passed=bool(f.get("passed", True)),
                severity=f.get("severity", "info"),
                message=f.get("message", ""),
                affected_component=f.get("affected_component"),
            )
            for f in findings_data
        )
        
        validation = cls(
            validation_identity=data.get("validation_identity", str(uuid.uuid4())),
            evaluated_model=data.get("evaluated_model", ""),
            performed_checks=tuple(data.get("performed_checks", [])),
            findings=findings,
            warnings=tuple(data.get("warnings", [])),
        )
        
        # Add provenance if present
        if hasattr(validation, 'provenance'):
            validation.provenance = dict(data.get("provenance", {}))
        
        return validation
    
    @classmethod
    def create(
        cls,
        evaluated_model: str,
        checks: Optional[List[str]] = None,
        findings: Optional[List[ValidationFinding]] = None,
        warnings: Optional[List[str]] = None,
    ) -> "ModelValidation":
        """
        Create a new model validation record.
        
        Args:
            evaluated_model: ID of the model being validated
            checks: List of check names performed (optional)
            findings: Individual finding results (optional)
            warnings: Warning messages (optional)
            
        Returns:
            A new validation record
        """
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_model=evaluated_model,
            performed_checks=tuple(checks or []),
            findings=tuple(findings or []),
            warnings=tuple(warnings or []),
            provenance={
                "created_at_utc": time.time(),
                "validator_version": "1.0",
            },
        )
    
    def add_finding(
        self,
        finding: ValidationFinding,
    ) -> "ModelValidation":
        """Create a revision with an additional finding."""
        return ModelValidation(
            validation_identity=self.validation_identity,
            evaluated_model=self.evaluated_model,
            performed_checks=self.performed_checks,
            findings=self.findings + (finding,),
            warnings=self.warnings,
            provenance={
                **getattr(self, 'provenance', {}),
                "finding_added_at_utc": time.time(),
                "added_finding": finding.check_name,
            },
        )
    
    def add_warning(
        self,
        warning: str,
    ) -> "ModelValidation":
        """Create a revision with an additional warning."""
        return ModelValidation(
            validation_identity=self.validation_identity,
            evaluated_model=self.evaluated_model,
            performed_checks=self.performed_checks,
            findings=self.findings,
            warnings=self.warnings + (warning,),
            provenance={
                **getattr(self, 'provenance', {}),
                "warning_added_at_utc": time.time(),
                "added_warning": warning,
            },
        )


# =============================================================================
# VALIDATION ENGINE
# =============================================================================


class ValidationEngine:
    """
    Performs validation checks on models.
    
    Ensures validation remains observational and never modifies models.
    """
    
    def __init__(
        self,
        minimum_check_count: int = 3,
    ):
        """
        Initialize the validation engine.
        
        Args:
            minimum_check_count: Minimum number of checks to perform
        """
        self._min_checks = minimum_check_count
    
    def validate(
        self,
        model_id: str,
        checks_to_perform: List[str],
        check_results: Dict[str, Tuple[bool, Optional[str], Optional[str]]],
    ) -> ModelValidation:
        """
        Perform validation on a model.
        
        Args:
            model_id: ID of the model being validated
            checks_to_perform: Names of checks to run
            check_results: Mapping of check names to (passed, message, affected_component)
            
        Returns:
            A validation record with all findings
        """
        findings = []
        warnings = []
        
        for check_name in checks_to_perform:
            if check_name in check_results:
                passed, message, affected = check_results[check_name]
                finding = ValidationFinding(
                    finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
                    check_name=check_name,
                    passed=bool(passed),
                    severity="error" if not passed else "info",
                    message=message or "",
                    affected_component=affected,
                )
                findings.append(finding)
                
                # Add warning if check failed
                if not passed:
                    warnings.append(message or f"Check {check_name} failed")
        
        return ModelValidation.create(
            evaluated_model=model_id,
            checks=checks_to_perform,
            findings=findings,
            warnings=warnings,
        )


__all__ = [
    "ValidationResult",
    "ValidationFinding",
    "ModelValidation",
    "ValidationEngine",
]