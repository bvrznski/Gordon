# Behavior Adaptation - Phase 7.25
# ================================

"""
Canonical Behavior Adaptation contract.

Behavior adaptation evaluates behavioral modifications for suitability,
effectiveness, reversibility, and risk.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class BehaviorAdaptation:
    """
    A behavioral adaptation that modifies Gordon's operational behavior.
    
    Behavior adaptation evaluates:
        - Expected improvement
        - Reversibility
        - Risk
        - Operational benefit
        - Context suitability
        - Resource impact
    
    Behavior adaptations remain explicit and are never permanent.
    """
    
    # Identity
    adaptation_identity: str              # Unique adaptation identifier
    
    # Adapted behavior
    adapted_behavior: str                 # Description of the new behavior
    
    # Policy governing the adaptation
    adaptation_policy: str                # How this adaptation is governed
    
    # Metrics for evaluation
    adaptation_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    activated_at_utc: Optional[float] = None
    deactivated_at_utc: Optional[float] = None
    
    @property
    def is_active(self) -> bool:
        """Check if adaptation is currently active."""
        return self.activated_at_utc is not None and self.deactivated_at_utc is None
    
    @classmethod
    def create(
        cls,
        adapted_behavior: str,
        adaptation_policy: str = "default",
        metrics: Optional[Dict[str, float]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> BehaviorAdaptation:
        """Create a new behavior adaptation."""
        return cls(
            adaptation_identity=f"behavior:{uuid.uuid4().hex[:16]}",
            adapted_behavior=adapted_behavior,
            adaptation_policy=adaptation_policy,
            adaptation_metrics=metrics or {},
            provenance=provenance or {},
            activated_at_utc=time.time(),
        )
    
    def deactivate(self) -> BehaviorAdaptation:
        """Return a copy with this adaptation deactivated."""
        return dataclass_replace(
            self,
            deactivated_at_utc=time.time(),
        )


@dataclass(frozen=True)
class BehaviorManagement:
    """
    Management of behavior adaptations.
    
    Behavior management evaluates:
        - Behavior suitability
        - Operational effectiveness
        - Expected benefit
        - Adaptation cost
        - Reversibility
        - Risk
    
    Behavior management remains explicit.
    """
    
    # Identity
    management_identity: str              # Unique management identifier
    
    # Adapted behavior
    adapted_behavior: str                 # The behavior being managed
    
    # Policy governing the adaptation
    behavior_policy: str                  # Management policy
    
    # Metrics
    adaptation_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "BehaviorAdaptation",
    "BehaviorManagement",
]