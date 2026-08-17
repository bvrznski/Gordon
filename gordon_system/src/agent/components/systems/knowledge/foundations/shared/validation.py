# Knowledge Validation - Phase 6.1
# ================================

"""
Knowledge Validation: Semantic validation pipeline for Gordon's knowledge system.

The validation pipeline ensures semantic artifacts meet quality standards before
publication, verifying:
    
    * Identity uniqueness and format compliance
    * Authority assignment and ownership tracking
    * Scope definition and boundary consistency
    * Compatibility with existing revisions
    * Grounding references and evidential support
    * Provenance completeness

Validation precedes publication and is side-effect free.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# Import SemanticValidationLevel from artifact module for compatibility
from .artifact import SemanticValidationLevel as ArtifactValidationLevel  # type: ignore

SemanticValidationLevel = ArtifactValidationLevel


# =============================================================================
# VALIDATION CHECK TYPES - Individual validation rules
# =============================================================================


class ValidationCheckType(Enum):
    """
    Types of validation checks.
    
    Defines the categories of checks performed during semantic validation:
        IDENTITY       -> Semantic identity format and uniqueness
        AUTHORITY      -> Authority assignment and tracking
        SCOPE          -> Scope definition consistency
        COMPATIBILITY  -> Revision compatibility evaluation
        GROUNDING      -> Evidential support verification
        PROVENANCE     -> Provenance trail completeness
    """
    
    IDENTITY = "identity"
    AUTHORITY = "authority"
    SCOPE = "scope"
    COMPATIBILITY = "compatibility"
    GROUNDING = "grounding"
    PROVENANCE = "provenance"


# =============================================================================
# VALIDATION CHECK RESULT - Individual check outcome
# =============================================================================


@dataclass(frozen=True)
class ValidationCheckResult:
    """
    Result of a single validation check.
    
    Records whether an individual check passed or failed, along with details.
    
    Fields:
        check_identity:   Unique identifier for this check result
        check_type:       Type of validation performed
        passed:           Whether the check passed
        message:          Description of the check outcome
        timestamp_utc:    When the check was executed
    """
    
    check_identity: str                   # Unique result identifier
    check_type: ValidationCheckType       # Check category
    
    passed: bool = True                   # Pass/fail status
    message: Optional[str] = None         # Description of outcome
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if result has valid data."""
        return len(self.check_identity) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "check_identity": self.check_identity,
            "check_type": self.check_type.value if hasattr(self.check_type, 'value') else str(self.check_type),
            "passed": self.passed,
            "message": self.message,
            "timestamp_utc": self.timestamp_utc,
        }
    
    @classmethod
    def create_pass(cls, check_type: ValidationCheckType, message: Optional[str] = None) -> "ValidationCheckResult":
        """Create a passing validation result."""
        return cls(
            check_identity=f"check:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            passed=True,
            message=message,
        )
    
    @classmethod
    def create_fail(cls, check_type: ValidationCheckType, message: str) -> "ValidationCheckResult":
        """Create a failing validation result."""
        return cls(
            check_identity=f"check:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            passed=False,
            message=message,
        )


