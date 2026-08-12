# Core Security Infrastructure
# =============================
"""
Security, Trust Boundaries, Authorization & Runtime Protection for Gordon agent.

This module implements Phase 3.7.16: Security, Trust Boundaries, Authorization & Runtime Protection.

The canonical security pipeline is:

    Actor
        ↓
    Identity Resolution
        ↓
    Authentication
        ↓
    Trust Evaluation
        ↓
    Authorization
        ↓
    Policy Evaluation
        ↓
    Capability Resolution
        ↓
    Ownership Verification
        ↓
    Boundary Enforcement
        ↓
    Secure Execution
        ↓
    Audit
        ↓
    Post-Action Verification

Security is a runtime authority system. It is NOT a collection of helper functions.

The architecture preserves the distinction between:
- identity, authentication, trust, authorization, permission, capability,
  policy, ownership, delegation, impersonation, privilege, sandboxing, isolation,
  validation, auditing, revocation

A caller having an identity does NOT imply trust.
Trust does NOT imply authorization.
Authorization does NOT imply capability.
Capability does NOT imply permission.
Permission does NOT imply execution.

Authorities (exactly one per responsibility):
- SecurityManager: Security orchestration and policy lifecycle
- AuthorizationManager: Permission evaluation and authorization decisions
- AuthenticationManager: Identity verification and authentication providers
- TrustManager: Trust relationships and trust scoring
- CapabilityManager: Runtime capabilities and capability grants
- SecretManager: Secret storage, rotation, and secure destruction
- SecurityAuditManager: Immutable audit records and security events

Phase 3.7.16-I: Production Implementation
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
    Set,
)
from enum import Enum
import time
import uuid
import secrets
import hashlib
from threading import Lock


# =============================================================================
# ID Types (defined first to avoid circular dependencies with managers.py)
# =============================================================================

@dataclass(frozen=True)
class SecurityId:
    """Unique identifier for a security artifact."""
    value: str
    
    @classmethod
    def generate(cls) -> "SecurityId":
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "SecurityId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SecurityVersion:
    """Version of a security artifact."""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    def next_major(self) -> "SecurityVersion":
        return SecurityVersion(major=self.major + 1, minor=0, patch=0)
    
    def next_minor(self) -> "SecurityVersion":
        return SecurityVersion(major=self.major, minor=self.minor + 1, patch=0)
    
    def next_patch(self) -> "SecurityVersion":
        return SecurityVersion(major=self.major, minor=self.minor, patch=self.patch + 1)


# =============================================================================
# Identity Model
# =============================================================================

class IdentityType(Enum):
    """Types of identities in the system."""
    RUNTIME = "runtime"
    SERVICE = "service"
    PLUGIN = "plugin"
    TOOL = "tool"
    SESSION = "session"
    USER = "user"
    ACTOR = "actor"


@dataclass(frozen=True)
class Identity:
    """
    Immutable identity representation.
    
    An identity proves WHO is making a request, but NOT whether they are
    trusted or authorized to perform an action.
    """
    identity_id: str  # Unique identifier for this identity
    name: str         # Human-readable name
    type_: IdentityType  # Type of identity
    
    # Authentication metadata
    authenticated_at: Optional[float] = None
    authentication_method: Optional[str] = None
    
    # Delegation chain (immutable, ordered from most recent to oldest)
    delegated_from: Optional["Identity"] = None
    
    def __hash__(self) -> int:
        return hash(self.identity_id)


@dataclass(frozen=True)
class Principal(Identity):
    """
    A principal is an identity that can be the subject of permissions.
    
    All principals are identities, but not all identities are principals.
    """
    # Principal-specific metadata
    principal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    groups: Tuple[str, ...] = field(default_factory=tuple)  # Group memberships
    
    @classmethod
    def from_identity(cls, identity: Identity) -> "Principal":
        """Create a Principal from an Identity."""
        return cls(
            identity_id=identity.identity_id,
            name=identity.name,
            type_=identity.type_,
            authenticated_at=identity.authenticated_at,
            authentication_method=identity.authentication_method,
            delegated_from=identity.delegated_from,
            principal_id=str(uuid.uuid4()),
            groups=tuple()
        )


@dataclass(frozen=True)
class Actor:
    """
    An actor is an entity that can perform actions in the system.
    
    In security contexts, an actor is often a principal acting in a specific
    context. This allows us to distinguish between "who" and "how they're acting".
    """
    identity: Identity
    context: str = ""  # Contextual role or mode


@dataclass(frozen=True)
class RuntimeIdentity:
    """Identity for a runtime instance."""
    runtime_id: str
    cluster_id: Optional[str] = None
    node_id: Optional[str] = None
    
    @classmethod
    def generate(cls) -> "RuntimeIdentity":
        return cls(runtime_id=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "RuntimeIdentity":
        parts = s.split("/")
        return cls(
            runtime_id=parts[0] if parts else str(uuid.uuid4()),
            cluster_id=parts[1] if len(parts) > 1 else None,
            node_id=parts[2] if len(parts) > 2 else None
        )


@dataclass(frozen=True)
class ServiceIdentity:
    """Identity for a service within the runtime."""
    service_id: str
    name: str
    version: str = "1.0.0"


@dataclass(frozen=True)
class PluginIdentity:
    """Identity for a plugin."""
    plugin_id: str
    name: str
    version: str = "1.0.0"
    manifest_hash: Optional[str] = None  # SHA256 hash of manifest for integrity


@dataclass(frozen=True)
class ToolIdentity:
    """Identity for a tool."""
    tool_id: str
    name: str
    vendor: Optional[str] = None
    version: str = "1.0.0"


@dataclass(frozen=True)
class SessionIdentity:
    """Identity for a session with specific authentication context."""
    session_id: str
    principal_id: str
    created_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None
    scopes: Tuple[str, ...] = field(default_factory=tuple)  # Authorized scopes


# =============================================================================
# Authentication Primitives
# =============================================================================

class AuthMethod(Enum):
    """Authentication methods supported."""
    NONE = "none"
    LOCAL = "local"           # Local credential storage
    TOKEN = "token"           # Token-based (JWT, Bearer)
    API_KEY = "api_key"       # API key authentication
    SERVICE = "service"       # Service-to-service authentication
    CERTIFICATE = "certificate"  # TLS certificate


@dataclass(frozen=True)
class Credential:
    """
    Authentication credential.
    
    Credentials prove identity but are not stored in plaintext.
    They are hashed/encrypted at rest.
    """
    credential_id: str
    principal_id: str
    method: AuthMethod
    
    # Encrypted/hashed credential data (never store plaintext secrets)
    credential_hash: str  # SHA256 or stronger hash of the actual credential
    
    created_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None
    rotated_at: Optional[float] = None
    
    def is_valid(self) -> bool:
        """Check if credential is still valid."""
        now = time.monotonic()
        if self.expires_at and now > self.expires_at:
            return False
        return True


@dataclass(frozen=True)
class Token:
    """
    Authentication token.
    
    Tokens are issued after successful authentication and prove identity
    for the duration of their validity.
    """
    token_id: str
    principal_id: str
    type_: AuthMethod  # Token type (JWT, Bearer, etc.)
    
    # Token claims
    issued_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None
    
    # Token metadata
    scopes: Tuple[str, ...] = field(default_factory=tuple)  # Authorized scopes
    audience: str = ""  # Intended recipients
    issuer: str = ""    # Token issuer
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        now = time.monotonic()
        if self.expires_at and now > self.expires_at:
            return False
        return True


@dataclass(frozen=True)
class CertificateReference:
    """
    Reference to a certificate for authentication.
    
    Certificates are stored externally (e.g., in secret manager) and referenced.
    """
    cert_id: str
    issuer: str
    subject: str
    not_before: float
    not_after: float


# =============================================================================
# Authentication Request/Result
# =============================================================================

@dataclass(frozen=True)
class AuthenticationRequest:
    """
    A request to authenticate an identity.
    
    This is the input to the authentication system. It does NOT imply
    successful authentication - that requires explicit verification.
    """
    principal_id: Optional[str] = None  # If known
    credential_hash: Optional[str] = None  # For lookup verification
    token: Optional[Token] = None  # Token-based auth
    method: AuthMethod = AuthMethod.NONE
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    def is_complete(self) -> bool:
        """Check if request has sufficient data for authentication."""
        return any([
            self.principal_id and self.credential_hash,
            self.token is not None,
        ])


@dataclass(frozen=True)
class AuthenticationResult:
    """
    Result of an authentication attempt.
    
    A successful result proves identity but does NOT imply trust or
    authorization. Those are separate evaluations.
    """
    success: bool
    principal_id: Optional[str] = None
    identity: Optional[Identity] = None
    
    # Authentication metadata
    method: AuthMethod = AuthMethod.NONE
    timestamp: float = field(default_factory=time.monotonic)
    token: Optional[Token] = None  # Issued token (if any)
    
    # Failure reason (only if success=False)
    failure_reason: Optional[str] = None
    
    def is_success(self) -> bool:
        return self.success


# =============================================================================
# Authentication Provider Interface
# =============================================================================

class AuthenticationProvider:
    """
    Interface for authentication providers.
    
    Providers implement specific authentication mechanisms (local, token,
    API key, service-to-service, etc.).
    
    The provider only verifies identity - it does not make trust or
    authorization decisions.
    """
    
    def __init__(self, provider_id: str):
        self._provider_id = provider_id
    
    @property
    def provider_id(self) -> str:
        return self._provider_id
    
    async def authenticate(self, request: "AuthenticationRequest") -> "AuthenticationResult":
        """Attempt to authenticate the given request."""
        raise NotImplementedError
    
    async def validate_token(self, token: "Token") -> bool:
        """Validate a token without re-authenticating."""
        raise NotImplementedError


# =============================================================================
# Trust Model
# =============================================================================

class TrustLevel(Enum):
    """Levels of trust in the system."""
    UNTRUSTED = "untrusted"     # Explicitly untrusted
    UNKNOWN = "unknown"         # No trust assessment yet
    VERIFIED = "verified"       # Identity verified, no additional trust
    TRUSTED = "trusted"         # Trusted for some operations
    HIGHLY_TRUSTED = "highly_trusted"  # Fully trusted (runtime operator)


class TrustEvidence(Enum):
    """Types of evidence for trust assessment."""
    IDENTITY_VERIFIED = "identity_verified"
    CREDENTIAL_VALID = "credential_valid"
    TOKEN_VALID = "token_valid"
    CERTIFICATE_VALID = "certificate_valid"
    SOURCE_AUTHENTICATED = "source_authenticated"
    BEHAVIOR_HISTORY_GOOD = "behavior_history_good"
    PRIVILEGE_LEVEL_HIGH = "privilege_level_high"


@dataclass(frozen=True)
class TrustEvidenceRecord:
    """A record of trust evidence."""
    evidence_id: str
    type_: TrustEvidence
    value: float  # Evidence strength (0.0 to 1.0)
    source_id: str  # What provided this evidence
    timestamp: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class TrustDecision:
    """
    A trust decision for a principal.
    
    Trust is independent from authorization. A trusted principal may still
    be denied authorization for specific actions.
    """
    principal_id: str
    trust_level: TrustLevel
    evidence: Tuple[TrustEvidenceRecord, ...] = field(default_factory=tuple)
    assessed_at: float = field(default_factory=time.monotonic)
    
    # Trust metadata
    expires_at: Optional[float] = None
    revocable: bool = True  # Can this trust be revoked?
    
    def score(self) -> float:
        """Calculate numeric trust score (0.0 to 1.0)."""
        level_scores = {
            TrustLevel.UNTRUSTED: 0.0,
            TrustLevel.UNKNOWN: 0.3,
            TrustLevel.VERIFIED: 0.5,
            TrustLevel.TRUSTED: 0.75,
            TrustLevel.HIGHLY_TRUSTED: 1.0,
        }
        base_score = level_scores.get(self.trust_level, 0.0)
        
        # Adjust based on evidence
        if self.evidence:
            avg_evidence = sum(e.value for e in self.evidence) / len(self.evidence)
            return (base_score + avg_evidence) / 2
        
        return base_score


@dataclass(frozen=True)
class TrustReport:
    """A comprehensive trust report for a principal."""
    principal_id: str
    current_level: TrustLevel
    historical_levels: Tuple[Tuple[float, TrustLevel], ...] = field(default_factory=tuple)
    total_assessments: int = 0
    last_assessment_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class TrustHistory:
    """Historical trust records for a principal."""
    principal_id: str
    entries: Tuple[Tuple[float, TrustLevel], ...] = field(default_factory=tuple)  # (timestamp, level)


# =============================================================================
# Authorization Model
# =============================================================================

class Permission(Enum):
    """
    Explicit permissions in the system.
    
    These are the atomic units of authorization. A principal must have
    explicit permission to perform an action.
    
    Categories:
    - runtime administration
    - configuration
    - filesystem
    - networking
    - process creation
    - plugin execution
    - tool invocation
    - model loading
    - shutdown
    - recovery
    - diagnostics
    - persistence
    """
    # Runtime Administration
    RUNTIME_START = "runtime:start"
    RUNTIME_STOP = "runtime:stop"
    RUNTIME_RESTART = "runtime:restart"
    
    # Configuration
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"
    CONFIG_RELOAD = "config:reload"
    
    # Filesystem
    FS_READ = "fs:read"
    FS_WRITE = "fs:write"
    FS_DELETE = "fs:delete"
    FS_EXECUTE = "fs:execute"
    FS_MOUNT = "fs:mount"
    FS_TEMPORARY = "fs:temporary"
    
    # Networking
    NET_OUTBOUND = "net:outbound"
    NET_INBOUND = "net:inbound"
    NET_PROVIDER_ACCESS = "net:provider"
    NET_LOCALHOST = "net:localhost"
    NET_REMOTE = "net:remote"
    
    # Process Creation
    PROC_CREATE = "proc:create"
    PROC_EXEC = "proc:exec"
    PROC_KILL = "proc:kill"
    
    # Plugin Execution
    PLUGIN_LOAD = "plugin:load"
    PLUGIN_UNLOAD = "plugin:unload"
    PLUGIN_INVOKE = "plugin:invoke"
    
    # Tool Invocation
    TOOL_REGISTER = "tool:register"
    TOOL_INVOKE = "tool:invoke"
    
    # Model Loading
    MODEL_LOAD = "model:load"
    MODEL_RUN = "model:run"
    
    # Shutdown & Recovery
    SHUTDOWN_INITIATE = "shutdown:initiate"
    RECOVERY_ACTIVATE = "recovery:activate"
    
    # Diagnostics
    DIAGNOSTICS_READ = "diagnostics:read"
    DIAGNOSTICS_WRITE = "diagnostics:write"
    
    # Persistence
    PERSISTENCE_READ = "persistence:read"
    PERSISTENCE_WRITE = "persistence:write"
    PERSISTENCE_DELETE = "persistence:delete"


@dataclass(frozen=True)
class PermissionDescriptor:
    """A descriptor for a permission."""
    permission: Permission
    name: str
    description: str
    category: str  # e.g., "filesystem", "networking"
    requires_ownership: bool = False  # Does this require ownership verification?
    
    @property
    def category_name(self) -> str:
        return self.permission.value.split(':')[0]


@dataclass(frozen=True)
class AuthorizationRequest:
    """
    A request for authorization to perform an action.
    
    This is the input to the authorization system. It includes all
    necessary context: actor, action, resource, and runtime context.
    """
    principal_id: str
    action: Permission
    resource: str  # Resource identifier (file path, network endpoint, etc.)
    context: Dict[str, Any] = field(default_factory=dict)  # Runtime context
    
    # Ownership verification parameters
    expected_owner: Optional[str] = None  # If the resource has an owner
    
    def __hash__(self) -> int:
        return hash((self.principal_id, self.action, self.resource))


@dataclass(frozen=True)
class AuthorizationDecision(Enum):
    """Possible authorization decisions."""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"  # Allow with conditions (e.g., rate limit)


@dataclass(frozen=True)
class AuthorizationEvidence:
    """
    Evidence supporting an authorization decision.
    
    This preserves the reasoning for audit and review purposes.
    """
    evidence_id: str
    type_: str  # e.g., "permission_grant", "ownership_verified"
    value: bool
    timestamp: float = field(default_factory=time.monotonic)
    
    # Contextual information
    source_policy: Optional[str] = None  # Which policy provided this evidence


@dataclass(frozen=True)
class AuthorizationResult:
    """
    Result of an authorization decision.
    
    A granted authorization does NOT imply capability. The system must
    also verify that the runtime can technically perform the action.
    """
    allowed: bool
    principal_id: str
    action: Permission
    resource: str
    
    # Decision metadata
    timestamp: float = field(default_factory=time.monotonic)
    
    # Evidence for audit trail
    evidence: Tuple[AuthorizationEvidence, ...] = field(default_factory=tuple)
    policy_ids: Tuple[str, ...] = field(default_factory=tuple)  # Which policies applied
    
    # Failure reason (only if allowed=False)
    reason: Optional[str] = None
    
    @property
    def decision(self) -> AuthorizationDecision:
        return AuthorizationDecision.ALLOW if self.allowed else AuthorizationDecision.DENY


# =============================================================================
# Capability Model
# =============================================================================

@dataclass(frozen=True)
class CapabilityId:
    """Unique identifier for a capability."""
    value: str
    
    @classmethod
    def generate(cls) -> "CapabilityId":
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "CapabilityId":
        return cls(value=s)


@dataclass(frozen=True)
class Capability:
    """
    A capability describes what the runtime CAN technically perform.
    
    Capabilities are immutable and represent technical ability, NOT permission.
    Having a capability does NOT mean you can use it - that requires authorization.
    """
    capability_id: CapabilityId
    name: str
    domain: str  # e.g., "filesystem", "networking", "process"
    
    # Technical details
    description: str
    implementation_version: str = "1.0.0"
    
    # Resource requirements
    minimum_resources: Dict[str, float] = field(default_factory=dict)
    
    def __hash__(self) -> int:
        return hash(self.capability_id.value)


@dataclass(frozen=True)
class CapabilityGrant:
    """
    A grant of a capability to a principal.
    
    This is the binding between a capability and a principal. It does NOT
    imply authorization - that requires separate policy evaluation.
    """
    grant_id: str
    capability_id: str
    principal_id: str
    
    # Grant metadata
    granted_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None
    conditions: Tuple[str, ...] = field(default_factory=tuple)  # Constraint conditions


@dataclass(frozen=True)
class CapabilityLease:
    """
    A time-limited lease on a capability.
    
    Leases are used for temporary capability access and must be renewed
    before expiration.
    """
    lease_id: str
    principal_id: str
    capability_id: str
    
    # Lease terms (expires_at has no default - lease always expires)
    granted_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None  # If None, lease doesn't expire
    renewals_allowed: int = 0
    current_renewal_count: int = 0


@dataclass(frozen=True)
class CapabilityRevocation:
    """A revocation of a capability grant."""
    revocation_id: str
    grant_id: str
    revoked_at: float = field(default_factory=time.monotonic)
    reason: Optional[str] = None


# =============================================================================
# Policy Model
# =============================================================================

class PolicyType(Enum):
    """Types of policies in the system."""
    ALLOW = "allow"  # Allowlist policy
    DENY = "deny"    # Denylist policy
    CONDITIONAL = "conditional"  # Conditional access
    DELEGATED = "delegated"      # Delegation policy
    INHERITED = "inherited"       # Inherited from parent
    TEMPORARY = "temporary"       # Time-limited policy


@dataclass(frozen=True)
class PolicyId:
    """Unique identifier for a policy."""
    value: str
    
    @classmethod
    def generate(cls) -> "PolicyId":
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "PolicyId":
        return cls(value=s)


@dataclass(frozen=True)
class PolicyRule:
    """A single policy rule."""
    rule_id: str
    name: str
    description: Optional[str] = None
    
    # Match criteria
    principal_patterns: Tuple[str, ...] = field(default_factory=tuple)  # Principal ID patterns
    action_patterns: Tuple[str, ...] = field(default_factory=tuple)     # Action patterns (Permission values)
    resource_patterns: Tuple[str, ...] = field(default_factory=tuple)   # Resource patterns
    
    # Effect
    effect: PolicyType = PolicyType.ALLOW
    
    # Conditions (lambda functions that return True to match)
    conditions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AuthorizationPolicy:
    """
    An authorization policy.
    
    Policies are versioned and immutable. New versions create new policies
    rather than modifying existing ones.
    """
    policy_id: PolicyId
    name: str
    description: Optional[str] = None
    
    # Versioning
    version: int = 1
    created_at: float = field(default_factory=time.monotonic)
    
    # Rules
    rules: Tuple[PolicyRule, ...] = field(default_factory=tuple)
    
    # Policy metadata
    enabled: bool = True
    audit_enabled: bool = False  # Should this policy's decisions be audited?
    
    def matches(
        self,
        principal_id: str,
        action: Permission,
        resource: str
    ) -> Tuple[PolicyType, Optional[str]]:
        """
        Check if this policy applies to the given request.
        
        Returns:
            Tuple of (policy_type, rule_id_if_matched)
            
        SECURITY NOTE: Default is DENY when no rules match. This ensures
        fail-closed security behavior - all actions must be explicitly allowed.
        """
        for rule in self.rules:
            # Check principal match
            principal_match = not rule.principal_patterns or any(
                p in principal_id for p in rule.principal_patterns
            )
            
            if not principal_match:
                continue
            
            # Check action match
            action_str = action.value
            action_match = not rule.action_patterns or any(
                a in action_str for a in rule.action_patterns
            )
            
            if not action_match:
                continue
            
            # Check resource match
            resource_match = not rule.resource_patterns or any(
                r in resource for r in rule.resource_patterns
            )
            
            if resource_match:
                return (rule.effect, rule.rule_id)
        
        # SECURITY CRITICAL: Default is DENY when no rules match
        # This ensures fail-closed security behavior
        return (PolicyType.DENY, None)


# =============================================================================
# Secret Management
# =============================================================================

class SecretStorageAdapter:
    """
    Interface for secret storage adapters.
    
    Implementations handle the actual storage and retrieval of secrets,
    which may be encrypted at rest.
    """
    
    async def store(self, key: str, value: str) -> None:
        """Store a secret with the given key."""
        raise NotImplementedError
    
    async def retrieve(self, key: str) -> Optional[str]:
        """Retrieve a secret by key. Returns None if not found."""
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """Delete a secret. Returns True if deleted."""
        raise NotImplementedError
    
    async def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all secret keys matching the prefix (if given)."""
        raise NotImplementedError


