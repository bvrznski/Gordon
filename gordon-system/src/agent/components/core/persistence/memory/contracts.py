# Memory Record Contracts
# =======================

"""
Memory record contracts for canonical representation and retrieval.

These contracts provide:
- Canonical memory record structure
- Query normalization interface
- Retrieval request/result types with bounded pagination
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import time


# =============================================================================
# Memory Record Types
# =============================================================================

class MemoryKind(Enum):
    """
    Categories of memory records.
    
    - EPISODIC: Specific events/observations with timestamp and context
    - SEMANTIC: General knowledge facts and concepts
    - PROCEDURAL: How-to instructions and skills
    - WORKING: Active, short-term cognitive state
    - CONTEXTUAL: Current situational awareness
    - PROSPETIVE: Future intentions and plans
    """
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    CONTEXTUAL = "contextual"
    PROSPECTIVE = "prospective"


class MemoryAccessScope(Enum):
    """Accessibility scope for memory records."""
    PRIVATE = "private"       # Owner only
    SHARED = "shared"         # Shared with specific parties
    PUBLIC = "public"         # Any system component


@dataclass(frozen=True)
class MemoryRecord:
    """
    Canonical memory record - the source of truth.
    
    All fields are immutable. Updates create new records with version tracking.
    
    Args:
        memory_id: Unique identifier for this memory
        kind: Category/type of memory (episodic, semantic, etc.)
        content_hash: Integrity hash of the content
        owner_id: ID of the owner (component/system identity)
        
        # Content
        content: The actual memory payload
        content_type: Type of content (text, structured, etc.)
        
        # Metadata
        created_at: When this record was first created
        updated_at: Last modification time
        version: Record version number (starts at 1)
        
        # Operational
        lifecycle_state: Active, expired, deleted, archived
        privacy_class: Open, confidential, restricted, private
        access_scope: Who can access this memory
        
        # Indexing & Retrieval
        tags: Semantic and operational tags for filtering
        source_event_id: Optional reference to original event/observation
        
        # Lifecycle
        expires_at: When this memory should expire (optional)
        
        # Provenance
        provenance_id: ID linking to provenance record
    """
    
    memory_id: str
    kind: MemoryKind
    content_hash: str
    
    owner_id: str
    
    # Content
    content: Any  # Can be any serializable type
    content_type: str = "text"
    
    # Timestamps & Versioning
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    version: int = 1
    
    # Operational State
    lifecycle_state: "MemoryLifecycleState" = field(default_factory=lambda: MemoryLifecycleState.ACTIVE)
    privacy_class: "MemoryPrivacyClass" = field(default_factory=lambda: MemoryPrivacyClass.OPEN)
    access_scope: MemoryAccessScope = MemoryAccessScope.PRIVATE
    
    # Indexing & Retrieval
    tags: List[str] = field(default_factory=list)
    source_event_id: Optional[str] = None
    
    # Lifecycle
    expires_at: Optional[float] = None
    
    # Provenance
    provenance_id: Optional[str] = None


class MemoryLifecycleState(Enum):
    """
    Lifecycle states for memory records.
    
    - ACTIVE: Current, retrievable memory
    - EXPIRED: Past expiration time (may be archived or deleted)
    - DELETED: Logically deleted (tombstone indicates removal)
    - ARCHIVED: Moved to archive storage tier
    """
    ACTIVE = "active"
    EXPIRED = "expired"
    DELETED = "deleted"
    ARCHIVED = "archived"


class MemoryPrivacyClass(Enum):
    """
    Privacy classification for memory records.
    
    - OPEN: No restrictions, system-wide access
    - CONFIDENTIAL: Requires explicit authorization
    - RESTRICTED: Limited distribution with audit trail
    - PRIVATE: High privacy, requires consent
    - PERSONAL_DATA: Subject to data protection regulations
    """
    OPEN = "open"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    PERSONAL_DATA = "personal_data"


# =============================================================================
# Query & Retrieval Contracts
# =============================================================================

@dataclass(frozen=True)
class MemoryQueryFilters:
    """
    Normalized query filters for memory retrieval.
    
    All fields are optional. Omitting a field means no filter is applied.
    
    Args:
        kinds: Filter by memory kind(s) (None = all kinds)
        owner_ids: Filter by owner ID(s) (None = all owners)
        tags: Match records with ALL these tags (AND logic)
        tag_any: Match records with ANY of these tags (OR logic)
        from_timestamp: Only memories created at or after this time
        to_timestamp: Only memories created before this time
        access_scope: Filter by access scope
        privacy_classes: Filter by privacy class(es)
        
        # Pagination
        limit: Maximum number of results (required, bounded)
        offset: Number of records to skip (for pagination)
        
        # Ordering
        sort_by: Field to sort by ('created_at', 'updated_at')
        sort_ascending: Sort direction
        
        # Index hints
        use_index: Whether to prefer index-based lookup
    """
    
    kinds: Optional[List[MemoryKind]] = None
    owner_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None  # AND logic - match ALL tags
    tag_any: Optional[List[str]] = None  # OR logic - match ANY tag
    
    from_timestamp: Optional[float] = None
    to_timestamp: Optional[float] = None
    
    access_scope: Optional[MemoryAccessScope] = None
    privacy_classes: Optional[List[MemoryPrivacyClass]] = None
    
    # Pagination (bounded by memory repository)
    limit: int = 100  # Default bounded limit
    offset: int = 0
    
    # Ordering
    sort_by: str = "created_at"
    sort_ascending: bool = False
    
    # Index hints
    use_index: bool = True


@dataclass(frozen=True)
class RetrievalRequest:
    """
    Normalized retrieval request from a semantic consumer.
    
    Args:
        request_id: Unique identifier for this request
        owner_scope: Scope of owners to search (None = all)
        
        # Query content
        query_text: Text query for lexical search
        tags: Tags to match
        filters: Structured query filters
        
        # Bounded execution
        limit: Maximum results (must be bounded by repository)
        offset: Pagination offset
        
        # Ranking
        ranking_mode: How to rank results (recency, relevance, etc.)
        min_score: Minimum score threshold for inclusion
        
        # Consistency
        consistency_level: Strong, read_your_writes, eventual
    """
    
    request_id: str
    owner_scope: Optional[str] = None
    
    # Query content
    query_text: Optional[str] = None
    tags: Optional[List[str]] = None
    filters: Optional[MemoryQueryFilters] = None
    
    # Bounded execution
    limit: int = 100
    offset: int = 0
    
    # Ranking options (repository enforces bounds)
    ranking_mode: str = "recency"  # recency, relevance, combined
    min_score: Optional[float] = None
    
    # Consistency
    consistency_level: str = "strong"


@dataclass(frozen=True)
class RetrievalResult:
    """
    Normalized retrieval result with pagination and metadata.
    
    Args:
        request_id: ID of the originating request
        result_id: Unique identifier for this result
        
        # Results
        candidates: List of matching memory records
        total_count: Total number of matching records (for pagination UI)
        
        # Timing & Performance
        query_time_ms: Time taken to execute the query
        cache_hit: Whether results came from cache
        
        # Pagination
        has_more: Whether there are more results beyond this page
        next_offset: Offset for next page (None if no more pages)
        
        # Ranking metadata
        scores: Per-record scores with score type
        ranks: Per-record rank positions
        
        # Partial failures
        partial_results: Whether partial failure occurred
        warnings: List of warning messages
    """
    
    request_id: str
    result_id: str
    
    # Results
    candidates: List[MemoryRecord]
    total_count: int  # Total matching records (for pagination)
    
    # Timing & Performance
    query_time_ms: float = 0.0
    cache_hit: bool = False
    
    # Pagination metadata
    has_more: bool = False
    next_offset: Optional[int] = None
    
    # Ranking metadata
    scores: Dict[str, float] = field(default_factory=dict)  # memory_id -> score
    ranks: Dict[str, int] = field(default_factory=dict)  # memory_id -> rank
    
    # Partial failures
    partial_results: bool = False
    warnings: List[str] = field(default_factory=list)


# =============================================================================
# Failure Types for Memory Operations
# =============================================================================

class MemoryFailureType(Enum):
    """Categories of memory operation failures."""
    
    INVALID_RECORD = "invalid_record"
    UNKNOWN_CATEGORY = "unknown_category"
    UNSUPPORTED_OPERATION = "unsupported_operation"
    DUPLICATE_MEMORY = "duplicate_memory"
    MEMORY_NOT_FOUND = "memory_not_found"
    VERSION_CONFLICT = "version_conflict"
    AUTHORIZATION_DENIED = "authorization_denied"
    PRIVACY_RESTRICTION = "privacy_restriction"
    RETENTION_CONFLICT = "retention_conflict"
    REPOSITORY_UNAVAILABLE = "repository_unavailable"
    STORE_UNAVAILABLE = "store_unavailable"
    TRANSACTION_FAILURE = "transaction_failure"
    SERIALIZATION_FAILURE = "serialization_failure"
    SCHEMA_MISMATCH = "schema_mismatch"
    INDEX_UNAVAILABLE = "index_unavailable"
    INDEX_STALE = "index_stale"
    EMBEDDING_FAILURE = "embedding_failure"
    QUERY_TIMEOUT = "query_timeout"
    RETRIEVAL_CANCELLED = "retrieval_cancelled"
    RESULT_LIMIT_EXCEEDED = "result_limit_exceeded"
    CORRUPTION_DETECTED = "corruption_detected"
    PARTIAL_PERSISTENCE_FAILURE = "partial_persistence_failure"
    
    @classmethod
    def is_retryable(cls, failure_type: "MemoryFailureType") -> bool:
        """Check if a failure type is retryable."""
        retryable = {
            cls.REPOSITORY_UNAVAILABLE,
            cls.STORE_UNAVAILABLE,
            cls.INDEX_UNAVAILABLE,
            cls.EMBEDDING_FAILURE,
            cls.QUERY_TIMEOUT,
            cls.PARTIAL_PERSISTENCE_FAILURE,
        }
        return failure_type in retryable


@dataclass(frozen=True)
class MemoryOperationFailure:
    """
    Failure information for memory operations.
    
    Args:
        failure_type: Category of failure
        message: Human-readable error description
        memory_id: ID of affected memory (if applicable)
        operation: Operation that failed
        retryable: Whether the operation can be retried
        partial_state: Description of partial state if applicable
    """
    
    failure_type: MemoryFailureType
    message: str
    
    memory_id: Optional[str] = None
    operation: str = "unknown"
    
    retryable: bool = False
    partial_state: Optional[str] = None


__all__ = [
    # Record types
    "MemoryKind",
    "MemoryAccessScope",
    "MemoryRecord",
    "MemoryLifecycleState",
    "MemoryPrivacyClass",
    
    # Query & Retrieval
    "MemoryQueryFilters",
    "RetrievalRequest",
    "RetrievalResult",
    
    # Failures
    "MemoryFailureType",
    "MemoryOperationFailure",
]