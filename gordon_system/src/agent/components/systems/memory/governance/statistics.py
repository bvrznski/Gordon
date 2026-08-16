# Governance Statistics - Shared Module

"""
Governance Statistics: Metrics collection for Memory governance.

This module provides statistical models for tracking governance system
performance, evaluation patterns, and trend analysis.

Statistics Categories:

    - Evaluation counts by type
    - Violation trends over time
    - Performance metrics (latency, throughput)
    
Anti-Patterns Rejected:

    - Mutable statistics without proper synchronization
    - Non-deterministic aggregation

Statistics Laws:

    STATISTICS-LAW-001: Statistics shall preserve evaluation data
    STATISTICS-LAW-002: Statistics shall remain inspectable
    STATISTICS-LAW-003: Statistics shall be deterministic
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# EVALUATION METRICS - Metrics for a single evaluation session
# =============================================================================


@dataclass(frozen=True)
class EvaluationMetrics:
    """
    Metrics for a single governance evaluation.
    
    Fields:
        metrics_id:          Unique identifier
        
        # Counts
        artifacts_evaluated: Total artifacts evaluated
        checks_performed:    Total checks performed
        violations_found:    Violations detected
        
        # By category
        integrity_violations: Integrity violations found
        compliance_violations: Compliance violations found
        
        # Performance
        start_time_utc:      When evaluation started
        end_time_utc:        When evaluation ended
        
    Properties:
        duration_seconds:    Evaluation duration in seconds
        check_rate:          Checks per second (if duration > 0)
    """
    
    metrics_id: str                         # Unique identifier
    
    artifacts_evaluated: int = 0          # Total artifacts evaluated
    checks_performed: int = 0             # Total checks performed
    violations_found: int = 0             # Violations detected
    
    integrity_violations: int = 0         # Integrity violations
    compliance_violations: int = 0        # Compliance violations
    
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)
    
    @property
    def duration_seconds(self) -> float:
        """Get evaluation duration in seconds."""
        return self.end_time_utc - self.start_time_utc
    
    @property
    def check_rate(self) -> float:
        """Get checks per second (0 if no duration)."""
        if self.duration_seconds <= 0:
            return 0.0
        return self.checks_performed / self.duration_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary representation."""
        return {
            "metrics_id": self.metrics_id,
            "artifacts_evaluated": self.artifacts_evaluated,
            "checks_performed": self.checks_performed,
            "violations_found": self.violations_found,
            "integrity_violations": self.integrity_violations,
            "compliance_violations": self.compliance_violations,
            "duration_seconds": self.duration_seconds,
            "check_rate": self.check_rate,
        }


# =============================================================================
# AGGREGATE METRICS - Aggregated statistics over time period
# =============================================================================


@dataclass(frozen=True)
class AggregateMetrics:
    """
    Aggregated governance statistics over a time period.
    
    Fields:
        metrics_id:          Unique identifier
        
        period_start_utc:    Start of aggregation period
        period_end_utc:      End of aggregation period
        
        # Counts
        total_evaluations:   Number of evaluations
        total_artifacts:     Total artifacts evaluated
        total_violations:    Total violations found
        
        # By category
        integrity_counts:    Violation counts by type
        compliance_counts:   Violation counts by type
    
    Properties:
        period_seconds:      Aggregation period in seconds
        avg_evaluations_per_second: Average evaluations per second
    """
    
    metrics_id: str                         # Unique identifier
    
    period_start_utc: float = field(default_factory=time.time)
    period_end_utc: float = field(default_factory=time.time)
    
    total_evaluations: int = 0            # Number of evaluations
    total_artifacts: int = 0              # Total artifacts evaluated
    total_violations: int = 0             # Total violations found
    
    integrity_counts: Dict[str, int] = field(default_factory=dict)      # Violation types
    compliance_counts: Dict[str, int] = field(default_factory=dict)     # Violation types
    
    @property
    def period_seconds(self) -> float:
        """Get aggregation period in seconds."""
        return self.period_end_utc - self.period_start_utc
    
    @property
    def avg_evaluations_per_second(self) -> float:
        """Get average evaluations per second (0 if no duration)."""
        if self.period_seconds <= 0:
            return 0.0
        return self.total_evaluations / self.period_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary representation."""
        return {
            "metrics_id": self.metrics_id,
            "period_start_utc": self.period_start_utc,
            "period_end_utc": self.period_end_utc,
            "total_evaluations": self.total_evaluations,
            "total_artifacts": self.total_artifacts,
            "total_violations": self.total_violations,
            "integrity_counts": dict(self.integrity_counts),
            "compliance_counts": dict(self.compliance_counts),
            "period_seconds": self.period_seconds,
            "avg_evaluations_per_second": self.avg_evaluations_per_second,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "EvaluationMetrics",
    "AggregateMetrics",
]