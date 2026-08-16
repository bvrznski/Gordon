# Derived Memory Health - Phase 5.1.6 Canonical Implementation
# =============================================================
"""
Health: System health monitoring for derived memory operations.

Purpose:
    Monitor and report on the health of the derivation system.
    
Health Categories:
    - Availability (is derivation service running?)
    - Latency (how long do derivations take?)
    - Error rates (what's failing?)
    - Resource utilization (memory, CPU)
    
Health Laws:
    HEALTH-LAW-001: Health remains inspectable
    HEALTH-LAW-002: Health updates are timely
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
import time


# =============================================================================
# DERIVATION SYSTEM HEALTH - Overall health status
# =============================================================================


@dataclass(frozen=True)
class DerivationHealth:
    """
    Health status for the derivation system.
    
    Fields:
        health_id:           Unique identifier for this health record
        timestamp_utc:       When this health was recorded
        
        # Availability
        is_available:        Is the service available?
        last_heartbeat_utc:  When was the last heartbeat received?
        
        # Performance metrics
        avg_derivation_latency_ms: Average derivation latency (ms)
        max_derivation_latency_ms: Maximum derivation latency (ms)
        
        # Error rates
        total_derivations:   Total derivations processed
        successful_count:    Successfully completed
        failed_count:        Failed completions
        error_rate:          Failed / Total (0.0-1.0)
        
        # Resource utilization
        memory_mb:           Current memory usage (MB)
        cpu_percent:         Current CPU usage (%)
        
        # Queue status
        pending_derivations: Number of derivations waiting
        active_derivations:  Number currently processing
        
    Health Laws:
        HEALTH-LAW-001: Health remains inspectable
    """
    
    health_id: str                          # Unique ID for this record
    
    timestamp_utc: float                    # When recorded
    
    # Availability
    is_available: bool = True               # Service available?
    last_heartbeat_utc: float = field(default_factory=time.time)
    
    # Performance metrics (ms)
    avg_derivation_latency_ms: float = 0.0
    max_derivation_latency_ms: float = 0.0
    
    # Error rates
    total_derivations: int = 0
    successful_count: int = 0
    failed_count: int = 0
    error_rate: float = 0.0                 # Failed / Total
    
    # Resource utilization (MB, %)
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    
    # Queue status
    pending_derivations: int = 0
    active_derivations: int = 0


# =============================================================================
# HEALTH STATUS - Simple health state indicator
# =============================================================================


class HealthStatus:
    """
    Health status indicators.
    
    | Status      | Description                                    |
    |-------------|------------------------------------------------|
    | HEALTHY     : Service is fully operational       |
    | DEGRADED    : Service degraded, some features   |
    | UNHEALTHY   : Service unhealthy, needs attention|
    | UNKNOWN     : Health unknown                    |
    """
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# =============================================================================
# DERIVATION HEALTH BUILDER - Mutable builder for health records
# =============================================================================


class DerivationHealthBuilder:
    """
    Mutable builder for constructing health records.
    
    Allows step-by-step construction before producing immutable record.
    """
    
    def __init__(self):
        """Initialize the builder."""
        self._health_id = f"health:{time.time_ns()}"
        self._timestamp_utc = time.time()
        
        # Availability
        self._is_available = True
        self._last_heartbeat_utc = self._timestamp_utc
        
        # Performance metrics (ms)
        self._avg_derivation_latency_ms = 0.0
        self._max_derivation_latency_ms = 0.0
        
        # Error counts
        self._total_derivations = 0
        self._successful_count = 0
        self._failed_count = 0
        
        # Resource utilization (MB, %)
        self._memory_mb = 0.0
        self._cpu_percent = 0.0
        
        # Queue status
        self._pending_derivations = 0
        self._active_derivations = 0
    
    def set_available(self, is_available: bool) -> "DerivationHealthBuilder":
        """Set the availability status."""
        self._is_available = is_available
        return self
    
    def update_derivation_latency(self, latency_ms: float) -> "DerivationHealthBuilder":
        """Update latency metrics with a new measurement."""
        if self._total_derivations == 0:
            self._avg_derivation_latency_ms = latency_ms
            self._max_derivation_latency_ms = latency_ms
        else:
            # Update running average
            total_time = self._avg_derivation_latency_ms * self._total_derivations
            new_total = total_time + latency_ms
            self._avg_derivation_latency_ms = new_total / (self._total_derivations + 1)
            
            # Update max if needed
            if latency_ms > self._max_derivation_latency_ms:
                self._max_derivation_latency_ms = latency_ms
        
        return self
    
    def record_success(self) -> "DerivationHealthBuilder":
        """Record a successful derivation."""
        self._total_derivations += 1
        self._successful_count += 1
        return self
    
    def record_failure(self) -> "DerivationHealthBuilder":
        """Record a failed derivation."""
        self._total_derivations += 1
        self._failed_count += 1
        return self
    
    def update_memory_mb(self, memory_mb: float) -> "DerivationHealthBuilder":
        """Update current memory usage (MB)."""
        self._memory_mb = memory_mb
        return self
    
    def update_cpu_percent(self, cpu_percent: float) -> "DerivationHealthBuilder":
        """Update current CPU usage (%)."""
        self._cpu_percent = cpu_percent
        return self
    
    def set_pending_derivations(self, count: int) -> "DerivationHealthBuilder":
        """Set the pending derivation count."""
        self._pending_derivations = max(0, count)
        return self
    
    def set_active_derivations(self, count: int) -> "DerivationHealthBuilder":
        """Set the active derivation count."""
        self._active_derivations = max(0, count)
        return self
    
    def update_heartbeat(self) -> "DerivationHealthBuilder":
        """Update the last heartbeat time."""
        self._last_heartbeat_utc = time.time()
        return self
    
    def build(self) -> DerivationHealth:
        """
        Build an immutable DerivationHealth from this builder.
        
        Returns:
            New DerivationHealth with all settings applied
        """
        # Calculate error rate
        if self._total_derivations > 0:
            error_rate = self._failed_count / self._total_derivations
        else:
            error_rate = 0.0
        
        return DerivationHealth(
            health_id=self._health_id,
            timestamp_utc=time.time(),
            is_available=self._is_available,
            last_heartbeat_utc=self._last_heartbeat_utc,
            avg_derivation_latency_ms=self._avg_derivation_latency_ms,
            max_derivation_latency_ms=self._max_derivation_latency_ms,
            total_derivations=self._total_derivations,
            successful_count=self._successful_count,
            failed_count=self._failed_count,
            error_rate=error_rate,
            memory_mb=self._memory_mb,
            cpu_percent=self._cpu_percent,
            pending_derivations=self._pending_derivations,
            active_derivations=self._active_derivations,
        )


# =============================================================================
# HEALTH CHECKER - Validates system health
# =============================================================================


class DerivationHealthChecker:
    """
    Health checker for derivation system.
    
    Evaluates current health status based on metrics.
    """
    
    def __init__(self):
        """Initialize the checker."""
        self._check_count = 0
    
    def check_health(
        self,
        health: DerivationHealth,
    ) -> Tuple[HealthStatus, List[str]]:
        """
        Check the current health status.
        
        Args:
            health: Current health record
            
        Returns:
            Tuple of (status, issues)
            
        Health Evaluation:
            - Available and low error rate = HEALTHY
            - Some degradation = DEGRADED
            - Critical issues = UNHEALTHY
        """
        self._check_count += 1
        
        issues = []
        
        # Check availability
        if not health.is_available:
            return (HealthStatus.UNHEALTHY, ["Service unavailable"])
        
        # Check error rate
        if health.error_rate > 0.5:
            issues.append(f"High error rate: {health.error_rate:.1%}")
        elif health.error_rate > 0.2:
            issues.append(f"Elevated error rate: {health.error_rate:.1%}")
        
        # Check latency (assuming threshold of 1000ms)
        if health.max_derivation_latency_ms > 5000:
            issues.append(f"High max latency: {health.max_derivation_latency_ms:.0f}ms")
        elif health.max_derivation_latency_ms > 2000:
            issues.append(f"Elevated max latency: {health.max_derivation_latency_ms:.0f}ms")
        
        # Check memory (assuming threshold of 4GB)
        if health.memory_mb > 4096:
            issues.append(f"High memory usage: {health.memory_mb:.0f}MB")
        
        # Determine status
        if len(issues) == 0:
            status = HealthStatus.HEALTHY
        elif len(issues) <= 2:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY
        
        return (status, issues)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get checker statistics."""
        return {
            "check_count": self._check_count,
        }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Health record
    "DerivationHealth",
    
    # Status
    "HealthStatus",
    
    # Builder
    "DerivationHealthBuilder",
    
    # Checker
    "DerivationHealthChecker",
]