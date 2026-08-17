# Strategy Selection - Phase 7.13
# ================================

"""
Canonical Strategy Selection definition.

Strategy selection determines which reasoning strategy to use based on
problem characteristics and available resources.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class StrategyKind(Enum):
    """Types of reasoning strategies."""
    
    # Single-reasoner strategies
    SINGLE_REASONER = "single_reasoner"           # Use single reasoner
    
    # Multi-reasoner strategies  
    MULTI_REASONER = "multi_reasoner"             # Parallel multi-reasoner
    HIERARCHICAL = "hierarchical"                 # Hierarchical reasoning
    COMPOSITIONAL = "compositional"               # Chain of reasoners
    
    # Advanced strategies
    ITERATIVE_REFINEMENT = "iterative_refinement"  # Iterative improvement
    COMPETITIVE = "competitive"                   # Multiple competing reasoners
    PARALLEL = "parallel"                         # Fully parallel execution
    CONSENSUS = "consensus"                       # Consensus voting


class SelectionRationale(Enum):
    """Rationale for strategy selection."""
    
    PROBLEM_CHARACTERIZATION = "problem_characterization"  # Problem structure matched
    CAPABILITY_MATCHING = "capability_matching"            # Capabilities aligned
    RESOURCE_AVAILABILITY = "resource_availability"        # Resources available
    HISTORY_SUCCESS = "history_success"                     # Past success with strategy
    TIME_CONSTRAINTS = "time_constraints"                   # Time budget considerations
    QUALITY_GOALS = "quality_goals"                         # Quality requirements
    UNCERTAINTY_MANAGEMENT = "uncertainty_management"       # Uncertainty handling needs


@dataclass(frozen=True)
class StrategySelection:
    """
    Strategy selection result from meta-reasoning.
    
    A strategy selection contains:
        - Identity and provenance
        - Candidate strategies evaluated
        - Selected strategy with rationale
        - Execution policy details
    
    Strategy selection remains deterministic given identical inputs.
    """
    
    # Identity
    selection_id: str                       # Unique selection identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Candidates considered
    candidate_strategies: List[StrategyKind]  # All strategies evaluated
    
    # Selection result
    selected_strategy: StrategyKind         # Selected reasoning strategy
    
    # Rationale
    selection_rationale: List[SelectionRationale]  # Why this strategy?
    
    # Execution policy
    execution_policy: Dict[str, Any] = field(default_factory=dict)  # Strategy-specific config
    
    # Resource allocation
    allocated_resources: Dict[str, float] = field(default_factory=dict)  # Resources assigned
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    selected_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate time taken for selection."""
        if self.selected_at_utc:
            return self.selected_at_utc - self.created_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        candidate_strategies: List[StrategyKind],
        selected_strategy: StrategyKind,
        selection_rationale: Optional[List[SelectionRationale]] = None,
    ) -> StrategySelection:
        """Create a new strategy selection."""
        if selection_rationale is None:
            selection_rationale = [SelectionRationale.PROBLEM_CHARACTERIZATION]
        
        return cls(
            selection_id=f"strategy_selection:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            candidate_strategies=candidate_strategies,
            selected_strategy=selected_strategy,
            selection_rationale=selection_rationale,
            selected_at_utc=time.time(),
        )
    
    def with_policy(self, policy: Dict[str, Any]) -> StrategySelection:
        """Return a copy with updated execution policy."""
        return dataclass_replace(
            self,
            execution_policy=policy,
        )
    
    def with_resources(self, resources: Dict[str, float]) -> StrategySelection:
        """Return a copy with updated resource allocation."""
        return dataclass_replace(
            self,
            allocated_resources=resources,
        )
    
    def to_completed(self) -> StrategySelection:
        """Mark selection as completed."""
        return dataclass_replace(
            self,
            selected_at_utc=time.time(),
        )


@dataclass(frozen=True)
class StrategyEvaluation:
    """
    Evaluation of a reasoning strategy for a given problem.
    
    Used during strategy selection to compare alternatives.
    """
    
    # Identity
    evaluation_id: str                      # Unique evaluation identifier
    
    # Strategy being evaluated
    strategy_kind: StrategyKind             # Which strategy?
    
    # Evaluation metrics
    estimated_success_rate: float           # Expected success probability (0-1)
    estimated_completion_time_seconds: float  # Expected duration
    resource_cost: Dict[str, float]         # Resources required
    
    # Quality estimates
    expected_quality_score: float = 0.0     # Quality estimate (0-1)
    confidence_level: float = 0.0           # Confidence in estimate (0-1)
    
    # Risks
    failure_risk: float = 0.0               # Failure probability
    uncertainty_level: float = 0.0          # Uncertainty about estimates
    
    @classmethod
    def create(
        cls,
        strategy_kind: StrategyKind,
        estimated_success_rate: float,
        estimated_completion_time_seconds: float,
        resource_cost: Optional[Dict[str, float]] = None,
    ) -> StrategyEvaluation:
        """Create a new strategy evaluation."""
        return cls(
            evaluation_id=f"strategy_eval:{uuid.uuid4().hex[:16]}",
            strategy_kind=strategy_kind,
            estimated_success_rate=estimated_success_rate,
            estimated_completion_time_seconds=estimated_completion_time_seconds,
            resource_cost=resource_cost or {},
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StrategySelection",
    "StrategyKind",
    "SelectionRationale",
    "StrategyEvaluation",
]