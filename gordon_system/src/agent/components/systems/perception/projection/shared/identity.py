# Perception Projection Identity - Phase 5.2.4
# =============================================

"""
Perception Projection Identity system.

Every published projection shall possess:
    - stable projection identity
    - projection kind
    - source revision references
    - publication revision
    - consumer contract reference
    - generation provenance

Projection identity represents the published view.
It does not replace source artifact identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import uuid


# =============================================================================
# PROJECTION KINDS
# =============================================================================


class ProjectionKind:
    """
    Kinds of projections supported by the system.
    
    Canonical projection domains:
        - PERCEPT: Individual or grouped Percepts
        - SCENE: One or more perceptual Scenes
        - EVENT: Observed state transitions
        - WORKSPACE: Bounded view for Workspace Network
    
    Shared mechanisms:
        - SNAPSHOT: Immutable capture at a revision
        - STREAM: Sequence of updates
        - INCREMENTAL: Changes relative to prior projection
        - SUMMARY: Reduced detail while preserving structure
        - DIAGNOSTIC: Health and diagnostics views
    """
    
    PERCEPT = "percept"
    SCENE = "scene"
    EVENT = "event"
    WORKSPACE = "workspace"
    
    SNAPSHOT = "snapshot"
    STREAM = "stream"
    INCREMENTAL = "incremental"
    SUMMARY = "summary"
    DIAGNOSTIC = "diagnostic"


# =============================================================================
# PROJECTION IDENTITY
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionIdentity:
    """
    Immutable identity for a published projection.
    
    Every projection must have a stable identity that distinguishes it
    from other projections, even when representing the same content at
    different revisions.
    
    Properties:
        projection_identity: Unique identifier for this projection
        projection_kind: The kind of projection (percept, scene, event, etc.)
        source_revision_references: References to source artifact revisions
        publication_revision: Revision number for this projection view
        consumer_contract_reference: Reference to the consumer contract used
        generation_provenance: How and why this projection was generated
    """
    
    projection_identity: str
    
    projection_kind: str
    
    # Source artifacts that were used to create this projection
    source_artifact_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Revision tracking
    source_revision_references: Dict[str, int] = field(default_factory=dict)
    publication_revision: int = 1
    
    # Consumer contract reference
    consumer_contract_reference: str = ""
    
    # Generation provenance
    generation_reason: str = "default"
    generated_at_utc: float = field(default_factory=hash)
    
    @classmethod
    def create(
        cls,
        projection_kind: str,
        source_artifact_ids: List[str],
        source_revisions: Optional[Dict[str, int]] = None,
        consumer_contract_reference: str = "",
        generation_reason: str = "default",
    ) -> "PerceptionProjectionIdentity":
        """
        Create a new projection identity.
        
        Args:
            projection_kind: Kind of projection (percept, scene, event, etc.)
            source_artifact_ids: IDs of source artifacts
            source_revisions: Mapping of artifact ID to revision
            consumer_contract_reference: Reference to consumer contract
            generation_reason: Reason for generating this projection
            
        Returns:
            New ProjectionIdentity instance
        """
        return cls(
            projection_identity=f"projection:{uuid.uuid4().hex[:24]}",
            projection_kind=projection_kind,
            source_artifact_ids=tuple(source_artifact_ids),
            source_revision_references=source_revisions or {},
            publication_revision=1,
            consumer_contract_reference=consumer_contract_reference,
            generation_reason=generation_reason,
            generated_at_utc=hash,  # Will be replaced by actual timestamp
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the projection identity has minimal required data."""
        return (
            len(self.projection_identity) > 0 and
            len(self.projection_kind) > 0
        )
    
    def with_revision(self, new_revision: int) -> "PerceptionProjectionIdentity":
        """
        Create a new identity with an updated publication revision.
        
        This preserves the projection identity while indicating a new version.
        
        Args:
            new_revision: The next revision number
            
        Returns:
            New ProjectionIdentity with incremented revision
        """
        return PerceptionProjectionIdentity(
            projection_identity=self.projection_identity,
            projection_kind=self.projection_kind,
            source_artifact_ids=self.source_artifact_ids,
            source_revision_references=dict(self.source_revision_references),
            publication_revision=new_revision,
            consumer_contract_reference=self.consumer_contract_reference,
            generation_reason=self.generation_reason,
            generated_at_utc=hash,  # Will be replaced
        )
    
    def with_consumer_contract(self, contract_ref: str) -> "PerceptionProjectionIdentity":
        """
        Create a new identity with updated consumer contract reference.
        
        Args:
            contract_ref: New consumer contract reference
            
        Returns:
            New ProjectionIdentity with updated contract reference
        """
        return PerceptionProjectionIdentity(
            projection_identity=self.projection_identity,
            projection_kind=self.projection_kind,
            source_artifact_ids=self.source_artifact_ids,
            source_revision_references=dict(self.source_revision_references),
            publication_revision=self.publication_revision + 1,
            consumer_contract_reference=contract_ref,
            generation_reason=self.generation_reason,
            generated_at_utc=hash,  # Will be replaced
        )
    
    def with_source_revisions(
        self,
        new_revisions: Dict[str, int],
    ) -> "PerceptionProjectionIdentity":
        """
        Create a new identity with updated source revision references.
        
        Args:
            new_revisions: Mapping of artifact ID to revision
            
        Returns:
            New ProjectionIdentity with updated revisions
        """
        return PerceptionProjectionIdentity(
            projection_identity=self.projection_identity,
            projection_kind=self.projection_kind,
            source_artifact_ids=self.source_artifact_ids,
            source_revision_references=dict(new_revisions),
            publication_revision=self.publication_revision + 1,
            consumer_contract_reference=self.consumer_contract_reference,
            generation_reason=self.generation_reason,
            generated_at_utc=hash,  # Will be replaced
        )


