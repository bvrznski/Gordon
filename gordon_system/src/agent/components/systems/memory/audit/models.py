# Memory Audit Models - Phase 5.1.9
# ====================================

"""
Core data models for Memory Audit operations.

These models define the immutable structures used throughout the audit subsystem:
    - MemoryAuditRequest: Input parameters for an audit
    - MemoryAuditSession: State management for a single audit run
    - MemoryAuditReport: Immutable audit findings report
    - AuditFinding: Individual finding from validation analysis
    - HealthAssessment: Aggregated health metrics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import time
import uuid

# Import enums (runtime to avoid circular deps)
try:
    from .enums import (
        AuditTypes,
        AuditCertificationStatus,
        FindingSeverity,
        MemoryDomains,
        ValidationState,
        ReferenceType,
        DataIntegrityState,
        AuditPhases,
    )
except ImportError:
    pass


# =============================================================================
# AUDIT FINDING - Individual validation result
# =============================================================================


@dataclass(frozen=True)
class AuditFinding:
    """
    Individual finding from an audit validation.
    
    Each AuditFinding represents a single observation during the audit process:
        - What was checked (validation_type)
        - Whether it passed or failed (state)
        - Severity level for prioritization
        - Description of the issue (if any)
        - Location/context where found
    
    AuditFindings are immutable and always include evidence for reproducibility.
    
    Fields:
        finding_id:         Unique identifier for this finding
        validation_type:    Type of validation performed
        state:             Validation result state
        severity:          How critical is this finding?
        
        location:          Where was the issue found? (artifact ID, path, etc.)
        description:       Human-readable description of the finding
        
        metadata:          Additional context and diagnostic data
        
        timestamp_utc:     When finding was recorded
        
    Properties:
        is_issue:           True if this represents an actual problem
        is_critical:        True if severity is CRITICAL
    """
    
    # Identity and classification
    finding_id: str                           # Unique identifier
    validation_type: str                      # What was validated?
    state: ValidationState                    # PASSED, FAILED, WARNING, etc.
    severity: FindingSeverity                 # How critical?
    
    # Location and description
    location: str                             # Artifact ID, path, or context
    description: str                          # Human-readable description
    
    # Evidence and metadata
    evidence: Tuple[str, ...] = field(default_factory=tuple)  # Supporting data
    metadata: Dict[str, Any] = field(default_factory=dict)    # Additional context
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_issue(self) -> bool:
        """Check if this finding represents an actual problem."""
        return self.state in (ValidationState.FAILED, ValidationState.WARNING)
    
    @property
    def is_critical(self) -> bool:
        """Check if severity is CRITICAL."""
        return self.severity == FindingSeverity.CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary representation."""
        return {
            "finding_id": self.finding_id,
            "validation_type": self.validation_type,
            "state": self.state.value if isinstance(self.state, Enum) else str(self.state),
            "severity": self.severity.value if isinstance(self.severity, Enum) else str(self.severity),
            "location": self.location,
            "description": self.description,
            "evidence": list(self.evidence),
            "metadata": dict(self.metadata),
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# HEALTH METRIC - Single health measurement
# =============================================================================


@dataclass(frozen=True)
class HealthMetric:
    """
    Single metric in a health assessment.
    
    Fields:
        name:              Metric name
        value:             Numeric value (0.0-1.0 typically)
        threshold:         Minimum acceptable value
        state:             HEALTHY, WARNING, CRITICAL
        
        unit:              Units of measurement
        description:       What this metric measures
        
        timestamp_utc:     When metric was captured
    """
    
    name: str                                 # Metric identifier
    value: float                             # Current value
    threshold: float = 0.8                   # Minimum acceptable (0.0-1.0)
    state: ValidationState = ValidationState.PASSED
    
    unit: str = ""                           # Measurement unit
    description: str = ""                    # Human-readable description
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_healthy(self) -> bool:
        """Check if metric meets threshold."""
        return self.value >= self.threshold and self.state == ValidationState.PASSED


# =============================================================================
# HEALTH ASSESSMENT - Aggregated health metrics
# =============================================================================


@dataclass(frozen=True)
class HealthAssessment:
    """
    Aggregated health assessment from audit.
    
    Health is computed from multiple sources:
        - Adapter health: Can adapters access memory?
        - Validation health: How many validations passed?
        - Lineage health: Is lineage complete and valid?
        - Provenance health: Is provenance complete?
        - Retrieval health: Are retrievals working?
        - Index health: Are indexes valid?
    
    Health Assessment Rules:
        - All metrics healthy = OVERALL_HEALTHY
        - Some warnings, no failures = DEGRADED
        - Any critical failure = UNHEALTHY
    
    Fields:
        overall_state:      Aggregated state (healthy/warning/critical)
        
        adapter_health:     Adapter accessibility metrics
        validation_health:  Validation result ratios
        lineage_health:     Lineage completeness metrics
        provenance_health:  Provenance completeness metrics
        retrieval_health:   Retrieval performance metrics
        index_health:       Index health metrics
        
        recent_failures:    List of recent failure descriptions
        timestamp_utc:      When assessment was computed
    
    Properties:
        is_healthy:         True if all metrics pass threshold
        has_warnings:       True if any metric is in warning state
        critical_count:     Number of critical failures
    """
    
    # Overall assessment
    overall_state: ValidationState = ValidationState.PASSED
    
    # Component health metrics
    adapter_health: Tuple[HealthMetric, ...] = field(default_factory=tuple)
    validation_health: Tuple[HealthMetric, ...] = field(default_factory=tuple)
    lineage_health: Tuple[HealthMetric, ...] = field(default_factory=tuple)
    provenance_health: Tuple[HealthMetric, ...] = field(default_factory=tuple)
    retrieval_health: Tuple[HealthMetric, ...] = field(default_factory=tuple)
    index_health: Tuple[HealthMetric, ...] = field(default_factory=tuple)
    
    # Failure tracking
    recent_failures: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_healthy(self) -> bool:
        """Check if overall assessment is healthy."""
        return self.overall_state == ValidationState.PASSED
    
    @property
    def has_warnings(self) -> bool:
        """Check if any component has warnings."""
        for metrics in (self.adapter_health, self.validation_health,
                       self.lineage_health, self.provenance_health,
                       self.retrieval_health, self.index_health):
            for m in metrics:
                if m.state == ValidationState.WARNING:
                    return True
        return False
    
    @property
    def critical_count(self) -> int:
        """Count of critical failures across all components."""
        count = 0
        for metrics in (self.adapter_health, self.validation_health,
                       self.lineage_health, self.provenance_health,
                       self.retrieval_health, self.index_health):
            for m in metrics:
                if m.state == ValidationState.FAILED and m.value < m.threshold * 0.5:
                    count += 1
        return count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health assessment to dictionary."""
        return {
            "overall_state": self.overall_state.value,
            "adapter_health": [m.to_dict() for m in self.adapter_health],
            "validation_health": [m.to_dict() for m in self.validation_health],
            "lineage_health": [m.to_dict() for m in self.lineage_health],
            "provenance_health": [m.to_dict() for m in self.provenance_health],
            "retrieval_health": [m.to_dict() for m in self.retrieval_health],
            "index_health": [m.to_dict() for m in self.index_health],
            "recent_failures": list(self.recent_failures),
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# MEMORY AUDIT REQUEST - Input parameters for audit
# =============================================================================


@dataclass(frozen=True)
class MemoryAuditRequest:
    """
    Request to perform a memory audit.
    
    Fields:
        request_id:         Unique identifier for this audit request
        
        audit_type:         What type of audit to perform (all, structural, integrity, etc.)
        domains:           Which memory domains to audit
        target_ids:        Specific memory IDs to audit (None = all)
        
        # Validation options
        validate_lineage:   Check lineage completeness?
        validate_provenance: Check provenance completeness?
        check_references:   Check for broken references?
        
        # Depth options
        depth:             Audit depth level (basic, extended, full)
        
        # Timing options
        timestamp_utc:      When request was made
        
    Properties:
        is_full_system:     True if this is a full system audit
        has_targets:        True if specific targets were specified
    
    Anti-Patterns Rejected:
        - Mutable requests (use copy_with to create modified versions)
        - Requests without audit types
    """
    
    # Request identification
    request_id: str                           # Unique identifier
    
    # Audit specification
    audit_type: AuditTypes                    # What type of audit?
    domains: Tuple[MemoryDomains, ...] = field(default_factory=tuple)  # Which domains
    
    # Target selection
    target_ids: Optional[Tuple[str, ...]] = None  # Specific IDs to audit
    
    # Validation scope
    validate_lineage: bool = True             # Check lineage?
    validate_provenance: bool = True          # Check provenance?
    check_references: bool = True             # Check references?
    
    # Depth level
    depth: str = "full"                       # basic, extended, full
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_full_system(self) -> bool:
        """Check if this is a full system audit."""
        return self.audit_type in (AuditTypes.FULL_SYSTEM_AUDIT, AuditTypes.HEALTH_CHECK)
    
    @property
    def has_targets(self) -> bool:
        """Check if specific targets were specified."""
        return self.target_ids is not None and len(self.target_ids) > 0
    
    def copy_with(
        self,
        **kwargs,
    ) -> "MemoryAuditRequest":
        """
        Create a modified copy of this request.
        
        Args:
            **kwargs: Fields to override
            
        Returns:
            New MemoryAuditRequest with updated fields
        """
        return dataclass_replace(self, **kwargs)


# =============================================================================
# MEMORY AUDIT SESSION - State for single audit run
# =============================================================================


@dataclass(frozen=True)
class MemoryAuditSession:
    """
    Session managing a single audit execution.
    
    The session tracks the state of an audit as it progresses through phases:
        PLANNING → SNAPSHOT → VALIDATION → ANALYSIS → HEALTH → REPORTING
    
    Each session produces exactly one report at completion.
    
    Fields:
        session_id:         Unique identifier for this session
        request:           Original audit request
        
        current_phase:      Current phase of execution
        start_time_utc:     When session started
        
        snapshot_time_utc:  When memory was snapshotted (if applicable)
        
        findings:          All findings collected during audit
        health_metrics:    Collected health metrics
        
        errors:            Errors encountered during audit
        warnings:          Warnings encountered during audit
        
    Properties:
        is_complete:        True if session has completed
        is_failed:          True if session failed
        finding_count:      Total number of findings
        critical_count:     Number of critical findings
    
    Anti-Patterns Rejected:
        - Sessions that never complete
        - Sessions that modify original request
        - Sessions without unique identifiers
    """
    
    # Session identification
    session_id: str                           # Unique identifier
    
    # Audit specification
    request: MemoryAuditRequest               # Original request
    
    # Execution state
    current_phase: AuditPhases = AuditPhases.PLANNING
    start_time_utc: float = field(default_factory=time.time)
    
    snapshot_time_utc: Optional[float] = None  # When snapshot was taken
    
    # Audit results
    findings: Tuple[AuditFinding, ...] = field(default_factory=tuple)
    health_metrics: Tuple[HealthMetric, ...] = field(default_factory=tuple)
    
    # Execution state
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_complete(self) -> bool:
        """Check if session has completed."""
        return self.current_phase == AuditPhases.REPORTING
    
    @property
    def is_failed(self) -> bool:
        """Check if session encountered errors."""
        return len(self.errors) > 0 or any(
            f.state == ValidationState.FAILED for f in self.findings
        )
    
    @property
    def finding_count(self) -> int:
        """Get total number of findings."""
        return len(self.findings)
    
    @property
    def critical_count(self) -> bool:
        """Get number of critical findings."""
        return sum(1 for f in self.findings if f.is_critical)
    
    @property
    def failure_count(self) -> int:
        """Get number of failed findings."""
        return sum(1 for f in self.findings if f.state == ValidationState.FAILED)
    
    @property
    def warning_count(self) -> int:
        """Get number of warnings."""
        return len(self.warnings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session state to dictionary."""
        return {
            "session_id": self.session_id,
            "request": self.request.to_dict(),
            "current_phase": self.current_phase.value,
            "start_time_utc": self.start_time_utc,
            "snapshot_time_utc": self.snapshot_time_utc,
            "finding_count": len(self.findings),
            "critical_count": self.critical_count,
            "failure_count": self.failure_count,
            "warning_count": len(self.warnings),
            "is_complete": self.is_complete,
            "is_failed": self.is_failed,
        }


# =============================================================================
# MEMORY AUDIT REPORT - Immutable audit findings report
# =============================================================================


@dataclass(frozen=True)
class MemoryAuditReport:
    """
    Immutable audit findings report.
    
    Every audit produces exactly one MemoryAuditReport. Reports are:
        - Immutable (never modified after creation)
        - Timestamped for reproducibility
        - Complete with all findings and context
    
    Report Structure:
        
        Summary:
            report_id, timestamp_utc, audit_type, domains_audited
            
        Findings:
            findings: All individual audit findings
            critical_count, warning_count, failure_count
            
        Health Assessment:
            health_assessment: Aggregated health metrics
            certification_status: Overall certification result
            
        Validation Details:
            lineage_validations: Lineage-specific findings
            provenance_validations: Provenance-specific findings
            integrity_validations: Integrity-specific findings
            
        Recommendations:
            recommendations: Suggested improvements
            
    Anti-Patterns Rejected:
        - Mutable reports
        - Reports without timestamps
        - Reports that hide findings
    """
    
    # Report identification
    report_id: str                            # Unique identifier
    timestamp_utc: float                      # When report was generated
    
    # Audit specification
    audit_type: AuditTypes                    # What type of audit?
    domains_audited: Tuple[MemoryDomains, ...] = field(default_factory=tuple)
    
    # Session context
    session_id: str = ""                      # Which session produced this?
    request_id: str = ""                      # Original request ID
    
    # Findings summary
    findings: Tuple[AuditFinding, ...] = field(default_factory=tuple)  # All findings
    critical_count: int = 0                   # Critical findings count
    warning_count: int = 0                    # Warning findings count
    failure_count: int = 0                    # Failed findings count
    info_count: int = 0                       # Info findings count
    
    # Health assessment
    health_assessment: Optional[HealthAssessment] = None
    certification_status: AuditCertificationStatus = AuditCertificationStatus.CERTIFIED
    
    # Validation breakdowns
    lineage_validations: Tuple[AuditFinding, ...] = field(default_factory=tuple)
    provenance_validations: Tuple[AuditFinding, ...] = field(default_factory=tuple)
    integrity_validations: Tuple[AuditFinding, ...] = field(default_factory=tuple)
    reference_validations: Tuple[AuditFinding, ...] = field(default_factory=tuple)
    
    # Recommendations
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Diagnostics
    duration_seconds: float = 0.0             # Total audit duration
    
    def __post_init__(self):
        """Compute derived fields after initialization."""
        # Recompute counts from findings tuple
        object.__setattr__(self, 'critical_count', 
                          sum(1 for f in self.findings if f.severity == FindingSeverity.CRITICAL))
        object.__setattr__(self, 'warning_count',
                          sum(1 for f in self.findings if f.state == ValidationState.WARNING))
        object.__setattr__(self, 'failure_count',
                          sum(1 for f in self.findings if f.state == ValidationState.FAILED))
        object.__setattr__(self, 'info_count',
                          sum(1 for f in self.findings if f.severity == FindingSeverity.INFO))
        
        # Update certification based on findings
        if len(self.findings) == 0:
            object.__setattr__(self, 'certification_status', AuditCertificationStatus.CERTIFIED)
        elif self.critical_count > 0 or self.failure_count > 0:
            object.__setattr__(self, 'certification_status', AuditCertificationStatus.FAILED)
        elif self.warning_count > 0:
            object.__setattr__(self, 'certification_status', AuditCertificationStatus.CERTIFIED_WITH_WARNINGS)
    
    @property
    def is_certified(self) -> bool:
        """Check if memory passed certification."""
        return self.certification_status in (
            AuditCertificationStatus.CERTIFIED,
            AuditCertificationStatus.CERTIFIED_WITH_WARNINGS,
        )
    
    @property
    def has_findings(self) -> bool:
        """Check if any findings were recorded."""
        return len(self.findings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            "report_id": self.report_id,
            "timestamp_utc": self.timestamp_utc,
            "audit_type": self.audit_type.value if isinstance(self.audit_type, Enum) else str(self.audit_type),
            "domains_audited": [d.value for d in self.domains_audited],
            "session_id": self.session_id,
            "request_id": self.request_id,
            "findings_count": len(self.findings),
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "failure_count": self.failure_count,
            "info_count": self.info_count,
            "is_certified": self.is_certified,
            "certification_status": self.certification_status.value if isinstance(self.certification_status, Enum) else str(self.certification_status),
            "recommendations": list(self.recommendations),
        }
    
    @classmethod
    def create(
        cls,
        session: MemoryAuditSession,
        health_assessment: Optional[HealthAssessment] = None,
        certification_status: Optional[AuditCertificationStatus] = None,
        recommendations: Optional[Tuple[str, ...]] = None,
    ) -> "MemoryAuditReport":
        """
        Create a MemoryAuditReport from a session.
        
        Args:
            session: The completed audit session
            health_assessment: Optional health assessment
            certification_status: Optional certification result
            recommendations: Optional list of recommendations
            
        Returns:
            New MemoryAuditReport with findings from session
        """
        # Generate report ID
        import hashlib
        report_id = f"report:{hashlib.md5(str(session.start_time_utc).encode()).hexdigest()[:16]}"
        
        return cls(
            report_id=report_id,
            timestamp_utc=time.time(),
            audit_type=session.request.audit_type,
            domains_audited=session.request.domains,
            session_id=session.session_id,
            request_id=session.request.request_id,
            findings=session.findings,
            health_assessment=health_assessment,
            certification_status=certification_status or AuditCertificationStatus.CERTIFIED,
            recommendations=recommendations or (),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass, returning new instance.
    
    Args:
        instance: The dataclass instance to modify
        **kwargs: Fields to override
        
    Returns:
        New instance with updated fields
    """
    import dataclasses
    
    if not dataclasses.is_dataclass(instance):
        raise TypeError("dataclass_replace requires a dataclass instance")
    
    return dataclasses.replace(instance, **kwargs)


__all__ = [
    # Core models
    "AuditFinding",
    "HealthMetric",
    "HealthAssessment",
    "MemoryAuditRequest",
    "MemoryAuditSession",
    "MemoryAuditReport",
    # Utility functions
    "dataclass_replace",
]