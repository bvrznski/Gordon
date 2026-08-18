# Stability Validation - Phase 7.26
# ==================================

"""
Canonical Stability Validation.

Validation ensures that stability assessments are correct and stabilization
plans are safe before execution.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class StabilityValidationResult(Enum):
    """Results of stability validation."""
    
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class StabilityValidationFinding:
    """A finding from stability validation."""
    
    finding_id: str
    finding_type: str           # e.g., "constraint_violation", "policy_mismatch"
    severity: float             # 0.0 to 1.0
    description: str
    affected_component: Optional[str] = None


@dataclass(frozen=True)
class StabilityValidation:
    """Result of a validation operation."""
    
    validation_id: str
    validated_entity_id: str     # ID of what was validated
    
    # Validation outcome
    result: StabilityValidationResult
    confidence: float            # 0.0 to 1.0, how certain is the result?
    
    # Findings (if any issues)
    findings: List[StabilityValidationFinding] = field(default_factory=list)
    
    # Validation metadata
    validated_at_utc: float = field(default_factory=time.time)
    validator_id: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.result == StabilityValidationResult.VALID
    
    @classmethod
    def create(
        cls,
        validated_entity_id: str,
        result: StabilityValidationResult,
        confidence: float = 1.0,
        findings: List[StabilityValidationFinding] = None,
        validator_id: Optional[str] = None,
    ) -> StabilityValidation:
        """Create a new validation result."""
        if findings is None:
            findings = []
        
        return cls(
            validation_id=f"valid:{uuid.uuid4().hex[:16]}",
            validated_entity_id=validated_entity_id,
            result=result,
            confidence=confidence,
            findings=findings,
            validator_id=validator_id,
        )


@dataclass(frozen=True)
class StabilityValidationGovernance:
    """Governing rules for stability validation."""
    
    governance_id: str
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Minimum confidence threshold
    min_confidence_threshold: float = 0.8
    
    # Required checks
    required_checks: List[str] = field(default_factory=list)


__all__ = [
    "StabilityValidation",
    "StabilityValidationFinding",
    "StabilityValidationGovernance",
    "StabilityValidationResult",
]