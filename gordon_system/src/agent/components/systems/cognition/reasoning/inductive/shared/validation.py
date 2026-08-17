# Induction Validation - Phase 7.2
# =================================

"""
Canonical Induction Validation Contract.

Validation evaluates the quality and reliability of induction results.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationResult(Enum):
    """Possible outcomes of induction validation."""
    
    VALID = "valid"                       # Meets all requirements
    CONDITIONALLY_VALID = "conditionally_valid"  # Meets most, has minor issues
    INVALID = "invalid"                   # Fails key requirements
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"  # Not enough data to decide


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single finding from induction validation.
    
    Findings record specific aspects of the validation process.
    """
    
    # Identity
    finding_id: str                       # Unique identifier
    
    # Finding details
    finding_kind: str                     # e.g., "low_confidence", "insufficient_support"
    severity: str = "info"                # info, warning, error
    
    # Description
    description: str                      # Human-readable explanation
    affected_component: Optional[str] = None  # Which component was evaluated?
    
    # Evidence for finding
    supporting_evidence: Tuple[str, ...] = ()  # Supporting data points
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    validator_id: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InductionValidation:
    """
    Validation of an induction session or result.
    
    A validation records:
        - What was validated
        - All findings from the evaluation
        - Overall validation outcome
        - Provenance tracking
    
    Validation remains observational; it does not modify results directly.
    """
    
    # Identity
    validation_id: str                    # Unique identifier for this validation
    
    # Validated artifact
    validated_artifact_type: str          # e.g., "generalization", "hypothesis_cluster"
    validated_artifact_id: str            # ID of the artifact being validated
    
    # Validation parameters
    confidence_threshold: float = 0.5     # Minimum acceptable confidence
    minimum_support: int = 1              # Minimum required evidence
    
    # Findings from validation
    findings: Tuple[ValidationFinding, ...]
    
    # Overall outcome
    result: ValidationResult = ValidationResult.VALID
    validation_message: str = ""          # Human-readable summary
    
    # Validation metrics
    total_checks_performed: int = 0       # How many checks?
    checks_passed: int = 0                # How many passed?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    validator_id: str = "default"
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def check_pass_rate(self) -> float:
        """Calculate the pass rate for validation checks."""
        if self.total_checks_performed == 0:
            return 1.0
        return self.checks_passed / self.total_checks_performed
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical (error-level) issues."""
        return any(f.severity == "error" for f in self.findings)
    
    @property
    def is_strictly_valid(self) -> bool:
        """Check if validation passed with no conditions."""
        return self.result == ValidationResult.VALID and not self.has_critical_issues


@dataclass(frozen=True)
class ValidationTrace:
    """
    Trace of validation steps for auditability.
    
    Each trace entry records a single step in the validation process.
    """
    
    # Identity
    trace_id: str                         # Unique trace identifier
    
    # Step information
    step_number: int                      # Order in validation sequence
    step_kind: str                        # e.g., "threshold_check", "consistency_check"
    
    # Context
    component_validated: str              # What was validated?
    result: Optional[str] = None          # Result of this step
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create_step(
        cls,
        trace_id: str,
        step_number: int,
        step_kind: str,
        component: str,
        result: Optional[str] = None,
    ) -> ValidationTrace:
        """Create a new validation trace step."""
        return cls(
            trace_id=trace_id,
            step_number=step_number,
            step_kind=step_kind,
            component_validated=component,
            result=result,
            timestamp_utc=time.time(),
        )


@dataclass(frozen=True)
class ValidationError(Exception):
    """
    Exception raised when validation fails.
    
    Contains detailed information about what failed and why.
    """
    
    error_id: str
    validation_result: ValidationResult
    error_message: str
    related_findings: Tuple[str, ...] = ()
    recovery_options: Tuple[str, ...] = ()


__all__ = [
    "ValidationResult",
    "ValidationFinding",
    "InductionValidation",
    "ValidationTrace",
    "ValidationError",
]