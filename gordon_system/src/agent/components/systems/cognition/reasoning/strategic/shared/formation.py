# Strategic Formation - Phase 7.18
# ================================

"""
Canonical Strategy Formation for Phase 7.18.

Strategy Formation is the canonical pipeline for strategic reasoning:
Mission Analysis -> Objective Decomposition -> Constraint Analysis ->
Strategy Generation -> Policy Alignment -> Validation -> Publication.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategyFormation:
    """
    The result of strategy formation for a given mission and objectives.
    
    Strategy Formation implements the canonical pipeline:
        1. Mission Analysis
        2. Objective Decomposition
        3. Constraint Analysis
        4. Strategy Generation
        5. Policy Alignment
        6. Validation
        7. Publication
    
    The resulting strategy is deterministic given identical inputs.
    """
    
    # Identity
    formation_id: str                       # Unique formation identifier
    
    # Input
    objective_set_id: str                   # Which objectives were analyzed?
    
    # Generation strategy (how the strategy was formed)
    generation_strategy: str = "canonical_pipeline"
    
    # Resulting strategy
    resulting_strategy: Optional[Dict[str, Any]] = None  # Strategy as structured data
    
    # Diagnostics from each stage
    mission_analysis_result: Optional[Dict[str, Any]] = None
    objective_decomposition_result: Optional[Dict[str, Any]] = None
    constraint_analysis_result: Optional[Dict[str, Any]] = None
    strategy_generation_result: Optional[Dict[str, Any]] = None
    policy_alignment_result: Optional[Dict[str, Any]] = None
    
    # Validation results
    validation_results: List[str] = field(default_factory=list)
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return time.time() - self.started_at_utc
    
    @classmethod
    def create(
        cls,
        objective_set_id: str,
        strategy_data: Dict[str, Any],
        validation_results: List[str] = None,
    ) -> StrategyFormation:
        """Create a new strategy formation result."""
        if validation_results is None:
            validation_results = []
        
        return cls(
            formation_id=f"strategy_formation:{uuid.uuid4().hex[:16]}",
            objective_set_id=objective_set_id,
            resulting_strategy=strategy_data,
            validation_results=list(validation_results),
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class StrategyFormationFailure:
    """
    Record of a failed strategy formation attempt.
    
    Failures can occur at any stage:
        - Mission ambiguity
        - Conflicting objectives
        - Resource infeasibility
        - Policy inconsistency
        - Adaptation failure
    """
    
    # Identity
    failure_id: str
    
    # Input that failed
    objective_set_id: str
    
    # Failure kind
    failure_kind: str                       # e.g., "conflict", "infeasible"
    
    # Diagnostics
    diagnostics: List[str] = field(default_factory=list)
    
    # Stage where failure occurred
    stage_failed: Optional[str] = None      # None means unknown/catastrophic
    
    # Timing
    failed_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class StrategyFormationProgress:
    """
    Progress tracking for an in-progress strategy formation.
    
    Allows monitoring of the canonical pipeline execution without
    requiring full completion.
    """
    
    # Identity
    progress_id: str
    
    # Formation being tracked
    formation_id: str
    
    # Current stage
    current_stage: str                      # e.g., "mission_analysis", "strategy_generation"
    
    # Progress indicators
    stages_completed: List[str] = field(default_factory=list)
    stages_remaining: List[str] = field(default_factory=list)
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    last_updated_at_utc: float = field(default_factory=time.time)


__all__ = [
    "StrategyFormation",
    "StrategyFormationFailure",
    "StrategyFormationProgress",
]