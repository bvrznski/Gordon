# Audit Models - Gordon Executive Network Audit Subsystem
# =========================================================

"""
Core data model types for the Executive Audit subsystem.
"""

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Optional, Tuple, Dict, Any, Literal
import time


# =============================================================================
# ID TYPES - Immutable identifiers
# =============================================================================

@dataclass(frozen=True)
class AuditSessionId:
    """Unique identifier for an audit session."""
    
    value: str = field(default_factory=lambda: f"audit_{time.time():.6f}_{hash(id(object())) % 10000:04x}")
    
    @classmethod
    def generate(cls) -> "AuditSessionId":
        return cls()


@dataclass(frozen=True)
class AuditReportId:
    """Unique identifier for an audit report."""
    
    value: str = field(default_factory=lambda: f"report_{time.time():.6f}_{hash(id(object())) % 10000:04x}")
    
    @classmethod
    def generate(cls) -> "AuditReportId":
        return cls()


# =============================================================================
# AUDIT SESSION - A single audit run (moved from __init__.py)
# =============================================================================

@dataclass(frozen=True)
class AuditSession:
    """
    A single audit session with its complete evidence trail.
    
    Sessions are immutable once created. Each session represents one
    complete audit cycle of the executive state.
    """
    
    session_id: str
    """Unique identifier for this audit session."""
    
    timestamp_utc: float
    """Unix timestamp when audit was initiated."""
    
    state_reference: Optional[str]
    """Reference to the executive state that was audited."""
    
    context_reference: Optional[str]
    """Reference to the executive context that was audited."""
    
    status: str  # AuditStatus as string for simplicity in models
    """Current status of this session."""
    
    findings: Tuple[AuditFinding, ...] = field(default_factory=tuple)
    """Findings from this audit session."""
    
    recommendations: Tuple[AuditRecommendation, ...] = field(default_factory=tuple)
    """Recommendations generated during this session."""
    
    evidence: Tuple[AuditEvidence, ...] = field(default_factory=tuple)
    """All evidence collected during this session."""
    
    diagnostics: Optional["AuditDiagnostics"] = None
    """Diagnostic information for this session."""
    
    report: Optional["AuditReport"] = None
    """Final report generated from findings and analysis."""
    
    @classmethod
    def create(
        cls,
        state_reference: Optional[str] = None,
        context_reference: Optional[str] = None,
        timestamp_utc: Optional[float] = None,
    ) -> "AuditSession":
        """
        Create a new audit session with the given references.
        
        Args:
            state_reference: Reference to executive state being audited
            context_reference: Reference to executive context being audited
            timestamp_utc: Unix timestamp (defaults to current time)
            
        Returns:
            New AuditSession instance in PENDING state
        """
        return cls(
            session_id=f"audit_{time.time():.6f}_{hash((state_reference, context_reference)) % 10000:04x}",
            timestamp_utc=timestamp_utc or time.time(),
            state_reference=state_reference,
            context_reference=context_reference,
            status="pending",
        )
    
    def with_status(self, status: str) -> "AuditSession":
        """Return a new session with updated status."""
        return dataclass_replace(self, status=status)
    
    def add_finding(self, finding: "AuditFinding") -> "AuditSession":
        """Add a finding to this session (returns new immutable instance)."""
        return dataclass_replace(
            self, findings=self.findings + (finding,)
        )
    
    def add_recommendation(
        self,
        recommendation: "AuditRecommendation"
    ) -> "AuditSession":
        """Add a recommendation to this session."""
        return dataclass_replace(
            self, recommendations=self.recommendations + (recommendation,)
        )
    
    def add_evidence(self, evidence: "AuditEvidence") -> "AuditSession":
        """Add evidence to this session."""
        return dataclass_replace(
            self, evidence=self.evidence + (evidence,)
        )


# =============================================================================
# EVIDENCE - The raw observations collected during audit
# =============================================================================

