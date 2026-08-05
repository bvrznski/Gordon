# Effective Configuration Module
# ==============================
"""
Effective configuration with source tracking, versioning, and snapshots.

Provides:
- Immutable effective configuration
- Source attribution tracking
- Versioned snapshots
- Runtime-scoped isolation

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
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

from . import ConfigurationSourceId


# =============================================================================
# Effective Configuration
# =============================================================================

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
    
    # Identity
    runtime_id: str  # Runtime this config applies to
    config_id: str  # Unique config instance ID
    version: int  # Configuration version number
    
    # Data
    domains: Dict[str, Dict[str, Any]]  # Domain -> field -> value
    sources: Dict[str, Tuple[str, ...]]  # Field path -> tuple of source IDs in precedence order
    
    # Metadata
    schema_versions: Dict[str, str] = field(default_factory=dict)  # domain -> schema version
    policy_version: Optional[str] = None
    feature_flag_version: Optional[str] = None
    capability_version: Optional[str] = None
    
    # Content fingerprint
    content_digest: str  # SHA256 or similar of effective values
    
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
    
    def get_source_attribution(self, field_path: str) -> Tuple[str, ...]:
        """
        Get the source attribution for a field.
        
        Returns sources in precedence order (highest priority last).
        """
        return self.sources.get(field_path, ())
    
    def with_value(self, domain: str, key: str, value: Any) -> "EffectiveConfiguration":
        """
        Return new configuration with one value updated.
        
        Creates a new snapshot rather than mutating the existing one.
        """
        domains = dict(self.domains)
        if domain not in domains:
            domains[domain] = {}
        domains[domain][key] = value
        
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
            content_digest=f"v{self.version}_{key}:{value}",
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
            content_digest=f"v{self.version}_redacted",
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


# =============================================================================
# Configuration Snapshot
# =============================================================================

@dataclass(frozen=True)
class ConfigurationSnapshotId:
    """Unique identifier for a configuration snapshot."""
    value: str
    
    @classmethod
    def generate(cls) -> "ConfigurationSnapshotId":
        return cls(value=str(time.monotonic()))
    
    @classmethod
    def from_string(cls, s: str) -> "ConfigurationSnapshotId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConfigurationSourceSnapshot:
    """
    Snapshot of a single configuration source at a point in time.
    """
    id: ConfigurationSourceId  # type: ignore
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
    effective_config: EffectiveConfiguration
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
# Configuration Diff
# =============================================================================

@dataclass(frozen=True)
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
    
    def requires_restart(self) -> bool:
        """Check if any changes require a restart."""
        return any(c.restart_required for c in self.changes)


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Effective Configuration
    "EffectiveConfiguration",
    
    # Snapshots
    "ConfigurationSnapshotId",
    "ConfigurationSourceSnapshot",
    "ConfigurationSnapshot",
    
    # Diffing
    "ConfigDiffChangeType",
    "ConfigDiffFinding",
    "ConfigurationDiff",
    
    # Source ID (re-exported)
    "ConfigurationSourceId",
]