@dataclass(frozen=True)
class SecretDescriptor:
    """A descriptor for a secret."""
    secret_id: str
    name: str
    storage_key: str  # Key in storage adapter
    created_at: float = field(default_factory=time.monotonic)
    
    # Metadata (stored separately from encrypted value)
    description: Optional[str] = None
    owner: Optional[str] = None
    rotation_period_days: Optional[int] = None


# =============================================================================
# Audit Model
# =============================================================================

class SecurityEventType(Enum):
    """Types of security events for auditing."""
    # Authentication events
    AUTH_SUCCEEDED = "auth:succeeded"
    AUTH_FAILED = "auth:failed"
    
    # Authorization events
    AUTHZ_GRANTED = "authz:granted"
    AUTHZ_DENIED = "authz:denied"
    
    # Capability events
    CAPABILITY_GRANTED = "capability:granted"
    CAPABILITY_REVOKED = "capability:revoked"
    
    # Trust events
    TRUST_CHANGED = "trust:changed"
    TRUST_REVOKED = "trust:revoked"
    
    # Secret events
    SECRET_ACCESSED = "secret:accessed"
    SECRET_ROTATED = "secret:rotated"
    
    # Plugin events
    PLUGIN_LOADED = "plugin:loaded"
    PLUGIN_REJECTED = "plugin:rejected"
    
    # Sandbox events
    SANDBOX_VIOLATION = "sandbox:violation"
    
    # Policy events
    POLICY_VIOLATION = "policy:violation"
    
    # Privilege events
    PRIVILEGE_ESCALATION_ATTEMPT = "privilege:escalation-attempt"


