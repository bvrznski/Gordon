# Reward Network - Stability Analysis Module (Phase 4.10.4)
# ===========================================================

"""
Stability analysis module for temporal reward evaluation.

Reward Stability measures how resistant a reward estimate is to change over time,
distinguishing between truly stable rewards and those that merely appear stable
due to short observation periods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardStability:
    """
    Semantic measure of reward estimate resistance to change.
    
    Stability represents how consistently a reward maintains its value over time,
    independent from confidence or uncertainty measures. A stable reward is one
    that shows little variation across repeated evaluation cycles.
    
    CRITICAL DISTINCTIONS:
        • Stability ≠ Confidence: A low-confidence estimate can be very stable
        • Stability ≠ Uncertainty: High uncertainty does not imply instability
        
    STABILITY TYPES:
        • high: Minimal variation over observation period
        • moderate: Some variation but consistent pattern
        • low: Significant variation indicating inherent volatility
        • unknown: Insufficient data for assessment
    
    PROPERTIES:
        • stability_id: Unique identifier for this stability measure
        • domain: Semantic domain being analyzed  
        • value: Numerical stability score (0.0 to 1.0)
        • resilience: Recovery speed after perturbation
        • persistence: Duration of stable state
        • variance: Observed variability in values
        
    NOT RESPONSIBLE FOR:
        • Predicting future stability
        • Modifying reward estimates based on stability
        • Learning from stability patterns
    """
    
    # Identity and reference (no defaults first)
    stability_id: str
    """Unique identifier for this stability measure."""
    
    domain: str  # BaselineDomain.*
    """Semantic domain being analyzed."""
    
    value: float = 1.0
    """Stability score (0.0=unstable, 1.0=fully stable)."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Stability components (always preserved)
    resilience: float = 1.0
    """Recovery speed after deviation from equilibrium."""
    
    persistence: int = 0
    """Duration of current stable state in time units."""
    
    max_persistence: int = 0
    """Maximum observed persistence in history."""
    
    # Variance measures
    variance: float = 0.0
    """Observed variance in reward values."""
    
    standard_deviation: float = 0.0
    """Standard deviation of observations."""
    
    coefficient_of_variation: float = 0.0
    """Normalized variability measure (std/mean)."""
    
    # Semantic evaluation fields
    classification: str = "unknown"  # high/moderate/low/unknown
    """Semantic classification of stability level."""
    
    confidence: float = 1.0
    """Confidence in the stability assessment."""
    
    uncertainty: float = 0.0
    """Uncertainty about the stability assessment."""
    
    # Context and provenance
    observation_window: int = 1
    """Number of time units analyzed."""
    
    data_points: Tuple[float, ...] = field(default_factory=tuple)
    """Raw observations used for analysis."""
    
    provenance: Optional[str] = None
    """Provenance reference for this stability analysis."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from stability analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.stability_id}@v{self.revision}"
    
    # Factory methods for stability classifications
    @classmethod
    def create_high_stability(
        cls,
        stability_id: str,
        domain: str = "reward",
        variance: float = 0.01,
        resilience: float = 0.95,
        persistence: int = 10,
    ) -> RewardStability:
        """Create a high-stability measure."""
        return cls(
            stability_id=stability_id,
            domain=domain,
            value=1.0 - variance * 2,  # high stability for low variance
            resilience=resilience,
            persistence=persistence,
            max_persistence=max(persistence, 1),
            variance=variance,
            standard_deviation=variance ** 0.5,
            coefficient_of_variation=variance ** 0.5 / max(variance, 0.01) if variance > 0 else 0,
            classification="high",
            confidence=0.9,
            uncertainty=0.1,
        )
    
    @classmethod
    def create_moderate_stability(
        cls,
        stability_id: str,
        domain: str = "reward",
        variance: float = 0.1,
        resilience: float = 0.7,
        persistence: int = 3,
    ) -> RewardStability:
        """Create a moderate-stability measure."""
        return cls(
            stability_id=stability_id,
            domain=domain,
            value=0.6 - variance * 2,  # decreases with higher variance
            resilience=resilience,
            persistence=persistence,
            max_persistence=max(persistence, 1),
            variance=variance,
            standard_deviation=variance ** 0.5,
            coefficient_of_variation=variance ** 0.5 / max(variance, 0.01) if variance > 0 else 0,
            classification="moderate",
            confidence=0.7,
            uncertainty=0.3,
        )
    
    @classmethod
    def create_low_stability(
        cls,
        stability_id: str,
        domain: str = "reward",
        variance: float = 0.5,
        resilience: float = 0.4,
        persistence: int = 1,
    ) -> RewardStability:
        """Create a low-stability measure."""
        return cls(
            stability_id=stability_id,
            domain=domain,
            value=0.2 - variance * 0.5,  # decreases with higher variance
            resilience=resilience,
            persistence=persistence,
            max_persistence=max(persistence, 1),
            variance=variance,
            standard_deviation=variance ** 0.5,
            coefficient_of_variation=variance ** 0.5 / max(variance, 0.01) if variance > 0 else 0,
            classification="low",
            confidence=0.5,
            uncertainty=0.5,
        )
    
    @classmethod
    def create_unknown_stability(
        cls,
        stability_id: str,
        domain: str = "reward",
        uncertainty: float = 0.5,
    ) -> RewardStability:
        """Create an unknown-stability measure (insufficient data)."""
        return cls(
            stability_id=stability_id,
            domain=domain,
            value=0.5,  # neutral
            resilience=0.5,
            persistence=0,
            max_persistence=0,
            variance=1.0,  # high assumed uncertainty
            standard_deviation=1.0,
            coefficient_of_variation=1.0,
            classification="unknown",
            confidence=1.0 - uncertainty,
            uncertainty=uncertainty,
        )
    
    @property
    def is_high(self) -> bool:
        """Check if stability is classified as high."""
        return self.classification == "high"
    
    @property
    def is_moderate(self) -> bool:
        """Check if stability is classified as moderate."""
        return self.classification == "moderate"
    
    @property
    def is_low(self) -> bool:
        """Check if stability is classified as low."""
        return self.classification == "low"
    
    @property
    def is_unknown(self) -> bool:
        """Check if stability classification is unknown."""
        return self.classification == "unknown"
    
    @property
    def has_sufficient_data(self) -> bool:
        """Check if there's enough data for meaningful assessment."""
        return self.observation_window >= 2 and self.confidence > 0.3


