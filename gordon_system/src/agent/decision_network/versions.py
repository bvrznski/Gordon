# Gordon Cognitive Architecture - Phase 4.5.2
# ===========================================
"""
Action Version Model

This module defines different versioning dimensions for Action identities,
distinguishing between identity, semantic, schema, and serialization versions.

CONCEPTUAL DISTINCT VERSION TYPES
==================================

1. Identity Version
   - Tracks the canonical semantic identity across revisions
   - Incremented on valid revisions that preserve continuity
   
2. Semantic Revision
   - Major/Minor/Patch versioning for semantic changes
   - Follows semver-like principles

3. Schema Version
   - Version of the data structure/schema
   - Changes when representation format changes

4. Serialization Version
   - Version of the wire format serialization
   - Changes when encoding format changes (JSON, protobuf, etc.)

5. Migration Version
   - Version for migration compatibility tracking
   - Determines if old representations can be migrated

6. Compatibility Window
   - How many versions back to maintain compatibility
   - Used for graceful upgrade paths

ARCHITECTURAL INVARIANTS
========================

ACTION-VERSION-INV-001: Identity version is independent of schema version.
ACTION-VERSION-INV-002: Semantic changes may not require schema changes.
ACTION-VERSION-INV-003: Serialization changes don't affect semantic meaning.
ACTION-VERSION-INV-004: Migration preserves conceptual identity.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VersionMatrix:
    """
    Complete version matrix for an Action.
    
    This encapsulates all version dimensions separately to avoid confusion
    between different kind of versioning concerns.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Identity version (canonical semantic identity)
    identity_version: int = field(default=1)
    """Version of the canonical identity across valid revisions."""
    
    # Semantic revision (major.minor.patch)
    major: int = field(default=0)
    """Major version - breaking semantic changes."""
    
    minor: int = field(default=1)
    """Minor version - backward compatible additions."""
    
    patch: int = field(default=0)
    """Patch version - bug fixes only."""
    
    # Schema version (data structure format)
    schema_version: int = field(default=1)
    """Version of the data schema/structure."""
    
    # Serialization version (wire format)
    serialization_version: int = field(default=1)
    """Version of the wire/serialization format."""
    
    # Migration compatibility
    migration_version: int = field(default=1)
    """Version for migration system compatibility."""
    
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
    
    def is_compatible_with(self, other: "VersionMatrix") -> bool:
        """
        Check if this version matrix is compatible with another.
        
        Compatibility requires:
            - Same schema_version (representation format)
            - Migration versions within compatibility window
        
        Args:
            other: Version matrix to compare against
            
        Returns:
            True if compatible
        """
        if self.schema_version != other.schema_version:
            return False
        return abs(self.migration_version - other.migration_version) <= self.compatibility_window
    
    def next_identity_version(self) -> "VersionMatrix":
        """Return new version with incremented identity_version."""
        return VersionMatrix(
            identity_version=self.identity_version + 1,
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            schema_version=self.schema_version,
            serialization_version=self.serialization_version,
            migration_version=self.migration_version,
            compatibility_window=self.compatibility_window,
        )
    
    def next_minor(self) -> "VersionMatrix":
        """Return new version with incremented minor (backward compatible)."""
        return VersionMatrix(
            identity_version=self.identity_version + 1,
            major=self.major,
            minor=self.minor + 1,
            patch=0,
            schema_version=self.schema_version,
            serialization_version=self.serialization_version,
            migration_version=self.migration_version,
            compatibility_window=self.compatibility_window,
        )
    
    def next_major(self) -> "VersionMatrix":
        """Return new version with incremented major (may break compatibility)."""
        return VersionMatrix(
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
# VERSION RELATIONSHIPS
# =============================================================================

@dataclass(frozen=True)
class VersionRelationship:
    """
    Relationship between two versions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    from_version: int = field(default=0)
    """Source version number."""
    
    to_version: int = field(default=1)
    """Target version number."""
    
    relationship_type: str = field(default="upgrade")
    """
    Type of relationship:
        - 'upgrade': Forward compatible
        - 'downgrade': Backward compatible (if supported)
        - 'migration': Requires migration process
        - 'incompatible': Not compatible
    """
    
    @property
    def is_compatible(self) -> bool:
        """Check if versions are compatible."""
        return self.relationship_type in ("upgrade", "downgrade")
    
    @property
    def is_migration_required(self) -> bool:
        """Check if migration is required."""
        return self.relationship_type == "migration"


@dataclass(frozen=True)
class VersionEquivalence:
    """
    Equivalence relationship between versions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    version_a: int = field(default=0)
    """First version."""
    
    version_b: int = field(default=0)
    """Second version."""
    
    equivalence_type: str = field(default="semantic")
    """
    Type of equivalence:
        - 'identity': Same semantic meaning
        - 'behavioral': Same behavior (with possible different representation)
        - 'structural': Same structure but different values
        - 'reference': Same reference in a particular context
    """
    
    @property
    def is_semantic_equivalence(self) -> bool:
        """Check if equivalence is semantic."""
        return self.equivalence_type == "semantic"
    
    @property
    def is_behavioral_equivalence(self) -> bool:
        """Check if equivalence is behavioral."""
        return self.equivalence_type == "behavioral"


# =============================================================================
# VERSION PROJECTION - View of version in a particular context
# =============================================================================

@dataclass(frozen=True)
class VersionProjection:
    """
    Projection of versions for a specific context.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Canonical versions
    canonical_identity_version: int = field(default=1)
    """The current canonical identity version."""
    
    canonical_schema_version: int = field(default=1)
    """The current canonical schema version."""
    
    canonical_serialization_version: int = field(default=1)
    """The current canonical serialization version."""
    
    # Supported versions (for compatibility)
    supported_identity_versions: list = field(default_factory=list)
    """List of identity versions this system supports."""
    
    supported_schema_versions: list = field(default_factory=list)
    """List of schema versions this system supports."""
    
    supported_serialization_versions: list = field(default_factory=list)
    """List of serialization versions this system supports."""
    
    @property
    def is_canonical_current(self) -> bool:
        """Check if canonical versions are the latest supported."""
        return (
            self.canonical_identity_version in self.supported_identity_versions and
            self.canonical_schema_version in self.supported_schema_versions and
            self.canonical_serialization_version in self.supported_serialization_versions
        )


__all__ = [
    "VersionMatrix",
    "VersionRelationship",
    "VersionEquivalence",
    "VersionProjection",
]