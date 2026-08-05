# Configuration Type Definitions
# =============================
"""
Core type definitions for Phase 3.8.4: Configuration & Dependency Management.

This module contains the fundamental type definitions that are shared across
configuration modules, avoiding circular import issues.
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
)
from enum import Enum
import time


# =============================================================================
# Core IDs
# =============================================================================

@dataclass(frozen=True)
class RuntimeId:
    """Unique identifier for a runtime instance."""
    value: str
    
    @classmethod
    def generate(cls) -> "RuntimeId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "RuntimeId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConfigurationId:
    """Unique identifier for a configuration instance."""
    value: str
    
    @classmethod
    def generate(cls) -> "ConfigurationId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "ConfigurationId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConfigurationVersion:
    """Version of a configuration artifact."""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    def next_major(self) -> "ConfigurationVersion":
        return ConfigurationVersion(major=self.major + 1, minor=0, patch=0)
    
    def next_minor(self) -> "ConfigurationVersion":
        return ConfigurationVersion(major=self.major, minor=self.minor + 1, patch=0)
    
    def next_patch(self) -> "ConfigurationVersion":
        return ConfigurationVersion(major=self.major, minor=self.minor, patch=self.patch + 1)


@dataclass(frozen=True)
class ConfigurationSourceId:
    """Unique identifier for a configuration source."""
    value: str
    
    @classmethod
    def generate(cls) -> "ConfigurationSourceId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "ConfigurationSourceId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConfigurationSnapshotId:
    """Unique identifier for a configuration snapshot."""
    value: str
    
    @classmethod
    def generate(cls) -> "ConfigurationSnapshotId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "ConfigurationSnapshotId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConfigurationSchemaId:
    """Unique identifier for a configuration schema."""
    value: str
    
    @classmethod
    def generate(cls) -> "ConfigurationSchemaId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "ConfigurationSchemaId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConfigurationDomainId:
    """Unique identifier for a configuration domain."""
    value: str
    
    @classmethod
    def from_string(cls, s: str) -> "ConfigurationDomainId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConfigurationChangeId:
    """Unique identifier for a configuration change."""
    value: str
    
    @classmethod
    def generate(cls) -> "ConfigurationChangeId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "ConfigurationChangeId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Precedence Model
# =============================================================================

class PrecedenceLevel(Enum):
    """Precedence levels for configuration sources."""
    BUILTIN_DEFAULTS = 0
    PROFILE_DEFAULTS = 10
    CONFIG_FILES = 20
    ENVIRONMENT_VARS = 30
    COMMAND_LINE_ARGS = 40
    RUNTIME_OVERRIDES = 50
    EMERGENCY_OVERRIDES = 100


@dataclass(frozen=True)
class PrecedenceRule:
    """A precedence rule defining source ordering."""
    source_type: str
    level: int
    order_in_level: int = 0
    
    def __lt__(self, other: "PrecedenceRule") -> bool:
        if self.level != other.level:
            return self.level < other.level
        return self.order_in_level < other.order_in_level


@dataclass(frozen=True)
class PrecedenceModel:
    """Deterministic precedence model for configuration sources."""
    rules: Tuple[PrecedenceRule, ...]
    
    def get_precedence(self, source_type: str) -> int:
        """Get precedence value for a source type (lower = higher priority)."""
        for rule in self.rules:
            if rule.source_type == source_type:
                return rule.level
        return 1000  # Default low precedence


# =============================================================================
# Source Types and Descriptors
# =============================================================================

class SourceType(Enum):
    """Types of configuration sources."""
    BUILTIN_DEFAULTS = "builtin_defaults"
    PROFILE_DEFAULTS = "profile_defaults"
    CONFIG_FILE = "config_file"
    ENVIRONMENT_VAR = "environment_var"
    COMMAND_LINE_ARG = "command_line_arg"
    RUNTIME_OVERRIDE = "runtime_override"
    REMOTE_CONFIG = "remote_config"


@dataclass(frozen=True)
class ConfigurationSourceDescriptor:
    """Descriptor for a configuration source."""
    id: ConfigurationSourceId
    name: str
    source_type: SourceType
    precedence_level: int
    is_readonly: bool = False
    optional: bool = True


@dataclass(frozen=True)
class ConfigurationSourceResult:
    """Result of loading a configuration source."""
    id: ConfigurationSourceId
    data: Dict[str, Any]
    parsed_at: float = field(default_factory=time.monotonic)
    errors: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SourceLoadingError:
    """An error that occurred while loading a source."""
    source_id: ConfigurationSourceId
    message: str
    timestamp: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class SourceParsingError:
    """An error that occurred while parsing a source."""
    source_id: ConfigurationSourceId
    path: Optional[str]
    message: str
    raw_value: Any
    timestamp: float = field(default_factory=time.monotonic)


# =============================================================================
# Schema Field Definition
# =============================================================================

class FieldType(Enum):
    """Types of schema fields."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    ENUM = "enum"


