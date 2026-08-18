# World-Model Reasoning Validation - Phase 7.44
# =================================

"""
Canonical World Validation.

Validation is observational - it evaluates the world model without modifying artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationKind(Enum):
    """Types of validation checks."""
    
    PERCEPTION_FAILURE = "perception_failure"
    WORLD_MODEL_FAILURE = "world_model_failure"
    PHYSICAL_VIOLATION = "physical_violation"
    CAUSAL_CONTRADICTION = "causal_contradiction"


class ValidationState(Enum):
    """Validation session states."""
    
    PENDING = "pending"
    ANALYZING = "analyzing"
    VERIFIED = "verified"
    ISSUES_FOUND = "issues_found"


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a validation check.
    """
    
    result_id: str
    timestamp_utc: float
    
    kind: ValidationKind
    passed: bool
    confidence: float = 1.0
    
    failure_description: Optional[str] = None
    affected_entities: List[str] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        kind: ValidationKind,
        passed: bool,
        confidence: float = 1.0,
    ) -> ValidationResult:
        """Create a new validation result."""
        return cls(
            result_id=f"validation_result:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            kind=kind,
            passed=passed,
            confidence=confidence,
            affected_entities=[],
        )


@dataclass(frozen=True)
class WorldValidation:
    """
    World validation analysis result.
    """
    
    validation_id: str
    
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    
    model_completeness: float = 1.0
    model_consistency: float = 1.0
    
    world_revision: int = 1
    
    confidence: float = 1.0
    provenance: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
        world_revision: int = 1,
    ) -> WorldValidation:
        """Create a new world validation."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            validation_results=[],
            total_checks=0,
            passed_checks=0,
            failed_checks=0,
            model_completeness=1.0,
            model_consistency=1.0,
            confidence=1.0,
            provenance=provenance,
            world_revision=world_revision,
        )
    
    def with_result(self, result: ValidationResult) -> WorldValidation:
        """Add a validation result."""
        new_results = self.validation_results + [result]
        
        return dataclass_replace(
            self,
            validation_results=new_results,
            total_checks=self.total_checks + 1,
            passed_checks=self.passed_checks + (1 if result.passed else 0),
            failed_checks=self.failed_checks + (0 if result.passed else 1),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ValidationKind",
    "ValidationState",
    "ValidationResult",
    "WorldValidation",
]