@dataclass(frozen=True)
class AuditEvidence:
    """
    Raw evidence collected during an audit session.
    
    Evidence is the foundation of all audit findings. Each piece of evidence
    includes its source, timestamp, value, and context for interpretation.
    """
    
    evidence_id: str
    """Unique identifier for this evidence item."""
    
    timestamp_utc: float
    """Unix timestamp when evidence was collected."""
    
    source_type: str
    """Category of source (e.g., 'state', 'context', 'program')."""
    
    source_id: Optional[str]
    """ID of the specific source component."""
    
    key: str
    """The property or metric being observed."""
    
    value: Any
    """The observed value."""
    
    expected_value: Optional[Any] = None
    """Expected value for comparison (if applicable)."""
    
    deviation_score: float = 0.0
    """How much this evidence deviates from expectations (0-1)."""
    
    context: Dict[str, Any] = field(default_factory=dict)
    """Additional context for interpreting the evidence."""
    
    @classmethod
    def create(
        cls,
        source_type: str,
        key: str,
        value: Any,
        timestamp_utc: Optional[float] = None,
        source_id: Optional[str] = None,
        expected_value: Optional[Any] = None,
    ) -> "AuditEvidence":
        """Create a new evidence item."""
        return cls(
            evidence_id=f"evidence_{time.time():.6f}_{hash((source_type, key, value)) % 10000:04x}",
            timestamp_utc=timestamp_utc or time.time(),
            source_type=source_type,
            source_id=source_id,
            key=key,
            value=value,
            expected_value=expected_value,
        )
    
    @property
    def is_anomalous(self) -> bool:
        """Check if this evidence indicates anomalous behavior."""
        return self.deviation_score > 0.5


# =============================================================================
# FINDING - A discovered issue during audit
# =============================================================================

@dataclass(frozen=True)
class AuditFinding:
    """
    A finding discovered during an audit session.
    
    Findings represent specific issues or anomalies detected in the executive
    state. Each finding includes severity, evidence trail, and description.
    """
    
    finding_id: str
    """Unique identifier for this finding."""
    
    timestamp_utc: float
    """Unix timestamp when finding was recorded."""
    
    kind: str
    """Category of finding (from FindingKind enum value)."""
    
    severity: Literal["critical", "high", "medium", "low", "info"]
    """Severity level of the finding."""
    
    description: str
    """Human-readable description of the issue."""
    
    evidence_ids: Tuple[str, ...]
    """IDs of evidence that support this finding."""
    
    affected_component: Optional[str] = None
    """Component or subsystem affected by this finding."""
    
    recommendation_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of recommendations to address this finding."""
    
    confidence_score: float = 1.0
    """Confidence in the finding's accuracy (0-1)."""
    
    @classmethod
    def create(
        cls,
        kind: str,
        severity: Literal["critical", "high", "medium", "low", "info"],
        description: str,
        evidence_ids: Tuple[str, ...] = (),
        timestamp_utc: Optional[float] = None,
    ) -> "AuditFinding":
        """Create a new finding."""
        return cls(
            finding_id=f"finding_{time.time():.6f}_{hash((kind, severity, description)) % 10000:04x}",
            timestamp_utc=timestamp_utc or time.time(),
            kind=kind,
            severity=severity,
            description=description,
            evidence_ids=evidence_ids,
            confidence_score=0.95 if severity in ("critical", "high") else 0.85,
        )
    
    @property
    def is_critical(self) -> bool:
        """Check if finding is critical severity."""
        return self.severity == "critical"
    
    @property
    def severity_score(self) -> float:
        """Get numeric score for severity (0-1)."""
        scores = {"critical": 1.0, "high": 0.85, "medium": 0.60, "low": 0.35, "info": 0.15}
        return scores.get(self.severity, 0.0)


# =============================================================================
# RECOMMENDATION - Suggested action to address a finding
# =============================================================================

