# Game Set - Phase 7.43
# =====================

"""
Canonical Game Set definition.

A game set defines the immutable strategic environment for reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GameSet:
    """
    Immutable set of games defining the strategic environment.
    
    A game set contains:
        - Set identity (unique identifier for this configuration)
        - Participating agents
        - Game constraints and boundaries
        - Payoff models
        - Provenance tracking
    
    Game sets remain immutable during reasoning to ensure reproducibility.
    """
    
    # Identity
    game_set_identity: str                    # Unique identifier for this game set
    
    # Agents
    participating_agents: Tuple[str, ...]     # List of agent identifiers involved
    
    # Constraints
    game_constraints: Dict[str, Any] = {}     # Constraints defining the game space
    
    # Payoff model
    payoff_model: str = "utility"             # Type of payoff model being used
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_set_id: Optional[str] = None  # If derived from another set
    
    @property
    def agent_count(self) -> int:
        """Number of participating agents."""
        return len(self.participating_agents)
    
    @classmethod
    def create(
        cls,
        participating_agents: List[str],
        game_constraints: Optional[Dict[str, Any]] = None,
        source_game_set_id: Optional[str] = None,
    ) -> GameSet:
        """Create a new game set."""
        return cls(
            game_set_identity=f"game_set:{uuid.uuid4().hex[:16]}",
            participating_agents=tuple(participating_agents),
            game_constraints=game_constraints or {},
            source_game_set_id=source_game_set_id,
        )
    
    def with_agent(self, agent: str) -> GameSet:
        """Return a new game set with an additional agent."""
        if agent in self.participating_agents:
            return self
        return dataclass_replace(
            self,
            participating_agents=self.participating_agents + (agent,),
        )
    
    def without_agent(self, agent: str) -> GameSet:
        """Return a new game set with an agent removed."""
        if agent not in self.participating_agents:
            return self
        return dataclass_replace(
            self,
            participating_agents=tuple(a for a in self.participating_agents if a != agent),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GameSet",
]