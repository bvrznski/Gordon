# Knowledge Concepts - Contracts - Phase 6.3
# ===========================================

"""
Concept Contracts for Gordon's Concept Subsystem.

This module defines the canonical contracts that govern concept identity,
instances, properties, prototypes, and their relationships.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# CONCEPT IDENTITY - Immutable semantic identity
# =============================================================================


@dataclass(frozen=True)
class ConceptIdentity:
    """
    Unique identifier for a concept.
    
    Concept identity is immutable and persists across revisions.
    Every concept must have exactly one unique semantic identity.
    
    Fields:
        identity:   Unique semantic identity string
        version:    Version number of this revision
        created_at: When the concept was first created
        provenance: Origin tracking information
    """
    identity: str
    version: int = 1
    created_at: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "version": self.version,
            "created_at": self.created_at,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def create(cls, name: str) -> ConceptIdentity:
        """Create a new identity for a concept."""
        return cls(
            identity=f"concept:{uuid.uuid4().hex[:16]}",
            version=1,
            created_at=time.time(),
            provenance={"name": name},
        )


# =============================================================================
# CONCEPT - Canonical concept structure
# =============================================================================


@dataclass(frozen=True)
class Concept:
    """
    Canonical representation of a semantic category.
    
    Concepts are abstract, timeless categories that organize meaning.
    They do not represent observations or instances - they define what
    kinds of things exist and how they relate.
    
    Fields:
        identity:         Unique immutable semantic identity
        canonical_name:   Primary name for this concept
        aliases:          Alternative names
        description:      Semantic definition
        properties:       Key defining properties
        parent_ids:       Generalization relationships (IS_A)
        child_ids:        Specialization relationships (IS_A)
        ontologies:       Ontology memberships
        abstraction_level: Position in hierarchy (0=most abstract)
        confidence:       Semantic confidence (0.0-1.0)
        revision:         Revision number for traceability
        provenance:       Origin tracking with timestamps and sources
    """
    identity: str
    canonical_name: str
    aliases: Tuple[str, ...] = field(default_factory=tuple)
    description: str = ""
    properties: Tuple[str, ...] = field(default_factory=tuple)
    parent_ids: Tuple[str, ...] = field(default_factory=tuple)
    child_ids: Tuple[str, ...] = field(default_factory=tuple)
    ontologies: Tuple[str, ...] = field(default_factory=tuple)
    abstraction_level: int = 0
    confidence: float = 0.5
    revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if concept has minimal required data."""
        return (
            len(self.identity) > 0 and
            len(self.canonical_name) > 0
        )

    @property
    def root_concepts(self) -> Tuple[str, ...]:
        """Get all root concepts (no parent relationships)."""
        roots = []
        for parent_id in self.parent_ids:
            if parent_id not in [c for c in self.child_ids]:
                roots.append(parent_id)
        return tuple(roots)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "canonical_name": self.canonical_name,
            "aliases": list(self.aliases),
            "description": self.description,
            "properties": list(self.properties),
            "parent_ids": list(self.parent_ids),
            "child_ids": list(self.child_ids),
            "ontologies": list(self.ontologies),
            "abstraction_level": self.abstraction_level,
            "confidence": self.confidence,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Concept:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            canonical_name=data.get("canonical_name", ""),
            aliases=tuple(data.get("aliases", [])),
            description=data.get("description", ""),
            properties=tuple(data.get("properties", [])),
            parent_ids=tuple(data.get("parent_ids", [])),
            child_ids=tuple(data.get("child_ids", [])),
            ontologies=tuple(data.get("ontologies", [])),
            abstraction_level=int(data.get("abstraction_level", 0)),
            confidence=float(data.get("confidence", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT INSTANCE - Concrete entity realization
# =============================================================================


@dataclass(frozen=True)
class ConceptInstance:
    """
    A concrete instance of a concept.
    
    Instances are specific realizations observed in the world. Multiple
    instances may belong to a single concept.
    
    Fields:
        identity:         Unique identifier for this instance
        concept_ids:      IDs of concepts this instance belongs to
        name:             Instance-specific name (if any)
        properties:       Observed property values
        temporal_scope:   When observed (start, end timestamps)
        spatial_scope:    Where observed (location data)
        confidence:       Classification confidence (0.0-1.0)
        revision:         Revision number for traceability
        provenance:       Origin tracking with observations and sources
    """
    identity: str
    concept_ids: Tuple[str, ...]
    name: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    temporal_scope: Tuple[float, float] = field(default_factory=lambda: (time.time(), time.time()))
    spatial_scope: Optional[Dict[str, Any]] = None
    confidence: float = 0.5
    revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if instance has minimal required data."""
        return len(self.identity) > 0 and len(self.concept_ids) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "concept_ids": list(self.concept_ids),
            "name": self.name,
            "properties": dict(self.properties),
            "temporal_scope": list(self.temporal_scope),
            "spatial_scope": self.spatial_scope,
            "confidence": self.confidence,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptInstance:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            concept_ids=tuple(data.get("concept_ids", [])),
            name=data.get("name", ""),
            properties=dict(data.get("properties", {})),
            temporal_scope=tuple(data.get("temporal_scope", [time.time(), time.time()])),
            spatial_scope=data.get("spatial_scope"),
            confidence=float(data.get("confidence", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT CLASSIFICATION - Instance to concept assignment
# =============================================================================


class ClassificationKind(Enum):
    """Kinds of classification outcomes."""
    EXACT = "exact"          # Perfect match
    PARTIAL = "partial"      # Partial match
    MULTIPLE = "multiple"    # Matches multiple concepts
    UNKNOWN = "unknown"      # Cannot classify


@dataclass(frozen=True)
class ConceptClassification:
    """
    Classification result for an instance.
    
    Classifications propose concept assignments based on observed features.
    Multiple candidates may be proposed with supporting evidence.
    
    Fields:
        identity:           Unique classification ID
        instance_id:        The instance being classified
        candidate_concepts: Proposed concept IDs with scores
        classification_kind: EXACT, PARTIAL, MULTIPLE, or UNKNOWN
        supporting_features: Features that support the classification
        confidence:         Classification confidence (0.0-1.0)
        uncertainty:        Remaining uncertainty (0.0-1.0)
        alternative_concepts: Competing hypotheses
        provenance:         Evidence source and reasoning trail
    """
    identity: str
    instance_id: str
    candidate_concepts: Tuple[Tuple[str, float], ...]
    classification_kind: ClassificationKind
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.5
    uncertainty: float = 0.5
    alternative_concepts: Tuple[str, ...] = field(default_factory=tuple)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def top_classification(self) -> Optional[Tuple[str, float]]:
        """Get the best classification candidate."""
        if not self.candidate_concepts:
            return None
        return max(self.candidate_concepts, key=lambda x: x[1])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "instance_id": self.instance_id,
            "candidate_concepts": [list(c) for c in self.candidate_concepts],
            "classification_kind": self.classification_kind.value,
            "supporting_features": list(self.supporting_features),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "alternative_concepts": list(self.alternative_concepts),
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptClassification:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            instance_id=data.get("instance_id", ""),
            candidate_concepts=tuple(tuple(c) for c in data.get("candidate_concepts", [])),
            classification_kind=ClassificationKind(data.get("classification_kind", "unknown")),
            supporting_features=tuple(data.get("supporting_features", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            alternative_concepts=tuple(data.get("alternative_concepts", [])),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT PROPERTY - Semantic property definition
# =============================================================================


class PropertyKind(Enum):
    """Kinds of concept properties."""
    STRUCTURAL = "structural"      # Inherent structure
    FUNCTIONAL = "functional"      # Capabilities and functions
    BEHAVIORAL = "behavioral"      # Typical behaviors
    TEMPORAL = "temporal"          # Time-related properties
    SPATIAL = "spatial"            # Location/extension
    SOCIAL = "social"              # Social relations
    PROCEDURAL = "procedural"      # Process-related
    QUANTITATIVE = "quantitative"  # Numerical values
    QUALITATIVE = "qualitative"    # Descriptive attributes


@dataclass(frozen=True)
class ConceptProperty:
    """
    A semantic property of a concept.
    
    Properties describe what concepts are and do. Instances provide values
    for these properties.
    
    Fields:
        identity:         Unique property ID
        concept_id:       The concept this property belongs to
        name:             Property name
        kind:             Property category (structural, functional, etc.)
        default_value:    Default value if not specified
        constraints:      Constraints on allowed values
        inherited:        Whether this is inherited from a parent
        overridden_by:    If overridden, the overriding concept ID
        provenance:       Origin tracking with property definitions
    """
    identity: str
    concept_id: str
    name: str
    kind: PropertyKind
    default_value: Optional[Any] = None
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    inherited: bool = False
    overridden_by: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "concept_id": self.concept_id,
            "name": self.name,
            "kind": self.kind.value,
            "default_value": self.default_value,
            "constraints": list(self.constraints),
            "inherited": self.inherited,
            "overridden_by": self.overridden_by,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptProperty:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            concept_id=data.get("concept_id", ""),
            name=data.get("name", ""),
            kind=PropertyKind(data.get("kind", "structural")),
            default_value=data.get("default_value"),
            constraints=tuple(data.get("constraints", [])),
            inherited=bool(data.get("inherited", False)),
            overridden_by=data.get("overridden_by"),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT PROTOTYPE - Representative semantic structure
# =============================================================================


@dataclass(frozen=True)
class ConceptPrototype:
    """
    A prototype for a concept.
    
    Prototypes represent typical or canonical members of a concept category.
    They are not specific instances but representative structures.
    
    Fields:
        identity:           Unique prototype ID
        concept_id:         The concept this is a prototype for
        defining_properties: Properties that must be present
        optional_properties: Properties that may be present
        excluded_properties: Properties that cannot be present
        confidence:         Prototype validity (0.0-1.0)
        uncertainty:        Remaining uncertainty
        provenance:         Construction evidence and reasoning
    """
    identity: str
    concept_id: str
    defining_properties: Tuple[str, ...]
    optional_properties: Tuple[str, ...] = field(default_factory=tuple)
    excluded_properties: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.5
    uncertainty: float = 0.5
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if prototype has valid data."""
        return len(self.identity) > 0 and len(self.concept_id) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "concept_id": self.concept_id,
            "defining_properties": list(self.defining_properties),
            "optional_properties": list(self.optional_properties),
            "excluded_properties": list(self.excluded_properties),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptPrototype:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            concept_id=data.get("concept_id", ""),
            defining_properties=tuple(data.get("defining_properties", [])),
            optional_properties=tuple(data.get("optional_properties", [])),
            excluded_properties=tuple(data.get("excluded_properties", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT ABSTRACTION - Removing detail to increase generality
# =============================================================================


@dataclass(frozen=True)
class ConceptAbstraction:
    """
    Abstraction operation on concepts.
    
    Abstraction removes unnecessary detail to create more general concepts.
    Examples: Golden Retriever -> Dog -> Mammal -> Animal
    
    Fields:
        identity:         Unique abstraction ID
        source_concepts:  Concepts being abstracted
        result_concept:   The resulting abstract concept
        abstraction_basis: What was abstracted (properties, relations, etc.)
        preserved_properties: Properties retained in abstraction
        removed_properties: Details removed for generality
        confidence:       Abstraction validity (0.0-1.0)
        provenance:       Evidence and reasoning trail
    """
    identity: str
    source_concepts: Tuple[str, ...]
    result_concept: str
    abstraction_basis: str
    preserved_properties: Tuple[str, ...] = field(default_factory=tuple)
    removed_properties: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.5
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if abstraction has valid data."""
        return (
            len(self.identity) > 0 and
            len(self.source_concepts) > 0 and
            len(self.result_concept) > 0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "source_concepts": list(self.source_concepts),
            "result_concept": self.result_concept,
            "abstraction_basis": self.abstraction_basis,
            "preserved_properties": list(self.preserved_properties),
            "removed_properties": list(self.removed_properties),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptAbstraction:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            source_concepts=tuple(data.get("source_concepts", [])),
            result_concept=data.get("result_concept", ""),
            abstraction_basis=data.get("abstraction_basis", ""),
            preserved_properties=tuple(data.get("preserved_properties", [])),
            removed_properties=tuple(data.get("removed_properties", [])),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT SPECIALIZATION - Adding constraints for specificity
# =============================================================================


@dataclass(frozen=True)
class ConceptSpecialization:
    """
    Specialization operation on concepts.
    
    Specialization adds constraints to create more specific concepts.
    Examples: Animal -> Mammal -> Dog -> Golden Retriever
    
    Fields:
        identity:           Unique specialization ID
        parent_concept_id:  The parent concept being specialized
        specialized_concept: The resulting specialized concept
        distinguishing_properties: New properties that distinguish the specialization
        inherited_properties: Properties from parent (for traceability)
        confidence:         Specialization validity (0.0-1.0)
        provenance:         Evidence and reasoning trail
    """
    identity: str
    parent_concept_id: str
    specialized_concept: str
    distinguishing_properties: Tuple[str, ...] = field(default_factory=tuple)
    inherited_properties: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.5
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if specialization has valid data."""
        return (
            len(self.identity) > 0 and
            len(self.parent_concept_id) > 0 and
            len(self.specialized_concept) > 0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "parent_concept_id": self.parent_concept_id,
            "specialized_concept": self.specialized_concept,
            "distinguishing_properties": list(self.distinguishing_properties),
            "inherited_properties": list(self.inherited_properties),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptSpecialization:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            parent_concept_id=data.get("parent_concept_id", ""),
            specialized_concept=data.get("specialized_concept", ""),
            distinguishing_properties=tuple(data.get("distinguishing_properties", [])),
            inherited_properties=tuple(data.get("inherited_properties", [])),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT GENERALIZATION - Identifying common structure
# =============================================================================


@dataclass(frozen=True)
class ConceptGeneralization:
    """
    Generalization operation on concepts.
    
    Generalization identifies common structure among multiple concepts
    to form a more general concept.
    
    Fields:
        identity:           Unique generalization ID
        source_concepts:    Concepts being generalized
        generalized_concept: The resulting general concept
        shared_properties:  Properties shared by all sources
        confidence:         Generalization validity (0.0-1.0)
        provenance:         Evidence and reasoning trail
    """
    identity: str
    source_concepts: Tuple[str, ...]
    generalized_concept: str
    shared_properties: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.5
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if generalization has valid data."""
        return (
            len(self.identity) > 0 and
            len(self.source_concepts) > 0 and
            len(self.generalized_concept) > 0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "source_concepts": list(self.source_concepts),
            "generalized_concept": self.generalized_concept,
            "shared_properties": list(self.shared_properties),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptGeneralization:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            source_concepts=tuple(data.get("source_concepts", [])),
            generalized_concept=data.get("generalized_concept", ""),
            shared_properties=tuple(data.get("shared_properties", [])),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONCEPT CATEGORY - Organizing related concepts
# =============================================================================


@dataclass(frozen=True)
class ConceptCategory:
    """
    A category organizing related concepts.
    
    Categories improve semantic organization by grouping related concepts.
    Examples: Living Things, Software, Processes, Geometry, Programming Languages
    
    Fields:
        identity:         Unique category ID
        category_name:    Name of the category
        member_concepts:  IDs of concepts in this category
        parent_category:  Parent category (for hierarchy)
        ontology:         Ontology membership
        provenance:       Origin tracking with timestamps and sources
    """
    identity: str
    category_name: str
    member_concepts: Tuple[str, ...] = field(default_factory=tuple)
    parent_category: Optional[str] = None
    ontology: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if category has valid data."""
        return len(self.identity) > 0 and len(self.category_name) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "category_name": self.category_name,
            "member_concepts": list(self.member_concepts),
            "parent_category": self.parent_category,
            "ontology": self.ontology,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConceptCategory:
        return cls(
            identity=data.get("identity", str(uuid.uuid4())),
            category
