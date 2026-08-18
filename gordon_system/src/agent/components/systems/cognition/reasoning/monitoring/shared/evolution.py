# Monitoring Evolution Contract - Phase 7.22
# =========================================

"""
Canonical Monitoring Evolution.

Evolution tracks how monitoring state changes over time.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StateTransition:
    """
    A single state transition in the monitoring evolution.
    """
    
    # Identity
    transition_id: str                        # Unique transition identifier
    
    # Transition details
    from_state: str                           # Previous state
    to_state: str                             # New state
    
    # Triggering event
    triggering_event: str = "unknown"         # What caused this transition?
    
    # Timing
    transitioned_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class MonitoringEvolution:
    """
    The evolution of a monitoring session over time.
    
    Evolution tracks:
        - State transitions
        - Triggering events
        - Resulting state changes
    
    Identity remains stable throughout evolution.
    """
    
    # Identity
    evolution_id: str                         # Unique evolution identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Evolution history
    transition_history: List[StateTransition] = field(default_factory=list)
    
    # Triggering events
    triggering_events: List[str] = field(default_factory=list)  # External triggers
    
    # Resulting state
    resulting_state: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def transition_count(self) -> int:
        """Get the number of transitions."""
        return len(self.transition_history)
    
    @property
    def is_completed(self) -> bool:
        """Check if evolution is completed."""
        return self.completed_at_utc is not None
    
    def add_transition(
        self,
        from_state: str,
        to_state: str,
        triggering_event: str = "unknown",
    ) -> MonitoringEvolution:
        """Add a state transition and return updated evolution."""
        new_transitions = list(self.transition_history)
        
        # Check for duplicate consecutive transitions
        if new_transitions:
            last_transition = new_transitions[-1]
            if last_transition.to_state == to_state:
                # Same end state, don't add duplicate
                return self
        
        new_transitions.append(StateTransition(
            transition_id=f"transition:{uuid.uuid4().hex[:16]}",
            from_state=from_state,
            to_state=to_state,
            triggering_event=triggering_event,
            transitioned_at_utc=time.time(),
        ))
        
        return dataclass_replace(
            self,
            transition_history=new_transitions,
        )
    
    def add_trigger(self, event: str) -> MonitoringEvolution:
        """Add a triggering event."""
        new_events = list(self.triggering_events)
        if event not in new_events:
            new_events.append(event)
        
        return dataclass_replace(
            self,
            triggering_events=new_events,
        )
    
    def update_resulting_state(self, state_updates: Dict[str, Any]) -> MonitoringEvolution:
        """Update the resulting state with new values."""
        new_state = dict(self.resulting_state)
        new_state.update(state_updates)
        
        return dataclass_replace(
            self,
            resulting_state=new_state,
        )
    
    def complete(self) -> MonitoringEvolution:
        """Mark evolution as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> MonitoringEvolution:
        """Create a new monitoring evolution tracker."""
        return cls(
            evolution_id=f"evolution:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            started_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MonitoringEvolution",
    "StateTransition",
]