# Gordon Cognitive Architecture - Phase 4.5.2
# ===========================================
"""
Action Identity Model - Canonical Architecture

This module implements the complete canonical identity system for Action artifacts
in the Gordon autonomous cognitive agent.

CANONICAL DEFINITION
====================

ActionIdentity is the immutable conceptual identity of one semantic Action.

It identifies the operation itself, not:
    - One execution
    - One attempt
    - One Effect
    - One Outcome
    - One runtime object
    - One coroutine
    - One thread
    - One process
    - One tool invocation

ACTION-ID-LAW-001: Every Action owns exactly one ActionIdentity.
ACTION-ID-LAW-002: ActionIdentity survives semantic revisions.
ACTION-ID-LAW-003: Revisions never overwrite history.
ACTION-ID-LAW-004: ExecutionAttempt never becomes ActionIdentity.
ACTION-ID-LAW-005: Identity continuity is explicit.
ACTION-ID-LAW-006: Identity relationships are immutable.
ACTION-ID-LAW-007: Replay never creates new identities.
ACTION-ID-LAW-008: Migration never changes conceptual identity.
ACTION-ID-LAW-009: Replacement never mutates previous identity.
ACTION-ID-LAW-010: History is append-only.

ARCHITECTURE
============

ActionIdentity (canonical semantic identity)
    ↓
ActionReference (reference to an Action or revision)
    ├── CanonicalActionReference (direct reference to canonical version)
    ├── ExternalActionReference (reference from external system)
    └── WeakActionReference (non-owning reference for caching)
    
    ↓
ActionRevision (semantic update record)
    ├── ActionRevisionReference (lightweight reference)
    └── ActionRevisionMetadata (administrative data)
    
    ↓
ActionLineage (immutable history graph)
    ├── ActionHistory (append-only log)
    ├── ActionDelta (change record)
    ├── ActionTransition (state transition)
    ├── ActionContinuation (continues identity)
    ├── ActionReplacement (replaces previous revision)
    └── ActionSupersession (supersedes with new identity)
    
    ↓
ActionVersion (versioning model)
    ├── IdentityVersion (identity's version number)
    ├── SemanticRevision (semantic change level)
    ├── SchemaVersion (representation format)
    ├── SerializationVersion (serialization format)
    ├── MigrationVersion (migration compatibility)
    └── CompatibilityVersion (compatibility window)

IDENTITY CONTINUITY RULES
=========================

Same Action (continues identity):
    - Same core operation concept
    - Same primary target type
    - Same intended effect category
    - Scope bounded changes only
    
Different Action (new identity):
    - Different primary operation concept
    - Material change to principal target
    - Fundamentally different intended effect
    - Different authority class
    - Different risk class
    - Conceptual continuity lost

IDENTITY TRANSITION TYPES
=========================

Continuation:  Same identity, valid revision
Replacement:   New identity replaces old (with traceability)
Supersession:  New identity supersedes old (stronger relationship)

ARCHITECTURAL INVARIANTS
========================

ACTION-ID-INV-001: Exactly one ActionIdentity per Action artifact.
ACTION-ID-INV-002: ActionIdentity is immutable and never regenerated.
ACTION-ID-INV-003: Revision history is acyclic and append-only.
ACTION-ID-INV-004: References never embed runtime handles or objects.
ACTION-ID-INV-005: Deterministic reconstruction from serialized form.
ACTION-ID-INV-006: Replay produces identical identity set.
ACTION-ID-INV-007: Migration preserves conceptual identity.
ACTION-ID-INV-008: Equivalence is context-dependent and explicit.
ACTION-ID-INV-009: Alias never equals canonical identity.
ACTION-ID-INV-010: All relationships are immutable.

IMPORT SAFETY
=============
This package performs no runtime initialization during import.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto
import hashlib


# =============================================================================
# IDENTITY KINDS - Semantic categories of identity types
# =============================================================================

class IdentityKind(Enum):
    """
    Categories of Action Identity kinds.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    PRIMITIVE = "primitive"
    """Basic semantic operation identity."""
    
    DERIVED = "derived"
    """Derived from another action via revision or transformation."""
    
    COMPOSITE = "composite"
    """Composite of multiple actions."""
    
    ABSTRACT = "abstract"
    """Abstract or template identity for parameterized actions."""
    
    SPECIALIZED = "specialized"
    """Specialization of a more general identity."""
    
    DEPRECATED = "deprecated"
    """Deprecated but preserved for historical continuity."""
    
    REPLACED = "replaced"
    """Replaced by another action (retained for traceability)."""
    
    SUPERSEDED = "superseded"
    """Superseded by another action with stronger relationship."""
    
    UNKNOWN = "unknown"


