# Core Plugins Interface
# ======================

"""
Core plugins interface - defines contracts for plugin loading and lifecycle.

This interface allows different plugin systems (dynamic loading, static registration,
remote plugins) while providing a consistent way to discover and manage plugins.

ARCHITECTURAL PRINCIPLES:
- Plugin discovery is separate from plugin execution
- Plugins follow explicit lifecycle (discover -> load -> activate -> deactivate -> unload)
- Multiple plugin systems can coexist
- Plugin failures don't crash the runtime
"""

from typing import Protocol, Optional, List, Dict, Any, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum
import time

T = TypeVar("T")


@dataclass(frozen=True)
class PluginId:
    """Unique identifier for a plugin."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "PluginId":
        """Generate a new unique plugin ID."""
        import uuid
        return cls(value=f"plugin_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def from_parts(cls, domain: str, name: str, version: str = "1.0") -> "PluginId":
        """Create a PluginId from domain, name, and version."""
        return cls(value=f"{domain}.{name}@{version}")


class PluginState(Enum):
    """Plugin lifecycle states."""
    
    DISCOVERED = "discovered"      # Found but not yet loaded
    LOADING = "loading"            # Currently loading
    READY = "ready"                # Loaded and ready to activate
    ACTIVE = "active"              # Active and running
    DEACTIVATING = "deactivating"  # Currently deactivating
    INACTIVE = "inactive"          # Inactive but loaded
    UNLOADING = "unloading"        # Currently unloading
    FAILED = "failed"              # Failed, requires recovery


@dataclass(frozen=True)
class PluginInfo:
    """
    Immutable information about a plugin.
    
    Args:
        plugin_id: Unique identifier for this plugin
        domain: What capability domain this plugin serves (e.g., "model", "storage")
        name: Human-readable name
        version: Plugin version string
        state: Current lifecycle state
        dependencies: List of other plugins this depends on
        capabilities: List of capability names this plugin provides
    """
    
    plugin_id: str
    domain: str
    name: str
    version: str = "1.0"
    state: PluginState = PluginState.DISCOVERED
    dependencies: List[str] = None  # type: ignore
    capabilities: List[str] = None  # type: ignore


@dataclass(frozen=True)
class PluginMetadata:
    """
    Metadata about a plugin implementation.
    
    Args:
        module_path: Where the plugin code is located
        entry_point: Function/class to instantiate
        config_schema: JSON schema for required configuration
        enabled_by_default: Whether the plugin activates automatically
    """
    
    module_path: str
    entry_point: str = "Plugin"
    config_schema: Optional[Dict[str, Any]] = None
    enabled_by_default: bool = True


class IPlugin(Protocol):
    """
    Interface for a plugin instance.
    
    Plugins implement specific functionality that integrates with the runtime.
    """
    
    @property
    def plugin_id(self) -> PluginId:
        """Get the unique ID of this plugin."""
        ...
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the plugin with configuration.
        
        Args:
            config: Plugin-specific configuration dictionary
        """
        ...
    
    async def activate(self) -> None:
        """
        Activate the plugin and begin its work.
        
        Called after initialization. The plugin should start
        any background tasks or register handlers here.
        """
        ...
    
    async def deactivate(self) -> None:
        """
        Deactivate the plugin gracefully.
        
        Cleanup resources, unregister handlers, stop background tasks.
        """
        ...
    
    async def shutdown(self) -> None:
        """
        Shutdown the plugin completely.
        
        Called after deactivation. Perform final cleanup.
        """
        ...


class IPluginLoader(Protocol):
    """
    Interface for loading plugins from various sources.
    
    Loaders are responsible for:
        - Locating plugin implementations (filesystem, remote, etc.)
        - Creating plugin instances
        - Validating plugin metadata
        - Handling load errors gracefully
    """
    
    @property
    def loader_id(self) -> str:
        """Get the unique ID of this loader."""
        ...
    
    async def discover(
        self,
        domain: Optional[str] = None,
    ) -> List[PluginMetadata]:
        """
        Discover plugins available from this loader.
        
        Args:
            domain: Filter by domain (None = all domains)
            
        Returns:
            List of plugin metadata found
        """
        ...
    
    async def load(
        self,
        metadata: PluginMetadata,
        config: Dict[str, Any],
    ) -> IPlugin:
        """
        Load a plugin from its metadata.
        
        Args:
            metadata: The plugin's metadata
            config: Runtime configuration for this plugin
            
        Returns:
            A loaded plugin instance ready for initialization
        """
        ...
    
    async def unload(self, plugin: IPlugin) -> None:
        """
        Unload a previously loaded plugin.
        
        Args:
            plugin: The plugin to unload
        """
        ...


