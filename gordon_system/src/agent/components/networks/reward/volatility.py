# Reward Network - Volatility Analysis Module (Phase 4.10.4)
# ===========================================================

"""
Volatility analysis module for temporal reward evaluation.

Reward Volatility measures short-term variability in reward estimates,
distinguishing between inherent instability and normal observation noise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardVolatility:
    """
    Semantic measure of short-term reward variability.
    
    Volatility represents the degree of short-term fluctuation in reward estimates,
    independent from stability (which considers longer-term patterns) and uncertainty
    (which considers knowledge state).
    
    CRITICAL DISTINCTIONS:
        • Volatility ≠ Uncertainty: A well-known estimate can be volatile
        • Volatility ≠ Instability: Short-term spikes may not indicate long-term instability
        
    VOLATILITY TYPES:
        • high: Significant short-term fluctuations detected
        • moderate: Some variation but within expected bounds
        • low: Minimal short-term variation observed
        • unknown: Insufficient data for assessment
    
    PROPERTIES:
        • volatility_id: Unique identifier for this volatility measure
        • domain: Semantic domain being analyzed
        • value: Numerical volatility score (0.0 to 1.0)
        • amplitude: Maximum deviation in observation period
        • frequency: Rate of fluctuation events
        • transience: Duration of volatile periods
        
    NOT RESPONSIBLE FOR:
        • Predicting future volatility
        • Modifying reward estimates based on volatility
        • Learning from volatility patterns
    """
    
    # Identity and reference (no defaults first)
    volatility_id: str
    """Unique identifier for this volatility measure."""
    
    domain: str  # BaselineDomain.*
    """Semantic domain being analyzed."""
    
    value: float = 0.0
    """Volatility score (0.0=stable, 1.0=highly volatile)."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Volatility components (always preserved)
    amplitude: float = 0.0
    """Maximum absolute deviation from mean in observations."""
    
    frequency: float = 0.0
    """Number of fluctuation events per observation unit."""
    
    transience: int = 0
    """Average duration of volatile periods in time units."""
    
    # Statistical measures
    variance: float = 0.0
    """Variance of observations."""
    
    standard_deviation: float = 0.0
    """Standard deviation of observations."""
    
    max_deviation: float = 0.0
    """Maximum absolute deviation from mean."""
    
    min_value: float = 0.0
    """Minimum observation value."""
    
    max_value: float = 0.0
    """Maximum observation value."""
    
    # Semantic evaluation fields
    classification: str = "unknown"  # high/moderate/low/unknown
    """Semantic classification of volatility level."""
    
    confidence: float = 1.0
    """Confidence in the volatility assessment."""
    
    uncertainty: float = 0.0
    """Uncertainty about the volatility assessment."""
    
    # Context and provenance
    observation_window: int = 1
    """Number of time units analyzed."""
    
    data_points: Tuple[float, ...] = field(default_factory=tuple)
    """Raw observations used for analysis."""
    
    provenance: Optional[str] = None
    """Provenance reference for this volatility analysis."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from volatility analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.volatility_id}@v{self.revision}"
    
    # Factory methods for volatility classifications
    @classmethod
    def create_high_volatility(
        cls,
        volatility_id: str,
        domain: str = "reward",
        amplitude: float = 0.5,
        frequency: float = 0.3,
        transience: int = 2,
    ) -> RewardVolatility:
        """Create a high-volatility measure."""
        return cls(
            volatility_id=volatility_id,
            domain=domain,
            value=min(1.0, amplitude * 2),
            amplitude=amplitude,
            frequency=frequency,
            transience=max(transience, 1),
            variance=amplitude ** 2,
            standard_deviation=amplitude,
            max_deviation=amplitude,
            classification="high",
            confidence=0.7,
            uncertainty=0.3,
        )
    
    @classmethod
    def create_moderate_volatility(
        cls,
        volatility_id: str,
        domain: str = "reward",
        amplitude: float = 0.2,
        frequency: float = 0.1,
        transience: int = 5,
    ) -> RewardVolatility:
        """Create a moderate-volatility measure."""
        return cls(
            volatility_id=volatility_id,
            domain=domain,
            value=min(1.0, amplitude * 2),
            amplitude=amplitude,
            frequency=frequency,
            transience=max(transience, 1),
            variance=amplitude ** 2,
            standard_deviation=amplitude,
            max_deviation=amplitude,
            classification="moderate",
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def create_low_volatility(
        cls,
        volatility_id: str,
        domain: str = "reward",
        amplitude: float = 0.05,
        frequency: float = 0.02,
        transience: int = 10,
    ) -> RewardVolatility:
        """Create a low-volatility measure."""
        return cls(
            volatility_id=volatility_id,
            domain=domain,
            value=min(1.0, amplitude * 2),
            amplitude=amplitude,
            frequency=frequency,
            transience=max(transience, 1),
            variance=amplitude ** 2,
            standard_deviation=amplitude,
            max_deviation=amplitude,
            classification="low",
            confidence=0.95,
            uncertainty=0.05,
        )
    
    @classmethod
    def create_unknown_volatility(
        cls,
        volatility_id: str,
        domain: str = "reward",
        uncertainty: float = 0.5,
    ) -> RewardVolatility:
        """Create an unknown-volatility measure (insufficient data)."""
        return cls(
            volatility_id=volatility_id,
            domain=domain,
            value=0.5,  # neutral
            amplitude=1.0,  # assume high uncertainty
            frequency=0.5,
            transience=1,
            variance=1.0,
            standard_deviation=1.0,
            max_deviation=1.0,
            classification="unknown",
            confidence=1.0 - uncertainty,
            uncertainty=uncertainty,
        )
    
    @property
    def is_high(self) -> bool:
        """Check if volatility is classified as high."""
        return self.classification == "high"
    
    @property
    def is_moderate(self) -> bool:
        """Check if volatility is classified as moderate."""
        return self.classification == "moderate"
    
    @property
    def is_low(self) -> bool:
        """Check if volatility is classified as low."""
        return self.classification == "low"
    
    @property
    def is_unknown(self) -> bool:
        """Check if volatility classification is unknown."""
        return self.classification == "unknown"
    
    @property
    def has_sufficient_data(self) -> bool:
        """Check if there's enough data for meaningful assessment."""
        return self.observation_window >= 2 and self.confidence > 0.3


