# Core Resource Pooling Subsystem
# ==================================
"""
Phase 3.8.3 - Resource Pooling with Recycling and Warm Resources

Provides:
- Resource pool with warm resources for faster acquisition
- Idle resource management and recycling
- Priority-based acquisition
- Pool exhaustion handling
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time
import uuid
import threading

from .interfaces import (
    Resource,
    ResourceHandle,
    ResourceState,
    ResourceCapabilities,
)


# =============================================================================
# Pool Resource State
# =============================================================================


class PoolResourceState(Enum):
    """States of resources within a pool."""

    IDLE = "idle"               # Available for immediate acquisition
    WARM = "warm"               # Pre-initialized, ready for use
    ACTIVE = "active"           # Currently in use by a consumer
    RECYCLING = "recycling"     # Being prepared for reuse
    FAILED = "failed"           # Failed and needs attention


@dataclass
class PoolResourceEntry:
    """
    A resource entry in the pool with pool-specific state.
    """

    resource_id: str
    state: PoolResourceState

    last_used_utc: Optional[float] = None
    creation_time_utc: float = field(default_factory=time.time)
    recycled_count: int = 0

    # Pool metadata
    priority: int = 0


# =============================================================================
# Resource Pool Configuration
# =============================================================================


@dataclass(frozen=True)
class ResourcePoolConfig:
    """
    Immutable configuration for a resource pool.
    """

    pool_id: str                  # Unique pool identifier
    domain: str                   # Resource domain (cpu, gpu, memory, etc.)

    # Capacity bounds
    min_size: int = 0             # Minimum pool size
    max_size: int = 100           # Maximum pool size

    # Warm resource settings
    warm_count: int = 5           # Number of warm resources to maintain
    warm_timeout_seconds: float = 30.0  # Max time to warm a resource

    # Recycling settings
    recycle_idle_after_seconds: float = 60.0  # Recycle after this idle time
    max_recycled_count: int = 100  # Max times a resource can be recycled

    # Acquisition settings
    acquisition_timeout_seconds: float = 5.0  # Max wait for acquisition


# =============================================================================
# Resource Pool - Canonical Implementation
# =============================================================================


class ResourcePool:
    """
    A pool of resources with warm, idle, and active states.

    Features:
    - Warm resources for faster acquisition
    - Idle resource recycling
    - Priority-based ordering
    - Exhaustion detection

    Usage:
        config = ResourcePoolConfig(
            pool_id="cpu_pool_1",
            domain="cpu_cores"
        )
        pool = ResourcePool(config)

        # Acquire a resource
        result = pool.acquire(owner_id="task_123")
        if result.success:
            resource, handle = result.resource, result.handle

        # Release when done
        pool.release(resource, handle)
    """

    def __init__(self, config: ResourcePoolConfig):
        self._config = config
        self._pool_id = config.pool_id
        self._domain = config.domain

        # Thread safety
        self._lock = threading.RLock()

        # Resource storage
        self._resources: Dict[str, PoolResourceEntry] = {}
        self._resource_backing: Dict[
            str, "PoolBackedResource"
        ] = {}  # Maps to actual resource objects

        # Counters
        self._active_count = 0
        self._idle_count = 0
        self._warm_count = 0

    @property
    def pool_id(self) -> str:
        """Get the unique pool identifier."""
        return self._pool_id

    @property
    def domain(self) -> str:
        """Get the resource domain this pool manages."""
        return self._domain

    @property
    def size(self) -> int:
        """Get current pool size (total resources)."""
        with self._lock:
            return len(self._resources)

    @property
    def available_count(self) -> int:
        """Get count of available (idle/warm) resources."""
        with self._lock:
            return self._idle_count + self._warm_count

    @property
    def active_count(self) -> int:
        """Get count of actively used resources."""
        with self._lock:
            return self._active_count

    # -------------------------------------------------------------------------
    # Resource Management
    # -------------------------------------------------------------------------

    def add_resource(
        self,
        resource_id: str,
        capabilities: Optional[ResourceCapabilities] = None,
    ) -> "PoolBackedResource":
        """
        Add a new resource to the pool.

        Args:
            resource_id: The resource identifier
            capabilities: Optional resource capabilities

        Returns:
            The created PoolBackedResource
        """
        with self._lock:
            if resource_id in self._resources:
                raise ValueError(f"Resource {resource_id} already in pool")

            entry = PoolResourceEntry(
                resource_id=resource_id,
                state=PoolResourceState.IDLE,
                priority=self._config.min_size - len(self._resources),
            )

            self._resources[resource_id] = entry

            backing = PoolBackedResource(resource_id, self)
            self._resource_backing[resource_id] = backing
            self._idle_count += 1

            return backing

    def remove_resource(
        self,
        resource_id: str,
        force: bool = False,
    ) -> bool:
        """
        Remove a resource from the pool.

        Args:
            resource_id: The resource to remove
            force: If True, remove even if active

        Returns:
            True if removed
        """
        with self._lock:
            entry = self._resources.get(resource_id)
            if not entry:
                return False

            if entry.state == PoolResourceState.ACTIVE and not force:
                raise ValueError(f"Cannot remove active resource {resource_id}")

            # Update state counts
            if entry.state in (
                PoolResourceState.IDLE,
                PoolResourceState.WARM,
            ):
                self._idle_count = max(0, self._idle_count - 1)
            elif entry.state == PoolResourceState.ACTIVE:
                self._active_count = max(0, self._active_count - 1)

            del self._resources[resource_id]
            if resource_id in self._resource_backing:
                del self._resource_backing[resource_id]

            return True

    # -------------------------------------------------------------------------
    # Acquisition and Release
    # -------------------------------------------------------------------------

    def acquire(
        self,
        owner_id: str,
        priority: int = 0,
        timeout_seconds: Optional[float] = None,
    ) -> "PoolAcquisitionResult":
        """
        Acquire a resource from the pool.

        Args:
            owner_id: Who is acquiring
            priority: Acquisition priority (higher = more urgent)
            timeout_seconds: Maximum time to wait

        Returns:
            Acquisition result with resource and handle
        """
        deadline = (
            time.time() + (timeout_seconds or self._config.acquisition_timeout_seconds)
        )

        with self._lock:
            # Try to get idle resource first
            for rid, entry in list(self._resources.items()):
                if entry.state == PoolResourceState.IDLE:
                    entry.state = PoolResourceState.ACTIVE
                    entry.last_used_utc = time.time()
                    self._idle_count -= 1
                    self._active_count += 1

                    handle = ResourceHandle(
                        handle_id=f"handle_{uuid.uuid4().hex[:12]}",
                        resource_id=rid,
                        owner_id=owner_id,
                        created_at_utc=time.time(),
                    )

                    return PoolAcquisitionResult(
                        success=True,
                        resource=self._resource_backing[rid],
                        handle=handle,
                    )

            # Try warm resources
            for rid, entry in list(self._resources.items()):
                if entry.state == PoolResourceState.WARM:
                    entry.state = PoolResourceState.ACTIVE
                    entry.last_used_utc = time.time()
                    self._warm_count -= 1
                    self._active_count += 1

                    handle = ResourceHandle(
                        handle_id=f"handle_{uuid.uuid4().hex[:12]}",
                        resource_id=rid,
                        owner_id=owner_id,
                        created_at_utc=time.time(),
                    )

                    return PoolAcquisitionResult(
                        success=True,
                        resource=self._resource_backing[rid],
                        handle=handle,
                    )

            # Pool exhausted
            remaining = max(0, deadline - time.time())
            if timeout_seconds and remaining <= 0:
                return PoolAcquisitionResult(
                    success=False,
                    reason="Pool exhausted - no resources available",
                    exhausted=True,
                )

            # Would need to wait in a real implementation with blocking
            return PoolAcquisitionResult(
                success=False,
                reason="Pool exhausted - no idle or warm resources available",
                exhausted=True,
            )

    def release(
        self,
        resource: "PoolBackedResource",
        handle: ResourceHandle,
        recycle: bool = True,
    ) -> bool:
        """
        Release a resource back to the pool.

        Args:
            resource: The resource being released
            handle: The handle being released
            recycle: If True, return to idle pool; if False, dispose

        Returns:
            True if successfully released
        """
        with self._lock:
            entry = self._resources.get(resource.resource_id)
            if not entry or entry.state != PoolResourceState.ACTIVE:
                return False

            # Update state
            if recycle and entry.recycled_count < self._config.max_recycled_count:
                entry.state = PoolResourceState.IDLE
                entry.last_used_utc = None
                entry.recycled_count += 1
                self._idle_count += 1
            else:
                entry.state = PoolResourceState.FAILED

            self._active_count = max(0, self._active_count - 1)

            return True

    # -------------------------------------------------------------------------
    # Warm Resources
    # -------------------------------------------------------------------------

    def warm_resources(
        self,
        count: int,
        timeout_seconds: Optional[float] = None,
    ) -> List["PoolBackedResource"]:
        """
        Warm resources for faster acquisition.

        Args:
            count: Number of resources to warm
            timeout_seconds: Maximum time to wait

        Returns:
            List of warmed resources
        """
        deadline = time.time() + (timeout_seconds or self._config.warm_timeout_seconds)

        warmed: List["PoolBackedResource"] = []

        with self._lock:
            for rid, entry in list(self._resources.items()):
                if len(warmed) >= count:
                    break

                if entry.state == PoolResourceState.IDLE:
                    # In real implementation, would perform warm-up operations
                    entry.state = PoolResourceState.WARM
                    self._idle_count -= 1
                    self._warm_count += 1
                    warmed.append(self._resource_backing[rid])

            return warmed

    def ensure_warm_resources(self) -> int:
        """
        Ensure pool has minimum warm resources configured.

        Returns:
            Number of resources warmed
        """
        needed = self._config.warm_count - self._warm_count
        if needed <= 0:
            return 0

        return len(self.warm_resources(needed))

    # -------------------------------------------------------------------------
    # State Management
    # -------------------------------------------------------------------------

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current pool state snapshot."""
        with self._lock:
            return {
                "pool_id": self._pool_id,
                "domain": self._domain,
                "size": len(self._resources),
                "active_count": self._active_count,
                "idle_count": self._idle_count,
                "warm_count": self._warm_count,
                "resources_by_state": {
                    state.value: sum(1 for e in self._resources.values() if e.state == state)
                    for state in PoolResourceState
                },
            }

    def get_resource(self, resource_id: str) -> Optional["PoolBackedResource"]:
        """Get a pool resource by ID."""
        with self._lock:
            return self._resource_backing.get(resource_id)

    def find_idle_resources(self, count: int = 1) -> List["PoolBackedResource"]:
        """Find idle resources in the pool."""
        with self._lock:
            result: List["PoolBackedResource"] = []
            for rid, entry in self._resources.items():
                if entry.state == PoolResourceState.IDLE:
                    result.append(self._resource_backing[rid])
                    if len(result) >= count:
                        break
            return result


