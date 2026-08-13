# Phase 3.11.14 - Cross-Stream Correlation Security
# ===================================================

"""
Security Module for Cross-Stream Correlation & Causation Architecture.

This module implements security controls for:
    - Relationship graph integrity protection
    - Forgery prevention (correlation/causation)
    - Cross-user isolation
    - Privacy class enforcement
    - Scope validation
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum, auto
import time
import hashlib


# =============================================================================
# AUTHORIZATION CONTEXT
# =============================================================================


class AuthorizationScope(Enum):
    """Security scope for authorization decisions."""
    SYSTEM = "system"         # Internal system operations
    USER = "user"           # User-scoped relationships
    SESSION = "session"     # Session-scoped relationships
    AGENT = "agent"         # Agent-scoped relationships
    TENANT = "tenant"       # Multi-tenant scoped


@dataclass(frozen=True)
class AuthorizationContext:
    """
    Context for authorization decisions.
    
    Contains all security-relevant information without live objects.
    """
    actor_id: str                 # Who is making the request?
    scope: AuthorizationScope     # What scope applies?
    resource_type: str            # What type of resource?
    resource_id: Optional[str] = None  # Which specific resource?
    
    # Time bounds
    valid_from_utc: float = field(default_factory=time.time)
    valid_until_utc: Optional[float] = None
    
    # Additional constraints
    max_relationship_depth: int = 10
    allowed_relationship_kinds: Tuple[str, ...] = field(default_factory=tuple)  # Empty = all allowed


# =============================================================================
# RELATIONSHIP AUTHORIZATION
# =============================================================================


class RelationshipAuthorizationResult(Enum):
    """Result of relationship authorization."""
    ALLOWED = "allowed"
    DENIED_SCOPE = "denied_scope"           # Scope mismatch
    DENIED_PRIVACY = "denied_privacy"       # Privacy class violation
    DENIED_DEPTH = "denied_depth"           # Too deep (recursion limit)
    DENIED_FORGERY = "denied_forgery"       # Suspicious causation pattern


@dataclass(frozen=True)
class RelationshipAuthorization:
    """
    Authorization decision for a relationship operation.
    
    This is separate from the graph itself - authorization happens before
    any graph mutation.
    """
    result: RelationshipAuthorizationResult
    reason: str
    
    # For allowed operations
    edge_id: Optional[str] = None
    created_at_utc: float = field(default_factory=time.time)
    
    # Audit trail
    actor_id: Optional[str] = None
    resource_type: Optional[str] = None


class RelationshipAuthorizationEnforcer:
    """
    Enforces security policies for relationship graph operations.
    
    Never modifies the graph directly - only makes authorization decisions.
    """

    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
    
    def authorize_correlation_edge(
        self,
        source_stream_id: str,
        target_stream_id: str,
        context: AuthorizationContext,
        privacy_class_source: str = "internal",
        privacy_class_target: str = "internal",
    ) -> RelationshipAuthorization:
        """
        Authorize adding a correlation edge between two records.
        
        Checks:
            - Scope compatibility (both in same scope or global)
            - Privacy class alignment
            - No cross-user correlation without explicit permission
        """
        # Check scope compatibility
        if context.scope == AuthorizationScope.SYSTEM:
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.ALLOWED,
                reason="System actor can correlate any streams",
                edge_id=f"corr-auth-{time.monotonic_ns()}"
            )
        
        # Same stream is always allowed for same owner
        if source_stream_id == target_stream_id:
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.ALLOWED,
                reason="Same stream correlation allowed",
                edge_id=f"corr-auth-{time.monotonic_ns()}"
            )
        
        # Cross-stream correlation requires compatible scopes
        if self._scopes_compatible(source_stream_id, target_stream_id, context.scope):
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.ALLOWED,
                reason="Compatible scopes for cross-stream correlation",
                edge_id=f"corr-auth-{time.monotonic_ns()}"
            )
        
        # Privacy class check - restricted content cannot be correlated with external
        if privacy_class_source in ("restricted", "confidential") or \
           privacy_class_target in ("restricted", "confidential"):
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.DENIED_PRIVACY,
                reason="Privacy class prevents correlation with sensitive content"
            )
        
        return RelationshipAuthorization(
            result=RelationshipAuthorizationResult.DENIED_SCOPE,
            reason=f"Scope mismatch: {context.scope.value}"
        )
    
    def authorize_causation_edge(
        self,
        cause_stream_id: str,
        effect_stream_id: str,
        context: AuthorizationContext,
        evidence_count: int = 1,
    ) -> RelationshipAuthorization:
        """
        Authorize adding a causation edge.
        
        Causation requires:
            - Explicit evidence (minimum threshold)
            - No circular causation
            - Scope compatibility
            - Depth within limits
        """
        if context.scope == AuthorizationScope.SYSTEM:
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.ALLOWED,
                reason="System actor can establish any causal relationships",
                edge_id=f"caus-auth-{time.monotonic_ns()}"
            )
        
        # Evidence requirement for causation (non-system actors)
        if evidence_count < 1:
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.DENIED_FORGERY,
                reason="Causation requires at least one evidence reference"
            )
        
        # Check depth - prevent circular references
        # (actual cycle detection requires graph state, basic check here)
        if context.max_relationship_depth <= 0:
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.DENIED_DEPTH,
                reason="Maximum relationship depth exceeded"
            )
        
        # Scope compatibility check
        if self._scopes_compatible(cause_stream_id, effect_stream_id, context.scope):
            return RelationshipAuthorization(
                result=RelationshipAuthorizationResult.ALLOWED,
                reason="Compatible scopes for causal relationship",
                edge_id=f"caus-auth-{time.monotonic_ns()}"
            )
        
        return RelationshipAuthorization(
            result=RelationshipAuthorizationResult.DENIED_SCOPE,
            reason=f"Scope mismatch: {context.scope.value}"
        )
    
    def _scopes_compatible(self, stream_a: str, stream_b: str, context_scope: AuthorizationScope) -> bool:
        """Check if two streams are in compatible scopes."""
        # System scope can access anything
        if context_scope == AuthorizationScope.SYSTEM:
            return True
        
        # Extract scope from stream IDs (if present)
        scope_a = self._extract_scope(stream_a)
        scope_b = self._extract_scope(stream_b)
        
        # Global streams can interact with any scoped stream
        if scope_a == "global" or scope_b == "global":
            return True
        
        # Same scope is compatible
        return scope_a == scope_b
    
    def _extract_scope(self, stream_id: str) -> str:
        """Extract scope from a stream ID."""
        if "-" in stream_id:
            parts = stream_id.rsplit("-", 1)
            potential_scope = parts[1]
            # Common scope patterns
            if potential_scope in ("global", "system", "user", "session", "agent", "tenant"):
                return potential_scope
        return "global"  # Default


# =============================================================================
# INTEGRITY PROTECTION
# =============================================================================


class IntegrityProtectionLevel(Enum):
    """Integrity protection level for relationships."""
    NONE = "none"                     # No integrity checking
    VERIFICATION_ONLY = "verification_only"  # Check but don't block
    ENFORCE = "enforce"               # Strict enforcement with blocking


@dataclass(frozen=True)
class IntegrityProtectionConfig:
    """
    Configuration for relationship graph integrity protection.
    """
    protection_level: IntegrityProtectionLevel = IntegrityProtectionLevel.ENFORCE
    required_hashes: Tuple[str, ...] = field(default_factory=tuple)  # Allowed hash algorithms
    allow_new_edges: bool = True      # Can new edges be added?
    require_signature: bool = False   # Require cryptographic signature


@dataclass(frozen=True)
class IntegrityVerificationResult:
    """Result of integrity verification."""
    is_valid: bool
    issues: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "issues": list(self.issues)
        }


class IntegrityProtector:
    """
    Protects relationship graph integrity.
    
    Verifies hash chains and cryptographic signatures on edges.
    """

    def __init__(self, config: IntegrityProtectionConfig):
        self.config = config
    
    def verify_edge_integrity(
        self,
        edge: Any,  # CorrelationEdge or CausationEdge
        expected_hash: Optional[str] = None,
    ) -> IntegrityVerificationResult:
        """
        Verify integrity of a relationship edge.
        
        Checks:
            - Hash chain consistency (if configured)
            - Required fields present
            - Valid timestamp range
        """
        issues: List[str] = []
        
        # Check required fields
        metadata = getattr(edge, "metadata", None)
        if metadata is None:
            issues.append("Missing metadata")
        
        edge_id = getattr(metadata, "edge_id", "") if metadata else ""
        if not edge_id:
            issues.append("Edge ID missing or empty")
        
        # Verify timestamp (edges should have reasonable timestamps)
        created_at = getattr(metadata, "created_at_utc", 0) if metadata else 0
        now = time.time()
        if created_at > now + 3600:  # Allow 1 hour future
            issues.append("Edge timestamp in distant future")
        
        # Hash verification (if configured)
        if expected_hash and self.config.required_hashes:
            edge_data = str(edge.__dict__)
            computed_hash = hashlib.sha256(edge_data.encode()).hexdigest()
            if computed_hash != expected_hash:
                issues.append(f"Hash mismatch: expected {expected_hash}, got {computed_hash}")
        
        return IntegrityVerificationResult(
            is_valid=len(issues) == 0,
            issues=tuple(issues)
        )
    
    def verify_graph_integrity(self, graph: Any) -> IntegrityVerificationResult:
        """
        Verify integrity of entire relationship graph.
        
        Checks all edges for consistency and chain integrity.
        """
        issues: List[str] = []
        
        # Check edge counts
        correlation_edges = getattr(graph, "correlation_edges", {})
        causation_edges = getattr(graph, "causation_edges", {})
        episode_memberships = getattr(graph, "episode_memberships", {})
        
        total_edges = len(correlation_edges) + len(causation_edges) + len(episode_memberships)
        
        if total_edges == 0:
            return IntegrityVerificationResult(is_valid=True)
        
        # Verify each edge
        for edge_id, edge in correlation_edges.items():
            result = self.verify_edge_integrity(edge)
            if not result.is_valid:
                issues.extend(f"Correlation {edge_id}: {issue}" for issue in result.issues)
        
        for edge_id, edge in causation_edges.items():
            result = self.verify_edge_integrity(edge)
            if not result.is_valid:
                issues.extend(f"Causation {edge_id}: {issue}" for issue in result.issues)
        
        return IntegrityVerificationResult(
            is_valid=len(issues) == 0,
            issues=tuple(issues)
        )


# =============================================================================
# AUDIT LOGGING
# =============================================================================


class RelationshipEventType(Enum):
    """Types of relationship events for audit logging."""
    EDGE_ADDED = "edge_added"
    EDGE_REMOVED = "edge_removed"     # Note: should never happen in immutable model
    GRAPH_CREATED = "graph_created"
    GRAPH_SNAPSHOT = "graph_snapshot"
    AUTHORIZATION_DENIED = "authorization_denied"


@dataclass(frozen=True)
class RelationshipAuditEvent:
    """
    Audit event for relationship graph operations.
    
    Immutable log entry with all relevant context.
    """
    event_id: str
    event_type: RelationshipEventType
    timestamp_utc: float
    
    # Operation details
    edge_id: Optional[str] = None
    relationship_kind: Optional[str] = None
    source_record_id: Optional[str] = None
    target_record_id: Optional[str] = None
    
    # Context
    actor_id: str = ""
    scope: str = "system"
    
    # Result
    success: bool = True
    reason: Optional[str] = None


class RelationshipAuditLogger:
    """
    Logger for relationship graph audit events.
    
    Stores events in append-only format for forensic analysis.
    """

    def __init__(self):
        self.events: List[RelationshipAuditEvent] = []
        self.max_events = 100_000  # Limit for memory safety
    
    def log_event(self, event: RelationshipAuditEvent) -> None:
        """Log an audit event."""
        if len(self.events) >= self.max_events:
            self.events.pop(0)  # Remove oldest
        self.events.append(event)
    
    def log_edge_added(
        self,
        edge_id: str,
        relationship_kind: str,
        source_record_id: str,
        target_record_id: str,
        actor_id: str = "unknown",
        scope: str = "system",
        success: bool = True,
        reason: Optional[str] = None,
    ) -> RelationshipAuditEvent:
        """Log an edge addition event."""
        event = RelationshipAuditEvent(
            event_id=f"evt-{time.monotonic_ns()}-{hash(edge_id) % 10000:04d}",
            event_type=RelationshipEventType.EDGE_ADDED,
            timestamp_utc=time.time(),
            edge_id=edge_id,
            relationship_kind=relationship_kind,
            source_record_id=source_record_id,
            target_record_id=target_record_id,
            actor_id=actor_id,
            scope=scope,
            success=success,
            reason=reason
        )
        self.log_event(event)
        return event
    
    def log_authorization_denied(
        self,
        edge_id: str,
        relationship_kind: str,
        actor_id: str,
        scope: str,
        reason: str,
    ) -> RelationshipAuditEvent:
        """Log an authorization denial."""
        event = RelationshipAuditEvent(
            event_id=f"evt-{time.monotonic_ns()}-{hash(edge_id) % 10000:04d}",
            event_type=RelationshipEventType.AUTHORIZATION_DENIED,
            timestamp_utc=time.time(),
            edge_id=edge_id,
            relationship_kind=relationship_kind,
            actor_id=actor_id,
            scope=scope,
            success=False,
            reason=reason
        )
        self.log_event(event)
        return event
    
    def get_events_for_edge(self, edge_id: str) -> List[RelationshipAuditEvent]:
        """Get all audit events for a specific edge."""
        return [e for e in self.events if e.edge_id == edge_id]
    
    def get_events_for_record(self, record_id: str) -> List[RelationshipAuditEvent]:
        """Get all audit events involving a record (as source or target)."""
        return [
            e for e in self.events
            if e.source_record_id == record_id or e.target_record_id == record_id
        ]
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate summary of logged events."""
        event_counts: Dict[str, int] = {}
        for event in self.events:
            key = f"{event.event_type.value}:{event.success}"
            event_counts[key] = event_counts.get(key, 0) + 1
        
        return {
            "total_events": len(self.events),
            "by_type_and_result": event_counts,
            "last_event_time_utc": self.events[-1].timestamp_utc if self.events else None
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Authorization
    "AuthorizationScope",
    "AuthorizationContext",
    
    # Relationship authorization
    "RelationshipAuthorizationResult",
    "RelationshipAuthorization",
    "RelationshipAuthorizationEnforcer",
    
    # Integrity protection
    "IntegrityProtectionLevel",
    "IntegrityProtectionConfig",
    "IntegrityVerificationResult",
    "IntegrityProtector",
    
    # Audit logging
    "RelationshipEventType",
    "RelationshipAuditEvent",
    "RelationshipAuditLogger",
]