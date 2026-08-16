# Reward Network - Drift Analysis Module (Phase 4.10.4)
# =======================================================

"""
Drift analysis module for temporal reward evaluation.

Reward Drift represents slow changes in long-term reward valuations, capturing
gradual shifts due to environmental evolution, goal evolution, competence growth,
or context changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardDrift:
    """
    Semantic representation of gradual reward valuation changes over time.
    
    Drift captures slow, persistent changes in how rewards are valued,
    distinct from short-term volatility or transient fluctuations. It reflects
    long-term adaptation to changing circumstances.
    
    DRIFT CAUSES:
        • Environmental evolution: Changing world conditions
        • Goal evolution: Shifting strategic objectives  
        • Competence growth: Improving capabilities
        • Context changes: Altered situational factors
        
    CRITICAL DISTINCTIONS:
        • Drift ≠ Volatility: Gradual change vs. short-term fluctuations
        • Drift ≠ Trend: Persistent shift vs. directional movement
        • Drift ≠ Learning: Descriptive observation vs. adaptive mechanism
        
    DRIFT TYPES:
        • positive: Gradual increase in reward valuation
        • negative: Gradual decrease in reward valuation
        • neutral: No significant long-term change
        • oscillating: Periodic shifts without net change
        • unknown: Insufficient data for assessment
    
    PROPERTIES:
        • drift_id: Unique identifier for this drift measure
        • domain: Semantic domain being analyzed
        • direction: Semantic direction of drift (positive/negative/neutral)
        • magnitude: Strength of the drift effect
        • rate: Speed of drift per time unit
        • persistence: Duration of drift observation
        
    NOT RESPONSIBLE FOR:
        • Predicting future drift patterns
        • Modifying reward estimates based on drift
        • Learning or adapting from drift patterns
    """
    
    # Identity and reference (no defaults first)
    drift_id: str
    """Unique identifier for this drift measure."""
    
    domain: str  # BaselineDomain.*
    """Semantic domain being analyzed."""
    
    direction: str = "neutral"  # positive/negative/neutral/oscillating/unknown
    """Semantic direction of the drift."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Drift components (always preserved)
    magnitude: float = 0.0
    """Overall strength of the drift effect."""
    
    rate: float = 0.0
    """Rate of change per observation unit."""
    
    persistence: int = 0
    """Number of consecutive units showing consistent drift direction."""
    
    max_persistence: int = 0
    """Maximum observed persistence in history."""
    
    # Statistical measures
    cumulative_change: float = 0.0
    """Total accumulated change over observation period."""
    
    variance_of_change: float = 0.0
    """Variance of the rate of change."""
    
    # Semantic evaluation fields
    classification: str = "unknown"  # positive/negative/neutral/oscillating/unknown
    """Semantic classification of drift type."""
    
    confidence: float = 1.0
    """Confidence in the drift assessment."""
    
    uncertainty: float = 0.0
    """Uncertainty about the drift assessment."""
    
    # Context and provenance
    observation_window: int = 1
    """Number of time units analyzed."""
    
    data_points: Tuple[float, ...] = field(default_factory=tuple)
    """Raw observations used for analysis."""
    
    provenance: Optional[str] = None
    """Provenance reference for this drift analysis."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from drift analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.drift_id}@v{self.revision}"
    
    # Factory methods for drift classifications
    @classmethod
    def create_positive_drift(
        cls,
        drift_id: str,
        domain: str = "reward",
        magnitude: float = 0.2,
        rate: float = 0.05,
        persistence: int = 5,
    ) -> RewardDrift:
        """Create a positive drift measure."""
        return cls(
            drift_id=drift_id,
            domain=domain,
            direction="positive",
            magnitude=magnitude,
            rate=max(0, rate),
            persistence=persistence,
            max_persistence=max(persistence, 1),
            cumulative_change=magnitude * persistence,
            variance_of_change=rate ** 2,
            classification="positive",
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def create_negative_drift(
        cls,
        drift_id: str,
        domain: str = "reward",
        magnitude: float = 0.2,
        rate: float = -0.05,
        persistence: int = 5,
    ) -> RewardDrift:
        """Create a negative drift measure."""
        return cls(
            drift_id=drift_id,
            domain=domain,
            direction="negative",
            magnitude=magnitude,
            rate=min(0, rate),
            persistence=persistence,
            max_persistence=max(persistence, 1),
            cumulative_change=magnitude * persistence,
            variance_of_change=abs(rate) ** 2,
            classification="negative",
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def create_neutral_drift(
        cls,
        drift_id: str,
        domain: str = "reward",
        magnitude: float = 0.0,
        rate: float = 0.0,
        persistence: int = 10,
    ) -> RewardDrift:
        """Create a neutral drift measure."""
        return cls(
            drift_id=drift_id,
            domain=domain,
            direction="neutral",
            magnitude=magnitude,
            rate=rate,
            persistence=persistence,
            max_persistence=max(persistence, 1),
            cumulative_change=0.0,
            variance_of_change=0.0,
            classification="neutral",
            confidence=0.95,
            uncertainty=0.05,
        )
    
    @classmethod
    def create_oscillating_drift(
        cls,
        drift_id: str,
        domain: str = "reward",
        magnitude: float = 0.3,
        rate: float = 0.1,
        persistence: int = 2,
    ) -> RewardDrift:
        """Create an oscillating drift measure."""
        return cls(
            drift_id=drift_id,
            domain=domain,
            direction="neutral",  # oscillation averages to neutral
            magnitude=magnitude,
            rate=rate,
            persistence=persistence,
            max_persistence=max(persistence, 1),
            cumulative_change=0.0,
            variance_of_change=magnitude ** 2,
            classification="oscillating",
            confidence=0.7,
            uncertainty=0.3,
        )
    
    @classmethod
    def create_unknown_drift(
        cls,
        drift_id: str,
        domain: str = "reward",
        uncertainty: float = 0.5,
    ) -> RewardDrift:
        """Create an unknown drift measure (insufficient data)."""
        return cls(
            drift_id=drift_id,
            domain=domain,
            direction="unknown",
            magnitude=0.5,  # neutral
            rate=0.0,
            persistence=0,
            max_persistence=0,
            cumulative_change=0.0,
            variance_of_change=1.0,
            classification="unknown",
            confidence=1.0 - uncertainty,
            uncertainty=uncertainty,
        )
    
    @property
    def is_positive(self) -> bool:
        """Check if drift direction is positive."""
        return self.direction == "positive"
    
    @property
    def is_negative(self) -> bool:
        """Check if drift direction is negative."""
        return self.direction == "negative"
    
    @property
    def is_neutral(self) -> bool:
        """Check if drift direction is neutral."""
        return self.direction == "neutral"
    
    @property
    def is_oscillating(self) -> bool:
        """Check if drift direction is oscillating."""
        return self.direction == "oscillating"
    
    @property
    def has_significant_drift(self) -> bool:
        """Check if drift magnitude exceeds noise threshold."""
        return abs(self.magnitude) > 0.1
    
    @property
    def has_sufficient_data(self) -> bool:
        """Check if there's enough data for meaningful assessment."""
        return self.observation_window >= 3 and self.confidence > 0.3


