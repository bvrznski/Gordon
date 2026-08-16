# Memory Identity - Phase 5.1 Canonical Semantic Identifier
# =========================================================

"""
Memory Identity: Stable, immutable identifiers for memory artifacts.

Every MemoryArtifact possesses:
    - stable identity (survives revisions)
    - semantic identity (what makes this 'this')
    - artifact kind (category classification)
    - revision tracking
    - provenance (origin history)

Identity Laws:
    IDENTITY-LAW-001: Every Memory Artifact has one stable semantic identity
    IDENTITY-LAW-002: Identity remains immutable
    IDENTITY-LAW-003: Identity survives revisions
    IDENTITY-LAW-004: Identity is globally unique within the Memory Substrate
    IDENTITY-LAW-005: Identity provenance is complete
    IDENTITY-LAW-006: Identity history is inspectable
    IDENTITY-LAW-007: Identity is never reassigned
    IDENTITY-LAW-008: Identity resolution is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# MEMORY IDENTITY KINDS
# =============================================================================


class MemoryIdentityKind(Enum):
    """
    Kinds of identity that can be assigned to artifacts.
    
    These define the semantic scope of identity:
        - ARTIFACT: Identity is unique per artifact (most common)
        - CONCEPT: Identity is for abstract concepts (shared across instances)
        - RELATIONSHIP: Identity is for relationships between artifacts
        - PROJECTION: Identity is for projection snapshots
        - QUERY_RESULT: Identity is for query result sets
    """
    
    ARTIFACT = "artifact"           # Unique per artifact instance
    CONCEPT = "concept"             # Shared across concept instances
    RELATIONSHIP = "relationship"   # Unique per relationship
    PROJECTION = "projection"       # Per projection snapshot
    QUERY_RESULT = "query_result"   # Per query result set


# =============================================================================
# MEMORY IDENTITY - Immutable Semantic Identifier
# =============================================================================


@dataclass(frozen=True)
class MemoryIdentity:
    """
    Immutable identifier for a memory artifact.
    
    Identity is the stable core that persists across revisions. When an artifact
    is revised, it keeps the same identity but gets a new revision number.
    
    Fields:
        artifact_id:           Globally unique artifact ID (UUID or equivalent)
        semantic_identity:     What makes this artifact semantically 'this'?
                                Can be content hash for factual artifacts,
                                logical equivalence for concepts
        
        # Revision tracking
        creation_revision:     First revision in this artifact's chain
        current_revision:      Current revision number (0 if not tracked)
        
        # Provenance
        provenance:            Where did this identity come from? (Any type to avoid circular deps)
        
        # Timestamps
        created_at_utc:        When identity was first assigned
    """
    
    # Core identifiers (required, no defaults)
    artifact_id: str                      # Globally unique identifier
    semantic_identity: str                # Semantic equivalence key
    
    # Classification - must be after required fields
    artifact_kind_str: str               # What kind of thing is this?
    
    # Revision tracking - must be after required fields with defaults
    creation_revision: str               # First revision in chain
    current_revision: int = 1            # Current revision number
    
    # All optional fields below
    provenance: Any = field(default_factory=lambda: {"origin": "system"})
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def revision_identity(self) -> str:
        """Get the current revision's identity URI."""
        return f"{self.artifact_id}:r{self.current_revision}"
    
    @property
    def identity_uri(self) -> str:
        """Get a URI-like identifier for this identity."""
        return f"memory://{self.artifact_kind_str}/{self.artifact_id}"
    
    @property
    def revision_uri(self) -> str:
        """Get the current revision's URI."""
        return f"{self.identity_uri}/r{self.current_revision}"
    
    @classmethod
    def create_for_artifact(
        cls,
        semantic_identity: str,
        artifact_kind_str: str = "unknown",
    ) -> "MemoryIdentity":
        """
        Create a new identity for an artifact.
        
        Args:
            semantic_identity: What makes this semantically 'this'?
            artifact_kind_str: String representation of the kind (optional)
            
        Returns:
            New MemoryIdentity with generated artifact_id
        """
        return cls(
            artifact_id=str(uuid.uuid4()),
            semantic_identity=semantic_identity,
            artifact_kind_str=artifact_kind_str,
            creation_revision=str(uuid.uuid4()),  # Initial revision ID
            current_revision=1,
            provenance={"origin": "system"},
            created_at_utc=time.time(),
        )
    
    @classmethod
    def from_uri(cls, uri: str) -> Optional["MemoryIdentity"]:
        """
        Parse a memory URI back into an identity.
        
        Format: memory://{kind}/{artifact_id}[/r{revision}]
        
        Args:
            uri: The URI to parse
            
        Returns:
            MemoryIdentity if parsing succeeds, None otherwise
        """
        try:
            # Remove protocol prefix
            if not uri.startswith("memory://"):
                return None
            
            rest = uri[9:]  # Skip "memory://"
            
            # Split into parts
            parts = rest.split("/")
            if len(parts) < 2:
                return None
            
            kind_str = parts[0]
            artifact_id = parts[1]
            
            # Parse revision if present
            current_revision = 1
            if len(parts) >= 4 and parts[2] == "r":
                current_revision = int(parts[3])
            
            return cls(
                artifact_id=artifact_id,
                semantic_identity=f"{kind_str}:{artifact_id}",
                artifact_kind_str=kind_str,
                creation_revision=str(uuid.uuid4()),
                current_revision=current_revision,
                provenance={"origin": "system"},
            )
        except Exception:
            return None

    def for_new_revision(self, new_content_hash: str) -> "MemoryIdentity":
        """
        Create identity for a new revision of this artifact.
        
        This preserves the artifact_id but creates a new revision tracking
        structure. The actual revision record is created by MemoryRevision.
        
        Args:
            new_content_hash: Hash of the new content
            
        Returns:
            New MemoryIdentity with incremented current_revision
        """
        return dataclass_replace(
            self,
            current_revision=self.current_revision + 1,
            provenance={
                "origin": "system",
                "creation_process": f"New revision created with hash: {new_content_hash[:16]}...",
                "change_reason": f"Revision update for artifact {self.artifact_id}",
            },
        )
    
    def is_same_artifact(self, other: "MemoryIdentity") -> bool:
        """Check if two identities refer to the same artifact (not revision)."""
        return (
            self.artifact_id == other.artifact_id
            and self.artifact_kind_str == other.artifact_kind_str
        )


