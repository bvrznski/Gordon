# Capability Registry - Phase 3.8.8.1
# =====================================
"""
Canonical capability registry for plugin capability management.

Provides:
- Capability discovery and registration
- Capability negotiation between plugins
- Version compatibility checking
- Provider priority management

Architecture:
    +---------------------+
    | CapabilityRegistry  |
    | (main entry point)  |
    +----------+----------+
               |
        +------+------+
        |             |
    +---v---+     +--v---+
    |Caps   |     |Providers
    |By ID  |     |By Domain
    +-------+     +--------+
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Any,
)
from enum import Enum
import asyncio
import time

# Import from abstraction module
try:
    from .abstraction import (
        Capability,
        CapabilityId,
        CapabilityDescriptor,
        CapabilityDeclaration,
        PluginVersion,
        PluginIdentifier,
        CapabilityError,
    )
except ImportError:
    # Fallback when running standalone or in different context
    class Capability:
        pass
    class CapabilityId:
        pass
    class CapabilityDescriptor:
        pass
    class CapabilityDeclaration:
        pass
    class PluginVersion:
        pass
    class CapabilityError(Exception):
        pass


@dataclass(frozen=True)
class ProviderPriority:
    """Priority configuration for capability providers."""
    
    provider_id: str
    priority_value: int  # Higher = more preferred
    
    @classmethod
    def default(cls) -> "ProviderPriority":
        """Get default priority (medium)."""
        return cls(provider_id="default", priority_value=50)


@dataclass(frozen=True)
class CapabilityQuery:
    """
    Query for capabilities matching specific criteria.
    
    All fields are optional - a capability matches if it satisfies
    ALL specified criteria.
    """
    
    domain: Optional[str] = None        # e.g., "llm", "embeddings"
    name: Optional[str] = None          # e.g., "chat_completion"
    min_version: Optional[PluginVersion] = None  # Minimum required version
    provider_id: Optional[str] = None   # Specific provider
    enabled_only: bool = True           # Only enabled capabilities
    
    def matches(self, capability: Capability) -> bool:
        """Check if a capability matches this query."""
        # Check domain filter
        if self.domain and capability.id.domain != self.domain:
            return False
        
        # Check name filter
        if self.name and capability.id.name != self.name:
            return False
        
        # Check version requirement
        if self.min_version:
            if not capability.is_compatible_with(self.min_version):
                return False
        
        # Check provider filter
        if self.provider_id and capability.provider_id != self.provider_id:
            return False
        
        # Check enabled status
        if self.enabled_only and not (capability.enabled and capability.available):
            return False
        
        return True


@dataclass(frozen=True)
class CapabilityMatchResult:
    """Result of a capability query."""
    
    capability: Capability
    provider_priority: int
    is_compatible: bool
    
    @classmethod
    def create(
        cls,
        capability: Capability,
        is_compatible: bool = True,
    ) -> "CapabilityMatchResult":
        """Create a match result with default priority."""
        return cls(
            capability=capability,
            provider_priority=capability.priority,
            is_compatible=is_compatible,
        )


class CapabilityRegistry:
    """
    Central registry for all plugin capabilities.
    
    Provides:
    - Capability registration and discovery
    - Version-based compatibility checking
    - Provider selection (highest priority wins)
    - Capability negotiation between plugins
    
    Thread-Safe:
        All public methods are async and use internal locks for thread safety.
    """
    
    def __init__(self):
        """Initialize the capability registry."""
        self._lock = asyncio.Lock()
        
        # Storage structures
        self._capabilities_by_id: Dict[str, Capability] = {}  # full_name -> capability
        self._capabilities_by_domain: Dict[str, List[Capability]] = {}
        self._providers_by_capability: Dict[str, Set[str]] = {}  # cap_name -> set of provider_ids
        
        # Metadata
        self._registration_times: Dict[str, float] = {}
        self._capability_declarations: Dict[str, CapabilityDeclaration] = {}
    
    async def register_capability(self, capability: Capability) -> None:
        """
        Register a new capability.
        
        Args:
            capability: The capability to register
            
        Raises:
            CapabilityError: If registration fails
        """
        async with self._lock:
            full_name = capability.full_name
            
            # Check for duplicates
            if full_name in self._capabilities_by_id:
                raise CapabilityError(
                    f"Capability '{full_name}' is already registered",
                    capability_id=capability.id.full_name,
                )
            
            # Store the capability
            self._capabilities_by_id[full_name] = capability
            
            # Index by domain
            if capability.id.domain not in self._capabilities_by_domain:
                self._capabilities_by_domain[capability.id.domain] = []
            self._capabilities_by_domain[capability.id.domain].append(capability)
            
            # Track provider for this capability type
            cap_type = f"{capability.id.domain}:{capability.id.name}"
            if cap_type not in self._providers_by_capability:
                self._providers_by_capability[cap_type] = set()
            if capability.provider_id:
                self._providers_by_capability[cap_type].add(capability.provider_id)
            
            # Record registration time
            self._registration_times[full_name] = time.monotonic()
    
    async def unregister_capability(self, full_name: str) -> bool:
        """
        Remove a capability from the registry.
        
        Args:
            full_name: The full name of the capability to remove
            
        Returns:
            True if unregistered, False if not found
        """
        async with self._lock:
            if full_name not in self._capabilities_by_id:
                return False
            
            capability = self._capabilities_by_id.pop(full_name)
            
            # Remove from domain index
            if capability.id.domain in self._capabilities_by_domain:
                self._capabilities_by_domain[capability.id.domain] = [
                    c for c in self._capabilities_by_domain[capability.id.domain]
                    if c.full_name != full_name
                ]
                if not self._capabilities_by_domain[capability.id.domain]:
                    del self._capabilities_by_domain[capability.id.domain]
            
            # Remove from provider index
            cap_type = f"{capability.id.domain}:{capability.id.name}"
            if cap_type in self._providers_by_capability and capability.provider_id:
                self._providers_by_capability[cap_type].discard(capability.provider_id)
            
            # Clean up metadata
            self._registration_times.pop(full_name, None)
            
            return True
    
    async def get_capability(self, full_name: str) -> Optional[Capability]:
        """
        Get a capability by its full name.
        
        Args:
            full_name: The full name (domain:name@version) of the capability
            
        Returns:
            Capability if found, None otherwise
        """
        async with self._lock:
            return self._capabilities_by_id.get(full_name)
    
    async def get_capabilities_by_domain(self, domain: str) -> List[Capability]:
        """
        Get all capabilities in a domain.
        
        Args:
            domain: The domain to search (e.g., "llm", "embeddings")
            
        Returns:
            List of capabilities in that domain
        """
        async with self._lock:
            return list(self._capabilities_by_domain.get(domain, []))
    
    async def get_capabilities_by_type(
        self,
        domain: str,
        name: str,
    ) -> List[Capability]:
        """
        Get all providers for a specific capability type.
        
        Args:
            domain: The capability domain
            name: The capability name
            
        Returns:
            List of capabilities (one per provider)
        """
        async with self._lock:
            cap_type = f"{domain}:{name}"
            results = []
            
            for capability in self._capabilities_by_id.values():
                if (capability.id.domain == domain and 
                    capability.id.name == name):
                    results.append(capability)
            
            return results
    
    async def query_capabilities(self, query: CapabilityQuery) -> List[CapabilityMatchResult]:
        """
        Query capabilities matching criteria.
        
        Args:
            query: The query criteria
            
        Returns:
            List of matching capabilities with metadata
        """
        async with self._lock:
            results = []
            
            for capability in self._capabilities_by_id.values():
                if query.matches(capability):
                    results.append(CapabilityMatchResult.create(capability))
            
            # Sort by priority (highest first)
            results.sort(
                key=lambda r: r.provider_priority,
                reverse=True
            )
            
            return results
    
    async def negotiate_capability(
        self,
        domain: str,
        name: str,
        min_version: Optional[PluginVersion] = None,
    ) -> Optional[Capability]:
        """
        Negotiate for a capability - select the best provider.
        
        Selection criteria (in order):
        1. Version compatibility (must satisfy min_version)
        2. Priority (higher = preferred)
        3. Registration time (earlier = preferred for ties)
        
        Args:
            domain: Capability domain
            name: Capability name
            min_version: Minimum required version
            
        Returns:
            Selected capability, or None if no compatible provider exists
        """
        async with self._lock:
            candidates = []
            
            for capability in self._capabilities_by_id.values():
                if (capability.id.domain == domain and 
                    capability.id.name == name):
                    
                    # Check compatibility
                    is_compatible = (
                        min_version is None or 
                        capability.is_compatible_with(min_version)
                    )
                    
                    if is_compatible:
                        candidates.append(capability)
            
            if not candidates:
                return None
            
            # Sort by priority (desc), then by registration time (asc for ties)
            candidates.sort(
                key=lambda c: (-c.priority, self._registration_times.get(c.full_name, 0))
            )
            
            return candidates[0]
    
    async def get_all_capabilities(self) -> Dict[str, Capability]:
        """
        Get all registered capabilities.
        
        Returns:
            Dictionary mapping full names to capabilities
        """
        async with self._lock:
            return dict(self._capabilities_by_id)
    
    async def get_capability_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all capabilities.
        
        Returns:
            Summary dictionary with counts and domain breakdowns
        """
        async with self._lock:
            domains: Dict[str, List[Dict]] = {}
            
            for capability in self._capabilities_by_id.values():
                if capability.id.domain not in domains:
                    domains[capability.id.domain] = []
                
                domains[capability.id.domain].append({
                    "name": capability.id.name,
                    "version": str(capability.version),
                    "provider_id": capability.provider_id,
                    "enabled": capability.enabled,
                    "available": capability.available,
                })
            
            return {
                "total_capabilities": len(self._capabilities_by_id),
                "domains": domains,
                "domains_count": len(domains),
            }
    
    async def has_capability(
        self,
        domain: str,
        name: str,
        version: Optional[PluginVersion] = None,
    ) -> bool:
        """
        Check if a capability exists (optionally with specific version).
        
        Args:
            domain: Capability domain
            name: Capability name
            version: Version to check (None = any version)
            
        Returns:
            True if the capability exists
        """
        async with self._lock:
            for capability in self._capabilities_by_id.values():
                if capability.id.domain == domain and capability.id.name == name:
                    if version is None:
                        return True
                    if capability.version.major == version.major:
                        return True
            
            return False
    
    def __len__(self) -> int:
        """Return number of registered capabilities."""
        return len(self._capabilities_by_id)
    
    def __contains__(self, full_name: str) -> bool:
        """Check if a capability is registered by full name."""
        return full_name in self._capabilities_by_id


# Global registry instance
_global_capability_registry: Optional[CapabilityRegistry] = None


def get_global_capability_registry() -> CapabilityRegistry:
    """
    Get the global capability registry.
    
    Creates one if it doesn't exist. For multi-tenant or test isolation,
    create separate instances directly.
    """
    global _global_capability_registry
    
    if _global_capability_registry is None:
        _global_capability_registry = CapabilityRegistry()
    
    return _global_capability_registry


def clear_global_capability_registry() -> None:
    """Clear the global capability registry (useful for testing)."""
    global _global_capability_registry
    _global_capability_registry = None


__all__ = [
    # Data types
    "ProviderPriority",
    "CapabilityQuery",
    "CapabilityMatchResult",
    
    # Main class
    "CapabilityRegistry",
    
    # Global accessors
    "get_global_capability_registry",
    "clear_global_capability_registry",
]