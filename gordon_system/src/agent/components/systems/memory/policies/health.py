# Memory Policy Health - Phase 5.1.5 Canonical Health Monitoring Module
# ======================================================================
"""
Memory Policy Health: Health status and diagnostics for policy evaluation.

Health metrics monitor:
    availability      : Is the policy available to evaluate?
    latency           : How fast does it evaluate?
    consistency       : Are decisions consistent?
    errors            : What errors have occurred?

Health Laws:
    HEALTH-LAW-001: Health is monitored but never affects evaluation
    HEALTH-LAW-002: Health metrics are deterministic and reproducible
    HEALTH-LAW-003: Health data is preserved for analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
from enum import Enum


# =============================================================================
# POLICY HEALTH STATUS - Current health state of a policy
# =============================================================================


class PolicyHealthStatus(Enum):
    """
    Health status of a memory policy.
    
    | Status      | Description                                   |
    |-------------|-----------------------------------------------|
    | HEALTHY     : Policy is fully functional
    | DEGRADED    : Policy is functional but with issues
    | UNAVAILABLE : Policy cannot evaluate proposals
    | ERROR       : Policy encountered an error
    """
    
    HEALTHY = "healthy"         # Fully functional
    DEGRADED = "degraded"       # Functional but with issues
    UNAVAILABLE = "unavailable" # Cannot evaluate
    ERROR = "error"             # Encountered an error


# =============================================================================
# POLICY HEALTH RECORD - Current health state of a policy
# =============================================================================


@dataclass(frozen=True)
class PolicyHealth:
    """
    Health record for a memory policy.
    
    Fields:
        policy_id:           ID of the policy being monitored
        
        # Status
        status:              Current health status
        last_status_change:  When did the status last change?
        
        # Availability
        available:           Is the policy currently available?
        uptime_seconds:      Total uptime (seconds)
        downtime_seconds:    Total downtime (seconds)
        
        # Performance metrics
        avg_evaluation_latency_ms: Average evaluation latency (ms)
        max_evaluation_latency_ms: Maximum observed latency (ms)
        min_evaluation_latency_ms: Minimum observed latency (ms)
        
        # Reliability
        total_evaluations:   Total evaluations attempted
        successful_evaluations: Successful evaluations
        failed_evaluations:  Failed evaluations
        
        # Errors and warnings
        error_count:         Number of errors encountered
        warning_count:       Number of warnings encountered
        last_error:          Description of the last error (if any)
        
        # Diagnostics
        last_evaluation_utc: When was the last evaluation?
    """
    
    policy_id: str                              # ID of the policy
    
    # Status
    status: PolicyHealthStatus = PolicyHealthStatus.HEALTHY
    last_status_change: float = field(default_factory=time.time)
    
    # Availability
    available: bool = True
    uptime_seconds: float = 0.0
    downtime_seconds: float = 0.0
    
    # Performance metrics
    avg_evaluation_latency_ms: float = 0.0
    max_evaluation_latency_ms: float = 0.0
    min_evaluation_latency_ms: Optional[float] = None
    
    # Reliability
    total_evaluations: int = 0
    successful_evaluations: int = 0
    failed_evaluations: int = 0
    
    # Errors and warnings
    error_count: int = 0
    warning_count: int = 0
    last_error: Optional[str] = None
    
    # Diagnostics
    last_evaluation_utc: float = field(default_factory=time.time)
    
    def record_success(self, latency_ms: float) -> "PolicyHealth":
        """Record a successful evaluation."""
        return self._update_health(
            success=True,
            latency_ms=latency_ms,
            error=None,
        )
    
    def record_failure(self, latency_ms: float, error: str) -> "PolicyHealth":
        """Record a failed evaluation."""
        return self._update_health(
            success=False,
            latency_ms=latency_ms,
            error=error,
        )
    
    def set_unavailable(self, reason: Optional[str] = None) -> "PolicyHealth":
        """Mark policy as unavailable."""
        return PolicyHealth(
            policy_id=self.policy_id,
            status=PolicyHealthStatus.UNAVAILABLE,
            last_status_change=time.time(),
            available=False,
            uptime_seconds=self.uptime_seconds,
            downtime_seconds=self.downtime_seconds + (time.time() - self.last_evaluation_utc),
            avg_evaluation_latency_ms=self.avg_evaluation_latency_ms,
            max_evaluation_latency_ms=self.max_evaluation_latency_ms,
            min_evaluation_latency_ms=self.min_evaluation_latency_ms,
            total_evaluations=self.total_evaluations,
            successful_evaluations=self.successful_evaluations,
            failed_evaluations=self.failed_evaluations,
            error_count=self.error_count + (1 if reason else 0),
            warning_count=self.warning_count,
            last_error=reason,
            last_evaluation_utc=time.time(),
        )
    
    def set_available(self) -> "PolicyHealth":
        """Mark policy as available."""
        return PolicyHealth(
            policy_id=self.policy_id,
            status=PolicyHealthStatus.HEALTHY,
            last_status_change=time.time(),
            available=True,
            uptime_seconds=self.uptime_seconds + (time.time() - self.last_evaluation_utc),
            downtime_seconds=self.downtime_seconds,
            avg_evaluation_latency_ms=self.avg_evaluation_latency_ms,
            max_evaluation_latency_ms=self.max_evaluation_latency_ms,
            min_evaluation_latency_ms=self.min_evaluation_latency_ms,
            total_evaluations=self.total_evaluations,
            successful_evaluations=self.successful_evaluations,
            failed_evaluations=self.failed_evaluations,
            error_count=self.error_count,
            warning_count=self.warning_count,
            last_error=None,
            last_evaluation_utc=time.time(),
        )
    
    def get_availability_rate(self) -> float:
        """Get availability rate (0.0-1.0)."""
        if self.total_evaluations == 0:
            return 1.0
        return self.successful_evaluations / self.total_evaluations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health record to dictionary representation."""
        return {
            "policy_id": self.policy_id,
            "status": self.status.value,
            "last_status_change": self.last_status_change,
            "available": self.available,
            "uptime_seconds": self.uptime_seconds,
            "downtime_seconds": self.downtime_seconds,
            "avg_evaluation_latency_ms": self.avg_evaluation_latency_ms,
            "max_evaluation_latency_ms": self.max_evaluation_latency_ms,
            "min_evaluation_latency_ms": self.min_evaluation_latency_ms,
            "total_evaluations": self.total_evaluations,
            "successful_evaluations": self.successful_evaluations,
            "failed_evaluations": self.failed_evaluations,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "last_error": self.last_error,
            "last_evaluation_utc": self.last_evaluation_utc,
        }
    
    def _update_health(
        self,
        success: bool,
        latency_ms: float,
        error: Optional[str],
    ) -> "PolicyHealth":
        """Internal method to update health after an evaluation."""
        total = self.total_evaluations + 1
        
        # Update latency metrics (running average)
        new_avg_latency = (
            (self.avg_evaluation_latency_ms * self.total_evaluations + latency_ms) / total
        )
        new_max_latency = max(self.max_evaluation_latency_ms, latency_ms)
        new_min_latency = (
            min(self.min_evaluation_latency_ms or float("inf"), latency_ms)
            if self.min_evaluation_latency_ms is not None
            else latency_ms
        )
        
        return PolicyHealth(
            policy_id=self.policy_id,
            status=PolicyHealthStatus.HEALTHY if success else PolicyHealthStatus.ERROR,
            last_status_change=time.time(),
            available=success,
            uptime_seconds=self.uptime_seconds + (1 if success else 0),
            downtime_seconds=self.downtime_seconds + (0 if success else 1),
            avg_evaluation_latency_ms=new_avg_latency,
            max_evaluation_latency_ms=new_max_latency,
            min_evaluation_latency_ms=new_min_latency,
            total_evaluations=total,
            successful_evaluations=self.successful_evaluations + (1 if success else 0),
            failed_evaluations=self.failed_evaluations + (0 if success else 1),
            error_count=self.error_count + (1 if error else 0),
            warning_count=self.warning_count,
            last_error=error,
            last_evaluation_utc=time.time(),
        )


