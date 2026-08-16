# Memory Validity - Phase 5.1 Canonical Validation State
# =======================================================

"""
Memory Validity: Explicit validation status for memory artifacts.

Every Memory Artifact possesses:
    - explicit validity (never inferred implicitly)
    - validity revision history
    - validity independent from accessibility
    - validity provenance

Validity Laws:
    VALIDITY-LAW-001: Every artifact has explicit validity
    VALIDITY-LAW-002: Validity is never inferred implicitly
    VALIDITY-LAW-003: Validity revisions preserve history
    VALIDITY-LAW-004: Validity is independent from accessibility
    VALIDITY-LAW-005: Validity is independent from confidence
    VALIDITY-LAW-006: Validity provenance is explicit
    VALIDITY-LAW-007: Historical validity states are inspectable
    VALIDITY-LAW-008: Validity evaluation is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid

# Import from other modules (runtime imports to handle circular dependencies)
try:
    from .provenance import MemoryProvenance
except ImportError:
    class MemoryProvenance:
        pass
try:
    from .revision import MemoryRevision
except ImportError:
    class MemoryRevision:
        pass


# =============================================================================
# MEMORY VALIDITY STATUS - Explicit validity states
# =============================================================================


class MemoryValidityStatus(Enum):
    """
    Validity status of a memory artifact.
    
    These are EXPLICIT states, never inferred:
        
        VALID:           Content passes all validation checks
        PARTIALLY_VALID: Some aspects valid, others not
        SUPERSEDED:      Replaced by newer revision
        EXPIRED:         No longer applicable (time-based)
        DISPUTED:        Validity is contested
        INVALID:         Validation failed
        UNKNOWN:         Status not yet determined
    """
    
    VALID = "valid"
    PARTIALLY_VALID = "partially_valid"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    DISPUTED = "disputed"
    INVALID = "invalid"
    UNKNOWN = "unknown"


# =============================================================================
# VALIDATION CHECK - Individual validation result
# =============================================================================


@dataclass(frozen=True)
class ValidationCheck:
    """
    Result of a single validation check.
    
    Fields:
        check_name:      What was checked?
        passed:          Did it pass?
        details:         Additional information (optional)
        timestamp_utc:   When the check was performed
    """
    
    check_name: str           # Name of the validation check
    passed: bool              # Did it pass?
    details: Optional[str] = None  # Additional context
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# VALIDATION RESULT - Complete validation outcome
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating an artifact.
    
    Fields:
        is_valid:              Overall validation result
        checks_performed:      List of all checks run
        passed_checks:         Count of passed checks
        failed_checks:         Count of failed checks
        
        failure_reasons:       Why did it fail (if applicable)
        
        # Provenance
        validated_by:          Who/what performed validation?
        validated_at_utc:      When was it validated?
        
        # Revision tracking
        revision_id:           Which revision was validated?
    """
    
    is_valid: bool                         # Overall result
    
    checks_performed: Tuple[str, ...]     # List of check names run
    passed_checks: int = 0                # Count of passed checks
    failed_checks: int = 0                # Count of failed checks
    
    failure_reasons: Tuple[str, ...] = field(default_factory=tuple)
    
    validated_by: Optional[str] = None
    validated_at_utc: float = field(default_factory=time.time)
    
    revision_id: Optional[str] = None
    
    @property
    def total_checks(self) -> int:
        """Total number of checks performed."""
        return self.passed_checks + self.failed_checks
    
    @classmethod
    def valid(
        cls,
        validated_by: Optional[str] = None,
        revision_id: Optional[str] = None,
    ) -> "ValidationResult":
        """
        Create a valid validation result.
        
        Args:
            validated_by: Who performed validation? (optional)
            revision_id: Which revision was validated? (optional)
            
        Returns:
            ValidationResult with is_valid=True
        """
        return cls(
            is_valid=True,
            checks_performed=tuple(),
            passed_checks=0,
            failed_checks=0,
            validated_by=validated_by,
            validated_at_utc=time.time(),
            revision_id=revision_id,
        )
    
    @classmethod
    def invalid(
        cls,
        failure_reasons: Tuple[str, ...],
        validated_by: Optional[str] = None,
        revision_id: Optional[str] = None,
    ) -> "ValidationResult":
        """
        Create an invalid validation result.
        
        Args:
            failure_reasons: Why did it fail?
            validated_by: Who performed validation? (optional)
            revision_id: Which revision was validated? (optional)
            
        Returns:
            ValidationResult with is_valid=False
        """
        return cls(
            is_valid=False,
            checks_performed=tuple(),
            passed_checks=0,
            failed_checks=len(failure_reasons),
            failure_reasons=failure_reasons,
            validated_by=validated_by,
            validated_at_utc=time.time(),
            revision_id=revision_id,
        )


