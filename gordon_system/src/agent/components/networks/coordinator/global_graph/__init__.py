# Gordon Cognitive Architecture - Phase 4.11.4
# ===========================================

"""
Global Coordination Graph Package
==================================

The Global Coordination Graph (GCG) is the persistent structural representation
of Gordon's coordinated cognitive architecture.

PACKAGE ORGANIZATION
====================
- enums.py: Canonical enumerations for node kinds, edge kinds, statuses
- graph_models.py: Core data models (graph, node, edge, partition, domain, component)
- graph_delta.py: Delta computation between revisions
- graph_builder.py: Graph construction and revision building
- graph_indexes.py: Immutable indexes for efficient lookups
- traversal.py: Graph traversal operations
- query.py: Query engine for graph exploration
- validation.py: Graph consistency validation
- serialization.py: Deterministic serialization

ARCHITECTURAL PRINCIPLES
========================
1. The GCG is purely descriptive - it does not execute cognition
2. All models are deeply immutable after construction
3. Revision lineage is preserved and queryable
4. Historical structures remain inspectable (never silently deleted)
5. Graph identity remains stable across revisions
6. Traversal never mutates graph state
7. Queries are read-only and produce explainable results

GCG VS COORDINATION PLAN
========================
- Coordination Plan: Episodic, one per coordination cycle
- Global Coordination Graph: Persistent, accumulates over time

The graph becomes Gordon's structural connectome - describing which systems
communicate, how information is routed, and where bottlenecks arise.

IMPORT SAFETY
=============
This package is import-safe:
- No filesystem access during import
- No network access during import
- No model loading during import
- No runtime initialization during import
"""

from __future__ import annotations

# Import everything from submodules to create unified public API

from .enums import (
    # Node kinds
    CoordinationGraphNodeKind,
    
    # Edge kinds  
    CoordinationGraphEdgeKind,
    
    # Statuses
    CoordinationNodeStatus,
    CoordinationEdgeStatus,
    
    # Revision and topology
    GraphRevisionKind,
    ComponentKind,
    GraphPartitionKind,
    GraphDomainKind,
    
    # Helper types
    SemanticScope,
    GraphConstructionPolicy,
)

from .graph_models import (
    GlobalCoordinationGraphIdentity,
    GlobalCoordinationGraphRevisionIdentity,
    GlobalCoordinationGraph,
    CoordinationGraphNode,
    CoordinationGraphEdge,
    CoordinationGraphPartition,
    CoordinationGraphDomain,
    CoordinationGraphComponent,
    GlobalCoordinationGraphIndexes,
)

from .graph_delta import (
    GlobalCoordinationGraphDelta,
    GraphRevisionBuildResult,
    IndexBuildResult,
)

# =============================================================================
# PUBLIC API SUMMARY
# =============================================================================

__all__ = [
    # Core enums
    "CoordinationGraphNodeKind",
    "CoordinationGraphEdgeKind",
    "CoordinationNodeStatus",
    "CoordinationEdgeStatus",
    "GraphRevisionKind",
    "ComponentKind",
    "GraphPartitionKind",
    "GraphDomainKind",
    "SemanticScope",
    "GraphConstructionPolicy",
    
    # Core models
    "GlobalCoordinationGraphIdentity",
    "GlobalCoordinationGraphRevisionIdentity",
    "GlobalCoordinationGraph",
    "CoordinationGraphNode",
    "CoordinationGraphEdge",
    "CoordinationGraphPartition",
    "CoordinationGraphDomain",
    "CoordinationGraphComponent",
    "GlobalCoordinationGraphIndexes",
    
    # Delta models
    "GlobalCoordinationGraphDelta",
    "GraphRevisionBuildResult",
    "IndexBuildResult",
]