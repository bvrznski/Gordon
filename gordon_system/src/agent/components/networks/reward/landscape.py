# Reward Network - Reward Landscape
# ==================================

"""
Reward landscape model for reward evaluation.

A RewardLandscape represents a complete valuation of all evaluated outcomes,
preserving hierarchy, timescales, benefit/cost decomposition, and traceability.

LANDSCAPE LAWS:
    LANDSCAPE-LAW-001: Exactly one canonical RewardLandscape exists.
    LANDSCAPE-LAW-002: RewardLandscape is immutable.
    LANDSCAPE-LAW-003: RewardLandscape preserves every RewardEstimate.
    LANDSCAPE-LAW-004: RewardLandscape preserves hierarchy.
    LANDSCAPE-LAW-005: RewardLandscape preserves temporal partitions.
    LANDSCAPE-LAW-006: RewardLandscape preserves benefit decomposition.
    LANDSCAPE-LAW-007: RewardLandscape preserves cost decomposition.
    LANDSCAPE-LAW-008: RewardLandscape preserves provenance.
    LANDSCAPE-LAW-009: RewardLandscape preserves findings.
    LANDSCAPE-LAW-010: RewardLandscape shall not rank executive priority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


RewardEstimateRef = str
"""Reference to a RewardEstimate."""


@dataclass(frozen=True)
class MultiTimescaleReward:
    """
    Multi-timescale reward representation.
    
    Preserves reward evaluation across multiple temporal horizons without
    collapsing them into a single scalar value.
    
    TIMESCALES:
        • immediate: Current moment (0-5 seconds)
        • short_term: Near future (seconds to minutes)
        • medium_term: Intermediate horizon (minutes to hours)  
        • long_term: Extended horizon (hours to days)
        • persistent: Long-lasting effect
        • delayed: Effect with time lag
    """
    
    immediate: float = 0.0
    short_term: float = 0.0
    medium_term: float = 0.0
    long_term: float = 0.0
    persistent: float = 0.0
    delayed: float = 0.0
    
    @property
    def total(self) -> float:
        """Compute total across all timescales."""
        return (
            self.immediate +
            self.short_term + 
            self.medium_term +
            self.long_term +
            self.persistent +
            self.delayed
        )


@dataclass(frozen=True)
class HierarchicalReward:
    """
    Hierarchical reward representation.
    
    Preserves reward evaluation across different levels of the cognitive
    hierarchy without collapsing them into a single scalar value.
    
    HIERARCHY LEVELS:
        • action: Individual motor actions
        • task: Sequences of actions toward subgoal
        • goal: Strategic objectives  
        • strategy: High-level approaches
        • mission: Ultimate purpose
    """
    
    action_level: float = 0.0
    task_level: float = 0.0
    goal_level: float = 0.0
    strategy_level: float = 0.0
    mission_level: float = 0.0
    
    @property
    def total(self) -> float:
        """Compute total across all hierarchy levels."""
        return (
            self.action_level +
            self.task_level +
            self.goal_level +
            self.strategy_level +
            self.mission_level
        )


# =============================================================================
# REWARD LANDSCAPE (Phase 4.10.1 - Part 2)
# =============================================================================

@dataclass(frozen=True, slots=True)
class RewardLandscape:
    """
    Complete valuation of evaluated outcomes.
    
    The RewardLandscape represents the entire reward evaluation result,
    preserving all structure for downstream consumption without modification.
    
    PROPERTIES:
        • landscape_id: Unique identifier
        • estimate_refs: References to all RewardEstimates (always preserved)
        • timescale_rewards: Multi-timescale rewards (always preserved)
        • hierarchical_rewards: Hierarchical rewards (always preserved)
        • findings: Key evaluation findings
        • limitations: Known limitations
        • trace: Evaluation trace
        
    PROPERTIES - NOT RESPONSIBLE FOR:
        • Ranking executive priority
        • Selecting actions
        • Modifying beliefs or world model
        • Updating policies
        
    The RewardLandscape is the final semantic output of reward evaluation.
    Downstream systems consume it for their own computations.
    """
    
    # Identity and reference (no defaults first)
    landscape_id: str
    """Unique identifier for this landscape."""
    
    estimate_refs: Tuple[RewardEstimateRef, ...]
    """References to all RewardEstimates."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Timescale partitions (always preserved)
    timescale_rewards: MultiTimescaleReward = field(default_factory=MultiTimescaleReward)
    """Multi-timescale reward representation."""
    
    # Hierarchical partitions (always preserved)  
    hierarchical_rewards: HierarchicalReward = field(default_factory=HierarchicalReward)
    """Hierarchical reward representation."""
    
    # Summary statistics
    total_magnitude: float = 0.0
    """Sum of all estimate magnitudes."""
    
    positive_count: int = 0
    """Count of positive valence estimates."""
    
    negative_count: int = 0
    """Count of negative valence estimates."""
    
    neutral_count: int = 0
    """Count of neutral valence estimates."""
    
    # Metadata
    provenance: Optional[str] = None
    """Provenance reference for this landscape construction method."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from evaluation."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this landscape."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Evaluation trace for provenance."""
    
    @classmethod
    def create(
        cls,
        landscape_id: str,
        estimate_refs: Tuple[RewardEstimateRef, ...],
        total_magnitude: float = 0.0,
        positive_count: int = 0,
        negative_count: int = 0,
        neutral_count: int = 0,
    ) -> RewardLandscape:
        """
        Create a new reward landscape.
        
        Args:
            landscape_id: Unique identifier for this landscape
            estimate_refs: References to all RewardEstimates
            total_magnitude: Sum of all estimate magnitudes
            positive_count: Count of positive valence estimates
            negative_count: Count of negative valence estimates
            neutral_count: Count of neutral valence estimates
            
        Returns:
            New RewardLandscape instance
        """
        return cls(
            landscape_id=landscape_id,
            revision=0,
            estimate_refs=estimate_refs,
            total_magnitude=total_magnitude,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
        )
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.landscape_id}@v{self.revision}"
    
    @property
    def estimate_count(self) -> int:
        """Get count of estimated outcomes."""
        return len(self.estimate_refs)
