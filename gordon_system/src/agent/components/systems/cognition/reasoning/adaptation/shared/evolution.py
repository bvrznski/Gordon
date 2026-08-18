# Adaptation Evolution - Phase 7.25
# =================================

"""
Canonical Adaptation Evolution contract.

Adaptations evolve through context changes, new observations, evaluation updates,
policy revisions, and resource changes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class AdaptationEvolution:
    """
    Evolution of an adaptation over time.
    
    Evolutions preserve identity while adapting to new conditions.
    """
    
    # Identity (preserved across evolution)
    evolution_identity: str               # Original adaptation identity
    
    # Evolution history
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Triggers for this evolution
    triggering_events: Tuple[str, ...] = field(default_factory=tuple)
    
    # Resulting configuration after evolution
    resulting_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    evolved_at_utc: Optional[float] = None
    
    @property
    def is_evolved(self) -> bool:
        """Check if evolution completed."""
        return self.evolved_at_utc is not None
    
    @classmethod
    def create(
        cls,
        original_identity: str,
        triggering_events: List[str],
        previous_configuration: Optional[Dict[str, Any]] = None,
        new_configuration: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationEvolution:
        """Create a new adaptation evolution."""
        history = []
        if previous_configuration:
            history.append({
                "type": "previous_state",
                "configuration": previous_configuration,
                "timestamp_utc": time.time(),
            })
        
        return cls(
            evolution_identity=original_identity,
            evolution_history=history,
            triggering_events=tuple(triggering_events),
            resulting_configuration=new_configuration or {},
            provenance=provenance or {},
            evolved_at_utc=time.time(),
        )
    
    def add_event(self, event_type: str, data: Dict[str, Any]) -> AdaptationEvolution:
        """Return a new evolution with an additional history entry."""
        new_history = [
            *self.evolution_history,
            {
                "type": event_type,
                "data": data,
                "timestamp_utc": time.time(),
            },
        ]
        return dataclass_replace(
            self,
            evolution_history=new_history,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationEvolution",
]