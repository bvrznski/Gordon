# Memory Audit Factories - Phase 5.1.9
# ======================================

"""
Factory functions for creating audit components.

These factories provide a consistent interface for constructing:
    - Audit requests
    - Audit sessions
    - Findings and reports
"""

from __future__ import annotations

import uuid
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import field

# Import core modules (runtime to avoid circular deps)
try:
    from .enums import (
        AuditTypes,
        AuditCertificationStatus,
        MemoryDomains,
        ValidationState,
    )
    from .models import (
        MemoryAuditRequest,
        MemoryAuditSession,
        MemoryAuditReport,
        AuditFinding,
        HealthAssessment,
        HealthMetric,
    )
except ImportError:
    pass


# =============================================================================
# REQUEST FACTORIES
# =============================================================================


def create_audit_request(
    audit_type: AuditTypes = AuditTypes.FULL_SYSTEM_AUDIT,
    domains: Optional[Tuple[MemoryDomains, ...]] = None,
    target_ids: Optional[Tuple[str, ...]] = None,
    validate_lineage: bool = True,
    validate_provenance: bool = True,
    check_references: bool = True,
    depth: str = "full",
) -> MemoryAuditRequest:
    """
    Create a new audit request with default or specified parameters.
    
    Args:
        audit_type: Type of audit to perform
        domains: Which memory domains to audit (None = all canonical domains)
        target_ids: Specific artifact IDs to audit (None = all)
        validate_lineage: Check lineage completeness?
        validate_provenance: Check provenance completeness?
        check_references: Check for broken references?
        depth: Audit depth level
        
    Returns:
        New MemoryAuditRequest instance
    """
    if domains is None:
        # Default to all canonical memory domains
        try:
            from .enums import MemoryDomains
            domains = tuple(MemoryDomains)
        except ImportError:
            domains = ()
    
    return MemoryAuditRequest(
        request_id=f"request:{uuid.uuid4().hex[:16]}",
        audit_type=audit_type,
        domains=domains,
        target_ids=target_ids,
        validate_lineage=validate_lineage,
        validate_provenance=validate_provenance,
        check_references=check_references,
        depth=depth,
    )


def create_health_check_request(
    target_ids: Optional[Tuple[str, ...]] = None,
) -> MemoryAuditRequest:
    """
    Create a quick health check request.
    
    Args:
        target_ids: Specific artifacts to check (None = all)
        
    Returns:
        Health check audit request
    """
    return create_audit_request(
        audit_type=AuditTypes.HEALTH_CHECK,
        target_ids=target_ids,
        depth="basic",
        validate_lineage=False,  # Skip detailed lineage for speed
        validate_provenance=False,  # Skip detailed provenance for speed
        check_references=True,  # Check references is fast
    )


def create_structural_audit_request(
    domains: Optional[Tuple[MemoryDomains, ...]] = None,
) -> MemoryAuditRequest:
    """Create a structural audit request."""
    return create_audit_request(
        audit_type=AuditTypes.STRUCTURAL_AUDIT,
        domains=domains,
        validate_lineage=False,
        validate_provenance=False,
        check_references=True,
    )


# =============================================================================
# SESSION FACTORIES
# =============================================================================


def create_audit_session(
    request: MemoryAuditRequest,
) -> MemoryAuditSession:
    """
    Create a new audit session for an audit request.
    
    Args:
        request: The audit request to execute
        
    Returns:
        New MemoryAuditSession in PLANNING phase
    """
    try:
        from .enums import AuditPhases
    except ImportError:
        AuditPhases = None
    
    return MemoryAuditSession(
        session_id=f"session:{uuid.uuid4().hex[:16]}",
        request=request,
        current_phase=AuditPhases.PLANNING if AuditPhases else "planning",  # Use default from dataclass
    )


# =============================================================================
# FINDING FACTORIES
# =============================================================================


