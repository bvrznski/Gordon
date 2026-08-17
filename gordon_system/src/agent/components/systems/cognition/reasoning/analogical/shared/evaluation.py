# Mapping Evaluation - Phase 7.12
# ===============================

"""
Canonical Mapping Evaluation Contract.

Evaluation assesses mappings without modifying them directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class QualityMetric:
    """
    A single quality metric for mapping evaluation.
    
    Metrics include:
        - Completeness (what fraction is covered?)
        - Consistency (are there contradictions?)
        - Coverage (how much structure is aligned?)
        - Preservation (how well are properties preserved?)
        - Usefulness (how valuable is the transfer?)
    """
    
    # Identity
    metric_id: str                              # Unique identifier
    
    # Metric details
    metric_name: str                            # e.g., "completeness", "consistency"
    metric_value: float = 0.0                   # The value (0.0 to 1.0)
    metric_weight: float = 1.0                  # How important is this metric?
    
    # Thresholds
    minimum_acceptable: float = 0.5             # What's the pass threshold?
    target_value: float = 1.0                   # What's our ideal value?
    
    # Metadata
    measured_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class MappingEvaluation:
    """
    Evaluation of a mapping quality.
    
    Evaluation considers:
        - Mapping completeness (what fraction is covered?)
        - Mapping consistency (are there contradictions?)
        - Coverage (how much structure is aligned?)
        - Structural preservation (how well are properties preserved?)
        - Transfer usefulness (how valuable is the transfer?)
    
    Evaluation remains observational; it never modifies mappings directly.
    """
    
    # Identity
    evaluation_id: str                          # Unique identifier
    
    # Evaluated mapping
    evaluated_mapping_id: str                   # Which mapping?
    
    # Quality metrics
    quality_metrics: Tuple[QualityMetric, ...] = ()
    
    # Findings by category
    structural_findings: Tuple[str, ...] = ()
    consistency_findings: Tuple[str, ...] = ()
    coverage_findings: Tuple[str, ...] = ()
    transfer_findings: Tuple[str, ...] = ()
    
    # Overall assessment
    overall_quality_score: float = 0.0          # Combined score
    is_qualified: bool = False                  # Does it pass all checks?
    
    # Metadata
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def metric_count(self) -> int:
        """Number of quality metrics."""
        return len(self.quality_metrics)
    
    @classmethod
    def create(
        cls,
        evaluated_mapping_id: str,
    ) -> MappingEvaluation:
        """Create a new mapping evaluation."""
        return cls(
            evaluation_id=f"mapping_evaluation:{uuid.uuid4().hex[:16]}",
            evaluated_mapping_id=evaluated_mapping_id,
        )
    
    def add_metric(self, metric: QualityMetric) -> MappingEvaluation:
        """Add a quality metric to evaluation."""
        return dataclass_replace(
            self,
            quality_metrics=self.quality_metrics + (metric,),
        )
    
    def record_structural_finding(self, finding: str) -> MappingEvaluation:
        """Record a structural finding."""
        return dataclass_replace(
            self,
            structural_findings=self.structural_findings + (finding,),
        )


@dataclass(frozen=True)
class EvaluationSummary:
    """
    Summary of evaluation results across multiple mappings.
    
    Used for reporting and system-level quality assessment.
    """
    
    # Identity
    summary_id: str                             # Unique identifier
    
    # Evaluated mappings
    evaluated_mappings: Tuple[str, ...] = ()    # Which mappings were evaluated?
    
    # Results by category
    passed_evaluations: int = 0                 # How many passed?
    failed_evaluations: int = 0                 # How many failed?
    warnings_found: int = 0                     # Any warnings?
    
    # Average metrics
    average_quality_score: float = 0.0          # Average quality across mappings
    
    # Detailed findings
    detailed_findings: Tuple[Dict[str, Any], ...] = ()
    
    # Metadata
    generated_at_utc: float = field(default_factory=time.time)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        total = self.passed_evaluations + self.failed_evaluations
        if total == 0:
            return 1.0
        return self.passed_evaluations / total
    
    @classmethod
    def create(cls) -> EvaluationSummary:
        """Create a new evaluation summary."""
        return cls(
            summary_id=f"evaluation_summary:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "QualityMetric",
    "MappingEvaluation",
    "EvaluationSummary",
]