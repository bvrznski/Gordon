# Legal Diagnostics - Phase 7.47 Part 1
# ======================================

"""
Diagnostics Contract.

Legal diagnostics provide:
    - System health monitoring
    - Performance metrics
    - Error tracking
    - Operational insights
    
Health remains descriptive.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DiagnosticReport:
    """
    A diagnostic report for a legal reasoning component.
    
    A diagnostic includes:
        - Component being diagnosed
        - Metrics collected
        - Issues detected (if any)
        - Performance data
    
    Diagnostics remain descriptive.
    """
    
    # Identity
    diagnostic_id: str                        # Unique identifier
    
    # Target
    target_type: str                          # e.g., "session", "interpretation"
    target_id: str                            # ID of component diagnosed
    
    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)  # Collected metrics
    
    # Issues
    issues_detected: Tuple[Dict[str, Any], ...] = ()  # Problems found
    health_status: Optional[str] = None       # e.g., "healthy", "degraded"
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        target_type: str,
        target_id: str,
    ) -> DiagnosticReport:
        """Create a new diagnostic report."""
        return cls(
            diagnostic_id=f"diagnostic:{uuid.uuid4().hex[:16]}",
            target_type=target_type,
            target_id=target_id,
        )
    
    def with_metrics(self, metrics: Dict[str, Any]) -> DiagnosticReport:
        """Add metrics to the diagnostic."""
        return dataclass_replace(
            self,
            metrics={**self.metrics, **metrics},
        )


@dataclass(frozen=True)
class HealthMetrics:
    """
    Health metrics for a legal reasoning subsystem.
    
    Includes:
        - Component counts
        - Performance statistics
        - Error rates
        - Response times
    
    Health remains descriptive (never prescriptive).
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Subsystem information
    subsystem_type: str                       # e.g., "obligations", "rights"
    
    # Counts
    total_components: int = 0                 # How many components?
    active_components: int = 0                # How many are active?
    
    # Performance
    average_response_time_ms: float = 0.0     # Average processing time
    max_response_time_ms: float = 0.0         # Peak response time
    
    # Quality metrics
    error_rate: float = 0.0                   # Error percentage
    validation_pass_rate: float = 1.0         # Pass rate for validations
    
    # Timing
    collected_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        subsystem_type: str,
    ) -> HealthMetrics:
        """Create new health metrics."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            subsystem_type=subsystem_type,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticReport",
    "HealthMetrics",
]