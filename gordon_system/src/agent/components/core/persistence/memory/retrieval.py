# Retrieval Infrastructure
# ========================

"""
Retrieval infrastructure for normalized memory queries.

This module provides:

- MemoryRetriever: Executes normalized retrieval requests with bounded results
- IndexCoordinator: Manages indices for efficient lookup
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time

from .contracts import (
    MemoryRecord,
    MemoryKind,
    MemoryQueryFilters,
    RetrievalRequest,
    RetrievalResult,
)

from .repository import MemoryRepository


# =============================================================================
# Index Coordinator
# =============================================================================

class IndexCoordinator:
    """
    Manages memory indices for efficient lookup.
    
    Provides index management and consistency guarantees between canonical
    records and indices.
    
    Usage:
        coordinator = IndexCoordinator()
        
        # Register repository for index updates
        await coordinator.register_repository(repo)
        
        # Sync indices from canonical records
        await coordinator.sync_indices()
    """
    
    def __init__(self) -> None:
        """Initialize the index coordinator."""
        self._repositories: List[MemoryRepository] = []
        self._indices_synced: bool = False
    
    async def register_repository(self, repo: MemoryRepository) -> None:
        """Register a repository to coordinate indices with."""
        if repo not in self._repositories:
            self._repositories.append(repo)
    
    async def sync_indices(self) -> bool:
        """
        Synchronize indices from canonical records.
        
        Returns:
            True if synchronization completed, False otherwise
        """
        # For in-memory implementation, indices are kept consistent
        # during record operations. This method is a no-op for now.
        self._indices_synced = True
        return True
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about indices."""
        stats = {
            "indices_synced": self._indices_synced,
            "repositories_count": len(self._repositories),
        }
        return stats


# =============================================================================
# Memory Retriever
# =============================================================================

class MemoryRetriever:
    """
    Executes normalized retrieval requests against memory repository.
    
    Provides bounded query execution with pagination support and result
    normalization. Does NOT own semantic interpretation - only infrastructure.
    
    Key Responsibilities:
    - Execute retrieval requests with bounded limits
    - Apply filters and sorting
    - Handle pagination
    - Return normalized results
    
    NOT responsible for:
    - Semantic ranking (that's owned by cognitive layer)
    - Determining relevance
    - Modifying memory records
    
    Usage:
        repository = InMemoryMemoryRepository()
        retriever = MemoryRetriever(repository, index_coordinator)
        
        request = RetrievalRequest(
            request_id="req-123",
            limit=50,
            filters=MemoryQueryFilters(kinds=[MemoryKind.EPISODIC])
        )
        
        result = await retriever.execute(request)
    """
    
    def __init__(
        self,
        repository: MemoryRepository,
        index_coordinator: IndexCoordinator
    ) -> None:
        """
        Initialize the memory retriever.
        
        Args:
            repository: The memory repository to query
            index_coordinator: Coordinator for index management
        """
        self._repository = repository
        self._index_coordinator = index_coordinator
    
    async def execute(self, request: RetrievalRequest) -> RetrievalResult:
        """
        Execute a retrieval request.
        
        Args:
            request: The normalized retrieval request
            
        Returns:
            Normalized result with pagination and metadata
        """
        start_time = time.monotonic()
        
        try:
            # Build query filters from request
            filters = self._build_filters(request)
            
            # Execute query
            candidates = await self._repository.query(filters)
            
            # Calculate timing
            query_time_ms = (time.monotonic() - start_time) * 1000
            
            # Determine pagination metadata
            total_count = len(candidates)
            
            # If limit was specified and we hit it, there might be more
            has_more = False
            next_offset = None
            if request.limit and len(candidates) >= request.limit:
                has_more = True
                next_offset = filters.offset + len(candidates)
            
            # Build result with scores (recency-based for now)
            scores: Dict[str, float] = {}
            ranks: Dict[str, int] = {}
            
            for i, record in enumerate(candidates):
                rank = filters.offset + i + 1
                ranks[record.memory_id] = rank
                
                # Simple recency score (higher = more recent)
                if request.ranking_mode == "recency":
                    scores[record.memory_id] = record.updated_at
            
            return RetrievalResult(
                request_id=request.request_id,
                result_id=f"result-{request.request_id}",
                candidates=candidates,
                total_count=total_count,
                query_time_ms=query_time_ms,
                has_more=has_more,
                next_offset=next_offset,
                scores=scores,
                ranks=ranks,
            )
            
        except Exception as e:
            # Return partial failure result
            return RetrievalResult(
                request_id=request.request_id,
                result_id=f"result-{request.request_id}",
                candidates=[],
                total_count=0,
                query_time_ms=(time.monotonic() - start_time) * 1000,
                partial_results=True,
                warnings=[f"Query failed: {str(e)}"],
            )
    
    async def get_by_id(self, memory_id: str) -> Optional[MemoryRecord]:
        """
        Get a single record by ID.
        
        Args:
            memory_id: The unique identifier of the record
            
        Returns:
            The record if found and active, None otherwise
        """
        return await self._repository.get(memory_id)
    
    async def exists(self, memory_id: str) -> bool:
        """
        Check if a record exists (and is not deleted).
        
        Args:
            memory_id: The unique identifier to check
            
        Returns:
            True if the record exists and is active, False otherwise
        """
        return await self._repository.exists(memory_id)
    
    async def count(self, request: Optional[RetrievalRequest] = None) -> int:
        """
        Count total matching records.
        
        Args:
            request: Retrieval request with filters (optional)
            
        Returns:
            Total count of matching active records
        """
        filters = self._build_filters(request) if request else None
        return await self._repository.count(filters)
    
    def _build_filters(self, request: Optional[RetrievalRequest]) -> MemoryQueryFilters:
        """Build query filters from retrieval request."""
        default_limit = 100
        
        if request is None:
            return MemoryQueryFilters(limit=default_limit)
        
        # Use provided filters or create new ones
        filters = request.filters or MemoryQueryFilters()
        
        # Override with request parameters
        return MemoryQueryFilters(
            kinds=filters.kinds,
            owner_ids=filters.owner_ids,
            tags=filters.tags,
            tag_any=filters.tag_any,
            from_timestamp=filters.from_timestamp,
            to_timestamp=filters.to_timestamp,
            access_scope=filters.access_scope,
            privacy_classes=filters.privacy_classes,
            limit=request.limit if request.limit else filters.limit,
            offset=request.offset,
            sort_by="created_at",  # Default sorting
            sort_ascending=False,  # Most recent first by default
        )


__all__ = [
    "IndexCoordinator",
    "MemoryRetriever",
]