# =============================================================================
# MEMORY IDENTITY BUILDER
# =============================================================================


class MemoryIdentityBuilder:
    """
    Mutable builder for constructing memory identities.
    """
    
    def __init__(
        self,
        artifact_kind_str: str = "unknown",
        semantic_identity: Optional[str] = None,
    ):
        self._artifact_id: str = str(uuid.uuid4())
        self._semantic_identity = semantic_identity
        self._artifact_kind_str = artifact_kind_str
        
        # Revision tracking
        self._creation_revision = str(uuid.uuid4())
        self._current_revision = 1
        
        # Provenance (dict to avoid circular deps)
        self._provenance = {"origin": "system"}
        
        # Timestamps
        self._created_at_utc = time.time()
    
    def set_artifact_id(self, artifact_id: str) -> "MemoryIdentityBuilder":
        """Set the artifact ID."""
        self._artifact_id = artifact_id
        return self
    
    def set_semantic_identity(self, semantic_identity: str) -> "MemoryIdentityBuilder":
        """Set the semantic identity."""
        self._semantic_identity = semantic_identity
        return self
    
    def set_artifact_kind_str(self, kind_str: str) -> "MemoryIdentityBuilder":
        """Set the artifact kind string."""
        self._artifact_kind_str = kind_str
        return self
    
    def set_creation_revision(self, revision_id: str) -> "MemoryIdentityBuilder":
        """Set the creation revision ID."""
        self._creation_revision = revision_id
        return self
    
    def set_current_revision(self, revision_number: int) -> "MemoryIdentityBuilder":
        """Set the current revision number."""
        if revision_number < 1:
            raise ValueError("Revision number must be >= 1")
        self._current_revision = revision_number
        return self
    
    def set_provenance_origin(self, origin: str) -> "MemoryIdentityBuilder":
        """Set provenance origin."""
        self._provenance["origin"] = origin
        return self
    
    def set_created_at(self, timestamp_utc: float) -> "MemoryIdentityBuilder":
        """Set creation timestamp."""
        self._created_at_utc = timestamp_utc
        return self
    
    def build(self) -> MemoryIdentity:
        """
        Build an immutable MemoryIdentity.
        
        Returns:
            New MemoryIdentity with all settings applied
            
        Raises:
            ValueError: If required fields are missing
        """
        if not self._artifact_id:
            raise ValueError("artifact_id is required")
        
        # Set semantic identity from artifact ID if not provided
        if self._semantic_identity is None:
            self._semantic_identity = f"{self._artifact_kind_str}:{self._artifact_id}"
        
        return MemoryIdentity(
            artifact_id=self._artifact_id,
            semantic_identity=self._semantic_identity,
            artifact_kind_str=self._artifact_kind_str,
            creation_revision=self._creation_revision,
            current_revision=self._current_revision,
            provenance=dict(self._provenance),
            created_at_utc=self._created_at_utc,
        )