# =============================================================================
# IDENTITY VERSION - Versioning dimensions
# =============================================================================

@dataclass(frozen=True)
class IdentityVersion:
    """
    Complete version information for an ActionIdentity.
    
    This separates different versioning concerns that are often conflated:
    
    - IdentityVersion: The semantic version of the identity itself
    - SemanticRevision: Level of semantic change (major/minor/patch)
    - SchemaVersion: Representation format version
    - SerializationVersion: Wire format version
    - MigrationVersion: Compatibility with migration system
    - CompatibilityVersion: Window for compatibility guarantees
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Semantic version (changes when semantic continuity is maintained)
    identity_version: int = field(default=1)
    """Incremented on valid revisions that preserve identity."""
    
    # Semantic revision level (semver-like)
    major: int = field(default=0)
    """Major semantic changes that may break compatibility."""
    
    minor: int = field(default=1)
    """Backward-compatible new features or refinements."""
    
    patch: int = field(default=0)
    """Backward-compatible bug fixes."""
    
    # Schema version (representation format)
    schema_version: int = field(default=1)
    """Version of the data schema/structure."""
    
    # Serialization version (wire format)
    serialization_version: int = field(default=1)
    """Version of the serialization format."""
    
    # Migration compatibility
    migration_version: int = field(default=1)
    """Version for migration compatibility tracking."""
    
    # Compatibility window
    compatibility_window: int = field(default=3)
    """Number of versions to maintain backward compatibility."""
    
    @property
    def semantic_string(self) -> str:
        """Return semantic version as string (e.g., '0.1.0')."""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @property
    def full_version_string(self) -> str:
        """Return complete version string."""
        return (
            f"v{self.identity_version} "
            f"(schema:v{self.schema_version}, "
            f"serialize:v{self.serialization_version})"
        )
    
    def is_compatible_with(self, other: "IdentityVersion") -> bool:
        """
        Check if this version is compatible with another.
        
        Compatibility requires:
            - Same schema_version
            - Migration versions within compatibility window
        
        Args:
            other: Version to compare against
            
        Returns:
            True if compatible
        """
        if self.schema_version != other.schema_version:
            return False
        return abs(self.migration_version - other.migration_version) <= self.compatibility_window
    
    def next_identity_version(self) -> "IdentityVersion":
        """Return new version with incremented identity_version."""
        return IdentityVersion(
            identity_version=self.identity_version + 1,
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            schema_version=self.schema_version,
            serialization_version=self.serialization_version,
            migration_version=self.migration_version,
            compatibility_window=self.compatibility_window,
        )
    
    def next_minor(self) -> "IdentityVersion":
        """Return new version with incremented minor (backward compatible)."""
        return IdentityVersion(
            identity_version=self.identity_version + 1,
            major=self.major,
            minor=self.minor + 1,
            patch=0,
            schema_version=self.schema_version,
            serialization_version=self.serialization_version,
            migration_version=self.migration_version,
            compatibility_window=self.compatibility_window,
        )
    
    def next_major(self) -> "IdentityVersion":
        """Return new version with incremented major (may break compatibility)."""
        return IdentityVersion(
            identity_version=self.identity_version + 1,
            major=self.major + 1,
            minor=0,
            patch=0,
            schema_version=self.schema_version,
            serialization_version=self.serialization_version,
            migration_version=self.migration_version,
            compatibility_window=self.compatibility_window,
        )


# =============================================================================
# ACTION IDENTITY - Canonical semantic identity
# =============================================================================

@dataclass(frozen=True)
class ActionIdentity:
    """
    Immutable semantic identity of an Action.
    
    The Action Identity represents the conceptual continuity of one possible
    operation across its revision history. It does NOT track runtime execution
    attempts or tool-call invocations.
    
    Example:
        An Action to "read file X" has one identity that persists through
        revisions like:
            v1: read the complete file
            v2: read lines 100-300 for boundedness
    
    Invariants:
        ACTION-ID-LAW-001: Every Action has exactly one ActionIdentity.
        ACTION-ID-LAW-002: ActionIdentity survives semantic revisions.
        ACTION-ID-LAW-003: Revisions never overwrite history.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # The canonical identity string (must be unique within namespace)
    value: str = field(default="")
    """The unique identifier for this action concept."""
    
    # Namespace for collision avoidance across subsystems
    namespace: str = field(default="default")
    """Namespace to prevent identity collisions."""
    
    # Identity kind
    kind: IdentityKind = field(default=IdentityKind.PRIMITIVE)
    """Category of this identity."""
    
    # Parent identity (for derived actions)
    parent_identity_id: Optional[str] = None
    """Parent ActionIdentity id if derived."""
    
    # Version information
    version: IdentityVersion = field(default_factory=IdentityVersion)
    """Complete version information for this identity."""
    
    @property
    def canonical_id(self) -> str:
        """
        Return the fully qualified canonical identity string.
        
        Format: {namespace}:{value}:v{identity_version}
        This ensures global uniqueness across namespaces and versions.
        """
        return f"{self.namespace}:{self.value}:v{self.version.identity_version}"
    
    @property
    def base_id(self) -> str:
        """Return the base identity without version (for lineage tracking)."""
        return f"{self.namespace}:{self.value}"
    
    @classmethod
    def primitive(
        cls,
        value: str,
        namespace: str = "default",
    ) -> "ActionIdentity":
        """
        Create a primitive ActionIdentity.
        
        Args:
            value: The unique identifier string
            namespace: Namespace for collision avoidance
            
        Returns:
            New primitive ActionIdentity instance
        """
        return cls(
            value=value,
            namespace=namespace,
            kind=IdentityKind.PRIMITIVE,
            version=IdentityVersion(identity_version=1, major=0, minor=1, patch=0),
        )
    
    @classmethod
    def derived_from(
        cls,
        parent: "ActionIdentity",
        value: Optional[str] = None,
    ) -> "ActionIdentity":
        """
        Create a derived ActionIdentity from a parent.
        
        Use this when creating revisions that preserve semantic continuity.
        
        Args:
            parent: Parent ActionIdentity
            value: New identifier if different, or same as parent
            
        Returns:
            New derived ActionIdentity instance
        """
        return cls(
            value=value or parent.value,
            namespace=parent.namespace,
            kind=IdentityKind.DERIVED,
            parent_identity_id=parent.canonical_id,
            version=parent.version.next_identity_version(),
        )
    
    @classmethod
    def from_string(cls, identity_str: str) -> "ActionIdentity":
        """
        Parse an identity string into an ActionIdentity.
        
        Expected format: {namespace}:{value} or {namespace}:{value}:v{version}
        
        Args:
            identity_str: The serialized identity string
            
        Returns:
            Parsed ActionIdentity instance
        """
        parts = identity_str.split(":")
        
        if len(parts) >= 3 and parts[-1].startswith("v"):
            # Has version: namespace:value:vN
            value = ":".join(parts[1:-1])  # Handle values with colons
            version_num = int(parts[-1][1:])  # Remove 'v' prefix
            return cls(
                value=value,
                namespace=parts[0],
                version=IdentityVersion(identity_version=version_num),
            )
        else:
            # No version: namespace:value
            value = ":".join(parts[1:]) if len(parts) > 1 else parts[0]
            return cls(
                value=value,
                namespace=parts[0] if len(parts) > 1 else "default",
                version=IdentityVersion(identity_version=1),
            )
    
    @classmethod
    def from_hash(cls, data: str, namespace: str = "default") -> "ActionIdentity":
        """
        Create an identity deterministically from hash of semantic data.
        
        This ensures equivalent semantic inputs produce identical identities.
        
        Args:
            data: Semantic data to hash
            namespace: Namespace for the identity
            
        Returns:
            Deterministic ActionIdentity based on hash
        """
        # Use SHA-256 to ensure deterministic, unique id
        hash_value = hashlib.sha256(data.encode("utf-8")).hexdigest()[:32]
        return cls(
            value=hash_value,
            namespace=namespace,
            kind=IdentityKind.PRIMITIVE,
            version=IdentityVersion(identity_version=1),
        )
    
    def __str__(self) -> str:
        """Return the fully qualified canonical identity string."""
        return self.canonical_id
    
    def __repr__(self) -> str:
        return f"ActionIdentity(id='{self.canonical_id}', kind='{self.kind.value}')"
    
    @property
    def is_derived(self) -> bool:
        """Check if this identity was derived from another."""
        return self.parent_identity_id is not None
    
    def equals_ignoring_version(self, other: "ActionIdentity") -> bool:
        """
        Check equality ignoring version differences.
        
        Used to determine if two references point to the same semantic concept
        regardless of revision level.
        
        Args:
            other: Another ActionIdentity to compare
            
        Returns:
            True if base identity matches
        """
        return self.base_id == other.base_id
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "value": self.value,
            "namespace": self.namespace,
            "kind": self.kind.value,
            "parent_identity_id": self.parent_identity_id,
            "version": {
                "identity_version": self.version.identity_version,
                "major": self.version.major,
                "minor": self.version.minor,
                "patch": self.version.patch,
                "schema_version": self.version.schema_version,
                "serialization_version": self.version.serialization_version,
                "migration_version": self.version.migration_version,
                "compatibility_window": self.version.compatibility_window,
            },
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionIdentity":
        """Deserialize from dictionary."""
        version_data = data.get("version", {})
        return cls(
            value=data.get("value", ""),
            namespace=data.get("namespace", "default"),
            kind=IdentityKind(data.get("kind", IdentityKind.PRIMITIVE.value)),
            parent_identity_id=data.get("parent_identity_id"),
            version=IdentityVersion(
                identity_version=version_data.get("identity_version", 1),
                major=version_data.get("major", 0),
                minor=version_data.get("minor", 1),
                patch=version_data.get("patch", 0),
                schema_version=version_data.get("schema_version", 1),
                serialization_version=version_data.get("serialization_version", 1),
                migration_version=version_data.get("migration_version", 1),
                compatibility_window=version_data.get("compatibility_window", 3),
            ),
        )


