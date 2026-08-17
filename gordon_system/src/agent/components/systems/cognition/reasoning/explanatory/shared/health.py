# Explanation Health - Phase 7.14
# ===============================

"""
Explanation health metrics for explanatory reasoning.

Health metrics are descriptive, not prescriptive.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class HealthMetrics:
    """
    Health metrics for an explanation session.
    
    Metrics include:
        - Claims explained
        - Evidence coverage
        - Justification completeness
        - Alternative explanations considered
        - Validation success rate
        - Interpretability score
        - Diagnostics summary
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Primary metrics
    claims_explained_count: int = 0           # How many claims explained?
    evidence_coverage_score: float = 0.5      # Coverage of evidence base
    justification_completeness_score: float = 0.5  # Justifications complete?
    
    # Secondary metrics
    alternatives_considered_count: int = 0    # Alternatives evaluated
    validation_success_rate: float = 1.0      # Pass rate for validations
    
    # Quality indicators
    interpretability_score: float = 0.5       # How interpretable?
    overall_health_score: float = 0.5         # Overall health (composite)
    
    @property
    def is_healthy(self) -> bool:
        """Check if explanation is in healthy state."""
        return (
            self.evidence_coverage_score >= 0.5 and
            self.justification_completeness_score >= 0.5 and
            self.interpretability_score >= 0.5
        )
    
    @classmethod
    def create(cls, **kwargs) -> "HealthMetrics":
        """Create health metrics."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            **kwargs
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HealthMetrics",
]