# =============================================================================
# MEMORY PROVENANCE - Complete origin tracking
# =============================================================================


@dataclass(frozen=True)
class MemoryProvenance:
    """
    Complete provenance record for a memory artifact.
    
    Every artifact has complete provenance showing where it came from, who
    created it, and what transformations it underwent. Provenance survives
    all revisions and changes.
    
    Fields:
        origin:               Primary source (person, system, event)
        
        # Creation process
        creation_process:     How was this artifact created?
        
        # Semantic time
        semantic_time_utc:    When this became semantically meaningful
        created_at_utc:       When the record was created
        
        # Change tracking
        change_reason:        Why was this revision created?
        changed_by:           Who made the change (optional)
    """
    
    # Core origin
    origin: str = "system"                # Primary source identifier
    
    # Creation process
    creation_process: Optional[str] = None  # How was this created?
    
    # Semantic time
    semantic_time_utc: float = field(default_factory=time.time)
    created_at_utc: float = field(default_factory=time.time)
    
    # Change tracking
    change_reason: Optional[str] = None
    changed_by: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if provenance has essential information."""
        return len(self.origin) > 0 and self.created_at_utc > 0.0
    
    def with_change_reason(self, reason: str) -> "MemoryProvenance":
        """Set the change reason."""
        return dataclass_replace(self, change_reason=reason)
    
    def with_changed_by(self, changer: str) -> "MemoryProvenance":
        """Set who made the change."""
        return dataclass_replace(self, changed_by=changer)


# =============================================================================
# MEMORY PROVENANCE SOURCE - A single source of information
# =============================================================================


@dataclass(frozen=True)
class MemoryProvenanceSource:
    """
    A single provenance source (where information came from).
    
    Fields:
        source_type:         Category of the source (observation, inference,
                             document, external_api, etc.)
        source_location:     Where to find the source (file path, URL, etc.)
        confidence:          0.0-1.0 trust in this source
        accessed_at_utc:     When we accessed the source
        notes:               Additional context about the source
    """
    
    source_type: str                      # observation, inference, document, api, etc.
    source_location: str                  # file path, URL, memory reference
    confidence: float = 1.0              # Trust in this source (0.0-1.0)
    accessed_at_utc: float = field(default_factory=time.time)
    notes: Optional[str] = None           # Additional context


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryIdentity, **kwargs) -> MemoryIdentity:
    """Replace fields in a frozen dataclass."""
    return MemoryIdentity(
        artifact_id=instance.artifact_id,
        semantic_identity=instance.semantic_identity,
        artifact_kind_str=kwargs.get("artifact_kind_str", instance.artifact_kind_str),
        creation_revision=kwargs.get("creation_revision", instance.creation_revision),
        current_revision=kwargs.get("current_revision", instance.current_revision),
        provenance=kwargs.get("provenance", instance.provenance),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
    )


def dataclass_replace_provenance(instance: MemoryProvenance, **kwargs) -> MemoryProvenance:
    """Replace fields in a frozen MemoryProvenance."""
    return MemoryProvenance(
        origin=kwargs.get("origin", instance.origin),
        creation_process=kwargs.get("creation_process", instance.creation_process),
        semantic_time_utc=kwargs.get("semantic_time_utc", instance.semantic_time_utc),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        change_reason=kwargs.get("change_reason", instance.change_reason),
        changed_by=kwargs.get("changed_by", instance.changed_by),
    )


def generate_artifact_id() -> str:
    """Generate a globally unique artifact ID."""
    return f"art:{uuid.uuid4().hex[:24]}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryIdentity",
    "MemoryIdentityKind",
    "MemoryIdentityBuilder",
    "MemoryProvenance",
    "MemoryProvenanceSource",
    "dataclass_replace",
    "dataclass_replace_provenance",
    "generate_artifact_id",
]