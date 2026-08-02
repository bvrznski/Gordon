# Core Health Projection Model
# ============================

"""
Health projection and monitoring for runtime entities.

This module provides:
- Distinct health dimensions (liveness, readiness, health, integrity)
- Deterministic health aggregation
- Health state projections as derived values
- Degradation tracking
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum, auto
import time


# =============================================================================
# Health Status Values
# =============================================================================

class HealthStatus(Enum):
    """
    Health status for runtime entities.
    
    The health model distinguishes between:
    - Liveness: Is the entity still responsive?
    - Readiness: Is the entity available for use?
    - Health: Is operating within acceptable conditions?
    - Integrity: Are structural contracts satisfied?
    
    Status values support at least:
        UNKNOWN, STARTING, HEALTHY, DEGRADED, UNHEALTHY, FAILED, STOPPING, STOPPED
    """
    
    # Initial states
    UNKNOWN = "unknown"         # Unknown health (not yet evaluated)
    STARTING = "starting"       # Entity is starting up
    
    # Valid operational states
    HEALTHY = "healthy"         # Fully operational
    DEGRADED = "degraded"       # Operational with reduced capability
    UNHEALTHY = "unhealthy"     # Not operating within acceptable conditions
    
    # Terminal states
    FAILED = "failed"           # Failed and not recoverable
    STOPPING = "stopping"       # Being stopped (not a failure)
    STOPPED = "stopped"         # Stopped intentionally (not a failure)


# =============================================================================
# Health Projections
# =============================================================================

@dataclass(frozen=True)
class HealthProjection:
    """
    A health projection for an entity.
    
    A projection is DERIVED from authoritative state, not a competing authority.
    It answers: "How capable is this entity of continuing its intended role?"
    
    The key distinction: health projections MUST NOT mutate authoritative state.
    
    Usage:
        # Get current projection (always derived from authoritative state)
        projection = runtime.get_health_projection(entity_id)
        
        if projection.is_healthy:
            # Entity can be used normally
            pass
        
        elif projection.is_degraded:
            # Use with reduced capability
            pass
        
        else:
            # Handle unhealthy entity
            pass
    """
    
    subject: str  # Entity identifier being projected
    
    # Overall status (derived from dimension states)
    overall_status: HealthStatus
    
    # Dimensional health (can be different per dimension)
    liveness: HealthStatus = HealthStatus.UNKNOWN
    readiness: HealthStatus = HealthStatus.UNKNOWN
    health: HealthStatus = HealthStatus.UNKNOWN
    integrity: HealthStatus = HealthStatus.UNKNOWN
    
    # Degradation tracking
    degradation_reasons: List[str] = field(default_factory=list)  # Why degraded?
    
    # Check results summary
    failed_checks: List[str] = field(default_factory=list)
    warning_checks: List[str] = field(default_factory=list)
    
    # Timestamps
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Source information
    source_state_version: int = 0  # What state version this projection is based on
    
    @property
    def is_healthy(self) -> bool:
        """Check if overall status is healthy."""
        return self.overall_status == HealthStatus.HEALTHY
    
    @property
    def is_degraded(self) -> bool:
        """Check if overall status is degraded."""
        return self.overall_status == HealthStatus.DEGRADED
    
    @property
    def is_unhealthy(self) -> bool:
        """Check if overall status is unhealthy or failed."""
        return self.overall_status in (HealthStatus.UNHEALTHY, HealthStatus.FAILED)
    
    @property
    def is_stopped_intentionally(self) -> bool:
        """Check if entity was intentionally stopped."""
        return self.overall_status == HealthStatus.STOPPED
    
    @property
    def has_failures(self) -> bool:
        """Check if any checks failed."""
        return len(self.failed_checks) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were recorded."""
        return len(self.warning_checks) > 0
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        import json
        
        return {
            "subject": self.subject,
            "overall_status": self.overall_status.value,
            "liveness": self.liveness.value,
            "readiness": self.readiness.value,
            "health": self.health.value,
            "integrity": self.integrity.value,
            "degradation_reasons": self.degradation_reasons,
            "failed_checks": self.failed_checks,
            "warning_checks": self.warning_checks,
            "evaluated_at_utc": self.evaluated_at_utc,
            "monotonic_time": self.monotonic_time,
            "source_state_version": self.source_state_version
        }
    
    @classmethod
    def create(
        cls,
        subject: str,
        liveness: HealthStatus = HealthStatus.UNKNOWN,
        readiness: HealthStatus = HealthStatus.UNKNOWN,
        health: HealthStatus = HealthStatus.UNKNOWN,
        integrity: HealthStatus = HealthStatus.UNKNOWN,
        degradation_reasons: Optional[List[str]] = None,
        failed_checks: Optional[List[str]] = None,
        warning_checks: Optional[List[str]] = None,
        source_state_version: int = 0
    ) -> "HealthProjection":
        """
        Create a new health projection.
        
        Args:
            subject: Entity identifier
            liveness: Liveness status
            readiness: Readiness status
            health: Health status
            integrity: Integrity status
            degradation_reasons: Why the entity might be degraded
            failed_checks: List of check names that failed
            warning_checks: List of check names with warnings
            source_state_version: State version this projection is based on
            
        Returns:
            A new HealthProjection instance
        """
        # Determine overall status from dimension states
        
        # Intentionally stopped should not be reported as failure
        if health == HealthStatus.STOPPED or integrity == HealthStatus.STOPPED:
            overall = HealthStatus.STOPPED
        
        # Check for failures first
        elif health == HealthStatus.UNHEALTHY or health == HealthStatus.FAILED:
            overall = HealthStatus.UNHEALTHY
        
        elif health == HealthStatus.DEGRADED:
            overall = HealthStatus.DEGRADED
        
        elif (liveness in (HealthStatus.UNKNOWN, HealthStatus.STARTING) and
              readiness == HealthStatus.UNKNOWN):
            overall = HealthStatus.STARTING
        
        # All dimensions healthy -> overall healthy
        elif all(s == HealthStatus.HEALTHY for s in [liveness, readiness, health, integrity]):
            overall = HealthStatus.HEALTHY
        
        else:
            # Mixed or unknown state - be conservative
            overall = HealthStatus.UNKNOWN
        
        return cls(
            subject=subject,
            overall_status=overall,
            liveness=liveness,
            readiness=readiness,
            health=health,
            integrity=integrity,
            degradation_reasons=degradation_reasons or [],
            failed_checks=failed_checks or [],
            warning_checks=warning_checks or [],
            source_state_version=source_state_version
        )
    
    @classmethod
    def healthy(cls, subject: str) -> "HealthProjection":
        """Create a healthy projection."""
        return cls.create(subject=subject)
    
    @classmethod
    def degraded(
        cls,
        subject: str,
        reasons: Optional[List[str]] = None,
        source_state_version: int = 0
    ) -> "HealthProjection":
        """Create a degraded projection."""
        return cls.create(
            subject=subject,
            health=HealthStatus.DEGRADED,
            degradation_reasons=reasons or [],
            source_state_version=source_state_version
        )
    
    @classmethod
    def unhealthy(
        cls,
        subject: str,
        failed_checks: Optional[List[str]] = None,
        source_state_version: int = 0
    ) -> "HealthProjection":
        """Create an unhealthy projection."""
        return cls.create(
            subject=subject,
            health=HealthStatus.UNHEALTHY,
            failed_checks=failed_checks or [],
            source_state_version=source_state_version
        )
    
    @classmethod
    def stopped(cls, subject: str) -> "HealthProjection":
        """Create a stopped (intentional) projection."""
        return cls.create(
            subject=subject,
            health=HealthStatus.STOPPED,
            liveness=HealthStatus.STOPPED,
            readiness=HealthStatus.STOPPED,
            integrity=HealthStatus.STOPPED
        )
    
    @classmethod
    def from_failed_checks(
        cls,
        subject: str,
        failed_check_results: List["ProbeResult"],
        source_state_version: int = 0
    ) -> "HealthProjection":
        """
        Create a projection from probe results.
        
        Args:
            subject: Entity identifier
            failed_check_results: List of ProbeResult with FAILED status
            source_state_version: State version this projection is based on
            
        Returns:
            A new HealthProjection instance
        """
        failed_names = [r.name for r in failed_check_results if not r.passed]
        
        # Determine overall status from probe severities and blocking status
        has_critical = any(r.is_blocking for r in failed_check_results)
        severity_sum = sum(1 for r in failed_check_results 
                          if r.severity == ProbeSeverity.ERROR or r.severity == ProbeSeverity.CRITICAL)
        
        health_status = (
            HealthStatus.UNHEALTHY if (has_critical or severity_sum > 0) else
            HealthStatus.DEGRADED if len(failed_check_results) > 0 else
            HealthStatus.HEALTHY
        )
        
        return cls.create(
            subject=subject,
            health=health_status,
            failed_checks=failed_names,
            source_state_version=source_state_version
        )


