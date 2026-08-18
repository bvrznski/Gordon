# Learning Validation - Phase 7.24
# ==============================

"""
Canonical Learning Validation Contract.

Learning Validation evaluates the quality of learning processes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class LearningValidation:
    """
    Validation result for a learning session.
    
    Validation evaluates:
        - Learning quality and validity
        - Evidence sufficiency
        - Generalization bounds
        - Integration consistency
    
    Validation remains observational; it never modifies learning artifacts directly.
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    
    # Evaluated sessions
    validated_sessions: List[str] = field(default_factory=list)  # Session IDs
    
    # Validation results
    findings: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True                     # Does learning pass validation?
    
    # Quality metrics
    confidence_score: float = 1.0             # 0.0 to 1.0
    evidence_quality: str = "unknown"         # "poor", "fair", "good", "excellent"
    
    # Timing
    validated_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    validation_policy: str = "standard"       # Which policy was used?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        validated_sessions: Optional[List[str]] = None,
        validation_policy: str = "standard",
    ) -> LearningValidation:
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            validated_sessions=validated_sessions or [],
            validation_policy=validation_policy,
            validated_at_utc=time.time(),
        )
    
    def with_finding(self, key: str, value: Any) -> LearningValidation:
        """Return a copy with an additional finding."""
        new_findings = dict(self.findings)
        new_findings[key] = value
        return dataclass_replace(
            self,
            findings=new_findings,
        )
    
    def invalidate(self, reason: str) -> LearningValidation:
        """Return a copy marked as invalid."""
        new_findings = dict(self.findings)
        new_findings["invalidation_reason"] = reason
        return dataclass_replace(
            self,
            is_valid=False,
            confidence_score=0.0,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LearningValidation",
]