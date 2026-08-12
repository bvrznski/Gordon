# Provider Framework - Phase 3.8.8.4
# ====================================
"""
Canonical Provider Framework for plugin capability exposure.

Provides:
- Provider descriptors and metadata
- Extension API contracts
- Dynamic composition support
- Adapter model for protocol conversion

Architecture:
    Plugin -> Provider -> ExtensionPoint -> Core
    
Where:
    - Plugin implements providers
    - Providers expose capabilities via extension points
    - Core consumes extensions through adapter layer
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Callable,
    Type,
    Set,
    Any,
)
from enum import Enum
import time

# Import from abstraction module
try:
    from .abstraction import (
        CapabilityId,
        PluginVersion,
        PluginContext,
        ExtensionPoint,
        ExtensionDescriptor,
        Extension,
    )
except ImportError:
    class CapabilityId:
        pass
    
    class PluginVersion:
        pass


class ProviderState(Enum):
    """States of provider lifecycle."""
    
    UNINITIALIZED = "uninitialized"   # Created but not initialized
    INITIALIZING = "initializing"     # Currently initializing
    INITIALIZED = "initialized"       # Ready for use
    STARTING = "starting"             # Starting up
    ACTIVE = "active"                 # Fully operational
    SUSPENDED = "suspended"           # Temporarily paused
    SHUTTING_DOWN = "shutting_down"   # Shutting down
    FAILED = "failed"                 # Failed state


@dataclass(frozen=True)
class ProviderIdentity:
    """
    Immutable identity of a provider.
    
    Used to uniquely identify providers in the registry and for routing.
    """
    
    provider_id: str                  # Unique identifier
    provider_type: str               # e.g., "llm", "embeddings"
    version: str                     # Provider implementation version
    
    hostname: Optional[str] = None   # Host where provider runs (for distributed)
    region: Optional[str] = None     # Geographic region
    
    @property
    def full_id(self) -> str:
        """Return fully qualified provider ID."""
        return f"{self.provider_id}@{self.version}"


@dataclass(frozen=True)
class ProviderConfig:
    """
    Configuration for a provider.
    
    Immutable configuration that defines how a provider is set up.
    """
    
    identity: ProviderIdentity
    
    enabled: bool = True             # Whether this provider is active
    priority: int = 50               # Higher = preferred for selection
    
    # Connection settings
    max_connections: int = 10
    connection_timeout_seconds: float = 30.0
    
    # Retry settings
    retry_count: int = 3
    retry_backoff_base_seconds: float = 0.1
    
    @classmethod
    def with_priority(cls, identity: ProviderIdentity, priority: int) -> "ProviderConfig":
        """Create config with specified priority."""
        return cls(
            identity=identity,
            enabled=True,
            priority=priority,
        )


@dataclass(frozen=True)
class CapabilityRegistration:
    """
    Registration of a capability by a provider.
    
    Links capabilities to their providers and tracks metadata.
    """
    
    capability_id: CapabilityId
    provider_id: str
    version: PluginVersion
    
    # Metadata
    name: str
    description: Optional[str] = None
    
    # Configuration
    enabled: bool = True
    config_hash: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Return fully qualified capability name."""
        return f"{self.capability_id.domain}:{self.capability_id.name}@{str(self.version)}"


# =============================================================================
# PROVIDER BASE CLASS
# =============================================================================