def create_finding(
    validation_type: str,
    state: ValidationState,
    severity: Optional[str] = None,
    location: str = "unknown",
    description: str = "",
    evidence: Tuple[str, ...] = (),
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditFinding:
    """
    Create a new audit finding.
    
    Args:
        validation_type: Type of validation performed
        state: Validation result (PASSED, FAILED, etc.)
        severity: Severity level (optional)
        location: Where the issue was found
        description: Human-readable description
        evidence: Supporting evidence for this finding
        metadata: Additional context
        
    Returns:
        New AuditFinding instance
    """
    return AuditFinding(
        finding_id=f"finding:{uuid.uuid4().hex[:16]}",
        validation_type=validation_type,
        state=state,
        severity=_get_severity(state, severity),
        location=location,
        description=description,
        evidence=evidence,
        metadata=dict(metadata) if metadata else {},
    )


def _get_severity(
    state: ValidationState,
    explicit_severity: Optional[str] = None,
) -> str:
    """Get severity based on state and optional explicit value."""
    # Map states to default severities
    state_to_severity = {
        ValidationState.FAILED: "error",
        ValidationState.WARNING: "warning",
        ValidationState.PASSED: "info",
    }
    
    if explicit_severity:
        return explicit_severity
    
    return state_to_severity.get(state, "info")


def create_critical_finding(
    validation_type: str,
    location: str,
    description: str,
    evidence: Tuple[str, ...] = (),
) -> AuditFinding:
    """Create a critical severity finding."""
    return create_finding(
        validation_type=validation_type,
        state=ValidationState.FAILED,
        severity="critical",
        location=location,
        description=description,
        evidence=evidence,
    )


def create_error_finding(
    validation_type: str,
    location: str,
    description: str,
    evidence: Tuple[str, ...] = (),
) -> AuditFinding:
    """Create an error severity finding."""
    return create_finding(
        validation_type=validation_type,
        state=ValidationState.FAILED,
        severity="error",
        location=location,
        description=description,
        evidence=evidence,
    )


def create_warning_finding(
    validation_type: str,
    location: str,
    description: str,
    evidence: Tuple[str, ...] = (),
) -> AuditFinding:
    """Create a warning severity finding."""
    return create_finding(
        validation_type=validation_type,
        state=ValidationState.WARNING,
        severity="warning",
        location=location,
        description=description,
        evidence=evidence,
    )


# =============================================================================
# HEALTH ASSESSMENT FACTORIES
# =============================================================================


def create_health_metric(
    name: str,
    value: float,
    threshold: float = 0.8,
    unit: str = "",
    description: str = "",
) -> HealthMetric:
    """
    Create a health metric.
    
    Args:
        name: Metric identifier
        value: Current value (0.0-1.0)
        threshold: Minimum acceptable value
        unit: Measurement unit
        description: Human-readable description
        
    Returns:
        New HealthMetric instance
    """
    # Determine state based on value and threshold
    if value >= threshold:
        state = ValidationState.PASSED
    elif value >= threshold * 0.5:
        state = ValidationState.WARNING
    else:
        state = ValidationState.FAILED
    
    return HealthMetric(
        name=name,
        value=value,
        threshold=threshold,
        state=state,
        unit=unit,
        description=description,
    )


def create_health_assessment(
    adapter_metrics: Tuple[HealthMetric, ...] = (),
    validation_metrics: Tuple[HealthMetric, ...] = (),
    lineage_metrics: Tuple[HealthMetric, ...] = (),
    provenance_metrics: Tuple[HealthMetric, ...] = (),
    retrieval_metrics: Tuple[HealthMetric, ...] = (),
    index_metrics: Tuple[HealthMetric, ...] = (),
) -> HealthAssessment:
    """
    Create a health assessment from component metrics.
    
    Args:
        adapter_metrics: Adapter accessibility metrics
        validation_metrics: Validation result ratios
        lineage_metrics: Lineage completeness metrics
        provenance_metrics: Provenance completeness metrics
        retrieval_metrics: Retrieval performance metrics
        index_metrics: Index health metrics
        
    Returns:
        New HealthAssessment instance
    """
    # Determine overall state
    all_metrics = (
        adapter_metrics + validation_metrics + lineage_metrics +
        provenance_metrics + retrieval_metrics + index_metrics
    )
    
    if not all_metrics:
        return HealthAssessment(
            overall_state=ValidationState.PASSED,
            adapter_health=adapter_metrics,
            validation_health=validation_metrics,
            lineage_health=lineage_metrics,
            provenance_health=provenance_metrics,
            retrieval_health=retrieval_metrics,
            index_health=index_metrics,
            timestamp_utc=time.time(),
        )
    
    # Check for failures and warnings
    has_critical = any(m.state == ValidationState.FAILED for m in all_metrics)
    has_warning = any(m.state == ValidationState.WARNING for m in all_metrics)
    
    if has_critical:
        overall_state = ValidationState.FAILED
    elif has_warning:
        overall_state = ValidationState.WARNING
    else:
        overall_state = ValidationState.PASSED
    
    return HealthAssessment(
        overall_state=overall_state,
        adapter_health=adapter_metrics,
        validation_health=validation_metrics,
        lineage_health=lineage_metrics,
        provenance_health=provenance_metrics,
        retrieval_health=retrieval_metrics,
        index_health=index_metrics,
        timestamp_utc=time.time(),
    )


# =============================================================================
# REPORT FACTORIES
# =============================================================================


def create_audit_report(
    session: MemoryAuditSession,
    findings: Tuple[AuditFinding, ...] = (),
    health_assessment: Optional[HealthAssessment] = None,
    recommendations: Tuple[str, ...] = (),
) -> MemoryAuditReport:
    """
    Create an audit report from a completed session.
    
    Args:
        session: Completed audit session
        findings: Audit findings (overrides session.findings if provided)
        health_assessment: Optional health assessment
        recommendations: List of recommendations
        
    Returns:
        New MemoryAuditReport instance
    """
    effective_findings = findings if findings else session.findings
    
    return MemoryAuditReport.create(
        session=session,
        health_assessment=health_assessment,
        recommendations=recommendations or (),
    )


__all__ = [
    # Request factories
    "create_audit_request",
    "create_health_check_request",
    "create_structural_audit_request",
    # Session factories
    "create_audit_session",
    # Finding factories
    "create_finding",
    "create_critical_finding",
    "create_error_finding",
    "create_warning_finding",
    # Health factories
    "create_health_metric",
    "create_health_assessment",
    # Report factories
    "create_audit_report",
]