@dataclass(frozen=True)
class DriftCollection:
    """
    Collection of drift measures across multiple domains.
    
    Aggregates individual drift assessments into a semantic summary
    while preserving all individual measure details for downstream analysis.
    """
    
    # Identity and reference (no defaults first)
    collection_id: str
    """Unique identifier for this drift collection."""
    
    revision: int = 0
    """Revision number for versioning."""

    
    # Drift storage (always preserved)
    drifts: Tuple[RewardDrift, ...] = field(default_factory=tuple)
    """Individual drift measures in this collection."""
    
    # Semantic aggregation fields
    dominant_direction: str = "neutral"
    """Most common direction across domains."""
    
    aggregate_magnitude: float = 0.0
    """Weighted average magnitude across all drifts."""
    
    aggregate_rate: float = 0.0
    """Average rate of change across drifts."""
    
    # Domain coverage
    domains_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic domains covered by this collection."""
    
    provenance: Optional[str] = None
    """Provenance reference for this collection."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from drift collection analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Collection analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.collection_id}@v{self.revision}"
    
    @property
    def drift_count(self) -> int:
        """Get count of drift measures in this collection."""
        return len(self.drifts)
    
    @classmethod
    def create_empty(cls, collection_id: str) -> DriftCollection:
        """Create an empty drift collection."""
        return cls(
            collection_id=collection_id,
            drifts=tuple(),
            dominant_direction="neutral",
            aggregate_magnitude=0.0,
            aggregate_rate=0.0,
        )
    
    @classmethod
    def from_drifts(cls, collection_id: str, drifts: Tuple[RewardDrift, ...]) -> DriftCollection:
        """
        Create a drift collection from individual measures.
        
        Analyzes the distribution of directions and computes
        aggregate semantic measures.
        """
        if not drifts:
            return cls.create_empty(collection_id)
        
        # Count direction frequencies
        direction_counts: dict[str, int] = {}
        for d in drifts:
            direction_counts[d.direction] = direction_counts.get(d.direction, 0) + 1
        
        # Find dominant direction (most common)
        dominant_direction = max(direction_counts.items(), key=lambda x: x[1])[0]
        
        # Compute aggregate metrics
        total_magnitude = sum(abs(d.magnitude) for d in drifts)
        aggregate_magnitude = sum(d.magnitude for d in drifts) / len(drifts)
        
        aggregate_rate = sum(d.rate for d in drifts) / len(drifts)
        
        # Collect domains analyzed
        domains = tuple(set(d.domain for d in drifts))
        
        return cls(
            collection_id=collection_id,
            drifts=drifts,
            dominant_direction=dominant_direction,
            aggregate_magnitude=aggregate_magnitude,
            aggregate_rate=aggregate_rate,
            domains_analyzed=domains,
        )


