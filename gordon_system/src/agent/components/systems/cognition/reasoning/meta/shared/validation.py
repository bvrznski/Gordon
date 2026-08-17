# Meta Reasoning Validation - Phase 7.13
# =======================================

"""
Canonical Meta-Reasoning Validation definition.

Validation provides observational validation of meta-reasoning execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationStatus(Enum):
    """Validation result status."""
    
    PENDING = "pending"                       # Validation pending
    VALIDATING = "validating"                 # Currently validating
    VALIDATED = "validated"                   # Successfully validated
    INVALIDATED = "invalidated"               # Validation failed
    SKIPPED = "skipped"                       # Validation skipped


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating a meta-reasoning artifact.
    
    A validation result contains:
        - Identity and provenance
        - Validation outcome
        - Detailed findings
        - Timestamps
    
    Validation remains observational (does not modify artifacts).
    """
    
    # Identity
    validation_id: str                      # Unique validation identifier
    
    # Artifact being validated
    artifact_type: str                      # What kind of artifact?
    artifact_id: str                        # Artifact identifier
    
    # Validation result
    status: ValidationStatus = ValidationStatus.PENDING
    
    # Detailed findings
    findings: List[str] = field(default_factory=list)  # Validation messages
    errors: List[str] = field(default_factory=list)   # Error messages
    warnings: List[str] = field(default_factory=list) # Warning messages
    
    # Timing
    requested_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate validation time."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.requested_at_utc
        return 0.0
    
    @property
    def is_valid(self) -> bool:
        """Check if validation succeeded."""
        return self.status == ValidationStatus.VALIDATED
    
    @classmethod
    def create(
        cls,
        artifact_type: str,
        artifact_id: str,
    ) -> ValidationResult:
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            status=ValidationStatus.VALIDATED,
            completed_at_utc=time.time(),
        )
    
    def with_findings(self, findings: List[str]) -> ValidationResult:
        """Add findings and return updated validation."""
        return dataclass_replace(
            self,
            findings=self.findings + findings,
        )
    
    def with_errors(self, errors: List[str]) -> ValidationResult:
        """Add errors and return updated validation."""
        return dataclass_replace(
            self,
            errors=self.errors + errors,
            status=ValidationStatus.INVALIDATED if errors else self.status,
        )
    
    def with_warnings(self, warnings: List[str]) -> ValidationResult:
        """Add warnings and return updated validation."""
        return dataclass_replace(
            self,
            warnings=self.warnings + warnings,
        )
    
    def mark_validated(self) -> ValidationResult:
        """Mark as validated."""
        return dataclass_replace(
            self,
            status=ValidationStatus.VALIDATED,
            completed_at_utc=time.time(),
        )
    
    def mark_invalidated(self, errors: List[str]) -> ValidationResult:
        """Mark as invalidated with errors."""
        return dataclass_replace(
            self,
            status=ValidationStatus.INVALIDATED,
            errors=self.errors + errors,
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class MetaReasoningValidation:
    """
    Validation of meta-reasoning execution artifacts.
    
    A validation result contains:
        - Identity and provenance
        - Validated session information
        - Validation findings
        - Recommendations (if any)
    
    Validation never modifies meta-reasoning artifacts directly.
    """
    
    # Identity
    validation_id: str                      # Unique validation identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Validated session
    validated_session_id: Optional[str] = None  # Session ID if applicable
    
    # Validation results
    results: List[ValidationResult] = field(default_factory=list)  # Artifact validations
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)  # Suggested improvements
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate validation time."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.created_at_utc
        return 0.0
    
    @property
    def overall_status(self) -> ValidationStatus:
        """Get overall validation status."""
        if not self.results:
            return ValidationStatus.PENDING
        
        statuses = [r.status for r in self.results]
        
        if ValidationStatus.INVALIDATED in statuses:
            return ValidationStatus.INVALIDATED
        if ValidationStatus.VALIDATING in statuses:
            return ValidationStatus.VALIDATING
        if all(s == ValidationStatus.VALIDATED for s in statuses):
            return ValidationStatus.VALIDATED
        
        return ValidationStatus.PENDING
    
    def add_result(self, result: ValidationResult) -> MetaReasoningValidation:
        """Add a validation result and return updated validation."""
        return dataclass_replace(
            self,
            results=self.results + [result],
        )
    
    def with_recommendation(self, recommendation: str) -> MetaReasoningValidation:
        """Add a recommendation and return updated validation."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + [recommendation],
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> MetaReasoningValidation:
        """Create a new validation session."""
        return cls(
            validation_id=f"meta_validation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
        )
    
    def to_completed(self) -> MetaReasoningValidation:
        """Mark validation as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningValidation",
    "ValidationStatus",
    "ValidationResult",
]