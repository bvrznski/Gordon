# Reward Network - Trend Analysis Module (Phase 4.10.4)
# =======================================================

"""
Trend analysis module for temporal reward estimation.

Reward Trends represent the semantic direction, velocity, and consistency of
reward evolution over time. Trend analysis is descriptive - it does not predict
future values or modify any system state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


TrendDirection = str
"""Type alias for trend directions (increasing/decreasing/stable/unknown)."""

TrendVelocity = float
"""Type alias for trend velocity measures."""


@dataclass(frozen=True)
class RewardTrend:
    """
    Semantic representation of reward evolution direction and pattern.
    
    A trend captures the overall directional behavior of a reward estimate
    over its observation period. Unlike trajectory analysis, trends focus
    on aggregate direction rather than detailed temporal patterns.
    
    PROPERTIES:
        • trend_id: Unique identifier for this trend
        • domain: Semantic domain being analyzed
        • direction: Overall movement (increasing/decreasing/stable/unknown)
        • velocity: Rate of change
        • consistency: Stability of the directional pattern
        • acceleration: Change in velocity over time
        • persistence: How long the current trend has persisted
        
    NOT RESPONSIBLE FOR:
        • Predicting future trends
        • Learning policies from trend patterns
        • Modifying reward estimates
    
    Trends answer "Which way is reward moving?" not "Where will it go next?"
    """
    
    # Identity and reference (no defaults first)
    trend_id: str
    """Unique identifier for this trend."""
    
    domain: str  # BaselineDomain.*
    """Semantic domain this trend analyzes."""
    
    direction: TrendDirection = "stable"
    """Overall movement direction."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Velocity measures (always preserved)
    velocity: float = 0.0
    """Rate of change per time unit."""
    
    acceleration: float = 0.0
    """Change in velocity over time."""
    
    consistency: float = 1.0
    """How consistently the trend direction has been maintained."""
    
    # Persistence measures
    persistence: int = 0
    """Number of consecutive time units with consistent direction."""
    
    max_persistence: int = 0
    """Maximum observed persistence in history."""
    
    # Semantic evaluation fields
    confidence: float = 1.0
    """Confidence in the trend classification."""
    
    uncertainty: float = 0.0
    """Uncertainty about the trend direction."""
    
    # Provenance and context
    observation_window: int = 1
    """Number of time units in analysis window."""
    
    data_points: Tuple[float, ...] = field(default_factory=tuple)
    """Raw data points used for trend estimation."""
    
    provenance: Optional[str] = None
    """Provenance reference for this trend analysis."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from trend analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.trend_id}@v{self.revision}"
    
    # Factory methods for common trend types
    @classmethod
    def create_increasing_trend(
        cls,
        trend_id: str,
        domain: str = "reward",
        velocity: float = 0.1,
        consistency: float = 0.8,
        persistence: int = 3,
    ) -> RewardTrend:
        """Create an increasing reward trend."""
        return cls(
            trend_id=trend_id,
            domain=domain,
            direction="increasing",
            velocity=abs(velocity),
            acceleration=0.01 if velocity > 0 else -0.01,
            consistency=min(consistency, 1.0),
            persistence=persistence,
            max_persistence=max(persistence, 1),
            confidence=consistency,
            uncertainty=1.0 - consistency,
        )
    
    @classmethod
    def create_decreasing_trend(
        cls,
        trend_id: str,
        domain: str = "reward",
        velocity: float = -0.1,
        consistency: float = 0.8,
        persistence: int = 3,
    ) -> RewardTrend:
        """Create a decreasing reward trend."""
        return cls(
            trend_id=trend_id,
            domain=domain,
            direction="decreasing",
            velocity=-abs(velocity),
            acceleration=-0.01 if velocity < 0 else 0.01,
            consistency=min(consistency, 1.0),
            persistence=persistence,
            max_persistence=max(persistence, 1),
            confidence=consistency,
            uncertainty=1.0 - consistency,
        )
    
    @classmethod
    def create_stable_trend(
        cls,
        trend_id: str,
        domain: str = "reward",
        velocity: float = 0.0,
        consistency: float = 0.95,
        persistence: int = 10,
    ) -> RewardTrend:
        """Create a stable reward trend."""
        return cls(
            trend_id=trend_id,
            domain=domain,
            direction="stable",
            velocity=velocity,
            acceleration=0.0,
            consistency=min(consistency, 1.0),
            persistence=persistence,
            max_persistence=max(persistence, 1),
            confidence=consistency,
            uncertainty=1.0 - consistency,
        )
    
    @classmethod
    def create_unknown_trend(
        cls,
        trend_id: str,
        domain: str = "reward",
        uncertainty: float = 0.5,
    ) -> RewardTrend:
        """Create an unknown trend (insufficient data)."""
        return cls(
            trend_id=trend_id,
            domain=domain,
            direction="unknown",
            velocity=0.0,
            acceleration=0.0,
            consistency=0.5,
            persistence=0,
            max_persistence=0,
            confidence=1.0 - uncertainty,
            uncertainty=uncertainty,
        )
    
    @property
    def is_increasing(self) -> bool:
        """Check if trend direction indicates increasing reward."""
        return self.direction == "increasing"
    
    @property
    def is_decreasing(self) -> bool:
        """Check if trend direction indicates decreasing reward."""
        return self.direction == "decreasing"
    
    @property
    def is_stable(self) -> bool:
        """Check if trend direction indicates stable reward."""
        return self.direction == "stable"
    
    @property
    def has_significant_velocity(self) -> bool:
        """Check if velocity exceeds noise threshold."""
        return abs(self.velocity) > 0.05
    
    @property
    def is_accelerating(self) -> bool:
        """Check if trend velocity is increasing over time."""
        return self.acceleration > 0.01 and self.is_increasing
    
    @property
    def is_decelerating(self) -> bool:
        """Check if trend velocity is decreasing over time."""
        return self.acceleration < -0.01 and self.is_decreasing


@dataclass(frozen=True)
class TrendCollection:
    """
    Collection of reward trends across multiple domains.
    
    Aggregates individual trends into a semantic summary while preserving
    all individual trend details for downstream analysis.
    """
    
    # Identity and reference (no defaults first)
    collection_id: str
    """Unique identifier for this trend collection."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Trend storage (always preserved)
    trends: Tuple[RewardTrend, ...] = field(default_factory=tuple)
    """Individual reward trends in this collection."""
    
    # Semantic aggregation fields
    dominant_direction: str = "stable"
    """Most common direction across all domains."""
    
    aggregate_velocity: float = 0.0
    """Weighted average velocity across trends."""
    
    aggregate_consistency: float = 1.0
    """Average consistency across trends."""
    
    # Domain coverage
    domains_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic domains covered by this trend collection."""
    
    provenance: Optional[str] = None
    """Provenance reference for this collection."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from trend collection analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Collection analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.collection_id}@v{self.revision}"
    
    @property
    def trend_count(self) -> int:
        """Get count of trends in this collection."""
        return len(self.trends)
    
    @classmethod
    def create_empty(cls, collection_id: str) -> TrendCollection:
        """Create an empty trend collection."""
        return cls(
            collection_id=collection_id,
            trends=tuple(),
            dominant_direction="stable",
            aggregate_velocity=0.0,
            aggregate_consistency=1.0,
        )
    
    @classmethod
    def from_trends(cls, collection_id: str, trends: Tuple[RewardTrend, ...]) -> TrendCollection:
        """
        Create a trend collection from individual trends.
        
        Analyzes the distribution of directions and computes
        aggregate semantic measures.
        """
        if not trends:
            return cls.create_empty(collection_id)
        
        # Count direction frequencies
        direction_counts: dict[str, int] = {}
        for t in trends:
            direction_counts[t.direction] = direction_counts.get(t.direction, 0) + 1
        
        # Find dominant direction (most common)
        dominant_direction = max(direction_counts.items(), key=lambda x: x[1])[0]
        
        # Compute aggregate metrics
        total_velocity = sum(abs(t.velocity) for t in trends)
        aggregate_velocity = (
            sum(t.velocity for t in trends) / len(trends)
        )
        
        total_consistency = sum(t.consistency for t in trends)
        aggregate_consistency = total_consistency / len(trends)
        
        # Collect domains analyzed
        domains = tuple(set(t.domain for t in trends))
        
        return cls(
            collection_id=collection_id,
            trends=trends,
            dominant_direction=dominant_direction,
            aggregate_velocity=aggregate_velocity,
            aggregate_consistency=aggregate_consistency,
            domains_analyzed=domains,
        )


