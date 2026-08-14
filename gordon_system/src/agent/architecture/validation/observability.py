# Observability & Diagnostics Module - Phase 3.24
# ================================================
#
# Validation history, audit history, compliance history,
# remediation history, score evolution.

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class HistoryEventType(Enum):
    """Types of events in validation history."""
    VALIDATION_PERFORMED = "validation_performed"
    AUDIT_COMPLETED = "audit_completed"
    COMPLIANCE_CHECKED = "compliance_checked"
    REMEDIATION_APPLIED = "remediation_applied"
    CERTIFICATION_ISSUED = "certification_issued"
    SCORE_UPDATED = "score_updated"


@dataclass(frozen=True)
class HistoryEvent:
    """
    A single event in validation history.
    
    INVARIANTS:
        EVT-001: Events are immutable once recorded
        EVT-002: All events have timestamps
        EVT-003: Events include source information
    """
    
    event_id: str = field(default_factory=lambda: f"evt_{time.time_ns()}")
    event_type: HistoryEventType
    
    # Timestamp
    timestamp_utc: float = field(default_factory=time.time)
    
    # Context
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    
    # Result data (JSON serializable)
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Source information
    source_validator: str = "unknown"


@dataclass(frozen=True)
class ValidationMetrics:
    """
    Metrics about validation operations.
    
    INVARIANTS:
        MET-001: Metrics are computed from events
        MET-002: All metrics are deterministic
    """
    
    # Counts
    total_validations: int = 0
    passed_validations: int = 0
    failed_validations: int = 0
    
    # Time-based
    first_validation_utc: Optional[float] = None
    last_validation_utc: Optional[float] = None
    
    # Rate metrics (computed from events)
    validation_rate_per_hour: float = 0.0
    failure_rate: float = 0.0


@dataclass(frozen=True)
class RepositoryHealth:
    """
    Overall repository health status.
    
    INVARIANTS:
        HLT-001: Health is computed from all validations
        HLT-002: Health includes all metrics
    """
    
    health_id: str = field(default_factory=lambda: f"health_{time.time_ns()}")
    computed_at_utc: float = field(default_factory=time.time)
    
    # Status
    overall_status: str = "healthy"  # healthy, warning, critical
    
    # Metrics
    validation_pass_rate: float = 1.0
    certification_rate: float = 1.0
    compliance_score: int = 100
    
    # Findings summary
    open_errors: int = 0
    open_warnings: int = 0
    open_critical: int = 0


@dataclass(frozen=True)
class ScoreEvolution:
    """
    Evolution of a score over time.
    
    INVARIANTS:
        SCL-001: Score evolution is immutable once recorded
        SCL-002: All data points are ordered by timestamp
    """
    
    score_id: str = field(default_factory=lambda: f"score_{time.time_ns()}")
    score_type: str  # e.g., "validation_coverage", "certification_ready"
    
    # Data points (timestamp, value)
    data_points: Tuple[Tuple[float, int], ...] = field(default_factory=tuple)
    
    # Summary
    current_value: int = 0
    max_value: int = 0
    min_value: int = 100  # Initialize to max possible
    
    @property
    def is_improving(self) -> bool:
        """Check if score is improving."""
        if len(self.data_points) < 2:
            return True
        return self.current_value >= self.min_value


@dataclass(frozen=True)
class AuditRecord:
    """
    Complete audit record.
    
    INVARIANTS:
        ADR-001: Records are immutable once generated
        ADR-002: All findings are included
    """
    
    record_id: str = field(default_factory=lambda: f"audit_{time.time_ns()}")
    audit_type: str  # e.g., "dependency", "ownership", "interface"
    audited_at_utc: float = field(default_factory=time.time)
    
    # Results
    passed_count: int = 0
    failed_count: int = 0
    
    # Evidence
    findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def overall_passed(self) -> bool:
        """Check if audit passed."""
        return self.failed_count == 0


# =============================================================================
# VALIDATION HISTORY STORE
# =============================================================================

