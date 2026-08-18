# Legal Validation - Phase 7.47 Part 1
# =====================================

"""
Validation Contract.

Legal validation remains observational:
    - It never modifies legal artifacts directly
    - It preserves findings and diagnostics
    - It assesses interpretation quality

Validation ensures the integrity of legal reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ValidationResult:
    """
    Validation result for a legal analysis component.
    
    A validation result includes:
        - Component being validated
        - Validation checks performed
        - Findings (issues detected or confirmations)
        - Diagnostics
    
    Validation remains observational and never modifies artifacts.
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    
    # Input
    target_type: str                          # e.g., "obligation", "right"
    target_id: str                            # ID of component being validated
    
    # Validation checks
    checks_performed: Tuple[str, ...] = ()    # Which checks ran?
    
    # Findings
    passed_checks: Tuple[Dict[str, Any], ...] = ()
    failed_checks: Tuple[Dict[str, Any], ...] = ()
    warnings: Tuple[Dict[str, Any], ...] = ()
    
    # Overall result
    is_valid: bool = False                    # Did all checks pass?
    validation_status: Optional[str] = None   # e.g., "valid", "invalid", "warning"
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        target_type: str,
        target_id: str,
    ) -> ValidationResult:
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            target_type=target_type,
            target_id=target_id,
            checks_performed=(),
        )
    
    def with_passed_checks(self, checks: List[Dict[str, Any]]) -> ValidationResult:
        """Add passed checks to result."""
        return dataclass_replace(
            self,
            passed_checks=self.passed_checks + tuple(checks),
        )
    
    def with_failed_checks(self, checks: List[Dict[str, Any]]) -> ValidationResult:
        """Add failed checks to result."""
        return dataclass_replace(
            self,
            failed_checks=self.failed_checks + tuple(checks),
            is_valid=False,
        )


@dataclass(frozen=True)
class ValidationSession:
    """
    A validation session tracking multiple validation results.
    
    Includes:
        - Session metadata
        - All validation results
        - Summary statistics
    """
    
    # Identity
    session_id: str                           # Unique identifier
    
    # Input
    legal_question: str                       # Question being validated
    
    # Results
    validation_results: Tuple[ValidationResult, ...] = ()
    
    # Summary
    total_validations: int = 0                # Count of results
    total_passed: int = 0                     # How many passed?
    total_failed: int = 0                     # How many failed?
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        legal_question: str,
    ) -> ValidationSession:
        """Create a new validation session."""
        return cls(
            session_id=f"validation_session:{uuid.uuid4().hex[:16]}",
            legal_question=legal_question,
        )
    
    def add_result(self, result: ValidationResult) -> ValidationSession:
        """Add a validation result to the session."""
        total = self.total_validations + 1
        passed = self.total_passed + (1 if result.is_valid else 0)
        
        return dataclass_replace(
            self,
            validation_results=self.validation_results + (result,),
            total_validations=total,
            total_passed=passed,
            total_failed=total - passed,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ValidationResult",
    "ValidationSession",
]