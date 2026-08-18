# Strategy Analysis - Phase 7.43
# ==============================

"""
Canonical Strategy Analysis definitions.

Strategy analysis evaluates:
    - Dominant strategies
    - Dominated strategies
    - Mixed strategies
    - Pure strategies
    - Strategy stability
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategyIdentity:
    """Unique identity for a strategy."""
    
    identity: str  # Unique identifier


@dataclass(frozen=True)
class StrategyAnalysis:
    """
    Analysis of strategies in a game.
    
    A strategy analysis includes:
        - Identity
        - Evaluated strategies
        - Strategy quality metrics
        - Confidence estimates
        - Provenance
    """
    
    # Identity
    analysis_identity: str                  # Unique identifier
    
    # Strategies evaluated
    evaluated_strategies: Tuple[str, ...]   # All strategies analyzed
    
    # Quality metrics
    strategy_quality: Dict[str, float] = {}  # Strategy -> quality score (0-1)
    
    # Confidence
    confidence: float = 1.0                 # Overall confidence in analysis
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # Source game for this analysis
    
    @classmethod
    def create(
        cls,
        evaluated_strategies: List[str],
        source_game_id: Optional[str] = None,
    ) -> StrategyAnalysis:
        """Create a new strategy analysis."""
        return cls(
            analysis_identity=f"strategy_analysis:{uuid.uuid4().hex[:16]}",
            evaluated_strategies=tuple(evaluated_strategies),
            source_game_id=source_game_id,
        )
    
    def with_quality(self, strategy: str, quality: float) -> StrategyAnalysis:
        """Add or update strategy quality."""
        new_quality = dict(self.strategy_quality)
        new_quality[strategy] = quality
        return dataclass_replace(self, strategy_quality=new_quality)


@dataclass(frozen=True)
class StrategyManagement:
    """
    Management of strategies over time.
    
    Strategy management includes:
        - Identity
        - Current strategy space
        - Dominant strategies identified
        - Robustness metrics
        - Provenance
    """
    
    # Identity
    management_identity: str                # Unique identifier
    
    # Strategy space
    strategy_space: Dict[str, Tuple[str, ...]]  # Agent -> available strategies
    
    # Dominant strategies
    dominant_strategies: Dict[str, str] = {}  # Agent -> dominant strategy
    dominated_strategies: Dict[str, List[str]] = {}  # Agent -> list of dominated
    
    # Robustness
    robustness: float = 1.0                 # How robust is this analysis?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_strategy_id: Optional[str] = None  # If derived from another
    
    @classmethod
    def create(
        cls,
        strategy_space: Dict[str, List[str]],
        source_strategy_id: Optional[str] = None,
    ) -> StrategyManagement:
        """Create new strategy management."""
        return cls(
            management_identity=f"strategy_mgmt:{uuid.uuid4().hex[:16]}",
            strategy_space={k: tuple(v) for k, v in strategy_space.items()},
            source_strategy_id=source_strategy_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StrategyIdentity",
    "StrategyAnalysis",
    "StrategyManagement",
]