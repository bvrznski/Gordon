# Motivational Projection Network - Temporal Projections (Phase 4.10.6)
# ====================================================================

"""
TemporalProjection model for Phase 4.10.6.

This module defines temporal partitions for projections across different
timescales: immediate, short-term, medium-term, long-term, persistent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class TemporalProjection:
    """
    A projection with explicit temporal semantics.

    TEMPORAL-LAW-001: Timescales remain explicit (never implicit).
    TEMPORAL-LAW-002: Multiple timescales can coexist.
    TEMPORAL-LAW-003: Temporal partitioning is immutable.
    
    TIMESCALES:
        • immediate: Current action cycle
        • short-term: Next few steps/ticks
        • medium-term: Strategy execution period
        • long-term: Goal achievement horizon
        • persistent: Mission/identity level
    """
    
    projection_id: str
    """Projection ID being temporally partitioned."""
    
    temporal_context: str = "immediate"
    """Timescale context for this projection."""
    
    # Temporal characteristics
    onset: float = 0.0
    """Time of onset (normalized 0.0-1.0)."""
    
    offset: float = 1.0
    """Time of offset/decay (normalized 0.0-1.0)."""
    
    duration: str = "instantaneous"
    """Duration description."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.projection_id}@{self.temporal_context}"
    
    def to_dict(self) -> dict:
        """Convert temporal projection to dictionary representation."""
        return {
            "projection_id": self.projection_id,
            "temporal_context": self.temporal_context,
            "onset": self.onset,
            "offset": self.offset,
            "duration": self.duration,
        }
    
    @classmethod
    def create_immediate(cls, projection_id: str) -> TemporalProjection:
        """Create an immediate timescale projection."""
        return cls(
            projection_id=projection_id,
            temporal_context="immediate",
            duration="instantaneous",
        )
    
    @classmethod
    def create_short_term(cls, projection_id: str) -> TemporalProjection:
        """Create a short-term timescale projection."""
        return cls(
            projection_id=projection_id,
            temporal_context="short-term",
            duration="brief",
        )
    
    @classmethod
    def create_medium_term(cls, projection_id: str) -> TemporalProjection:
        """Create a medium-term timescale projection."""
        return cls(
            projection_id=projection_id,
            temporal_context="medium-term",
            duration="intermediate",
        )
    
    @classmethod
    def create_long_term(cls, projection_id: str) -> TemporalProjection:
        """Create a long-term timescale projection."""
        return cls(
            projection_id=projection_id,
            temporal_context="long-term",
            duration="extended",
        )
    
    @classmethod
    def create_persistent(cls, projection_id: str) -> TemporalProjection:
        """Create a persistent timescale projection."""
        return cls(
            projection_id=projection_id,
            temporal_context="persistent",
            duration="ongoing",
        )


@dataclass(frozen=True)
class ProjectionTimescales:
    """
    All temporal partitions for projections in an evaluation.

    TEMPORAL-LAW-004: Timescales remain explicit and independent.
    TEMPORAL-LAW-005: Temporal aggregates are preserved.
    
    NOT RESPONSIBLE FOR:
        • Scheduling
        • Timing decisions
        • Time management
    """
    
    timescale_id: str = "projection_timescales"
    """Unique identifier for this temporal partition."""
    
    revisions: Tuple[int, ...] = field(default_factory=tuple)
    """Revision numbers for each projection."""
    
    # Maps timescale to projections in that timescale
    immediate_projections: Tuple[str, ...] = field(default_factory=tuple)
    short_term_projections: Tuple[str, ...] = field(default_factory=tuple)
    medium_term_projections: Tuple[str, ...] = field(default_factory=tuple)
    long_term_projections: Tuple[str, ...] = field(default_factory=tuple)
    persistent_projections: Tuple[str, ...] = field(default_factory=tuple)
    
    # Temporal metadata
    provenance: str = "unknown"
    """Source information for traceability."""
    
    def get_projections_at_timescale(self, timescale: str) -> Tuple[str, ...]:
        """Get all projections at a specific timescale."""
        if timescale == "immediate":
            return self.immediate_projections
        elif timescale == "short-term":
            return self.short_term_projections
        elif timescale == "medium-term":
            return self.medium_term_projections
        elif timescale == "long-term":
            return self.long_term_projections
        elif timescale == "persistent":
            return self.persistent_projections
        return ()
    
    def to_dict(self) -> dict:
        """Convert timescales to dictionary representation."""
        return {
            "timescale_id": self.timescale_id,
            "immediate": list(self.immediate_projections),
            "short_term": list(self.short_term_projections),
            "medium_term": list(self.medium_term_projections),
            "long_term": list(self.long_term_projections),
            "persistent": list(self.persistent_projections),
        }
    
    @classmethod
    def create_empty(cls, timescale_id: str = "projection_timescales") -> ProjectionTimescales:
        """Create an empty temporal partition."""
        return cls(timescale_id=timescale_id)
    
    @classmethod
    def from_projection_list(
        cls,
        projections: Tuple[Tuple[str, str], ...],
        timescale_id: str = "projection_timescales",
    ) -> ProjectionTimescales:
        """
        Create timescales from (projection_id, timescale) tuples.
        
        Args:
            projections: List of (projection_id, timescale) tuples
            timescale_id: Unique identifier for this partition
        """
        immediate = []
        short_term = []
        medium_term = []
        long_term = []
        persistent = []
        
        for proj_id, timescale in projections:
            if timescale == "immediate":
                immediate.append(proj_id)
            elif timescale == "short-term":
                short_term.append(proj_id)
            elif timescale == "medium-term":
                medium_term.append(proj_id)
            elif timescale == "long-term":
                long_term.append(proj_id)
            elif timescale == "persistent":
                persistent.append(proj_id)
        
        return cls(
            timescale_id=timescale_id,
            immediate_projections=tuple(sorted(immediate)),
            short_term_projections=tuple(sorted(short_term)),
            medium_term_projections=tuple(sorted(medium_term)),
            long_term_projections=tuple(sorted(long_term)),
            persistent_projections=tuple(sorted(persistent)),
        )


__all__ = ["TemporalProjection", "ProjectionTimescales"]