class Provider(ExtensionPoint):
    """
    Base class for all providers.
    
    Providers implement extension points by inheriting from this class and
    implementing the required abstract methods. Each provider:
        - Implements one or more capability interfaces
        - Registers itself with the capability registry
        - Exposes health and status information
    
    Lifecycle:
        1. __init__(context, config) - Constructor
        2. initialize() - One-time setup
        3. start() - Start accepting requests
        4. stop() - Stop accepting requests
        5. shutdown() - Clean up resources
    """
    
    def __init__(
        self,
        context: PluginContext,
        config: ProviderConfig,
    ):
        """Initialize the provider."""
        self._context = context
        self._config = config
        self._identity = config.identity
        self._state = ProviderState.UNINITIALIZED
    
    @property
    def provider_id(self) -> str:
        """Get the provider identifier."""
        return self._identity.provider_id
    
    @property
    def provider_type(self) -> str:
        """Get the provider type."""
        return self._identity.provider_type
    
    @property
    def version(self) -> str:
        """Get the provider version."""
        return self._identity.version
    
    @property
    def state(self) -> ProviderState:
        """Get current provider state."""
        return self._state
    
    @property
    def context(self) -> PluginContext:
        """Get the plugin context."""
        return self._context
    
    @property
    def config(self) -> ProviderConfig:
        """Get the provider configuration."""
        return self._config
    
    # -------------------------------------------------------------------------
    # Extension Point Implementation
    # -------------------------------------------------------------------------
    
    @property
    def extension_point_id(self) -> str:
        """Unique identifier for this extension point type."""
        return f"provider:{self.provider_type}"
    
    @property
    def api_version(self) -> str:
        """Extension point API version."""
        return "1.0.0"
    
    # -------------------------------------------------------------------------
    # Lifecycle Methods (override as needed)
    # -------------------------------------------------------------------------
    
    async def initialize(self) -> None:
        """
        Initialize the provider.
        
        Called once after construction to perform one-time setup.
        This is where you would:
            - Connect to external services
            - Load configuration from context
            - Validate dependencies
            
        Default: no-op (provider can be initialized without explicit call)
        """
        self._state = ProviderState.INITIALIZED
    
    async def start(self) -> None:
        """
        Start the provider.
        
        Called when the provider should begin accepting requests.
        Default: no-op
        """
        if self._state == ProviderState.INITIALIZED:
            self._state = ProviderState.ACTIVE
        elif self._state == ProviderState.SUSPENDED:
            self._state = ProviderState.ACTIVE
    
    async def stop(self) -> None:
        """
        Stop the provider.
        
        Called when the provider should cease accepting new requests.
        Pending requests may still complete. Default: no-op
        """
        if self._state == ProviderState.ACTIVE:
            self._state = ProviderState.SUSPENDED
    
    async def shutdown(self) -> None:
        """
        Shutdown the provider.
        
        Called during plugin unload to clean up resources. Override this
        to close connections, release resources, etc.
        Default: no-op
        """
        if self._state == ProviderState.SUSPENDED:
            self._state = ProviderState.UNINITIALIZED
    
    # -------------------------------------------------------------------------
    # Capability Methods (override as needed)
    # -------------------------------------------------------------------------
    
    def get_capabilities(self) -> List[CapabilityRegistration]:
        """
        Get all capabilities provided by this provider.
        
        Default: empty list. Override to expose capabilities.
        """
        return []
    
    def is_capability_available(self, capability_id: CapabilityId) -> bool:
        """Check if a specific capability is available."""
        for reg in self.get_capabilities():
            if reg.capability_id == capability_id and reg.enabled:
                return True
        return False
    
    # -------------------------------------------------------------------------
    # Health & Status
    # -------------------------------------------------------------------------
    
    async def check_health(self) -> tuple[bool, Optional[str]]:
        """
        Check provider health.
        
        Returns:
            Tuple of (healthy, reason_if_not_healthy)
        """
        if self._state == ProviderState.FAILED:
            return False, "Provider in failed state"
        if not self.config.enabled:
            return False, "Provider disabled"
        return True, None
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status information."""
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "version": self.version,
            "state": self._state.value,
            "enabled": self.config.enabled,
            "priority": self.config.priority,
        }
    
    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------
    
    async def reload_config(self, new_config: ProviderConfig) -> None:
        """
        Reload configuration.
        
        Override to apply configuration changes at runtime.
        Default: replaces config and reinitializes
        
        Args:
            new_config: The new configuration
        """
        self._config = new_config
        self._identity = new_config.identity
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.provider_id})"


# =============================================================================
# PROVIDER REGISTRY (in plugins namespace)
# =============================================================================


class PluginProviderRegistry:
    """
    Registry for plugin providers.
    
    Manages provider lifecycle, discovery, and capability registration.
    Integrates with the global CapabilityRegistry.
    """
    
    def __init__(self):
        """Initialize the provider registry."""
        self._lock = None  # Placeholder
        
        # Storage
        self._providers_by_id: Dict[str, Provider] = {}
        self._registrations: Dict[ProviderIdentity, List[CapabilityRegistration]] = {}
        
        # Indexes
        self._capabilities_by_type: Dict[str, List[CapabilityRegistration]] = {}
    
    async def register_provider(self, provider: Provider) -> None:
        """
        Register a provider.
        
        Args:
            provider: The provider to register
            
        Raises:
            ValueError: If provider is already registered
        """
        identity = provider._identity
        
        if identity.provider_id in self._providers_by_id:
            raise ValueError(
                f"Provider '{identity.provider_id}' is already registered"
            )
        
        # Store provider
        self._providers_by_id[identity.provider_id] = provider
        
        # Register capabilities
        registrations: List[CapabilityRegistration] = []
        for cap_reg in provider.get_capabilities():
            registrations.append(cap_reg)
            
            cap_type = f"{cap_reg.capability_id.domain}:{cap_reg.capability_id.name}"
            if cap_type not in self._capabilities_by_type:
                self._capabilities_by_type[cap_type] = []
            self._capabilities_by_type[cap_type].append(cap_reg)
        
        self._registrations[identity] = registrations
    
    async def unregister_provider(self, provider_id: str) -> bool:
        """
        Unregister a provider.
        
        Args:
            provider_id: The provider to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if provider_id not in self._providers_by_id:
            return False
        
        provider = self._providers_by_id.pop(provider_id)
        
        # Remove from registrations index
        identity = provider._identity
        if identity in self._registrations:
            del self._registrations[identity]
        
        # Rebuild capability index (simplified - could be more efficient)
        self._capabilities_by_type.clear()
        for pid, prov in self._providers_by_id.items():
            for cap_reg in prov.get_capabilities():
                cap_type = f"{cap_reg.capability_id.domain}:{cap_reg.capability_id.name}"
                if cap_type not in self._capabilities_by_type:
                    self._capabilities_by_type[cap_type] = []
                self._capabilities_by_type[cap_type].append(cap_reg)
        
        return True
    
    async def get_provider(self, provider_id: str) -> Optional[Provider]:
        """Get a registered provider by ID."""
        return self._providers_by_id.get(provider_id)
    
    async def get_providers_for_capability(
        self,
        domain: str,
        name: str,
    ) -> List[CapabilityRegistration]:
        """
        Get all providers for a specific capability.
        
        Args:
            domain: Capability domain
            name: Capability name
            
        Returns:
            List of capability registrations (sorted by priority)
        """
        cap_type = f"{domain}:{name}"
        registrations = list(self._capabilities_by_type.get(cap_type, []))
        
        # Sort by provider priority
        registrations.sort(
            key=lambda r: self._providers_by_id.get(r.provider_id, None).config.priority 
                         if r.provider_id in self._providers_by_id else 0,
            reverse=True
        )
        
        return registrations
    
    async def get_all_providers(self) -> Dict[str, Provider]:
        """Get all registered providers."""
        return dict(self._providers_by_id)
    
    def __len__(self) -> int:
        return len(self._providers_by_id)


