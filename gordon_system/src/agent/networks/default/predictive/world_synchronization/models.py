# Canonical World Synchronization Models - Phase 4.9.6
# =======================================================
"""
Immutable model definitions for WorldModelSynchronization subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final
from enum import Enum


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
class WorldModelIdentity(SemanticIdentity):
    """Identity for a world model."""
    pass


@dataclass(frozen=True, slots=True)
class EntityIdentity(SemanticIdentity):
    """Identity for an entity."""
    pass


@dataclass(frozen=True, slots=True)
class RelationshipIdentity(SemanticIdentity):
    """Identity for a relationship."""
    pass


@dataclass(frozen=True, slots=True)
class OntologyIdentity(SemanticIdentity):
    """Identity for an ontology concept."""
    pass


@dataclass(frozen=True, slots=True)
class ContextIdentity(SemanticIdentity):
    """Identity for a context partition."""
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
    Immutable provenance tracking for world model elements.
    
    Fields:
        source_identity:       Source of the world element
        timestamp_ref:         Semantic time reference (not wall-clock)
        author:                Author or originator reference
        context_ref:           Context in which the element was formed
    """
    source_identity: str | None = None
    timestamp_ref: str | None = None  # External semantic time reference
    author: str | None = None
    context_ref: str | None = None


# =============================================================================
# SEMANTIC TIME REFERENCE (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticTime:
    """
    External semantic time reference for world model operations.
    
    Rules:
        - Time is supplied externally
        - No wall-clock acquisition in this module
    """
    identity: str  # SemanticIdentity or string code
    timestamp_ref: str | None = None


# =============================================================================
# ATTRIBUTE MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Attribute:
    """
    Immutable attribute key-value pair.
    
    Fields:
        name:         Attribute name/identifier
        value:        Attribute value (any JSON-serializable type)
        confidence:   Confidence in the attribute [0.0, 1.0]
        provenance:   Source of this attribute
    
    Rules:
        - Attributes are deeply immutable
        - No attribute modification; only new versions created
    """
    name: str
    value: Any
    confidence: float = 1.0
    provenance: Provenance | None = None
    
    def __post_init__(self) -> None:
        if not isinstance(self.confidence, (int, float)) or self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Attribute confidence must be a value between 0.0 and 1.0")


# =============================================================================
# ENTITY MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Entity:
    """
    Canonical immutable entity model.
    
    Fields:
        identity:          Unique entity identity
        attributes:        Collection of attribute key-value pairs
        relationships:     Related entities by relationship type
        revision_number:   Current revision number
        provenance:        Provenance tracking
        lifecycle_status:  Entity lifecycle state (CREATE/UPDATE/DEPRECATE/etc.)
    
    Rules:
        - Entities are deeply immutable
        - Identity remains stable across revisions
        - No entity modification; only new revisions created
    """
    identity: str  # EntityIdentity or string code
    attributes: tuple[Attribute, ...] = field(default_factory=tuple)
    relationships: tuple[str, ...] = field(default_factory=tuple)  # Relationship IDs
    revision_number: int = 1
    provenance: Provenance | None = None
    lifecycle_status: str = "ACTIVE"  # Active lifecycle status
    
    def __post_init__(self) -> None:
        if self.revision_number < 1:
            raise ValueError("Entity revision number must be at least 1")


# =============================================================================
# RELATIONSHIP MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Relationship:
    """
    Canonical immutable relationship model.
    
    Fields:
        identity:          Unique relationship identity
        source_entity:     Source entity identity
        target_entity:     Target entity identity
        relationship_type: Type of semantic relation
        attributes:        Additional relationship attributes
        revision_number:   Current revision number
        provenance:        Provenance tracking
    
    Rules:
        - Relationships are deeply immutable
        - Endpoints reference valid entities
        - No relationship modification; only new revisions created
    """
    identity: str  # RelationshipIdentity or string code
    source_entity: str  # EntityIdentity of source
    target_entity: str  # EntityIdentity of target
    relationship_type: str  # RelationshipType enum value
    attributes: tuple[Attribute, ...] = field(default_factory=tuple)
    revision_number: int = 1
    provenance: Provenance | None = None
    
    def __post_init__(self) -> None:
        if self.revision_number < 1:
            raise ValueError("Relationship revision number must be at least 1")


