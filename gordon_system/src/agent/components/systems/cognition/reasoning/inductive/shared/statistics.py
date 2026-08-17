# Induction Statistics - Phase 7.2
# ==================================

"""
Canonical Statistical Support Contract.

Statistics evaluate observations to support generalizations.
"""

from __future__ import annotations

import time
import uuid
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StatisticalSupport:
    """
    Statistical support for a generalization or pattern.
    
    Statistics evaluate:
        - Frequency of observations
        - Coverage (proportion of data represented)
        - Variance and consistency
        - Support diversity
    
    Statistical evidence remains explicit and inspectable.
    """
    
    # Identity
    statistics_identity: str              # Unique identifier for this statistical report
    
    # Supporting observations
    supporting_observations: Tuple[str, ...]  # IDs of observations analyzed
    
    # Statistical measures
    frequency: float = 0.0                # Frequency of target outcome
    coverage: float = 0.0                 # Proportion of data covered (0-1)
    
    variance: float = 0.0                 # Variance in the data
    standard_deviation: float = 0.0       # Standard deviation
    standard_error: float = 0.0           # Standard error of mean
    
    # Sample statistics
    sample_size: int = 0                  # Number of observations
    min_value: Optional[float] = None     # Minimum observed value
    max_value: Optional[float] = None     # Maximum observed value
    mean_value: float = 0.0               # Mean of observed values
    
    # Confidence in statistics
    confidence: float = 0.5               # Confidence in these statistics (0-1)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    statistical_method: str = "default"   # Which method was used?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def effective_sample_size(self) -> float:
        """
        Calculate effective sample size accounting for variance.
        
        Higher variance reduces the effective informativeness of samples.
        """
        if self.sample_size == 0 or self.variance == 0:
            return float(self.sample_size)
        
        # Effective sample size decreases with higher variance
        efficiency = max(0.1, 1.0 - (self.standard_deviation / max(self.mean_value, 0.001)))
        return self.sample_size * efficiency


@dataclass(frozen=True)
class StatisticalDistribution:
    """
    Describes the distribution of values in a sample.
    
    Used for understanding the shape and characteristics of data.
    """
    
    distribution_id: str
    distribution_type: str = "unknown"     # e.g., "normal", "uniform", "bimodal"
    
    # Central tendency
    mean: float = 0.0
    median: float = 0.0
    mode: Optional[float] = None
    
    # Spread
    variance: float = 0.0
    standard_deviation: float = 0.0
    interquartile_range: Tuple[float, float] = (0.0, 1.0)
    
    # Shape
    skewness: float = 0.0                 # Asymmetry
    kurtosis: float = 0.0                 # Tailedness
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    data_points_count: int = 0


@dataclass(frozen=True)
class StatisticalTestResult:
    """
    Result of a statistical test.
    
    Used to determine if observed patterns are statistically significant.
    """
    
    test_id: str
    test_name: str                        # e.g., "chi_square", "t_test"
    
    # Test parameters
    null_hypothesis: str                  # What is being tested against?
    alternative_hypothesis: str           # What is the competing claim?
    
    # Results
    test_statistic: float = 0.0
    p_value: float = 1.0                  # Probability of observing this result if null is true
    significance_level: float = 0.05      # Threshold for rejecting null
    
    # Decision
    rejected_null_hypothesis: bool = False
    statistical_significance: str = "not_significant"  # not_significant, significant, highly_significant
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    test_assumptions: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StatisticalSummary:
    """
    Summary statistics for a dataset.
    
    Provides high-level overview of data characteristics.
    """
    
    summary_id: str
    total_observations: int = 0
    
    # Value distributions
    value_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    frequency_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Correlations
    correlation_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    data_sources: Tuple[str, ...] = field(default_factory=tuple)


def calculate_statistics(values: List[float]) -> StatisticalSupport:
    """
    Calculate basic statistics from a list of values.
    
    This is a utility function for computing common statistical measures.
    """
    if not values:
        return StatisticalSupport(
            statistics_identity=f"stats:{uuid.uuid4().hex[:16]}",
            supporting_observations=(),
            sample_size=0,
        )
    
    n = len(values)
    mean = sum(values) / n
    
    # Calculate variance and standard deviation
    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std_dev = math.sqrt(variance)
        std_error = std_dev / math.sqrt(n)
    else:
        variance = 0.0
        std_dev = 0.0
        std_error = 0.0
    
    return StatisticalSupport(
        statistics_identity=f"stats:{uuid.uuid4().hex[:16]}",
        supporting_observations=(),
        sample_size=n,
        mean_value=mean,
        variance=variance,
        standard_deviation=std_dev,
        standard_error=std_error,
        min_value=min(values),
        max_value=max(values),
    )


__all__ = [
    "StatisticalSupport",
    "StatisticalDistribution",
    "StatisticalTestResult",
    "StatisticalSummary",
    "calculate_statistics",
]