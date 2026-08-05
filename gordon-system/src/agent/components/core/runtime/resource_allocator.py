# Resource Allocator - VRAM/RAM Allocation Authority
# ================================================

"""
Resource allocator for deterministic memory allocation and tracking.

This module provides:
- VRAM tracker for GPU memory
- RAM tracker for system memory
- Resource leasing with expiration
- Fragmentation management

Architecture Principle: Exactly ONE resource allocator instance exists.
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


# =============================================================================
# RESOURCE STATES AND LEASES
# =============================================================================


class ResourceState(Enum):
    """States of a resource allocation."""
    
    AVAILABLE = "available"         # Not allocated
    ALLOCATED = "allocated"         # Allocated but not necessarily active
    ACTIVE = "active"               # Currently in use
    RELEASING = "releasing"         # Being released
    RELEASED = "released"           # Released and available again


@dataclass(frozen=True)
class ResourceLease:
    """
    Immutable lease on a resource allocation.
    
    Represents a time-bound reservation of resources.
    """
    
    lease_id: str               # Unique lease ID
    resource_type: str          # "vram" or "ram"
    bytes_allocated: int        # Number of bytes allocated
    owner_id: str               # ID of the owner (e.g., model_id)
    
    # Timing - must come after required fields
    granted_at: float = field(default_factory=time.time)  # When lease was granted
    expires_at: Optional[float] = None  # Auto-release time (optional)
    
    @property
    def is_expired(self) -> bool:
        """Check if lease has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    @property
    def remaining_ms(self) -> float:
        """Get remaining lease time in milliseconds."""
        if self.expires_at is None:
            return float("inf")
        return max(0, (self.expires_at - time.time()) * 1000)


# =============================================================================
# TRACKERS
# =============================================================================


@dataclass(frozen=True)
class ResourceMetrics:
    """Resource utilization metrics."""
    
    total_bytes: int          # Total available
    allocated_bytes: int      # Currently allocated
    active_bytes: int         # Actively in use
    free_bytes: int           # Free (total - allocated)
    
    @property
    def utilization_percent(self) -> float:
        """Get utilization as percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.allocated_bytes / self.total_bytes) * 100


class VRAMTracker:
    """
    VRAM memory tracker for GPU memory management.
    
    Tracks:
    - Total VRAM available
    - Currently allocated VRAM
    - Fragmentation patterns
    - Active allocations
    
    Does NOT:
    - Allocate/deallocate actual GPU memory (handled by runtime adapters)
    - Own GPU devices (tracked separately)
    """
    
    def __init__(self, total_vram_bytes: int):
        """
        Initialize the VRAM tracker.
        
        Args:
            total_vram_bytes: Total available VRAM in bytes
        """
        self._total_vram = total_vram_bytes
        
        # Allocations (lease_id -> ResourceLease)
        self._allocations: Dict[str, ResourceLease] = {}
        
        # Fragmentation tracking
        self._fragmentation_count = 0
        
        # Statistics
        self._peak_allocated = 0
        
        self._lock = __import__("threading").Lock()
    
    @property
    def total_bytes(self) -> int:
        """Get total VRAM in bytes."""
        return self._total_vram
    
    @property
    def allocated_bytes(self) -> int:
        """Get currently allocated VRAM in bytes."""
        with self._lock:
            return sum(lease.bytes_allocated for lease in self._allocations.values())
    
    @property
    def free_bytes(self) -> int:
        """Get available VRAM in bytes."""
        return self._total_vram - self.allocated_bytes
    
    def get_metrics(self) -> ResourceMetrics:
        """
        Get current VRAM metrics.
        
        Returns:
            ResourceMetrics with utilization info
        """
        with self._lock:
            allocated = sum(
                lease.bytes_allocated 
                for lease in self._allocations.values()
            )
            
            return ResourceMetrics(
                total_bytes=self._total_vram,
                allocated_bytes=allocated,
                active_bytes=allocated,  # All allocated is considered active
                free_bytes=self._total_vram - allocated,
            )
    
    def allocate(
        self,
        owner_id: str,
        bytes_requested: int,
        duration_ms: Optional[int] = None,
    ) -> Tuple[bool, Optional[str], Optional[ResourceLease]]:
        """
        Allocate VRAM.
        
        Args:
            owner_id: Owner of the allocation (e.g., model_id)
            bytes_requested: Number of bytes to allocate
            duration_ms: Optional auto-release duration in ms
            
        Returns:
            Tuple of (success, lease_id, lease if successful)
        """
        with self._lock:
            if bytes_requested > self.free_bytes:
                return False, None, None
            
            lease = ResourceLease(
                lease_id=str(uuid.uuid4()),
                resource_type="vram",
                bytes_allocated=bytes_requested,
                granted_at=time.time(),
                expires_at=(
                    time.time() + (duration_ms / 1000)
                    if duration_ms else None
                ),
                owner_id=owner_id,
            )
            
            self._allocations[lease.lease_id] = lease
            
            # Update peak
            current_allocated = sum(
                l.bytes_allocated for l in self._allocations.values()
            )
            self._peak_allocated = max(self._peak_allocated, current_allocated)
            
            return True, lease.lease_id, lease
    
    def release(self, lease_id: str) -> bool:
        """
        Release a VRAM allocation.
        
        Args:
            lease_id: The lease to release
            
        Returns:
            True if released, False if not found
        """
        with self._lock:
            if lease_id not in self._allocations:
                return False
            
            del self._allocations[lease_id]
            return True
    
    def release_all(self, owner_id: str) -> int:
        """
        Release all allocations for an owner.
        
        Args:
            owner_id: Owner whose allocations to release
            
        Returns:
            Number of releases
        """
        with self._lock:
            leases_to_release = [
                lid for lid, lease in self._allocations.items()
                if lease.owner_id == owner_id
            ]
            
            for lease_id in leases_to_release:
                del self._allocations[lease_id]
            
            return len(leases_to_release)
    
    def find_fragments(self) -> List[int]:
        """
        Find allocation fragment sizes.
        
        Returns:
            List of allocated chunk sizes
        """
        with self._lock:
            return [
                lease.bytes_allocated
                for lease in self._allocations.values()
            ]
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired leases.
        
        Returns:
            Number of leases cleaned up
        """
        now = time.time()
        expired = []
        
        with self._lock:
            for lease_id, lease in list(self._allocations.items()):
                if lease.expires_at and now > lease.expires_at:
                    expired.append(lease_id)
            
            for lease_id in expired:
                del self._allocations[lease_id]
            
            return len(expired)


