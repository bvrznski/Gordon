# Core Runtime Integrity Models & Manager
# ========================================

"""
Immutable integrity models for runtime monitoring.

Provides:
- Immutable integrity check, finding, violation models
- Typed integrity status and reports  
- Integrity snapshot generation
- Integrity history tracking
- Canonical IntegrityManager as single source of truth for integrity
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Set
from enum import Enum, auto
import uuid
import time
import threading
import asyncio


# =============================================================================
# RUNTIME OBSERVER (CANONICAL AUTHORITY)
# =============================================================================

class RuntimeObserver:
    """
    Canonical authority for runtime observation coordination.
    
    This is THE ONE source of truth for runtime observation. It owns:
    
    - Observation pipeline orchestration
    - Measurement collection scheduling
    - Evaluation triggering
    - Evidence publication
    
    Invariants:
        1. Exactly one per runtime instance
        2. Observational only (never mutates subsystem state)
        3. Deterministic evaluation ordering
        4. Bounded history tracking
    
    The RuntimeObserver sits at the top of the observation pipeline:
    
        Observation → Measurement → Evaluation → Health/Integrity Assessment
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the RuntimeObserver.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
            
        Note: This creates a NEW observer. For singleton behavior,
        use create_runtime_observer() from runtime_monitoring/__init__.py
        """
        self._runtime_id = runtime_id
        
        # Core state
        self._lock = threading.RLock()
        
        # Evaluation cadence tracking
        self._last_health_eval_time: float = 0.0
        self._last_integrity_eval_time: float = 0.0
        self._eval_count = 0
        
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this observer serves."""
        return self._runtime_id
    
    @property
    def health_evaluation_cadence_seconds(self) -> float:
        """Get the time since last health evaluation."""
        with self._lock:
            if self._last_health_eval_time == 0.0:
                return 0.0
            return time.monotonic() - self._last_health_eval_time
    
    @property
    def integrity_evaluation_cadence_seconds(self) -> float:
        """Get the time since last integrity evaluation."""
        with self._lock:
            if self._last_integrity_eval_time == 0.0:
                return 0.0
            return time.monotonic() - self._last_integrity_eval_time
    
    def record_health_evaluation(self, elapsed: float) -> None:
        """Record that a health evaluation was completed."""
        with self._lock:
            self._last_health_eval_time = time.monotonic()
            self._eval_count += 1
    
    def record_integrity_evaluation(self, elapsed: float) -> None:
        """Record that an integrity evaluation was completed."""
        with self._lock:
            self._last_integrity_eval_time = time.monotonic()
            self._eval_count += 1
    
    @property
    def total_evaluations(self) -> int:
        """Get total number of evaluations performed."""
        with self._lock:
            return self._eval_count


# =============================================================================
# SEVERITY ENUMERATION (MUST COME FIRST - referenced by other classes)
# =============================================================================


class Severity(Enum):
    """
    Integrity violation severity levels.
    
    Severity determines impact:
        WARNING - Non-blocking concern, may indicate future issues
        ERROR   - Blocks normal operation, needs attention
        CRITICAL - Immediate failure, requires intervention
    """
    
    WARNING = "warning"  # Non-blocking concern
    ERROR = "error"      # Blocks operation
    CRITICAL = "critical"  # Immediate failure


# =============================================================================
# INTEGRITY STATUS VALUES
# =============================================================================


class IntegrityStatus(Enum):
    """
    Canonical integrity status values.
    
    States:
        UNKNOWN   - Not yet evaluated (initial state)
        VERIFIED  - All checks passed, architecture correct
        DEGRADED  - Some issues found but not critical
        VIOLATED  - Critical architectural violations detected
        
    Note: Integrity evaluates architectural correctness. Integrity NEVER 
    declares health or availability. A system can be healthy but have 
    integrity violations (e.g., deprecated API usage), or vice versa.
    """
    
    UNKNOWN = "unknown"     # Initial state, not yet evaluated
    VERIFIED = "verified"   # All checks passed, architecture correct
    DEGRADED = "degraded"   # Some non-critical issues found
    VIOLATED = "violated"   # Critical violations detected


