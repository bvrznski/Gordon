# Memory Repository Implementation
# ================================

"""
Memory repository for canonical storage and retrieval of memory records.

This module provides:

Repository Contract:
- MemoryRepository: Interface for CRUD operations on memory records

Storage Implementations:
- InMemoryMemoryRepository: Thread-safe in-memory repository for testing

Principles:
- Records are immutable (updates create new versions)
- Single source of truth per runtime instance
- Bounded queries with pagination support
- No semantic interpretation - infrastructure only
"""

import threading
import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterable
from collections import defaultdict

from .contracts import (
    MemoryRecord,
    MemoryKind,
    MemoryLifecycleState,
    MemoryPrivacyClass,
    MemoryAccessScope,
    MemoryQueryFilters,
    RetrievalRequest,
    RetrievalResult,
)


# =============================================================================
# Repository Interface
# =============================================================================

class MemoryRepository:
    """
    Interface for memory record storage and retrieval.
    
    This interface provides canonical CRUD operations for memory records.
    
    Key Principles:
    - Records are immutable (updates create new versions with incremented version)
    - Bounded queries with pagination support
    - No semantic interpretation - purely infrastructure
    - Thread-safe where applicable
    
    Usage:
        repository = InMemoryMemoryRepository()
        
        # Store a record
        record = MemoryRecord(
            memory_id="mem-123",
            content={"text": "Hello world"},
            kind=MemoryKind.EPISODIC,
            content_hash="abc123...",
            owner_id="component-1"
        )
        await repository.save(record)
        
        # Retrieve by ID
        retrieved = await repository.get("mem-123")
    """
    
    async def save(self, record: MemoryRecord) -> str:
        """
        Save a memory record.
        
        Args:
            record: The memory record to store
            
        Returns:
            The memory_id of the stored record
            
        Raises:
            ValueError: If record is invalid
            RuntimeError: On storage failure
        """
        raise NotImplementedError
    
    async def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """
        Retrieve a memory record by ID.
        
        Args:
            memory_id: The unique identifier of the record
            
        Returns:
            The record if found, None otherwise
        """
        raise NotImplementedError
    
    async def exists(self, memory_id: str) -> bool:
        """
        Check if a memory record exists.
        
        Args:
            memory_id: The unique identifier to check
            
        Returns:
            True if the record exists, False otherwise
        """
        raise NotImplementedError
    
    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory record (logical deletion via lifecycle_state).
        
        Args:
            memory_id: The unique identifier of the record to delete
            
        Returns:
            True if deleted, False if not found
        """
        raise NotImplementedError
    
    async def query(
        self,
        filters: MemoryQueryFilters
    ) -> List[MemoryRecord]:
        """
        Query memory records with bounded results.
        
        Args:
            filters: Query filters including pagination limits
            
        Returns:
            List of matching records (bounded by limit)
        """
        raise NotImplementedError
    
    async def count(self, filters: Optional[MemoryQueryFilters] = None) -> int:
        """
        Count total matching records.
        
        Args:
            filters: Filters to apply (None = all records)
            
        Returns:
            Total count of matching records
        """
        raise NotImplementedError


# =============================================================================
# In-Memory Implementation
# =============================================================================

class InMemoryMemoryRepository(MemoryRepository):
    """
    Thread-safe in-memory memory repository for testing.
    
    This implementation provides:
    - In-memory storage with dictionary backing
    - Thread-safe operations using RLock
    - Indexes for efficient lookup by kind, owner, tags
    - Bounded query results with pagination
    
    IMPORTANT: This is NOT durable. Data is lost on process exit.
    Only use for testing and development environments.
    
    Usage:
        repo = InMemoryMemoryRepository()
        await repo.save(record)
        records = await repo.query(filters)
    """
    
    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        self._lock = threading.RLock()
        
        # Main storage: memory_id -> MemoryRecord
        self._records: Dict[str, MemoryRecord] = {}
        
        # Indexes for efficient lookup
        self._index_kind: Dict[MemoryKind, List[str]] = defaultdict(list)
        self._index_owner: Dict[str, List[str]] = defaultdict(list)
        self._index_tag: Dict[str, List[str]] = defaultdict(list)
        self._index_timestamp: List[tuple] = []  # (timestamp, memory_id) sorted
        
        # Version tracking for update validation
        self._versions: Dict[str, int] = {}
        
        # Statistics
        self._stats = {
            "save_calls": 0,
            "get_calls": 0,
            "query_calls": 0,
            "delete_calls": 0,
        }
    
    async def save(self, record: MemoryRecord) -> str:
        """
        Save a memory record.
        
        - Creates new record if ID not present
        - Creates new version if ID exists (version increment)
        - Updates indexes to reflect current state
        
        Args:
            record: The memory record to store
            
        Returns:
            The memory_id of the stored/updated record
            
        Raises:
            ValueError: If record has invalid state or missing required fields
        """
        with self._lock:
            # Validate record
            if not record.memory_id:
                raise ValueError("MemoryRecord must have a memory_id")
            
            if not record.owner_id:
                raise ValueError("MemoryRecord must have an owner_id")
            
            if not record.content_hash:
                raise ValueError("MemoryRecord must have a content_hash")
            
            memory_id = record.memory_id
            
            # Handle versioning for updates
            if memory_id in self._records:
                existing = self._records[memory_id]
                expected_version = record.version
                
                # If version provided, validate it matches current
                if expected_version is not None and expected_version > 1:
                    current_version = self._versions.get(memory_id, 0)
                    if expected_version != current_version + 1:
                        raise ValueError(
                            f"Version conflict: expected {current_version + 1}, got {expected_version}"
                        )
                
                # Increment version for update
                new_version = existing.version + 1
                
                # Create updated record with new version and timestamp
                record = MemoryRecord(
                    memory_id=memory_id,
                    kind=record.kind,
                    content_hash=record.content_hash,
                    owner_id=record.owner_id,
                    content=record.content,
                    content_type=record.content_type,
                    created_at=existing.created_at,  # Preserve creation time
                    updated_at=time.time(),  # Update timestamp
                    version=new_version,
                    lifecycle_state=record.lifecycle_state,
                    privacy_class=record.privacy_class,
                    access_scope=record.access_scope,
                    tags=record.tags,
                    source_event_id=record.source_event_id,
                    expires_at=record.expires_at,
                    provenance_id=record.provenance_id,
                )
            else:
                # New record, version 1
                self._versions[memory_id] = 0
            
            # Store the record
            self._records[memory_id] = record
            self._versions[memory_id] = record.version
            
            # Update indexes
            self._update_indexes(memory_id, record)
            
            self._stats["save_calls"] += 1
            
            return memory_id
    
    async def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """
        Retrieve a memory record by ID.
        
        Args:
            memory_id: The unique identifier of the record
            
        Returns:
            The record if found and not deleted, None otherwise
        """
        with self._lock:
            record = self._records.get(memory_id)
            
            if record is None:
                return None
            
            # Return None for deleted records
            if record.lifecycle_state == MemoryLifecycleState.DELETED:
                return None
            
            self._stats["get_calls"] += 1
            return record
    
    async def exists(self, memory_id: str) -> bool:
        """
        Check if a memory record exists (and is not deleted).
        
        Args:
            memory_id: The unique identifier to check
            
        Returns:
            True if the record exists and is active, False otherwise
        """
        with self._lock:
            record = self._records.get(memory_id)
            
            if record is None:
                return False
            
            # Consider deleted records as non-existent for retrieval purposes
            return record.lifecycle_state != MemoryLifecycleState.DELETED
    
    async def delete(self, memory_id: str) -> bool:
        """
        Perform logical deletion by setting lifecycle_state to DELETED.
        
        Args:
            memory_id: The unique identifier of the record to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if memory_id not in self._records:
                return False
            
            record = self._records[memory_id]
            
            # Create updated record with DELETED state
            new_record = MemoryRecord(
                memory_id=memory_id,
                kind=record.kind,
                content_hash=record.content_hash,
                owner_id=record.owner_id,
                content=record.content,
                content_type=record.content_type,
                created_at=record.created_at,
                updated_at=time.time(),
                version=record.version + 1,
                lifecycle_state=MemoryLifecycleState.DELETED,
                privacy_class=record.privacy_class,
                access_scope=record.access_scope,
                tags=record.tags,
                source_event_id=record.source_event_id,
                expires_at=record.expires_at,
                provenance_id=record.provenance_id,
            )
            
            self._records[memory_id] = new_record
            self._versions[memory_id] = new_record.version
            
            # Update indexes
            self._update_indexes(memory_id, new_record)
            
            self._stats["delete_calls"] += 1
            return True
    
    async def query(self, filters: MemoryQueryFilters) -> List[MemoryRecord]:
        """
        Query memory records with bounded results.
        
        Implements:
        - Filtering by kind, owner, tags, timestamps
        - Pagination support (limit/offset)
        - Sorting by timestamp
        
        Args:
            filters: Query filters including pagination limits
            
        Returns:
            List of matching records (bounded by filters.limit)
        """
        with self._lock:
            # Get all candidate IDs (filtered or all)
            candidate_ids = self._get_candidate_ids(filters)
            
            # Apply additional filters
            filtered_records = []
            for memory_id in candidate_ids:
                record = self._records.get(memory_id)
                
                if record is None:
                    continue
                
                # Skip deleted records
                if record.lifecycle_state == MemoryLifecycleState.DELETED:
                    continue
                
                # Apply kind filter
                if filters.kinds and record.kind not in filters.kinds:
                    continue
                
                # Apply owner filter
                if filters.owner_ids and record.owner_id not in filters.owner_ids:
                    continue
                
                # Apply timestamp filter
                if filters.from_timestamp and record.created_at < filters.from_timestamp:
                    continue
                
                if filters.to_timestamp and record.created_at >= filters.to_timestamp:
                    continue
                
                filtered_records.append(record)
            
            # Sort records
            reverse = not filters.sort_ascending
            if filters.sort_by == "created_at":
                filtered_records.sort(
                    key=lambda r: r.created_at,
                    reverse=reverse
                )
            elif filters.sort_by == "updated_at":
                filtered_records.sort(
                    key=lambda r: r.updated_at,
                    reverse=reverse
                )
            
            # Apply pagination
            total_count = len(filtered_records)
            start = filters.offset
            end = filters.offset + min(filters.limit, total_count - start) if filters.limit else None
            
            result_records = filtered_records[start:end]
            
            # Calculate next offset for pagination
            has_more = end is not None and end < total_count
            next_offset = end if has_more else None
            
            self._stats["query_calls"] += 1
            
            return result_records
    
    async def count(self, filters: Optional[MemoryQueryFilters] = None) -> int:
        """
        Count total matching records.
        
        Args:
            filters: Filters to apply (None = all active records)
            
        Returns:
            Total count of matching records
        """
        query_filters = filters or MemoryQueryFilters()
        
        with self._lock:
            candidate_ids = self._get_candidate_ids(query_filters)
            count = 0
            
            for memory_id in candidate_ids:
                record = self._records.get(memory_id)
                
                if record is None:
                    continue
                
                # Skip deleted records
                if record.lifecycle_state == MemoryLifecycleState.DELETED:
                    continue
                
                # Apply kind filter
                if query_filters.kinds and record.kind not in query_filters.kinds:
                    continue
                
                # Apply owner filter
                if query_filters.owner_ids and record.owner_id not in query_filters.owner_ids:
                    continue
                
                count += 1
            
            return count
    
    def _get_candidate_ids(self, filters: MemoryQueryFilters) -> List[str]:
        """
        Get candidate memory IDs based on available indexes.
        
        Uses indexes when possible, falls back to all records otherwise.
        """
        # Start with most specific filter or fallback
        if filters.owner_ids and len(filters.owner_ids) == 1:
            owner_id = filters.owner_ids[0]
            return list(self._index_owner.get(owner_id, []))
        
        if filters.kinds and len(filters.kinds) == 1:
            kind = filters.kinds[0]
            return list(self._index_kind.get(kind, []))
        
        # Fall back to all record IDs
        return list(self._records.keys())
    
    def _update_indexes(self, memory_id: str, record: MemoryRecord) -> None:
        """Update all indexes for a record."""
        # Clear old index entries (will re-add)
        self._index_kind[record.kind] = [
            mid for mid in self._index_kind[record.kind] if mid != memory_id
        ]
        self._index_owner[record.owner_id] = [
            mid for mid in self._index_owner[record.owner_id] if mid != memory_id
        ]
        
        for tag in record.tags:
            self._index_tag[tag] = [
                mid for mid in self._index_tag[tag] if mid != memory_id
            ]
        
        # Re-add to indexes
        self._index_kind[record.kind].append(memory_id)
        self._index_owner[record.owner_id].append(memory_id)
        
        for tag in record.tags:
            self._index_tag[tag].append(memory_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        with self._lock:
            return {
                "total_records": len(self._records),
                "active_records": sum(
                    1 for r in self._records.values()
                    if r.lifecycle_state != MemoryLifecycleState.DELETED
                ),
                **self._stats,
                "indexes": {
                    "kinds": {k.value: len(v) for k, v in self._index_kind.items()},
                    "owners": {k: len(v) for k, v in self._index_owner.items()},
                    "tags": {k: len(v) for k, v in self._index_tag.items()},
                },
            }


__all__ = [
    "MemoryRepository",
    "InMemoryMemoryRepository",
]