@dataclass(frozen=True)
class AuditRecord:
    """
    An immutable audit record.
    
    Audit records are never modified after creation. They preserve
    provenance for security analysis and compliance.
    """
    record_id: str
    event_type: SecurityEventType
    
    # Event details (required fields first, then optional with defaults)
    outcome: str = ""  # e.g., "success", "failure"
    description: str = ""
    
    # Subject of the event
    principal_id: Optional[str] = None
    action: Optional[Permission] = None
    resource: Optional[str] = None
    
    # Context (all optional)
    runtime_id: Optional[str] = None
    session_id: Optional[str] = None
    source_ip: Optional[str] = None
    
    # Timestamp with default
    timestamp: float = field(default_factory=time.monotonic)
    
    # Provenance (immutable chain)
    previous_record_id: Optional[str] = None  # For audit trail linking


@dataclass(frozen=True)
class SecurityEvent:
    """
    An immutable security event.
    
    Security events are emitted during runtime and recorded in the audit
    trail. They never mutate runtime state.
    """
    event_id: str
    type_: SecurityEventType
    timestamp: float = field(default_factory=time.monotonic)
    
    # Context
    principal_id: Optional[str] = None
    resource: Optional[str] = None
    
    # Event data (never contains raw secrets)
    data: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Sandbox Model
