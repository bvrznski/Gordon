# Core Resource Interface Hierarchy
# ==================================
"""
Phase 3.8.3 - Canonical Resource Management Interfaces

This module defines the canonical interface contracts for:
- Resource (base interface)
- ResourceHandle (usage handle)
- ResourceOwner (ownership contract)
- ResourceLease (temporary use rights)
- ResourcePool (resource pool with recycling)
- ResourceAllocator (allocation authority)
- ResourceRegistry (metadata registry)
- ResourceProvider (external resource source)

All implementations MUST conform to these contracts.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum
import time
import uuid


# =============================================================================
# Core Resource Identity Types
# =============================================================================


class ResourceId(str):
    """Unique identifier for a resource within the system."""

    def __new__(cls, value: str = ""):
        return super().__new__(cls, value)

    @classmethod
    def generate(cls) -> "ResourceId":
        return cls(value=f"res_{uuid.uuid4().hex[:16]}")

    @property
    def value(self) -> str:
        return self


class ResourceDomain(str):
    """Type of resource domain (cpu, gpu, memory, storage, etc.)."""

    def __new__(cls, value: str = ""):
        return super().__new__(cls, value)


# =============================================================================
# Core State Machine
# =============================================================================


class ResourceState(Enum):
    """
    Canonical resource lifecycle states.

    Transitions must be explicit and validated.
    """

    # Discovery states
    DISCOVERED = "discovered"       # Observed but not yet validated
    VALIDATED = "validated"         # Passed validation checks

    # Ready states
    AVAILABLE = "available"         # Ready for allocation
    RESERVED = "reserved"           # Reserved for future use

    # Allocation states
    ALLOCATED = "allocated"         # Permanently assigned
    LEASED = "leased"               # Has active lease
    IN_USE = "in_use"               # Currently being consumed

    # Degraded states
    DEGRADED = "degraded"           # Functional but degraded
    UNRELIABLE = "unreliable"       # May fail soon

    # Release states
    RELEASING = "releasing"         # In process of release
    RELEASED = "released"           # Released, awaiting cleanup
    RECLAIMED = "reclaimed"         # Reclaimed from owner

    # Unavailable states
    UNAVAILABLE = "unavailable"     # Not available for use
    FAILED = "failed"               # Failed, needs recovery
    QUARANTINED = "quarantined"     # Removed from rotation


# =============================================================================
# Capability Model
# =============================================================================


@dataclass(frozen=True)
class ResourceCapability:
    """
    A capability that a resource possesses.

    Capabilities are immutable properties of a resource.
    """

    name: str                       # e.g., "cuda", "tensor_core", "nvlink"
    version: Optional[str] = None   # Version if applicable
    enabled: bool = True            # Whether this capability is currently enabled


@dataclass(frozen=True)
class ResourceCapabilities:
    """
    Set of capabilities for a resource.
    """

    compute: Tuple[str, ...] = field(default_factory=tuple)     # e.g., "fp64", "int8"
    memory: Tuple[str, ...] = field(default_factory=tuple)      # e.g., "ecc", "high_bandwidth"
    io: Tuple[str, ...] = field(default_factory=tuple)          # e.g., "nvlink", "pcie_gen4"

    @property
    def all_capabilities(self) -> List[ResourceCapability]:
        """Get all capabilities as a list."""
        result: List[ResourceCapability] = []
        for name in self.compute:
            result.append(ResourceCapability(name=f"compute:{name}"))
        for name in self.memory:
            result.append(ResourceCapability(name=f"memory:{name}"))
        for name in self.io:
            result.append(ResourceCapability(name=f"io:{name}"))
        return result


# =============================================================================
# Resource Metadata
# =============================================================================


@dataclass(frozen=True)
class ResourceMetadata:
    """
    Immutable metadata about a resource.

    Used by ResourceRegistry for lookup and diagnostics.
    """

    # Identity
    resource_id: str
    domain: str
    kind: str                       # e.g., "logical_core", "gpu_device"

    # Classification
    vendor: Optional[str] = None    # Manufacturer/vendor name
    model: Optional[str] = None     # Model identifier
    serial_number: Optional[str] = None

    # Physical properties
    location: Optional[str] = None  # Physical location (rack, slot)
    topology: Dict[str, Any] = field(default_factory=dict)  # NUMA, PCI, etc.

    # Configuration
    is_exclusive: bool = False      # Can only be used by one owner at a time
    is_partitionable: bool = True   # Can be split into smaller units

    # Metadata (bounded)
    labels: Dict[str, str] = field(default_factory=dict)


# =============================================================================
# Resource Interface (Canonical Base)
# =============================================================================


@runtime_checkable
class Resource(Protocol):
    """
    Canonical interface for all managed resources.

    Every resource in the system MUST implement this interface.
    """

    @property
    def resource_id(self) -> str:
        """Get the unique identifier for this resource."""
        ...

    @property
    def domain(self) -> str:
        """Get the resource domain (cpu, gpu, memory, etc.)."""
        ...

    @property
    def state(self) -> ResourceState:
        """Get the current resource state."""
        ...

    @property
    def total_capacity(self) -> float:
        """Get total available capacity in domain units."""
        ...

    @property
    def free_capacity(self) -> float:
        """Get currently available capacity."""
        ...

    @property
    def used_capacity(self) -> float:
        """Get currently used capacity."""
        ...

    @property
    def metadata(self) -> ResourceMetadata:
        """Get resource metadata."""
        ...

    @property
    def capabilities(self) -> ResourceCapabilities:
        """Get resource capabilities."""
        ...

    @property
    def health_status(self) -> str:
        """Get current health status (healthy, degraded, failed, etc.)."""
        ...

    def can_use(self, owner_id: str, lease_id: Optional[str] = None) -> bool:
        """
        Check if this resource can be used by an owner.

        Args:
            owner_id: The owner requesting access
            lease_id: Optional lease ID for authorization

        Returns:
            True if use is authorized
        """
        ...

    def get_usage_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current usage statistics."""
        ...


