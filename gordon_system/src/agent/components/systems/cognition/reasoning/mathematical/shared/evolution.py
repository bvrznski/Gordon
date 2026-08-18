# Mathematical Evolution - Phase 7.46
# ====================================

"""
Canonical mathematical evolution tracking.

Mathematical reasoning evolves through:
    - constraint refinement
    - objective refinement
    - proof refinement
    - symbolic simplification
    - numerical refinement

Mathematical identity remains stable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class MathematicalEvolution:
    """
    Record of mathematical problem evolution.
    
    Tracks how a mathematical session has been refined or adapted over time
    while preserving its core identity.
    """
    
    evolution_id: str                     # Unique identifier
    
    # Identity preservation
    original_identity: str                # Original semantic identity
    current_identity: str                 # Current semantic identity (may be updated)
    
    # Evolution history
    evolution_history: List[str] = field(default_factory=list)  # Evolution steps
    triggering_events: List[str] = field(default_factory=list)  # What triggered each change
    
    # Updated solution
    updated_solution: Optional[str] = None  # Latest solution after evolution
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        original_identity: str,
        current_identity: str,
    ) -> MathematicalEvolution:
        """Create a new mathematical evolution record."""
        return cls(
            evolution_id=f"mathematical_evolution:{uuid.uuid4().hex[:16]}",
            original_identity=original_identity,
            current_identity=current_identity,
        )


@dataclass(frozen=True)
class EvolutionTrigger(Enum):
    """Triggers for mathematical evolution."""
    
    NEW_CONSTRAINT = "new_constraint"
    CONSTRAINT_RELAXATION = "constraint_relaxation"
    OBJECTIVE_REDEFINITION = "objective_redefinition"
    SYMBOLIC_SIMPLIFICATION = "symbolic_simplification"
    NUMERICAL_REFINEMENT = "numerical_refinement"
    PROOF_EXTENSION = "proof_extension"
    AXIOM_ADDITION = "axiom_addition"


@dataclass(frozen=True)
class EvolutionStep:
    """
    A single evolution step in mathematical reasoning.
    
    Contains the type of evolution and its effects.
    """
    
    step_id: str                          # Unique identifier
    trigger_type: EvolutionTrigger        # What triggered this step
    before_state: Optional[str] = None    # State before evolution
    after_state: Optional[str] = None     # State after evolution
    
    @classmethod
    def create(
        cls,
        trigger_type: EvolutionTrigger,
        before_state: Optional[str] = None,
        after_state: Optional[str] = None,
    ) -> EvolutionStep:
        """Create a new evolution step."""
        return cls(
            step_id=f"evolution_step:{uuid.uuid4().hex[:16]}",
            trigger_type=trigger_type,
            before_state=before_state,
            after_state=after_state,
        )


__all__ = [
    "MathematicalEvolution",
    "EvolutionTrigger",
    "EvolutionStep",
]