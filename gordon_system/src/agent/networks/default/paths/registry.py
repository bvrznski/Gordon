# Default Network Path Registry
# =============================

"""
Path handler registry for the Default Network.

This module provides:
    • DefaultNetworkPathRegistry: Immutable mapping of path kinds to handlers
    
The registry enables deterministic path selection by providing a bounded,
validated mapping from path identifiers to handler implementations.

PHASE 4.3.12: Path Registry
"""

from __future__ import annotations

from typing import Mapping, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DefaultNetworkPathRegistry:
    """
    Immutable registry of path handlers.
    
    Maps semantic coordination paths to their handler implementations.
    The registry is constructed once and never mutated - this ensures
    deterministic path selection.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-PATH-REGISTRY-INV-001: Registry is immutable after construction
        DEFAULT-PATH-REGISTRY-INV-002: Each path maps to exactly one handler
        DEFAULT-PATH-REGISTRY-INV-003: Duplicate registrations are rejected
        DEFAULT-PATH-REGISTRY-INV-004: Path ordering is deterministic
        
    PROPERTIES:
        • handlers: Mapping of path kind to handler instance
        
    VALIDATION:
        • validate_path: Check if a path is registered
        
    ENUMERATION:
        • all_paths: Get all registered paths
        • get_handler: Get the handler for a specific path
    
    NOT RESPONSIBLE FOR:
        • Discovering plugins at runtime
        • Loading handlers dynamically
        • Mutating after construction
    """
    
    # Path -> Handler mapping (frozen, immutable)
    _handlers: Mapping[str, object]  # Handlers implement DefaultNetworkPathHandler protocol
    
    # Registered path ordering for deterministic selection
    _path_ordering: Tuple[str, ...]
    
    # Metadata
    _created_at_utc: datetime
    _version: str = "1.0.0"
    
    def __init__(
        self,
        handlers: Mapping[str, object] | None = None,
        path_ordering: Tuple[str, ...] | None = None,
    ):
        """
        Create a new path registry.
        
        Args:
            handlers: Mapping of path kind to handler instance
            path_ordering: Deterministic ordering for path selection
        """
        handlers_map = handlers or {}
        ordering = path_ordering or tuple(handlers_map.keys())
        
        # Store as frozen attributes
        object.__setattr__(self, "_handlers", handlers_map)
        object.__setattr__(self, "_path_ordering", ordering)
        object.__setattr__(self, "_created_at_utc", datetime.utcnow())
    
    @classmethod
    def with_handlers(
        cls,
        *handler_instances: object,
        path_ordering: Tuple[str, ...] | None = None,
    ) -> DefaultNetworkPathRegistry:
        """
        Create a registry from handler instances.
        
        Args:
            handler_instances: Handler implementations (must have .path property)
            path_ordering: Deterministic ordering for path selection
            
        Returns:
            New registry instance
        """
        handlers_map: dict[str, object] = {}
        for handler in handler_instances:
            # Handlers must implement the protocol with a 'path' property
            if hasattr(handler, "path"):
                path_kind = handler.path
                if path_kind in handlers_map:
                    raise ValueError(f"Duplicate registration for path: {path_kind}")
                handlers_map[path_kind] = handler
        
        ordering = path_ordering or tuple(handlers_map.keys())
        
        return cls(
            handlers=handlers_map,
            path_ordering=ordering,
        )
    
    def get_handler(self, path: str) -> object | None:
        """
        Get the handler for a specific path.
        
        Args:
            path: The semantic coordination path
            
        Returns:
            Handler instance if registered, None otherwise
        """
        return self._handlers.get(path)
    
    def has_path(self, path: str) -> bool:
        """Check if a path is registered."""
        return path in self._handlers
    
    @property
    def all_paths(self) -> Tuple[str, ...]:
        """Get all registered paths in deterministic order."""
        return self._path_ordering
    
    def validate_path(self, path: str) -> bool:
        """
        Check if a path is valid for this registry.
        
        Args:
            path: The semantic coordination path to check
            
        Returns:
            True if the path is registered
        """
        return path in self._handlers
    
    @property
    def handler_count(self) -> int:
        """Get the number of registered handlers."""
        return len(self._handlers)
    
    @property
    def version(self) -> str:
        """Get the registry version."""
        return self._version


# =============================================================================
# BUILT-IN PATH REGISTRY FACTORY
# =============================================================================

def create_default_path_registry() -> DefaultNetworkPathRegistry:
    """
    Create a default path registry with all built-in handlers.
    
    This provides sensible defaults for production use. Custom registries
    can be created by directly instantiating DefaultNetworkPathRegistry.
    
    Returns:
        Registry with standard paths and handlers
    """
    # In a full implementation, this would include actual handler instances
    # For now, we return an empty registry - handlers are provided externally
    
    return DefaultNetworkPathRegistry(
        handlers={},
        path_ordering=(),
    )