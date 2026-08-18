# Experimental Reasoning - Validation
# ====================================

"""
Canonical Validation contracts.

Validation assesses the feasibility and quality of experiment designs.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating an experiment design.
    
    Validation remains observational - it never modifies experimental artifacts directly.
    """
    
    # Identity
    validation_id: str                          # Unique identifier
    experiment_identity: str                    # Which experiment was validated?
    
    # Validation result
    is_valid: bool = False                      # Overall validation outcome
    
    # Validation details
    valid_components: Tuple[str, ...] = ()      # Components that passed validation
    invalid_components: Tuple[str, ...] = ()    # Components that failed validation
    
    # Quality metrics
    design_quality_score: float = 0.0           # 0-1 scale
    completeness_score: float = 0.0             # How complete is the design?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @property
    def validation_status(self) -> str:
        """Get human-readable status."""
        if self.is_valid:
            return "valid"
        elif self.invalid_components:
            return f"invalid: {', '.join(self.invalid_components)}"
        else:
            return "indeterminate"


@dataclass(frozen=True)
class ValidationIssue:
    """
    A specific issue found during validation.
    
    Issues are categorized by severity and type.
    """
    
    # Identity
    issue_id: str                               # Unique identifier
    
    # Issue details
    component_name: str                         # Which component has the issue?
    issue_type: str = "warning"                 # "error", "warning", "info"
    description: str = ""                       # What is wrong?
    
    # Severity (0-1, higher is more severe)
    severity: float = 0.5
    
    # Recommended fix
    recommended_fix: Optional[str] = None       # How to fix this issue?
    
    @property
    def is_error(self) -> bool:
        """Check if this is an error-level issue."""
        return self.issue_type == "error"
    
    @property
    def is_warning(self) -> bool:
        """Check if this is a warning-level issue."""
        return self.issue_type == "warning"


@dataclass(frozen=True)
class ValidationReport:
    """
    Complete validation report for an experiment design.
    
    Includes all issues found and overall assessment.
    """
    
    # Identity
    report_id: str                              # Unique identifier
    
    # Experiment info
    experiment_identity: str                    # Validated experiment
    validation_timestamp_utc: float = field(default_factory=time.time)
    
    # Validation details
    is_valid: bool = False                      # Overall validity
    issues: Tuple[ValidationIssue, ...] = ()    # All issues found
    
    @property
    def error_count(self) -> int:
        """Get the number of errors."""
        return sum(1 for i in self.issues if i.is_error)
    
    @property
    def warning_count(self) -> int:
        """Get the number of warnings."""
        return sum(1 for i in self.issues if i.is_warning)
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        is_valid: bool = False,
        issues: List[ValidationIssue] = None,
    ) -> ValidationReport:
        """Create a new validation report."""
        return cls(
            report_id=f"validation:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            is_valid=is_valid,
            issues=tuple(issues or []),
        )


__all__ = [
    "ValidationResult",
    "ValidationIssue",
    "ValidationReport",
]