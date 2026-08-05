# Provider Registry - Centralized Provider Management
# ====================================================
"""
Provider registry for deterministic provider registration and discovery.

The ProviderRegistry owns:
- Provider registration with unique identifiers
- Capability-based provider selection
- Health monitoring coordination
- Lifecycle integration

Key Design Decisions:
- Registration is explicit and must be done before providers can be used
- Duplicate provider IDs are rejected
- Provider selection is capability-aware (can query by supported capabilities)
- No automatic discovery - all registration must be explicit
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
import uuid
import time
import asyncio

from .exceptions import ProviderError, ProviderNotReadyError, ProviderConfigError
from .types import ProviderIdentity, ProviderStatus, CapabilityDeclaration, ProviderConfig


class RegistrationSource(Enum):
    """Where a provider registration came from."""
    CONFIGURATION = "configuration"  # From config file/ENV
    DYNAMIC = "dynamic"              # Registered at runtime
    TEST = "test"                    # Test-only provider


@dataclass(frozen=True)
class ProviderRegistration:
    """
    Immutable record of a registered provider.
    
    This is the authoritative source for what providers are available.
    """
    registration_id: str               # Unique internal ID
    provider_id: str                   # User-facing identifier
    kind: str                          # ProviderKind value
    version: str                       # Provider version
    
    # Capabilities
    capabilities: CapabilityDeclaration
    
    # Lifecycle state
    status: ProviderStatus
    initialized: bool
    started: bool
    
    # Metadata
    source: RegistrationSource
    registered_at: float               # Unix timestamp
    config_hash: Optional[str] = None  # For detecting configuration changes


@dataclass(frozen=True)
class CapabilityQuery:
    """
    Query for providers supporting specific capabilities.
    
    All fields are optional. A provider matches if it supports ALL requested
    capabilities and meets all other specified criteria.
    """
    required_capabilities: Set[str] = field(default_factory=set)  # e.g., {"chat_completion", "streaming"}
    kind_filter: Optional[str] = None  # Filter by ProviderKind
    min_context_tokens: Optional[int] = None
    max_concurrent_requests: Optional[int] = None
    
    def matches(self, registration: ProviderRegistration) -> bool:
        """Check if this registration matches the query."""
        # Check status - must be running
        if registration.status != ProviderStatus.RUNNING:
            return False
        
        # Check kind filter
        if self.kind_filter and registration.kind != self.kind_filter:
            return False
        
        # Check capability declarations
        declared = registration.capabilities
        
        # Map capability names to attributes on CapabilityDeclaration
        capability_map = {
            "chat_completion": declared.supports_chat_completion,
            "text_generation": declared.supports_text_generation,
            "embeddings": declared.supports_embeddings,
            "vision": declared.supports_vision,
            "asr": declared.supports_audio_input,
            "tts": declared.supports_audio_output,
            "image_gen": declared.supports_image_gen,
            "ocr": declared.supports_ocr,
            "detection": declared.supports_detection,
            "segmentation": declared.supports_segmentation,
            "streaming": declared.supports_streaming,
            "tool_calling": declared.supports_tool_calling,
            "structured_output": declared.supports_structured_output,
            "reranking": declared.supports_reranking,
        }
        
        for cap in self.required_capabilities:
            if not capability_map.get(cap, False):
                return False
        
        # Check context capacity
        if (self.min_context_tokens is not None and 
            registration.capabilities.max_context_tokens is not None):
            if registration.capabilities.max_context_tokens < self.min_context_tokens:
                return False
        
        return True


class ProviderRegistry:
    """
    Central registry for all provider registrations.
    
    Provides:
    - Deterministic provider registration with unique IDs
    - Capability-based discovery and selection
    - Health status tracking
    - Lifecycle integration
    
    Usage:
        # Create the registry
        registry = ProviderRegistry()
        
        # Register a provider
        registry.register_provider(
            provider_id="openai-gpt4",
            kind="llm",
            capabilities=CapabilityDeclaration(supports_chat_completion=True, ...),
            source=RegistrationSource.CONFIGURATION
        )
        
        # Query for providers by capability
        llm_providers = registry.get_providers_by_capability("chat_completion")
        
        # Get a specific provider
        registration = registry.get_registration("openai-gpt4")
    """
    
    def __init__(self):
        """Initialize the provider registry."""
        self._registrations: Dict[str, ProviderRegistration] = {}  # provider_id -> registration
        self._registration_ids: Dict[str, str] = {}  # registration_id -> provider_id
        self._lock = asyncio.Lock()
    
    async def register_provider(
        self,
        provider_id: str,
        kind: str,
        capabilities: CapabilityDeclaration,
        version: str = "1.0.0",
        source: RegistrationSource = RegistrationSource.CONFIGURATION,
        config_hash: Optional[str] = None,
    ) -> ProviderRegistration:
        """
        Register a new provider with the registry.
        
        Args:
            provider_id: Unique identifier for this provider instance
            kind: Provider kind (LLM, VLM, etc.)
            capabilities: Declared capabilities of this provider
            version: Provider version string
            source: Where this registration came from
            config_hash: Hash of configuration for change detection
            
        Returns:
            The created ProviderRegistration
            
        Raises:
            ValueError: If provider_id is already registered
            ProviderConfigError: If provider_id is empty or invalid
        """
        async with self._lock:
            # Validate provider_id
            if not provider_id or not isinstance(provider_id, str):
                raise ProviderConfigError(
                    message="Provider ID must be a non-empty string",
                    provider_id=provider_id,
                    operation="registration",
                    retryable=False
                )
            
            # Check for duplicates
            if provider_id in self._registrations:
                existing = self._registrations[provider_id]
                raise ValueError(
                    f"Provider '{provider_id}' is already registered. "
                    f"Existing: kind={existing.kind}, version={existing.version}"
                )
            
            # Create registration record
            registration_id = f"reg_{uuid.uuid4().hex[:8]}"
            now = time.monotonic()
            
            registration = ProviderRegistration(
                registration_id=registration_id,
                provider_id=provider_id,
                kind=kind,
                version=version,
                capabilities=capabilities,
                status=ProviderStatus.UNINITIALIZED,
                initialized=False,
                started=False,
                source=source,
                registered_at=now,
                config_hash=config_hash
            )
            
            # Store the registration
            self._registrations[provider_id] = registration
            self._registration_ids[registration_id] = provider_id
            
            return registration
    
    async def unregister_provider(self, provider_id: str) -> bool:
        """
        Remove a provider from the registry.
        
        Args:
            provider_id: The provider to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        async with self._lock:
            if provider_id in self._registrations:
                del self._registrations[provider_id]
                # Find and remove from registration_ids
                for reg_id, pid in list(self._registration_ids.items()):
                    if pid == provider_id:
                        del self._registration_ids[reg_id]
                        break
                return True
            return False
    
    async def get_registration(self, provider_id: str) -> Optional[ProviderRegistration]:
        """
        Get registration info for a provider.
        
        Args:
            provider_id: The provider to look up
            
        Returns:
            ProviderRegistration if found, None otherwise
        """
        async with self._lock:
            return self._registrations.get(provider_id)
    
    async def get_provider_status(self, provider_id: str) -> Optional[ProviderStatus]:
        """Get just the status of a provider."""
        registration = await self.get_registration(provider_id)
        return registration.status if registration else None
    
    async def update_provider_status(
        self,
        provider_id: str,
        new_status: ProviderStatus,
        initialized: bool = False,
        started: bool = False
    ) -> Optional[ProviderRegistration]:
        """
        Update a provider's status.
        
        This is called by providers during their lifecycle to report state changes.
        
        Args:
            provider_id: The provider to update
            new_status: The new status value
            initialized: Whether the provider has been initialized
            started: Whether the provider has been started
            
        Returns:
            Updated ProviderRegistration, or None if not found
        """
        async with self._lock:
            if provider_id not in self._registrations:
                return None
            
            existing = self._registrations[provider_id]
            
            # Create updated registration with new state
            updated = ProviderRegistration(
                registration_id=existing.registration_id,
                provider_id=existing.provider_id,
                kind=existing.kind,
                version=existing.version,
                capabilities=existing.capabilities,
                status=new_status,
                initialized=initialized,
                started=started,
                source=existing.source,
                registered_at=existing.registered_at,
                config_hash=existing.config_hash
            )
            
            self._registrations[provider_id] = updated
            return updated
    
    def get_all_registrations(self) -> Dict[str, ProviderRegistration]:
        """
        Get all registered providers.
        
        Returns:
            Dictionary mapping provider_id to registration
        """
        return dict(self._registrations)
    
    def get_provider_ids(self) -> List[str]:
        """Get list of all registered provider IDs."""
        return list(self._registrations.keys())
    
    async def get_providers_by_capability(
        self,
        capability: str,
        kind_filter: Optional[str] = None
    ) -> List[ProviderRegistration]:
        """
        Get all providers supporting a specific capability.
        
        Args:
            capability: The capability to search for (e.g., "chat_completion")
            kind_filter: Optional filter by ProviderKind
            
        Returns:
            List of registrations supporting the capability
        """
        async with self._lock:
            results = []
            
            for registration in self._registrations.values():
                # Check status - must be running
                if registration.status != ProviderStatus.RUNNING:
                    continue
                
                # Check kind filter
                if kind_filter and registration.kind != kind_filter:
                    continue
                
                # Check capability
                declared = registration.capabilities
                cap_map = {
                    "chat_completion": declared.supports_chat_completion,
                    "text_generation": declared.supports_text_generation,
                    "embeddings": declared.supports_embeddings,
                    "vision": declared.supports_vision,
                    "asr": declared.supports_audio_input,
                    "tts": declared.supports_audio_output,
                    "image_gen": declared.supports_image_gen,
                    "ocr": declared.supports_ocr,
                    "detection": declared.supports_detection,
                    "segmentation": declared.supports_segmentation,
                    "streaming": declared.supports_streaming,
                    "tool_calling": declared.supports_tool_calling,
                    "structured_output": declared.supports_structured_output,
                    "reranking": declared.supports_reranking,
                }
                
                if cap_map.get(capability, False):
                    results.append(registration)
            
            return results
    
    async def get_providers_by_kind(
        self,
        kind: str
    ) -> List[ProviderRegistration]:
        """Get all providers of a specific kind."""
        async with self._lock:
            return [
                r for r in self._registrations.values()
                if r.kind == kind and r.status == ProviderStatus.RUNNING
            ]
    
    async def count_by_status(self) -> Dict[str, int]:
        """
        Count providers by status.
        
        Returns:
            Dictionary mapping status to count
        """
        async with self._lock:
            counts: Dict[str, int] = {}
            for reg in self._registrations.values():
                status_str = reg.status.value
                counts[status_str] = counts.get(status_str, 0) + 1
            return counts
    
    def get_capabilities_summary(self) -> Dict[str, List[str]]:
        """
        Get a summary of all capabilities across registered providers.
        
        Returns:
            Dictionary mapping capability name to list of provider IDs that support it
        """
        cap_to_providers: Dict[str, List[str]] = {}
        
        for reg in self._registrations.values():
            declared = reg.capabilities
            caps = [
                ("chat_completion", declared.supports_chat_completion),
                ("text_generation", declared.supports_text_generation),
                ("embeddings", declared.supports_embeddings),
                ("vision", declared.supports_vision),
                ("asr", declared.supports_audio_input),
                ("tts", declared.supports_audio_output),
                ("image_gen", declared.supports_image_gen),
                ("ocr", declared.supports_ocr),
                ("detection", declared.supports_detection),
                ("segmentation", declared.supports_segmentation),
                ("streaming", declared.supports_streaming),
                ("tool_calling", declared.supports_tool_calling),
                ("structured_output", declared.supports_structured_output),
                ("reranking", declared.supports_reranking),
            ]
            
            for cap_name, supported in caps:
                if supported and reg.status == ProviderStatus.RUNNING:
                    if cap_name not in cap_to_providers:
                        cap_to_providers[cap_name] = []
                    cap_to_providers[cap_name].append(reg.provider_id)
        
        return cap_to_providers
    
    async def verify_provider_ready(self, provider_id: str) -> None:
        """
        Verify a provider is ready to accept requests.
        
        Raises ProviderNotReadyError if not ready.
        
        Args:
            provider_id: The provider to check
            
        Raises:
            ProviderNotReadyError: If the provider is not ready
            ValueError: If the provider is not registered
        """
        registration = await self.get_registration(provider_id)
        
        if registration is None:
            raise ValueError(f"Unknown provider ID: {provider_id}")
        
        if registration.status != ProviderStatus.RUNNING:
            raise ProviderNotReadyError(
                message=f"Provider '{provider_id}' is not ready (status: {registration.status.value})",
                provider_id=provider_id,
                operation="request"
            )
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on all registered providers.
        
        Returns:
            Dictionary mapping provider_id to health report
        """
        results: Dict[str, Dict[str, Any]] = {}
        
        for provider_id in self._registrations.keys():
            # Note: This is a placeholder - actual health checks would be
            # implemented by the specific provider implementations
            results[provider_id] = {
                "status": "pending",
                "ready": False,
                "message": "Health check not implemented for this provider"
            }
        
        return results
    
    def __len__(self) -> int:
        """Return number of registered providers."""
        return len(self._registrations)
    
    def __contains__(self, provider_id: str) -> bool:
        """Check if a provider is registered."""
        return provider_id in self._registrations


# Global registry instance (for single-tenant systems)
# For multi-tenant systems, create separate instances per tenant
_global_registry: Optional[ProviderRegistry] = None


def get_global_registry() -> ProviderRegistry:
    """
    Get the global provider registry.
    
    Creates one if it doesn't exist. For multi-tenant or test isolation,
    use ProviderRegistry directly instead.
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    
    return _global_registry


def clear_global_registry() -> None:
    """Clear the global registry (useful for testing)."""
    global _global_registry
    _global_registry = None


__all__ = [
    # Enums
    "RegistrationSource",
    
    # Data classes
    "ProviderRegistration",
    "CapabilityQuery",
    
    # Classes
    "ProviderRegistry",
    
    # Global accessors
    "get_global_registry",
    "clear_global_registry",
]