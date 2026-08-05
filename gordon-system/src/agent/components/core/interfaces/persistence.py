# Core Persistence Interface
# ===========================

"""
Core persistence interface - defines contracts for storage backends.

This interface allows multiple persistence implementations (memory, file,
database) while providing a consistent way to store and retrieve data.

ARCHITECTURAL PRINCIPLES:
- Storage is backend-agnostic
- Data can be persisted, retrieved, and deleted
- Transactions support optional
- Query syntax is backend-independent
"""

from typing import Protocol, Optional, List, Dict, Any, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum


T = TypeVar("T")


@dataclass(frozen=True)
class RecordId:
    """Unique identifier for a persistent record."""
    value: str
    
    @classmethod
    def generate(cls) -> "RecordId":
        """Generate a new random ID."""
        import uuid
        return cls(value=f"rec_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def from_string(cls, s: str) -> "RecordId":
        """Create an ID from a string."""
        return cls(value=s)


class PersistenceOperation(Enum):
    """Types of persistence operations."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"


@dataclass(frozen=True)
class PersistenceResult:
    """
    Result of a persistence operation.
    
    Args:
        success: Whether the operation succeeded
        record_id: ID of the affected record (if applicable)
        version: Record version after operation (if available)
        error_message: Error details if failed
    """
    success: bool
    record_id: Optional[str] = None
    version: Optional[int] = None
    error_message: Optional[str] = None


class IPersistenceStore(Protocol):
    """
    Interface for a persistence store.
    
    A store is responsible for:
        - Storing records with unique IDs
        - Retrieving records by ID or query
        - Updating and deleting records
        - Managing record versions
    
    Stores are backend-agnostic - the same interface works for
    in-memory, file, database, etc. implementations.
    """
    
    @property
    def store_name(self) -> str:
        """Get the name of this persistence store."""
        ...
    
    async def open(self) -> None:
        """Open the store connection/resource."""
        ...
    
    async def close(self) -> None:
        """Close the store connection/resource."""
        ...
    
    async def save(
        self,
        record_id: RecordId,
        data: Dict[str, Any],
        version: Optional[int] = None,
    ) -> PersistenceResult:
        """
        Save a record to the store.
        
        Args:
            record_id: Unique identifier for this record
            data: The record data (JSON-serializable)
            version: Expected current version (for optimistic locking)
            
        Returns:
            Result with success status and new version
        """
        ...
    
    async def load(self, record_id: RecordId) -> Optional[Dict[str, Any]]:
        """
        Load a record from the store.
        
        Args:
            record_id: The ID of the record to load
            
        Returns:
            Record data or None if not found
        """
        ...
    
    async def delete(self, record_id: RecordId) -> PersistenceResult:
        """
        Delete a record from the store.
        
        Args:
            record_id: The ID of the record to delete
            
        Returns:
            Result with success status
        """
        ...
    
    async def query(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Query records matching criteria.
        
        Args:
            filters: Key-value pairs to match
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of matching records
        """
        ...
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records matching criteria.
        
        Args:
            filters: Filters to apply (None = count all)
            
        Returns:
            Number of matching records
        """
        ...


class IPersistenceRepository(Protocol):
    """
    Interface for a typed persistence repository.
    
    Repositories provide type-safe access to persisted data,
    handling conversion between domain objects and raw storage.
    
    Args:
        T: The type of entity this repository manages
    """
    
    @property
    def entity_type(self) -> str:
        """Get the name of the entity type managed by this repository."""
        ...
    
    async def save(self, entity: Any) -> PersistenceResult:
        """
        Save an entity to the underlying store.
        
        Args:
            entity: The domain entity to persist
            
        Returns:
            Result with success status and version
        """
        ...
    
    async def load(self, record_id: RecordId) -> Optional[Any]:
        """
        Load an entity from the underlying store.
        
        Args:
            record_id: The ID of the entity to load
            
        Returns:
            Domain entity or None if not found
        """
        ...
    
    async def delete(self, record_id: RecordId) -> PersistenceResult:
        """
        Delete an entity from the underlying store.
        
        Args:
            record_id: The ID of the entity to delete
            
        Returns:
            Result with success status
        """
        ...
    
    async def find_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Any]:
        """
        Load all entities from the store.
        
        Args:
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of domain entities
        """
        ...
    
    async def find_by_field(
        self,
        field_name: str,
        field_value: Any,
        limit: Optional[int] = None,
    ) -> List[Any]:
        """
        Find entities by a specific field value.
        
        Args:
            field_name: Name of the field to search
            field_value: Value to match
            limit: Maximum number of results
            
        Returns:
            List of matching domain entities
        """
        ...


class PersistenceError(Exception):
    """Raised when persistence operations fail."""
    pass


class RecordNotFoundError(PersistenceError):
    """Raised when a record is not found."""
    
    def __init__(self, record_id: str):
        super().__init__(f"Record not found: {record_id}")
        self.record_id = record_id


class OptimisticLockError(PersistenceError):
    """Raised when version check fails during update."""
    
    def __init__(self, record_id: str, expected_version: int, actual_version: int):
        super().__init__(
            f"Version conflict for {record_id}: "
            f"expected {expected_version}, got {actual_version}"
        )
        self.record_id = record_id
        self.expected_version = expected_version
        self.actual_version = actual_version


__all__ = [
    "RecordId",
    "PersistenceOperation",
    "PersistenceResult",
    "IPersistenceStore",
    "IPersistenceRepository",
    "PersistenceError",
    "RecordNotFoundError",
    "OptimisticLockError",
]