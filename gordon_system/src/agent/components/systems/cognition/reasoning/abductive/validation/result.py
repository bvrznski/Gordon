# Abduction Validation Result - Phase 7.3
# =====================================

"""
Validation results for abductive reasoning.

This module provides:
    - Validation outcomes (valid, invalid, conditional)
    - Validation findings (issues identified)
    - Validation traces (step-by-step validation history)
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationResult(Enum):
    """Results of abductive validation."""
    
    VALID = "valid"                           # Meets all requirements
    CONDITIONALLY_VALID = "conditionally_valid"  # Meets main requirements with findings
    INVALID = "invalid"                       # Fails critical requirements


class ValidationFindingKind(Enum):
    """Kinds of validation findings."""
    
    LOW_CONFIDENCE = "low_confidence"         # Confidence below threshold
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"  # Not enough supporting evidence
    MISSING_CAUSAL_LINK = "missing_causal_link"      # Causal mechanism not explained
    INCONSISTENT_WITH_KNOWLEDGE = "inconsistent_with_knowledge"  # Conflicts with known facts
    UNACCEPTABLE_ASSUMPTION = "unacceptable_assumption"  # Assumptions are problematic


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding.
    
    Each finding describes a specific issue identified during validation.
    """
    
    # Identity
    finding_id: str                           # Unique identifier
    
    # Content
    finding_kind: ValidationFindingKind       # What kind of issue?
    description: str                          # Detailed explanation
    
    # Assessment
    severity: str = "warning"                 # "info", "warning", or "error"
    confidence: float = 1.0                   # Confidence in the finding itself
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical issue."""
        return self.severity == "error"
    
    @property
    def is_warning(self) -> bool:
        """Check if this is a warning."""
        return self.severity == "warning"
    
    @classmethod
    def create(
        cls,
        finding_kind: ValidationFindingKind,
        description: str,
        severity: str = "warning",
        confidence: float = 1.0,
    ) -> ValidationFinding:
        """Create a new validation finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
            severity=severity,
            confidence=confidence,
        )


@dataclass(frozen=True)
class ValidationTrace:
    """
    Trace of the validation process.
    
    This records:
        - All validation steps performed
        - Intermediate results
        - Evidence considered at each step
    
    Trace remains inspectable for audit and debugging.
    """
    
    # Identity
    trace_id: str                             # Unique identifier
    
    # Steps
    validation_steps: Tuple[Dict[str, Any], ...]  # Each step recorded
    
    # Summary
    total_steps: int = 0                      # Total validation steps
    passed_steps: int = 0                     # Steps that passed
    
    @classmethod
    def create(
        cls,
        validation_steps: List[Dict[str, Any]],
    ) -> ValidationTrace:
        """Create a new validation trace."""
        return cls(
            trace_id=f"trace:{uuid.uuid4().hex[:16]}",
            validation_steps=tuple(validation_steps),
            total_steps=len(validation_steps),
            passed_steps=sum(1 for s in validation_steps if s.get("result") == "passed"),
        )


@dataclass(frozen=True)
class ValidationResultRecord:
    """
    Complete validation result record.
    
    This provides:
        - Final outcome (valid/invalid/conditionally_valid)
        - All findings identified
        - Validation trace
        - Timestamps and provenance
    
    Validation results remain immutable once recorded.
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    validated_artifact_type: str              # What was validated?
    validated_artifact_id: str                # Which artifact?
    
    # Results
    result: ValidationResult                  # Overall outcome
    findings: Tuple[ValidationFinding, ...] = ()  # All findings
    
    # Trace
    validation_trace: Optional[ValidationTrace] = None  # Validation history
    
    @property
    def is_strictly_valid(self) -> bool:
        """Check if the artifact passed all validation checks."""
        return self.result == ValidationResult.VALID and len(self.findings) == 0
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical (error) issues."""
        return any(f.is_critical for f in self.findings)
    
    @property
    def finding_count(self) -> int:
        """Number of validation findings."""
        return len(self.findings)
    
    @classmethod
    def create(
        cls,
        validated_artifact_type: str,
        validated_artifact_id: str,
        result: ValidationResult = ValidationResult.VALID,
        findings: Optional[List[ValidationFinding]] = None,
        trace: Optional[ValidationTrace] = None,
    ) -> ValidationResultRecord:
        """Create a new validation result record."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            validated_artifact_type=validated_artifact_type,
            validated_artifact_id=validated_artifact_id,
            result=result,
            findings=tuple(findings or []),
            validation_trace=trace,
        )


@dataclass(frozen=True)
class AbductionValidationError(Exception):
    """
    Exception raised when abductive validation fails.
    
    This exception carries detailed information about:
        - What validation failed
        - Which requirements were violated
        - Suggested remediation
    
    Errors remain inspectable for debugging and logging.
    """
    
    # Identity
    error_id: str                             # Unique identifier
    
    # Error details
    error_type: str                           # Category of error
    message: str                              # Human-readable description
    
    # Context
    affected_artifact_type: Optional[str] = None  # What was being validated?
    affected_artifact_id: Optional[str] = None    # Which artifact?
    
    # Remediation
    suggested_remediation: Tuple[str, ...] = ()  # How to fix it?
    
    @property
    def is_critical(self) -> bool:
        """Check if this error is critical."""
        return self.error_type in ("data_corruption", "security_violation")
    
    @classmethod
    def create(
        cls,
        error_type: str,
        message: str,
        affected_artifact_type: Optional[str] = None,
        affected_artifact_id: Optional[str] = None,
        suggested_remediation: Optional[List[str]] = None,
    ) -> AbductionValidationError:
        """Create a new validation error."""
        return cls(
            error_id=f"error:{uuid.uuid4().hex[:16]}",
            error_type=error_type,
            message=message,
            affected_artifact_type=affected_artifact_type,
            affected_artifact_id=affected_artifact_id,
            suggested_remediation=tuple(suggested_remediation or []),
        )


__all__ = [
    "ValidationResult",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
    "ValidationResultRecord",
    "AbductionValidationError",
]