# World-Model Reasoning Health - Phase 7.44
# =================================

"""
Canonical World Model Health Metrics.

Health metrics describe world model quality and stability.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class HealthMetric:
    """
    A health metric measurement.
    """
    
    metric_id: str
    
    kind: str
    value: float
    threshold: Optional[float] = None
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class WorldHealth:
    """
    World model health status.
    """
    
    health_id: str
    
    entity_persistence: float = 1.0
    scene_consistency: float = 1.0
    tracking_stability: float = 1.0
    physical_consistency: float = 1.0
    world_completeness: float = 1.0
    validation_success_rate: float = 1.0
    
    overall_health: float = 1.0
    
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
    ) -> WorldHealth:
        """Create a new world health status."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            entity_persistence=1.0,
            scene_consistency=1.0,
            tracking_stability=1.0,
            physical_consistency=1.0,
            world_completeness=1.0,
            validation_success_rate=1.0,
            overall_health=1.0,
            provenance=provenance,
        )


__all__ = [
    "HealthMetric",
    "WorldHealth",
]