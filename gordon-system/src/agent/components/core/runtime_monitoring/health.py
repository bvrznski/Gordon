# Core Runtime Health Models & Manager
# =====================================

"""
Immutable health models for runtime monitoring.

Provides:
- Immutable health check, observation, measurement, evaluation models
- Typed health status and findings
- Health report and snapshot generation
- Health history tracking
- Canonical HealthManager as single source of truth for health
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from enum import Enum, auto
import uuid
import time
import threading
import asyncio

# =============================================================================
# HEALTH STATUS VALUES
# =============================================================================


class HealthStatus(Enum):
    """
    Canonical health status values.
    
    States:
        UNKNOWN     - Not yet evaluated (initial state)
        HEALTHY     - Operating within acceptable conditions  
        DEGRADED    - Operational with reduced capability
        UNHEALTHY   - Not operating within acceptable conditions
        FAILED      - Failed and not recoverable
        
    Note: Health evaluates runtime condition. Health NEVER declares readiness.
    Readiness is a separate concern evaluated by ReadinessController.
    """
    
    UNKNOWN = "unknown"       # Initial state, not yet evaluated
    HEALTHY = "healthy"       # Fully operational
    DEGRADED = "degraded"     # Operational with reduced capability
    UNHEALTHY = "unhealthy"   # Not within acceptable conditions  
    FAILED = "failed"         # Failed and not recoverable


# =============================================================================
# HEALTH DOMAIN ENUMERATION
# =============================================================================


class HealthDomain(Enum):
    """
    Health evaluation domains.
    
    Each domain is evaluated independently to support partial degradation.
    """
    
    KERNEL = "kernel"
    RUNTIME = "runtime"
    LIFECYCLE = "lifecycle"
    SCHEDULER = "scheduler"
    EXECUTOR = "executor"
    RESOURCES = "resources"
    WORKERS = "workers"
    QUEUES = "queues"
    STORAGE = "storage"
    NETWORKING = "networking"
    MODELS = "models"
    PLUGINS = "plugins"
    SERVICES = "services"
    COGNITION_INTERFACES = "cognition_interfaces"
    COMMUNICATION = "communication"
    OBSERVABILITY = "observability"


# =============================================================================
# HEALTH FINDING (BASE CLASS)
# =============================================================================


@dataclass(frozen=True)
class HealthFinding:
    """
    A single health finding from an evaluation.
    
    Findings are immutable and preserve provenance for debugging and audit.
    """
    
    # Identifiers
    finding_id: str  # Unique identifier
    check_name: str  # Which check generated this
    
    # Classification
    status: HealthStatus  # UNKNOWN, HEALTHY, DEGRADED, UNHEALTHY, FAILED
    domain: HealthDomain  # Which domain this affects
    
    # Severity classification
    severity: "Severity"
    
    # Content
    message: str  # Human-readable finding description
    evidence: Dict[str, Any] = field(default_factory=dict)  # Supporting data
    
    # Source information
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_failure(self) -> bool:
        """Check if this finding indicates a failure state."""
        return self.status in (HealthStatus.UNHEALTHY, HealthStatus.FAILED)
    
    @property
    def is_degraded(self) -> bool:
        """Check if this finding indicates degraded state."""
        return self.status == HealthStatus.DEGRADED
    
    @classmethod
    def healthy(cls, check_name: str, domain: HealthDomain, message: str = "OK") -> "HealthFinding":
        """Create a healthy finding."""
        return cls(
            finding_id=f"health_finding_{uuid.uuid4().hex[:12]}",
            check_name=check_name,
            status=HealthStatus.HEALTHY,
            domain=domain,
            severity=Severity.INFO,
            message=message
        )
    
    @classmethod
    def degraded(cls, check_name: str, domain: HealthDomain, message: str) -> "HealthFinding":
        """Create a degraded finding."""
        return cls(
            finding_id=f"health_finding_{uuid.uuid4().hex[:12]}",
            check_name=check_name,
            status=HealthStatus.DEGRADED,
            domain=domain,
            severity=Severity.WARNING,
            message=message
        )
    
    @classmethod
    def unhealthy(cls, check_name: str, domain: HealthDomain, message: str) -> "HealthFinding":
        """Create an unhealthy finding."""
        return cls(
            finding_id=f"health_finding_{uuid.uuid4().hex[:12]}",
            check_name=check_name,
            status=HealthStatus.UNHEALTHY,
            domain=domain,
            severity=Severity.ERROR,
            message=message
        )
    
    @classmethod
    def failed(cls, check_name: str, domain: HealthDomain, message: str) -> "HealthFinding":
        """Create a failed finding."""
        return cls(
            finding_id=f"health_finding_{uuid.uuid4().hex[:12]}",
            check_name=check_name,
            status=HealthStatus.FAILED,
            domain=domain,
            severity=Severity.CRITICAL,
            message=message
        )


# =============================================================================
# SEVERITY ENUMERATION
# =============================================================================


class Severity(Enum):
    """
    Finding severity levels.
    
    Severity determines impact on overall health aggregation:
        INFO     - Informational, no status change
        WARNING  - Notable but non-blocking
        ERROR    - Blocks healthy status
        CRITICAL - Immediate failure condition
    """
    
    INFO = "info"          # Informational only
    WARNING = "warning"    # Non-blocking concern
    ERROR = "error"        # Blocks healthy status  
    CRITICAL = "critical"  # Immediate failure


# =============================================================================
# HEALTH CHECK (EVALUATION REQUEST)
# =============================================================================


@dataclass(frozen=True)
class HealthCheck:
    """
    A request to evaluate health.
    
    Checks are immutable evaluation requests. They do NOT mutate state.
    """
    
    # Identity
    check_id: str  # Unique identifier for this check request
    
    # Target
    subject: str   # What is being checked (entity ID, domain, etc.)
    
    # Configuration
    domain: HealthDomain       # Which domain to evaluate
    check_type: str            # Type of health check (e.g., "liveness", "readiness")
    timeout_seconds: float = 30.0  # Maximum evaluation time
    
    # Context
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# HEALTH MEASUREMENT (RAW OBSERVATION)
# =============================================================================


@dataclass(frozen=True)
class HealthMeasurement:
    """
    A single measurement from health evaluation.
    
    Measurements are the raw data points before aggregation.
    They are immutable and preserve provenance.
    """
    
    # Identifiers
    measurement_id: str  # Unique identifier
    
    # Source
    check_id: str        # Which check generated this
    subject: str         # What was measured
    
    # Domain context
    domain: HealthDomain
    dimension: str       # Dimension within domain (e.g., "cpu_usage", "memory_mb")
    
    # Value
    value: Any           # Raw measurement value
    unit: Optional[str] = None  # Unit of measurement
    
    # Status at time of measurement
    status: HealthStatus = HealthStatus.UNKNOWN
    
    # Timestamps
    measured_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    @classmethod
    def from_value(
        cls,
        check_id: str,
        subject: str,
        domain: HealthDomain,
        dimension: str,
        value: Any,
        unit: Optional[str] = None,
        status: HealthStatus = HealthStatus.UNKNOWN
    ) -> "HealthMeasurement":
        """Create a measurement from a raw value."""
        return cls(
            measurement_id=f"measurement_{uuid.uuid4().hex[:12]}",
            check_id=check_id,
            subject=subject,
            domain=domain,
            dimension=dimension,
            value=value,
            unit=unit,
            status=status
        )


# =============================================================================
# HEALTH OBSERVATION (AGGREGATED RESULT)
# =============================================================================


@dataclass(frozen=True)
class HealthObservation:
    """
    An aggregated health observation.
    
    Observations are the result of evaluating multiple measurements.
    They represent the current state of a subject's health.
    """
    
    # Identifiers
    observation_id: str  # Unique identifier
    
    # Target
    subject: str         # What was observed (entity ID)
    domain: HealthDomain  # Which domain
    
    # Result
    status: HealthStatus  # FINAL aggregated status
    findings: Tuple[HealthFinding, ...] = field(default_factory=tuple)
    
    # Metrics summary
    total_measurements: int = 0
    healthy_findings: int = 0
    degraded_findings: int = 0
    unhealthy_findings: int = 0
    
    # Timestamps
    observed_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Context
    evaluation_duration_seconds: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """Check if overall status is healthy."""
        return self.status == HealthStatus.HEALTHY
    
    @property
    def is_degraded(self) -> bool:
        """Check if status is degraded."""
        return self.status == HealthStatus.DEGRADED
    
    @property
    def is_unhealthy(self) -> bool:
        """Check if status is unhealthy or failed."""
        return self.status in (HealthStatus.UNHEALTHY, HealthStatus.FAILED)
    
    @classmethod
    def healthy(cls, subject: str, domain: HealthDomain) -> "HealthObservation":
        """Create a healthy observation."""
        return cls(
            observation_id=f"observation_{uuid.uuid4().hex[:12]}",
            subject=subject,
            domain=domain,
            status=HealthStatus.HEALTHY
        )
    
    @classmethod
    def degraded(cls, subject: str, domain: HealthDomain) -> "HealthObservation":
        """Create a degraded observation."""
        return cls(
            observation_id=f"observation_{uuid.uuid4().hex[:12]}",
            subject=subject,
            domain=domain,
            status=HealthStatus.DEGRADED
        )
    
    @classmethod
    def unhealthy(cls, subject: str, domain: HealthDomain) -> "HealthObservation":
        """Create an unhealthy observation."""
        return cls(
            observation_id=f"observation_{uuid.uuid4().hex[:12]}",
            subject=subject,
            domain=domain,
            status=HealthStatus.UNHEALTHY
        )
    
    @classmethod
    def failed(cls, subject: str, domain: HealthDomain) -> "HealthObservation":
        """Create a failed observation."""
        return cls(
            observation_id=f"observation_{uuid.uuid4().hex[:12]}",
            subject=subject,
            domain=domain,
            status=HealthStatus.FAILED
        )


# =============================================================================
# HEALTH EVALUATION (COMPLETE ASSESSMENT)
# =============================================================================


@dataclass(frozen=True)
class HealthEvaluation:
    """
    A complete health evaluation for a subject.
    
    Evaluations aggregate multiple observations and produce final status.
    They are immutable and include full provenance.
    """
    
    # Identifiers
    evaluation_id: str  # Unique identifier
    
    # Target
    subject: str        # What was evaluated
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Observations by domain
    observations: Dict[HealthDomain, HealthObservation] = field(default_factory=dict)
    
    # Aggregated status
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Summary statistics
    total_observations: int = 0
    healthy_domains: int = 0
    degraded_domains: int = 0
    unhealthy_domains: int = 0
    failed_domains: int = 0
    
    # Timing
    evaluation_duration_seconds: float = 0.0
    total_measurements: int = 0
    
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
    
    @classmethod
    def create(
        cls,
        subject: str,
        observations: Dict[HealthDomain, HealthObservation],
        evaluation_duration_seconds: float = 0.0,
        total_measurements: int = 0
    ) -> "HealthEvaluation":
        """Create an evaluation from domain observations."""
        
        # Calculate statistics
        healthy_count = sum(1 for o in observations.values() if o.is_healthy)
        degraded_count = sum(1 for o in observations.values() if o.is_degraded)
        unhealthy_count = sum(1 for o in observations.values() if o.is_unhealthy)
        
        # Determine overall status (most restrictive wins)
        overall_status = (
            HealthStatus.FAILED if unhealthy_count > 0 else
            HealthStatus.DEGRADED if degraded_count > 0 else
            HealthStatus.HEALTHY if healthy_count == len(observations) else
            HealthStatus.UNKNOWN
        )
        
        return cls(
            evaluation_id=f"evaluation_{uuid.uuid4().hex[:12]}",
            subject=subject,
            evaluated_at_utc=time.time(),
            monotonic_time=time.monotonic(),
            observations=dict(observations),
            overall_status=overall_status,
            total_observations=len(observations),
            healthy_domains=healthy_count,
            degraded_domains=degraded_count,
            unhealthy_domains=unhealthy_count,
            failed_domains=unhealthy_count - degraded_count - healthy_count if unhealthy_count > 0 else 0,
            evaluation_duration_seconds=evaluation_duration_seconds,
            total_measurements=total_measurements
        )


# =============================================================================
# HEALTH REPORT (COLLECTION OF EVALUATIONS)
# =============================================================================


@dataclass(frozen=True)
class HealthReport:
    """
    A collection of health evaluations for a specific scope.
    
    Reports are the output of health assessment - immutable and typed.
    They never become authorities, only observables.
    """
    
    # Scope
    subject: str               # What these reports are about (runtime_id, etc.)
    report_type: str = "health"  # Report type identifier
    
    # Evaluations
    evaluations: Tuple[HealthEvaluation, ...] = field(default_factory=tuple)
    
    # Timestamps
    generated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Summary statistics
    total_subjects: int = 0
    healthy_count: int = 0
    degraded_count: int = 0
    unhealthy_count: int = 0
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if any evaluation is unhealthy or failed."""
        return self.unhealthy_count > 0
    
    @property
    def overall_status(self) -> HealthStatus:
        """
        Determine overall status from evaluations.
        
        Priority: FAILED > UNHEALTHY > DEGRADED > UNKNOWN > HEALTHY
        """
        if self.unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        if self.degraded_count > 0:
            return HealthStatus.DEGRADED
        if self.healthy_count == len(self.evaluations):
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN
    
    def get_by_status(self, status: HealthStatus) -> List[HealthEvaluation]:
        """Get all evaluations with the specified overall status."""
        return [e for e in self.evaluations if e.overall_status == status]
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "subject": self.subject,
            "report_type": self.report_type,
            "generated_at_utc": self.generated_at_utc,
            "overall_status": self.overall_status.value,
            "total_subjects": len(self.evaluations),
            "healthy_count": self.healthy_count,
            "degraded_count": self.degraded_count,
            "unhealthy_count": self.unhealthy_count,
        }
    
    @classmethod
    def create(
        cls,
        subject: str,
        evaluations: Optional[List[HealthEvaluation]] = None,
        report_type: str = "health"
    ) -> "HealthReport":
        """Create a health report from evaluations."""
        
        evals = tuple(evaluations or [])
        
        # Calculate statistics
        healthy = sum(1 for e in evals if e.is_healthy)
        degraded = sum(1 for e in evals if e.is_degraded)
        unhealthy = sum(1 for e in evals if e.is_unhealthy)
        
        return cls(
            subject=subject,
            report_type=report_type,
            evaluations=evals,
            total_subjects=len(evals),
            healthy_count=healthy,
            degraded_count=degraded,
            unhealthy_count=unhealthy
        )


