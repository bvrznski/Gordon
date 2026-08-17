# Knowledge Model - Phase 5.4
# ===========================

"""
Knowledge Model: Coherent semantic representations organizing multiple concepts.

Models organize domain knowledge by structuring related concepts and their
relations into unified semantic representations. Examples include Filesystem,
Python Runtime, Compiler, Conversation, Operating System.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# MODEL SCOPE - Domain coverage
# =============================================================================


class ModelScope(Enum):
    """
    Scope of a semantic model.
    
    Defines the breadth and depth of domain coverage for a model.
    """
    
    NARROW = "narrow"               # Limited, focused scope
    BROAD = "broad"                 # Wide scope with many concepts
    DOMAIN_SPECIFIC = "domain_specific"  # Specialized to one domain
    CROSS_DOMAIN = "cross_domain"   # Integrates multiple domains


# =============================================================================
# MODEL MODEL - Canonical model structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeModel:
    """
    Canonical representation of a semantic model in Gordon's knowledge system.
    
    A model organizes multiple concepts into a coherent representation of
    a domain or concept. Models preserve their boundaries, limitations,
    and revision history.
    
    Fields:
        model_identity:        Unique identifier for this model
        concepts:              Concept IDs included in this model
        relations:             Relations between concepts in the model
        scope:                 Domain coverage of this model
        limitations:           Known limitations of this model
        confidence:            Semantic confidence in this model (0.0-1.0)
        uncertainty:           Semantic uncertainty about this model
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    model_identity: str               # Unique ID for this model
    
    # Domain content
    concepts: Tuple[str, ...] = field(default_factory=tuple)  # Concept IDs
    relations: Tuple[Tuple[str, str, str], ...] = field(default_factory=tuple)  # (source, target, kind)
    
    # Scope and boundaries
    name: str = ""
    domain: str = "general"
    scope: ModelScope = ModelScope.BROAD
    
    # Limitations and constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Quality metrics (required)
    confidence: float = 0.5           # Semantic confidence (0.0-1.0)
    uncertainty: float = 0.5          # Semantic uncertainty (0.0-1.0)
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if model has minimal required data."""
        return (
            len(self.model_identity) > 0 and
            self.scope is not None
        )
    
    @property
    def concept_count(self) -> int:
        """Get the number of concepts in this model."""
        return len(self.concepts)
    
    @property
    def relation_count(self) -> bool:
        """Get the number of relations in this model."""
        return len(self.relations)
    
    def get_concept_relations(
        self,
        concept_id: str,
    ) -> Tuple[Tuple[str, str], ...]:
        """
        Get all relations involving a specific concept.
        
        Args:
            concept_id: The concept ID to query
            
        Returns:
            Tuples of (target_id, relation_kind) for all relations
        """
        relations = []
        for source, target, kind in self.relations:
            if source == concept_id:
                relations.append((target, kind))
            elif target == concept_id:
                # Invert direction for incoming relations
                relations.append((source, kind))
        return tuple(relations)
    
    def has_concept(self, concept_id: str) -> bool:
        """Check if a concept is included in this model."""
        return concept_id in self.concepts
    
    @classmethod
    def create(
        cls,
        name: str = "",
        domain: str = "general",
        concepts: Optional[List[str]] = None,
        relations: Optional[List[Tuple[str, str, str]]] = None,
        limitations: Optional[List[str]] = None,
        scope: ModelScope = ModelScope.BROAD,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeModel":
        """
        Create a new model.
        
        Args:
            name: Human-readable name (optional)
            domain: Domain context (e.g., "filesystem", "runtime")
            concepts: Concept IDs included (optional)
            relations: Relations between concepts as (source, target, kind) tuples
            limitations: Known limitations (optional)
            scope: Model scope
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            provenance: Origin tracking data (optional)
        """
        return cls(
            model_identity=f"model:{uuid.uuid4().hex[:16]}",
            name=name,
            domain=domain,
            concepts=tuple(concepts or []),
            relations=tuple(relations or []),
            scope=scope,
            limitations=tuple(limitations or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for serialization."""
        return {
            "model_identity": self.model_identity,
            "name": self.name,
            "domain": self.domain,
            "concepts": list(self.concepts),
            "relations": [list(r) for r in self.relations],
            "scope": self.scope.value if self.scope else None,
            "limitations": list(self.limitations),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeModel":
        """Create model from dictionary."""
        scope_value = data.get("scope", "broad")
        try:
            scope = ModelScope(scope_value)
        except ValueError:
            scope = ModelScope.BROAD
        
        return cls(
            model_identity=data.get("model_identity", str(uuid.uuid4())),
            name=data.get("name", ""),
            domain=data.get("domain", "general"),
            concepts=tuple(data.get("concepts", [])),
            relations=tuple(tuple(r) for r in data.get("relations", [])),
            scope=scope,
            limitations=tuple(data.get("limitations", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )
    
    def add_concept(
        self,
        concept_id: str,
    ) -> "KnowledgeModel":
        """Create a revision with an additional concept."""
        if concept_id in self.concepts:
            return self
        
        return KnowledgeModel(
            model_identity=self.model_identity,
            name=self.name,
            domain=self.domain,
            concepts=self.concepts + (concept_id,),
            relations=self.relations,
            scope=self.scope,
            limitations=self.limitations,
            confidence=self.confidence * 0.98,  # Slight decrease for new uncertainty
            uncertainty=self.uncertainty * 1.02,
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "concept_added": concept_id,
                "revised_at_utc": time.time(),
            },
        )
    
    def add_relation(
        self,
        source: str,
        target: str,
        relation_kind: str,
    ) -> "KnowledgeModel":
        """Create a revision with an additional relation."""
        new_relation = (source, target, relation_kind)
        if new_relation in self.relations:
            return self
        
        return KnowledgeModel(
            model_identity=self.model_identity,
            name=self.name,
            domain=self.domain,
            concepts=self.concepts,
            relations=self.relations + (new_relation,),
            scope=self.scope,
            limitations=self.limitations,
            confidence=min(1.0, self.confidence * 1.02),  # Slight increase
            uncertainty=max(0.0, self.uncertainty * 0.98),
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "relation_added": new_relation,
                "revised_at_utc": time.time(),
            },
        )


# =============================================================================
# MODEL BUILDER
# =============================================================================


class ModelBuilder:
    """
    Builds and validates semantic models.
    
    Ensures models have coherent structure and consistent relationships.
    """
    
    def __init__(
        self,
        minimum_concept_count: int = 2,
        minimum_relation_count: int = 1,
    ):
        """
        Initialize the builder.
        
        Args:
            minimum_concept_count: Minimum concepts required
            minimum_relation_count: Minimum relations required
        """
        self._min_concepts = minimum_concept_count
        self._min_relations = minimum_relation_count
    
    def validate_model(
        self,
        model: KnowledgeModel,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a semantic model.
        
        Args:
            model: The model to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check minimum concept count
        if len(model.concepts) < self._min_concepts:
            issues.append(f"Model has {len(model.concepts)} concepts, minimum is {self._min_concepts}")
        
        # Check for orphan concepts (not connected by relations)
        related_concepts = set()
        for source, target, _ in model.relations:
            related_concepts.add(source)
            related_concepts.add(target)
        
        for concept in model.concepts:
            if concept not in related_concepts:
                issues.append(f"Orphan concept: {concept} has no relations")
        
        return len(issues) == 0, issues
    
    def build_simple_model(
        self,
        name: str,
        domain: str,
        concepts: List[str],
        relations: Optional[List[Tuple[str, str, str]]] = None,
    ) -> KnowledgeModel:
        """
        Build a simple model with minimal validation.
        
        Args:
            name: Human-readable name
            domain: Domain context
            concepts: Concept IDs to include
            relations: Relations between concepts
            
        Returns:
            A new model
        """
        return KnowledgeModel.create(
            name=name,
            domain=domain,
            concepts=concepts,
            relations=relations or [],
            confidence=0.7 if len(concepts) >= 2 else 0.3,
        )


__all__ = [
    "ModelScope",
    "KnowledgeModel",
    "ModelBuilder",
]