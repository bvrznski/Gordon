# Knowledge Model Comparison - Phase 6.7
# =======================================

"""
Model Comparison: Evaluate models against each other on shared dimensions.

Comparisons remain observational - they don't modify models, just describe their
relationships and relative quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# COMPARISON METRIC - Dimension of comparison
# =============================================================================


class ComparisonMetric(Enum):
    """
    Dimensions along which models can be compared.
    
    Each comparison shall use explicit metrics to ensure objective evaluation.
    """
    
    COVERAGE = "coverage"             # Breadth of domain covered
    ACCURACY = "accuracy"             # Fidelity to observed reality
    CONSISTENCY = "consistency"       # Internal logical coherence
    PREDICTION_QUALITY = "prediction_quality"  # Quality of predictions made
    COMPLEXITY = "complexity"         # Model simplicity vs expressiveness


# =============================================================================
# MODEL COMPARISON - Canonical comparison record
# =============================================================================


@dataclass(frozen=True)
class ModelComparison:
    """
    Canonical representation of model comparison in Gordon's knowledge system.
    
    Comparisons provide objective evaluation of models along specified dimensions.
    
    Fields:
        comparison_identity:   Unique identifier for this comparison
        compared_models:       IDs of models being compared
        comparison_metrics:    Metrics used in the comparison
        findings:              Results of comparisons on each metric
        recommendations:       Suggestions based on comparison
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    comparison_identity: str            # Unique ID for this comparison
    
    # Compared models (required)
    compared_models: Tuple[str, ...]    # IDs of the models being compared
    
    # Metrics used
    comparison_metrics: Tuple[ComparisonMetric, ...] = field(default_factory=tuple)  # Metrics used
    
    # Findings per metric
    findings: Dict[str, float] = field(default_factory=dict)  # Metric -> result
    
    # Recommendations (if any)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)  # Suggested actions
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def model_count(self) -> int:
        """Get the number of models being compared."""
        return len(self.compared_models)
    
    @property
    def is_valid(self) -> bool:
        """Check if comparison has minimal required data."""
        return (
            len(self.comparison_identity) > 0 and
            self.model_count >= 2
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert comparison to dictionary for serialization."""
        return {
            "comparison_identity": self.comparison_identity,
            "compared_models": list(self.compared_models),
            "comparison_metrics": [m.value if m else None for m in self.comparison_metrics],
            "findings": dict(self.findings),
            "recommendations": list(self.recommendations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelComparison":
        """Create comparison from dictionary."""
        metrics_data = data.get("comparison_metrics", [])
        comparison_metrics = tuple(
            ComparisonMetric(m) if m else None
            for m in metrics_data
        )
        
        return cls(
            comparison_identity=data.get("comparison_identity", str(uuid.uuid4())),
            compared_models=tuple(data.get("compared_models", [])),
            comparison_metrics=comparison_metrics,
            findings=dict(data.get("findings", {})),
            recommendations=tuple(data.get("recommendations", [])),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        compared_models: List[str],
        metrics: Optional[List[ComparisonMetric]] = None,
        findings: Optional[Dict[str, float]] = None,
    ) -> "ModelComparison":
        """
        Create a new model comparison.
        
        Args:
            compared_models: IDs of models being compared
            metrics: Metrics used in comparison (optional)
            findings: Results per metric (optional)
            
        Returns:
            A new comparison record
        """
        return cls(
            comparison_identity=f"comparison:{uuid.uuid4().hex[:16]}",
            compared_models=tuple(compared_models),
            comparison_metrics=tuple(metrics or []),
            findings=dict(findings or {}),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def add_finding(
        self,
        metric: str,
        result: float,
    ) -> "ModelComparison":
        """Create a revision with an additional finding."""
        return ModelComparison(
            comparison_identity=self.comparison_identity,
            compared_models=self.compared_models,
            comparison_metrics=self.comparison_metrics,
            findings={**self.findings, metric: result},
            recommendations=self.recommendations,
            provenance={
                **self.provenance,
                "finding_added_at_utc": time.time(),
                "added_metric": metric,
            },
        )
    
    def add_recommendation(
        self,
        recommendation: str,
    ) -> "ModelComparison":
        """Create a revision with an additional recommendation."""
        return ModelComparison(
            comparison_identity=self.comparison_identity,
            compared_models=self.compared_models,
            comparison_metrics=self.comparison_metrics,
            findings=self.findings,
            recommendations=self.recommendations + (recommendation,),
            provenance={
                **self.provenance,
                "recommendation_added_at_utc": time.time(),
                "added_recommendation": recommendation,
            },
        )


__all__ = [
    "ComparisonMetric",
    "ModelComparison",
]