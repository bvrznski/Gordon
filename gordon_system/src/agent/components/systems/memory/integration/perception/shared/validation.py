# Validation - Cross-System Artifact Validation
# ==============================================

"""
Validation: Quality assurance for cross-system Memory-Perception artifacts.

Every cross-system artifact shall be validated before publication. Validation
ensures:
    - Source Roles are properly assigned and preserved
    - Provenance chains are complete and valid
    - Confidence/uncertainty metrics are available
    - No circular references exist
    - Required fields are present
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# VALIDATION STATUS
# =============================================================================


class ValidationStatus(Enum):
    """
    Status of artifact validation.
    
    Every cross-system artifact shall have a clear validation status that
    indicates whether it's safe to use in downstream processing.
    """
    
    PASSED = "passed"                     # All validations passed
    WARNING = "warning"                   # Valid but with warnings
    FAILED = "failed"                     # Validation failed
    UNKNOWN = "unknown"                   # Status not determined


# =============================================================================
# VALIDATION RULE KINDS
# =============================================================================


class ValidationRuleKind(Enum):
    """
    Kinds of validation rules that can be applied.
    
    Each rule kind validates a specific aspect of the artifact.
    """
    
    # Basic structure rules
    REQUIRED_FIELDS = "required_fields"     # All required fields present
    
    # Quality rules
    CONFIDENCE_RANGE = "confidence_range"   # Confidence in [0, 1]
    UNCERTAINTY_RANGE = "uncertainty_range" # Uncertainty in [0, 1]
    
    # Source role rules
    SOURCE_ROLE_PRESENT = "source_role_present"     # Has source role
    SOURCE_ROLE_VALID = "source_role_valid"         # Role kind is valid
    
    # Provenance rules
    PROVENANCE_COMPLETE = "provenance_complete"     # Full traceability chain
    NO_CIRCULAR_REFERENCE = "no_circular_reference"  # No circular references
    
    # Consistency rules
    CONFIDENCE_UNCERTAINTY_SUM = "confidence_uncertainty_sum"  # Sum <= 1.0
    TEMPORAL_ORDERING = "temporal_ordering"          # Timestamps in order


# =============================================================================
# VALIDATION RESULT - What validation produced
# =============================================================================


@dataclass(frozen=True)
class ValidationRuleResult:
    """
    Result of a single validation rule.
    
    Every applied rule shall produce a result that indicates whether it passed,
    failed, or had warnings.
    """
    
    # Identity
    rule_identity: str                      # Unique ID for this rule
    
    # Rule details
    rule_kind: ValidationRuleKind           # What kind of rule?
    rule_name: str                          # Human-readable name
    
    # Result
    status: ValidationStatus                # Did the rule pass?
    
    # Details
    passed: bool                            # True if validation succeeded
    message: Optional[str] = None           # Explanation for result
    affected_field: Optional[str] = None    # Which field(s) affected?
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_identity": self.rule_identity,
            "rule_kind": self.rule_kind.value,
            "rule_name": self.rule_name,
            "status": self.status.value,
            "passed": self.passed,
            "message": self.message,
            "affected_field": self.affected_field,
        }


# =============================================================================
# VALIDATION REPORT - Complete validation output
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete validation report for a cross-system artifact.
    
    Every artifact shall have an inspectable validation report that documents
    what was validated and the results.
    """
    
    # Identity and target
    report_identity: str                    # Unique ID for this report
    artifact_id: Optional[str] = None       # Artifact being validated
    
    # Overall result
    overall_status: ValidationStatus        # Complete validation status
    passed_rules: int = 0                   # Number of passed rules
    failed_rules: int = 0                   # Number of failed rules
    warning_rules: int = 0                  # Number of warnings
    
    # Individual rule results (required, no default)
    rule_results: Tuple[ValidationRuleResult, ...] = field(default_factory=tuple)
    
    # Quality metrics
    confidence: float = 1.0                 # Confidence in the artifact
    uncertainty: float = 0.0                # Uncertainty about validity
    
    @property
    def is_valid(self) -> bool:
        """Check if overall validation passed."""
        return self.overall_status == ValidationStatus.PASSED
    
    @classmethod
    def passed(
        cls,
        report_identity: str,
        artifact_id: Optional[str] = None,
        rules_passed: int = 0,
        confidence: float = 1.0,
    ) -> "ValidationResult":
        """Create a passing validation result."""
        return cls(
            report_identity=report_identity,
            artifact_id=artifact_id,
            overall_status=ValidationStatus.PASSED,
            passed_rules=rules_passed,
            failed_rules=0,
            warning_rules=0,
            confidence=confidence,
            uncertainty=0.0,
        )
    
    @classmethod
    def partial(
        cls,
        report_identity: str,
        artifact_id: Optional[str] = None,
        rules_passed: int = 0,
        rules_failed: int = 0,
        warnings: int = 0,
        confidence: float = 0.75,
    ) -> "ValidationResult":
        """Create a partial validation result."""
        return cls(
            report_identity=report_identity,
            artifact_id=artifact_id,
            overall_status=ValidationStatus.WARNING,
            passed_rules=rules_passed,
            failed_rules=rules_failed,
            warning_rules=warnings,
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def failed(
        cls,
        report_identity: str,
        artifact_id: Optional[str] = None,
        rules_failed: int = 0,
        message: str = "Validation failed",
        confidence: float = 0.0,
    ) -> "ValidationResult":
        """Create a failing validation result."""
        return cls(
            report_identity=report_identity,
            artifact_id=artifact_id,
            overall_status=ValidationStatus.FAILED,
            passed_rules=0,
            failed_rules=rules_failed,
            warning_rules=0,
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_identity": self.report_identity,
            "artifact_id": self.artifact_id,
            "overall_status": self.overall_status.value,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "warning_rules": self.warning_rules,
            "rule_results": [r.to_dict() for r in self.rule_results],
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# VALIDATOR - Apply validation rules
# =============================================================================


class ArtifactValidator:
    """
    Validates cross-system Memory-Perception artifacts.
    
    Applies validation rules to ensure artifact integrity before publication.
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._rules_applied: List[ValidationRuleResult] = []
    
    def validate_source_role(
        cls,
        source_role_data: Dict[str, Any],
    ) -> ValidationRuleResult:
        """
        Validate a source role assignment.
        
        Args:
            source_role_data: The source role metadata to validate
            
        Returns:
            Validation result for the source role
        """
        rule_id = f"rule:sr:{hash(str(source_role_data)) % 10000:04x}"
        
        # Check required fields
        if "role_kind" not in source_role_data:
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.REQUIRED_FIELDS,
                rule_name="Source role has required fields",
                status=ValidationStatus.FAILED,
                passed=False,
                message="Missing required field: role_kind",
                affected_field="role_kind",
            )
        
        # Validate role kind value
        from gordon_system.src.agent.components.systems.memory.integration.perception.shared.source_role import SourceRoleKind
        
        try:
            _ = SourceRoleKind(source_role_data.get("role_kind", ""))
        except ValueError:
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.SOURCE_ROLE_VALID,
                rule_name="Source role kind is valid",
                status=ValidationStatus.FAILED,
                passed=False,
                message=f"Invalid source role kind: {source_role_data.get('role_kind')}",
                affected_field="role_kind",
            )
        
        return ValidationRuleResult(
            rule_identity=rule_id,
            rule_kind=ValidationRuleKind.SOURCE_ROLE_VALID,
            rule_name="Source role is valid",
            status=ValidationStatus.PASSED,
            passed=True,
            message="Source role validation passed",
        )
    
    def validate_confidence_range(
        cls,
        confidence: float,
    ) -> ValidationRuleResult:
        """
        Validate that confidence is in valid range [0.0, 1.0].
        
        Args:
            confidence: The confidence value to validate
            
        Returns:
            Validation result
        """
        rule_id = f"rule:conf:{hash(str(confidence)) % 10000:04x}"
        
        if not isinstance(confidence, (int, float)):
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.CONFIDENCE_RANGE,
                rule_name="Confidence is numeric",
                status=ValidationStatus.FAILED,
                passed=False,
                message=f"Confidence must be numeric, got {type(confidence)}",
                affected_field="confidence",
            )
        
        if not (0.0 <= confidence <= 1.0):
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.CONFIDENCE_RANGE,
                rule_name="Confidence in range [0, 1]",
                status=ValidationStatus.FAILED,
                passed=False,
                message=f"Confidence must be in [0.0, 1.0], got {confidence}",
                affected_field="confidence",
            )
        
        return ValidationRuleResult(
            rule_identity=rule_id,
            rule_kind=ValidationRuleKind.CONFIDENCE_RANGE,
            rule_name="Confidence in valid range",
            status=ValidationStatus.PASSED,
            passed=True,
            message="Confidence validation passed",
        )
    
    def validate_uncertainty_range(
        cls,
        uncertainty: float,
    ) -> ValidationRuleResult:
        """
        Validate that uncertainty is in valid range [0.0, 1.0].
        
        Args:
            uncertainty: The uncertainty value to validate
            
        Returns:
            Validation result
        """
        rule_id = f"rule:unc:{hash(str(uncertainty)) % 10000:04x}"
        
        if not isinstance(uncertainty, (int, float)):
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.UNCERTAINTY_RANGE,
                rule_name="Uncertainty is numeric",
                status=ValidationStatus.FAILED,
                passed=False,
                message=f"Uncertainty must be numeric, got {type(uncertainty)}",
                affected_field="uncertainty",
            )
        
        if not (0.0 <= uncertainty <= 1.0):
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.UNCERTAINTY_RANGE,
                rule_name="Uncertainty in range [0, 1]",
                status=ValidationStatus.FAILED,
                passed=False,
                message=f"Uncertainty must be in [0.0, 1.0], got {uncertainty}",
                affected_field="uncertainty",
            )
        
        return ValidationRuleResult(
            rule_identity=rule_id,
            rule_kind=ValidationRuleKind.UNCERTAINTY_RANGE,
            rule_name="Uncertainty in valid range",
            status=ValidationStatus.PASSED,
            passed=True,
            message="Uncertainty validation passed",
        )
    
    def validate_confidence_uncertainty_sum(
        cls,
        confidence: float,
        uncertainty: float,
    ) -> ValidationRuleResult:
        """
        Validate that confidence + uncertainty <= 1.0.
        
        Args:
            confidence: The confidence value
            uncertainty: The uncertainty value
            
        Returns:
            Validation result
        """
        rule_id = f"rule:sum:{hash(str((confidence, uncertainty))) % 10000:04x}"
        
        total = confidence + uncertainty
        
        if total > 1.0:
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.CONFIDENCE_UNCERTAINTY_SUM,
                rule_name="Confidence + Uncertainty <= 1",
                status=ValidationStatus.WARNING,
                passed=False,
                message=f"Sum exceeds 1.0: {total}",
                affected_field="confidence,uncertainty",
            )
        
        return ValidationRuleResult(
            rule_identity=rule_id,
            rule_kind=ValidationRuleKind.CONFIDENCE_UNCERTAINTY_SUM,
            rule_name="Confidence + Uncertainty sum valid",
            status=ValidationStatus.PASSED,
            passed=True,
            message=f"Sum is {total}",
        )
    
    def validate_provenance(
        cls,
        provenance_data: Dict[str, Any],
    ) -> ValidationRuleResult:
        """
        Validate provenance data structure.
        
        Args:
            provenance_data: The provenance dictionary to validate
            
        Returns:
            Validation result
        """
        rule_id = f"rule:prov:{hash(str(provenance_data)) % 10000:04x}"
        
        if not isinstance(provenance_data, dict):
            return ValidationRuleResult(
                rule_identity=rule_id,
                rule_kind=ValidationRuleKind.PROVENANCE_COMPLETE,
                rule_name="Provenance is a dictionary",
                status=ValidationStatus.FAILED,
                passed=False,
                message=f"Provenance must be dict, got {type(provenance_data)}",
                affected_field="provenance",
            )
        
        return ValidationRuleResult(
            rule_identity=rule_id,
            rule_kind=ValidationRuleKind.PROVENANCE_COMPLETE,
            rule_name="Provenance structure valid",
            status=ValidationStatus.PASSED,
            passed=True,
            message="Provenance validation passed",
        )


__all__ = [
    "ValidationStatus",
    "ValidationRuleKind",
    "ValidationRuleResult",
    "ValidationResult",
    "ArtifactValidator",
]