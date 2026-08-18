# Decision Validation - Phase 7.19
# ===============================

"""
Canonical Decision Validation Contract.

Decision Validation is observational; it never modifies decision artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DecisionValidation:
    """
    Validation of a decision session or commitment.
    
    Validation remains observational; it never modifies the decision directly.
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # Validated decision
    validated_decision: str                 # Decision ID being validated
    
    # Validation findings
    is_valid: bool = True                   # Does the decision pass validation?
    
    # Findings (list of checks performed)
    findings: Tuple[str, ...] = ()          # What was checked?
    
    # Validation failures (if any)
    failures: Tuple[str, ...] = ()          # What failed?
    
    # Validation constraints satisfied
    constraint_satisfaction: Dict[str, bool] = field(default_factory=dict)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def validation_passed(self) -> bool:
        """Check if all validations passed."""
        return self.is_valid and len(self.failures) == 0
    
    @classmethod
    def create(
        cls,
        validated_decision: str,
        findings: Optional[List[str]] = None,
        failures: Optional[List[str]] = None,
        constraint_satisfaction: Optional[Dict[str, bool]] = None,
    ) -> DecisionValidation:
        """Create a new validation record."""
        return cls(
            validation_id=f"decision_validation:{uuid.uuid4().hex[:16]}",
            validated_decision=validated_decision,
            is_valid=len(failures or []) == 0,
            findings=tuple(findings or []),
            failures=tuple(failures or []),
            constraint_satisfaction=constraint_satisfaction or {},
        )


__all__ = [
    "DecisionValidation",
]