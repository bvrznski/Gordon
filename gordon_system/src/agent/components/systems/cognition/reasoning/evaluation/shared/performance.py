# Performance Assessment - Phase 7.23
# ====================================

"""
Performance Assessment for Gordon's Evaluation Reasoning subsystem.

Performance assessment evaluates:
- Objective completion
- Resource efficiency
- Latency
- Correctness
- Robustness
- Constraint satisfaction
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PerformanceMetricKind(Enum):
    """Kinds of performance metrics."""
    
    TIME = "time"               # Temporal metrics (latency, throughput)
    RESOURCE = "resource"       # Resource utilization (memory, CPU, I/O)
    CORRECTNESS = "correctness" # Output correctness
    ROBUSTNESS = "robustness"   # Error handling, resilience
    COMPLETION = "completion"   # Objective completion


@dataclass(frozen=True)
class PerformanceMetric:
    """
    A single performance metric.
    
    Each metric contains:
        - Metric kind and name
        - Value and units
        - Threshold (optional, for pass/fail)
        - Timestamps
    
    Metrics remain explicit and inspectable.
    """
    
    metric_id: str                      # Unique metric identifier
    metric_kind: PerformanceMetricKind  # What kind of metric?
    metric_name: str                    # Name of this metric
    value: float                        # Measured value
    expected_value: Optional[float] = None  # Expected reference value
    units: str = "unit"                 # Units of measurement
    threshold: Optional[float] = None   # Pass/fail threshold
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_pass(self) -> bool:
        """Check if metric passed (if threshold defined)."""
        if self.threshold is None or self.expected_value is None:
            return True  # No constraint to check against
        # Pass if within acceptable range of expected value
        return abs(self.value - self.expected_value) <= self.threshold


@dataclass(frozen=True)
class PerformanceAssessment:
    """
    A performance assessment for a single target or set.
    
    An assessment contains:
        - Assessment identity
        - Evaluated targets
        - Performance metrics (all measured)
        - Assessment result (summary)
        - Provenance tracking
    
    Assessments remain explicit and independently inspectable.
    """
    
    # Identity
    assessment_id: str                  # Unique assessment identifier
    semantic_identity: str              # Semantic identity for traceability
    
    # Evaluated target
    evaluated_target: Dict[str, Any] = field(default_factory=dict)  # Target info
    
    # Metrics
    performance_metrics: List[PerformanceMetric] = field(default_factory=list)
    
    # Assessment result
    assessment_result: Optional[str] = None  # "pass", "fail", "partial"
    summary: str = ""                        # Human-readable summary
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_assessment_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def metric_count(self) -> int:
        """Return number of metrics in this assessment."""
        return len(self.performance_metrics)
    
    @property
    def passed_metric_count(self) -> int:
        """Count metrics that passed."""
        return sum(1 for m in self.performance_metrics if m.is_pass)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluated_target: Dict[str, Any],
        metrics: List[PerformanceMetric],
        origin_context: str = "unknown",
        source_assessment_id: Optional[str] = None,
    ) -> PerformanceAssessment:
        """Create a new performance assessment."""
        # Determine result
        passed_count = sum(1 for m in metrics if m.is_pass)
        total = len(metrics)
        
        if total == 0:
            result = "pass"  # No constraints to check
        elif passed_count == total:
            result = "pass"
        elif passed_count > 0:
            result = "partial"
        else:
            result = "fail"
        
        return cls(
            assessment_id=f"perf:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_target=dict(evaluated_target),
            performance_metrics=list(metrics),
            assessment_result=result,
            summary=f"{passed_count}/{total} metrics passed",
            origin_context=origin_context,
            source_assessment_id=source_assessment_id,
            created_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PerformanceMetricKind",
    "PerformanceMetric",
    "PerformanceAssessment",
]