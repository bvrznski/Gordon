# Creative Exploration Management - Phase 7.33
# ===========================================

"""
Canonical Creative Exploration.

Creative exploration evaluates alternative designs, architectures, plans,
hypotheses, representations, and strategies within defined boundaries.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ExplorationStrategy(Enum):
    """Strategies for creative exploration."""
    
    ALTERNATIVE_GENERATION = "alternative_generation"  # Generate multiple alternatives
    DIVERGENT_SEARCH = "divergent_search"              # Broad search across space
    CONVERGENT_REFINEMENT = "convergent_refinement"    # Refine promising ideas
    BREADTH_FIRST = "breadth_first"                    # Explore wide variety first
    DEPTH_FIRST = "depth_first"                        # Deep dive into specific area


@dataclass(frozen=True)
class CreativeExploration:
    """
    Represents a creative exploration process.
    
    A creative exploration includes:
        - Exploration boundaries and scope
        - Alternatives explored
        - Metrics tracking exploration progress
        - Provenance tracking
    
    Explorations remain explicit for traceability.
    """
    
    # Identity
    exploration_id: str                     # Unique exploration identifier
    semantic_identity: str                  # Semantic identity
    
    # Exploration boundaries
    exploration_scope: str = "general"      # e.g., "architecture", "design"
    
    # Explored space
    explored_alternatives: List[str] = field(default_factory=list)  # IDs of explored alternatives
    unexplored_candidates: List[str] = field(default_factory=list)  # Remaining candidates
    
    # Exploration metrics
    exploration_depth: int = 0              # How deep we've explored
    exploration_breadth: int = 0            # How wide we've explored
    
    # Strategy
    strategy: ExplorationStrategy = ExplorationStrategy.ALTERNATIVE_GENERATION
    
    # Results
    promising_alternatives: List[str] = field(default_factory=list)  # Top candidates
    rejected_alternatives: List[str] = field(default_factory=list)   # Discarded candidates
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_alternatives(self) -> int:
        """Return total alternatives processed."""
        return len(self.explored_alternatives) + len(self.unexplored_candidates)
    
    @property
    def exploration_rate(self) -> float:
        """Calculate exploration completion rate."""
        total = self.total_alternatives
        if total == 0:
            return 1.0
        return len(self.explored_alternatives) / total
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        exploration_scope: str = "general",
        alternatives: Optional[List[str]] = None,
        strategy: ExplorationStrategy = ExplorationStrategy.ALTERNATIVE_GENERATION,
    ) -> CreativeExploration:
        """Create a new creative exploration."""
        return cls(
            exploration_id=f"exploration:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            exploration_scope=exploration_scope,
            explored_alternatives=alternatives or [],
            strategy=strategy,
            created_at_utc=time.time(),
        )
    
    def with_alternative(self, alt_id: str) -> CreativeExploration:
        """Add an alternative to explored list."""
        if alt_id in self.explored_alternatives:
            return self
        new_explored = list(self.explored_alternatives)
        new_unexplored = [a for a in self.unexplored_candidates if a != alt_id]
        return dataclass_replace(
            self,
            explored_alternatives=new_explored + [alt_id],
            unexplored_candidates=new_unexplored,
            exploration_depth=self.exploration_depth + 1,
        )
    
    def with_promising(self, alt_id: str) -> CreativeExploration:
        """Mark an alternative as promising."""
        if alt_id in self.promising_alternatives:
            return self
        new_promising = list(self.promising_alternatives)
        if alt_id not in new_promising:
            new_promising.append(alt_id)
        return dataclass_replace(
            self,
            promising_alternatives=new_promising,
            exploration_breadth=len(new_promising),
        )
    
    def with_rejected(self, alt_id: str) -> CreativeExploration:
        """Mark an alternative as rejected."""
        if alt_id in self.rejected_alternatives:
            return self
        new_rejected = list(self.rejected_alternatives)
        if alt_id not in new_rejected and alt_id not in self.promising_alternatives:
            new_rejected.append(alt_id)
        return dataclass_replace(
            self,
            rejected_alternatives=new_rejected,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeExploration",
    "ExplorationStrategy",
]