# Deduction Validation - Phase 7.1
# ================================

"""
Canonical Deduction Validation Contract.

Deduction Validation evaluates proofs without modifying them directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DeductionValidation:
    """
    Validation of a deduction session or proof.
    
    Validation evaluates:
        - Rule correctness (did the rule follow its format?)
        - Premise validity (are premises properly accepted?)
        - Proof completeness (is every step justified?)
        - Unsupported steps (are there gaps in reasoning?)
        - Logical consistency (do conclusions follow from premises?)
    
    Validation remains observational; it never modifies the proof directly.
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # Target
    evaluated_proof: str                    # Which proof was evaluated?
    
    # Validation checks performed
    validation_checks: Dict[str, bool] = field(default_factory=dict)
    # e.g., {"rule_correctness": True, "trace_complete": True}
    
    # Findings
    findings: Tuple[Dict[str, Any], ...] = ()  # List of finding dicts
    
    # Unsupported steps (gaps in reasoning)
    unsupported_steps: Tuple[str, ...] = ()
    
    # Overall assessment
    is_valid: bool = False                  # Passed all checks?
    validity_reasons: Tuple[str, ...] = ()  # Why/why not?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    validated_at_utc: float = field(default_factory=time.time)
    
    @property
    def check_count(self) -> int:
        """Total number of checks performed."""
        return len(self.validation_checks)
    
    @property
    def passed_check_count(self) -> int:
        """Number of checks that passed."""
        return sum(1 for v in self.validation_checks.values() if v)
    
    @classmethod
    def create(
        cls,
        evaluated_proof: str,
        check_names: Optional[List[str]] = None,
    ) -> DeductionValidation:
        """Create a new validation with initial checks."""
        initial_checks = {name: False for name in (check_names or [])}
        return cls(
            validation_id=f"deduction_validation:{uuid.uuid4().hex[:16]}",
            evaluated_proof=evaluated_proof,
            validation_checks=initial_checks,
        )
    
    def record_check(self, check_name: str, passed: bool, details: Optional[Dict[str, Any]] = None) -> "DeductionValidation":
        """Record result of a validation check."""
        new_checks = dict(self.validation_checks)
        new_checks[check_name] = passed
        
        findings_list = list(self.findings)
        if details:
            finding = {
                "check": check_name,
                "passed": passed,
                **(details or {})
            }
            findings_list.append(finding)
        
        return dataclass_replace(
            self,
            validation_checks=new_checks,
            findings=tuple(findings_list),
        )
    
    def record_unsupported_step(self, step: str) -> "DeductionValidation":
        """Record an unsupported step in the proof."""
        return dataclass_replace(
            self,
            unsupported_steps=self.unsupported_steps + (step,),
        )
    
    def finalize(self, is_valid: bool, reasons: Optional[List[str]] = None) -> "DeductionValidation":
        """Mark validation as complete."""
        return dataclass_replace(
            self,
            is_valid=is_valid,
            validity_reasons=tuple(reasons or []),
            diagnostics={
                **self.diagnostics,
                "completed_at_utc": time.time(),
            },
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DeductionValidation",
]