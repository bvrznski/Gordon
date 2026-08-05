# Plugin Registry - Phase 3.8.8.2
# =================================
"""
Canonical plugin registry for discovery, registration, and lifecycle management.

Provides:
- Plugin discovery from multiple sources
- Registration with duplicate detection
- Manifest validation
- Discovery source tracking

Discovery Sources:
    - Local packages (file system)
    - Configured directories
    - Bundled plugins (included in core)
    - Remote repositories (future extension)
"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Any,
    Callable,
    Awaitable,
)
from enum import Enum
import asyncio
import time
import uuid

# Import from abstraction module
try:
    from .abstraction import (
        PluginManifest,
        PluginDescriptor,
        PluginState,
        PluginError,
        DuplicateRegistrationError,
        PluginVersion,
        PluginIdentifier,
    )
except ImportError:
    class PluginManifest:
        pass
    class PluginDescriptor:
        pass
    class PluginError(Exception):
        pass


class DiscoverySource(Enum):
    """Where a plugin was discovered from."""
    
    LOCAL_PACKAGE = "local_package"       # From local filesystem packages
    CONFIGURED_DIR = "configured_dir"     # From configured search paths
    BUNDLED = "bundled"                   # Bundled with core distribution
    REMOTE_REPO = "remote_repo"           # From remote repository (future)
    TEST_SOURCE = "test_source"           # Test-only plugins


@dataclass(frozen=True)
class RegistrationRecord:
    """
    Record of a registered plugin.
    
    This is the authoritative source for what plugins are available.
    """
    
    registration_id: str               # Unique internal ID
    plugin_descriptor: PluginDescriptor
    
    # Discovery info
    source: DiscoverySource
    discovered_at: float               # Unix timestamp
    verified_at: Optional[float] = None  # When manifest was validated
    
    # Registration metadata
    config_hash: Optional[str] = None  # For detecting changes
    
    @property
    def plugin_id(self) -> str:
        """Get the plugin identifier string."""
        return str(self.plugin_descriptor.manifest.id)
    
    @property
    def version(self) -> PluginVersion:
        """Get the plugin version."""
        return self.plugin_descriptor.manifest.version
    
    @classmethod
    def create(
        cls,
        descriptor: PluginDescriptor,
        source: DiscoverySource = DiscoverySource.LOCAL_PACKAGE,
    ) -> "RegistrationRecord":
        """Create a new registration record."""
        return cls(
            registration_id=f"reg_{uuid.uuid4().hex[:8]}",
            plugin_descriptor=descriptor,
            source=source,
            discovered_at=time.monotonic(),
            verified_at=None,
        )


@dataclass(frozen=True)
class DiscoveryResult:
    """Result of a discovery operation."""
    
    record: RegistrationRecord
    manifest_valid: bool
    errors: List[str] = field(default_factory=list)


# =============================================================================
# MANIFEST VALIDATION
# =============================================================================


def validate_manifest(manifest: PluginManifest) -> tuple[bool, List[str]]:
    """
    Validate a plugin manifest.
    
    Args:
        manifest: The manifest to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if not manifest.id or not str(manifest.id):
        errors.append("Plugin must have a valid identifier")
    
    if not manifest.version or not str(manifest.version):
        errors.append("Plugin must have a version")
    
    if not manifest.name:
        errors.append("Plugin must have a display name")
    
    if not manifest.description:
        errors.append("Plugin must have a description")
    
    # Check version format
    try:
        _ = str(manifest.version)
    except Exception as e:
        errors.append(f"Invalid version format: {e}")
    
    return len(errors) == 0, errors


# =============================================================================
# DISCOVERY ABSTRACTIONS
# =============================================================================


