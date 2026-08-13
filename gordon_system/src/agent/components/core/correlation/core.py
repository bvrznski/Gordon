# Phase 3.11.14 - Cross-Stream Correlation Core Types
# =====================================================

"""
Core type definitions for Cross-Stream Correlation & Causation Architecture.

This module contains the primary type definitions that are shared across
the correlation graph, security, observability, and integration modules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
from enum import Enum, auto
import time
import uuid
import hashlib


# =============================================================================
# IDENTITY TYPES - Immutable Relationship Identifiers
# =============================================================================


class CorrelationIdType(Enum):
    """Categories of correlation identifiers."""
    CORRELATION = "correlation"
    CAUSATION = "causation"
    EPISODE = "episode"
    EXECUTION_EPISODE = "execution_episode"
    EXPERIENCE = "experience"
    SITUATION = "situation"


@dataclass(frozen=True)
class CorrelationId:
    """Identifier for semantic correlation between records."""
    value: str
    kind: CorrelationIdType = CorrelationIdType.CORRELATION
    
    @classmethod
    def generate(cls) -> "CorrelationId":
        return cls(value=str(uuid.uuid4()), kind=CorrelationIdType.CORRELATION)


@dataclass(frozen=True)
class EpisodeId:
    """Identifier for an episode (temporal grouping of related records)."""
    value: str
    
    @classmethod
    def generate(cls) -> "EpisodeId":
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_context(cls, context_type: str, timestamp_ns: int, nonce: str) -> "EpisodeId":
        hash_input = f"{context_type}:{timestamp_ns}:{nonce}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return cls(value=f"episode:{hash_value}")


@dataclass(frozen=True)
class CausationChainId:
    """Identifier for a chain of causal relationships."""
    value: str
    
    @classmethod
    def generate(cls) -> "CausationChainId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class EdgeMetadata:
    """Metadata attached to a relationship edge."""
    edge_id: str
    relationship_kind: "RelationshipKind"
    confidence: float = 1.0
    provenance: Dict[str, Any] = field(default_factory=dict)
    creator: Optional[str] = None
    created_at_utc: float = field(default_factory=time.time)
    policy_version: str = "1.0.0"
    trust: float = 1.0
    privacy_class: str = "internal"
    scope: str = "global"
    evidence_chain: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# RELATIONSHIP KINDS - Types of Semantic Relationships
# =============================================================================


class RelationshipKind(Enum):
    """Canonical kinds of semantic relationships between stream records."""
    
    # CORRELATION (association - NO causation implied)
    CORRELATES_WITH = "correlates_with"
    SIMILAR_TO = "similar_to"
    ALIGNED_WITH = "aligned_with"
    TEMPORALLY_ASSOCIATED_WITH = "temporally_associated_with"
    
    # DIRECT CAUSATION
    DIRECTLY_CAUSES = "directly_causes"
    TRIGGERS = "triggers"
    INITIATES = "initiates"
    
    # INDIRECT CAUSATION
    INDIRECTLY_CAUSES = "indirectly_causes"
    CONTRIBUTES_TO = "contributes_to"
    ENABLES = "enables"
    PREVENTS = "prevents"
    
    # CONTRIBUTION & DEPENDENCY
    CONTRIBUTED_TO = "contributed_to"
    INFLUENCED = "influenced"
    DEPENDS_ON = "depends_on"
    REQUIRES = "requires"
    BUILDING_BLOCK_OF = "building_block_of"
    
    # EVIDENCE RELATIONSHIPS
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFUTES = "refutes"
    CONFIRMS = "confirms"
    
    # PREDICTION RELATIONSHIPS
    PREDICTED = "predicted"
    FULFILLED = "fulfilled"
    VIOLATED = "violated"
    
    # CONTEXTUAL
    CONTEXT_FOR = "context_for"
    SITUATION_OF = "situation_of"
    PART_OF_EPISODE = "part_of_episode"
    CONTINUATION_OF = "continuation_of"
    
    # TEMPORAL (separate from causation)
    HAPPENED_BEFORE = "happened_before"
    HAPPENED_AFTER = "happened_after"
    CONCURRENT_WITH = "concurrent_with"
    OVERLAPS_WITH = "overlaps_with"
    
    # EXECUTION RELATIONSHIPS
    EXECUTED_IN_THREAD = "executed_in_thread"
    PART_OF_LOOP = "part_of_loop"
    STAGE_OF_CYCLE = "stage_of_cycle"
    OUTPUT_OF_CAPABILITY = "output_of_capability"
    
    # OWNERSHIP REFERENCES (not transfer)
    ORIGINATED_FROM_STREAM = "originated_from_stream"
    REFERENCED_BY_STREAM = "referenced_by_stream"


# =============================================================================
# EDGE TYPES - Relationship Representation
# =============================================================================


class RelationshipGraphError(Exception):
    """Base exception for graph operations."""
    pass


class DuplicateEdgeError(RelationshipGraphError):
    """Raised when attempting to add a duplicate edge."""
    def __init__(self, edge_id: str, existing_edge: Any):
        self.edge_id = edge_id
        self.existing_edge = existing_edge
        super().__init__(f"Duplicate edge {edge_id}: {existing_edge}")


class CausationWithoutEvidenceError(RelationshipGraphError):
    """Raised when causation is asserted without evidence."""
    def __init__(self, cause_record: str, effect_record: str):
        self.cause_record = cause_record
        self.effect_record = effect_record
        super().__init__(
            f"Causation from {cause_record} to {effect_record} "
            "must include explicit evidence references"
        )


@dataclass(frozen=True)
class CorrelationEdge:
    """Immutable edge representing a correlation relationship."""
    source_record_id: str
    target_record_id: str
    stream_id_source: str
    stream_id_target: str
    correlation_id: CorrelationId
    kind: RelationshipKind
    metadata: EdgeMetadata


@dataclass(frozen=True)
class CausationEdge:
    """Immutable edge representing a causal relationship."""
    cause_record_id: str
    effect_record_id: str
    stream_id_cause: str
    stream_id_effect: str
    causation_chain_id: CausationChainId
    kind: RelationshipKind
    evidence_references: Tuple[str, ...]
    metadata: EdgeMetadata


@dataclass(frozen=True)
class EpisodeEdge:
    """Immutable edge representing episode membership."""
    record_id: str
    stream_id: str
    episode_id: EpisodeId
    role_in_episode: str = ""
    metadata: EdgeMetadata = field(default_factory=lambda: EdgeMetadata(
        edge_id="", relationship_kind=RelationshipKind.PART_OF_EPISODE
    ))


# =============================================================================
# GRAPH STRUCTURE - Immutable Relationship Graph
# =============================================================================


@dataclass(frozen=True)
class RelationshipGraphSnapshot:
    """Immutable snapshot of the relationship graph at a point in time."""
    snapshot_id: str
    created_at_utc: float
    edge_count: int
    record_count: int
    correlation_edges: Tuple[str, ...]
    causation_edges: Tuple[str, ...]
    episode_memberships: Tuple[str, ...]


@dataclass(frozen=True)
class RelationshipGraph:
    """Immutable semantic relationship graph."""
    graph_id: str
    correlation_edges: Dict[str, CorrelationEdge]
    causation_edges: Dict[str, CausationEdge]
    episode_memberships: Dict[str, EpisodeEdge]
    created_at_utc: float = field(default_factory=time.time)
    graph_version: str = "1.0.0"
    integrity_hash: Optional[str] = None
    
    @classmethod
    def create_empty(cls) -> "RelationshipGraph":
        return cls(
            graph_id=f"graph-{uuid.uuid4().hex[:16]}",
            correlation_edges={},
            causation_edges={},
            episode_memberships={},
            created_at_utc=time.time()
        )
    
    def add_correlation_edge(
        self,
        source_record_id: str,
        target_record_id: str,
        stream_id_source: str,
        stream_id_target: str,
        relationship_kind: RelationshipKind,
        metadata: Optional[EdgeMetadata] = None,
    ) -> "RelationshipGraph":
        if metadata is None:
            metadata = EdgeMetadata(
                edge_id=f"corr-{uuid.uuid4().hex[:16]}",
                relationship_kind=relationship_kind
            )
        
        edge = CorrelationEdge(
            source_record_id=source_record_id,
            target_record_id=target_record_id,
            stream_id_source=stream_id_source,
            stream_id_target=stream_id_target,
            correlation_id=CorrelationId.generate(),
            kind=relationship_kind,
            metadata=metadata
        )
        
        new_edges = dict(self.correlation_edges)
        if edge.metadata.edge_id in new_edges:
            raise DuplicateEdgeError(edge.metadata.edge_id, edge)
        new_edges[edge.metadata.edge_id] = edge
        
        return dataclass_replace(
            self,
            correlation_edges=new_edges,
            integrity_hash=self._compute_integrity_hash()
        )
    
    def add_causation_edge(
        self,
        cause_record_id: str,
        effect_record_id: str,
        stream_id_cause: str,
        stream_id_effect: str,
        relationship_kind: RelationshipKind,
        evidence_references: Tuple[str, ...],
        metadata: Optional[EdgeMetadata] = None,
    ) -> "RelationshipGraph":
        if not evidence_references:
            raise CausationWithoutEvidenceError(cause_record_id, effect_record_id)
        
        if metadata is None:
            metadata = EdgeMetadata(
                edge_id=f"caus-{uuid.uuid4().hex[:16]}",
                relationship_kind=relationship_kind,
                provenance={"evidence_count": len(evidence_references), "created_by": "graph_manager"}
            )
        
        edge = CausationEdge(
            cause_record_id=cause_record_id,
            effect_record_id=effect_record_id,
            stream_id_cause=stream_id_cause,
            stream_id_effect=stream_id_effect,
            causation_chain_id=CausationChainId.generate(),
            kind=relationship_kind,
            evidence_references=evidence_references,
            metadata=metadata
        )
        
        new_edges = dict(self.causation_edges)
        if edge.metadata.edge_id in new_edges:
            raise DuplicateEdgeError(edge.metadata.edge_id, edge)
        new_edges[edge.metadata.edge_id] = edge
        
        return dataclass_replace(
            self,
            causation_edges=new_edges,
            integrity_hash=self._compute_integrity_hash()
        )
    
    def add_episode_membership(
        self,
        record_id: str,
        stream_id: str,
        episode_id: EpisodeId,
        role_in_episode: str = "",
        metadata: Optional[EdgeMetadata] = None,
    ) -> "RelationshipGraph":
        if metadata is None:
            metadata = EdgeMetadata(
                edge_id=f"epi-{uuid.uuid4().hex[:16]}",
                relationship_kind=RelationshipKind.PART_OF_EPISODE
            )
        
        edge = EpisodeEdge(
            record_id=record_id,
            stream_id=stream_id,
            episode_id=episode_id,
            role_in_episode=role_in_episode,
            metadata=metadata
        )
        
        new_edges = dict(self.episode_memberships)
        if edge.metadata.edge_id in new_edges:
            raise DuplicateEdgeError(edge.metadata.edge_id, edge)
        new_edges[edge.metadata.edge_id] = edge
        
        return dataclass_replace(
            self,
            episode_memberships=new_edges,
            integrity_hash=self._compute_integrity_hash()
        )
    
    def _compute_integrity_hash(self) -> str:
        all_edge_ids = (
            sorted(self.correlation_edges.keys()) +
            sorted(self.causation_edges.keys()) +
            sorted(self.episode_memberships.keys())
        )
        hash_input = ":".join(all_edge_ids)
        return hashlib.sha256(hash_input.encode()).hexdigest()[:32]
    
    def get_correlated_records(self, record_id: str) -> List[str]:
        correlated = set()
        for edge in self.correlation_edges.values():
            if edge.source_record_id == record_id:
                correlated.add(edge.target_record_id)
            elif edge.target_record_id == record_id:
                correlated.add(edge.source_record_id)
        return list(correlated)
    
    def get_causes(self, effect_record_id: str) -> List[CausationEdge]:
        return [
            edge for edge in self.causation_edges.values()
            if edge.effect_record_id == effect_record_id
        ]
    
    def get_effects(self, cause_record_id: str) -> List[CausationEdge]:
        return [
            edge for edge in self.causation_edges.values()
            if edge.cause_record_id == cause_record_id
        ]
    
    def to_snapshot(self) -> RelationshipGraphSnapshot:
        return RelationshipGraphSnapshot(
            snapshot_id=f"snapshot-{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
            edge_count=len(self.correlation_edges) + len(self.causation_edges) + len(self.episode_memberships),
            record_count=self._count_unique_records(),
            correlation_edges=tuple(self.correlation_edges.keys()),
            causation_edges=tuple(self.causation_edges.keys()),
            episode_memberships=tuple(self.episode_memberships.keys())
        )
    
    def _count_unique_records(self) -> int:
        records = set()
        for edge in self.correlation_edges.values():
            records.add(edge.source_record_id)
            records.add(edge.target_record_id)
        for edge in self.causation_edges.values():
            records.add(edge.cause_record_id)
            records.add(edge.effect_record_id)
        for edge in self.episode_memberships.values():
            records.add(edge.record_id)
        return len(records)


# =============================================================================
# TRAVERSAL - Graph Navigation
# =============================================================================


class TraversalDirection(Enum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"
    BOTH = "both"


@dataclass
class TraversalResult:
    """Result of a graph traversal operation."""
    source_id: str
    target_id: str
    edges_traversed: List[str]
    edge_kinds: List[str]
    total_distance: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edges_traversed": self.edges_traversed,
            "edge_kinds": self.edge_kinds,
            "total_distance": self.total_distance
        }


class RelationshipGraphTraversal:
    """Immutable traversal state for graph navigation."""
    
    @staticmethod
    def find_paths(
        graph: RelationshipGraph,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
        allow_correlation: bool = True,
        allow_causation: bool = True,
    ) -> List[TraversalResult]:
        if source_id == target_id:
            return [TraversalResult(source_id, target_id, [], [], 0)]
        
        results: List[TraversalResult] = []
        visited: Set[str] = {source_id}
        queue: List[Tuple[str, List[str], List[str]]] = [(source_id, [], [])]
        
        while queue and len(results) < 100:
            current_id, edges, kinds = queue.pop(0)
            
            if len(edges) >= max_depth:
                continue
            
            for edge in graph.correlation_edges.values():
                next_id = None
                if edge.source_record_id == current_id:
                    next_id = edge.target_record_id
                elif edge.target_record_id == current_id:
                    next_id = edge.source_record_id
                
                if next_id is not None and next_id not in visited and allow_correlation:
                    new_edges = edges + [edge.metadata.edge_id]
                    new_kinds = kinds + [edge.kind.value]
                    
                    if next_id == target_id:
                        results.append(TraversalResult(source_id, target_id, new_edges, new_kinds, len(new_edges)))
                    else:
                        visited.add(next_id)
                        queue.append((next_id, new_edges, new_kinds))
            
            for edge in graph.causation_edges.values():
                next_id = None
                if edge.cause_record_id == current_id:
                    next_id = edge.effect_record_id
                elif edge.effect_record_id == current_id:
                    next_id = edge.cause_record_id
                
                if next_id is not None and next_id not in visited and allow_causation:
                    new_edges = edges + [edge.metadata.edge_id]
                    new_kinds = kinds + [edge.kind.value]
                    
                    if next_id == target_id:
                        results.append(TraversalResult(source_id, target_id, new_edges, new_kinds, len(new_edges)))
                    else:
                        visited.add(next_id)
                        queue.append((next_id, new_edges, new_kinds))
        
        return results
    
    @staticmethod
    def find_causal_chain(
        graph: RelationshipGraph,
        effect_record_id: str,
        max_depth: int = 10,
    ) -> List[TraversalResult]:
        results: List[TraversalResult] = []
        visited: Set[str] = {effect_record_id}
        queue: List[Tuple[str, List[str], List[str], int]] = [(effect_record_id, [], [], 0)]
        
        while queue:
            current_id, edges, kinds, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            for edge in graph.causation_edges.values():
                if edge.effect_record_id == current_id:
                    cause_id = edge.cause_record_id
                    
                    if cause_id not in visited:
                        new_edges = edges + [edge.metadata.edge_id]
                        new_kinds = kinds + [edge.kind.value]
                        
                        results.append(TraversalResult(
                            cause_id, effect_record_id, new_edges, new_kinds, depth + 1))
                        
                        visited.add(cause_id)
                        queue.append((cause_id, new_edges, new_kinds, depth + 1))
        
        return results
    
    @staticmethod
    def get_transitive_effects(
        graph: RelationshipGraph,
        cause_record_id: str,
        max_depth: int = 10,
    ) -> List[TraversalResult]:
        results: List[TraversalResult] = []
        visited: Set[str] = {cause_record_id}
        queue: List[Tuple[str, List[str], List[str], int]] = [(cause_record_id, [], [], 0)]
        
        while queue:
            current_id, edges, kinds, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            for edge in graph.causation_edges.values():
                if edge.cause_record_id == current_id:
                    effect_id = edge.effect_record_id
                    
                    if effect_id not in visited:
                        new_edges = edges + [edge.metadata.edge_id]
                        new_kinds = kinds + [edge.kind.value]
                        
                        results.append(TraversalResult(
                            cause_record_id, effect_id, new_edges, new_kinds, depth + 1))
                        
                        visited.add(effect_id)
                        queue.append((effect_id, new_edges, new_kinds, depth + 1))
        
        return results


# =============================================================================
# EPISODE MANAGEMENT
# =============================================================================


@dataclass(frozen=True)
class EpisodeDescriptor:
    """Descriptor for an episode (temporal grouping)."""
    episode_id: EpisodeId
    context_type: str
    created_at_utc: float
    description: Optional[str] = None
    first_record_time_utc: Optional[float] = None
    last_record_time_utc: Optional[float] = None
    record_ids: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EpisodeManager:
    """Immutable episode management state."""
    episodes: Dict[EpisodeId, EpisodeDescriptor]
    
    @classmethod
    def create_empty(cls) -> "EpisodeManager":
        return cls(episodes={})
    
    def to_descriptor(self) -> Dict[EpisodeId, EpisodeDescriptor]:
        return dict(self.episodes)


# =============================================================================
# UTILITIES
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "CorrelationIdType",
    "CorrelationId",
    "EpisodeId",
    "CausationChainId",
    
    # Edge metadata
    "EdgeMetadata",
    
    # Relationship kinds
    "RelationshipKind",
    
    # Error types
    "RelationshipGraphError",
    "DuplicateEdgeError",
    "CausationWithoutEvidenceError",
    
    # Edge types
    "CorrelationEdge",
    "CausationEdge",
    "EpisodeEdge",
    
    # Graph types
    "RelationshipGraphSnapshot",
    "RelationshipGraph",
    
    # Traversal types
    "TraversalDirection",
    "TraversalResult",
    "RelationshipGraphTraversal",
    
    # Episode management
    "EpisodeDescriptor",
    "EpisodeManager",
]