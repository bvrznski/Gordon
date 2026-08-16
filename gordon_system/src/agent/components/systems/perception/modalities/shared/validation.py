# Modality Validation - Phase 5.2 Pre-Activation Verification
# ===========================================================

"""
ModalityValidation: The process of verifying that a modality meets all required
conditions before activation.

Validation precedes activation and publication. It checks capabilities,
permissions, sandbox scope, calibration state, and output conformance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# VALIDATION STATUS - Outcome of validation check
# =============================================================================


class ValidationStatus(Enum):
    """
    Status of a validation check.
    
    PENDING: Validation not yet attempted
    PASSED: All checks passed
    FAILED: One or more checks failed
    PARTIAL: Some checks passed, some failed (degraded operation)
    SKIPPED: Check not applicable for this modality
    """
    
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


# =============================================================================
# VALIDATION CHECK - Individual validation item
# =============================================================================


@dataclass(frozen=True)
class ValidationCheck:
    """
    A single validation check result.
    
    Fields:
        check_name:          Name of the check
        
        status:              Status of this check
        
        message:             Human-readable description
        
        details:             Additional technical details
        
        timestamp_utc:       When the check was performed
    """
    
    # Core identity (required)
    check_name: str                     # Check identifier
    
    status: str = "pending"             # ValidationStatus value
    
    message: str = ""                   # Description
    
    details: Dict[str, Any] = field(default_factory=dict)  # Details
    
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# VALIDATION RESULT - Complete validation result
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete validation result for a modality.
    
    Fields:
        is_valid:            Overall validity (all required checks passed)
        
        status:              Overall status
        
        checks:              Tuple of individual check results
        
        failed_checks:       Checks that failed
        partial_pass_checks: Checks with partial pass
        skipped_checks:      Checks that were skipped
        
        validation_time_utc: When validation completed
        
        revision:            Result version number
    """
    
    # Core identity (required)
    is_valid: bool = False              # True if all required checks passed
    
    status: str = "pending"             # Overall ValidationStatus
    
    checks: Tuple[ValidationCheck, ...] = field(default_factory=tuple)
    
    failed_checks: Tuple[str, ...] = field(default_factory=tuple)
    partial_pass_checks: Tuple[str, ...] = field(default_factory=tuple)
    skipped_checks: Tuple[str, ...] = field(default_factory=tuple)
    
    validation_time_utc: float = field(default_factory=time.time)
    
    revision: int = 1
    
    @classmethod
    def create(
        cls,
        checks: Tuple[ValidationCheck, ...],
    ) -> "ValidationResult":
        """
        Create a validation result from individual checks.
        
        Args:
            checks: Individual validation check results
            
        Returns:
            New ValidationResult instance
        """
        failed = tuple(c.check_name for c in checks if c.status == "failed")
        partial = tuple(c.check_name for c in checks if c.status == "partial")
        skipped = tuple(c.check_name for c in checks if c.status == "skipped")
        
        # Status calculation
        if len(failed) > 0:
            status = "failed"
            is_valid = False
        elif len(partial) > 0 or len(skipped) > 0:
            status = "partial"
            is_valid = False
        elif len(checks) > 0:
            status = "passed"
            is_valid = True
        else:
            status = "pending"
            is_valid = False
        
        return cls(
            is_valid=is_valid,
            status=status,
            checks=checks,
            failed_checks=failed,
            partial_pass_checks=partial,
            skipped_checks=skipped,
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the validation result.
        
        Returns:
            Dictionary with summary information
        """
        return {
            "is_valid": self.is_valid,
            "status": self.status,
            "total_checks": len(self.checks),
            "passed_count": len(self.checks) - len(self.failed_checks) - len(self.partial_pass_checks) - len(self.skipped_checks),
            "failed_count": len(self.failed_checks),
            "partial_count": len(self.partial_pass_checks),
            "skipped_count": len(self.skipped_checks),
        }


# =============================================================================
# VALIDATOR - Interface for validation operations
# =============================================================================


class Validator:
    """
    Interface for validating modality readiness.
    
    Implementations verify:
        - Declared capabilities
        - Required permissions
        - Effective sandbox scope
        - Availability state
        - Calibration state (where applicable)
        - Source identity verification
        - Output contract conformance
        - Provenance completeness
        - Confidence validity
        - Compatibility
    """
    
    def validate_modality(
        self,
        modality_identity: str,
        capabilities: Tuple[str, ...],
        permissions: Tuple[str, ...],
        sandbox_profile: str,
        availability: str,
        calibration_state: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate a modality for activation.
        
        Args:
            modality_identity: Modality to validate
            capabilities: Declared capabilities
            permissions: Effective permissions
            sandbox_profile: Active sandbox level
            availability: Current availability state
            calibration_state: Calibration state (if applicable)
            
        Returns:
            Validation result
        """
        raise NotImplementedError
    
    def validate_output(
        self,
        modality_identity: str,
        output_type: str,
        confidence: float,
        uncertainty: float,
        provenance: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a produced output against contract.
        
        Args:
            modality_identity: Producing modality
            output_type: Type of output (observation, signal, feature, percept)
            confidence: Output confidence 0.0-1.0
            uncertainty: Output uncertainty 0.0-1.0
            provenance: Output provenance
            
        Returns:
            Tuple of (is_valid, error_message if not valid)
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "ValidationStatus",
    
    # Dataclasses
    "ValidationCheck",
    "ValidationResult",
    
    # Classes
    "Validator",
]