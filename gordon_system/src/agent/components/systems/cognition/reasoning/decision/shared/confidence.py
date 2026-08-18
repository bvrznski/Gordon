# Decision Confidence Calibration - Phase 7.19
# ===========================================

"""
Canonical Decision Confidence Calibration Contract.

Confidence calibration evaluates model agreement, evidence sufficiency,
historical reliability, and uncertainty.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ConfidenceMetrics:
    """
    Confidence metrics for a decision.
    
    Metrics include:
        - Model agreement (how many models agree?)
        - Evidence sufficiency (is evidence adequate?)
        - Historical reliability (past performance)
        - Uncertainty level
        - Expected robustness
    """
    
    # Identity
    confidence_id: str                      # Unique identifier
    
    # Evaluated decision
    evaluated_decision: str                 # Decision ID being evaluated
    
    # Model agreement (0-1, percentage of models that agree)
    model_agreement: float = 0.0
    
    # Evidence metrics
    evidence_sufficiency: float = 0.0       # Is evidence adequate? (0-1)
    evidence_quality: float = 0.0           # Quality of evidence (0-1)
    
    # Historical reliability (0-1, based on past decisions in similar contexts)
    historical_reliability: float = 0.5
    
    # Uncertainty level (0-1, inverse of confidence)
    uncertainty: float = 0.5                # High uncertainty = low confidence
    
    # Expected robustness (how well will this hold up to new evidence?)
    expected_robustness: float = 0.5
    
    @property
    def calibrated_confidence(self) -> float:
        """Calculate overall calibrated confidence."""
        base_confidence = (
            self.model_agreement * 0.3 +
            self.evidence_sufficiency * 0.25 +
            self.evidence_quality * 0.15 +
            (1 - self.uncertainty) * 0.15 +
            self.historical_reliability * 0.15
        )
        return max(0.0, min(1.0, base_confidence))
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if confidence is high (>= 0.8)."""
        return self.calibrated_confidence >= 0.8
    
    @property
    def is_low_confidence(self) -> bool:
        """Check if confidence is low (< 0.5)."""
        return self.calibrated_confidence < 0.5
    
    @classmethod
    def create(
        cls,
        evaluated_decision: str,
        model_agreement: float = 0.0,
        evidence_sufficiency: float = 0.0,
        uncertainty: float = 0.5,
    ) -> ConfidenceMetrics:
        """Create new confidence metrics."""
        return cls(
            confidence_id=f"confidence_metrics:{uuid.uuid4().hex[:16]}",
            evaluated_decision=evaluated_decision,
            model_agreement=model_agreement,
            evidence_sufficiency=evidence_sufficiency,
            uncertainty=uncertainty,
        )


@dataclass(frozen=True)
class ConfidenceCalibration:
    """
    Complete confidence calibration for a decision.
    
    Calibration remains explicit; it never hides uncertainty.
    """
    
    # Identity
    calibration_id: str                     # Unique identifier
    
    # Calibrated decision
    calibrated_decision: str                # Decision ID being calibrated
    
    # Calibration metrics
    calibration_metrics: Tuple[ConfidenceMetrics, ...]
    
    # Uncertainty model (how does uncertainty change with new evidence?)
    uncertainty_model: str = "linear"       # linear, logarithmic, exponential
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def metric_count(self) -> int:
        """Count of calibration metrics."""
        return len(self.calibration_metrics)
    
    def get_metric_for_model(self, model_name: str) -> Optional[ConfidenceMetrics]:
        """Get confidence metric for a specific model."""
        for metric in self.calibration_metrics:
            if metric.confidence_id.endswith(model_name):
                return metric
        return None
    
    @classmethod
    def create(
        cls,
        calibrated_decision: str,
        metrics: List[ConfidenceMetrics],
        uncertainty_model: str = "linear",
    ) -> ConfidenceCalibration:
        """Create a new confidence calibration."""
        return cls(
            calibration_id=f"confidence_calibration:{uuid.uuid4().hex[:16]}",
            calibrated_decision=calibrated_decision,
            calibration_metrics=tuple(metrics),
            uncertainty_model=uncertainty_model,
        )


__all__ = [
    "ConfidenceMetrics",
    "ConfidenceCalibration",
]