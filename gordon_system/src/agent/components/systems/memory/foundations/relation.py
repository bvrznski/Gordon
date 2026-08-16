# Memory Relation - Phase 5.1 Canonical Semantic Graph Edge
# ==========================================================

"""
Memory Relation: Semantic connections between memory artifacts.

Memory is not a filesystem, not a table, not a vector database. Memory is
a semantic graph with persistent artifacts and explicit relations.

Relations include:
    REFERENCES     : Points to another artifact
    CONTAINS       : Contains other artifacts
    BELONGS_TO     : Belongs to a collection
    PRECEDES       : Occurred before
    FOLLOWS        : Occurred after
    SUPPORTS       : Supports or confirms
    CONTRADICTS    : Contradicts
    DERIVED_FROM   : Derived from another artifact
    CAUSES         : Causes another artifact
    GENERALIZES    : Is a generalization of
    SPECIALIZES    : Is a specialization of
    SIMILAR_TO     : Similar to another artifact

Relation Laws:
    RELATION-LAW-001: Every semantic relationship is explicit
    RELATION-LAW-002: Relations connect Memory Artifacts only
    RELATION-LAW-003: Relations preserve provenance
    RELATION-LAW-004: Relations preserve confidence
    RELATION-LAW-005: Relations preserve uncertainty
    RELATION-LAW-006: Relations preserve revision lineage
    RELATION-LAW-007: Relations are first-class semantic objects
    RELATION-LAW-008: Relation evaluation is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import time
import uuid


# =============================================================================
# MEMORY RELATION KINDS - Semantic relationship types
# =============================================================================


class MemoryRelationKind(Enum):
    """
    Types of semantic relationships between memory artifacts.
    
    | Kind              | Description                                       |
    |-------------------|--------------------------------------------------|
    | REFERENCES        | Points to another artifact (reference)           |
    | CONTAINS          | Contains other artifacts as parts                |
    | BELONGS_TO        | Belongs to a collection or category              |
    | PRECEDES          | Occurred/started before                          |
    | FOLLOWS           | Occurred/started after                           |
    | SUPPORTS          | Supports, confirms, or validates                 |
    | CONTRADICTS       | Contradicts or negates                           |
    | DERIVED_FROM      | Derived from another artifact                    |
    | CAUSES            | Causes the target artifact                       |
    | GENERALIZES       | Is a generalization of target                    |
    | SPECIALIZES       | Is a specialization of target                    |
    | SIMILAR_TO        | Similar in meaning or content                    |
    | PART_OF           | Is part of another artifact                      |
    | HAS_PART          | Has the target as a part                         |
    | EXPLAINS          | Provides explanation for target                  |
    | PREDICTS          | Predicts the occurrence of target                |
    """
    
    REFERENCES = "references"
    CONTAINS = "contains"
    BELONGS_TO = "belongs_to"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    CAUSES = "causes"
    GENERALIZES = "generalizes"
    SPECIALIZES = "specializes"
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    HAS_PART = "has_part"
    EXPLAINS = "explains"
    PREDICTS = "predicts"


# =============================================================================
# MEMORY RELATION - Semantic graph edge
# =============================================================================


@dataclass(frozen=True)
class MemoryRelation:
    """
    Explicit semantic relationship between two memory artifacts.
    
    Relations are first-class objects with their own identity, provenance,
    confidence, and revision history. They form the edges of the semantic graph.
    
    Fields:
        identity:           Unique ID for this relation record
        
        # Graph structure
        source_artifact:    What is connected? (artifact_id)
        target_artifact:    To what is it connected? (artifact_id)
        
        # Relation type
        relation_kind:      What kind of relationship?
        strength:           How strong is this connection? (0.0-1.0)
        
        # Confidence & uncertainty
        confidence:         Belief in this relationship (0.0-1.0)
        uncertainty:        Uncertainty about this relationship
        
        # Provenance
        provenance:         How was this relation established?
        
        # Timestamps
        created_at_utc:     When was the relation recorded?
    """
    
    identity: str                         # Unique ID for this relation record
    
    # Graph structure
    source_artifact: str                  # Source artifact's artifact_id
    target_artifact: str                  # Target artifact's artifact_id
    
    # Relation type
    relation_kind: MemoryRelationKind     # Kind of relationship
    
    strength: float = 1.0                 # Strength of connection (0.0-1.0)
    
    # Confidence and uncertainty
    confidence: float = 1.0               # Belief in this relationship
    uncertainty: float = 0.0              # Uncertainty about this relationship
    
    # Provenance
    provenance: Optional[str] = None      # How was this established?
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def relation_id(self) -> str:
        """Get a canonical ID for this relation."""
        return self.identity
    
    @classmethod
    def create_reference(
        cls,
        source_artifact: str,
        target_artifact: str,
        strength: float = 1.0,
        confidence: float = 1.0,
    ) -> "MemoryRelation":
        """
        Create a reference relationship.
        
        Args:
            source_artifact: What points to the target?
            target_artifact: What is being referenced?
            strength: How strongly does it reference? (optional)
            confidence: Trust in this relation (optional)
            
        Returns:
            New MemoryRelation with REFERENCES kind
        """
        return cls(
            identity=str(uuid.uuid4()),
            source_artifact=source_artifact,
            target_artifact=target_artifact,
            relation_kind=MemoryRelationKind.REFERENCES,
            strength=strength,
            confidence=confidence,
        )
    
    @classmethod
    def create_supports(
        cls,
        supporting_artifact: str,
        supported_artifact: str,
        confidence: float = 1.0,
    ) -> "MemoryRelation":
        """
        Create a supports relationship.
        
        Args:
            supporting_artifact: What supports the other?
            supported_artifact: What is being supported?
            confidence: Trust in this relation (optional)
            
        Returns:
            New MemoryRelation with SUPPORTS kind
        """
        return cls(
            identity=str(uuid.uuid4()),
            source_artifact=supporting_artifact,
            target_artifact=supported_artifact,
            relation_kind=MemoryRelationKind.SUPPORTS,
            confidence=confidence,
        )
    
    @classmethod
    def create_contradicts(
        cls,
        contradictor: str,
        contradicted: str,
        uncertainty: float = 0.5,
    ) -> "MemoryRelation":
        """
        Create a contradicts relationship.
        
        Args:
            contradictor: What contradicts the other?
            contradicted: What is being contradicted?
            uncertainty: Uncertainty about this contradiction? (optional)
            
        Returns:
            New MemoryRelation with CONTRADICTS kind
        """
        return cls(
            identity=str(uuid.uuid4()),
            source_artifact=contradictor,
            target_artifact=contradicted,
            relation_kind=MemoryRelationKind.CONTRADICTS,
            uncertainty=uncertainty,
        )
    
    def inverse(self) -> "MemoryRelation":
        """
        Create the inverse relationship.
        
        Returns:
            New MemoryRelation with reversed source/target
        """
        # Map to inverse kind if available
        inverse_kinds = {
            MemoryRelationKind.SUPPORTS: MemoryRelationKind.CONTRADICTS,
            MemoryRelationKind.PRECEDES: MemoryRelationKind.FOLLOWS,
            MemoryRelationKind.GENERALIZES: MemoryRelationKind.SPECIALIZES,
            MemoryRelationKind.HAS_PART: MemoryRelationKind.PART_OF,
        }
        
        inverse_kind = inverse_kinds.get(self.relation_kind, self.relation_kind)
        
        return dataclass_replace(
            self,
            source_artifact=self.target_artifact,
            target_artifact=self.source_artifact,
            relation_kind=inverse_kind,
        )
    
    def with_confidence(self, confidence: float) -> "MemoryRelation":
        """Return copy with new confidence."""
        return dataclass_replace(self, confidence=confidence)
    
    def with_strength(self, strength: float) -> "MemoryRelation":
        """Return copy with new strength."""
        return dataclass_replace(self, strength=strength)


# =============================================================================
# MEMORY SUBGRAPH - Localized portion of the graph
# =============================================================================


@dataclass(frozen=True)
class MemorySubgraph:
    """
    A local subgraph centered on one artifact.
    
    Useful for localized reasoning without loading the entire graph.
    
    Fields:
        root_artifact:      The central artifact of this subgraph
        
        # Graph content
        artifacts:          All artifacts in this subgraph (including root)
        relations:          All relations between these artifacts
        
        # Boundary specification
        boundary_depth:     How far from root to include?
        
        # Provenance
        provenance:         Where did this subgraph come from?
    """
    
    root_artifact: str                    # Central artifact ID
    
    # Graph content
    artifacts: Tuple[str, ...]            # All artifact IDs in subgraph
    relations: Tuple[MemoryRelation, ...] # Relations between them
    
    # Boundary specification
    boundary_depth: int = 2               # Max distance from root
    
    # Provenance
    provenance: Optional[str] = None      # How was this extracted?
    
    @property
    def artifact_count(self) -> int:
        """Count of artifacts in this subgraph."""
        return len(self.artifacts)
    
    @property
    def relation_count(self) -> int:
        """Count of relations in this subgraph."""
        return len(self.relations)


# =============================================================================
# MEMORY PATH - Sequence of relations between artifacts
# =============================================================================


@dataclass(frozen=True)
class MemoryPath:
    """
    A path through the semantic graph from one artifact to another.
    
    Paths represent chains of relationships that can be traversed for
    reasoning or retrieval.
    
    Fields:
        start:              Starting artifact ID
        
        # Path content
        end:                Ending artifact ID
        traversed_relations: Sequence of relations followed
        
        # Path properties
        path_length:        Number of steps in the path
        path_type:          Category of path (causal, semantic, temporal)
        
        # Confidence & provenance
        confidence:         Belief in this path's validity (0.0-1.0)
        provenance:         How was this path determined?
    """
    
    start: str                            # Starting artifact ID
    
    # Path content
    end: str                              # Ending artifact ID
    traversed_relations: Tuple[str, ...]  # Relation IDs followed
    
    # Path properties
    path_length: int = 0                  # Number of relations traversed
    path_type: str = "unknown"            # Category: causal, semantic, temporal, etc.
    
    # Confidence & provenance
    confidence: float = 1.0               # Belief in this path's validity
    provenance: Optional[str] = None      # How was this path determined?
    
    @classmethod
    def create(
        cls,
        start_artifact: str,
        end_artifact: str,
        relations: Tuple[MemoryRelation, ...],
    ) -> "MemoryPath":
        """
        Create a path from a sequence of relations.
        
        Args:
            start_artifact: Starting artifact ID
            end_artifact: Ending artifact ID  
            relations: Relations traversed to get from start to end
            
        Returns:
            New MemoryPath with computed properties
        """
        return cls(
            start=start_artifact,
            end=end_artifact,
            traversed_relations=tuple(r.identity for r in relations),
            path_length=len(relations),
            path_type="semantic",  # Default, can be refined based on relation kinds
            confidence=min((r.confidence for r in relations), default=1.0),
            provenance=f"path from {start_artifact} to {end_artifact}",
        )


# =============================================================================
# MEMORY CLUSTER - Group of related artifacts
# =============================================================================


@dataclass(frozen=True)
class MemoryCluster:
    """
    A cluster of memory artifacts that are semantically related.
    
    Clusters help organize the graph into meaningful groups. They never replace
    individual artifacts but provide higher-level structure.
    
    Fields:
        cluster_identity:   Unique ID for this cluster
        
        # Cluster content
        member_artifacts:   Artifact IDs in this cluster
        internal_relations: Relations between members
        
        # Cluster properties
        summary:            Brief description of the cluster
        cohesion_score:     How tightly connected is the cluster? (0.0-1.0)
        
        # Provenance
        cluster_kind:       Category of cluster (topic, event, concept, etc.)
    """
    
    cluster_identity: str                 # Unique ID for this cluster
    
    # Cluster content
    member_artifacts: Tuple[str, ...]     # Artifact IDs in cluster
    internal_relations: Tuple[MemoryRelation, ...] = field(default_factory=tuple)
    
    # Cluster properties
    summary: Optional[str] = None         # Description of the cluster
    cohesion_score: float = 1.0           # How tightly connected?
    
    # Provenance
    cluster_kind: str = "semantic"        # Category: topic, event, concept
    
    @property
    def member_count(self) -> int:
        """Count of members in this cluster."""
        return len(self.member_artifacts)
    
    @property
    def relation_count(self) -> int:
        """Count of internal relations."""
        return len(self.internal_relations)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance, **kwargs):
    """Replace fields in a frozen dataclass (generic)."""
    if isinstance(instance, MemoryRelation):
        return MemoryRelation(
            identity=kwargs.get("identity", instance.identity),
            source_artifact=kwargs.get("source_artifact", instance.source_artifact),
            target_artifact=kwargs.get("target_artifact", instance.target_artifact),
            relation_kind=kwargs.get("relation_kind", instance.relation_kind),
            strength=kwargs.get("strength", instance.strength),
            confidence=kwargs.get("confidence", instance.confidence),
            uncertainty=kwargs.get("uncertainty", instance.uncertainty),
            provenance=kwargs.get("provenance", instance.provenance),
            created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        )
    elif isinstance(instance, MemorySubgraph):
        return MemorySubgraph(
            root_artifact=kwargs.get("root_artifact", instance.root_artifact),
            artifacts=kwargs.get("artifacts", instance.artifacts),
            relations=kwargs.get("relations", instance.relations),
            boundary_depth=kwargs.get("boundary_depth", instance.boundary_depth),
            provenance=kwargs.get("provenance", instance.provenance),
        )
    elif isinstance(instance, MemoryPath):
        return MemoryPath(
            start=kwargs.get("start", instance.start),
            end=kwargs.get("end", instance.end),
            traversed_relations=kwargs.get("traversed_relations", instance.traversed_relations),
            path_length=kwargs.get("path_length", instance.path_length),
            path_type=kwargs.get("path_type", instance.path_type),
            confidence=kwargs.get("confidence", instance.confidence),
            provenance=kwargs.get("provenance", instance.provenance),
        )
    elif isinstance(instance, MemoryCluster):
        return MemoryCluster(
            cluster_identity=kwargs.get("cluster_identity", instance.cluster_identity),
            member_artifacts=kwargs.get("member_artifacts", instance.member_artifacts),
            internal_relations=kwargs.get("internal_relations", instance.internal_relations),
            summary=kwargs.get("summary", instance.summary),
            cohesion_score=kwargs.get("cohesion_score", instance.cohesion_score),
            cluster_kind=kwargs.get("cluster_kind", instance.cluster_kind),
        )
    else:
        raise TypeError(f"Unknown type: {type(instance)}")


def dataclass_replace_relation(instance: MemoryRelation, **kwargs) -> MemoryRelation:
    """Replace fields in a frozen MemoryRelation."""
    return MemoryRelation(
        identity=kwargs.get("identity", instance.identity),
        source_artifact=kwargs.get("source_artifact", instance.source_artifact),
        target_artifact=kwargs.get("target_artifact", instance.target_artifact),
        relation_kind=kwargs.get("relation_kind", instance.relation_kind),
        strength=kwargs.get("strength", instance.strength),
        confidence=kwargs.get("confidence", instance.confidence),
        uncertainty=kwargs.get("uncertainty", instance.uncertainty),
        provenance=kwargs.get("provenance", instance.provenance),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryRelation",
    "MemoryRelationKind",
    "MemorySubgraph",
    "MemoryPath",
    "MemoryCluster",
    "dataclass_replace_relation",
]