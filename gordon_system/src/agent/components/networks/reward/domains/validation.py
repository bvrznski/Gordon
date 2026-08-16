# Multi-Domain Reward Engine - Validation (Phase 4.10.5)
# =========================================================

"""
Validation system for Phase 4.10.5 Multi-Domain Reward Engine.

This module provides validation functions that ensure reward domain
classifications remain deterministic, immutable, and traceable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional, List

from .domain import RewardDomain, DomainType
from .profile import RewardProfile
from .state import MultiDomainRewardState


class DomainValidationErrorType(Enum):
    """
    Types of validation errors in domain classification.
    
    VALIDATION-LAW-006: Validation findings remain typed.
    """
    
    # Request-level errors
    INVALID_REQUEST = "invalid_request"
    """Invalid request structure."""
    
    MISSING_DOMAINS = "missing_domains"
    """No domains were classified."""
    
    # Domain-level errors
    UNKNOWN_DOMAIN = "unknown_domain"
    """Unknown domain type encountered."""
    
    INVALID_CONFIDENCE = "invalid_confidence"
    """Confidence value outside valid range [0.0, 1.0]."""
    
    INVALIDUncertainty = "invalid_uncertainty"
    """Uncertainty value outside valid range [0.0, 1.0]."""
    
    # Profile-level errors
    INVALID_PROFILE = "invalid_profile"
    """Invalid reward profile structure."""
    
    SCALAR_COLLAPSE = "scalar_collapse"
    """Domains collapsed into scalar (forbidden)."""
    
    # State-level errors
    INVALID_STATE = "invalid_state"
    """Invalid multi-domain state structure."""
    
    MUTABLE_OBJECT = "mutable_object"
    """Mutable object found in immutable context."""
    
    # System errors
    UNKNOWN = "unknown"
    """Unknown error type."""


@dataclass(frozen=True)
class DomainValidationResult:
    """
    Result of a domain validation operation.
    
    VALIDATION-LAW-001: Validation precedes classification.
    VALIDATION-LAW-002: Validation follows profile construction.
    VALIDATION-LAW-003: Validation precedes MultiDomainRewardState construction.
    VALIDATION-LAW-004: Validation remains side-effect free.
    VALIDATION-LAW-005: Validation shall never mutate semantic models.
    
    PROPERTIES:
        • is_valid: Whether validation passed
        • errors: List of validation errors found
        • findings: List of validation findings
        • trace: Trace of validation operations
    
    NOT RESPONSIBLE FOR:
        • Modifying input objects
        • Generating motivation
    """
    
    is_valid: bool = True
    """Whether validation passed."""
    
    errors: Tuple[DomainValidationErrorType, ...] = field(default_factory=tuple)
    """List of validation errors found."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation findings."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Trace of validation operations."""
    
    def merge(self, other: DomainValidationResult) -> DomainValidationResult:
        """Merge another validation result into this one."""
        if not other.is_valid:
            return DomainValidationResult(
                is_valid=False,
                errors=self.errors + other.errors,
                findings=self.findings + other.findings,
                trace=self.trace + other.trace,
            )
        return self
    
    def to_dict(self) -> dict:
        """Convert result to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "errors": [e.value for e in self.errors],
            "findings": list(self.findings),
        }
    
    @classmethod
    def success(cls, findings: Tuple[str, ...] = ()) -> DomainValidationResult:
        """Create a successful validation result."""
        return cls(is_valid=True, findings=findings)
    
    @classmethod
    def failure(
        cls,
        errors: Tuple[DomainValidationErrorType, ...],
        findings: Tuple[str, ...] = (),
    ) -> DomainValidationResult:
        """Create a failed validation result."""
        return cls(is_valid=False, errors=errors, findings=findings)


class DomainValidator:
    """
    Validator for reward domain classifications.
    
    VALIDATION-LAW-007: Validation ordering remains deterministic.
    VALIDATION-LAW-008: Validation shall reject inconsistent Reward Profiles explicitly.
    
    PROPERTIES:
        • validates domains
        • validates profiles  
        • validates states
    
    NOT RESPONSIBLE FOR:
        • Modifying input objects
        • Generating motivation
    """
    
    @staticmethod
    def validate_domain(domain: RewardDomain) -> DomainValidationResult:
        """Validate a single reward domain."""
        findings = []
        errors = []
        
        # Validate confidence range
        if not (0.0 <= domain.confidence <= 1.0):
            errors.append(DomainValidationErrorType.INVALID_CONFIDENCE)
            findings.append(f"INVALID_CONFIDENCE:{domain.confidence}")
        
        # Validate uncertainty range
        if not (0.0 <= domain.uncertainty <= 1.0):
            errors.append(DomainValidationErrorType.INVALIDUncertainty)
            findings.append(f"INVALID_UNCERTAINTY:{domain.uncertainty}")
        
        # Validate confidence + uncertainty <= 1.1 (allow small floating point error)
        if domain.confidence + domain.uncertainty > 1.1:
            errors.append(DomainValidationErrorType.INVALIDUncertainty)
            findings.append("CONFIDENCE_PLUS_UNCERTAINTY_EXCEEDS_ONE")
        
        return DomainValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            findings=tuple(findings),
            trace=("DOMAIN_VALIDATED",),
        )
    
    @staticmethod
    def validate_profile(profile: RewardProfile) -> DomainValidationResult:
        """Validate a reward profile."""
        findings = list(profile.findings)
        errors = []
        
        # Check for scalar collapse (forbidden by PROFILE-LAW-008)
        if hasattr(profile, "scalar_value"):
            errors.append(DomainValidationErrorType.SCALAR_COLLAPSE)
            findings.append("SCALAR_COLLAPSE_DETECTED")
        
        # Validate each domain profile
        for dp in profile.domain_profiles:
            result = DomainValidator.validate_domain(
                RewardDomain(
                    domain_type=dp.domain_type,
                    confidence=dp.confidence,
                    uncertainty=dp.uncertainty,
                )
            )
            if not result.is_valid:
                errors.extend(result.errors)
                findings.extend(result.findings)
        
        return DomainValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            findings=tuple(findings),
            trace=("PROFILE_VALIDATED",),
        )
    
    @staticmethod
    def validate_state(state: MultiDomainRewardState) -> DomainValidationResult:
        """Validate a multi-domain reward state."""
        findings = list(state.findings)
        errors = []
        
        # Validate the contained profile
        profile_result = DomainValidator.validate_profile(state.reward_profile)
        if not profile_result.is_valid:
            errors.extend(profile_result.errors)
            findings.extend(profile_result.findings)
        
        return DomainValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            findings=tuple(findings),
            trace=("STATE_VALIDATED",),
        )


def validate_domain(domain: RewardDomain) -> bool:
    """Validate a domain and return success/failure boolean."""
    result = DomainValidator.validate_domain(domain)
    return result.is_valid


def validate_profile(profile: RewardProfile) -> bool:
    """Validate a profile and return success/failure boolean."""
    result = DomainValidator.validate_profile(profile)
    return result.is_valid


def validate_state(state: MultiDomainRewardState) -> bool:
    """Validate a state and return success/failure boolean."""
    result = DomainValidator.validate_state(state)
    return result.is_valid


__all__ = [
    "DomainValidationErrorType",
    "DomainValidationResult",
    "DomainValidator",
    "validate_domain",
    "validate_profile",
    "validate_state",
]