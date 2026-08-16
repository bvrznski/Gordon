# Governance Health - Shared Module

"""
Governance Health: Health scoring and reporting for Memory governance.

This module provides health models for assessing governance system status
and providing actionable health insights.

Health Categories:

    - Integrity health
    - Compliance health
    - Audit health
    - Migration readiness
    - Repair readiness
    
Anti-Patterns Rejected:

    - Mutable health scores without proper synchronization
    - Non-deterministic health scoring

Health Laws:

    HEALTH-LAW-001: Health shall be deterministically computed
    HEALTH-LAW-002: Health shall remain inspectable
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# HEALTH SCORE - Single health metric (0.0-1.0)
# =============================================================================


@dataclass(frozen=True)
class HealthScore:
    """
    A single health score for a governance domain.
    
    Fields:
        name:                Domain name (integrity, compliance, etc.)
        score:               0.0-1.0 health score
        status:              "healthy", "warning", "critical", or "unknown"
        
        issues:              List of issue descriptions
        recommendations:     Suggested improvements
        
    Properties:
        is_healthy:          True if score >= 0.9
        has_issues:          True if any issues recorded
    """
    
    name: str                               # Domain name
    
    score: float = 1.0                    # 0.0-1.0 health score
    status: str = "unknown"               # healthy/warning/critical/unknown
    
    issues: Tuple[str, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_healthy(self) -> bool:
        """Check if health score indicates healthy state."""
        return self.score >= 0.9
    
    @property
    def has_issues(self) -> bool:
        """Check if any issues were recorded."""
        return len(self.issues) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert score to dictionary representation."""
        return {
            "name": self.name,
            "score": self.score,
            "status": self.status,
            "is_healthy": self.is_healthy,
            "has_issues": self.has_issues,
            "issues": list(self.issues),
            "recommendations": list(self.recommendations),
        }


# =============================================================================
# HEALTH REPORT - Complete health assessment
# =============================================================================


@dataclass(frozen=True)
class HealthReport:
    """
    Complete health report for governance evaluation.
    
    Fields:
        report_id:           Unique identifier
        
        scores:              HealthScore instances for each domain
        overall_score:       Weighted average of all scores
        
        timestamp_utc:       When report was generated
        revision_id:         Memory system revision at time of report
    
    Properties:
        is_healthy:          True if overall score >= 0.9
        critical_count:      Number of domains with critical health
        warning_count:       Number of domains with warning health
    """
    
    report_id: str                          # Unique identifier
    
    scores: Tuple[HealthScore, ...]        # Domain health scores
    
    overall_score: float = 1.0            # Weighted average (0.0-1.0)
    
    timestamp_utc: float = field(default_factory=time.time)
    revision_id: str = ""                 # Memory system revision
    
    @property
    def is_healthy(self) -> bool:
        """Check if overall health is healthy."""
        return self.overall_score >= 0.9
    
    @property
    def critical_count(self) -> int:
        """Count of domains with critical health."""
        return sum(1 for s in self.scores if s.status == "critical")
    
    @property
    def warning_count(self) -> int:
        """Count of domains with warning health."""
        return sum(1 for s in self.scores if s.status == "warning")
    
    def get_score(self, name: str) -> Optional[HealthScore]:
        """Get score for a specific domain by name."""
        for s in self.scores:
            if s.name == name:
                return s
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            "report_id": self.report_id,
            "overall_score": self.overall_score,
            "is_healthy": self.is_healthy,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "timestamp_utc": self.timestamp_utc,
            "revision_id": self.revision_id,
            "scores": [s.to_dict() for s in self.scores],
        }


# =============================================================================
# HEALTH METRICS - Raw metrics for health calculation
# =============================================================================


@dataclass(frozen=True)
class HealthMetrics:
    """
    Raw metrics used to calculate health scores.
    
    Fields:
        # Integrity metrics
        integrity_violations:     Number of integrity violations
        integrity_check_count:    Total integrity checks performed
        
        # Compliance metrics  
        compliance_violations:    Number of compliance violations
        compliance_check_count:   Total compliance checks performed
        
        # Audit metrics
        audit_event_count:        Total audit events recorded
        
        # Performance metrics
        avg_evaluation_duration_seconds: Average evaluation duration
    
    Properties:
        integrity_health_score:   Health score for integrity (0.0-1.0)
        compliance_health_score:  Health score for compliance (0.0-1.0)
    """
    
    # Integrity metrics
    integrity_violations: int = 0
    integrity_check_count: int = 0
    
    # Compliance metrics
    compliance_violations: int = 0
    compliance_check_count: int = 0
    
    # Audit metrics
    audit_event_count: int = 0
    
    # Performance metrics
    avg_evaluation_duration_seconds: float = 0.0
    
    @property
    def integrity_health_score(self) -> float:
        """Calculate integrity health score (0.0-1.0)."""
        if self.integrity_check_count == 0:
            return 1.0  # No checks = assume healthy
        
        violation_ratio = self.integrity_violations / max(self.integrity_check_count, 1)
        return round(max(0.0, 1.0 - violation_ratio), 3)
    
    @property
    def compliance_health_score(self) -> float:
        """Calculate compliance health score (0.0-1.0)."""
        if self.compliance_check_count == 0:
            return 1.0  # No checks = assume healthy
        
        violation_ratio = self.compliance_violations / max(self.compliance_check_count, 1)
        return round(max(0.0, 1.0 - violation_ratio), 3)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary representation."""
        return {
            "integrity_health_score": self.integrity_health_score,
            "compliance_health_score": self.compliance_health_score,
            "overall_score": (self.integrity_health_score + self.compliance_health_score) / 2,
            "audit_event_count": self.audit_event_count,
            "avg_evaluation_duration_seconds": self.avg_evaluation_duration_seconds,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "HealthScore",
    "HealthReport",
    "HealthMetrics",
]