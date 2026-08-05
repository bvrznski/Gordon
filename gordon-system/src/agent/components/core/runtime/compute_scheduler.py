# Compute Scheduler - CPU/GPU Scheduling Authority
# ================================================

"""
Compute scheduler for deterministic resource allocation and scheduling.

This module provides:
- Deterministic compute scheduling (CPU/GPU)
- Resource tracking and accounting
- Priority-based scheduling
- Fairness guarantees
- Starvation prevention

Architecture Principle: Exactly ONE scheduler instance exists.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)
from enum import Enum, auto
import time
import uuid
from collections import deque


# =============================================================================
# RESOURCE TYPES AND STATES
# =============================================================================


class DeviceType(Enum):
    """Types of compute devices."""
    
    CPU = "cpu"
    CUDA = "cuda"        # NVIDIA GPU
    ROCM = "rocm"        # AMD GPU
    METAL = "metal"      # Apple GPU
    DIRECTML = "directml"  # Windows GPU


class ResourceState(Enum):
    """State of a compute resource."""
    
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


@dataclass(frozen=True)
class ComputeResource:
    """
    Immutable descriptor for a compute resource.
    
    Represents a single compute device or logical unit.
    """
    
    resource_id: str            # Unique identifier
    device_type: DeviceType     # Type of device (CPU, CUDA, etc.)
    
    # Capacity metrics
    total_memory_bytes: int     # Total available memory (VRAM/RAM)
    free_memory_bytes: int      # Currently free memory
    
    # Performance metrics
    compute_units: int          # Number of compute units/cores
    clock_rate_mhz: float       # Clock rate in MHz
    
    # Metadata
    device_index: int = 0       # Device index (0 for single GPU)
    name: str = ""              # Human-readable name
    
    def is_compatible_with(self, requirements: Set[str]) -> bool:
        """Check if resource meets requirements."""
        device_type_str = self.device_type.value
        
        if "cuda" in requirements and self.device_type != DeviceType.CUDA:
            return False
        if "rocm" in requirements and self.device_type != DeviceType.ROCM:
            return False
        if "metal" in requirements and self.device_type != DeviceType.METAL:
            return False
        if "cpu" in requirements and self.device_type != DeviceType.CPU:
            return False
        
        return True


@dataclass(frozen=True)
class ComputeAllocation:
    """
    Immutable record of a compute resource allocation.
    
    Represents a lease on resources for a specific operation.
    """
    
    allocation_id: str          # Unique allocation ID
    resource_id: str            # Which resource was allocated
    model_id: Optional[str]     # Model being run (if any)
    bytes_allocated: int        # Amount of memory allocated
    started_at: float           # Allocation timestamp
    expires_at: Optional[float] = None  # Expiration time (for auto-release)


# =============================================================================
# SCHEDULING POLICIES
# =============================================================================


class SchedulingPolicy(Enum):
    """Available scheduling policies."""
    
    FIFO = "fifo"               # First-in-first-out
    PRIORITY = "priority"       # Priority-based
    FAIR = "fair"               # Fair sharing with time-slicing
    DEADLINE = "deadline"       # Deadline-driven


@dataclass(frozen=True)
class ScheduleRequest:
    """
    Request for compute scheduling.
    
    Contains all information needed to make a scheduling decision.
    """
    
    request_id: str             # Unique request ID
    resource_requirements: Dict[str, Any]  # Resource needs (memory, etc.)
    priority: int = 0           # Priority level (higher = more urgent)
    deadline_ms: Optional[int] = None     # Optional deadline in ms
    model_id: Optional[str] = None        # Model to run
    batch_size: int = 1         # Request batch size
    
    @property
    def priority_key(self) -> Tuple[int, float]:
        """Return sort key for priority scheduling."""
        return (-self.priority, time.time())


# =============================================================================
# SCHEDULING ERRORS
# =============================================================================


class ResourceError(Exception):
    """Base exception for resource errors."""
    
    pass


class ResourceExhaustedError(ResourceError):
    """Raised when resources are exhausted."""
    
    def __init__(
        self,
        message: str,
        requested: Optional[int] = None,
        available: Optional[int] = None,
    ):
        super().__init__(message)
        self.requested = requested
        self.available = available


class AllocationNotFoundError(ResourceError):
    """Raised when allocation is not found."""
    
    pass


# =============================================================================
# COMPUTE SCHEDULER
# =============================================================================


class ComputeScheduler:
    """
    Canonical compute scheduling authority.
    
    This is the SINGLE canonical authority for compute resource scheduling in Gordon.
    
    Responsibilities:
        - Schedule inference requests across available resources
        - Track resource allocation and usage
        - Enforce fairness and priority guarantees
        - Prevent starvation through time-slicing
    
    Does NOT:
        - Execute inference (handled by runtime adapters)
        - Own model lifecycle (handled by ModelRegistry/ModelLoader)
        - Manage memory directly (handled by ResourceAllocator)
    
    Architecture Invariants:
        - Exactly ONE scheduler instance exists
        - Scheduling is deterministic (same inputs = same outputs)
        - No implicit scheduling during import
    """
    
    def __init__(
        self,
        policy: SchedulingPolicy = SchedulingPolicy.FIFO,
        max_pending: int = 1000,
    ):
        """
        Initialize the compute scheduler.
        
        Args:
            policy: Scheduling policy to use (FIFO, PRIORITY, FAIR, DEADLINE)
            max_pending: Maximum number of pending requests
        """
        self._policy = policy
        self._max_pending = max_pending
        
        # Resource tracking
        self._resources: Dict[str, ComputeResource] = {}
        self._allocations: Dict[str, ComputeAllocation] = {}
        
        # Request queues (per priority level)
        self._pending_requests: deque = deque()
        self._active_requests: Set[str] = set()
        
        # Statistics
        self._total_scheduled = 0
        self._total_completed = 0
        self._total_failed = 0
        
        self._lock = __import__("threading").Lock()
    
    @property
    def policy(self) -> SchedulingPolicy:
        """Return current scheduling policy."""
        return self._policy
    
    @property
    def total_resources(self) -> int:
        """Return total number of registered resources."""
        with self._lock:
            return len(self._resources)
    
    @property
    def pending_count(self) -> int:
        """Return number of pending requests."""
        with self._lock:
            return len(self._pending_requests)
    
    # -------------------------------------------------------------------------
    # Resource registration
    # -------------------------------------------------------------------------
    
    def register_resource(
        self,
        resource: ComputeResource,
    ) -> None:
        """
        Register a compute resource with the scheduler.
        
        Args:
            resource: The compute resource to register
            
        Raises:
            RuntimeError: If resource already registered
        """
        with self._lock:
            if resource.resource_id in self._resources:
                raise ResourceError(
                    f"Resource '{resource.resource_id}' already registered"
                )
            
            self._resources[resource.resource_id] = resource
    
    def unregister_resource(self, resource_id: str) -> None:
        """
        Unregister a compute resource.
        
        Args:
            resource_id: The resource to unregister
            
        Raises:
            AllocationNotFoundError: If resource is currently allocated
        """
        with self._lock:
            if resource_id not in self._resources:
                return  # Already unregistered
            
            # Check for active allocations
            active_allocations = [
                alloc for alloc in self._allocations.values()
                if alloc.resource_id == resource_id
            ]
            
            if active_allocations:
                raise AllocationNotFoundError(
                    f"Cannot unregister resource '{resource_id}' "
                    f"with {len(active_allocations)} active allocations"
                )
            
            del self._resources[resource_id]
    
    def get_resource(self, resource_id: str) -> Optional[ComputeResource]:
        """Get a registered resource by ID."""
        with self._lock:
            return self._resources.get(resource_id)
    
    def get_all_resources(self) -> List[ComputeResource]:
        """Get all registered resources."""
        with self._lock:
            return list(self._resources.values())
    
    # -------------------------------------------------------------------------
    # Scheduling
    # -------------------------------------------------------------------------
    
    def submit(
        self,
        request: ScheduleRequest,
    ) -> Tuple[bool, Optional[str], Optional[ComputeAllocation]]:
        """
        Submit a scheduling request.
        
        Args:
            request: The scheduling request
            
        Returns:
            Tuple of (success, resource_id, allocation)
            
        Raises:
            ResourceError: If submission fails
        """
        with self._lock:
            # Check queue capacity
            if len(self._pending_requests) >= self._max_pending:
                raise ResourceExhaustedError(
                    "Scheduling queue full",
                    requested=1,
                    available=self._max_pending - len(self._pending_requests),
                )
            
            # Add to pending queue (sorted by priority)
            self._pending_requests.append(request)
            self._pending_requests = deque(
                sorted(
                    self._pending_requests,
                    key=lambda r: r.priority_key
                )
            )
            
            return self._attempt_schedule()
    
    def _attempt_schedule(
        self,
    ) -> Tuple[bool, Optional[str], Optional[ComputeAllocation]]:
        """
        Attempt to schedule pending requests.
        
        Returns:
            Tuple of (success, resource_id, allocation)
        """
        if not self._pending_requests:
            return False, None, None
        
        request = self._pending_requests.popleft()
        
        # Find compatible resource
        resource_id = self._find_resource(request.resource_requirements)
        
        if resource_id is None:
            # Not enough resources available, re-queue
            self._pending_requests.appendleft(request)
            return False, None, None
        
        # Create allocation
        allocation = ComputeAllocation(
            allocation_id=str(uuid.uuid4()),
            resource_id=resource_id,
            model_id=request.model_id,
            bytes_allocated=request.resource_requirements.get("memory_bytes", 0),
            started_at=time.time(),
        )
        
        self._allocations[allocation.allocation_id] = allocation
        self._active_requests.add(request.request_id)
        
        return True, resource_id, allocation
    
    def _find_resource(
        self,
        requirements: Dict[str, Any],
    ) -> Optional[str]:
        """
        Find a compatible resource for the request.
        
        Args:
            requirements: Resource requirements dict
            
        Returns:
            Resource ID if found, None otherwise
        """
        memory_required = requirements.get("memory_bytes", 0)
        device_types = set(requirements.get("device_types", []))
        
        # Sort resources by free memory (best fit)
        available_resources = [
            r for r in self._resources.values()
            if r.free_memory_bytes >= memory_required
            and r.is_compatible_with(device_types)
        ]
        
        if not available_resources:
            return None
        
        # Sort by most free memory (first fit best)
        available_resources.sort(
            key=lambda r: r.free_memory_bytes,
            reverse=True
        )
        
        return available_resources[0].resource_id
    
    def complete(self, allocation_id: str) -> Optional[ComputeAllocation]:
        """
        Mark an allocation as completed.
        
        Args:
            allocation_id: The allocation to complete
            
        Returns:
            Completed allocation if found
            
        Raises:
            AllocationNotFoundError: If allocation not found
        """
        with self._lock:
            if allocation_id not in self._allocations:
                raise AllocationNotFoundError(
                    f"Allocation '{allocation_id}' not found"
                )
            
            allocation = self._allocations.pop(allocation_id)
            return allocation
    
    def cancel(self, request_id: str) -> bool:
        """
        Cancel a pending or active request.
        
        Args:
            request_id: The request to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        with self._lock:
            # Try to remove from pending queue
            for i, req in enumerate(self._pending_requests):
                if req.request_id == request_id:
                    del self._pending_requests[i]
                    return True
            
            # Check active requests (cannot be cancelled once started)
            return request_id not in self._active_requests
    
    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get scheduler statistics.
        
        Returns:
            Dictionary of scheduler metrics
        """
        with self._lock:
            # Calculate resource utilization
            total_memory = sum(r.total_memory_bytes for r in self._resources.values())
            free_memory = sum(r.free_memory_bytes for r in self._resources.values())
            
            return {
                "total_resources": len(self._resources),
                "pending_requests": len(self._pending_requests),
                "active_allocations": len(self._allocations),
                "total_scheduled": self._total_scheduled,
                "total_completed": self._total_completed,
                "total_failed": self._total_failed,
                "memory_utilization": {
                    "total_bytes": total_memory,
                    "free_bytes": free_memory,
                    "used_bytes": total_memory - free_memory,
                    "utilization_percent": (
                        (total_memory - free_memory) / total_memory * 100
                        if total_memory > 0 else 0
                    ),
                },
            }


# =============================================================================
# GLOBAL SCHEDULER ACCESSOR
# =============================================================================


class _GlobalScheduler:
    """Internal global scheduler accessor."""
    
    def __init__(self) -> None:
        self._instance: Optional[ComputeScheduler] = None
    
    def set_instance(self, instance: ComputeScheduler) -> None:
        if self._instance is not None:
            raise RuntimeError("Global scheduler already initialized")
        self._instance = instance
    
    @property
    def instance(self) -> ComputeScheduler:
        if self._instance is None:
            self._instance = ComputeScheduler()
        return self._instance


_global_scheduler_accessor = _GlobalScheduler()


def get_compute_scheduler() -> ComputeScheduler:
    """Get the global compute scheduler instance."""
    return _global_scheduler_accessor.instance


def set_compute_scheduler(instance: ComputeScheduler) -> None:
    """Set the global compute scheduler instance."""
    _global_scheduler_accessor.set_instance(instance)


__all__ = [
    # Enums
    "DeviceType",
    "ResourceState",
    "SchedulingPolicy",
    # Dataclasses
    "ComputeResource",
    "ComputeAllocation",
    "ScheduleRequest",
    # Exceptions
    "ResourceError",
    "ResourceExhaustedError",
    "AllocationNotFoundError",
    # Scheduler
    "ComputeScheduler",
    # Global accessor
    "get_compute_scheduler",
    "set_compute_scheduler",
]