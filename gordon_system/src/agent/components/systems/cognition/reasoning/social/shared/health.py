# Social Health - Phase 7.32
# ==========================

"""
Canonical Social Health metrics.

Health Metrics:
- Model completeness
- Belief confidence  
- Intention confidence
- Relationship accuracy
- Prediction quality
- Validation success
- Diagnostics

Health remains descriptive.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class SocialHealth:
    """
    Social health metrics.
    
    Describes the health status of social reasoning results:
        - Model completeness (what was successfully modeled)
        - Belief confidence scores  
        - Intention confidence scores
        - Relationship accuracy estimates
        - Prediction quality ratings
        - Validation success rate
        
    Health remains descriptive - it does not modify artifacts.
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Health metrics (all descriptive)
    model_completeness: float = 0.0           # 0.0 to 1.0 - fraction of expected models
    belief_confidence_avg: float = 0.0        # Average confidence across beliefs
    intention_confidence_avg: float = 0.0     # Average confidence across intentions  
    relationship_accuracy: float = 0.0        # Estimated accuracy of relationships
    
    prediction_quality: float = 0.0           # Quality of predictions
    validation_success_rate: float = 1.0      # Fraction of validations passed
    
    # Diagnostics (issues found)
    diagnostics: Tuple[Dict[str, Any], ...] = ()
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def overall_health_score(self) -> float:
        """Compute an overall health score."""
        weights = {
            "model_completeness": 0.15,
            "belief_confidence_avg": 0.20,
            "intention_confidence_avg": 0.20,
            "relationship_accuracy": 0.20,
            "prediction_quality": 0.15,
            "validation_success_rate": 0.10,
        }
        
        score = (
            self.model_completeness * weights["model_completeness"] +
            self.belief_confidence_avg * weights["belief_confidence_avg"] +
            self.intention_confidence_avg * weights["intention_confidence_avg"] +
            self.relationship_accuracy * weights["relationship_accuracy"] +
            self.prediction_quality * weights["prediction_quality"] +
            self.validation_success_rate * weights["validation_success_rate"]
        )
        return round(score, 3)
    
    @property
    def has_issues(self) -> bool:
        """Check if there are any health issues."""
        return len(self.diagnostics) > 0
    
    @classmethod
    def create(cls) -> SocialHealth:
        """Create a new social health record."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )
    
    def with_diagnostic(self, diagnostic: Dict[str, Any]) -> SocialHealth:
        """Return a copy with an additional diagnostic."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SocialHealth",
]