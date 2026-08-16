# Integration Request - Phase 5.1.7 Canonical Request Interface
# ===============================================================

"""
Memory Integration Request: Request format for subsystem communication.

Every request to Memory must include:
    - identity (unique request identifier)
    - requester (which subsystem is making the request)
    - purpose (what the requester wants to achieve)
    - requested scope (what artifacts/relations are needed)
    - constraints (filters, limits, etc.)
    - authorization context

Request Laws:
    REQUEST-LAW-001: Every request has explicit identity
    REQUEST-LAW-002: Requests include consumer information
    REQUEST-LAW-003: Scope and purpose are explicitly stated
    REQUEST-LAW-004: Constraints are explicit and enforceable
    REQUEST-LAW-005: Authorization context is included
    REQUEST-LAW-006: Requests are immutable once created
    REQUEST-LAW-007: Equivalent requests produce equivalent responses
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REQUEST TYPES - What kind of request?
# =============================================================================


class RequestType(Enum):
    """
    Types of integration requests.
    
    | Type         | Description                                        |
    |--------------|----------------------------------------------------|
    | QUERY        | Query for information                              |
    | PROJECT      | Request a projection                               |
    | VALIDATE     | Validate some assertion                            |
    | DERIVE       | Request derived information                        |
    | VALIDATE     | Validate some assertion                            |
    | SYNCHRONIZE  | Request synchronization                            |
    | CONFIGURE    | Configure consumer behavior                        |
    """
    
    QUERY = "query"
    PROJECT = "project"
    VALIDATE = "validate"
    DERIVE = "derive"
    SYNCHRONIZE = "synchronize"
    CONFIGURE = "configure"


# =============================================================================
# SCOPE DEFINITION
# =============================================================================


class ScopeType(Enum):
    """
    Types of scope that can be requested.
    
    | Type          | Description                                        |
    |---------------|----------------------------------------------------|
    | MEMORY        | Memory artifacts and their states                  |
    | PROJECTIONS   | Projections over memory                            |
    | DERIVATIONS   | Derived information                                |
    | HISTORY       | Historical records                                 |
    | POLICY        | Policy evaluation                                  |
    """
    
    MEMORY = "memory"
    PROJECTIONS = "projections"
    DERIVATIONS = "derivations"
    HISTORY = "history"
    POLICY = "policy"


@dataclass(frozen=True)
class RequestScope:
    """
    Definition of the requested scope.
    
    Fields:
        scope_type:     What kind of scope is being requested?
        artifact_ids:   Specific artifact IDs (optional)
        relation_types: Relation types to include
        time_range:     Time range for historical queries
        
        # Constraints
        limit:          Maximum results (0 = no limit)
        offset:         Skip this many results
        
        # Projection configuration
        depth:          Traversal depth for graph queries
        include_meta:   Include metadata and provenance?
    """
    
    scope_type: ScopeType = ScopeType.MEMORY
    
    artifact_ids: Tuple[str, ...] = field(default_factory=tuple)
    relation_types: Tuple[str, ...] = field(default_factory=tuple)
    
    # Time range (optional)
    start_time_utc: Optional[float] = None
    end_time_utc: Optional[float] = None
    
    # Constraints
    limit: int = 0  # 0 means no limit
    offset: int = 0
    
    # Projection configuration
    depth: int = 1
    include_meta: bool = True


# =============================================================================
# REQUEST AUTHORIZATION
# =============================================================================


@dataclass(frozen=True)
class RequestAuthorization:
    """
    Authorization context for the request.
    
    Fields:
        policy_reference:   Which authorization policy applies?
        visibility_context: Context for visibility evaluation
        
        # Authentication
        requester_id:       Who is making the request?
        session_id:         Session context (if any)
        
        # Permissions
        allowed_operations: Operations this requester can perform
        denied_operations:  Operations explicitly forbidden
    """
    
    policy_reference: Optional[str] = None
    visibility_context: Dict[str, Any] = field(default_factory=dict)
    
    requester_id: str = "anonymous"
    session_id: Optional[str] = None
    
    allowed_operations: Tuple[str, ...] = ("read",)
    denied_operations: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# INTEGRATION REQUEST
# =============================================================================


@dataclass(frozen=True)
class MemoryIntegrationRequest:
    """
    Complete integration request to Memory.
    
    Every request goes through the canonical pipeline:
        Request -> Authorization -> Visibility -> Projection -> Response
    
    Fields:
        request_id:         Unique identifier for this request
        
        # Identity and provenance
        requester:          Which subsystem is making the request?
        purpose:            What does the requester want to achieve?
        
        # Request details
        request_type:       Type of request being made
        scope:              What is being requested?
        
        # Configuration
        constraints:        Additional constraints on results
        
        # Authorization
        authorization:      Authorization context for this request
        
        # Execution
        timestamp_utc:      When was this request created?
        correlation_id:     For distributed tracing
    """
    
    request_id: str                         # Unique identifier
    
    # Identity and provenance
    requester: str                          # Consumer subsystem name
    purpose: str                            # What the requester wants
    
    # Request details
    request_type: RequestType = RequestType.QUERY
    scope: RequestScope = field(default_factory=RequestScope)
    
    # Configuration
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Authorization
    authorization: RequestAuthorization = field(default_factory=RequestAuthorization)
    
    # Execution context
    timestamp_utc: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None
    
    def with_requester(self, requester: str) -> MemoryIntegrationRequest:
        """Return a copy with the specified requester."""
        return dataclass_replace(self, requester=requester)
    
    def with_purpose(self, purpose: str) -> MemoryIntegrationRequest:
        """Return a copy with the specified purpose."""
        return dataclass_replace(self, purpose=purpose)
    
    def with_scope(self, scope: RequestScope) -> MemoryIntegrationRequest:
        """Return a copy with the specified scope."""
        return dataclass_replace(self, scope=scope)
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate this request.
        
        Returns: (is_valid, error_message)
        """
        # Check required fields
        if not self.request_id:
            return (False, "request_id is required")
        
        if not self.requester:
            return (False, "requester is required")
        
        if not self.purpose:
            return (False, "purpose is required")
        
        # Validate timestamp
        if self.timestamp_utc <= 0:
            return (False, "timestamp must be positive")
        
        return (True, None)


