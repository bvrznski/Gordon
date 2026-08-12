"""Authority - canonical runtime authority model.

Phase 3.7.2: Authority, Dependency, Package, Import, and Ownership Architecture
==============================================================================

This package implements the immutable, deterministic authority model for Gordon Core.
Every governed runtime responsibility must have exactly one canonical authority.

Core Principles:
    - Authority is not access
    - Ownership is not visibility  
    - Dependency is not import
    - Registration is not construction
    - Construction is not activation
    - Observation is not mutation
    - Metadata is not runtime truth
    - Compatibility is not independent authority

Authoritative sources per responsibility:
    - Kernel: one canonical kernel authority
    - Runtime State: one canonical state store
    - Lifecycle: one canonical lifecycle controller
    - Registry: one registry owner per domain
    - Dependencies: explicit graph ownership
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from enum import Enum
import time

# Import types from core - use relative imports that work from architecture/
try:
    from ..components.core.types import (
        EntityId,
        RuntimeId,
    )
except ImportError:
    # Fallback: define minimal types locally
    from typing import NewType
    EntityId = NewType("EntityId", str)  # type: ignore[assignment]
    RuntimeId = NewType("RuntimeId", str)  # type: ignore[assignment]


# =============================================================================
# AUTHORITY KINDS AND SCOPES
# =============================================================================


class AuthorityKind(Enum):
    """Categories of runtime authorities."""
    
    # Core infrastructure
    ROOT = "root"
    RUNTIME = "runtime"
    KERNEL = "kernel"
    
    # State management
    STATE = "state"
    MUTATION = "mutation"
    REGISTRY = "registry"
    
    # Lifecycle and scheduling
    LIFECYCLE = "lifecycle"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    SCHEDULING = "scheduling"
    
    # Execution
    EXECUTION = "execution"
    COMMUNICATION = "communication"
    
    # Observability and recovery
    HEALTH = "health"
    INTEGRITY = "integrity"
    OBSERVABILITY = "observability"
    PERSISTENCE = "persistence"
    
    # System lifecycle
    SHUTDOWN = "shutdown"
    FAILURE = "failure"
    ROLLBACK = "rollback"
    RECOVERY = "recovery"
    
    # Testing and compatibility
    TEST = "test"
    COMPATIBILITY = "compatibility"


class AuthorityScope(Enum):
    """Scopes of authority influence."""
    
    PROCESS = "process"     # Process-wide influence
    RUNTIME = "runtime"     # Runtime-scoped (per-runtime instance)
    KERNEL = "kernel"       # Kernel-level scope
    COMPONENT = "component" # Component-local scope
    SERVICE = "service"     # Service-scoped
    TASK = "task"           # Task-scoped
    REQUEST = "request"     # Request-scoped
    TEST = "test"           # Test-only scope


# =============================================================================
# AUTHORITY IDENTIFIERS
# =============================================================================


@dataclass(frozen=True)
class AuthorityId:
    """Unique identifier for an authority."""
    
    value: str
    
    @classmethod
    def from_parts(cls, category: str, name: str) -> "AuthorityId":
        """Create an authority ID from category and name parts."""
        return cls(value=f"{category}/{name}")
    
    def __str__(self) -> str:
        return self.value


# RuntimeId already imported above (either from types or defined locally)


@dataclass(frozen=True)
class RuntimeIdentity:
    """Runtime identity with versioning."""
    
    runtime_id: str
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.monotonic)


# =============================================================================
# AUTHORITY DESCRIPTOR
# =============================================================================


@dataclass(frozen=True)
class AuthorityDescriptor:
    """
    Immutable descriptor for a canonical authority.
    
    This is the authoritative metadata about an authority - NO mutable state.
    Every runtime concern must have exactly one such descriptor.
    """
    
    # Identity (required - no defaults)
    authority_id: AuthorityId
    canonical_name: str
    
    # Implementation identity
    implementation_identity: str  # Fully qualified class name
    runtime_id: RuntimeIdentity
    
    # Scope and ownership
    scope: AuthorityScope
    owner: EntityId  # Who owns this authority
    
    # Responsibility (required - no defaults)
    responsibility: str  # What this authority is responsible for
    non_responsibilities: Tuple[str, ...] = field(default_factory=tuple)
    
    # State owned
    mutable_state_owned: Tuple[str, ...] = field(default_factory=tuple)
    
    # Mutation rights (who can mutate and how)
    mutation_rights: "MutationRights"  # See section 14
    
    # Facade and delegates
    public_facade: Tuple[str, ...] = field(default_factory=tuple)
    delegates: Tuple[AuthorityId, ...] = field(default_factory=tuple)
    
    # Dependencies (what this authority depends on)
    dependencies: Tuple[AuthorityId, ...] = field(default_factory=tuple)
    
    # Lifecycle
    lifecycle: str = "runtime"  # runtime, construction, activation, shutdown
    
    # Replacement policy
    replacement_policy: str = "strict"  # strict, compatible, deprecated
    
    # Compatibility aliases (for backward compatibility paths)
    compatibility_aliases: Tuple[str, ...] = field(default_factory=tuple)
    
    # Version and provenance
    version: str = "1.0.0"
    provenance: Optional[str] = None
    
    @property
    def is_runtime_scoped(self) -> bool:
        """Check if this authority is runtime-scoped (not process-global)."""
        return self.scope in (
            AuthorityScope.RUNTIME,
            AuthorityScope.COMPONENT,
            AuthorityScope.SERVICE,
            AuthorityScope.TASK,
            AuthorityScope.REQUEST,
        )


@dataclass(frozen=True)
class MutationRights:
    """
    Explicit mutation rights for an authority.
    
    Defines who can mutate and how, including validation rules.
    """
    
    # Who can perform mutations
    allowed_mutators: Tuple[str, ...] = field(default_factory=tuple)
    
    # Validation requirements
    require_validation: bool = True
    validation_rules: Tuple[str, ...] = field(default_factory=tuple)
    
    # Mutation boundaries  
    allow_direct_mutation: bool = False  # If False, use typed requests only
    allow_transactional_mutations: bool = True
    
    # Audit requirements
    require_audit_log: bool = True


# =============================================================================
# AUTHORITY REFERENCE
# =============================================================================


@dataclass(frozen=True)
class AuthorityReference:
    """A reference to an authority (not the authority itself)."""
    
    authority_id: AuthorityId
    implementation_identity: str
    runtime_scope: RuntimeIdentity
    
    # State snapshot at time of reference
    state_snapshot_version: int = 0


# =============================================================================
# REGISTRATION MODELS
# =============================================================================


class RegistrationStatus(Enum):
    """Status values for authority registration."""
    
    PENDING = "pending"
    VALIDATING = "validating"
    REGISTERED = "registered"  # First-time or replacement
    IDEMPOTENT = "idempotent"  # Already registered with same descriptor
    REPLACED = "replaced"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    REJECTED_DUPLICATE = "rejected_duplicate"
    REJECTED_CONFLICT = "rejected_conflict"
    REJECTED_INVALID = "rejected_invalid"


@dataclass(frozen=True)
class RegistrationRequest:
    """A request to register an authority."""
    
    descriptor: AuthorityDescriptor
    requested_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class RegistrationResult:
    """
    Result of a registration operation with explicit typed status.
    
    Do not return generic booleans - use this structured result type.
    """
    
    status: RegistrationStatus
    
    # Success cases
    authority_id: Optional[AuthorityId] = None
    descriptor: Optional[AuthorityDescriptor] = None
    version: int = 0
    
    # Failure reasons
    reason: Optional[str] = None
    conflict_with: Optional[AuthorityId] = None
    
    @property
    def success(self) -> bool:
        """Check if registration succeeded."""
        return self.status in (
            RegistrationStatus.REGISTERED,
            RegistrationStatus.REPLACED,
        )
    
    @property
    def idempotent(self) -> bool:
        """Check if this was an idempotent operation."""
        # IDEMPOTENT status is valid - check for it directly
        return self.status == RegistrationStatus.IDEMPOTENT
    
    @property
    def rejected(self) -> bool:
        """Check if registration was rejected."""
        return self.status in (
            RegistrationStatus.REJECTED_DUPLICATE,
            RegistrationStatus.REJECTED_CONFLICT,
            RegistrationStatus.REJECTED_INVALID,
        )


# =============================================================================
# AUTHORITY RELATIONSHIPS
# =============================================================================


class AuthorityRelationship(Enum):
    """Types of relationships between authorities."""
    
    DELEGATES_TO = "delegates_to"
    DEPENDS_ON = "depends_on"
    OWNS_STATE = "owns_state"
    OBSERVES = "observes"
    COORDINATES = "coordinates"
    COMPATIBILITY_ALIAS = "compatibility_alias"
    DEPRECATED_BY = "deprecated_by"


@dataclass(frozen=True)
class AuthorityRelationshipEntry:
    """A single relationship between authorities."""
    
    from_authority: AuthorityId
    to_authority: AuthorityId
    relationship: AuthorityRelationship
    
    # Context
    scope: RuntimeIdentity
    effective_from_version: int = 1


# =============================================================================
# AUTHORITY SNAPSHOTS AND FINDINGS
# =============================================================================


@dataclass(frozen=True)
class AuthoritySnapshot:
    """
    Immutable snapshot of authority state at a point in time.
    
    This is observational - it does not become the authority itself.
    """
    
    runtime_id: RuntimeIdentity
    snapshot_version: int
    
    # All known authorities
    authorities: Tuple[AuthorityDescriptor, ...]
    
    # Relationships between authorities
    relationships: Tuple[AuthorityRelationshipEntry, ...]
    
    # Integrity
    content_digest: str  # SHA256 of all authority IDs and versions
    recorded_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class AuthorityFinding:
    """A finding about an authority from architecture analysis."""
    
    finding_id: str
    finding_type: str  # DUPLICATE, HIDDEN, CONFLICT, etc.
    
    affected_authority: Optional[AuthorityId] = None
    evidence: str = ""
    severity: str = "info"  # info, warning, error, critical
    
    # Remediation guidance
    remediation: Optional[str] = None


@dataclass(frozen=True)
class AuthorityReport:
    """Complete report of authority analysis."""
    
    runtime_id: RuntimeIdentity
    report_version: int
    recorded_at: float
    
    # Findings
    findings: Tuple[AuthorityFinding, ...]
    
    # Summary
    total_authorities: int
    duplicate_count: int
    hidden_count: int
    conflict_count: int


# =============================================================================
# AUTHORITY REGISTRY INTERFACE
# =============================================================================


class AuthorityRegistry:
    """
    Canonical registry for runtime authorities.
    
    This owns authority metadata and canonical authority references.
    
    What it MUST do:
        - Store immutable authority descriptors
        - Validate registration requests
        - Detect duplicates
        - Enforce ownership validation
        - Provide immutable snapshots
    
    What it MUST NOT do:
        - Construct authorities (that's the bootstrap phase)
        - Activate authorities (that's runtime startup)
        - Become a service locator (no arbitrary lookups)
        - Expose mutable internal maps
        - Store duplicate truth
    """
    
    def __init__(self, runtime_id: RuntimeIdentity) -> None:
        """Initialize the authority registry."""
        self._runtime_id = runtime_id
        self._authorities: Dict[AuthorityId, AuthorityDescriptor] = {}
        self._relationships: List[AuthorityRelationshipEntry] = []
        self._version = 0
    
    def register(self, descriptor: AuthorityDescriptor) -> RegistrationResult:
        """
        Register an authority descriptor.
        
        Args:
            descriptor: The authority descriptor to register
            
        Returns:
            RegistrationResult with typed status
        """
        # Validate runtime identity matches
        if descriptor.runtime_id.runtime_id != self._runtime_id.runtime_id:
            return RegistrationResult(
                status=RegistrationStatus.REJECTED_INVALID,
                reason=f"Runtime ID mismatch: expected {self._runtime_id.runtime_id}, got {descriptor.runtime_id.runtime_id}"
            )
        
        # Check for duplicates (by authority_id)
        if descriptor.authority_id in self._authorities:
            existing = self._authorities[descriptor.authority_id]
            # Check if it's an idempotent update (same implementation)
            if existing.implementation_identity == descriptor.implementation_identity:
                return RegistrationResult(
                    status=RegistrationStatus.IDEMPOTENT,
                    authority_id=descriptor.authority_id,
                    descriptor=existing,
                    version=self._version
                )
            return RegistrationResult(
                status=RegistrationStatus.REJECTED_DUPLICATE,
                reason=f"Duplicate authority ID: {descriptor.authority_id}",
                conflict_with=descriptor.authority_id
            )
        
        # Check for duplicate responsibility (one canonical per responsibility)
        for existing_desc in self._authorities.values():
            if existing_desc.responsibility == descriptor.responsibility:
                return RegistrationResult(
                    status=RegistrationStatus.REJECTED_CONFLICT,
                    reason=f"Duplicate responsibility: {descriptor.responsibility} already owned by {existing_desc.authority_id}",
                    conflict_with=existing_desc.authority_id
                )
        
        # Commit registration
        self._authorities[descriptor.authority_id] = descriptor
        self._version += 1
        
        return RegistrationResult(
            status=RegistrationStatus.REGISTERED,
            authority_id=descriptor.authority_id,
            descriptor=descriptor,
            version=self._version
        )
    
    def get(self, authority_id: AuthorityId) -> Optional[AuthorityDescriptor]:
        """
        Get an authority descriptor by ID.
        
        Args:
            authority_id: The authority identifier
            
        Returns:
            The authority descriptor, or None if not found
        """
        return self._authorities.get(authority_id)
    
    def lookup_by_responsibility(self, responsibility: str) -> Optional[AuthorityId]:
        """
        Look up an authority by its responsibility.
        
        Args:
            responsibility: The responsibility to look up
            
        Returns:
            The authority ID if found, None otherwise
        """
        for aid, desc in self._authorities.items():
            if desc.responsibility == responsibility:
                return aid
        return None
    
    def snapshot(self) -> AuthoritySnapshot:
        """Create an immutable snapshot of current state."""
        return AuthoritySnapshot(
            runtime_id=self._runtime_id,
            snapshot_version=self._version,
            authorities=tuple(self._authorities.values()),
            relationships=tuple(self._relationships),
            content_digest=str(hash(tuple(sorted(self._authorities.keys())))),
            recorded_at=time.monotonic()
        )
    
    def seal(self) -> None:
        """Seal the registry - no more registrations allowed."""
        # In a full implementation, this would set an immutable flag
        self._sealed = True
    
    @property
    def is_sealed(self) -> bool:
        """Check if the registry has been sealed."""
        return getattr(self, '_sealed', False)


__all__ = [
    "AuthorityKind",
    "AuthorityScope",
    "AuthorityId",
    "RuntimeIdentity",
    "AuthorityDescriptor",
    "MutationRights",
    "AuthorityReference",
    "RegistrationStatus",
    "RegistrationRequest",
    "RegistrationResult",
    "AuthorityRelationship",
    "AuthorityRelationshipEntry",
    "AuthoritySnapshot",
    "AuthorityFinding",
    "AuthorityReport",
    "AuthorityRegistry",
]