class DiscoveryBackend(ABC):
    """Abstract base for plugin discovery backends."""
    
    @property
    @abstractmethod
    def source(self) -> DiscoverySource:
        """The discovery source this backend handles."""
        pass
    
    async def discover_plugins(
        self,
        filter_func: Optional[Callable[[PluginManifest], bool]] = None,
    ) -> List[DiscoveryResult]:
        """
        Discover plugins from this source.
        
        Args:
            filter_func: Optional function to filter results
            
        Returns:
            List of discovery results
        """
        raise NotImplementedError


class LocalPackageDiscovery(DiscoveryBackend):
    """Discovers plugins from local package directories."""
    
    def __init__(self, package_paths: List[str]):
        self.package_paths = package_paths
    
    @property
    def source(self) -> DiscoverySource:
        return DiscoverySource.LOCAL_PACKAGE
    
    async def discover_plugins(
        self,
        filter_func: Optional[Callable[[PluginManifest], bool]] = None,
    ) -> List[DiscoveryResult]:
        """Discover from local packages."""
        # This is a stub - real implementation would scan package directories
        results: List[DiscoveryResult] = []
        
        for path in self.package_paths:
            try:
                manifest = await self._load_manifest(path)
                if filter_func and not filter_func(manifest):
                    continue
                
                is_valid, errors = validate_manifest(manifest)
                
                descriptor = PluginDescriptor(manifest=manifest)
                record = RegistrationRecord.create(
                    descriptor,
                    DiscoverySource.LOCAL_PACKAGE,
                )
                
                results.append(DiscoveryResult(
                    record=record,
                    manifest_valid=is_valid,
                    errors=errors,
                ))
            except Exception as e:
                # Log error but continue with other packages
                pass
        
        return results
    
    async def _load_manifest(self, path: str) -> PluginManifest:
        """Load a plugin manifest from a path."""
        # Stub - would parse actual manifest file
        return PluginManifest.create(
            namespace="local",
            name=f"plugin_{uuid.uuid4().hex[:6]}",
            version="1.0.0",
            display_name="Local Plugin",
            description="Plugin discovered from local filesystem",
        )


class ConfiguredDirectoryDiscovery(DiscoveryBackend):
    """Discovers plugins from configured directories."""
    
    def __init__(self, directory_paths: List[str]):
        self.directory_paths = directory_paths
    
    @property
    def source(self) -> DiscoverySource:
        return DiscoverySource.CONFIGURED_DIR
    
    async def discover_plugins(
        self,
        filter_func: Optional[Callable[[PluginManifest], bool]] = None,
    ) -> List[DiscoveryResult]:
        """Discover from configured directories."""
        results: List[DiscoveryResult] = []
        
        for path in self.directory_paths:
            try:
                manifest = await self._load_manifest(path)
                if filter_func and not filter_func(manifest):
                    continue
                
                is_valid, errors = validate_manifest(manifest)
                
                descriptor = PluginDescriptor(
                    manifest=manifest,
                    source_path=path,
                    discovery_timestamp=time.monotonic(),
                )
                
                record = RegistrationRecord.create(
                    descriptor,
                    DiscoverySource.CONFIGURED_DIR,
                )
                
                results.append(DiscoveryResult(
                    record=record,
                    manifest_valid=is_valid,
                    errors=errors,
                ))
            except Exception as e:
                pass
        
        return results
    
    async def _load_manifest(self, path: str) -> PluginManifest:
        """Load manifest from a directory."""
        # Stub implementation
        return PluginManifest.create(
            namespace="configured",
            name=f"plugin_{uuid.uuid4().hex[:6]}",
            version="1.0.0",
            display_name="Configured Plugin",
            description="Plugin from configured directory",
        )


# =============================================================================
# PLUGIN REGISTRY
# =============================================================================


