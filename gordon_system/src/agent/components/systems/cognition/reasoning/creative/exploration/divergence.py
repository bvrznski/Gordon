# Creative Divergence Management - Phase 7.33
# ==========================================

"""
Canonical Creative Divergence.

Divergence management determines search breadth, constraint relaxation,
novelty pressure, exploration diversity, idea independence, and search
termination.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DivergencePolicy(Enum):
    """Strategies for divergence management."""
    
    CONVERGENT = "convergent"               # Focus on promising ideas
    BALANCED = "balanced"                   # Balance exploration and exploitation
    DIVERGENT = "divergent"                 # Broad exploration
    EXTREME = "extreme"                     # Maximum novelty pressure


@dataclass(frozen=True)
class CreativeDivergence:
    """
    Manages creative divergence during reasoning.
    
    A divergence manager includes:
        - Divergence policy (how aggressively to explore)
        - Exploration diversity metrics
        - Search state tracking
        - Termination conditions
    
    Divergence remains explicit for reproducibility.
    """
    
    # Identity
    divergence_id: str                      # Unique divergence identifier
    semantic_identity: str                  # Semantic identity
    
    # Policy
    policy: DivergencePolicy = DivergencePolicy.BALANCED
    
    # Divergence metrics
    current_novelty_pressure: float = 0.5   # Current pressure for novelty (0-1)
    exploration_diversity: float = 0.5      # Diversity of explored space (0-1)
    
    # Search state
    search_breadth: int = 0                 # How wide we've searched
    search_depth: int = 0                   # How deep we've searched
    
    # Termination conditions
    max_iterations: int = 10                # Maximum divergence iterations
    termination_threshold: float = 0.9      # When to terminate (saturation)
    
    # Provenance
    provenance_id: Optional[str] = None     # ID of creative session
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_saturated(self) -> bool:
        """Check if divergence has reached saturation."""
        return self.exploration_diversity >= self.termination_threshold
    
    @property
    def iteration_progress(self) -> float:
        """Calculate progress through iterations."""
        if self.max_iterations == 0:
            return 1.0
        return min(1.0, (self.search_breadth + self.search_depth) / self.max_iterations)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        policy: DivergencePolicy = DivergencePolicy.BALANCED,
        max_iterations: int = 10,
        termination_threshold: float = 0.9,
        provenance_id: Optional[str] = None,
    ) -> CreativeDivergence:
        """Create a new creative divergence manager."""
        return cls(
            divergence_id=f"divergence:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            policy=policy,
            max_iterations=max_iterations,
            termination_threshold=termination_threshold,
            provenance_id=provenance_id,
            created_at_utc=time.time(),
        )
    
    def with_novelty_pressure(self, pressure: float) -> CreativeDivergence:
        """Return a copy with updated novelty pressure."""
        return dataclass_replace(
            self,
            current_novelty_pressure=max(0.0, min(1.0, pressure)),
        )
    
    def with_diversity(self, diversity: float) -> CreativeDivergence:
        """Return a copy with updated exploration diversity."""
        return dataclass_replace(
            self,
            exploration_diversity=max(0.0, min(1.0, diversity)),
        )
    
    def is_aggressive(self) -> bool:
        """Check if this divergence policy is aggressive."""
        return self.policy in (DivergencePolicy.DIVERGENT, DivergencePolicy.EXTREME)
    
    def is_conservative(self) -> bool:
        """Check if this divergence policy is conservative."""
        return self.policy == DivergencePolicy.CONVERGENT


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeDivergence",
    "DivergencePolicy",
]