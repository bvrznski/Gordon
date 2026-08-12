# Core Configuration Infrastructure
# ================================
"""
Configuration management system for Gordon autonomous cognitive agent.

This module implements Phase 3.8.4: Configuration & Dependency Management.

The canonical configuration pipeline is:

    Configuration Sources
        ↓
    Collection
        ↓
    Parsing
        ↓
    Schema Validation
        ↓
    Normalization
        ↓
    Precedence Resolution
        ↓
    Merge Semantics
        ↓
    Policy Evaluation
        ↓
    Effective Configuration
        ↓
    Runtime Application
        ↓
    Verification
        ↓
    Commit
        ↓
    History

Configuration is executable authority. A configuration value may alter runtime assembly,
activation, model selection, resource allocation, scheduling, communication, recovery,
shutdown, security boundaries, policy enforcement, feature availability, and capability
publication.

Authorities (exactly one per responsibility):
- ConfigurationAuthority: Canonical configuration ownership and management
- SchemaRegistry: Authoritative schema definitions
- ProviderRegistry: Configuration source registry and precedence management
- ValidationEngine: Configuration validation with typed failures

Phase 3.8.4: Configuration & Dependency Management
"""

# Re-export types from the dedicated types module to avoid circular imports
from .types import (
    # IDs
    RuntimeId,
    ConfigurationId, 
    ConfigurationVersion,
    ConfigurationSourceId,
    ConfigurationSnapshotId,
    ConfigurationSchemaId,
    ConfigurationDomainId,
    ConfigurationChangeId,
    
    # Precedence
    PrecedenceLevel,
    PrecedenceRule,
    PrecedenceModel,
    
    # Sources
    SourceType,
    ConfigurationSourceDescriptor,
    ConfigurationSourceResult,
    SourceLoadingError,
    SourceParsingError,
    
    # Schema
    FieldType,
    SchemaField,
    DomainSchema,
    ValidationError,
    ConfigurationDomain,
    SecretReference,
    ConfigurationEvent,
    MergeSemantic,
    MergeRule,
    NormalizationRule,
    ConfigDiffChangeType,
    ConfigDiffFinding,
    ConfigurationDiff,
    ConfigurationSourceSnapshot,
    ConfigurationSnapshot,
    RegisteredSource,
)
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import time
import hashlib