@dataclass(frozen=True)
class SchemaField:
    """A field definition in a configuration schema."""
    name: str
    field_type: FieldType
    required: bool = False
    default: Any = None
    description: Optional[str] = None
    
    # Validation constraints
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[Tuple[str, ...]] = None
    
    # Metadata
    mutability: str = "RUNTIME_MUTABLE"
    restart_required: bool = False
    sensitive: bool = False


@dataclass(frozen=True)
class DomainSchema:
    """A schema for a single configuration domain."""
    domain_id: str
    fields: Tuple[SchemaField, ...]
    schema_version: ConfigurationVersion = field(default_factory=lambda: ConfigurationVersion(1, 0, 0))


@dataclass(frozen=True)
class SchemaConflictType(Enum):
    """Types of schema conflicts."""
    DUPLICATE_PATH = "duplicate_path"
    INCOMPATIBLE_TYPES = "incompatible_types"
    CONFLICTING_DEFAULTS = "conflicting_defaults"
    CONFLICTING_MUTABILITY = "conflicting_mutability"
    CONFLICTING_OWNERSHIP = "conflicting_ownership"
    CIRCULAR_DERIVED = "circular_derived"


@dataclass(frozen=True)
class SchemaConflict:
    """A schema conflict detected during composition."""
    conflict_type: SchemaConflictType
    path: str
    message: str
    affected_schemas: Tuple[str, ...]


@dataclass(frozen=True)
class SchemaRegistryId:
    """Unique identifier for a schema registry."""
    value: str
    
    @classmethod
    def generate(cls) -> "SchemaRegistryId":
        return cls(value=str(hash(time.monotonic())))
    
    @classmethod
    def from_string(cls, s: str) -> "SchemaRegistryId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SchemaRegistration:
    """A registered schema with metadata."""
    schema_id: ConfigurationSchemaId
    domain_schema: DomainSchema
    registered_at: float = field(default_factory=time.monotonic)
    version: ConfigurationVersion = field(default_factory=lambda: ConfigurationVersion(1, 0, 0))


@dataclass(frozen=True)
class ValidationError:
    """A validation error."""
    path: str
    message: str
    value: Any


# =============================================================================
# Configuration Domain
# =============================================================================

@dataclass(frozen=True)
class ConfigurationDomain:
    """A configuration domain with its schema and defaults."""
    domain_id: str
    owner: Optional[str] = None  # Owner team/org
    version: int = 1
    
    # Schema fields (path -> expected type)
    fields: Dict[str, type] = field(default_factory=dict)
    
    # Default values
    defaults: Dict[str, Any] = field(default_factory=dict)
    
    # Mutability class (STATIC, RUNTIME_MUTABLE, etc.)
    mutability_class: str = "RUNTIME_MUTABLE"
    
    # Restart requirement
    restart_required: bool = False


# =============================================================================
# Secret Reference
# =============================================================================

@dataclass(frozen=True)
class SecretReference:
    """
    A reference to a secret value stored externally.
    
    Configuration should store secret references, not plaintext secret values.
    Secrets are resolved at runtime when needed by consumers with appropriate
    authorization and audit logging.
    """
    provider: str  # e.g., "vault", "secrets_manager"
    path: str  # Secret path/identifier in provider
    
    @property
    def resolved(self) -> bool:
        """A secret reference is not resolved until runtime."""
        return False


# =============================================================================
# Configuration Events
# =============================================================================

@dataclass(frozen=True)
class ConfigurationEvent:
    """An event in the configuration lifecycle."""
    event_type: str  # SOURCE_LOADED, PARSED, VALIDATED, etc.
    timestamp: float = field(default_factory=time.monotonic)
    runtime_id: Optional[str] = None
    config_version: int = 1


# =============================================================================
# Merge Semantics
# =============================================================================

class MergeSemantic(Enum):
    """Merge semantics for configuration fields."""
    REPLACE = "replace"  # Replace old value with new
    DEEP_MERGE = "deep_merge"  # Recursively merge dicts
    APPEND = "append"  # Append to list
    PREPEND = "prepend"  # Prepend to list
    UNION = "union"  # Union of sets/lists
    KEYED_MERGE = "keyed_merge"  # Merge by key field
    DELETE = "delete"  # Delete the field
    UNSET = "unset"  # Unset the field (use default)
    FORBIDDEN_OVERRIDE = "forbidden_override"  # Error on override


