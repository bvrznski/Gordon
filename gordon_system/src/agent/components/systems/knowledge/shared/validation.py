# Knowledge Validation - Phase 5.4
# ================================

"""
Knowledge Validation: Verifies correctness of knowledge artifacts before publication.

Validation ensures outputs conform to expected contracts and that all required
properties are correctly propagated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# VALIDATION RESULT - Outcome of validation check
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
# VALIDATION RESULT - Result of a validation session
# =============================================================================


@dataclass(frozen=True)
class KnowledgeValidation:
    """
    Validation result for knowledge operations.
    
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
    ) -> "KnowledgeValidation":
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
                "origin": "knowledge_validation",
                "created_at_utc": time.time(),
            },
        )


# =============================================================================
# VALIDATION ENGINE
# =============================================================================


class KnowledgeValidationEngine:
    """
    Validates knowledge artifacts for semantic integrity.
    
    Provides validation services for all knowledge artifact types.
    """
    
    def __init__(
        self,
        minimum_confidence: float = 0.3,
        maximum_uncertainty: float = 0.9,
    ):
        """
        Initialize the validation engine.
        
        Args:
            minimum_confidence: Minimum acceptable confidence
            maximum_uncertainty: Maximum acceptable uncertainty
        """
        self._minimum_confidence = minimum_confidence
        self._maximum_uncertainty = maximum_uncertainty
    
    def validate_assertion(
        self,
        assertion_identity: str,
        statement: str,
        confidence: float,
        uncertainty: float,
    ) -> KnowledgeValidation:
        """
        Validate an assertion.
        
        Args:
            assertion_identity: ID of the assertion
            statement: Assertion content
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            
        Returns:
            Validation result
        """
        failures = []
        
        # Rule 1: Identity must be present
        if not assertion_identity or len(assertion_identity) == 0:
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="assertion_identity",
                check_description="Assertion must have an identity",
                actual_value="empty" if not assertion_identity else None,
                severity="error",
            ))
        
        # Rule 2: Statement must not be empty
        if not statement or len(statement.strip()) == 0:
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="statement_content",
                check_description="Assertion must have non-empty content",
                actual_value="empty" if not statement else None,
                severity="error",
            ))
        
        # Rule 3: Confidence must be in range
        if not (0.0 <= confidence <= 1.0):
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="confidence_range",
                check_description="Confidence must be between 0.0 and 1.0",
                actual_value=str(confidence),
                expected_value="0.0-1.0",
                severity="error",
            ))
        
        # Rule 4: Uncertainty must be in range
        if not (0.0 <= uncertainty <= 1.0):
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="uncertainty_range",
                check_description="Uncertainty must be between 0.0 and 1.0",
                actual_value=str(uncertainty),
                expected_value="0.0-1.0",
                severity="error",
            ))
        
        return KnowledgeValidation.create(
            target_identity=assertion_identity,
            checks_performed=[
                "assertion_identity_present",
                "statement_not_empty",
                "confidence_range",
                "uncertainty_range",
            ],
            failures=failures,
            confidence_valid=len([f for f in failures if f.check_name == "confidence_range"]) == 0,
            uncertainty_valid=len([f for f in failures if f.check_name == "uncertainty_range"]) == 0,
            output_valid=len(failures) == 0,
        )
    
    def validate_belief(
        self,
        belief_identity: str,
        confidence: float,
        uncertainty: float,
        supporting_evidence_count: int,
    ) -> KnowledgeValidation:
        """
        Validate a belief.
        
        Args:
            belief_identity: ID of the belief
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            supporting_evidence_count: Number of supporting evidence items
            
        Returns:
            Validation result
        """
        failures = []
        
        # Rule 1: Identity must be present
        if not belief_identity or len(belief_identity) == 0:
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="belief_identity",
                check_description="Belief must have an identity",
                actual_value="empty" if not belief_identity else None,
                severity="error",
            ))
        
        # Rule 2: Confidence must be in range
        if not (0.0 <= confidence <= 1.0):
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="confidence_range",
                check_description="Confidence must be between 0.0 and 1.0",
                actual_value=str(confidence),
                expected_value="0.0-1.0",
                severity="error",
            ))
        
        # Rule 3: Uncertainty must be in range
        if not (0.0 <= uncertainty <= 1.0):
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="uncertainty_range",
                check_description="Uncertainty must be between 0.0 and 1.0",
                actual_value=str(uncertainty),
                expected_value="0.0-1.0",
                severity="error",
            ))
        
        # Rule 4: ACCEPTED beliefs need minimum supporting evidence
        if supporting_evidence_count == 0:
            failures.append(ValidationFailure(
                identity="fail:" + uuid.uuid4().hex[:8],
                check_name="supporting_evidence",
                check_description="Belief needs supporting evidence",
                actual_value=str(supporting_evidence_count),
                expected_value=">=1",
                severity="warn",
            ))
        
        return KnowledgeValidation.create(
            target_identity=belief_identity,
            checks_performed=[
                "belief_identity_present",
                "confidence_range",
                "uncertainty_range",
                "supporting_evidence",
            ],
            failures=failures,
            confidence_valid=len([f for f in failures if f.check_name == "confidence_range"]) == 0,
            uncertainty_valid=len([f for f in failures if f.check_name == "uncertainty_range"]) == 0,
            output_valid=len(failures) == 0,
        )


__all__ = [
    "ValidationResult",
    "ValidationFailure",
    "KnowledgeValidation",
    "KnowledgeValidationEngine",
]