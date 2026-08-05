# Storage Backends
# ================

"""
Storage backend protocols and implementations.

This module provides:
- StorageBackendProtocol: Interface for persistence storage
- InMemoryBackend: Memory-based storage (for testing)
- FilesystemBackend: Local filesystem storage

Key principle: Backends are adapters - they do not own persistence policy.
Persistence authority is separate from storage location.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterable, BinaryIO
from enum import Enum, auto
import uuid
import time


# =============================================================================
# Backend Capability Types
# =============================================================================

class BackendFeature(Enum):
    """Features a backend may support."""
    
    ATOMIC_WRITE = "atomic_write"
    TRANSACTION = "transaction"
    CONTENT_ADDRESSING = "content_addressing"
    CHECKSUMS = "checksums"
    COMPRESSION = "compression"
    ENCRYPTION = "encryption"
    LISTING = "listing"
    DELETION = "deletion"


# =============================================================================
# Backend Capabilities
# =============================================================================

@dataclass(frozen=True)
class BackendCapabilities:
    """Set of capabilities supported by a backend."""
    
    atomic_write: bool = False
    transaction: bool = False
    content_addressing: bool = True  # Can use content hash as address
    checksums: bool = True
    compression: bool = False
    encryption: bool = False
    
    listing: bool = True
    deletion: bool = True
    
    max_object_size_bytes: int = 10_000_000  # 10MB default
    max_total_storage_bytes: Optional[int] = None


# =============================================================================
# Backend Request Types
# =============================================================================

@dataclass(frozen=True)
class WriteRequest:
    """A write request to storage."""
    
    key: str
    data: bytes
    checksum: Optional[str] = None  # Client-provided checksum
    compression: Optional[str] = None
    encryption_key_id: Optional[str] = None


@dataclass(frozen=True)
class ReadRequest:
    """A read request from storage."""
    
    key_or_id: str
    expected_checksum: Optional[str] = None


# =============================================================================
# Backend Result Types
# =============================================================================

@dataclass(frozen=True)
class WriteResult:
    """Result of a write operation."""
    
    success: bool
    object_id: str  # Content address or generated ID
    checksum: str
    timestamp: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class ReadResult:
    """Result of a read operation."""
    
    success: bool
    data: Optional[bytes] = None
    actual_checksum: Optional[str] = None
    timestamp: float = field(default_factory=time.monotonic)


# =============================================================================
# Storage Backend Protocol
# =============================================================================

class StorageBackendProtocol(ABC):
    """
    Interface for storage backends.
    
    PersistenceManager uses this interface - it does not implement storage
    directly. Backends are adapters that provide storage capabilities.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this backend."""
        pass
    
    @abstractmethod
    def capabilities(self) -> BackendCapabilities:
        """Return backend capabilities."""
        pass
    
    @abstractmethod
    async def write(
        self,
        key: str,
        data: bytes,
        checksum: Optional[str] = None
    ) -> WriteResult:
        """
        Write data to storage.
        
        Args:
            key: Storage key (may be ignored for content-addressed backends)
            data: Data to write
            checksum: Client-provided checksum for validation
            
        Returns:
            WriteResult with object ID and computed checksum
        """
        pass
    
    @abstractmethod
    async def read(
        self,
        key_or_id: str,
        expected_checksum: Optional[str] = None
    ) -> ReadResult:
        """
        Read data from storage.
        
        Args:
            key_or_id: Key or content address
            expected_checksum: If provided, verify against it
            
        Returns:
            ReadResult with data (or error info)
        """
        pass
    
    @abstractmethod
    async def exists(self, key_or_id: str) -> bool:
        """Check if object exists."""
        pass
    
    @abstractmethod
    async def delete(self, key_or_id: str) -> bool:
        """Delete an object. Returns True if deleted."""
        pass
    
    @abstractmethod
    async def list_keys(self, prefix: str = "") -> AsyncIterable[str]:
        """List keys matching a prefix."""
        pass
    
    @abstractmethod
    async def verify_checksum(
        self,
        data: bytes,
        expected_checksum: str
    ) -> bool:
        """Verify that data matches checksum."""
        pass


# =============================================================================
# In-Memory Backend (for testing)
# =============================================================================

class InMemoryBackend(StorageBackendProtocol):
    """
    Memory-based storage backend for testing and development.
    
    This backend stores all data in a Python dict. It does NOT persist
    across process restarts, so it should only be used for:
        - Unit tests
        - Development environments
        - Temporary caching
    
    NOT suitable for production persistence.
    """
    
    def __init__(self) -> None:
        self._data: Dict[str, bytes] = {}
        self._checksums: Dict[str, str] = {}
        self._object_ids: Dict[str, str] = {}  # key -> content address
        self._content_to_key: Dict[str, str] = {}  # content hash -> key
    
    @property
    def name(self) -> str:
        return "in_memory"
    
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            atomic_write=True,
            transaction=False,
            content_addressing=True,
            checksums=True,
            compression=False,
            encryption=False,
            listing=True,
            deletion=True,
        )
    
    async def write(
        self,
        key: str,
        data: bytes,
        checksum: Optional[str] = None
    ) -> WriteResult:
        """Write to memory."""
        import hashlib
        
        # Compute content address (SHA256 hash)
        computed_checksum = hashlib.sha256(data).hexdigest()
        
        # Use content address as object ID
        object_id = f"content://{computed_checksum[:16]}"
        
        # Store data
        self._data[key] = data
        self._checksums[key] = computed_checksum
        self._object_ids[key] = object_id
        
        # Track by content for deduplication
        if computed_checksum not in self._content_to_key:
            self._content_to_key[computed_checksum] = key
        
        return WriteResult(
            success=True,
            object_id=object_id,
            checksum=computed_checksum,
        )
    
    async def read(
        self,
        key_or_id: str,
        expected_checksum: Optional[str] = None
    ) -> ReadResult:
        """Read from memory."""
        import hashlib
        
        # Resolve key from content address if needed
        if key_or_id.startswith("content://"):
            hash_prefix = key_or_id[10:]  # Remove "content://"
            
            # Find matching key by checking stored checksums
            found_key = None
            for k, v in self._checksums.items():
                if v.startswith(hash_prefix):
                    found_key = k
                    break
            
            if not found_key:
                return ReadResult(success=False)
            
            key_or_id = found_key
        
        data = self._data.get(key_or_id)
        
        if data is None:
            return ReadResult(success=False)
        
        # Verify checksum
        actual_checksum = hashlib.sha256(data).hexdigest()
        
        if expected_checksum and expected_checksum != actual_checksum:
            return ReadResult(
                success=False,
                actual_checksum=actual_checksum,
            )
        
        return ReadResult(
            success=True,
            data=data,
            actual_checksum=actual_checksum,
        )
    
    async def exists(self, key_or_id: str) -> bool:
        """Check if object exists."""
        return key_or_id in self._data
    
    async def delete(self, key_or_id: str) -> bool:
        """Delete from memory."""
        if key_or_id in self._data:
            del self._data[key_or_id]
        
        # Also clean up checksums and mappings
        keys_to_remove = [
            k for k in list(self._checksums.keys())
            if k == key_or_id or self._object_ids.get(k) == key_or_id
        ]
        
        for k in keys_to_remove:
            del self._checksums[k]
            if k in self._object_ids:
                del self._object_ids[k]
        
        return len(keys_to_remove) > 0
    
    async def list_keys(self, prefix: str = "") -> AsyncIterable[str]:
        """List all keys."""
        for key in self._data.keys():
            if key.startswith(prefix):
                yield key
    
    async def verify_checksum(
        self,
        data: bytes,
        expected_checksum: str
    ) -> bool:
        """Verify checksum."""
        import hashlib
        computed = hashlib.sha256(data).hexdigest()
        return computed == expected_checksum


# =============================================================================
# Filesystem Backend (placeholder)
# =============================================================================

class FilesystemBackend(StorageBackendProtocol):
    """
    Local filesystem storage backend.
    
    This is a placeholder - would be implemented with actual file I/O
    for production use. Key considerations:
        - Atomic writes using temp files + rename
        - Directory structure for organization
        - File permissions and ownership
        - Disk space limits
    """
    
    def __init__(self, base_path: str) -> None:
        self._base_path = base_path
    
    @property
    def name(self) -> str:
        return "filesystem"
    
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            atomic_write=True,
            transaction=False,
            content_addressing=True,
            checksums=True,
            compression=False,
            encryption=False,
            listing=True,
            deletion=True,
            max_object_size_bytes=100_000_000,  # 100MB
        )
    
    async def write(
        self,
        key: str,
        data: bytes,
        checksum: Optional[str] = None
    ) -> WriteResult:
        """Write to filesystem (not implemented)."""
        raise NotImplementedError("FilesystemBackend not fully implemented")
    
    async def read(
        self,
        key_or_id: str,
        expected_checksum: Optional[str] = None
    ) -> ReadResult:
        """Read from filesystem (not implemented)."""
        raise NotImplementedError("FilesystemBackend not fully implemented")
    
    async def exists(self, key_or_id: str) -> bool:
        """Check if file exists (not implemented)."""
        raise NotImplementedError("FilesystemBackend not fully implemented")
    
    async def delete(self, key_or_id: str) -> bool:
        """Delete from filesystem (not implemented)."""
        raise NotImplementedError("FilesystemBackend not fully implemented")
    
    async def list_keys(self, prefix: str = "") -> AsyncIterable[str]:
        """List files (not implemented)."""
        raise NotImplementedError("FilesystemBackend not fully implemented")
    
    async def verify_checksum(
        self,
        data: bytes,
        expected_checksum: str
    ) -> bool:
        """Verify checksum."""
        import hashlib
        computed = hashlib.sha256(data).hexdigest()
        return computed == expected_checksum


__all__ = [
    # Backend types
    "BackendFeature",
    
    # Capabilities
    "BackendCapabilities",
    
    # Requests and results
    "WriteRequest",
    "ReadRequest",
    "WriteResult",
    "ReadResult",
    
    # Protocol
    "StorageBackendProtocol",
    
    # Implementations
    "InMemoryBackend",
    "FilesystemBackend",
]