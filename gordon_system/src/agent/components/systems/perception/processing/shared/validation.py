# Perception Processing Validation - Phase 5.2.2
# ==============================================

"""
Validation: Verifies processing correctness before publication.

Validation ensures outputs conform to expected contracts and that all
required properties are correctly propagated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# VALIDATION RESULT - Outcome of validation
# =============================================================================


class ValidationResult(Enum):
    """
    Result of a validation check.
    
    Results:
        PASS:     Validation succeeded
        WARN:     Passed but with warnings
        FAIL:     Validation failed
        SKIP:     Not applicable, skipping
    """
    
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


# =============================================================================
# VALIDATION FAILURE - Details of a validation failure
# =============================================================================


@dataclass(frozen=True)
class ValidationFailure:
    """
    Information about a specific validation failure.
    
    Fields:
        identity:           Unique identifier for this failure record
        check_name:         What check failed?
        check_description:  Description of what was expected
        actual_value:       What was actually found?
        expected_value:     What should have been there?
        severity:           How severe is the failure?
        recoverable:        Can processing continue despite this failure?
    """
    
    identity: str                # Unique ID for this failure
    
    check_name: str             # e.g., "confidence_range", "output_kinds_match"
    check_description: str      # What was checked
    
    actual_value: Optional[str] = None
    expected_value: Optional[str] = None
    
    severity: str = "error"     # error, warning, info
    recoverable: bool = False   # Can processing continue?
    
    @property
    def is_error(self) -> bool:
        """Check if this is an error-level failure."""
        return self.severity == "error"
    
    @property
    def is_warning(self) -> bool:
        """Check if this is a warning-level issue."""
        return self.severity == "warn"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "identity": self.identity,
            "check_name": self.check_name,
            "check_description": self.check_description,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value,
            "severity": self.severity,
            "recoverable": self.recoverable,
        }


# =============================================================================
# PROCESSING VALIDATION - Validation engine
# =============================================================================


@dataclass(frozen=True)
class ProcessingValidation:
    """
    Validation result for processing operations.
    
    Fields:
        identity:           Unique validation session ID
        target_identity:    What was validated?
        checks_performed:   List of check names that were run
        failures:           Any validation failures encountered
        confidence_valid:   Is the confidence valid?
        uncertainty_valid:  Is the uncertainty valid?
        output_valid:       Are outputs valid for publication?
        provenance:         Origin tracking
    """
    
    identity: str                    # Unique session ID
    
    target_identity: str             # What was validated (stage, pipeline, result)
    
    checks_performed: Tuple[str, ...] = field(default_factory=tuple)
    failures: Tuple[ValidationFailure, ...] = field(default_factory=tuple)
    
    confidence_valid: bool = True
    uncertainty_valid: bool = True
    output_valid: bool = False
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed with no errors."""
        return self.output_valid and all(not f.is_error for f in self.failures)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "identity": self.identity,
            "target_identity": self.target_identity,
            "checks_performed": list(self.checks_performed),
            "failures": [f.to_dict() for f in self.failures],
            "confidence_valid": self.confidence_valid,
            "uncertainty_valid": self.uncertainty_valid,
            "output_valid": self.output_valid,
        }
    
    @classmethod
    def create(
        cls,
        target_identity: str,
        checks_performed: Optional[List[str]] = None,
        failures: Optional[List[ValidationFailure]] = None,
        confidence_valid: bool = True,
        uncertainty_valid: bool = True,
        output_valid: bool = False,
    ) -> "ProcessingValidation":
        """Create a validation result."""
        return cls(
            identity=f"validate:{uuid.uuid4().hex[:16]}",
            target_identity=target_identity,
            checks_performed=tuple(checks_performed or []),
            failures=tuple(failures or []),
            confidence_valid=confidence_valid,
            uncertainty_valid=uncertainty_valid,
            output_valid=output_valid,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )