# Core Providers Interface
# ========================

"""
Core providers interface - defines contracts for provider abstractions.

This interface allows different provider implementations (local, remote,
mock) while providing a consistent way to access external capabilities.

ARCHITECTURAL PRINCIPLES:
- Providers are backend-agnostic
- Provider selection is external to core logic
- Multiple providers can be registered and queried
- Failover between providers is supported
"""

from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ProviderId:
    """Unique identifier for a provider."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "ProviderId":
        """Generate a new unique provider ID."""
        import uuid
        return cls(value=f"provider_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def from_parts(cls, domain: str, name: str) -> "ProviderId":
        """Create a ProviderId from domain and name."""
        return cls(value=f"{domain}.{name}")


class ProviderState(Enum):
    """Provider lifecycle states."""
    
    UNINITIALIZED = "uninitialized"  # Created but not ready
    INITIALIZING = "initializing"    # Currently initializing
    READY = "ready"                  # Ready to provide services
    DEGRADED = "degraded"            # Partially available
    FAILED = "failed"                # Not available, needs recovery


@dataclass(frozen=True)
class ProviderInfo:
    """
    Immutable information about a provider.
    
    Args:
        provider_id: Unique identifier for this provider
        domain: What type of capability this provides (e.g., "model", "storage")
        name: Human-readable name
        version: Provider implementation version
        state: Current lifecycle state
        capabilities: List of capability names this provider supports
    """
    
    provider_id: str
    domain: str
    name: str
    version: str = "1.0.0"
    state: ProviderState = ProviderState.UNINITIALIZED
    capabilities: List[str] = None  # type: ignore


class IProvider(Protocol):
    """
    Interface for a capability provider.
    
    Providers are responsible for:
        - Implementing specific capabilities (e.g., model inference, storage)
        - Reporting their health and availability
        - Supporting failover scenarios
    
    This is a BEHAVIORAL contract - implementations can use various
    mechanisms as long as they conform to the interface.
    """
    
    @property
    def provider_id(self) -> ProviderId:
        """Get the unique ID of this provider."""
        ...
    
    @property
    def domain(self) -> str:
        """Get the capability domain this provider serves."""
        ...
    
    @property
    def state(self) -> ProviderState:
        """Get the current lifecycle state of this provider."""
        ...
    
    async def initialize(self) -> None:
        """
        Initialize the provider.
        
        Called once before use. May perform connection setup,
        resource allocation, etc.
        """
        ...
    
    async def shutdown(self) -> None:
        """
        Shutdown the provider gracefully.
        
        Cleanup resources and close connections.
        """
        ...
    
    async def is_available(self) -> bool:
        """Check if this provider can accept requests."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on this provider.
        
        Returns:
            Dictionary with health status information
        """
        ...


class IProviderRegistry(Protocol):
    """
    Interface for the provider registry - maintains providers and enables discovery.
    
    The registry:
        - Stores provider information
        - Enables lookup by domain or capability
        - Supports multiple providers per domain (for failover)
        - Maintains preferred provider ordering
    """
    
    @property
    def registry_id(self) -> str:
        """Get the unique ID of this registry."""
        ...
    
    async def register(
        self,
        provider: IProvider,
        is_preferred: bool = False,
    ) -> None:
        """
        Register a provider with the registry.
        
        Args:
            provider: The provider to register
            is_preferred: If True, this provider gets priority for new requests
        """
        ...
    
    async def unregister(self, provider_id: str) -> bool:
        """
        Remove a provider from the registry.
        
        Args:
            provider_id: The ID of the provider to remove
            
        Returns:
            True if found and removed
        """
        ...
    
    def get_provider(
        self,
        domain: str,
        capability: Optional[str] = None,
    ) -> Optional[IProvider]:
        """
        Get a suitable provider for a domain.
        
        Args:
            domain: The capability domain (e.g., "model", "storage")
            capability: Specific capability required (optional)
            
        Returns:
            A provider instance or None if no suitable provider available
        """
        ...
    
    def get_all_providers(
        self,
        domain: Optional[str] = None,
    ) -> List[IProvider]:
        """
        Get all providers, optionally filtered by domain.
        
        Args:
            domain: Filter by this domain (None = all domains)
            
        Returns:
            List of provider instances
        """
        ...
    
    async def get_provider_state(
        self,
        provider_id: str,
    ) -> Optional[ProviderInfo]:
        """Get information about a registered provider."""
        ...


class IProviderSelector(Protocol):
    """
    Interface for selecting providers from the registry.
    
    Implementations can use different selection strategies:
        - Round-robin for load balancing
        - Health-aware (avoid unhealthy providers)
        - Cost-based (prefer cheaper options)
        - Latency-based (prefer faster responses)
    """
    
    @property
    def selector_id(self) -> str:
        """Get the unique ID of this selector."""
        ...
    
    def select(
        self,
        domain: str,
        registry: IProviderRegistry,
    ) -> Optional[IProvider]:
        """
        Select a provider for a given domain.
        
        Args:
            domain: The capability domain to select for
            registry: The provider registry to select from
            
        Returns:
            A selected provider or None if no suitable provider found
        """
        ...
    
    def report_success(self, provider_id: str) -> None:
        """Report that a provider request succeeded."""
        ...
    
    def report_failure(self, provider_id: str) -> None:
        """Report that a provider request failed."""
        ...


class ProviderError(Exception):
    """Raised when provider operations fail."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Raised when a provider is not available for requests."""
    
    def __init__(self, provider_id: str):
        super().__init__(f"Provider {provider_id} is not available")
        self.provider_id = provider_id


class NoSuitableProviderError(ProviderError):
    """Raised when no suitable provider can be found."""
    
    def __init__(self, domain: str, capability: Optional[str] = None):
        msg = f"No suitable provider found for domain '{domain}'"
        if capability:
            msg += f" with capability '{capability}'"
        super().__init__(msg)
        self.domain = domain
        self.capability = capability


__all__ = [
    "ProviderId",
    "ProviderState",
    "ProviderInfo",
    "IProvider",
    "IProviderRegistry",
    "IProviderSelector",
    "ProviderError",
    "ProviderNotAvailableError",
    "NoSuitableProviderError",
]