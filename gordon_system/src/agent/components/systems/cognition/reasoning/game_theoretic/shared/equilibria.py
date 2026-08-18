# Equilibrium Analysis - Phase 7.43
# ==================================

"""
Canonical Equilibrium Analysis definitions.

Equilibrium analysis evaluates:
    - Nash equilibria
    - Pareto optima
    - Stackelberg equilibria
    - Correlated equilibria
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class EquilibriumIdentity:
    """Unique identity for an equilibrium."""
    
    identity: str  # Unique identifier


@dataclass(frozen=True)
class EquilibriumAnalysis:
    """
    Analysis of equilibria in a game.
    
    An equilibrium analysis includes:
        - Identity
        - Equilibrium model
        - Equilibrium type
        - Stability metrics
        - Provenance
    """
    
    # Identity
    analysis_identity: str                  # Unique identifier
    
    # Equilibrium model
    equilibrium_model: str                  # Type of equilibrium (e.g., "nash")
    
    # Equilibria found
    equilibria_found: Tuple[str, ...] = ()  # All equilibria discovered
    
    # Stability metrics
    stability_metrics: Dict[str, float] = {}  # Equilibrium -> stability score
    
    # Confidence
    confidence: float = 1.0                 # Overall confidence in analysis
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # Source game for this analysis
    
    @classmethod
    def create(
        cls,
        equilibrium_model: str,
        source_game_id: Optional[str] = None,
    ) -> EquilibriumAnalysis:
        """Create a new equilibrium analysis."""
        return cls(
            analysis_identity=f"equilibrium_analysis:{uuid.uuid4().hex[:16]}",
            equilibrium_model=equilibrium_model,
            source_game_id=source_game_id,
        )
    
    def add_equilibrium(self, equilibrium: str, stability: float = 1.0) -> EquilibriumAnalysis:
        """Add an equilibrium to the analysis."""
        new_stability = dict(self.stability_metrics)
        new_stability[equilibrium] = stability
        return dataclass_replace(
            self,
            equilibria_found=self.equilibria_found + (equilibrium,),
            stability_metrics=new_stability,
        )


@dataclass(frozen=True)
class EquilibriumManagement:
    """
    Management of equilibria over time.
    
    Equilibrium management includes:
        - Identity
        - Current equilibrium set
        - Stability metrics
        - Provenance
    """
    
    # Identity
    management_identity: str                # Unique identifier
    
    # Equilibrium set
    equilibrium_set: Tuple[str, ...] = ()   # All equilibria tracked
    
    # Stability metrics
    stability_metrics: Dict[str, float] = {}  # Equilibrium -> stability score
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_equilibrium_id: Optional[str] = None  # If derived from another
    
    @classmethod
    def create(
        cls,
        source_equilibrium_id: Optional[str] = None,
    ) -> EquilibriumManagement:
        """Create new equilibrium management."""
        return cls(
            management_identity=f"equilibrium_mgmt:{uuid.uuid4().hex[:16]}",
            source_equilibrium_id=source_equilibrium_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EquilibriumIdentity",
    "EquilibriumAnalysis",
    "EquilibriumManagement",
]