class RAMTracker:
    """
    System RAM memory tracker.
    
    Similar to VRAMTracker but for system memory.
    """
    
    def __init__(self, total_ram_bytes: int):
        """
        Initialize the RAM tracker.
        
        Args:
            total_ram_bytes: Total available RAM in bytes
        """
        self._total_ram = total_ram_bytes
        self._allocations: Dict[str, ResourceLease] = {}
        self._peak_allocated = 0
        
        self._lock = __import__("threading").Lock()
    
    @property
    def total_bytes(self) -> int:
        """Get total RAM in bytes."""
        return self._total_ram
    
    @property
    def allocated_bytes(self) -> int:
        """Get currently allocated RAM in bytes."""
        with self._lock:
            return sum(lease.bytes_allocated for lease in self._allocations.values())
    
    @property
    def free_bytes(self) -> int:
        """Get available RAM in bytes."""
        return self._total_ram - self.allocated_bytes
    
    def get_metrics(self) -> ResourceMetrics:
        """
        Get current RAM metrics.
        
        Returns:
            ResourceMetrics with utilization info
        """
        with self._lock:
            allocated = sum(
                lease.bytes_allocated 
                for lease in self._allocations.values()
            )
            
            return ResourceMetrics(
                total_bytes=self._total_ram,
                allocated_bytes=allocated,
                active_bytes=allocated,
                free_bytes=self._total_ram - allocated,
            )
    
    def allocate(
        self,
        owner_id: str,
        bytes_requested: int,
        duration_ms: Optional[int] = None,
    ) -> Tuple[bool, Optional[str], Optional[ResourceLease]]:
        """Allocate RAM."""
        with self._lock:
            if bytes_requested > self.free_bytes:
                return False, None, None
            
            lease = ResourceLease(
                lease_id=str(uuid.uuid4()),
                resource_type="ram",
                bytes_allocated=bytes_requested,
                granted_at=time.time(),
                expires_at=(
                    time.time() + (duration_ms / 1000)
                    if duration_ms else None
                ),
                owner_id=owner_id,
            )
            
            self._allocations[lease.lease_id] = lease
            
            current_allocated = sum(
                l.bytes_allocated for l in self._allocations.values()
            )
            self._peak_allocated = max(self._peak_allocated, current_allocated)
            
            return True, lease.lease_id, lease
    
    def release(self, lease_id: str) -> bool:
        """Release a RAM allocation."""
        with self._lock:
            if lease_id not in self._allocations:
                return False
            del self._allocations[lease_id]
            return True
    
    def release_all(self, owner_id: str) -> int:
        """Release all allocations for an owner."""
        with self._lock:
            leases_to_release = [
                lid for lid, lease in self._allocations.items()
                if lease.owner_id == owner_id
            ]
            
            for lease_id in leases_to_release:
                del self._allocations[lease_id]
            
            return len(leases_to_release)
    
    def cleanup_expired(self) -> int:
        """Clean up expired leases."""
        now = time.time()
        expired = []
        
        with self._lock:
            for lease_id, lease in list(self._allocations.items()):
                if lease.expires_at and now > lease.expires_at:
                    expired.append(lease_id)
            
            for lease_id in expired:
                del self._allocations[lease_id]
            
            return len(expired)


# =============================================================================
# RESOURCE ERRORS
# =============================================================================


class ResourceError(Exception):
    """Base exception for resource errors."""
    
    pass


class OutOfMemoryError(ResourceError):
    """Raised when memory is exhausted."""
    
    def __init__(
        self,
        message: str,
        requested: int = 0,
        available: int = 0,
    ):
        super().__init__(message)
        self.requested = requested
        self.available = available


