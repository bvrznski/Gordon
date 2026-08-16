# Derived Memory Statistics - Phase 5.1.6 Canonical Implementation
# ================================================================
"""
Statistics: Metrics about derivation execution and health.

Purpose:
    Provide aggregate statistics about derived memory operations.
    
Metrics Categories:
    - Derivation counts (total, by kind)
    - Validation metrics (success, failure rates)
    - Confidence distributions
    - Execution timing
    
Stats Laws:
    STATS-LAW-001: Statistics remain inspectable
    STATS-LAW-002: Statistics preserve provenance
    STATS-LAW-003: Statistics are deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import time


# =============================================================================
# STATISTICS BUCKET - Time-bounded statistics collection
# =============================================================================


@dataclass(frozen=True)
class DerivationStatisticsBucket:
    """
    Statistics for a time bucket (e.g., hour, day).
    
    Fields:
        bucket_id:           Unique ID for this bucket
        start_utc:           Start of bucket (UTC timestamp)
        end_utc:             End of bucket (UTC timestamp)
        
        # Counts
        total_derivations:   Total derivations in this period
        causal_count:        Causal derivations
        counterfactual_count: Counterfactual derivations
        predictive_count:    Predictive derivations
        
        # Validation stats
        validation_passed:   Validated successfully
        validation_failed:   Failed validation
        
        # Timing (ms)
        total_validation_time_ms: Total validation time
        avg_validation_time_ms:   Average validation time
        
    Stats Laws:
        STATS-LAW-003: Statistics are deterministic
    """
    
    bucket_id: str                          # Unique ID for this bucket
    
    start_utc: float                        # Start of period (UTC)
    end_utc: float                          # End of period (UTC)
    
    # Counts
    total_derivations: int = 0
    causal_count: int = 0
    counterfactual_count: int = 0
    predictive_count: int = 0
    
    # Validation stats
    validation_passed: int = 0
    validation_failed: int = 0
    
    # Timing (ms)
    total_validation_time_ms: float = 0.0
    avg_validation_time_ms: float = 0.0


# =============================================================================
# DERIVATION STATISTICS - Aggregate derivation metrics
# =============================================================================


@dataclass(frozen=True)
class DerivationStatistics:
    """
    Aggregate statistics for derived memory operations.
    
    Fields:
        period_start_utc:    Start of the统计 period
        period_end_utc:      End of the统计 period
        
        # Total counts
        total_derivations:   All derivations in period
        causal_count:        Causal derivations only
        counterfactual_count: Counterfactual derivations only
        predictive_count:    Predictive derivations only
        
        # By status
        proposed_count:      Not yet validated
        validating_count:    Being validated
        validated_count:     Successfully validated
        rejected_count:      Failed validation
        published_count:     Published to memory substrate
        
        # Validation stats
        total_validation_passed: All validations that passed
        total_validation_failed: All validations that failed
        validation_rate:     Passed / (passed + failed)
        
        # Confidence distribution
        min_confidence:      Lowest confidence in derivations
        max_confidence:      Highest confidence in derivations
        avg_confidence:      Average confidence across all
        
        # Timing stats (ms)
        total_inference_time_ms: Total inference time
        avg_inference_time_ms:   Average inference time per derivation
        total_validation_time_ms: Total validation time
        avg_validation_time_ms:  Average validation time
        
    Stats Laws:
        STATS-LAW-001: Statistics remain inspectable
        STATS-LAW-002: Statistics preserve provenance
    """
    
    period_start_utc: float                 # Start of period (UTC)
    period_end_utc: float                   # End of period (UTC)
    
    # Total counts
    total_derivations: int = 0
    causal_count: int = 0
    counterfactual_count: int = 0
    predictive_count: int = 0
    
    # By status
    proposed_count: int = 0
    validating_count: int = 0
    validated_count: int = 0
    rejected_count: int = 0
    published_count: int = 0
    
    # Validation stats
    total_validation_passed: int = 0
    total_validation_failed: int = 0
    validation_rate: float = 1.0            # Passed / (passed + failed)
    
    # Confidence distribution
    min_confidence: float = 0.0
    max_confidence: float = 1.0
    avg_confidence: float = 0.5
    
    # Timing stats (ms)
    total_inference_time_ms: float = 0.0
    avg_inference_time_ms: float = 0.0
    total_validation_time_ms: float = 0.0
    avg_validation_time_ms: float = 0.0


# =============================================================================
# STATISTICS BUILDER - Mutable builder for statistics
# =============================================================================


class DerivationStatisticsBuilder:
    """
    Mutable builder for constructing derivation statistics.
    
    Allows incremental aggregation before producing immutable stats.
    """
    
    def __init__(self, period_start_utc: Optional[float] = None):
        """Initialize the builder."""
        self._period_start_utc = period_start_utc or time.time()
        self._period_end_utc = self._period_start_utc
        
        # Counters
        self._total_derivations = 0
        self._causal_count = 0
        self._counterfactual_count = 0
        self._predictive_count = 0
        
        # By status
        self._proposed_count = 0
        self._validating_count = 0
        self._validated_count = 0
        self._rejected_count = 0
        self._published_count = 0
        
        # Validation stats
        self._total_validation_passed = 0
        self._total_validation_failed = 0
        
        # Confidence tracking
        self._confidences: List[float] = []
        
        # Timing (ms)
        self._total_inference_time_ms = 0.0
        self._total_validation_time_ms = 0.0
    
    def record_derivation(
        self,
        kind_: str,                           # causal, counterfactual, predictive
        status: Optional[str] = None,         # proposed, validating, validated, rejected, published
        confidence: float = 0.5,
        inference_time_ms: float = 0.0,
        validation_status: Optional[str] = None,  # passed, failed
        validation_time_ms: float = 0.0,
    ):
        """Record a derivation in the statistics."""
        self._total_derivations += 1
        self._period_end_utc = time.time()
        
        # Count by kind
        if kind_ == "causal":
            self._causal_count += 1
        elif kind_ == "counterfactual":
            self._counterfactual_count += 1
        elif kind_ == "predictive":
            self._predictive_count += 1
        
        # Count by status
        if status == "proposed":
            self._proposed_count += 1
        elif status == "validating":
            self._validating_count += 1
        elif status == "validated":
            self._validated_count += 1
        elif status == "rejected":
            self._rejected_count += 1
        elif status == "published":
            self._published_count += 1
        
        # Track confidence
        if 0.0 <= confidence <= 1.0:
            self._confidences.append(confidence)
        
        # Update timing
        self._total_inference_time_ms += inference_time_ms
        
        # Update validation stats
        if validation_status == "passed":
            self._total_validation_passed += 1
            self._total_validation_time_ms += validation_time_ms
        elif validation_status == "failed":
            self._total_validation_failed += 1
    
    def update_period_end(self, end_utc: float) -> None:
        """Update the period end time."""
        self._period_end_utc = end_utc
    
    def build(self) -> DerivationStatistics:
        """
        Build an immutable DerivationStatistics from this builder.
        
        Returns:
            New DerivationStatistics with all settings applied
        """
        # Calculate confidence stats
        if len(self._confidences) > 0:
            min_conf = min(self._confidences)
            max_conf = max(self._confidences)
            avg_conf = sum(self._confidences) / len(self._confidences)
        else:
            min_conf = 0.5
            max_conf = 0.5
            avg_conf = 0.5
        
        # Calculate validation rate
        total_val = self._total_validation_passed + self._total_validation_failed
        if total_val > 0:
            val_rate = self._total_validation_passed / total_val
        else:
            val_rate = 1.0
        
        # Calculate average times
        avg_inf_time = (
            self._total_inference_time_ms / self._total_derivations
            if self._total_derivations > 0
            else 0.0
        )
        avg_val_time = (
            self._total_validation_time_ms / self._total_validation_passed
            if self._total_validation_passed > 0
            else 0.0
        )
        
        return DerivationStatistics(
            period_start_utc=self._period_start_utc,
            period_end_utc=self._period_end_utc,
            total_derivations=self._total_derivations,
            causal_count=self._causal_count,
            counterfactual_count=self._counterfactual_count,
            predictive_count=self._predictive_count,
            proposed_count=self._proposed_count,
            validating_count=self._validating_count,
            validated_count=self._validated_count,
            rejected_count=self._rejected_count,
            published_count=self._published_count,
            total_validation_passed=self._total_validation_passed,
            total_validation_failed=self._total_validation_failed,
            validation_rate=val_rate,
            min_confidence=min_conf,
            max_confidence=max_conf,
            avg_confidence=avg_conf,
            total_inference_time_ms=self._total_inference_time_ms,
            avg_inference_time_ms=avg_inf_time,
            total_validation_time_ms=self._total_validation_time_ms,
            avg_validation_time_ms=avg_val_time,
        )


# =============================================================================
# DISTRIBUTION STATISTICS - Distribution of metrics
# =============================================================================


@dataclass(frozen=True)
class MetricDistribution:
    """
    Statistics about the distribution of a metric.
    
    Fields:
        metric_name:         Name of the metric
        bucket_count:        Number of buckets in histogram
        min_value:           Minimum value observed
        max_value:           Maximum value observed
        mean_value:          Mean (average) value
        std_deviation:       Standard deviation
        
        # Histogram bins (bucket -> count)
        histogram:           Dict mapping bucket to count
        
    Stats Laws:
        STATS-LAW-001: Statistics remain inspectable
    """
    
    metric_name: str                        # Name of the metric
    
    bucket_count: int = 0                   # Number of histogram buckets
    min_value: float = 0.0                  # Minimum value
    max_value: float = 1.0                  # Maximum value
    mean_value: float = 0.5                 # Mean
    std_deviation: float = 0.0              # Standard deviation
    
    histogram: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Bucket
    "DerivationStatisticsBucket",
    
    # Statistics
    "DerivationStatistics",
    
    # Builder
    "DerivationStatisticsBuilder",
    
    # Distribution
    "MetricDistribution",
]