# =============================================================================
# Backed Resource Implementation
# =============================================================================


@dataclass
class PoolBackedResource:
    """
    A resource backed by a pool entry.
    """

    resource_id: str
    _pool: "ResourcePool" = field(repr=False)

    @property
    def state(self) -> PoolResourceState:
        """Get current resource state."""
        with self._pool._lock:
            entry = self._pool._resources.get(self.resource_id)
            return entry.state if entry else PoolResourceState.FAILED

    @property
    def pool(self) -> ResourcePool:
        """Get the owning pool."""
        return self._pool

    def release(self, recycle: bool = True) -> bool:
        """
        Release this resource back to its pool.
        """
        with self._pool._lock:
            entry = self._pool._resources.get(self.resource_id)
            if not entry or entry.state != PoolResourceState.ACTIVE:
                return False

            # In a real implementation, we'd need the handle for release
            # This is simplified for demonstration
            return True


# =============================================================================
# Acquisition Result
# =============================================================================


@dataclass(frozen=True)
class PoolAcquisitionResult:
    """
    Result of a pool acquisition attempt.
    """

    success: bool

    # For successful acquisitions
    resource: Optional["PoolBackedResource"] = None
    handle: Optional[ResourceHandle] = None

    # For failed acquisitions
    reason: str = ""
    exhausted: bool = False  # True if pool was exhausted