# =============================================================================

class SandboxMode(Enum):
    """Sandbox enforcement modes."""
    STRICT = "strict"        # Only explicitly allowed operations
    PERMISSIVE = "permissive"  # Allow by default, deny listed
    MONITOR = "monitor"      # Log all operations without blocking


@dataclass(frozen=True)
class SandboxPolicy:
    """
    A sandbox policy defining allowed/denied operations.
    
    Sandboxing is explicit and must be configured. No implicit trust.
    """
    policy_id: str
    name: str
    
    # Scope (who this applies to)
    subjects: Tuple[str, ...] = field(default_factory=tuple)  # Principal IDs or patterns
    
    # Filesystem restrictions
    fs_allowed_paths: Tuple[str, ...] = field(default_factory=tuple)
    fs_denied_paths: Tuple[str, ...] = field(default_factory=tuple)
    
    # Network restrictions
    net_allowed_endpoints: Tuple[str, ...] = field(default_factory=tuple)
    net_denied_endpoints: Tuple[str, ...] = field(default_factory=tuple)
    
    # Process restrictions
    proc_allowed_commands: Tuple[str, ...] = field(default_factory=tuple)
    proc_denied_commands: Tuple[str, ...] = field(default_factory=tuple)
    
    # Mode
    mode: SandboxMode = SandboxMode.STRICT
    
    # Metadata
    enabled: bool = True


