# Core Diagnostics Manager
# ========================

"""
Diagnostics collection and reporting infrastructure for Gordon.

This module provides:
- DiagnosticsManager: Canonical authority for diagnostics
- Diagnostic report generation
- Snapshot capture
- Runtime state analysis

Diagnostics are OBSERVATIONAL - they never change runtime behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import threading
import time
import uuid

from .models import LogContext


# =============================================================================
# DIAGNOSTIC SEVERITY
# =============================================================================

class DiagnosticSeverity(Enum):
    """
    Severity levels for diagnostic records.
    
    Ordering (lowest to highest): TRACE < DEBUG < INFO < NOTICE < 
                                  WARNING < ERROR < CRITICAL
    """
    
    TRACE = auto()        # Internal details (rarely shown)
    DEBUG = auto()        # Detailed debugging information
    INFO = auto()         # Notable diagnostic events
    NOTICE = auto()       # Important milestones
    WARNING = auto()      # Potential issues
    ERROR = auto()        # Actual errors requiring attention
    CRITICAL = auto()     # System-impacting conditions


@dataclass(frozen=True)
class DiagnosticFinding:
    """
    A single diagnostic finding.
    
    Represents one observed issue or notable state in the runtime.
    """
    
    finding_id: str
    source: str                  # Component that generated this finding
    
    severity: DiagnosticSeverity
    code: str                    # Machine-readable code (e.g., "CPU_HIGH")
    
    title: str                   # Human-readable summary
    description: str = ""        # Detailed explanation
    
    # Evidence and context
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp_utc: float = field(default_factory=time.time)
    
    # Resolution information
    is_resolved: bool = False
    resolved_at: Optional[float] = None
    resolution_notes: str = ""
    
    @property
    def is_critical(self) -> bool:
        """Check if this finding is critical."""
        return self.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.CRITICAL)
    
    def resolve(
        self,
        notes: str = "",
        resolved_at: Optional[float] = None
    ) -> "DiagnosticFinding":
        """Return a copy marked as resolved."""
        return DiagnosticFinding(
            finding_id=self.finding_id,
            source=self.source,
            severity=self.severity,
            code=self.code,
            title=self.title,
            description=self.description,
            evidence=dict(self.evidence),
            timestamp_utc=self.timestamp_utc,
            is_resolved=True,
            resolved_at=resolved_at or time.time(),
            resolution_notes=notes
        )


@dataclass(frozen=True)
class DiagnosticReport:
    """
    A complete diagnostic report for a specific scope.
    
    Contains multiple findings and summary information.
    """
    
    report_id: str
    subject: str                 # What this report is about
    
    timestamp_utc: float = field(default_factory=time.time)
    duration_seconds: float = 0.0
    
    # Findings
    findings: List[DiagnosticFinding] = field(default_factory=list)
    
    @property
    def count(self) -> int:
        """Return total number of findings."""
        return len(self.findings)
    
    @property
    def critical_count(self) -> bool:
        """Return count of critical findings."""
        return sum(1 for f in self.findings if f.is_critical)
    
    @property
    def has_issues(self) -> bool:
        """Check if report contains any issues."""
        return len(self.findings) > 0
    
    def get_by_severity(self, severity: DiagnosticSeverity) -> List[DiagnosticFinding]:
        """Get all findings with the specified severity."""
        return [f for f in self.findings if f.severity == severity]
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert report to JSON-serializable dictionary."""
        return {
            "report_id": self.report_id,
            "subject": self.subject,
            "timestamp_utc": self.timestamp_utc,
            "duration_seconds": self.duration_seconds,
            "count": len(self.findings),
            "critical_count": self.critical_count,
            "has_issues": self.has_issues,
            "findings": [f.to_dict() if hasattr(f, 'to_dict') else {
                "finding_id": f.finding_id,
                "source": f.source,
                "severity": f.severity.name,
                "code": f.code,
                "title": f.title,
                "description": f.description,
                "evidence": f.evidence,
                "is_resolved": f.is_resolved,
            } for f in self.findings]
        }


# =============================================================================
# DIAGNOSTICS MANAGER
# =============================================================================

