# Case Retrieval Pipeline - Phase 7.4
# ===================================

"""
Canonical Case Retrieval Pipeline Contract.

Retrieval identifies candidate cases for analogical reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AnalogyRetrieval:
    """
    A case retrieval result from the pipeline.
    
    Retrieval evaluates:
        - Similar structure to target problem
        - Similar relations/roles
        - Similar goals
        - Similar failures
        - Similar solutions
    
    Retriever remains traceable and deterministic.
    """
    
    # Identity
    retrieval_id: str                         # Unique identifier
    
    # Target problem特征 extraction
    target_problem_features: Dict[str, Any] = field(default_factory=dict)
    
    # Retrieved cases with rankings
    retrieved_cases: Tuple[Tuple[Any, float], ...] = ()
    
    # Ranking metrics
    ranking_strategy: str = "structural_similarity"  # How were cases ranked?
    
    # Diagnostics
    retrieval_time_ms: float = 0.0            # Time spent retrieving
    candidates_evaluated: int = 0             # Total candidates examined
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def retrieval_count(self) -> int:
        """Number of cases successfully retrieved."""
        return len(self.retrieved_cases)
    
    @classmethod
    def create(
        cls,
        target_problem_features: Optional[Dict[str, Any]] = None,
        ranking_strategy: str = "structural_similarity",
    ) -> AnalogyRetrieval:
        """Create a new retrieval result."""
        return cls(
            retrieval_id=f"analogy_retrieval:{uuid.uuid4().hex[:16]}",
            target_problem_features=target_problem_features or {},
            ranking_strategy=ranking_strategy,
        )
    
    def add_case(self, case: Any, similarity_score: float) -> AnalogyRetrieval:
        """Add a retrieved case with its similarity score."""
        return dataclass_replace(
            self,
            retrieved_cases=self.retrieved_cases + ((case, similarity_score),),
        )
    
    def sorted_by_similarity(self) -> List[Tuple[Any, float]]:
        """Return cases sorted by similarity (highest first)."""
        return list(sorted(self.retrieved_cases, key=lambda x: x[1], reverse=True))


@dataclass(frozen=True)
class FeatureExtraction:
    """
    Features extracted from a problem for retrieval comparison.
    
    Extracted features include:
        - Structural elements (entities, relations)
        - Goal specifications
        - Constraint descriptions
        - Failure patterns (if applicable)
        - Solution templates
    """
    
    # Identity
    extraction_id: str                        # Unique identifier
    
    # Feature categories
    structural_features: Dict[str, Any] = field(default_factory=dict)  # Graph structure
    relational_features: Dict[str, Any] = field(default_factory=dict)  # Relations between elements
    goal_features: Tuple[str, ...] = ()     # High-level goals
    constraint_features: Tuple[str, ...] = ()  # Constraints and limitations
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        structural: Optional[Dict[str, Any]] = None,
        relational: Optional[Dict[str, Any]] = None,
        goals: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> FeatureExtraction:
        """Create feature extraction result."""
        return cls(
            extraction_id=f"feature_extraction:{uuid.uuid4().hex[:16]}",
            structural_features=structural or {},
            relational_features=relational or {},
            goal_features=tuple(goals or []),
            constraint_features=tuple(constraints or []),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AnalogyRetrieval",
    "FeatureExtraction",
]