# =============================================================================
# ACTION REFERENCE - Reference to an Action or revision
# =============================================================================

@dataclass(frozen=True)
class ActionReference:
    """
    Base class for references to Actions.
    
    References preserve identity, revision, schema version, namespace, owner,
    and provenance without embedding runtime objects.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Target identity
    target_identity_id: str = field(default="")
    """The ActionIdentity being referenced."""
    
    # Optional revision reference
    revision_reference: Optional[str] = None
    """Specific revision if not canonical version."""
    
    # Schema and version info
    schema_version: int = field(default=1)
    """Schema version of the target."""
    
    serialization_version: int = field(default=1)
    """Serialization format version."""
    
    @property
    def id(self) -> str:
        """Return fully qualified reference identifier."""
        if self.revision_reference:
            return f"{self.target_identity_id}:{self.revision_reference}"
        return self.target_identity_id
    
    def __str__(self) -> str:
        return self.id
    
    def __repr__(self) -> str:
        return f"ActionReference(id='{self.id}')"
    
    @property
    def is_canonical(self) -> bool:
        """Check if this references the canonical version."""
        return self.revision_reference is None


@dataclass(frozen=True)
class CanonicalActionReference(ActionReference):
    """
    Reference to the canonical (most recent valid) revision of an Action.
    
    This is used when you want the current, authoritative version without
    needing to track specific revision history.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    def __init__(self, target_identity_id: str = ""):
        super().__init__(
            target_identity_id=target_identity_id,
            schema_version=1,
            serialization_version=1,
        )
    
    @property
    def id(self) -> str:
        """Return canonical reference identifier."""
        return self.target_identity_id
    
    @classmethod
    def from_identity(cls, identity: ActionIdentity) -> "CanonicalActionReference":
        """Create a canonical reference from an ActionIdentity."""
        return cls(target_identity_id=identity.canonical_id)


