# Integration Health - Phase 5.1.7 System Health Monitoring
# ==========================================================

"""
Memory Integration Health: Monitors the health and availability of integration endpoints.

Health monitoring provides:
    - Real-time availability status
    - Latency metrics for communication
    - Error rates and failure patterns
    - Contract compatibility status
    - Session integrity verification

Health Laws:
    HEALTH-LAW-001: Health must be continuously monitored
    HEALTH-LAW-002: Health status must be publicly available
    HEALTH-LAW-003: Health metrics must be measurable
    HEALTH-LAW-004: Health failures must be observable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# HEALTH STATES
# =============================================================================


class HealthState(Enum):
    """
    States of integration health.
    
    | State      | Description                                      |
    |------------|--------------------------------------------------|
    | HEALTHY    | Fully operational                                |
    | DEGRADED   | Operational but with degraded performance        |
    | ERROR      | Experiencing errors                              |
    | UNAVAILABLE| Not available                                    |
    """
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


# =============================================================================
# LATENCY METRICS
# =============================================================================


@dataclass(frozen=True)
class LatencyMetrics:
    """
    Metrics about communication latency.
    
    Fields:
        p50_ms:       50th percentile latency (median)
        p95_ms:       95th percentile latency
        p99_ms:       99th percentile latency
        
        min_ms:       Minimum observed latency
        max_ms:       Maximum observed latency
        avg_ms:       Average latency
        
        window_start: When did this measurement window start?
    """
    
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0
    
    window_start: float = field(default_factory=time.time)
    
    def is_acceptable(self, threshold_ms: float = 1000.0) -> bool:
        """Check if latency is within acceptable threshold."""
        return self.p95_ms <= threshold_ms


# =============================================================================
# ERROR METRICS
# =============================================================================


@dataclass(frozen=True)
class ErrorMetrics:
    """
    Metrics about errors in communication.
    
    Fields:
        total_errors:      Total number of errors in window
        error_rate:        Rate of errors (0.0-1.0)
        
        timeout_count:     Number of timeouts
        contract_mismatch: Number of contract mismatches
        auth_failures:     Number of authorization failures
        
        last_error_time:   When was the last error?
    """
    
    total_errors: int = 0
    error_rate: float = 0.0
    
    timeout_count: int = 0
    contract_mismatch: int = 0
    auth_failures: int = 0
    
    last_error_time: Optional[float] = None


# =============================================================================
# INTEGRATION HEALTH STATUS
# =============================================================================


@dataclass(frozen=True)
class IntegrationHealthStatus:
    """
    Health status for an integration endpoint.
    
    Fields:
        integration_type: Which integration is this?
        
        # State
        state:           Current health state
        last_check_utc:  When was health last checked?
        
        # Metrics
        latency:         Latency metrics
        errors:          Error metrics
        
        # Contract status
        contract_valid:  Is the current contract valid?
        version_compatible: Are versions compatible?
        
        # Diagnostics
        message:         Human-readable status message
        details:         Additional diagnostic information
    """
    
    integration_type: str                   # e.g., "perception", "workspace"
    
    # State
    state: HealthState = HealthState.HEALTHY
    last_check_utc: float = field(default_factory=time.time)
    
    # Metrics
    latency: LatencyMetrics = field(default_factory=LatencyMetrics)
    errors: ErrorMetrics = field(default_factory=ErrorMetrics)
    
    # Contract status
    contract_valid: bool = True
    version_compatible: bool = True
    
    # Diagnostics
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def is_healthy(self) -> bool:
        """Check if the integration is healthy."""
        return self.state == HealthState.HEALTHY


# =============================================================================
# INTEGRATION HEALTH CHECKER
# =============================================================================


class IntegrationHealthChecker:
    """
    Checker for integration health status.
    
    Provides health monitoring, metrics collection,
    and failure detection for all integrations.
    
    Usage:
        checker = IntegrationHealthChecker()
        
        # Register an integration to monitor
        checker.register_integration("perception")
        
        # Update health on each operation
        result = checker.record_success("perception", latency_ms=50.0)
        
        # Get current health status
        status = checker.get_status("perception")
    """
    
    def __init__(self, max_error_rate: float = 0.1):
        self._status: Dict[str, IntegrationHealthStatus] = {}
        self._latency_windows: Dict[str, List[float]] = {}
        self._error_windows: Dict[str, List[Tuple[float, str]]] = {}
        self.max_error_rate = max_error_rate
        self.window_size_seconds = 300  # 5 minutes
    
    def register_integration(self, integration_type: str) -> None:
        """Register an integration for health monitoring."""
        if integration_type not in self._status:
            self._status[integration_type] = IntegrationHealthStatus(
                integration_type=integration_type
            )
            self._latency_windows[integration_type] = []
            self._error_windows[integration_type] = []
    
    def record_success(self, integration_type: str, latency_ms: float) -> None:
        """Record a successful operation."""
        if integration_type not in self._status:
            self.register_integration(integration_type)
        
        # Record latency
        window = self._latency_windows[integration_type]
        window.append(latency_ms)
        
        # Keep only recent measurements
        cutoff = time.time() - self.window_size_seconds
        window[:] = [l for l in window if l > cutoff]
        
        self._update_status(integration_type)
    
    def record_error(self, integration_type: str, error_type: str) -> None:
        """Record an operation failure."""
        if integration_type not in self._status:
            self.register_integration(integration_type)
        
        # Record error
        window = self._error_windows[integration_type]
        window.append((time.time(), error_type))
        
        # Keep only recent measurements
        cutoff = time.time() - self.window_size_seconds
        window[:] = [(t, e) for t, e in window if t > cutoff]
        
        self._update_status(integration_type)
    
    def record_contract_mismatch(self, integration_type: str) -> None:
        """Record a contract compatibility issue."""
        if integration_type not in self._status:
            self.register_integration(integration_type)
        
        status = self._status[integration_type]
        status = dataclass_replace(status, 
                                   contract_valid=False,
                                   state=HealthState.ERROR,
                                   message="Contract mismatch detected")
        self._status[integration_type] = status
    
    def record_timeout(self, integration_type: str) -> None:
        """Record a timeout event."""
        if integration_type not in self._status:
            self.register_integration(integration_type)
        
        # Record as error
        self.record_error(integration_type, "timeout")
    
    def get_status(self, integration_type: str) -> Optional[IntegrationHealthStatus]:
        """Get the current health status for an integration."""
        if integration_type not in self._status:
            return None
        
        # Update before returning
        self._update_status(integration_type)
        return dict(self._status).get(integration_type)
    
    def get_all_statuses(self) -> Dict[str, IntegrationHealthStatus]:
        """Get health status for all integrations."""
        for integration in list(self._status.keys()):
            self._update_status(integration)
        return dict(self._status)
    
    def _update_status(self, integration_type: str) -> None:
        """Update the health status for an integration."""
        if integration_type not in self._status:
            return
        
        # Get current window data
        latencies = self._latency_windows.get(integration_type, [])
        errors = self._error_windows.get(integration_type, [])
        
        # Calculate metrics
        latency_metrics = LatencyMetrics()
        if latencies:
            sorted_lat = sorted(latencies)
            n = len(sorted_lat)
            
            latency_metrics.p50_ms = sorted_lat[n // 2] if n > 0 else 0.0
            latency_metrics.p95_ms = sorted_lat[int(n * 0.95)] if n > 0 else 0.0
            latency_metrics.p99_ms = sorted_lat[min(int(n * 0.99), n - 1)] if n > 0 else 0.0
            
            latency_metrics.min_ms = min(latencies)
            latency_metrics.max_ms = max(latencies)
            latency_metrics.avg_ms = sum(latencies) / len(latencies)
        
        # Calculate error metrics
        error_metrics = ErrorMetrics()
        if errors:
            cutoff = time.time() - self.window_size_seconds
            recent_errors = [(t, e) for t, e in errors if t > cutoff]
            
            error_metrics.total_errors = len(recent_errors)
            error_metrics.error_rate = len(recent_errors) / max(len(latencies), 1)
            
            error_metrics.timeout_count = sum(1 for _, e in recent_errors if "timeout" in e.lower())
        
        # Determine state
        current_status = self._status[integration_type]
        
        if error_metrics.error_rate > self.max_error_rate:
            new_state = HealthState.ERROR
            message = f"High error rate: {error_metrics.error_rate:.1%}"
        elif not current_status.version_compatible or not current_status.contract_valid:
            new_state = HealthState.DEGRADED
            message = "Compatibility issue detected"
        else:
            new_state = HealthState.HEALTHY
            message = ""
        
        # Update status
        new_status = dataclass_replace(current_status,
                                       state=new_state,
                                       latency=latency_metrics,
                                       errors=error_metrics,
                                       message=message)
        self._status[integration_type] = new_status


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace (Python 3.7 compatible)."""
    fields = instance.__dataclass_fields__
    return type(instance)(
        **{f.name: kwargs.get(f.name, getattr(instance, f.name)) 
           for f in fields.values()}
    )