class IPluginRegistry(Protocol):
    """
    Interface for the plugin registry - maintains loaded plugins and enables discovery.
    
    The registry:
        - Stores plugin instances and metadata
        - Enables lookup by domain or capability
        - Manages dependencies between plugins
        - Tracks plugin lifecycle state
    """
    
    @property
    def registry_id(self) -> str:
        """Get the unique ID of this registry."""
        ...
    
    async def register_plugin(
        self,
        plugin: IPlugin,
        metadata: PluginMetadata,
    ) -> None:
        """
        Register a loaded plugin with the registry.
        
        Args:
            plugin: The loaded plugin instance
            metadata: Its metadata
        """
        ...
    
    async def unregister(self, plugin_id: str) -> bool:
        """
        Remove a plugin from the registry.
        
        Args:
            plugin_id: The ID of the plugin to remove
            
        Returns:
            True if found and removed
        """
        ...
    
    def get_plugin(
        self,
        plugin_id: str,
    ) -> Optional[IPlugin]:
        """
        Get a registered plugin by ID.
        
        Args:
            plugin_id: The plugin's unique ID
            
        Returns:
            The plugin instance or None if not found
        """
        ...
    
    def get_plugins_for_domain(
        self,
        domain: str,
    ) -> List[IPlugin]:
        """
        Get plugins for a specific domain.
        
        Args:
            domain: The capability domain (e.g., "model", "storage")
            
        Returns:
            List of plugin instances in that domain
        """
        ...
    
    async def get_plugin_state(
        self,
        plugin_id: str,
    ) -> Optional[PluginInfo]:
        """Get information about a registered plugin."""
        ...


class IPluginManager(Protocol):
    """
    Interface for managing the complete plugin lifecycle.
    
    The manager handles:
        - Discovery of available plugins
        - Loading and initialization
        - Activation/deactivation sequence (respecting dependencies)
        - Shutdown and unloading
    """
    
    @property
    def manager_id(self) -> str:
        """Get the unique ID of this manager."""
        ...
    
    async def load_all(
        self,
        enabled_only: bool = True,
    ) -> List[IPlugin]:
        """
        Load all available plugins.
        
        Args:
            enabled_only: If True, only load plugins marked as enabled
            
        Returns:
            List of successfully loaded plugin instances
        """
        ...
    
    async def activate_all(self) -> None:
        """Activate all loaded and ready plugins."""
        ...
    
    async def deactivate_all(self) -> None:
        """Deactivate all active plugins in reverse order."""
        ...
    
    async def unload_all(self) -> None:
        """Unload all loaded plugins."""
        ...


class PluginError(Exception):
    """Raised when plugin operations fail."""
    pass


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""
    
    def __init__(self, plugin_id: str, cause: Optional[Exception] = None):
        msg = f"Failed to load plugin {plugin_id}"
        if cause:
            msg += f": {cause}"
        super().__init__(msg)
        self.plugin_id = plugin_id
        self.cause = cause


class PluginDependencyError(PluginError):
    """Raised when plugin dependencies cannot be resolved."""
    
    def __init__(self, plugin_id: str, missing: List[str]):
        super().__init__(
            f"Plugin {plugin_id} has unmet dependencies: {missing}"
        )
        self.plugin_id = plugin_id
        self.missing = missing


__all__ = [
    "PluginId",
    "PluginState",
    "PluginInfo",
    "PluginMetadata",
    "IPlugin",
    "IPluginLoader",
    "IPluginRegistry",
    "IPluginManager",
    "PluginError",
    "PluginLoadError",
    "PluginDependencyError",
]