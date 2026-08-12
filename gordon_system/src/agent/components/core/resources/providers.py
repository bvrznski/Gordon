# Core Resource Provider Architecture
# ====================================
"""
Phase 3.8.3 - Resource Providers for CPU, GPU, Memory, Storage & External Services

Provides:
- Provider interfaces with common contracts
- Provider registry for discovery and registration
- Health monitoring per provider
- Backend-independent resource access
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time
import uuid
import threading

from .interfaces import (
    Resource,
    ResourceMetadata,
    ResourceState,
    ResourceCapabilities,
)


# =============================================================================
# Provider Types
# =============================================================================


class ProviderType(Enum):
    """Types of resource providers."""

    CPU = "cpu"                   # CPU cores and topology
    GPU = "gpu"                   # GPU devices and VRAM
    MEMORY = "memory"             # RAM and storage memory
    STORAGE = "storage"           # Disk and filesystems
    NETWORK = "network"           # Network interfaces and connections
    PROCESS = "process"           # OS processes
    THREAD = "thread"             # OS threads
    EXTERNAL = "external"         # External services (LLM, DB, etc.)


# =============================================================================
# Provider Identity and State
# =============================================================================


@dataclass(frozen=True)
class ProviderIdentity:
    """
    Immutable identity of a provider.
    """

    provider_id: str                # Unique identifier
    provider_type: ProviderType     # What type of resources this serves
    version: str                    # Implementation version

    hostname: Optional[str] = None  # Host where provider runs (for distributed)
    region: Optional[str] = None    # Geographic region


class ProviderState(Enum):
    """
    State of a resource provider.
    """

    UNKNOWN = "unknown"             # Not yet evaluated
    INITIALIZING = "initializing"   # Starting up
    HEALTHY = "healthy"             # Fully operational
    DEGRADED = "degraded"           # Partial functionality
    UNAVAILABLE = "unavailable"     # Temporarily unavailable
    FAILED = "failed"               # Non-functional


# =============================================================================
# Provider Configuration
# =============================================================================


@dataclass(frozen=True)
class ProviderConfig:
    """
    Immutable configuration for a provider.
    """

    identity: ProviderIdentity

    enabled: bool = True            # Whether this provider is active
    refresh_interval_seconds: float = 60.0  # Health check interval

    max_connections: int = 10       # For external providers


# =============================================================================
# Resource Provider Interface (Canonical)
# =============================================================================


@dataclass
class ResourceProvider:
    """
    Base class for all resource providers.

    Each provider implements discovery, health monitoring, and capability reporting.
    """

    def __init__(self, config: ProviderConfig):
        self._config = config
        self._identity = config.identity

        self._lock = threading.RLock()

        # Resources known to this provider (discovered)
        self._resources: Dict[str, Tuple[Resource, ResourceMetadata]] = {}

        # Current state
        self._state = ProviderState.INITIALIZING
        self._last_health_check_utc: Optional[float] = None

    @property
    def provider_id(self) -> str:
        """Get the unique provider identifier."""
        return self._identity.provider_id

    @property
    def provider_type(self) -> ProviderType:
        """Get the resource type this provider serves."""
        return self._identity.provider_type

    @property
    def version(self) -> str:
        """Get provider implementation version."""
        return self._identity.version

    @property
    def state(self) -> ProviderState:
        """Get current provider state."""
        with self._lock:
            return self._state

    # -------------------------------------------------------------------------
    # Discovery and Resources
    # -------------------------------------------------------------------------

    def discover_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        """
        Discover resources available from this provider.

        Returns:
            List of (resource, metadata) tuples
        """
        raise NotImplementedError("Subclass must implement discover_resources()")

    def get_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        """Get currently known resources."""
        with self._lock:
            return list(self._resources.values())

    def register_resource(
        self, resource: Resource, metadata: ResourceMetadata
    ) -> bool:
        """
        Register a discovered resource.
        """
        with self._lock:
            if resource.resource_id in self._resources:
                return False

            self._resources[resource.resource_id] = (resource, metadata)
            return True

    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource."""
        with self._lock:
            if resource_id not in self._resources:
                return False

            del self._resources[resource_id]
            return True

    # -------------------------------------------------------------------------
    # Health Monitoring
    # -------------------------------------------------------------------------

    def validate_health(
        self,
        resource: Resource,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate health of a specific resource.

        Args:
            resource: The resource to validate

        Returns:
            Tuple of (healthy, reason_if_not)
        """
        raise NotImplementedError("Subclass must implement validate_health()")

    def check_provider_health(
        self,
    ) -> Tuple[ProviderState, Optional[str]]:
        """
        Check overall provider health.

        Returns:
            Tuple of (state, reason_if_unhealthy)
        """
        with self._lock:
            now = time.time()
            self._last_health_check_utc = now

            # Default: healthy if provider is enabled
            if not self._config.enabled:
                return ProviderState.UNAVAILABLE, "Provider disabled"

            return ProviderState.HEALTHY, None

    def get_provider_state(self) -> Dict[str, Any]:
        """Get current provider state."""
        with self._lock:
            resources = list(self._resources.values())
            healthy_count = sum(
                1 for r, _ in resources if r.state == ResourceState.AVAILABLE
            )

            return {
                "provider_id": self._identity.provider_id,
                "provider_type": self._identity.provider_type.value,
                "version": self._identity.version,
                "state": self._state.value,
                "enabled": self._config.enabled,
                "resource_count": len(resources),
                "healthy_resource_count": healthy_count,
                "last_health_check_utc": self._last_health_check_utc,
            }

    # -------------------------------------------------------------------------
    # Capability Reporting
    # -------------------------------------------------------------------------

    def get_capabilities(self) -> ResourceCapabilities:
        """
        Get capabilities supported by this provider.

        Returns immutable capabilities.
        """
        return ResourceCapabilities(compute=(), memory=(), io=())

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def start(self) -> bool:
        """Start the provider."""
        with self._lock:
            if self._state == ProviderState.HEALTHY:
                return True

            try:
                # Perform startup operations
                self.discover_resources()
                state, _ = self.check_provider_health()
                self._state = state
                return self._state in (ProviderState.HEALTHY, ProviderState.DEGRADED)
            except Exception:
                self._state = ProviderState.FAILED
                return False

    def stop(self) -> bool:
        """Stop the provider."""
        with self._lock:
            self._resources.clear()
            self._state = ProviderState.UNKNOWN
            return True


# =============================================================================
# CPU Provider
# =============================================================================


@dataclass(frozen=True)
class CPUResource(Resource):
    """
    A CPU core resource.
    """

    resource_id: str = ""
    _domain: str = "cpu_cores"

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def state(self) -> ResourceState:
        return ResourceState.AVAILABLE

    @property
    def total_capacity(self) -> float:
        return 1.0  # One full core

    @property
    def free_capacity(self) -> float:
        return self.total_capacity

    @property
    def used_capacity(self) -> float:
        return 0.0

    @property
    def metadata(self) -> ResourceMetadata:
        return ResourceMetadata(
            resource_id=self.resource_id,
            domain=self._domain,
            kind="logical_core",
            vendor="system",
        )

    @property
    def capabilities(self) -> ResourceCapabilities:
        return ResourceCapabilities(compute=("fp64", "int8"), memory=(), io=())

    @property
    def health_status(self) -> str:
        return "healthy"

    def can_use(self, owner_id: str, lease_id: Optional[str] = None) -> bool:
        return True

    def get_usage_snapshot(self) -> Dict[str, Any]:
        return {"utilization": 0.0}


@dataclass(frozen=True)
class CPUProviderConfig:
    """Configuration for CPU provider."""
    
    identity: ProviderIdentity
    enabled: bool = True


class CPUProvider(ResourceProvider):
    """
    Provider for CPU resources.

    Discovers logical CPU cores from the OS.
    """

    def __init__(self, config: CPUProviderConfig):
        super().__init__(config)
        self._cpu_count = 1  # Default

    def discover_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        """
        Discover CPU cores.

        In real implementation, would query OS for actual core count.
        """
        resources: List[Tuple[Resource, ResourceMetadata]] = []

        for i in range(self._cpu_count):
            resource = CPUResource(resource_id=f"cpu_core_{i}")
            metadata = ResourceMetadata(
                resource_id=resource.resource_id,
                domain="cpu_cores",
                kind="logical_core",
                vendor="system",
                labels={"core_index": str(i)},
            )
            resources.append((resource, metadata))

        return resources

    def validate_health(self, resource: Resource) -> Tuple[bool, Optional[str]]:
        if not isinstance(resource, CPUResource):
            return False, "Not a CPU resource"

        return True, None


# =============================================================================
# GPU Provider
# =============================================================================


@dataclass(frozen=True)
class GPUDevice(Resource):
    """
    A GPU device resource.
    """

    resource_id: str = ""
    _vram_mb: float = 0.0

    @property
    def domain(self) -> str:
        return "gpu_vram_mb"

    @property
    def state(self) -> ResourceState:
        return ResourceState.AVAILABLE

    @property
    def total_capacity(self) -> float:
        return self._vram_mb

    @property
    def free_capacity(self) -> float:
        return self.total_capacity

    @property
    def used_capacity(self) -> float:
        return 0.0

    @property
    def metadata(self) -> ResourceMetadata:
        return ResourceMetadata(
            resource_id=self.resource_id,
            domain="gpu_vram_mb",
            kind="gpu_device",
            vendor="nvidia",
            model="unknown",
        )

    @property
    def capabilities(self) -> ResourceCapabilities:
        return ResourceCapabilities(
            compute=("fp64", "fp16", "int8"),
            memory=("ecc",),
            io=("nvlink", "pcie_gen4"),
        )

    @property
    def health_status(self) -> str:
        return "healthy"

    def can_use(self, owner_id: str, lease_id: Optional[str] = None) -> bool:
        return True

    def get_usage_snapshot(self) -> Dict[str, Any]:
        return {"utilization": 0.0}


@dataclass(frozen=True)
class GPUProviderConfig:
    """Configuration for GPU provider."""
    
    identity: ProviderIdentity
    enabled: bool = True
    device_ids: List[int] = field(default_factory=list)


class GPUProvider(ResourceProvider):
    """
    Provider for GPU resources.

    Discovers GPU devices and their VRAM.
    """

    def __init__(self, config: GPUProviderConfig):
        super().__init__(config)
        self._device_ids = config.device_ids or [0]

    def discover_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        """
        Discover GPU devices.

        In real implementation, would query CUDA runtime.
        """
        resources: List[Tuple[Resource, ResourceMetadata]] = []

        for device_id in self._device_ids:
            # Example: 8GB VRAM per device
            vram_mb = 8192.0

            resource = GPUDevice(
                resource_id=f"gpu_{device_id}",
                _vram_mb=vram_mb,
            )

            metadata = ResourceMetadata(
                resource_id=resource.resource_id,
                domain="gpu_vram_mb",
                kind="gpu_device",
                vendor="nvidia",
                model="rtx_3090",  # Example
                labels={"device_id": str(device_id)},
            )

            resources.append((resource, metadata))

        return resources

    def validate_health(self, resource: Resource) -> Tuple[bool, Optional[str]]:
        if not isinstance(resource, GPUDevice):
            return False, "Not a GPU resource"

        # Check for any hardware errors
        return True, None


# =============================================================================
# Memory Provider
# =============================================================================


@dataclass(frozen=True)
class MemoryResource(Resource):
    """
    A memory region resource.
    """

    resource_id: str = ""
    _capacity_mb: float = 0.0

    @property
    def domain(self) -> str:
        return "memory_mb"

    @property
    def state(self) -> ResourceState:
        return ResourceState.AVAILABLE

    @property
    def total_capacity(self) -> float:
        return self._capacity_mb

    @property
    def free_capacity(self) -> float:
        return self.total_capacity

    @property
    def used_capacity(self) -> float:
        return 0.0

    @property
    def metadata(self) -> ResourceMetadata:
        return ResourceMetadata(
            resource_id=self.resource_id,
            domain="memory_mb",
            kind="memory_region",
            vendor="system",
        )

    @property
    def capabilities(self) -> ResourceCapabilities:
        return ResourceCapabilities(memory=("high_bandwidth",), io=(), compute=())

    @property
    def health_status(self) -> str:
        return "healthy"

    def can_use(self, owner_id: str, lease_id: Optional[str] = None) -> bool:
        return True

    def get_usage_snapshot(self) -> Dict[str, Any]:
        return {"utilization": 0.0}


@dataclass(frozen=True)
class MemoryProviderConfig:
    """Configuration for memory provider."""
    
    identity: ProviderIdentity
    enabled: bool = True


class MemoryProvider(ResourceProvider):
    """
    Provider for system memory (RAM) resources.
    """

    def __init__(self, config: MemoryProviderConfig):
        super().__init__(config)
        self._total_memory_mb = 16384.0  # Example: 16GB

    def discover_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        resources: List[Tuple[Resource, ResourceMetadata]] = []

        resource = MemoryResource(
            resource_id="system_memory",
            _capacity_mb=self._total_memory_mb,
        )

        metadata = ResourceMetadata(
            resource_id=resource.resource_id,
            domain="memory_mb",
            kind="system_memory",
            vendor="system",
        )

        resources.append((resource, metadata))
        return resources

    def validate_health(self, resource: Resource) -> Tuple[bool, Optional[str]]:
        if not isinstance(resource, MemoryResource):
            return False, "Not a memory resource"

        return True, None


# =============================================================================
# Storage Provider
# =============================================================================


@dataclass(frozen=True)
class StorageDevice(Resource):
    """
    A storage device resource.
    """

    resource_id: str = ""
    _capacity_gb: float = 0.0

    @property
    def domain(self) -> str:
        return "storage_gb"

    @property
    def state(self) -> ResourceState:
        return ResourceState.AVAILABLE

    @property
    def total_capacity(self) -> float:
        return self._capacity_gb

    @property
    def free_capacity(self) -> float:
        return self.total_capacity

    @property
    def used_capacity(self) -> float:
        return 0.0

    @property
    def metadata(self) -> ResourceMetadata:
        return ResourceMetadata(
            resource_id=self.resource_id,
            domain="storage_gb",
            kind="disk_device",
            vendor="ssd_vendor",
            model="nvme_ssd",
        )

    @property
    def capabilities(self) -> ResourceCapabilities:
        return ResourceCapabilities(io=("high_throughput", "low_latency"), memory=(), compute=())

    @property
    def health_status(self) -> str:
        return "healthy"

    def can_use(self, owner_id: str, lease_id: Optional[str] = None) -> bool:
        return True

    def get_usage_snapshot(self) -> Dict[str, Any]:
        return {"utilization": 0.0}


@dataclass(frozen=True)
class StorageProviderConfig:
    """Configuration for storage provider."""
    
    identity: ProviderIdentity
    enabled: bool = True


class StorageProvider(ResourceProvider):
    """
    Provider for storage devices.
    """

    def __init__(self, config: StorageProviderConfig):
        super().__init__(config)
        self._device_count = 1

    def discover_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        resources: List[Tuple[Resource, ResourceMetadata]] = []

        for i in range(self._device_count):
            resource = StorageDevice(
                resource_id=f"storage_device_{i}",
                _capacity_gb=500.0,  # Example: 500GB
            )

            metadata = ResourceMetadata(
                resource_id=resource.resource_id,
                domain="storage_gb",
                kind="disk_device",
                vendor="ssd_vendor",
                model="nvme_ssd",
            )

            resources.append((resource, metadata))

        return resources

    def validate_health(self, resource: Resource) -> Tuple[bool, Optional[str]]:
        if not isinstance(resource, StorageDevice):
            return False, "Not a storage device"

        return True, None


# =============================================================================
# Network Provider
# =============================================================================


@dataclass(frozen=True)
class NetworkInterface(Resource):
    """
    A network interface resource.
    """

    resource_id: str = ""
    _bandwidth_mbps: float = 0.0

    @property
    def domain(self) -> str:
        return "network_mbps"

    @property
    def state(self) -> ResourceState:
        return ResourceState.AVAILABLE

    @property
    def total_capacity(self) -> float:
        return self._bandwidth_mbps

    @property
    def free_capacity(self) -> float:
        return self.total_capacity

    @property
    def used_capacity(self) -> float:
        return 0.0

    @property
    def metadata(self) -> ResourceMetadata:
        return ResourceMetadata(
            resource_id=self.resource_id,
            domain="network_mbps",
            kind="network_interface",
            vendor="system",
        )

    @property
    def capabilities(self) -> ResourceCapabilities:
        return ResourceCapabilities(io=("high_bandwidth",), memory=(), compute=())

    @property
    def health_status(self) -> str:
        return "healthy"

    def can_use(self, owner_id: str, lease_id: Optional[str] = None) -> bool:
        return True

    def get_usage_snapshot(self) -> Dict[str, Any]:
        return {"utilization": 0.0}


@dataclass(frozen=True)
class NetworkProviderConfig:
    """Configuration for network provider."""
    
    identity: ProviderIdentity
    enabled: bool = True


class NetworkProvider(ResourceProvider):
    """
    Provider for network interfaces.
    """

    def __init__(self, config: NetworkProviderConfig):
        super().__init__(config)

    def discover_resources(
        self,
    ) -> List[Tuple[Resource, ResourceMetadata]]:
        resources: List[Tuple[Resource, ResourceMetadata]] = []

        # Example: one 10 Gbps interface
        resource = NetworkInterface(
            resource_id="network_interface_0",
            _bandwidth_mbps=10000.0,
        )

        metadata = ResourceMetadata(
            resource_id=resource.resource_id,
            domain="network_mbps",
            kind="network_interface",
            vendor="system",
        )

        resources.append((resource, metadata))
        return resources

    def validate_health(self, resource: Resource) -> Tuple[bool, Optional[str]]:
        if not isinstance(resource, NetworkInterface):
            return False, "Not a network interface"

        return True, None


# =============================================================================
# Provider Registry
# =============================================================================


class ProviderRegistry:
    """
    Registry for all resource providers.

    Manages provider lifecycle and provides discovery.
    """

    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id

        self._lock = threading.RLock()

        # Storage
        self._providers_by_id: Dict[str, ResourceProvider] = {}
        self._providers_by_type: Dict[ProviderType, List[ResourceProvider]] = {}

    def register_provider(self, provider: ResourceProvider) -> bool:
        """
        Register a provider with the registry.
        """
        with self._lock:
            if provider.provider_id in self._providers_by_id:
                return False

            self._providers_by_id[provider.provider_id] = provider

            ptype = provider.provider_type
            if ptype not in self._providers_by_type:
                self._providers_by_type[ptype] = []
            self._providers_by_type[ptype].append(provider)

            return True

    def unregister_provider(self, provider_id: str) -> bool:
        """
        Unregister a provider.
        """
        with self._lock:
            if provider_id not in self._providers_by_id:
                return False

            provider = self._providers_by_id.pop(provider_id)
            ptype = provider.provider_type

            if ptype in self._providers_by_type:
                self._providers_by_type[ptype] = [
                    p for p in self._providers_by_type[ptype]
                    if p.provider_id != provider_id
                ]

            return True

    def get_provider(
        self, provider_id: str
    ) -> Optional[ResourceProvider]:
        """Get a provider by ID."""
        with self._lock:
            return self._providers_by_id.get(provider_id)

    def get_providers_for_type(
        self, ptype: ProviderType
    ) -> List[ResourceProvider]:
        """Get all providers for a type."""
        with self._lock:
            return list(self._providers_by_type.get(ptype, []))

    def discover_all_resources(
        self,
    ) -> Dict[str, List[Tuple[Resource, ResourceMetadata]]]:
        """
        Discover resources from all providers.

        Returns: provider_id -> [(resource, metadata), ...]
        """
        with self._lock:
            result: Dict[
                str, List[Tuple[Resource, ResourceMetadata]]
            ] = {}

            for provider in self._providers_by_id.values():
                try:
                    resources = provider.discover_resources()
                    result[provider.provider_id] = resources
                except Exception:
                    # In real impl, would log error
                    pass

            return result

    def get_all_providers_state(
        self,
    ) -> Dict[str, Dict[str, Any]]:
        """Get state of all providers."""
        with self._lock:
            return {
                pid: provider.get_provider_state()
                for pid, provider in self._providers_by_id.items()
            }

    def check_all_health(self) -> Dict[str, Tuple[ProviderState, Optional[str]]]:
        """Check health of all providers."""
        with self._lock:
            return {
                pid: provider.check_provider_health()
                for pid, provider in self._providers_by_id.items()
            }


# =============================================================================
# Public API Exports
# =============================================================================


__all__ = [
    # Types and enums
    "ProviderType",
    "ProviderState",

    # Configuration
    "ProviderIdentity",
    "ProviderConfig",

    # Base classes
    "ResourceProvider",

    # Provider implementations
    "CPUProvider",
    "GPUProvider",
    "MemoryProvider",
    "StorageProvider",
    "NetworkProvider",

    # Registry
    "ProviderRegistry",

    # Resource types (for provider use)
    "CPUResource",
    "GPUDevice",
    "MemoryResource",
    "StorageDevice",
    "NetworkInterface",
]