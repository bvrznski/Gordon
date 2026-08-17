# Knowledge Model Health - Phase 6.7
# ===================================

"""
Model Health: Metrics describing model quality, stability, and maintenance.

Health metrics are descriptive rather than prescriptive, providing insight into
model condition without modifying it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# HEALTH STATUS - Overall health classification
# =============================================================================


class HealthStatus(Enum):
    """
    Classification of model health.
    
    Provides a high-level summary of model condition based on metrics.
    """
    
    HEALTHY = "healthy"               # All metrics within acceptable ranges
    DEGRADED = "degraded"             # Some issues but functional
    CRITICAL = "critical"             # Major issues requiring attention


# =============================================================================
# MODEL HEALTH - Canonical health record
# =============================================================================


@dataclass(frozen=True)
class ModelHealth:
    """
    Canonical representation of model health in Gordon's knowledge system.
    
    Health metrics provide descriptive insight into model condition without
    modifying the model itself.
    
    Fields:
        health_identity:       Unique identifier for this health assessment
        evaluated_model:       ID of the model being assessed
        coverage:              Model domain coverage score (0.0-1.0)
        prediction_accuracy:   Historical prediction accuracy (0.0-1.0)
        assumption_count:      Number of explicit assumptions
        validation_failures:   Number of failed validations
        revision_depth:        Total revisions made to model
        dependency_depth:      Depth of dependency chain
        stability:             Stability score (0.0-1.0)
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    health_identity: str                # Unique ID for this health assessment
    
    # Evaluated model reference (required)
    evaluated_model: str                # Model being assessed
    
    # Health metrics (required - 0.0 to 1.0 where applicable)
    coverage: float = 0.5               # Domain coverage score
    prediction_accuracy: float = 0.5    # Historical accuracy
    assumption_count: int = 0           # Number of assumptions
    validation_failures: int = 0        # Failed validations count
    revision_depth: int = 1             # Total revisions
    dependency_depth: int = 0           # Dependency chain depth
    
    # Derived stability metric (computed)
    @property
    def stability(self) -> float:
        """
        Calculate stability based on other metrics.
        
        Higher is more stable - less revision, fewer failures, more assumptions
        indicates more established understanding.
        """
        if self.revision_depth <= 1:
            base_stability = 0.8
        elif self.revision_depth <= 3:
            base_stability = 0.6
        else:
            base_stability = max(0.2, 0.4 - (self.revision_depth * 0.05))
        
        # Reduce for validation failures
        if self.validation_failures > 0:
            base_stability *= max(0.5, 1.0 - (self.validation_failures * 0.1))
        
        return max(0.0, min(1.0, base_stability))
    
    @property
    def status(self) -> HealthStatus:
        """Determine overall health status."""
        if self.stability >= 0.7 and self.validation_failures == 0:
            return HealthStatus.HEALTHY
        elif self.stability >= 0.4 or self.validation_failures <= 2:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.CRITICAL
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if health record has minimal required data."""
        return (
            len(self.health_identity) > 0 and
            len(self.evaluated_model) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health record to dictionary for serialization."""
        return {
            "health_identity": self.health_identity,
            "evaluated_model": self.evaluated_model,
            "coverage": self.coverage,
            "prediction_accuracy": self.prediction_accuracy,
            "assumption_count": self.assumption_count,
            "validation_failures": self.validation_failures,
            "revision_depth": self.revision_depth,
            "dependency_depth": self.dependency_depth,
            "stability": self.stability,
            "status": self.status.value if self.status else None,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelHealth":
        """Create health record from dictionary."""
        return cls(
            health_identity=data.get("health_identity", str(uuid.uuid4())),
            evaluated_model=data.get("evaluated_model", ""),
            coverage=float(data.get("coverage", 0.5)),
            prediction_accuracy=float(data.get("prediction_accuracy", 0.5)),
            assumption_count=int(data.get("assumption_count", 0)),
            validation_failures=int(data.get("validation_failures", 0)),
            revision_depth=int(data.get("revision_depth", 1)),
            dependency_depth=int(data.get("dependency_depth", 0)),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        evaluated_model: str,
        coverage: float = 0.5,
        prediction_accuracy: float = 0.5,
        assumption_count: int = 0,
        validation_failures: int = 0,
        revision_depth: int = 1,
        dependency_depth: int = 0,
    ) -> "ModelHealth":
        """
        Create a new model health assessment.
        
        Args:
            evaluated_model: ID of the model being assessed
            coverage: Domain coverage score (0.0-1.0)
            prediction_accuracy: Historical accuracy (0.0-1.0)
            assumption_count: Number of assumptions
            validation_failures: Failed validation count
            revision_depth: Total revisions made
            dependency_depth: Dependency chain depth
            
        Returns:
            A new health record
        """
        return cls(
            health_identity=f"health:{uuid.uuid4().hex[:16]}",
            evaluated_model=evaluated_model,
            coverage=max(0.0, min(1.0, float(coverage))),
            prediction_accuracy=max(0.0, min(1.0, float(prediction_accuracy))),
            assumption_count=max(0, int(assumption_count)),
            validation_failures=max(0, int(validation_failures)),
            revision_depth=max(1, int(revision_depth)),
            dependency_depth=max(0, int(dependency_depth)),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


# =============================================================================
# HEALTH METRICS - Helper for comprehensive health evaluation
# =============================================================================


@dataclass(frozen=True)
class HealthMetrics:
    """
    Container for comprehensive health metrics.
    
    Aggregates various metrics for complete model health assessment.
    
    Fields:
        coverage:              Domain coverage (0.0-1.0)
        accuracy:              Historical accuracy (0.0-1.0)
        consistency:           Internal consistency score (0.0-1.0)
        stability:             Stability over time (0.0-1.0)
        maturity:              Maturity level (0.0-1.0)
    """
    
    coverage: float = 0.5
    accuracy: float = 0.5
    consistency: float = 0.5
    stability: float = 0.5
    maturity: float = 0.5
    
    @property
    def overall_score(self) -> float:
        """Calculate overall health score as average of metrics."""
        return (
            self.coverage + self.accuracy + 
            self.consistency + self.stability + self.maturity
        ) / 5.0


__all__ = [
    "HealthStatus",
    "ModelHealth",
    "HealthMetrics",
]