# =============================================================================
# HEALTH SNAPSHOT (POINT-IN-TIME VIEW)
# =============================================================================


@dataclass(frozen=True)
class HealthSnapshot:
    """
    An immutable point-in-time snapshot of health state.
    
    Snapshots are used for:
    - Historical analysis
    - Comparison between time periods
    - Debugging and audit trails
    
    They capture the complete health state at a moment in time.
    """
    
    # Identifiers
    snapshot_id: str           # Unique identifier
    runtime_id: str            # Which runtime this is about
    
    # Timestamps
    captured_at_utc: float     # When snapshot was taken
    monotonic_time: float      # For ordering snapshots
    
    # Versioning
    version: int               # Snapshot sequence number
    previous_snapshot_id: Optional[str] = None  # Chain to previous
    
    # State
    evaluations: Dict[str, HealthEvaluation] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """Check if all subjects in snapshot are healthy."""
        return all(e.is_healthy for e in self.evaluations.values()) and len(self.evaluations) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "runtime_id": self.runtime_id,
            "captured_at_utc": self.captured_at_utc,
            "version": self.version,
            "previous_snapshot_id": self.previous_snapshot_id,
            "is_healthy": self.is_healthy,
            "evaluation_count": len(self.evaluations),
        }
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        evaluations: Dict[str, HealthEvaluation],
        version: int = 1,
        previous_snapshot_id: Optional[str] = None
    ) -> "HealthSnapshot":
        """Create a new health snapshot."""
        return cls(
            snapshot_id=f"snapshot_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            captured_at_utc=time.time(),
            monotonic_time=time.monotonic(),
            version=version,
            previous_snapshot_id=previous_snapshot_id,
            evaluations=dict(evaluations)
        )


