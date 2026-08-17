# Knowledge Provenance - Phase 5.4
# ================================

"""
Knowledge Provenance: Origin tracking for semantic artifacts.

Provenance records the complete history of a knowledge artifact, including when,
where, and how it was created or modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PROVENANCE TRAIL - Complete history chain
# =============================================================================


@dataclass(frozen=True)
class ProvenanceEvent:
    """
    A single event in the provenance trail.
    
    Records an action taken on a knowledge artifact with full context.
    
    Fields:
        event_identity:        Unique identifier for this event
        timestamp_utc:         When the event occurred (seconds since epoch)
        actor_type:            Type of actor (e.g., "system", "user", "reasoning")
        actor_id:              ID of the actor performing the action
        action:                What action was performed
        context:               Context surrounding this event
    """
    
    # Identity and metadata (required)
    event_identity: str               # Unique ID for this event
    
    timestamp_utc: float              # When the event occurred
    actor_type: str = "system"        # e.g., "system", "user", "reasoning"
    actor_id: str = ""                # Actor identifier
    
    action: str = ""                  # What action was performed
    context: Dict[str, Any] = field(default_factory=dict)  # Event context


# =============================================================================
# PROVENANCE METADATA - Provenance record for knowledge artifacts
# =============================================================================


@dataclass(frozen=True)
class KnowledgeProvenance:
    """
    Provenance metadata for knowledge artifacts.
    
    Tracks the complete history of a semantic artifact from creation through
    all revisions, preserving full traceability.
    
    Fields:
        provenance_identity:   Unique identifier for this provenance record
        origin_timestamp_utc:  When the original artifact was created
        actor_type:            Original actor type
        actor_id:              Original actor ID
        revision_history:      List of events in the revision history
        current_revision:      Current revision number
    """
    
    # Identity and metadata (required)
    provenance_identity: str          # Unique ID for this provenance record
    
    origin_timestamp_utc: float       # When original artifact was created
    actor_type: str = "system"        # Original actor type
    actor_id: str = ""                # Original actor ID
    
    revision_history: Tuple[ProvenanceEvent, ...] = field(default_factory=tuple)
    
    @property
    def current_revision(self) -> int:
        """Get the current revision number."""
        return len(self.revision_history) + 1
    
    @classmethod
    def create_initial(
        cls,
        actor_type: str = "system",
        actor_id: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeProvenance":
        """
        Create initial provenance for a new artifact.
        
        Args:
            actor_type: Type of actor creating the artifact
            actor_id: ID of the actor
            context: Creation context (optional)
        """
        return cls(
            provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
            origin_timestamp_utc=time.time(),
            actor_type=actor_type,
            actor_id=actor_id,
            revision_history=tuple([
                ProvenanceEvent(
                    event_identity=f"event:{uuid.uuid4().hex[:16]}",
                    timestamp_utc=time.time(),
                    actor_type=actor_type,
                    actor_id=actor_id,
                    action="create",
                    context=context or {},
                )
            ]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provenance to dictionary for serialization."""
        return {
            "provenance_identity": self.provenance_identity,
            "origin_timestamp_utc": self.origin_timestamp_utc,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "revision_history": [
                {
                    "event_identity": e.event_identity,
                    "timestamp_utc": e.timestamp_utc,
                    "actor_type": e.actor_type,
                    "actor_id": e.actor_id,
                    "action": e.action,
                    "context": dict(e.context),
                }
                for e in self.revision_history
            ],
            "current_revision": self.current_revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeProvenance":
        """Create provenance record from dictionary."""
        events = []
        for event_data in data.get("revision_history", []):
            events.append(ProvenanceEvent(
                event_identity=event_data.get("event_identity", ""),
                timestamp_utc=float(event_data.get("timestamp_utc", time.time())),
                actor_type=event_data.get("actor_type", "system"),
                actor_id=event_data.get("actor_id", ""),
                action=event_data.get("action", ""),
                context=dict(event_data.get("context", {})),
            ))
        
        return cls(
            provenance_identity=data.get("provenance_identity", str(uuid.uuid4())),
            origin_timestamp_utc=float(data.get("origin_timestamp_utc", time.time())),
            actor_type=data.get("actor_type", "system"),
            actor_id=data.get("actor_id", ""),
            revision_history=tuple(events),
        )
    
    def add_event(
        self,
        action: str,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeProvenance":
        """
        Create a new provenance record with an additional event.
        
        Args:
            action: Action being performed
            actor_type: Type of actor (optional, defaults to current)
            actor_id: ID of actor (optional, defaults to current)
            context: Event context (optional)
        """
        new_event = ProvenanceEvent(
            event_identity=f"event:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            actor_type=actor_type or self.actor_type,
            actor_id=actor_id or self.actor_id,
            action=action,
            context=context or {},
        )
        
        return KnowledgeProvenance(
            provenance_identity=self.provenance_identity,
            origin_timestamp_utc=self.origin_timestamp_utc,
            actor_type=self.actor_type,
            actor_id=self.actor_id,
            revision_history=self.revision_history + (new_event,),
        )


__all__ = [
    "ProvenanceEvent",
    "KnowledgeProvenance",
]