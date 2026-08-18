# Evaluation Health - Phase 7.23
# =============================

"""
Evaluation Health metrics for Gordon's Evaluation Reasoning subsystem.

Metrics include:
- Evaluations completed
- Metric coverage
- Quality estimation accuracy
- Verification success rate
- Assessment consistency
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class HealthMetrics:
    """
    Health metrics for the evaluation reasoning subsystem.
    
    Metrics include:
        - Evaluations completed (total and by type)
        - Metric coverage (percentage of expected metrics measured)
        - Quality estimation accuracy
        - Verification success rate
        - Assessment consistency
        - Diagnostics
    """
    
    # Identity
    health_id: str                      # Unique health identifier
    
    # Completion metrics
    evaluations_completed: int = 0      # Total completed evaluations
    evaluations_by_mode: Dict[str, int] = field(default_factory=dict)  # Completed by mode
    
    # Quality metrics
    metric_coverage: float = 0.0        # Percentage of expected metrics measured (0-1)
    quality_estimation_accuracy: float = 0.0  # Accuracy of quality estimates
    
    # Success metrics
    verification_success_rate: float = 0.0  # Rate of successful verifications
    assessment_consistency: float = 0.0     # Consistency across evaluations
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    measured_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class EvaluationHealth:
    """
    Health status of an evaluation session.
    
    Health contains:
        - Health identity
        - Health metrics
        - Overall health assessment (healthy/warning/critical)
        - Provenance tracking
    
    Health remains descriptive and never modifies evaluation artifacts directly.
    """
    
    # Identity
    health_id: str                      # Unique health identifier
    semantic_identity: str              # Semantic identity for traceability
    
    # Metrics
    metrics: HealthMetrics
    
    # Overall assessment
    overall_health: str = "unknown"     # healthy/warning/critical
    issues: List[str] = field(default_factory=list)  # Detected issues
    
    # Metadata
    measured_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_health_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        metrics: HealthMetrics,
        origin_context: str = "unknown",
        source_health_id: Optional[str] = None,
    ) -> EvaluationHealth:
        """Create a new evaluation health status."""
        # Determine overall health based on metrics
        issues = []
        
        if metrics.evaluations_completed == 0:
            issues.append("No evaluations completed yet")
        
        if metrics.metric_coverage < 0.5:
            issues.append(f"Low metric coverage: {metrics.metric_coverage:.1%}")
        
        if metrics.quality_estimation_accuracy < 0.7:
            issues.append(f"Low quality estimation accuracy: {metrics.quality_estimation_accuracy:.1%}")
        
        if metrics.assessment_consistency < 0.8:
            issues.append(f"Low assessment consistency: {metrics.assessment_consistency:.1%}")
        
        # Determine overall status
        if not issues:
            overall = "healthy"
        elif len(issues) == 1 and metrics.evaluations_completed > 0:
            overall = "warning"
        else:
            overall = "critical"
        
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            metrics=metrics,
            overall_health=overall,
            issues=list(issues),
            origin_context=origin_context,
            source_health_id=source_health_id,
            measured_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HealthMetrics",
    "EvaluationHealth",
]