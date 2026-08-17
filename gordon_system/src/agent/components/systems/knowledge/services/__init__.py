"""Knowledge Services - Phase 6.9 Knowledge Reasoning Support.

This module implements the canonical knowledge service layer that provides
deterministic, traceable semantic access to Gordon's Knowledge Graph.

Architecture (Phase 6.9 Part 1):
    Knowledge
      ↓
    Knowledge Services  <- This layer
      ↓
    Reasoning
      ↓
    Planning
      ↓
    Decision Making

The Knowledge Service layer forms Gordon's **semantic API**.
Higher cognitive systems should never manipulate Concepts, Assertions, Beliefs,
or Graphs directly. Instead, they interact through explicit services that
provide deterministic, traceable access to semantic knowledge.

This separation decouples cognitive algorithms from knowledge representation,
allowing the underlying ontology, graph organization or storage mechanisms
to evolve without affecting reasoning, planning, or learning.
"""

from .shared import (
    # Service descriptor (Part 2 Section 1)
    KnowledgeServiceDescriptor,
    ServiceKind,
    LifecycleState,
    SupportedArtifact,
    ProvenanceRecord,
    # Query session (Part 2 Section 2)
    QuerySession,
    KnowledgeQuery,
    QueryKind,
    Constraint,
    OrderingDirection,
    # Lookup (Part 2 Section 5)
    SemanticLookup,
    LookupStrategy,
    AmbiguityKind,
    ResolvedArtifact,
    # Retrieval (Part 2 Section 6)
    KnowledgeRetrieval,
    RetrievalStrategy,
    FilteringStrategy,
    RankingStrategy,
    RetrievedArtifact,
    RetrievalPipeline,
    # Navigation (Part 2 Section 9)
    NavigationSession,
    TraversalStrategy,
    TerminationCondition,
    NavigationPath,
    # Explanation (Part 2 Section 10, 11)
    KnowledgeExplanation,
    ExplanationScope,
    ExplanationGraph,
    ExplanationGraphNode,
    ExplanationGraphEdge,
    ExplanationPipeline,
    # Discovery (Part 2 Section 12, 13)
    KnowledgeDiscovery,
    DiscoveryMethod,
    DiscoveryCandidate,
    DiscoveryPipeline,
    # Analytics (Part 2 Section 16, 17)
    KnowledgeAnalytics,
    KnowledgeMetrics,
    AnalyticsFinding,
    AnalyticsPipeline,
    # Cache (Part 2 Section 18)
    KnowledgeCache,
    InvalidationPolicy,
    FreshnessPolicy,
    # Governance (Part 2 Section 20)
    KnowledgeServiceGovernance,
    GovernanceFinding,
)

from .shared.validation import (
    ValidationResult,
    ServiceValidation,
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
    # Validation
    "ValidationResult",
    "ServiceValidation",
]