# =============================================================================
# MEMORY VALIDITY - Explicit validity state
# =============================================================================


@dataclass(frozen=True)
class MemoryValidity:
    """
    Explicit validity state for a memory artifact.
    
    Validity is an EXPLICIT property that does NOT depend on confidence,
    accessibility, or any other factor. An artifact can be valid but inactive,
    or invalid but currently active.
    
    Fields:
        status:           Current validity status
        validated_at_utc: When was this validated?
        
        # Revision tracking
        revision_id:      Which revision is this valid for?
        previous_validity: Reference to prior validity state
        
        # Validation details
        validation_result: Full validation outcome
        
        # Provenance
        validated_by:     Who/what performed the validation?
    """
    
    status: MemoryValidityStatus           # Current explicit validity
    
    validated_at_utc: float = field(default_factory=time.time)
    
    # Revision tracking
    revision_id: Optional[str] = None
    previous_validity_id: Optional[str] = None
    
    # Validation details
    validation_result: ValidationResult = field(
        default_factory=lambda: ValidationResult(
            is_valid=False,
            checks_performed=tuple(),
            passed_checks=0,
            failed_checks=0,
        )
    )
    
    # Provenance
    validated_by: Optional[str] = None
    
    @classmethod
    def valid(
        cls,
        revision_id: Optional[str] = None,
        validated_by: Optional[str] = None,
    ) -> "MemoryValidity":
        """
        Create a valid validity state.
        
        Args:
            revision_id: Which revision is this for? (optional)
            validated_by: Who performed validation? (optional)
            
        Returns:
            MemoryValidity with VALID status
        """
        return cls(
            status=MemoryValidityStatus.VALID,
            revision_id=revision_id,
            validated_by=validated_by,
            validation_result=ValidationResult.valid(validated_by, revision_id),
        )
    
    @classmethod
    def partially_valid(
        cls,
        details: str,
        revision_id: Optional[str] = None,
        validated_by: Optional[str] = None,
    ) -> "MemoryValidity":
        """
        Create a partially valid validity state.
        
        Args:
            details: What's the partial validity situation?
            revision_id: Which revision is this for? (optional)
            validated_by: Who performed validation? (optional)
            
        Returns:
            MemoryValidity with PARTIALLY_VALID status
        """
        return cls(
            status=MemoryValidityStatus.PARTIALLY_VALID,
            revision_id=revision_id,
            validated_by=validated_by,
            validation_result=ValidationResult.invalid(
                failure_reasons=(f"Partial validity: {details}",),
                validated_by=validated_by,
                revision_id=revision_id,
            ),
        )
    
    @classmethod
    def invalid(
        cls,
        reason: str,
        revision_id: Optional[str] = None,
        validated_by: Optional[str] = None,
    ) -> "MemoryValidity":
        """
        Create an invalid validity state.
        
        Args:
            reason: Why is it invalid?
            revision_id: Which revision is this for? (optional)
            validated_by: Who performed validation? (optional)
            
        Returns:
            MemoryValidity with INVALID status
        """
        return cls(
            status=MemoryValidityStatus.INVALID,
            revision_id=revision_id,
            validated_by=validated_by,
            validation_result=ValidationResult.invalid(
                failure_reasons=(reason,),
                validated_by=validated_by,
                revision_id=revision_id,
            ),
        )
    
    @classmethod
    def unknown(
        cls,
        revision_id: Optional[str] = None,
    ) -> "MemoryValidity":
        """
        Create an unknown validity state.
        
        Args:
            revision_id: Which revision is this for? (optional)
            
        Returns:
            MemoryValidity with UNKNOWN status
        """
        return cls(
            status=MemoryValidityStatus.UNKNOWN,
            revision_id=revision_id,
            validation_result=ValidationResult(
                is_valid=False,
                checks_performed=tuple(),
                passed_checks=0,
                failed_checks=0,
            ),
        )
    
    def validate(self) -> "MemoryValidity":
        """Mark as validated (assuming it was already validated)."""
        return dataclass_replace(
            self,
            status=MemoryValidityStatus.VALID,
            validated_at_utc=time.time(),
            validation_result=self.validation_result,
        )
    
    def invalidate(self, reason: str) -> "MemoryValidity":
        """Mark as invalid."""
        return dataclass_replace(
            self,
            status=MemoryValidityStatus.INVALID,
            validated_at_utc=time.time(),
            validation_result=ValidationResult.invalid((reason,), self.validated_by, self.revision_id),
        )
    
    def is_valid(self) -> bool:
        """Check if this artifact is currently valid."""
        return self.status in (MemoryValidityStatus.VALID, MemoryValidityStatus.PARTIALLY_VALID)


