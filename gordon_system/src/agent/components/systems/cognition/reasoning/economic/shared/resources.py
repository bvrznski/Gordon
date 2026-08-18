# Resource Analysis - Phase 7.48 Part 2
# ======================================

"""
Resource Analysis.

Resource analysis evaluates:
    - scarcity
    - availability
    - capacity
    - consumption
    - renewability
    - substitutability

Resources remain explicit.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared.descriptor import (
    EconomicLifecycleState,
)


@dataclass(frozen=True)
class ResourceAssessment:
    """Assessment of a single resource."""
    
    resource_id: str                  # Unique resource identifier
    resource_type: str                # Type (compute, memory, storage, etc.)
    availability: float               # Currently available quantity
    capacity: Optional[float] = None  # Maximum capacity
    utilization: Optional[float] = None  # Current utilization rate (0-1)
    origin: Optional[str] = None      # Source/origin of the resource
    
    @property
    def is_scarce(self) -> bool:
        """Check if resource is scarce (limited availability)."""
        return self.availability < 1.0 or (
            self.capacity is not None and self.availability / self.capacity < 0.2
        )


@dataclass(frozen=True)
class ResourceInventory:
    """Complete inventory of resources."""
    
    inventory_id: str                 # Unique inventory identifier
    resources: Dict[str, ResourceAssessment]
    total_available: float = field(init=False)  # Computed property
    
    def __post_init__(self):
        # Calculate total available using object.__setattr__ for frozen dataclass
        total = sum(r.availability for r in self.resources.values())
        object.__setattr__(self, 'total_available', total)


@dataclass(frozen=True)
class ResourceAnalysis:
    """Complete analysis of resource state."""
    
    analysis_id: str                  # Unique analysis identifier
    semantic_identity: str            # What this analysis represents
    
    inventory: ResourceInventory
    scarcity_assessment: Dict[str, bool]  # Per-resource scarcity
    substitutability_matrix: Optional[Dict[tuple, float]] = None  # How substitutable resources are
    
    lifecycle_state: EconomicLifecycleState = EconomicLifecycleState.CREATED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        resources: Dict[str, ResourceAssessment],
    ) -> ResourceAnalysis:
        """Create a new resource analysis."""
        return cls(
            analysis_id=f"resource_analysis:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            inventory=ResourceInventory(inventory_id=str(uuid.uuid4()), resources=resources),
            scarcity_assessment={
                rid: assessment.is_scarce
                for rid, assessment in resources.items()
            },
        )


__all__ = [
    "ResourceAnalysis",
    "ResourceAssessment",
    "ResourceInventory",
]