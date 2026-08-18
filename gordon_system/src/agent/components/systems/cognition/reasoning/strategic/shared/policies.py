# Strategic Policies - Phase 7.18
# ===============================

"""
Canonical Policy Construction for Phase 7.18.

Policies define stable behavioral principles including resource policies,
risk policies, learning policies, interaction policies, and ethical constraints.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicPolicy:
    """
    A policy defining stable behavioral principles for strategic reasoning.
    
    Policies include:
        - Resource allocation policies
        - Risk tolerance policies
        - Learning and adaptation policies
        - Interaction and communication policies
        - Ethical constraints
    
    Policies remain explicit and inspectable to ensure transparency.
    """
    
    # Identity
    policy_id: str                          # Unique policy identifier
    
    # Policy type
    policy_type: str                        # e.g., "resource", "risk", "learning"
    
    # Governing rules (explicit, machine-readable)
    governing_rules: List[str]              # Rules in natural language
    
    # Applicability conditions
    applicability_conditions: List[str] = field(default_factory=list)
    
    # Priority within policy set
    priority: int = 0                       # Higher values = higher priority
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_context: str = "unknown"


@dataclass(frozen=True)
class PolicyConstruction:
    """
    Result of policy construction for a given strategy.
    
    Policy construction evaluates behavioral constraints, resource policies,
    risk policies, adaptation rules, mission alignment, and consistency.
    """
    
    # Identity
    construction_id: str
    
    # Input
    strategy_identity: str                  # Which strategy?
    objective_set_id: str                   # Which objectives?
    
    # Participating policies
    participating_policies: List[StrategicPolicy]
    
    # Governing constraints (derived from analysis)
    governing_constraints: List[str] = field(default_factory=list)
    
    # Justification for each policy
    justifications: Dict[str, str] = field(default_factory=dict)  # policy_id -> explanation
    
    # Consistency check result
    consistency_check_passed: bool = True
    consistency_issues: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class PolicyConflict:
    """
    A detected conflict between policies.
    """
    
    # Identity
    conflict_id: str
    
    # Involved policies
    conflicting_policies: List[str]         # policy_ids
    
    # Conflict description
    conflict_description: str               # What conflicts?
    
    # Recommended resolution
    recommended_resolution: Optional[str] = None  # How to resolve it?


@dataclass(frozen=True)
class PolicyAdaptation:
    """
    Adaptation of policies based on environmental changes.
    """
    
    # Identity
    adaptation_id: str
    
    # Original policy
    original_policy_id: str
    
    # Adapted policy (can be the same with updated metadata)
    adapted_policy: StrategicPolicy
    
    # Triggering event
    adaptation_trigger: str                 # e.g., "resource_change", "mission_update"
    
    # Rationale for adaptation
    adaptation_rationale: str               # Why was it adapted?
    
    # Provenance
    adapted_at_utc: float = field(default_factory=time.time)


__all__ = [
    "StrategicPolicy",
    "PolicyConstruction",
    "PolicyConflict",
    "PolicyAdaptation",
]