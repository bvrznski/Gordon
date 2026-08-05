# Memory Runtime Infrastructure
# =============================

"""
Memory runtime for Gordon - storage, retrieval, and lifecycle management.

This module provides:

Memory Repository Contract
--------------------------
- MemoryRepository: Interface for memory record CRUD operations
- MemoryRetrievalInterface: Bounded retrieval with pagination support

Memory Record Contracts
-----------------------
- MemoryRecord: Canonical memory representation
- MemoryQueryFilters: Query parameter normalization
- RetrievalRequest: Standardized retrieval request
- RetrievalResult: Standardized result with pagination

Storage Implementation
----------------------
- InMemoryMemoryRepository: Thread-safe in-memory repository
- FilesystemMemoryRepository: Persistent file-based storage (placeholder)

Retrieval Infrastructure
------------------------
- MemoryRetriever: Executes normalized retrieval requests
- IndexCoordinator: Manages memory indices for efficient lookup

Memory Lifecycle
----------------
- MemoryExpirationManager: Automatic expiration handling
- MemoryTombstone: Logical deletion tracking

Security & Privacy
------------------
- MemoryAuthorization: Access control enforcement
- PrivacyFilter: Result privacy filtering

This layer provides infrastructure only. It does NOT own:
- Semantic meaning of memories
- Attention/salience decisions
- Cognitive relevance
- Reasoning policy
"""

from .repository import (
    MemoryRepository,
    InMemoryMemoryRepository,
)

from .contracts import (
    MemoryRecord,
    MemoryQueryFilters,
    RetrievalRequest,
    RetrievalResult,
)

from .retrieval import (
    MemoryRetriever,
    IndexCoordinator,
)

from .lifecycle import (
    MemoryExpirationManager,
    MemoryTombstone,
)

from .security import (
    MemoryAuthorization,
    PrivacyFilter,
)

__all__ = [
    # Repository
    "MemoryRepository",
    "InMemoryMemoryRepository",
    
    # Contracts
    "MemoryRecord",
    "MemoryQueryFilters",
    "RetrievalRequest",
    "RetrievalResult",
    
    # Retrieval
    "MemoryRetriever",
    "IndexCoordinator",
    
    # Lifecycle
    "MemoryExpirationManager",
    "MemoryTombstone",
    
    # Security
    "MemoryAuthorization",
    "PrivacyFilter",
]