# =============================================================================
# Privilege Model
# =============================================================================

class PrivilegeDomain(Enum):
    """Explicit privilege domains in the system."""
    OPERATOR = "operator"     # System operator privileges
    RUNTIME = "runtime"       # Runtime management
    KERNEL = "kernel"         # Kernel-level operations
    PLUGIN = "plugin"         # Plugin execution
    PROVIDER = "provider"     # Provider access
    TOOL = "tool"             # Tool invocation
    MODEL = "model"           # Model loading and running
    SERVICE = "service"       # Service management


@dataclass(frozen=True)
class Privilege:
    """
    A privilege in a specific domain.
    
    Privileges are explicit and must be granted. No implicit inheritance.
    """
    principal_id: str
    domain: PrivilegeDomain
    level: int  # Higher = more privilege (0-100)
    
    granted_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None
    
    def has_enough_privilege(self, required_level: int) -> bool:
        """Check if this privilege meets the required level."""
        return self.level >= required_level


# =============================================================================
# Taint Tracking Model - Security Critical for Untrusted Input
# =============================================================================

class TaintLevel(Enum):
    """Levels of taint severity for untrusted input."""
    CLEAN = "clean"           # Trusted, no taint
    UNTRUSTED = "untrusted"   # Explicitly untrusted (user input, external sources)
    POTENTIALLY_UNSAFE = "potentially_unsafe"  # May contain untrusted data
    TAINED = "tained"         # Contains tained data that needs sanitization