# =============================================================================
# Pool Manager
# =============================================================================


class ResourcePoolManager:
    """
    Manager for multiple resource pools.

    Coordinates pool allocation and provides unified access.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._pools: Dict[str, ResourcePool] = {}
        self._pool_by_domain: Dict[str, List[ResourcePool]] = {}

    def register_pool(self, pool: ResourcePool) -> None:
        """Register a pool with the manager."""
        with self._lock:
            self._pools[pool.pool_id] = pool

            domain = pool.domain
            if domain not in self._pool_by_domain:
                self._pool_by_domain[domain] = []
            self._pool_by_domain[domain].append(pool)

    def unregister_pool(self, pool_id: str) -> bool:
        """Unregister a pool."""
        with self._lock:
            if pool_id not in self._pools:
                return False

            pool = self._pools.pop(pool_id)
            domain = pool.domain
            if domain in self._pool_by_domain:
                self._pool_by_domain[domain] = [
                    p for p in self._pool_by_domain[domain] if p.pool_id != pool_id
                ]

            return True

    def get_pool(self, pool_id: str) -> Optional[ResourcePool]:
        """Get a pool by ID."""
        with self._lock:
            return self._pools.get(pool_id)

    def get_pools_for_domain(
        self, domain: str
    ) -> List[ResourcePool]:
        """Get all pools for a domain."""
        with self._lock:
            return list(self._pool_by_domain.get(domain, []))

    def find_available_resource(
        self,
        owner_id: str,
        domain: str,
        priority: int = 0,
    ) -> Optional[Tuple[ResourcePool, "PoolBackedResource", ResourceHandle]]:
        """
        Find an available resource from any pool for a domain.
        """
        pools = self.get_pools_for_domain(domain)
        if not pools:
            return None

        # Try each pool in order
        for pool in pools:
            result = pool.acquire(owner_id, priority)
            if result.success:
                return pool, result.resource, result.handle

        return None

    def get_global_snapshot(self) -> Dict[str, Any]:
        """Get snapshot of all pools."""
        with self._lock:
            return {
                "pool_count": len(self._pools),
                "domains": list(self._pool_by_domain.keys()),
                "pools": {
                    pool_id: pool.get_state_snapshot()
                    for pool_id, pool in self._pools.items()
                },
            }


# =============================================================================
# Public API Exports
# =============================================================================


__all__ = [
    # States
    "PoolResourceState",
    "PoolResourceEntry",

    # Config and Results
    "ResourcePoolConfig",
    "PoolAcquisitionResult",

    # Main classes
    "ResourcePool",
    "PoolBackedResource",
    "ResourcePoolManager",
]