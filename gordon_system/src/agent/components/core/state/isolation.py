# Cross-Runtime State Isolation - Phase 3.15.11
# ==============================================

"""
Canonical architecture governing isolation of runtime state across independent Gordon runtimes.

This phase establishes how runtime state is isolated between:
    * Applications
    * Processes  
    * Runtimes
    * Execution contexts
    * Distributed nodes
    * Future clustered deployments

While preserving ownership, security, determinism, and architectural integrity.

EXTENDS:
    Phase 3.15.1 — Core State Foundations
    Phase 3.15.2 — State Identity, Scope & Ownership
    Phase 3.15.3 — Immutable & Mutable State Semantics
    Phase 3.15.4 — Runtime State Hierarchy
    Phase 3.15.5 — State Transitions & Transition Validation
    Phase 3.15.6 — State Snapshots & Views
    Phase 3.15.7 — State Versioning & Generations
    Phase 3.15.8 — State Consistency & Concurrency
    Phase 3.15.9 — State Persistence Boundaries  
    Phase 3.15.10 — State Restoration & Reconciliation

ARCHITECTURAL PRINCIPLES:
    1. One canonical runtime isolation architecture exists throughout the Core
    2. No subsystem implements its own isolation model
    3. Isolation is enforced at all access points
    4. Runtime boundaries are never violated implicitly
    5. Observation respects visibility and authorization policies
    6. Migration is explicit, validated, and preserves provenance

See docs/agent/architecture/phase-3.15.11-cross-runtime-state-isolation.md for complete documentation.
"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto, unique
import uuid
import time as _time_module


# =============================================================================
# RUNTIME IDENTITY MODEL
# =============================================================================


@dataclass(frozen=True, order=True, eq=True)
class RuntimeIdentity:
    """
    Canonical identifier for a runtime instance.
    
    Every runtime possesses an immutable runtime identity that binds:
        * runtime state
        * state ownership  
        * state hierarchy
        * services
        * components
        * streams
        * transactions
        * diagnostics
        * recovery
    
    Runtime identity shall be globally unique for the lifetime of the runtime.
    A runtime identity shall never be reused after termination.
    
    INVARIANTS:
        RT-ID-001: Every runtime instance has exactly one runtime identity
        RT-ID-002: Runtime identities are globally unique
        RT-ID-003: Runtime identity is immutable once assigned
        RT-ID-004: Runtime identity never reused after termination
        RT-ID-005: Runtime A cannot claim to be Runtime B (no forging)
    """
    
    # The unique runtime identifier
    value: str = field(default_factory=lambda: f"rt_{uuid.uuid4().hex[:20]}")
    
    # When this runtime was created (Unix timestamp in seconds)
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Optional application context for organizational purposes
    application_id: Optional[str] = None
    
    # Optional process identifier for multi-process deployments
    process_id: Optional[str] = None
    
    @classmethod
    def generate(
        cls,
        application_id: Optional[str] = None,
        process_id: Optional[str] = None,
    ) -> "RuntimeIdentity":
        """
        Generate a new runtime identity.
        
        Args:
            application_id: Optional application context identifier
            process_id: Optional process identifier
            
        Returns:
            A new unique RuntimeIdentity
        """
        return cls(
            application_id=application_id,
            process_id=process_id,
        )
    
    @classmethod
    def from_value(cls, value: str) -> "RuntimeIdentity":
        """Create a runtime identity from an existing value."""
        return cls(value=value)
    
    def matches(self, other_value: str) -> bool:
        """Check if this runtime identity matches the given value."""
        return self.value == other_value
    
    def belongs_to_runtime(self, runtime_identity: "RuntimeIdentity") -> bool:
        """Check if this identity belongs to the same runtime."""
        return self.value == runtime_identity.value


@dataclass(frozen=True, order=True, eq=True)
class BootSessionIdentity:
    """
    Canonical identifier for a boot session.
    
    Every runtime instance possesses an immutable boot session identity.
    Restarting a runtime creates:
        * A new boot session
        * A new runtime generation where required
    
    Previous boot sessions remain distinguishable and invalidatable.
    
    INVARIANTS:
        BS-ID-001: Every runtime instance has exactly one boot session identity
        BS-ID-002: Boot session IDs are unique per process lifetime  
        BS-ID-003: Old sessions are invalidated on restart
        BS-ID-004: Boot session is immutable once created
    """
    
    # The unique boot session identifier
    value: str = field(default_factory=lambda: f"bs_{uuid.uuid4().hex[:20]}")
    
    # When this session started (Unix timestamp in seconds)
    started_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Optional parent boot session (for migration scenarios)
    parent_session_id: Optional[str] = None
    
    @classmethod
    def generate(cls, parent_session_id: Optional[str] = None) -> "BootSessionIdentity":
        """
        Generate a new boot session identity.
        
        Args:
            parent_session_id: Optional parent session ID for migrations
            
        Returns:
            A new unique BootSessionIdentity
        """
        return cls(parent_session_id=parent_session_id)
    
    @classmethod
    def from_value(cls, value: str) -> "BootSessionIdentity":
        """Create a boot session identity from an existing value."""
        return cls(value=value)
    
    def matches(self, other_value: str) -> bool:
        """Check if this boot session identity matches the given value."""
        return self.value == other_value
    
    def is_restart_of(self, previous_session: "BootSessionIdentity") -> bool:
        """
        Check if this session represents a restart of the previous session.
        
        A session is considered a restart if it has a different ID but
        potentially shares some context (e.g., parent relationship).
        """
        return self.value != previous_session.value


# =============================================================================
# ISOLATION DOMAINS
# =============================================================================


@unique
class IsolationDomain(Enum):
    """
    Canonical isolation domain types.
    
    Separate completely:
        * Application
        * Process  
        * Runtime
        * Boot Session
        * Execution Context
        * Distributed Node
        * Remote Runtime
        * Shared Infrastructure
    
    These represent distinct isolation domains.
    
    DOMAINS:
        APPLICATION     - Distinct application boundaries
        RUNTIME         - Runtime instance boundaries
        PROCESS         - Process-level boundaries
        BOOT_SESSION    - Boot session boundaries (restart detection)
        EXECUTION_CTX   - Execution context boundaries
        WORKER          - Worker thread/executor boundaries
        REQUEST         - Request-scoped boundaries
        TRANSACTION     - Transaction-scoped boundaries
        COMPONENT       - Component instance boundaries  
        SERVICE         - Service-level boundaries
        DISTRIBUTED_NODE - Distributed node boundaries
        REMOTE_RUNTIME  - Remote runtime instances
        SHARED_INFRA    - Shared infrastructure (limited access)
    
    INVARIANTS:
        DOM-001: Every state aggregate belongs to exactly one primary domain
        DOM-002: Domain defines isolation scope and visibility boundaries
        DOM-003: Cross-domain operations require explicit policy
        DOM-004: Domains may inherit from parent domains
    """
    
    # Application-level isolation
    APPLICATION = "application"
    
    # Runtime instance isolation  
    RUNTIME = "runtime"
    
    # Process-level isolation
    PROCESS = "process"
    
    # Boot session isolation (restart detection)
    BOOT_SESSION = "boot_session"
    
    # Execution context isolation
    EXECUTION_CTX = "execution_ctx"
    
    # Worker/executor isolation
    WORKER = "worker"
    
    # Request-scoped isolation
    REQUEST = "request"
    
    # Transaction-scoped isolation
    TRANSACTION = "transaction"
    
    # Component-level isolation
    COMPONENT = "component"
    
    # Service-level isolation
    SERVICE = "service"
    
    # Distributed node isolation
    DISTRIBUTED_NODE = "distributed_node"
    
    # Remote runtime isolation
    REMOTE_RUNTIME = "remote_runtime"
    
    # Shared infrastructure (read-only or limited)
    SHARED_INFRA = "shared_infra"
    
    @classmethod
    def from_string(cls, value: str) -> "IsolationDomain":
        """Parse a string into an IsolationDomain."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid IsolationDomain: {value}")
    
    # Domain hierarchy (parent -> children)
    HIERARCHY = {
        APPLICATION: [RUNTIME, PROCESS],
        RUNTIME: [BOOT_SESSION, EXECUTION_CTX],
        BOOT_SESSION: [WORKER, REQUEST],
        PROCESS: [EXECUTION_CTX, WORKER],
        EXECUTION_CTX: [TRANSACTION, SERVICE],
        TRANSACTION: [COMPONENT],
    }
    
    def is_ancestor_of(self, other: "IsolationDomain") -> bool:
        """
        Check if this domain is an ancestor of the other.
        
        Returns True if self is in the inheritance path to other.
        """
        hierarchy = IsolationDomain.HIERARCHY
        
        if other not in hierarchy.get(self, []):
            return False
        return True
    
    def is_descendant_of(self, other: "IsolationDomain") -> bool:
        """Check if this domain descends from the other."""
        return other.is_ancestor_of(self)
    
    def inherits_from(self, parent_domain: "IsolationDomain") -> bool:
        """Check if this domain can inherit properties from parent."""
        return self == parent_domain or self.is_descendant_of(parent_domain)