# =============================================================================
# Resource Handle (Usage Token)
# =============================================================================


@dataclass(frozen=True)
class ResourceHandle:
    """
    A handle that authorizes use of a resource.

    This is the token given to consumers after allocation/lease.
    """

    handle_id: str                  # Unique identifier for this handle
    resource_id: str                # Which resource this grants access to
    owner_id: str                   # Who owns this handle

    lease_id: Optional[str] = None  # Link to lease if applicable
    created_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None  # When handle expires

    # Authorization context
    can_read: bool = True           # Can read resource state
    can_write: bool = False         # Can modify resource (if supported)
    can_control: bool = False       # Can control/operate resource

    def is_valid(self, owner_id: Optional[str] = None) -> bool:
        """
        Check if this handle is still valid.

        Args:
            owner_id: Optional owner ID to validate against

        Returns:
            True if handle is valid and authorized
        """
        # Check expiration
        if self.expires_at_utc and time.time() > self.expires_at_utc:
            return False

        # Check ownership if specified
        if owner_id and self.owner_id != owner_id:
            return False

        return True


# =============================================================================
# Resource Owner Interface
# =============================================================================


@runtime_checkable
class ResourceOwner(Protocol):
    """
    Interface for resource owners.

    Owners have authority over their allocated resources.
    """

    @property
    def owner_id(self) -> str:
        """Get the unique owner identifier."""
        ...

    @property
    def owner_type(self) -> str:
        """Get the type of owner (task, service, user)."""
        ...

    def can_access(
        self,
        resource: Resource,
        lease_id: Optional[str] = None,
        handle: Optional[ResourceHandle] = None,
    ) -> bool:
        """
        Check if this owner can access a resource.

        Args:
            resource: The resource to check
            lease_id: Optional lease ID for authorization
            handle: Optional handle for authorization

        Returns:
            True if access is authorized
        """
        ...

    def acquire_handle(
        self,
        resource: Resource,
        lease_id: Optional[str] = None,
    ) -> Optional[ResourceHandle]:
        """
        Acquire a handle for accessing this resource.

        Args:
            resource: The resource to get a handle for
            lease_id: Optional lease ID

        Returns:
            A valid handle, or None if acquisition failed
        """
        ...

    def release_handle(self, handle: ResourceHandle) -> bool:
        """
        Release a previously acquired handle.

        Args:
            handle: The handle to release

        Returns:
            True if successfully released
        """
        ...


# =============================================================================
# Resource Pool Interface
# =============================================================================


@dataclass(frozen=True)
class PoolResource:
    """
    A resource in a pool with its pool-specific metadata.
    """

    resource_id: str
    state: str                      # Pool-specific state (idle, active, warm)

    last_used_utc: Optional[float] = None
    creation_time_utc: float = field(default_factory=time.time)

    # Pool metadata
    pool_name: str = ""
    pool_priority: int = 0


