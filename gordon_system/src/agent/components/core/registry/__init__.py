# Core Registry Infrastructure
# ============================
"""
Core runtime entity registries.

Provides controlled registration and lookup for runtime entities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypeVar, Generic, Callable, Tuple
import threading
from enum import Enum
import time

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


# =============================================================================
# Runtime Registry (Phase 3.7+)
# =============================================================================

class EntityCategory(Enum):
    """
    Categories of runtime entities in the registry.
    
    Allows for organized lookup and lifecycle management.
    """
    COMPONENT = "component"
    SERVICE = "service"
    TASK = "task"
    CONTEXT = "context"
    RESOURCE = "resource"
    OBSERVABILITY = "observability"
    INTEGRITY = "integrity"


@dataclass(frozen=True)
class RuntimeRegistryEntry:
    """
    Enhanced registry entry with metadata.
    
    Provides additional context for runtime entities beyond basic key-value pairs.
    """
    
    entity_id: EntityId
    category: EntityCategory
    name: str
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.monotonic)
    
    @property
    def full_name(self) -> str:
        """Return fully qualified name with version."""
        return f"{self.name}@{self.version}"


@dataclass(frozen=True)
class RegistryMetadata:
    """
    Metadata about a registry operation.
    
    Used for tracing and diagnostics.
    """
    
    operation: str  # register, get, deregister, snapshot
    key: str
    timestamp: float = field(default_factory=time.monotonic)
    duration_ms: float = 0.0
    
    @property
    def is_read_operation(self) -> bool:
        """Check if this is a read-only operation."""
        return self.operation in ("get", "snapshot")


class RuntimeRegistry:
    """
    Production-grade registry for runtime entities.
    
    Provides:
    - Multi-category entity management
    - Immutable snapshots with versioning
    - Event notification for changes
    - Metadata tracking for diagnostics
    - Thread-safe operations
    
    Usage:
        registry = RuntimeRegistry()
        
        # Register entities by category
        registry.register(
            EntityId("service_a"),
            MyService(),
            category=EntityCategory.SERVICE,
            name="my_service"
        )
        
        # Get entity
        service = registry.get(EntityId("service_a"))
        
        # Create snapshot for determinism
        snapshot = registry.snapshot()
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        
        # Category-based registries
        self._registries: Dict[EntityCategory, Registry[Any]] = {
            category: Registry() for category in EntityCategory
        }
        
        # Global index by entity_id
        self._entity_index: Dict[str, Tuple[EntityCategory, str]] = {}  # id -> (category, key)
        
        # Metadata tracking
        self._metadata_history: List[RegistryMetadata] = []
    
    def _get_registry(self, category: EntityCategory) -> Registry[Any]:
        """Get the registry for a category."""
        return self._registries[category]
    
    def register(
        self,
        entity_id: EntityId,
        entity: T,
        category: EntityCategory,
        name: str,
        version: str = "1.0.0",
        key: Optional[str] = None
    ) -> bool:
        """
        Register an entity with metadata.
        
        Args:
            entity_id: Unique identifier for the entity
            entity: The entity instance to register
            category: Category of this entity
            name: Human-readable name
            version: Entity version
            key: Optional override key (defaults to entity_id)
            
        Returns:
            True if registered successfully
            
        Raises:
            RegistrationError: If entity already exists
        """
        with self._lock:
            actual_key = key or str(entity_id.value)
            registry = self._get_registry(category)
            
            # Register in category-specific registry
            registry.register(actual_key, entity)
            
            # Update global index
            self._entity_index[str(entity_id.value)] = (category, actual_key)
            
            # Record metadata for diagnostics
            metadata = RegistryMetadata(
                operation="register",
                key=actual_key
            )
            self._metadata_history.append(metadata)
            
            return True
    
    def get(self, entity_id: EntityId) -> Optional[Any]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: The entity's unique identifier
            
        Returns:
            The registered entity, or None if not found
        """
        with self._lock:
            key_info = self._entity_index.get(str(entity_id.value))
            
            if key_info is None:
                return None
            
            category, key = key_info
            registry = self._get_registry(category)
            
            metadata = RegistryMetadata(
                operation="get",
                key=key
            )
            self._metadata_history.append(metadata)
            
            return registry.get(key)
    
    def get_by_category(self, category: EntityCategory) -> Dict[str, Any]:
        """
        Get all entities in a specific category.
        
        Args:
            category: The category to query
            
        Returns:
            Dictionary of key -> entity for the category
        """
        with self._lock:
            return dict(self._get_registry(category).get_all())
    
    def deregister(self, entity_id: EntityId) -> Optional[Any]:
        """
        Remove an entity from the registry.
        
        Args:
            entity_id: The entity's unique identifier
            
        Returns:
            The removed entity, or None if not found
        """
        with self._lock:
            key_info = self._entity_index.get(str(entity_id.value))
            
            if key_info is None:
                return None
            
            category, key = key_info
            registry = self._get_registry(category)
            
            result = registry.deregister(key)
            
            # Remove from global index
            del self._entity_index[str(entity_id.value)]
            
            metadata = RegistryMetadata(
                operation="deregister",
                key=key
            )
            self._metadata_history.append(metadata)
            
            return result
    
    def snapshot(self) -> "RuntimeRegistrySnapshot":
        """
        Create an immutable snapshot of the registry state.
        
        All sub-registries are snapshotted atomically.
        """
        with self._lock:
            category_snapshots: Dict[str, RegistrySnapshot] = {}
            for category, registry in self._registries.items():
                category_snapshots[category.value] = registry.snapshot()
            
            metadata_snapshot = list(self._metadata_history)
            
            return RuntimeRegistrySnapshot(
                category_snapshots=category_snapshots,
                entity_index=dict(self._entity_index),
                metadata_history=metadata_snapshot
            )
    
    def find_by_name(self, name: str) -> List[Tuple[EntityId, Any]]:
        """
        Find entities by name (case-insensitive partial match).
        
        Args:
            name: Name or partial name to search for
            
        Returns:
            List of (entity_id, entity) tuples matching the name
        """
        results = []
        
        with self._lock:
            for category in EntityCategory:
                registry = self._get_registry(category)
                entries = registry.get_all()
                
                for key, entity in entries.items():
                    # Get metadata from entity if available
                    if hasattr(entity, 'name') and hasattr(entity, 'entity_id'):
                        if name.lower() in entity.name.lower():
                            results.append((entity.entity_id, entity))
        
        return results
    
    def clear(self) -> None:
        """Clear all registries."""
        with self._lock:
            for registry in self._registries.values():
                registry.clear()
            self._entity_index.clear()
    
    @property
    def size(self) -> int:
        """Return total number of registered entities across all categories."""
        with self._lock:
            return len(self._entity_index)
    
    @property
    def category_sizes(self) -> Dict[str, int]:
        """Return entity counts per category."""
        with self._lock:
            return {cat.value: reg.size for cat, reg in self._registries.items()}


@dataclass(frozen=True)
class RuntimeRegistrySnapshot:
    """
    Immutable snapshot of runtime registry state.
    
    Used for determinism and rollback capabilities.
    """
    
    category_snapshots: Dict[str, RegistrySnapshot]
    entity_index: Dict[str, Tuple[EntityCategory, str]]
    metadata_history: List[RegistryMetadata]
    
    def get(self, entity_id: EntityId) -> Optional[Any]:
        """Get an entity from the snapshot."""
        key_info = self.entity_index.get(str(entity_id.value))
        
        if key_info is None:
            return None
        
        category_str, key = key_info
        category_snap = self.category_snapshots.get(category_str)
        
        if category_snap is None:
            return None
        
        return category_snap.get(key)
    
    def get_category(self, category: EntityCategory) -> Dict[str, Any]:
        """Get all entities in a category from the snapshot."""
        snap = self.category_snapshots.get(category.value)
        if snap:
            return snap.entries
        return {}
    
    @property
    def total_entities(self) -> int:
        """Return total entity count across all categories."""
        return len(self.entity_index)


class RegistryObserver:
    """
    Observer interface for registry changes.
    
    Allows external systems to react to registry events.
    """
    
    async def on_register(self, entry: RuntimeRegistryEntry) -> None:
        """Called when an entity is registered."""
        pass
    
    async def on_deregister(self, entity_id: EntityId) -> None:
        """Called when an entity is deregistered."""
        pass
    
    async def on_snapshot(self, snapshot: RuntimeRegistrySnapshot) -> None:
        """Called when a snapshot is created."""
        pass


__all__ = [
    "RegistryEntry",
    "Registry",
    "ComponentRegistry", 
    "ServiceRegistry",
    "RegistrySnapshot",
    # Phase 3.7+ additions
    "EntityCategory",
    "RuntimeRegistryEntry",
    "RegistryMetadata",
    "RuntimeRegistry",
    "RuntimeRegistrySnapshot",
    "RegistryObserver",
]