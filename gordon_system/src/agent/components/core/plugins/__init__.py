# Plugin & Extensibility Infrastructure - Phase 3.8.8
# ======================================================
"""
Canonical Plugin & Extensibility Infrastructure for Gordon Core.

This package provides the foundation for safe, deterministic plugin extension
without modifying Core internals.

Core Principles:
    - Core owns all extension contracts
    - Plugins implement published interfaces only
    - Extension is versioned and validated
    - Discovery is deterministic
    - Lifecycle is explicitly managed

Architecture Overview:

    +---------------------+
    |   Plugin Registry   |  <- Central registration authority
    +----------+----------+
               |
    +----------v----------+       +-------------------+
    |  Plugin Discovery   |------>|  Manifest Parser  |
    +----------+----------+       +-------------------+
               |
    +----------v----------+       +-------------------+
    |  Capability Registry|<----->| Capability Model  |
    +----------+----------+       +-------------------+
               |
    +----------v----------+       +-------------------+
    | Lifecycle Manager   |------>| Plugin Lifecycle  |
    +----------+----------+       +-------------------+
               |
    +----------v----------+       +-------------------+
    | Dependency Resolver |<----->| Compatibility Engine|
    +---------------------+       +-------------------+

Public API:
    - Plugin, PluginManifest, PluginDescriptor
    - ExtensionPoint, Extension
    - CapabilityRegistry, Capability
    - DiscoveryService, RegistrationService
    - LifecycleManager
    - DependencyResolver

Version: 3.8.8.1-rc1
"""

from typing import Any

# Core abstractions
from .abstraction import (
    # State machine
    PluginState,
    
    # Manifest types
    PluginVersion,
    PluginIdentifier,
    PluginManifest,
    PluginDescriptor,
    
    # Context and runtime
    PluginContext,
    
    # Extension system
    ExtensionPoint,
    ExtensionDescriptor,
    Extension,
    
    # Capabilities
    CapabilityId,
    CapabilityMetadata,
    CapabilityDeclaration,
    Capability,
    CapabilityDescriptor,
    
    # Plugin base class
    Plugin,
    ExtensionImpl,
    
    # Exceptions
    PluginError,
    PluginLoadError,
    PluginUnloadError,
    LifecycleTransitionError,
    DuplicateRegistrationError,
    MissingDependencyError,
    CircularDependencyError,
    CompatibilityError,
    CapabilityError,
    ExtensionPointError,
    
    # Utilities
    create_plugin_context,
    validate_manifest,
)

# Capabilities
from .capability import (
    ProviderPriority,
    CapabilityQuery,
    CapabilityMatchResult,
    CapabilityRegistry,
    get_global_capability_registry,
    clear_global_capability_registry,
)

# Lifecycle
from .lifecycle import (
    LifecycleEventType,
    LifecycleEvent,
    PluginHealthReport,
    LifecycleManager,
    LifecycleHooks,
)

# Registry and Discovery
from .registry import (
    DiscoverySource,
    RegistrationRecord,
    DiscoveryResult,
    validate_manifest as registry_validate_manifest,
    DiscoveryBackend,
    LocalPackageDiscovery,
    ConfiguredDirectoryDiscovery,
    DiscoveryService,
    PluginRegistry,
)

# Dependencies
from .dependencies import (
    DependencyType,
    DependencyConstraint,
    Dependency,
    DependencyGraph,
    ResolutionResult,
    DependencyResolver,
)

# Compatibility
from .compatibility import (
    CompatibilityLevel,
    CompatibilityProfile,
    CompatibilityResult,
    CompatibilityEngine,
    get_global_compatibility_engine,
)

# Loader
from .loader import (
    LoadStrategy,
    LoadResult,
    UnloadResult,
    PluginLoader,
    EagerLoader,
)

# Runtime Integration
from .runtime_integration import (
    OrchestrationPhase,
    OrchestrationEvent,
    IsolationBoundary,
    IsolationPolicy,
    ResourceLease,
    PluginOrchestrator,
    ResourceGovernance,
)

# Provider Framework
from .provider import (
    ProviderState,
    ProviderIdentity,
    ProviderConfig,
    CapabilityRegistration,
    Provider,
    PluginProviderRegistry,
    ProtocolAdapter,
    CompatibilityAdapter,
    CompositionPlan,
)

__all__ = [
    # State machine
    "PluginState",
    
    # Manifest types
    "PluginVersion",
    "PluginIdentifier",
    "PluginManifest",
    "PluginDescriptor",
    
    # Context and runtime
    "PluginContext",
    
    # Extension system
    "ExtensionPoint",
    "ExtensionDescriptor",
    "Extension",
    
    # Capabilities
    "CapabilityId",
    "CapabilityMetadata",
    "CapabilityDeclaration",
    "Capability",
    "CapabilityDescriptor",
    
    # Plugin base class
    "Plugin",
    "ExtensionImpl",
    
    # Exceptions
    "PluginError",
    "PluginLoadError",
    "PluginUnloadError",
    "LifecycleTransitionError",
    "DuplicateRegistrationError",
    "MissingDependencyError",
    "CircularDependencyError",
    "CompatibilityError",
    "CapabilityError",
    "ExtensionPointError",
    
    # Capabilities module
    "ProviderPriority",
    "CapabilityQuery",
    "CapabilityMatchResult",
    "CapabilityRegistry",
    "get_global_capability_registry",
    "clear_global_capability_registry",
    
    # Lifecycle module
    "LifecycleEventType",
    "LifecycleEvent",
    "PluginHealthReport",
    "LifecycleManager",
    "LifecycleHooks",
    
    # Registry module
    "DiscoverySource",
    "RegistrationRecord",
    "DiscoveryResult",
    "validate_manifest",  # Alias to registry_validate_manifest
    "DiscoveryBackend",
    "LocalPackageDiscovery",
    "ConfiguredDirectoryDiscovery",
    "DiscoveryService",
    "PluginRegistry",
    
    # Dependencies module
    "DependencyType",
    "DependencyConstraint",
    "Dependency",
    "DependencyGraph",
    "ResolutionResult",
    "DependencyResolver",
    
    # Compatibility module
    "CompatibilityLevel",
    "CompatibilityProfile",
    "CompatibilityResult",
    "CompatibilityEngine",
    "get_global_compatibility_engine",
    
    # Loader module
    "LoadStrategy",
    "LoadResult",
    "UnloadResult",
    "PluginLoader",
    "EagerLoader",
    
    # Runtime Integration module
    "OrchestrationPhase",
    "OrchestrationEvent",
    "IsolationBoundary",
    "IsolationPolicy",
    "ResourceLease",
    "PluginOrchestrator",
    "ResourceGovernance",
    
    # Provider Framework module
    "ProviderState",
    "ProviderIdentity",
    "ProviderConfig",
    "CapabilityRegistration",
    "Provider",
    "PluginProviderRegistry",
    "ProtocolAdapter",
    "CompatibilityAdapter",
    "CompositionPlan",
]
