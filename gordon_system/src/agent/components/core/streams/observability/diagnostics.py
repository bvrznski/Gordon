# Stream Diagnostics Layer - Phase 3.11.16
# ==========================================

"""
Canonical Stream Diagnostics implementation.

Diagnostics are PASSIVE inspection of stream state:
- They NEVER modify stream behavior
- They NEVER trigger recovery or remediation
- They ONLY read and report current state

Supported diagnostics:
- publication: Publication success/failure rates
- subscription: Subscription activity and health
- replay: Replay progress and failures  
- checkpoint: Checkpoint creation and validation
- routing: Routing decisions and delays
- correlation: Correlation chain tracking
- causation: Causal relationship analysis
- authorization: Authorization check results
- privacy: Privacy constraint verification
- trust: Trust evaluation for sources
- integrity: Integrity check results
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# DIAGNOSTIC SEVERITY
# =============================================================================


class DiagnosticSeverity(Enum):
    """
    Severity level for diagnostic findings.
    
    Order: DEBUG < INFO < NOTICE < WARNING < ERROR < CRITICAL
    """
    DEBUG = "debug"           # Detailed technical information
    INFO = "info"             # General informational message
    NOTICE = "notice"         # Normal but significant finding
    WARNING = "warning"       # Potential issue that may need attention
    ERROR = "error"           # Error condition detected
    CRITICAL = "critical"     # Critical failure requiring immediate attention


# =============================================================================
# DIAGNOSTIC FINDING
# =============================================================================


@dataclass(frozen=True)
class DiagnosticFinding:
    """
    Immutable diagnostic finding.
    
    A single diagnostic observation about stream behavior.
    Findings are read-only and never influence the system.
    """
    
    # Identity
    finding_id: str                 # Unique ID for this finding
    sequence_number: int            # Order in diagnostics
    
    # Finding details
    timestamp_utc: float            # When finding was made
    severity: DiagnosticSeverity    # Severity level
    
    # Stream context
    stream_id: Optional[str] = None     # Which stream?
    component_id: Optional[str] = None  # Which component?
    
    # Finding type and description
    category: str                   # e.g., "publication", "subscription"
    finding_type: str               # e.g., "slow_subscriber", "high_backlog"
    message: str                    # Human-readable description
    
    # Values for analysis
    metric_value: Optional[float] = None  # Measured value (if any)
    threshold_value: Optional[float] = None  # Threshold that triggered finding
    
    # Context and references
    related_records: Tuple[str, ...] = field(default_factory=tuple)  # Record IDs
    correlation_id: Optional[str] = None
    parent_finding_id: Optional[str] = None  # For hierarchical findings
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "finding_id": self.finding_id,
            "sequence_number": self.sequence_number,
            "timestamp_utc": self.timestamp_utc,
            "severity": self.severity.value,
            "stream_id": self.stream_id,
            "component_id": self.component_id,
            "category": self.category,
            "finding_type": self.finding_type,
            "message": self.message,
            "metric_value": self.metric_value,
            "threshold_value": self.threshold_value,
            "related_records": list(self.related_records),
            "correlation_id": self.correlation_id,
            "parent_finding_id": self.parent_finding_id,
        }

    @classmethod
    def create(
        cls,
        category: str,
        finding_type: str,
        message: str,
        severity: DiagnosticSeverity = DiagnosticSeverity.INFO,
        stream_id: Optional[str] = None,
        component_id: Optional[str] = None,
        metric_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
    ) -> "DiagnosticFinding":
        """Create a new diagnostic finding."""
        return cls(
            finding_id=f"diag-{time.monotonic_ns()}-{hash(message) % 1000:04d}",
            sequence_number=0,  # Will be set by manager
            timestamp_utc=time.time(),
            severity=severity,
            stream_id=stream_id,
            component_id=component_id,
            category=category,
            finding_type=finding_type,
            message=message,
            metric_value=metric_value,
            threshold_value=threshold_value,
        )


# =============================================================================
# DIAGNOSTIC REPORT
# =============================================================================


@dataclass(frozen=True)
class DiagnosticReport:
    """
    Immutable diagnostic report containing multiple findings.
    
    Used for reporting and read-only inspection of stream health.
    Contains only bounded data - no live objects or references.
    """
    
    # Identity
    report_id: str                  # Unique ID for this report
    
    # Timestamps
    created_at_utc: float           # When report was generated
    period_start_utc: Optional[float] = None  # Report period start (if applicable)
    period_end_utc: Optional[float] = None    # Report period end (if applicable)
    
    # Findings by severity
    findings: Tuple[DiagnosticFinding, ...] = field(default_factory=tuple)
    
    # Summary statistics
    total_findings: int = 0         # Total number of findings
    critical_count: int = 0         # Critical findings count
    error_count: int = 0            # Error findings count
    warning_count: int = 0          # Warning findings count
    
    def __post_init__(self):
        """Post-initialization to set computed fields."""
        if self.findings:
            object.__setattr__(self, 'total_findings', len(self.findings))
            
            critical = sum(1 for f in self.findings if f.severity == DiagnosticSeverity.CRITICAL)
            error = sum(1 for f in self.findings if f.severity == DiagnosticSeverity.ERROR)
            warning = sum(1 for f in self.findings if f.severity == DiagnosticSeverity.WARNING)
            
            object.__setattr__(self, 'critical_count', critical)
            object.__setattr__(self, 'error_count', error)
            object.__setattr__(self, 'warning_count', warning)

    def has_critical(self) -> bool:
        """Check if report contains any critical findings."""
        return self.critical_count > 0

    def has_errors(self) -> bool:
        """Check if report contains any error findings."""
        return self.error_count > 0

    def filter_by_severity(
        self,
        severity: DiagnosticSeverity
    ) -> "DiagnosticReport":
        """Filter findings by severity level."""
        filtered = tuple(f for f in self.findings if f.severity == severity)
        return dataclass_replace(self, findings=filtered)

    def filter_by_category(
        self,
        category: str
    ) -> "DiagnosticReport":
        """Filter findings by category (e.g., 'publication', 'subscription')."""
        filtered = tuple(f for f in self.findings if f.category == category)
        return dataclass_replace(self, findings=filtered)


# =============================================================================
# STREAM DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class StreamDiagnostics:
    """
    Immutable diagnostics snapshot for a stream.
    
    Contains all diagnostic information about a stream's current state.
    Used for monitoring and read-only inspection.
    """
    
    # Identity
    stream_id: str                  # Which stream?
    diagnostics_session_id: str     # Session identifier
    
    # Timestamps
    captured_at_utc: float          # When snapshot was taken
    
    # Summary statistics
    total_publications: int = 0
    total_subscriptions: int = 0
    active_replays: int = 0
    active_checkpoints: int = 0
    
    # Rate metrics (per second)
    publication_rate: float = 0.0
    subscription_rate: float = 0.0
    replay_rate: float = 0.0
    
    # Level metrics
    backlog_size: int = 0
    queue_depth: int = 0
    cursor_lag_records: int = 0
    
    # Resource utilization (percentage 0-100)
    storage_utilization_percent: float = 0.0
    memory_utilization_percent: float = 0.0
    
    # Health indicators
    backpressure_active: bool = False
    integrity_failures_total: int = 0
    
    @classmethod
    def create_empty(cls, stream_id: str) -> "StreamDiagnostics":
        """Create an empty diagnostics snapshot."""
        return cls(
            stream_id=stream_id,
            diagnostics_session_id=f"diag-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
            captured_at_utc=time.time(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "stream_id": self.stream_id,
            "diagnostics_session_id": self.diagnostics_session_id,
            "captured_at_utc": self.captured_at_utc,
            "total_publications": self.total_publications,
            "total_subscriptions": self.total_subscriptions,
            "active_replays": self.active_replays,
            "active_checkpoints": self.active_checkpoints,
            "publication_rate": self.publication_rate,
            "subscription_rate": self.subscription_rate,
            "replay_rate": self.replay_rate,
            "backlog_size": self.backlog_size,
            "queue_depth": self.queue_depth,
            "cursor_lag_records": self.cursor_lag_records,
            "storage_utilization_percent": self.storage_utilization_percent,
            "memory_utilization_percent": self.memory_utilization_percent,
            "backpressure_active": self.backpressure_active,
            "integrity_failures_total": self.integrity_failures_total,
        }


# =============================================================================
# HEALTH DIAGNOSTIC
# =============================================================================


@dataclass(frozen=True)
class HealthDiagnostic:
    """
    Diagnostic related to stream health status.
    
    Represents a diagnostic finding that affects or reflects stream health.
    """
    
    # Identity
    diagnostic_id: str              # Unique ID
    
    # Health state being diagnosed
    current_health_state: str       # Current state (healthy, degraded, etc.)
    health_issue_type: str          # Type of issue (congestion, failure, etc.)
    
    # Stream context
    stream_id: Optional[str] = None
    component_id: Optional[str] = None
    
    # Timestamps
    detected_at_utc: float = field(default_factory=time.time)
    resolved_at_utc: Optional[float] = None  # If resolved
    
    # Details
    description: str                # Human-readable description
    severity: DiagnosticSeverity = DiagnosticSeverity.WARNING
    
    # Impact assessment (read-only, never used for control)
    estimated_recovery_time_seconds: float = 0.0
    affected_records_estimate: int = 0
    
    # Resolution status
    is_resolved: bool = False
    resolution_note: Optional[str] = None
    
    def resolve(self, note: str) -> "HealthDiagnostic":
        """Create new diagnostic marked as resolved."""
        return dataclass_replace(
            self,
            is_resolved=True,
            resolved_at_utc=time.time(),
            resolution_note=note,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_diagnostic_finding(
    category: str,
    finding_type: str,
    message: str,
    severity: DiagnosticSeverity = DiagnosticSeverity.INFO,
    stream_id: Optional[str] = None,
) -> DiagnosticFinding:
    """
    Create a new diagnostic finding.
    
    Args:
        category: Category (e.g., "publication", "subscription")
        finding_type: Type of finding
        message: Human-readable description
        severity: Severity level
        stream_id: Optional stream identifier
        
    Returns:
        Immutable DiagnosticFinding instance
    """
    return DiagnosticFinding.create(
        category=category,
        finding_type=finding_type,
        message=message,
        severity=severity,
        stream_id=stream_id,
    )


def create_stream_diagnostics(
    stream_id: str,
    total_publications: int = 0,
    total_subscriptions: int = 0,
    backlog_size: int = 0,
) -> StreamDiagnostics:
    """
    Create a stream diagnostics snapshot.
    
    Args:
        stream_id: Which stream to snapshot
        total_publications: Total publications count
        total_subscriptions: Total subscriptions count  
        backlog_size: Current backlog size
        
    Returns:
        Immutable StreamDiagnostics instance
    """
    return StreamDiagnostics(
        stream_id=stream_id,
        diagnostics_session_id=f"diag-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
        captured_at_utc=time.time(),
        total_publications=total_publications,
        total_subscriptions=total_subscriptions,
        backlog_size=backlog_size,
    )


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) 
                      for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Severity
    "DiagnosticSeverity",
    
    # Findings and reports
    "DiagnosticFinding",
    "DiagnosticReport",
    
    # Stream diagnostics
    "StreamDiagnostics",
    
    # Health diagnostic
    "HealthDiagnostic",
    
    # Factory functions
    "create_diagnostic_finding",
    "create_stream_diagnostics",
    "dataclass_replace",
]