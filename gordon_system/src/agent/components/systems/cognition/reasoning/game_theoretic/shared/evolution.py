# Game Evolution - Phase 7.43
# =========================

"""
Canonical Game Evolution definitions.

Game evolution handles:
    - Strategy revisions
    - Payoff revisions
    - Agent additions/removals
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EvolutionTrigger(Enum):
    """Triggers for game evolution."""
    
    STRATEGY_UPDATE = "strategy_update"
    PAYOFF_REVISION = "payoff_revision"
    AGENT_ADDITION = "agent_addition"
    AGENT_REMOVAL = "agent_removal"
    ENVIRONMENTAL_CHANGE = "environmental_change"


@dataclass(frozen=True)
class GameEvolution:
    """
    Evolution of a game over time.
    
    A game evolution includes:
        - Identity
        - Evolution history
        - Triggering events
        - Resulting game state
        - Provenance
    """
    
    # Identity
    evolution_identity: str                 # Unique identifier
    
    # History
    evolution_history: Tuple[str, ...] = ()  # All evolutionary steps
    
    # Triggers
    triggers: Tuple[EvolutionTrigger, ...] = ()  # What triggered each step?
    
    # Resulting game
    resulting_game: Optional[str] = None    # Final game identity
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # If evolved from another game
    
    @classmethod
    def create(
        cls,
        source_game_id: Optional[str] = None,
    ) -> GameEvolution:
        """Create a new game evolution."""
        return cls(
            evolution_identity=f"game_evolution:{uuid.uuid4().hex[:16]}",
            source_game_id=source_game_id,
        )
    
    def add_step(self, step: str, trigger: EvolutionTrigger) -> GameEvolution:
        """Add an evolutionary step."""
        return dataclass_replace(
            self,
            evolution_history=self.evolution_history + (step,),
            triggers=self.triggers + (trigger,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GameEvolution",
    "EvolutionTrigger",
]
