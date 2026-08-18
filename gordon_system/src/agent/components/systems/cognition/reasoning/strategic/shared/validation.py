# Strategic Validation - Phase 7.18
# ================================

"""
Canonical Strategic Validation for Phase 7.18.

Validation is observational, preserving findings without mutating strategic artifacts.
It distinguishes between strategic inconsistency and planning failure.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicValidation:
    """
    Result of strategic validation for a given strategy.
    
    Validation is purely observational - it never modifies strategic artifacts directly.
    It preserves findings for later inspection and audit.
    """
    
    # Identity
    validation_id: str                      # Unique validation identifier
    
    # Input being validated
    strategy_identity: str                  # Which strategy?
    objective_set_id: str                   # Which objectives?
    
    # Validation checks performed
    validation_checks: List[str] = field(default_factory=list)  # e.g., "consistency", "feasibility"
    
    # Results of each check
    check_results: Dict[str, bool] = field(default_factory=dict)  # check_name -> passed
    
    # Findings (issues discovered)
    findings: List[Dict[str, Any]] = field(default_factory=list)  # structured finding records
    
    # Overall validation result
    validation_passed: bool = True          # All checks must pass
    
    # Validation type
    validation_type: str = "comprehensive"  # e.g., "consistency", "feasibility"
    
    # Provenance
    validated_at_utc: float = field(default_factory=time.time)
    validator_identity: str = ""            # Who/what performed the validation?


@dataclass(frozen=True)
class ValidationFailure:
    """
    Record of a failed validation check.
    """
    
    # Identity
    failure_id: str
    
    # Input that failed validation
    strategy_identity: str
    
    # Check that failed
    failed_check: str                       # e.g., "mission_alignment", "resource_feasibility"
    
    # Failure details
    failure_description: str                # What was wrong?
    
    # Suggested remediation
    suggested_remediation: Optional[str] = None  # How to fix it?
    
    # Timing
    failed_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ValidationTrace:
    """
    Complete trace of validation for a strategy.
    
    Allows full replay and audit of all validation decisions.
    """
    
    # Identity
    trace_id: str
    
    # Strategy being validated
    strategy_identity: str
    
    # Sequence of validations
    validation_sequence: List[StrategicValidation]
    
    # Current status
    current_status: str = "valid"           # valid, needs_revision, invalid
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    last_validated_at_utc: Optional[float] = None
    
    @property
    def validation_count(self) -> int:
        """Return the number of validations in this trace."""
        return len(self.validation_sequence)


__all__ = [
    "StrategicValidation",
    "ValidationFailure",
    "ValidationTrace",
]