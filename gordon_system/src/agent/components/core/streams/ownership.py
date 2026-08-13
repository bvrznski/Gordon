# Stream Ownership Model - Phase 3.11.3
# ======================================

"""
Canonical stream ownership architecture.

This module implements explicit ownership roles for semantic streams,
distinguishing between:
    - Semantic ownership (domain semantics, purpose, validation)
    - Infrastructure ownership (Core transport/storage interface)
    - Runtime ownership (scoped active instance state)
    - Authority roles (lifecycle, commit, configuration, etc.)

Ownership Model:
    One stream has exactly one semantic owner who defines its meaning.
    Core owns generic infrastructure only.
    Each scoped runtime instance has exactly one runtime owner.
    Each active stream has exactly one lifecycle authority.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
import time


# =============================================================================
# OWNERSHIP ROLES - Semantic Distinctions
# =============================================================================


class StreamOwnershipRole(Enum):
    """
    Canonical ownership roles for streams.
    
    These roles may be held by the same subsystem but remain semantically
    distinct. The model enforces explicit role separation:
        - Do not collapse into a generic "owner" field
        - Each role has specific authority boundaries
    """
    
    # Primary ownership (what does this stream MEAN?)
    SEMANTIC_OWNER = "semantic_owner"
    """Defines: purpose, domain semantics, validation rules, schemas,
       publication policy, retention requirements"""
    
    INFRASTRUCTURE_OWNER = "infrastructure_owner"
    """Core owns: transport layer, storage interface, cursor management,
       checkpoint infrastructure, generic recovery seams"""
    
    RUNTIME_OWNER = "runtime_owner"
    """Scoped instance owns: active lifecycle state, generation reference,
       commit authority binding, runtime registration, policy snapshot"""
    
    # Authority roles (who may ACT on this stream?)
    LIFECYCLE_AUTHORITY = "lifecycle_authority"
    """Singular per stream: commits lifecycle transitions only"""
    
    COMMIT_AUTHORITY = "commit_authority"
    """Canonical position allocator; may allocate positions for commits.
       Distinct from lifecycle authority even when same object holds both."""
    
    CONFIGURATION_AUTHORITY = "configuration_authority"
    """May configure: descriptor, policy references, scope model,
       generation parameters"""
    
    ADMINISTRATIVE_AUTHORITY = "administrative_authority"
    """May perform: declaration, activation, pause, drain, closure,
       reset, policy migration, ownership migration, recovery request"""
    
    PRODUCER_AUTHORITY = "producer_authority"
    """May publish: records when authorized by owner and runtime policy.
       Does NOT own lifecycle or ordering."""
    
    CONSUMER_AUTHORITY = "consumer_authority"
    """May consume: records when authorized. Does NOT own lifecycle,
       ordering, commit authority."""
    
    OBSERVER_AUTHORITY = "observer_authority"
    """May inspect: bounded health, diagnostics, lifecycle state,
       integrity. Passive only - no mutation."""
    
    RECOVERY_AUTHORITY = "recovery_authority"
    """May recover: validate last committed state, rebuild indexes,
       isolate invalid producers/consumers, reopen from safe descriptors.
       Must not fabricate records or rewrite history."""


# =============================================================================
# OWNERSHIP DESCRIPTOR - Immutable Configuration
# =============================================================================


@dataclass(frozen=True)
class StreamOwnershipDescriptor:
    """
    Immutable descriptor for stream ownership configuration.
    
    Contains all ownership information without live objects, locks, or callbacks.
    This is what gets persisted and restored across restarts.
    
    Key Principles:
        - Immutable after creation
        - No live instances (only identifiers/strings)
        - Bounded metadata only
        - Provenance preserved for audit
    """
    
    # Stream identity
    stream_id: str
    
    # Ownership role bindings (stable identifiers, NOT instances)
    semantic_owner_id: Optional[str] = None
    infrastructure_owner_id: str = "core"
    runtime_owner_id: Optional[str] = None
    
    # Authority bindings
    lifecycle_authority_id: Optional[str] = None
    commit_authority_id: Optional[str] = None
    
    configuration_authority_id: Optional[str] = None
    administrative_authority_id: Optional[str] = None
    recovery_authority_id: Optional[str] = None
    
    # Domain interaction authorities
    producer_authority_id: Optional[str] = None
    consumer_authority_id: Optional[str] = None
    observer_authority_id: Optional[str] = None
    
    # Scope and versioning
    scope: str = "global"  # global, user, session, agent, tenant, etc.
    ownership_version: int = 1
    
    # Temporal bounds
    effective_from_utc: float = field(default_factory=time.time)
    effective_until_utc: Optional[float] = None
    
    # Provenance (audit trail)
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create_initial(
        cls,
        stream_id: str,
        runtime_instance_id: str,
        semantic_owner: Optional[str] = None,
    ) -> "StreamOwnershipDescriptor":
        """Create initial ownership descriptor."""
        return cls(
            stream_id=stream_id,
            infrastructure_owner_id="core",
            runtime_owner_id=runtime_instance_id,
            scope=cls._infer_scope(runtime_instance_id),
            semantic_owner_id=semantic_owner,
        )
    
    @staticmethod
    def _infer_scope(instance_id: str) -> str:
        """Infer scope from instance ID."""
        if "user:" in instance_id or "session:" in instance_id:
            return "user"
        if "agent:" in instance_id:
            return "agent"
        if "tenant:" in instance_id:
            return "tenant"
        return "global"
    
    def is_compatible_with(self, other: "StreamOwnershipDescriptor") -> bool:
        """Check compatibility for integration."""
        # Same stream ID required
        if self.stream_id != other.stream_id:
            return False
        
        # Scope must match (unless both are global)
        if self.scope != other.scope and self.scope != "global" and other.scope != "global":
            return False
        
        # Ownership version must be compatible
        return abs(self.ownership_version - other.ownership_version) <= 1
    
    def with_runtime_owner(self, new_owner: str) -> "StreamOwnershipDescriptor":
        """Return descriptor with updated runtime owner."""
        return dataclass_replace(
            self,
            runtime_owner_id=new_owner,
            ownership_version=self.ownership_version + 1
        )
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """Check if this descriptor has expired."""
        at = at_utc or time.time()
        return self.effective_until_utc is not None and at > self.effective_until_utc


# =============================================================================
# OWNERSHIP VALIDATION
# =============================================================================


def validate_ownership_descriptor(
    descriptor: StreamOwnershipDescriptor,
    known_roles: Optional[Set[str]] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate ownership descriptor structure.
    
    Checks:
        - Required fields are present
        - Authority assignments don't conflict
        - Scope is valid
    
    Args:
        descriptor: The ownership descriptor to validate
        known_roles: Set of valid role identifiers (if None, use default)
    
    Returns:
        (is_valid, error_message) tuple
    """
    if not descriptor.stream_id:
        return False, "stream_id is required"
    
    # Core infrastructure owner must be set and non-empty
    if not descriptor.infrastructure_owner_id or descriptor.infrastructure_owner_id == "":
        return False, "infrastructure_owner_id must be set"
    
    # Runtime owner should be unique per scope
    # (validation against duplicates handled by registry)
    
    # Authority uniqueness: each authority type may be bound to at most one entity
    authorities = [
        descriptor.lifecycle_authority_id,
        descriptor.commit_authority_id,
    ]
    non_none_auths = [a for a in authorities if a is not None]
    if len(non_none_auths) != len(set(non_none_auths)):
        return False, "Multiple authority bindings would conflict"
    
    # Runtime owner should not be None for active streams
    if descriptor.scope != "global" and descriptor.runtime_owner_id is None:
        return False, "runtime_owner must be set for scoped streams"
    
    return True, None


