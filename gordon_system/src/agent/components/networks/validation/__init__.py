# Gordon Cognitive Architecture - Phase 4.5.2
# ===========================================
"""
Action Identity Validation Module

This package provides validators for the Action identity system:
- Identity uniqueness and integrity
- Lineage correctness
- Revision continuity
- Reference integrity
- Acyclic history verification
- Version compatibility
- Serialization integrity
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a validation operation.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    is_valid: bool = field(default=True)
    """Whether the validation passed."""
    
    errors: List[str] = field(default_factory=list)
    """List of error messages if validation failed."""
    
    warnings: List[str] = field(default_factory=list)
    """List of warning messages."""
    
    @classmethod
    def valid(cls) -> "ValidationResult":
        """Create a successful validation result."""
        return cls(is_valid=True, errors=[], warnings=[])
    
    @classmethod
    def invalid(cls, errors: List[str], warnings: Optional[List[str]] = None) -> "ValidationResult":
        """Create an invalid validation result."""
        return cls(
            is_valid=False,
            errors=list(errors),
            warnings=list(warnings or []),
        )
    
    def add_error(self, error: str) -> "ValidationResult":
        """Add an error and return new immutable instance."""
        return ValidationResult(
            is_valid=False,
            errors=[*self.errors, error],
            warnings=list(self.warnings),
        )
    
    def add_warning(self, warning: str) -> "ValidationResult":
        """Add a warning and return new immutable instance."""
        return ValidationResult(
            is_valid=self.is_valid,
            errors=list(self.errors),
            warnings=[*self.warnings, warning],
        )


__all__ = ["ValidationResult"]