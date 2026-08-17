# Knowledge Relation - Phase 5.4
# ==============================

"""
Knowledge Relation: Semantic connections between concepts.

Relations connect concepts in Gordon's knowledge graph, forming the structure
of semantic understanding. Examples include contains, uses, depends_on,
implements, communicates_with, owns, part_of, causes, precedes, follows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# RELATION KINDS - Types of semantic connections
# =============================================================================


class RelationKind(Enum):
    """
    Kinds of semantic relations between concepts.
    
    These define the nature of relationships in the knowledge graph.
    """
    
    # Structural relationships
    IS_A = "is_a"                   # Inheritance/specialization
    PART_OF = "part_of"             # Composition/part-whole
    INSTANCE_OF = "instance_of"     # Instance to class
    
    # Behavioral relationships
    USES = "uses"                   # Dependency: uses another concept
    DEPENDS_ON = "depends_on"       # Dependency relationship
    IMPLEMENTS = "implements"       # Implementation relation
    
    # Communication and interaction
    COMMUNICATES_WITH = "communicates_with"
    INTERACTS_WITH = "interacts_with"
    
    # Causal relationships
    CAUSES = "causes"               # Causality
    PRECEDES = "precedes"           # Temporal ordering
    FOLLOWS = "follows"             # Temporal ordering
    
    # Semantic relationships
    ASSOCIATED_WITH = "associated_with"
    SIMILAR_TO = "similar_to"       # Semantic equivalence/analogy
    CONFLICTS_WITH = "conflicts_with"  # Contradiction
    
    # Unknown/indeterminate
    UNKNOWN = "unknown"


# =============================================================================
# RELATION MODEL - Canonical relation structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeRelation:
    """
    Canonical representation of a semantic relationship in Gordon's knowledge system.
    
    Relations connect concepts in the knowledge graph, forming the structure
    of semantic understanding. Every relation has direction and preserves
    its provenance and confidence metrics.
    
    Fields:
        relation_identity:     Unique identifier for this relation
        source:                Source concept ID
        target:                Target concept ID
        relation_kind:         Type of relationship
        strength:              Strength of the relationship (0.0-1.0)
        confidence:            Semantic confidence in this relation (0.0-1.0)
        uncertainty:           Semantic uncertainty about this relation
        justification:         Evidence supporting this relation
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    relation_identity: str            # Unique ID for this relation
    
    # Concept references (required)
    source: str                       # Source concept ID
    target: str                       # Target concept ID
    
    # Relation type (required)
    relation_kind: RelationKind       # Kind of relationship
    
    # Relationship metrics
    strength: float = 0.5             # Strength (0.0-1.0)
    
    # Quality metrics (required)
    confidence: float = 0.5           # Semantic confidence (0.0-1.0)
    uncertainty: float = 0.5          # Semantic uncertainty (0.0-1.0)
    
    # Justification and history
    justification: str = ""           # Explanation for this relation
    revision: int = 1                 # Revision number for traceability
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if relation has minimal required data."""
        return (
            len(self.relation_identity) > 0 and
            len(self.source) > 0 and
            len(self.target) > 0 and
            self.relation_kind is not None
        )
    
    @property
    def is_causal(self) -> bool:
        """Check if this relation represents causality."""
        return self.relation_kind in (RelationKind.CAUSES,)
    
    @property
    def is_temporal(self) -> bool:
        """Check if this relation represents temporal ordering."""
        return self.relation_kind in (RelationKind.PRECEDES, RelationKind.FOLLOWS)
    
    @classmethod
    def create(
        cls,
        source_id: str,
        target_id: str,
        relation_kind: RelationKind = RelationKind.UNKNOWN,
        strength: float = 0.5,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        justification: str = "",
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeRelation":
        """
        Create a new relation.
        
        Args:
            source_id: Source concept ID
            target_id: Target concept ID
            relation_kind: Type of relationship
            strength: Relationship strength (0.0-1.0)
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            justification: Explanation for this relation (optional)
            provenance: Origin tracking data (optional)
        """
        return cls(
            relation_identity=f"relation:{uuid.uuid4().hex[:16]}",
            source=source_id,
            target=target_id,
            relation_kind=relation_kind,
            strength=max(0.0, min(1.0, float(strength))),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            justification=justification,
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relation to dictionary for serialization."""
        return {
            "relation_identity": self.relation_identity,
            "source": self.source,
            "target": self.target,
            "relation_kind": self.relation_kind.value if self.relation_kind else None,
            "strength": self.strength,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "justification": self.justification,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeRelation":
        """Create relation from dictionary."""
        kind_value = data.get("relation_kind", "unknown")
        try:
            relation_kind = RelationKind(kind_value)
        except ValueError:
            relation_kind = RelationKind.UNKNOWN
        
        return cls(
            relation_identity=data.get("relation_identity", str(uuid.uuid4())),
            source=data.get("source", ""),
            target=data.get("target", ""),
            relation_kind=relation_kind,
            strength=float(data.get("strength", 0.5)),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            justification=data.get("justification", ""),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )
    
    def invert(self) -> "KnowledgeRelation":
        """
        Create an inverted version of this relation.
        
        Returns a new relation with source and target swapped, and the
        relation kind inverted if possible (e.g., PRECEDES -> FOLLOWS).
        """
        # Map inverse relations
        inverse_kinds = {
            RelationKind.PRECEDES: RelationKind.FOLLOWS,
            RelationKind.FOLLOWS: RelationKind.PRECEDES,
            RelationKind.CAUSES: RelationKind.DEPENDS_ON,  # Simplified
        }
        
        new_kind = inverse_kinds.get(self.relation_kind, self.relation_kind)
        
        return KnowledgeRelation(
            relation_identity=f"relation:{uuid.uuid4().hex[:16]}",
            source=self.target,
            target=self.source,
            relation_kind=new_kind,
            strength=self.strength,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            justification=f"Inverted from {self.relation_identity}: {self.justification}",
            provenance={
                "original_relation": self.relation_identity,
                "inverted_at_utc": time.time(),
            },
        )


# =============================================================================
# RELATION BUILDER
# =============================================================================


class RelationBuilder:
    """
    Builds and validates relations in the knowledge graph.
    
    Ensures relations are well-formed and consistent with domain knowledge.
    """
    
    def __init__(
        self,
        allow_circular_relations: bool = True,
        minimum_strength: float = 0.1,
    ):
        """
        Initialize the builder.
        
        Args:
            allow_circular_relations: Allow A -> B -> A cycles
            minimum_strength: Minimum acceptable relation strength
        """
        self._allow_circular = allow_circular_relations
        self._minimum_strength = minimum_strength
    
    def validate_relation(
        self,
        source_id: str,
        target_id: str,
        relation_kind: RelationKind,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a proposed relation.
        
        Args:
            source_id: Source concept ID
            target_id: Target concept ID
            relation_kind: Type of relationship
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for self-referential relations
        if source_id == target_id:
            issues.append("Source and target cannot be the same concept")
        
        # Validate strength range
        # Note: validation would happen at construction time
        
        return len(issues) == 0, issues
    
    def build_is_a_relation(
        self,
        child_id: str,
        parent_id: str,
        confidence: float = 0.9,
    ) -> KnowledgeRelation:
        """
        Build an IS_A relation (inheritance).
        
        Args:
            child_id: Child concept ID
            parent_id: Parent concept ID
            confidence: Confidence in the inheritance (0.0-1.0)
            
        Returns:
            A new IS_A relation from child to parent
        """
        return KnowledgeRelation.create(
            source_id=child_id,
            target_id=parent_id,
            relation_kind=RelationKind.IS_A,
            strength=confidence,
            confidence=confidence,
            justification=f"{child_id} is a specialized form of {parent_id}",
        )
    
    def build_part_of_relation(
        self,
        part_id: str,
        whole_id: str,
        confidence: float = 0.85,
    ) -> KnowledgeRelation:
        """
        Build a PART_OF relation (composition).
        
        Args:
            part_id: Part concept ID
            whole_id: Whole concept ID
            confidence: Confidence in the composition (0.0-1.0)
            
        Returns:
            A new PART_OF relation from part to whole
        """
        return KnowledgeRelation.create(
            source_id=part_id,
            target_id=whole_id,
            relation_kind=RelationKind.PART_OF,
            strength=confidence,
            confidence=confidence,
            justification=f"{part_id} is a component of {whole_id}",
        )
    
    def build_uses_relation(
        self,
        consumer_id: str,
        provider_id: str,
        confidence: float = 0.7,
    ) -> KnowledgeRelation:
        """
        Build a USES relation (dependency).
        
        Args:
            consumer_id: Consumer concept ID
            provider_id: Provider concept ID
            confidence: Confidence in the dependency (0.0-1.0)
            
        Returns:
            A new USES relation from consumer to provider
        """
        return KnowledgeRelation.create(
            source_id=consumer_id,
            target_id=provider_id,
            relation_kind=RelationKind.USES,
            strength=confidence,
            confidence=confidence,
            justification=f"{consumer_id} depends on {provider_id}",
        )


__all__ = [
    "RelationKind",
    "KnowledgeRelation",
    "RelationBuilder",
]