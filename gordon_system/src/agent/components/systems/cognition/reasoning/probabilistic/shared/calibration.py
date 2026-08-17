# Confidence Calibration - Phase 7.7
# ===================================

"""
Canonical confidence calibration contracts.

Calibration evaluates prediction accuracy and adjusts confidence estimates.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class CalibrationMetrics:
    """
    Metrics for evaluating calibration quality.
    
    Measures how well reported confidence matches actual accuracy.
    """
    
    # Accuracy metrics
    accuracy: float = 0.5                   # Overall prediction accuracy
    
    # Confidence metrics  
    average_confidence: float = 0.5         # Average reported confidence
    confidence_std: float = 0.1             # Standard deviation of confidence
    
    # Calibration error metrics
    expected_calibration_error: float = 0.1  # ECE measure
    max_calibration_error: float = 0.2       # Maximum calibration gap
    
    # Binning statistics (for ECE)
    num_bins: int = 10                      # Number of confidence bins
    bin_accuracies: Dict[float, float] = field(default_factory=dict)  # bin_center → accuracy
    bin_counts: Dict[float, int] = field(default_factory=dict)        # bin_center → count
    
    @property
    def is_well_calibrated(self) -> bool:
        """Check if calibration error is within acceptable bounds."""
        return self.expected_calibration_error <= 0.1


@dataclass(frozen=True)
class CalibrationAdjustment:
    """
    Adjustment to apply for better calibration.
    
    Represents how confidence should be transformed.
    """
    
    # Identity
    adjustment_id: str                      # Unique identifier
    
    # Adjustment type
    adjustment_type: str = "spline"         # "spline", "affine", "isotonic"
    
    # Parameters
    original_confidence: float = 0.5        # What was the original?
    adjusted_confidence: float = 0.5        # What should it be?
    
    # Evidence
    num_samples_used: int = 1               # How much data informed this?
    
    @classmethod
    def identity(cls) -> CalibrationAdjustment:
        """Create an adjustment that makes no change."""
        return cls(
            adjustment_id=f"adjustment:{uuid.uuid4().hex[:16]}",
            original_confidence=0.5,
            adjusted_confidence=0.5,
            num_samples_used=0,
        )


@dataclass(frozen=True)
class ConfidenceCalibration:
    """
    Calibration result for a set of predictions.
    
    Shows how confidence estimates compare to actual outcomes.
    """
    
    # Identity
    calibration_id: str                     # Unique identifier
    
    # Evaluated predictions
    evaluated_predictions: Tuple[str, ...] = ()  # Prediction IDs evaluated
    
    # Metrics
    metrics: CalibrationMetrics = field(default_factory=CalibrationMetrics)
    
    # Adjustments to apply
    adjustments: Tuple[CalibrationAdjustment, ...] = ()
    
    # Metadata
    calibrated_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_well_calibrated(self) -> bool:
        """Check if calibration meets quality thresholds."""
        return self.metrics.is_well_calibrated and len(self.adjustments) <= 1
    
    @classmethod
    def create_empty(cls) -> ConfidenceCalibration:
        """Create a calibration result with no data."""
        return cls(
            calibration_id=f"calibration:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConfidenceCalibration", 
    "CalibrationMetrics",
    "CalibrationAdjustment",
]