class DiagnosticsManager:
    """
    Canonical authority for diagnostics collection and reporting.
    
    Provides:
        - Diagnostic finding generation
        - Report creation and management
        - Runtime state snapshots
    
    INVAR: Exactly one DiagnosticsManager exists per runtime.
    INVAR: Diagnostics never mutate runtime behavior.
    
    Usage:
        # Create manager (runtime-scoped)
        manager = DiagnosticsManager(runtime_id="runtime_123")
        
        # Generate findings
        manager.finding(
            source="cpu_monitor",
            code="CPU_HIGH",
            severity=DiagnosticSeverity.WARNING,
            title="High CPU usage detected",
            value=current_cpu_usage
        )
        
        # Get report for specific scope
        report = manager.get_report("runtime")
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
        max_findings_per_scope: int = 1000,
        retention_seconds: float = 3600.0,  # 1 hour default
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        self._max_findings = max(max_findings_per_scope, 100)
        self._retention_seconds = retention_seconds
        
        # Thread-safe state
        self._lock = threading.RLock()
        
        # Findings by scope
        self._findings: Dict[str, List[DiagnosticFinding]] = {}
        
        # Report cache
        self._reports: Dict[str, DiagnosticReport] = {}
        
        # Statistics
        self._total_findings_generated = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    def _get_scope_findings(self, scope: str) -> List[DiagnosticFinding]:
        """Get or create findings list for a scope."""
        if scope not in self._findings:
            self._findings[scope] = []
        return self._findings[scope]
    
    # ------------------------------------------------------------------
    # Finding Generation
    # ------------------------------------------------------------------
    
    def finding(
        self,
        source: str,
        code: str,
        severity: DiagnosticSeverity,
        title: str,
        description: str = "",
        **evidence
    ) -> DiagnosticFinding:
        """
        Generate a diagnostic finding.
        
        Args:
            source: Component that generated the finding
            code: Machine-readable code for this finding type
            severity: Severity level of the finding
            title: Human-readable summary
            description: Detailed explanation (optional)
            **evidence: Additional data supporting the finding
            
        Returns:
            Generated DiagnosticFinding instance
        """
        finding_id = f"diag_{uuid.uuid4().hex[:12]}"
        
        finding = DiagnosticFinding(
            finding_id=finding_id,
            source=source,
            severity=severity,
            code=code,
            title=title,
            description=description,
            evidence=evidence,
            timestamp_utc=time.time()
        )
        
        # Store in findings (bounded by scope)
        with self._lock:
            scope_findings = self._get_scope_findings("runtime")
            
            # Enforce limit - remove oldest if needed
            while len(scope_findings) >= self._max_findings:
                scope_findings.pop(0)
            
            scope_findings.append(finding)
            self._total_findings_generated += 1
        
        return finding
    
    def info(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> DiagnosticFinding:
        """Generate an INFO-level diagnostic finding."""
        return self.finding(
            source=source,
            code=code,
            severity=DiagnosticSeverity.INFO,
            title=title,
            **evidence
        )
    
    def warning(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> DiagnosticFinding:
        """Generate a WARNING-level diagnostic finding."""
        return self.finding(
            source=source,
            code=code,
            severity=DiagnosticSeverity.WARNING,
            title=title,
            **evidence
        )
    
    def error(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> DiagnosticFinding:
        """Generate an ERROR-level diagnostic finding."""
        return self.finding(
            source=source,
            code=code,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            **evidence
        )
    
    def critical(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> DiagnosticFinding:
        """Generate a CRITICAL-level diagnostic finding."""
        return self.finding(
            source=source,
            code=code,
            severity=DiagnosticSeverity.CRITICAL,
            title=title,
            **evidence
        )
    
    # ------------------------------------------------------------------
    # Report Generation
    # ------------------------------------------------------------------
    
    def get_report(self, subject: str) -> DiagnosticReport:
        """
        Get a diagnostic report for a specific subject.
        
        Args:
            subject: What to generate report for (runtime, task, etc.)
            
        Returns:
            DiagnosticReport with findings for this subject
        """
        with self._lock:
            # Get findings for this scope
            scope_findings = self._get_scope_findings(subject)
            
            # Clean expired findings
            cutoff = time.time() - self._retention_seconds
            valid_findings = [
                f for f in scope_findings 
                if f.timestamp_utc > cutoff
            ]
            
            report_id = f"report_{uuid.uuid4().hex[:12]}"
            
            return DiagnosticReport(
                report_id=report_id,
                subject=subject,
                timestamp_utc=time.time(),
                findings=list(valid_findings)
            )
    
    def get_runtime_report(self) -> DiagnosticReport:
        """Get a diagnostic report for the entire runtime."""
        return self.get_report("runtime")
    
    # ------------------------------------------------------------------
    # Snapshot Capture
    # ------------------------------------------------------------------
    
    @dataclass(frozen=True)
    class RuntimeSnapshot:
        """Immutable snapshot of runtime diagnostics at a point in time."""
        
        runtime_id: str
        timestamp_utc: float
        
        total_findings: int = 0
        critical_count: int = 0
        warning_count: int = 0
        info_count: int = 0
        
        # By source
        findings_by_source: Dict[str, int] = field(default_factory=dict)
        
        # Status summary
        status: str = "healthy"  # healthy, degraded, critical
    
    def capture_snapshot(self) -> RuntimeSnapshot:
        """
        Capture a snapshot of current diagnostic state.
        
        Returns:
            RuntimeSnapshot with all current diagnostics
        """
        with self._lock:
            now = time.time()
            cutoff = now - self._retention_seconds
            
            # Collect valid findings across all scopes
            all_findings: List[DiagnosticFinding] = []
            
            for scope, findings in self._findings.items():
                valid = [f for f in findings if f.timestamp_utc > cutoff]
                all_findings.extend(valid)
            
            # Count by severity and source
            critical_count = sum(1 for f in all_findings if f.severity == DiagnosticSeverity.CRITICAL)
            warning_count = sum(1 for f in all_findings if f.severity == DiagnosticSeverity.WARNING)
            info_count = sum(1 for f in all_findings if f.severity == DiagnosticSeverity.INFO)
            
            source_counts: Dict[str, int] = {}
            for f in all_findings:
                source_counts[f.source] = source_counts.get(f.source, 0) + 1
            
            # Determine status
            if critical_count > 0:
                status = "critical"
            elif warning_count > 5:  # Multiple warnings indicates degradation
                status = "degraded"
            else:
                status = "healthy"
            
            return self.RuntimeSnapshot(
                runtime_id=self._runtime_id,
                timestamp_utc=now,
                total_findings=len(all_findings),
                critical_count=critical_count,
                warning_count=warning_count,
                info_count=info_count,
                findings_by_source=source_counts,
                status=status
            )
    
    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------
    
    def get_findings(
        self,
        scope: str = "runtime",
        severity: Optional[DiagnosticSeverity] = None,
        source: Optional[str] = None,
    ) -> List[DiagnosticFinding]:
        """
        Get findings filtered by criteria.
        
        Args:
            scope: Scope to search (default: runtime)
            severity: Filter by severity (optional)
            source: Filter by source component (optional)
            
        Returns:
            List of matching findings
        """
        with self._lock:
            scope_findings = self._get_scope_findings(scope)
            
            result = list(scope_findings)
            
            if severity is not None:
                result = [f for f in result if f.severity == severity]
            
            if source is not None:
                result = [f for f in result if f.source == source]
            
            return result
    
    def get_critical_findings(self, scope: str = "runtime") -> List[DiagnosticFinding]:
        """Get all critical findings in a scope."""
        return self.get_findings(scope=scope, severity=DiagnosticSeverity.CRITICAL)
    
    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    
    def clear(self, scope: Optional[str] = None) -> None:
        """
        Clear diagnostic findings.
        
        Args:
            scope: Scope to clear (None clears all)
        """
        with self._lock:
            if scope is None:
                self._findings.clear()
            elif scope in self._findings:
                del self._findings[scope]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get diagnostic statistics."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "total_findings_generated": self._total_findings_generated,
                "scopes_with_findings": len(self._findings),
                "report_cache_size": len(self._reports),
            }


# =============================================================================
# BUILT-IN DIAGNOSTIC SOURCES
# =============================================================================

class ResourceDiagnostics:
    """Resource utilization diagnostics."""
    
    @staticmethod
    def cpu_high(value: float, threshold: float) -> DiagnosticFinding:
        return DiagnosticFinding(
            finding_id="",
            source="resource_monitor",
            severity=DiagnosticSeverity.WARNING,
            code="CPU_HIGH",
            title="High CPU usage detected",
            description=f"CPU utilization ({value:.1%}) exceeds threshold ({threshold:.1%})",
            evidence={"cpu_usage": value, "threshold": threshold}
        )
    
    @staticmethod
    def memory_high(value: float, threshold: float) -> DiagnosticFinding:
        return DiagnosticFinding(
            finding_id="",
            source="resource_monitor",
            severity=DiagnosticSeverity.WARNING,
            code="MEMORY_HIGH",
            title="High memory usage detected",
            description=f"Memory utilization ({value:.1%}) exceeds threshold ({threshold:.1%})",
            evidence={"memory_usage": value, "threshold": threshold}
        )
    
    @staticmethod
    def disk_full(value: float, threshold: float) -> DiagnosticFinding:
        return DiagnosticFinding(
            finding_id="",
            source="resource_monitor",
            severity=DiagnosticSeverity.ERROR,
            code="DISK_FULL",
            title="Disk space critical",
            description=f"Disk usage ({value:.1%}) exceeds threshold ({threshold:.1%})",
            evidence={"disk_usage": value, "threshold": threshold}
        )


class SystemDiagnostics:
    """System-level diagnostics."""
    
    @staticmethod
    def thread_pool_exhausted(active: int, max_threads: int) -> DiagnosticFinding:
        return DiagnosticFinding(
            finding_id="",
            source="thread_pool",
            severity=DiagnosticSeverity.WARNING,
            code="THREAD_POOL_EXHAUSTED",
            title="Thread pool near exhaustion",
            description=f"Active threads ({active}) approaching limit ({max_threads})",
            evidence={"active_threads": active, "max_threads": max_threads}
        )
    
    @staticmethod
    def queue_overflow(name: str, depth: int, max_depth: int) -> DiagnosticFinding:
        return DiagnosticFinding(
            finding_id="",
            source="queue_monitor",
            severity=DiagnosticSeverity.WARNING,
            code="QUEUE_OVERFLOW",
            title="Queue overflow detected",
            description=f"Queue '{name}' depth ({depth}) exceeds limit ({max_depth})",
            evidence={"queue": name, "depth": depth, "max_depth": max_depth}
        )


__all__ = [
    "DiagnosticSeverity",
    "DiagnosticFinding",
    "DiagnosticReport",
    "DiagnosticsManager",
    "ResourceDiagnostics",
    "SystemDiagnostics",
]