@dataclass(frozen=True)
class DriftAnalyzer:
    """
    Deterministic drift analysis engine.
    
    Analyzes sequences of reward values to extract semantic drift information
    without statistical modeling or prediction.
    """
    
    # Analysis parameters (deterministic configuration)
    drift_threshold: float = 0.1
    """Minimum cumulative change for 'significant' drift."""
    
    @classmethod
    def analyze_drift(
        cls,
        values: Tuple[float, ...],
        domain: str = "reward",
        drift_id: str = "default-drift",
    ) -> RewardDrift:
        """
        Analyze a sequence of reward values and extract drift information.
        
        Args:
            values: Sequence of reward values over time
            domain: Semantic domain being analyzed
            drift_id: Identifier for the resulting drift measure
            
        Returns:
            RewardDrift with semantic analysis results
        """
        if len(values) < 3:
            return RewardDrift.create_unknown_drift(
                drift_id=drift_id,
                domain=domain,
                uncertainty=0.5,
            )
        
        # Compute first differences to detect changes
        differences = tuple(
            values[i + 1] - values[i] for i in range(len(values) - 1)
        )
        
        if not differences:
            return RewardDrift.create_unknown_drift(
                drift_id=drift_id,
                domain=domain,
                uncertainty=0.5,
            )
        
        # Calculate cumulative change
        cumulative_change = values[-1] - values[0]
        
        # Determine direction of overall trend
        if cumulative_change > cls.drift_threshold:
            direction = "positive"
            classification = "positive"
        elif cumulative_change < -cls.drift_threshold:
            direction = "negative"
            classification = "negative"
        else:
            direction = "neutral"
            
            # Check for oscillation (alternating positive/negative differences)
            alternating_count = sum(
                1 for i in range(len(differences) - 1)
                if (differences[i] > 0 and differences[i + 1] < 0) or
                   (differences[i] < 0 and differences[i + 1] > 0)
            )
            
            if alternating_count >= len(differences) * 0.5:
                classification = "oscillating"
            else:
                classification = "neutral"
        
        # Calculate rate of change per observation
        rate = cumulative_change / (len(values) - 1) if len(values) > 1 else 0
        
        # Calculate magnitude as absolute cumulative change normalized
        magnitude = abs(cumulative_change)
        
        # Count persistence of consistent direction
        persistence = cls._calculate_drift_persistence(differences, values[0])
        
        # Compute variance of the rate
        if len(differences) >= 2:
            diff_mean = sum(differences) / len(differences)
            variance_of_change = sum(
                (d - diff_mean) ** 2 for d in differences
            ) / (len(differences) - 1)
        else:
            variance_of_change = 0.0
        
        # Determine confidence based on consistency
        if classification == "neutral":
            confidence = min(0.95, 1.0 - magnitude)
        else:
            consistent_count = sum(
                1 for d in differences 
                if (d > 0 and cumulative_change > 0) or 
                   (d < 0 and cumulative_change < 0)
            )
            confidence = min(0.95, consistent_count / len(differences)) if differences else 0.5
        
        return RewardDrift(
            drift_id=drift_id,
            domain=domain,
            direction=direction,
            magnitude=magnitude,
            rate=rate,
            persistence=persistence,
            max_persistence=max(persistence, 1),
            cumulative_change=cumulative_change,
            variance_of_change=variance_of_change,
            classification=classification,
            confidence=min(confidence, 1.0),
            uncertainty=1.0 - min(confidence, 1.0),
            observation_window=len(values),
            data_points=values,
        )
    
    @classmethod
    def _calculate_drift_persistence(cls, differences: Tuple[float, ...], initial_value: float) -> int:
        """
        Calculate persistence of drift direction.
        
        Counts consecutive differences in the same direction as overall trend.
        """
        if not differences or len(differences) < 2:
            return 1
        
        # Determine overall direction
        total_change = sum(differences)
        
        if total_change > 0:
            target_direction = 1  # positive
        elif total_change < 0:
            target_direction = -1  # negative
        else:
            return 1  # neutral, no persistence to measure
        
        current_persistence = 1
        max_persistence = 1
        
        for diff in differences:
            if (diff > 0 and target_direction == 1) or (diff < 0 and target_direction == -1):
                current_persistence += 1
                max_persistence = max(max_persistence, current_persistence)
            else:
                current_persistence = 1
        
        return max_persistence