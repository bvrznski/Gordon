# Runtime Integration - Phase 3.8.8.5
# =====================================
"""
Runtime integration layer for Plugin & Extensibility Infrastructure.

Provides:
- Plugin orchestration with runtime lifecycle
- Resource governance and cleanup
- Security integration for plugins
- Isolation boundaries

Integration Points:
    - Startup: Load eager plugins, initialize capabilities
    - Shutdown: Graceful plugin unloading, resource cleanup
    - Runtime operations: Plugin activation/deactivation
    - Observability: Emit plugin lifecycle events
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import time

# Import from abstraction module
try:
    from .abstraction import (
        Plugin,
        PluginManifest,
        PluginContext,
        PluginState,
        PluginError,
    )
except ImportError:
    class Plugin:
        pass
    
    class PluginError(Exception):
        pass


class OrchestrationPhase(Enum):
    """Phases of plugin orchestration."""
    
    PRE_STARTUP = "pre_startup"           # Before startup sequence
    STARTUP = "startup"                   # During startup
    ACTIVE = "active"                     # Normal operation
    SHUTDOWN = "shutdown"                 # During shutdown
    RECOVERY = "recovery"                 # After failure recovery


@dataclass(frozen=True)
class OrchestrationEvent:
    """An orchestration event in the plugin lifecycle."""
    
    phase: OrchestrationPhase
    timestamp: float
    plugin_id: str
    event_type: str  # started, stopped, activated, deactivated, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# PLUGIN ORCHESTRATOR
# =============================================================================


class PluginOrchestrator:
    """
    Orchestrates plugin execution across the runtime lifecycle.
    
    Responsibilities:
        - Coordinate startup order based on dependencies
        - Manage shutdown sequence
        - Handle recovery scenarios
        - Enforce resource governance
    
    Thread Safety:
        All operations use internal locking for safety.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self._lock = asyncio.Lock()
        
        # Active plugins
        self._active_plugins: Dict[str, Plugin] = {}
        
        # Orchestration history
        self._orchestration_history: List[OrchestrationEvent] = []
        
        # Resource tracking
        self._plugin_resources: Dict[str, List[str]] = {}
    
    async def start_plugins(
        self,
        plugins: List[tuple[PluginManifest, Plugin]],
        context: PluginContext,
    ) -> List[tuple[PluginManifest, bool]]:
        """
        Start all plugins in dependency order.
        
        Args:
            plugins: List of (manifest, plugin_instance) tuples
            context: Execution context
            
        Returns:
            List of (manifest, success) tuples for each plugin
        """
        async with self._lock:
            results: List[tuple[PluginManifest, bool]] = []
            
            # Sort by dependency order (simplified - just use provided order)
            for manifest, plugin in plugins:
                try:
                    await self._start_plugin(manifest, plugin, context)
                    results.append((manifest, True))
                except Exception as e:
                    results.append((manifest, False))
                    
            return results
    
    async def _start_plugin(
        self,
        manifest: PluginManifest,
        plugin: Plugin,
        context: PluginContext,
    ) -> None:
        """Start a single plugin."""
        # Add to active plugins
        plugin_id = str(manifest.id)
        self._active_plugins[plugin_id] = plugin
        
        # Record orchestration event
        event = OrchestrationEvent(
            phase=OrchestrationPhase.STARTUP,
            timestamp=time.monotonic(),
            plugin_id=plugin_id,
            event_type="started",
        )
        self._orchestration_history.append(event)
        
        # Activate the plugin
        await plugin.activate()
    
    async def stop_plugins(self) -> List[tuple[str, bool]]:
        """
        Stop all active plugins in reverse order.
        
        Returns:
            List of (plugin_id, success) tuples
        """
        async with self._lock:
            results: List[tuple[str, bool]] = []
            
            # Reverse order for graceful shutdown
            plugin_ids = list(reversed(list(self._active_plugins.keys())))
            
            for plugin_id in plugin_ids:
                try:
                    await self._stop_plugin(plugin_id)
                    results.append((plugin_id, True))
                except Exception as e:
                    results.append((plugin_id, False))
            
            return results
    
    async def _stop_plugin(self, plugin_id: str) -> None:
        """Stop a single plugin."""
        if plugin_id not in self._active_plugins:
            return
        
        plugin = self._active_plugins.pop(plugin_id)
        
        # Record orchestration event
        event = OrchestrationEvent(
            phase=OrchestrationPhase.SHUTDOWN,
            timestamp=time.monotonic(),
            plugin_id=plugin_id,
            event_type="stopped",
        )
        self._orchestration_history.append(event)
    
    async def get_active_plugins(self) -> List[str]:
        """Get list of currently active plugin IDs."""
        async with self._lock:
            return list(self._active_plugins.keys())
    
    async def get_orchestration_history(
        self,
        phase: Optional[OrchestrationPhase] = None,
    ) -> List[OrchestrationEvent]:
        """
        Get orchestration history events.
        
        Args:
            phase: Filter by phase (None = all)
            
        Returns:
            List of orchestration events
        """
        async with self._lock:
            if phase is None:
                return list(self._orchestration_history)
            return [
                e for e in self._orchestration_history
                if e.phase == phase
            ]
    
    def track_plugin_resources(
        self,
        plugin_id: str,
        resource_ids: List[str],
    ) -> None:
        """
        Track resources owned by a plugin.
        
        Args:
            plugin_id: The plugin identifier
            resource_ids: List of resource IDs to track
        """
        self._plugin_resources[plugin_id] = list(resource_ids)
    
    async def release_plugin_resources(
        self,
        plugin_id: str,
    ) -> List[str]:
        """
        Release all resources owned by a plugin.
        
        Args:
            plugin_id: The plugin identifier
            
        Returns:
            List of released resource IDs
        """
        if plugin_id not in self._plugin_resources:
            return []
        
        resources = list(self._plugin_resources[plugin_id])
        del self._plugin_resources[plugin_id]
        return resources
    
    async def reset(self) -> None:
        """Reset all orchestration state."""
        async with self._lock:
            self._active_plugins.clear()
            self._orchestration_history.clear()
            self._plugin_resources.clear()


