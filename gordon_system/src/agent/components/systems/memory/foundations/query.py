# Memory Query - Phase 5.1 Canonical Read-Only Access
# =====================================================

"""
Memory Query: Read-only access to memory substrate.

All queries are:
    - Read-only (never mutate)
    - Deterministic (same inputs produce same outputs)
    - Semantic (work with semantic artifacts, not storage details)

Query Laws:
    QUERY-LAW-001: Memory Queries are read-only
    QUERY-LAW-002: Queries never mutate Memory Artifacts
    QUERY-LAW-003: Queries preserve determinism
    QUERY-LAW-004: Equivalent queries produce equivalent semantic results
    QUERY-LAW-005: Queries preserve provenance
    QUERY-LAW-006: Query limitations are explicit
    QUERY-LAW-007: Historical query semantics remain compatible
    QUERY-LAW-008: Query execution is side-effect free
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# MEMORY QUERY TYPES - What kind of query?
# =============================================================================


class MemoryQueryKind(Enum):
    """
    Types of memory queries.
    
    | Query Kind     | Description                                       |
    |----------------|--------------------------------------------------|
    | ARTIFACT       | Retrieve specific artifacts                       |
    | RELATION       | Find relationships between artifacts              |
    | SUBGRAPH       | Get subgraph around an artifact                   |
    | PATH           | Find paths between artifacts                      |
    | SUMMARY        | Get summary statistics                            |
    | HISTORY        | View revision history                             |
    | SNAPSHOT       | Get projection snapshot                           |
    """
    
    ARTIFACT = "artifact"
    RELATION = "relation"
    SUBGRAPH = "subgraph"
    PATH = "path"
    SUMMARY = "summary"
    HISTORY = "history"
    SNAPSHOT = "snapshot"


# =============================================================================
# QUERY RESULT - Query outcome
# =============================================================================


@dataclass(frozen=True)
class QueryResult:
    """
    Result of a memory query.
    
    Fields:
        result_id:         Unique ID for this result
        
        # Content
        results:           List of matching items (artifact IDs, etc.)
        
        # Metadata
        query_type:        What type of query was run?
        total_count:       Total number of matches found
        limited:           Were results truncated by limit?
        
        # Performance
        execution_time_ms: How long did it take? (in milliseconds)
        
        # Provenance
        executed_by:       Who/what executed this query?
        timestamp_utc:     When was the query executed?
    """
    
    result_id: str                        # Unique ID for this result
    
    # Content
    results: Tuple[str, ...]              # List of matching items
    metadata: Dict[str, Any] = field(default_factory=dict)  # Extra result data
    
    # Metadata
    query_type: str = "unknown"           # What kind of query?
    total_count: int = 0                  # Total matches (including truncated)
    limited: bool = False                 # Were results truncated?
    
    # Performance
    execution_time_ms: float = 0.0        # Time in milliseconds
    
    # Provenance
    executed_by: Optional[str] = None     # Who ran the query?
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# ARTIFACT QUERY - Retrieve artifacts
# =============================================================================


@dataclass(frozen=True)
class ArtifactQuery:
    """
    Query for retrieving memory artifacts.
    
    Fields:
        artifact_ids:      Which specific artifact IDs to retrieve?
        
        # Filters
        artifact_kinds:    Filter by kind (optional)
        validity_states:   Filter by validity status (optional)
        created_after_utc: Only artifacts after this time (optional)
        created_before_utc: Only artifacts before this time (optional)
        
        # Pagination
        limit:             Maximum results to return
        offset:            Skip this many results
        
        # Output options
        include_revisions: Include all revisions of matching artifacts?
    """
    
    artifact_ids: Tuple[str, ...] = field(default_factory=tuple)  # Specific IDs
    
    # Filters
    artifact_kinds: Tuple[str, ...] = field(default_factory=tuple)
    validity_states: Tuple[str, ...] = field(default_factory=tuple)
    created_after_utc: Optional[float] = None
    created_before_utc: Optional[float] = None
    
    # Pagination
    limit: int = 100
    offset: int = 0
    
    # Output options
    include_revisions: bool = False


# =============================================================================
# RELATION QUERY - Find relationships
# =============================================================================


@dataclass(frozen=True)
class RelationQuery:
    """
    Query for retrieving memory relations.
    
    Fields:
        source_artifacts:  Only relations from these sources?
        
        # Filters
        relation_kinds:    Filter by relation kind (optional)
        target_artifacts:  Only relations to these targets? (optional)
        
        # Output options
        limit:             Maximum results
        offset:            Skip this many results
    """
    
    source_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Optional filters
    
    relation_kinds: Tuple[str, ...] = field(default_factory=tuple)
    target_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    limit: int = 100
    offset: int = 0


# =============================================================================
# SUBGRAPH QUERY - Get local graph neighborhood
# =============================================================================


@dataclass(frozen=True)
class SubgraphQuery:
    """
    Query for retrieving a subgraph around an artifact.
    
    Fields:
        root_artifact:     The central artifact
        
        # Search parameters
        depth:             How far to traverse from root?
        
        # Output options
        include_incoming:  Include relations pointing TO root?
        include_outgoing:  Include relations coming FROM root?
    """
    
    root_artifact: str                    # Central artifact
    
    # Search parameters
    depth: int = 2                        # Max traversal depth
    
    # Output options
    include_incoming: bool = True         # Relations TO root
    include_outgoing: bool = True         # Relations FROM root


# =============================================================================
# PATH QUERY - Find relationship chains
# =============================================================================


@dataclass(frozen=True)
class PathQuery:
    """
    Query for finding paths between artifacts.
    
    Fields:
        start_artifact:    Where does the path start?
        end_artifact:      Where does the path end (optional)?
        
        # Search parameters
        max_depth:         Maximum length of path to find
        
        # Filters
        relation_kinds:    Only traverse these relation kinds? (optional)
        
        # Output options
        limit_paths:       Maximum number of paths to return
    """
    
    start_artifact: str                   # Path starts here
    
    end_artifact: Optional[str] = None    # Path ends here (if specified)
    
    max_depth: int = 10                   # Maximum path length
    
    relation_kinds: Tuple[str, ...] = field(default_factory=tuple)  # Optional filter
    
    limit_paths: int = 10                 # Max paths to return


# =============================================================================
# SUMMARY QUERY - Get statistics
# =============================================================================


@dataclass(frozen=True)
class SummaryQuery:
    """
    Query for getting summary information.
    
    Fields:
        include_artifacts:      Count of artifacts?
        include_relations:      Count of relations?
        include_clusters:       Count of clusters?
        
        time_range_start_utc:   Only count from this time? (optional)
        time_range_end_utc:     Only count until this time? (optional)
    """
    
    include_artifacts: bool = True
    include_relations: bool = True
    include_clusters: bool = True
    
    time_range_start_utc: Optional[float] = None
    time_range_end_utc: Optional[float] = None


# =============================================================================
# HISTORY QUERY - View revision history
# =============================================================================


@dataclass(frozen=True)
class HistoryQuery:
    """
    Query for retrieving revision history.
    
    Fields:
        artifact_id:       Which artifact's history?
        
        # Time range
        after_revision:    Only revisions after this number? (optional)
        
        # Output options
        limit:             Maximum revisions to return
    """
    
    artifact_id: str                      # Artifact to view history for
    
    after_revision: Optional[int] = None  # Start from this revision
    
    limit: int = 100


# =============================================================================
# SNAPSHOT QUERY - Get projection snapshot
# =============================================================================


@dataclass(frozen=True)
class SnapshotQuery:
    """
    Query for getting a memory snapshot.
    
    Fields:
        semantic_time_utc: What point in time?
        
        # Scope
        scope_artifacts:   Only these artifacts? (optional)
    """
    
    semantic_time_utc: float              # Point in time to snapshot
    
    scope_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Optional filter


# =============================================================================
# MEMORY QUERY - Complete query specification
# =============================================================================


@dataclass(frozen=True)
class MemoryQuery:
    """
    Complete memory query specification.
    
    All queries are read-only and deterministic.
    
    Fields:
        query_id:          Unique ID for this query
        
        # Query kind
        query_kind:        What type of query?
        
        # Parameters (varies by kind)
        artifact_query:    ArtifactQuery if kind is ARTIFACT
        relation_query:    RelationQuery if kind is RELATION
        subgraph_query:    SubgraphQuery if kind is SUBGRAPH
        path_query:        PathQuery if kind is PATH
        summary_query:     SummaryQuery if kind is SUMMARY
        history_query:     HistoryQuery if kind is HISTORY
        snapshot_query:    SnapshotQuery if kind is SNAPSHOT
        
        # Execution context
        executed_by:       Who/what is executing?
        timestamp_utc:     When was query created?
        
        # Limitations (for observability)
        max_execution_ms:  Maximum allowed execution time
    """
    
    query_id: str                         # Unique ID for this query
    
    # Query kind
    query_kind: MemoryQueryKind           # What type of query?
    
    # Parameters - exactly one should be populated based on query_kind
    artifact_query: Optional[ArtifactQuery] = None
    relation_query: Optional[RelationQuery] = None
    subgraph_query: Optional[SubgraphQuery] = None
    path_query: Optional[PathQuery] = None
    summary_query: Optional[SummaryQuery] = None
    history_query: Optional[HistoryQuery] = None
    snapshot_query: Optional[SnapshotQuery] = None
    
    # Execution context
    executed_by: Optional[str] = None     # Who/what is executing?
    timestamp_utc: float = field(default_factory=time.time)
    
    # Limitations
    max_execution_ms: float = 60_000.0    # 60 seconds default timeout
    
    @classmethod
    def for_artifacts(
        cls,
        artifact_ids: Tuple[str, ...] = tuple(),
        limit: int = 100,
        executed_by: Optional[str] = None,
    ) -> "MemoryQuery":
        """
        Create an artifact query.
        
        Args:
            artifact_ids: Specific IDs to look up
            limit: Max results
            executed_by: Who's executing? (optional)
            
        Returns:
            MemoryQuery with ArtifactQuery parameters
        """
        return cls(
            query_id=str(hash(time.time())),
            query_kind=MemoryQueryKind.ARTIFACT,
            artifact_query=ArtifactQuery(
                artifact_ids=artifact_ids,
                limit=limit,
            ),
            executed_by=executed_by,
        )
    
    @classmethod
    def for_subgraph(
        cls,
        root_artifact: str,
        depth: int = 2,
        executed_by: Optional[str] = None,
    ) -> "MemoryQuery":
        """
        Create a subgraph query.
        
        Args:
            root_artifact: Central artifact
            depth: Max traversal depth
            executed_by: Who's executing? (optional)
            
        Returns:
            MemoryQuery with SubgraphQuery parameters
        """
        return cls(
            query_id=str(hash(time.time())),
            query_kind=MemoryQueryKind.SUBGRAPH,
            subgraph_query=SubgraphQuery(
                root_artifact=root_artifact,
                depth=depth,
            ),
            executed_by=executed_by,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryQuery",
    "MemoryQueryKind",
    "QueryResult",
    "ArtifactQuery",
    "RelationQuery",
    "SubgraphQuery",
    "PathQuery",
    "SummaryQuery",
    "HistoryQuery",
    "SnapshotQuery",
]