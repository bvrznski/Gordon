# Explanation Validation - Phase 7.14
# ====================================

"""
Explanation validation for explanatory reasoning.

Validation remains observational - it evaluates but does not mutate.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ValidationIdentity:
    """
    Immutable identity for an explanation validation process.
    """
    
    semantic_identity: str                    # Stable identity across runs
    validation_number: int = 1                # For repeated validations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, validation_number: int = 1) -> ValidationIdentity:
        """Create a new validation identity."""
        return cls(
            semantic_identity=semantic_identity,
            validation_number=validation_number,
        )


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating an explanation.
    
    Evaluates:
        - Claim correctness
        - Evidence quality
        - Justification completeness
        - Narrative coherence
        - Interpretability
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Validated artifact
    validated_explanation_id: str             # Which explanation was checked?
    
    # Findings
    is_valid: bool = False                    # Overall validity
    unsupported_claims: Tuple[str, ...] = ()  # Claims lacking support
    incomplete_reasoning: Tuple[str, ...] = () # Reasoning gaps
    
    # Metrics
    claim_coverage_score: float = 0.5         # How many claims explained?
    evidence_quality_score: float = 0.5       # Evidence reliability
    justification_completeness_score: float = 0.5  # Justifications complete?
    
    @property
    def overall_score(self) -> float:
        """Calculate validation score."""
        return (
            (1.0 if self.is_valid else 0.0) * 0.3 +
            self.claim_coverage_score * 0.2 +
            self.evidence_quality_score * 0.3 +
            self.justification_completeness_score * 0.2
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        validated_explanation_id: str,
        is_valid: bool = False,
    ) -> "ValidationResult":
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            validated_explanation_id=validated_explanation_id,
            is_valid=is_valid,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ValidationIdentity",
    "ValidationResult",
]