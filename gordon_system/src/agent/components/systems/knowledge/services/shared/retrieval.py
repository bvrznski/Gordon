"""Retrieval Service - Phase 6.9 Part 2 Section 6.

This module implements the canonical contract for semantic artifact retrieval
in Knowledge Services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# RETRIEVAL STRATEGY - Phase 6.9 Part 2 Section 6
# =============================================================================


class RetrievalStrategy(Enum):
    """
    Strategies for semantic retrieval.
    
    Direct Access:
        IDENTITY      -> Exact identity-based retrieval
        CATEGORICAL   -> Category/type-based retrieval
    
    Graph-Based:
        GRAPH         -> Graph structure-based retrieval
        NAVIGATION    -> Traversal-based retrieval
        
    Semantic-Based:
        SEMANTIC      -> Semantic similarity matching
        CONTEXT       -> Context-aware retrieval
    
    Complex:
        COMBINED      -> Multiple strategies combined
    """
    
    IDENTITY = "identity"
    CATEGORICAL = "categorical"
    GRAPH = "graph"
    NAVIGATION = "navigation"
    SEMANTIC = "semantic"
    CONTEXT = "context"
    COMBINED = "combined"


# =============================================================================
# FILTERING STRATEGY - Phase 6.9 Part 2 Section 6
# =============================================================================


class FilteringStrategy(Enum):
    """
    Strategies for result filtering.
    
    Per RETRIEVAL-LAW-003: Constraint filtering shall remain deterministic.
    """
    
    NONE = "none"                      # No filtering (raw results)
    EXACT_MATCH = "exact_match"        # Exact constraint matching
    PARTIAL_MATCH = "partial_match"    # Partial/fuzzy matching
    COMBINED = "combined"              # Multiple strategies combined


# =============================================================================
# RANKING STRATEGY - Phase 6.9 Part 2 Section 6
# =============================================================================


class RankingStrategy(Enum):
    """
    Strategies for result ranking.
    
    Per RETRIEVAL-LAW-002: Retrieval ranking strategy shall remain explicit.
    """
    
    NONE = "none"                      # No ranking (natural order)
    CONFIDENCE = "confidence"          # Rank by confidence scores
    RELEVANCE = "relevance"            # Rank by relevance score
    ALPHABETICAL = "alphabetical"      # Alphabetical ordering
    TEMPORAL = "temporal"              # Time-based ordering


# =============================================================================
# RETRIEVED ARTIFACT - Phase 6.9 Part 2 Section 6
# =============================================================================


@dataclass(frozen=True)
class RetrievedArtifact:
    """
    Artifact retrieved from the knowledge base.
    
    Per RETRIEVAL-LAW-001: Retrieval shall preserve semantic identity.
    
    Fields:
        artifact_identity: Unique identifier for this artifact
        artifact_kind: Kind of artifact (concept, assertion, etc.)
        confidence: Confidence score for retrieval (0.0 - 1.0)
        source_info: Information about where this was retrieved from
    """
    
    artifact_identity: str
    artifact_kind: str
    confidence: float = 1.0
    source_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert retrieved artifact to dictionary."""
        return {
            "artifact_identity": self.artifact_identity,
            "artifact_kind": self.artifact_kind,
            "confidence": self.confidence,
            "source_info": dict(self.source_info),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RetrievedArtifact:
        """Create retrieved artifact from dictionary."""
        return cls(
            artifact_identity=data.get("artifact_identity", ""),
            artifact_kind=data.get("artifact_kind", "unknown"),
            confidence=float(data.get("confidence", 1.0)),
            source_info=dict(data.get("source_info", {})),
        )


# =============================================================================
# RETRIEVAL PIPELINE - Phase 6.9 Part 2 Section 6
# =============================================================================


@dataclass(frozen=True)
class RetrievalPipeline:
    """
    Execution pipeline for retrieval operations.
    
    Per RETRIEVAL-LAW-004: Retrieval provenance shall remain complete.
    Per RETRIEVAL-LAW-005: Retrieval diagnostics shall remain reconstructable.
    
    Fields:
        pipeline_identity: Unique identifier for this pipeline
        participating_steps: Ordered list of pipeline steps
        filtering_strategy: Strategy used for filtering
        ranking_strategy: Strategy used for ranking
        
    Pipeline Steps (Part 2 Section 6):
        1. Query
        2. Candidate Retrieval
        3. Constraint Filtering
        4. Ranking
        5. Validation
        6. Result Publication
    """
    
    pipeline_identity: str  # Unique identifier
    
    # Pipeline steps (required)
    participating_steps: Tuple[str, ...]
    
    # Strategies (required per LAW-002, LAW-003)
    filtering_strategy: FilteringStrategy
    ranking_strategy: RankingStrategy
    
    # Diagnostics (for reconstruction - Per LAW-005)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate pipeline after creation."""
        if not self.pipeline_identity:
            raise ValueError("pipeline_identity cannot be empty")
    
    @classmethod
    def create_default(
        cls,
    ) -> "RetrievalPipeline":
        """
        Create a default retrieval pipeline.
        
        Returns:
            New RetrievalPipeline with standard steps and strategies
        """
        return cls(
            pipeline_identity=f"retrieval-pipeline:{uuid.uuid4().hex[:16]}",
            participating_steps=(
                "query_validation",
                "candidate_retrieval",
                "constraint_filtering",
                "ranking",
                "validation",
                "result_publication",
            ),
            filtering_strategy=FilteringStrategy.EXACT_MATCH,
            ranking_strategy=RankingStrategy.CONFIDENCE,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary for serialization."""
        return {
            "pipeline_identity": self.pipeline_identity,
            "participating_steps": list(self.participating_steps),
            "filtering_strategy": self.filtering_strategy.value,
            "ranking_strategy": self.ranking_strategy.value,
            "diagnostics": dict(self.diagnostics),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RetrievalPipeline":
        """Create pipeline from dictionary."""
        return cls(
            pipeline_identity=data.get("pipeline_identity", str(uuid.uuid4())),
            participating_steps=tuple(data.get("participating_steps", [])),
            filtering_strategy=FilteringStrategy(data.get("filtering_strategy", "exact_match")),
            ranking_strategy=RankingStrategy(data.get("ranking_strategy", "confidence")),
            diagnostics=dict(data.get("diagnostics", {})),
        )


# =============================================================================
# KNOWLEDGE RETRIEVAL - Phase 6.9 Part 2 Section 4
# =============================================================================


@dataclass(frozen=True)
class KnowledgeRetrieval:
    """
    Semantic artifact retrieval operation result.
    
    Per RETRIEVAL-LAW-001: Retrieval shall preserve semantic identity.
    Per RETRIEVAL-LAW-006: Retrieval shall never fabricate semantic artifacts.
    
    Fields:
        retrieval_identity: Unique identifier for this retrieval
        retrieval_strategy: Strategy used for retrieval
        participating_sources: Sources that participated in retrieval
        retrieved_artifacts: Artifacts successfully retrieved
        
    Invariants:
        * Semantic identities are preserved (RETRIEVAL-LAW-001)
        * No artifacts are fabricated (RETRIEVAL-LAW-006)
        * Results remain deterministic (implied by Phase 6.9 laws)
    """
    
    retrieval_identity: str  # Unique identifier
    
    # Retrieval strategy (required)
    retrieval_strategy: RetrievalStrategy
    
    # Participating sources
    participating_sources: Tuple[str, ...]
    
    # Retrieved artifacts (may be empty if none found)
    retrieved_artifacts: Tuple[RetrievedArtifact, ...]
    
    # Confidence in results (0.0 - 1.0)
    confidence: float = 0.0
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate retrieval result after creation."""
        if not self.retrieval_identity:
            raise ValueError("retrieval_identity cannot be empty")
    
    @property
    def artifact_count(self) -> int:
        """Number of artifacts retrieved."""
        return len(self.retrieved_artifacts)
    
    @classmethod
    def create_initial(
        cls,
        retrieval_strategy: RetrievalStrategy,
        sources: List[str],
    ) -> "KnowledgeRetrieval":
        """
        Create a new initial knowledge retrieval.
        
        Args:
            retrieval_strategy: Strategy to use for retrieval
            sources: Sources to query
            
        Returns:
            New KnowledgeRetrieval with empty results
        """
        return cls(
            retrieval_identity=f"retrieval:{uuid.uuid4().hex[:16]}",
            retrieval_strategy=retrieval_strategy,
            participating_sources=tuple(sources),
            retrieved_artifacts=tuple(),
            provenance=(
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Knowledge retrieval initialization",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ),
        )
    
    def add_artifact(
        self,
        artifact: RetrievedArtifact,
    ) -> "KnowledgeRetrieval":
        """Add a retrieved artifact and return new result."""
        # Recalculate confidence based on average of all artifacts
        all_confidences = [a.confidence for a in self.retrieved_artifacts] + [artifact.confidence]
        avg_confidence = sum(all_confidences) / len(all_confidences)
        
        return KnowledgeRetrieval(
            retrieval_identity=self.retrieval_identity,
            retrieval_strategy=self.retrieval_strategy,
            participating_sources=self.participating_sources,
            retrieved_artifacts=tuple(list(self.retrieved_artifacts) + [artifact]),
            confidence=avg_confidence,
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Added retrieved artifact: {artifact.artifact_identity}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert retrieval result to dictionary for serialization."""
        return {
            "retrieval_identity": self.retrieval_identity,
            "retrieval_strategy": self.retrieval_strategy.value,
            "participating_sources": list(self.participating_sources),
            "retrieved_artifacts": [a.to_dict() for a in self.retrieved_artifacts],
            "confidence": self.confidence,
            "provenance": list(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeRetrieval":
        """Create retrieval result from dictionary."""
        artifacts = []
        for a_data in data.get("retrieved_artifacts", []):
            if isinstance(a_data, dict):
                artifacts.append(RetrievedArtifact.from_dict(a_data))
        
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            retrieval_identity=data.get("retrieval_identity", str(uuid.uuid4())),
            retrieval_strategy=RetrievalStrategy(data.get("retrieval_strategy", "identity")),
            participating_sources=tuple(data.get("participating_sources", [])),
            retrieved_artifacts=tuple(artifacts),
            confidence=float(data.get("confidence", 0.0)),
            provenance=tuple(provenance),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Retrieval strategies (Part 2 Section 6)
    "RetrievalStrategy",
    # Filtering strategies (Part 2 Section 6)
    "FilteringStrategy",
    # Ranking strategies (Part 2 Section 6)
    "RankingStrategy",
    # Retrieved artifact
    "RetrievedArtifact",
    # Retrieval pipeline
    "RetrievalPipeline",
    # Knowledge retrieval
    "KnowledgeRetrieval",
]