# Continuity Management - Phase 7.31
# ====================================

"""
Temporal Continuity Management.

Continuity evaluates identity persistence, goal continuity,
behavior continuity, and belief continuity across time.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class TemporalContinuity:
    """
    Continuity assessment across temporal intervals.
    
    Continuity evaluates:
        - Identity persistence
        - Experience ordering
        - Goal continuity
        - Mission continuity
        - Behavior continuity
        - Belief continuity
    
    Continuity remains explicit.
    """
    
    # Identity
    continuity_identity: str              # Unique continuity identifier
    
    # Evaluated intervals (start, end) in Unix timestamps
    evaluated_intervals: List[Tuple[float, float]]
    
    # Continuity metrics
    identity_continuity_score: float = 1.0
    goal_continuity_score: float = 1.0
    behavior_continuity_score: float = 1.0
    belief_continuity_score: float = 1.0
    
    # Summary
    continuity_summary: str = "continuous"
    continuity_confidence: float = 1.0
    
    # Provenance
    source_set_identity: str              # Which set was evaluated?
    
    @property
    def total_duration_seconds(self) -> float:
        """Calculate total duration of all intervals."""
        return sum(end - start for start, end in self.evaluated_intervals)
    
    @classmethod
    def create(
        cls,
        evaluated_intervals: List[Tuple[float, float]],
        source_set_identity: str,
    ) -> TemporalContinuity:
        """Create a new temporal continuity assessment."""
        return cls(
            continuity_identity=f"continuity:{uuid.uuid4().hex[:16]}",
            evaluated_intervals=evaluated_intervals,
            source_set_identity=source_set_identity,
        )


@dataclass(frozen=True)
class IdentityEvolution:
    """
    Identity evolution across the lifespan.
    
    Evolution determines:
        - Major cognitive changes
        - Goal evolution
        - Belief evolution
        - Mission evolution
        - Behavior evolution
        - Competency evolution
    
    Evolution remains explicit.
    """
    
    # Identity
    evolution_identity: str               # Unique evolution identifier
    
    # Identity changes
    identity_changes: List[str]
    trigger_events: List[Tuple[float, str]]  # (timestamp, description)
    
    # Resulting identity
    resulting_identity: str               # Description of evolved identity
    
    # Confidence
    identity_confidence: float = 1.0
    
    # Provenance
    source_set_identity: str              # Which set was evaluated?


@dataclass(frozen=True)
class NarrativePublication:
    """
    Published life narrative.
    
    Publication determines:
        - Identity summaries
        - Life summaries
        - Mission summaries
        - Continuity reports
        - Identity snapshots
    
    Publication remains explicit.
    """
    
    # Identity
    publication_identity: str             # Unique publication identifier
    
    # Published narrative
    published_narrative: Dict[str, Any]   # Complete narrative structure
    
    # Scope
    publication_scope: str                # e.g., "lifetime", "year_2024"
    publication_policy: str = "public"    # e.g., "public", "restricted"
    
    # Provenance
    source_narrative_identity: str        # Which narrative was published?
    published_at_utc: float = field(default_factory=time.time)


__all__ = [
    "TemporalContinuity",
    "IdentityEvolution",
    "NarrativePublication",
]