# =============================================================================
# ONTOLOGY CONCEPT MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class OntologyConcept:
    """
    Canonical immutable ontology concept model.
    
    Fields:
        identity:          Unique concept identity
        name:              Concept name/label
        description:       Concept description
        parent_concepts:   Parent concepts (inheritance hierarchy)
        child_concepts:    Child concepts (specializations)
        attributes:        Concept metadata and constraints
        revision_number:   Current revision number
        provenance:        Provenance tracking
    
    Rules:
        - Concepts are deeply immutable
        - Identity remains stable across evolution
        - Hierarchy must remain acyclic
    """
    identity: str  # OntologyIdentity or string code
    name: str
    description: str = ""
    parent_concepts: tuple[str, ...] = field(default_factory=tuple)
    child_concepts: tuple[str, ...] = field(default_factory=tuple)
    attributes: tuple[Attribute, ...] = field(default_factory=tuple)
    revision_number: int = 1
    provenance: Provenance | None = None
    
    def __post_init__(self) -> None:
        if self.revision_number < 1:
            raise ValueError("OntologyConcept revision number must be at least 1")


# =============================================================================
# CONTEXT MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Context:
    """
    Canonical immutable context partition model.
    
    Fields:
        identity:          Context partition identity
        context_type:      Type of context (task/conversation/environment/etc.)
        entities:          Entities in this context
        relationships:     Relationships active in this context
        temporal_extent:   Temporal bounds (semantic time)
        provenance:        Provenance tracking
    
    Rules:
        - Contexts remain independent
        - No cross-context inference
        - Explicit context boundaries preserved
    """
    identity: str  # ContextIdentity or string code
    context_type: str  # ContextType enum value
    entities: tuple[str, ...] = field(default_factory=tuple)
    relationships: tuple[str, ...] = field(default_factory=tuple)
    temporal_extent: tuple[str, str] | None = None  # (start_ref, end_ref)
    provenance: Provenance | None = None


# =============================================================================
# GRAPH NODE MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class GraphNode:
    """
    Canonical immutable graph node model.
    
    Fields:
        node_id:           Unique node identifier
        entity_ref:        Reference to entity (if any)
        attributes:        Node metadata and labels
        contexts:          Contexts this node belongs to
    
    Rules:
        - Nodes are deeply immutable
        - Node IDs remain stable across graph revisions
    """
    node_id: str
    entity_ref: str | None = None  # EntityIdentity reference
    attributes: tuple[Attribute, ...] = field(default_factory=tuple)
    contexts: tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# GRAPH EDGE MODEL (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class GraphEdge:
    """
    Canonical immutable graph edge model.
    
    Fields:
        edge_id:           Unique edge identifier
        source_node:       Source node ID
        target_node:       Target node ID
        relationship_type: Edge semantic type
        attributes:        Edge metadata
    
    Rules:
        - Edges are deeply immutable
        - Endpoints reference valid nodes
        - No duplicate edges between same nodes with same type
    """
    edge_id: str
    source_node: str
    target_node: str
    relationship_type: str  # RelationshipType enum value
    attributes: tuple[Attribute, ...] = field(default_factory=tuple)


# =============================================================================
# FAILURE RECORD (TYPED FINDINGS)
# =============================================================================

@dataclass(frozen=True, slots=True)
class FailureRecord:
    """
    Typed failure record for world synchronization findings.
    
    Fields:
        kind:               Failure category
        description:        Human-readable description
        context:            Context where failure occurred
        timestamp_ref:      Semantic time reference
    
    Rules:
        - Failures are typed and actionable
        - No silent failures allowed
    """
    kind: str  # FailureKind enum value
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
    
    Rules:
        - Deterministic encoding required
        - No runtime-dependent data in payload
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

CANONICAL_SCHEMA_PREFIX: Final[str] = "gordon.world_synchronization"
DEFAULT_SCHEMA_VERSION: Final[str] = "1.0.0"