# Adaptation Validation - Phase 7.25
# =================================

"""
Canonical Adaptation Validation contract.

Validation ensures adaptations are correct, compatible, and safe before
application.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationResult(Enum):
    """Results of adaptation validation."""
    
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


@dataclass(frozen=True)
class AdaptationValidation:
    """
    Validation of an adaptation.
    
    Validation remains observational - it does not modify adaptations,
    only reports on their correctness and safety.
    """
    
    # Identity
    validation_identity: str              # Unique validation identifier
    
    # Evaluated adaptation reference
    evaluated_adaptation_id: str          # ID of the adapted being validated
    
    # Result
    result: ValidationResult              # Validation outcome
    
    # Findings
    findings: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    validated_at_utc: Optional[float] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.result == ValidationResult.PASSED
    
    @classmethod
    def create(
        cls,
        evaluated_adaptation_id: str,
        result: ValidationResult,
        findings: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationValidation:
        """Create a new adaptation validation."""
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_adaptation_id=evaluated_adaptation_id,
            result=result,
            findings=findings or {},
            provenance=provenance or {},
            validated_at_utc=time.time(),
        )
    
    @classmethod
    def passed(
        cls,
        evaluated_adaptation_id: str,
        findings: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationValidation:
        """Create a passed validation."""
        return cls.create(evaluated_adaptation_id, ValidationResult.PASSED, findings, provenance)
    
    @classmethod
    def failed(
        cls,
        evaluated_adaptation_id: str,
        findings: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationValidation:
        """Create a failed validation."""
        return cls.create(evaluated_adaptation_id, ValidationResult.FAILED, findings, provenance)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationValidation",
    "ValidationResult",
]