# =============================================================================
# IDENTITY BUILDER
# =============================================================================


class PerceptionProjectionIdentityBuilder:
    """
    Mutable builder for constructing projection identities.
    
    Usage:
        identity = (PerceptionProjectionIdentityBuilder()
            .set_projection_kind("percept")
            .add_source_artifact("artifact1")
            .set_consumer_contract("consumer:123")
            .build())
    """
    
    def __init__(self):
        self._projection_identity: str = f"projection:{uuid.uuid4().hex[:24]}"
        self._projection_kind: str = "unknown"
        self._source_artifact_ids: List[str] = []
        self._source_revision_references: Dict[str, int] = {}
        self._publication_revision: int = 1
        self._consumer_contract_reference: str = ""
        self._generation_reason: str = "default"
    
    def set_identity(self, identity: str) -> "PerceptionProjectionIdentityBuilder":
        """Set the projection identity."""
        self._projection_identity = identity
        return self
    
    def set_kind(self, kind: str) -> "PerceptionProjectionIdentityBuilder":
        """Set the projection kind (percept, scene, event, workspace)."""
        self._projection_kind = kind
        return self
    
    def add_source_artifact(self, artifact_id: str) -> "PerceptionProjectionIdentityBuilder":
        """Add a source artifact ID."""
        if artifact_id not in self._source_artifact_ids:
            self._source_artifact_ids.append(artifact_id)
        return self
    
    def set_source_revisions(
        self,
        revisions: Dict[str, int],
    ) -> "PerceptionProjectionIdentityBuilder":
        """Set source revision references."""
        self._source_revision_references = dict(revisions)
        return self
    
    def increment_revision(self) -> "PerceptionProjectionIdentityBuilder":
        """Increment the publication revision."""
        self._publication_revision += 1
        return self
    
    def set_consumer_contract(self, contract_ref: str) -> "PerceptionProjectionIdentityBuilder":
        """Set consumer contract reference."""
        self._consumer_contract_reference = contract_ref
        return self
    
    def set_generation_reason(self, reason: str) -> "PerceptionProjectionIdentityBuilder":
        """Set the generation reason."""
        self._generation_reason = reason
        return self
    
    def build(self) -> PerceptionProjectionIdentity:
        """Build an immutable ProjectionIdentity."""
        if not self._projection_kind:
            raise ValueError("projection kind is required")
        if len(self._source_artifact_ids) == 0:
            raise ValueError("at least one source artifact is required")
        
        return PerceptionProjectionIdentity(
            projection_identity=self._projection_identity,
            projection_kind=self._projection_kind,
            source_artifact_ids=tuple(self._source_artifact_ids),
            source_revision_references=dict(self._source_revision_references),
            publication_revision=self._publication_revision,
            consumer_contract_reference=self._consumer_contract_reference,
            generation_reason=self._generation_reason,
            generated_at_utc=hash,  # Will be replaced
        )


__all__ = [
    "ProjectionKind",
    "PerceptionProjectionIdentity",
    "PerceptionProjectionIdentityBuilder",
]