# =============================================================================
# OWNERSHIP TRANSFER REQUEST
# =============================================================================


@dataclass(frozen=True)
class OwnershipTransferRequest:
    """
    Request to transfer ownership of a stream.
    
    Transfer is rare, explicit, versioned, and atomic. It may be required for:
        - Runtime migration
        - Process replacement
        - Distributed partition reassignment
        - System upgrade
        - Controlled failover
    
    Never permits arbitrary producer-driven ownership transfer.
    """
    
    # Request metadata
    request_id: str  # Unique ID for this transfer request
    timestamp_utc: float = field(default_factory=time.time)
    
    # Stream identity
    stream_id: str
    
    # Source and target
    source_owner_id: Optional[str] = None  # Expected current owner (for compare-and-swap)
    target_owner_id: Optional[str] = None  # Who will become new owner
    
    # Scope
    scope: str = "global"
    
    # Validation context
    expected_ownership_version: int = 1
    expected_state_before: str = "active"  # Expected lifecycle state before transfer
    
    # Transfer requirements
    quiescence_required: bool = True       # Must quiesce first?
    drain_required: bool = False           # Must drain before transfer?
    
    # Timeout
    deadline_utc: Optional[float] = None   # When must this complete by?
    
    # Reason for transfer
    reason: str = "standard"
    
    def is_ready_for_execution(self, current_state: str) -> bool:
        """Check if this request can be executed given current state."""
        # If drain required but stream not drained, cannot proceed
        if self.drain_required and current_state != "drained":
            return False
        
        # If quiescence required, need to check stream has no active producers/consumers
        # (validation deferred to higher layer)
        
        return True


@dataclass(frozen=True)
class OwnershipTransferResult:
    """
    Result of an ownership transfer attempt.
    
    A failed transfer must leave one unambiguous canonical owner.
    Never permit split ownership.
    """
    
    # Outcome
    success: bool
    
    # For successful transfers
    new_owner_id: Optional[str] = None
    new_ownership_version: int = 1
    transfer_complete_at_utc: float = field(default_factory=time.time)
    
    # For rejected/failed transfers
    rejection_reason: Optional[str] = None
    state_before_transfer: Optional[str] = None
    
    # Partial outcome tracking
    partial_failure: bool = False
    failed_step: Optional[str] = None


# =============================================================================
# SCOPE ISOLATION
# =============================================================================