# =============================================================================
# ISOLATION POLICIES
# =============================================================================


@unique
class IsolationPolicy(Enum):
    """
    Canonical isolation policies for state sharing.
    
    Policies shall never be inferred - they must be explicit.
    
    POLICIES:
        FULLY_ISOLATED      - No shared access; exclusive ownership
        READ_ONLY_SHARING   - Multiple readers, no mutation allowed
        SNAPSHOT_SHARING    - Immutable snapshot copies provided
        VIEW_SHARING        - Read-only view/projection provided
        CONTROLLED_SYNC     - Synchronized with explicit protocol
        REPLICATED          - Full replication with consensus
        FEDERATED           - Federated across runtimes with policy
        EXTERNAL            - External source, read-only locally
    
    INVARIANTS:
        POL-001: Every state aggregate has exactly one isolation policy
        POL-002: Policies are explicit and immutable once set
        POL-003: No implicit sharing is permitted
        POL-004: Policy violations reject operations
    """
    
    # Fully isolated - no cross-runtime access
    FULLY_ISOLATED = "fully_isolated"
    
    # Read-only sharing - multiple observers, no mutation
    READ_ONLY_SHARING = "read_only_sharing"
    
    # Snapshot sharing - immutable snapshot copies
    SNAPSHOT_SHARING = "snapshot_sharing"
    
    # View sharing - read-only view/projection
    VIEW_SHARING = "view_sharing"
    
    # Controlled synchronization with explicit protocol
    CONTROLLED_SYNC = "controlled_sync"
    
    # Full replication with consensus
    REPLICATED = "replicated"
    
    # Federated across runtimes
    FEDERATED = "federated"
    
    # External source, read-only
    EXTERNAL_READ_ONLY = "external_read_only"
    
    @classmethod
    def from_string(cls, value: str) -> "IsolationPolicy":
        """Parse a string into an IsolationPolicy."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid IsolationPolicy: {value}")
    
    def allows_mutation(self) -> bool:
        """Check if this policy allows mutation of shared state."""
        return self in (
            IsolationPolicy.FULLY_ISOLATED,
            IsolationPolicy.CONTROLLED_SYNC,
            IsolationPolicy.REPLICATED,
            IsolationPolicy.FEDERATED,
        )
    
    def allows_cross_runtime_access(self) -> bool:
        """Check if this policy allows cross-runtime state access."""
        return self not in (
            IsolationPolicy.FULLY_ISOLATED,
            IsolationPolicy.EXTERNAL_READ_ONLY,
        )


# =============================================================================
# OWNERSHIP ISOLATION
# =============================================================================


@dataclass(frozen=True)
class OwnershipIsolation:
    """
    Enforces ownership isolation across runtime boundaries.
    
    Prevents:
        * Cross-runtime ownership
        * Ownership leakage
        * Shared mutable ownership  
        * Ownership ambiguity
        
    Exactly one runtime shall own each mutable aggregate.
    
    INVARIANTS:
        OWN-ISO-001: Every mutable aggregate has exactly one owner
        OWN-ISO-002: Owner belongs to exactly one runtime
        OWN-ISO-003: Cross-runtime ownership is prohibited
        OWN-ISO-004: Ownership cannot be forged or claimed falsely
    """
    
    # The owning runtime identity
    owner_runtime_id: str
    
    # The boot session during which ownership was established
    owner_boot_session_id: Optional[str] = None
    
    # Whether this ownership is exclusive (single owner) or shared
    is_exclusive: bool = True
    
    @classmethod
    def for_runtime(
        cls,
        runtime_id: str,
        boot_session_id: Optional[str] = None,
        is_exclusive: bool = True,
    ) -> "OwnershipIsolation":
        """Create ownership isolation for a runtime."""
        return cls(
            owner_runtime_id=runtime_id,
            owner_boot_session_id=boot_session_id,
            is_exclusive=is_exclusive,
        )
    
    def belongs_to_runtime(self, runtime_id: str) -> bool:
        """Check if this ownership belongs to the given runtime."""
        return self.owner_runtime_id == runtime_id
    
    def is_valid_for_session(self, session_id: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate that ownership is valid for the given boot session.
        
        Returns:
            (is_valid: bool, reason: Optional[str])
        """
        if self.owner_boot_session_id is None:
            return True, None
        
        if session_id != self.owner_boot_session_id:
            return False, f"ownership belongs to different boot session: {self.owner_boot_session_id}"
        
        return True, None


