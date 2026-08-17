# Causal Validation - Phase 7.5
# ============================

"""
Canonical Causal Validation.

Validation evaluates causal structures without modifying them.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ValidationIssue:
    """
    A single validation issue found during evaluation.
    """
    
    # Identity
    issue_id: str                       # Unique issue identifier
    
    # Issue type
    issue_type: str                     # "error", "warning", "info"
    
    # Location
    affected_element: Optional[str] = None  # Which element has the issue?
    
    # Description
    description: str                    # What is wrong?
    
    # Severity (0-1, higher = more severe)
    severity: float = 1.0               # How bad is this issue?


@dataclass(frozen=True)
class CausalValidation:
    """
    Validation result for a causal reasoning session.
    
    Validation remains observational - it never modifies causal models directly.
    """
    
    # Identity
    validation_id: str                  # Unique validation identifier
    
    # Evaluated artifacts
    evaluated_artifacts: Tuple[str, ...]  # What was validated?
    
    # Findings
    findings: Tuple[ValidationIssue, ...]  # Issues found
    
    # Overall status
    validation_status: str = "valid"    # "valid", "invalid", "warning"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return self.validation_status == "valid" or all(
            f.issue_type != "error" for f in self.findings
        )
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return any(f.issue_type == "warning" for f in self.findings)
    
    @property
    def issue_count(self) -> int:
        """Total number of issues found."""
        return len(self.findings)


@dataclass(frozen=True)
class ValidationReport:
    """
    A complete validation report with all stages.
    
    From initial check to final evaluation.
    """
    
    # Identity
    report_id: str                      # Unique report identifier
    
    # Evaluated components
    evaluated_components: Tuple[str, ...]  # What was validated?
    
    # Detailed findings
    detailed_findings: Tuple[ValidationIssue, ...]
    
    # Summary statistics
    total_issues: int = 0               # Total issues found
    error_count: int = 0                # Number of errors
    warning_count: int = 0              # Number of warnings
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None


def make_validation(
    artifacts: Tuple[str, ...],
    issues: List[ValidationIssue],
) -> CausalValidation:
    """Create a new validation."""
    issues_tuple = tuple(issues)
    
    # Determine status
    has_errors = any(i.issue_type == "error" for i in issues_tuple)
    has_warnings = any(i.issue_type == "warning" for i in issues_tuple)
    
    if has_errors:
        status = "invalid"
    elif has_warnings:
        status = "warning"
    else:
        status = "valid"
    
    return CausalValidation(
        validation_id=f"validation:{uuid.uuid4().hex[:16]}",
        evaluated_artifacts=artifacts,
        findings=issues_tuple,
        validation_status=status,
    )


__all__ = [
    "ValidationIssue",
    "CausalValidation",
    "ValidationReport",
]