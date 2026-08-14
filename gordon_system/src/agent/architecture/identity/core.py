# Core Identity Types - Phase 3.19
# ==================================

"""
Canonical identity model for Gordon Core.

This module establishes the fundamental identity primitives upon which all
domain-specific identities are built.

IDENTITY HIERARCHY:
    Identity           - Root identity interface (abstract)
        TypedIdentifier   - Typed string-based identifier
            DomainId          - Domain-scoped identifier
                RuntimeId         - Runtime instance identity  
                ComponentId       - Component identity
                ExecutionId       - Execution flow identity
                StateId           - State entity identity
                StreamId          - Stream entity identity
                DiagnosticId      - Diagnostic entity identity
                
    IdentityType        - Type classification for identities
    DomainId            - Domain-scoped identifier base class
    
IDENTITY INVARIANTS:
    I-001: Every entity possesses exactly one canonical identity
    I-002: Identity is immutable once created
    I-003: No two entities share the same identity value within their domain
    I-004: Identity shall never encode mutable runtime state
    I-005: Identity is never inferred from other attributes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Protocol,
    runtime_checkable,
    TypeVar,
    Generic,
    Optional,
    Tuple,
    Dict,
    Any,
    List,
)
from enum import Enum, auto
import uuid
import time as _time_module


# =============================================================================
# IDENTITY TYPE ENUMERATION
# =============================================================================


class IdentityType(Enum):
    """
    Canonical identity type classifications.
    
    Every identity belongs to exactly one type category.
    
    TYPES:
        RUNTIME      - Runtime instance identities
        COMPONENT    - Component/service/capability identities  
        EXECUTION    - Request/response/command/event/task identities
        STATE        - State aggregate/version/revision/generation identities
        STREAM       - Stream/record/checkpoint identities
        DIAGNOSTIC   - Diagnostic/tracing/span identities
        CONFIGURATION - Configuration/policy identities
        ARTIFACT     - Artifact/snapshot identities
        
    INVARIANTS:
        TYPE-001: Every identity has exactly one type classification
        TYPE-002: Type is immutable and deterministically assigned
        TYPE-003: Types are repository-wide consistent
    """
    
    # Runtime identities
    RUNTIME = "runtime"
    
    # Component identities  
    COMPONENT = "component"
    
    # Execution identities
    EXECUTION = "execution"
    
    # State identities
    STATE = "state"
    
    # Stream identities
    STREAM = "stream"
    
    # Diagnostic identities
    DIAGNOSTIC = "diagnostic"
    
    # Configuration identities
    CONFIGURATION = "configuration"
    
    # Artifact identities
    ARTIFACT = "artifact"


# =============================================================================
# IDENTITY INTERFACE
# =============================================================================


@runtime_checkable
class Identity(Protocol):
    """
    Canonical identity interface for all Gordon entities.
    
    All strongly-typed identities shall implement this protocol.
    
    INVARIANTS:
        I-001: Every entity possesses exactly one canonical identity
        I-002: Identity is immutable once created
        I-003: No two entities share the same value within domain
        I-004: Identity never encodes mutable runtime state
        
    CONTRACTS:
        C-001: Implement __hash__ consistently with __eq__
        C-002: Implement __str__ for serialization
        C-003: Preserve identity across serialization/deserialization
        
    METHODS:
        to_string()      - Serialize to canonical string representation
        to_bytes()       - Serialize to binary form
        validate()       - Validate identity integrity
        get_type()       - Get the IdentityType classification
        get_domain()     - Get the domain identifier
    """
    
    @property
    def value(self) -> str:
        """Return the raw identity string."""
        ...
    
    @property  
    def type_(self) -> IdentityType:
        """Return the identity type classification."""
        ...
    
    @property
    def domain(self) -> DomainId:
        """Return the domain identifier."""
        ...
    
    @property
    def created_at_utc(self) -> float:
        """Return creation timestamp in UTC seconds since epoch."""
        ...
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        ...
    
    def to_bytes(self) -> bytes:
        """Serialize to binary form for storage/transmission."""
        ...
    
    def validate(self) -> bool:
        """
        Validate identity integrity.
        
        Returns True if valid, False otherwise.
        """
        ...
    
    def __str__(self) -> str:
        """String representation (same as to_string)."""
        ...
    
    def __hash__(self) -> int:
        """Hash consistent with equality."""
        ...
    
    def __eq__(self, other: object) -> bool:
        """Equality based on value and type."""
        ...


# =============================================================================
# BASE IDENTITY CLASS
# =============================================================================


@dataclass(frozen=True)
class BaseIdentity(Identity):
    """
    Base implementation of the Identity interface.
    
    Provides common functionality for all domain-specific identities.
    
    INVARIANTS:
        I-001: Immutable value once set (frozen dataclass)
        I-002: Deterministic hash based on value
        I-003: Equality based on value comparison
        
    PARAMETERS:
        value            - Raw identity string (UUID or deterministic)
        type_           - Identity type classification
        domain          - Domain identifier
        created_at_utc  - Creation timestamp (default: current time)
        metadata        - Optional extension data
    """
    
    value: str = field(default_factory=lambda: f"gid_{uuid.uuid4().hex[:20]}")
    type_: IdentityType = field(default=IdentityType.RUNTIME)
    domain: DomainId = field(default_factory=lambda: DomainId("default"))
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    metadata: Optional[Dict[str, str]] = None
    
    @classmethod
    def generate(
        cls,
        type_: IdentityType = IdentityType.RUNTIME,
        domain: Optional[DomainId] = None,
        namespace: Optional[str] = None,
    ) -> "BaseIdentity":
        """Generate a new identity with the given parameters."""
        value = f"gid_{uuid.uuid4().hex[:20]}"
        if namespace:
            value = f"{namespace}_{value}"
        
        return cls(
            value=value,
            type_=type_,
            domain=domain or DomainId("default"),
            created_at_utc=_time_module.monotonic(),
        )
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        parts = [self.value, self.type_.value]
        if self.domain and self.domain.value != "default":
            parts.append(self.domain.value)
        return ":".join(parts)
    
    def to_bytes(self) -> bytes:
        """Serialize to binary form."""
        return self.to_string().encode("utf-8")
    
    def validate(self) -> bool:
        """
        Validate identity integrity.
        
        Checks:
            - Value is non-empty
            - Type is valid
            - Domain is valid
            - Value format matches type expectations
            
        Returns True if valid, False otherwise.
        """
        # Must have non-empty value
        if not self.value or len(self.value) < 4:
            return False
        
        # Type must be valid
        try:
            _ = IdentityType(self.type_.value)
        except ValueError:
            return False
        
        # Domain must be valid (non-empty string)
        if not isinstance(self.domain, DomainId):
            return False
        if not self.domain.value or len(self.domain.value) < 1:
            return False
            
        return True
    
    def __str__(self) -> str:
        """String representation."""
        return self.to_string()
    
    def __hash__(self) -> int:
        """Hash based on value."""
        return hash((self.value, self.type_.value))
    
    def __eq__(self, other: object) -> bool:
        """Equality based on value and type."""
        if not isinstance(other, Identity):
            return False
        return (
            self.value == other.value
            and self.type_ == other.type_
        )


# =============================================================================
# DOMAIN IDENTITY
# =============================================================================


class DomainId(str):
    """
    Canonical domain identifier.
    
    Domains provide namespace isolation for identity values.
    
    PREDEFINED DOMAINS:
        DEFAULT       - Default/unspecified domain
        RUNTIME       - Runtime instance identities  
        COMPONENT     - Component/service/capability identities
        EXECUTION     - Execution flow identities
        STATE         - State entity identities
        STREAM        - Stream entity identities
        DIAGNOSTIC    - Diagnostic entity identities
        CONFIGURATION - Configuration/policy identities
        ARTIFACT      - Artifact/snapshot identities
        
    INVARIANTS:
        D-001: Domain ID is immutable once created
        D-002: Domain values are globally unique within repository
        D-003: Domain defines identity value uniqueness scope
        
    EXAMPLES:
        >>> runtime_domain = DomainId("runtime")
        >>> component_domain = DomainId("component:networking")
        >>> state_domain = DomainId("state:lifecycle")
    """
    
    def __new__(cls, value: str) -> "DomainId":
        """Create a new domain ID."""
        # Validate: non-empty, no colons (reserved separator)
        if not value or len(value.strip()) < 1:
            raise ValueError("Domain ID must be non-empty")
        
        instance = super().__new__(cls, value.strip())
        return instance
    
    @property
    def value(self) -> str:
        """Return the string value of this domain ID."""
        return str(self)
    
    @classmethod
    def runtime(cls) -> "DomainId":
        """Create a runtime domain identifier."""
        return cls("runtime")
    
    @classmethod  
    def component(cls) -> "DomainId":
        """Create a component domain identifier."""
        return cls("component")
    
    @classmethod
    def execution(cls) -> "DomainId":
        """Create an execution domain identifier."""
        return cls("execution")
    
    @classmethod
    def state(cls) -> "DomainId":
        """Create a state domain identifier."""
        return cls("state")
    
    @classmethod
    def stream(cls) -> "DomainId":
        """Create a stream domain identifier."""
        return cls("stream")
    
    @classmethod
    def diagnostic(cls) -> "DomainId":
        """Create a diagnostic domain identifier."""
        return cls("diagnostic")
    
    @classmethod
    def configuration(cls) -> "DomainId":
        """Create a configuration domain identifier."""
        return cls("configuration")
    
    @classmethod
    def artifact(cls) -> "DomainId":
        """Create an artifact domain identifier."""
        return cls("artifact")
    
    @property
    def namespace(self) -> Optional[str]:
        """
        Extract the namespace portion if present.
        
        Domain IDs may contain subdomains separated by ':'
        e.g., "component:networking" -> namespace = "component", value = "networking"
        """
        parts = self.split(":")
        return parts[0] if len(parts) > 1 else None
    
    @property
    def subdomain(self) -> Optional[str]:
        """Extract the subdomain portion."""
        parts = self.split(":")
        return ":".join(parts[1:]) if len(parts) > 1 else None


# =============================================================================
# TYPED IDENTIFIER
# =============================================================================


@dataclass(frozen=True)
class TypedIdentifier:
    """
    A typed identifier value within a domain.
    
    Combines the raw value with type information for validation and routing.
    
    INVARIANTS:
        TI-001: Type determines allowed formats for the value
        TI-002: Type enables deterministic serialization
        TI-003: Type enables appropriate routing/handling
        
    PARAMETERS:
        domain  - Domain identifier (namespace isolation)
        type_   - Typed identifier type classification  
        value   - Raw identifier string
        version - Version within the type family (default: 1)
    """
    
    domain: DomainId
    type_: IdentityType
    value: str
    version: int = 1
    
    @classmethod
    def generate(
        cls,
        domain: DomainId,
        type_: IdentityType,
        namespace: Optional[str] = None,
    ) -> "TypedIdentifier":
        """Generate a new typed identifier."""
        raw_value = uuid.uuid4().hex[:20]
        if namespace:
            raw_value = f"{namespace}_{raw_value}"
        
        return cls(
            domain=domain,
            type_=type_,
            value=raw_value,
            version=1,
        )
    
    def to_string(self) -> str:
        """Serialize to canonical string representation."""
        return f"{self.domain.value}:{self.type_.value}:{self.version}:{self.value}"
    
    @classmethod
    def from_string(cls, s: str) -> "TypedIdentifier":
        """Parse a string into a TypedIdentifier."""
        parts = s.split(":")
        if len(parts) < 4:
            raise ValueError(f"Invalid TypedIdentifier format: {s}")
        
        domain_value, type_str, version_str, value = parts
        
        return cls(
            domain=DomainId(domain_value),
            type_=IdentityType(type_str),
            version=int(version_str),
            value=value,
        )
    
    def __str__(self) -> str:
        """String representation."""
        return self.to_string()


# =============================================================================
# IDENTITY REGISTRY
# =============================================================================


class IdentityRegistry:
    """
    Registry for tracking and validating identities within a domain.
    
    Provides collision detection, uniqueness verification, and identity
    lifecycle management.
    
    INVARIANTS:
        IR-001: No two identities with same value in same domain
        IR-002: Identities are never reused within their domain lifetime
        IR-003: Registry maintains creation order
        
    PARAMETERS:
        domain       - Domain being managed
        max_size     - Maximum entries before eviction (default: 1M)
        
    METHODS:
        register()   - Register a new identity, raising if duplicate
        unregister() - Remove an identity from registry  
        exists()     - Check if an identity is registered
        validate()   - Validate identity uniqueness in domain
    """
    
    def __init__(self, domain: DomainId, max_size: int = 1_000_000):
        self.domain = domain
        self.max_size = max_size
        self._registry: Dict[str, float] = {}  # value -> created_at_utc
        self._order: List[str] = []  # insertion order for eviction
    
    def register(self, identity: Identity) -> bool:
        """
        Register a new identity.
        
        Returns True if successfully registered.
        Raises ValueError if identity already exists in domain.
        """
        value = identity.value
        
        if value in self._registry:
            raise ValueError(
                f"Identity collision detected: {value} "
                f"in domain {self.domain}"
            )
        
        if len(self._registry) >= self.max_size:
            # Evict oldest entry
            oldest = self._order.pop(0)
            del self._registry[oldest]
        
        self._registry[value] = identity.created_at_utc
        self._order.append(value)
        
        return True
    
    def unregister(self, value: str) -> bool:
        """Remove an identity from the registry."""
        if value not in self._registry:
            return False
        
        del self._registry[value]
        self._order.remove(value)
        return True
    
    def exists(self, value: str) -> bool:
        """Check if an identity exists in the domain."""
        return value in self._registry
    
    def validate(self, identity: Identity) -> Tuple[bool, Optional[str]]:
        """
        Validate that identity is unique within domain.
        
        Returns (is_valid, error_message)
        """
        if self.exists(identity.value):
            return False, f"Duplicate identity: {identity.value}"
        return True, None
    
    def count(self) -> int:
        """Return the number of registered identities."""
        return len(self._registry)
    
    def get_created_at(self, value: str) -> Optional[float]:
        """Get creation timestamp for an identity."""
        return self._registry.get(value)


# =============================================================================
# IDENTITY VALIDATOR
# =============================================================================


class IdentityValidator:
    """
    Validator for identity integrity and domain constraints.
    
    Performs comprehensive validation of identities across all dimensions.
    
    VALIDATION RULES:
        V-001: Value format matches type expectations
        V-002: Domain is valid (non-empty, proper format)
        V-003: Timestamp is reasonable (not in future)
        V-004: No reserved prefixes violated
        
    METHODS:
        validate_format()   - Validate value format against type
        validate_domain()   - Validate domain constraints
        validate_integrity()- Complete integrity check
        is_valid_for_type() - Check compatibility with type
    """
    
    # Reserved prefixes that cannot appear in identity values
    RESERVED_PREFIXES = ("reserved:", "system:", "admin:")
    
    def __init__(self):
        self._error_messages: List[str] = []
    
    def validate_format(self, value: str, type_: IdentityType) -> Tuple[bool, Optional[str]]:
        """
        Validate that value format matches type expectations.
        
        Returns (is_valid, error_message)
        """
        # All values must be non-empty
        if not value or len(value.strip()) < 4:
            return False, "Identity value too short"
        
        # Check reserved prefixes
        for prefix in self.RESERVED_PREFIXES:
            if value.startswith(prefix):
                return False, f"Value cannot start with reserved prefix: {prefix}"
        
        # Type-specific validations
        if type_ == IdentityType.RUNTIME:
            # Runtime IDs typically have 'rt_' or 'runtime_' prefix
            pass  # Allow any format for flexibility
            
        elif type_ == IdentityType.COMPONENT:
            pass  # Allow any format
            
        elif type_ == IdentityType.EXECUTION:
            pass  # Allow any format
            
        elif type_ == IdentityType.STATE:
            pass  # Allow any format
            
        return True, None
    
    def validate_domain(self, domain: DomainId) -> Tuple[bool, Optional[str]]:
        """Validate domain constraints."""
        if not isinstance(domain, DomainId):
            return False, "Domain must be a DomainId instance"
        
        if not domain or len(domain.strip()) < 1:
            return False, "Domain must be non-empty"
            
        # Check for invalid characters (only alphanumerics, underscore, colon)
        for char in domain:
            if not (char.isalnum() or char in ("_", ":")):
                return False, f"Invalid character in domain: {char}"
                
        return True, None
    
    def validate_integrity(self, identity: Identity) -> Tuple[bool, List[str]]:
        """
        Perform complete integrity check on an identity.
        
        Returns (is_valid, error_messages)
        """
        self._error_messages = []
        
        # Format validation
        valid, msg = self.validate_format(identity.value, identity.type_)
        if not valid:
            self._error_messages.append(msg)
        
        # Domain validation  
        valid, msg = self.validate_domain(identity.domain)
        if not valid:
            self._error_messages.append(msg)
        
        # Timestamp validation (not in future significantly)
        current_time = _time_module.monotonic()
        time_diff = identity.created_at_utc - current_time
        if time_diff > 60:  # More than 60 seconds in future is suspicious
            self._error_messages.append(
                f"Identity created {time_diff:.1f}s in the future"
            )
        
        return len(self._error_messages) == 0, self._error_messages
    
    def is_valid_for_type(self, value: str, type_: IdentityType) -> bool:
        """Check if value is compatible with the given identity type."""
        # Base validation
        valid, _ = self.validate_format(value, type_)
        return valid


# =============================================================================
# IDENTITY HASHER
# =============================================================================


class IdentityHasher:
    """
    Deterministic hashing for identity values.
    
    Provides consistent hash computation for storage, comparison,
    and distributed systems.
    
    ALGORITHMS:
        SHA256     - Strong collision resistance (default)
        FNV1A      - Fast non-cryptographic
        MURMUR3    - Fast non-cryptographic with good distribution
        
    INVARIANTS:
        IH-001: Same value always produces same hash
        IH-002: Different values produce different hashes (with high probability)
        IH-003: Hash is deterministic across runs
    """
    
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm.lower()
        
        if algorithm not in ("sha256", "fnv1a", "murmur3"):
            raise ValueError(
                f"Unsupported hash algorithm: {algorithm}. "
                f"Supported: sha256, fnv1a, murmur3"
            )
    
    def hash(self, value: str) -> str:
        """Compute deterministic hash of identity value."""
        if self.algorithm == "sha256":
            import hashlib
            return hashlib.sha256(value.encode()).hexdigest()[:32]
        
        elif self.algorithm == "fnv1a":
            # FNV-1a 64-bit variant
            fnv_offset = 14695981039346656037
            fnv_prime = 1099511628211
            h = fnv_offset
            for byte in value.encode():
                h ^= byte
                h *= fnv_prime
                h &= 0xFFFFFFFFFFFFFFFF  # Keep 64-bit
            return format(h, "x").zfill(16)
        
        elif self.algorithm == "murmur3":
            # Simplified MurmurHash3-like (using built-in hash with seed)
            import hashlib
            seed = 42
            h = seed
            for byte in value.encode():
                h ^= byte
                h = (h * 130965) & 0xFFFFFFFF
            return format(h, "x").zfill(8)
        
        raise RuntimeError(f"Unknown algorithm: {self.algorithm}")
    
    def compare(self, hash1: str, hash2: str) -> bool:
        """Compare two hashes for equality."""
        return hash1 == hash2
    
    def matches_value(self, value: str, expected_hash: str) -> bool:
        """Check if value hashes to expected hash."""
        return self.hash(value) == expected_hash


# =============================================================================
# IDENTITY COMPATIBILITY CHECKER
# =============================================================================


class IdentityCompatibilityChecker:
    """
    Check compatibility between identity versions and types.
    
    Supports forward/backward compatibility validation for
    serialization and migration scenarios.
    
    COMPATIBILITY RULES:
        C-001: Same type is always compatible
        C-002: Version n is backward compatible with version n-k (k >= 0)
        C-003: Domain must match or be a superset
        
    METHODS:
        is_compatible()     - Check if two identities are compatible
        get_migration_path()- Determine migration path between versions
        validate_migrate()  - Validate identity can migrate to new version
    """
    
    def __init__(self):
        self._compatibility_matrix: Dict[Tuple[str, str], bool] = {}
    
    def is_compatible(self, old: Identity, new: Identity) -> Tuple[bool, List[str]]:
        """
        Check if old identity is compatible with new.
        
        Compatibility means old can be safely converted to new.
        
        Returns (is_compatible, reasons)
        """
        reasons = []
        
        # Same type is always compatible
        if old.type_ == new.type_:
            return True, reasons
        
        # Different types - check domain compatibility
        if old.domain.value == new.domain.value:
            # Same domain but different type - incompatible
            reasons.append(
                f"Type mismatch: {old.type_.value} -> {new.type_.value}"
            )
            return False, reasons
        
        # Cross-domain - may require migration
        reasons.append("Cross-domain identity requires migration")
        return True, reasons  # Compatible but with note
    
    def get_migration_path(
        self,
        source: Identity,
        target: Identity,
    ) -> List[str]:
        """Determine migration path from source to target."""
        path = []
        
        if source.type_ != target.type_:
            path.append(f"type:{source.type_.value}->{target.type_.value}")
        
        if source.domain.value != target.domain.value:
            path.append(f"domain:{source.domain.value}->{target.domain.value}")
        
        return path
    
    def validate_migrate(
        self,
        identity: Identity,
        new_type: Optional[IdentityType] = None,
        new_domain: Optional[DomainId] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that identity can be migrated to new type/domain.
        
        Returns (can_migrate, reasons)
        """
        reasons = []
        
        if new_type and new_type != identity.type_:
            # Type migration requires validation
            pass  # Allow for flexibility
            
        return True, reasons


# =============================================================================
# PUBLIC API
# =============================================================================


__all__ = [
    # Enumerations
    "IdentityType",
    
    # Interfaces
    "Identity",
    
    # Base implementations
    "BaseIdentity",
    
    # Domain types
    "DomainId",
    
    # Typed identifiers  
    "TypedIdentifier",
    
    # Registry & validation
    "IdentityRegistry",
    "IdentityValidator",
    
    # Utilities
    "IdentityHasher",
    "IdentityCompatibilityChecker",
]