class PluginRegistry:
    """
    Central registry for all plugin registrations.
    
    Provides:
        - Deterministic plugin registration with unique IDs
        - Duplicate detection and rejection
        - Discovery source tracking
        - Manifest validation
    
    Thread Safety:
        All operations are async and use internal locking.
    """
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._lock = asyncio.Lock()
        
        # Storage structures
        self._registrations: Dict[str, RegistrationRecord] = {}  # plugin_id -> record
        self._registration_ids: Dict[str, str] = {}  # reg_id -> plugin_id
        
        # Discovery source tracking
        self._by_source: Dict[DiscoverySource, Set[str]] = {}
        
        # Health tracking
        self._health_status: Dict[str, str] = {}
    
    async def register_plugin(
        self,
        descriptor: PluginDescriptor,
        source: DiscoverySource = DiscoverySource.LOCAL_PACKAGE,
        config_hash: Optional[str] = None,
    ) -> RegistrationRecord:
        """
        Register a plugin with the registry.
        
        Args:
            descriptor: The plugin descriptor (with manifest)
            source: Where this plugin was discovered from
            config_hash: Hash of configuration for change detection
            
        Returns:
            The created registration record
            
        Raises:
            DuplicateRegistrationError: If plugin is already registered
        """
        async with self._lock:
            plugin_id = str(descriptor.manifest.id)
            
            # Check for duplicates
            if plugin_id in self._registrations:
                existing = self._registrations[plugin_id]
                raise DuplicateRegistrationError(
                    f"Plugin '{plugin_id}' is already registered",
                    plugin_id=plugin_id,
                    existing_plugin=existing,
                )
            
            # Create the registration record
            record = RegistrationRecord.create(descriptor, source)
            if config_hash:
                record = PluginRegistry._update_with_config_hash(record, config_hash)
            
            # Store the record
            self._registrations[plugin_id] = record
            self._registration_ids[record.registration_id] = plugin_id
            
            # Track by source
            if source not in self._by_source:
                self._by_source[source] = set()
            self._by_source[source].add(plugin_id)
            
            return record
    
    async def unregister_plugin(self, plugin_id: str) -> bool:
        """
        Remove a plugin from the registry.
        
        Args:
            plugin_id: The plugin identifier
            
        Returns:
            True if unregistered, False if not found
        """
        async with self._lock:
            if plugin_id not in self._registrations:
                return False
            
            record = self._registrations.pop(plugin_id)
            
            # Remove from registration_ids
            for reg_id, pid in list(self._registration_ids.items()):
                if pid == plugin_id:
                    del self._registration_ids[reg_id]
                    break
            
            # Remove from source tracking
            source = record.source
            if source in self._by_source:
                self._by_source[source].discard(plugin_id)
            
            return True
    
    async def get_registration(self, plugin_id: str) -> Optional[RegistrationRecord]:
        """
        Get registration info for a plugin.
        
        Args:
            plugin_id: The plugin identifier
            
        Returns:
            RegistrationRecord if found, None otherwise
        """
        async with self._lock:
            return self._registrations.get(plugin_id)
    
    async def get_plugin_ids(self) -> List[str]:
        """Get all registered plugin IDs."""
        async with self._lock:
            return list(self._registrations.keys())
    
    async def get_all_registrations(
        self,
    ) -> Dict[str, RegistrationRecord]:
        """
        Get all registered plugins.
        
        Returns:
            Dictionary mapping plugin_id to registration record
        """
        async with self._lock:
            return dict(self._registrations)
    
    async def get_registrations_by_source(
        self,
        source: DiscoverySource,
    ) -> List[RegistrationRecord]:
        """
        Get all registrations from a specific discovery source.
        
        Args:
            source: The discovery source
            
        Returns:
            List of registration records
        """
        async with self._lock:
            plugin_ids = self._by_source.get(source, set())
            return [self._registrations[pid] for pid in plugin_ids]
    
    async def count_by_source(self) -> Dict[str, int]:
        """Count plugins by discovery source."""
        async with self._lock:
            return {s.value: len(ids) for s, ids in self._by_source.items()}
    
    async def verify_plugin_valid(
        self,
        plugin_id: str,
    ) -> tuple[bool, List[str]]:
        """
        Verify a plugin's manifest is valid.
        
        Args:
            plugin_id: The plugin identifier
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        async with self._lock:
            record = self._registrations.get(plugin_id)
            
            if not record:
                return False, [f"Unknown plugin ID: {plugin_id}"]
            
            is_valid, errors = validate_manifest(record.plugin_descriptor.manifest)
            return is_valid, errors
    
    def has_plugin(self, plugin_id: str) -> bool:
        """Check if a plugin is registered."""
        return plugin_id in self._registrations
    
    async def update_health_status(
        self,
        plugin_id: str,
        status: str,
    ) -> None:
        """
        Update the health status of a plugin.
        
        Args:
            plugin_id: The plugin identifier
            status: Health status string (healthy, degraded, failed)
        """
        async with self._lock:
            self._health_status[plugin_id] = status
    
    async def get_health_status(self, plugin_id: str) -> Optional[str]:
        """Get the health status of a plugin."""
        async with self._lock:
            return self._health_status.get(plugin_id)
    
    def __len__(self) -> int:
        """Return number of registered plugins."""
        return len(self._registrations)
    
    def __contains__(self, plugin_id: str) -> bool:
        """Check if a plugin is registered."""
        return plugin_id in self._registrations
    
    @staticmethod
    def _update_with_config_hash(
        record: RegistrationRecord,
        config_hash: str,
    ) -> RegistrationRecord:
        """Update a record with a configuration hash."""
        # Return new record with updated config_hash
        return RegistrationRecord(
            registration_id=record.registration_id,
            plugin_descriptor=record.plugin_descriptor,
            source=record.source,
            discovered_at=record.discovered_at,
            verified_at=record.verified_at,
            config_hash=config_hash,
        )


# =============================================================================
# DISCOVERY SERVICE (orchestrates multiple backends)
# =============================================================================


class DiscoveryService:
    """
    Orchestrates plugin discovery across multiple backends.
    
    Provides a unified interface for discovering plugins from
    various sources while handling deduplication and validation.
    """
    
    def __init__(self, registry: PluginRegistry):
        """
        Initialize the discovery service.
        
        Args:
            registry: The plugin registry to register discovered plugins in
        """
        self._registry = registry
        self._backends: List[DiscoveryBackend] = []
        self._lock = asyncio.Lock()
    
    def add_backend(self, backend: DiscoveryBackend) -> None:
        """
        Add a discovery backend.
        
        Args:
            backend: The discovery backend to add
        """
        with self._lock:
            self._backends.append(backend)
    
    async def discover_all(
        self,
        filter_func: Optional[Callable[[PluginManifest], bool]] = None,
    ) -> List[DiscoveryResult]:
        """
        Discover plugins from all configured backends.
        
        Args:
            filter_func: Optional function to filter results
            
        Returns:
            List of discovery results from all sources
        """
        all_results: List[DiscoveryResult] = []
        
        for backend in self._backends:
            try:
                results = await backend.discover_plugins(filter_func)
                all_results.extend(results)
            except Exception as e:
                # Log error but continue with other backends
                pass
        
        return all_results
    
    async def register_discovered(
        self,
        result: DiscoveryResult,
    ) -> RegistrationRecord:
        """
        Register a discovered plugin.
        
        Args:
            result: The discovery result containing the record
            
        Returns:
            The registration record
            
        Raises:
            DuplicateRegistrationError: If already registered
        """
        return await self._registry.register_plugin(
            result.record.plugin_descriptor,
            result.record.source,
            config_hash=result.record.config_hash,
        )
    
    def get_backend_count(self) -> int:
        """Get number of configured discovery backends."""
        return len(self._backends)


__all__ = [
    # Enums
    "DiscoverySource",
    
    # Data classes
    "RegistrationRecord",
    "DiscoveryResult",
    
    # Validation
    "validate_manifest",
    
    # Discovery backends
    "DiscoveryBackend",
    "LocalPackageDiscovery",
    "ConfiguredDirectoryDiscovery",
    "DiscoveryService",
    
    # Registry
    "PluginRegistry",
]