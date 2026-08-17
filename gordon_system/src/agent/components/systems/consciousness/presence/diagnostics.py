# Gordon Phase 5.7.5-I: Presence Engine - Diagnostics and Health
# ===============================================================================
"""
Diagnostics, health monitoring, and observability for the Presence Engine.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class PresenceMetrics:
    """
    Immutable metrics record at a point in time.
    
    Metrics are passive - they do not influence behavior, only observe it.
    """
    
    timestamp_utc: float = field(default_factory=time.time)
    """When these metrics were recorded."""
    
    generation: int = 0
    """Current generation number."""
    
    admitted_total: int = 0
    """Total items admitted since initialization."""
    
    withdrawn_total: int = 0
    """Total items withdrawn since initialization."""
    
    active_count: int = 0
    """Currently active presence count."""
    
    fading_count: int = 0
    """Currently fading presence count."""
    
    admission_failures: int = 0
    """Total admission failures (policy violations)."""
    
    transition_latencies_ms: Tuple[float, ...] = field(default_factory=tuple)
    """Transition latencies in milliseconds for recent transitions."""
    
    @property
    def total_present(self) -> int:
        """Total items currently in presence (not withdrawn)."""
        return self.active_count + self.fading_count
    
    @property
    def admission_rate(self) -> float:
        """Calculate admission rate from admitted and failures."""
        total = self.admitted_total + self.admission_failures
        if total == 0:
            return 1.0
        return self.admitted_total / total


@dataclass(frozen=True)
class HealthStatus:
    """
    Immutable health status at a point in time.
    
    Represents overall engine health without exposing internal state.
    """
    
    timestamp_utc: float = field(default_factory=time.time)
    """When this health check was performed."""
    
    is_healthy: bool = True
    """Overall health indicator."""
    
    can_admit: bool = True
    """Can accept new candidate content."""
    
    can_withdraw: bool = True
    """Can withdraw content."""
    
    can_transition: bool = True
    """Can perform state transitions."""
    
    error_count_rolling_60s: int = 0
    """Error count in last 60 seconds."""
    
    warning_count_rolling_60s: int = 0
    """Warning count in last 60 seconds."""
    
    latency_p50_ms: float = 0.0
    """50th percentile transition latency (ms)."""
    
    latency_p99_ms: float = 0.0
    """99th percentile transition latency (ms)."""
    
    @classmethod
    def healthy(cls) -> "HealthStatus":
        """Create a healthy status."""
        return cls()
    
    @classmethod
    def unhealthy(cls, error_count: int = 1, **kwargs) -> "HealthStatus":
        """Create an unhealthy status."""
        return cls(
            is_healthy=False,
            can_admit=False,
            can_withdraw=False,
            can_transition=False,
            error_count_rolling_60s=error_count,
            **kwargs
        )


@dataclass
class Diagnostics:
    """
    Canonical diagnostics collector for Presence Engine.
    
    Responsibilities:
        - Collect metrics during operation
        - Monitor health status
        - Expose observability data
        
    NOT responsible for:
        - Making decisions about admission or transitions
        - Modifying presence state
    """
    
    _metrics: Dict[str, int] = field(default_factory=dict)
    """Metrics counters."""
    
    _transition_latencies_ms: list = field(default_factory=list)
    """Recent transition latencies."""
    
    _errors_60s: list = field(default_factory=list)
    """Error timestamps (last 60 seconds)."""
    
    _warnings_60s: list = field(default_factory=list)
    """Warning timestamps (last 60 seconds)."""
    
    def __post_init__(self) -> None:
        """Initialize metrics."""
        self._metrics["admitted_total"] = 0
        self._metrics["withdrawn_total"] = 0
        self._metrics["transition_count"] = 0
    
    @property
    def metrics(self) -> PresenceMetrics:
        """Get current metrics (immutable)."""
        return PresenceMetrics(
            generation=self._metrics.get("generation", 0),
            admitted_total=self._metrics.get("admitted_total", 0),
            withdrawn_total=self._metrics.get("withdrawn_total", 0),
            active_count=self._metrics.get("active_count", 0),
            fading_count=self._metrics.get("fading_count", 0),
            admission_failures=self._metrics.get("failure_count", 0),
            transition_latencies_ms=tuple(self._transition_latencies_ms[-100:]),
        )
    
    @property
    def health(self) -> HealthStatus:
        """Get current health status."""
        now = time.time()
        
        # Clean old errors/warnings
        self._errors_60s = [t for t in self._errors_60s if now - t < 60]
        self._warnings_60s = [t for t in self._warnings_60s if now - t < 60]
        
        return HealthStatus(
            error_count_rolling_60s=len(self._errors_60s),
            warning_count_rolling_60s=len(self._warnings_60s),
        )
    
    def record_admission(
        self,
        success: bool = True,
        latency_ms: Optional[float] = None,
    ) -> None:
        """Record an admission event."""
        if success:
            self._metrics["admitted_total"] += 1
            if latency_ms is not None:
                self._transition_latencies_ms.append(latency_ms)
                # Keep only recent
                if len(self._transition_latencies_ms) > 1000:
                    self._transition_latencies_ms = self._transition_latencies_ms[-1000:]
        else:
            self._metrics["failure_count"] += 1
    
    def record_withdrawal(
        self,
        latency_ms: Optional[float] = None,
    ) -> None:
        """Record a withdrawal event."""
        self._metrics["withdrawn_total"] += 1
        self._metrics["transition_count"] += 1
        
        if latency_ms is not None:
            self._transition_latencies_ms.append(latency_ms)
    
    def record_transition(
        self,
        latency_ms: float,
    ) -> None:
        """Record a transition event."""
        self._metrics["transition_count"] += 1
        self._transition_latencies_ms.append(latency_ms)
        
        if len(self._transition_latencies_ms) > 1000:
            self._transition_latencies_ms = self._transition_latencies_ms[-1000:]
    
    def record_error(self, now_utc: Optional[float] = None) -> None:
        """Record an error event."""
        if now_utc is None:
            now_utc = time.time()
        self._errors_60s.append(now_utc)
    
    def record_warning(self, now_utc: Optional[float] = None) -> None:
        """Record a warning event."""
        if now_utc is None:
            now_utc = time.time()
        self._warnings_60s.append(now_utc)