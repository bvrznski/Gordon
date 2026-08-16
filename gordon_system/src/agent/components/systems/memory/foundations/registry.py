# Memory Registry - Phase 5.1 Canonical Artifact Discovery
# =========================================================

"""
Memory Registry: Discovery and tracking of memory artifacts.

Responsibilities:
    - Discover artifacts (find by ID, kind, etc.)
    - Track identities (what artifact IDs exist?)
    - Track revisions (which is current?)
    - Track provenance (where did they come from?)

Registry never owns artifacts - it only tracks them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# REGISTRY ENTRY - Tracking information for one artifact
# =============================================================================


@dataclass(frozen=True)
class RegistryEntry:
    """
    Tracking entry for a memory artifact.
    
    This contains metadata about the artifact without exposing its content.
    
    Fields:
        artifact_id:       Unique identifier
        
        # Artifact info
        artifact_kind:     What kind of artifact is this?
        
        # Revision tracking
        current_revision:  Which revision is currently active?
        total_revisions:   Total revisions in chain
        
        # Status
        status:            Active, archived, etc.
        validity:          Validity status
        
        # Timestamps
        created_at_utc:    When was the first version created?
        updated_at_utc:    When was the latest revision created?
        
        # Provenance (summary)
        origin_summary:    Where did this come from? (aggregated)
    """
    
    artifact_id: str                      # Unique identifier
    
    # Artifact info
    artifact_kind: Optional[str] = None   # What kind of thing is this?
    
    # Revision tracking
    current_revision: int = 1             # Current active revision number
    total_revisions: int = 1              # Total revisions in chain
    
    # Status
    status: str = "active"                # active, dormant, archived, etc.
    validity: str = "unknown"             # valid, invalid, unknown, etc.
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    # Provenance (summary - not full provenance record)
    origin_summary: Optional[str] = None  # Where did this come from?
    
    @property
    def is_current(self) -> bool:
        """Check if this entry's current revision matches the stored value."""
        return self.current_revision > 0
    
    def with_new_revision(
        self,
        new_content_hash: str,
    ) -> "RegistryEntry":
        """
        Create a registry entry updated for a new revision.
        
        Args:
            new_content_hash: Hash of the new content
            
        Returns:
            New RegistryEntry with incremented revision count
        """
        return dataclass_replace_entry(
            self,
            current_revision=self.current_revision + 1,
            total_revisions=self.total_revisions + 1,
            updated_at_utc=time.time(),
        )


# =============================================================================
# REGISTRY INDEX - Indexes for fast lookup
# =============================================================================


@dataclass(frozen=True)
class RegistryIndex:
    """
    Index entry for efficient artifact discovery.
    
    Fields:
        index_type:        What kind of index is this?
        index_key:         The key used for lookup (artifact_kind, timestamp range, etc.)
        
        # Indexed entries
        artifact_ids:      Which artifacts have this property?
    """
    
    index_type: str                       # e.g., "by_kind", "by_validity", "by_time"
    index_key: Optional[str] = None       # The specific value (e.g., "concept")
    
    artifact_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def count(self) -> int:
        """Count of indexed artifacts."""
        return len(self.artifact_ids)


# =============================================================================
# MEMORY REGISTRY - Artifact discovery and tracking
# =============================================================================


