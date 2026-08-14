# Data & Artifact Lineage Identities - Phase 3.19.9
# ====================================================

"""
Lineage identity types for tracking data provenance and evolution.

Every artifact in Gordon should track:
    - Parent-child relationships (where it came from)
    - Derivation chains (how it evolved)
    - Transformation history (what operations were applied)

LINEAGE HIERARCHY:
    LineageId               - Complete lineage trace
        ├── DerivationId          - How data was derived
        └── TransformationId      - What transformations were applied
        
INVARIANTS:
    LIN-001: Every artifact has exactly one complete lineage
    LIN-002: Lineage forms a directed acyclic graph (no cycles)
    LIN-003: Lineage is immutable once created
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import uuid


# =============================================================================
# LINEAGE IDENTITY
# =============================================================================


@dataclass(frozen=True)
class LineageId:
    """
    Canonical identity for a complete lineage trace.
    
    A lineage trace represents the full history of how an artifact
    came to exist, including all parent artifacts and transformations.
    
    INVARIANTS:
        LIN-001: Every artifact has exactly one lineage trace
        LIN-002: Lineage traces form a DAG (no cycles)
        LIN-003: Lineage IDs are globally unique
        
    PARAMETERS:
        value         - The actual UUID string
        root_id       - ID of the original source artifact
        depth         - Number of transformations from root
    """
    
    value: str = field(default_factory=lambda: f"ln_{uuid.uuid4().hex[:20]}")
    root_id: Optional[str] = None
    depth: int = 1
    
    @classmethod
    def generate(cls, root_id: Optional[str] = None) -> "LineageId":
        """Generate a new lineage ID."""
        return cls(root_id=root_id)
    
    @property
    def is_root(self) -> bool:
        """Check if this is the root of the lineage (no parents)."""
        return self.root_id is None
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node with no children."""
        return self.depth == 1


# =============================================================================
# DERIVATION IDENTITY
# =============================================================================


@dataclass(frozen=True)
class DerivationId:
    """
    Canonical identity for a derivation relationship.
    
    A derivation represents the relationship between two artifacts where
    one was derived from another (e.g., a processed version).
    
    INVARIANTS:
        DER-001: Every derivation has exactly one source and target
        DER-002: Derivation IDs are globally unique
        DER-003: Derivations form DAGs (no cycles)
        
    PARAMETERS:
        value         - The actual UUID string
        source_id     - ID of the source artifact
        target_id     - ID of the derived artifact
        type          - Type of derivation (copy, transform, aggregate, etc.)
    """
    
    value: str = field(default_factory=lambda: f"drv_{uuid.uuid4().hex[:20]}")
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    derivation_type: Optional[str] = None  # e.g., "transform", "aggregate"
    
    @classmethod
    def generate(
        cls,
        source_id: str,
        target_id: str,
        derivation_type: Optional[str] = None,
    ) -> "DerivationId":
        """Generate a derivation ID for a specific relationship."""
        hash_input = f"{source_id}:{target_id}:{derivation_type or ''}"
        value = uuid.uuid5(uuid.NAMESPACE_DNS, hash_input).hex[:20]
        return cls(
            value=f"drv_{value}",
            source_id=source_id,
            target_id=target_id,
            derivation_type=derivation_type,
        )


# =============================================================================
# TRANSFORMATION IDENTITY
# =============================================================================


@dataclass(frozen=True)
class TransformationId:
    """
    Canonical identity for a transformation operation.
    
    A transformation is an operation that modifies data from one form to
    another, with the original and transformed versions both preserved.
    
    INVARIANTS:
        TRA-001: Every transformation has exactly one input and output
        TRA-002: Transformations are deterministic (same input -> same output)
        TRA-003: Transformation IDs are globally unique
        
    PARAMETERS:
        value         - The actual UUID string
        operation     - Name of the transformation operation
        input_ids     - IDs of input artifacts
        output_id     - ID of output artifact
        config_hash   - Hash of configuration used for this transformation
    """
    
    value: str = field(default_factory=lambda: f"tfm_{uuid.uuid4().hex[:20]}")
    operation: str  # e.g., "filter", "aggregate", "join"
    input_ids: tuple[str, ...] = field(default_factory=tuple)
    output_id: Optional[str] = None
    config_hash: Optional[str] = None
    
    @classmethod
    def generate(
        cls,
        operation: str,
        input_ids: Optional[tuple[str, ...]] = None,
        output_id: Optional[str] = None,
        config_hash: Optional[str] = None,
    ) -> "TransformationId":
        """Generate a transformation ID."""
        return cls(
            value=f"tfm_{uuid.uuid4().hex[:20]}",
            operation=operation,
            input_ids=input_ids or tuple(),
            output_id=output_id,
            config_hash=config_hash,
        )


