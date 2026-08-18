# Autobiographical Set - Phase 7.31
# ==================================

"""
Autobiographical Set.

An autobiographical set defines the participating experiences, constraints,
and policies for an autobiographical reasoning session.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class AutobiographicalObject:
    """
    An object participating in autobiographical reasoning.
    
    Objects include:
        - Episodes (experiences)
        - Missions
        - Goals
        - Reflections
        - Learning events
        - Major decisions
        - Identity transitions
    
    Each object maintains its own identity and historical lineage.
    """
    
    # Object identity
    object_identity: str                  # Unique identifier for the object
    temporal_position: float              # When in the timeline (Unix timestamp)
    object_type: str                      # e.g., "episode", "mission", "goal"
    
    # Autobiographical role
    autobiographical_role: str            # e.g., "turning_point", "ongoing_theme"
    
    # Supporting history
    supporting_history: str               # Evidence supporting inclusion
    narrative_weight: float = 1.0         # Weight in narrative construction
    
    # Provenance
    provenance: str = "unknown"           # Source of the object


@dataclass(frozen=True)
class AutobiographicalSet:
    """
    A set of objects participating in autobiographical reasoning.
    
    An autobiographical set defines:
        - Participating episodes, reflections, identity constraints
        - Chronological boundaries
        - Narrative policies
    
    Sets remain immutable during reasoning.
    """
    
    # Identity
    set_identity: str                     # Unique set identifier
    
    # Participating events/objects
    participating_objects: List[AutobiographicalObject]
    
    # Narrative scope
    narrative_scope: str                  # e.g., "lifetime", "year_2024"
    narrative_focus: Optional[str] = None  # Specific theme if any
    
    # Continuity constraints
    continuity_constraints: List[str]     # Constraints for identity continuity
    temporal_min_utc: Optional[float] = None
    temporal_max_utc: Optional[float] = None
    
    # Narrative policies
    narrative_policy: str = "complete"    # e.g., "complete", "thematic"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def object_count(self) -> int:
        """Number of participating objects."""
        return len(self.participating_objects)
    
    @property
    def sorted_by_time(self) -> List[AutobiographicalObject]:
        """Return objects sorted by temporal position."""
        return sorted(
            self.participating_objects,
            key=lambda obj: obj.temporal_position
        )
    
    @classmethod
    def create(
        cls,
        participating_objects: List[AutobiographicalObject],
        narrative_scope: str = "lifetime",
        narrative_focus: Optional[str] = None,
        continuity_constraints: Optional[List[str]] = None,
        temporal_min_utc: Optional[float] = None,
        temporal_max_utc: Optional[float] = None,
    ) -> AutobiographicalSet:
        """Create a new autobiographical set."""
        return cls(
            set_identity=f"autobiography_set:{uuid.uuid4().hex[:16]}",
            participating_objects=participating_objects,
            narrative_scope=narrative_scope,
            narrative_focus=narrative_focus,
            continuity_constraints=continuity_constraints or [],
            temporal_min_utc=temporal_min_utc,
            temporal_max_utc=temporal_max_utc,
        )


@dataclass(frozen=True)
class LifeNarrative:
    """
    A constructed life narrative from autobiographical reasoning.
    
    Narrative derives:
        - Major chapters
        - Important transitions
        - Long-term missions
        - Identity milestones
        - Critical events
        - Ongoing themes
    
    Narrative remains explicit.
    """
    
    # Identity
    narrative_identity: str               # Unique narrative identifier
    
    # Structure
    narrative_structure: Dict[str, Any]   # Chapters, sections, etc.
    major_chapters: List[str]
    transitions: List[Tuple[str, str]]    # (from_state, to_state)
    
    # Summary
    narrative_summary: str                # High-level summary
    narrative_confidence: float = 1.0     # Confidence in narrative
    
    # Provenance
    source_set_identity: str              # Which set produced this?
    reasoning_trace_id: Optional[str] = None


__all__ = [
    "AutobiographicalObject",
    "AutobiographicalSet",
    "LifeNarrative",
]