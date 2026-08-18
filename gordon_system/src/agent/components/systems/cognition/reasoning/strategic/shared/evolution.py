# Strategic Evolution - Phase 7.18
# ================================

"""
Canonical Strategic Evolution for Phase 7.18.

Strategies evolve through experience, evaluation, learning, environmental changes,
and mission updates while maintaining identity stability.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicEvolution:
    """
    Evolution of a strategy over time through various learning mechanisms.
    
    Strategies evolve through:
        - Experience (historical outcomes)
        - Evaluation (performance metrics)
        - Learning (knowledge acquisition)
        - Environmental changes (external factors)
        - Mission updates (changed objectives)
    
    Identity remains stable throughout evolution.
    """
    
    # Identity
    evolution_id: str                       # Unique evolution identifier
    
    # Strategy being evolved
    strategy_identity: str                  # Which strategy?
    
    # Evolution history (chronological, oldest first)
    evolution_history: List[str] = field(default_factory=list)  # Step IDs
    
    # Triggering events for each evolution step
    triggering_events: Dict[str, str] = field(default_factory=dict)  # step_id -> event_type
    
    # Resulting strategy after all evolutions
    resulting_strategy: Optional[Dict[str, Any]] = None
    
    # Evolution metrics
    total_evolution_steps: int = 0          # Total steps taken
    final_strategic_identity: str = ""      # Identity at end (should equal original)
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    last_updated_at_utc: Optional[float] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if evolution has completed."""
        return self.resulting_strategy is not None


@dataclass(frozen=True)
class EvolutionStep:
    """
    A single step in the strategic evolution process.
    """
    
    # Identity
    step_id: str
    
    # Previous state
    previous_state_identity: str
    
    # Triggering event type
    trigger_type: str                       # e.g., "mission_update", "resource_change"
    
    # Change description
    change_description: str                 # What changed?
    
    # Resulting state
    resulting_state_identity: str
    
    # Timing
    executed_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class EvolutionFailure:
    """
    Record of a failed evolution attempt.
    """
    
    # Identity
    failure_id: str
    
    # Input that failed
    strategy_identity: str
    
    # Failure kind
    failure_kind: str                       # e.g., "identity_breach", "incompatible_change"
    
    # Diagnostics
    diagnostics: List[str] = field(default_factory=list)
    
    # Timing
    failed_at_utc: float = field(default_factory=time.time)


__all__ = [
    "StrategicEvolution",
    "EvolutionStep",
    "EvolutionFailure",
]