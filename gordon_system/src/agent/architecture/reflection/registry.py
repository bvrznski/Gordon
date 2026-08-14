"""Reflection Registry - Phase 3.23 Canonical Registry Architecture.
================================================================================

Canonical registries for reflection metadata, discovery results, and audit records.

ARCHITECTURAL PRINCIPLES:
- Registries store metadata, they don't own behavior
- Registries are discoverable without instantiation
- One canonical registry per concern type
- All registries expose immutable metadata

REGISTRY RESPONSIBILITIES:
- Store and index metadata records
- Provide discovery of registered entities
- Expose audit trails and validation reports
- Support manifest generation

"""
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time


# =============================================================================
# REGISTRY TYPES & CATEGORIES
# =============================================================================


class RegistryType(Enum):
    """Types of registries in the reflection architecture."""
    
    ENTITY_METADATA = "entity_metadata"
    CAPABILITY = "capability"
    INTERFACE = "interface"
    DEPENDENCY = "dependency"
    SECURITY_POLICY = "security_policy"
    CONFIGURATION_SCHEMA = "configuration_schema"
    EXECUTION_PROFILE = "execution_profile"
    DIAGNOSTIC_ENDPOINT = "diagnostic_endpoint"


class RegistryScope(Enum):
    """Scope of registry contents."""
    
    GLOBAL = "global"  # Entire repository
    PACKAGE = "package"  # Specific package
    MODULE = "module"  # Specific module


# =============================================================================
# REGISTRY ENTRY MODELS
# =============================================================================


@dataclass(frozen=True)
class RegistryEntry:
    """
    A single entry in a registry.
    
    Immutable record of registration with metadata and provenance.
    """
    
    # Identity (required - no defaults)
    entry_id: str  # Unique identifier for this entry
    registered_at_utc: float
    
    # Content reference
    content_type: str  # e.g., "EntityMetadata", "CapabilityDefinition"
    content_reference: str  # Reference to actual content
    
    # Classification
    category: str
    tags: Tuple[str, ...] = ()
    
    # Status
    status: str = "active"  # active, deprecated, retired


@dataclass(frozen=True)
class ManifestEntry:
    """
    An entry in a manifest (group of entries).
    
    Represents a complete snapshot of a registry at a point in time.
    """
    
    manifest_id: str  # Unique identifier for the manifest
    generated_at_utc: float
    
    registry_type: RegistryType
    scope: RegistryScope
    
    entries: Tuple[RegistryEntry, ...]
    
    @property
    def entry_count(self) -> int:
        """Get the number of entries in this manifest."""
        return len(self.entries)


# =============================================================================
# REGISTRY MODELS
# =============================================================================


