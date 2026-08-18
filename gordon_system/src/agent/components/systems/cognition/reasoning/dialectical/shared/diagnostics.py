# Dialectical Diagnostics - Phase 7.17
# ====================================

"""
Canonical Dialectical Diagnostics Contract.

Diagnostics provide observability into dialectical reasoning processes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DialecticalDiagnostics:
    """
    Diagnostics for a dialectical process.

    Provides observability into:
        - Reasoning performance
        - Resource usage
        - Processing bottlenecks
        - Error patterns
        - Trace completeness
    """

    # Identity
    diagnostics_id: str                     # Unique identifier

    # Process diagnostics
    reasoning_steps_completed: int = 0
    total_reasoning_steps: int = 0
    resource_usage_percent: float = 0.0
    processing_bottlenecks: Tuple[str, ...] = ()

    # Error tracking
    errors_encountered: Tuple[Dict[str, Any], ...] = ()
    error_types: Tuple[str, ...] = ()

    # Timing breakdown (for each stage)
    timing_breakdown: Dict[str, float] = field(default_factory=dict)

    # Timing
    recorded_at_utc: float = field(default_factory=time.time)

    @property
    def completion_percent(self) -> float:
        """Calculate completion percentage."""
        if self.total_reasoning_steps == 0:
            return 100.0
        return (self.reasoning_steps_completed / self.total_reasoning_steps) * 100

    @classmethod
    def create(
        cls,
    ) -> DialecticalDiagnostics:
        """Create a new diagnostics record."""
        return cls(
            diagnostics_id=f"dialectical_diagnostics:{uuid.uuid4().hex[:16]}",
        )

    def with_reasoning_step(self) -> DialecticalDiagnostics:
        """Record a completed reasoning step."""
        return dataclass_replace(
            self,
            reasoning_steps_completed=self.reasoning_steps_completed + 1,
        )

    def set_total_steps(self, total: int) -> DialecticalDiagnostics:
        """Set the total number of steps to complete."""
        return dataclass_replace(
            self,
            total_reasoning_steps=total,
        )

    def with_timing(self, stage: str, duration_seconds: float) -> DialecticalDiagnostics:
        """Record timing for a stage."""
        new_timing = dict(self.timing_breakdown)
        new_timing[stage] = duration_seconds
        return dataclass_replace(
            self,
            timing_breakdown=new_timing,
        )

    def with_error(self, error: Dict[str, Any]) -> DialecticalDiagnostics:
        """Record an encountered error."""
        return dataclass_replace(
            self,
            errors_encountered=self.errors_encountered + (error,),
            error_types=self.error_types + (error.get("type", "unknown"),),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DialecticalDiagnostics",
]