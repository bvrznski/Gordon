# Salience Network Decay State
# ============================
#
# Canonical implementation of semantic decay (Phase 4.8.4).
#

"""
Decay state for semantic loss expectations.

DECAY vs PERSISTENCE:
    - Decay: Expected loss of salience or validity
    - Persistence: Expected semantic continuity
    
DECAY CATEGORIES:
    - NONE: No expected decay
    - SLOW: Gradual loss over extended period
    - MODERATE: Noticeable loss within reasonable time
    - RAPID: Quick loss of significance
    - EXPIRED: Already past decay threshold
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SalienceDecayState:
    """
    Canonical semantic decay representation.
    
    DECAY KINDS:
        - NONE: No expected decay (persistent significance)
        - SLOW: Gradual loss over extended period (> 10 time units)
        - MODERATE: Noticeable loss within reasonable time (4-10 time units)
        - RAPID: Quick loss of significance (< 4 time units)
        - EXPIRED: Already past decay threshold
    
    DECAY LAWS:
        - SALIENCE-DECAY-LAW-001: Decay describes expected semantic loss
        - SALIENCE-DECAY-LAW-002: No runtime computation occurs in State
        - SALIENCE-DECAY-LAW-003: External time reference required for actual computation
    
    DECAY COMPOSITION:
        - decay_policy_id: Reference to external decay policy where applicable
        - semantic_half_life: Expected half-life category
        - persistence_dependency: What the decay depends on
    """
    
    kind: str = field(default="unknown")
    """Semantic decay classification."""
    
    decay_policy_id: str | None = field(default=None)
    """External decay policy reference where applicable."""
    
    expected_half_life: str = field(default="unknown")
    """Expected semantic half-life category."""
    
    temporal_reference_id: str | None = field(default=None)
    """External time reference for decay computation (not computed internally)."""