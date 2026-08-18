# Introspection Health - Phase 7.29
# =================================

"""
Introspection Health measures introspection quality metrics.

Health is:
    Descriptive - It reports on current state, not modifying it
    
Health metrics include:
    - Self-model accuracy
    - Awareness completeness
    - Consistency quality
    - Diagnostic coverage
    - Publication quality
    - Validation success
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class IntrospectionHealth:
    """
    Health metrics for introspection reasoning.
    
    A health report contains:
        - Explicit identity
        - Health metrics (descriptive, not modifying)
        - Summary assessment
        - Provenance tracking
    
    Health remains descriptive.
    """
    
    # Identity
    health_id: str                            # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Health metrics
    self_model_accuracy: float = 1.0          # How accurate are self models?
    awareness_completeness: float = 1.0       # How complete is awareness?
    consistency_quality: float = 1.0          # Quality of consistency checks
    diagnostic_coverage: float = 1.0          # Coverage of diagnostics
    
    # Publication quality
    publication_correctness: float = 1.0      # Accuracy of publications
    
    # Validation metrics
    validation_success_rate: float = 1.0      # Success rate of validations
    
    # Overall health score (derived from metrics)
    overall_health_score: float = 1.0         # Combined health indicator
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> IntrospectionHealth:
        """Create a new introspection health report."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
        )
    
    def with_metrics(self, metrics: Dict[str, float]) -> IntrospectionHealth:
        """Return a copy with updated metrics."""
        result = self
        for key, value in metrics.items():
            if hasattr(result, key):
                result = dataclass_replace(
                    result,
                    **{key: value}
                )
        return result


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntrospectionHealth",
]