# Memory Access Request - Phase 5.1.3 Canonical Access Query
# ============================================================

"""
Memory Access Request: Query and authorization context for memory access.

Every access request contains:
    - identity (request identifier)
    - consumer (which component is making the request)
    - requested scope (what artifacts/relations are being queried)
    - requested projection (how the results should be formatted)
    - constraints (filters, limits, etc.)
    - authorization context (policy references)

Request Laws:
    REQUEST-LAW-001: Every access request has explicit identity
    REQUEST-LAW-002: Requests always include consumer information
    REQUEST-LAW-003: Scope and projection are explicitly requested
    REQUEST-LAW-004: Constraints are explicit and enforceable
    REQUEST-LAW-005: Authorization context is always included
    REQUEST-LAW-006: Equivalent requests produce equivalent responses
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# PROJECTION TYPES - What kind of projection?
# =============================================================================


class ProjectionType(Enum):
    """
    Types of projections that can be requested.
    
    | Type         | Description                                  |
    |--------------|---------------------------------------------|
    | FULL         | Complete artifact data with all fields      |
    | SUMMARY      | Summary statistics only                     |
    | IDENTIFIERS  | Artifact IDs only                           |
    | METADATA     | Metadata and provenance only                |
    | RELATIONSHIP | Relationships between artifacts             |
    """
    
    FULL = "full"
    SUMMARY = "summary"
    IDENTIFIERS = "identifiers"
    METADATA = "metadata"
    RELATIONSHIP = "relationship"


# =============================================================================
# ACCESS REQUEST - Complete query specification
# =============================================================================


@dataclass(frozen=True)
class MemoryAccessRequest:
    """
    Complete access request with authorization context.
    
    Every request is processed through the canonical pipeline:
        Request -> Authorization -> Visibility -> Projection -> Response
    
    Fields:
        request_id:          Unique identifier for this request
        
        # Consumer identity
        session_id:          Which session made this request?
        requester_id:        Who/what is making the request?
        
        # Query scope
        artifact_ids:        Specific artifact IDs to retrieve (optional)
        query_kind:          What type of query is this?
        
        # Projection configuration
        projection_type:     How should results be formatted?
        include_revisions:   Include all revisions of matching artifacts?
        depth:               For subgraph queries, how deep to traverse?
        
        # Constraints
        limit:               Maximum number of results (0 = no limit)
        offset:              Skip this many results
        filter_conditions:   Additional filters on artifact properties
        
        # Authorization context
        policy_reference:    Which authorization policy applies?
        visibility_context:  Context for visibility evaluation
        
        # Execution context
        timestamp_utc:       When was request created?
        priority:            Request priority (0-1, higher = more urgent)
        
        # Metadata
        correlation_id:      For distributed tracing
        tags:                Additional metadata labels
    """
    
    # Core identity (required)
    request_id: str
    
    # Consumer identity
    session_id: Optional[str] = None  # If part of a session
    requester_id: str                 # Who/what is making the request?
    
    # Query scope
    artifact_ids: Tuple[str, ...] = field(default_factory=tuple)  # Specific IDs to fetch
    query_kind: str = "artifact"      # What type of query (artifact, subgraph, summary)
    
    # Projection configuration
    projection_type: ProjectionType = ProjectionType.FULL
    include_revisions: bool = False   # Include all revisions?
    depth: int = 2                    # For graph queries
    
    # Constraints
    limit: int = 100                  # Max results (0 = no limit)
    offset: int = 0                   # Skip first N results
    filter_conditions: Dict[str, Any] = field(default_factory=dict)  # Extra filters
    
    # Authorization context
    policy_reference: Optional[str] = None
    visibility_context: Dict[str, Any] = field(default_factory=dict)
    
    # Execution context
    timestamp_utc: float = field(default_factory=time.time)
    priority: float = 0.5             # Priority (0.0-1.0)
    
    # Metadata
    correlation_id: Optional[str] = None  # For distributed tracing
    tags: Tuple[str, ...] = field(default_factory=tuple)  # Labels
    
    @property
    def is_summary_query(self) -> bool:
        """Check if this is a summary statistics query."""
        return self.query_kind == "summary"
    
    @property
    def is_artifact_query(self) -> bool:
        """Check if this is an artifact retrieval query."""
        return self.query_kind == "artifact" and len(self.artifact_ids) > 0
    
    @property
    def is_subgraph_query(self) -> bool:
        """Check if this is a subgraph traversal query."""
        return self.query_kind == "subgraph"
    
    def with_limit(self, limit: int) -> MemoryAccessRequest:
        """Return a copy with updated limit."""
        return dataclass_replace(self, limit=limit)
    
    def with_offset(self, offset: int) -> MemoryAccessRequest:
        """Return a copy with updated offset."""
        return dataclass_replace(self, offset=offset)
    
    def add_filter(self, key: str, value: Any) -> MemoryAccessRequest:
        """Add a filter condition."""
        new_filters = dict(self.filter_conditions)
        new_filters[key] = value
        return dataclass_replace(self, filter_conditions=new_filters)
    
    def with_projection_type(self, projection_type: ProjectionType) -> MemoryAccessRequest:
        """Return a copy with updated projection type."""
        return dataclass_replace(self, projection_type=projection_type)
    
    @classmethod
    def for_artifacts(
        cls,
        artifact_ids: Tuple[str, ...],
        requester_id: str,
        session_id: Optional[str] = None,
    ) -> MemoryAccessRequest:
        """
        Create an artifact retrieval request.
        
        Args:
            artifact_ids: Which artifacts to retrieve?
            requester_id: Who's making the request?
            session_id: Which session (optional)?
            
        Returns:
            New MemoryAccessRequest for artifact retrieval
        """
        return cls(
            request_id=str(time.time_ns()),
            session_id=session_id,
            requester_id=requester_id,
            artifact_ids=artifact_ids,
            query_kind="artifact",
            projection_type=ProjectionType.FULL,
        )
    
    @classmethod
    def for_subgraph(
        cls,
        root_artifact: str,
        requester_id: str,
        depth: int = 2,
        session_id: Optional[str] = None,
    ) -> MemoryAccessRequest:
        """
        Create a subgraph traversal request.
        
        Args:
            root_artifact: Central artifact to traverse from
            depth: Max traversal depth
            requester_id: Who's making the request?
            session_id: Which session (optional)?
            
        Returns:
            New MemoryAccessRequest for subgraph query
        """
        return cls(
            request_id=str(time.time_ns()),
            session_id=session_id,
            requester_id=requester_id,
            artifact_ids=(root_artifact,),
            query_kind="subgraph",
            projection_type=ProjectionType.RELATIONSHIP,
            depth=depth,
        )
    
    @classmethod
    def for_summary(
        cls,
        requester_id: str,
        session_id: Optional[str] = None,
    ) -> MemoryAccessRequest:
        """
        Create a summary statistics request.
        
        Args:
            requester_id: Who's making the request?
            session_id: Which session (optional)?
            
        Returns:
            New MemoryAccessRequest for summary query
        """
        return cls(
            request_id=str(time.time_ns()),
            session_id=session_id,
            requester_id=requester_id,
            query_kind="summary",
            projection_type=ProjectionType.SUMMARY,
        )
    
    @classmethod
    def for_identifiers_only(
        cls,
        requester_id: str,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> MemoryAccessRequest:
        """
        Create a request that returns only identifiers.
        
        Args:
            filter_conditions: Filters to apply
            requester_id: Who's making the request?
            limit: Max results
            
        Returns:
            New MemoryAccessRequest returning only IDs
        """
        return cls(
            request_id=str(time.time_ns()),
            requester_id=requester_id,
            query_kind="artifact",
            projection_type=ProjectionType.IDENTIFIERS,
            limit=limit,
            filter_conditions=filter_conditions or {},
        )


# =============================================================================
# ACCESS REQUEST BUILDER - Mutable builder
# =============================================================================


class MemoryAccessRequestBuilder:
    """
    Mutable builder for constructing access requests.
    
    Allows step-by-step configuration before producing an immutable request.
    """
    
    def __init__(self, requester_id: str):
        self._request_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._requester_id: str = requester_id
        
        # Query scope
        self._artifact_ids: List[str] = []
        self._query_kind: str = "artifact"
        
        # Projection configuration
        self._projection_type: ProjectionType = ProjectionType.FULL
        self._include_revisions: bool = False
        self._depth: int = 2
        
        # Constraints
        self._limit: int = 100
        self._offset: int = 0
        self._filter_conditions: Dict[str, Any] = {}
        
        # Authorization context
        self._policy_reference: Optional[str] = None
        self._visibility_context: Dict[str, Any] = {}
        
        # Execution context
        self._timestamp_utc: float = time.time()
        self._priority: float = 0.5
        
        # Metadata
        self._correlation_id: Optional[str] = None
        self._tags: List[str] = []
    
    def set_request_id(self, request_id: str) -> "MemoryAccessRequestBuilder":
        """Set the request ID."""
        self._request_id = request_id
        return self
    
    def set_session_id(self, session_id: str) -> "MemoryAccessRequestBuilder":
        """Set the session ID."""
        self._session_id = session_id
        return self
    
    def add_artifact_id(self, artifact_id: str) -> "MemoryAccessRequestBuilder":
        """Add an artifact ID to the request."""
        if artifact_id not in self._artifact_ids:
            self._artifact_ids.append(artifact_id)
        return self
    
    def set_query_kind(self, query_kind: str) -> "MemoryAccessRequestBuilder":
        """Set the query kind (artifact, subgraph, summary)."""
        self._query_kind = query_kind
        return self
    
    def set_projection_type(self, projection_type: ProjectionType) -> "MemoryAccessRequestBuilder":
        """Set the projection type."""
        self._projection_type = projection_type
        return self
    
    def set_include_revisions(self, include: bool) -> "MemoryAccessRequestBuilder":
        """Set whether to include all revisions."""
        self._include_revisions = include
        return self
    
    def set_depth(self, depth: int) -> "MemoryAccessRequestBuilder":
        """Set traversal depth for graph queries."""
        if depth < 0:
            raise ValueError("Depth must be >= 0")
        self._depth = depth
        return self
    
    def set_limit(self, limit: int) -> "MemoryAccessRequestBuilder":
        """Set maximum results (0 = no limit)."""
        self._limit = max(0, limit)
        return self
    
    def set_offset(self, offset: int) -> "MemoryAccessRequestBuilder":
        """Set result offset."""
        if offset < 0:
            raise ValueError("Offset must be >= 0")
        self._offset = offset
        return self
    
    def add_filter(self, key: str, value: Any) -> "MemoryAccessRequestBuilder":
        """Add a filter condition."""
        self._filter_conditions[key] = value
        return self
    
    def set_policy_reference(self, policy_id: str) -> "MemoryAccessRequestBuilder":
        """Set the authorization policy reference."""
        self._policy_reference = policy_id
        return self
    
    def add_visibility_context(self, key: str, value: Any) -> "MemoryAccessRequestBuilder":
        """Add to visibility context."""
        self._visibility_context[key] = value
        return self
    
    def set_priority(self, priority: float) -> "MemoryAccessRequestBuilder":
        """Set request priority (0.0-1.0)."""
        self._priority = max(0.0, min(1.0, priority))
        return self
    
    def set_correlation_id(self, correlation_id: str) -> "MemoryAccessRequestBuilder":
        """Set distributed tracing ID."""
        self._correlation_id = correlation_id
        return self
    
    def add_tag(self, tag: str) -> "MemoryAccessRequestBuilder":
        """Add a metadata tag."""
        if tag not in self._tags:
            self._tags.append(tag)
        return self
    
    def build(self) -> MemoryAccessRequest:
        """
        Build an immutable MemoryAccessRequest.
        
        Returns:
            New MemoryAccessRequest with all settings applied
        """
        return MemoryAccessRequest(
            request_id=self._request_id or str(time.time_ns()),
            session_id=self._session_id,
            requester_id=self._requester_id,
            artifact_ids=tuple(self._artifact_ids),
            query_kind=self._query_kind,
            projection_type=self._projection_type,
            include_revisions=self._include_revisions,
            depth=self._depth,
            limit=self._limit,
            offset=self._offset,
            filter_conditions=dict(self._filter_conditions),
            policy_reference=self._policy_reference,
            visibility_context=dict(self._visibility_context),
            timestamp_utc=self._timestamp_utc,
            priority=self._priority,
            correlation_id=self._correlation_id,
            tags=tuple(self._tags),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryAccessRequest, **kwargs) -> MemoryAccessRequest:
    """Replace fields in a frozen dataclass."""
    return MemoryAccessRequest(
        request_id=instance.request_id,
        session_id=kwargs.get("session_id", instance.session_id),
        requester_id=kwargs.get("requester_id", instance.requester_id),
        artifact_ids=kwargs.get("artifact_ids", instance.artifact_ids),
        query_kind=kwargs.get("query_kind", instance.query_kind),
        projection_type=kwargs.get("projection_type", instance.projection_type),
        include_revisions=kwargs.get("include_revisions", instance.include_revisions),
        depth=kwargs.get("depth", instance.depth),
        limit=kwargs.get("limit", instance.limit),
        offset=kwargs.get("offset", instance.offset),
        filter_conditions=dict(instance.filter_conditions) if "filter_conditions" not in kwargs else kwargs["filter_conditions"],
        policy_reference=kwargs.get("policy_reference", instance.policy_reference),
        visibility_context=dict(instance.visibility_context) if "visibility_context" not in kwargs else kwargs["visibility_context"],
        timestamp_utc=kwargs.get("timestamp_utc", instance.timestamp_utc),
        priority=kwargs.get("priority", instance.priority),
        correlation_id=kwargs.get("correlation_id", instance.correlation_id),
        tags=kwargs.get("tags", instance.tags),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryAccessRequest",
    "ProjectionType",
    "MemoryAccessRequestBuilder",
    "dataclass_replace",
]