@dataclass(frozen=True)
class AuditRecommendation:
    """
    A recommendation generated during an audit session.
    
    Recommendations are advisory suggestions for how to address findings.
    They never execute automatically - downstream systems decide whether
    and how to apply them.
    """
    
    recommendation_id: str
    """Unique identifier for this recommendation."""
    
    timestamp_utc: float
    """Unix timestamp when recommendation was generated."""
    
    kind: str
    """Category of recommendation (from RecommendationKind enum value)."""
    
    description: str
    """Human-readable explanation of the recommended action."""
    
    finding_ids: Tuple[str, ...]
    """IDs of findings this recommendation addresses."""
    
    rationale: Optional[str] = None
    """Rationale for why this recommendation was made."""
    
    priority: Literal["urgent", "high", "medium", "low"] = "medium"
    """Priority level for implementation."""
    
    estimated_impact: Literal["positive", "neutral", "negative"] = "positive"
    """Expected impact of implementing this recommendation."""
    
    @classmethod
    def create(
        cls,
        kind: str,
        description: str,
        finding_ids: Tuple[str, ...] = (),
        timestamp_utc: Optional[float] = None,
        rationale: Optional[str] = None,
    ) -> "AuditRecommendation":
        """Create a new recommendation."""
        return cls(
            recommendation_id=f"recommendation_{time.time():.6f}_{hash((kind, description)) % 10000:04x}",
            timestamp_utc=timestamp_utc or time.time(),
            kind=kind,
            description=description,
            finding_ids=finding_ids,
            rationale=rationale,
            priority="high" if "critical" in [f.severity for f in finding_ids] else "medium",
        )
    
    @property
    def is_urgent(self) -> bool:
        """Check if recommendation requires immediate attention."""
        return self.priority == "urgent"


# =============================================================================
# REPORT - Summary of an audit session's results
# =============================================================================

@dataclass(frozen=True)
class AuditReport:
    """
    A summary report generated from an audit session.
    
    Reports provide a structured view of findings, recommendations,
    risk assessment, and overall audit quality for the session.
    """
    
    report_id: str
    """Unique identifier for this report."""
    
    timestamp_utc: float
    """Unix timestamp when report was generated."""
    
    session_id: str
    """ID of the audit session this report summarizes."""
    
    status: Literal["completed", "degraded", "failed"]
    """Overall audit session status."""
    
    summary: Dict[str, Any]
    """Summary statistics and key findings."""
    
    findings_summary: Dict[str, int]
    """Counts of findings by severity level."""
    
    risk_score: int
    """Overall risk score (0-100)."""
    
    risk_level: Literal["negligible", "low", "medium", "high"]
    """Overall risk assessment level."""
    
    recommendations_count: int
    """Number of recommendations in this session."""
    
    evidence_count: int
    """Number of evidence items collected."""
    
    audit_type: str = "scheduled"
    """Type of audit that generated this report."""
    
    degradation_info: Optional[Dict[str, Any]] = None
    """Information about degraded functionality if applicable."""
    
    @classmethod
    def create(
        cls,
        session_id: str,
        status: Literal["completed", "degraded", "failed"],
        findings_summary: Dict[str, int],
        risk_score: int,
        recommendations_count: int = 0,
        evidence_count: int = 0,
        timestamp_utc: Optional[float] = None,
    ) -> "AuditReport":
        """Create a new audit report."""
        # Determine risk level based on score
        if risk_score >= 80:
            risk_level = "high"
        elif risk_score >= 50:
            risk_level = "medium"
        elif risk_score > 0:
            risk_level = "low"
        else:
            risk_level = "negligible"
        
        return cls(
            report_id=f"report_{time.time():.6f}_{hash((session_id, status)) % 10000:04x}",
            timestamp_utc=timestamp_utc or time.time(),
            session_id=session_id,
            status=status,
            summary={
                "timestamp": timestamp_utc or time.time(),
                "audit_type": "scheduled",
                "overall_assessment": "healthy" if risk_score < 50 else "attention_required"
            },
            findings_summary=findings_summary,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations_count=recommendations_count,
            evidence_count=evidence_count,
        )
    
    @property
    def needs_attention(self) -> bool:
        """Check if this report indicates the executive requires attention."""
        return self.risk_score >= 50 or self.status == "degraded"


# =============================================================================
# HEALTH - Current health status of the audit subsystem
# =============================================================================

