# World-Model Reasoning Evolution - Phase 7.44
# =================================

"""
Canonical World Evolution Management.

World evolution tracks how the world state changes across revisions while preserving lineage.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EvolutionTrigger(Enum):
    """Triggers for world evolution."""
    
    NEW_OBSERVATION = "new_observation"         # New sensor data arrived
    ENTITY_DISCOVERY = "entity_discovery"       # Found new entity
    ENTITY_DISAPPEARANCE = "entity_disappearance"  # Entity no longer observed
    ENVIRONMENTAL_CHANGE = "environmental_change"  # Environment evolved naturally
    PHYSICAL_EVENT = "physical_event"           # Physical interaction occurred
    TRANSFORMATION = "transformation"           # Entity changed form


@dataclass(frozen=True)
class WorldRevision:
    """
    A revision of the world model.
    
    Each revision maintains complete lineage for reconstruction and evolution tracking.
    """
    
    revision_id: str                    # Unique identifier
    timestamp_utc: float                # When this revision was created
    
    # Lineage
    parent_revision_id: Optional[str] = None  # Previous revision (None if initial)
    previous_state_hash: Optional[str] = None   # Hash of previous world state
    current_state_hash: str             # Hash of current world state
    
    # Revision metadata
    trigger: EvolutionTrigger = EvolutionTrigger.NEW_OBSERVATION
    revision_number: int = 1            # Sequential revision number
    
    @classmethod
    def create(
        cls,
        timestamp_utc: Optional[float] = None,
        parent_revision_id: Optional[str] = None,
        previous_state_hash: Optional[str] = None,
        current_state_hash: str = "",
        trigger: EvolutionTrigger = EvolutionTrigger.NEW_OBSERVATION,
        revision_number: int = 1,
    ) -> WorldRevision:
        """Create a new world revision."""
        return cls(
            revision_id=f"revision:{uuid.uuid4().hex[:16]}",
            timestamp_utc=timestamp_utc or time.time(),
            parent_revision_id=parent_revision_id,
            previous_state_hash=previous_state_hash,
            current_state_hash=current_state_hash,
            trigger=trigger,
            revision_number=revision_number,
        )


@dataclass(frozen=True)
class WorldEvolution:
    """
    World evolution analysis result.
    
    A WorldEvolution contains:
        - Evolution identity
        - Evolution history (complete lineage of revisions)
        - Triggering events
        - Updated world model
        - Provenance tracking
    """
    
    # Identity
    evolution_id: str                   # Unique evolution identifier
    
    # History
    evolution_history: List[WorldRevision] = field(default_factory=list)
    
    # Triggers and updates
    triggering_events: List[str]        # What events triggered evolution?
    updated_world_model: Dict[str, Any] = field(default_factory=dict)  # Final world state
    
    # Metadata
    initial_state_hash: Optional[str] = None
    final_state_hash: str = ""
    
    # Confidence and provenance
    confidence: float = 1.0
    provenance: Optional[str] = None
    world_identity: str = "default"     # World identity (stable across evolutions)
    
    @classmethod
    def create(
        cls,
        world_identity: str = "default",
        provenance: Optional[str] = None,
    ) -> WorldEvolution:
        """Create a new world evolution analysis."""
        return cls(
            evolution_id=f"evolution:{uuid.uuid4().hex[:16]}",
            evolution_history=[],
            triggering_events=[],
            updated_world_model={},
            final_state_hash="",
            confidence=1.0,
            provenance=provenance,
            world_identity=world_identity,
        )
    
    def add_revision(self, revision: WorldRevision) -> WorldEvolution:
        """Add a revision to evolution history."""
        new_history = self.evolution_history + [revision]
        
        return dataclass_replace(
            self,
            evolution_history=new_history,
            confidence=self.confidence * 0.98,  # Slight reduction with each revision
        )
    
    def add_trigger(self, trigger_event: str) -> WorldEvolution:
        """Add a triggering event."""
        new_triggers = self.triggering_events + [trigger_event]
        
        return dataclass_replace(
            self,
            triggering_events=new_triggers,
        )


# Helper function for dataclass replacement
def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EvolutionTrigger",
    "WorldRevision",
    "WorldEvolution",
]