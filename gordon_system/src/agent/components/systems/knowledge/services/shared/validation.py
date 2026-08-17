"""Service Validation - Phase 6.9 Part 2.

This module implements validation utilities for knowledge services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# VALIDATION RESULT - Phase 6.9 Service Validation
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of service validation.
    
    Fields:
        result_identity: Unique identifier for this result
        check_type: Type of check that was performed
        status: Pass, fail, or warning
        message: Human-readable description
    """
    
    result_identity: str
    check_type: str
    status: str  # "pass", "fail", "warning"
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "result_identity": self.result_identity,
            "check_type": self.check_type,
            "status": self.status,
            "message": self.message,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ValidationResult:
        """Create validation result from dictionary."""
        return cls(
            result_identity=data.get("result_identity", str(uuid.uuid4())),
            check_type=data.get("check_type", "unknown"),
            status=data.get("status", "pass"),
            message=data.get("message", ""),
        )
    
    @classmethod
    def create_pass(cls, check_type: str, message: str = "") -> "ValidationResult":
        """Create a passing validation result."""
        return cls(
            result_identity=f"result:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            status="pass",
            message=message,
        )
    
    @classmethod
    def create_fail(cls, check_type: str, message: str = "") -> "ValidationResult":
        """Create a failing validation result."""
        return cls(
            result_identity=f"result:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            status="fail",
            message=message,
        )
    
    @classmethod
    def create_warning(cls, check_type: str, message: str = "") -> "ValidationResult":
        """Create a warning validation result."""
        return cls(
            result_identity=f"result:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            status="warning",
            message=message,
        )


# =============================================================================
# SERVICE VALIDATION - Phase 6.9
# =============================================================================


@dataclass(frozen=True)
class ServiceValidation:
    """
    Validation result for a knowledge service.
    
    Fields:
        validation_identity: Unique identifier for this validation
        validated_service: Service that was validated
        
    Invariants:
        * Validation is observational only
        * Results are traceable
    """
    
    validation_identity: str  # Unique identifier
    
    validated_service: Dict[str, Any]
    
    results: Tuple[ValidationResult, ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate after creation."""
        if not self.validation_identity:
            raise ValueError("validation_identity cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if all validation checks passed."""
        return all(r.status == "pass" for r in self.results)
    
    @classmethod
    def create_initial(
        cls,
        service: Dict[str, Any],
    ) -> "ServiceValidation":
        """
        Create initial service validation.
        
        Args:
            service: Service to validate
            
        Returns:
            New ServiceValidation ready for checks
        """
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            validated_service=dict(service),
        )
    
    def add_result(
        self,
        result: ValidationResult,
    ) -> "ServiceValidation":
        """Add a validation result."""
        return ServiceValidation(
            validation_identity=self.validation_identity,
            validated_service=dict(self.validated_service),
            results=tuple(list(self.results) + [result]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation to dictionary."""
        return {
            "validation_identity": self.validation_identity,
            "validated_service": dict(self.validated_service),
            "results": [r.to_dict() for r in self.results],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceValidation":
        """Create validation from dictionary."""
        return cls(
            validation_identity=data.get("validation_identity", str(uuid.uuid4())),
            validated_service=dict(data.get("validated_service", {})),
            results=tuple(ValidationResult.from_dict(r) for r in data.get("results", []) if isinstance(r, dict)),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Validation result
    "ValidationResult",
    # Service validation
    "ServiceValidation",
]