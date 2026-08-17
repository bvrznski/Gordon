# Interval Reasoning - Phase 7.8
# ===============================

"""
Canonical Interval Reasoning.

Interval reasoning evaluates durations, containment, adjacency, overlap,
precedence, and succession.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class IntervalRelationType(Enum):
    """Types of relations between intervals."""
    
    BEFORE = "before"                       # Interval A ends before B starts
    MEETS = "meets"                         # Interval A ends when B starts
    OVERLAPS = "overlaps"                   # Intervals overlap partially
    FINISHES = "finishes"                   # Intervals have same end, A starts later
    EQUALS = "equals"                       # Intervals are identical
    STARTS = "starts"                       # Intervals have same start, A ends earlier
    DURING = "during"                       # Interval A is during interval B


@dataclass(frozen=True)
class TemporalInterval:
    """
    Temporal interval representing a duration.
    
    Intervals represent durations and define:
        - Start (when it begins)
        - End (when it ends)
        - Duration
        - Granularity
        - Uncertainty
    
    Intervals remain explicit.
    """
    
    # Identity
    interval_id: str                        # Unique interval identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Boundaries
    start_timestamp_utc: float              # When does the interval begin?
    end_timestamp_utc: float                # When does the interval end?
    
    # Duration properties
    duration_seconds: Optional[float] = None  # Explicit duration if known
    
    # Granularity and uncertainty
    granularity_seconds: float = 1.0        # Resolution of measurement
    uncertainty_seconds: float = 0.0        # Uncertainty in timing
    
    # Provenance
    source_interval_id: Optional[str] = None   # If derived from another interval
    origin_system: str = "unknown"              # Where did the interval originate?
    
    @property
    def mid_timestamp(self) -> float:
        """Return the midpoint of this interval."""
        return (self.start_timestamp_utc + self.end_timestamp_utc) / 2.0
    
    @property
    def is_point_interval(self) -> bool:
        """Check if this is a point interval (duration ~ 0)."""
        return abs(self.duration_seconds or 0.0) < self.granularity_seconds * 0.1
    
    @property
    def is_valid(self) -> bool:
        """Check if the interval has valid boundaries."""
        return self.end_timestamp_utc >= self.start_timestamp_utc
    
    def contains_timepoint(self, timepoint: float) -> bool:
        """Check if a timepoint falls within this interval."""
        tolerance = self.uncertainty_seconds + self.granularity_seconds
        return (self.start_timestamp_utc - tolerance <= 
                timepoint <= 
                self.end_timestamp_utc + tolerance)
    
    def overlaps_with(self, other: TemporalInterval) -> bool:
        """Check if this interval overlaps with another."""
        return not (self.end_timestamp_utc < other.start_timestamp_utc or
                    other.end_timestamp_utc < self.start_timestamp_utc)
    
    def strictly_before(self, other: TemporalInterval) -> bool:
        """Check if this interval strictly precedes another."""
        return self.end_timestamp_utc <= other.start_timestamp_utc
    
    def strictly_after(self, other: TemporalInterval) -> bool:
        """Check if this interval strictly follows another."""
        return other.strictly_before(self)
    
    def contains_interval(self, other: TemporalInterval) -> bool:
        """Check if this interval fully contains another."""
        return (self.start_timestamp_utc <= other.start_timestamp_utc and
                self.end_timestamp_utc >= other.end_timestamp_utc)
    
    def starts_at(self, other: TemporalInterval) -> bool:
        """Check if this interval starts at the same time as another."""
        return abs(self.start_timestamp_utc - other.start_timestamp_utc) < self.granularity_seconds
    
    def finishes_at(self, other: TemporalInterval) -> bool:
        """Check if this interval ends at the same time as another."""
        return abs(self.end_timestamp_utc - other.end_timestamp_utc) < self.granularity_seconds


@dataclass(frozen=True)
class IntervalReasoning:
    """
    Result of interval reasoning over a set of intervals.
    
    Interval reasoning evaluates:
        - Duration
        - Containment
        - Adjacency
        - Overlap
        - Precedence
        - Succession
    
    Intervals remain explicit.
    """
    
    # Identity
    reasoning_id: str                       # Unique reasoning identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Input intervals
    participating_intervals: Tuple[TemporalInterval, ...]
    
    # Inferred relations
    inferred_relations: Tuple[IntervalRelationType, ...] = ()  # Relations found
    
    # Consistency assessment
    consistency: float = 1.0                # Consistency score (0.0 to 1.0)
    consistency_issues: Tuple[str, ...] = ()   # Any issues found
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_reasoning_id: Optional[str] = None   # If derived from another analysis
    origin_context: str = "unknown"             # Where did the reasoning originate?
    
    @property
    def interval_count(self) -> int:
        """Return the number of intervals analyzed."""
        return len(self.participating_intervals)
    
    @property
    def has_issues(self) -> bool:
        """Check if any consistency issues were found."""
        return len(self.consistency_issues) > 0
    
    def get_interval_by_id(self, interval_id: str) -> Optional[TemporalInterval]:
        """Get an interval by its ID."""
        for interval in self.participating_intervals:
            if interval.interval_id == interval_id:
                return interval
        return None
    
    def find_overlapping_pairs(self) -> List[Tuple[str, str]]:
        """Find all pairs of overlapping intervals."""
        overlaps = []
        intervals = list(self.participating_intervals)
        
        for i, interval1 in enumerate(intervals):
            for interval2 in intervals[i+1:]:
                if interval1.overlaps_with(interval2):
                    overlaps.append((interval1.interval_id, interval2.interval_id))
        
        return overlaps
    
    def find_before_relations(self) -> List[Tuple[str, str]]:
        """Find all before relations between intervals."""
        before_rels = []
        intervals = list(self.participating_intervals)
        
        for i, interval1 in enumerate(intervals):
            for interval2 in intervals[i+1:]:
                if interval1.strictly_before(interval2):
                    before_rels.append((interval1.interval_id, interval2.interval_id))
        
        return before_rels
    
    def find_after_relations(self) -> List[Tuple[str, str]]:
        """Find all after relations between intervals."""
        after_rels = []
        intervals = list(self.participating_intervals)
        
        for i, interval1 in enumerate(intervals):
            for interval2 in intervals[i+1:]:
                if interval1.strictly_after(interval2):
                    after_rels.append((interval1.interval_id, interval2.interval_id))
        
        return after_rels


@dataclass(frozen=True)
class IntervalReasoningIdentity:
    """
    Immutable identity for an interval reasoning result.
    
    Allows replay and verification of interval analysis results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    reasoning_number: int = 1                 # For repeated reasonings
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, reasoning_number: int = 1) -> IntervalReasoningIdentity:
        """Create a new interval reasoning identity."""
        return cls(
            semantic_identity=semantic_identity,
            reasoning_number=reasoning_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalInterval",
    "IntervalReasoning",
    "IntervalReasoningIdentity",
    "IntervalRelationType",
]