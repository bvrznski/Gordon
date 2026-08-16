# Reward Network - Reward Trajectory Model (Phase 4.10.4)
# =========================================================

"""
Reward trajectory model for temporal reward evolution.

A RewardTrajectory represents the longitudinal evolution of reward values over time,
preserving semantic meaning without statistical modeling or prediction.

TRAJECTORY TYPES:
    • increasing: Reward value growing over time
    • decreasing: Reward value declining over time  
    • stable: Reward value remaining relatively constant
    • oscillating: Reward value fluctuating periodically
    • plateau: Initial increase followed by leveling off
    • recovering: Decline followed by recovery
    • collapsing: Rapid decline to near-zero or negative
    • unknown: Insufficient data to determine pattern

TRAJECTORY LAWS:
    TRAJECTORY-LAW-001: Every RewardTrajectory references at least one RewardEstimate.
    TRAJECTORY-LAW-002: RewardTrajectories remain immutable.
    TRAJECTORY-LAW-003: Trajectory type remains explicit.
    TRAJECTORY-LAW-004: Trajectory confidence remains independent.
    TRAJECTORY-LAW-005: Trajectory uncertainty remains independent.
    TRAJECTORY-LAW-006: Trajectory provenance remains preserved.
    TRAJECTORY-LAW-007: Trajectory revisions preserve lineage.
    TRAJECTORY-LAW-008: Trajectory estimation remains deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


TrajectoryKind = str
"""Type alias for trajectory kinds."""


@dataclass(frozen=True)
class RewardTrajectory:
    """
    Longitudinal evolution model for a single reward estimate.
    
    A trajectory represents how a particular reward value evolves through time,
    capturing patterns like growth, decay, stability, and oscillation. The 
    trajectory is descriptive - it does not predict future values or modify
    any system state.
    
    PROPERTIES:
        • trajectory_id: Unique identifier for this trajectory
        • estimate_ref: Reference to the RewardEstimate being modeled
        • trajectory_type: Semantic type of evolution pattern
        • trend: Directional summary (increasing/decreasing/stable)
        • stability: Resistance to change over time
        • volatility: Short-term variability measure
        • timescale: Temporal horizon of analysis
        • confidence: Confidence in the trajectory type
        • uncertainty: Uncertainty about the pattern
        
    NOT RESPONSIBLE FOR:
        • Predicting future reward values
        • Learning policies from trajectories
        • Making executive decisions
        • Modifying estimates or histories
    
    The trajectory is a semantic representation of temporal behavior.
    It answers "How is this reward changing?" not "What will it become?"
    """
    
    # Identity and reference (no defaults first)
    trajectory_id: str
    """Unique identifier for this trajectory."""
    
    estimate_ref: str  # RewardEstimate.canonical_identity
    """Reference to the RewardEstimate being modeled."""
    
    trajectory_type: TrajectoryKind  # TrajectoryKind.*
    """Semantic type of evolution pattern."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Semantic analysis fields (always preserved)
    trend: str = "stable"  # increasing/decreasing/stable/unknown
    """Directional summary over the observation period."""
    
    stability: float = 1.0
    """Resistance to change (0.0=unstable, 1.0=stable)."""
    
    volatility: float = 0.0
    """Short-term variability measure (0.0=no variance, higher=more variable)."""
    
    # Temporal context
    timescale: str = "medium_term"  # immediate/short_term/medium_term/long_term/persistent
    """Temporal horizon of this trajectory analysis."""
    
    # Semantic evaluation fields
    confidence: float = 1.0
    """Confidence in the trajectory classification."""
    
    uncertainty: float = 0.0
    """Uncertainty about the trajectory type."""
    
    # Provenance and lineage
    baseline_ref: Optional[str] = None
    """Reference to the AdaptiveRewardBaseline used as context."""
    
    history_window: int = 1
    """Number of historical points in this analysis."""
    
    provenance: Optional[str] = None
    """Provenance reference for this trajectory construction."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from trajectory analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.trajectory_id}@v{self.revision}"
    
    @classmethod
    def create_increasing(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        confidence: float = 1.0,
        volatility: float = 0.1,
        timescale: str = "medium_term",
    ) -> RewardTrajectory:
        """Create an increasing reward trajectory."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="increasing",
            trend="increasing",
            stability=0.5 + (1.0 - volatility) * 0.3,  # decreasing stability with higher volatility
            volatility=volatility,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            timescale=timescale,
        )
    
    @classmethod
    def create_decreasing(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        confidence: float = 1.0,
        volatility: float = 0.1,
        timescale: str = "medium_term",
    ) -> RewardTrajectory:
        """Create a decreasing reward trajectory."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="decreasing",
            trend="decreasing",
            stability=0.5 + (1.0 - volatility) * 0.3,
            volatility=volatility,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            timescale=timescale,
        )
    
    @classmethod
    def create_stable(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        confidence: float = 1.0,
        volatility: float = 0.05,
        timescale: str = "medium_term",
    ) -> RewardTrajectory:
        """Create a stable reward trajectory."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="stable",
            trend="stable",
            stability=1.0 - volatility * 0.5,  # high stability with low volatility
            volatility=volatility,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            timescale=timescale,
        )
    
    @classmethod
    def create_oscillating(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        confidence: float = 1.0,
        amplitude: float = 0.2,
        timescale: str = "short_term",
    ) -> RewardTrajectory:
        """Create an oscillating reward trajectory."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="oscillating",
            trend="stable",  # oscillation averages to stable direction
            stability=0.3,  # inherently less stable due to fluctuations
            volatility=amplitude * 2.0,  # volatility proportional to amplitude
            confidence=confidence,
            uncertainty=1.0 - confidence,
            timescale=timescale,
        )
    
    @classmethod
    def create_plateau(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        confidence: float = 1.0,
        initial_growth: float = 0.3,
        plateau_level: float = 0.5,
        timescale: str = "long_term",
    ) -> RewardTrajectory:
        """Create a plateau reward trajectory (initial increase then leveling)."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="plateau",
            trend="stable",  # final phase dominates
            stability=0.8,  # stable after initial change
            volatility=0.1,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            timescale=timescale,
        )
    
    @classmethod
    def create_recovering(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        confidence: float = 1.0,
        initial_decline: float = 0.3,
        recovery_rate: float = 0.2,
        timescale: str = "medium_term",
    ) -> RewardTrajectory:
        """Create a recovering reward trajectory."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="recovering",
            trend="increasing",  # final phase dominates
            stability=0.4,  # recovery indicates instability
            volatility=0.2,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            timescale=timescale,
        )
    
    @classmethod
    def create_collapsing(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        confidence: float = 1.0,
        collapse_rate: float = 0.4,
        timescale: str = "short_term",
    ) -> RewardTrajectory:
        """Create a collapsing reward trajectory."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="collapsing",
            trend="decreasing",
            stability=0.1,  # highly unstable during collapse
            volatility=collapse_rate * 2.0,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            timescale=timescale,
        )
    
    @classmethod
    def create_unknown(
        cls,
        trajectory_id: str,
        estimate_ref: str,
        uncertainty: float = 0.5,
        timescale: str = "immediate",
    ) -> RewardTrajectory:
        """Create an unknown reward trajectory (insufficient data)."""
        return cls(
            trajectory_id=trajectory_id,
            estimate_ref=estimate_ref,
            trajectory_type="unknown",
            trend="unknown",
            stability=0.5,  # neutral uncertainty
            volatility=uncertainty * 2.0,  # high uncertainty implies higher observed variance
            confidence=1.0 - uncertainty,
            uncertainty=uncertainty,
            timescale=timescale,
        )
    
    @property
    def is_increasing(self) -> bool:
        """Check if trajectory type indicates increasing reward."""
        return self.trajectory_type == "increasing"
    
    @property
    def is_decreasing(self) -> bool:
        """Check if trajectory type indicates decreasing reward."""
        return self.trajectory_type == "decreasing"
    
    @property
    def is_stable(self) -> bool:
        """Check if trajectory type indicates stable reward."""
        return self.trajectory_type == "stable"
    
    @property
    def is_oscillating(self) -> bool:
        """Check if trajectory type indicates oscillating reward."""
        return self.trajectory_type == "oscillating"
    
    @property
    def has_sufficient_data(self) -> bool:
        """Check if there's enough data for meaningful analysis."""
        return self.history_window >= 1 and self.confidence > 0.3


