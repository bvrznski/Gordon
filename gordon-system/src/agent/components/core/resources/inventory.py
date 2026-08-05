# Core Resource Inventory
# =======================
"""
Immutable resource inventory with versioning and discovery tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
import time

# =============================================================================
# Resource Identity Types
# =============================================================================

class ResourceDomainId(str):
    """Unique identifier for a resource domain (e.g., "cpu", "gpu", "memory")."""
    pass


@dataclass(frozen=True)
class ResourceId:
    """
    Stable, immutable resource identifier.
    
    A resource ID is stable across discovery refreshes and uniquely identifies
    a physical or logical resource within a runtime.
    """
    
    domain_id: str                    # e.g., "gpu"
    device_uuid: Optional[str] = None  # Physical device UUID if applicable
    logical_id: Optional[str] = None   # Logical ID (port, file path, etc.)
    generation: int = 1               # Generation for split-brain fencing
    
    @classmethod
    def from_device(cls, domain: str, uuid_str: str) -> "ResourceId":
        """Create a resource ID from a physical device."""
        return cls(domain_id=domain, device_uuid=uuid_str)
    
    @classmethod
    def from_logical(cls, domain: str, logical_id: str) -> "ResourceId":
        """Create a resource ID from a logical source."""
        return cls(domain_id=domain, logical_id=logical_id)
    
    def __str__(self) -> str:
        if self.device_uuid:
            return f"{self.domain_id}:{self.device_uuid}:gen{self.generation}"
        elif self.logical_id:
            return f"{self.domain_id}:{self.logical_id}:gen{self.generation}"
        return f"{self.domain_id}:unknown:gen{self.generation}"


@dataclass(frozen=True)
class ReservationId:
    """Unique identifier for a reservation."""
    value: str
    
    @classmethod
    def generate(cls) -> "ReservationId":
        return cls(value=f"res_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class AllocationId:
    """Unique identifier for an allocation."""
    value: str
    
    @classmethod
    def generate(cls) -> "AllocationId":
        return cls(value=f"alloc_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class LeaseId:
    """Unique identifier for a lease."""
    value: str
    
    @classmethod
    def generate(cls) -> "LeaseId":
        return cls(value=f"lease_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class OwnerId:
    """Unique identifier for an owner (task, service, etc.)."""
    value: str


@dataclass(frozen=True)
class GenerationEpoch:
    """
    Epoch counter for split-brain fencing.
    
    Each time a new authority is activated, the epoch increments.
    Old attempts with lower epochs are rejected.
    """
    value: int
    
    def next(self) -> "GenerationEpoch":
        return GenerationEpoch(value=self.value + 1)


# =============================================================================
# Resource State
# =============================================================================

class ResourceState(Enum):
    """
    Canonical resource states.
    
    Transitions:
        DISCOVERED → AVAILABLE
        AVAILABLE ↔ RESERVED ↔ ALLOCATED ↔ LEASED ↔ IN_USE
        IN_USE → DEGRADED (if issues detected)
        Any active state → UNAVAILABLE (if failure)
        UNAVAILABLE → QUARANTINED (after failed recovery attempts)
    """
    
    # Discovery states
    DISCOVERED = "discovered"         # Just discovered, not yet validated
    AVAILABLE = "available"           # Valid and ready for use
    
    # Reservation states
    RESERVED = "reserved"             # Held for potential allocation
    
    # Allocation states
    ALLOCATED = "allocated"           # Permanently assigned to an owner
    LEASED = "leased"                 # Has active lease (time-bound usage)
    IN_USE = "in_use"                 # Currently being used by consumer
    
    # Degraded states
    DEGRADED = "degraded"             # Functional but with issues
    UNDER_PRESSURE = "under_pressure" # Under resource pressure
    
    # Release states
    RELEASING = "releasing"           # In process of being released
    RELEASED = "released"             # Released but not yet reconciled
    
    # Unavailable states
    UNAVAILABLE = "unavailable"       # Not available for use
    FAILED = "failed"                 # Failed, needs recovery
    QUARANTINED = "quarantined"       # Removed from rotation
    DEREGISTERING = "deregistering"   # Being removed


# =============================================================================
# Resource Descriptor (Immutable Artifact)
# =============================================================================

@dataclass(frozen=True)
class ResourceDescriptor:
    """
    Immutable descriptor for a resource.
    
    This is the canonical record of a resource - no mutations allowed.
    All state changes go through ResourceManager.
    
    Properties that never change:
        - identity (resource_id, generation)
        - domain and kind
        - topology and capabilities
    
    Properties that can change (via refresh):
        - current capacity readings
        - health status
        - location info
    """
    
    # Identity
    resource_id: ResourceId           # Stable ID for this resource
    runtime_id: str                   # Which runtime owns this
    generation: int                   # For split-brain fencing
    
    # Classification
    domain: str                       # e.g., "cpu", "gpu", "memory"
    kind: str                         # e.g., "logical_core", "gpu_device", "vram"
    name: Optional[str] = None        # Human-readable name
    
    # Capacity (immutable from descriptor perspective) - MUST come before fields with defaults
    total_capacity: float = 0.0       # Total available capacity (default 0 for dataclass ordering)
    unit: str = "unit"                # Unit of measurement
    
    # Properties
    is_exclusive: bool = False        # Can only be used by one owner at a time
    is_partitionable: bool = True     # Can be split into smaller units
    is_reclaimable: bool = True       # Can be reclaimed from owner
    is_persistent: bool = False       # Survives runtime restart
    
    # Location
    location: Optional[str] = None    # Physical location (node, rack, etc.)
    
    # Health
    health_status: str = "healthy"    # Current health assessment
    
    # Topology
    numa_node: Optional[int] = None   # NUMA node for CPU/memory
    pci_address: Optional[str] = None  # PCI address for devices
    
    # Capabilities (fixed)
    capabilities: Tuple[str, ...] = field(default_factory=tuple)  # e.g., "cuda", "tensor_core"
    
    # Metadata (bounded size)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_available(self) -> bool:
        """Check if resource is in an available state."""
        return self.health_status == "healthy" and not self.is_persistent
    
    @classmethod
    def create_cpu_core(cls, core_id: int, runtime_id: str, generation: int = 1) -> "ResourceDescriptor":
        """Create a CPU core descriptor."""
        return cls(
            resource_id=ResourceId.from_logical("cpu", f"core_{core_id}"),
            runtime_id=runtime_id,
            generation=generation,
            domain="cpu",
            kind="logical_core",
            total_capacity=1.0,  # One full core
            unit="cores",
        )
    
    @classmethod
    def create_gpu_device(cls, device_uuid: str, vram_mb: float, runtime_id: str, generation: int = 1) -> "ResourceDescriptor":
        """Create a GPU device descriptor."""
        return cls(
            resource_id=ResourceId.from_device("gpu", device_uuid),
            runtime_id=runtime_id,
            generation=generation,
            domain="gpu",
            kind="gpu_device",
            total_capacity=vram_mb,
            unit="MB",
            capabilities=("cuda", "tensor_core") if vram_mb >= 8192 else ("cuda",),
        )


# =============================================================================
# Resource Inventory
# =============================================================================

class ResourceInventory:
    """
    Authoritative inventory of known resources.
    
    This is THE source of truth for what resources exist in the runtime.
    All resource operations must reference this inventory.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Core storage
        self._descriptors_by_id: Dict[str, ResourceDescriptor] = {}
        self._ids_by_domain: Dict[str, List[ResourceId]] = {}
        
        # Version tracking
        self._version = 0
        self._last_refresh_time: Optional[float] = None
        
        # Discovery source info (for validation)
        self._discovery_sources: Dict[str, Tuple[int, float]] = {}  # source_id -> (generation, timestamp)
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this inventory serves."""
        return self._runtime_id
    
    @property
    def version(self) -> int:
        """Get current inventory version."""
        with self._lock:
            return self._version
    
    def get_all_resource_ids(self) -> List[str]:
        """Get all registered resource IDs."""
        with self._lock:
            return list(self._descriptors_by_id.keys())
    
    def has_resource(self, resource_id: str) -> bool:
        """Check if a resource is in the inventory."""
        with self._lock:
            return resource_id in self._descriptors_by_id
    
    def get_descriptor(self, resource_id: str) -> Optional[ResourceDescriptor]:
        """Get descriptor for a resource."""
        with self._lock:
            return self._descriptors_by_id.get(resource_id)
    
    def get_all_descriptors(self) -> List[ResourceDescriptor]:
        """Get all descriptors."""
        with self._lock:
            return list(self._descriptors_by_id.values())
    
    def get_resources_by_domain(self, domain: str) -> List[ResourceDescriptor]:
        """Get all resources in a domain."""
        with self._lock:
            result = []
            for desc in self._descriptors_by_id.values():
                if desc.domain == domain:
                    result.append(desc)
            return result
    
    def add_descriptor(self, descriptor: ResourceDescriptor) -> None:
        """
        Add a new resource descriptor.
        
        Args:
            descriptor: The descriptor to add
            
        Raises:
            ValueError: If runtime mismatch or duplicate
        """
        with self._lock:
            if descriptor.runtime_id != self._runtime_id:
                raise ValueError(
                    f"Cannot add descriptor from {descriptor.runtime_id} "
                    f"to inventory for {self._runtime_id}"
                )
            
            resource_id_str = str(descriptor.resource_id)
            
            if resource_id_str in self._descriptors_by_id:
                # Update existing
                old_desc = self._descriptors_by_id[resource_id_str]
                if descriptor.generation <= old_desc.generation:
                    raise ValueError(
                        f"Cannot add descriptor with generation {descriptor.generation} "
                        f"when current is {old_desc.generation}"
                    )
            
            self._descriptors_by_id[resource_id_str] = descriptor
            
            # Update domain index
            if descriptor.domain not in self._ids_by_domain:
                self._ids_by_domain[descriptor.domain] = []
            if resource_id_str not in [str(r) for r in self._ids_by_domain[descriptor.domain]]:
                self._ids_by_domain[descriptor.domain].append(descriptor.resource_id)
            
            self._version += 1
    
    def remove_descriptor(self, resource_id: str) -> Optional[ResourceDescriptor]:
        """
        Remove a descriptor from the inventory.
        
        Args:
            resource_id: The ID to remove
            
        Returns:
            The removed descriptor, or None if not found
        """
        with self._lock:
            desc = self._descriptors_by_id.pop(resource_id, None)
            
            if desc and desc.domain in self._ids_by_domain:
                self._ids_by_domain[desc.domain] = [
                    rid for rid in self._ids_by_domain[desc.domain]
                    if str(rid) != resource_id
                ]
            
            if desc:
                self._version += 1
            
            return desc
    
    def update_descriptor(self, descriptor: ResourceDescriptor) -> None:
        """Update an existing descriptor (e.g., after refresh)."""
        with self._lock:
            resource_id_str = str(descriptor.resource_id)
            if resource_id_str in self._descriptors_by_id:
                # Update generation if higher
                old_desc = self._descriptors_by_id[resource_id_str]
                if descriptor.generation > old_desc.generation:
                    self._descriptors_by_id[resource_id_str] = descriptor
                    self._version += 1
    
    def record_discovery_source(
        self,
        source_id: str,
        generation: int
    ) -> None:
        """Record a discovery source for validation."""
        with self._lock:
            self._discovery_sources[source_id] = (generation, time.time())
    
    def get_snapshot(self) -> "ResourceInventorySnapshot":
        """Get an immutable snapshot of inventory state."""
        with self._lock:
            return ResourceInventorySnapshot(
                runtime_id=self._runtime_id,
                version=self._version,
                resource_count=len(self._descriptors_by_id),
                domain_counts={
                    domain: len(ids) 
                    for domain, ids in self._ids_by_domain.items()
                },
                descriptors=[d for d in self._descriptors_by_id.values()],
            )


@dataclass(frozen=True)
class ResourceInventorySnapshot:
    """
    Immutable snapshot of inventory state.
    
    Used for debugging and multi-runtime coordination.
    """
    runtime_id: str
    version: int
    resource_count: int
    domain_counts: Dict[str, int]
    descriptors: List[ResourceDescriptor]


# =============================================================================
# Discovery Source (external)
# =============================================================================

class ResourceDiscoveryAdapter:
    """
    Protocol for discovery adapters.
    
    Adapters discover resources from external sources without allocating them.
    The ResourceManager validates and registers observations.
    """
    
    async def discover(self) -> Tuple[List[ResourceDescriptor], Optional[str]]:
        """
        Discover resources.
        
        Returns:
            Tuple of (descriptors, partial_failure_reason_or_none)
            
        Must:
            - Not allocate any resources
            - Not mutate inventory directly
            - Preserve stale observations separately
            - Identify source and version
        """
        raise NotImplementedError


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    # Identity types
    "ResourceId",
    "ResourceDomainId",
    "ReservationId",
    "AllocationId",
    "LeaseId",
    "OwnerId",
    "GenerationEpoch",
    
    # States and descriptors
    "ResourceState",
    "ResourceDescriptor",
    
    # Inventory
    "ResourceInventory",
    "ResourceInventorySnapshot",
    
    # Discovery
    "ResourceDiscoveryAdapter",
]