@dataclass(frozen=True)
class ExternalActionReference(ActionReference):
    """
    Reference to an Action from an external system.
    
    Used when importing or referencing actions defined in other systems.
    Preserves provenance information about the external source.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # External system identification
    source_system: str = field(default="")
    """External system that defines this action."""
    
    source_identity_id: str = field(default="")
    """Original identity in the source system."""
    
    @property
    def id(self) -> str:
        return f"external:{self.source_system}:{self.target_identity_id}"
    
    @classmethod
    def from_external(
        cls,
        source_system: str,
        external_id: str,
        target_identity_id: str = "",
    ) -> "ExternalActionReference":
        """Create an external reference."""
        return cls(
            target_identity_id=target_identity_id,
            source_system=source_system,
            source_identity_id=external_id,
        )


@dataclass(frozen=True)
class WeakActionReference(ActionReference):
    """
    Non-owning, weak reference to an Action for caching or lookup.
    
    Does not participate in identity ownership or lifecycle management.
    Used for performance optimization where strong references are unnecessary.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Weak reference metadata
    cache_hint: bool = field(default=True)
    """Hint that this reference may be cached."""
    
    @property
    def id(self) -> str:
        return f"weak:{self.target_identity_id}"
    
    @classmethod
    def weak_from(cls, identity: ActionIdentity) -> "WeakActionReference":
        """Create a weak reference from an ActionIdentity."""
        return cls(
            target_identity_id=identity.canonical_id,
            cache_hint=True,
        )


