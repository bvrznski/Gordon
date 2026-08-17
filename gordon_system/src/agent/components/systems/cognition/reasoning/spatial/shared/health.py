# Spatial Health - Phase 7.9
# =========================

"""
Canonical Spatial Health Metrics.

Spatial health tracks:
    entities represented, transformations executed, geometry/topology consistency,
    navigation completeness, validation success, diagnostics.
    
Health remains descriptive (never prescriptive).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class HealthMetric:
    """
    Individual health metric.
    
    Each metric tracks one aspect of spatial reasoning health.
    """
    
    # Identity
    metric_id: str                          # Unique identifier
    
    # Metric name
    metric_name: str                        # e.g., "entity_count", "transformation_count"
    
    # Value
    value: float                            # Current value
    unit: str = ""                          # Unit of measurement (optional)
    
    # Status
    status: str = "normal"                  # normal, warning, critical
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class SpatialHealth:
    """
    Health metrics for spatial reasoning system.
    
    Health remains descriptive (never prescriptive).
    """
    
    # Identity
    health_id: str                          # Unique identifier
    
    # Entity tracking
    entities_represented: int = 0           # Total entities in model
    entity_types: Dict[str, int] = field(default_factory=dict)  # Type counts
    
    # Transformations
    transformations_executed: int = 0       # Number of transforms run
    transformation_success_rate: float = 1.0  # Success fraction
    
    # Geometry consistency
    geometry_consistency_score: float = 1.0   # 0.0 to 1.0
    geometry_issues_count: int = 0          # Count of issues
    
    # Topology consistency  
    topology_consistency_score: float = 1.0   # 0.0 to 1.0
    topology_issues_count: int = 0          # Count of issues
    
    # Navigation completeness
    navigation_complete: bool = True        # Is navigation fully determined?
    reachable_region_ratio: float = 1.0     # Ratio of space covered
    
    # Validation success
    validation_success_rate: float = 1.0    # Success fraction
    validations_run: int = 0                # Number of validations
    
    # Diagnostics summary
    diagnostic_summary: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def overall_score(self) -> float:
        """Calculate overall health score (0.0 to 1.0)."""
        scores = [
            self.geometry_consistency_score,
            self.topology_consistency_score,
            self.transformation_success_rate,
            self.validation_success_rate,
        ]
        return sum(scores) / len(scores)
    
    @property
    def has_issues(self) -> bool:
        """Check if any issues detected."""
        return (
            self.geometry_issues_count > 0 or
            self.topology_issues_count > 0 or
            self.transformation_success_rate < 1.0 or
            self.validation_success_rate < 1.0
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> SpatialHealth:
        """Create a new health metrics result."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def update_metric(self, name: str, value: float) -> SpatialHealth:
        """Return new health with updated metric."""
        metrics = {
            "entities_represented": lambda v: dataclass_replace(self, entities_represented=int(v)),
            "transformations_executed": lambda v: dataclass_replace(self, transformations_executed=int(v)),
            "geometry_consistency_score": lambda v: dataclass_replace(self, geometry_consistency_score=v),
            "topology_consistency_score": lambda v: dataclass_replace(self, topology_consistency_score=v),
            "transformation_success_rate": lambda v: dataclass_replace(self, transformation_success_rate=v),
            "validation_success_rate": lambda v: dataclass_replace(self, validation_success_rate=v),
        }
        
        if name in metrics:
            return metrics[name](value)
        return self


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialHealth", 
    "HealthMetric",
]