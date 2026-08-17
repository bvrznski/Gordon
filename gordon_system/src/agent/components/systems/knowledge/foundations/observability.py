# Knowledge Observability - Phase 6.1
# ====================================

"""
Knowledge Observability: Semantic quality metrics in Gordon's knowledge system.

Observability provides read-only visibility into semantic state:
    
    * Active artifacts count
    * Draft artifacts count  
    * Published artifacts count
    * Validation failure rates
    * Certification status
    * Compatibility violations
    * Migration counts
    * Governance findings
    * Health scores
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# OBSERVABILITY METRICS - Semantic state indicators
# =============================================================================


@dataclass(frozen=True)
class ObservabilityMetric:
    """
    Individual observability metric.
    
    Records a single measurable aspect of semantic state.
    
    Fields:
        metric_identity:   Unique identifier for this metric
        metric_name:       What is being measured
        metric_value:      The observed value
        metric_unit:       Unit of measurement (count, rate, percentage)
        timestamp_utc:     When metric was captured
        context:           Additional context (e.g., scope, category)
    """
    
    # Identity and metadata (required)
    metric_identity: str                  # Unique metric ID
    
    metric_name: str                      # What is measured
    
    metric_value: float = 0.0             # The value observed
    metric_unit: str = "count"            # count/rate/percentage/unit
    
    timestamp_utc: float = field(default_factory=time.time)
    
    context: Dict[str, Any] = field(default_factory=dict)  # Additional info
    
    @property
    def is_valid(self) -> bool:
        """Check if metric has valid data."""
        return (
            len(self.metric_identity) > 0 and
            len(self.metric_name) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization."""
        return {
            "metric_identity": self.metric_identity,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "timestamp_utc": self.timestamp_utc,
            "context": dict(self.context),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservabilityMetric":
        """Create metric from dictionary."""
        return cls(
            metric_identity=data.get("metric_identity", str(uuid.uuid4())),
            metric_name=data.get("metric_name", ""),
            metric_value=float(data.get("metric_value", 0)),
            metric_unit=data.get("metric_unit", "count"),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            context=dict(data.get("context", {})),
        )


# =============================================================================
# OBSERVABILITY REPORT - Complete state snapshot
# =============================================================================


@dataclass(frozen=True)
class ObservabilityReport:
    """
    Complete observability report at a point in time.
    
    Aggregates all metrics into a comprehensive view of semantic health.
    
    Fields:
        report_identity:   Unique identifier for this report
        timestamp_utc:     When report was captured
        metric_count:      Total number of metrics in report
        metrics:           All observed metrics
        summary:           High-level summary of findings
    """
    
    # Identity and metadata (required)
    report_identity: str                  # Unique report ID
    
    timestamp_utc: float = field(default_factory=time.time)  # Snapshot time
    
    metric_count: int = 0                 # Number of metrics
    metrics: Tuple[ObservabilityMetric, ...] = field(default_factory=tuple)  # All metrics
    
    summary: Optional[str] = None         # High-level summary
    
    @property
    def is_valid(self) -> bool:
        """Check if report has valid data."""
        return len(self.report_identity) > 0 and self.metric_count >= 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "report_identity": self.report_identity,
            "timestamp_utc": self.timestamp_utc,
            "metric_count": self.metric_count,
            "metrics": [m.to_dict() for m in self.metrics],
            "summary": self.summary,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservabilityReport":
        """Create report from dictionary."""
        metrics = []
        for m_data in data.get("metrics", []):
            metrics.append(ObservabilityMetric.from_dict(m_data))
        
        return cls(
            report_identity=data.get("report_identity", str(uuid.uuid4())),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            metric_count=int(data.get("metric_count", len(metrics))),
            metrics=tuple(metrics),
            summary=data.get("summary"),
        )


# =============================================================================
# OBSERVABILITY ENGINE - Metrics collection
# =============================================================================


class ObservabilityEngine:
    """
    Engine for collecting semantic observability metrics.
    
    Provides read-only visibility into the state of knowledge artifacts
    without modifying any data. Supports monitoring and alerting scenarios.
    """
    
    def __init__(
        self,
        collect_artifact_metrics: bool = True,
        collect_validation_metrics: bool = True,
        collect_governance_metrics: bool = True,
    ):
        """
        Initialize the observability engine.
        
        Args:
            collect_artifact_metrics: Whether to track artifact counts
            collect_validation_metrics: Whether to track validation status
            collect_governance_metrics: Whether to track governance findings
        """
        self._collect_artifacts = collect_artifact_metrics
        self._collect_validations = collect_validation_metrics
        self._collect_governance = collect_governance_metrics
        
        # Internal metrics store (in real implementation, this would be persistent)
        self._metrics_store: Dict[str, List[ObservabilityMetric]] = {}
    
    def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        unit: str = "count",
        context: Optional[Dict[str, Any]] = None,
    ) -> ObservabilityMetric:
        """
        Record a single metric.
        
        Args:
            metric_name: What is being measured
            metric_value: The observed value
            unit: Unit of measurement
            context: Additional context
            
        Returns:
            Recorded metric with identity and timestamp
        """
        metric = ObservabilityMetric(
            metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=unit,
            timestamp_utc=time.time(),
            context=context or {},
        )
        
        if metric_name not in self._metrics_store:
            self._metrics_store[metric_name] = []
        
        self._metrics_store[metric_name].append(metric)
        return metric
    
    def collect_artifact_metrics(
        self,
        artifacts: List[Dict[str, Any]],
    ) -> Tuple[ObservabilityMetric, ...]:
        """
        Collect metrics about artifacts.
        
        Args:
            artifacts: List of artifact data dictionaries
            
        Returns:
            Tuple of recorded metrics
        """
        if not self._collect_artifacts:
            return tuple()
        
        total = len(artifacts)
        active_count = sum(1 for a in artifacts if a.get("lifecycle_state") == "active")
        draft_count = sum(1 for a in artifacts if a.get("lifecycle_state") == "draft")
        certified_count = sum(1 for a in artifacts if a.get("certification_level") in ("certified", "verified"))
        
        metrics = [
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="total_artifacts",
                metric_value=float(total),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="active_artifacts",
                metric_value=float(active_count),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="draft_artifacts",
                metric_value=float(draft_count),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="certified_artifacts",
                metric_value=float(certified_count),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
        ]
        
        # Store and return
        for metric in metrics:
            name = metric.metric_name
            if name not in self._metrics_store:
                self._metrics_store[name] = []
            self._metrics_store[name].append(metric)
        
        return tuple(metrics)
    
    def collect_validation_metrics(
        self,
        validation_results: List[Dict[str, Any]],
    ) -> Tuple[ObservabilityMetric, ...]:
        """
        Collect metrics about validation results.
        
        Args:
            validation_results: List of validation result data
            
        Returns:
            Tuple of recorded metrics
        """
        if not self._collect_validations:
            return tuple()
        
        total = len(validation_results)
        passed_count = sum(1 for v in validation_results if v.get("passed", False))
        failed_count = total - passed_count
        
        pass_rate = (passed_count / total * 100) if total > 0 else 0.0
        
        metrics = [
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="total_validations",
                metric_value=float(total),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="passed_validations",
                metric_value=float(passed_count),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="failed_validations",
                metric_value=float(failed_count),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="validation_pass_rate",
                metric_value=pass_rate,
                metric_unit="percentage",
                timestamp_utc=time.time(),
            ),
        ]
        
        for metric in metrics:
            name = metric.metric_name
            if name not in self._metrics_store:
                self._metrics_store[name] = []
            self._metrics_store[name].append(metric)
        
        return tuple(metrics)
    
    def collect_governance_metrics(
        self,
        findings: List[Dict[str, Any]],
    ) -> Tuple[ObservabilityMetric, ...]:
        """
        Collect metrics about governance findings.
        
        Args:
            findings: List of governance finding data
            
        Returns:
            Tuple of recorded metrics
        """
        if not self._collect_governance:
            return tuple()
        
        total = len(findings)
        critical_count = sum(1 for f in findings if f.get("severity") == "critical")
        high_count = sum(1 for f in findings if f.get("severity") == "high")
        
        metrics = [
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="total_governance_findings",
                metric_value=float(total),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="critical_findings",
                metric_value=float(critical_count),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
            ObservabilityMetric(
                metric_identity=f"metric:{uuid.uuid4().hex[:16]}",
                metric_name="high_severity_findings",
                metric_value=float(high_count),
                metric_unit="count",
                timestamp_utc=time.time(),
            ),
        ]
        
        for metric in metrics:
            name = metric.metric_name
            if name not in self._metrics_store:
                self._metrics_store[name] = []
            self._metrics_store[name].append(metric)
        
        return tuple(metrics)
    
    def get_report(self) -> ObservabilityReport:
        """
        Get current observability report.
        
        Returns:
            Complete report with all collected metrics
        """
        all_metrics = []
        for metrics_list in self._metrics_store.values():
            all_metrics.extend(metrics_list)
        
        return ObservabilityReport(
            report_identity=f"report:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            metric_count=len(all_metrics),
            metrics=tuple(all_metrics),
        )


__all__ = [
    # Metric types
    "ObservabilityMetric",
    # Report types  
    "ObservabilityReport",
    # Engine
    "ObservabilityEngine",
]