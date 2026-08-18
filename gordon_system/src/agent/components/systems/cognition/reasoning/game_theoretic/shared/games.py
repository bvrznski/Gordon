# Game Model - Phase 7.43
# ======================

"""
Canonical Game Model definition.

A game model represents an explicit strategic environment.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GameIdentity:
    """Unique identity for a game."""
    
    identity: str  # Unique identifier


@dataclass(frozen=True)
class GameModel:
    """
    Explicit strategic environment representation.
    
    A game model includes:
        - Game identity
        - Participating agents
        - Strategy space
        - Payoff functions
        - Information availability
        - Game type
    
    Game Models remain explicit and inspectable.
    """
    
    # Identity
    game_identity: str                      # Unique identifier for this game
    
    # Agents
    participating_agents: Tuple[str, ...]   # List of agent identifiers involved
    
    # Strategy space
    strategy_space: Dict[str, Tuple[str, ...]]  # Agent -> strategies available
    
    # Payoff model
    payoff_model: str                       # Type of payoff function
    payoff_functions: Optional[Dict[str, Any]] = None  # Explicit payoff definitions
    
    # Information structure
    information_type: str = "complete"      # complete, incomplete, imperfect, etc.
    
    # Game type
    game_type: str = "normal_form"          # normal_form, extensive_form, bayesian, etc.
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # If derived from another game
    
    @property
    def agent_count(self) -> int:
        """Number of participating agents."""
        return len(self.participating_agents)
    
    @property
    def has_payoff_functions(self) -> bool:
        """Check if explicit payoff functions are defined."""
        return self.payoff_functions is not None
    
    @classmethod
    def create(
        cls,
        game_identity: str,
        participating_agents: List[str],
        strategy_space: Dict[str, List[str]],
        payoff_model: str = "utility",
        information_type: str = "complete",
        game_type: str = "normal_form",
        source_game_id: Optional[str] = None,
    ) -> GameModel:
        """Create a new game model."""
        return cls(
            game_identity=game_identity,
            participating_agents=tuple(participating_agents),
            strategy_space={k: tuple(v) for k, v in strategy_space.items()},
            payoff_model=payoff_model,
            information_type=information_type,
            game_type=game_type,
            source_game_id=source_game_id,
        )


@dataclass(frozen=True)
class GameTrace:
    """
    Complete trace of a game session.
    
    A trace contains:
        - Trace identity
        - Game history (all games considered)
        - Game graph (relationships between games)
        - Diagnostics
        - Provenance
    
    Traces remain inspectable for analysis and debugging.
    """
    
    # Identity
    trace_identity: str                     # Unique identifier for this trace
    
    # History
    game_history: Tuple[str, ...] = ()      # All games in sequence
    
    # Game graph (relationships)
    game_graph: Dict[str, List[str]] = {}   # game_id -> list of related game_ids
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()       # Any diagnostic info
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, trace_identity: str) -> GameTrace:
        """Create a new game trace."""
        return cls(trace_identity=trace_identity)
    
    def add_game(self, game_id: str, related_games: Optional[List[str]] = None) -> GameTrace:
        """Add a game to the trace."""
        related = related_games or []
        new_graph = dict(self.game_graph)
        new_graph[game_id] = related
        return dataclass_replace(
            self,
            game_history=self.game_history + (game_id,),
            game_graph=new_graph,
        )
    
    def add_diagnostic(self, diagnostic: str) -> GameTrace:
        """Add a diagnostic entry."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GameIdentity",
    "GameModel",
    "GameTrace",
]