class ValidationHistoryStore:
    """
    Stores and manages validation history.
    
    FEATURES:
        - Event tracking
        - Metrics computation
        - Health monitoring
        - Score evolution tracking
    """
    
    def __init__(self):
        self._events: List[HistoryEvent] = []
        self._audit_records: List[AuditRecord] = []
        self._score_evolution: Dict[str, ScoreEvolution] = {}
    
    def record_event(self, event: HistoryEvent) -> None:
        """Record a history event."""
        self._events.append(event)
    
    def get_events(
        self,
        event_type: Optional[HistoryEventType] = None,
        since_utc: Optional[float] = None,
        until_utc: Optional[float] = None,
    ) -> List[HistoryEvent]:
        """
        Get events from history.
        
        Args:
            event_type: Filter by event type
            since_utc: Start timestamp filter
            until_utc: End timestamp filter
            
        Returns:
            List of matching events
        """
        result = self._events
        
        if event_type is not None:
            result = [e for e in result if e.event_type == event_type]
        
        if since_utc is not None:
            result = [e for e in result if e.timestamp_utc >= since_utc]
        
        if until_utc is not None:
            result = [e for e in result if e.timestamp_utc <= until_utc]
        
        return result
    
    def get_audit_records(
        self,
        audit_type: Optional[str] = None,
    ) -> List[AuditRecord]:
        """Get audit records."""
        result = self._audit_records
        if audit_type is not None:
            result = [r for r in result if r.audit_type == audit_type]
        return result
    
    def compute_metrics(self) -> ValidationMetrics:
        """Compute current metrics from events."""
        validations = [
            e for e in self._events 
            if e.event_type == HistoryEventType.VALIDATION_PERFORMED
        ]
        
        passed = sum(1 for e in validations if e.details.get("passed", False))
        failed = len(validations) - passed
        
        timestamps = [e.timestamp_utc for e in validations]
        
        return ValidationMetrics(
            total_validations=len(validations),
            passed_validations=passed,
            failed_validations=failed,
            first_validation_utc=min(timestamps) if timestamps else None,
            last_validation_utc=max(timestamps) if timestamps else None,
            validation_rate_per_hour=len(validations) / max(1, (max(timestamps) - min(timestamps)) / 3600) if len(timestamps) > 1 else 0.0,
            failure_rate=failed / len(validations) if validations else 0.0,
        )
    
    def compute_repository_health(self) -> RepositoryHealth:
        """Compute overall repository health."""
        metrics = self.compute_metrics()
        
        # Determine status
        if metrics.failure_rate > 0.2:
            status = "critical"
        elif metrics.failure_rate > 0.05:
            status = "warning"
        else:
            status = "healthy"
        
        return RepositoryHealth(
            overall_status=status,
            validation_pass_rate=1.0 - metrics.failure_rate,
            certification_rate=self._compute_certification_rate(),
            compliance_score=self._compute_compliance_score(),
            open_errors=self._count_open_findings("error"),
            open_warnings=self._count_open_findings("warning"),
            open_critical=self._count_open_findings("critical"),
        )
    
    def _compute_certification_rate(self) -> float:
        """Compute certification rate."""
        certifications = [
            e for e in self._events 
            if e.event_type == HistoryEventType.CERTIFICATION_ISSUED
        ]
        if not certifications:
            return 1.0
        certified = sum(1 for e in certifications if e.details.get("certified", False))
        return certified / len(certifications)
    
    def _compute_compliance_score(self) -> int:
        """Compute compliance score (0-100)."""
        # Simplified - would compute from actual compliance checks
        return 100
    
    def _count_open_findings(self, severity: str) -> int:
        """Count open findings of a given severity."""
        count = 0
        for event in self._events:
            if event.event_type == HistoryEventType.VALIDATION_PERFORMED:
                findings = event.details.get("findings", [])
                count += sum(1 for f in findings if f.get("severity") == severity)
        return count
    
    def record_score_update(self, score_type: str, value: int) -> None:
        """Record a score update."""
        if score_type not in self._score_evolution:
            self._score_evolution[score_type] = ScoreEvolution(
                score_id=f"score_{time.time_ns()}",
                score_type=score_type,
            )
        
        evolution = self._score_evolution[score_type]
        new_point = (time.time(), value)
        
        # Update data points
        current_points = list(evolution.data_points) if evolution.data_points else []
        current_points.append(new_point)
        
        # Recreate with updated data
        self._score_evolution[score_type] = ScoreEvolution(
            score_id=evolution.score_id,
            score_type=score_type,
            data_points=tuple(current_points),
            current_value=value,
            max_value=max(evolution.max_value, value),
            min_value=min(evolution.min_value, value),
        )


# =============================================================================
# DIAGNOSTIC REPORTER
# =============================================================================

class DiagnosticReporter:
    """Generates diagnostic reports from history."""
    
    def __init__(self, history_store: ValidationHistoryStore):
        self._history = history_store
    
    def generate_validation_history_report(
        self,
        since_utc: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate a validation history report.
        
        Returns:
            Report dictionary with all validation history details
        """
        events = self._history.get_events(since_utc=since_utc)
        metrics = self._history.compute_metrics()
        health = self._history.compute_repository_health()
        
        return {
            "report_id": f"vh_{time.time_ns()}",
            "generated_at_utc": time.time(),
            "summary": {
                "total_validations": metrics.total_validations,
                "passed_validations": metrics.passed_validations,
                "failed_validations": metrics.failed_validations,
                "overall_status": health.overall_status,
            },
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "timestamp_utc": e.timestamp_utc,
                    "entity_id": e.entity_id,
                    "entity_type": e.entity_type,
                    "details": e.details,
                }
                for e in events
            ],
        }
    
    def generate_score_evolution_report(
        self,
        score_type: str,
    ) -> ScoreEvolution:
        """Generate a score evolution report."""
        return self._history._score_evolution.get(score_type, ScoreEvolution(score_id=f"score_{time.time_ns()}", score_type=score_type))


__all__ = [
    "HistoryEventType",
    "HistoryEvent",
    "ValidationMetrics",
    "RepositoryHealth",
    "ScoreEvolution",
    "AuditRecord",
    "ValidationHistoryStore",
    "DiagnosticReporter",
]