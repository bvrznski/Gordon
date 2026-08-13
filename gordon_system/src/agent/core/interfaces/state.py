# Core State Interface
# ====================

"""
Core state interface - defines contracts for state stores.

This interface allows different state storage mechanisms (memory, file,
database, distributed) while providing a consistent way to read and write state.

ARCHITECTURAL PRINCIPLES:
- State is backend-agnostic
- State can be read, written, and deleted
- Transactions support optional
- Versioning for concurrent access
"""

from typing import Protocol, Optional, List, Dict, Any, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum

T = TypeVar("T")


@dataclass(frozen=True)
class StateId:
    """Unique identifier for a state entry."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "StateId":
        """Generate a new random ID."""
        import uuid
        return cls(value=f"state_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def from_string(cls, s: str) -> "StateId":
        """Create an ID from a string."""
        return cls(value=s)


@dataclass(frozen=True)
class StateVersion:
    """
    Version information for state entries.
    
    Args:
        version_number: Monotonically increasing version counter
        timestamp_utc: When this version was created
        actor_id: Who made the change (optional, for audit)
    """
    
    version_number: int
    timestamp_utc: float = 0.0
    actor_id: Optional[str] = None


@dataclass(frozen=True)
class StateEntry(Generic[T]):
    """
    A state entry with its metadata.
    
    Args:
        key: Unique key for this state entry (dot-separated path)
        value: The actual state value (any type)
        version: Version information
        created_at_utc: When this entry was first created
        updated_at_utc: When this entry was last modified
        tags: Tags for categorization and lookup
    """
    
    key: str
    value: T
    version: StateVersion
    created_at_utc: float = 0.0
    updated_at_utc: float = 0.0
    tags: List[str] = None  # type: ignore


class IStateStore(Protocol):
    """
    Interface for a state store.
    
    A store is responsible for:
        - Storing state entries with unique keys
        - Retrieving state by key or query
        - Updating and deleting state
        - Managing versions and history
    
    Stores are backend-agnostic - the same interface works for
    in-memory, file, database, distributed storage, etc.
    """
    
    @property
    def store_name(self) -> str:
        """Get the name of this state store."""
        ...
    
    async def open(self) -> None:
        """Open the store connection/resource."""
        ...
    
    async def close(self) -> None:
        """Close the store connection/resource."""
        ...
    
    async def get(
        self,
        key: str,
        version: Optional[int] = None,
    ) -> Optional[StateEntry[Any]]:
        """
        Get a state entry by key.
        
        Args:
            key: The state key (dot-separated path)
            version: Specific version to retrieve (None = latest)
            
        Returns:
            State entry or None if not found
        """
        ...
    
    async def set(
        self,
        key: str,
        value: Any,
        expected_version: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> StateEntry[Any]:
        """
        Set a state entry.
        
        Args:
            key: The state key (dot-separated path)
            value: The value to store
            expected_version: Version for optimistic locking (None = allow any)
            tags: Tags to attach to this entry
            
        Returns:
            The created/updated state entry with its version
            
        Raises:
            OptimisticLockError: If expected_version doesn't match current
        """
        ...
    
    async def delete(
        self,
        key: str,
    ) -> bool:
        """
        Delete a state entry.
        
        Args:
            key: The state key to delete
            
        Returns:
            True if deleted, False if not found
        """
        ...
    
    async def query(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[StateEntry[Any]]:
        """
        Query state entries matching criteria.
        
        Args:
            filters: Key-value pairs to match
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of matching state entries
        """
        ...
    
    async def exists(self, key: str) -> bool:
        """Check if a state entry exists."""
        ...
    
    async def get_version(self, key: str) -> Optional[StateVersion]:
        """Get the current version of a state entry."""
        ...
    
    async def increment_counter(
        self,
        key: str,
        amount: int = 1,
    ) -> int:
        """
        Atomically increment a counter state.
        
        Args:
            key: The state key
            amount: Amount to increment by
            
        Returns:
            New counter value after increment
        """
        ...
    
    async def get_all(self) -> Dict[str, StateEntry[Any]]:
        """Get all state entries."""
        ...


class IStateRepository(Protocol):
    """
    Interface for a typed state repository.
    
    Repositories provide type-safe access to state,
    handling conversion between domain objects and raw storage.
    """
    
    @property
    def entity_type(self) -> str:
        """Get the name of the entity type managed by this repository."""
        ...
    
    async def save(self, key: str, entity: Any) -> StateEntry[Any]:
        """
        Save an entity to state.
        
        Args:
            key: The state key
            entity: The domain entity to persist
            
        Returns:
            State entry with version info
        """
        ...
    
    async def load(self, key: str) -> Optional[Any]:
        """
        Load an entity from state.
        
        Args:
            key: The state key
            
        Returns:
            Domain entity or None if not found
        """
        ...
    
    async def delete(self, key: str) -> bool:
        """
        Delete an entity from state.
        
        Args:
            key: The state key
            
        Returns:
            True if deleted
        """
        ...


class StateError(Exception):
    """Raised when state operations fail."""
    pass


class StateNotFoundError(StateError):
    """Raised when a state entry is not found."""
    
    def __init__(self, key: str):
        super().__init__(f"State not found: {key}")
        self.key = key


class OptimisticLockError(StateError):
    """Raised when version check fails during update."""
    
    def __init__(self, key: str, expected_version: int, actual_version: int):
        super().__init__(
            f"Version conflict for {key}: "
            f"expected {expected_version}, got {actual_version}"
        )
        self.key = key
        self.expected_version = expected_version
        self.actual_version = actual_version


__all__ = [
    "StateId",
    "StateVersion",
    "StateEntry",
    "IStateStore",
    "IStateRepository",
    "StateError",
    "StateNotFoundError",
    "OptimisticLockError",
]