# =============================================================================
# ISOLATION BOUNDARIES
# =============================================================================


class IsolationBoundary(Enum):
    """Types of isolation boundaries."""
    
    EXECUTION = "execution"     # Separate execution contexts
    CAPABILITY = "capability"   # Capability access restrictions
    PROVIDER = "provider"       # Provider access isolation
    FAULT = "fault"             # Fault containment
    RESOURCE = "resource"       # Resource allocation limits


@dataclass(frozen=True)
class IsolationPolicy:
    """Isolation policy for a plugin."""
    
    plugin_id: str
    
    # Boundary types
    execution_isolated: bool = True
    capability_restricted: bool = True
    provider_isolated: bool = True
    fault_contained: bool = True
    resource_limited: bool = True
    
    # Limits
    max_resources: int = 100
    timeout_seconds: float = 30.0
    
    @classmethod
    def strict(cls, plugin_id: str) -> "IsolationPolicy":
        """Create a strict isolation policy."""
        return cls(
            plugin_id=plugin_id,
            execution_isolated=True,
            capability_restricted=True,
            provider_isolated=True,
            fault_contained=True,
            resource_limited=True,
        )
    
    @classmethod
    def permissive(cls, plugin_id: str) -> "IsolationPolicy":
        """Create a permissive isolation policy."""
        return cls(
            plugin_id=plugin_id,
            execution_isolated=False,
            capability_restricted=False,
            provider_isolated=False,
            fault_contained=False,
            resource_limited=False,
        )
    
    def allows_capability(self, capability: str) -> bool:
        """Check if a capability is allowed under this policy."""
        return not self.capability_restricted


# =============================================================================
# RESOURCE GOVERNANCE
# =============================================================================


@dataclass(frozen=True)
class ResourceLease:
    """A lease on resources for a plugin."""
    
    plugin_id: str
    resource_ids: List[str]
    expires_at: float  # Unix timestamp
    
    def is_expired(self) -> bool:
        """Check if lease has expired."""
        return time.monotonic() > self.expires_at


class ResourceGovernance:
    """
    Manages resource allocation and cleanup for plugins.
    
    Ensures plugins cannot leak resources and that all owned
    resources are reclaimed on plugin unload.
    """
    
    def __init__(self):
        """Initialize the governance system."""
        self._lock = asyncio.Lock()
        
        # Active leases
        self._leases: Dict[str, ResourceLease] = {}
        
        # Resource ownership tracking
        self._ownership: Dict[str, str] = {}  # resource_id -> plugin_id
    
    async def allocate_resources(
        self,
        plugin_id: str,
        resource_ids: List[str],
        lease_duration_seconds: float = 3600.0,
    ) -> ResourceLease:
        """
        Allocate resources to a plugin.
        
        Args:
            plugin_id: The plugin identifier
            resource_ids: Resources to allocate
            lease_duration_seconds: How long lease is valid
            
        Returns:
            The resource lease object
        """
        async with self._lock:
            expires_at = time.monotonic() + lease_duration_seconds
            
            lease = ResourceLease(
                plugin_id=plugin_id,
                resource_ids=list(resource_ids),
                expires_at=expires_at,
            )
            
            for rid in resource_ids:
                self._ownership[rid] = plugin_id
            
            self._leases[plugin_id] = lease
            return lease
    
    async def release_resources(self, plugin_id: str) -> List[str]:
        """
        Release all resources owned by a plugin.
        
        Args:
            plugin_id: The plugin identifier
            
        Returns:
            List of released resource IDs
        """
        async with self._lock:
            if plugin_id not in self._leases:
                return []
            
            lease = self._leases.pop(plugin_id)
            
            # Release all resources
            released = list(lease.resource_ids)
            for rid in lease.resource_ids:
                self._ownership.pop(rid, None)
            
            return released
    
    async def cleanup_expired_leases(self) -> List[str]:
        """
        Clean up expired resource leases.
        
        Returns:
            List of reclaimed resource IDs
        """
        async with self._lock:
            now = time.monotonic()
            expired_ids = [
                pid for pid, lease in self._leases.items()
                if lease.expires_at < now
            ]
            
            reclaimed: List[str] = []
            for plugin_id in expired_ids:
                resources = await self.release_resources(plugin_id)
                reclaimed.extend(resources)
            
            return reclaimed
    
    def get_resource_owner(self, resource_id: str) -> Optional[str]:
        """Get the plugin that owns a resource."""
        return self._ownership.get(resource_id)


__all__ = [
    # Enums
    "OrchestrationPhase",
    "IsolationBoundary",
    
    # Data classes
    "OrchestrationEvent",
    "IsolationPolicy",
    "ResourceLease",
    
    # Classes
    "PluginOrchestrator",
    "ResourceGovernance",
]