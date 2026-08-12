# Core Configuration Interface
# ============================

"""
Core configuration interface - defines contracts for configuration sources.

This interface allows multiple configuration backends (file, environment,
remote service) while providing a consistent way to read and watch configuration.

ARCHITECTURAL PRINCIPLES:
- Configuration is immutable at runtime (after startup)
- Configuration can be hot-reloaded without restart
- Sources can be layered with override semantics
"""

from typing import Protocol, Optional, Any, Dict, List, Union
from dataclasses import dataclass
from enum import Enum


class ConfigValueType(Enum):
    """Types of configuration values."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


@dataclass(frozen=True)
class ConfigEntry:
    """
    A single configuration entry with its metadata.
    
    Args:
        key: Dot-separated path to the configuration value
        value: The actual configuration value (any type)
        source: Name of the source that provided this value
        default_value: Optional default if not explicitly set
        is_required: Whether this value must be present
    """
    key: str
    value: Any
    source: str = "unknown"
    default_value: Any = None
    is_required: bool = False


class IConfigurationSource(Protocol):
    """
    Interface for a single configuration source.
    
    Examples of implementations:
        - FileConfigSource (YAML, JSON files)
        - EnvConfigSource (environment variables)
        - RemoteConfigSource (HTTP/HTTPS API)
        - ConsulConfigSource (Consul KV store)
        - ZookeeperConfigSource (ZooKeeper)
    """
    
    @property
    def source_name(self) -> str:
        """Get the unique name of this configuration source."""
        ...
    
    async def load(self) -> Dict[str, Any]:
        """
        Load all configuration from this source.
        
        Returns:
            Dictionary mapping configuration keys to values
        """
        ...
    
    async def get_value(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get a single configuration value by key.
        
        Args:
            key: Dot-separated configuration path (e.g., "server.port")
            default: Value to return if key not found
            
        Returns:
            The configuration value or default
        """
        ...
    
    async def watch(
        self,
        callback: callable,  # type: ignore  # Callable[[Dict[str, Any]], None]
    ) -> str:
        """
        Register a callback for configuration changes.
        
        Args:
            callback: Function to call when config changes
            
        Returns:
            Watch ID for removing the watcher later
        """
        ...
    
    def unwatch(self, watch_id: str) -> bool:
        """
        Remove a registered watcher.
        
        Args:
            watch_id: The ID returned from watch()
            
        Returns:
            True if watcher was removed
        """
        ...


class IConfigurationProvider(Protocol):
    """
    Interface for the configuration provider - the entry point for config access.
    
    This is typically a singleton that coordinates multiple sources.
    """
    
    async def load(self) -> Dict[str, Any]:
        """
        Load configuration from all registered sources with proper overrides.
        
        Sources are loaded in priority order. Later sources override earlier ones.
        
        Returns:
            Merged configuration dictionary
        """
        ...
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get a configuration value.
        
        Args:
            key: Dot-separated path to the value
            default: Value if not found
            
        Returns:
            The configuration value or default
        """
        ...
    
    async def get_async(self, key: str, default: Any = None) -> Optional[Any]:
        """Async version of get()."""
        ...
    
    def has_key(self, key: str) -> bool:
        """Check if a configuration key exists."""
        ...
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Complete merged configuration dictionary
        """
        ...
    
    @property
    def sources(self) -> List[IConfigurationSource]:
        """Get the list of configured sources in priority order."""
        ...


class ConfigurationError(Exception):
    """Raised when configuration loading or access fails."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when a required configuration value is missing."""
    
    def __init__(self, key: str):
        super().__init__(f"Missing required configuration value: {key}")
        self.key = key


__all__ = [
    "ConfigValueType",
    "ConfigEntry",
    "IConfigurationSource",
    "IConfigurationProvider",
    "ConfigurationError",
    "MissingConfigurationError",
]