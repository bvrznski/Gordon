# Core Registry Interface
# ======================

"""
Core registry interface - defines contracts for entity registration and discovery.

The registry is a central directory that allows components to:
- Register their presence and capabilities
- Discover other components
- Query by type, tag, or capability

ARCHITECTURAL PRINCIPLES:
- Registry is the single source of truth for component metadata
- Registration is explicit (components opt-in)
- Queries are efficient without deep introspection
"""

from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class EntityRecord:
    """
    A record in the registry about an entity.
    
    Args:
        entity_id: Unique identifier for the entity
        entity_type: The type/class of the entity
        registration_time_utc: When the entity registered
        version: Entity version string
        status: Current registration status
        metadata: Additional key-value data about the entity
        tags: List of tags for filtering
    """
    entity_id: str
    entity_type: str
    registration_time_utc: float = 0.0
    version: str = "1.0.0"
    status: str = "active"  # active, inactive, deprecated
    metadata: Dict[str, Any] = None  # type: ignore
    tags: List[str] = None  # type: ignore


class IRegistry(Protocol):
    """
    Interface for the entity registry.
    
    The registry provides:
        - Registration of entities with their capabilities
        - Query by entity ID, type, or tag
        - Listing all registered entities
        - Status updates for entities
    """
    
    @property
    def registry_id(self) -> str:
        """Get the unique ID of this registry."""
        ...
    
    async def register(
        self,
        record: EntityRecord,
    ) -> None:
        """
        Register an entity in the registry.
        
        Args:
            record: The entity record to register
            
        If the entity is already registered, this should update
        the existing record with new information.
        """
        ...
    
    async def deregister(
        self,
        entity_id: str,
    ) -> bool:
        """
        Remove an entity from the registry.
        
        Args:
            entity_id: The ID of the entity to remove
            
        Returns:
            True if the entity was registered and removed
        """
        ...
    
    async def lookup(self, entity_id: str) -> Optional[EntityRecord]:
        """Look up a registered entity by its ID."""
        ...
    
    async def find_by_type(
        self,
        entity_type: str,
        status_filter: Optional[str] = None,
    ) -> List[EntityRecord]:
        """
        Find entities by type.
        
        Args:
            entity_type: The entity type to match
            status_filter: Filter by status (None = all)
            
        Returns:
            List of matching entity records
        """
        ...
    
    async def find_by_tag(
        self,
        tag: str,
        status_filter: Optional[str] = None,
    ) -> List[EntityRecord]:
        """
        Find entities with a specific tag.
        
        Args:
            tag: The tag to match
            status_filter: Filter by status (None = all)
            
        Returns:
            List of matching entity records
        """
        ...
    
    async def find_all(
        self,
        status_filter: Optional[str] = None,
    ) -> List[EntityRecord]:
        """
        Get all registered entities.
        
        Args:
            status_filter: Filter by status (None = all)
            
        Returns:
            List of entity records
        """
        ...
    
    async def update_status(
        self,
        entity_id: str,
        new_status: str,
    ) -> bool:
        """Update the status of a registered entity."""
        ...


class IRegistryObserver(Protocol):
    """
    Interface for components that observe registry changes.
    """
    
    async def on_entity_registered(self, record: EntityRecord) -> None:
        """Called when a new entity is registered."""
        ...
    
    async def on_entity_deregistered(self, entity_id: str) -> None:
        """Called when an entity is removed from the registry."""
        ...
    
    async def on_entity_updated(
        self,
        record: EntityRecord,
        previous_version: Optional[str],
    ) -> None:
        """
        Called when a registered entity's information changes.
        
        Args:
            record: The updated entity record
            previous_version: The version before the update (if known)
        """
        ...


class RegistryError(Exception):
    """Raised when registry operations fail."""
    pass


class EntityNotFoundError(RegistryError):
    """Raised when looking up a non-existent entity."""
    
    def __init__(self, entity_id: str):
        super().__init__(f"Entity not found in registry: {entity_id}")
        self.entity_id = entity_id


__all__ = [
    "EntityRecord",
    "IRegistry",
    "IRegistryObserver",
    "RegistryError",
    "EntityNotFoundError",
]