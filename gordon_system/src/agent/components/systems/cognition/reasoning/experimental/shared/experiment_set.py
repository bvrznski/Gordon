# Experimental Reasoning - Experiment Set
# ========================================

"""
Canonical Experiment Set.

An experiment set defines candidate experiments, tested hypotheses,
measurement plans, resource limits, and evaluation criteria.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExperimentSetIdentity:
    """
    Immutable identity for an experiment set.
    
    Allows replay and verification of experiment set results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Set context
    set_number: int = 1                      # For repeated sets
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, set_number: int = 1) -> ExperimentSetIdentity:
        """Create a new experiment set identity."""
        return cls(
            semantic_identity=semantic_identity,
            set_number=set_number,
        )


class EvaluationScope(Enum):
    """Scopes for evaluating experiments in the set."""
    
    ALL = "all"                               # Evaluate all experiments
    TOP_N = "top_n"                          # Only evaluate top N candidates
    THRESHOLD = "threshold"                  # Only evaluate above threshold
    SEQUENTIAL = "sequential"                # Sequential evaluation until success


@dataclass(frozen=True)
class ExperimentSet:
    """
    Immutable set of candidate experiments.
    
    An experiment set defines:
        - Candidate experiments for testing hypotheses
        - Tested hypotheses (theories under investigation)
        - Measurement plans for each experiment
        - Resource limits and constraints
        - Evaluation criteria for experimental selection
    
    Experiment sets remain immutable during design, allowing replay
    and verification of the design process.
    """
    
    # Identity
    set_identity: str                        # Unique identifier
    semantic_identity: str                   # Stable identity across runs
    
    # Participating experiments
    participating_experiments: Tuple[str, ...]  # Experiment identities (descriptions)
    
    # Tested hypotheses
    tested_hypotheses: Tuple[str, ...]       # Hypotheses being evaluated
    
    # Evaluation scope
    evaluation_scope: EvaluationScope = EvaluationScope.ALL
    top_n_count: int = 5                     # For TOP_N mode
    threshold: float = 0.5                   # For THRESHOLD mode
    
    # Resource constraints
    max_experiments: int = 100               # Maximum candidate experiments
    resource_limits: Dict[str, float] = field(default_factory=dict)  # e.g., "time": 3600, "cost": 1000
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did experiment set originate?
    
    @property
    def experiment_count(self) -> int:
        """Get the number of experiments in the set."""
        return len(self.participating_experiments)
    
    @property
    def hypothesis_count(self) -> int:
        """Get the number of tested hypotheses."""
        return len(self.tested_hypotheses)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        experiments: List[str],
        hypotheses: List[str],
        origin_context: str = "unknown",
        evaluation_scope: EvaluationScope = EvaluationScope.ALL,
        top_n_count: int = 5,
        threshold: float = 0.5,
    ) -> ExperimentSet:
        """Create a new experiment set."""
        return cls(
            set_identity=f"experiment_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_experiments=tuple(experiments),
            tested_hypotheses=tuple(hypotheses),
            origin_context=origin_context,
            evaluation_scope=evaluation_scope,
            top_n_count=top_n_count,
            threshold=threshold,
        )


__all__ = [
    "ExperimentSetIdentity",
    "EvaluationScope",
    "ExperimentSet",
]