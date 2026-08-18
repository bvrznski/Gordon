# Decision Health - Phase 7.19
# ===========================

"""
Canonical Decision Health Contract.

Decision Health tracks metrics about the decision reasoning system.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DecisionHealth:
    """
    Health metrics for decision reasoning.
    
    Metrics include:
        - Options evaluated (how many options were considered?)
        - Decision latency (how long did decisions take?)
        - Utility estimation quality
        - Confidence calibration quality
        - Decision reversals (how often are decisions revised?)
        - Validation success rate
        - Diagnostics
    
    Health remains descriptive; it never modifies the reasoning directly.
    """
    
    # Identity
    health_id: str                          # Unique identifier
    
    # Options metrics
    options_evaluated_count: int = 0        # Total options evaluated
    
    # Timing metrics
    average_decision_latency_seconds: float = 0.0
    max_decision_latency_seconds: float = 0.0
    
    # Evaluation quality
    utility_estimation_quality: float = 0.0 # Quality of utility estimates (0-1)
    confidence_calibration_quality: float = 0.0  # Quality of confidence calibration
    
    # Decision metrics
    decision_reversal_count: int = 0        # How often are decisions revised?
    validation_success_count: int = 0       # Validated decisions
    validation_failure_count: int = 0       # Invalid decisions
    
    # Timing
    recorded_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_decisions(self) -> int:
        """Count of total decisions made."""
        return self.validation_success_count + self.validation_failure_count
    
    @property
    def validation_rate(self) -> float:
        """Validation success rate (0.0 to 1.0)."""
        total = self.total_decisions
        if total == 0:
            return 0.0
        return self.validation_success_count / total
    
    @classmethod
    def create(cls) -> "DecisionHealth":
        """Create a new health record."""
        return cls(
            health_id=f"decision_health:{uuid.uuid4().hex[:16]}",
        )
    
    def increment_option(self) -> "DecisionHealth":
        """Record an option evaluation."""
        return dataclass_replace(
            self,
            options_evaluated_count=self.options_evaluated_count + 1,
        )
    
    def record_decision_latency(self, latency_seconds: float) -> "DecisionHealth":
        """Record a decision latency measurement."""
        new_count = self.validation_success_count + self.validation_failure_count
        total_latency = (
            self.average_decision_latency_seconds * new_count + latency_seconds
        )
        
        return dataclass_replace(
            self,
            average_decision_latency_seconds=total_latency / (new_count + 1),
            max_decision_latency_seconds=max(self.max_decision_latency_seconds, latency_seconds),
        )
    
    def record_validation(self, passed: bool) -> "DecisionHealth":
        """Record a validation result."""
        if passed:
            return dataclass_replace(
                self,
                validation_success_count=self.validation_success_count + 1,
            )
        else:
            return dataclass_replace(
                self,
                validation_failure_count=self.validation_failure_count + 1,
            )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionHealth",
]