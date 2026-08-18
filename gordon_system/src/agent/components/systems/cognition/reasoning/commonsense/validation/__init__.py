# Commonsense Validation - Phase 7.45
# ====================================

"""
Validation contracts for Commonsense Reasoning.

Validation is observational and never modifies commonsense artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# VALIDATION RESULT
# =============================================================================

@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a validation check.
    
    Each result includes:
        - Whether the check passed
        - If it failed, why it failed
        - The affected artifact
    """
    
    result_id: str                            # Unique identifier
    check_name: str                           # Name of the validation check
    passed: bool                              # Did the check pass?
    
    failure_reason: Optional[str] = None      # Why did it fail? (if applicable)
    
    @classmethod
    def create(
        cls,
        check_name: str,
        passed: bool,
        failure_reason: Optional[str] = None,
    ) -> ValidationResult:
        """Create a new validation result."""
        return cls(
            result_id=f"validation_result:{uuid.uuid4().hex[:16]}",
            check_name=check_name,
            passed=passed,
            failure_reason=failure_reason,
        )


# =============================================================================
# VALIDATION FINDINGS
# =============================================================================

@dataclass(frozen=True)
class ValidationFindings:
    """
    Complete set of validation findings for a commonsense session.
    
    Findings include:
        - All validation results
        - Summary statistics
        - Recommendations (if any issues found)
    """
    
    # Identity
    findings_id: str                          # Unique findings identifier
    
    # Results
    validation_results: Tuple[ValidationResult, ...] = field(default_factory=tuple)
    
    # Statistics
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        validation_results: Tuple[ValidationResult, ...],
    ) -> ValidationFindings:
        """Create new validation findings."""
        total = len(validation_results)
        passed = sum(1 for r in validation_results if r.passed)
        return cls(
            findings_id=f"validation_findings:{uuid.uuid4().hex[:16]}",
            validation_results=validation_results,
            total_checks=total,
            passed_checks=passed,
            failed_checks=total - passed,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if all validations passed."""
        return self.failed_checks == 0


# =============================================================================
# VALIDATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class CommonsenseValidation:
    """
    Validation contract for commonsense reasoning.
    
    Validation remains observational and never modifies artifacts directly.
    """
    
    # Identity
    validation_id: str                        # Unique validation identifier
    
    # Validation data
    validated_session_id: str                 # ID of the session being validated
    validation_type: str                      # Type of validation performed
    
    # Results
    findings: ValidationFindings              # Complete set of findings
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        validated_session_id: str,
        validation_type: str,
        findings: ValidationFindings,
    ) -> CommonsenseValidation:
        """Create a new commonsense validation."""
        return cls(
            validation_id=f"commonsense_validation:{uuid.uuid4().hex[:16]}",
            validated_session_id=validated_session_id,
            validation_type=validation_type,
            findings=findings,
        )


__all__ = [
    "ValidationResult",
    "ValidationFindings",
    "CommonsenseValidation",
]