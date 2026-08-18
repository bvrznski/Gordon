# Adaptation Health - Phase 7.25
# =============================

"""
Canonical Adaptation Health metrics.

Health metrics describe the operational state of adaptation systems.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class AdaptationHealth:
    """
    Health metrics for adaptation sessions and systems.
    
    Metrics include:
        - Adaptations applied
        - Configuration stability
        - Rollback success rate
        - Behavior effectiveness
        - Policy consistency
        - Validation success rate
        - Diagnostics
    
    Health remains descriptive.
    """
    
    # Identity
    health_identity: str                  # Unique health identifier
    
    # Metrics
    adaptations_applied: int = 0
    configuration_stability_score: float = 1.0
    rollback_success_rate: float = 1.0
    behavior_effectiveness_score: float = 1.0
    policy_consistency_score: float = 1.0
    validation_success_rate: float = 1.0
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    evaluated_at_utc: Optional[float] = None
    
    @property
    def overall_score(self) -> float:
        """Calculate overall health score."""
        if self.adaptations_applied == 0:
            return 1.0
        
        scores = [
            self.configuration_stability_score,
            self.rollback_success_rate,
            self.behavior_effectiveness_score,
            self.policy_consistency_score,
            self.validation_success_rate,
        ]
        
        # Weight by adaptation count
        base_score = sum(scores) / len(scores)
        
        # Penalize for high failure rate (if diagnostics indicate issues)
        if self.diagnostics.get("failure_count", 0) > 0:
            penalty = min(0.5, self.diagnostics["failure_count"] * 0.1)
            return max(0.0, base_score - penalty)
        
        return base_score
    
    @classmethod
    def create(
        cls,
        adaptations_applied: int = 0,
        diagnostics: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationHealth:
        """Create a new adaptation health report."""
        return cls(
            health_identity=f"health:{uuid.uuid4().hex[:16]}",
            adaptations_applied=adaptations_applied,
            diagnostics=diagnostics or {},
            provenance=provenance or {},
            evaluated_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationHealth",
]