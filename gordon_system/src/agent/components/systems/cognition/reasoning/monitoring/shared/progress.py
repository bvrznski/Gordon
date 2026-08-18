# Monitoring Progress Contract - Phase 7.22
# =========================================

"""
Canonical Progress Estimate.

Progress tracking provides completion estimates for monitored executions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CompletionEstimate:
    """
    A completion estimate for a specific component.
    """
    
    # Component identifier
    component_id: str                         # What is being tracked?
    
    # Progress
    total_units: int = 0                      # Total work units
    completed_units: int = 0                  # Completed work units
    
    # Timing
    started_at_utc: Optional[float] = None
    estimated_completion_utc: Optional[float] = None
    elapsed_seconds: float = 0.0
    
    # Velocity metrics
    units_per_second: float = 0.0
    
    @property
    def ratio(self) -> float:
        """Calculate completion ratio (0.0 to 1.0)."""
        if self.total_units == 0:
            return 0.0
        return self.completed_units / self.total_units


@dataclass(frozen=True)
class ProgressEstimate:
    """
    A progress estimate for monitored execution.
    
    A progress estimate contains:
        - Identity and provenance
        - Tracked execution reference
        - Completion estimates
        - Confidence levels
        - Velocity metrics
    
    Progress remains explicit and traceable.
    """
    
    # Identity
    progress_id: str                          # Unique progress identifier
    
    # Tracked execution
    tracked_execution: str                    # ID of what is being tracked
    plan_reference: Optional[str] = None      # Reference to original plan
    
    # Completion estimates
    completion_estimates: List[CompletionEstimate] = field(default_factory=list)
    
    # Overall progress
    total_units: int = 0                      # Total work across all components
    completed_units: int = 0                  # Completed work across all components
    
    # Timing
    estimated_completion_utc: Optional[float] = None
    confidence: float = 0.0                   # Confidence in the estimate (0.0 to 1.0)
    
    # Velocity metrics
    average_velocity: float = 0.0             # Units per second average
    velocity_stddev: float = 0.0              # Velocity variability
    
    # Critical path
    critical_path_components: List[str] = field(default_factory=list)  # Components limiting progress
    
    # Timing
    recorded_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def completion_ratio(self) -> int:
        """Calculate overall completion ratio (0 to 100)."""
        if self.total_units == 0:
            return 0
        return int((self.completed_units / self.total_units) * 100)
    
    @property
    def has_critical_path(self) -> bool:
        """Check if critical path components exist."""
        return len(self.critical_path_components) > 0
    
    def get_component_estimate(self, component_id: str) -> Optional[CompletionEstimate]:
        """Get completion estimate for a specific component."""
        for est in self.completion_estimates:
            if est.component_id == component_id:
                return est
        return None
    
    def add_or_update_estimate(
        self,
        component_id: str,
        total_units: int = 0,
        completed_units: int = 0,
        units_per_second: float = 0.0,
    ) -> ProgressEstimate:
        """Add or update a component's completion estimate."""
        new_estimates = list(self.completion_estimates)
        
        for i, est in enumerate(new_estimates):
            if est.component_id == component_id:
                new_estimates[i] = dataclass_replace(
                    est,
                    total_units=total_units,
                    completed_units=completed_units,
                    units_per_second=units_per_second,
                    elapsed_seconds=time.time() - (est.started_at_utc or time.time()),
                )
                break
        else:
            # Add new estimate
            new_estimates.append(CompletionEstimate(
                component_id=component_id,
                total_units=total_units,
                completed_units=completed_units,
                units_per_second=units_per_second,
                started_at_utc=time.time(),
            ))
        
        return dataclass_replace(
            self,
            completion_estimates=new_estimates,
            # Recalculate totals
            total_units=sum(e.total_units for e in new_estimates),
            completed_units=sum(e.completed_units for e in new_estimates),
        )
    
    def update_confidence(self, confidence: float) -> ProgressEstimate:
        """Update progress confidence."""
        return dataclass_replace(
            self,
            confidence=confidence,
        )
    
    def to_completed(self, estimated_completion_utc: Optional[float] = None) -> ProgressEstimate:
        """Mark progress as completed."""
        return dataclass_replace(
            self,
            estimated_completion_utc=estimated_completion_utc or time.time(),
            confidence=1.0,
        )
    
    @classmethod
    def create(
        cls,
        tracked_execution: str,
        plan_reference: Optional[str] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> ProgressEstimate:
        """Create a new progress estimate."""
        return cls(
            progress_id=f"progress:{uuid.uuid4().hex[:16]}",
            tracked_execution=tracked_execution,
            plan_reference=plan_reference,
            recorded_at_utc=time.time(),
            source_descriptor_id=source_descriptor_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ProgressEstimate",
    "CompletionEstimate",
]