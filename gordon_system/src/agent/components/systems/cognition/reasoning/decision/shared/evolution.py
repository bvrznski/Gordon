# Decision Evolution - Phase 7.19
# =============================

"""
Canonical Decision Evolution Contract.

Decisions evolve through experience, evaluation, learning,
environmental change, and strategic adaptation.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DecisionEvolution:
    """
    Evolution of a decision over time.
    
    Identity remains stable while the commitment may change.
    """
    
    # Identity (stable across all evolution states)
    evolution_identity: str                 # Original decision identity
    
    # History of changes
    evolution_history: Tuple[str, ...] = ()  # All state transitions
    
    # Triggering events that caused evolution
    triggering_events: Tuple[str, ...] = ()
    
    # Resulting decision (current state)
    resulting_decision: str                 # Current committed option
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def evolution_count(self) -> int:
        """Count of evolution steps."""
        return len(self.evolution_history)
    
    @classmethod
    def create(
        cls,
        evolution_identity: str,
        triggering_events: List[str],
        resulting_decision: str,
    ) -> DecisionEvolution:
        """Create a new decision evolution."""
        return cls(
            evolution_identity=evolution_identity,
            evolution_history=tuple([f"init:{resulting_decision}"]),
            triggering_events=tuple(triggering_events),
            resulting_decision=resulting_decision,
        )
    
    def evolve(self, new_state: str, trigger: str) -> DecisionEvolution:
        """Return a copy with the decision evolved to a new state."""
        new_history = list(self.evolution_history)
        new_history.append(f"{trigger}:{new_state}")
        
        return dataclass_replace(
            self,
            evolution_history=tuple(new_history),
            resulting_decision=new_state,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionEvolution",
]