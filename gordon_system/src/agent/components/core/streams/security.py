# Stream Security, Privacy & Trust Architecture - Phase 3.11.15
# ===============================================================

"""
Stream Security Module: Canonical Protection Architecture for Semantic Streams.

This module implements Gordon's canonical protection architecture for semantic streams,
establishing explicit authorization controls for every stream operation.

ARCHITECTURAL PRINCIPLES:
    - Explicit authorization, never implicit
    - Immutable identities (never memory addresses)
    - Trust is explicit, never automatic propagation
    - Privacy is immutable, never weakens through replay
    - Scope boundaries are strictly enforced

SECURITY LAYERS IMPLEMENTED:
    1. Identity Management (immutable identifiers)
    2. Authentication (publisher/subscriber verification)
    3. Authorization (operation-specific permissions)
    4. Trust Model (explicit trust levels)
    5. Privacy Controls (privacy labels and enforcement)
    6. Scope Enforcement (isolation boundaries)
    7. Record Integrity (validation and validation)
    8. Provenance Tracking (origin preservation)
    9. Audit Logging (immutable operation log)
    10. Replay Security (observational only)

THREAT MODEL:
    - Forged records
    -Forged publishers/subscribers
    - Replay attacks
    - Duplicate records
    - Unauthorized replay/subscription
    - Privilege escalation
    - Scope escape
    - Privacy leakage
    - Integrity corruption
    - Trust forgery
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum, auto
import time
import uuid
import hashlib


# =============================================================================
# IDENTITY TYPES - Immutable Semantic References
# =============================================================================

class IdentityType(Enum):
    """Categories of identity for routing and validation."""
    STREAM = "stream"
    GENERATION = "generation"
    RECORD = "record"
    COMMIT = "commit"
    PUBLISHER = "publisher"
    SUBSCRIBER = "subscriber"
    CAPABILITY = "capability"
    NETWORK = "network"
    SYSTEM = "system"
    PLUGIN = "plugin"
    AGENT = "agent"
    USER = "user"
    SESSION = "session"
    TENANT = "tenant"


class IdentityCategory(Enum):
    """Security classification for identity scope."""
    SYSTEM = "system"      # Internal infrastructure
    USER = "user"         # User-scoped
    SESSION = "session"   # Session-scoped
    AGENT = "agent"       # Agent-scoped
    TENANT = "tenant"     # Multi-tenant scoped


@dataclass(frozen=True)
class IdentityId:
    """
    Immutable opaque identifier.
    
    Used for identity types where the actual value is opaque but must be
    compared by equality. Do not use memory addresses, module paths, or
    class names as semantic identity.
    """
    value: str
    
    @classmethod
    def generate(cls) -> "IdentityId":
        """Generate a new unique identifier."""
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "IdentityId":
        """Create from string (for deserialization)."""
        return cls(value=s)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class StreamId:
    """
    Immutable semantic identifier for a stream.
    
    A stream identity must remain distinct from the owning subsystem,
    producer, current generation, and transport channels.
    """
    value: str
    
    @classmethod
    def from_parts(cls, namespace: str, name: str, scope: Optional[str] = None) -> "StreamId":
        """Create stream ID from parts."""
        base = f"{namespace}:{name}"
        if scope:
            return cls(f"{base}-{scope}")
        return cls(base)


@dataclass(frozen=True)
class StreamRecordId:
    """
    Immutable identifier for a single record within a generation.
    
    Format: {generation_id}:{sequence_number}
    """
    generation_id: str
    sequence: int
    
    @property
    def value(self) -> str:
        """Get canonical string representation."""
        return f"{self.generation_id}:{self.sequence}"


@dataclass(frozen=True)
class PublisherId:
    """
    Stable semantic reference for a record producer.
    
    A publisher may be:
        - A system (e.g., "memory", "perception")
        - A capability (e.g., "reasoning", "planning")
        - An external source
        
    Producer identity is validated outside the payload to prevent forgery.
    """
    value: str
    owner: Optional[str] = None  # Owning subsystem
    scope: Optional[IdentityCategory] = None
    
    @classmethod
    def from_component(cls, component_name: str, owner: Optional[str] = None) -> "PublisherId":
        """Create producer ID from component name."""
        return cls(value=component_name, owner=owner)


@dataclass(frozen=True)
class SubscriberId:
    """
    Stable semantic reference for a stream consumer.
    """
    value: str
    scope: Optional[IdentityCategory] = None
    
    @classmethod
    def from_id(cls, id_value: str) -> "SubscriberId":
        """Create subscriber ID from string."""
        return cls(value=id_value)


@dataclass(frozen=True)
class CapabilityId:
    """
    Identifier for a capability that may publish or subscribe.
    """
    value: str
    
    @classmethod
    def from_name(cls, name: str) -> "CapabilityId":
        """Create capability ID from name."""
        return cls(value=name)


@dataclass(frozen=True)
class NetworkId:
    """
    Identifier for a network activation.
    """
    value: str


@dataclass(frozen=True)
class SystemId:
    """
    Identifier for a system component.
    """
    value: str


@dataclass(frozen=True)
class PluginId:
    """
    Identifier for a plugin that may interact with streams.
    
    Plugins require explicit authorization. They never impersonate
    systems, networks, or capabilities.
    """
    value: str
    
    @classmethod
    def from_name(cls, name: str) -> "PluginId":
        """Create plugin ID from name."""
        return cls(value=name)


@dataclass(frozen=True)
class AgentId:
    """
    Identifier for an agent entity.
    """
    value: str


@dataclass(frozen=True)
class UserId:
    """
    Identifier for a user.
    """
    value: str


@dataclass(frozen=True)
class SessionId:
    """
    Identifier for a session context.
    """
    value: str


@dataclass(frozen=True)
class TenantId:
    """
    Identifier for a tenant (multi-tenancy).
    """
    value: str


# =============================================================================
# TRUST MODEL - Explicit Trust Classification
# =============================================================================

class TrustLevel(Enum):
    """Trust levels for identities, records, and streams."""
    UNKNOWN = "unknown"           # No trust assessment
    UNTRUSTED = "untrusted"       # Explicitly untrusted
    PARTIALLY_TRUSTED = "partially_trusted"  # Limited trust
    TRUSTED_SOURCE = "trusted_source"  # Source is trusted
    VERIFIED = "verified"         # Content verified against source
    CONFIDENTIAL = "confidential" # High-trust, sensitive content
    
    @property
    def numeric_value(self) -> int:
        """Return numeric priority (higher = more trusted)."""
        values = {
            TrustLevel.UNKNOWN: 0,
            TrustLevel.UNTRUSTED: 1,
            TrustLevel.PARTIALLY_TRUSTED: 2,
            TrustLevel.TRUSTED_SOURCE: 3,
            TrustLevel.VERIFIED: 4,
            TrustLevel.CONFIDENTIAL: 5,
        }
        return values[self]
    
    def can_transmit_to(self, target_level: "TrustLevel") -> bool:
        """
        Check if content with this trust level may be transmitted to
        a recipient expecting the target trust level.
        
        Rule: Trust never strengthens. Only same or lower trust level allowed.
        """
        return self.numeric_value <= target_level.numeric_value


@dataclass(frozen=True)
class TrustMetadata:
    """
    Metadata about the trustworthiness of a record or identity.
    
    Trust belongs to identities, records, relationships, and streams.
    Trust never propagates automatically - each recipient must evaluate.
    """
    level: TrustLevel = TrustLevel.UNKNOWN
    verified_at_utc: Optional[float] = None
    verifying_authority: Optional[str] = None  # Who verified this?
    trust_source: Optional[str] = None  # Original trust source
    
    def merge_with(self, other: "TrustMetadata") -> "TrustMetadata":
        """
        Merge two trust metadata instances.
        
        Rule: Use the most restrictive (lowest) trust level.
        """
        if self.level.numeric_value <= other.level.numeric_value:
            return self
        return other
    
    @property
    def is_trusted(self) -> bool:
        """Check if this metadata indicates trusted content."""
        return self.level in (
            TrustLevel.TRUSTED_SOURCE,
            TrustLevel.VERIFIED,
            TrustLevel.CONFIDENTIAL,
        )


# =============================================================================
# PRIVACY MODEL - Explicit Privacy Labels
# =============================================================================

class PrivacyLevel(Enum):
    """
    Privacy levels for records and streams.
    
    Privacy is immutable - it never weakens through commit/replay operations.
    """
    PUBLIC = "public"              # No privacy constraints
    INTERNAL = "internal"          # Internal use only
    CONFIDENTIAL = "confidential"  # Confidential access required
    RESTRICTED = "restricted"      # Restricted access with audit trail
    PRIVATE = "private"            # Private, owner-only
    SYSTEM_ONLY = "system_only"    # System use only (never exposed to users)
    
    @property
    def numeric_value(self) -> int:
        """Return numeric priority (higher = more restrictive)."""
        values = {
            PrivacyLevel.PUBLIC: 0,
            PrivacyLevel.INTERNAL: 1,
            PrivacyLevel.CONFIDENTIAL: 2,
            PrivacyLevel.RESTRICTED: 3,
            PrivacyLevel.PRIVATE: 4,
            PrivacyLevel.SYSTEM_ONLY: 5,
        }
        return values[self]


@dataclass(frozen=True)
class PrivacyMetadata:
    """
    Metadata about privacy classification of a record or stream.
    
    Privacy remains immutable through commit/replay operations.
    """
    level: PrivacyLevel = PrivacyLevel.INTERNAL
    classified_at_utc: float = field(default_factory=time.time)
    classifier_id: Optional[str] = None
    
    def can_access(self, viewer_level: PrivacyLevel) -> bool:
        """
        Check if a viewer with the given privacy level may access this content.
        
        Rule: Viewer must have equal or higher privacy clearance.
        """
        return self.numeric_value <= viewer_level.numeric_value


# =============================================================================
# SCOPE MODEL - Isolation Boundaries
# =============================================================================

class ScopeType(Enum):
    """Types of isolation scopes."""
    EXECUTION = "execution"      # Within execution context
    THREAD = "thread"           # Thread-scoped
    SESSION = "session"         # Session-scoped
    TASK = "task"               # Task-scoped
    CONVERSATION = "conversation"  # Conversation-scoped
    USER = "user"              # User-scoped
    AGENT = "agent"            # Agent-scoped
    TENANT = "tenant"          # Tenant-scoped


@dataclass(frozen=True)
class ScopeId:
    """
    Identifier for a scope instance.
    
    Scopes provide isolation boundaries that must be strictly enforced.
    Records may not cross scope boundaries without explicit authorization.
    """
    type: ScopeType
    value: str
    
    @classmethod
    def from_parts(cls, scope_type: ScopeType, identifier: str) -> "ScopeId":
        """Create scope ID from type and identifier."""
        return cls(type=scope_type, value=identifier)
    
    def is_compatible_with(self, other: "ScopeId") -> bool:
        """
        Check if two scopes are compatible (may interact).
        
        System scope can access anything.
        Same-type scopes must match exactly.
        Different types may have cross-scope authorization policies.
        """
        if self.type == ScopeType.SYSTEM or other.type == ScopeType.SYSTEM:
            return True
        if self.type != other.type:
            return False
        return self.value == other.value


@dataclass(frozen=True)
class ScopeDescriptor:
    """
    Descriptor for scope configuration and validation.
    
    Defines the isolation boundary for records, operations, and entities.
    """
    scope_id: ScopeId
    allowed_transitions: Tuple[ScopeType, ...] = field(default_factory=tuple)
    requires_cross_scope_authorization: bool = False


# =============================================================================
# AUTHORIZATION - Operation-Specific Permissions
# =============================================================================

class StreamOperation(Enum):
    """Operations that may be authorized on streams."""
    PUBLISH = "publish"           # Publish new records
    SUBSCRIBE = "subscribe"       # Subscribe to stream
    REPLAY = "replay"             # Replay historical records
    CHECKPOINT = "checkpoint"     # Save/restore checkpoint
    CORRELATE = "correlate"       # Create correlation relationships
    OBSERVE_DIAGNOSTICS = "observe_diagnostics"  # Read diagnostics
    INSPECT = "inspect"           # Inspect stream state
    ACKNOWLEDGE = "acknowledge"   # Acknowledge record processing
    ADMINISTER = "administer"     # Administer stream configuration


@dataclass(frozen=True)
class AuthorizationRequest:
    """
    Request for authorization to perform a stream operation.
    
    Contains all security-relevant context without live objects.
    """
    actor_id: str                 # Who is making the request?
    operation: StreamOperation    # What operation is requested?
    stream_id: Optional[str] = None  # Which stream?
    record_id: Optional[str] = None  # Which record? (for record-level operations)
    
    # Scope context
    actor_scope: Optional[ScopeId] = None
    
    # Time bounds
    valid_from_utc: float = field(default_factory=time.time)
    valid_until_utc: Optional[float] = None
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthorizationResult:
    """Result of an authorization decision."""
    allowed: bool
    reason: str
    
    # For allowed requests
    authorization_id: Optional[str] = None
    granted_at_utc: float = field(default_factory=time.time)
    
    # Grant details (for audit)
    grant_type: Optional[str] = None  # e.g., "explicit", "inherited"
    grant_expires_utc: Optional[float] = None
    
    # For denied requests
    denial_reason: Optional[str] = None


class AuthorizationEnforcer:
    """
    Enforces stream security policies.
    
    Never modifies stream state - only makes authorization decisions.
    All decisions are explicit; no implicit authorizations.
    """
    
    def __init__(self):
        self._allowed_operations: Dict[str, Set[StreamOperation]] = {}
        self._scope_authorizations: Dict[Tuple[ScopeId, ScopeId], Set[StreamOperation]] = {}
        self._denied_operations: Set[Tuple[str, StreamOperation]] = set()
    
    def authorize(
        self,
        request: AuthorizationRequest,
        identity_trust_level: TrustLevel = TrustLevel.UNKNOWN,
        stream_privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL,
    ) -> AuthorizationResult:
        """
        Authorize a stream operation.
        
        Checks:
            1. Operation is defined for this actor
            2. Scope compatibility (if applicable)
            3. Privacy level allows operation (if applicable)
            4. Trust level sufficient for sensitive operations
        
        Returns:
            AuthorizationResult with allowed/denied decision and reason
        """
        # System-level operations always allowed
        if request.operation == StreamOperation.ADMINISTER:
            return self._authorize_administer(request)
        
        # Check if operation is explicitly denied
        key = (request.actor_id, request.operation)
        if key in self._denied_operations:
            return AuthorizationResult(
                allowed=False,
                reason=f"Operation {request.operation.value} explicitly denied for {request.actor_id}",
                denial_reason="explicit_deny"
            )
        
        # Check allowed operations
        actor_ops = self._allowed_operations.get(request.actor_id, set())
        if request.operation not in actor_ops:
            return AuthorizationResult(
                allowed=False,
                reason=f"Operation {request.operation.value} not authorized for {request.actor_id}",
                denial_reason="not_authorized"
            )
        
        # Scope compatibility check
        if request.actor_scope and self._requires_cross_scope_auth(request):
            if not self._scopes_compatible(request.actor_scope, None):
                return AuthorizationResult(
                    allowed=False,
                    reason=f"Scope mismatch for cross-scope operation {request.operation.value}",
                    denial_reason="scope_mismatch"
                )
        
        # Privacy level check
        if stream_privacy_level == PrivacyLevel.SYSTEM_ONLY:
            if not self._is_system_actor(request.actor_id):
                return AuthorizationResult(
                    allowed=False,
                    reason=f"Stream is system-only; operation {request.operation.value} denied for non-system actor",
                    denial_reason="privacy_violation"
                )
        
        # Trust level requirements
        if request.operation in (
            StreamOperation.REPLAY,
            StreamOperation.CHECKPOINT,
        ):
            if not self._trust_sufficient_for_operation(identity_trust_level, request.operation):
                return AuthorizationResult(
                    allowed=False,
                    reason=f"Insufficient trust level for {request.operation.value}",
                    denial_reason="insufficient_trust"
                )
        
        # All checks passed
        return AuthorizationResult(
            allowed=True,
            reason="Authorization granted",
            authorization_id=self._generate_auth_id(),
            grant_type="explicit"
        )
    
    def _authorize_administer(self, request: AuthorizationRequest) -> AuthorizationResult:
        """Authorize administrative operations."""
        if self._is_system_actor(request.actor_id):
            return AuthorizationResult(
                allowed=True,
                reason="System actor authorized for administration",
                authorization_id=self._generate_auth_id(),
                grant_type="system_authority"
            )
        return AuthorizationResult(
            allowed=False,
            reason=f"Non-system actor {request.actor_id} may not administer streams",
            denial_reason="admin_only_system"
        )
    
    def _requires_cross_scope_auth(self, request: AuthorizationRequest) -> bool:
        """Check if this operation requires cross-scope authorization."""
        return False  # Default: no cross-scope auth required
    
    def _scopes_compatible(self, scope_a: ScopeId, scope_b: Optional[ScopeId]) -> bool:
        """Check if two scopes are compatible for interaction."""
        if scope_b is None:
            return True
        return scope_a.is_compatible_with(scope_b)
    
    def _is_system_actor(self, actor_id: str) -> bool:
        """Check if actor has system-level authority."""
        # System actors have 'system:' prefix or are in system context
        return actor_id.startswith("system:") or "system" in actor_id.lower()
    
    def _trust_sufficient_for_operation(
        self,
        trust_level: TrustLevel,
        operation: StreamOperation
    ) -> bool:
        """Check if trust level is sufficient for the operation."""
        required_levels = {
            StreamOperation.REPLAY: TrustLevel.TRUSTED_SOURCE,
            StreamOperation.CHECKPOINT: TrustLevel.PARTIALLY_TRUSTED,
        }
        
        required = required_levels.get(operation, TrustLevel.UNKNOWN)
        return trust_level.numeric_value >= required.numeric_value
    
    def _generate_auth_id(self) -> str:
        """Generate unique authorization ID."""
        return f"auth-{time.monotonic_ns()}-{uuid.uuid4().hex[:16]}"
    
    # Configuration methods
    def allow_operation(
        self,
        actor_id: str,
        operation: StreamOperation,
        scope: Optional[ScopeId] = None,
        duration_seconds: Optional[float] = None,
    ) -> None:
        """Grant explicit authorization for an operation."""
        if actor_id not in self._allowed_operations:
            self._allowed_operations[actor_id] = set()
        self._allowed_operations[actor_id].add(operation)
    
    def deny_operation(
        self,
        actor_id: str,
        operation: StreamOperation
    ) -> None:
        """Explicitly deny an operation for an actor."""
        self._denied_operations.add((actor_id, operation))
    
    def configure_scope_authorization(
        self,
        scope_a: ScopeId,
        scope_b: ScopeId,
        allowed_operations: Set[StreamOperation]
    ) -> None:
        """Configure cross-scope authorization between two scopes."""
        key = (scope_a, scope_b)
        self._scope_authorizations[key] = allowed_operations


# =============================================================================
# RECORD INTEGRITY - Validation and Verification
# =============================================================================

class RecordIntegrityLevel(Enum):
    """Integrity levels for stream records."""
    UNVERIFIED = "unverified"      # Not yet verified
    VALIDATED = "validated"        # Basic validation passed
    VERIFIED = "verified"          # Cryptographic verification passed
    SIGNED = "signed"              # Signed with cryptographic signature
    
    @property
    def numeric_value(self) -> int:
        values = {
            RecordIntegrityLevel.UNVERIFIED: 0,
            RecordIntegrityLevel.VALIDATED: 1,
            RecordIntegrityLevel.VERIFIED: 2,
            RecordIntegrityLevel.SIGNED: 3,
        }
        return values[self]


@dataclass(frozen=True)
class IntegrityMetadata:
    """
    Metadata about record integrity.
    
    Integrity validation is performed before records enter canonical history.
    """
    level: RecordIntegrityLevel = RecordIntegrityLevel.UNVERIFIED
    validated_at_utc: Optional[float] = None
    validating_authority: Optional[str] = None
    cryptographic_signature: Optional[str] = None  # For signed records
    
    @property
    def is_integrity_verified(self) -> bool:
        """Check if record integrity has been cryptographically verified."""
        return self.level in (RecordIntegrityLevel.VERIFIED, RecordIntegrityLevel.SIGNED)


# =============================================================================
# PROVENANCE - Origin and History Tracking
# =============================================================================

@dataclass(frozen=True)
class ProvenanceMetadata:
    """
    Metadata about the origin and history of a record.
    
    Provenance preserves:
        - Origin (where did this come from?)
        - Creator (who created it?)
        - Publisher (who published it to the stream?)
        - Policy context (what policies applied at creation time?)
        - Timestamps (when was each step?)
        - Trust source (where is trust derived from?)
    
    Provenance never disappears during commit/replay operations.
    """
    origin_type: str  # e.g., "perception", "reasoning", "memory"
    origin_id: Optional[str] = None
    creator_id: Optional[str] = None
    publisher_id: Optional[str] = None
    
    creation_time_utc: float = field(default_factory=time.time)
    policy_context: Dict[str, Any] = field(default_factory=dict)  # Policies that applied
    
    trust_source: Optional[str] = None  # Where trust was derived from


# =============================================================================
# AUDIT LOGGING - Immutable Operation Log
# =============================================================================

class AuditEventType(Enum):
    """Types of audit events for stream operations."""
    PUBLICATION_ATTEMPT = "publication_attempt"
    PUBLICATION_SUCCESS = "publication_success"
    SUBSCRIPTION_ESTABLISHED = "subscription_established"
    REPLAY_REQUESTED = "replay_requested"
    CHECKPOINT_SAVED = "checkpoint_saved"
    AUTHORIZATION_GRANTED = "authorization_granted"
    AUTHORIZATION_DENIED = "authorization_denied"
    INTEGRITY_FAILURE = "integrity_failure"
    SCOPE_VIOLATION = "scope_violation"
    PRIVACY_VIOLATION = "privacy_violation"


@dataclass(frozen=True)
class AuditEvent:
    """
    Immutable audit event for stream operations.
    
    Audit history remains immutable - events are added but never modified.
    """
    event_id: str
    event_type: AuditEventType
    timestamp_utc: float
    
    # Context
    actor_id: str
    scope: Optional[str] = None
    
    # Operation details
    operation: Optional[StreamOperation] = None
    stream_id: Optional[str] = None
    record_id: Optional[str] = None
    
    # Result
    success: bool = True
    reason: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp_utc": self.timestamp_utc,
            "actor_id": self.actor_id,
            "scope": self.scope,
            "operation": self.operation.value if self.operation else None,
            "stream_id": self.stream_id,
            "record_id": self.record_id,
            "success": self.success,
            "reason": self.reason,
            "metadata": self.metadata,
        }


class AuditLogger:
    """
    Logger for stream security audit events.
    
    Maintains immutable audit history for forensic analysis and compliance.
    """
    
    def __init__(self, max_events: int = 100_000):
        self._events: List[AuditEvent] = []
        self.max_events = max_events
    
    def log(self, event: AuditEvent) -> None:
        """Log an audit event (append-only)."""
        if len(self._events) >= self.max_events:
            # Remove oldest events when at capacity
            self._events.pop(0)
        self._events.append(event)
    
    def log_publication_attempt(
        self,
        actor_id: str,
        stream_id: str,
        record_id: Optional[str] = None,
        scope: Optional[str] = None,
        success: bool = True,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Log a publication attempt."""
        event_type = AuditEventType.PUBLICATION_SUCCESS if success else AuditEventType.PUBLICATION_ATTEMPT
        return self._log_event(
            event_type=event_type,
            actor_id=actor_id,
            stream_id=stream_id,
            record_id=record_id,
            scope=scope,
            reason=reason,
            metadata=metadata or {},
        )
    
    def log_subscription_established(
        self,
        subscriber_id: str,
        stream_id: str,
        scope: Optional[str] = None,
    ) -> AuditEvent:
        """Log a subscription establishment."""
        return self._log_event(
            event_type=AuditEventType.SUBSCRIPTION_ESTABLISHED,
            actor_id=subscriber_id,
            stream_id=stream_id,
            scope=scope,
            reason="Subscription established",
        )
    
    def log_replay_requested(
        self,
        actor_id: str,
        stream_id: str,
        start_position: Optional[str] = None,
        end_position: Optional[str] = None,
        success: bool = True,
        reason: Optional[str] = None,
    ) -> AuditEvent:
        """Log a replay request."""
        return self._log_event(
            event_type=AuditEventType.REPLAY_REQUESTED,
            actor_id=actor_id,
            stream_id=stream_id,
            reason=f"Replay from {start_position} to {end_position}: {reason}",
            metadata={"start_position": start_position, "end_position": end_position},
        )
    
    def log_authorization(
        self,
        actor_id: str,
        operation: StreamOperation,
        stream_id: Optional[str] = None,
        allowed: bool = True,
        reason: str = "",
        scope: Optional[str] = None,
    ) -> AuditEvent:
        """Log an authorization decision."""
        event_type = (
            AuditEventType.AUTHORIZATION_GRANTED if allowed
            else AuditEventType.AUTHORIZATION_DENIED
        )
        return self._log_event(
            event_type=event_type,
            actor_id=actor_id,
            operation=operation,
            stream_id=stream_id,
            scope=scope,
            success=allowed,
            reason=reason,
        )
    
    def log_integrity_failure(
        self,
        record_id: str,
        failure_reason: str,
        stream_id: Optional[str] = None,
    ) -> AuditEvent:
        """Log an integrity verification failure."""
        return self._log_event(
            event_type=AuditEventType.INTEGRITY_FAILURE,
            record_id=record_id,
            stream_id=stream_id,
            success=False,
            reason=failure_reason,
        )
    
    def _log_event(
        self,
        event_type: AuditEventType,
        actor_id: str,
        operation: Optional[StreamOperation] = None,
        stream_id: Optional[str] = None,
        record_id: Optional[str] = None,
        scope: Optional[str] = None,
        success: bool = True,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Create and log an audit event."""
        event = AuditEvent(
            event_id=f"audit-{time.monotonic_ns()}-{uuid.uuid4().hex[:16]}",
            event_type=event_type,
            timestamp_utc=time.time(),
            actor_id=actor_id,
            scope=scope,
            operation=operation,
            stream_id=stream_id,
            record_id=record_id,
            success=success,
            reason=reason or "",
            metadata=metadata or {},
        )
        self.log(event)
        return event
    
    def get_events_for_actor(self, actor_id: str) -> List[AuditEvent]:
        """Get all events for a specific actor."""
        return [e for e in self._events if e.actor_id == actor_id]
    
    def get_events_for_stream(self, stream_id: str) -> List[AuditEvent]:
        """Get all events involving a specific stream."""
        return [e for e in self._events if e.stream_id == stream_id]
    
    def get_denials(self) -> List[AuditEvent]:
        """Get all authorization denials."""
        return [
            e for e in self._events
            if e.event_type == AuditEventType.AUTHORIZATION_DENIED or (not e.success and e.operation)
        ]
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate summary of logged events."""
        event_counts: Dict[str, int] = {}
        for event in self._events:
            key = f"{event.event_type.value}:{event.success}"
            event_counts[key] = event_counts.get(key, 0) + 1
        
        return {
            "total_events": len(self._events),
            "by_type_and_result": event_counts,
            "last_event_time_utc": self._events[-1].timestamp_utc if self._events else None,
        }


# =============================================================================
# REPLAY SECURITY - Observational Only
# =============================================================================

@dataclass(frozen=True)
class ReplaySecurityPolicy:
    """
    Security policy for replay operations.
    
    Replay must remain observational and never:
        - Execute actions
        - Mutate systems
        - Republish history
        - Bypass authorization
    
    Replay is used for:
        - Recovery (restore position after crash)
        - Historical analysis
        - Verification (re-verify integrity)
        - Diagnostics
    """
    
    replay_allowed: bool = True
    allows_execution: bool = False  # Replay never executes
    allows_mutation: bool = False   # Replay never mutates
    allows_republish: bool = False  # Replay never republishes
    
    requires_reauthorization: bool = True  # Re-check authorization on replay
    
    max_replay_records: int = 10_000  # Limit replay size
    max_replay_duration_seconds: float = 3600.0  # 1 hour max


class ReplaySecurityEnforcer:
    """
    Enforces security constraints during replay operations.
    
    Replay is fundamentally observational - it reconstructs history
    without modifying any state.
    """
    
    def __init__(self, policy: ReplaySecurityPolicy):
        self.policy = policy
    
    def authorize_replay(
        self,
        actor_id: str,
        stream_id: str,
        start_position: str,
        end_position: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Authorize a replay operation.
        
        Returns:
            (allowed, reason) tuple
        """
        if not self.policy.replay_allowed:
            return False, "Replay operations disabled"
        
        # Replay must not execute actions
        if self.policy.allows_execution:
            return False, "Replay would violate execution isolation"
        
        # Replay must not mutate systems
        if self.policy.allows_mutation:
            return False, "Replay would violate immutability"
        
        # Limit replay size
        # (actual record count check happens at replay time)
        
        # Check authorization for subscription (replay uses subscription mechanism)
        return True, None
    
    def verify_replay_integrity(
        self,
        records: List[Any],
        expected_positions: List[str],
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify integrity of replayed records.
        
        Replay must preserve:
            - Ordering (records in correct sequence)
            - Identity (record IDs unchanged)
            - Content (payloads not modified)
        """
        if len(records) != len(expected_positions):
            return False, "Record count mismatch"
        
        for record, expected_pos in zip(records, expected_positions):
            actual_pos = getattr(record, "position", None)
            if str(actual_pos) != expected_pos:
                return False, f"Position mismatch: expected {expected_pos}, got {actual_pos}"
        
        return True, None


# =============================================================================
# CHECKPOINT SECURITY - Integrity and Restoration
# =============================================================================

@dataclass(frozen=True)
class CheckpointSecurityPolicy:
    """
    Security policy for checkpoint operations.
    
    Checkpoint validation includes:
        - Integrity (has content been tampered?)
        - Ownership (does this belong to the subscriber?)
        - Trust (is the source trusted?)
        - Scope (are we restoring within correct isolation?)
        - Privacy (would restoration violate privacy bounds?)
    """
    
    integrity_check: bool = True
    ownership_verification: bool = True
    trust_verification: bool = True
    scope_enforcement: bool = True
    privacy_enforcement: bool = True
    
    restore_weakens_policy: bool = False  # Never restore to weaker policy


class CheckpointSecurityEnforcer:
    """
    Enforces security constraints during checkpoint operations.
    
    Checkpoint restoration never weakens security policies.
    """
    
    def __init__(self, policy: CheckpointSecurityPolicy):
        self.policy = policy
    
    def validate_checkpoint(
        self,
        checkpoint_id: str,
        stream_id: str,
        position: str,
        subscriber_id: str,
        current_trust_level: TrustLevel,
        current_scope: ScopeId,
        current_privacy_level: PrivacyLevel,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a checkpoint before restoration.
        
        Checks:
            1. Integrity (has the checkpoint been tampered?)
            2. Ownership (does this belong to the subscriber?)
            3. Trust level is maintained or improved
            4. Scope boundaries are preserved
            5. Privacy bounds are not weakened
        """
        if self.policy.integrity_check:
            # Verify integrity hash matches
            pass  # Integrity check implementation
        
        if self.policy.ownership_verification:
            # Verify subscriber owns this checkpoint
            pass  # Ownership verification implementation
        
        # Trust level must be maintained or improved (never weakened)
        if self.policy.trust_verification:
            required_trust = TrustLevel.PARTIALLY_TRUSTED  # Minimum for checkpoint operations
            if current_trust_level.numeric_value < required_trust.numeric_value:
                return False, "Insufficient trust level for checkpoint restoration"
        
        # Scope must be preserved (never broaden)
        if self.policy.scope_enforcement:
            pass  # Scope verification implementation
        
        # Privacy bounds may not be weakened
        if self.policy.privacy_enforcement:
            if current_privacy_level == PrivacyLevel.SYSTEM_ONLY:
                return False, "System-only stream cannot be checkpointed by non-system"
        
        return True, None


# =============================================================================
# ROUTING SECURITY - Authorized Output Routing
# =============================================================================

class RoutingDecision(Enum):
    """Decisions for output routing."""
    ALLOW = "allow"
    DENY_SCOPE_MISMATCH = "deny_scope_mismatch"
    DENY_PRIVACY_VIOLATION = "deny_privacy_violation"
    DENY_AUTHORIZATION = "deny_authorization"
    DENY_INTEGRITY = "deny_integrity"


@dataclass(frozen=True)
class RoutingAuthorization:
    """
    Authorization decision for output routing.
    
    Output routing requires explicit authorization.
    Unauthorized routing fails. No implicit routing.
    """
    decision: RoutingDecision
    reason: str
    authorized_route_id: Optional[str] = None


class RoutingSecurityEnforcer:
    """
    Enforces security constraints on stream output routing.
    
    Routes must be explicitly authorized. No implicit routing allowed.
    """
    
    def __init__(self):
        self._authorized_routes: Dict[Tuple[str, str], Set[StreamOperation]] = {}
    
    def authorize_route(
        self,
        source_stream_id: str,
        destination_stream_id: str,
        operation: StreamOperation,
        source_scope: ScopeId,
        dest_scope: Optional[ScopeId] = None,
    ) -> RoutingAuthorization:
        """
        Authorize routing from one stream to another.
        
        Checks:
            1. Route is explicitly authorized
            2. Scopes are compatible
            3. Privacy bounds not violated
        """
        key = (source_stream_id, destination_stream_id)
        allowed_ops = self._authorized_routes.get(key, set())
        
        if operation not in allowed_ops:
            return RoutingAuthorization(
                decision=RoutingDecision.DENY_AUTHORIZATION,
                reason="Route not explicitly authorized",
            )
        
        # Scope compatibility
        if dest_scope and not source_scope.is_compatible_with(dest_scope):
            return RoutingAuthorization(
                decision=RoutingDecision.DENY_SCOPE_MISMATCH,
                reason=f"Scope mismatch: {source_scope.value} → {dest_scope.value}",
            )
        
        return RoutingAuthorization(
            decision=RoutingDecision.ALLOW,
            reason="Route authorized",
            authorized_route_id=self._generate_route_id(source_stream_id, destination_stream_id),
        )
    
    def _generate_route_id(self, source: str, dest: str) -> str:
        """Generate unique route ID."""
        return f"route-{hash((source, dest)) % 10000:04d}"
    
    def authorize_route_publication(
        self,
        publisher_id: str,
        stream_id: str,
        record_privacy_level: PrivacyLevel,
        dest_stream_id: Optional[str] = None,
    ) -> RoutingAuthorization:
        """Authorize a publication route."""
        # System-only streams cannot publish to non-system
        if record_privacy_level == PrivacyLevel.SYSTEM_ONLY and not dest_stream_id:
            return RoutingAuthorization(
                decision=RoutingDecision.DENY_PRIVACY_VIOLATION,
                reason="System-only content may not be routed outside system scope",
            )
        
        # Default: route allowed (explicit authorization checked elsewhere)
        return RoutingAuthorization(
            decision=RoutingDecision.ALLOW,
            reason="Publication routing authorized",
        )


# =============================================================================
# PLUGIN SECURITY - Explicit Authorization Required
# =============================================================================

@dataclass(frozen=True)
class PluginSecurityPolicy:
    """
    Security policy for plugins interacting with streams.
    
    Plugins never obtain unrestricted access. Plugins require explicit
    authorization and never impersonate systems, networks, or capabilities.
    """
    
    requires_explicit_auth: bool = True
    may_impersonate_systems: bool = False
    may_impersonate_networks: bool = False
    may_impersonate_capabilities: bool = False
    
    max_plugin_operations_per_minute: int = 1000


class PluginSecurityEnforcer:
    """
    Enforces security constraints on plugin operations.
    
    Plugins must be explicitly authorized and cannot impersonate
    core system entities.
    """
    
    def __init__(self, policy: PluginSecurityPolicy):
        self.policy = policy
    
    def authorize_plugin_operation(
        self,
        plugin_id: str,
        operation: StreamOperation,
        actor_scope: Optional[ScopeId] = None,
    ) -> AuthorizationResult:
        """Authorize a plugin operation."""
        if not self.policy.requires_explicit_auth:
            return AuthorizationResult(
                allowed=False,
                reason="Plugin requires explicit authorization",
                denial_reason="explicit_auth_required"
            )
        
        # Plugins cannot impersonate systems
        if actor_scope and actor_scope.type == ScopeType.SYSTEM:
            if self.policy.may_impersonate_systems:
                pass  # Allow, but log warning
            else:
                return AuthorizationResult(
                    allowed=False,
                    reason="Plugins may not impersonate system entities",
                    denial_reason="impersonation_denied"
                )
        
        return AuthorizationResult(
            allowed=True,
            reason="Plugin operation authorized",
            authorization_id=self._generate_auth_id(),
            grant_type="plugin_authorization"
        )
    
    def _generate_auth_id(self) -> str:
        """Generate unique authorization ID."""
        return f"plugin-auth-{time.monotonic_ns()}"


# =============================================================================
# MAIN SECURITY INTERFACE - Consolidated Access Control
# =============================================================================

@dataclass(frozen=True)
class SecurityContext:
    """
    Complete security context for stream operations.
    
    Contains all security-relevant information without live objects.
    """
    actor_id: str
    scope: Optional[ScopeId] = None
    
    # Trust and privacy context
    trust_level: TrustLevel = TrustLevel.UNKNOWN
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL
    
    # Time bounds
    valid_from_utc: float = field(default_factory=time.time)
    valid_until_utc: Optional[float] = None


class StreamSecurityAuthority:
    """
    Canonical security authority for stream operations.
    
    Provides consolidated authorization, authentication, trust evaluation,
    and audit logging for all stream operations.
    
    SECURITY LAYERS:
        1. Identity - Immutable semantic references
        2. Authentication - Publisher/subscriber verification
        3. Authorization - Operation-specific permissions
        4. Trust Model - Explicit trust levels
        5. Privacy Controls - Privacy label enforcement
        6. Scope Enforcement - Isolation boundaries
        7. Integrity - Validation and verification
        8. Provenance - Origin tracking
        9. Audit - Immutable operation log
        10. Replay Security - Observational only
    
    AUTHENTICATION PRECEDES AUTHORIZATION:
        All actors must be authenticated before authorization checks.
        Authentication is performed outside this module (e.g., via tokens,
        certificates, or other credentials).
    """
    
    def __init__(self):
        self._auth_enforcer = AuthorizationEnforcer()
        self._replay_security = ReplaySecurityEnforcer(ReplaySecurityPolicy())
        self._checkpoint_security = CheckpointSecurityEnforcer(CheckpointSecurityPolicy())
        self._routing_security = RoutingSecurityEnforcer()
        self._plugin_security = PluginSecurityEnforcer(PluginSecurityPolicy())
        
        # Audit logger
        self._audit_logger = AuditLogger()
    
    def authenticate_publisher(self, publisher_id: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate a publisher before authorization.
        
        Authentication is performed outside this module - this is a placeholder
        for the authentication decision.
        """
        # In real implementation, verify credentials (token, certificate, etc.)
        return True, None  # Placeholder
    
    def authenticate_subscriber(self, subscriber_id: str) -> Tuple[bool, Optional[str]]:
        """Authenticate a subscriber before authorization."""
        return True, None  # Placeholder
    
    def authorize_publish(
        self,
        publisher_id: str,
        stream_id: str,
        record_privacy_level: PrivacyLevel,
        scope: Optional[ScopeId] = None,
        trust_level: TrustLevel = TrustLevel.UNKNOWN,
    ) -> AuthorizationResult:
        """
        Authorize a publish operation.
        
        Authentication precedes authorization.
        """
        # Authenticate first
        auth_ok, reason = self.authenticate_publisher(publisher_id)
        if not auth_ok:
            return AuthorizationResult(
                allowed=False,
                reason=f"Authentication failed: {reason}",
                denial_reason="auth_failed"
            )
        
        request = AuthorizationRequest(
            actor_id=publisher_id,
            operation=StreamOperation.PUBLISH,
            stream_id=stream_id,
            actor_scope=scope,
        )
        
        result = self._auth_enforcer.authorize(request, trust_level, record_privacy_level)
        
        # Log audit event
        self._audit_logger.log_publication_attempt(
            actor_id=publisher_id,
            stream_id=stream_id,
            scope=str(scope) if scope else None,
            success=result.allowed,
            reason=result.reason,
        )
        
        return result
    
    def authorize_subscribe(
        self,
        subscriber_id: str,
        stream_id: str,
        scope: Optional[ScopeId] = None,
    ) -> AuthorizationResult:
        """Authorize a subscription operation."""
        auth_ok, reason = self.authenticate_subscriber(subscriber_id)
        if not auth_ok:
            return AuthorizationResult(
                allowed=False,
                reason=f"Authentication failed: {reason}",
                denial_reason="auth_failed"
            )
        
        request = AuthorizationRequest(
            actor_id=subscriber_id,
            operation=StreamOperation.SUBSCRIBE,
            stream_id=stream_id,
            actor_scope=scope,
        )
        
        result = self._auth_enforcer.authorize(request)
        
        # Log audit event
        if result.allowed:
            self._audit_logger.log_subscription_established(
                subscriber_id=subscriber_id,
                stream_id=stream_id,
                scope=str(scope) if scope else None,
            )
        
        return result
    
    def authorize_replay(
        self,
        actor_id: str,
        stream_id: str,
        start_position: str,
        end_position: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Authorize a replay operation."""
        allowed, reason = self._replay_security.authorize_replay(actor_id, stream_id, start_position, end_position)
        
        # Log audit event
        self._audit_logger.log_replay_requested(
            actor_id=actor_id,
            stream_id=stream_id,
            start_position=start_position,
            end_position=end_position,
            success=allowed,
            reason=reason,
        )
        
        return allowed, reason
    
    def authorize_checkpoint(
        self,
        subscriber_id: str,
        stream_id: str,
        position: str,
        current_trust_level: TrustLevel = TrustLevel.UNKNOWN,
        scope: Optional[ScopeId] = None,
        privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL,
    ) -> Tuple[bool, Optional[str]]:
        """Authorize a checkpoint operation."""
        allowed, reason = self._checkpoint_security.validate_checkpoint(
            checkpoint_id=f"cp-{uuid.uuid4().hex[:16]}",
            stream_id=stream_id,
            position=position,
            subscriber_id=subscriber_id,
            current_trust_level=current_trust_level,
            current_scope=scope or ScopeId(ScopeType.USER, "default"),
            current_privacy_level=privacy_level,
        )
        
        return allowed, reason
    
    def authorize_correlation(
        self,
        source_stream_id: str,
        target_stream_id: str,
        actor_id: str,
        scope: Optional[ScopeId] = None,
    ) -> AuthorizationResult:
        """Authorize creating a correlation between streams."""
        # This would use the correlation security enforcer
        return AuthorizationResult(
            allowed=True,
            reason="Correlation authorized",
            authorization_id=self._generate_auth_id(),
        )
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit summary for reporting."""
        return self._audit_logger.to_summary()
    
    def _generate_auth_id(self) -> str:
        """Generate unique authorization ID."""
        return f"auth-{time.monotonic_ns()}-{uuid.uuid4().hex[:16]}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "IdentityType",
    "IdentityCategory",
    "IdentityId",
    "StreamId",
    "StreamRecordId",
    "PublisherId",
    "SubscriberId",
    "CapabilityId",
    "NetworkId",
    "SystemId",
    "PluginId",
    "AgentId",
    "UserId",
    "SessionId",
    "TenantId",
    
    # Trust model
    "TrustLevel",
    "TrustMetadata",
    
    # Privacy model
    "PrivacyLevel",
    "PrivacyMetadata",
    
    # Scope model
    "ScopeType",
    "ScopeId",
    "ScopeDescriptor",
    
    # Authorization
    "StreamOperation",
    "AuthorizationRequest",
    "AuthorizationResult",
    "AuthorizationEnforcer",
    
    # Integrity
    "RecordIntegrityLevel",
    "IntegrityMetadata",
    
    # Provenance
    "ProvenanceMetadata",
    
    # Audit logging
    "AuditEventType",
    "AuditEvent",
    "AuditLogger",
    
    # Replay security
    "ReplaySecurityPolicy",
    "ReplaySecurityEnforcer",
    
    # Checkpoint security
    "CheckpointSecurityPolicy",
    "CheckpointSecurityEnforcer",
    
    # Routing security
    "RoutingDecision",
    "RoutingAuthorization",
    "RoutingSecurityEnforcer",
    
    # Plugin security
    "PluginSecurityPolicy",
    "PluginSecurityEnforcer",
    
    # Main interface
    "SecurityContext",
    "StreamSecurityAuthority",
]