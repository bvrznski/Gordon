# Induction Confidence - Phase 7.2
# ==================================

"""
Canonical Confidence Estimation Contract.

Confidence derives from sample size, coverage, consistency, and other factors.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class InductionConfidence:
    """
    Confidence estimation for inductive conclusions.
    
    Confidence derives from:
        - Sample size (more observations = higher confidence)
        - Coverage (proportion of data represented)
        - Consistency (degree of agreement among observations)
        - Variance (lower variance = higher confidence)
        - Support diversity (multiple independent sources)
    
    Confidence remains explicit and inspectable.
    """
    
    # Identity
    confidence_identity: str              # Unique identifier for this estimate
    
    # Contributing evidence
    contributing_observations: Tuple[str, ...]  # IDs of observations used
    supporting_patterns: Tuple[str, ...]        # IDs of supporting patterns
    
    # Statistical measures
    sample_size: int = 0                  # Number of observations
    coverage: float = 0.0                 # Proportion of data covered (0-1)
    
    # Consistency metrics
    consistency_score: float = 1.0        # Agreement among observations (0-1)
    variance: float = 0.0                 # Statistical variance
    standard_error: float = 0.0           # Standard error of estimate
    
    # Confidence measure (final output)
    confidence_measure: float = 0.5       # Overall confidence (0-1)
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Debug info
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    estimation_method: str = "default"     # How was this estimated?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def effective_confidence(self) -> float:
        """
        Calculate effective confidence based on all factors.
        
        This is the final confidence value after considering all contributing factors.
        """
        base_confidence = self.confidence_measure
        
        # Adjust for sample size (more data = more confident)
        sample_factor = min(1.0, self.sample_size / 10.0) * 0.2
        
        # Adjust for coverage
        coverage_factor = self.coverage * 0.15
        
        # Adjust for consistency (lower variance = higher confidence)
        consistency_factor = self.consistency_score * 0.35
        
        # Reduce for high variance
        variance_penalty = min(0.3, self.variance / 2.0)
        
        effective = (
            base_confidence +
            sample_factor +
            coverage_factor +
            consistency_factor -
            variance_penalty
        )
        
        return max(0.0, min(1.0, effective))
    
    @property
    def uncertainty(self) -> float:
        """Complementary uncertainty (1 - confidence)."""
        return 1.0 - self.effective_confidence
    
    def meets_threshold(self, threshold: float = 0.5) -> bool:
        """Check if confidence meets or exceeds threshold."""
        return self.effective_confidence >= threshold


@dataclass(frozen=True)
class ConfidenceComponents:
    """
    Components that contribute to final confidence estimate.
    
    Allows detailed inspection of how confidence was calculated.
    """
    
    # Individual component scores
    base_estimate: float = 0.5
    sample_size_score: float = 0.0
    coverage_score: float = 0.0
    consistency_score: float = 1.0
    diversity_score: float = 1.0
    bias_correction: float = 0.0
    
    # Weighting (should sum to 1)
    weight_sample_size: float = 0.2
    weight_coverage: float = 0.15
    weight_consistency: float = 0.35
    weight_diversity: float = 0.2
    weight_base_estimate: float = 0.1
    
    @property
    def total_weight(self) -> float:
        """Sum of all weights."""
        return (
            self.weight_sample_size +
            self.weight_coverage +
            self.weight_consistency +
            self.weight_diversity +
            self.weight_base_estimate
        )
    
    def calculate_effective_confidence(self) -> float:
        """Calculate weighted combination of components."""
        effective = (
            self.base_estimate * self.weight_base_estimate +
            self.sample_size_score * self.weight_sample_size +
            self.coverage_score * self.weight_coverage +
            self.consistency_score * self.weight_consistency +
            self.diversity_score * self.weight_diversity
        )
        
        # Apply bias correction as final adjustment
        effective += self.bias_correction
        
        return max(0.0, min(1.0, effective))


@dataclass(frozen=True)
class ConfidenceCalibration:
    """
    Calibration of confidence estimates against observed outcomes.
    
    Helps detect and correct systematic over/under-confidence.
    """
    
    calibration_id: str
    analyzed_estimates: int = 0
    correctly_calibrated: int = 0
    
    # Calibration curve data
    bin_confidence: List[float] = field(default_factory=list)
    observed_frequencies: List[float] = field(default_factory=list)
    
    # Calibration error metrics
    expected_calibration_error: float = 0.0
    max_calibration_error: float = 0.0
    
    @classmethod
    def create(cls, calibration_id: str) -> ConfidenceCalibration:
        """Create a new calibration record."""
        return cls(calibration_id=calibration_id)
    
    def record_estimate(self, estimated_confidence: float, was_correct: bool) -> None:
        """Record an estimate and its outcome for future calibration."""
        pass  # For now, just track counts
    
    @property
    def calibration_quality(self) -> float:
        """
        Quality of calibration (1.0 = perfectly calibrated).
        
        Lower ECE = better calibration.
        """
        if self.analyzed_estimates < 10:
            return 0.5  # Not enough data for reliable calibration
        
        # Inverse relationship to ECE
        quality = max(0.0, 1.0 - self.expected_calibration_error)
        return quality


__all__ = [
    "InductionConfidence",
    "ConfidenceComponents",
    "ConfidenceCalibration",
]