# =============================================================================
# VERSION LINEAGE
# =============================================================================


@dataclass(frozen=True)
class VersionLineageId:
    """
    Canonical identity for a version lineage.
    
    Version lineages track how an artifact evolved through multiple versions
    within the same generation (e.g., configuration updates).
    
    INVARIANTS:
        VLN-001: Every version belongs to exactly one version lineage
        VLN-002: Version lineages form linear chains (v1 -> v2 -> v3...)
        VLN-003: Version IDs are deterministic from sequence number
        
    PARAMETERS:
        value         - The actual UUID string
        artifact_id   - ID of the artifact being versioned
        current_version - Current version number in this lineage
    """
    
    value: str = field(default_factory=lambda: f"vln_{uuid.uuid4().hex[:20]}")
    artifact_id: Optional[str] = None
    current_version: int = 1
    
    @classmethod
    def generate(cls, artifact_id: Optional[str] = None) -> "VersionLineageId":
        """Generate a version lineage ID."""
        return cls(artifact_id=artifact_id)
    
    @property
    def is_initial(self) -> bool:
        """Check if this is the initial version (v1)."""
        return self.current_version == 1


# =============================================================================
# REVISION LINEAGE
# =============================================================================


@dataclass(frozen=True)
class RevisionLineageId:
    """
    Canonical identity for a revision lineage.
    
    Revisions represent different states of an artifact within the same
    version (e.g., drafts, patches, hotfixes).
    
    INVARIANTS:
        REV-001: Every revision belongs to exactly one revision lineage  
        REV-002: Revision lineages form linear chains
        REV-003: Revisions are ordered within their lineage
        
    PARAMETERS:
        value         - The actual UUID string
        version_id    - ID of the version containing this revision
        revision_num  - Revision number within the version
    """
    
    value: str = field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:20]}")
    version_id: Optional[str] = None
    revision_num: int = 1
    
    @classmethod
    def generate(cls, version_id: Optional[str] = None) -> "RevisionLineageId":
        """Generate a revision lineage ID."""
        return cls(version_id=version_id)
    
    @property
    def is_initial_revision(self) -> bool:
        """Check if this is the initial revision (r1)."""
        return self.revision_num == 1


# =============================================================================
# LINEAGE REGISTRY
# =============================================================================


class LineageRegistry:
    """
    Registry for tracking lineage relationships.
    
    Provides utilities for managing lineage traces, derivations,
    and transformations.
    
    INVARIANTS:
        LR-001: Lineage forms a DAG (no cycles)
        LR-002: Each artifact has exactly one complete lineage
        LR-003: Derivations link source to target artifacts
        
    METHODS:
        track_lineage()     - Register an artifact's lineage
        add_derivation()    - Register derivation relationship
        add_transformation()- Register transformation operation
        get_lineage()       - Get full lineage trace for an artifact
        get_derivations()   - Get all derivations of an artifact
    """
    
    def __init__(self):
        self._lineages: dict[str, LineageId] = {}  # artifact_id -> lineage_id
        self._derivations: list[DerivationId] = []
        self._transformations: list[TransformationId] = []
        self._version_lineages: dict[str, VersionLineageId] = {}
    
    def track_lineage(
        self,
        artifact_id: str,
        lineage_id: LineageId,
    ) -> None:
        """Register an artifact's lineage."""
        self._lineages[artifact_id] = lineage_id
    
    def add_derivation(self, derivation: DerivationId) -> bool:
        """Add a derivation relationship. Returns False if duplicate."""
        for d in self._derivations:
            if d.value == derivation.value:
                return False
        self._derivations.append(derivation)
        return True
    
    def add_transformation(
        self,
        transformation: TransformationId,
    ) -> bool:
        """Add a transformation operation. Returns False if duplicate."""
        for t in self._transformations:
            if t.value == transformation.value:
                return False
        self._transformations.append(transformation)
        return True
    
    def get_lineage(self, artifact_id: str) -> Optional[LineageId]:
        """Get the lineage ID for an artifact."""
        return self._lineages.get(artifact_id)
    
    def get_derivations(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> list[DerivationId]:
        """Get derivations, optionally filtered by source or target."""
        results = self._derivations
        if source_id:
            results = [d for d in results if d.source_id == source_id]
        if target_id:
            results = [d for d in results if d.target_id == target_id]
        return results
    
    def get_transformation(self, input_id: str) -> Optional[TransformationId]:
        """Get the transformation that produced a given output."""
        for t in self._transformations:
            if input_id in t.input_ids:
                return t
        return None


__all__ = [
    "LineageId",
    "DerivationId",
    "TransformationId",
    "VersionLineageId",
    "RevisionLineageId",
    "LineageRegistry",
]