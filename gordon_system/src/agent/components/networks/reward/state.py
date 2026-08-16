# Reward Network - State Models (Phase 4.10.1-4)
# ================================================

"""
Reward state models for tracking evaluation results and temporal analysis.

This file contains both Phase 4.10.1-3 basic reward states AND
Phase 4.10.4 temporal aggregation states.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# REWARD STATE (Phase 4.10.1-3 - Basic state tracking)
# =============================================================================

@dataclass(frozen=True)
class RewardState:
    """
    Current state of the reward evaluation system.
    
    PROPERTIES:
        • landscape: Current RewardLandscape (or None if not computed)
        • baseline: Reference baseline for comparison
        • history: Recent evaluation history
        
    NOT RESPONSIBLE FOR:
        • Learning or adapting policies
        • Modifying previous landscapes
        • Making executive decisions
    """
    
    state_id: str = "default"
    """Unique identifier for this state."""
    
    current_landscape: Optional[dict] = None
    """Current reward landscape (or None)."""
    
    baseline: Optional[dict] = None
    """Reference baseline for comparison."""
    
    history: Tuple[dict, ...] = field(default_factory=tuple)
    """Recent evaluation history."""
    
    @property
    def has_landscape(self) -> bool:
        """Check if a landscape is present."""
        return self.current_landscape is not None
    
    @property
    def estimate_count(self) -> int:
        """Get count of estimates in current landscape."""
        if not self.current_landscape:
            return 0
        return len(self.current_landscape.get("reward_estimates", ()))


# =============================================================================
# TEMPORAL REWARD STATE (Phase 4.10.4 - Temporal aggregation)
# =============================================================================

@dataclass(frozen=True)
class TemporalRewardState:
    """
    Aggregate temporal reward state representing the complete longitudinal
    evaluation of how reward values are changing over time.
    
    This is the canonical output of Phase 4.10.4 - Reward Dynamics &
    Adaptive Baseline Engine. It combines all temporal analyses into a single,
    immutable semantic projection without modifying any reward estimates or
    making decisions based on the analysis.
    
    PROPERTIES:
        • state_id: Unique identifier for this temporal reward state
        • trajectories: Individual trajectory models for each estimate
        • baselines: Current adaptive baseline values
        • trends: Directional trend analysis
        • stability: Resistance to change measures
        • volatility: Short-term variability measures
        • drift: Long-term valuation shifts
        • homeostasis: Equilibrium state analysis
        
    NOT RESPONSIBLE FOR:
        • Modifying reward estimates from Phase 4.10.3
        • Learning or adapting policies
        • Making executive decisions
        • Selecting actions
    """
    
    # Identity and reference (no defaults first)
    state_id: str
    """Unique identifier for this temporal reward state."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Temporal analysis results (always preserved)
    trajectories: Tuple[dict, ...] = field(default_factory=tuple)
    """Individual trajectory models for each estimate (as dicts)."""
    
    baselines: Tuple[dict, ...] = field(default_factory=tuple)
    """Current adaptive baseline values (as dicts)."""
    
    trends: Tuple[dict, ...] = field(default_factory=tuple)
    """Directional trend analysis results (as dicts)."""
    
    stability: Tuple[dict, ...] = field(default_factory=tuple)
    """Resistance to change measures (as dicts)."""
    
    volatility: Tuple[dict, ...] = field(default_factory=tuple)
    """Short-term variability measures (as dicts)."""
    
    drift: Tuple[dict, ...] = field(default_factory=tuple)
    """Long-term valuation shift analysis (as dicts)."""
    
    homeostasis: Tuple[dict, ...] = field(default_factory=tuple)
    """Equilibrium state analysis results (as dicts)."""
    
    # Aggregated collections (always preserved)
    trajectory_collection: Optional[dict] = None
    """Aggregated trajectory collection."""
    
    trend_collection: Optional[dict] = None
    """Aggregated trend collection."""
    
    stability_collection: Optional[dict] = None
    """Aggregated stability collection."""
    
    volatility_collection: Optional[dict] = None
    """Aggregated volatility collection."""
    
    drift_collection: Optional[dict] = None
    """Aggregated drift collection."""
    
    homeostasis_collection: Optional[dict] = None
    """Aggregated homeostasis collection."""
    
    # Semantic summary (always preserved)
    dominant_trajectory_pattern: str = "unknown"
    """Most common trajectory pattern across estimates."""
    
    dominant_trend_direction: str = "stable"
    """Most common trend direction across domains."""
    
    aggregate_stability: float = 1.0
    """Overall stability level."""
    
    aggregate_volatility: float = 0.0
    """Overall volatility level."""
    
    # Temporal context
    observation_window: int = 1
    """Total number of time units analyzed."""
    
    timescales_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Timescales covered by this analysis."""
    
    domains_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic domains covered by this analysis."""
    
    # History (always preserved)
    history: Optional[dict] = None
    """Historical record of evaluations."""
    
    # Provenance and trace
    provenance: Optional[str] = None
    """Provenance reference for this state construction."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from temporal analysis."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this state."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.state_id}@v{self.revision}"
    
    # Aggregation properties
    @property
    def trajectory_count(self) -> int:
        """Get count of analyzed trajectories."""
        return len(self.trajectories)
    
    @property
    def baseline_count(self) -> int:
        """Get count of analyzed baselines."""
        return len(self.baselines)
    
    @property
    def trend_count(self) -> int:
        """Get count of analyzed trends."""
        return len(self.trends)
    
    @property
    def stability_count(self) -> int:
        """Get count of analyzed stabilities."""
        return len(self.stability)
    
    @property
    def volatility_count(self) -> int:
        """Get count of analyzed volatilities."""
        return len(self.volatility)
    
    @property
    def drift_count(self) -> int:
        """Get count of analyzed drifts."""
        return len(self.drift)
    
    @property
    def homeostasis_count(self) -> int:
        """Get count of analyzed homeostases."""
        return len(self.homeostasis)
    
    @property
    def has_estimates_analyzed(self) -> bool:
        """Check if any estimates were analyzed."""
        return self.trajectory_count > 0
    
    # Factory methods for state creation
    @classmethod
    def create_empty(cls, state_id: str) -> TemporalRewardState:
        """Create an empty temporal reward state."""
        return cls(
            state_id=state_id,
        )
    
    @classmethod
    def from_analysis_dict(
        cls,
        state_id: str,
        trajectories: Tuple[dict, ...] = tuple(),
        baselines: Tuple[dict, ...] = tuple(),
        trends: Tuple[dict, ...] = tuple(),
        stabilities: Tuple[dict, ...] = tuple(),
        volatilities: Tuple[dict, ...] = tuple(),
        drifts: Tuple[dict, ...] = tuple(),
        homeostases: Tuple[dict, ...] = tuple(),
        history: Optional[dict] = None,
        observation_window: int = 1,
    ) -> TemporalRewardState:
        """
        Create a temporal reward state from analysis result dictionaries.
        
        Args:
            state_id: Unique identifier for this state
            trajectories: Individual trajectory dicts
            baselines: Baseline value dicts
            trends: Trend analysis dicts
            stabilities: Stability measure dicts
            volatilities: Volatility measure dicts
            drifts: Drift analysis dicts
            homeostases: Homeostasis state dicts
            history: History dict (optional)
            observation_window: Total time units analyzed
            
        Returns:
            New TemporalRewardState instance with all analyses aggregated
        """
        # Compute aggregates
        trajectory_collection = cls._aggregate_trajectories(trajectories)
        trend_collection = cls._aggregate_trends(trends)
        stability_collection = cls._aggregate_stabilities(stabilities)
        volatility_collection = cls._aggregate_volatilities(volatilities)
        drift_collection = cls._aggregate_drifts(drifts)
        homeostasis_collection = cls._aggregate_homeostases(homeostases)
        
        # Build state dictionary
        return cls(
            state_id=state_id,
            revision=0,
            trajectories=trajectories,
            baselines=baselines,
            trends=trends,
            stability=stabilities,
            volatility=volatilities,
            drift=drifts,
            homeostasis=homeostases,
            trajectory_collection=trajectory_collection,
            trend_collection=trend_collection,
            stability_collection=stability_collection,
            volatility_collection=volatility_collection,
            drift_collection=drift_collection,
            homeostasis_collection=homeostasis_collection,
            dominant_trajectory_pattern=trajectory_collection.get("dominant_pattern", "unknown"),
            dominant_trend_direction=trend_collection.get("dominant_direction", "stable"),
            aggregate_stability=stability_collection.get("aggregate_stability", 1.0),
            aggregate_volatility=volatility_collection.get("aggregate_volatility", 0.0),
            observation_window=observation_window,
            timescales_analyzed=tuple(trajectory_collection.get("timescales_analyzed", ())),
            domains_analyzed=tuple(set(b.get("domain", "") for b in baselines)),
            history=history,
            provenance="phase_4_10_4_temporal_analysis",
            findings=("analysis_complete",),
            limitations=(),
            trace=("STATE_CREATED", "VALIDATION_COMPLETED"),
        )
    
    @classmethod
    def _aggregate_trajectories(cls, trajectories: Tuple[dict, ...]) -> dict:
        """Aggregate trajectory collection."""
        if not trajectories:
            return {"collection_id": "", "dominant_pattern": "unknown"}
        
        pattern_counts = {}
        for t in trajectories:
            pt = t.get("trajectory_type", "unknown")
            pattern_counts[pt] = pattern_counts.get(pt, 0) + 1
        
        dominant_pattern = max(pattern_counts.items(), key=lambda x: x[1])[0] if pattern_counts else "unknown"
        avg_stability = sum(t.get("stability", 1.0) for t in trajectories) / len(trajectories) if trajectories else 1.0
        
        return {
            "collection_id": "trajectory-collection",
            "dominant_pattern": dominant_pattern,
            "summary_trend": "stable" if dominant_pattern == "stable" else "directional",
            "aggregate_stability": avg_stability,
            "timescales_analyzed": ("medium_term",),
        }
    
    @classmethod
    def _aggregate_trends(cls, trends: Tuple[dict, ...]) -> dict:
        """Aggregate trend collection."""
        if not trends:
            return {"collection_id": "", "dominant_direction": "stable"}
        
        direction_counts = {}
        for t in trends:
            d = t.get("direction", "stable")
            direction_counts[d] = direction_counts.get(d, 0) + 1
        
        dominant_direction = max(direction_counts.items(), key=lambda x: x[1])[0] if direction_counts else "stable"
        avg_consistency = sum(t.get("consistency", 1.0) for t in trends) / len(trends) if trends else 1.0
        
        return {
            "collection_id": "trend-collection",
            "dominant_direction": dominant_direction,
            "aggregate_consistency": avg_consistency,
        }
    
    @classmethod
    def _aggregate_stabilities(cls, stabilities: Tuple[dict, ...]) -> dict:
        """Aggregate stability collection."""
        if not stabilities:
            return {"collection_id": "", "aggregate_stability": 1.0}
        
        aggregate = sum(s.get("value", 1.0) for s in stabilities) / len(stabilities) if stabilities else 1.0
        
        return {
            "collection_id": "stability-collection",
            "aggregate_stability": aggregate,
        }
    
    @classmethod
    def _aggregate_volatilities(cls, volatilities: Tuple[dict, ...]) -> dict:
        """Aggregate volatility collection."""
        if not volatilities:
            return {"collection_id": "", "aggregate_volatility": 0.0}
        
        aggregate = sum(v.get("value", 0.0) for v in volatilities) / len(volatilities) if volatilities else 0.0
        
        return {
            "collection_id": "volatility-collection",
            "aggregate_volatility": aggregate,
        }
    
    @classmethod
    def _aggregate_drifts(cls, drifts: Tuple[dict, ...]) -> dict:
        """Aggregate drift collection."""
        if not drifts:
            return {"collection_id": "", "dominant_direction": "neutral"}
        
        direction_counts = {}
        for d in drifts:
            dir_val = d.get("direction", "neutral")
            direction_counts[dir_val] = direction_counts.get(dir_val, 0) + 1
        
        dominant_direction = max(direction_counts.items(), key=lambda x: x[1])[0] if direction_counts else "neutral"
        
        return {
            "collection_id": "drift-collection",
            "dominant_direction": dominant_direction,
        }
    
    @classmethod
    def _aggregate_homeostases(cls, homeostases: Tuple[dict, ...]) -> dict:
        """Aggregate homeostasis collection."""
        if not homeostases:
            return {"collection_id": "", "aggregate_adaptation_pressure": 0.0}
        
        aggregate = sum(h.get("adaptation_pressure", 0.0) for h in homeostases) / len(homeostases) if homeostases else 0.0
        
        return {
            "collection_id": "homeostasis-collection",
            "aggregate_adaptation_pressure": aggregate,
        }


__all__ = [
    # Phase 4.10.1-3 basic state
    "RewardState",
    # Phase 4.10.4 temporal aggregation state
    "TemporalRewardState",
]