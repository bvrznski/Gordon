# Narrative Event Models
# ======================

"""
Immutable models for narrative events and temporal positioning.

ARCHITECTURAL PRINCIPLES:
    - Events are semantic objects (not runtime commands)
    - Events are deeply immutable
    - Temporal positions preserve event time vs record time distinction
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


# =============================================================================
# EVENT TEMPORAL POSITION - Event timing information
# =============================================================================

@dataclass(frozen=True, slots=True)
class EventTemporalPosition:
    """
    Immutable temporal position of an event.
    
    Narrative time preserves multiple timestamps:
        - event_time: When the actual event occurred
        - record_time: When it was recorded in system memory
        - narrative_time: When it became part of the narrative
    
    These times may differ significantly for remembered or simulated events.
    """
    
    # Event timing
    event_time_utc: Optional[datetime] = None
    """When the event actually occurred (if known)."""
    
    record_time_utc: Optional[datetime] = None
    """When the event was recorded in system memory."""
    
    narrative_time_utc: datetime = field(default_factory=datetime.utcnow)
    """When this event became part of the narrative coordination."""
    
    # Temporal certainty
    time_precision: str = "second"
    """Precision of the event timestamp (second, minute, hour, day)."""
    
    temporal_uncertainty_seconds: float = 0.0
    """Estimated uncertainty in event timing (in seconds)."""
    
    # Ordering relations to other events
    precedes_event_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Event IDs that this event is known to precede."""
    
    follows_event_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Event IDs that this event is known to follow."""
    
    @classmethod
    def from_events(
        cls,
        event_time_utc: Optional[datetime],
        record_time_utc: Optional[datetime],
        precedes_events: Tuple[str, ...] = (),
        follows_events: Tuple[str, ...] = (),
    ) -> EventTemporalPosition:
        """Create temporal position from event timing."""
        return cls(
            event_time_utc=event_time_utc,
            record_time_utc=record_time_utc,
            narrative_time_utc=datetime.utcnow(),
            time_precision="second",
            temporal_uncertainty_seconds=0.0,
            precedes_event_ids=precedes_events,
            follows_event_ids=follows_events,
        )


# =============================================================================
# NARRATIVE EVENT - Semantic unit of a narrative
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeEvent:
    """
    Immutable semantic event in a narrative.
    
    An event represents a significant occurrence or state change that is
    relevant to the narrative. Events may be observed, recorded, inferred,
    simulated, or counterfactual - their factuality must be preserved.
    """
    
    # Identity and kind
    event_id: str
    """Unique identifier for this event."""
    
    kind: str  # NarrativeEventKind.*
    """The canonical category of this event."""
    
    # Semantic content (bounded representation)
    semantic_content: str
    """Core semantic description of the event (not full prose)."""
    
    subject_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to subjects affected by or involved in the event."""
    
    participant_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to participants in this event."""
    
    # Temporal position
    temporal_position: EventTemporalPosition
    """When and how this event fits in time."""
    
    # Factuality and quality
    factuality_classification: str  # FactualityClassification.*
    """Factuality of the event content."""
    
    confidence: float = 0.5
    """Confidence in this event (0.0 to 1.0)."""
    
    importance: float = 0.5
    """Importance for narrative coherence (0.0 to 1.0)."""
    
    # Causal status
    causal_status: str = "unknown"
    """Causal role: 'cause', 'effect', 'correlation', 'unknown'."""
    
    preceding_event_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Event IDs that this event follows."""
    
    following_event_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Event IDs that follow this event."""
    
    # Source and provenance
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """Source reference IDs for this event."""
    
    provenance: str = "canonical"
    """Provenance reference for this event."""
    
    @classmethod
    def new(
        cls,
        kind: str,
        semantic_content: str,
        subject_references: Tuple[str, ...] = (),
        participant_references: Tuple[str, ...] = (),
        temporal_position: Optional[EventTemporalPosition] = None,
        factuality_classification: str = "recorded",
        confidence: float = 0.5,
    ) -> NarrativeEvent:
        """Create a new narrative event."""
        return cls(
            event_id=f"event_{id(cls)}",
            kind=kind,
            semantic_content=semantic_content,
            subject_references=subject_references,
            participant_references=participant_references,
            temporal_position=temporal_position or EventTemporalPosition(),
            factuality_classification=factuality_classification,
            confidence=confidence,
        )


# =============================================================================
# EVENT ORDERING RELATION - Temporal ordering constraint
# =============================================================================

@dataclass(frozen=True, slots=True)
class EventOrderingRelation:
    """
    Immutable relation specifying temporal ordering between events.
    
    Used when evidence supports only partial ordering of events.
    """
    
    relation_id: str
    """Unique identifier for this relation."""
    
    first_event_id: str
    """Event that occurs first."""
    
    second_event_id: str
    """Event that occurs after the first."""
    
    temporal_relation_kind: str  # TemporalRelationKind.*
    """The kind of temporal relationship."""
    
    confidence: float = 0.5
    """Confidence in this ordering (0.0 to 1.0)."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Source references supporting this ordering."""
    
    @classmethod
    def before(
        cls,
        first_event_id: str,
        second_event_id: str,
        confidence: float = 0.5,
    ) -> EventOrderingRelation:
        """Create a 'before' relation (first occurs before second)."""
        return cls(
            relation_id=f"order_{id(cls)}",
            first_event_id=first_event_id,
            second_event_id=second_event_id,
            temporal_relation_kind="before",
            confidence=confidence,
        )
    
    @classmethod
    def simultaneous(
        cls,
        event_a_id: str,
        event_b_id: str,
        confidence: float = 0.5,
    ) -> EventOrderingRelation:
        """Create a 'simultaneous' relation."""
        return cls(
            relation_id=f"order_{id(cls)}",
            first_event_id=event_a_id,
            second_event_id=event_b_id,
            temporal_relation_kind="simultaneous",
            confidence=confidence,
        )