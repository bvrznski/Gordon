# Core Resource Discovery
# =======================
"""
Side-effect-free resource discovery adapters.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time


@dataclass(frozen=True)
class DiscoverySource(Enum):
    """Sources of resource discovery."""
    OS = "os"                           # Operating system APIs
    CUDA = "cuda"                       # CUDA runtime
    NVML = "nvml"                       # NVIDIA Management Library
    PYTORCH = "pytorch"                 # PyTorch device API
    PROCESS_TABLE = "process_table"
    FILESYSTEM = "filesystem"
    NETWORK_INTERFACES = "network_interfaces"
    CONFIGURATION = "configuration"
    CONTAINER_RUNTIME = "container_runtime"
    SERVICE_REGISTRY = "service_registry"
    EXTERNAL_PROVIDER = "external_provider"


@dataclass(frozen=True)
class DiscoveryObservation:
    """
    A single observation of a resource during discovery.
    
    Immutable, side-effect-free - just records what was found.
    """
    resource_id: str
    domain: str                 # e.g., "cpu_cores", "gpu_vram_mb"
    quantity: float             # Amount available
    
    source: DiscoverySource
    source_version: str         # Version of the discovery mechanism
    
    timestamp_utc: float = field(default_factory=time.time)
    
    location: Optional[str] = None      # Physical location (PCI, NUMA node)
    topology: Dict[str, Any] = field(default_factory=dict)  # Topology info


@dataclass(frozen=True)
class DiscoveryResult:
    """
    Result of a discovery run.
    
    Contains all observations from one discovery cycle.
    """
    result_id: str
    timestamp_utc: float
    
    source: DiscoverySource
    version: str                # Discovery mechanism version
    
    observations: Tuple[DiscoveryObservation, ...]
    
    partial_failure: bool = False  # True if some sources failed partially


@dataclass(frozen=True)
class DiscoveryConfig:
    """
    Configuration for discovery.
    
    Immutable - set once at startup.
    """
    source: DiscoverySource
    refresh_interval_seconds: float
    
    enabled: bool = True
    max_observations: int = 1000    # Bounded history


class ResourceDiscoveryAdapter:
    """
    Adapter for resource discovery.
    
    Side-effect-free: only observes, never allocates or mutates state.
    Produces immutable observations.
    """
    
    def __init__(self, source: DiscoverySource, version: str):
        self.source = source
        self.version = version
    
    def discover(self) -> List[DiscoveryObservation]:
        """
        Perform discovery and return observations.
        
        Must be:
            - Side-effect-free (no mutations)
            - Bounded in time
            - Report partial failures
            - Preserve stale prior inventory separately
        """
        raise NotImplementedError("Subclass must implement discover()")
    
    def get_config(self) -> DiscoveryConfig:
        """Get discovery configuration."""
        return DiscoveryConfig(
            source=self.source,
            version=self.version,
            refresh_interval_seconds=60.0,  # Default
        )


class OsResourceDiscovery(ResourceDiscoveryAdapter):
    """
    OS-based resource discovery adapter.
    
    Discovers CPU cores, memory, network interfaces from the OS.
    """
    
    def __init__(self):
        super().__init__(source=DiscoverySource.OS, version="1.0")
    
    def discover(self) -> List[DiscoveryObservation]:
        """Discover OS resources."""
        # In real implementation, would query OS APIs
        observations = []
        
        # Example CPU cores observation
        observations.append(DiscoveryObservation(
            resource_id=f"cpu_{self.source.value}_core_0",
            domain="cpu_cores",
            quantity=1.0,
            source=self.source,
            source_version=self.version,
            location="physical",
        ))
        
        return observations


class CudaDiscoveryAdapter(ResourceDiscoveryAdapter):
    """
    CUDA-based GPU discovery adapter.
    
    Discovers GPU devices and VRAM via CUDA runtime.
    """
    
    def __init__(self):
        super().__init__(source=DiscoverySource.CUDA, version="1.0")
    
    def discover(self) -> List[DiscoveryObservation]:
        """Discover CUDA resources."""
        # In real implementation, would query CUDA runtime
        observations = []
        
        # Example GPU observation
        observations.append(DiscoveryObservation(
            resource_id=f"cuda_gpu_0",
            domain="gpu_devices",
            quantity=1.0,
            source=self.source,
            source_version=self.version,
            location="PCI:00:01.0",
        ))
        
        return observations


class DiscoveryEngine:
    """
    Engine for managing resource discovery.
    
    Coordinates multiple adapters and produces aggregated results.
    """
    
    def __init__(self, runtime_id: str):
        self.runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Registered adapters
        self._adapters: List[ResourceDiscoveryAdapter] = []
        
        # Discovery history (bounded)
        self._history: List[DiscoveryResult] = []
        self._max_history = 100
    
    def register_adapter(self, adapter: ResourceDiscoveryAdapter) -> None:
        """Register a discovery adapter."""
        with self._lock:
            self._adapters.append(adapter)
    
    def run_discovery(self) -> DiscoveryResult:
        """
        Run all adapters and aggregate results.
        
        Returns:
            Aggregated discovery result
        """
        with self._lock:
            all_observations: List[DiscoveryObservation] = []
            partial_failure = False
            
            for adapter in self._adapters:
                try:
                    observations = adapter.discover()
                    all_observations.extend(observations)
                except Exception as e:
                    partial_failure = True
                    # Log error but continue with other adapters
            
            result = DiscoveryResult(
                result_id=f"disc_{time.time():.0f}",
                timestamp_utc=time.time(),
                source=DiscoverySource.OS,  # Primary source for aggregation
                version="1.0",
                observations=tuple(all_observations),
                partial_failure=partial_failure,
            )
            
            self._history.append(result)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]
            
            return result
    
    def get_last_discovery(self) -> Optional[DiscoveryResult]:
        """Get the most recent discovery result."""
        with self._lock:
            if not self._history:
                return None
            return self._history[-1]
    
    def get_stale_observations(
        self,
        cutoff_seconds: float = 300.0  # 5 minutes default
    ) -> List[DiscoveryObservation]:
        """
        Get observations that are considered stale.
        
        These should be preserved separately from current inventory.
        """
        with self._lock:
            if not self._history:
                return []
            
            cutoff = time.time() - cutoff_seconds
            
            # Find observations older than cutoff in history
            stale = []
            for result in self._history:
                if result.timestamp_utc < cutoff:
                    stale.extend(result.observations)
            
            return stale


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "DiscoverySource",
    "DiscoveryObservation",
    "DiscoveryResult",
    "DiscoveryConfig",
    "ResourceDiscoveryAdapter",
    "OsResourceDiscovery",
    "CudaDiscoveryAdapter",
    "DiscoveryEngine",
]