@dataclass(frozen=True)
class VolatilityCollection:
    """
    Collection of volatility measures across multiple domains.
    
    Aggregates individual volatility assessments into a semantic summary
    while preserving all individual measure details for downstream analysis.
    """
    
    # Identity and reference (no defaults first)
    collection_id: str
    """Unique identifier for this volatility collection."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Volatility storage (always preserved)
    volatilities: Tuple[RewardVolatility, ...] = field(default_factory=tuple)
    """Individual volatility measures in this collection."""
    
    # Semantic aggregation fields
    dominant_classification: str = "unknown"
    """Most common classification across domains."""
    
    aggregate_volatility: float = 0.0
    """Weighted average volatility across all measures."""
    
    aggregate_amplitude: float = 0.0
    """Average amplitude across volatilities."""
    
    # Domain coverage
    domains_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic domains covered by this collection."""
    
    provenance: Optional[str] = None
    """Provenance reference for this collection."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from volatility collection analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Collection analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.collection_id}@v{self.revision}"
    
    @property
    def volatility_count(self) -> int:
        """Get count of volatility measures in this collection."""
        return len(self.volatilities)
    
    @classmethod
    def create_empty(cls, collection_id: str) -> VolatilityCollection:
        """Create an empty volatility collection."""
        return cls(
            collection_id=collection_id,
            volatilities=tuple(),
            dominant_classification="unknown",
            aggregate_volatility=0.0,
            aggregate_amplitude=0.0,
        )
    
    @classmethod
    def from_volatilities(cls, collection_id: str, volatilities: Tuple[RewardVolatility, ...]) -> VolatilityCollection:
        """
        Create a volatility collection from individual measures.
        
        Analyzes the distribution of classifications and computes
        aggregate semantic measures.
        """
        if not volatilities:
            return cls.create_empty(collection_id)
        
        # Count classification frequencies
        classification_counts: dict[str, int] = {}
        for v in volatilities:
            classification_counts[v.classification] = classification_counts.get(v.classification, 0) + 1
        
        # Find dominant classification (most common)
        dominant_classification = max(classification_counts.items(), key=lambda x: x[1])[0]
        
        # Compute aggregate metrics
        total_volatility = sum(v.value for v in volatilities)
        aggregate_volatility = total_volatility / len(volatilities)
        
        total_amplitude = sum(v.amplitude for v in volatilities)
        aggregate_amplitude = total_amplitude / len(volatilities)
        
        # Collect domains analyzed
        domains = tuple(set(v.domain for v in volatilities))
        
        return cls(
            collection_id=collection_id,
            volatilities=volatilities,
            dominant_classification=dominant_classification,
            aggregate_volatility=aggregate_volatility,
            aggregate_amplitude=aggregate_amplitude,
            domains_analyzed=domains,
        )


@dataclass(frozen=True)
class VolatilityAnalyzer:
    """
    Deterministic volatility analysis engine.
    
    Analyzes sequences of reward values to extract semantic volatility information
    without statistical modeling or prediction.
    """
    
    # Analysis parameters (deterministic configuration)
    high_volatility_threshold: float = 0.3
    """Amplitude above which volatility is classified as 'high'."""
    
    moderate_volatility_threshold: float = 0.6
    """Amplitude above which volatility drops to 'moderate' or 'low'."""
    
    @classmethod
    def analyze_volatility(
        cls,
        values: Tuple[float, ...],
        domain: str = "reward",
        volatility_id: str = "default-volatility",
    ) -> RewardVolatility:
        """
        Analyze a sequence of reward values and extract volatility information.
        
        Args:
            values: Sequence of reward values over time
            domain: Semantic domain being analyzed
            volatility_id: Identifier for the resulting volatility measure
            
        Returns:
            RewardVolatility with semantic analysis results
        """
        if len(values) < 2:
            return RewardVolatility.create_unknown_volatility(
                volatility_id=volatility_id,
                domain=domain,
                uncertainty=0.5,
            )
        
        # Compute statistics
        mean_value = sum(values) / len(values)
        
        # Find min and max for amplitude calculation
        min_val = min(values)
        max_val = max(values)
        amplitude = abs(max_val - min_val)
        
        # Compute variance
        variance = sum((v - mean_value) ** 2 for v in values) / (len(values) - 1) if len(values) > 1 else 0
        standard_deviation = variance ** 0.5
        
        # Calculate maximum deviation from mean
        max_deviation = max(abs(v - mean_value) for v in values)
        
        # Count fluctuation events (up-down or down-up transitions)
        frequency = cls._count_fluctuations(values, mean_value, standard_deviation)
        
        # Estimate transience (average duration of volatile periods)
        transience = cls._estimate_transience(values, mean_value, standard_deviation)
        
        # Determine classification based on amplitude
        if amplitude >= cls.high_volatility_threshold:
            classification = "high"
            value = min(1.0, amplitude)
        elif amplitude >= cls.moderate_volatility_threshold * cls.high_volatility_threshold:
            classification = "moderate"
            value = min(1.0, amplitude)
        else:
            classification = "low"
            value = min(1.0, amplitude / 2)
        
        return RewardVolatility(
            volatility_id=volatility_id,
            domain=domain,
            value=value,
            amplitude=amplitude,
            frequency=frequency,
            transience=max(transience, 1),
            variance=variance,
            standard_deviation=standard_deviation,
            max_deviation=max_deviation,
            min_value=min_val,
            max_value=max_val,
            classification=classification,
            confidence=min(0.95, 1.0 - amplitude * 2),
            uncertainty=amplitude * 2,
            observation_window=len(values),
            data_points=values,
        )
    
    @classmethod
    def _count_fluctuations(cls, values: Tuple[float, ...], mean_value: float, std_dev: float) -> float:
        """
        Count the number of fluctuation events in the sequence.
        
        A fluctuation is a transition from above to below or vice versa
        relative to the mean by at least one standard deviation.
        """
        if len(values) < 2:
            return 0.0
        
        threshold = std_dev
        fluctuations = 0
        
        for i in range(1, len(values)):
            prev_sign = 1 if values[i - 1] >= mean_value + threshold else (-1 if values[i - 1] <= mean_value - threshold else 0)
            curr_sign = 1 if values[i] >= mean_value + threshold else (-1 if values[i] <= mean_value - threshold else 0)
            
            # Count sign changes (excluding neutral states)
            if prev_sign != 0 and curr_sign != 0 and prev_sign != curr_sign:
                fluctuations += 1
        
        return fluctuations / max(len(values) - 1, 1)
    
    @classmethod
    def _estimate_transience(cls, values: Tuple[float, ...], mean_value: float, std_dev: float) -> int:
        """
        Estimate the average duration of volatile periods.
        
        A volatile period is a sequence of consecutive deviations from the mean
        by more than one standard deviation.
        """
        if len(values) < 2:
            return 1
        
        threshold = std_dev
        current_duration = 0
        total_durations = []
        
        for v in values:
            if abs(v - mean_value) > threshold:
                current_duration += 1
            else:
                if current_duration > 0:
                    total_durations.append(current_duration)
                current_duration = 0
        
        # Don't forget the last period
        if current_duration > 0:
            total_durations.append(current_duration)
        
        return max(sum(total_durations) // len(total_durations), 1) if total_durations else 1