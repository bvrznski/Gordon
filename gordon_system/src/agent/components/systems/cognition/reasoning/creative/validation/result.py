# Creative Validation Result - Phase 7.33
# ======================================

"""
Canonical Creative Validation Result.

Validation is observational only - it never modifies creative artifacts directly.
It evaluates novelty, coherence, and usefulness of creative outputs.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationOutcome(Enum):
    """Possible outcomes of creative validation."""
    
    PASSED = "passed"                       # Meets all criteria
    FAILED_NOVELTY = "failed_novelty"       # Insufficient novelty
    FAILED_COHERENCE = "failed_coherence"   # Inconsistent with knowledge base
    FAILED_USEFULNESS = "failed_usefulness" # Insufficient practical value
    PENDING = "pending"                     # Validation not yet complete


@dataclass(frozen=True)
class CreativeValidationResult:
    """
    Represents the result of creative validation.
    
    A validation result includes:
        - Outcome (pass/fail categories)
        - Quality metrics
        - Findings and diagnostics
    
    Validation remains observational only.
    """
    
    # Identity
    validation_id: str                      # Unique validation identifier
    semantic_identity: str                  # Semantic identity
    
    # Outcome
    outcome: ValidationOutcome = ValidationOutcome.PENDING
    
    # Quality metrics (0-1)
    novelty_score: float = 0.0              # Novelty assessment
    coherence_score: float = 0.0            # Coherence with existing knowledge
    usefulness_score: float = 0.0           # Practical value estimate
    
    # Findings
    findings: List[str] = field(default_factory=list)  # Validation notes
    
    # Provenance
    validated_object_id: Optional[str] = None   # Object that was validated
    validation_timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_passed(self) -> bool:
        """Check if validation passed."""
        return self.outcome == ValidationOutcome.PASSED
    
    @property
    def is_failed_novelty(self) -> bool:
        """Check if failed due to insufficient novelty."""
        return self.outcome == ValidationOutcome.FAILED_NOVELTY
    
    @property
    def is_failed_coherence(self) -> bool:
        """Check if failed due to coherence issues."""
        return self.outcome == ValidationOutcome.FAILED_COHERENCE
    
    @property
    def is_failed_usefulness(self) -> bool:
        """Check if failed due to insufficient usefulness."""
        return self.outcome == ValidationOutcome.FAILED_USEFULNESS
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        validated_object_id: Optional[str] = None,
    ) -> CreativeValidationResult:
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            validated_object_id=validated_object_id,
            validation_timestamp_utc=time.time(),
        )
    
    def with_outcome(self, outcome: ValidationOutcome) -> CreativeValidationResult:
        """Return a copy with updated outcome."""
        return dataclass_replace(
            self,
            outcome=outcome,
        )
    
    def with_novelty_score(self, score: float) -> CreativeValidationResult:
        """Return a copy with updated novelty score."""
        return dataclass_replace(
            self,
            novelty_score=max(0.0, min(1.0, score)),
        )
    
    def add_finding(self, finding: str) -> CreativeValidationResult:
        """Add a finding to the validation result."""
        return dataclass_replace(
            self,
            findings=list(self.findings) + [finding],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeValidationResult",
    "ValidationOutcome",
]