# =============================================================================
# INTEGRITY DOMAIN ENUMERATION
# =============================================================================


class IntegrityDomain(Enum):
    """
    Integrity verification domains.
    
    Each domain verifies architectural correctness independently.
    """
    
    OWNERSHIP = "ownership"                    # Component ownership verification
    DEPENDENCY_GRAPH = "dependency_graph"      # Dependency graph consistency
    LIFECYCLE_CONSISTENCY = "lifecycle_consistency"  # Lifecycle transitions
    RUNTIME_STATE = "runtime_state"            # Runtime state validity
    CONFIGURATION = "configuration"           # Config consistency
    CAPABILITY_GRAPH = "capability_graph"     # Capability relationships
    REGISTRY = "registry"                     # Registry integrity
    SYNCHRONIZATION = "synchronization"        # Thread/sync correctness
    RESOURCE_OWNERSHIP = "resource_ownership"  # Resource allocation
    SCHEDULER_INVARIANTS = "scheduler_invariants"   # Scheduler rules
    EXECUTOR_INVARIANTS = "executor_invariants"     # Executor rules


# =============================================================================
# INTEGRITY VIOLATION (BASE CLASS)
# =============================================================================


@dataclass(frozen=True)
class IntegrityViolation:
    """
    A single integrity violation from an evaluation.
    
    Violations are immutable and preserve provenance for debugging and audit.
    """
    
    # Identifiers
    violation_id: str  # Unique identifier
    
    # Classification
    domain: IntegrityDomain   # Which domain was violated
    severity: Severity        # Severity level (WARNING, ERROR, CRITICAL)
    
    # Content
    message: str              # Human-readable violation description
    evidence: Dict[str, Any] = field(default_factory=dict)  # Supporting data
    
    # Source information  
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_blocking(self) -> bool:
        """Check if this violation blocks operation."""
        return self.severity in (Severity.ERROR, Severity.CRITICAL)
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical violation."""
        return self.severity == Severity.CRITICAL
    
    @classmethod
    def warning(cls, domain: IntegrityDomain, message: str, **evidence) -> "IntegrityViolation":
        """Create a warning-level violation."""
        return cls(
            violation_id=f"integrity_violation_{uuid.uuid4().hex[:12]}",
            domain=domain,
            severity=Severity.WARNING,
            message=message,
            evidence=evidence
        )
    
    @classmethod
    def error(cls, domain: IntegrityDomain, message: str, **evidence) -> "IntegrityViolation":
        """Create an error-level violation."""
        return cls(
            violation_id=f"integrity_violation_{uuid.uuid4().hex[:12]}",
            domain=domain,
            severity=Severity.ERROR,
            message=message,
            evidence=evidence
        )
    
    @classmethod
    def critical(cls, domain: IntegrityDomain, message: str, **evidence) -> "IntegrityViolation":
        """Create a critical violation."""
        return cls(
            violation_id=f"integrity_violation_{uuid.uuid4().hex[:12]}",
            domain=domain,
            severity=Severity.CRITICAL,
            message=message,
            evidence=evidence
        )


# =============================================================================
# INTEGRITY FINDING (BASE CLASS)
# =============================================================================


@dataclass(frozen=True)
class IntegrityFinding:
    """
    A single finding from an integrity check.
    
    Findings can be either pass or fail. They preserve provenance.
    """
    
    # Identifiers
    finding_id: str  # Unique identifier
    
    # Check info
    check_name: str  # Which check generated this
    domain: IntegrityDomain  # Which domain this affects
    
    # Result
    passed: bool          # Did the check pass?
    status: IntegrityStatus  # VERIFIED, DEGRADED, VIOLATED
    severity: Severity = Severity.WARNING  # For failure findings
    
    # Content
    message: str = ""     # Human-readable description
    evidence: Dict[str, Any] = field(default_factory=dict)  # Supporting data
    
    # Source information
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    @property
    def is_pass(self) -> bool:
        """Check if this finding indicates a pass."""
        return self.passed and self.status == IntegrityStatus.VERIFIED
    
    @property
    def is_fail(self) -> bool:
        """Check if this finding indicates a failure."""
        return not self.passed or self.status in (IntegrityStatus.DEGRADED, IntegrityStatus.VIOLATED)
    
    @classmethod
    def pass_finding(cls, check_name: str, domain: IntegrityDomain, message: str = "OK") -> "IntegrityFinding":
        """Create a passing finding."""
        return cls(
            finding_id=f"integrity_finding_{uuid.uuid4().hex[:12]}",
            check_name=check_name,
            domain=domain,
            passed=True,
            status=IntegrityStatus.VERIFIED,
            message=message
        )
    
    @classmethod
    def fail_finding(cls, check_name: str, domain: IntegrityDomain, message: str) -> "IntegrityFinding":
        """Create a failing finding."""
        return cls(
            finding_id=f"integrity_finding_{uuid.uuid4().hex[:12]}",
            check_name=check_name,
            domain=domain,
            passed=False,
            status=IntegrityStatus.VIOLATED,
            severity=Severity.ERROR,  # Failures are at least ERROR level
            message=message
        )
    
    @classmethod
    def degraded_finding(cls, check_name: str, domain: IntegrityDomain, message: str) -> "IntegrityFinding":
        """Create a degraded finding."""
        return cls(
            finding_id=f"integrity_finding_{uuid.uuid4().hex[:12]}",
            check_name=check_name,
            domain=domain,
            passed=True,
            status=IntegrityStatus.DEGRADED,
            severity=Severity.WARNING,  # Degraded is at least WARNING level
            message=message
        )


# =============================================================================
# INTEGRITY CHECK (EVALUATION REQUEST)
# =============================================================================


@dataclass(frozen=True)
class IntegrityCheck:
    """
    A request to evaluate integrity.
    
    Checks are immutable evaluation requests. They do NOT mutate state.
    """
    
    # Identity
    check_id: str  # Unique identifier for this check request
    
    # Target
    subject: str   # What is being checked (entity ID, component, etc.)
    
    # Configuration
    domain: IntegrityDomain   # Which domain to verify
    timeout_seconds: float = 30.0  # Maximum evaluation time
    
    # Context
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# INTEGRITY EVALUATION (COMPLETE ASSESSMENT)
# =============================================================================


@dataclass(frozen=True)
class IntegrityEvaluation:
    """
    A complete integrity evaluation for a subject.
    
    Evaluations aggregate multiple findings and produce final status.
    They are immutable and include full provenance.
    """
    
    # Identifiers
    evaluation_id: str  # Unique identifier
    
    # Target
    subject: str        # What was evaluated
    evaluated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Findings by domain
    findings: Dict[IntegrityDomain, Tuple[IntegrityFinding, ...]] = field(default_factory=dict)
    
    # Aggregated status
    overall_status: IntegrityStatus = IntegrityStatus.UNKNOWN
    
    # Summary statistics
    total_findings: int = 0
    passing_findings: int = 0
    failing_findings: int = 0
    degraded_findings: int = 0
    
    # Timing
    evaluation_duration_seconds: float = 0.0
    
    @property
    def is_verified(self) -> bool:
        """Check if overall status is verified."""
        return self.overall_status == IntegrityStatus.VERIFIED
    
    @property
    def is_degraded(self) -> bool:
        """Check if overall status is degraded."""
        return self.overall_status == IntegrityStatus.DEGRADED
    
    @property
    def is_violated(self) -> bool:
        """Check if overall status is violated."""
        return self.overall_status == IntegrityStatus.VIOLATED
    
    @classmethod
    def create(
        cls,
        subject: str,
        findings_by_domain: Dict[IntegrityDomain, List[IntegrityFinding]],
        evaluation_duration_seconds: float = 0.0
    ) -> "IntegrityEvaluation":
        """Create an evaluation from domain findings."""
        
        # Flatten all findings
        all_findings: List[IntegrityFinding] = []
        for findings in findings_by_domain.values():
            all_findings.extend(findings)
        
        # Calculate statistics
        passing = sum(1 for f in all_findings if f.is_pass)
        failing = sum(1 for f in all_findings if f.is_fail and not f.is_degraded)
        degraded = sum(1 for f in all_findings if f.status == IntegrityStatus.DEGRADED)
        
        # Determine overall status - critical errors have severity CRITICAL
        has_critical = any(getattr(f, 'severity', Severity.WARNING) == Severity.CRITICAL and f.is_fail for f in all_findings)
        has_error = any(getattr(f, 'severity', Severity.WARNING) == Severity.ERROR and f.is_fail for f in all_findings)
        
        if has_critical:
            overall_status = IntegrityStatus.VIOLATED
        elif has_error or failing > 0:
            overall_status = IntegrityStatus.DEGRADED
        elif degraded > 0:
            overall_status = IntegrityStatus.DEGRADED
        else:
            overall_status = IntegrityStatus.VERIFIED
        
        # Convert lists to tuples for immutability
        findings_tuple: Dict[IntegrityDomain, Tuple[IntegrityFinding, ...]] = {}
        for domain, findings in findings_by_domain.items():
            findings_tuple[domain] = tuple(findings)
        
        return cls(
            evaluation_id=f"evaluation_{uuid.uuid4().hex[:12]}",
            subject=subject,
            evaluated_at_utc=time.time(),
            monotonic_time=time.monotonic(),
            findings=findings_tuple,
            overall_status=overall_status,
            total_findings=len(all_findings),
            passing_findings=passing,
            failing_findings=failing,
            degraded_findings=degraded,
            evaluation_duration_seconds=evaluation_duration_seconds
        )


# =============================================================================
# INTEGRITY REPORT (COLLECTION OF EVALUATIONS)
# =============================================================================


@dataclass(frozen=True)
class IntegrityReport:
    """
    A collection of integrity evaluations for a specific scope.
    
    Reports are the output of integrity assessment - immutable and typed.
    They never become authorities, only observables.
    """
    
    # Scope
    subject: str               # What these reports are about (runtime_id, etc.)
    report_type: str = "integrity"  # Report type identifier
    
    # Evaluations
    evaluations: Tuple[IntegrityEvaluation, ...] = field(default_factory=tuple)
    
    # Timestamps
    generated_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Summary statistics
    total_subjects: int = 0
    verified_count: int = 0
    degraded_count: int = 0
    violated_count: int = 0
    
    @property
    def has_violations(self) -> bool:
        """Check if any evaluation has violations."""
        return self.violated_count > 0
    
    @property
    def overall_status(self) -> IntegrityStatus:
        """
        Determine overall status from evaluations.
        
        Priority: VIOLATED > DEGRADED > VERIFIED
        """
        if self.violated_count > 0:
            return IntegrityStatus.VIOLATED
        if self.degraded_count > 0:
            return IntegrityStatus.DEGRADED
        if self.verified_count == len(self.evaluations):
            return IntegrityStatus.VERIFIED
        return IntegrityStatus.UNKNOWN
    
    def get_by_status(self, status: IntegrityStatus) -> List[IntegrityEvaluation]:
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
            "verified_count": self.verified_count,
            "degraded_count": self.degraded_count,
            "violated_count": self.violated_count,
        }
    
    @classmethod
    def create(
        cls,
        subject: str,
        evaluations: Optional[List[IntegrityEvaluation]] = None,
        report_type: str = "integrity"
    ) -> "IntegrityReport":
        """Create an integrity report from evaluations."""
        
        evals = tuple(evaluations or [])
        
        # Calculate statistics
        verified = sum(1 for e in evals if e.is_verified)
        degraded = sum(1 for e in evals if e.is_degraded)
        violated = sum(1 for e in evals if e.is_violated)
        
        return cls(
            subject=subject,
            report_type=report_type,
            evaluations=evals,
            total_subjects=len(evals),
            verified_count=verified,
            degraded_count=degraded,
            violated_count=violated
        )


# =============================================================================
# INTEGRITY SNAPSHOT (POINT-IN-TIME VIEW)
# =============================================================================


@dataclass(frozen=True)
class IntegritySnapshot:
    """
    An immutable point-in-time snapshot of integrity state.
    
    Snapshots are used for:
    - Historical analysis
    - Comparison between time periods  
    - Debugging and audit trails
    
    They capture the complete integrity state at a moment in time.
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
    evaluations: Dict[str, IntegrityEvaluation] = field(default_factory=dict)
    
    @property
    def is_verified(self) -> bool:
        """Check if all subjects in snapshot are verified."""
        return all(e.is_verified for e in self.evaluations.values()) and len(self.evaluations) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "runtime_id": self.runtime_id,
            "captured_at_utc": self.captured_at_utc,
            "version": self.version,
            "previous_snapshot_id": self.previous_snapshot_id,
            "is_verified": self.is_verified,
            "evaluation_count": len(self.evaluations),
        }
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        evaluations: Dict[str, IntegrityEvaluation],
        version: int = 1,
        previous_snapshot_id: Optional[str] = None
    ) -> "IntegritySnapshot":
        """Create a new integrity snapshot."""
        return cls(
            snapshot_id=f"integrity_snapshot_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            captured_at_utc=time.time(),
            monotonic_time=time.monotonic(),
            version=version,
            previous_snapshot_id=previous_snapshot_id,
            evaluations=dict(evaluations)
        )


