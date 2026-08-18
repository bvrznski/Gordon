# Predictive Validation Model - Phase 7.40
# =========================================

"""
Predictive validation model evaluates forecast quality and correctness.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ValidationOutcome(Enum):
    """Possible validation outcomes."""
    
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    CANNOT_VALIDATE = "cannot_validate"


@dataclass(frozen=True)
class ValidationResult:
    """Result of a single validation check."""
    
    check_id: str
    check_name: str
    outcome: ValidationOutcome
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def pass_check(cls, check_name: str, message: str = None) -> ValidationResult:
        """Create a passing validation result."""
        return cls(
            check_id=f"check:{uuid.uuid4().hex[:16]}",
            check_name=check_name,
            outcome=ValidationOutcome.PASSED,
            message=message,
        )
    
    @classmethod
    def fail_check(cls, check_name: str, message: str) -> ValidationResult:
        """Create a failing validation result."""
        return cls(
            check_id=f"check:{uuid.uuid4().hex[:16]}",
            check_name=check_name,
            outcome=ValidationOutcome.FAILED,
            message=message,
        )


@dataclass(frozen=True)
class ValidationFinding:
    """A finding from the validation process."""
    
    finding_id: str
    finding_type: str  # e.g., "format_error", "range_violation"
    severity: str  # "critical", "error", "warning", "info"
    description: str
    
    @classmethod
    def create(cls, finding_type: str, severity: str, description: str) -> ValidationFinding:
        """Create a validation finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            finding_type=finding_type,
            severity=severity,
            description=description,
        )


@dataclass(frozen=True)
class PredictiveValidation:
    """
    Comprehensive predictive validation model.
    
    Validation is observational - it does not modify forecasts but
    reports on their correctness and quality.
    """
    
    # Identity
    validation_identity: str
    
    # Validation results
    check_results: List[ValidationResult]
    overall_valid: bool
    
    # Findings
    findings: List[ValidationFinding] = field(default_factory=list)
    
    # Metadata
    validated_at_utc: float = field(default_factory=time.time)
    forecasts_validated: List[str] = field(default_factory=list)  # Forecast IDs validated
    
    @classmethod
    def create(
        cls,
        check_results: List[ValidationResult],
        findings: List[ValidationFinding] = None,
        forecasts_validated: List[str] = None,
    ) -> PredictiveValidation:
        """Create a predictive validation result."""
        overall_valid = all(r.outcome == ValidationOutcome.PASSED for r in check_results)
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            check_results=check_results,
            overall_valid=overall_valid,
            findings=findings or [],
            validated_at_utc=time.time(),
            forecasts_validated=forecasts_validated or [],
        )


__all__ = [
    "PredictiveValidation",
    "ValidationResult",
    "ValidationFinding",
    "ValidationOutcome",
]