# Narrative Temporal Models
# =========================

"""
Immutable models for narrative temporal ordering and time references.

ARCHITECTURAL PRINCIPLES:
    - Event time, record time, and interpretation time are distinguished
    - Temporal precision is explicit
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


# =============================================================================
# NARRATIVE TEMPORAL SCOPE - Temporal constraints for narrative
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeTemporalScope:
    """
    Immutable temporal scope defining the time range and precision of a narrative.
    
    Narrative time preserves multiple timestamps:
        - event_time: When events actually occurred
        - record_time: When events were recorded in memory
        - interpretation_time: When interpretations were formed
        
    These times may differ, especially for remembered or simulated content.
    """
    
    start_time_utc: Optional[datetime] = None
    """Start of temporal relevance window."""
    
    end_time_utc: Optional[datetime] = None
    """End of temporal relevance window."""
    
    event_time_precision: str = "second"
    """Precision for event timestamps (second, minute, hour, day)."""
    
    record_time_precision: str = "millisecond"
    """Precision for record timestamps."""
    
    interpretation_time_precision: str = "second"
    """Precision for interpretation timestamps."""
    
    uncertainty_buffer_seconds: float = 60.0
    """Buffer for uncertain temporal relations."""
    
    @classmethod
    def from_window(
        cls,
        start_utc: datetime,
        end_utc: datetime,
    ) -> NarrativeTemporalScope:
        """Create a temporal scope from a time window."""
        return cls(
            start_time_utc=start_utc,
            end_time_utc=end_utc,
            event_time_precision="second",
            record_time_precision="millisecond",
            interpretation_time_precision="second",
            uncertainty_buffer_seconds=30.0,
        )
    
    @classmethod
    def current_context(cls) -> NarrativeTemporalScope:
        """Create a scope for current context (24-hour window)."""
        return cls(
            event_time_precision="second",
            record_time_precision="millisecond",
            interpretation_time_precision="second",
            uncertainty_buffer_seconds=30.0,
        )


# =============================================================================
# NARRATIVE TIME REFERENCE - Reference point for temporal statements
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeTimeReference:
    """
    Immutable reference point for temporal statements in a narrative.
    
    Each time reference includes its own timing and relationship to other times.
    """
    
    reference_id: str
    """Unique identifier for this time reference."""
    
    timestamp_utc: Optional[datetime] = None
    """Actual timestamp if known."""
    
    reference_kind: str = "absolute"
    """Kind of reference (absolute, relative, approximate)."""
    
    precision: str = "second"
    """Time precision level."""
    
    confidence: float = 0.5
    """Confidence in the time reference (0.0 to 1.0)."""
    
    @classmethod
    def absolute(
        cls,
        timestamp_utc: datetime,
        precision: str = "second",
    ) -> NarrativeTimeReference:
        """Create an absolute time reference."""
        return cls(
            reference_id=f"time_ref_{id(cls)}",
            timestamp_utc=timestamp_utc,
            reference_kind="absolute",
            precision=precision,
            confidence=0.95,
        )
    
    @classmethod
    def relative_to_event(
        cls,
        event_id: str,
        offset_seconds: float,
        uncertainty_seconds: float = 0.0,
    ) -> NarrativeTimeReference:
        """Create a time reference relative to an event."""
        return cls(
            reference_id=f"time_ref_{id(cls)}",
            timestamp_utc=None,
            reference_kind="relative",
            precision="second",
            confidence=0.5 - (uncertainty_seconds / 3600),
        )


# =============================================================================
# NARRATIVE TEMPORAL RELATION - Temporal relationship between elements
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeTemporalRelation:
    """
    Immutable relation specifying temporal ordering between narrative elements.
    
    Used for both events and larger structures like sequences or episodes.
    """
    
    relation_id: str
    """Unique identifier for this temporal relation."""
    
    element_a_id: str
    """First element ID (event, sequence, episode)."""
    
    element_b_id: str
    """Second element ID."""
    
    kind: str  # TemporalRelationKind.*
    """Type of temporal relationship."""
    
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
        """Create a 'precedes' temporal relation (A before B)."""
        return cls(
            relation_id=f"temp_rel_{id(cls)}",
            element_a_id=element_a_id,
            element_b_id=element_b_id,
            kind="before",
            confidence=confidence,
        )
    
    @classmethod
    def after(
        cls,
        element_a_id: str,
        element_b_id: str,
        confidence: float = 0.5,
    ) -> NarrativeTemporalRelation:
        """Create an 'after' temporal relation (A after B)."""
        return cls(
            relation_id=f"temp_rel_{id(cls)}",
            element_a_id=element_a_id,
            element_b_id=element_b_id,
            kind="after",
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
    
    @classmethod
    def simultaneous(
        cls,
        element_a_id: str,
        element_b_id: str,
        confidence: float = 0.5,
    ) -> NarrativeTemporalRelation:
        """Create a 'simultaneous' temporal relation."""
        return cls(
            relation_id=f"temp_rel_{id(cls)}",
            element_a_id=element_a_id,
            element_b_id=element_b_id,
            kind="simultaneous",
            confidence=confidence,
        )
    
    @classmethod
    def unknown_order(
        cls,
        element_a_id: str,
        element_b_id: str,
    ) -> NarrativeTemporalRelation:
        """Create an 'unknown' temporal relation."""
        return cls(
            relation_id=f"temp_rel_{id(cls)}",
            element_a_id=element_a_id,
            element_b_id=element_b_id,
            kind="unknown",
            confidence=0.0,
        )