# =============================================================================
# ACTION REVISION REFERENCE - Reference to a specific revision
# =============================================================================

@dataclass(frozen=True)
class ActionRevisionReference:
    """
    Reference to a specific revision of an Action.
    
    This is a lightweight reference used when you need to point to a revision
    without embedding the full revision data.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # The action identity being referenced
    identity_id: str = field(default="")
    """The ActionIdentity that this revision belongs to."""
    
    # Revision number (1 for initial, increments for subsequent)
    revision_number: int = 1
    """Sequential revision number within the identity's history."""
    
    @property
    def id(self) -> str:
        """Return fully qualified revision identifier."""
        return f"{self.identity_id}:v{self.revision_number}"
    
    def __str__(self) -> str:
        return self.id
    
    def __repr__(self) -> str:
        return f"ActionRevisionReference(id='{self.id}')"
    
    @classmethod
    def from_identity_and_revision(
        cls,
        identity: ActionIdentity,
        revision_number: int = 1,
    ) -> "ActionRevisionReference":
        """Create a revision reference from an identity and revision number."""
        return cls(
            identity_id=identity.canonical_id,
            revision_number=revision_number,
        )


# =============================================================================
# ACTION REVISION METADATA - Administrative revision information
# =============================================================================

@dataclass(frozen=True)
class ActionRevisionMetadata:
    """
    Metadata about an Action Revision.
    
    This contains administrative information about the revision, such as
    who proposed it, when, and why. It does NOT contain semantic content.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Revision identification
    identity_id: str = field(default="")
    """ActionIdentity this revision belongs to."""
    
    revision_number: int = 1
    """Sequential number within the identity's history."""
    
    parent_revision_id: Optional[str] = None
    """Parent revision if this is not the initial revision."""
    
    # Revision tracking
    created_at_semantic_time: float = field(default=0.0)
    """Semantic time when revision was created (externally supplied)."""
    
    revision_kind: str = field(default="standard")
    """Kind of revision (standard, correction, refinement, etc.)."""
    
    # Provenance
    proposed_by: Optional[str] = None
    """Entity or process that proposed this revision."""
    
    validated_by: Optional[str] = None
    """Entity that validated the revision."""
    
    @property
    def revision_id(self) -> str:
        """Return the unique revision identifier."""
        return f"{self.identity_id}:v{self.revision_number}"
    
    def is_initial_revision(self) -> bool:
        """Check if this is the first revision of an action."""
        return self.parent_revision_id is None
    
    def has_parent(self, other_revision: "ActionRevisionMetadata") -> bool:
        """
        Check if this revision follows another in history.
        
        Args:
            other_revision: The potential parent revision
            
        Returns:
            True if this revision's parent matches the other revision
        """
        return self.parent_revision_id == other_revision.revision_id
    
    def to_reference(self) -> ActionRevisionReference:
        """Convert to a lightweight revision reference."""
        return ActionRevisionReference(
            identity_id=self.identity_id,
            revision_number=self.revision_number,
        )


__all__ = [
    # Identity kinds
    "IdentityKind",
    
    # Versioning
    "IdentityVersion",
    
    # Core identity
    "ActionIdentity",
    
    # References
    "ActionReference",
    "CanonicalActionReference",
    "ExternalActionReference",
    "WeakActionReference",
    
    # Revision references
    "ActionRevisionReference",
    "ActionRevisionMetadata",
]