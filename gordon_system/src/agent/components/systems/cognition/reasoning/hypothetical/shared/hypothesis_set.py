# Hypothesis Set - Phase 7.15 Part 2
# ====================================

"""
Canonical Hypothesis Set.

Hypothesis Sets define candidate hypotheses, assumptions, constraints,
exploration strategy, and termination conditions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class HypothesisIdentity:
    """
    Immutable identity for a hypothesis.
    
    Allows tracking and comparison of hypotheses across sessions.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> HypothesisIdentity:
        """Create a new hypothesis identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


@dataclass(frozen=True)
class ExplorationStrategy:
    """
    Defines how possibility space should be explored.
    
    Strategy includes:
        - Expansion pattern
        - Filtering criteria
        - Pruning rules
        - Termination conditions
    """
    
    # Strategy classification
    expansion_pattern: str                    # e.g., "breadth_first", "depth_first", "heuristic"
    filtering_criteria: Tuple[str, ...] = ()  # Criteria for candidate filtering
    pruning_rules: Tuple[str, ...] = ()       # Rules for removing candidates
    
    # Termination conditions
    max_candidates: int = 10                  # Maximum candidates before termination
    min_coverage: float = 0.5                 # Minimum coverage threshold
    time_limit_seconds: Optional[float] = None  # Optional time limit
    
    @classmethod
    def create(
        cls,
        expansion_pattern: str = "breadth_first",
        max_candidates: int = 10,
        min_coverage: float = 0.5,
        time_limit_seconds: Optional[float] = None,
    ) -> ExplorationStrategy:
        """Create a new exploration strategy."""
        return cls(
            expansion_pattern=expansion_pattern,
            filtering_criteria=(),
            pruning_rules=(),
            max_candidates=max_candidates,
            min_coverage=min_coverage,
            time_limit_seconds=time_limit_seconds,
        )


@dataclass(frozen=True)
class HypothesisSetIdentity:
    """
    Immutable identity for a hypothesis set.
    
    Allows replay and verification of hypothetical reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Set context
    set_number: int = 1                       # For repeated sets
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, set_number: int = 1) -> HypothesisSetIdentity:
        """Create a new hypothesis set identity."""
        return cls(
            semantic_identity=semantic_identity,
            set_number=set_number,
        )


@dataclass(frozen=True)
class HypothesisSet:
    """
    Immutable hypothesis set for hypothetical reasoning.
    
    A hypothesis set contains:
        - Candidate hypotheses with their supporting assumptions
        - Assumption set defining the reasoning context
        - Exploration scope and constraints
        - Provenance tracking
    
    Hypothesis sets remain immutable during exploration to ensure
    reproducibility and traceability.
    """
    
    # Identity
    hypothesis_set_id: str                    # Unique set identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Contents
    participating_hypotheses: Tuple[HypothesisIdentity, ...]  # Hypotheses in the set
    assumption_set: Tuple[str, ...] = ()      # Assumptions underlying hypotheses
    
    # Exploration scope
    exploration_scope: str                    # e.g., "global", "local", "contextual"
    constraints: Tuple[str, ...] = ()         # Constraints on candidates
    
    # Strategy
    exploration_strategy: ExplorationStrategy = field(
        default_factory=lambda: ExplorationStrategy.create()
    )
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did hypothesis set originate?
    
    @property
    def total_hypotheses(self) -> int:
        """Return the number of hypotheses in the set."""
        return len(self.participating_hypotheses)
    
    @property
    def is_empty(self) -> bool:
        """Check if hypothesis set is empty."""
        return self.total_hypotheses == 0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        hypotheses: List[HypothesisIdentity],
        exploration_scope: str = "global",
        constraints: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None,
        exploration_strategy: Optional[ExplorationStrategy] = None,
    ) -> HypothesisSet:
        """Create a new hypothesis set."""
        return cls(
            hypothesis_set_id=f"hypothesis_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_hypotheses=tuple(hypotheses),
            assumption_set=tuple(assumptions or []),
            exploration_scope=exploration_scope,
            constraints=tuple(constraints or []),
            exploration_strategy=exploration_strategy or ExplorationStrategy.create(),
        )
    
    def with_hypothesis(self, hypothesis: HypothesisIdentity) -> "HypothesisSet":
        """Return a copy with the hypothesis added."""
        new_hypotheses = self.participating_hypotheses + (hypothesis,)
        return dataclass_replace(
            self,
            participating_hypotheses=new_hypotheses,
        )
    
    def without_hypothesis(self, hypothesis: HypothesisIdentity) -> "HypothesisSet":
        """Return a copy with the hypothesis removed."""
        new_hypotheses = tuple(h for h in self.participating_hypotheses if h != hypothesis)
        return dataclass_replace(
            self,
            participating_hypotheses=new_hypotheses,
        )


@dataclass(frozen=True)
class AssumptionSet:
    """
    Set of assumptions underlying a hypothesis set.
    
    Assumptions include:
        - Physical assumptions
        - Logical assumptions  
        - Semantic assumptions
        - Environmental assumptions
        - Resource assumptions
    """
    
    # Identity
    assumption_set_id: str                    # Unique set identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Contents
    explicit_assumptions: Tuple[str, ...]     # Explicitly stated assumptions
    
    # Dependency tracking
    dependency_graph: Dict[str, Tuple[str, ...]] = field(default_factory=dict)  # assumption -> dependencies
    
    # Justification
    justification: str = "default"            # How are these assumptions justified?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        explicit_assumptions: List[str],
        dependency_graph: Optional[Dict[str, List[str]]] = None,
        justification: str = "default",
    ) -> AssumptionSet:
        """Create a new assumption set."""
        return cls(
            assumption_set_id=f"assumption_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            explicit_assumptions=tuple(explicit_assumptions),
            dependency_graph={k: tuple(v) for k, v in (dependency_graph or {}).items()},
            justification=justification,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HypothesisIdentity",
    "ExplorationStrategy",
    "HypothesisSetIdentity",
    "HypothesisSet",
    "AssumptionSet",
]