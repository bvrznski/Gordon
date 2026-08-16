# Canonical Belief Revision Models - Phase 4.9.5
# ================================================
"""
Immutable model definitions for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final
from uuid import UUID


# =============================================================================
# SEMANTIC IDENTITIES (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticIdentity:
    """
    Immutable semantic identity with stable equality.
    
    Rules:
        - Empty identities are rejected at construction
        - Identities must be deterministically unique within scope
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("SemanticIdentity must have a non-empty string value")
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SemanticIdentity):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return f"SemanticIdentity({self.value})"


@dataclass(frozen=True, slots=True)
class BeliefIdentity(SemanticIdentity):
    """Identity for a belief."""
    pass


# =============================================================================
# VERSION TRACKING (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Revision:
    """
    Immutable revision tracking with semantic versioning.
    
    Rules:
        - Major, minor, patch must be non-negative integers
        - Build metadata and pre-release are optional strings
    """
    major: int = 1
    minor: int = 0
    patch: int = 0
    build_metadata: str | None = None
    prerelease: str | None = None
    
    def __post_init__(self) -> None:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("Revision components must be non-negative")
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version


# =============================================================================
# PROVENANCE TRACKING (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Provenance:
    """
    Immutable provenance tracking for beliefs.
    
    Fields:
        source_identity:       Source of the belief
        timestamp_ref:         Semantic time reference (not wall-clock)
        author:                Author or originator reference
        context_ref:           Context in which the belief was formed
    """
    source_identity: str | None = None
    timestamp_ref: str | None = None  # External semantic time reference
    author: str | None = None
    context_ref: str | None = None


# =============================================================================
# CANONICAL BELIEF MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Belief:
    """
    Canonical immutable belief model.
    
    Fields:
        identity:               Unique belief identity
        semantic_content:       The actual content/meaning of the belief
        confidence:             Confidence value [0.0, 1.0]
        uncertainty:            Uncertainty decomposition
        hierarchy_level:        Belief hierarchy level (sensory/contextual/conceptual/abstract)
        supporting_evidence:    Supporting evidence references
        revision_history:       Immutable history of revisions
        provenance:             Provenance tracking
        revision_number:        Current revision number
    
    Rules:
        - Beliefs are deeply immutable
        - Identity remains stable across revisions
        - No belief modification; only new revisions created
    """
    identity: str  # BeliefIdentity or string code
    semantic_content: dict[str, Any]
    confidence: float = 0.5
    uncertainty: dict[str, Any] = field(default_factory=dict)
    hierarchy_level: str = "contextual"  # BeliefHierarchyLevel or string code
    supporting_evidence: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    revision_history: tuple[Revision, ...] = field(default_factory=lambda: (Revision(major=1),))
    provenance: Provenance | None = None
    revision_number: int = 1
    
    def __post_init__(self) -> None:
        if not isinstance(self.confidence, (int, float)) or self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Belief confidence must be a value between 0.0 and 1.0")
        if self.revision_number < 1:
            raise ValueError("Belief revision number must be at least 1")


# =============================================================================
# BELIEF STATE (CANONICAL AGGREGATE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class BeliefState:
    """
    Canonical immutable belief state aggregate.
    
    Fields:
        beliefs:                Collection of all beliefs
        hierarchy:              Hierarchical organization
        dependencies:           Dependency graph
        confidence:             Overall confidence in the state
        uncertainty:            Overall uncertainty decomposition
        revision_graph:         Immutable revision lineage
        trace:                  Structural trace of state construction
    
    Rules:
        - Exactly one canonical BeliefState exists at any time
        - Immutable aggregate
        - Revision creates new BeliefState, doesn't modify existing
    """
    beliefs: tuple[Belief, ...] = field(default_factory=tuple)
    hierarchy: dict[str, Any] | None = None  # Hierarchical organization
    dependencies: dict[str, Any] | None = None  # DependencyGraph representation
    confidence: float = 0.5
    uncertainty: dict[str, Any] = field(default_factory=dict)
    revision_graph: dict[str, Any] | None = None  # BeliefRevisionGraph representation
    trace: tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# PRECISION LANDSCAPE REFERENCE (EXTERNAL SUPPLY)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PrecisionLandscapeReference:
    """
    Reference to a precision landscape (external supply).
    
    Rules:
        - Precision authority is external
        - No ownership transfer via reference
    """
    identity: str  # SemanticIdentity or string code
    estimates: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    hierarchy: dict[str, float] | None = None


# =============================================================================
# CONTEXT PROJECTION (EXTERNAL SUPPLY)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ContextProjection:
    """
    External context projection for revision evaluation.
    
    Fields:
        identity:           Semantic identity of context
        temporal_ref:       Temporal reference (semantic time)
        spatial_ref:        Spatial reference
        semantic_ref:       Semantic context reference
        world_state:        Current world state representation
    """
    identity: str  # SemanticIdentity or string code
    temporal_ref: str | None = None
    spatial_ref: str | None = None
    semantic_ref: str | None = None
    world_state: dict[str, Any] | None = None


# =============================================================================
# WORLD MODEL PROJECTION (EXTERNAL SUPPLY)
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorldModelProjection:
    """
    External world model projection for revision evaluation.
    
    Fields:
        identity:           Semantic identity of world model
        entities:           World entity references
        relationships:      Entity relationship graph
        ontology:           Ontological framework
    """
    identity: str  # SemanticIdentity or string code
    entities: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    relationships: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    ontology: dict[str, Any] | None = None


# =============================================================================
# SEMANTIC TIME REFERENCE (EXTERNAL SUPPLY)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticTime:
    """
    External semantic time reference for revision.
    
    Rules:
        - Time is supplied externally
        - No wall-clock acquisition in this module
    """
    identity: str  # SemanticIdentity or string code
    timestamp_ref: str | None = None


# =============================================================================
# FAILURE RECORD (TYPED FINDINGS)
# =============================================================================

@dataclass(frozen=True, slots=True)
class FailureRecord:
    """
    Typed failure record for revision findings.
    
    Fields:
        kind:               Failure category
        description:        Human-readable description
        context:            Context where failure occurred
        timestamp_ref:      Semantic time reference
    """
    kind: str  # FailureKind or string code
    description: str
    context: dict[str, Any] | None = None
    timestamp_ref: str | None = None


# =============================================================================
# CANONICAL SERIALIZATION ENVELOPE (DETERMINISTIC)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SerializationEnvelope:
    """
    Immutable serialization envelope for deterministic serialization.
    
    Fields:
        schema:           Schema identifier
        schema_version:   Schema version string
        kind:             Concrete type discriminator
        payload:          Serialized content (deterministic format)
        provenance:       Optional provenance metadata
    """
    schema: str
    schema_version: str
    kind: str
    payload: dict[str, Any]
    provenance: Provenance | None = None
    
    def __post_init__(self) -> None:
        if not self.schema or not isinstance(self.schema, str):
            raise ValueError("SerializationEnvelope schema must be non-empty")
        if not self.schema_version or not isinstance(self.schema_version, str):
            raise ValueError("SerializationEnvelope schema_version must be non-empty")
        if not self.kind or not isinstance(self.kind, str):
            raise ValueError("SerializationEnvelope kind must be non-empty")


# =============================================================================
# CANONICAL SCHEMA CONSTANTS
# =============================================================================

CANONICAL_SCHEMA_PREFIX: Final[str] = "gordon.belief_revision"
DEFAULT_SCHEMA_VERSION: Final[str] = "1.0.0"