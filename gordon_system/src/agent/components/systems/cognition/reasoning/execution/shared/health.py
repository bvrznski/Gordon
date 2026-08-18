# Execution Reasoning Health - Phase 7.21
# =======================================

"""
Canonical Execution Health metrics for Phase 7.21.

Health metrics track:
    - Commands orchestrated
    - Parallel efficiency
    - Authorization latency
    - Rollback success
    - Adaptation frequency
    - Validation success
    - Diagnostics
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExecutionHealth:
    """
    Execution Health provides health metrics for the execution subsystem.
    
    Metrics include:
        - Commands orchestrated
        - Parallel efficiency
        - Authorization latency
        - Rollback success rate
        - Adaptation frequency
        - Validation success rate
        - Diagnostics
    
    Health remains descriptive and observational.
    """
    
    # Identity
    health_identity: str                        # Unique health identifier
    
    # Metrics snapshot time
    measured_at_utc: float = field(default_factory=time.time)
    
    # Command metrics
    commands_orchestrated: int = 0              # Total commands executed
    parallel_commands: int = 0                  # Parallel command count
    
    # Efficiency metrics
    authorization_latency_seconds: float = 0.0  # Average authorization latency
    synchronization_overhead_seconds: float = 0.0  # Synchronization overhead
    
    # Success metrics
    rollback_success_rate: float = 1.0          # Rollback success rate (0-1)
    validation_success_rate: float = 1.0        # Validation success rate (0-1)
    
    @property
    def overall_health_score(self) -> float:
        """Calculate overall health score (0-1)."""
        return (
            self.validation_success_rate * 0.4 +
            self.rollback_success_rate * 0.3 +
            (1.0 - min(self.authorization_latency_seconds / 10.0, 1.0)) * 0.2 +
            (1.0 - min(self.synchronization_overhead_seconds / 5.0, 1.0)) * 0.1
        )
    
    @property
    def authorization_integrity_score(self) -> float:
        """Authorization integrity score."""
        return self.authorization_latency_seconds if self.authorization_latency_seconds > 0 else 1.0
    
    @classmethod
    def create(cls) -> ExecutionHealth:
        """Create a new execution health instance with default metrics."""
        return cls(health_identity=f"health:{uuid.uuid4().hex[:16]}")
    
    def record_command(self, is_parallel: bool = False) -> ExecutionHealth:
        """Return a new instance with command count incremented."""
        return dataclass_replace(
            self,
            commands_orchestrated=self.commands_orchestrated + 1,
            parallel_commands=self.parallel_commands + (1 if is_parallel else 0),
        )
    
    def record_authorization(self, latency_seconds: float) -> ExecutionHealth:
        """Return a new instance with authorization metrics updated."""
        return dataclass_replace(
            self,
            authorization_latency_seconds=latency_seconds,
        )


@dataclass(frozen=True)
class HealthMetricsSnapshot:
    """
    Snapshot of health metrics at a point in time.
    
    Used for diagnostics and historical analysis.
    """
    
    # Identity
    snapshot_identity: str                      # Unique snapshot identifier
    
    # Timestamp
    recorded_at_utc: float = field(default_factory=time.time)
    
    # Metrics values
    commands_orchestrated: int = 0
    parallel_commands: int = 0
    authorization_latency_seconds: float = 0.0
    rollback_success_rate: float = 1.0
    validation_success_rate: float = 1.0
    
    @classmethod
    def create(cls) -> HealthMetricsSnapshot:
        """Create a new health metrics snapshot."""
        return cls(snapshot_identity=f"snapshot:{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class HealthAlert:
    """
    A health alert for attention.
    
    Includes severity level and diagnostic information.
    """
    
    # Identity
    alert_identity: str                         # Unique alert identifier
    
    # Alert details
    alert_type: str                             # e.g., "high_latency", "low_success_rate"
    description: str                            # Human-readable description
    
    # Severity (info, warning, critical)
    severity: str = "warning"                   # Alert severity level
    
    @classmethod
    def create(
        cls,
        alert_type: str,
        description: str,
        severity: str = "warning",
    ) -> HealthAlert:
        """Create a new health alert."""
        return cls(
            alert_identity=f"alert:{uuid.uuid4().hex[:16]}",
            alert_type=alert_type,
            description=description,
            severity=severity,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
]