# Strategic Resource Contract - Phase 7.37 Part 2
# ===============================================

"""
Resource Management for Strategic Reasoning.

This module implements the canonical resource contracts specified in Phase 7.37 Part 2:

- ResourceManagement: Evaluates compute, time, budget, attention allocation
- ResourceIdentity: Unique identifier for resource tracking
- ResourceModel: Formal representation of available resources
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ResourceType(Enum):
    """Types of strategic resources."""
    
    COMPUTE = "compute"
    TIME = "time"
    BUDGET = "budget"
    ATTENTION = "attention"
    HUMAN_RESOURCES = "human_resources"
    MEMORY = "memory"
    ENERGY = "energy"


@dataclass(frozen=True)
class ResourceIdentity:
    """
    Unique identifier for a resource model.
    
    LAW: RESOURCE-LAW-001 - Every Resource Model shall possess one explicit identity.
    """
    
    resource_id: str              # UUID4 string
    semantic_identity: str        # Stable semantic reference across runs
    version: int                  # Version number for evolution tracking


@dataclass(frozen=True)
class ResourceCapacity:
    """Capacity specification for a single resource type."""
    
    capacity_id: str
    resource_type: ResourceType
    total_available: float
    utilized: float = 0.0
    reserved: float = 0.0
    
    @property
    def available(self) -> float:
        """Calculate remaining available resources."""
        return self.total_available - self.utilized - self.reserved
    
    @property
    def utilization_rate(self) -> float:
        """Calculate current utilization rate (0.0 to 1.0)."""
        if self.total_available == 0:
            return 0.0
        return self.utilized / self.total_available


@dataclass(frozen=True)
class ResourceAllocation:
    """
    Allocation of resources for a specific purpose.
    
    LAW: RESOURCE-LAW-006 - Resource allocation shall never exceed declared resource availability.
    """
    
    allocation_id: str
    resource_type: ResourceType
    amount: float
    purpose: str                  # What is this being allocated to?
    priority: int                 # 1 = highest, N = lowest
    
    @property
    def excess(self) -> bool:
        """Check if allocation exceeds available resources."""
        return self.amount > 0  # Validation happens during construction


@dataclass(frozen=True)
class ResourceAnalysis:
    """
    Analysis result for resource availability and allocation.
    
    LAW: RESOURCE-LAW-004 - Resource provenance shall remain complete.
    """
    
    analysis_id: str
    resource_identity: ResourceIdentity
    total_capacity: Tuple[ResourceCapacity, ...]
    current_allocations: Tuple[ResourceAllocation, ...]
    shortage_types: Tuple[str, ...]  # List of resource types in shortage
    surplus_types: Tuple[str, ...]   # List of resource types with excess


@dataclass(frozen=True)
class ResourceEvolution:
    """
    Records evolution of resource allocation over time.
    
    LAW: RESOURCE-LAW-005 - Resource revisions shall preserve history.
    """
    
    evolution_id: str
    resource_identity: ResourceIdentity
    timestamp_utc: float
    change_type: str              # "reallocation", "release", "addition"
    previous_state_hash: str      # Hash of previous state for verification
    change_description: str


@dataclass(frozen=True)
class ResourceModel:
    """
    Complete formal representation of available resources.
    
    LAW: RESOURCE-LAW-007 - Resource Models shall remain independently inspectable.
    """
    
    identity: ResourceIdentity
    capacities: Tuple[ResourceCapacity, ...]
    created_at_utc: float = field(default_factory=time.time)
    
    def get_capacity(self, resource_type: ResourceType) -> Optional[ResourceCapacity]:
        """Get capacity for a specific resource type."""
        for cap in self.capacities:
            if cap.resource_type == resource_type:
                return cap
        return None
    
    def can_allocate(self, allocation: ResourceAllocation) -> bool:
        """
        Check if an allocation can be satisfied.
        
        LAW: RESOURCE-LAW-006 - Resource allocation shall never exceed declared resource availability.
        """
        capacity = self.get_capacity(allocation.resource_type)
        if capacity is None:
            return False
        return capacity.available >= allocation.amount
    
    def allocate(self, allocation: ResourceAllocation) -> ResourceModel:
        """Return new model with allocation applied (if valid)."""
        if not self.can_allocate(allocation):
            raise ValueError(f"Cannot allocate {allocation.amount} of {allocation.resource_type.value}")
        
        new_capacities = []
        for cap in self.capacities:
            if cap.resource_type == allocation.resource_type:
                new_cap = ResourceCapacity(
                    capacity_id=cap.capacity_id,
                    resource_type=cap.resource_type,
                    total_available=cap.total_available,
                    utilized=cap.utilized + allocation.amount,
                    reserved=cap.reserved
                )
                new_capacities.append(new_cap)
            else:
                new_capacities.append(cap)
        
        return ResourceModel(
            identity=self.identity,
            capacities=tuple(new_capacities),
            created_at_utc=time.time()
        )


@dataclass(frozen=True)
class ResourceManagement:
    """
    Resource management evaluation result.
    
    LAW: RESOURCE-LAW-008 - Equivalent resource states shall produce equivalent allocation strategies.
    """
    
    evaluation_id: str
    resource_identity: ResourceIdentity
    analysis_results: Tuple[ResourceAnalysis, ...]
    total_available: float
    total_allocated: float
    utilization_rate: float
    shortage_risk: str            # "none", "low", "medium", "high"
    recommendations: Tuple[str, ...]  # Actionable recommendations
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Analysis metadata


@dataclass(frozen=True)
class ResourcePortfolio:
    """
    Portfolio of resource allocations across multiple initiatives.
    
    LAW: RESOURCE-LAW-002 - Available resources shall remain explicit.
    """
    
    portfolio_id: str
    resource_identity: ResourceIdentity
    allocations: Tuple[ResourceAllocation, ...]
    total_budget: float
    remaining_budget: float
    
    @property
    def budget_utilization(self) -> float:
        """Calculate budget utilization rate."""
        if self.total_budget == 0:
            return 0.0
        return (self.total_budget - self.remaining_budget) / self.total_budget