# =============================================================================
# ADAPTER MODEL
# =============================================================================


class ProtocolAdapter(ExtensionPoint):
    """
    Base class for protocol adapters.
    
    Adapters convert between different protocol implementations while
    maintaining the same capability interface.
    """
    
    @property
    def extension_point_id(self) -> str:
        return "adapter:protocol"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def can_adapt(self, source_protocol: Type, target_protocol: Type) -> bool:
        """Check if this adapter can convert between protocols."""
        raise NotImplementedError


class CompatibilityAdapter(ProtocolAdapter):
    """
    Adapter for handling protocol compatibility differences.
    """
    
    def __init__(
        self,
        source_version: PluginVersion,
        target_version: PluginVersion,
    ):
        self._source_version = source_version
        self._target_version = target_version
    
    def can_adapt(self, source_protocol: Type, target_protocol: Type) -> bool:
        # Simplified version compatibility check
        return (self._target_version.major == self._source_version.major and
                self._target_version.minor >= self._source_version.minor)


# =============================================================================
# DYNAMIC COMPOSITION
# =============================================================================


class CompositionPlan:
    """
    Plan for dynamic composition of providers.
    
    Used during startup to determine which providers to load and in what order.
    """
    
    def __init__(self):
        """Initialize an empty composition plan."""
        self.providers: List[str] = []  # Provider IDs in loading order
        self.dependencies: Dict[str, Set[str]] = {}  # provider -> dependencies
    
    def add_provider(self, provider_id: str, depends_on: Optional[List[str]] = None) -> None:
        """
        Add a provider to the composition plan.
        
        Args:
            provider_id: The provider ID
            depends_on: List of providers this one depends on
        """
        self.providers.append(provider_id)
        if depends_on:
            self.dependencies[provider_id] = set(depends_on)
    
    def get_loading_order(self) -> List[str]:
        """
        Get providers in correct loading order.
        
        Uses topological sort based on dependency graph.
        Returns:
            List of provider IDs
        """
        # Simple Kahn's algorithm for topological sort
        in_degree: Dict[str, int] = {p: 0 for p in self.providers}
        
        for provider, deps in self.dependencies.items():
            if provider in in_degree:
                in_degree[provider] += len(deps)
        
        queue = [p for p in self.providers if in_degree.get(p, 0) == 0]
        result = []
        
        while queue:
            provider = queue.pop(0)
            result.append(provider)
            
            # Find dependents and reduce their in-degree
            for other_provider, deps in self.dependencies.items():
                if provider in deps:
                    in_degree[other_provider] -= 1
                    if in_degree[other_provider] == 0:
                        queue.append(other_provider)
        
        return result


__all__ = [
    # Enums
    "ProviderState",
    
    # Data classes
    "ProviderIdentity",
    "ProviderConfig",
    "CapabilityRegistration",
    
    # Provider base class
    "Provider",
    "PluginProviderRegistry",
    
    # Adapter model
    "ProtocolAdapter",
    "CompatibilityAdapter",
    
    # Composition
    "CompositionPlan",
]