# =============================================================================
# MEMORY VALIDATION - Validation operations
# =============================================================================


class MemoryValidation:
    """
    Validation operations for memory artifacts.
    
    This class provides validation functionality without modifying artifacts.
    All validations are side-effect free.
    """
    
    @staticmethod
    def validate_identity(identity: str) -> Tuple[bool, List[str]]:
        """
        Validate an artifact identity.
        
        Args:
            identity: The identity to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not identity or len(identity) == 0:
            errors.append("Identity cannot be empty")
        
        if len(identity) > 256:
            errors.append("Identity is too long (>256 chars)")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def validate_provenance(provenance: Optional[MemoryProvenance]) -> Tuple[bool, List[str]]:
        """
        Validate provenance completeness.
        
        Args:
            provenance: The provenance to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if provenance is None:
            errors.append("Provenance is required")
            return (False, errors)
        
        # Basic validation - could add more checks
        return (provenance.is_complete, errors)
    
    @staticmethod
    def validate_revision(
        revision: MemoryRevision,
        previous_revision_id: Optional[str],
    ) -> Tuple[bool, List[str]]:
        """
        Validate a revision record.
        
        Args:
            revision: The revision to validate
            previous_revision_id: The ID it's supposed to supersede
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if not revision.revision_identity:
            errors.append("Revision identity is required")
        
        # Check lineage consistency if we have a previous ID
        if previous_revision_id and revision.previous_revision_id != previous_revision_id:
            errors.append(
                f"Previous revision mismatch: expected {previous_revision_id}, "
                f"got {revision.previous_revision_id}"
            )
        
        return (len(errors) == 0, errors)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryValidity, **kwargs) -> MemoryValidity:
    """Replace fields in a frozen dataclass."""
    return MemoryValidity(
        status=kwargs.get("status", instance.status),
        validated_at_utc=kwargs.get("validated_at_utc", instance.validated_at_utc),
        revision_id=kwargs.get("revision_id", instance.revision_id),
        previous_validity_id=kwargs.get("previous_validity_id", instance.previous_validity_id),
        validation_result=kwargs.get("validation_result", instance.validation_result),
        validated_by=kwargs.get("validated_by", instance.validated_by),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryValidity",
    "MemoryValidityStatus",
    "ValidationCheck",
    "ValidationResult",
    "MemoryValidation",
    "dataclass_replace",
]