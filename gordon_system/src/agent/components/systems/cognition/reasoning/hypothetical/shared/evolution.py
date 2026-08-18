# Hypothesis Evolution - Phase 7.15 Part 2
# ==========================================

"""
Canonical Hypothesis Evolution Contract.

Hypotheses evolve through new observations, reasoning, simulation,
analogy, experimentation, and evaluation.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class EvolutionIdentity:
    """
    Immutable identity for a hypothesis evolution track.
    
    Allows tracking evolution history across sessions.
    """
    
    semantic_identity: str                    # Stable identity across runs
    
    @classmethod
    def create(cls, semantic_identity: str) -> EvolutionIdentity:
        """Create a new evolution identity."""
        return cls(semantic_identity=semantic_identity)


@dataclass(frozen=True)
class HypothesisEvolution:
    """
    Record of hypothesis evolution.
    
    Tracks how hypotheses have changed over time through various
    reasoning processes while preserving original identity.
    """
    
    # Identity
    evolution_id: str                         # Unique identifier
    
    # Evolution history (chronological chain)
    evolution_history: Tuple[str, ...] = ()   # All evolutionary steps
    
    # Triggering events
    triggering_events: Tuple[str, ...] = ()   # What caused changes?
    
    # Resulting state
    resulting_state: str = "unchanged"        # Final state description
    
    # Metadata
    evolved_at_utc: float = field(default_factory=time.time)
    
    @property
    def evolution_count(self) -> int:
        """Return number of evolutionary steps."""
        return len(self.evolution_history)
    
    @classmethod
    def create(
        cls,
        triggering_events: Optional[List[str]] = None,
        evolution_steps: Optional[List[str]] = None,
        resulting_state: str = "unchanged",
    ) -> HypothesisEvolution:
        """Create a new evolution record."""
        return cls(
            evolution_id=f"evolution:{uuid.uuid4().hex[:16]}",
            evolution_history=tuple(evolution_steps or []),
            triggering_events=tuple(triggering_events or []),
            resulting_state=resulting_state,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EvolutionIdentity",
    "HypothesisEvolution",
]