# =============================================================================
# RESOURCE ALLOCATOR
# =============================================================================


class ResourceAllocator:
    """
    Canonical resource allocation authority.
    
    This is the SINGLE canonical authority for memory allocation in Gordon.
    
    Responsibilities:
        - Track VRAM and RAM usage
        - Manage resource leases with expiration
        - Prevent leaks through automatic cleanup
    
    Does NOT:
        - Allocate actual GPU/CPU memory (handled by runtimes)
        - Own compute resources (tracked separately)
    
    Architecture Invariants:
        - Exactly ONE allocator instance exists
        - Allocation is deterministic
        - No implicit allocation during import
    """
    
    def __init__(
        self,
        total_vram_bytes: int = 16 * 1024 * 1024 * 1024,  # 16 GB default
        total_ram_bytes: int = 32 * 1024 * 1024 * 1024,   # 32 GB default
    ):
        """
        Initialize the resource allocator.
        
        Args:
            total_vram_bytes: Total available VRAM
            total_ram_bytes: Total available RAM
        """
        self._vram_tracker = VRAMTracker(total_vram_bytes)
        self._ram_tracker = RAMTracker(total_ram_bytes)
        
        # Statistics
        self._total_allocations = 0
        self._total_releases = 0
        
        self._lock = __import__("threading").Lock()
    
    @property
    def vram(self) -> VRAMTracker:
        """Get the VRAM tracker."""
        return self._vram_tracker
    
    @property
    def ram(self) -> RAMTracker:
        """Get the RAM tracker."""
        return self._ram_tracker
    
    # -------------------------------------------------------------------------
    # Allocation (deterministic)
    # -------------------------------------------------------------------------
    
    def allocate(
        self,
        owner_id: str,
        bytes_requested: int,
        device_type: str = "cpu",
        duration_ms: Optional[int] = None,
    ) -> Tuple[bool, Optional[str], Optional[ResourceLease]]:
        """
        Allocate resources.
        
        Args:
            owner_id: Owner of the allocation
            bytes_requested: Number of bytes to allocate
            device_type: Device type ("cpu" or "gpu")
            duration_ms: Optional auto-release duration
            
        Returns:
            Tuple of (success, lease_id, lease if successful)
        """
        with self._lock:
            if device_type == "gpu" or "cuda" in device_type.lower():
                success, lease_id, lease = self._vram_tracker.allocate(
                    owner_id,
                    bytes_requested,
                    duration_ms
                )
            else:
                success, lease_id, lease = self._ram_tracker.allocate(
                    owner_id,
                    bytes_requested,
                    duration_ms
                )
            
            if success:
                self._total_allocations += 1
            
            return success, lease_id, lease
    
    def release(self, lease_id: str) -> bool:
        """
        Release a resource allocation.
        
        Args:
            lease_id: The lease to release
            
        Returns:
            True if released
        """
        with self._lock:
            # Try VRAM first
            if self._vram_tracker.release(lease_id):
                self._total_releases += 1
                return True
            
            # Then RAM
            if self._ram_tracker.release(lease_id):
                self._total_releases += 1
                return True
            
            return False
    
    def release_all(self, owner_id: str) -> int:
        """
        Release all allocations for an owner.
        
        Args:
            owner_id: Owner whose allocations to release
            
        Returns:
            Total number of releases (VRAM + RAM)
        """
        with self._lock:
            vram_released = self._vram_tracker.release_all(owner_id)
            ram_released = self._ram_tracker.release_all(owner_id)
            
            return vram_released + ram_released
    
    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired leases.
        
        Returns:
            Total number of leases cleaned up
        """
        with self._lock:
            vram_cleaned = self._vram_tracker.cleanup_expired()
            ram_cleaned = self._ram_tracker.cleanup_expired()
            
            return vram_cleaned + ram_cleaned
    
    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get allocator statistics.
        
        Returns:
            Dictionary of allocator metrics
        """
        with self._lock:
            vram_metrics = self._vram_tracker.get_metrics()
            ram_metrics = self._ram_tracker.get_metrics()
            
            return {
                "total_allocations": self._total_allocations,
                "total_releases": self._total_releases,
                "vram": {
                    "total_bytes": vram_metrics.total_bytes,
                    "allocated_bytes": vram_metrics.allocated_bytes,
                    "free_bytes": vram_metrics.free_bytes,
                    "utilization_percent": vram_metrics.utilization_percent,
                },
                "ram": {
                    "total_bytes": ram_metrics.total_bytes,
                    "allocated_bytes": ram_metrics.allocated_bytes,
                    "free_bytes": ram_metrics.free_bytes,
                    "utilization_percent": ram_metrics.utilization_percent,
                },
            }


__all__ = [
    # Enums
    "ResourceState",
    # Dataclasses
    "ResourceLease",
    "ResourceMetrics",
    # Trackers
    "VRAMTracker",
    "RAMTracker",
    # Exceptions
    "ResourceError",
    "OutOfMemoryError",
    # Allocator
    "ResourceAllocator",
]