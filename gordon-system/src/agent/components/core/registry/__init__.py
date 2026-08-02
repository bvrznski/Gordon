# Core Registry Infrastructure
# ============================

"""
Core runtime entity registries.

Provides controlled registration and lookup for runtime entities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypeVar, Generic
import threading
from enum import Enum

from ..types import EntityId


T = TypeVar("T")


@dataclass(frozen=True)
class RegistryEntry:
    """A registry entry containing key-value pair."""
    
    key: str
    value: Any
    timestamp: float  # monotonic timestamp of registration
    
    @classmethod
    def create(cls, key: str, value: Any) -> "RegistryEntry":
        import time
        return cls(key=key, value=value, timestamp=time.monotonic())


class Registry(Generic[T]):
    """
    Thread-safe registry for runtime entities.
    
    Provides:
    - Controlled registration and lookup
    - Duplicate prevention
    - Immutable snapshots
    - Explicit deregistration
    
    Usage:
        registry = Registry[str]()
        registry.register("service_a", "value")
        value = registry.get("service_a")
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: Dict[str, T] = {}
        self._order: List[str] = []  # Track registration order
    
    def register(self, key: str, value: T) -> bool:
        """
        Register an entity with the given key.
        
        Args:
            key: Unique identifier for the entity
            value: The entity to register
            
        Returns:
            True if registered successfully
            
        Raises:
            RegistrationError: If key already exists
        """
        with self._lock:
            if key in self._entries:
                from ..exceptions import RegistrationError
                raise RegistrationError(
                    f"Duplicate registration key: {key}",
                    registry_key=key
                )
            self._entries[key] = value
            self._order.append(key)
            return True
    
    def get(self, key: str) -> Optional[T]:
        """
        Get an entity by its key.
        
        Args:
            key: The entity's registered key
            
        Returns:
            The registered entity, or None if not found
        """
        with self._lock:
            return self._entries.get(key)
    
    def contains(self, key: str) -> bool:
        """Check if a key exists in the registry."""
        with self._lock:
            return key in self._entries
    
    def deregister(self, key: str) -> Optional[T]:
        """
        Remove an entity from the registry.
        
        Args:
            key: The entity's registered key
            
        Returns:
            The removed entity, or None if not found
        """
        with self._lock:
            if key in self._entries:
                value = self._entries.pop(key)
                self._order.remove(key)
                return value
            return None
    
    def get_all(self) -> Dict[str, T]:
        """Get all registry entries as an immutable copy."""
        with self._lock:
            return dict(self._entries)
    
    def keys(self) -> List[str]:
        """Get all registered keys in registration order."""
        with self._lock:
            return list(self._order)
    
    def snapshot(self) -> "RegistrySnapshot":
        """Create an immutable snapshot of the registry state."""
        with self._lock:
            return RegistrySnapshot(
                entries=dict(self._entries),
                order=list(self._order)
            )
    
    @property
    def size(self) -> int:
        """Return the number of registered entities."""
        with self._lock:
            return len(self._entries)


@dataclass(frozen=True)
class RegistrySnapshot:
    """Immutable snapshot of registry state."""
    
    entries: Dict[str, Any]
    order: List[str]
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the snapshot."""
        return self.entries.get(key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return as dictionary."""
        return dict(self.entries)


# Component registry - for core components
class ComponentRegistry(Registry):
    """Registry specifically for component instances."""
    pass


# Service registry - for service instances  
class ServiceRegistry(Registry):
    """Registry specifically for service instances."""
    pass


__all__ = [
    "RegistryEntry",
    "Registry",
    "ComponentRegistry", 
    "ServiceRegistry",
    "RegistrySnapshot",
]
