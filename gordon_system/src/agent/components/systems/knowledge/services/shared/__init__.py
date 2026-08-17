"""Shared Service Contracts - Phase 6.9 Part 2 Section 23.

This module implements the canonical knowledge service infrastructure that
provides deterministic, traceable semantic access to Gordon's Knowledge Graph.
"""

from .descriptor import (
    KnowledgeServiceDescriptor,
    ServiceKind,
    LifecycleState,
    SupportedArtifact,
    ProvenanceRecord,
)

from .query_session import (
    QuerySession,
    KnowledgeQuery,
    QueryKind,
    Constraint,
    OrderingDirection,
)

from .lookup import (
    SemanticLookup,
    LookupStrategy,
    AmbiguityKind,
    ResolvedArtifact,
)

from .retrieval import (
    KnowledgeRetrieval,
    RetrievalStrategy,
    FilteringStrategy,
    RankingStrategy,
    RetrievedArtifact,
    RetrievalPipeline,
)

from .navigation import (
    NavigationSession,
    TraversalStrategy,
    TerminationCondition,
    NavigationPath,
)

from .explanation import (
    KnowledgeExplanation,
    ExplanationScope,
    ExplanationGraph,
    ExplanationGraphNode,
    ExplanationGraphEdge,
    ExplanationPipeline,
)

from .discovery import (
    KnowledgeDiscovery,
    DiscoveryMethod,
    DiscoveryCandidate,
    DiscoveryPipeline,
)

from .analytics import (
    KnowledgeAnalytics,
    KnowledgeMetrics,
    AnalyticsFinding,
    AnalyticsPipeline,
)

from .cache import (
    KnowledgeCache,
    InvalidationPolicy,
    FreshnessPolicy,
)

from .governance import (
    KnowledgeServiceGovernance,
    GovernanceFinding,
)

__all__ = [
    # Service descriptor (Part 2 Section 1)
    "KnowledgeServiceDescriptor",
    "ServiceKind",
    "LifecycleState",
    "SupportedArtifact",
    "ProvenanceRecord",
    # Query session (Part 2 Section 2)
    "QuerySession",
    "KnowledgeQuery",
    "QueryKind",
    "Constraint",
    "OrderingDirection",
    # Lookup (Part 2 Section 5)
    "SemanticLookup",
    "LookupStrategy",
    "AmbiguityKind",
    "ResolvedArtifact",
    # Retrieval (Part 2 Section 6)
    "KnowledgeRetrieval",
    "RetrievalStrategy",
    "FilteringStrategy",
    "RankingStrategy",
    "RetrievedArtifact",
    "RetrievalPipeline",
    # Navigation (Part 2 Section 9)
    "NavigationSession",
    "TraversalStrategy",
    "TerminationCondition",
    "NavigationPath",
    # Explanation (Part 2 Section 10, 11)
    "KnowledgeExplanation",
    "ExplanationScope",
    "ExplanationGraph",
    "ExplanationGraphNode",
    "ExplanationGraphEdge",
    "ExplanationPipeline",
    # Discovery (Part 2 Section 12, 13)
    "KnowledgeDiscovery",
    "DiscoveryMethod",
    "DiscoveryCandidate",
    "DiscoveryPipeline",
    # Analytics (Part 2 Section 16, 17)
    "KnowledgeAnalytics",
    "KnowledgeMetrics",
    "AnalyticsFinding",
    "AnalyticsPipeline",
    # Cache (Part 2 Section 18)
    "KnowledgeCache",
    "InvalidationPolicy",
    "FreshnessPolicy",
    # Governance (Part 2 Section 20)
    "KnowledgeServiceGovernance",
    "GovernanceFinding",
]