# =============================================================================
# INTEGRITY HISTORY ENTRY
# =============================================================================


@dataclass(frozen=True)
class IntegrityHistoryEntry:
    """
    An entry in the integrity history log.
    
    History entries are immutable and preserve complete provenance for audit.
    """
    
    # Identifiers
    history_id: str            # Unique identifier for this entry
    runtime_id: str            # Which runtime this is about
    
    # Timestamps
    timestamp_utc: float       # When event occurred
    monotonic_time: float      # For ordering
    
    # Event type
    event_type: "IntegrityEventType"  # What kind of integrity event
    
    # State
    previous_status: Optional[IntegrityStatus] = None
    new_status: Optional[IntegrityStatus] = None
    
    # Details
    subject: str = ""          # What changed (entity ID)
    reason: Optional[str] = None  # Why it changed
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def status_changed(
        cls,
        runtime_id: str,
        subject: str,
        previous_status: IntegrityStatus,
        new_status: IntegrityStatus,
        reason: Optional[str] = None
    ) -> "IntegrityHistoryEntry":
        """Create a status change event."""
        return cls(
            history_id=f"integrity_hist_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            timestamp_utc=time.time(),
            monotonic_time=time.monotonic(),
            event_type=IntegrityEventType.STATUS_CHANGED,
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
    ) -> "IntegrityHistoryEntry":
        """Create a snapshot event."""
        return cls(
            history_id=f"integrity_hist_{uuid.uuid4().hex[:12]}",
            runtime_id=runtime_id,
            timestamp_utc=time.time(),
            monotonic_time=time.monotonic(),
            event_type=IntegrityEventType.SNAPSHOT_TAKEN,
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
# INTEGRITY EVENT TYPE ENUM
# =============================================================================


class IntegrityEventType(Enum):
    """Types of integrity events for history tracking."""
    
    STATUS_CHANGED = "status_changed"         # Status transition occurred
    SNAPSHOT_TAKEN = "snapshot_taken"         # Snapshot was generated
    EVALUATION_STARTED = "evaluation_started"   # Evaluation began
    EVALUATION_COMPLETED = "evaluation_completed"  # Evaluation finished


# =============================================================================
# INTEGRITY MANAGER (CANONICAL AUTHORITY)
# =============================================================================


class IntegrityManager:
    """
    Canonical authority for integrity evaluation and monitoring.
    
    This is THE ONE source of truth for runtime integrity. It owns:
    
    - Invariant evaluation
    - Structural verification
    - Ownership verification
    - Dependency verification  
    - Consistency verification
    - Integrity reports
    - Integrity history
    
    Integrity Manager Invariants:
        1. Exactly one per runtime instance
        2. Evaluates independently of health and availability
        3. Never mutates subsystem state directly
        4. Reports are immutable and typed
        5. History preserves provenance
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the IntegrityManager.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
            
        Note: This creates a NEW manager. For singleton behavior,
        use create_integrity_manager() from runtime_monitoring/__init__.py
        """
        self._runtime_id = runtime_id
        
        # Core state
        self._lock = threading.RLock()
        self._evaluations: Dict[str, IntegrityEvaluation] = {}
        self._snapshots: List[IntegritySnapshot] = []
        self._history: List[IntegrityHistoryEntry] = []
        
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
    # Integrity Evaluation (main entry point)
    # -------------------------------------------------------------------------
    
    async def evaluate(
        self,
        subject: str,
        domain_checks: Dict[IntegrityDomain, Callable[[str], Any]],
        timeout_seconds: float = 30.0
    ) -> IntegrityEvaluation:
        """
        Evaluate integrity for a subject across multiple domains.
        
        This is the canonical evaluation method. It:
        1. Executes domain-specific checks sequentially  
        2. Aggregates results deterministically
        3. Produces an immutable IntegrityEvaluation
        
        Args:
            subject: Entity to evaluate (entity ID, component name, etc.)
            domain_checks: Dict mapping domains to check functions
            timeout_seconds: Maximum time for evaluation
            
        Returns:
            Immutable IntegrityEvaluation with complete status
        """
        start_time = time.monotonic()
        self._evaluation_sequence += 1
        
        # Execute domain checks sequentially (to avoid overwhelming)
        findings_by_domain: Dict[IntegrityDomain, List[IntegrityFinding]] = {}
        
        for domain, check_fn in domain_checks.items():
            try:
                result = await asyncio.to_thread(check_fn, subject)
                
                if isinstance(result, bool):
                    finding = (
                        IntegrityFinding.pass_finding("check", domain, "Check passed")
                        if result else
                        IntegrityFinding.fail_finding("check", domain, "Check failed")
                    )
                elif isinstance(result, IntegrityFinding):
                    finding = result
                else:
                    # Default: assume verified
                    finding = IntegrityFinding.pass_finding("check", domain, "Check completed")
                
                findings_by_domain[domain] = [finding]
                
            except Exception as e:
                # Check failed -> violation
                findings_by_domain[domain] = [
                    IntegrityFinding.fail_finding(
                        "check",
                        domain,
                        f"Check error: {type(e).__name__}: {str(e)}"
                    )
                ]
        
        # Create evaluation
        evaluation_duration = time.monotonic() - start_time
        
        evaluation = IntegrityEvaluation.create(
            subject=subject,
            findings_by_domain=findings_by_domain,
            evaluation_duration_seconds=evaluation_duration
        )
        
        # Store evaluation
        with self._lock:
            self._evaluations[subject] = evaluation
            
            # Generate history entry
            prev_eval = self._evaluations.get(subject)
            if prev_eval and prev_eval.overall_status != evaluation.overall_status:
                self._history.append(IntegrityHistoryEntry.status_changed(
                    runtime_id=self._runtime_id,
                    subject=subject,
                    previous_status=prev_eval.overall_status,
                    new_status=evaluation.overall_status
                ))
        
        return evaluation
    
    # -------------------------------------------------------------------------
    # Snapshot Management
    # -------------------------------------------------------------------------
    
    def take_snapshot(self) -> IntegritySnapshot:
        """
        Take a point-in-time snapshot of current integrity state.
        
        Returns:
            Immutable IntegritySnapshot with complete state at moment
        """
        with self._lock:
            self._snapshot_version += 1
            
            previous_id = None
            if self._snapshots:
                previous_id = self._snapshots[-1].snapshot_id
            
            snapshot = IntegritySnapshot.create(
                runtime_id=self._runtime_id,
                evaluations=dict(self._evaluations),
                version=self._snapshot_version,
                previous_snapshot_id=previous_id
            )
            
            self._snapshots.append(snapshot)
            
            # Record history entry
            self._history.append(IntegrityHistoryEntry.snapshot_taken(
                runtime_id=self._runtime_id,
                snapshot_id=snapshot.snapshot_id,
                version=self._snapshot_version
            ))
            
            return snapshot
    
    def get_latest_snapshot(self) -> Optional[IntegritySnapshot]:
        """Get the most recent snapshot, if any."""
        with self._lock:
            if self._snapshots:
                return self._snapshots[-1]
            return None
    
    # -------------------------------------------------------------------------
    # Report Generation
    # -------------------------------------------------------------------------
    
    def generate_report(self, subject: Optional[str] = None) -> IntegrityReport:
        """
        Generate an integrity report for a subject or all subjects.
        
        Args:
            subject: Specific subject to report on (None = all)
            
        Returns:
            Immutable IntegrityReport with current status
        """
        with self._lock:
            if subject is not None and subject in self._evaluations:
                evaluation = self._evaluations[subject]
                return IntegrityReport.create(subject, [evaluation])
            else:
                # Report on all subjects
                evaluations = list(self._evaluations.values())
                return IntegrityReport.create(
                    subject=self._runtime_id,
                    evaluations=evaluations
                )
    
    # -------------------------------------------------------------------------
    # History Queries
    # -------------------------------------------------------------------------
    
    def get_history(self, since_timestamp: Optional[float] = None) -> List[IntegrityHistoryEntry]:
        """
        Get integrity history entries.
        
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
    
    def get_evaluation(self, subject: str) -> Optional[IntegrityEvaluation]:
        """Get the latest evaluation for a subject."""
        with self._lock:
            return self._evaluations.get(subject)
    
    def is_verified(self, subject: str) -> bool:
        """
        Check if a subject's integrity is verified.
        
        This is a convenience method. For production use, prefer
        generate_report() to get full context.
        """
        evaluation = self.get_evaluation(subject)
        return evaluation.is_verified if evaluation else False
    
    def get_overall_status(self) -> IntegrityStatus:
        """Get overall runtime integrity status."""
        with self._lock:
            evaluations = list(self._evaluations.values())
            
            if not evaluations:
                return IntegrityStatus.UNKNOWN
            
            # Most restrictive wins
            for status in (IntegrityStatus.VIOLATED, IntegrityStatus.DEGRADED):
                if any(e.overall_status == status for e in evaluations):
                    return status
            
            return IntegrityStatus.VERIFIED


__all__ = [
    # Runtime Observer Authority
    "RuntimeObserver",
    
    # Severity levels - MUST come first since other classes reference it
    "Severity",
    
    # Status values
    "IntegrityStatus",
    
    # Domain enumeration  
    "IntegrityDomain",
    
    # Models
    "IntegrityViolation",
    "IntegrityFinding",
    "IntegrityCheck",
    "IntegrityEvaluation",
    "IntegrityReport",
    "IntegritySnapshot", 
    "IntegrityHistoryEntry",
    
    # Event types
    "IntegrityEventType",
    
    # Authorities
    "IntegrityManager",
]
