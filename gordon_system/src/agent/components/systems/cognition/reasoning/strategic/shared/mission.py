# Strategic Mission Contract - Phase 7.37 Part 2
# ===============================================

"""
Mission Management for Strategic Reasoning.

This module implements the canonical mission contracts specified in Phase 7.37 Part 2:

- MissionManagement: Evaluates missions for coherence, feasibility, dependencies, priorities
- MissionIdentity: Unique identifier for mission tracking
- MissionModel: Formal representation of strategic intent
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MissionState(Enum):
    """Mission lifecycle states."""
    
    CREATED = "created"
    ANALYZING = "analyzing"
    VALIDATED = "validated"
    ACTIVE = "active"
    DEFERRED = "deferred"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MissionQuality(Enum):
    """Mission quality assessment categories."""
    
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


@dataclass(frozen=True)
class MissionIdentity:
    """
    Unique identifier for a mission.
    
    LAW: MISSION-LAW-001 - Every Mission shall possess one explicit identity.
    """
    
    mission_id: str               # UUID4 string
    semantic_identity: str        # Stable semantic reference across runs
    version: int                  # Version number for evolution tracking


@dataclass(frozen=True)
class MissionObjective:
    """
    Individual objective within a mission.
    
    LAW: MISSION-LAW-002 - Mission objectives shall remain explicit.
    """
    
    objective_id: str
    description: str
    priority: int                 # 1 = highest, N = lowest
    success_threshold: float      # 0.0 to 1.0 for quantitative assessment


@dataclass(frozen=True)
class MissionConstraint:
    """Constraints that bound mission execution."""
    
    constraint_id: str
    type: str                     # e.g., "resource", "timeline", "legal"
    description: str
    hard: bool                    # Hard constraints cannot be violated
    value: Any


@dataclass(frozen=True)
class MissionDependency:
    """
    Dependency relationship between missions.
    
    LAW: MISSION-LAW-003 - Mission priorities shall remain explicit.
    """
    
    dependency_id: str
    source_mission_id: str        # The mission that depends on another
    target_mission_id: str        # The mission being depended upon
    type: str                     # "hard", "soft", "optional"
    strength: float               # 0.0 to 1.0


@dataclass(frozen=True)
class MissionAnalysis:
    """
    Analysis result for a single mission.
    
    LAW: MISSION-LAW-004 - Mission provenance shall remain complete.
    """
    
    analysis_id: str
    mission_identity: MissionIdentity
    coherence_score: float        # How well-aligned is the mission?
    feasibility_score: float      # Can this mission be achieved?
    priority_rank: int            # Relative to other missions
    quality_rating: MissionQuality


@dataclass(frozen=True)
class MissionEvolution:
    """
    Records evolution of a mission over time.
    
    LAW: MISSION-LAW-005 - Mission revisions shall preserve history.
    """
    
    evolution_id: str
    mission_identity: MissionIdentity
    timestamp_utc: float
    change_type: str              # "revision", "refinement", "redefinition"
    previous_state_hash: str      # Hash of previous state for verification
    change_description: str


@dataclass(frozen=True)
class MissionModel:
    """
    Complete formal representation of a mission.
    
    LAW: MISSION-LAW-007 - Mission Models shall remain independently inspectable.
    """
    
    identity: MissionIdentity
    statement: str                # The mission statement/summary
    description: str              # Detailed mission description
    objectives: Tuple[MissionObjective, ...]
    constraints: Tuple[MissionConstraint, ...]
    dependencies: Tuple[MissionDependency, ...]
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def hash_state(self) -> str:
        """Compute state hash for evolution tracking."""
        import hashlib
        content = f"{self.identity.mission_id}:{self.identity.version}:{self.statement}:{self.description}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True)
class MissionManagement:
    """
    Mission management evaluation result.
    
    LAW: MISSION-LAW-008 - Equivalent missions shall produce equivalent strategic evaluations.
    """
    
    evaluation_id: str
    mission_identity: MissionIdentity
    analysis_results: Tuple[MissionAnalysis, ...]
    coherence_score: float
    feasibility_score: float
    priority_rank: int
    quality_rating: MissionQuality
    recommendations: Tuple[str, ...]  # Actionable recommendations
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Analysis metadata


@dataclass(frozen=True)
class MissionPortfolioAlignment:
    """
    How well a mission aligns with the current strategic portfolio.
    
    LAW: MISSION-LAW-006 - Mission evaluations shall never silently redefine mission objectives.
    """
    
    alignment_id: str
    mission_identity: MissionIdentity
    portfolio_mission_ids: Tuple[str, ...]
    alignment_score: float        # 0.0 to 1.0
    conflicts: Tuple[str, ...]    # List of conflict descriptions