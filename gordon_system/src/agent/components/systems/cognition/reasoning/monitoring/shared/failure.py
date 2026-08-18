# Monitoring Failure Contract - Phase 7.22
# ========================================

"""
Canonical Monitoring Failure.

Failures represent monitoring breakdowns and their diagnostics.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Types of monitoring failures."""
    
    OBSERVATION_LOSS = "observation_loss"
    SENSOR_FAILURE = "sensor_failure"
    INCONSISTENT_OBSERVATIONS = "inconsistent_observations"
    STATE_RECONSTRUCTION_FAILURE = "state_reconstruction_failure"
    SAMPLING_FAILURE = "sampling_failure"
    COMMUNICATION_INTErruPTION = "communication_interruption"


@dataclass(frozen=True)
class MonitoringFailure:
    """
    A monitoring failure with diagnostics.
    
    Failures include:
        - Failure identity and type
        - Diagnostics information
        - Recovery options
    
    Failures remain explicit and inspectable.
    """
    
    # Identity
    failure_id: str                           # Unique failure identifier
    
    # Failure classification
    failure_kind: FailureKind                 # What kind of failure?
    severity: str = "error"                   # error, critical, warning
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Recovery options
    recovery_options: List[str] = field(default_factory=list)
    
    # Supporting observations (before/during failure)
    supporting_observations: List[str] = field(default_factory=list)
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    resolved_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def is_resolved(self) -> bool:
        """Check if failure has been resolved."""
        return self.resolved_at_utc is not None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate how long the failure lasted."""
        if self.is_resolved:
            return self.resolved_at_utc - self.occurred_at_utc
        return time.time() - self.occurred_at_utc
    
    def add_recovery_option(self, option: str) -> MonitoringFailure:
        """Add a recovery option."""
        new_options = list(self.recovery_options)
        if option not in new_options:
            new_options.append(option)
        
        return dataclass_replace(
            self,
            recovery_options=new_options,
        )
    
    def add_diagnostics(self, diagnostics: Dict[str, Any]) -> MonitoringFailure:
        """Add diagnostic information."""
        new_diagnostics = dict(self.diagnostics)
        new_diagnostics.update(diagnostics)
        
        return dataclass_replace(
            self,
            diagnostics=new_diagnostics,
        )
    
    def mark_resolved(self) -> MonitoringFailure:
        """Mark the failure as resolved."""
        return dataclass_replace(
            self,
            resolved_at_utc=time.time(),
        )
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        diagnostics: Optional[Dict[str, Any]] = None,
        severity: str = "error",
        source_descriptor_id: Optional[str] = None,
    ) -> MonitoringFailure:
        """Create a new monitoring failure."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostics=diagnostics or {},
            severity=severity,
            occurred_at_utc=time.time(),
            source_descriptor_id=source_descriptor_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MonitoringFailure",
    "FailureKind",
]