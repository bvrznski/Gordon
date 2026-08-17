"""Graphs - Knowledge Graph organization for Gordon Cognitive Architecture (Phase 6.8).

This module implements the canonical semantic organization layer that integrates
all Knowledge Artifacts into one navigable semantic structure.

Knowledge Graphs provide:
    * Semantic connectivity across all artifacts
    * Multi-layer graph organization
    * Cross-domain navigation
    * Subgraph management
    * Graph indexing and traversal
    * Graph governance and validation

Architecture Summary (Phase 6.8):
    Concepts → Assertions → Relations → Beliefs → Models → KnowledgeGraph
                                                                  ↓
                                                          Reasoning
                                                                  ↓
                                                          Planning
                                                                  ↓
                                                       Decision Making
"""

from .shared.descriptor import GraphDescriptor, GraphKind, GraphLifecycleState
from .shared.graph import KnowledgeGraph, KnowledgeSubgraph
from .shared.node import GraphNode
from .shared.edge import GraphEdge, EdgeDirection
from .shared.topology import (
    GraphTopology,
    TopologyKind,
    GraphMetrics,
)
from .shared.layer import GraphLayer, LayerKind, InterLayerMapping
from .shared.traversal import GraphTraversalSession, TraversalStrategy
from .shared.indexing import GraphIndex, GraphIndexEntry, IndexingStrategy
from .shared.composition import GraphComposition, CompositionStrategy
from .shared.partition import GraphPartition, PartitionStrategy
from .shared.validation import GraphValidation, ValidationResult
from .shared.governance import GraphGovernance, GovernanceFindings
from .shared.health import GraphHealth, HealthMetrics
from .shared.diagnostics import GraphDiagnostic, GraphDiagnosticsReport

__all__ = [
    # Descriptors and kinds
    "GraphDescriptor",
    "GraphKind",
    "GraphLifecycleState",
    # Nodes and edges
    "GraphNode",
    "GraphEdge",
    "EdgeDirection",
    # Topology
    "GraphTopology",
    "TopologyKind",
    "GraphMetrics",
    # Layers
    "GraphLayer",
    "LayerKind",
    "InterLayerMapping",
    # Traversal
    "GraphTraversalSession",
    "TraversalStrategy",
    # Indexing
    "GraphIndex",
    "GraphIndexEntry",
    "IndexingStrategy",
    # Composition and partition
    "GraphComposition",
    "CompositionStrategy",
    "GraphPartition",
    "PartitionStrategy",
    # Validation
    "GraphValidation",
    "ValidationResult",
    # Governance
    "GraphGovernance",
    "GovernanceFindings",
    # Health
    "GraphHealth",
    "HealthMetrics",
    # Diagnostics
    "GraphDiagnostic",
    "GraphDiagnosticsReport",
    # Graphs (Part 1 Section 2, 10)
    "KnowledgeGraph",
    "KnowledgeSubgraph",
]