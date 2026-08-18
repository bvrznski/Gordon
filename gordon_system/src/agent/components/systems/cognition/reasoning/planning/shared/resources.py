# Resource Planning - Phase 7.20
# ==============================

"""
Canonical Resource Planning contracts for Phase 7.20.

Resource allocation evaluates availability, contention, expected consumption,
reservation strategy, fallback allocation, and allocation policy.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ResourceType(Enum):
    """Types of resources that can be allocated."""
    
    COMPUTE = "compute"                     # CPU/GPU processing capacity
    MEMORY = "memory"                       # RAM/storage capacity
    TOOL = "tool"                           # Software tools and utilities
    TIME = "time"                           # Time budget
    EXTERNAL_SERVICE = "external_service"   # External API/Service access


class AllocationPolicy(Enum):
    """Resource allocation policies."""
    
    BEST_EFFORT = "best_effort"             # Use if available, skip if not
    RESERVE = "reserve"                     # Must reserve before use
    DYNAMIC_ALLOCATION = "dynamic_allocation"  # Allocate at runtime as needed


@dataclass(frozen=True)
class ResourceAllocation:
    """
    An allocation of resources to a task or plan.
    
    Resources include:
        - Compute capacity (CPU/GPU time)
        - Memory/storage space
        - Tools and utilities
        - Time budget
        - External service access
    """
    
    # Identity
    allocation_id: str                        # Unique allocation identifier
    
    # Allocated resources
    resource_type: ResourceType               # What kind of resource?
    resource_name: str                        # Resource instance name (e.g., "gpu-1", "api-key")
    quantity: float = 1.0                     # Amount allocated
    
    # Allocation policy
    allocation_policy: AllocationPolicy = AllocationPolicy.BEST_EFFORT
    
    # Expected consumption
    expected_consumption_rate: float = 1.0   # Per-second rate of use
    expected_duration_seconds: float = 0.0     # How long it will be used
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    allocated_at_utc: Optional[float] = None
    
    # Provenance
    originating_plan_id: Optional[str] = None
    task_id: Optional[str] = None             # Which task uses this resource?
    
    @property
    def total_consumed(self) -> float:
        """Calculate total resource consumed over expected duration."""
        return self.expected_consumption_rate * self.expected_duration_seconds
    
    @classmethod
    def create(
        cls,
        resource_type: ResourceType,
        resource_name: str,
        allocation_policy: AllocationPolicy = AllocationPolicy.BEST_EFFORT,
    ) -> ResourceAllocation:
        """Create a new resource allocation."""
        return cls(
            allocation_id=f"resource:{uuid.uuid4().hex[:16]}",
            resource_type=resource_type,
            resource_name=resource_name,
            allocation_policy=allocation_policy,
        )


@dataclass(frozen=True)
class ResourcePlanning:
    """
    Planning for resource usage across a plan.
    
    Evaluates:
        - Resource availability
        - Resource contention (conflicts)
        - Expected consumption patterns
        - Reservation strategy
        - Fallback allocation options
    """
    
    # Identity
    planning_id: str                          # Unique planning record identifier
    
    # Participating resources
    allocated_resources: Tuple[ResourceAllocation, ...] = ()
    
    # Allocation strategy
    allocation_strategy: str = "sequential"   # How are resources allocated?
    reservation_policy: str = "first_come_first_served"  # Reservation order
    
    # Resource capacity information (for analysis)
    available_compute: float = 0.0            # Total available compute units
    available_memory: float = 0.0             # Total available memory units
    total_expected_consumption: float = 0.0   # Sum of all expected usage
    
    # Conflicts and contention
    resource_conflicts: Tuple[str, ...] = ()  # IDs of conflicting allocations
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        allocated_resources: Tuple[ResourceAllocation, ...],
        allocation_strategy: str = "sequential",
    ) -> ResourcePlanning:
        """Create a new resource planning record."""
        total_consumption = sum(r.total_consumed for r in allocated_resources)
        
        return cls(
            planning_id=f"resourceplanning:{uuid.uuid4().hex[:16]}",
            allocated_resources=allocated_resources,
            allocation_strategy=allocation_strategy,
            total_expected_consumption=total_consumption,
        )


@dataclass(frozen=True)
class ResourceAvailability:
    """
    Availability analysis of resources.
    
    Determines which resources are available, reserved, or in contention.
    """
    
    # Identity
    availability_id: str                      # Unique availability record identifier
    
    # Resource status
    resource_name: str                        # Which resource?
    is_available: bool = False                # Currently available?
    reserved_by: Optional[str] = None         # Who has it reserved? (plan ID)
    reserved_until_utc: Optional[float] = None  # Reservation expiration
    
    # Allocation info
    allocation_requested: float = 0.0         # How much was requested?
    allocation_granted: float = 0.0           # How much was granted?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    originating_plan_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        resource_name: str,
        is_available: bool = False,
    ) -> ResourceAvailability:
        """Create a new availability record."""
        return cls(
            availability_id=f"availability:{uuid.uuid4().hex[:16]}",
            resource_name=resource_name,
            is_available=is_available,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ResourceAllocation",
    "ResourceType",
    "AllocationPolicy",
    "ResourcePlanning",
    "ResourceAvailability",
]