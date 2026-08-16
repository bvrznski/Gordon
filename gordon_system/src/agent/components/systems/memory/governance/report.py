# Governance Report - Shared Module

"""
Governance Report: Complete evaluation summary with recommendations.

This module provides the governance report model and helper functions for
generating reports from governance evaluations.

Report Structure:

    - Report identification (ID, timestamp, scope)
    - Evaluation results (status, certification status)
    - Findings (violations, warnings, recommendations)
    - Evidence records (audit trail)
    - Diagnostics (evaluation metadata)

Anti-Patterns Rejected:

    - Mutable reports
    - Hidden findings
    - Non-deterministic report generation

Report Laws:

    REPORT-LAW-001: Every governance report shall possess explicit identity
    REPORT-LAW-002: Reports shall preserve evidence
    REPORT-LAW-003: Reports shall preserve provenance
    REPORT-LAW-004: Reports shall preserve diagnostics
    REPORT-LAW-005: Reports shall preserve revision identity
    REPORT-LAW-006: Reports shall remain immutable
    REPORT-LAW-007: Reports shall remain inspectable
    REPORT-LAW-008: Report generation shall remain deterministic
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time
import hashlib


# =============================================================================
# GOVERNANCE REPORT - Complete evaluation summary
# =============================================================================


@dataclass(frozen=True)
class GovernanceReport:
    """
    Complete governance evaluation report.
    
    Reports are immutable and serve as official records of governance state.
    
    Fields:
        report_id:          Unique identifier for this report
        
        evaluation_scope:   What was evaluated (full, integrity_only, etc.)
        timestamp_utc:      When report was generated
        status:             Governance state at time of generation
        
        certification_status: Result of certification (pass/fail/conditional)
        
        violations:         All violations found during evaluation
        warnings:           Warning messages
        recommendations:    Suggested improvements
        
        evidence_records:   Evidence supporting decisions
        diagnostics:        Evaluation metadata and metrics
        
        revision_id:        Memory system revision at time of report
    
    Properties:
        is_certified:       True if memory passed certification
        has_violations:     True if any violations were found
        critical_count:     Number of critical severity violations
        error_count:        Number of error severity violations
        warning_count:      Number of warnings
    """
    
    # Report identification
    report_id: str                          # Unique report identifier
    evaluation_scope: str                  # What was evaluated (full, integrity_only, etc.)
    timestamp_utc: float                   # When report was generated
    
    # Evaluation results
    status: str = "complete"               # Governance state at time of generation
    certification_status: Optional[str] = None  # Certification result (pass/fail/conditional)
    
    # Findings
    violations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Evidence and diagnostics
    evidence_records: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Revision information
    revision_id: str = ""                  # Memory system revision at time of report
    
    @property
    def is_certified(self) -> bool:
        """Check if memory passed certification."""
        return self.certification_status == "pass" and len(self.violations) == 0
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0
    
    @property
    def critical_count(self) -> int:
        """Count of critical severity violations."""
        return sum(1 for v in self.violations 
                   if v.get("severity") == "critical")
    
    @property
    def error_count(self) -> int:
        """Count of error severity violations."""
        return sum(1 for v in self.violations 
                   if v.get("severity") == "error")
    
    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return len(self.warnings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            "report_id": self.report_id,
            "evaluation_scope": self.evaluation_scope,
            "timestamp_utc": self.timestamp_utc,
            "status": self.status,
            "certification_status": self.certification_status,
            "violations": [dict(v) for v in self.violations],
            "warnings": list(self.warnings),
            "recommendations": list(self.recommendations),
            "evidence_records": [dict(e) for e in self.evidence_records],
            "diagnostics": dict(self.diagnostics),
            "revision_id": self.revision_id,
        }
    
    @classmethod
    def create(
        cls,
        evaluation_scope: str = "full_memory_system",
        status: str = "complete",
        certification_status: Optional[str] = None,
        violations: Optional[Tuple[Dict[str, Any], ...]] = None,
        warnings: Optional[Tuple[str, ...]] = None,
        recommendations: Optional[Tuple[str, ...]] = None,
        evidence_records: Optional[Tuple[Dict[str, Any], ...]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        revision_id: str = "",
    ) -> "GovernanceReport":
        """
        Create a new governance report.
        
        Args:
            evaluation_scope: What was evaluated
            status: Governance state
            certification_status: Certification result (pass/fail/conditional)
            violations: Violations found
            warnings: Warning messages
            recommendations: Suggested improvements
            evidence_records: Evidence records from evaluation
            diagnostics: Diagnostic information
            revision_id: Memory system revision identifier
            
        Returns:
            New GovernanceReport instance
        """
        return cls(
            report_id=f"report:{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}",
            evaluation_scope=evaluation_scope,
            timestamp_utc=time.time(),
            status=status,
            certification_status=certification_status,
            violations=violations or (),
            warnings=warnings or (),
            recommendations=recommendations or (),
            evidence_records=evidence_records or (),
            diagnostics=dict(diagnostics) if diagnostics else {},
            revision_id=revision_id,
        )


# =============================================================================
# REPORT SUMMARY - Human-readable report summary
# =============================================================================


@dataclass(frozen=True)
class ReportSummary:
    """
    Human-readable summary of a governance report.
    
    Fields:
        title:             Report title
        summary:           Brief summary text
        
        certified:         Whether memory is certified
        violation_count:   Number of violations found
        warning_count:     Number of warnings
        
        timestamp_utc:     When summary was generated
    """
    
    title: str                              # Report title
    summary: str                           # Brief summary text
    
    certified: bool                        # Whether memory is certified
    violation_count: int = 0               # Number of violations found
    warning_count: int = 0                 # Number of warnings
    
    timestamp_utc: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary representation."""
        return {
            "title": self.title,
            "summary": self.summary,
            "certified": self.certified,
            "violation_count": self.violation_count,
            "warning_count": self.warning_count,
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GovernanceReport",
    "ReportSummary",
]