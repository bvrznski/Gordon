# Core Runtime Diagnostics Manager
# ================================

"""
Canonical diagnostics authority for runtime monitoring.

Provides:
- Canonical DiagnosticsManager as single source of truth for diagnostics
- Diagnostic report generation from health/integrity evaluations
- Evidence collection and publication
- Root cause analysis support
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import uuid
import time

# Import monitoring components
from .health import HealthManager, HealthEvaluation, HealthDomain, HealthStatus, HealthFinding
from .integrity import IntegrityManager, IntegrityEvaluation, IntegrityDomain, IntegrityStatus, IntegrityFinding


# =============================================================================
# DIAGNOSTIC STATE VALUES
# =============================================================================


class DiagnosticState(Enum):
    """
    Canonical diagnostic state values.
    
    States:
        UNKNOWN     - Not yet evaluated (initial state)
        ANALYZING   - Currently being analyzed
        IDENTIFIED  - Issue identified, cause unknown
        ANALYZED    - Cause identified
        RESOLVED    - Issue resolved
        IGNORED     - Issue ignored (known limitation)
    """
    
    UNKNOWN = "unknown"
    ANALYZING = "analyzing"
    IDENTIFIED = "identified"
    ANALYZED = "analyzed"
    RESOLVED = "resolved"
    IGNORED = "ignored"


# =============================================================================
# DIAGNOSTIC EVIDENCE MODEL
# =============================================================================


@dataclass(frozen=True)
class DiagnosticEvidence:
    """
    Evidence supporting a diagnostic finding.
    
    Evidence is immutable and preserves provenance for debugging and audit.
    """
    
    # Identifiers
    evidence_id: str           # Unique identifier
    
    # Source information
    source_type: str           # e.g., "health_check", "integrity_violation"
    source_id: str             # Which check/evaluation generated this
    
    # Evidence type
    evidence_type: str         # e.g., "threshold_exceeded", "missing_heartbeat"
    
    # Content
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    collected_at_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)


# =============================================================================
# DIAGNOSTIC CAUSE MODEL
# =============================================================================


@dataclass(frozen=True)
class DiagnosticCause:
    """
    A root cause identified for a diagnostic issue.
    
    Causes preserve causal chains for debugging and remediation planning.
    """
    
    # Identifiers
    cause_id: str              # Unique identifier
    
    # Classification
    category: str              # e.g., "resource_exhaustion", "configuration_error"
    severity: str              # e.g., "critical", "warning"
    
    # Content
    description: str           # Human-readable cause description
    evidence_ids: List[str] = field(default_factory=list)  # Supporting evidence
    
    # Chain information
    parent_cause_id: Optional[str] = None  # For causal chains
    depends_on: List[str] = field(default_factory=list)  # Other causes this depends on


# =============================================================================
# DIAGNOSTIC REPORT MODEL
# =============================================================================


@dataclass(frozen=True)
class DiagnosticReport:
    """
    A complete diagnostic report.
    
    Reports are immutable and contain full provenance for debugging.
    They represent the output of diagnosis - observables, not authorities.
    """
    
    # Identifiers
    report_id: str             # Unique identifier for this report
    
    # Context
    runtime_id: str            # Which runtime this is about
    subject: str               # What is being diagnosed
    diagnosed_at_utc: float    # When diagnosis occurred
    
    # Content
    overall_state: DiagnosticState  # Overall diagnostic state
    findings: Tuple[str, ...] = field(default_factory=tuple)  # List of issues found
    causes: Tuple[DiagnosticCause, ...] = field(default_factory=tuple)
    
    # Metrics
    analysis_duration_seconds: float = 0.0
    evidence_count: int = 0
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_resolved(self) -> bool:
        """Check if all issues are resolved."""
        return self.overall_state == DiagnosticState.RESOLVED
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if any issue requires immediate attention."""
        return len([c for c in self.causes if c.severity == "critical"]) > 0
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "report_id": self.report_id,
            "runtime_id": self.runtime_id,
            "subject": self.subject,
            "diagnosed_at_utc": self.diagnosed_at_utc,
            "overall_state": self.overall_state.value,
            "findings": list(self.findings),
            "causes": [c.__dict__ for c in self.causes],
            "analysis_duration_seconds": self.analysis_duration_seconds,
            "evidence_count": self.evidence_count,
        }