# =============================================================================
# REWARD TRAJECTORY COLLECTION (Aggregation)
# =============================================================================

@dataclass(frozen=True)
class RewardTrajectoryCollection:
    """
    Collection of reward trajectories across multiple estimates.
    
    Aggregates individual trajectories into a semantic summary while
    preserving all individual trajectory details for downstream analysis.
    
    PROPERTIES:
        • collection_id: Unique identifier for this collection
        • trajectories: Individual trajectory models
        • dominant_pattern: Most common trajectory type in collection
        • summary_trend: Overall directional trend across all estimates
        • aggregate_stability: Weighted stability measure
        
    NOT RESPONSIBLE FOR:
        • Modifying individual trajectories
        • Making decisions based on patterns
        • Learning from temporal data
    """
    
    # Identity and reference (no defaults first)
    collection_id: str
    """Unique identifier for this trajectory collection."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Trajectory storage (always preserved)
    trajectories: Tuple[RewardTrajectory, ...] = field(default_factory=tuple)
    """Individual reward trajectories in this collection."""
    
    # Semantic aggregation fields
    dominant_pattern: str = "unknown"
    """Most common trajectory type across all estimates."""
    
    summary_trend: str = "stable"
    """Overall directional trend across the collection."""
    
    aggregate_stability: float = 1.0
    """Weighted stability measure across all trajectories."""
    
    # Timescale coverage
    timescales_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Timescales covered by this trajectory analysis."""
    
    provenance: Optional[str] = None
    """Provenance reference for this collection."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from trajectory collection analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Collection analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.collection_id}@v{self.revision}"
    
    @property
    def trajectory_count(self) -> int:
        """Get count of trajectories in this collection."""
        return len(self.trajectories)
    
    @property
    def has_trajectories(self) -> bool:
        """Check if any trajectories exist in the collection."""
        return len(self.trajectories) > 0
    
    @classmethod
    def create_empty(cls, collection_id: str) -> RewardTrajectoryCollection:
        """Create an empty trajectory collection."""
        return cls(
            collection_id=collection_id,
            trajectories=tuple(),
            dominant_pattern="unknown",
            summary_trend="stable",
            aggregate_stability=1.0,
        )
    
    @classmethod
    def from_trajectories(
        cls,
        collection_id: str,
        trajectories: Tuple[RewardTrajectory, ...],
    ) -> RewardTrajectoryCollection:
        """
        Create a trajectory collection from individual trajectories.
        
        Analyzes the distribution of trajectory types and computes
        aggregate semantic measures.
        """
        if not trajectories:
            return cls.create_empty(collection_id)
        
        # Count trajectory type frequencies
        pattern_counts: dict[str, int] = {}
        for t in trajectories:
            pattern_counts[t.trajectory_type] = pattern_counts.get(t.trajectory_type, 0) + 1
        
        # Find dominant pattern (most common)
        dominant_pattern = max(pattern_counts.items(), key=lambda x: x[1])[0]
        
        # Compute aggregate stability
        total_stability = sum(t.stability for t in trajectories)
        aggregate_stability = total_stability / len(trajectories)
        
        # Determine summary trend based on trajectory trends
        trend_counts: dict[str, int] = {}
        for t in trajectories:
            trend_counts[t.trend] = trend_counts.get(t.trend, 0) + 1
        
        # Most common trend dominates (with stability weighted toward 'stable')
        if "stable" in trend_counts and trend_counts["stable"] >= len(trajectories) * 0.5:
            summary_trend = "stable"
        else:
            summary_trend = max(trend_counts.items(), key=lambda x: x[1])[0]
        
        # Collect timescales analyzed
        timescales = tuple(set(t.timescale for t in trajectories))
        
        return cls(
            collection_id=collection_id,
            trajectories=trajectories,
            dominant_pattern=dominant_pattern,
            summary_trend=summary_trend,
            aggregate_stability=aggregate_stability,
            timescales_analyzed=timescales,
        )