# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Diagnostic Findings and Reports
===============================

Diagnostic models for architectural analysis.

DIAGNOSTIC LAWS (from spec)
---------------------------
DIAGNOSTIC-LAW-001: Diagnostics shall preserve supporting observations.
DIAGNOSTIC-LAW-002: Root-cause candidates shall remain hypotheses unless verified.
DIAGNOSTIC-LAW-003: Diagnostic severity shall remain explicit.
DIAGNOSTIC-LAW-004: Affected architecture shall remain explicit.
DIAGNOSTIC-LAW-005: Diagnostics shall preserve confidence.
DIAGNOSTIC-LAW-006: Diagnostics shall preserve uncertainty.
DIAGNOSTIC-LAW-007: Diagnostics shall preserve provenance.
DIAGNOSTIC-LAW-008: Diagnostic generation shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# =============================================================================
# DIAGNOSTIC FINDING
# =============================================================================

@dataclass(frozen=True, slots=True)
class DiagnosticFinding:
    """
    Immutable diagnostic finding about architectural behavior.
    
    DIAGNOSTIC-LAW-001: Findings preserve supporting observations (metrics).
    DIAGNOSTIC-LAW-002: Root causes remain hypotheses unless verified.
    """
    
    identity: str
    """Unique identifier for this diagnostic."""
    
    affected_scope: str
    """Scope being diagnosed (network, cycle, goal, etc.)."""
    
    root_cause_candidates: tuple[str, ...] = ()
    """Possible root causes (hypotheses)."""
    
    supporting_evidence: tuple[str, ...] = ()
    """Evidence supporting this diagnosis."""
    
    severity: str = "warning"
    """Severity level of the finding."""
    
    confidence: float = 0.5
    """Confidence in the diagnosis."""
    
    recommendations: tuple[str, ...] = ()
    """Suggested investigations or remediations."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this diagnostic."""
    
    def __post_init__(self):
        """Validate diagnostic components."""
        if not self.identity:
            raise ValueError("Diagnostic identity cannot be empty")
        
        if not self.affected_scope:
            raise ValueError("Affected scope cannot be empty")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        affected_scope: str,
        root_cause_candidates: tuple[str, ...] = (),
        supporting_evidence: tuple[str, ...] = (),
        severity: str = "warning",
        confidence: float = 0.5,
        recommendations: tuple[str, ...] = (),
        provenance: Optional[dict[str, str]] = None,
    ) -> DiagnosticFinding:
        """
        Create a new diagnostic finding.
        
        Args:
            affected_scope: Scope being diagnosed
            root_cause_candidates: Possible root causes
            supporting_evidence: Evidence supporting diagnosis
            severity: Severity level (critical, warning, info)
            confidence: Confidence in the diagnosis
            recommendations: Suggested remediations
            provenance: Optional provenance dictionary
            
        Returns:
            New DiagnosticFinding instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"diag:{affected_scope}:{severity}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            identity=f"diagnostic:{identity_hash}",
            affected_scope=affected_scope,
            root_cause_candidates=root_cause_candidates,
            supporting_evidence=supporting_evidence,
            severity=severity,
            confidence=confidence,
            recommendations=recommendations,
            provenance=provenance or {},
        )
    
    def is_verified(self) -> bool:
        """Check if diagnosis has been verified (high confidence)."""
        return self.confidence >= 0.8
    
    def to_dict(self) -> dict[str, Any]:
        """Convert diagnostic to dictionary."""
        return {
            "identity": self.identity,
            "affected_scope": self.affected_scope,
            "root_cause_candidates": list(self.root_cause_candidates),
            "supporting_evidence": list(self.supporting_evidence),
            "severity": self.severity,
            "confidence": self.confidence,
            "recommendations": list(self.recommendations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DiagnosticFinding:
        """Create diagnostic from dictionary."""
        return cls(
            identity=data["identity"],
            affected_scope=data["affected_scope"],
            root_cause_candidates=tuple(data.get("root_cause_candidates", [])),
            supporting_evidence=tuple(data.get("supporting_evidence", [])),
            severity=data.get("severity", "warning"),
            confidence=float(data.get("confidence", 0.5)),
            recommendations=tuple(data.get("recommendations", [])),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# DIAGNOSTIC REPORT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    """
    Immutable diagnostic report aggregating multiple findings.
    
    DIAGNOSTIC-LAW-001: Reports preserve supporting evidence (findings).
    """
    
    identity: str
    """Unique identifier for this report."""
    
    observed_scope: str
    """Scope being diagnosed."""
    
    findings: tuple[DiagnosticFinding, ...] = ()
    """Collection of diagnostic findings."""
    
    overall_severity: str = "normal"
    """Overall severity level."""
    
    confidence: float = 0.5
    """Confidence in the diagnosis."""
    
    recommendations: tuple[str, ...] = ()
    """Suggested investigations or remediations."""
    
    limitations: tuple[str, ...] = ()
    """Limitations of this report."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this report."""
    
    def __post_init__(self):
        """Validate report components."""
        if not self.identity:
            raise ValueError("Report identity cannot be empty")
        
        if not self.observed_scope:
            raise ValueError("Observed scope cannot be empty")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        observed_scope: str,
        findings: tuple[DiagnosticFinding, ...] = (),
        overall_severity: str = "normal",
        confidence: float = 0.5,
        recommendations: tuple[str, ...] = (),
        provenance: Optional[dict[str, str]] = None,
    ) -> DiagnosticReport:
        """
        Create a new diagnostic report.
        
        Args:
            observed_scope: Scope being diagnosed
            findings: Collection of diagnostic findings
            overall_severity: Overall severity level
            confidence: Confidence in the diagnosis
            recommendations: Suggested remediations
            provenance: Optional provenance dictionary
            
        Returns:
            New DiagnosticReport instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"report:diag:{observed_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            identity=f"report:diagnostic:{identity_hash}",
            observed_scope=observed_scope,
            findings=findings,
            overall_severity=overall_severity,
            confidence=confidence,
            recommendations=recommendations,
            provenance=provenance or {},
        )
    
    @property
    def highest_severity(self) -> str:
        """Get the highest severity among all findings."""
        if not self.findings:
            return "normal"
        
        severity_order = {"critical": 3, "warning": 2, "info": 1}
        max_sev = 1
        
        for finding in self.findings:
            current = severity_order.get(finding.severity, 0)
            if current > max_sev:
                max_sev = current
        
        return {3: "critical", 2: "warning", 1: "info"}.get(max_sev, "normal")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "identity": self.identity,
            "observed_scope": self.observed_scope,
            "findings": [f.to_dict() for f in self.findings],
            "overall_severity": self.overall_severity,
            "confidence": self.confidence,
            "recommendations": list(self.recommendations),
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DiagnosticReport:
        """Create report from dictionary."""
        return cls(
            identity=data["identity"],
            observed_scope=data["observed_scope"],
            findings=tuple(DiagnosticFinding.from_dict(f) for f in data.get("findings", [])),
            overall_severity=data.get("overall_severity", "normal"),
            confidence=float(data.get("confidence", 0.5)),
            recommendations=tuple(data.get("recommendations", [])),
            limitations=tuple(data.get("limitations", [])),
            provenance=dict(data.get("provenance", {})),
        )