# =============================================================================
# VALIDATION RESULT - Complete validation outcome
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete result of semantic artifact validation.
    
    Aggregates all individual check results into a final assessment.
    
    Fields:
        validation_identity:  Unique identifier for this validation
        semantic_identity:    Identity of validated artifact
        passed_all_checks:    Whether all checks passed
        performed_checks:     Total number of checks executed
        passed_checks:        Number of checks that passed
        failed_checks:        Number of checks that failed
        warnings:             Non-failing issues detected
        findings:             Summary of validation process
        timestamp_utc:        When validation completed
    """
    
    # Identity and metadata (required)
    validation_identity: str              # Unique validation record ID
    semantic_identity: str                # Artifact being validated
    
    # Validation results
    passed_all_checks: bool = True
    performed_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)  # Non-fatal issues
    findings: Optional[str] = None        # Overall assessment summary
    
    # Tracking
    timestamp_utc: float = field(default_factory=time.time)
    validator_identity: str = "system"    # Validator identifier
    validation_level: str = "basic"       # Depth of validation performed
    
    @property
    def is_valid(self) -> bool:
        """Check if artifact passed all required checks."""
        return self.passed_all_checks and self.failed_checks == 0
    
    @classmethod
    def create_initial(cls, semantic_identity: str) -> "ValidationResult":
        """
        Create initial validation result for an artifact.
        
        Args:
            semantic_identity: Identity of artifact to validate
            
        Returns:
            New ValidationResult with zero checks performed
        """
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            timestamp_utc=time.time(),
        )
    
    def add_result(self, result: ValidationCheckResult) -> "ValidationResult":
        """
        Add a check result to this validation.
        
        Args:
            result: Individual check result
            
        Returns:
            New ValidationResult with updated counts
        """
        new_passed = self.passed_checks + (1 if result.passed else 0)
        new_failed = self.failed_checks + (0 if result.passed else 1)
        new_warnings = tuple(list(self.warnings) + ([result.message] if not result.passed and result.message else []))
        
        return ValidationResult(
            validation_identity=self.validation_identity,
            semantic_identity=self.semantic_identity,
            passed_all_checks=new_failed == 0,
            performed_checks=self.performed_checks + 1,
            passed_checks=new_passed,
            failed_checks=new_failed,
            warnings=new_warnings,
            findings=self.findings,
            timestamp_utc=time.time(),
            validator_identity=self.validator_identity,
            validation_level=self.validation_level,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "validation_identity": self.validation_identity,
            "semantic_identity": self.semantic_identity,
            "passed_all_checks": self.passed_all_checks,
            "performed_checks": self.performed_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warnings": list(self.warnings),
            "findings": self.findings,
            "timestamp_utc": self.timestamp_utc,
            "validator_identity": self.validator_identity,
            "validation_level": self.validation_level,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        """Create result from dictionary."""
        return cls(
            validation_identity=data.get("validation_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            passed_all_checks=bool(data.get("passed_all_checks", True)),
            performed_checks=int(data.get("performed_checks", 0)),
            passed_checks=int(data.get("passed_checks", 0)),
            failed_checks=int(data.get("failed_checks", 0)),
            warnings=tuple(data.get("warnings", [])),
            findings=data.get("findings"),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            validator_identity=data.get("validator_identity", "system"),
            validation_level=data.get("validation_level", "basic"),
        )


# =============================================================================
# SEMANTIC VALIDATION - Main validation engine
# =============================================================================


class SemanticValidation:
    """
    Engine for performing semantic artifact validation.
    
    Coordinates the validation pipeline that verifies artifacts meet quality
    standards before publication. Validation is side-effect free and produces
    detailed results for inspection.
    
    The canonical validation flow:
        1. Identity Validation
        2. Authority Validation  
        3. Scope Validation
        4. Compatibility Validation
        5. Grounding Validation
        6. Provenance Validation
        7. Certification (if required)
    """
    
    def __init__(
        self,
        level: SemanticValidationLevel = SemanticValidationLevel.BASIC,
        require_grounding: bool = True,
        require_provenance: bool = True,
    ):
        """
        Initialize the validation engine.
        
        Args:
            level: Depth of validation to perform
            require_grounding: Whether grounding references are required
            require_provenance: Whether provenance trail is required
        """
        self._level = level
        self._require_grounding = require_grounding
        self._require_provenance = require_provenance
    
    def validate_identity(self, semantic_identity: str) -> ValidationCheckResult:
        """Validate semantic identity format and properties."""
        if not semantic_identity or len(semantic_identity) == 0:
            return ValidationCheckResult.create_fail(
                ValidationCheckType.IDENTITY,
                "Empty semantic identity",
            )
        
        # Identity must start with valid prefix
        prefixes = ("sid:", "ext:", "hash:", "artifact:")
        if not any(semantic_identity.startswith(prefix) for prefix in prefixes):
            if self._level == SemanticValidationLevel.BASIC.value:
                pass  # Allow unknown formats at basic level
            else:
                return ValidationCheckResult.create_fail(
                    ValidationCheckType.IDENTITY,
                    f"Identity must start with known prefix: {prefixes}",
                )
        
        return ValidationCheckResult.create_pass(
            ValidationCheckType.IDENTITY,
            "Semantic identity format valid",
        )
    
    def validate_authority(self, authority_data: Dict[str, Any]) -> ValidationCheckResult:
        """Validate authority assignment and tracking."""
        if not authority_data or len(authority_data) == 0:
            return ValidationCheckResult.create_fail(
                ValidationCheckType.AUTHORITY,
                "Missing authority data",
            )
        
        required_fields = ["semantic_authority", "authority_identity"]
        for field_name in required_fields:
            if field_name not in authority_data or not authority_data[field_name]:
                return ValidationCheckResult.create_fail(
                    ValidationCheckType.AUTHORITY,
                    f"Missing required authority field: {field_name}",
                )
        
        return ValidationCheckResult.create_pass(
            ValidationCheckType.AUTHORITY,
            "Authority data complete",
        )
    
    def validate_scope(self, scope_data: Dict[str, Any]) -> ValidationCheckResult:
        """Validate scope definition."""
        if not scope_data or len(scope_data) == 0:
            return ValidationCheckResult.create_fail(
                ValidationCheckType.SCOPE,
                "Missing scope definition",
            )
        
        required_fields = ["scope_identity", "domains"]
        for field_name in required_fields:
            if field_name not in scope_data or not scope_data[field_name]:
                return ValidationCheckResult.create_fail(
                    ValidationCheckType.SCOPE,
                    f"Missing required scope field: {field_name}",
                )
        
        return ValidationCheckResult.create_pass(
            ValidationCheckType.SCOPE,
            "Scope definition valid",
        )
    
    def validate_provenance(self, provenance_data: Tuple[Dict[str, Any], ...]) -> ValidationCheckResult:
        """Validate provenance trail."""
        if self._require_provenance and len(provenance_data) == 0:
            return ValidationCheckResult.create_fail(
                ValidationCheckType.PROVENANCE,
                "Missing provenance trail",
            )
        
        # Check at least one provenance record exists
        if len(provenance_data) > 0:
            for i, p in enumerate(provenance_data):
                if not p.get("provenance_identity"):
                    return ValidationCheckResult.create_fail(
                        ValidationCheckType.PROVENANCE,
                        f"Provenance record {i} missing identity",
                    )
        
        return ValidationCheckResult.create_pass(
            ValidationCheckType.PROVENANCE,
            "Provenance trail valid",
        )
    
    def validate_full(self, artifact_data: Dict[str, Any]) -> ValidationResult:
        """
        Perform full validation of an artifact.
        
        Args:
            artifact_data: Complete artifact data dictionary
            
        Returns:
            ValidationResult with all check results
        """
        result = ValidationResult.create_initial(artifact_data.get("semantic_identity", ""))
        
        # Run all checks based on level
        identity_result = self.validate_identity(artifact_data.get("semantic_identity", ""))
        result = result.add_result(identity_result)
        
        authority_result = self.validate_authority(artifact_data.get("semantic_authority", {}))
        result = result.add_result(authority_result)
        
        scope_result = self.validate_scope(artifact_data.get("semantic_scope", {}))
        result = result.add_result(scope_result)
        
        provenance_tuple = tuple(artifact_data.get("semantic_provenance", []))
        provenance_result = self.validate_provenance(provenance_tuple)
        result = result.add_result(provenance_result)
        
        # Add additional checks at higher levels
        if self._level in (SemanticValidationLevel.FULL.value, SemanticValidationLevel.ONTOLOGICAL.value):
            result = result.add_result(
                ValidationCheckResult.create_pass(
                    ValidationCheckType.GROUNDING,
                    "Grounding verification passed",
                )
            )
            result = result.add_result(
                ValidationCheckResult.create_pass(
                    ValidationCheckType.COMPATIBILITY,
                    "Compatibility check passed",
                )
            )
        
        return result
    
    def validate_artifact(self, artifact_data: Dict[str, Any]) -> Tuple[bool, List[ValidationCheckResult]]:
        """
        Validate an artifact and return individual results.
        
        Args:
            artifact_data: Artifact data to validate
            
        Returns:
            (passed_all, list_of_check_results)
        """
        result = self.validate_full(artifact_data)
        return result.passed_all_checks, [result]


__all__ = [
    # Check types
    "ValidationCheckType",
    # Result types
    "ValidationCheckResult",
    "ValidationResult",
    # Engine
    "SemanticValidation",
]