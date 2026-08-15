# Focusing Network Validation Contracts
# ======================================

"""
Validation contracts for the FocusingNetwork Phase 4.2.8.

These define validation expectations without implementing validation logic.
The FocusingNetwork follows these rules but doesn't define them.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
from datetime import datetime


# =============================================================================
# VALIDATION REPORT - Result of a validation operation
# =============================================================================

@dataclass(frozen=True)
class ValidationReport:
    """
    Immutable report of validation results.
    
    Contains validation outcome information without exposing how validation
    was performed. Only the results, not the validation logic.
    
    PROPERTIES:
        • Immutable once created
        • Complete validation result summary
        • Versioned for compatibility tracking
    """
    
    # Report identity
    report_id: str = field(default_factory=lambda: f"validation_report_{id(datetime.utcnow()):x}")
    """Unique identifier for this validation report."""
    
    # Validation outcome
    is_valid: bool = True
    """Whether validation passed."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """Error messages if validation failed."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Warning messages for non-critical issues."""
    
    # Validation context
    validated_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When validation was performed."""
    
    validation_type: str = "unknown"
    """Type of validation (e.g., 'input', 'output', 'state')."""
    
    # Validation metadata
    target_id: Optional[str] = None
    """ID of the item that was validated (if any)."""
    
    def merge(self, other: "ValidationReport") -> "ValidationReport":
        """
        Merge two validation reports.
        
        Args:
            other: Another validation report to merge
            
        Returns:
            New ValidationReport with combined results
        """
        return ValidationReport(
            report_id=f"{self.report_id}_{other.report_id}",
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            validated_at_utc=max(self.validated_at_utc, other.validated_at_utc),
            validation_type=self.validation_type,
            target_id=self.target_id or other.target_id,
        )
    
    @classmethod
    def valid(cls) -> "ValidationReport":
        """Create a successful validation report."""
        return cls(is_valid=True)
    
    @classmethod
    def invalid(cls, *errors: str) -> "ValidationReport":
        """
        Create an invalid validation report.
        
        Args:
            *errors: Error messages for the failure
            
        Returns:
            New ValidationReport with is_valid=False and provided errors
        """
        return cls(is_valid=False, errors=errors)


# =============================================================================
# ASSESSMENT VALIDATOR - Validates assessment outputs
# =============================================================================

@dataclass(frozen=True)
class AssessmentValidator:
    """
    Defines validation expectations for assessments.
    
    Specifies what makes an assessment valid without implementing the
    validation. The FocusingNetwork uses these rules but doesn't define them.
    
    PROPERTIES:
        • Rules are defined, not implemented here
        • Versioned for compatibility tracking
        • External implementation responsibility
    """
    
    # Validator identity
    validator_id: str = field(default_factory=lambda: f"assessment_validator_{id(datetime.utcnow()):x}")
    """Unique identifier for this validator."""
    
    # Required assessment fields
    required_fields: Tuple[str, ...] = (
        "assessment_id",
        "timestamp_utc",
        "overall_focus_score",
    )
    """Fields that must be present in any assessment."""
    
    # Value range rules
    score_range_min: float = 0.0
    """Minimum valid value for scores."""
    
    score_range_max: float = 1.0
    """Maximum valid value for scores."""
    
    # Assessment type validation
    valid_assessment_types: Tuple[str, ...] = (
        "focus",
        "priority",
        "relevance",
        "competition",
        "suppression",
        "precision",
        "persistence",
        "bias",
        "allocation",
    )
    """Valid assessment type identifiers."""
    
    def validate_score(self, score: float) -> bool:
        """
        Check if a score is within valid range.
        
        Args:
            score: Score value to validate
            
        Returns:
            True if score is in [min, max], False otherwise
        """
        return self.score_range_min <= score <= self.score_range_max
    
    def is_valid_assessment_type(self, assessment_type: str) -> bool:
        """
        Check if an assessment type is valid.
        
        Args:
            assessment_type: Assessment type identifier
            
        Returns:
            True if the type is in valid_assessment_types
        """
        return assessment_type in self.valid_assessment_types


# =============================================================================
# CONTEXT VALIDATOR - Validates context projections
# =============================================================================

@dataclass(frozen=True)
class ContextValidator:
    """
    Defines validation expectations for context projections.
    
    Specifies what makes a context projection valid without implementing
    the validation. The FocusingNetwork uses these rules but doesn't define them.
    
    PROPERTIES:
        • Rules are defined, not implemented here
        • Versioned for compatibility tracking
        • External implementation responsibility
    """
    
    # Validator identity
    validator_id: str = field(default_factory=lambda: f"context_validator_{id(datetime.utcnow()):x}")
    """Unique identifier for this validator."""
    
    # Required context fields
    required_projection_fields: Tuple[str, ...] = (
        "projection_id",
        "created_at_utc",
    )
    """Fields that must be present in any projection."""
    
    # Range validation rules
    probability_range_min: float = 0.0
    """Minimum valid value for probabilities and ratios."""
    
    probability_range_max: float = 1.0
    """Maximum valid value for probabilities and ratios."""
    
    percentage_range_min: float = 0.0
    """Minimum valid value for percentages."""
    
    percentage_range_max: float = 100.0
    """Maximum valid value for percentages."""
    
    # Timestamp validation
    allow_future_timestamps: bool = True
    """Whether future timestamps are allowed in projections."""
    
    max_time_diff_seconds: float = 3600.0
    """Maximum time difference from current time (1 hour)."""
    
    def validate_probability(self, value: float) -> bool:
        """
        Check if a value is a valid probability.
        
        Args:
            value: Value to check
            
        Returns:
            True if value is in [0.0, 1.0], False otherwise
        """
        return self.probability_range_min <= value <= self.probability_range_max
    
    def validate_percentage(self, value: float) -> bool:
        """
        Check if a value is a valid percentage.
        
        Args:
            value: Value to check
            
        Returns:
            True if value is in [0.0, 100.0], False otherwise
        """
        return self.percentage_range_min <= value <= self.percentage_range_max


# =============================================================================
# STATE VALIDATOR - Validates state views
# =============================================================================

@dataclass(frozen=True)
class StateValidator:
    """
    Defines validation expectations for state views.
    
    Specifies what makes a state view valid without implementing the
    validation. The FocusingNetwork uses these rules but doesn't define them.
    
    PROPERTIES:
        • Rules are defined, not implemented here
        • Versioned for compatibility tracking
        • External implementation responsibility
    """
    
    # Validator identity
    validator_id: str = field(default_factory=lambda: f"state_validator_{id(datetime.utcnow()):x}")
    """Unique identifier for this validator."""
    
    # State view validation rules
    required_view_fields: Tuple[str, ...] = (
        "view_id",
        "timestamp_utc",
    )
    """Fields that must be present in any state view."""
    
    # Count bounds (for bounded state)
    max_target_count: int = 100
    """Maximum number of targets allowed in a state view."""
    
    max_allocation_count: int = 50
    """Maximum number of allocations tracked."""
    
    max_history_entries: int = 1000
    """Maximum history entries to retain."""
    
    # Value bounds
    confidence_range_min: float = 0.0
    """Minimum valid confidence value."""
    
    confidence_range_max: float = 1.0
    """Maximum valid confidence value."""
    
    def validate_target_count(self, count: int) -> bool:
        """
        Check if a target count is within bounds.
        
        Args:
            count: Number of targets
            
        Returns:
            True if count <= max_target_count
        """
        return count <= self.max_target_count
    
    def validate_confidence(self, confidence: float) -> bool:
        """
        Check if a confidence value is valid.
        
        Args:
            confidence: Confidence value to check
            
        Returns:
            True if confidence is in [0.0, 1.0]
        """
        return self.confidence_range_min <= confidence <= self.confidence_range_max


# =============================================================================
# FOCUS VALIDATION CONTRACT - Main validation interface
# =============================================================================

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FocusValidationContract(Protocol):
    """
    Protocol for validation of FocusingNetwork data.
    
    Defines all validation expectations that external systems can use to
    validate inputs and outputs without coupling to implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new validators via enum)
    
    OWNERSHIP:
        - Validation rules are owned by this contract definition
        - Network follows these rules but doesn't define them
    
    USE BY:
        - External systems validate inputs before sending to network
        - Consumer may validate outputs from network
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def is_valid_input(
        self,
        input_data: Dict[str, Any],
    ) -> ValidationReport:
        """
        Validate input data for the FocusingNetwork.
        
        Args:
            input_data: Input dictionary to validate
            
        Returns:
            ValidationReport with is_valid flag and error/warning messages
        """
        ...
    
    @abstractmethod
    def is_valid_output(
        self,
        output_data: Dict[str, Any],
    ) -> ValidationReport:
        """
        Validate output data from the FocusingNetwork.
        
        Args:
            output_data: Output dictionary to validate
            
        Returns:
            ValidationReport with is_valid flag and error/warning messages
        """
        ...
    
    @abstractmethod
    def validate_assessment(
        self,
        assessment: Dict[str, Any],
    ) -> ValidationReport:
        """
        Validate an assessment.
        
        Args:
            assessment: Assessment dictionary to validate
            
        Returns:
            ValidationReport with is_valid flag and error/warning messages
        """
        ...
    
    @abstractmethod
    def get_validation_rules(self) -> Tuple[Dict[str, Any], ...]:
        """
        Get all validation rule definitions.
        
        Returns:
            Tuple of rule dictionaries describing each validation rule
        """
        ...


__all__ = [
    # Validation result
    "ValidationReport",
    # Validator rule sets (not implementations)
    "AssessmentValidator",
    "ContextValidator",
    "StateValidator",
    # Main validation interface
    "FocusValidationContract",
]