# Import from types module
from .types import SchemaConflictType


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
class EffectiveConfiguration:
    """
    The effective configuration for a runtime.
    
    Contains:
    - Resolved values from all sources with precedence applied
    - Source attribution (which source provided each value)
    - Schema and policy information
    - Version and snapshot tracking
    
    This is the authoritative configuration that consumers should use.
    """
    
    # Identity (no defaults - must be provided)
    runtime_id: str  # Runtime this config applies to
    config_id: str  # Unique config instance ID
    version: int  # Configuration version number
    
    # Content fingerprint (SHA256 of effective values) - must come before fields with defaults
    content_digest: str
    
    # Data
    domains: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Domain -> field -> value
    sources: Dict[str, Tuple[ConfigurationSourceId, ...]] = field(default_factory=dict)  # Field path -> tuple of source IDs in precedence order
    
    # Metadata (with defaults)
    schema_versions: Dict[str, ConfigurationVersion] = field(default_factory=dict)  # domain -> schema version
    policy_version: Optional[ConfigurationVersion] = None
    feature_flag_version: Optional[ConfigurationVersion] = None
    capability_version: Optional[ConfigurationVersion] = None
    
    # Provenance
    created_at: float = field(default_factory=time.monotonic)
    sources_processed_at: Dict[str, float] = field(default_factory=dict)  # source_id -> timestamp
    
    # Diagnostics
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    deprecations: Tuple[str, ...] = field(default_factory=tuple)
    unresolved_optional: Tuple[str, ...] = field(default_factory=tuple)
    
    def get(self, domain: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value from a specific domain.
        
        Args:
            domain: Configuration domain (e.g., "kernel", "runtime")
            key: Field name within the domain
            default: Default value if not found
            
        Returns:
            The configuration value or default
        """
        domain_data = self.domains.get(domain, {})
        return domain_data.get(key, default)
    
    def has_key(self, domain: str, key: str) -> bool:
        """Check if a key exists in a domain."""
        domain_data = self.domains.get(domain, {})
        return key in domain_data
    
    def with_value(self, domain: str, key: str, value: Any) -> "EffectiveConfiguration":
        """
        Return new configuration with one value updated.
        
        Creates a new snapshot rather than mutating the existing one.
        Uses deep copy to ensure complete immutability.
        """
        import copy
        domains = copy.deepcopy(self.domains)
        if domain not in domains:
            domains[domain] = {}
        domains[domain][key] = value
        
        # Recalculate digest
        content_str = str(sorted(domain.items()) for domain in domains.values())
        new_digest = hashlib.sha256(content_str.encode()).hexdigest()
        
        return EffectiveConfiguration(
            runtime_id=self.runtime_id,
            config_id=str(hash(time.monotonic())),  # New ID for new snapshot
            version=self.version + 1,
            domains=domains,
            sources=dict(self.sources),
            schema_versions=dict(self.schema_versions),
            policy_version=self.policy_version,
            feature_flag_version=self.feature_flag_version,
            capability_version=self.capability_version,
            content_digest=new_digest,
            created_at=time.monotonic(),
            sources_processed_at=dict(self.sources_processed_at),
            warnings=self.warnings,
            deprecations=self.deprecations,
            unresolved_optional=self.unresolved_optional
        )
    
    def without_secrets(self) -> "EffectiveConfiguration":
        """Return configuration with sensitive values redacted."""
        secret_patterns = ("password", "secret", "token", "key", "credential")
        
        filtered_domains = {}
        for domain, data in self.domains.items():
            filtered_data = {}
            for key, value in data.items():
                if any(p in key.lower() for p in secret_patterns):
                    filtered_data[key] = "***FILTERED***"
                else:
                    filtered_data[key] = value
            filtered_domains[domain] = filtered_data
        
        # Recalculate digest
        content_str = str(sorted(domain.items()) for domain in filtered_domains.values())
        new_digest = hashlib.sha256(content_str.encode()).hexdigest()
        
        return EffectiveConfiguration(
            runtime_id=self.runtime_id,
            config_id=str(hash(time.monotonic())),  # New ID
            version=self.version,
            domains=filtered_domains,
            sources=dict(self.sources),
            schema_versions=dict(self.schema_versions),
            policy_version=self.policy_version,
            feature_flag_version=self.feature_flag_version,
            capability_version=self.capability_version,
            content_digest=new_digest,
            created_at=time.monotonic(),
            sources_processed_at=dict(self.sources_processed_at),
            warnings=self.warnings,
            deprecations=self.deprecations,
            unresolved_optional=self.unresolved_optional
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as a flat dictionary."""
        result = {}
        for domain, data in self.domains.items():
            for key, value in data.items():
                full_key = f"{domain}.{key}"
                result[full_key] = value
        return result


class SchemaRegistry:
    """
    Registry for configuration schemas.
    
    Provides:
    - Schema registration and retrieval
    - Schema composition with conflict detection
    - Version tracking
    
    Invariants:
    - One schema per domain path
    - No conflicting field definitions
    - Schemas are immutable once registered
    """
    
    def __init__(self):
        self._schemas: Dict[str, SchemaRegistration] = {}
        self._registry_id = SchemaRegistryId.generate()
        self._lock = __import__("threading").Lock()
    
    @property
    def registry_id(self) -> SchemaRegistryId:
        """Get the registry ID."""
        return self._registry_id
    
    def register_schema(
        self,
        domain_id: str,
        fields: Tuple[SchemaField, ...],
        version: Optional[ConfigurationVersion] = None
    ) -> ConfigurationSchemaId:
        """
        Register a schema for a domain.
        
        Args:
            domain_id: Domain identifier (e.g., "kernel", "runtime")
            fields: Schema field definitions
            version: Optional schema version
            
        Returns:
            Registered schema ID
            
        Raises:
            ValueError: If schema conflicts with existing schema
        """
        if not domain_id:
            raise ValueError("domain_id is required")
        
        if not fields:
            raise ValueError("At least one field is required")
        
        if version is None:
            version = ConfigurationVersion(1, 0, 0)
        
        # Check for conflicts
        with self._lock:
            existing = self._schemas.get(domain_id)
            if existing is not None:
                self._check_conflicts(existing.domain_schema, fields, domain_id)
            
            # Create new schema registration
            domain_schema = DomainSchema(
                domain_id=domain_id,
                fields=fields,
                schema_version=version
            )
            
            schema_id = ConfigurationSchemaId.generate()
            registration = SchemaRegistration(
                schema_id=schema_id,
                domain_schema=domain_schema,
                version=version
            )
            
            self._schemas[domain_id] = registration
        
        return schema_id
    
    def _check_conflicts(
        self,
        existing: DomainSchema,
        new_fields: Tuple[SchemaField, ...],
        domain_id: str
    ) -> None:
        """Check for conflicts between existing and new schemas."""
        existing_by_name = {f.name: f for f in existing.fields}
        
        for field in new_fields:
            if field.name in existing_by_name:
                existing_field = existing_by_name[field.name]
                
                # Check type compatibility
                if field.field_type != existing_field.field_type:
                    raise ValueError(
                        f"Schema conflict in {domain_id}.{field.name}: "
                        f"type mismatch (existing: {existing_field.field_type}, new: {field.field_type})"
                    )
                
                # Check mutability
                if field.mutability != existing_field.mutability:
                    raise ValueError(
                        f"Schema conflict in {domain_id}.{field.name}: "
                        f"mutability mismatch (existing: {existing_field.mutability}, new: {field.mutability})"
                    )
    
    def get_schema(self, domain_id: str) -> Optional[DomainSchema]:
        """Get a registered schema by domain ID."""
        registration = self._schemas.get(domain_id)
        if registration:
            return registration.domain_schema
        return None
    
    def get_all_schemas(self) -> Dict[str, DomainSchema]:
        """Get all registered schemas."""
        with self._lock:
            return {
                k: v.domain_schema for k, v in self._schemas.items()
            }
    
    def list_domains(self) -> List[str]:
        """List all domain IDs with registered schemas."""
        with self._lock:
            return list(self._schemas.keys())


class ConfigurationAuthority:
    """
    Canonical configuration authority for a runtime.
    
    This is the single source of truth for all configuration operations.
    
    Responsibilities:
    - Source registration and collection
    - Parsing and validation
    - Normalization and merge
    - Precedence resolution
    - Effective configuration generation
    - Snapshot creation and versioning
    - Configuration history
    
    Invariants:
    - Exactly one per runtime
    - All configuration flows through this authority
    - No direct source access by consumers
    - Immutable effective configurations
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._sources: Dict[str, Any] = {}  # Will hold source implementations
        self._precedence_model: Optional[PrecedenceModel] = None
        self._current_config: Optional[EffectiveConfiguration] = None
        self._config_version: int = 1
        self._lock = __import__("threading").Lock()
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    @property
    def current_config(self) -> Optional[EffectiveConfiguration]:
        """Get the current effective configuration."""
        with self._lock:
            return self._current_config
    
    @property
    def config_version(self) -> int:
        """Get the current configuration version."""
        with self._lock:
            return self._config_version
    
    def load_sources(
        self,
        sources: Tuple[Any, ...],
        precedence_model: Optional[PrecedenceModel] = None
    ) -> "ConfigurationAuthority":
        """
        Register configuration sources.
        
        Args:
            sources: Sequence of source implementations
            precedence_model: Optional precedence model for ordering
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            if precedence_model is not None:
                self._precedence_model = precedence_model
            
            for source in sources:
                # Source would have a source_id property
                self._sources[source.source_id.value] = source
            
            return self
    
    def resolve_configuration(self) -> EffectiveConfiguration:
        """
        Resolve configuration from all registered sources.
        
        Performs:
        1. Load raw values from all sources
        2. Parse and normalize values
        3. Apply precedence rules (higher priority wins)
        4. Merge with merge semantics
        
        Returns:
            EffectiveConfiguration with resolved values
        """
        with self._lock:
            # Collect all source results
            all_data: Dict[str, Any] = {}
            sources_by_field: Dict[str, List[Tuple[int, ConfigurationSourceId]]] = {}
            
            if self._precedence_model is None:
                # Default precedence: last registered wins
                for idx, (source_id, source) in enumerate(self._sources.items()):
                    result = source.load()
                    for field_path in result.data.keys():
                        sources_by_field.setdefault(field_path, []).append((idx, ConfigurationSourceId.from_string(source_id)))
            
            # Apply precedence and merge (simplified - actual implementation would be more complex)
            # For now, use the last source's values as winners
            final_data = {}
            for field_path, source_list in sources_by_field.items():
                if source_list:
                    _, winning_source_id = max(source_list, key=lambda x: x[0])
                    winning_source = self._sources.get(winning_source_id.value) if winning_source_id else None
                    if winning_source:
                        result = winning_source.load()
                        final_data[field_path] = result.data.get(field_path)
            
            # Create content digest
            content_str = str(sorted(final_data.items()))
            content_digest = hashlib.sha256(content_str.encode()).hexdigest()
            
            self._current_config = EffectiveConfiguration(
                runtime_id=self._runtime_id,
                config_id=ConfigurationId.generate().value,
                version=self._config_version,
                domains={"default": final_data},
                sources={
                    field: (sources_by_field[field][-1][1],) if sources_by_field.get(field)
                    else ()
                    for field in final_data
                },
                schema_versions={},
                content_digest=content_digest
            )
            
            return self._current_config
    
    def create_snapshot(self, effective_config: Optional[EffectiveConfiguration] = None) -> ConfigurationSnapshot:
        """
        Create a snapshot of current configuration state.
        
        Args:
            effective_config: Effective config to snapshot (uses current if not provided)
            
        Returns:
            ConfigurationSnapshot
        """
        with self._lock:
            if effective_config is None:
                effective_config = self._current_config
            
            if effective_config is None:
                raise ValueError("No configuration available for snapshot")
            
            # Create source snapshots
            source_snapshots = tuple(
                ConfigurationSourceSnapshot(
                    id=ConfigurationSourceId.from_string(source_id),
                    name=f"source_{idx}",
                    data={}
                )
                for idx, (source_id, _) in enumerate(self._sources.items())
            )
            
            return ConfigurationSnapshot(
                snapshot_id=ConfigurationSnapshotId.generate().value,
                effective_config=effective_config,
                source_snapshots=source_snapshots
            )


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # IDs (from types)
    "RuntimeId",
    "ConfigurationId", 
    "ConfigurationVersion",
    "ConfigurationSourceId",
    "ConfigurationSnapshotId",
    "ConfigurationSchemaId",
    "ConfigurationDomainId",
    "ConfigurationChangeId",
    
    # Precedence (from types)
    "PrecedenceLevel",
    "PrecedenceRule",
    "PrecedenceModel",
    
    # Sources (from types)
    "SourceType",
    "ConfigurationSourceDescriptor",
    "ConfigurationSourceResult",
    "SourceLoadingError",
    "SourceParsingError",
    
    # Schema (from types)
    "FieldType",
    "SchemaField",
    "DomainSchema",
    "ValidationError",
    "SchemaConflictType",
    "SchemaConflict",
    "SchemaRegistryId",
    "SchemaRegistration",
    "SchemaRegistry",
    
    # Domains and Secrets (from types)
    "ConfigurationDomain",
    "SecretReference",
    
    # Events (from types)
    "ConfigurationEvent",
    
    # Merge Semantics (from types)
    "MergeSemantic",
    "MergeRule",
    
    # Normalization (from types)
    "NormalizationRule",
    
    # Diffing (from types)
    "ConfigDiffChangeType",
    "ConfigDiffFinding",
    "ConfigurationDiff",
    
    # Snapshots (from types)
    "ConfigurationSourceSnapshot",
    "ConfigurationSnapshot",
    
    # Effective Configuration
    "EffectiveConfiguration",
    
    # Authorities
    "ConfigurationAuthority",
]

# Re-export SchemaConflictType for convenience
