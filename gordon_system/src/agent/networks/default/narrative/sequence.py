# Narrative Sequence Models
# =========================

"""
Immutable models for narrative sequences and temporal ordering.

ARCHITECTURAL PRINCIPLES:
    - Sequences represent ordered event arrangements
    - Partial ordering is supported when evidence doesn't support total order
    - Gaps in sequences are explicitly represented
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, FrozenSet


# =============================================================================
# SEQUENCE ORDER RELATION - Ordering constraint between events
# =============================================================================

@dataclass(frozen=True, slots=True)
class SequenceOrderRelation:
    """
    Immutable relation specifying ordering between events in a sequence.
    
    Supports partial orderings when full temporal ordering cannot be established.
    """
    
    relation_id: str
    """Unique identifier for this ordering relation."""
    
    event_a_id: str
    """First event reference."""
    
    event_b_id: str
    """Second event reference."""
    
    order_kind: str  # TemporalRelationKind.*
    """The kind of temporal relationship between events."""
    
    confidence: float = 0.5
    """Confidence in this ordering (0.0 to 1.0)."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Source references supporting this ordering."""
    
    @classmethod
    def before(
        cls,
        event_a_id: str,
        event_b_id: str,
        confidence: float = 0.5,
    ) -> SequenceOrderRelation:
        """Create a 'before' relation (A occurs before B)."""
        return cls(
            relation_id=f"order_{id(cls)}",
            event_a_id=event_a_id,
            event_b_id=event_b_id,
            order_kind="before",
            confidence=confidence,
        )
    
    @classmethod
    def after(
        cls,
        event_a_id: str,
        event_b_id: str,
        confidence: float = 0.5,
    ) -> SequenceOrderRelation:
        """Create an 'after' relation (A occurs after B)."""
        return cls(
            relation_id=f"order_{id(cls)}",
            event_a_id=event_a_id,
            event_b_id=event_b_id,
            order_kind="after",
            confidence=confidence,
        )
    
    @classmethod
    def simultaneous(
        cls,
        event_a_id: str,
        event_b_id: str,
        confidence: float = 0.5,
    ) -> SequenceOrderRelation:
        """Create a 'simultaneous' relation."""
        return cls(
            relation_id=f"order_{id(cls)}",
            event_a_id=event_a_id,
            event_b_id=event_b_id,
            order_kind="simultaneous",
            confidence=confidence,
        )
    
    @classmethod
    def unordered(
        cls,
        event_a_id: str,
        event_b_id: str,
    ) -> SequenceOrderRelation:
        """Create an 'unordered' relation (temporal relationship unknown)."""
        return cls(
            relation_id=f"order_{id(cls)}",
            event_a_id=event_a_id,
            event_b_id=event_b_id,
            order_kind="unknown",
            confidence=0.0,
        )


# =============================================================================
# NARRATIVE SEQUENCE - Ordered event arrangement
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeSequence:
    """
    Immutable ordered arrangement of events representing a narrative timeline.
    
    A sequence represents an event ordering that may be:
        - Total (complete ordering of all events)
        - Partial (only some events have known order)
        - With gaps (missing events between known events)
        
    The sequence preserves both temporal and semantic organization.
    """
    
    # Identity
    sequence_id: str
    """Unique identifier for this sequence."""
    
    narrative_id: Optional[str] = None
    """Narrative ID if part of a specific narrative."""
    
    # Events in the sequence
    events: Tuple[str, ...] = field(default_factory=tuple)
    """Event IDs in the sequence (order may be partial)."""
    
    # Ordering relations
    order_relations: Tuple[SequenceOrderRelation, ...] = field(default_factory=tuple)
    """Explicit ordering constraints between events."""
    
    # Temporal bounds
    start_time_utc: Optional[str] = None
    """Start of temporal range (ISO string if known)."""
    
    end_time_utc: Optional[str] = None
    """End of temporal range (ISO string if known)."""
    
    # Assessment
    confidence: float = 0.5
    """Overall confidence in the sequence (0.0 to 1.0)."""
    
    completeness: str = "unknown"
    """Sequence completeness classification."""
    
    # Gap information
    gap_count: int = 0
    """Number of identified gaps in the sequence."""
    
    gap_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Gap IDs that affect this sequence."""
    
    provenance: str = "canonical"
    """Provenance reference for this sequence."""
    
    @classmethod
    def from_events(
        cls,
        event_ids: Tuple[str, ...],
        order_relations: Tuple[SequenceOrderRelation, ...] = (),
        confidence: float = 0.5,
        completeness: str = "unknown",
    ) -> NarrativeSequence:
        """Create a sequence from events and ordering relations."""
        return cls(
            sequence_id=f"sequence_{id(cls)}",
            events=event_ids,
            order_relations=order_relations,
            confidence=confidence,
            completeness=completeness,
            gap_count=0,
        )


# =============================================================================
# TEMPORAL RELATION KINDS (re-exported for convenience)
# =============================================================================

# Re-exports from enums
from .enums import TemporalRelationKind as TemporalRelationKindEnum


@dataclass(frozen=True, slots=True)
class NarrativeTemporalRelation:
    """
    Immutable temporal relation between two narrative elements.
    
    Used to specify temporal ordering when events or sequences are compared.
    """
    
    relation_id: str
    """Unique identifier for this temporal relation."""
    
    element_a_id: str
    """First element ID (event, sequence, or episode)."""
    
    element_b_id: str
    """Second element ID."""
    
    kind: str  # TemporalRelationKind.*
    """The type of temporal relationship."""
    
    confidence: float = 0.5
    """Confidence in this relation (0.0 to 1.0)."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Source references supporting this relation."""
    
    @classmethod
    def precedes(
        cls,
        element_a_id: str,
        element_b_id: str,
        confidence: float = 0.5,
    ) -> NarrativeTemporalRelation:
        """Create a 'precedes' temporal relation."""
        return cls(
            relation_id=f"temp_rel_{id(cls)}",
            element_a_id=element_a_id,
            element_b_id=element_b_id,
            kind="before",
            confidence=confidence,
        )
    
    @classmethod
    def overlaps(
        cls,
        element_a_id: str,
        element_b_id: str,
        confidence: float = 0.5,
    ) -> NarrativeTemporalRelation:
        """Create an 'overlaps' temporal relation."""
        return cls(
            relation_id=f"temp_rel_{id(cls)}",
            element_a_id=element_a_id,
            element_b_id=element_b_id,
            kind="overlaps",
            confidence=confidence,
        )