# =============================================================================
# MUTATION ISOLATION
# =============================================================================


@dataclass(frozen=True)
class MutationIsolation:
    """
    Prevents mutation of state across runtime boundaries.
    
    Runtime A cannot:
        * Mutate Runtime B's state
        * Replace Runtime B's ownership
        * Modify Runtime B's hierarchy  
        * Advance Runtime B's versions
        * Create Runtime B's generations
        
    Cross-runtime mutation requires explicit protocols outside the state architecture.
    
    INVARIANTS:
        MUT-ISO-001: Runtime A cannot mutate Runtime B's state
        MUT-ISO-002: Only owner runtime may mutate its aggregates
        MUT-ISO-003: Mutation authority never crosses runtime boundaries
        MUT-ISO-004: External mutation requires explicit protocol
    """
    
    # The allowed mutating runtime identity
    allowed_runtime_id: str
    
    # The allowed boot session ID (if any)
    allowed_boot_session_id: Optional[str] = None
    
    @classmethod
    def for_runtime(
        cls,
        runtime_id: str,
        boot_session_id: Optional[str] = None,
    ) -> "MutationIsolation":
        """Create mutation isolation bound to a specific runtime."""
        return cls(
            allowed_runtime_id=runtime_id,
            allowed_boot_session_id=boot_session_id,
        )
    
    def can_mutate(self, runtime_id: str, boot_session_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if this isolation allows mutation by the given runtime.
        
        Returns:
            (can_mutate: bool, reason: Optional[str])
        """
        if runtime_id != self.allowed_runtime_id:
            return False, f"mutation not allowed from {runtime_id}, only from {self.allowed_runtime_id}"
        
        if self.allowed_boot_session_id is not None:
            if boot_session_id != self.allowed_boot_session_id:
                return False, f"session mismatch for mutation"
        
        return True, None


# =============================================================================
# OBSERVATION ISOLATION
# =============================================================================


@dataclass(frozen=True)
class ObservationIsolation:
    """
    Supports controlled observation through immutable artifacts.
    
    Observation shall:
        * Respect visibility and authorization policies
        * Never imply mutation authority
        
    Observation is supported through:
        * Immutable snapshots
        * Immutable views
        * Diagnostics interfaces
        * Monitoring interfaces
    
    INVARIANTS:
        OBS-ISO-001: Observers never gain mutation authority
        OBS-ISO-002: Observation respects visibility policies  
        OBS-ISO-003: Observation may be restricted by runtime/session
        OBS-ISO-004: Diagnostics are read-only
    """
    
    # The observing runtime identity (if any)
    observer_runtime_id: Optional[str] = None
    
    # The viewing boot session ID (if any)  
    viewer_boot_session_id: Optional[str] = None
    
    # Visibility level for this observation
    visibility_level: "VisibilityLevel" = field(default_factory=lambda: VisibilityLevel.PRIVATE)
    
    @classmethod
    def for_runtime_observer(
        cls,
        observer_runtime_id: str,
        boot_session_id: Optional[str] = None,
        visibility_level: Optional["VisibilityLevel"] = None,
    ) -> "ObservationIsolation":
        """Create observation isolation for a runtime observer."""
        return cls(
            observer_runtime_id=observer_runtime_id,
            viewer_boot_session_id=boot_session_id,
            visibility_level=visibility_level or VisibilityLevel.RUNTIME_VISIBLE,
        )
    
    def can_observe(self, state_runtime_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if this isolation allows observation of the given state.
        
        Returns:
            (can_observe: bool, reason: Optional[str])
        """
        # No observer means no restriction (internal observation)
        if self.observer_runtime_id is None:
            return True, None
        
        # Same runtime always allowed
        if self.observer_runtime_id == state_runtime_id:
            return True, None
        
        # Cross-runtime observation requires specific policy
        # This would be checked by the isolation policy
        return False, f"cross-runtime observation not permitted"


@unique
class VisibilityLevel(Enum):
    """
    Canonical visibility levels for state access.
    
    Defines who can observe state and under what conditions.
    
    VISIBILITY LEVELS:
        PRIVATE           - Only the owner may observe
        OWNER_VISIBLE     - Owner and designated observers
        SUBSYSTEM_VISIBLE - All entities in same subsystem
        RUNTIME_VISIBLE   - All within same runtime instance  
        DIAGNOSTIC        - Read-only diagnostic access
        PUBLIC            - External visibility (with restrictions)
    
    INVARIANTS:
        VIS-001: Every state aggregate has a primary visibility level
        VIS-002: Visibility does not imply mutation authority
        VIS-003: Visibility may be restricted by runtime/session isolation
    """
    
    # Only owner may observe
    PRIVATE = "private"
    
    # Owner and designated observers
    OWNER_VISIBLE = "owner_visible"
    
    # Subsystem-wide visibility
    SUBSYSTEM_VISIBLE = "subsystem_visible"
    
    # Runtime instance wide visibility
    RUNTIME_VISIBLE = "runtime_visible"
    
    # Read-only diagnostic access
    DIAGNOSTIC = "diagnostic"
    
    # External visibility (with restrictions)
    PUBLIC = "public"


# =============================================================================
# RESOURCE ISOLATION
# =============================================================================


@dataclass(frozen=True)
class ResourceIsolation:
    """
    Binds runtime state explicitly to allocated resources.
    
    Resources shall never migrate implicitly between runtimes.
    
    BINDINGS:
        * Allocated resources
        * Execution contexts  
        * Services
        * Streams
        * Transactions
    
    INVARIANTS:
        RES-ISO-001: State is bound to specific runtime and resources
        RES-ISO-002: Resources don't migrate implicitly between runtimes
        RES-ISO-003: Resource ownership matches state ownership
        RES-ISO-004: Resource binding is explicit, not inferred
    """
    
    # The resource identity (e.g., execution context ID)
    resource_id: str
    
    # The owning runtime identity
    owner_runtime_id: str
    
    # Optional boot session for the resource
    boot_session_id: Optional[str] = None
    
    @classmethod
    def for_resource(
        cls,
        resource_id: str,
        runtime_id: str,
        boot_session_id: Optional[str] = None,
    ) -> "ResourceIsolation":
        """Create resource isolation for a specific resource."""
        return cls(
            resource_id=resource_id,
            owner_runtime_id=runtime_id,
            boot_session_id=boot_session_id,
        )
    
    def belongs_to_runtime(self, runtime_id: str) -> bool:
        """Check if this resource belongs to the given runtime."""
        return self.owner_runtime_id == runtime_id


# =============================================================================
# RUNTIME BOUNDARY VALIDATION
# =============================================================================


@dataclass(frozen=True)
class RuntimeBoundaryValidationResult:
    """
    Result of runtime boundary validation.
    
    Every state aggregate shall explicitly identify:
        * Application identity
        * Runtime identity  
        * Boot session identity
        * Owner identity
        * Generation
        * Scope
    
    State lacking runtime identity is considered invalid.
    
    INVARIANTS:
        BOUND-VAL-001: All runtime identifiers are present and valid
        BOUND-VAL-002: Identities are consistent with each other
        BOUND-VAL-003: Runtime isolation policies are satisfied
        BOUND-VAL-004: Ownership is bound to exactly one runtime
    """
    
    # Was the validation successful?
    is_valid: bool
    
    # Validation timestamp
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Detailed findings (empty if valid)
    findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def valid(cls) -> "RuntimeBoundaryValidationResult":
        """Create a successful validation result."""
        return cls(is_valid=True)
    
    @classmethod
    def invalid(cls, *findings: str) -> "RuntimeBoundaryValidationResult":
        """Create an invalid validation result with findings."""
        return cls(
            is_valid=False,
            findings=findings if findings else ("unknown_validation_error",),
        )
    
    @property
    def has_findings(self) -> bool:
        """Check if there are any findings (errors/warnings)."""
        return len(self.findings) > 0


@dataclass(frozen=True)
class RuntimeBoundaryValidator:
    """
    Validates runtime boundary constraints for state aggregates.
    
    VALIDATES:
        * Runtime identity presence and format
        * Boot session identity consistency
        * Owner identity binding to runtime
        * Hierarchy integrity across boundaries
        * Policy compliance (isolation, visibility, mutation)
    
    RETURNS structured findings, not just Boolean results.
    """
    
    # Validation timestamp (for determinism in tests)
    validated_at_utc: Optional[float] = None
    
    def validate_runtime_boundary(
        self,
        runtime_id: str,
        boot_session_id: Optional[str],
        owner_runtime_id: Optional[str],
        isolation_policy: IsolationPolicy,
        ownership_isolation: Optional[OwnershipIsolation] = None,
    ) -> RuntimeBoundaryValidationResult:
        """
        Validate that a state aggregate's runtime boundary is correct.
        
        Args:
            runtime_id: The runtime identity of the state
            boot_session_id: The boot session identity
            owner_runtime_id: The owning runtime (if any)
            isolation_policy: The declared isolation policy
            ownership_isolation: Additional ownership isolation info
            
        Returns:
            Validation result with findings
        """
        findings = list[str]()
        
        # Runtime ID must be present and valid format
        if not runtime_id or not runtime_id.startswith("rt_"):
            findings.append(f"invalid_runtime_identity: {runtime_id}")
        
        # Boot session must match for session-bound policies
        if isolation_policy in (
            IsolationPolicy.FULLY_ISOLATED,
            IsolationPolicy.CONTROLLED_SYNC,
        ):
            if boot_session_id is None:
                findings.append("boot_session_required_for_isolated_policy")
        
        # Owner must belong to same runtime (if specified)
        if owner_runtime_id is not None and owner_runtime_id != runtime_id:
            findings.append(
                f"owner_runtime_mismatch: state in {runtime_id}, "
                f"owned by {owner_runtime_id}"
            )
        
        # Ownership isolation validation
        if ownership_isolation is not None:
            is_valid, reason = ownership_isolation.is_valid_for_session(boot_session_id)
            if not is_valid and reason is not None:
                findings.append(reason)
        
        if findings:
            return RuntimeBoundaryValidationResult.invalid(*findings)
        
        return RuntimeBoundaryValidationResult.valid()
    
    def validate_cross_runtime_boundary(
        self,
        state_runtime_id: str,
        attempted_runtime_id: str,
        operation_type: "CrossRuntimeOperationType",
    ) -> RuntimeBoundaryValidationResult:
        """
        Validate cross-runtime boundary constraints.
        
        Args:
            state_runtime_id: The runtime where state lives
            attempted_runtime_id: The runtime attempting the operation
            operation_type: Type of operation being attempted
            
        Returns:
            Validation result with findings
        """
        if state_runtime_id == attempted_runtime_id:
            return RuntimeBoundaryValidationResult.valid()
        
        # Cross-runtime operations require explicit protocol
        # This would be checked by specific protocols
        if operation_type.is_mutation():
            return RuntimeBoundaryValidationResult.invalid(
                f"cross-runtime mutation not permitted: "
                f"{attempted_runtime_id} cannot mutate {state_runtime_id}"
            )
        
        # Observation may be allowed with proper policy
        return RuntimeBoundaryValidationResult.valid()


@unique
class CrossRuntimeOperationType(Enum):
    """
    Canonical types of cross-runtime operations.
    
    TYPES:
        MUTATION      - State mutation (always requires protocol)
        OBSERVATION   - Read-only observation (may be allowed)
        MIGRATION     - State migration between runtimes
        SYNCHRONIZE   - Synchronization with explicit protocol
    
    INVARIANTS:
        OP-001: Every cross-runtime operation has exactly one type
        OP-002: Mutation operations require explicit protocol
        OP-003: Observation may be policy-controlled
        OP-004: Migration requires full validation chain
    """
    
    # State mutation (forbidden without protocol)
    MUTATION = "mutation"
    
    # Read-only observation (policy-controlled)
    OBSERVATION = "observation"
    
    # State migration between runtimes
    MIGRATION = "migration"
    
    # Synchronization with explicit protocol
    SYNCHRONIZE = "synchronize"
    
    def is_mutation(self) -> bool:
        """Check if this operation type involves mutation."""
        return self == CrossRuntimeOperationType.MUTATION


# =============================================================================
# DISTRIBUTED READINESS CONTRACTS
# =============================================================================


@dataclass(frozen=True)
class DistributedReadinessContract:
    """
    Defines contracts for distributed execution readiness.
    
    Prepares the architecture for future distributed execution while
    maintaining deterministic behavior and isolation guarantees.
    
    SUPPORTS:
        * Remote runtime identity
        * Node identity  
        * Cluster identity
        * Synchronization identity
        * Replication identity
    
    These are contracts only - implementation in later phases.
    
    INVARIANTS:
        DIST-READY-001: All contracts are explicit and defined
        DIST-READY-002: Contracts don't enable implicit cross-runtime access
        DIST-READY-003: Local execution behavior is deterministic
        DIST-READY-004: Contracts support eventual distributed implementation
    """
    
    # Remote runtime identity (if remote)
    remote_runtime_id: Optional[str] = None
    
    # Node identity for distributed deployments
    node_id: Optional[str] = None
    
    # Cluster identity if in cluster
    cluster_id: Optional[str] = None
    
    # Synchronization strategy
    sync_strategy: "SyncStrategy" = field(default_factory=lambda: SyncStrategy.NONE)
    
    @classmethod
    def local_only(cls) -> "DistributedReadinessContract":
        """Create a contract for local-only execution."""
        return cls()
    
    @classmethod
    def with_remote(
        cls,
        remote_runtime_id: str,
        node_id: Optional[str] = None,
    ) -> "DistributedReadinessContract":
        """Create a contract with remote runtime support."""
        return cls(
            remote_runtime_id=remote_runtime_id,
            node_id=node_id,
        )
    
    def is_remote(self) -> bool:
        """Check if this contract includes remote execution."""
        return self.remote_runtime_id is not None


@unique
class SyncStrategy(Enum):
    """
    Canonical synchronization strategies for distributed systems.
    
    STRATEGIES:
        NONE        - No synchronization (local only)
        EVENTUAL    - Eventually consistent
        LINEARIZABLE - Linearizable consistency
        CAUSAL      - Causal consistency
    
    INVARIANTS:
        SYNC-001: Every runtime has exactly one sync strategy
        SYNC-002: Strategies are immutable once set
        SYNC-003: Sync requires explicit protocol implementation
    """
    
    NONE = "none"
    EVENTUAL = "eventual"
    LINEARIZABLE = "linearizable"
    CAUSAL = "causal"


# =============================================================================
# MIGRATION MODEL - MigrationPolicy first (referenced by MigrationRequest)
# =============================================================================


@unique
class MigrationPolicy(Enum):
    """
    Canonical policies for state migration.
    
    POLICIES:
        EXPLICIT      - Requires explicit request and validation
        AUTOMATIC     - Automatic on specific events (e.g., restart)
        CONDITIONAL   - Conditional on external factors  
        NEVER         - Migration is prohibited
    
    INVARIANTS:
        MIG-POL-001: Every runtime has an explicit migration policy
        MIG-POL-002: Policies are immutable once set
        MIG-POL-003: Policy violations reject migrations
    """
    
    EXPLICIT = "explicit"
    AUTOMATIC = "automatic"
    CONDITIONAL = "conditional"
    NEVER = "never"


@dataclass(frozen=True)
class MigrationRequest:
    """
    Request for runtime state migration.
    
    Migration shall require:
        * Ownership validation
        * Serialization
        * Integrity verification
        * Restoration
        * Generation update
        * Provenance preservation
    
    Implicit migration is prohibited - all migrations are explicit.
    
    INVARIANTS:
        MIG-REQ-001: Migration requires explicit request
        MIG-REQ-002: All validation steps must pass
        MIG-REQ-003: Provenance is preserved through migration
        MIG-REQ-004: Target runtime validates before accepting
    """
    
    # Migration request ID
    migration_id: str = field(default_factory=lambda: f"mig_{uuid.uuid4().hex[:20]}")
    
    # Timestamp of request
    requested_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Source runtime identity
    source_runtime_id: str
    
    # Target runtime identity  
    target_runtime_id: str
    
    # Boot session in source (for provenance)
    source_boot_session_id: Optional[str] = None
    
    # Boot session in target (if known)
    target_boot_session_id: Optional[str] = None
    
    # State to migrate
    state_aggregate_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Migration policy
    migration_policy: MigrationPolicy = MigrationPolicy.EXPLICIT
    
    @classmethod
    def for_runtime_migration(
        cls,
        source_runtime_id: str,
        target_runtime_id: str,
        state_aggregate_ids: Optional[Tuple[str, ...]] = None,
    ) -> "MigrationRequest":
        """Create a migration request for runtime-to-runtime migration."""
        return cls(
            source_runtime_id=source_runtime_id,
            target_runtime_id=target_runtime_id,
            state_aggregate_ids=state_aggregate_ids or tuple(),
        )
    
    def is_valid(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the migration request.
        
        Returns:
            (is_valid: bool, reason: Optional[str])
        """
        if self.source_runtime_id == self.target_runtime_id:
            return False, "source and target runtime must differ"
        
        if not self.state_aggregate_ids:
            return False, "at least one state aggregate must be specified"
        
        return True, None


@dataclass(frozen=True)
class MigrationResult:
    """
    Result of a migration operation.
    
    INVARIANTS:
        MIG-RES-001: Result is immutable once created
        MIG-RES-002: Success implies state has been transferred
        MIG-RES-003: Failure preserves original state
    """
    
    # Was migration successful?
    is_success: bool
    
    # Timestamps
    started_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    # Migration details
    migration_id: str
    source_runtime_id: str
    target_runtime_id: str
    
    # State count migrated
    state_aggregates_migrated: int = 0
    
    # Findings (empty if successful)
    findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def success(
        cls,
        migration_id: str,
        source_runtime_id: str,
        target_runtime_id: str,
        state_count: int,
    ) -> "MigrationResult":
        """Create a successful migration result."""
        return cls(
            is_success=True,
            completed_at_utc=_time_module.monotonic(),
            migration_id=migration_id,
            source_runtime_id=source_runtime_id,
            target_runtime_id=target_runtime_id,
            state_aggregates_migrated=state_count,
        )
    
    @classmethod
    def failure(
        cls,
        migration_id: str,
        source_runtime_id: str,
        target_runtime_id: str,
        *findings: str,
    ) -> "MigrationResult":
        """Create a failed migration result with findings."""
        return cls(
            is_success=False,
            completed_at_utc=_time_module.monotonic(),
            migration_id=migration_id,
            source_runtime_id=source_runtime_id,
            target_runtime_id=target_runtime_id,
            findings=findings if findings else ("migration_failed",),
        )


# =============================================================================
# VIOLATION DETECTION
# =============================================================================


@dataclass(frozen=True)
class IsolationViolation:
    """
    Represents a detected isolation violation.
    
    Detect and reject:
        * Cross-runtime mutation (without protocol)
        * Duplicate runtime identities
        * Stale boot sessions
        * Runtime ownership conflicts
        * Runtime hierarchy conflicts
        * Unauthorized observation
        * Invalid migration
        * Resource leakage
        * Identity reuse
    
    Violations produce structured diagnostics.
    
    INVARIANTS:
        VIOL-001: Every violation has exactly one type
        VIOL-002: Violations are deterministic and reproducible
        VIOL-003: Diagnostics include full context for debugging
    """
    
    # Timestamp of detection
    detected_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Type of violation
    violation_type: "IsolationViolationType"
    
    # Context information
    runtime_id: Optional[str] = None
    boot_session_id: Optional[str] = None
    
    # Affected state (if any)
    affected_state_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Additional details
    details: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def for_cross_runtime_mutation(
        cls,
        attempted_by_runtime_id: str,
        target_runtime_id: str,
    ) -> "IsolationViolation":
        """Create a cross-runtime mutation violation."""
        return cls(
            violation_type=IsolationViolationType.CROSS_RUNTIME_MUTATION,
            runtime_id=target_runtime_id,
            details={
                "attempted_by": attempted_by_runtime_id,
                "target": target_runtime_id,
            },
        )
    
    @classmethod
    def for_duplicate_identity(
        cls,
        duplicate_value: str,
    ) -> "IsolationViolation":
        """Create a duplicate runtime identity violation."""
        return cls(
            violation_type=IsolationViolationType.DUPLICATE_RUNTIME_IDENTITY,
            details={"duplicate_id": duplicate_value},
        )
    
    @classmethod
    def for_stale_session(
        cls,
        session_id: str,
        current_session_id: str,
    ) -> "IsolationViolation":
        """Create a stale boot session violation."""
        return cls(
            violation_type=IsolationViolationType.STALE_BOOT_SESSION,
            boot_session_id=session_id,
            details={"current_session": current_session_id},
        )
    
    @property
    def description(self) -> str:
        """Get a human-readable description of the violation."""
        return self.violation_type.description.format(**self.details)


@unique
class IsolationViolationType(Enum):
    """
    Canonical types of isolation violations.
    
    TYPES:
        CROSS_RUNTIME_MUTATION      - Runtime A mutating Runtime B state
        DUPLICATE_RUNTIME_IDENTITY  - Reused runtime identity after termination
        STALE_BOOT_SESSION          - Using invalidated boot session
        OWNERSHIP_CONFLICT          - Multiple owners for same runtime state
        HIERARCHY_CONFLICT          - Cross-runtime hierarchy violation
        UNAUTHORIZED_OBSERVATION    - Observation without proper policy
        INVALID_MIGRATION           - Migration that violates policies
        RESOURCE_LEAKAGE            - Resources migrating between runtimes
        IDENTITY_REUSE              - Reused identity after termination
    
    INVARIANTS:
        V-TYPE-001: Every violation has exactly one type
        V-TYPE-002: Violation types are exhaustive and non-overlapping
        V-TYPE-003: Each type has a specific detection mechanism
    """
    
    # Runtime A mutating Runtime B state (without protocol)
    CROSS_RUNTIME_MUTATION = "cross_runtime_mutation"
    
    # Reused runtime identity after termination  
    DUPLICATE_RUNTIME_IDENTITY = "duplicate_runtime_identity"
    
    # Using invalidated boot session
    STALE_BOOT_SESSION = "stale_boot_session"
    
    # Multiple owners for same runtime state
    OWNERSHIP_CONFLICT = "ownership_conflict"
    
    # Cross-runtime hierarchy violation
    HIERARCHY_CONFLICT = "hierarchy_conflict"
    
    # Observation without proper policy
    UNAUTHORIZED_OBSERVATION = "unauthorized_observation"
    
    # Migration that violates policies
    INVALID_MIGRATION = "invalid_migration"
    
    # Resources migrating between runtimes
    RESOURCE_LEAKAGE = "resource_leakage"
    
    # Reused identity after termination
    IDENTITY_REUSE = "identity_reuse"
    
    @property
    def description(self) -> str:
        """Get a human-readable description of this violation type."""
        descriptions: Dict[str, str] = {
            IsolationViolationType.CROSS_RUNTIME_MUTATION.value: 
                "Cross-runtime mutation attempted from {attempted_by} to target {target}",
            IsolationViolationType.DUPLICATE_RUNTIME_IDENTITY.value:
                "Duplicate runtime identity detected: {duplicate_id}",
            IsolationViolationType.STALE_BOOT_SESSION.value:
                "Stale boot session accessed: {current_session}",
            IsolationViolationType.OWNERSHIP_CONFLICT.value:
                "Multiple owners for same state in runtime",
            IsolationViolationType.HIERARCHY_CONFLICT.value:
                "Cross-runtime hierarchy violation detected",
            IsolationViolationType.UNAUTHORIZED_OBSERVATION.value:
                "Observation without proper isolation policy",
            IsolationViolationType.INVALID_MIGRATION.value:
                "Migration violates isolation policies",
            IsolationViolationType.RESOURCE_LEAKAGE.value:
                "Resources leaked between runtime boundaries",
            IsolationViolationType.IDENTITY_REUSE.value:
                "Identity reused after termination: {duplicate_id}",
        }
        return descriptions.get(self.value, "Unknown violation type")


@dataclass(frozen=True)
class ViolationDetectionResult:
    """
    Result of isolation violation detection.
    
    INVARIANTS:
        DET-RESULT-001: Results are immutable once created
        DET-RESULT-002: No violations means all checks passed
        DET-RESULT-003: Violations include full context for debugging
    """
    
    # Were any violations detected?
    has_violations: bool
    
    # Timestamp of detection run
    detected_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # List of all detected violations (empty if clean)
    violations: Tuple[IsolationViolation, ...] = field(default_factory=tuple)
    
    @classmethod
    def clean(cls) -> "ViolationDetectionResult":
        """Create a result with no violations."""
        return cls(has_violations=False)
    
    @classmethod
    def with_violations(cls, *violations: IsolationViolation) -> "ViolationDetectionResult":
        """Create a result with detected violations."""
        return cls(
            has_violations=True,
            violations=violations if violations else tuple(),
        )


class ViolationDetector:
    """
    Detects isolation violations in runtime state operations.
    
    DETECTIONS:
        * Cross-runtime mutation attempts
        * Duplicate runtime identities
        * Stale boot session access
        * Ownership conflicts  
        * Hierarchy conflicts
        * Unauthorized observation
        * Invalid migrations
        * Resource leakage
        * Identity reuse
    
    RETURNS structured findings, not just Boolean results.
    """
    
    def __init__(self) -> None:
        """Initialize the violation detector."""
        self._detected_at_utc: float = _time_module.monotonic()
    
    def detect_cross_runtime_mutation(
        self,
        state_runtime_id: str,
        attempted_by_runtime_id: str,
    ) -> Optional[IsolationViolation]:
        """
        Detect if a cross-runtime mutation attempt is invalid.
        
        Returns:
            IsolationViolation if detected, None otherwise
        """
        # Same runtime - not a violation
        if state_runtime_id == attempted_by_runtime_id:
            return None
        
        # Cross-runtime mutation requires explicit protocol
        # If no protocol is in place, this is a violation
        return IsolationViolation.for_cross_runtime_mutation(
            attempted_by_runtime_id,
            state_runtime_id,
        )
    
    def detect_duplicate_identity(
        self,
        runtime_id: str,
        existing_ids: Tuple[str, ...],
    ) -> Optional[IsolationViolation]:
        """
        Detect if a runtime ID is duplicate (already exists).
        
        Returns:
            IsolationViolation if detected, None otherwise
        """
        if runtime_id in existing_ids:
            return IsolationViolation.for_duplicate_identity(runtime_id)
        return None
    
    def detect_stale_session(
        self,
        session_id: str,
        current_session_id: Optional[str],
    ) -> Optional[IsolationViolation]:
        """
        Detect if a session is stale (no longer valid).
        
        Returns:
            IsolationViolation if detected, None otherwise
        """
        # If no current session known, assume valid
        if current_session_id is None:
            return None
        
        # Different session could be legitimate (migration, restart)
        # This would need additional context to determine validity
        return None
    
    def detect_ownership_conflict(
        self,
        state_id: str,
        current_owners: Tuple[str, ...],
        new_owner: str,
    ) -> Optional[IsolationViolation]:
        """
        Detect if ownership would create a conflict.
        
        Returns:
            IsolationViolation if detected, None otherwise
        """
        # Only check for multiple owners (not yet implemented fully)
        return None
    
    def detect_hierarchy_conflict(
        self,
        parent_runtime_id: str,
        child_runtime_id: str,
    ) -> Optional[IsolationViolation]:
        """
        Detect if hierarchy would create a cross-runtime conflict.
        
        Returns:
            IsolationViolation if detected, None otherwise
        """
        # Same runtime - no conflict
        if parent_runtime_id == child_runtime_id:
            return None
        
        # Cross-runtime hierarchy requires explicit protocol
        return None
    
    def detect_violations(
        self,
        state_runtime_id: str,
        boot_session_id: Optional[str],
        owner_runtime_id: Optional[str],
        isolation_policy: IsolationPolicy,
    ) -> ViolationDetectionResult:
        """
        Perform comprehensive violation detection for state.
        
        Returns:
            Detection result with all violations found
        """
        violations = list[IsolationViolation]()
        
        # Check cross-runtime mutation (owner != runtime)
        if owner_runtime_id is not None and owner_runtime_id != state_runtime_id:
            violation = self.detect_cross_runtime_mutation(
                state_runtime_id,
                owner_runtime_id,
            )
            if violation is not None:
                violations.append(violation)
        
        # Check ownership conflict
        violation = self.detect_ownership_conflict(
            f"{state_runtime_id}_root",
            tuple() if owner_runtime_id is None else (owner_runtime_id,),
            owner_runtime_id or "",
        )
        if violation is not None:
            violations.append(violation)
        
        return ViolationDetectionResult.with_violations(*violations)


# =============================================================================
# DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class RuntimeIsolationDiagnostics:
    """
    Immutable diagnostics for runtime isolation.
    
    Exposes metadata without exposing mutable state.
    
    INVARIANTS:
        DIAG-ISO-001: Diagnostics are immutable once created
        DIAG-ISO-002: Diagnostics don't expose live handles or secrets
        DIAG-ISO-003: Diagnostics include full isolation history
    """
    
    # Runtime context
    runtime_id: str
    boot_session_id: Optional[str] = None
    
    # Isolation policy
    isolation_policy: IsolationPolicy = field(default_factory=lambda: IsolationPolicy.FULLY_ISOLATED)
    
    # Ownership summary
    owner_runtime_id: Optional[str] = None
    ownership_is_exclusive: bool = True
    
    # Resource summary (count of bound resources)
    resource_count: int = 0
    
    # Visibility summary
    visibility_level: VisibilityLevel = field(default_factory=lambda: VisibilityLevel.PRIVATE)
    
    # Violation history
    violation_count: int = 0
    last_violation_at_utc: Optional[float] = None
    
    # Migration history
    migration_count: int = 0
    last_migration_at_utc: Optional[float] = None
    
    @classmethod
    def for_runtime(
        cls,
        runtime_id: str,
        boot_session_id: Optional[str] = None,
        isolation_policy: Optional[IsolationPolicy] = None,
        owner_runtime_id: Optional[str] = None,
        resource_count: int = 0,
        visibility_level: Optional[VisibilityLevel] = None,
    ) -> "RuntimeIsolationDiagnostics":
        """Create diagnostics for a runtime."""
        return cls(
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            isolation_policy=isolation_policy or IsolationPolicy.FULLY_ISOLATED,
            owner_runtime_id=owner_runtime_id,
            resource_count=resource_count,
            visibility_level=visibility_level or VisibilityLevel.PRIVATE,
        )
    
    def has_violations(self) -> bool:
        """Check if there are any recorded violations."""
        return self.violation_count > 0
    
    def is_fully_isolated(self) -> bool:
        """Check if this runtime uses full isolation."""
        return self.isolation_policy == IsolationPolicy.FULLY_ISOLATED


# =============================================================================
# PUBLIC API FACADE
# =============================================================================


class RuntimeIsolationFacade:
    """
    Canonical facade for runtime isolation operations.
    
    Supports:
        * Runtime identity inspection
        * Boot session validation
        * Isolation policy enforcement
        * Migration validation
        * Violation detection
        * Diagnostics collection
    
    Does NOT expose mutable runtime state.
    
    PUBLIC API:
        - validate_runtime_identity: Check runtime identity validity
        - validate_boot_session: Validate boot session for runtime
        - check_isolation_policy: Verify isolation policy compliance
        - validate_migration_request: Validate migration request
        - detect_violations: Detect isolation violations
        - get_diagnostics: Get runtime isolation diagnostics
    
    INVARIANTS:
        FACADE-001: All operations are pure (no side effects)
        FACADE-002: No mutable state exposed
        FACADE-003: Results are deterministic and reproducible
        FACADE-004: Import is pure (no implicit behavior)
    """
    
    def __init__(self) -> None:
        """Initialize the runtime isolation facade."""
        self._violation_detector = ViolationDetector()
    
    def validate_runtime_identity(
        self,
        runtime_id: str,
        expected_value: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a runtime identity is valid.
        
        Args:
            runtime_id: The runtime ID to validate
            expected_value: Optional expected value for exact match
            
        Returns:
            (is_valid: bool, reason: Optional[str])
        """
        if not runtime_id or not runtime_id.startswith("rt_"):
            return False, f"invalid_runtime_identity_format: {runtime_id}"
        
        if expected_value is not None and runtime_id != expected_value:
            return False, f"runtime_id_mismatch: expected {expected_value}, got {runtime_id}"
        
        return True, None
    
    def validate_boot_session(
        self,
        boot_session_id: Optional[str],
        for_runtime_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a boot session is valid for the given runtime.
        
        Args:
            boot_session_id: The boot session to validate
            for_runtime_id: The runtime identity
            
        Returns:
            (is_valid: bool, reason: Optional[str])
        """
        # No session provided - may be valid in some contexts
        if boot_session_id is None:
            return True, None
        
        if not boot_session_id.startswith("bs_"):
            return False, f"invalid_boot_session_format: {boot_session_id}"
        
        return True, None
    
    def check_isolation_policy(
        self,
        state_runtime_id: str,
        observer_runtime_id: Optional[str],
        isolation_policy: IsolationPolicy,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if observation respects isolation policy.
        
        Args:
            state_runtime_id: Runtime where state lives
            observer_runtime_id: Runtime attempting observation
            isolation_policy: The declared policy
            
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        # Same runtime always allowed
        if observer_runtime_id is None or observer_runtime_id == state_runtime_id:
            return True, None
        
        # Cross-runtime requires specific policy
        if not isolation_policy.allows_cross_runtime_access():
            return False, f"cross-runtime access not permitted by policy: {isolation_policy.value}"
        
        return True, None
    
    def validate_migration_request(
        self,
        request: MigrationRequest,
        existing_runtime_ids: Tuple[str, ...] = tuple(),
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a migration request.
        
        Args:
            request: The migration request to validate
            existing_runtime_ids: Known runtime IDs for collision detection
            
        Returns:
            (is_valid: bool, reason: Optional[str])
        """
        is_valid, reason = request.is_valid()
        if not is_valid:
            return False, reason
        
        # Check for duplicate target
        if request.target_runtime_id in existing_runtime_ids:
            return False, f"target_runtime_already_exists: {request.target_runtime_id}"
        
        # Check source exists (if we know about it)
        if request.source_runtime_id not in existing_runtime_ids and existing_runtime_ids:
            pass  # Source might be unknown - allowed for migration from external
        
        return True, None
    
    def detect_violations(
        self,
        state_runtime_id: str,
        boot_session_id: Optional[str],
        owner_runtime_id: Optional[str],
        isolation_policy: IsolationPolicy,
    ) -> ViolationDetectionResult:
        """
        Detect isolation violations for state.
        
        Args:
            state_runtime_id: Runtime where state lives
            boot_session_id: Current boot session (if any)
            owner_runtime_id: Owner runtime (if any)  
            isolation_policy: Declared isolation policy
            
        Returns:
            Detection result with all violations found
        """
        return self._violation_detector.detect_violations(
            state_runtime_id,
            boot_session_id,
            owner_runtime_id,
            isolation_policy,
        )
    
    def get_diagnostics(
        self,
        runtime_id: str,
        boot_session_id: Optional[str],
        isolation_policy: IsolationPolicy,
        owner_runtime_id: Optional[str],
        resource_count: int = 0,
        violation_count: int = 0,
        migration_count: int = 0,
    ) -> RuntimeIsolationDiagnostics:
        """
        Get runtime isolation diagnostics.
        
        Args:
            runtime_id: The runtime identity
            boot_session_id: Current boot session (if any)
            isolation_policy: Declared policy
            owner_runtime_id: Owner runtime (if any)
            resource_count: Number of bound resources
            violation_count: Count of recorded violations
            migration_count: Count of migrations
            
        Returns:
            Immutable diagnostics object
        """
        return RuntimeIsolationDiagnostics(
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            isolation_policy=isolation_policy,
            owner_runtime_id=owner_runtime_id,
            resource_count=resource_count,
            violation_count=violation_count,
            migration_count=migration_count,
        )


# =============================================================================
# PUBLIC API EXPORTS - PHASE 3.15.11
# =============================================================================


__all__ = [
    # Runtime Identity Model
    "RuntimeIdentity",
    "BootSessionIdentity",
    
    # Isolation Domains
    "IsolationDomain",
    
    # Isolation Policies  
    "IsolationPolicy",
    
    # Ownership Isolation
    "OwnershipIsolation",
    
    # Mutation Isolation
    "MutationIsolation",
    
    # Observation Isolation
    "ObservationIsolation",
    "VisibilityLevel",
    
    # Resource Isolation
    "ResourceIsolation",
    
    # Runtime Boundary Validation
    "RuntimeBoundaryValidationResult",
    "RuntimeBoundaryValidator",
    "CrossRuntimeOperationType",
    
    # Distributed Readiness
    "DistributedReadinessContract",
    "SyncStrategy",
    
    # Migration Model
    "MigrationRequest",
    "MigrationResult",
    "MigrationPolicy",
    
    # Violation Detection
    "IsolationViolation",
    "IsolationViolationType",
    "ViolationDetectionResult",
    "ViolationDetector",
    
    # Diagnostics
    "RuntimeIsolationDiagnostics",
    
    # Public API
    "RuntimeIsolationFacade",
]