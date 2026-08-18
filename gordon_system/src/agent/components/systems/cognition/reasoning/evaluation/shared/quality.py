# Quality Estimation - Phase 7.23
# ===============================

"""
Quality Estimation for Gordon's Evaluation Reasoning subsystem.

Quality estimation evaluates:
- Accuracy
- Consistency
- Reliability
- Reproducibility
- Stability
- Confidence
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class QualityMetricKind(Enum):
    """Kinds of quality metrics."""
    
    ACCURACY = "accuracy"           # Correctness of outputs
    CONSISTENCY = "consistency"     # Internal coherence
    RELIABILITY = "reliability"     # Dependable performance
    REPRODUCIBILITY = "reproducibility"  # Same results under same conditions
    STABILITY = "stability"         # Resistance to perturbations
    CONFIDENCE = "confidence"       # Certainty estimate


@dataclass(frozen=True)
class QualityMetric:
    """
    A single quality metric.
    
    Each metric contains:
        - Metric kind and name
        - Value (0.0-1.0 scale for most metrics)
        - Confidence in this measurement
        - Timestamps
    
    Metrics remain explicit and inspectable.
    """
    
    metric_id: str                  # Unique metric identifier
    metric_kind: QualityMetricKind  # What kind of quality metric?
    metric_name: str                # Name of this metric
    value: float                    # Measured quality (typically 0.0-1.0)
    confidence: Optional[float] = None  # Confidence in measurement
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_high_quality(self) -> bool:
        """Check if this metric indicates high quality."""
        return self.value >= 0.8  # Threshold for "high" quality


@dataclass(frozen=True)
class QualityAssessment:
    """
    A quality assessment for a single target or set.
    
    An assessment contains:
        - Assessment identity
        - Quality metrics (all measured)
        - Quality score (aggregated)
        - Confidence in the overall assessment
        - Provenance tracking
    
    Assessments remain explicit and independently inspectable.
    """
    
    # Identity
    quality_id: str                   # Unique quality identifier
    semantic_identity: str            # Semantic identity for traceability
    
    # Metrics
    quality_metrics: List[QualityMetric] = field(default_factory=list)
    
    # Assessment result
    quality_score: float = 0.0        # Aggregated quality score (0.0-1.0)
    confidence: float = 0.0           # Confidence in this assessment
    
    # Quality characteristics
    accuracy_estimate: Optional[float] = None
    consistency_estimate: Optional[float] = None
    reliability_estimate: Optional[float] = None
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_assessment_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def metric_count(self) -> int:
        """Return number of metrics in this assessment."""
        return len(self.quality_metrics)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        metrics: List[QualityMetric],
        origin_context: str = "unknown",
        source_assessment_id: Optional[str] = None,
    ) -> QualityAssessment:
        """Create a new quality assessment."""
        if not metrics:
            return cls(
                quality_id=f"qual:{uuid.uuid4().hex[:16]}",
                semantic_identity=semantic_identity,
                quality_metrics=[],
                quality_score=0.0,
                confidence=0.0,
                origin_context=origin_context,
                source_assessment_id=source_assessment_id,
                created_at_utc=time.time(),
            )
        
        # Calculate aggregate score (average of metric values)
        avg_value = sum(m.value for m in metrics) / len(metrics)
        
        # Estimate confidence based on metric count and coverage
        base_confidence = min(0.5 + (len(metrics) * 0.1), 0.95)
        
        return cls(
            quality_id=f"qual:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            quality_metrics=list(metrics),
            quality_score=avg_value,
            confidence=base_confidence,
            accuracy_estimate=next((m.value for m in metrics if m.metric_kind == QualityMetricKind.ACCURACY), None),
            consistency_estimate=next((m.value for m in metrics if m.metric_kind == QualityMetricKind.CONSISTENCY), None),
            reliability_estimate=next((m.value for m in metrics if m.metric_kind == QualityMetricKind.RELIABILITY), None),
            origin_context=origin_context,
            source_assessment_id=source_assessment_id,
            created_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "QualityMetricKind",
    "QualityMetric",
    "QualityAssessment",
]