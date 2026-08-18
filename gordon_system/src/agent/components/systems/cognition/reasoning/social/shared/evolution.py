# Social Evolution - Phase 7.32
# ============================

"""
Canonical Social Evolution.

Social models evolve through:
- New observations
- New interactions  
- Belief revisions
- Goal revisions
- Relationship changes

Identity remains stable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class SocialEvolution:
    """
    Social evolution result.
    
    Represents how social models changed over time:
        - Evolution identity (stable across revisions)
        - Evolution history (revision log)
        - Triggering events (what caused the change)
        - Resulting models after evolution
        
    Historical agent models remain immutable.
    """
    
    # Identity
    evolution_id: str                         # Unique identifier for this evolution event
    
    # Core evolution data
    agent_id: str                            # Which agent's model evolved?
    evolution_timestamp_utc: float           # When did this evolution occur?
    
    # Evolution history
    previous_model_state: Optional[Dict[str, Any]] = None  # Model before evolution
    current_model_state: Dict[str, Any] = field(default_factory=dict)  # Model after evolution
    
    # Triggering events
    triggering_events: Tuple[Any, ...] = ()   # What caused this change?
    
    # Metadata
    revision_number: int = 1
    confidence_at_evolution: float = 0.5
    
    @property
    def is_first_revision(self) -> bool:
        """Check if this is the first revision."""
        return self.revision_number == 1
    
    def get_previous_state_or_current(self, key: str, default: Any = None) -> Any:
        """Get a value from previous state or current state."""
        if self.previous_model_state and key in self.previous_model_state:
            return self.previous_model_state[key]
        return self.current_model_state.get(key, default)
    
    @classmethod
    def create(
        cls,
        agent_id: str,
        current_model_state: Dict[str, Any],
    ) -> SocialEvolution:
        """Create a new social evolution record."""
        return cls(
            evolution_id=f"evolution:{uuid.uuid4().hex[:16]}",
            agent_id=agent_id,
            evolution_timestamp_utc=time.time(),
            current_model_state=current_model_state,
        )
    
    def with_previous_state(self, previous_state: Dict[str, Any]) -> SocialEvolution:
        """Return a copy with previous model state recorded."""
        return dataclass_replace(
            self,
            previous_model_state=previous_state,
            revision_number=self.revision_number + 1,
        )
    
    def with_triggering_event(self, event: Any) -> SocialEvolution:
        """Return a copy with an additional triggering event."""
        return dataclass_replace(
            self,
            triggering_events=self.triggering_events + (event,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SocialEvolution",
]