# =============================================================================
# HEALTH HISTORY ENTRY
# =============================================================================


@dataclass(frozen=True)
class HealthHistoryEntry:
    """
    An entry in the health history log.
    
    History entries are immutable and preserve complete provenance for audit.
    """
    
    # Identifiers
    history_id: str            # Unique identifier for this entry
    runtime_id: str            # Which runtime this is about
    
    # Timestamps
    timestamp_utc: float       # When event occurred
    monotonic_time: float      # For ordering
    
    # Event type
    event_type: "HealthEventType"  # What kind of health event
    
    # State
    previous_status: Optional[HealthStatus] = None
    new_status: Optional[HealthStatus] = None
    
    # Details
    subject: str = ""          # What changed (entity ID)
    reason: Optional[str] = None  # Why it changed
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def status_changed(
        cls,
        runtime_id: str,
        subject: str,
        previous_status: HealthStatus,
        new_status: HealthStatus,
        reason: Optional[str] = None
    ) -> "HealthHistoryEntry":
        """Create a status change event."""
        return cls(
            history_id=f"health_hist_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            timestamp_utc=time.time(),
            monotonic_time=time.monotonic(),
            event_type=HealthEventType.STATUS_CHANGED,
            previous_status=previous_status,
            new_status=new_status,
            subject=subject,
            reason=reason
        )
    
    @classmethod
    def snapshot_taken(
        cls,
        runtime_id: str,
        snapshot_id: str,
        version: int
    ) -> "HealthHistoryEntry":
        """Create a snapshot event."""
        return cls(
            history_id=f"health_hist_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            timestamp_utc=time.time(),
            monotonic_time=time.monotonic(),
            event_type=HealthEventType.SNAPSHOT_TAKEN,
            new_status=None,
            subject=snapshot_id,
            details={"version": version}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "history_id": self.history_id,
            "runtime_id": self.runtime_id,
            "timestamp_utc": self.timestamp_utc,
            "event_type": self.event_type.value,
            "previous_status": self.previous_status.value if self.previous_status else None,
            "new_status": self.new_status.value if self.new_status else None,
            "subject": self.subject,
            "reason": self.reason,
        }


