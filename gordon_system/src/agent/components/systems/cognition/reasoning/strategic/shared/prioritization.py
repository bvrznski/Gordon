# Strategic Prioritization - Phase 7.18
# ======================================

"""
Canonical Objective Prioritization for Phase 7.18.

Prioritization evaluates importance, urgency, dependency, resource demand,
expected utility, and mission contribution to order objectives.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ObjectivePrioritization:
    """
    Result of objective prioritization.
    
    Prioritization evaluates:
        - Importance to mission success
        - Urgency of execution
        - Dependencies between objectives
        - Resource demand (time, cost, personnel)
        - Expected utility (value achieved)
        - Mission contribution alignment
    
    Priorities remain explicit and inspectable for transparency.
    """
    
    # Identity
    prioritization_id: str                  # Unique identifier
    
    # Input
    objective_set_id: str                   # Which objectives were prioritized?
    
    # Participating objectives with their original indices
    participating_objectives: List[int]     # Indices into original objectives list
    
    # Prioritization policy used
    prioritization_policy: str = "default"  # e.g., "mission_first", "resource_optimized"
    
    # Resulting order (by index)
    resulting_order: List[int]              # Ordered indices
    
    # Priority scores per objective
    priority_scores: Dict[int, float] = field(default_factory=dict)  # index -> score
    
    # Rationale for each position in the order
    ordering_rationale: Dict[int, str] = field(default_factory=dict)  # position -> explanation
    
    # Conflicts resolved during prioritization
    conflicts_resolved: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class PrioritizationFailure:
    """
    Record of a failed prioritization attempt.
    """
    
    # Identity
    failure_id: str
    
    # Input that failed
    objective_set_id: str
    
    # Failure kind
    failure_kind: str                       # e.g., "circular_dependency", "insufficient_info"
    
    # Diagnostics
    diagnostics: List[str] = field(default_factory=list)
    
    # Timing
    failed_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class PrioritizationMetrics:
    """
    Metrics computed during prioritization.
    """
    
    # Mission alignment score (0-1)
    mission_alignment_score: float = 0.0
    
    # Overall priority variance (lower = more consistent priorities)
    priority_variance: float = 0.0
    
    # Number of priority changes from input order
    reorder_count: int = 0
    
    # Resource feasibility (0-1, based on total resource demand vs availability)
    resource_feasibility: float = 0.0


__all__ = [
    "ObjectivePrioritization",
    "PrioritizationFailure",
    "PrioritizationMetrics",
]