@dataclass(frozen=True)
class MergeRule:
    """A merge rule for a specific field path."""
    path: str
    semantic: MergeSemantic


# =============================================================================
# Normalization Rules
# =============================================================================

@dataclass(frozen=True)
class NormalizationRule:
    """A normalization rule for a specific field."""
    path: str  # Field path (dot-notation)
    normalizers: Tuple[Any, ...] = field(default_factory=tuple)  # List of normalizer instances


# =============================================================================
# Configuration Diff
# =============================================================================

class ConfigDiffChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


@dataclass(frozen=True)
class ConfigDiffFinding:
    """A single change found in a configuration diff."""
    field_path: str
    change_type: str  # "added", "removed", or "modified"
    
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    source_changed: bool = False  # Did the source attribution change?
    restart_required: bool = False  # Does this require a component/runtime restart?


@dataclass(frozen=True)
class ConfigurationDiff:
    """
    Diff between two configuration snapshots.
    
    Shows what changed between versions.
    """
    
    from_snapshot_id: str
    to_snapshot_id: str
    
    changes: Tuple[ConfigDiffFinding, ...]
    
    # Summary
    added_fields: int = 0
    removed_fields: int = 0
    modified_fields: int = 0
    
    created_at: float = field(default_factory=time.monotonic)
    
    def has_changes(self) -> bool:
        """Check if there are any differences."""
        return len(self.changes) > 0


# =============================================================================
# Configuration Snapshot
# =============================================================================

@dataclass(frozen=True)
class ConfigurationSourceSnapshot:
    """
    Snapshot of a single configuration source at a point in time.
    """
    id: ConfigurationSourceId
    name: str
    data: Dict[str, Any]
    loaded_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class ConfigurationSnapshot:
    """
    Immutable snapshot of configuration at a point in time.
    
    Used for:
    - Drift detection (compare to current effective config)
    - Rollback (restore previous state)
    - Diagnostics (historical view)
    - Multi-runtime isolation
    """
    
    snapshot_id: str
    effective_config: "EffectiveConfiguration"
    applied_version: Optional[int] = None  # If different from effective
    
    # Source snapshots for provenance
    source_snapshots: Tuple[ConfigurationSourceSnapshot, ...] = field(default_factory=tuple)
    
    # Version info
    created_at: float = field(default_factory=time.monotonic)
    
    def is_current(self) -> bool:
        """Check if this snapshot represents the currently applied configuration."""
        return self.applied_version is None or self.applied_version == self.effective_config.version
    
    def has_applied_changes(self) -> bool:
        """Check if there are unapplied changes."""
        return self.applied_version is not None and self.applied_version < self.effective_config.version


# =============================================================================
# Registered Source
# =============================================================================

@dataclass(frozen=True)
class RegisteredSource:
    """A registered configuration source with its descriptor."""
    descriptor: ConfigurationSourceDescriptor
    protocol: Any  # ConfigurationSourceProtocol


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # IDs
    "RuntimeId",
    
    # Schema Conflict Types
    "SchemaConflictType",
    "SchemaConflict",
    "SchemaRegistryId",
    "SchemaRegistration",
    "ConfigurationId", 
    "ConfigurationVersion",
    "ConfigurationSourceId",
    "ConfigurationSnapshotId",
    "ConfigurationSchemaId",
    "ConfigurationDomainId",
    "ConfigurationChangeId",
    
    # Precedence
    "PrecedenceLevel",
    "PrecedenceRule",
    "PrecedenceModel",
    
    # Sources
    "SourceType",
    "ConfigurationSourceDescriptor",
    "ConfigurationSourceResult",
    "SourceLoadingError",
    "SourceParsingError",
    
    # Schema
    "FieldType",
    "SchemaField",
    "DomainSchema",
    "ValidationError",
    
    # Domains and Secrets
    "ConfigurationDomain",
    "SecretReference",
    
    # Events
    "ConfigurationEvent",
    
    # Merge Semantics
    "MergeSemantic",
    "MergeRule",
    
    # Normalization
    "NormalizationRule",
    
    # Diffing
    "ConfigDiffChangeType",
    "ConfigDiffFinding",
    "ConfigurationDiff",
    
    # Snapshots
    "ConfigurationSourceSnapshot",
    "ConfigurationSnapshot",
    
    # Provider Registry
    "RegisteredSource",
]