# =============================================================================
# HEALTH EVENT TYPE ENUM
# =============================================================================


class HealthEventType(Enum):
    """Types of health events for history tracking."""
    
    STATUS_CHANGED = "status_changed"       # Status transition occurred
    SNAPSHOT_TAKEN = "snapshot_taken"       # Snapshot was generated
    EVALUATION_STARTED = "evaluation_started"  # Evaluation began
    EVALUATION_COMPLETED = "evaluation_completed"  # Evaluation finished
    HEARTBEAT_LOST = "heartbeat_lost"       # Heartbeat signal lost
    HEARTBEAT_RESTORED = "heartbeat_restored"  # Heartbeat signal restored
    WATCHDOG_TRIGGERED = "watchdog_triggered"   # Watchdog triggered alert


# =============================================================================
# HEALTH MANAGER (CANONICAL AUTHORITY)
# =============================================================================


class HealthManager:
    """
    Canonical authority for health evaluation and monitoring.
    
    This is THE ONE source of truth for runtime health. It owns:
    
    - Health registration
    - Health evaluation  
    - Health aggregation
    - Health snapshots
    - Health reports
    - Heartbeat supervision
    - Health history
    
    Health Manager Invariants:
        1. Exactly one per runtime instance
        2. Evaluates independently of readiness
        3. Never mutates subsystem state directly
        4. Reports are immutable and typed
        5. History preserves provenance
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the HealthManager.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
            
        Note: This creates a NEW manager. For singleton behavior,
        use create_health_manager() from runtime_monitoring/__init__.py
        """
        self._runtime_id = runtime_id
        
        # Core state
        self._lock = threading.RLock()
        self._evaluations: Dict[str, HealthEvaluation] = {}
        self._snapshots: List[HealthSnapshot] = []
        self._history: List[HealthHistoryEntry] = []
        
        # Counters
        self._snapshot_version = 0
        self._evaluation_sequence = 0
        
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this manager serves."""
        return self._runtime_id
    
    @property
    def snapshot_count(self) -> int:
        """Get total number of snapshots taken."""
        with self._lock:
            return len(self._snapshots)
    
    @property
    def evaluation_count(self) -> int:
        """Get total number of evaluations stored."""
        with self._lock:
            return len(self._evaluations)
    
    # -------------------------------------------------------------------------
    # Health Evaluation (main entry point)
    # -------------------------------------------------------------------------
    
    async def evaluate(
        self,
        subject: str,
        domain_checks: Dict[HealthDomain, Callable[[str], Any]],
        timeout_seconds: float = 30.0
    ) -> HealthEvaluation:
        """
        Evaluate health for a subject across multiple domains.
        
        This is the canonical evaluation method. It:
        1. Executes domain-specific checks concurrently
        2. Aggregates results deterministically  
        3. Produces an immutable HealthEvaluation
        
        Args:
            subject: Entity to evaluate (entity ID, component name, etc.)
            domain_checks: Dict mapping domains to check functions
            timeout_seconds: Maximum time for evaluation
            
        Returns:
            Immutable HealthEvaluation with complete status
            
        Raises:
            asyncio.TimeoutError: If evaluation exceeds timeout
        """
        start_time = time.monotonic()
        self._evaluation_sequence += 1
        
        # Execute domain checks concurrently
        tasks = []
        for domain, check_fn in domain_checks.items():
            task = asyncio.create_task(self._execute_domain_check(
                subject=subject,
                domain=domain,
                check_fn=check_fn,
                timeout_seconds=timeout_seconds / len(domain_checks)
            ))
            tasks.append((domain, task))
        
        # Wait for all checks to complete
        results: Dict[HealthDomain, HealthObservation] = {}
        total_measurements = 0
        
        for domain, task in tasks:
            try:
                observation = await asyncio.wait_for(task, timeout=timeout_seconds / len(domain_checks))
                results[domain] = observation
                total_measurements += observation.total_measurements
                
            except asyncio.TimeoutError:
                # Timeout -> unhealthy for this domain
                results[domain] = HealthObservation.unhealthy(subject, domain)
        
        # Create evaluation
        evaluation_duration = time.monotonic() - start_time
        
        evaluation = HealthEvaluation.create(
            subject=subject,
            observations=results,
            evaluation_duration_seconds=evaluation_duration,
            total_measurements=total_measurements
        )
        
        # Store evaluation
        with self._lock:
            self._evaluations[subject] = evaluation
            
            # Generate history entry
            prev_eval = self._evaluations.get(subject)
            if prev_eval and prev_eval.overall_status != evaluation.overall_status:
                self._history.append(HealthHistoryEntry.status_changed(
                    runtime_id=self._runtime_id,
                    subject=subject,
                    previous_status=prev_eval.overall_status,
                    new_status=evaluation.overall_status
                ))
        
        return evaluation
    
    async def _execute_domain_check(
        self,
        subject: str,
        domain: HealthDomain,
        check_fn: Callable[[str], Any],
        timeout_seconds: float
    ) -> HealthObservation:
        """Execute a single domain health check."""
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(check_fn, subject),
                timeout=timeout_seconds
            )
            
            # Convert result to status
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.DEGRADED
            elif isinstance(result, HealthStatus):
                status = result
            else:
                # Default: assume healthy if no error
                status = HealthStatus.HEALTHY
            
            return HealthObservation(
                observation_id=f"observation_{uuid.uuid4().hex[:12]}",
                subject=subject,
                domain=domain,
                status=status,
                findings=(HealthFinding.healthy("check", domain, "Check completed"),)
            )
            
        except Exception as e:
            # Check failed -> unhealthy
            return HealthObservation.unhealthy(subject, domain)
    
    # -------------------------------------------------------------------------
    # Snapshot Management
    # -------------------------------------------------------------------------
    
    def take_snapshot(self) -> HealthSnapshot:
        """
        Take a point-in-time snapshot of current health state.
        
        Returns:
            Immutable HealthSnapshot with complete state at moment
        """
        with self._lock:
            self._snapshot_version += 1
            
            previous_id = None
            if self._snapshots:
                previous_id = self._snapshots[-1].snapshot_id
            
            snapshot = HealthSnapshot.create(
                runtime_id=self._runtime_id,
                evaluations=dict(self._evaluations),
                version=self._snapshot_version,
                previous_snapshot_id=previous_id
            )
            
            self._snapshots.append(snapshot)
            
            # Record history entry
            self._history.append(HealthHistoryEntry.snapshot_taken(
                runtime_id=self._runtime_id,
                snapshot_id=snapshot.snapshot_id,
                version=self._snapshot_version
            ))
            
            return snapshot
    
    def get_latest_snapshot(self) -> Optional[HealthSnapshot]:
        """Get the most recent snapshot, if any."""
        with self._lock:
            if self._snapshots:
                return self._snapshots[-1]
            return None
    
    # -------------------------------------------------------------------------
    # Report Generation
    # -------------------------------------------------------------------------
    
    def generate_report(self, subject: Optional[str] = None) -> HealthReport:
        """
        Generate a health report for a subject or all subjects.
        
        Args:
            subject: Specific subject to report on (None = all)
            
        Returns:
            Immutable HealthReport with current status
        """
        with self._lock:
            if subject is not None and subject in self._evaluations:
                evaluation = self._evaluations[subject]
                return HealthReport.create(subject, [evaluation])
            else:
                # Report on all subjects
                evaluations = list(self._evaluations.values())
                return HealthReport.create(
                    subject=self._runtime_id,
                    evaluations=evaluations
                )
    
    # -------------------------------------------------------------------------
    # History Queries
    # -------------------------------------------------------------------------
    
    def get_history(self, since_timestamp: Optional[float] = None) -> List[HealthHistoryEntry]:
        """
        Get health history entries.
        
        Args:
            since_timestamp: Only return entries after this timestamp
            
        Returns:
            List of history entries in chronological order
        """
        with self._lock:
            if since_timestamp is None:
                return list(self._history)
            
            return [e for e in self._history if e.timestamp_utc >= since_timestamp]
    
    # -------------------------------------------------------------------------
    # State Query Methods
    # -------------------------------------------------------------------------
    
    def get_evaluation(self, subject: str) -> Optional[HealthEvaluation]:
        """Get the latest evaluation for a subject."""
        with self._lock:
            return self._evaluations.get(subject)
    
    def is_healthy(self, subject: str) -> bool:
        """
        Check if a subject is healthy.
        
        This is a convenience method. For production use, prefer
        generate_report() to get full context.
        """
        evaluation = self.get_evaluation(subject)
        return evaluation.is_healthy if evaluation else False
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall runtime health status."""
        with self._lock:
            evaluations = list(self._evaluations.values())
            
            if not evaluations:
                return HealthStatus.UNKNOWN
            
            # Most restrictive wins
            for status in (HealthStatus.FAILED, HealthStatus.UNHEALTHY, HealthStatus.DEGRADED):
                if any(e.overall_status == status for e in evaluations):
                    return status
            
            return HealthStatus.HEALTHY