@dataclass(frozen=True)
class MemoryRegistry:
    """
    Registry for memory artifact discovery.
    
    Responsibilities:
        - Discover artifacts (find by ID, kind, status, etc.)
        - Track identities (what IDs exist?)
        - Track revisions (which is current?)
        - Provide indexes for fast lookup
        
    Never owns artifacts - only tracks their presence and metadata.
    
    Fields:
        entries:           Mapping of artifact_id -> RegistryEntry
        indexes:           Indexes for efficient discovery
        total_artifacts:   Count of all tracked artifacts
        created_at_utc:    When registry was initialized
    """
    
    # Storage
    entries: Dict[str, RegistryEntry] = field(default_factory=dict)
    indexes: Tuple[RegistryIndex, ...] = field(default_factory=tuple)
    
    # Metadata
    total_artifacts: int = 0
    created_at_utc: float = field(default_factory=time.time)
    
    def get_entry(self, artifact_id: str) -> Optional[RegistryEntry]:
        """Get the registry entry for an artifact."""
        return self.entries.get(artifact_id)
    
    def has_artifact(self, artifact_id: str) -> bool:
        """Check if an artifact is registered."""
        return artifact_id in self.entries
    
    def get_current_revision(self, artifact_id: str) -> int:
        """Get the current revision number for an artifact."""
        entry = self.entries.get(artifact_id)
        return entry.current_revision if entry else 0
    
    def list_by_kind(self, kind: str) -> Tuple[str, ...]:
        """List all artifacts of a specific kind."""
        # Find or create index by kind
        for idx in self.indexes:
            if idx.index_type == "by_kind" and idx.index_key == kind:
                return idx.artifact_ids
        
        # Fallback: filter entries
        return tuple(
            aid for aid, entry in self.entries.items()
            if entry.artifact_kind == kind
        )
    
    def list_by_status(self, status: str) -> Tuple[str, ...]:
        """List all artifacts with a specific status."""
        return tuple(
            aid for aid, entry in self.entries.items()
            if entry.status == status
        )
    
    def list_all_ids(self) -> Tuple[str, ...]:
        """Get all artifact IDs in the registry."""
        return tuple(self.entries.keys())
    
    def update_entry(
        self,
        artifact_id: str,
        new_entry: RegistryEntry,
    ) -> "MemoryRegistry":
        """
        Update a registry entry.
        
        Args:
            artifact_id: Which entry to update
            new_entry: The new entry data
            
        Returns:
            New MemoryRegistry with updated entry
        """
        new_entries = dict(self.entries)
        new_entries[artifact_id] = new_entry
        
        return dataclass_replace_registry(
            self,
            entries=new_entries,
            total_artifacts=len(new_entries),
        )
    
    def add_entry(self, artifact_id: str, entry: RegistryEntry) -> "MemoryRegistry":
        """Add a new entry to the registry."""
        return self.update_entry(artifact_id, entry)
    
    def remove_entry(self, artifact_id: str) -> "MemoryRegistry":
        """Remove an entry from the registry."""
        new_entries = {k: v for k, v in self.entries.items() if k != artifact_id}
        
        # Also update indexes
        new_indexes = []
        for idx in self.indexes:
            if artifact_id in idx.artifact_ids:
                remaining = tuple(aid for aid in idx.artifact_ids if aid != artifact_id)
                new_indexes.append(dataclass_replace_index(idx, artifact_ids=remaining))
            else:
                new_indexes.append(idx)
        
        return MemoryRegistry(
            entries=new_entries,
            indexes=tuple(new_indexes),
            total_artifacts=len(new_entries),
            created_at_utc=self.created_at_utc,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_registry(instance: MemoryRegistry, **kwargs) -> MemoryRegistry:
    """Replace fields in a frozen MemoryRegistry."""
    return MemoryRegistry(
        entries=dict(instance.entries) if "entries" not in kwargs else kwargs["entries"],
        indexes=kwargs.get("indexes", instance.indexes),
        total_artifacts=kwargs.get("total_artifacts", instance.total_artifacts),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
    )


def dataclass_replace_entry(instance: RegistryEntry, **kwargs) -> RegistryEntry:
    """Replace fields in a frozen RegistryEntry."""
    return RegistryEntry(
        artifact_id=instance.artifact_id,
        artifact_kind=kwargs.get("artifact_kind", instance.artifact_kind),
        current_revision=kwargs.get("current_revision", instance.current_revision),
        total_revisions=kwargs.get("total_revisions", instance.total_revisions),
        status=kwargs.get("status", instance.status),
        validity=kwargs.get("validity", instance.validity),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        updated_at_utc=kwargs.get("updated_at_utc", instance.updated_at_utc),
        origin_summary=kwargs.get("origin_summary", instance.origin_summary),
    )


def dataclass_replace_index(instance: RegistryIndex, **kwargs) -> RegistryIndex:
    """Replace fields in a frozen RegistryIndex."""
    return RegistryIndex(
        index_type=instance.index_type,
        index_key=kwargs.get("index_key", instance.index_key),
        artifact_ids=kwargs.get("artifact_ids", instance.artifact_ids),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryRegistry",
    "RegistryEntry",
    "RegistryIndex",
    "dataclass_replace_registry",
    "dataclass_replace_entry",
    "dataclass_replace_index",
]