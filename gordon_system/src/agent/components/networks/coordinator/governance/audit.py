# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Audit Framework
=========================================================

Architectural compliance audits and findings.

Following:
* AUDIT-LAW-001 through AUDIT-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# GOVERNANCE AUDIT
# =============================================================================

@dataclass(frozen=True, slots=True)
class GovernanceAudit:
    """
    Immutable audit record.
    
    Audits remain observational - they do not perform actions.
    
    AUDIT-LAW-001: Audits shall remain observational
    AUDIT-LAW-002: Audits shall preserve evidence
    AUDIT-LAW-003: Audit findings shall distinguish facts from recommendations
    AUDIT-LAW-004: Audit scope shall remain explicit
    AUDIT-LAW-005: Audit provenance shall remain complete
    AUDIT-LAW-006: Historical audits shall remain inspectable
    AUDIT-LAW-007: Audit revisions shall preserve lineage
    AUDIT-LAW-008: Audit generation shall remain deterministic
    
    CCG-AUDIT-INV-001: Audit is immutable (deeply frozen)
    CCG-AUDIT-INV-002: Audit has no runtime references
    """
    audit_identity: str
    """Unique identifier for this audit."""
    
    audited_scope: str
    """Scope that was audited."""
    
    governing_rules: tuple[str, ...]
    """Rules used for auditing."""
    
    observations: tuple[str, ...] = field(default_factory=tuple)
    """Audit observations."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Audit findings."""
    
    violations: tuple[str, ...] = field(default_factory=tuple)
    """Violations found."""
    
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    """Recommendations for improvement."""
    
    provenance_ref: str | None = None
    """Reference to audit provenance record."""
    
    @classmethod
    def create(
        cls,
        audit_id: str,
        scope: str,
        rules: tuple[str, ...],
        observations: tuple[str, ...] | None = None,
        findings: tuple[str, ...] | None = None,
        violations: tuple[str, ...] | None = None,
        recommendations: tuple[str, ...] | None = None,
    ) -> GovernanceAudit:
        """
        Create a new audit record.
        
        Args:
            audit_id: Unique identifier
            scope: Scope audited
            rules: Rules applied
            observations: Audit observations
            findings: Findings made
            violations: Violations found
            recommendations: Recommendations
            
        Returns:
            A new GovernanceAudit instance
        """
        return cls(
            audit_identity=audit_id,
            audited_scope=scope,
            governing_rules=rules,
            observations=observations or (),
            findings=findings or (),
            violations=violations or (),
            recommendations=recommendations or (),
            provenance_ref=None,
        )
    
    def get_status(self) -> str:
        """
        Get the audit status.
        
        Returns:
            Audit status string
        """
        if self.violations:
            return "violations_found"
        elif self.findings:
            return "findings_recorded"
        else:
            return "compliant"


# =============================================================================
# AUDIT REPORT
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuditReport:
    """
    Immutable audit report.
    
    CCG-AUDIT-REP-INV-001: Report is immutable
    CCG-AUDIT-REP-INV-002: Report has no runtime references
    
    AUDIT-LAW-003: Findings distinguish facts from recommendations
    """
    audit_identity: str
    """Audit that generated this report."""
    
    audited_scope: str
    """Scope that was audited."""
    
    constitutional_findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings related to constitutional compliance."""
    
    policy_findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings related to policy compliance."""
    
    violations: tuple[str, ...] = field(default_factory=tuple)
    """Violations found."""
    
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    """Recommendations for improvement."""
    
    confidence: float = 1.0
    """Confidence in the audit findings."""
    
    provenance_ref: str | None = None
    """Reference to report provenance record."""
    
    @classmethod
    def of(
        cls,
        audit_id: str,
        scope: str,
        constitutional_findings: tuple[str, ...] | None = None,
        policy_findings: tuple[str, ...] | None = None,
        violations: tuple[str, ...] | None = None,
        recommendations: tuple[str, ...] | None = None,
        confidence: float = 1.0,
    ) -> AuditReport:
        """
        Create an audit report.
        
        Args:
            audit_id: Audit identifier
            scope: Scope audited
            constitutional_findings: Constitutional findings
            policy_findings: Policy findings
            violations: Violations found
            recommendations: Recommendations
            confidence: Confidence level
            
        Returns:
            A new AuditReport instance
        """
        return cls(
            audit_identity=audit_id,
            audited_scope=scope,
            constitutional_findings=constitutional_findings or (),
            policy_findings=policy_findings or (),
            violations=violations or (),
            recommendations=recommendations or (),
            confidence=min(1.0, max(0.0, float(confidence))),
            provenance_ref=None,
        )
    
    def is_compliant(self) -> bool:
        """Check if the audit indicates compliance."""
        return len(self.violations) == 0


# =============================================================================
# AUDIT HISTORY
# =============================================================================

@dataclass(frozen=True, slots=True)
class AuditHistory:
    """
    Immutable history of audits for a scope.
    
    CCG-AUDIT-HIST-INV-001: History is immutable
    CCG-AUDIT-HIST-INV-002: History has no runtime references
    
    AUDIT-LAW-006: Historical audits remain inspectable
    """
    audited_scope: str
    """Scope with audit history."""
    
    audit_records: tuple[GovernanceAudit, ...] = field(default_factory=tuple)
    """Audit records for this scope."""
    
    @classmethod
    def of(
        cls,
        scope: str,
        audits: tuple[GovernanceAudit, ...] | None = None,
    ) -> AuditHistory:
        """
        Create an audit history.
        
        Args:
            scope: Scope with history
            audits: Audit records
            
        Returns:
            A new AuditHistory instance
        """
        return cls(
            audited_scope=scope,
            audit_records=audits or (),
        )
    
    def get_latest_audit(self) -> GovernanceAudit | None:
        """Get the most recent audit."""
        if self.audit_records:
            return self.audit_records[-1]
        return None
    
    def has_violations(self) -> bool:
        """Check if any audit in history found violations."""
        for audit in self.audit_records:
            if audit.violations:
                return True
        return False


# =============================================================================
# AUDIT TYPE REGISTRY
# =============================================================================

class AuditTypeRegistry:
    """
    Registry of audit types.
    
    CCG-AUDIT-REG-INV-001: Registry is immutable
    CCG-AUDIT-REG-INV-002: Registry has no runtime references
    
    AUDIT-LAW-001: Audits remain observational
    """
    
    CONSTITUTION = "constitution"
    """Constitutional audit - checks constitutional compliance."""
    
    AUTHORITY = "authority"
    """Authority audit - checks authority boundaries."""
    
    POLICY = "policy"
    """Policy audit - checks policy compliance."""
    
    TRUST = "trust"
    """Trust domain audit - checks trust enforcement."""
    
    COORDINATION = "coordination"
    """Coordination protocol audit - checks protocol compliance."""
    
    ARCHITECTURE = "architecture"
    """Architecture audit - checks architectural topology."""
    
    SECURITY = "security"
    """Security audit - checks security policies."""
    
    COMPLIANCE = "compliance"
    """General compliance audit."""