@dataclass(frozen=True)
class AuditHealth:
    """
    Health status of the audit subsystem.
    
    This provides a snapshot of the audit engine's operational status,
    including any degradation, error rates, and component availability.
    """
    
    status: Literal["healthy", "degraded", "unavailable"]
    """Overall health status."""
    
    last_audit_utc: Optional[float]
    """Unix timestamp of last completed audit (if any)."""
    
    failure_count: int = 0
    """Count of consecutive failures."""
    
    degradation_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons for degradation if applicable."""
    
    component_health: Dict[str, Literal["available", "unavailable"]] = field(
        default_factory=dict
    )
    """Health status of individual components."""
    
    @classmethod
    def healthy(cls) -> "AuditHealth":
        """Create a healthy health status."""
        return cls(status="healthy", last_audit_utc=None)
    
    @classmethod
    def degraded(cls, reasons: Tuple[str, ...] = ()) -> "AuditHealth":
        """Create a degraded health status."""
        return cls(
            status="degraded",
            last_audit_utc=None,
            degradation_reasons=reasons,
        )
    
    @classmethod
    def unavailable(cls) -> "AuditHealth":
        """Create an unavailable health status."""
        return cls(status="unavailable", last_audit_utc=None)
    
    @property
    def is_operational(self) -> bool:
        """Check if the audit subsystem can operate."""
        return self.status != "unavailable"


# =============================================================================
# METRICS - Statistics from completed audit sessions
# =============================================================================

@dataclass(frozen=True)
class AuditMetrics:
    """
    Metrics from completed audit sessions.
    
    This provides aggregated statistics about audit activity, including
    counts of findings by category and severity, average session duration,
    and other relevant metrics.
    """
    
    total_sessions: int = 0
    """Total number of audit sessions run."""
    
    successful_sessions: int = 0
    """Number of sessions completed successfully."""
    
    failed_sessions: int = 0
    """Number of sessions that failed."""
    
    degraded_sessions: int = 0
    """Number of sessions with degraded functionality."""
    
    total_findings: int = 0
    """Total findings across all sessions."""
    
    findings_by_kind: Dict[str, int] = field(default_factory=dict)
    """Counts of findings grouped by kind."""
    
    findings_by_severity: Dict[str, int] = field(default_factory=dict)
    """Counts of findings grouped by severity level."""
    
    average_session_duration_seconds: float = 0.0
    """Average duration of audit sessions in seconds."""
    
    total_recommendations: int = 0
    """Total recommendations generated across all sessions."""
    
    @classmethod
    def initial(cls) -> "AuditMetrics":
        """Create initial metrics with zero counts."""
        return cls()


# =============================================================================
# DIAGNOSTICS - Diagnostic information about audit process
# =============================================================================

@dataclass(frozen=True)
class AuditDiagnostics:
    """
    Diagnostic information about an audit session.
    
    This provides detailed timing, resource usage, and other diagnostic
    data about the audit process for debugging and performance analysis.
    """
    
    session_id: str
    """ID of the audited session."""
    
    start_time_utc: float
    """Unix timestamp when audit started."""
    
    end_time_utc: Optional[float] = None
    """Unix timestamp when audit ended (if completed)."""
    
    state_collection_seconds: float = 0.0
    """Time spent collecting state data."""
    
    evidence_collection_seconds: float = 0.0
    """Time spent collecting evidence."""
    
    analysis_seconds: float = 0.0
    """Time spent analyzing findings."""
    
    recommendation_seconds: float = 0.0
    """Time spent generating recommendations."""
    
    report_generation_seconds: float = 0.0
    """Time spent generating report."""
    
    components_queried: Tuple[str, ...] = field(default_factory=tuple)
    """Components that were queried during audit."""
    
    errors_encountered: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Errors encountered during audit (if any)."""
    
    warnings_encountered: Tuple[str, ...] = field(default_factory=tuple)
    """Warnings encountered during audit."""
    
    @classmethod
    def create(cls, session_id: str) -> "AuditDiagnostics":
        """Create a new diagnostics object starting at current time."""
        return cls(session_id=session_id, start_time_utc=time.time())
    
    @property
    def total_seconds(self) -> float:
        """Get total audit duration in seconds."""
        if self.end_time_utc:
            return self.end_time_utc - self.start_time_utc
        return time.time() - self.start_time_utc
    
    @property
    def has_errors(self) -> bool:
        """Check if any errors were encountered."""
        return len(self.errors_encountered) > 0