class ScopeIsolationError(Exception):
    """Raised when scope isolation would be violated."""
    
    def __init__(self, stream_id: str, current_scope: str, attempted_scope: str):
        self.stream_id = stream_id
        self.current_scope = current_scope
        self.attempted_scope = attempted_scope
        super().__init__(
            f"Scope isolation violation for {stream_id}: "
            f"current={current_scope}, attempted={attempted_scope}"
        )


def validate_scope_compatibility(
    existing_stream_ids: Set[str],
    new_stream_id: str,
    new_scope: str,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that adding a stream with new_scope doesn't violate scope isolation.
    
    Rules:
        - If existing streams are global, new scope can be anything
        - If existing streams have specific scopes, new must match (unless both global)
        - Cross-user/tenant/agent scoped streams require explicit shared-stream policy
    
    Returns:
        (is_compatible, reason) tuple
    """
    if not existing_stream_ids:
        return True, None  # No existing streams to conflict with
    
    # Get existing scopes
    existing_scopes = set()
    for sid in existing_stream_ids:
        if "-" in sid:
            parts = sid.rsplit("-", 1)
            scope = parts[1]
            if scope not in ["core", "perception", "consciousness", "cognition", "memory", "action"]:
                existing_scopes.add(scope)
    
    # If new stream is global, it's compatible with everything
    if new_scope == "global":
        return True, None
    
    # If there are scoped streams and new is also scoped, they must match
    if existing_scopes:
        if new_scope not in existing_scopes:
            return False, f"Scope {new_scope} conflicts with existing scopes: {existing_scopes}"
    
    return True, None


# =============================================================================
# OWNERSHIP IDENTITY - Stable Identifiers
# =============================================================================


class OwnershipIdentityType(Enum):
    """Categories of ownership identities."""
    SYSTEM = "system"
    COMPONENT = "component"
    USER = "user"
    SESSION = "session"
    AGENT = "agent"
    TENANT = "tenant"
    EXTERNAL = "external"


@dataclass(frozen=True)
class OwnershipIdentity:
    """
    Stable semantic reference for an ownership identity.
    
    Identity is independent of:
        - Python module path
        - Object memory address
        - Thread ID
        - Class name alone
    
    Identity depends on:
        - Stable identifier string
        - Type classification
        - Scope binding (where applicable)
    """
    
    type: OwnershipIdentityType
    identifier: str  # Unique within its type and scope
    scope: Optional[str] = None
    
    @classmethod
    def from_system_component(cls, component_name: str) -> "OwnershipIdentity":
        """Create identity for a Core system component."""
        return cls(
            type=OwnershipIdentityType.COMPONENT,
            identifier=component_name,
        )
    
    @classmethod
    def from_user(cls, user_id: str) -> "OwnershipIdentity":
        """Create identity for a user-scoped owner."""
        return cls(
            type=OwnershipIdentityType.USER,
            identifier=user_id,
            scope="user",
        )
    
    @classmethod
    def from_agent(cls, agent_id: str) -> "OwnershipIdentity":
        """Create identity for an agent-scoped owner."""
        return cls(
            type=OwnershipIdentityType.AGENT,
            identifier=agent_id,
            scope="agent",
        )
    
    @classmethod
    def from_tenant(cls, tenant_id: str) -> "OwnershipIdentity":
        """Create identity for a multi-tenant scoped owner."""
        return cls(
            type=OwnershipIdentityType.TENANT,
            identifier=tenant_id,
            scope="tenant",
        )


# =============================================================================
# DUPLICATE DETECTION
# =============================================================================


class DuplicateRuntimeOwnerError(Exception):
    """Raised when attempting to register duplicate runtime owner for same stream/scope."""
    
    def __init__(self, stream_id: str, scope: str, existing_owner: str):
        self.stream_id = stream_id
        self.scope = scope
        self.existing_owner = existing_owner
        super().__init__(
            f"Duplicate runtime owner for {stream_id} in scope '{scope}': "
            f"{existing_owner}"
        )


class DuplicateAuthorityError(Exception):
    """Raised when attempting to bind duplicate authority."""
    
    def __init__(self, stream_id: str, authority_type: str, existing_id: str):
        self.stream_id = stream_id
        self.authority_type = authority_type
        self.existing_id = existing_id
        super().__init__(
            f"Duplicate {authority_type} for {stream_id}: {existing_id}"
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Role enumeration
    "StreamOwnershipRole",
    
    # Descriptor
    "StreamOwnershipDescriptor",
    "validate_ownership_descriptor",
    
    # Transfer model
    "OwnershipTransferRequest",
    "OwnershipTransferResult",
    
    # Scope isolation
    "ScopeIsolationError",
    "validate_scope_compatibility",
    
    # Identity
    "OwnershipIdentityType",
    "OwnershipIdentity",
    
    # Duplicate errors
    "DuplicateRuntimeOwnerError",
    "DuplicateAuthorityError",
]


# =============================================================================
# DATACLASS REPLACE UTILITY
# =============================================================================


def _dataclass_replace_impl(obj: Any, **kwargs) -> Any:
    """Internal helper - do not export directly."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    return _dataclass_replace_impl(obj, **kwargs)
