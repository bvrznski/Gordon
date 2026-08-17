# Reasoning Resource Allocation - Phase 7.13
# ===========================================

"""
Canonical Reasoning Resource Allocation definition.

Resource allocation manages compute, memory, time, and other resources
for reasoning orchestration.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ResourceKind(Enum):
    """Kinds of computational resources."""
    
    # CPU resources
    COMPUTE_CORES = "compute_cores"         # CPU cores
    COMPUTE_SECONDS = "compute_seconds"     # CPU time
    
    # Memory resources
    MEMORY_MB = "memory_mb"                 # RAM in megabytes
    MEMORY_GB = "memory_gb"                 # RAM in gigabytes
    
    # Storage resources  
    STORAGE_MB = "storage_mb"               # Persistent storage MB
    STORAGE_GB = "storage_gb"               # Persistent storage GB
    
    # Time resources
    WALL_CLOCK_SECONDS = "wall_clock_seconds"  # Total time budget
    
    # Specialized resources
    GPU_CORES = "gpu_cores"                 # GPU cores
    GPU_MEMORY_MB = "gpu_memory_mb"         # GPU memory MB


@dataclass(frozen=True)
class AllocationConstraints:
    """
    Constraints on resource allocation.
    
    Defines hard limits for resource allocation decisions.
    """
    
    max_compute_cores: int = 16             # Maximum CPU cores
    max_memory_gb: float = 32.0             # Maximum RAM GB
    max_storage_gb: float = 100.0           # Maximum storage GB
    max_wall_clock_seconds: float = 3600.0  # Maximum total time (1 hour)
    
    min_compute_cores: int = 1              # Minimum CPU cores
    min_memory_gb: float = 1.0              # Minimum RAM GB


@dataclass(frozen=True)
class ReasoningResourceAllocation:
    """
    Resource allocation for reasoning execution.
    
    An allocation contains:
        - Identity and provenance
        - Allocated resources by kind
        - Allocation strategy used
        - Constraints that applied
    
    Resource allocations remain explicit and inspectable at all times.
    """
    
    # Identity
    allocation_id: str                      # Unique allocation identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Allocated resources
    allocated_resources: Dict[str, float]   # Resource kind -> amount
    
    # Allocation strategy
    allocation_strategy: str = "greedy"     # Strategy name
    
    # Constraints that applied
    allocation_constraints: AllocationConstraints = field(
        default_factory=AllocationConstraints
    )
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    allocated_at_utc: Optional[float] = None
    
    @property
    def total_compute_seconds(self) -> float:
        """Total compute seconds allocated."""
        return self.allocated_resources.get("compute_seconds", 0.0)
    
    @property
    def total_memory_gb(self) -> float:
        """Total memory GB allocated."""
        mb = self.allocated_resources.get("memory_mb", 0.0)
        return mb / 1024
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        allocated_resources: Dict[str, float],
        allocation_strategy: str = "greedy",
        constraints: Optional[AllocationConstraints] = None,
    ) -> ReasoningResourceAllocation:
        """Create a new resource allocation."""
        if constraints is None:
            constraints = AllocationConstraints()
        
        return cls(
            allocation_id=f"resource_allocation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            allocated_resources=allocated_resources,
            allocation_strategy=allocation_strategy,
            allocation_constraints=constraints,
            allocated_at_utc=time.time(),
        )
    
    def with_allocated_resources(self, resources: Dict[str, float]) -> ReasoningResourceAllocation:
        """Return a copy with updated resource allocation."""
        new_resources = dict(self.allocated_resources)
        new_resources.update(resources)
        return dataclass_replace(
            self,
            allocated_resources=new_resources,
        )
    
    def get_resource(self, kind: str) -> float:
        """Get allocated amount for a resource kind."""
        return self.allocated_resources.get(kind, 0.0)
    
    def has_exceeded(self, kind: str, limit: float) -> bool:
        """Check if allocation exceeded limit for a resource kind."""
        return self.get_resource(kind) > limit


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReasoningResourceAllocation",
    "ResourceKind",
    "AllocationConstraints",
]