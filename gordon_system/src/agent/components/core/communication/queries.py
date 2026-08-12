# Core Query Contracts
# ====================

"""
Query contracts for information retrieval requests.

Queries represent:
- Informational requests that should not mutate domain state
- May have multiple handlers (each returns partial results)
- Result limits and pagination support
- Consistency requirements where relevant

Query semantics:
- Queries request information, not state changes
- Operational metrics and caches may change (not considered mutation)
- Do not use events as queries
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Protocol
from enum import Enum
import time


class QueryConsistency(Enum):
    """Query consistency requirements."""
    EVENTUAL = "eventual"      # May return stale data
    CONSISTENT = "consistent"  # Must be consistent with current state
    STRONG = "strong"          # Strong consistency, may be slower


@dataclass(frozen=True)
class QueryId:
    """Unique identifier for a query."""
    value: str
    
    @classmethod
    def generate(cls) -> "QueryId":
        import uuid
        return cls(value=f"qry_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class QueryMetadata:
    """Immutable metadata for queries."""
    query_type: str  # e.g., "state.get", "metrics.summarize"
    
    source_id: Optional[str] = None
    runtime_id: Optional[str] = None
    
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    priority: int = 0
    deadline_utc: Optional[float] = None
    
    consistency_requirement: QueryConsistency = QueryConsistency.EVENTUAL
    result_limit: Optional[int] = None
    pagination_token: Optional[str] = None
    
    security_context: Dict[str, Any] = field(default_factory=dict)
    
    def with_correlation(self, corr_id: str) -> "QueryMetadata":
        return QueryMetadata(
            query_type=self.query_type,
            source_id=self.source_id,
            runtime_id=self.runtime_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            correlation_id=corr_id,
            causation_id=self.causation_id,
            priority=self.priority,
            deadline_utc=self.deadline_utc,
            consistency_requirement=self.consistency_requirement,
            result_limit=self.result_limit,
            pagination_token=self.pagination_token,
            security_context=dict(self.security_context),
        )


@dataclass(frozen=True)
class Query:
    """
    Base class for query contracts.
    
    Queries request information without intentionally mutating domain state.
    They may return cached or computed data.
    
    Invariants:
        - Do not mutate semantic state (operational metrics are OK to update)
        - May have multiple handlers returning partial results
        - Result limits prevent unbounded responses
    """
    
    query_id: QueryId
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: QueryMetadata = field(default_factory=QueryMetadata)
    
    @classmethod
    def create(
        cls,
        query_type: str,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        priority: int = 0,
        deadline_utc: Optional[float] = None,
        consistency: QueryConsistency = QueryConsistency.EVENTUAL,
        result_limit: Optional[int] = None,
    ) -> "Query":
        """Create a new query."""
        metadata = QueryMetadata(
            query_type=query_type,
            correlation_id=correlation_id,
            causation_id=causation_id,
            priority=priority,
            deadline_utc=deadline_utc,
            consistency_requirement=consistency,
            result_limit=result_limit,
        )
        return cls(
            query_id=QueryId.generate(),
            payload=dict(payload or {}),
            metadata=metadata,
        )


class QueryHandler(Protocol):
    """Protocol for query handlers."""
    
    async def __call__(self, query: Query) -> "QueryResult":
        """Handle a query and return result."""
        ...


@dataclass(frozen=True)
class QueryResult:
    """
    Result of a query execution.
    
    Queries may return partial results from multiple handlers. The final
    result aggregates all responses.
    """
    
    query_id: QueryId
    
    success: bool
    total_results: int = 0  # Total available, not just returned
    
    # Pagination info
    next_pagination_token: Optional[str] = None
    has_more: bool = False
    
    result_data: Dict[str, Any] = field(default_factory=dict)
    partial_results: List[Dict[str, Any]] = field(default_factory=list)
    
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Execution context
    handler_id: Optional[str] = None
    execution_time_ms: float = 0.0
    
    @classmethod
    def success(
        cls,
        query_id: QueryId,
        result_data: Dict[str, Any],
        total_results: int = 1,
        partial_results: Optional[List[Dict[str, Any]]] = None,
        handler_id: Optional[str] = None,
        execution_time_ms: float = 0.0,
    ) -> "QueryResult":
        return cls(
            query_id=query_id,
            success=True,
            total_results=total_results,
            result_data=dict(result_data),
            partial_results=list(partial_results or []),
            handler_id=handler_id,
            execution_time_ms=execution_time_ms,
        )
    
    @classmethod
    def failure(
        cls,
        query_id: QueryId,
        error_message: str,
        error_type: Optional[str] = None,
    ) -> "QueryResult":
        return cls(
            query_id=query_id,
            success=False,
            error_message=error_message,
            error_type=error_type,
        )
    
    @classmethod
    def timeout(cls, query_id: QueryId) -> "QueryResult":
        return cls(
            query_id=query_id,
            success=False,
            error_message="Query execution timed out",
        )


class QueryHandlerRegistry:
    """
    Registry for query handlers.
    
    Queries may have multiple handlers - each returns partial results
    that are aggregated by the caller.
    """
    
    def __init__(self):
        self._lock = None
        self._handlers: Dict[str, List[QueryHandler]] = {}
    
    def _get_lock(self):
        import threading
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    def register(
        self,
        query_type: str,
        handler: QueryHandler,
    ) -> bool:
        """
        Register a handler for a query type.
        
        Multiple handlers can be registered per query type. All will be
        invoked and their results aggregated.
        
        Args:
            query_type: The query type to handle
            handler: Async callable that processes the query
            
        Returns:
            True if registration succeeded
        """
        lock = self._get_lock()
        with lock:
            if query_type not in self._handlers:
                self._handlers[query_type] = []
            self._handlers[query_type].append(handler)
            return True
    
    def unregister(
        self,
        query_type: str,
        handler: QueryHandler,
    ) -> bool:
        """Remove a specific handler from a query type."""
        lock = self._get_lock()
        with lock:
            if query_type not in self._handlers:
                return False
            try:
                self._handlers[query_type].remove(handler)
                if not self._handlers[query_type]:
                    del self._handlers[query_type]
                return True
            except ValueError:
                return False
    
    def get_handlers(self, query_type: str) -> List[QueryHandler]:
        """Get all handlers for a query type."""
        lock = self._get_lock()
        with lock:
            return list(self._handlers.get(query_type, []))
    
    def has_handlers(self, query_type: str) -> bool:
        """Check if any handlers are registered for this query type."""
        return len(self.get_handlers(query_type)) > 0
    
    def get_all_handlers(self) -> Dict[str, List[QueryHandler]]:
        """Get all registered handlers by query type."""
        lock = self._get_lock()
        with lock:
            return {k: list(v) for k, v in self._handlers.items()}


# =============================================================================
# BUILT-IN QUERY TYPES (canonical examples)
# =============================================================================

@dataclass(frozen=True)
class GetStateQuery(Query):
    """Request current state from a component."""
    
    scope: str = "runtime"
    consistency: QueryConsistency = QueryConsistency.EVENTUAL


@dataclass(frozen=True)
class GetMetricsQuery(Query):
    """Request metrics/monitoring data."""
    
    metric_names: List[str] = field(default_factory=list)
    time_range_seconds: int = 60
    aggregate: str = "latest"  # latest, avg, min, max


@dataclass(frozen=True)
class ListComponentsQuery(Query):
    """Request list of available components."""
    
    component_type: Optional[str] = None  # Filter by type


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Types
    "QueryConsistency",
    
    # Identities
    "QueryId",
    
    # Metadata
    "QueryMetadata",
    
    # Contracts
    "Query",
    "QueryHandler",
    
    # Results
    "QueryResult",
    
    # Registry
    "QueryHandlerRegistry",
    
    # Built-in queries
    "GetStateQuery",
    "GetMetricsQuery",
    "ListComponentsQuery",
]