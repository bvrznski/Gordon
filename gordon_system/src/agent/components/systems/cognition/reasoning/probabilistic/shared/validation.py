# Probabilistic Validation - Phase 7.7
# ====================================

"""
Canonical validation contracts for probabilistic reasoning.

Validation remains observational - it never modifies artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class ValidationRule(Enum):
    """Rules for validating probabilistic reasoning."""
    
    PRIOR_EXISTS = "prior_exists"                   # Prior must be defined
    LIKELIHOOD_DEFINED = "likelihood_defined"       # Likelihood function must exist
    SUM_TO_ONE = "sum_to_one"                       # Probabilities must sum to 1
    NON_NEGATIVE = "non_negative"                   # No negative probabilities
    CALIBRATION_ACCURATE = "calibration_accurate"   # Calibrated within bounds
    NO_CYCLES = "no_cycles"                         # No dependency cycles


@dataclass(frozen=True)
class ValidationFinding:
    """
    A finding from validation of probabilistic reasoning.
    
    Represents one aspect of the validation result.
    """
    
    # Identity
    finding_id: str                         # Unique identifier
    
    # Finding details
    rule_name: str = ""                     # Which rule was checked?
    passed: bool = True                     # Did it pass?
    
    # Details
    description: str = ""                   # Human-readable description
    severity: str = "info"                  # "info", "warning", or "error"
    
    # Location
    affected_component: Optional[str] = None  # Which part failed validation?


@dataclass(frozen=True)
class ProbabilisticValidationResult:
    """
    Complete validation result for a probabilistic session.
    
    Validation is observational - it never modifies artifacts directly.
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # What was validated
    validated_session_identity: str         # Which session was validated?
    
    # Findings
    findings: Tuple[ValidationFinding, ...] = ()
    
    # Overall result
    overall_passed: bool = True             # Did all checks pass?
    validation_rules_checked: int = 0       # How many rules evaluated?
    
    # Timestamps
    validated_at_utc: float = field(default_factory=time.time)
    
    @property
    def error_count(self) -> int:
        """Count number of errors (severity='error')."""
        return sum(1 for f in self.findings if f.severity == "error")
    
    @property
    def warning_count(self) -> int:
        """Count number of warnings (severity='warning')."""
        return sum(1 for f in self.findings if f.severity == "warning")
    
    @classmethod
    def create_passed(cls, session_id: str, rules_checked: int = 0) -> ProbabilisticValidationResult:
        """Create a result showing all checks passed."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            validated_session_identity=session_id,
            findings=(),
            overall_passed=True,
            validation_rules_checked=rules_checked,
        )
    
    @classmethod
    def create_failed(cls, session_id: str, finding: ValidationFinding) -> ProbabilisticValidationResult:
        """Create a result showing validation failed."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            validated_session_identity=session_id,
            findings=(finding,),
            overall_passed=False,
            validation_rules_checked=1,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ProbabilisticValidationResult",
    "ValidationFinding", 
    "ValidationRule",
]