# =============================================================================
# Probe Result and Results
# =============================================================================

class ProbeDimension(Enum):
    """Probe dimension classification."""
    
    LIVENESS = "liveness"       # Is the entity still responsive?
    READINESS = "readiness"     # Is it available for use?
    HEALTH = "health"           # Operating within acceptable conditions?
    INTEGRITY = "integrity"     # Structural contracts satisfied?


class ProbeSeverity(Enum):
    """Probe severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    @property
    def is_blocking(self) -> bool:
        return self in (ProbeSeverity.ERROR, ProbeSeverity.CRITICAL)
    
    @property
    def is_error(self) -> bool:
        return self in (ProbeSeverity.ERROR, ProbeSeverity.CRITICAL)


@dataclass(frozen=True)
class ProbeResult:
    """
    Result of a health or integrity probe.
    
    Probes are read-only operations that evaluate state.
    They MUST NOT mutate the entity they're probing.
    """
    
    name: str  # Unique probe identifier
    subject: str  # Entity being probed
    
    dimension: ProbeDimension  # What this probe checks
    
    passed: bool = False  # Did the check pass?
    severity: ProbeSeverity = ProbeSeverity.INFO
    
    summary: str = ""  # Human-readable summary
    evidence: Dict[str, Any] = field(default_factory=dict)  # Supporting data
    
    blocking: bool = False  # Does failure block normal operation?
    
    started_at: float = field(default_factory=time.time)
    completed_at: float = field(default_factory=time.time)
    
    remediation: Optional[str] = None
    valid_until: Optional[float] = None  # When result expires
    
    @property
    def duration(self) -> float:
        """Get probe execution duration."""
        return self.completed_at - self.started_at
    
    @classmethod
    def pass_result(
        cls,
        name: str,
        subject: str,
        dimension: ProbeDimension,
        summary: str = "",
        **evidence
    ) -> "ProbeResult":
        """Create a passing probe result."""
        return cls(
            name=name,
            subject=subject,
            dimension=dimension,
            passed=True,
            severity=ProbeSeverity.INFO,
            summary=summary or f"{name} check passed",
            evidence=evidence,
            blocking=False
        )
    
    @classmethod
    def fail_result(
        cls,
        name: str,
        subject: str,
        dimension: ProbeDimension,
        severity: ProbeSeverity = ProbeSeverity.ERROR,
        blocking: bool = True,
        summary: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None
    ) -> "ProbeResult":
        """Create a failing probe result."""
        return cls(
            name=name,
            subject=subject,
            dimension=dimension,
            passed=False,
            severity=severity,
            summary=summary or f"{name} check failed",
            evidence=evidence or {},
            blocking=blocking,
            remediation=remediation
        )


# =============================================================================
# Health Check Contract
# =============================================================================

class HealthChecker:
    """
    Contract for health checking implementations.
    
    Implementations should be:
    - Idempotent (can call multiple times safely)
    - Side-effect free (don't modify entity state)
    - Deterministic (same inputs -> same outputs)
    - Fast (no blocking I/O unless timeout允许)
    
    Usage:
        class MyHealthChecker(HealthChecker):
            async def check(self, subject: str) -> ProbeResult:
                # Check health of 'subject'
                return ProbeResult.pass_result(...)
        
        checker = MyHealthChecker()
        result = await checker.check("entity_123")
    """
    
    @property
    def name(self) -> str:
        """Return unique name for this checker."""
        return type(self).__name__
    
    async def check(self, subject: str) -> ProbeResult:
        """
        Execute the health check.
        
        Args:
            subject: Entity identifier to check
            
        Returns:
            ProbeResult with check outcome
            
        Raises:
            TimeoutError: If check exceeds timeout
            CancelledError: If check was cancelled
        """
        raise NotImplementedError


# =============================================================================
# Health Aggregation
# =============================================================================

class HealthAggregator:
    """
    Deterministic health aggregation logic.
    
    Aggregates multiple probe results into a single projection.
    Follows explicit rules rather than "worst enum wins" logic.
    """
    
    def __init__(self) -> None:
        self._state: Dict[str, List[ProbeResult]] = {}
    
    def add_results(self, subject: str, results: List[ProbeResult]) -> None:
        """Add probe results for a subject."""
        if subject not in self._state:
            self._state[subject] = []
        self._state[subject].extend(results)
    
    def get_projection(self, subject: str) -> HealthProjection:
        """
        Get health projection for a subject based on stored results.
        
        Aggregation rules (these are explicit and deterministic):
        - One blocking integrity failure makes the entity UNHEALTHY
        - One unavailable required dependency makes readiness false
        - Optional provider failure produces DEGRADED
        - Intentionally stopped entities should not be misclassified
        
        Args:
            subject: Entity identifier
            
        Returns:
            HealthProjection with aggregated status
        """
        results = self._state.get(subject, [])
        
        if not results:
            return HealthProjection.create(subject=subject)
        
        # Categorize results by dimension
        liveness_results = [r for r in results if r.dimension == ProbeDimension.LIVENESS]
        readiness_results = [r for r in results if r.dimension == ProbeDimension.READINESS]
        health_results = [r for r in results if r.dimension == ProbeDimension.HEALTH]
        integrity_results = [r for r in results if r.dimension == ProbeDimension.INTEGRITY]
        
        # Determine dimension states
        liveness_state = self._aggregate_dimension(liveness_results, HealthStatus.UNKNOWN)
        readiness_state = self._aggregate_dimension(readiness_results, HealthStatus.UNKNOWN)
        health_state = self._aggregate_dimension(health_results, HealthStatus.HEALTHY)
        integrity_state = self._aggregate_dimension(integrity_results, HealthStatus.HEALTHY)
        
        # Collect failures and warnings
        failed_checks = [r.name for r in results if not r.passed]
        warning_checks = [r.name for r in results 
                        if not r.passed and r.severity == ProbeSeverity.WARNING]
        
        return HealthProjection.create(
            subject=subject,
            liveness=liveness_state,
            readiness=readiness_state,
            health=health_state,
            integrity=integrity_state,
            failed_checks=failed_checks,
            warning_checks=warning_checks
        )
    
    def _aggregate_dimension(
        self,
        results: List[ProbeResult],
        default_status: HealthStatus
    ) -> HealthStatus:
        """
        Aggregate probe results for a single dimension.
        
        Args:
            results: Probe results for this dimension
            default_status: Status if no results
            
        Returns:
            Aggregated status for the dimension
        """
        if not results:
            return default_status
        
        # Check for blocking failures first (highest priority)
        blocking_failures = [r for r in results if not r.passed and r.blocking]
        if blocking_failures:
            return HealthStatus.UNHEALTHY
        
        # Check for non-blocking failures
        non_blocking_failures = [r for r in results if not r.passed]
        if non_blocking_failures:
            return HealthStatus.DEGRADED
        
        # All passed - check for warnings (not failures but notable)
        warnings = [r for r in results if r.severity == ProbeSeverity.WARNING]
        if warnings:
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def clear(self, subject: Optional[str] = None) -> None:
        """Clear stored results."""
        if subject is None:
            self._state.clear()
        elif subject in self._state:
            del self._state[subject]


__all__ = [
    # Status values
    "HealthStatus",
    
    # Projections
    "HealthProjection",
    
    # Probe system
    "ProbeDimension",
    "ProbeSeverity",
    "ProbeResult",
    
    # Contracts
    "HealthChecker",
    
    # Aggregation
    "HealthAggregator",
]