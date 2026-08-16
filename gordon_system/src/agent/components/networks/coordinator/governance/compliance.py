# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Compliance Evaluation
===============================================================

Constitutional compliance evaluation and violation tracking.

Following:
* COMPLIANCE-LAW-001 through COMPLIANCE-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# COMPLIANCE EVALUATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ComplianceEvaluation:
    """
    Immutable compliance evaluation result.
    
    COMPLIANCE-LAW-001: Every evaluated artifact references governing principles
    COMPLIANCE-LAW-002: Compliance preserves supporting evidence
    COMPLIANCE-LAW-003: Violations shall remain explicit
    COMPLIANCE-LAW-004: Compliance confidence shall remain explicit
    COMPLIANCE-LAW-005: Compliance limitations shall remain explicit
    COMPLIANCE-LAW-006: Compliance provenance shall remain complete
    COMPLIANCE-LAW-007: Historical compliance evaluations shall remain inspectable
    COMPLIANCE-LAW-008: Compliance evaluation shall remain deterministic
    
    CCG-COMP-EVAL-INV-001: Evaluation is immutable
    CCG-COMP-EVAL-INV-002: Evaluation has no runtime references
    """
    evaluated_artifact: str
    """Reference to the artifact being evaluated."""
    
    governing_rules: tuple[str, ...]
    """Rules used for evaluation."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Evaluation findings."""
    
    violations: tuple[str, ...] = field(default_factory=tuple)
    """Any violations found."""
    
    confidence: float = 1.0
    """Confidence in the evaluation (0.0 to 1.0)."""
    
    provenance_ref: str | None = None
    """Reference to evaluation provenance record."""
    
    @classmethod
    def evaluate(
        cls,
        artifact: str,
        rules: tuple[str, ...],
        findings: tuple[str, ...] | None = None,
        violations: tuple[str, ...] | None = None,
        confidence: float = 1.0,
    ) -> ComplianceEvaluation:
        """
        Create a compliance evaluation.
        
        Args:
            artifact: Artifact being evaluated
            rules: Rules applied
            findings: Evaluation findings
            violations: Any violations found
            confidence: Confidence level
            
        Returns:
            A new ComplianceEvaluation instance
        """
        return cls(
            evaluated_artifact=artifact,
            governing_rules=rules,
            findings=findings or (),
            violations=violations or (),
            confidence=min(1.0, max(0.0, float(confidence))),
            provenance_ref=None,
        )
    
    def get_status(self) -> str:
        """
        Get the compliance status based on evaluation.
        
        Returns:
            Compliance status string
        """
        if not self.violations and self.confidence >= 0.95:
            return "compliant"
        elif not self.violations:
            return "conditionally_compliant"
        elif any("constitutional" in v.lower() for v in self.violations):
            return "critical_violation"
        else:
            return "non_compliant"


# =============================================================================
# VIOLATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConstitutionalViolation:
    """
    Immutable constitutional violation record.
    
    COMPLIANCE-VIOL-INV-001: Violation is immutable
    COMPLIANCE-VIOL-INV-002: Violation has no runtime references
    
    VIOLATION-LAW-001: Violations shall be explicit and typed
    VIOLATION-LAW-002: Severity shall remain explicit
    """
    violated_principle: str
    """Constitutional principle that was violated."""
    
    severity: str = "warning"
    """Severity level of the violation."""
    
    affected_artifacts: tuple[str, ...] = field(default_factory=tuple)
    """Artifacts affected by this violation."""
    
    evidence: tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting the violation."""
    
    proposed_resolution: str | None = None
    """Proposed way to resolve this violation."""
    
    provenance_ref: str | None = None
    """Reference to violation provenance record."""
    
    @classmethod
    def of(
        cls,
        principle: str,
        severity: str = "warning",
        artifacts: tuple[str, ...] | None = None,
        evidence: tuple[str, ...] | None = None,
    ) -> ConstitutionalViolation:
        """
        Create a constitutional violation record.
        
        Args:
            principle: Violated principle
            severity: Severity level
            artifacts: Affected artifacts
            evidence: Supporting evidence
            
        Returns:
            A new ConstitutionalViolation instance
        """
        return cls(
            violated_principle=principle,
            severity=severity,
            affected_artifacts=artifacts or (),
            evidence=evidence or (),
            proposed_resolution=None,
            provenance_ref=None,
        )
    
    def is_critical(self) -> bool:
        """Check if this violation is critical."""
        return self.severity in ("critical", "fatal")


# =============================================================================
# COMPLIANCE REPORT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ComplianceReport:
    """
    Immutable compliance report.
    
    CCG-COMP-REP-INV-001: Report is immutable
    CCG-COMP-REP-INV-002: Report has no runtime references
    
    COMPLIANCE-LAW-007: Historical evaluations remain inspectable
    """
    evaluated_artifacts: tuple[str, ...]
    """Artifacts evaluated in this report."""
    
    compliance_status: str = "unknown"
    """Overall compliance status."""
    
    violations: tuple[ConstitutionalViolation, ...] = field(default_factory=tuple)
    """Violations found."""
    
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    """Recommendations for improvement."""
    
    confidence: float = 1.0
    """Confidence in this report."""
    
    provenance_ref: str | None = None
    """Reference to report provenance record."""
    
    @classmethod
    def of(
        cls,
        artifacts: tuple[str, ...],
        violations: tuple[ConstitutionalViolation, ...] | None = None,
        recommendations: tuple[str, ...] | None = None,
        confidence: float = 1.0,
    ) -> ComplianceReport:
        """
        Create a compliance report.
        
        Args:
            artifacts: Evaluated artifacts
            violations: Violations found
            recommendations: Improvement recommendations
            confidence: Confidence level
            
        Returns:
            A new ComplianceReport instance
        """
        return cls(
            evaluated_artifacts=artifacts,
            compliance_status="compliant" if not violations else "non_compliant",
            violations=violations or (),
            recommendations=recommendations or (),
            confidence=min(1.0, max(0.0, float(confidence))),
            provenance_ref=None,
        )
    
    def is_compliant(self) -> bool:
        """Check if the report indicates compliance."""
        return self.compliance_status == "compliant"
    
    def has_violations(self) -> bool:
        """Check if there are violations in this report."""
        return len(self.violations) > 0