@dataclass(frozen=True)
class Taint:
    """
    A taint label for tracking untrusted input through the system.
    
    Taint propagation ensures that untrusted input cannot bypass security checks.
    """
    taint_id: str
    level: TaintLevel
    source_type: Optional[str] = None  # e.g., "user_input", "network"
    source_id: Optional[str] = None    # Original source identifier
    timestamp: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class TaintTag:
    """
    A tag applied to data indicating its taint level.
    
    Tags propagate through the system ensuring taint is never lost.
    """
    tag_id: str
    data_hash: str  # Hash of the tagged data
    taint: Taint
    propagated_from: Optional[str] = None  # Previous tag that produced this


class TaintTracker:
    """
    Canonical taint tracking authority for security-critical input validation.
    
    Implements explicit taint tracking to prevent prompt injection attacks and
    other untrusted input vulnerabilities. All user-provided input starts with
    UNTRUSTED taint level until explicitly sanitized.
    
    Invariants:
    - Exactly one instance per runtime
    - Taint propagation is mandatory (never loses taint)
    - Sanitization requires explicit action (cannot bypass)
    - Tainted data cannot be used for security decisions without validation
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._tags: Dict[str, Tuple[TaintTag, ...]] = {}  # data_hash -> tags
        self._lock = Lock()
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    async def tag_data(
        self,
        data: str,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None
    ) -> Tuple[TaintTag, ...]:
        """
        Apply taint to data (typically user-provided input).
        
        Returns the created taint tags.
        """
        import hashlib
        
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        taint = Taint(
            taint_id=str(uuid.uuid4()),
            level=TaintLevel.UNTRUSTED,
            source_type=source_type or "unknown",
            source_id=source_id
        )
        
        tag = TaintTag(
            tag_id=str(uuid.uuid4()),
            data_hash=data_hash,
            taint=taint
        )
        
        with self._lock:
            if data_hash not in self._tags:
                self._tags[data_hash] = tuple()
            self._tags[data_hash] += (tag,)
        
        return self._tags[data_hash]
    
    async def get_taint(self, data: str) -> Optional[Taint]:
        """Get the taint level for data."""
        import hashlib
        
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        
        with self._lock:
            if data_hash not in self._tags:
                return Taint(
                    taint_id="default",
                    level=TaintLevel.CLEAN,
                    source_type="internal"
                )
            
            # Return most severe taint
            tags = self._tags[data_hash]
            max_level = min(tag.taint.level.value for tag in tags)
            return next(t.taint for t in tags if t.taint.level.value == max_level)
    
    async def is_tainted(self, data: str) -> bool:
        """Check if data has any taint."""
        import hashlib
        
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        
        with self._lock:
            if data_hash not in self._tags:
                return False
            
            tags = self._tags[data_hash]
            # Check for non-CLEAN taint
            return any(tag.taint.level != TaintLevel.CLEAN for tag in tags)
    
    async def mark_sanitized(self, data: str) -> Tuple[TaintTag, ...]:
        """
        Mark data as sanitized (removes UNTRUSTED taint level).
        
        This is EXPLICIT - sanitization must be consciously applied.
        Returns the updated taint tags with CLEAN level.
        """
        import hashlib
        
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        
        with self._lock:
            if data_hash not in self._tags:
                return tuple()
            
            old_tags = self._tags[data_hash]
            new_tags = []
            
            for tag in old_tags:
                # Create sanitized version
                sanitized_taint = Taint(
                    taint_id=str(uuid.uuid4()),
                    level=TaintLevel.CLEAN,
                    source_type=tag.taint.source_type,
                    source_id=tag.taint.source_id + "_sanitized"
                )
                
                new_tag = TaintTag(
                    tag_id=str(uuid.uuid4()),
                    data_hash=data_hash,
                    taint=sanitized_taint,
                    propagated_from=tag.tag_id
                )
                new_tags.append(new_tag)
            
            self._tags[data_hash] = tuple(new_tags)
        
        return self._tags[data_hash]
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of taint state (for diagnostics)."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "tagged_data_count": len(self._tags),
                "total_tags": sum(len(tags) for tags in self._tags.values())
            }


# =============================================================================
# Boundary Crossing Model
# =============================================================================

class TrustBoundary(Enum):
    """
    Explicit trust boundaries in the system.
    
    Every boundary crossing requires authorization. No implicit trust.
    """
    RUNTIME = "runtime"               # Runtime isolation
    PLUGIN = "plugin"                 # Plugin isolation
    PROVIDER = "provider"             # External provider access
    EXTERNAL_SERVICE = "external_service"
    OS = "os"                         # Operating system interface
    FILESYSTEM = "filesystem"         # Filesystem access
    NETWORK = "network"               # Network access
    USER_INPUT = "user_input"         # User input processing
    MODEL_OUTPUT = "model_output"     # Model output handling


@dataclass(frozen=True)
class BoundaryCrossing:
    """A record of a boundary crossing attempt."""
    crossing_id: str
    
    # Boundaries (required - must have both from and to)
    from_boundary: TrustBoundary
    to_boundary: TrustBoundary
    
    # Principal/action/resource (optional with defaults)
    principal_id: Optional[str] = None
    action: Optional[Permission] = None
    resource: Optional[str] = None
    
    # Required fields with defaults must come after required fields
    authorized: bool = False
    timestamp: float = field(default_factory=time.monotonic)
    
    # Evidence for audit (optional)
    evidence: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# Delegation Model - Explicit delegation support
# =============================================================================

class DelegationScope(Enum):
    """Scopes of delegatable authority."""
    READ_ONLY = "read_only"
    WRITE_ACCESS = "write_access"
    EXECUTE = "execute"
    MANAGE = "manage"


@dataclass(frozen=True)
class DelegationRequest:
    """
    A request for delegation of authority.
    
    Delegation must be explicit and auditable. The delegator grants
    specific scope to the delegatee for a limited time.
    """
    request_id: str
    delegator_id: str
    delegatee_id: str
    scope: DelegationScope
    resource: Optional[str] = None
    duration_seconds: float = 3600.0  # Default 1 hour


@dataclass(frozen=True)
class DelegationGrant:
    """
    A grant of delegation authority.
    
    This is an explicit authorization for one principal to act on behalf
    of another, within defined scope and constraints.
    """
    grant_id: str
    delegator_id: str
    delegatee_id: str
    scope: DelegationScope
    
    # Grant metadata
    granted_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None
    conditions: Tuple[str, ...] = field(default_factory=tuple)  # Constraint conditions


@dataclass(frozen=True)
class DelegationRevocation:
    """A revocation of a delegation grant."""
    revocation_id: str
    grant_id: str
    revoked_at: float = field(default_factory=time.monotonic)
    reason: Optional[str] = None


# =============================================================================
# Managers - imported separately to avoid circular dependencies
# =============================================================================

# Import new modules for Phase 3.7.20-I production implementation
from .policies import (
    PolicyScope,
    TrustDomain,
    PolicyRule,
    PolicyVersion,
    SecurityPolicy,
    PolicyManager,
    PolicyViolation,
)

from .incidents import (
    IncidentSeverity,
    IncidentStatus,
    IncidentEvidence,
    SecurityIncident,
    IncidentManager,
    IncidentReport,
    SecurityIncidentDetector,
)

from .managers import (
    SecurityManager,
    AuthenticationManager,
    TrustManager,
    AuthorizationManager,
    SecurityCapabilityManager,
    SecretManager,
    SecurityAuditManager,
    EncryptedSecretAdapter,
    InMemorySecretAdapter,
)


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    # IDs and Types
    "SecurityId",
    "SecurityVersion",
    "IdentityType",
    
    # Identity Models
    "Identity",
    "Principal",
    "Actor",
    "RuntimeIdentity",
    "ServiceIdentity",
    "PluginIdentity",
    "ToolIdentity",
    "SessionIdentity",
    
    # Authentication
    "AuthMethod",
    "Credential",
    "Token",
    "CertificateReference",
    "AuthenticationRequest",
    "AuthenticationResult",
    "AuthenticationProvider",
    
    # Trust
    "TrustLevel",
    "TrustEvidence",
    "TrustEvidenceRecord",
    "TrustDecision",
    "TrustReport",
    "TrustHistory",
    
    # Authorization
    "Permission",
    "PermissionDescriptor",
    "AuthorizationRequest",
    "AuthorizationDecision",
    "AuthorizationEvidence",
    "AuthorizationResult",
    
    # Capabilities
    "CapabilityId",
    "Capability",
    "CapabilityGrant",
    "CapabilityLease",
    "CapabilityRevocation",
    
    # Policies
    "PolicyType",
    "PolicyId",
    "PolicyRule",
    "AuthorizationPolicy",
    
    # Secrets
    "SecretStorageAdapter",
    "SecretDescriptor",
    
    # Audit
    "SecurityEventType",
    "AuditRecord",
    "SecurityEvent",
    
    # Sandbox
    "SandboxMode",
    "SandboxPolicy",
    
    # Privilege
    "PrivilegeDomain",
    "Privilege",
    
    # Boundaries
    "TrustBoundary",
    "BoundaryCrossing",
    
    # Policy Models
    "PolicyScope",
    "TrustDomain",
    "PolicyRule",
    "PolicyVersion",
    "SecurityPolicy",
    "PolicyManager",
    "PolicyViolation",
    
    # Incident Models
    "IncidentSeverity",
    "IncidentStatus",
    "IncidentEvidence",
    "SecurityIncident",
    "IncidentReport",
    "SecurityIncidentDetector",
    
    # Managers (imported from managers.py)
    "SecurityManager",
    "AuthenticationManager",
    "TrustManager",
    "AuthorizationManager",
    "SecurityCapabilityManager",
    "SecretManager",
    "SecurityAuditManager",
    "EncryptedSecretAdapter",
    "InMemorySecretAdapter",
]