# =============================================================================
# POLICY HEALTH MONITOR - Monitor health of multiple policies
# =============================================================================


class PolicyHealthMonitor:
    """
    Monitor and aggregate health status across multiple policies.
    
    Maintains a comprehensive view of system health for all memory policies.
    """
    
    def __init__(self):
        """Initialize the health monitor."""
        self._health_records: Dict[str, PolicyHealth] = {}
        self._start_time_utc = time.time()
        
    def get_or_create_health_record(self, policy_id: str) -> PolicyHealth:
        """Get or create a health record for a policy."""
        if policy_id not in self._health_records:
            self._health_records[policy_id] = PolicyHealth(policy_id=policy_id)
        return self._health_records[policy_id]
    
    def record_policy_evaluation(
        self,
        policy_id: str,
        latency_ms: float,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """
        Record a policy evaluation result.
        
        Args:
            policy_id: Which policy evaluated?
            latency_ms: How long did it take? (ms)
            success: Was the evaluation successful?
            error: Error message if failed
        """
        health = self.get_or_create_health_record(policy_id)
        if success:
            self._health_records[policy_id] = health.record_success(latency_ms)
        else:
            self._health_records[policy_id] = health.record_failure(latency_ms, error or "Unknown error")
    
    def set_policy_unavailable(self, policy_id: str, reason: Optional[str] = None) -> None:
        """Mark a policy as unavailable."""
        health = self.get_or_create_health_record(policy_id)
        self._health_records[policy_id] = health.set_unavailable(reason)
    
    def set_policy_available(self, policy_id: str) -> None:
        """Mark a policy as available."""
        health = self.get_or_create_health_record(policy_id)
        self._health_records[policy_id] = health.set_available()
    
    def get_policy_health(self, policy_id: str) -> Optional[PolicyHealth]:
        """Get the health record for a specific policy."""
        return self._health_records.get(policy_id)
    
    def get_all_policies_health(self) -> Dict[str, PolicyHealth]:
        """Get health records for all policies."""
        return dict(self._health_records)
    
    def get_system_health_status(self) -> PolicyHealthStatus:
        """
        Get the overall system health status.
        
        Returns the most severe status across all policies.
        """
        if not self._health_records:
            return PolicyHealthStatus.HEALTHY
        
        # Check for any unavailable or error policies
        has_unavailable = any(
            h.status == PolicyHealthStatus.UNAVAILABLE for h in self._health_records.values()
        )
        has_error = any(h.error_count > 0 for h in self._health_records.values())
        has_degraded = any(
            h.status == PolicyHealthStatus.DEGRADED or
            (h.get_availability_rate() < 0.95 and h.total_evaluations > 10)
            for h in self._health_records.values()
        )
        
        if has_unavailable:
            return PolicyHealthStatus.UNAVAILABLE
        elif has_error:
            return PolicyHealthStatus.ERROR
        elif has_degraded:
            return PolicyHealthStatus.DEGRADED
        else:
            return PolicyHealthStatus.HEALTHY
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get a summary of system health across all policies."""
        policies = self.get_all_policies_health()
        
        total_evaluations = sum(h.total_evaluations for h in policies.values())
        successful = sum(h.successful_evaluations for h in policies.values())
        failed = sum(h.failed_evaluations for h in policies.values())
        
        avg_latency = 0.0
        max_latency = 0.0
        
        for health in policies.values():
            if health.total_evaluations > 0:
                # Weight average by evaluations
                weighted = health.avg_evaluation_latency_ms * health.total_evaluations
                avg_latency += weighted
        
        if total_evaluations > 0:
            avg_latency /= total_evaluations
        
        return {
            "timestamp_utc": time.time(),
            "start_time_utc": self._start_time_utc,
            "uptime_seconds": time.time() - self._start_time_utc,
            "total_policies_monitored": len(policies),
            "system_status": self.get_system_health_status().value,
            "summary": {
                "total_evaluations": total_evaluations,
                "successful_evaluations": successful,
                "failed_evaluations": failed,
                "success_rate": successful / total_evaluations if total_evaluations > 0 else 1.0,
                "avg_evaluation_latency_ms": avg_latency,
                "policies_by_status": {
                    "healthy": sum(1 for h in policies.values() if h.status == PolicyHealthStatus.HEALTHY),
                    "degraded": sum(1 for h in policies.values() if h.status == PolicyHealthStatus.DEGRADED),
                    "unavailable": sum(1 for h in policies.values() if h.status == PolicyHealthStatus.UNAVAILABLE),
                    "error": sum(1 for h in policies.values() if h.status == PolicyHealthStatus.ERROR),
                },
            },
            "policies": {pid: h.to_dict() for pid, h in policies.items()},
        }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Health status enum
    "PolicyHealthStatus",
    
    # Health record
    "PolicyHealth",
    
    # Monitor
    "PolicyHealthMonitor",
]