# =============================================================================
# HEALTH AGGREGATOR (UTILITY)
# =============================================================================


class HealthAggregator:
    """
    Deterministic health aggregation logic.
    
    Aggregates multiple health findings into a single status.
    Follows explicit rules rather than "worst enum wins" logic.
    """
    
    def __init__(self) -> None:
        self._findings: Dict[str, List[HealthFinding]] = {}
    
    def add_finding(self, subject: str, finding: HealthFinding) -> None:
        """Add a finding for a subject."""
        if subject not in self._findings:
            self._findings[subject] = []
        self._findings[subject].append(finding)
    
    def aggregate_subject(self, subject: str) -> HealthStatus:
        """
        Aggregate findings for a subject into a status.
        
        Rules:
            - One CRITICAL failure -> FAILED
            - One ERROR failure -> UNHEALTHY  
            - Any WARNING findings -> DEGRADED
            - No failures -> HEALTHY
            
        Args:
            subject: Subject to aggregate
            
        Returns:
            Aggregated HealthStatus
        """
        findings = self._findings.get(subject, [])
        
        if not findings:
            return HealthStatus.UNKNOWN
        
        # Check for critical failures first (highest priority)
        critical_failures = [
            f for f in findings 
            if f.is_failure and f.severity == Severity.CRITICAL
        ]
        if critical_failures:
            return HealthStatus.FAILED
        
        # Check for error-level failures
        error_failures = [
            f for f in findings 
            if f.is_failure and f.severity == Severity.ERROR
        ]
        if error_failures:
            return HealthStatus.UNHEALTHY
        
        # Check for warnings
        warnings = [f for f in findings if f.status == HealthStatus.DEGRADED]
        if warnings:
            return HealthStatus.DEGRADED
        
        # All healthy
        return HealthStatus.HEALTHY
    
    def clear(self, subject: Optional[str] = None) -> None:
        """Clear stored findings."""
        if subject is None:
            self._findings.clear()
        elif subject in self._findings:
            del self._findings[subject]


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Status values
    "HealthStatus",
    
    # Domain enumeration
    "HealthDomain",
    
    # Severity levels
    "Severity",
    
    # Models
    "HealthFinding",
    "HealthCheck",
    "HealthMeasurement", 
    "HealthObservation",
    "HealthEvaluation",
    "HealthReport",
    "HealthSnapshot",
    "HealthHistoryEntry",
    
    # Event types
    "HealthEventType",
    
    # Authorities
    "HealthManager",
    
    # Utilities
    "HealthAggregator",
]