@dataclass(frozen=True)
class TrendAnalyzer:
    """
    Deterministic trend analysis engine.
    
    Analyzes sequences of reward values to extract semantic trend information
    without statistical modeling or prediction.
    
    ANALYSIS METHOD:
        1. Compute first differences between consecutive values
        2. Determine direction from aggregate sign of differences
        3. Calculate velocity as mean difference per time unit
        4. Measure consistency as stability of direction
        5. Detect acceleration from change in differences
        
    NOT RESPONSIBLE FOR:
        • Learning or adapting analysis methods
        • Predicting future values
        • Modifying input data
    """
    
    # Analysis parameters (deterministic configuration)
    velocity_threshold: float = 0.05
    """Minimum absolute difference for 'significant' change."""
    
    consistency_window: int = 3
    """Window size for consistency measurement."""
    
    @classmethod
    def analyze_trend(
        cls,
        values: Tuple[float, ...],
        domain: str = "reward",
        trend_id: str = "default-trend",
    ) -> RewardTrend:
        """
        Analyze a sequence of reward values and extract trend information.
        
        Args:
            values: Sequence of reward values over time
            domain: Semantic domain being analyzed
            trend_id: Identifier for the resulting trend
            
        Returns:
            RewardTrend with semantic analysis results
        """
        if not values or len(values) < 2:
            return RewardTrend.create_unknown_trend(
                trend_id=trend_id,
                domain=domain,
                uncertainty=0.5,
            )
        
        # Compute first differences
        differences: Tuple[float, ...] = tuple(
            values[i + 1] - values[i] for i in range(len(values) - 1)
        )
        
        if not differences:
            return RewardTrend.create_unknown_trend(
                trend_id=trend_id,
                domain=domain,
                uncertainty=0.5,
            )
        
        # Determine direction from aggregate of differences
        positive_diffs = sum(1 for d in differences if d > cls.velocity_threshold)
        negative_diffs = sum(1 for d in differences if d < -cls.velocity_threshold)
        neutral_diffs = len(differences) - positive_diffs - negative_diffs
        
        # Direction determination logic
        if positive_diffs > negative_diffs and positive_diffs >= len(differences) * 0.5:
            direction = "increasing"
        elif negative_diffs > positive_diffs and negative_diffs >= len(differences) * 0.5:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # Calculate velocity as mean difference
        velocity = sum(differences) / len(differences)
        
        # Calculate acceleration (change in differences)
        if len(differences) >= 2:
            diff_differences = tuple(
                differences[i + 1] - differences[i] for i in range(len(differences) - 1)
            )
            acceleration = sum(diff_differences) / len(diff_differences) / len(differences)
        else:
            acceleration = 0.0
        
        # Calculate consistency as stability of direction
        if positive_diffs + negative_diffs > 0:
            consistent_count = max(positive_diffs, negative_diffs)
            consistency = consistent_count / (positive_diffs + negative_diffs)
        else:
            consistency = 1.0  # all neutral, fully consistent in being stable
        
        # Calculate persistence
        persistence = cls._calculate_persistence(differences)
        
        return RewardTrend(
            trend_id=trend_id,
            domain=domain,
            direction=direction,
            velocity=velocity,
            acceleration=acceleration,
            consistency=min(consistency, 1.0),
            persistence=persistence,
            max_persistence=max(persistence, 1),
            confidence=min(consistency, 1.0),
            uncertainty=1.0 - min(consistency, 1.0),
            observation_window=len(values),
            data_points=values,
        )
    
    @classmethod
    def _calculate_persistence(cls, differences: Tuple[float, ...]) -> int:
        """
        Calculate persistence of directional consistency.
        
        Returns the length of the longest consecutive sequence of
        consistent direction (all positive or all negative).
        """
        if not differences:
            return 0
        
        max_persistence = 1
        current_persistence = 1
        last_direction: Optional[bool] = None  # True=positive, False=negative, None=neutral
        
        for diff in differences:
            is_positive = diff > cls.velocity_threshold
            is_negative = diff < -cls.velocity_threshold
            
            if is_positive or is_negative:
                current_direction = is_positive
                
                if last_direction is not None and current_direction == last_direction:
                    current_persistence += 1
                else:
                    max_persistence = max(max_persistence, current_persistence)
                    current_persistence = 1
                
                last_direction = current_direction
            else:
                # Neutral breaks persistence
                max_persistence = max(max_persistence, current_persistence)
                current_persistence = 1
                last_direction = None
        
        return max(max_persistence, current_persistence)