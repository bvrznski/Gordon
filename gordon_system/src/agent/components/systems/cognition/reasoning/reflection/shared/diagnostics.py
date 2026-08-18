# Diagnostics - Phase 7.28
# =======================

"""
Diagnostics provide runtime observability for reflection sessions.

Diagnostics track:
    - Session health metrics
    - Performance indicators
    - Resource utilization
    - Error rates and anomalies
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ReflectionHealth:
    """
    Health status of a reflection session.
    
    Health metrics track:
        - Session completion rate
        - Performance indicators
        - Resource utilization
        - Error rates and anomalies
    """
    
    # Identity
    health_id: str                            # Unique health identifier
    
    # Overall status
    overall_status: str = "healthy"           # healthy, warning, critical
    
    # Metrics
    reflection_count: int = 0                 # Total reflections processed
    success_count: int = 0                    # Successful reflections
    failure_count: int = 0                    # Failed reflections
    
    # Performance
    avg_duration_seconds: float = 0.0         # Average duration
    peak_memory_mb: float = 0.0               # Peak memory usage
    cpu_utilization_percent: float = 0.0      # CPU utilization
    
    # Errors and warnings
    error_count: int = 0                      # Total errors
    warning_count: int = 0                    # Total warnings
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    monitoring_window_start_utc: float = field(default_factory=time.time)
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate."""
        if self.reflection_count == 0:
            return 1.0
        return self.success_count / self.reflection_count
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.reflection_count == 0:
            return 0.0
        return self.failure_count / self.reflection_count


@dataclass(frozen=True)
class ReflectionDiagnostics:
    """
    Diagnostics for reflection sessions.
    
    Diagnostics track:
        - Session lifecycle events
        - Performance metrics
        - Resource utilization
        - Error tracking
    
    Diagnostics remain independently inspectable.
    """
    
    # Identity
    diagnostics_id: str                       # Unique diagnostics identifier
    
    # Lifecycle events
    session_started_at_utc: Optional[float] = None
    session_completed_at_utc: Optional[float] = None
    
    # Performance metrics
    total_processing_time_seconds: float = 0.0
    memory_peak_mb: float = 0.0
    
    # Errors and warnings
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    @classmethod
    def create(
        cls,
        session_started_at_utc: Optional[float] = None,
    ) -> ReflectionDiagnostics:
        """Create new diagnostics."""
        return cls(
            diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            session_started_at_utc=session_started_at_utc,
        )
    
    def add_error(self, error: Dict[str, Any]) -> ReflectionDiagnostics:
        """Add an error to diagnostics."""
        return dataclass_replace(
            self,
            errors=self.errors + [error],
        )
    
    def add_warning(self, warning: Dict[str, Any]) -> ReflectionDiagnostics:
        """Add a warning to diagnostics."""
        return dataclass_replace(
            self,
            warnings=self.warnings + [warning],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReflectionHealth",
    "ReflectionDiagnostics",
]