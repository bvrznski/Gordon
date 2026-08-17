"""Explanation Service - Phase 6.9 Part 2 Section 10.

This module implements the canonical contract for explanation generation
in Knowledge Services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# EXPLANATION SCOPE - Phase 6.9 Part 2 Section 10
# =============================================================================


class ExplanationScope(Enum):
    """
    Scope of explanations.
    
    Per EXPLANATION-LAW-003: Evidence shall remain traceable.
    
    Types:
        WHY         -> Cause/effect explanation
        HOW         -> Mechanism/process explanation
        WHERE       -> Location/spatial explanation
        WHAT        -> Definition/fact explanation
        WHICH       -> Choice/selection explanation
    """
    
    WHY = "why"
    HOW = "how"
    WHERE = "where"
    WHAT = "what"
    WHICH = "which"


# =============================================================================
# EXPLANATION GRAPH NODE - Phase 6.9 Part 2 Section 10
# =============================================================================


@dataclass(frozen=True)
class ExplanationGraphNode:
    """
    Node in the explanation graph.
    
    Per EXPLANATION-LAW-002: Explanation paths shall remain explicit.
    
    Fields:
        node_identity: Unique identifier for this node
        node_kind: Kind of explanation node (evidence, inference, etc.)
        content: Content of this node
        confidence: Confidence in this node's validity
    """
    
    node_identity: str  # Unique identifier
    
    node_kind: str  # "evidence", "inference", "rule", "concept", etc.
    content: Dict[str, Any]
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "node_identity": self.node_identity,
            "node_kind": self.node_kind,
            "content": dict(self.content),
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExplanationGraphNode:
        """Create node from dictionary."""
        return cls(
            node_identity=data.get("node_identity", str(uuid.uuid4())),
            node_kind=data.get("node_kind", "evidence"),
            content=dict(data.get("content", {})),
            confidence=float(data.get("confidence", 1.0)),
        )


# =============================================================================
# EXPLANATION GRAPH EDGE - Phase 6.9 Part 2 Section 10
# =============================================================================


@dataclass(frozen=True)
class ExplanationGraphEdge:
    """
    Edge in the explanation graph.
    
    Per EXPLANATION-LAW-001: Every Explanation references supporting semantic artifacts.
    
    Fields:
        edge_identity: Unique identifier for this edge
        source_node: Source node of this edge
        target_node: Target node of this edge
        relation_kind: Kind of relationship between nodes
        evidence: Supporting evidence for this relation
    """
    
    edge_identity: str  # Unique identifier
    
    source_node: str
    target_node: str
    relation_kind: str  # "supports", "explains", "implies", etc.
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "edge_identity": self.edge_identity,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "relation_kind": self.relation_kind,
            "evidence": list(self.evidence),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExplanationGraphEdge:
        """Create edge from dictionary."""
        return cls(
            edge_identity=data.get("edge_identity", str(uuid.uuid4())),
            source_node=data.get("source_node", ""),
            target_node=data.get("target_node", ""),
            relation_kind=data.get("relation_kind", "supports"),
            evidence=tuple(data.get("evidence", [])),
        )


# =============================================================================
# EXPLANATION GRAPH - Phase 6.9 Part 2 Section 10
# =============================================================================


@dataclass(frozen=True)
class ExplanationGraph:
    """
    Graph representation of an explanation.
    
    Per EXPLANATION-LAW-004: Explanation provenance shall remain complete.
    
    Fields:
        graph_identity: Unique identifier for this explanation graph
        nodes: Nodes in the graph (evidence, inferences, etc.)
        edges: Edges representing relationships between nodes
        
    Invariants:
        * Every node has supporting evidence (EXPLANATION-LAW-001)
        * Paths remain explicit (EXPLANATION-LAW-002)
        * Evidence is traceable (EXPLANATION-LAW-003)
    """
    
    graph_identity: str  # Unique identifier
    
    nodes: Tuple[ExplanationGraphNode, ...]
    edges: Tuple[ExplanationGraphEdge, ...]
    
    def __post_init__(self) -> None:
        """Validate graph after creation."""
        if not self.graph_identity:
            raise ValueError("graph_identity cannot be empty")
    
    @classmethod
    def create_initial(
        cls,
        root_node: Optional[ExplanationGraphNode] = None,
    ) -> "ExplanationGraph":
        """
        Create initial explanation graph.
        
        Args:
            root_node: Initial root node (optional)
            
        Returns:
            New ExplanationGraph with optional root node
        """
        nodes = (root_node,) if root_node else tuple()
        return cls(
            graph_identity=f"explanation-graph:{uuid.uuid4().hex[:16]}",
            nodes=nodes,
            edges=tuple(),
        )
    
    def add_node(
        self,
        node: ExplanationGraphNode,
    ) -> "ExplanationGraph":
        """Add a node to the explanation graph."""
        return ExplanationGraph(
            graph_identity=self.graph_identity,
            nodes=tuple(list(self.nodes) + [node]),
            edges=self.edges,
        )
    
    def add_edge(
        self,
        edge: ExplanationGraphEdge,
    ) -> "ExplanationGraph":
        """Add an edge between explanation nodes."""
        # Verify source and target exist in graph
        existing_node_ids = {n.node_identity for n in self.nodes}
        if edge.source_node not in existing_node_ids:
            raise ValueError(f"Source node '{edge.source_node}' not in graph")
        if edge.target_node not in existing_node_ids:
            raise ValueError(f"Target node '{edge.target_node}' not in graph")
        
        return ExplanationGraph(
            graph_identity=self.graph_identity,
            nodes=self.nodes,
            edges=tuple(list(self.edges) + [edge]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary."""
        return {
            "graph_identity": self.graph_identity,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExplanationGraph":
        """Create graph from dictionary."""
        nodes = []
        edges = []
        
        for n_data in data.get("nodes", []):
            if isinstance(n_data, dict):
                nodes.append(ExplanationGraphNode.from_dict(n_data))
        
        for e_data in data.get("edges", []):
            if isinstance(e_data, dict):
                edges.append(ExplanationGraphEdge.from_dict(e_data))
        
        return cls(
            graph_identity=data.get("graph_identity", str(uuid.uuid4())),
            nodes=tuple(nodes),
            edges=tuple(edges),
        )


# =============================================================================
# EXPLANATION PIPELINE - Phase 6.9 Part 2 Section 11
# =============================================================================


@dataclass(frozen=True)
class ExplanationPipeline:
    """
    Pipeline for generating explanations.
    
    Per EXPLANATION-LAW-004: Explanation provenance shall remain complete.
    
    Pipeline Steps (Part 2 Section 10):
        1. Question - The question to be explained
        2. Relevant Artifacts - Find supporting artifacts
        3. Dependency Expansion - Expand dependencies
        4. Evidence Collection - Collect evidence
        5. Explanation Graph - Build explanation graph
        6. Explanation - Generate final explanation
        
    Fields:
        pipeline_identity: Unique identifier for this pipeline
        explanation_scope: Scope of the explanation
        supporting_artifacts: Artifacts used in explanation
        
    Invariants:
        * Explanations remain traceable (EXPLANATION-LAW-001)
        * Paths are explicit (EXPLANATION-LAW-002)
        * Evidence is traceable (EXPLANATION-LAW-003)
    """
    
    pipeline_identity: str  # Unique identifier
    
    # Scope (required)
    explanation_scope: ExplanationScope
    
    # Supporting artifacts
    supporting_artifacts: Tuple[str, ...]
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate pipeline after creation."""
        if not self.pipeline_identity:
            raise ValueError("pipeline_identity cannot be empty")
    
    @classmethod
    def create_initial(
        cls,
        scope: ExplanationScope,
        question_artifact: Optional[str] = None,
    ) -> "ExplanationPipeline":
        """
        Create initial explanation pipeline.
        
        Args:
            scope: Scope of the explanation
            question_artifact: Artifact being explained (optional)
            
        Returns:
            New ExplanationPipeline ready for processing
        """
        artifacts = (question_artifact,) if question_artifact else tuple()
        
        return cls(
            pipeline_identity=f"explanation-pipeline:{uuid.uuid4().hex[:16]}",
            explanation_scope=scope,
            supporting_artifacts=artifacts,
        )
    
    def add_supporting_artifact(
        self,
        artifact: str,
    ) -> "ExplanationPipeline":
        """Add a supporting artifact to the pipeline."""
        return ExplanationPipeline(
            pipeline_identity=self.pipeline_identity,
            explanation_scope=self.explanation_scope,
            supporting_artifacts=tuple(list(self.supporting_artifacts) + [artifact]),
            diagnostics=dict(self.diagnostics),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary."""
        return {
            "pipeline_identity": self.pipeline_identity,
            "explanation_scope": self.explanation_scope.value,
            "supporting_artifacts": list(self.supporting_artifacts),
            "diagnostics": dict(self.diagnostics),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExplanationPipeline":
        """Create pipeline from dictionary."""
        return cls(
            pipeline_identity=data.get("pipeline_identity", str(uuid.uuid4())),
            explanation_scope=ExplanationScope(data.get("explanation_scope", "why")),
            supporting_artifacts=tuple(data.get("supporting_artifacts", [])),
            diagnostics=dict(data.get("diagnostics", {})),
        )


# =============================================================================
# KNOWLEDGE EXPLANATION - Phase 6.9 Part 2 Section 8
# =============================================================================


@dataclass(frozen=True)
class KnowledgeExplanation:
    """
    Generated explanation from knowledge services.
    
    Per EXPLANATION-LAW-001: Every Explanation references supporting semantic artifacts.
    Per EXPLANATION-LAW-007: Explanation shall remain independently inspectable.
    
    Fields:
        explanation_identity: Unique identifier for this explanation
        supporting_artifacts: Semantic artifacts supporting this explanation
        explanation_graph: Graph representation of the explanation
        
    Invariants:
        * Explanations reference supporting artifacts (EXPLANATION-LAW-001)
        * Paths are explicit (EXPLANATION-LAW-002)
        * Evidence is traceable (EXPLANATION-LAW-003)
    """
    
    explanation_identity: str  # Unique identifier
    
    # Supporting artifacts
    supporting_artifacts: Tuple[str, ...]
    
    # Graph representation
    explanation_graph: ExplanationGraph
    
    # Scope of the explanation
    explanation_scope: ExplanationScope = ExplanationScope.WHY
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate explanation after creation."""
        if not self.explanation_identity:
            raise ValueError("explanation_identity cannot be empty")
    
    @property
    def artifact_count(self) -> int:
        """Number of supporting artifacts."""
        return len(self.supporting_artifacts)
    
    @classmethod
    def create_initial(
        cls,
        question: str,
        scope: ExplanationScope = ExplanationScope.WHY,
    ) -> "KnowledgeExplanation":
        """
        Create initial explanation structure.
        
        Args:
            question: Question being explained
            scope: Scope of the explanation
            
        Returns:
            New KnowledgeExplanation ready for processing
        """
        graph = ExplanationGraph.create_initial(
            root_node=ExplanationGraphNode(
                node_identity=f"question:{uuid.uuid4().hex[:16]}",
                node_kind="question",
                content={"text": question},
            )
        )
        
        return cls(
            explanation_identity=f"explanation:{uuid.uuid4().hex[:16]}",
            supporting_artifacts=tuple(),
            explanation_graph=graph,
            explanation_scope=scope,
            provenance=(
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Explanation generation initialization",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert explanation to dictionary."""
        return {
            "explanation_identity": self.explanation_identity,
            "supporting_artifacts": list(self.supporting_artifacts),
            "explanation_graph": self.explanation_graph.to_dict(),
            "explanation_scope": self.explanation_scope.value,
            "provenance": list(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeExplanation":
        """Create explanation from dictionary."""
        return cls(
            explanation_identity=data.get("explanation_identity", str(uuid.uuid4())),
            supporting_artifacts=tuple(data.get("supporting_artifacts", [])),
            explanation_graph=ExplanationGraph.from_dict(data.get("explanation_graph", {})),
            explanation_scope=ExplanationScope(data.get("explanation_scope", "why")),
            provenance=tuple(data.get("provenance", [])),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Explanation scopes (Part 2 Section 10)
    "ExplanationScope",
    # Explanation graph nodes
    "ExplanationGraphNode",
    # Explanation graph edges
    "ExplanationGraphEdge",
    # Explanation graphs
    "ExplanationGraph",
    # Explanation pipeline
    "ExplanationPipeline",
    # Knowledge explanation
    "KnowledgeExplanation",
]