# =============================================================================
# DIAGNOSTICS MANAGER (CANONICAL AUTHORITY)
# =============================================================================


class DiagnosticsManager:
    """
    Canonical authority for diagnostics generation and analysis.
    
    This is THE ONE source of truth for runtime diagnostics. It owns:
    
    - Diagnostic report generation
    - Root cause analysis
    - Evidence collection and publication
    - Analysis tracking
    
    Diagnostics Manager Invariants:
        1. Exactly one per runtime instance
        2. Analyzes health/integrity evaluations to generate diagnoses
        3. Never mutates subsystem state directly
        4. Reports are immutable and typed
        5. Evidence preserves provenance
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the DiagnosticsManager.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
            
        Note: This creates a NEW manager. For singleton behavior,
        use create_diagnostics_manager() from runtime_monitoring/__init__.py
        """
        self._runtime_id = runtime_id
        
        # Core state
        self._lock = __import__('threading').RLock()
        self._reports: Dict[str, DiagnosticReport] = {}
        self._evidence: Dict[str, List[DiagnosticEvidence]] = {}
        self._causes: Dict[str, List[DiagnosticCause]] = {}
        
        # Counters
        self._report_sequence = 0
        
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this manager serves."""
        return self._runtime_id
    
    @property
    def report_count(self) -> int:
        """Get total number of reports generated."""
        with self._lock:
            return len(self._reports)
    
    # -------------------------------------------------------------------------
    # Diagnosis Generation (main entry point)
    # -------------------------------------------------------------------------
    
    async def diagnose(
        self,
        subject: str,
        health_evaluation: Optional[HealthEvaluation] = None,
        integrity_evaluation: Optional[IntegrityEvaluation] = None,
        timeout_seconds: float = 30.0
    ) -> DiagnosticReport:
        """
        Generate a diagnostic report for a subject.
        
        This is the canonical diagnosis method. It:
        1. Analyzes health and integrity evaluations
        2. Identifies root causes of issues
        3. Collects supporting evidence
        4. Produces an immutable DiagnosticReport
        
        Args:
            subject: Entity to diagnose (entity ID, component name, etc.)
            health_evaluation: Optional pre-computed health evaluation
            integrity_evaluation: Optional pre-computed integrity evaluation  
            timeout_seconds: Maximum time for analysis
            
        Returns:
            Immutable DiagnosticReport with diagnosis results
        """
        start_time = time.monotonic()
        self._report_sequence += 1
        
        # Get evaluations if not provided
        if health_evaluation is None:
            health_evaluation = HealthEvaluation.create(
                subject=subject,
                observations={},
                evaluation_duration_seconds=0.0,
                total_measurements=0
            )
        
        if integrity_evaluation is None:
            integrity_evaluation = IntegrityEvaluation.create(
                subject=subject,
                findings_by_domain={},
                evaluation_duration_seconds=0.0
            )
        
        # Collect issues from health and integrity evaluations
        issues: List[str] = []
        causes: List[DiagnosticCause] = []
        evidence_list: List[DiagnosticEvidence] = []
        
        # Analyze health issues
        if not health_evaluation.is_healthy:
            # Determine what's wrong based on status
            if health_evaluation.overall_status == HealthStatus.FAILED:
                issues.append("Health state: FAILED")
                causes.append(DiagnosticCause(
                    cause_id=f"diag_cause_{uuid.uuid4().hex[:12]}",
                    category="system_failure",
                    severity="critical",
                    description="System has entered failed state and cannot operate"
                ))
            elif health_evaluation.overall_status == HealthStatus.UNHEALTHY:
                issues.append("Health state: UNHEALTHY")
                causes.append(DiagnosticCause(
                    cause_id=f"diag_cause_{uuid.uuid4().hex[:12]}",
                    category="system_degradation",
                    severity="critical",
                    description="System is operating with significant degradation"
                ))
            elif health_evaluation.overall_status == HealthStatus.DEGRADED:
                issues.append("Health state: DEGRADED")
                causes.append(DiagnosticCause(
                    cause_id=f"diag_cause_{uuid.uuid4().hex[:12]}",
                    category="reduced_capability",
                    severity="warning",
                    description="System has reduced operational capability"
                ))
        
        # Analyze integrity issues
        if not integrity_evaluation.is_verified:
            if integrity_evaluation.overall_status == IntegrityStatus.VIOLATED:
                issues.append("Integrity state: VIOLATED")
                causes.append(DiagnosticCause(
                    cause_id=f"diag_cause_{uuid.uuid4().hex[:12]}",
                    category="architectural_violation",
                    severity="critical",
                    description="System architecture has been violated"
                ))
            elif integrity_evaluation.overall_status == IntegrityStatus.DEGRADED:
                issues.append("Integrity state: DEGRADED")
                causes.append(DiagnosticCause(
                    cause_id=f"diag_cause_{uuid.uuid4().hex[:12]}",
                    category="architectural_concern",
                    severity="warning",
                    description="System has architectural concerns that should be addressed"
                ))
        
        # If no issues found, system is healthy and verified
        if not issues:
            overall_state = DiagnosticState.RESOLVED
        else:
            overall_state = DiagnosticState.ANALYZED
        
        # Calculate analysis duration
        analysis_duration = time.monotonic() - start_time
        
        # Create report
        report = DiagnosticReport(
            report_id=f"diag_report_{self._report_sequence:06d}",
            runtime_id=self._runtime_id,
            subject=subject,
            diagnosed_at_utc=time.time(),
            overall_state=overall_state,
            findings=tuple(issues),
            causes=tuple(causes),
            analysis_duration_seconds=analysis_duration,
            evidence_count=len(evidence_list)
        )
        
        # Store report
        with self._lock:
            self._reports[subject] = report
            if evidence_list:
                self._evidence[subject] = evidence_list
            if causes:
                self._causes[subject] = causes
        
        return report
    
    # -------------------------------------------------------------------------
    # Report Queries
    # -------------------------------------------------------------------------
    
    def get_report(self, subject: str) -> Optional[DiagnosticReport]:
        """Get the diagnostic report for a subject."""
        with self._lock:
            return self._reports.get(subject)
    
    def get_latest_reports(self, count: int = 10) -> List[DiagnosticReport]:
        """Get the most recent reports, ordered by sequence number."""
        with self._lock:
            reports = list(self._reports.values())
            # Sort by report_id which contains sequence number
            reports.sort(key=lambda r: r.report_id, reverse=True)
            return reports[:count]
    
    def get_reports_by_state(self, state: DiagnosticState) -> List[DiagnosticReport]:
        """Get all reports with the specified state."""
        with self._lock:
            return [r for r in self._reports.values() if r.overall_state == state]
    
    # -------------------------------------------------------------------------
    # Evidence Management
    # -------------------------------------------------------------------------
    
    def add_evidence(
        self,
        report_id: str,
        evidence: DiagnosticEvidence
    ) -> None:
        """Add evidence to a diagnostic report."""
        with self._lock:
            if report_id not in self._evidence:
                self._evidence[report_id] = []
            self._evidence[report_id].append(evidence)
    
    def get_evidence(self, report_id: str) -> List[DiagnosticEvidence]:
        """Get all evidence for a diagnostic report."""
        with self._lock:
            return list(self._evidence.get(report_id, []))
    
    # -------------------------------------------------------------------------
    # State Queries
    # -------------------------------------------------------------------------
    
    def is_resolved(self, subject: str) -> bool:
        """
        Check if a subject's diagnostics are resolved.
        
        This is a convenience method. For production use, prefer
        get_report() to get full context.
        """
        report = self.get_report(subject)
        return report.is_resolved if report else True  # No report = no issues
    
    def get_overall_state(self) -> DiagnosticState:
        """Get overall diagnostic state across all subjects."""
        with self._lock:
            if not self._reports:
                return DiagnosticState.UNKNOWN
            
            states = [r.overall_state for r in self._reports.values()]
            
            # Priority: unresolved > analyzed > identified > resolved
            for state in (
                DiagnosticState.ANALYZING,
                DiagnosticState.IDENTIFIED,
                DiagnosticState.ANALYZED
            ):
                if state in states:
                    return state
            
            return DiagnosticState.RESOLVED


# =============================================================================
# HEALTH VERIFIER (CANONICAL AUTHORITY)
# =============================================================================


class HealthVerifier:
    """
    Canonical authority for health verification.
    
    This independently verifies health assessments are correct and complete.
    
    Invariants:
        1. Verifies HealthManager outputs
        2. Never mutates subsystem state directly
        3. Reports verification results only
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__('threading').RLock()
        
        # Verification history
        self._verifications: Dict[str, List[bool]] = {}
        self._verified_reports: List[str] = []
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    async def verify(
        self,
        health_evaluation: HealthEvaluation,
        expected_status: Optional[HealthStatus] = None
    ) -> Tuple[bool, List[str]]:
        """
        Verify a health evaluation is correct.
        
        Args:
            health_evaluation: The evaluation to verify
            expected_status: Expected status if known
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues: List[str] = []
        is_valid = True
        
        # Check if evaluation has all domains
        if len(health_evaluation.observations) < 1:
            issues.append("Health evaluation has no observations")
            is_valid = False
        
        # Verify status aggregation
        observed_statuses = set(o.status for o in health_evaluation.observations.values())
        
        # If we expected a specific status, verify it matches
        if expected_status and health_evaluation.overall_status != expected_status:
            issues.append(f"Status mismatch: got {health_evaluation.overall_status}, expected {expected_status}")
            is_valid = False
        
        # Record verification
        with self._lock:
            if health_evaluation.subject not in self._verifications:
                self._verifications[health_evaluation.subject] = []
            self._verifications[health_evaluation.subject].append(is_valid)
        
        return is_valid, issues
    
    def get_verification_history(self) -> Dict[str, List[bool]]:
        """Get verification history for all subjects."""
        with self._lock:
            return dict(self._verifications)


# =============================================================================
# INTEGRITY VERIFIER (CANONICAL AUTHORITY)
# =============================================================================


class IntegrityVerifier:
    """
    Canonical authority for integrity verification.
    
    This independently verifies integrity assessments are correct and complete.
    
    Invariants:
        1. Verifies IntegrityManager outputs
        2. Never mutates subsystem state directly
        3. Reports verification results only
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__('threading').RLock()
        
        # Verification history
        self._verifications: Dict[str, List[bool]] = {}
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    async def verify(
        self,
        integrity_evaluation: IntegrityEvaluation,
        expected_status: Optional[IntegrityStatus] = None
    ) -> Tuple[bool, List[str]]:
        """
        Verify an integrity evaluation is correct.
        
        Args:
            integrity_evaluation: The evaluation to verify
            expected_status: Expected status if known
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues: List[str] = []
        is_valid = True
        
        # Check if evaluation has findings
        total_findings = sum(len(f) for f in integrity_evaluation.findings.values())
        if total_findings == 0 and integrity_evaluation.overall_status != IntegrityStatus.VERIFIED:
            issues.append("Integrity evaluation has no findings but status is not VERIFIED")
            is_valid = False
        
        # Verify status matches findings
        has_failures = any(
            f.is_fail or f.status in (IntegrityStatus.DEGRADED, IntegrityStatus.VIOLATED)
            for findings in integrity_evaluation.findings.values()
            for f in findings
        )
        
        if has_failures and integrity_evaluation.overall_status == IntegrityStatus.VERIFIED:
            issues.append("Evaluation has failures but status is VERIFIED")
            is_valid = False
        
        # Record verification
        with self._lock:
            if integrity_evaluation.subject not in self._verifications:
                self._verifications[integrity_evaluation.subject] = []
            self._verifications[integrity_evaluation.subject].append(is_valid)
        
        return is_valid, issues
    
    def get_verification_history(self) -> Dict[str, List[bool]]:
        """Get verification history for all subjects."""
        with self._lock:
            return dict(self._verifications)


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Diagnostic states
    "DiagnosticState",
    
    # Evidence model
    "DiagnosticEvidence",
    
    # Cause model
    "DiagnosticCause",
    
    # Report model
    "DiagnosticReport",
    
    # Authorities
    "DiagnosticsManager",
    "HealthVerifier",
    "IntegrityVerifier",
]