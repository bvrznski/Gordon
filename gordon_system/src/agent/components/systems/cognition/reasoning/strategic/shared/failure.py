# Strategic Failure - Phase 7.18
# ==============================

"""
Canonical Strategic Failure for Phase 7.18.

Strategic Failures include conflicting objectives, resource infeasibility,
policy inconsistency, mission ambiguity, and adaptation failure.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicFailure:
    """
    Record of a strategic failure.
    
    Failures include:
        - Conflicting objectives (incompatible goals)
        - Resource infeasibility (can't be achieved with available resources)
        - Policy inconsistency (violates governing policies)
        - Mission ambiguity ( unclear or missing mission definition)
        - Adaptation failure (strategy couldn't adapt to changes)
    
    Failures remain explicit for learning and recovery.
    """
    
    # Identity
    failure_id: str                         # Unique failure identifier
    
    # Context
    objective_set_id: str                   # Which objectives failed?
    strategy_identity: Optional[str] = None  # Which strategy failed?
    
    # Failure kind
    failure_kind: str                       # e.g., "conflict", "infeasible"
    
    # Diagnostics
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)  # structured analysis
    
    # Recovery options (what could be done?)
    recovery_options: List[str] = field(default_factory=list)
    
    # Timing
    failed_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class FailureCategory:
    """Categories of strategic failures."""
    
    CONFLICTING_OBJECTIVES = "conflicting_objectives"
    RESOURCE_INFEASIBILITY = "resource_infeasibility"
    POLICY_INCONSISTENCY = "policy_inconsistency"
    MISSION_AMBIGUITY = "mission Ambiguity"
    ADAPTATION_FAILURE = "adaptation_failure"


@dataclass(frozen=True)
class FailureRecoveryPlan:
    """
    Plan for recovering from a strategic failure.
    """
    
    # Identity
    recovery_id: str
    
    # Original failure
    failure_id: str
    
    # Recovery strategy
    recovery_strategy: str                  # High-level approach
    
    # Steps to execute
    recovery_steps: List[str] = field(default_factory=list)
    
    # Expected outcome
    expected_outcome: str                   # What will be achieved?
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)


__all__ = [
    "StrategicFailure",
    "FailureCategory",
    "FailureRecoveryPlan",
]