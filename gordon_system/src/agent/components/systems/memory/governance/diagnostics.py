# Governance Diagnostics - Shared Module

"""
Governance Diagnostics: Health and diagnostic information for Memory.

This module provides diagnostic models for monitoring governance system health,
performance, and issues.

Diagnostics Categories:

    - Integrity diagnostics
    - Compliance diagnostics
    - Audit diagnostics
    - Performance metrics
    
Anti-Patterns Rejected:

    - Mutable diagnostic state
    - Hidden diagnostic data
    - Non-deterministic diagnostic generation

Diagnostics Laws:

    DIAGNOSTICS-LAW-001: Diagnostics shall preserve system state
    DIAGNOSTICS-LAW-002: Diagnostics shall remain inspectable
    DIAGNOSTICS-LAW-003: Diagnostics shall be deterministic
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# DIAGNOSTIC METRICS - Performance and health metrics
# =============================================================================


@dataclass(frozen=True)
class DiagnosticMetrics:
    """
    Metrics for governance system diagnostics.
    
    Fields:
        check_count:         Total number of checks performed
        violation_count:     Number of violations found
        
        # Time-based metrics
        start_time_utc:      When evaluation started
        end_time_utc:        When evaluation ended
        
        # By category
        integrity_checks:    Integrity checks performed
        compliance_checks:   Compliance checks performed
        
        duration_seconds:    Total evaluation duration
    
    Properties:
        duration_seconds:    Evaluation duration in seconds
        is_healthy:          True if no violations found
        check_rate:          Checks per second (if duration > 0)
    """
    
    check_count: int = 0                  # Total checks performed
    violation_count: int = 0              # Violations found
    
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)
    
    integrity_checks: int = 0             # Integrity checks
    compliance_checks: int = 0            # Compliance checks
    
    @property
    def duration_seconds(self) -> float:
        """Get evaluation duration in seconds."""
        return self.end_time_utc - self.start_time_utc
    
    @property
    def is_healthy(self) -> bool:
        """Check if diagnostics show healthy state."""
        return self.violation_count == 0
    
    @property
    def check_rate(self) -> float:
        """Get checks per second (0 if no duration)."""
        if self.duration_seconds <= 0:
            return 0.0
        return self.check_count / self.duration_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary representation."""
        return {
            "check_count": self.check_count,
            "violation_count": self.violation_count,
            "duration_seconds": self.duration_seconds,
            "integrity_checks": self.integrity_checks,
            "compliance_checks": self.compliance_checks,
            "is_healthy": self.is_healthy,
            "check_rate": self.check_rate,
        }


# =============================================================================
# DIAGNOSTIC REPORT - Complete diagnostic information
# =============================================================================


@dataclass(frozen=True)
class DiagnosticReport:
    """
    Complete diagnostic report for governance evaluation.
    
    Fields:
        report_id:           Unique identifier
        
        metrics:             DiagnosticMetrics instance
        violations:          List of violation diagnostics
        
        system_state:        System state at time of diagnosis
        recommendations:     Suggested improvements
    
    Properties:
        is_healthy:          True if no issues found
        issue_count:         Total number of diagnostic issues
    """
    
    report_id: str                          # Unique identifier
    
    metrics: DiagnosticMetrics              # Performance and health metrics
    violations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    system_state: Dict[str, Any] = field(default_factory=dict)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_healthy(self) -> bool:
        """Check if diagnostics show healthy state."""
        return self.metrics.is_healthy and len(self.violations) == 0
    
    @property
    def issue_count(self) -> int:
        """Get total number of diagnostic issues."""
        return len(self.violations)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            "report_id": self.report_id,
            "metrics": self.metrics.to_dict(),
            "violations": [dict(v) for v in self.violations],
            "system_state": dict(self.system_state),
            "recommendations": list(self.recommendations),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "DiagnosticMetrics",
    "DiagnosticReport",
]