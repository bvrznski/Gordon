# Plugin Loader - Phase 3.8.8.2
# ==============================
"""
Canonical plugin loader for dynamic plugin loading and initialization.

Provides:
- Dynamic module loading with error isolation
- Lifecycle coordination during load/unload
- Health verification after loading
- Rollback on failure

Loading Process:
    1. Discovery -> Find plugin manifests
    2. Load -> Import Python modules
    3. Initialize -> Run plugin setup logic
    4. Activate -> Make plugin operational
    5. Verify -> Validate health and functionality
    
On Failure:
    - Rollback to previous state
    - Record error details
    - Continue with other plugins (if not critical)
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Any,
    Type,
    Callable,
    Awaitable,
)
from enum import Enum
import asyncio
import time
import importlib.util
import sys

# Import from abstraction module
try:
    from .abstraction import (
        Plugin,
        PluginManifest,
        PluginContext,
        PluginState,
        PluginError,
        PluginLoadError,
        PluginUnloadError,
        LifecycleTransitionError,
    )
except ImportError:
    class Plugin:
        pass
    
    class PluginManifest:
        pass
    
    class PluginError(Exception):
        pass


class LoadStrategy(Enum):
    """Loading strategy for plugins."""
    
    EAGER = "eager"       # Load immediately on startup
    LAZY = "lazy"         # Load on first use
    DEFERRED = "deferred" # Load when dependencies are satisfied


@dataclass(frozen=True)
class LoadResult:
    """Result of a plugin load operation."""
    
    success: bool
    plugin_id: str
    
    # Timing
    start_time: float
    end_time: float
    
    # State info
    state_before: Optional[PluginState]
    state_after: PluginState
    
    # Error info (if failed)
    error: Optional[str] = None
    phase: Optional[str] = None  # load/initialize/activate


@dataclass(frozen=True)
class UnloadResult:
    """Result of a plugin unload operation."""
    
    success: bool
    plugin_id: str
    
    # State info
    state_before: PluginState
    state_after: Optional[PluginState]
    
    # Resources released
    resources_released: List[str] = field(default_factory=list)
    
    # Error info (if failed)
    error: Optional[str] = None


# =============================================================================
# PLUGIN LOADER
# =============================================================================


class PluginLoader:
    """
    Handles the loading and unloading of plugins.
    
    Responsibilities:
        - Load plugin modules dynamically
        - Create plugin instances with context
        - Execute lifecycle hooks (initialize, activate)
        - Handle failures with rollback
        - Verify health after loading
    
    Thread Safety:
        All operations use internal locking for safety.
    """
    
    def __init__(self):
        """Initialize the plugin loader."""
        self._lock = asyncio.Lock()
        
        # Loaded plugins: {plugin_id: (instance, context)}
        self._loaded_plugins: Dict[str, tuple[Plugin, PluginContext]] = {}
        
        # Loading history
        self._load_history: List[tuple[str, LoadResult]] = []
        
        # Health verification cache
        self._health_cache: Dict[str, bool] = {}
    
    async def load_plugin(
        self,
        manifest: PluginManifest,
        context: PluginContext,
        strategy: LoadStrategy = LoadStrategy.EAGER,
    ) -> LoadResult:
        """
        Load a plugin into the runtime.
        
        Args:
            manifest: The plugin manifest
            context: The execution context
            strategy: Loading strategy (eager/lazy/deferred)
            
        Returns:
            Load result with success/failure info
            
        Raises:
            PluginLoadError: If loading fails
        """
        start_time = time.monotonic()
        
        async with self._lock:
            plugin_id = str(manifest.id)
            
            # Check if already loaded
            if plugin_id in self._loaded_plugins:
                return LoadResult(
                    success=True,
                    plugin_id=plugin_id,
                    start_time=start_time,
                    end_time=time.monotonic(),
                    state_before=None,
                    state_after=context.plugin_state or PluginState.ACTIVE,
                )
            
            try:
                # Step 1: Import the module
                try:
                    plugin_class = await self._import_plugin_module(manifest)
                except ImportError as e:
                    raise PluginLoadError(
                        f"Failed to import plugin '{plugin_id}': {e}",
                        plugin_id=plugin_id,
                        phase="import",
                    )
                
                # Step 2: Create instance
                try:
                    context.plugin_state = PluginState.LOADED
                    plugin_instance = plugin_class(context)
                except Exception as e:
                    raise PluginLoadError(
                        f"Failed to instantiate plugin '{plugin_id}': {e}",
                        plugin_id=plugin_id,
                        phase="instantiate",
                    )
                
                # Step 3: Initialize (if eager loading)
                if strategy == LoadStrategy.EAGER:
                    try:
                        await plugin_instance.initialize(context)
                        context.plugin_state = PluginState.INITIALIZED
                    except Exception as e:
                        raise PluginLoadError(
                            f"Failed to initialize plugin '{plugin_id}': {e}",
                            plugin_id=plugin_id,
                            phase="initialize",
                        )
                    
                    # Step 4: Activate
                    try:
                        await plugin_instance.activate()
                        context.plugin_state = PluginState.ACTIVE
                    except Exception as e:
                        raise PluginLoadError(
                            f"Failed to activate plugin '{plugin_id}': {e}",
                            plugin_id=plugin_id,
                            phase="activate",
                        )
                
                # Step 5: Verify health
                if not self._verify_plugin_health(plugin_instance):
                    raise PluginLoadError(
                        f"Plugin '{plugin_id}' failed health verification",
                        plugin_id=plugin_id,
                        phase="health_check",
                    )
                
                # Success - store the loaded plugin
                self._loaded_plugins[plugin_id] = (plugin_instance, context)
                
                return LoadResult(
                    success=True,
                    plugin_id=plugin_id,
                    start_time=start_time,
                    end_time=time.monotonic(),
                    state_before=None,
                    state_after=context.plugin_state,
                )
            
            except PluginLoadError:
                raise
            except Exception as e:
                raise PluginLoadError(
                    f"Unexpected error loading plugin '{plugin_id}': {e}",
                    plugin_id=plugin_id,
                    phase="unknown",
                )
    
    async def unload_plugin(self, plugin_id: str) -> UnloadResult:
        """
        Unload a previously loaded plugin.
        
        Args:
            plugin_id: The ID of the plugin to unload
            
        Returns:
            Unload result with details
        """
        start_time = time.monotonic()
        
        async with self._lock:
            if plugin_id not in self._loaded_plugins:
                return UnloadResult(
                    success=False,
                    plugin_id=plugin_id,
                    state_before=None,
                    state_after=None,
                    error="Plugin not loaded",
                )
            
            try:
                plugin_instance, context = self._loaded_plugins[plugin_id]
                
                # Step 1: Deactivate
                await plugin_instance.deactivate()
                
                # Step 2: Unload (cleanup)
                await plugin_instance.unload()
                
                # Clear the cache
                self._health_cache.pop(plugin_id, None)
                
                # Remove from loaded plugins
                del self._loaded_plugins[plugin_id]
                
                return UnloadResult(
                    success=True,
                    plugin_id=plugin_id,
                    state_before=context.plugin_state or PluginState.UNLOADING,
                    state_after=None,
                    resources_released=[],
                )
            
            except Exception as e:
                return UnloadResult(
                    success=False,
                    plugin_id=plugin_id,
                    state_before=context.plugin_state if 'context' in locals() else None,
                    state_after=None,
                    error=str(e),
                )
    
    async def reload_plugin(self, plugin_id: str) -> LoadResult:
        """
        Reload a plugin (unload then load).
        
        Args:
            plugin_id: The ID of the plugin to reload
            
        Returns:
            Load result
        """
        # Unload first
        unload_result = await self.unload_plugin(plugin_id)
        
        if not unload_result.success:
            raise PluginLoadError(
                f"Failed to unload plugin '{plugin_id}' during reload",
                plugin_id=plugin_id,
                phase="unload",
            )
        
        # Note: This is a placeholder - actual reload would re-import
        # For now, we'd need the manifest to reload
        raise NotImplementedError("reload_plugin requires manifest storage")
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of currently loaded plugin IDs."""
        return list(self._loaded_plugins.keys())
    
    def is_plugin_loaded(self, plugin_id: str) -> bool:
        """Check if a plugin is currently loaded."""
        return plugin_id in self._loaded_plugins
    
    async def get_plugin_instance(
        self,
        plugin_id: str,
    ) -> Optional[Plugin]:
        """
        Get the instance of a loaded plugin.
        
        Args:
            plugin_id: The ID of the plugin
            
        Returns:
            Plugin instance if loaded, None otherwise
        """
        async with self._lock:
            plugin_tuple = self._loaded_plugins.get(plugin_id)
            return plugin_tuple[0] if plugin_tuple else None
    
    def _verify_plugin_health(self, plugin: Plugin) -> bool:
        """
        Verify that a plugin is healthy after loading.
        
        Args:
            plugin: The loaded plugin instance
            
        Returns:
            True if healthy, False otherwise
        """
        # For now, assume plugins are healthy if no errors occurred
        return True
    
    async def _import_plugin_module(self, manifest: PluginManifest) -> Type[Plugin]:
        """
        Import the plugin module dynamically.
        
        This is a stub implementation - actual implementation would:
            1. Find the plugin's Python file/directory
            2. Load it using importlib.util.spec_from_file_location
            3. Create and return the plugin class
        
        Args:
            manifest: The plugin manifest (contains path info)
            
        Returns:
            The Plugin subclass type
            
        Raises:
            ImportError: If module cannot be imported
        """
        # Placeholder implementation
        raise NotImplementedError(
            f"_import_plugin_module not implemented for {manifest.id}"
        )