@dataclass(frozen=True)
class EntityMetadataRegistry:
    """
    Registry for entity metadata.
    
    Indexes all architectural entities with their complete metadata.
    """
    
    entries: Tuple[EntityMetadata, ...] = ()  # Import from metadata module
    
    @property
    def count(self) -> int:
        """Get the number of registered entities."""
        return len(self.entries)
    
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Get metadata by entity ID."""
        for entry in self.entries:
            if hasattr(entry, 'identity') and getattr(entry.identity, 'id', None) == entity_id:
                return entry
        return None
    
    def find_by_type(self, type_name: str) -> Tuple[Any, ...]:
        """Find all entries of a given type."""
        result = []
        for entry in self.entries:
            if hasattr(entry, 'identity') and getattr(entry.identity, 'type_', '') == type_name:
                result.append(entry)
        return tuple(result)
    
    def get_entities_by_category(self, category: str) -> Tuple[Any, ...]:
        """Get all entities in a category."""
        result = []
        for entry in self.entries:
            if hasattr(entry, 'identity') and getattr(entry.identity, 'category', '') == category:
                result.append(entry)
        return tuple(result)


@dataclass(frozen=True)
class CapabilityRegistry:
    """
    Registry for capabilities.
    
    Indexes all capabilities across the repository with their contracts.
    """
    
    entries: Tuple[CapabilityMetadata, ...] = ()
    
    @property
    def count(self) -> int:
        """Get the number of registered capabilities."""
        return len(self.entries)
    
    def get_by_type(self, capability_type: str) -> Tuple[Any, ...]:
        """Get all capabilities of a given type."""
        result = []
        for entry in self.entries:
            if hasattr(entry, 'type_') and getattr(entry.type_, 'value', '') == capability_type:
                result.append(entry)
        return tuple(result)


@dataclass(frozen=True)
class AuditRecord:
    """
    A single audit record.
    
    Immutable log of an audit operation with results.
    """
    
    record_id: str
    timestamp_utc: float
    
    # Audit details
    audit_type: str  # e.g., "validation", "discovery", "migration"
    target: str  # What was audited
    
    # Results
    passed: bool
    findings: Tuple[str, ...] = ()
    
    # Metadata
    auditor: str = "system"


@dataclass(frozen=True)
class AuditLog:
    """
    Complete audit log.
    
    Immutable record of all audit operations.
    """
    
    records: Tuple[AuditRecord, ...]
    generated_at_utc: float = field(default_factory=time.time)
    
    @property
    def count(self) -> int:
        """Get the number of audit records."""
        return len(self.records)
    
    @property
    def passed_count(self) -> int:
        """Get the number of passed audits."""
        return sum(1 for r in self.records if r.passed)
    
    @property
    def failed_count(self) -> int:
        """Get the number of failed audits."""
        return sum(1 for r in self.records if not r.passed)


# =============================================================================
# REGISTRY BUILDER - For controlled creation
# =============================================================================


class RegistryBuilder:
    """
    Builder for registries with immutability guarantees.
    
    Ensures all required fields are present before freezing.
    Once built, the result is frozen and immutable.
    """
    
    def __init__(self) -> None:
        self._entity_metadata_entries: List[Any] = []
        self._capability_entries: List[CapabilityMetadata] = []
        self._audit_records: List[AuditRecord] = []
    
    # Entity metadata registry
    def add_entity_metadata(self, entry: Any) -> "RegistryBuilder":
        """Add an entity metadata entry."""
        self._entity_metadata_entries.append(entry)
        return self
    
    def set_entity_metadata_registry(
        self,
        entries: Tuple[Any, ...]
    ) -> "RegistryBuilder":
        """Set the entity metadata registry with a tuple of entries."""
        # Validate that all items have the required structure
        for entry in entries:
            if not hasattr(entry, 'identity'):
                raise ValueError("EntityMetadata must have 'identity' attribute")
        self._entity_metadata_entries = list(entries)
        return self
    
    def build_entity_metadata_registry(self) -> EntityMetadataRegistry:
        """Build the entity metadata registry."""
        return EntityMetadataRegistry(
            entries=tuple(self._entity_metadata_entries)
        )
    
    # Capability registry
    def add_capability(self, capability: CapabilityMetadata) -> "RegistryBuilder":
        """Add a capability entry."""
        self._capability_entries.append(capability)
        return self
    
    def build_capability_registry(self) -> CapabilityRegistry:
        """Build the capability registry."""
        return CapabilityRegistry(entries=tuple(self._capability_entries))
    
    # Audit log
    def add_audit_record(self, record: AuditRecord) -> "RegistryBuilder":
        """Add an audit record."""
        self._audit_records.append(record)
        return self
    
    def build_audit_log(self) -> AuditLog:
        """Build the audit log."""
        return AuditLog(
            records=tuple(self._audit_records),
            generated_at_utc=time.time()
        )


# =============================================================================
# REGISTRY OPERATIONS
# =============================================================================


def create_entity_metadata_registry_from_inventory(inventory: Any) -> EntityMetadataRegistry:
    """
    Create an entity metadata registry from an architecture inventory.
    
    Args:
        inventory: ArchitectureInventory with packages, modules, etc.
        
    Returns:
        EntityMetadataRegistry with entries for all discovered entities
    """
    # This would be implemented to convert inventory entries to metadata entries
    # For now, return empty - concrete implementation depends on specific requirements
    return EntityMetadataRegistry(entries=())


def create_manifest(
    registry_type: RegistryType,
    scope: RegistryScope,
    entries: Tuple[RegistryEntry, ...]
) -> ManifestEntry:
    """
    Create a manifest for a set of registry entries.
    
    Args:
        registry_type: Type of registry
        scope: Scope of the entries (global, package, module)
        entries: The entries to include in the manifest
        
    Returns:
        ManifestEntry with all entries and metadata
    """
    import uuid
    
    return ManifestEntry(
        manifest_id=str(uuid.uuid4()),
        generated_at_utc=time.time(),
        registry_type=registry_type,
        scope=scope,
        entries=entries
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enumerations
    "RegistryType",
    "RegistryScope",
    
    # Entry models
    "RegistryEntry",
    "ManifestEntry",
    
    # Registry models
    "EntityMetadataRegistry",
    "CapabilityRegistry",
    
    # Audit models
    "AuditRecord",
    "AuditLog",
    
    # Builder
    "RegistryBuilder",
    
    # Operations
    "create_entity_metadata_registry_from_inventory",
    "create_manifest",
]