# =============================================================================
# REQUEST BUILDER
# =============================================================================


def create_request(
    requester: str,
    purpose: str,
    request_type: RequestType = RequestType.QUERY,
    scope: Optional[RequestScope] = None,
    constraints: Optional[Dict[str, Any]] = None,
    authorization: Optional[RequestAuthorization] = None
) -> MemoryIntegrationRequest:
    """
    Create a new integration request.
    
    Args:
        requester:     Which subsystem is making the request?
        purpose:       What does the requester want to achieve?
        request_type:  Type of request (default: QUERY)
        scope:         What is being requested?
        constraints:   Additional constraints
        authorization: Authorization context
        
    Returns:
        A new MemoryIntegrationRequest with a generated ID.
    """
    return MemoryIntegrationRequest(
        request_id=str(uuid.uuid4()),
        requester=requester,
        purpose=purpose,
        request_type=request_type,
        scope=scope or RequestScope(),
        constraints=constraints or {},
        authorization=authorization or RequestAuthorization()
    )


# =============================================================================
# REQUEST REPLY
# =============================================================================


@dataclass(frozen=True)
class RequestReply:
    """
    Reply to a specific request.
    
    Fields:
        reply_id:           Unique identifier for this reply
        
        # Reference to original request
        request_id:         ID of the request being replied to
        
        # Content
        response_data:      The actual response data
        metadata:           Response metadata (count, etc.)
        
        # Diagnostics
        latency_ms:         How long did processing take?
        warnings:           Non-critical issues encountered
    """
    
    reply_id: str                           # Unique identifier
    
    request_id: str                         # ID of original request
    
    response_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    latency_ms: float = 0.0
    warnings: Tuple[str, ...] = field(default_factory=tuple)


def create_reply(
    request_id: str,
    response_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> RequestReply:
    """
    Create a reply to a request.
    
    Args:
        request_id:     ID of the original request
        response_data:  The response payload
        metadata:       Additional response metadata
        
    Returns:
        A new RequestReply with a generated ID.
    """
    return RequestReply(
        reply_id=str(uuid.uuid4()),
        request_id=request_id,
        response_data=response_data,
        metadata=metadata or {}
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace (Python 3.7 compatible)."""
    return type(instance)(
        **{field.name: kwargs.get(field.name, getattr(instance, field.name))
           for field in instance.__dataclass_fields__.values()}
    )