@dataclass(frozen=True)
class StabilityCollection:
    """
    Collection of stability measures across multiple domains.
    
    Aggregates individual stability assessments into a semantic summary
    while preserving all individual measure details for downstream analysis.
    """
    
    # Identity and reference (no defaults first)
    collection_id: str
    """Unique identifier for this stability collection."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Stability storage (always preserved)
    stabilities: Tuple[RewardStability, ...] = field(default_factory=tuple)
    """Individual stability measures in this collection."""
    
    # Semantic aggregation fields
    dominant_classification: str = "unknown"
    """Most common classification across domains."""
    
    aggregate_stability: float = 1.0
    """Weighted average stability across all measures."""
    
    aggregate_resilience: float = 1.0
    """Average resilience across stabilities."""
    
    # Domain coverage
    domains_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic domains covered by this collection."""
    
    provenance: Optional[str] = None
    """Provenance reference for this collection."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from stability collection analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Collection analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.collection_id}@v{self.revision}"
    
    @property
    def stability_count(self) -> int:
        """Get count of stability measures in this collection."""
        return len(self.stabilities)
    
    @classmethod
    def create_empty(cls, collection_id: str) -> StabilityCollection:
        """Create an empty stability collection."""
        return cls(
            collection_id=collection_id,
            stabilities=tuple(),
            dominant_classification="unknown",
            aggregate_stability=1.0,
            aggregate_resilience=1.0,
        )
    
    @classmethod
    def from_stabilities(cls, collection_id: str, stabilities: Tuple[RewardStability, ...]) -> StabilityCollection:
        """
        Create a stability collection from individual measures.
        
        Analyzes the distribution of classifications and computes
        aggregate semantic measures.
        """
        if not stabilities:
            return cls.create_empty(collection_id)
        
        # Count classification frequencies
        classification_counts: dict[str, int] = {}
        for s in stabilities:
            classification_counts[s.classification] = classification_counts.get(s.classification, 0) + 1
        
        # Find dominant classification (most common)
        dominant_classification = max(classification_counts.items(), key=lambda x: x[1])[0]
        
        # Compute aggregate metrics
        total_stability = sum(s.value for s in stabilities)
        aggregate_stability = total_stability / len(stabilities)
        
        total_resilience = sum(s.resilience for s in stabilities)
        aggregate_resilience = total_resilience / len(stabilities)
        
        # Collect domains analyzed
        domains = tuple(set(s.domain for s in stabilities))
        
        return cls(
            collection_id=collection_id,
            stabilities=stabilities,
            dominant_classification=dominant_classification,
            aggregate_stability=aggregate_stability,
            aggregate_resilience=aggregate_resilience,
            domains_analyzed=domains,
        )


@dataclass(frozen=True)
class StabilityAnalyzer:
    """
    Deterministic stability analysis engine.
    
    Analyzes sequences of reward values to extract semantic stability information
    without statistical modeling or prediction.
    """
    
    # Analysis parameters (deterministic configuration)
    high_stability_threshold: float = 0.1
    """Variance below which stability is classified as 'high'."""
    
    moderate_stability_threshold: float = 0.4
    """Variance above which stability drops to 'moderate' or 'low'."""
    
    @classmethod
    def analyze_stability(
        cls,
        values: Tuple[float, ...],
        domain: str = "reward",
        stability_id: str = "default-stability",
    ) -> RewardStability:
        """
        Analyze a sequence of reward values and extract stability information.
        
        Args:
            values: Sequence of reward values over time
            domain: Semantic domain being analyzed
            stability_id: Identifier for the resulting stability measure
            
        Returns:
            RewardStability with semantic analysis results
        """
        if len(values) < 2:
            return RewardStability.create_unknown_stability(
                stability_id=stability_id,
                domain=domain,
                uncertainty=0.5,
            )
        
        # Compute mean and variance
        mean_value = sum(values) / len(values)
        variance = sum((v - mean_value) ** 2 for v in values) / (len(values) - 1) if len(values) > 1 else 0
        
        standard_deviation = variance ** 0.5
        coefficient_of_variation = standard_deviation / abs(mean_value) if mean_value != 0 else 0
        
        # Determine classification based on variance
        if variance <= cls.high_stability_threshold:
            classification = "high"
            value = 1.0 - variance * 2
        elif variance <= cls.moderate_stability_threshold:
            classification = "moderate"
            value = 0.6 - variance
        else:
            classification = "low"
            value = max(0.1, 0.2 - variance * 0.5)
        
        # Compute resilience (inversely related to variance)
        resilience = max(0.0, min(1.0, 1.0 - variance))
        
        # Estimate persistence based on consecutive similarity
        persistence = cls._estimate_persistence(values, mean_value, standard_deviation)
        
        return RewardStability(
            stability_id=stability_id,
            domain=domain,
            value=min(max(value, 0.0), 1.0),
            resilience=resilience,
            persistence=persistence,
            max_persistence=max(persistence, 1),
            variance=variance,
            standard_deviation=standard_deviation,
            coefficient_of_variation=coefficient_of_variation,
            classification=classification,
            confidence=min(0.95, 1.0 - variance * 2),
            uncertainty=variance * 2,
            observation_window=len(values),
            data_points=values,
        )
    
    @classmethod
    def _estimate_persistence(cls, values: Tuple[float, ...], mean_value: float, std_dev: float) -> int:
        """
        Estimate the persistence of stable state.
        
        Counts consecutive values within one standard deviation of the mean.
        """
        if not values or len(values) < 2:
            return 1
        
        threshold = std_dev
        current_persistence = 1
        max_persistence = 1
        
        for i in range(1, len(values)):
            if abs(values[i] - mean_value) <= threshold:
                current_persistence += 1
                max_persistence = max(max_persistence, current_persistence)
            else:
                current_persistence = 1
        
        return max_persistence