@runtime_checkable
class ResourcePool(Protocol):
    """
    Interface for resource pooling.

    Pools manage groups of resources with shared characteristics.
    """

    @property
    def pool_id(self) -> str:
        """Get the unique pool identifier."""
        ...

    @property
    def domain(self) -> str:
        """Get the resource domain this pool manages."""
        ...

    @property
    def size(self) -> int:
        """Get current pool size (total resources)."""
        ...

    @property
    def available_count(self) -> int:
        """Get count of available (idle/warm) resources."""
        ...

    @property
    def active_count(self) -> int:
        """Get count of actively used resources."""
        ...

    def acquire_resource(
        self,
        owner_id: str,
        priority: int = 0,
    ) -> Optional[Tuple[Resource, ResourceHandle]]:
        """
        Acquire a resource from the pool.

        Args:
            owner_id: Who is acquiring
            priority: Acquisition priority

        Returns:
            Tuple of (resource, handle) or None if pool exhausted
        """

    def release_resource(
        self,
        resource: Resource,
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

    def warm_resources(
        self,
        count: int,
        timeout_seconds: Optional[float] = None,
    ) -> List[Resource]:
        """
        Warm resources for faster acquisition.

        Creates/prepares resources in advance of need.

        Args:
            count: Number of resources to warm
            timeout_seconds: Maximum time to wait

        Returns:
            List of warmed resources
        """

    def get_pool_snapshot(self) -> Dict[str, Any]:
        """Get current pool state snapshot."""
        ...


# =============================================================================
# Resource Allocator Interface
# =============================================================================


@runtime_checkable
class ResourceAllocator(Protocol):
    """
    Interface for resource allocators.

    Allocators make allocation decisions within their domain.
    """

    @property
    def allocator_id(self) -> str:
        """Get unique allocator identifier."""
        ...

    @property
    def domain(self) -> str:
        """Get the resource domain this allocator manages."""
        ...

    def can_allocate(
        self,
        requested_quantity: float,
        owner_id: Optional[str] = None,
        reservation_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if allocation is possible.

        Args:
            requested_quantity: Amount to allocate
            owner_id: Who will own the resource
            reservation_id: Optional existing reservation

        Returns:
            Tuple of (can_allocate, reason_if_not)
        """

    def allocate(
        self,
        requested_quantity: float,
        owner_id: str,
        reservation_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[Resource], Optional[str]]:
        """
        Allocate resources.

        Args:
            requested_quantity: Amount to allocate
            owner_id: Who will own the resource
            reservation_id: Optional existing reservation

        Returns:
            Tuple of (success, allocated_resource, reason_if_not)
        """

    def release(
        self,
        resource: Resource,
        reason: str = "",
    ) -> bool:
        """
        Release a previously allocated resource.

        Args:
            resource: The resource to release
            reason: Reason for release

        Returns:
            True if successfully released
        """

    def get_allocation_state(self) -> Dict[str, Any]:
        """Get current allocation state."""
        ...


# =============================================================================
# Resource Registry Interface
# =============================================================================


@runtime_checkable
class ResourceRegistry(Protocol):
    """
    Interface for resource registry.

    The registry owns metadata about resources, not the resources themselves.
    """

    @property
    def registry_id(self) -> str:
        """Get unique registry identifier."""
        ...

    def register(
        self,
        resource: Resource,
        metadata: ResourceMetadata,
    ) -> bool:
        """
        Register a resource with its metadata.

        Args:
            resource: The resource to register
            metadata: Its metadata

        Returns:
            True if registration successful
        """

    def deregister(self, resource_id: str) -> bool:
        """
        Remove a resource from the registry.

        Args:
            resource_id: ID of resource to remove

        Returns:
            True if removed
        """

    def lookup(
        self,
        resource_id: str,
    ) -> Tuple[Optional[Resource], Optional[ResourceMetadata]]:
        """
        Look up a resource by ID.

        Args:
            resource_id: The resource ID

        Returns:
            Tuple of (resource, metadata) or (None, None) if not found
        """

    def find_by_domain(
        self,
        domain: str,
        state_filter: Optional[ResourceState] = None,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        """
        Find resources by domain.

        Args:
            domain: The resource domain
            state_filter: Optional state filter

        Returns:
            List of (resource, metadata) tuples
        """

    def get_registry_snapshot(self) -> Dict[str, Any]:
        """Get registry state snapshot."""
        ...


# =============================================================================
# Resource Provider Interface
# =============================================================================


@runtime_checkable
class ResourceProvider(Protocol):
    """
    Interface for resource providers.

    Providers expose resources from external sources.
    """

    @property
    def provider_id(self) -> str:
        """Get unique provider identifier."""
        ...

    @property
    def domain(self) -> str:
        """Get the resource domain this provider serves."""
        ...

    @property
    def version(self) -> str:
        """Get provider implementation version."""
        ...

    def discover_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        """
        Discover available resources from this provider.

        Returns:
            List of (resource, metadata) tuples
        """

    def validate_health(
        self,
        resource: Resource,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate health of a resource from this provider.

        Args:
            resource: The resource to validate

        Returns:
            Tuple of (healthy, reason_if_not)
        """

    def get_provider_state(self) -> Dict[str, Any]:
        """Get current provider state."""
        ...


# =============================================================================
# Public API Exports
# =============================================================================


__all__ = [
    # Identity types
    "ResourceId",
    "ResourceDomain",

    # States and capabilities
    "ResourceState",
    "ResourceCapability",
    "ResourceCapabilities",
    "ResourceMetadata",

    # Core interfaces
    "Resource",
    "ResourceHandle",
    "ResourceOwner",
    "ResourcePool",
    "ResourceAllocator",
    "ResourceRegistry",
    "ResourceProvider",
]