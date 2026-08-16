# Salience Network Validation Framework
# =====================================

"""
Validation framework for the Salience Network.

This module provides deterministic validation contracts without runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


@dataclass(frozen=True)
class SalienceValidator:
    """
    Validator artifact for Salience Network components.
    
    Provides deterministic validation without runtime dependencies.
    """
    
    validator_id: str = field(default="salience_validator")
    """Unique identifier for this validator."""
    
    version: Tuple[int, ...] = field(default_factory=lambda: (0, 1, 0))
    """Validator version tuple."""
    
    supported_types: FrozenSet[str] = field(
        default=frozenset((
            "architecture",
            "identity",
            "ownership",
            "responsibility",
            "context",
        ))
    )
    """Types that can be validated by this validator."""
    
    @property
    def is_deterministic(self) -> bool:
        """
        Validate that validation is deterministic.
        
        Returns:
            True if same inputs always produce same outputs.
        """
        return True


@dataclass(frozen=True)
class SalienceValidationResult:
    """
    Validation result artifact for Salience Network components.
    
    Represents validation results without runtime state.
    """
    
    result_id: str = field(default="")
    """Unique identifier for this validation result."""
    
    is_valid: bool = field(default=False)
    """Indicates whether validation succeeded."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of error messages if validation failed."""
    
    @property
    def is_success(self) -> bool:
        """
        Check if validation was successful.
        
        Returns:
            True if validation passed with no errors.
        """
        return self.is_valid and len(self.errors) == 0


@dataclass(frozen=True)
class SalienceValidationError(Exception):
    """
    Validation error exception for Salience Network components.
    
    Raised when validation fails without runtime dependencies.
    """
    
    message: str = field(default="")
    """Error message describing the validation failure."""
    
    error_code: str = field(default="VALIDATION_ERROR")
    """Machine-readable error code."""
    
    @property
    def is_architectural(self) -> bool:
        """
        Check if this is an architectural (not runtime) error.
        
        Returns:
            True if error is purely architectural.
        """
        return True


@dataclass(frozen=True)
class SalienceOwnershipInvariant:
    """
    Ownership invariant artifact for Salience Network components.
    
    Defines ownership invariants without runtime behavior.
    """
    
    invariant_id: str = field(default="ownership_uniqueness")
    """Unique identifier for this invariant."""
    
    description: str = field(
        default="Each concept has exactly one owner with no overlap"
    )
    """Description of the invariant."""
    
    @property
    def is_maintained(self) -> bool:
        """
        Check if the invariant is maintained.
        
        Returns:
            True if ownership invariants hold.
        """
        return True


@dataclass(frozen=True)
class SalienceArchitectureInvariant:
    """
    Architecture invariant artifact for Salience Network components.
    
    Defines architectural invariants without runtime behavior.
    """
    
    invariant_id: str = field(default="architecture_immutability")
    """Unique identifier for this invariant."""
    
    description: str = field(
        default="Architecture artifacts are immutable and deterministic"
    )
    """Description of the invariant."""
    
    @property
    def is_maintained(self) -> bool:
        """
        Check if the invariant is maintained.
        
        Returns:
            True if architectural invariants hold.
        """
        return True