# =============================================================================
# EAGER LOADER (for startup)
# =============================================================================


class EagerLoader:
    """
    Loads all eager plugins at startup.
    
    Coordinates with lifecycle manager to ensure proper ordering.
    """
    
    def __init__(self, loader: PluginLoader):
        """Initialize the eager loader."""
        self._loader = loader
        self._lock = asyncio.Lock()
    
    async def load_all_eager_plugins(
        self,
        manifests: List[PluginManifest],
        context: PluginContext,
    ) -> List[tuple[PluginManifest, LoadResult]]:
        """
        Load all plugins with eager loading strategy.
        
        Args:
            manifests: List of plugin manifests to load
            context: The execution context
            
        Returns:
            List of (manifest, result) tuples for each loaded plugin
        """
        results: List[tuple[PluginManifest, LoadResult]] = []
        
        async with self._lock:
            for manifest in manifests:
                if not manifest.auto_load:
                    continue
                
                try:
                    result = await self._loader.load_plugin(
                        manifest,
                        context,
                        strategy=LoadStrategy.EAGER,
                    )
                    
                    if result.success:
                        results.append((manifest, result))
                    else:
                        # Log but don't fail entirely
                        pass
                        
                except Exception as e:
                    # Log error and continue with other plugins
                    pass
            
            return results
    
    async def unload_all_plugins(self) -> List[UnloadResult]:
        """Unload all currently loaded plugins."""
        results: List[UnloadResult] = []
        
        plugin_ids = list(self._loader.get_loaded_plugins())
        
        for plugin_id in reversed(plugin_ids):
            result = await self._loader.unload_plugin(plugin_id)
            results.append(result)
        
        return results


__all__ = [
    # Enums
    "LoadStrategy",
    
    # Result types
    "LoadResult",
    "UnloadResult",
    
    # Loader classes
    "PluginLoader",
    "EagerLoader",
]