# Core Diagnostic Records
# =======================

"""
Structured diagnostic records for runtime diagnostics.

This module provides:
- Stable diagnostic codes for machine processing
- Structured evidence and remediation
- Severity classification
- Redaction support for sensitive data
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import time


# =============================================================================
# Diagnostic Codes (Machine-Processable)
# =============================================================================

class DiagnosticCode(Enum):
    """
    Machine-readable diagnostic codes.
    
    These codes allow automated systems to:
    - Group related diagnostics
    - Apply specific handling rules
    - Correlate with recovery plans
    
    Usage:
        code = DiagnosticCode.DEPENDENCY_RESOLUTION_FAILED
        report = DiagnosticReport(
            code=code,
            summary="Dependency resolution failed",
            ...
        )
    """
    
    # Lifecycle diagnostics
    LIFECYCLE_STATE_INVALID_TRANSITION = auto()
    LIFECYCLE_ENTITY_NOT_FOUND = auto()
    LIFECYCLE_TIMEOUT_EXCEEDED = auto()
    
    # Dependency diagnostics
    DEPENDENCY_RESOLUTION_FAILED = auto()
    DEPENDENCY_CYCLE_DETECTED = auto()
    DEPENDENCY_UNAVAILABLE = auto()
    
    # Registry diagnostics
    REGISTRY_ENTRY_CONFLICT = auto()
    REGISTRY_SEAL_VIOLATION = auto()
    REGISTRY_VERSION_MISMATCH = auto()
    
    # Execution diagnostics
    EXECUTION_FAILED = auto()
    EXECUTION_TIMEOUT = auto()
    EXECUTION_CANCELLATION_REQUESTED = auto()
    
    # Scheduling diagnostics
    SCHEDULING_QUEUE_FULL = auto()
    SCHEDULING_TASK_NOT_FOUND = auto()
    
    # Resource diagnostics
    RESOURCE_ACQUISITION_FAILED = auto()
    RESOURCE_LEAK_DETECTED = auto()
    RESOURCE_RELEASE_ERROR = auto()
    
    # Health diagnostics
    HEALTH_CHECK_FAILED = auto()
    HEALTH_READINESS_FALSE = auto()
    HEALTH_LIVENESS_FALSE = auto()
    
    # Integrity diagnostics
    INTEGRITY_INVARIANT_VIOLATION = auto()
    INTEGRITY_STATE_MISMATCH = auto()
    
    # Recovery diagnostics
    RECOVERY_ATTEMPTED = auto()
    RECOVERY_FAILED = auto()
    RECOVERY_BUDGET_EXHAUSTED = auto()
    
    # Runtime diagnostics
    RUNTIME_STATE_INVALID = auto()
    RUNTIME_CONTEXT_MISSING = auto()


# =============================================================================
# Diagnostic Severity Levels
# =============================================================================

class DiagnosticSeverity(Enum):
    """
    Diagnostic severity levels.
    
    These correspond to EventSeverity but focus on diagnostic impact:
        - TRACE: Internal diagnostic details (rarely logged)
        - DEBUG: Detailed diagnostic information for troubleshooting
        - INFO: Notable diagnostic events
        - NOTICE: Important diagnostic milestones
        - WARNING: Potential issues or unusual states
        - ERROR: Actual errors requiring attention
        - CRITICAL: System-impacting conditions
    """
    
    TRACE = auto()
    DEBUG = auto()
    INFO = auto()
    NOTICE = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


# =============================================================================
# Diagnostic Record
# =============================================================================

@dataclass(frozen=True)
class DiagnosticRecord:
    """
    A structured diagnostic record.
    
    Provides:
    - Stable machine-readable code for classification
    - Human-readable summary and details
    - Evidence with source context
    - Remediation guidance
    - Timestamps and correlation
    
    Usage:
        record = DiagnosticRecord(
            code=DiagnosticCode.EXECUTION_FAILED,
            severity=DiagnosticSeverity.ERROR,
            summary="Task execution failed",
            details={"error": str(error)},
            source="task_executor",
            runtime_id=runtime_id,
            entity_id=entity_id
        )
    """
    
    # Identification
    diagnostic_id: str  # Unique identifier
    code: DiagnosticCode  # Machine-readable classification
    
    # Severity and priority
    severity: DiagnosticSeverity
    is_blocking: bool = False  # Whether this blocks normal operation
    
    # Source context (must come before fields with defaults)
    source: Optional[str] = None  # Component/module that generated this
    runtime_id: Optional[str] = None  # Runtime instance identifier
    entity_id: Optional[str] = None  # Affected entity (if any)
    
    # Context (summary and details must have defaults since they come after optional fields)
    summary: str = ""  # One-line summary (empty string default)
    details: Dict[str, Any] = field(default_factory=dict)  # Extended information
    task_id: Optional[str] = None  # Task context (if any)
    
    # Timestamps
    timestamp_utc: float = field(default_factory=time.time)  # UTC wall-clock
    monotonic_time: float = field(default_factory=time.monotonic)  # For ordering
    
    # Evidence chain
    related_event_ids: List[str] = field(default_factory=list)  # Correlated events
    related_failure_id: Optional[str] = None  # Associated failure record
    
    # Remediation guidance (machine and human readable)
    remediation: Optional[str] = None
    recommended_actions: List[str] = field(default_factory=list)
    
    # Redaction tracking
    has_sensitive_data: bool = False
    
    @property
    def is_critical(self) -> bool:
        """Check if this diagnostic requires immediate attention."""
        return self.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.CRITICAL)
    
    @property
    def can_proceed(self) -> bool:
        """Check if operation can continue despite this diagnostic."""
        # Blocking or critical diagnostics indicate issues that may require action
        return not (self.is_blocking and self.is_critical)
    
    def with_details(self, **new_details: Any) -> "DiagnosticRecord":
        """Return a copy with additional details."""
        new_details_dict = dict(self.details)
        new_details_dict.update(new_details)
        
        return DiagnosticRecord(
            diagnostic_id=self.diagnostic_id,
            code=self.code,
            severity=self.severity,
            is_blocking=self.is_blocking,
            summary=self.summary,
            details=new_details_dict,
            source=self.source,
            runtime_id=self.runtime_id,
            entity_id=self.entity_id,
            task_id=self.task_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            related_event_ids=list(self.related_event_ids),
            related_failure_id=self.related_failure_id,
            remediation=self.remediation,
            recommended_actions=list(self.recommended_actions),
            has_sensitive_data=self.has_sensitive_data
        )
    
    def with_severity(self, severity: DiagnosticSeverity) -> "DiagnosticRecord":
        """Return a copy with updated severity."""
        return DiagnosticRecord(
            diagnostic_id=self.diagnostic_id,
            code=self.code,
            severity=severity,
            is_blocking=self.is_blocking,
            summary=self.summary,
            details=dict(self.details),
            source=self.source,
            runtime_id=self.runtime_id,
            entity_id=self.entity_id,
            task_id=self.task_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            related_event_ids=list(self.related_event_ids),
            related_failure_id=self.related_failure_id,
            remediation=self.remediation,
            recommended_actions=list(self.recommended_actions),
            has_sensitive_data=self.has_sensitive_data
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "diagnostic_id": self.diagnostic_id,
            "code": self.code.name if hasattr(self.code, 'name') else str(self.code),
            "severity": self.severity.name if hasattr(self.severity, 'name') else str(self.severity),
            "is_blocking": self.is_blocking,
            "summary": self.summary,
            "details": self.details,
            "source": self.source,
            "runtime_id": self.runtime_id,
            "entity_id": self.entity_id,
            "task_id": self.task_id,
            "timestamp_utc": self.timestamp_utc,
            "monotonic_time": self.monotonic_time,
            "related_event_ids": self.related_event_ids,
            "related_failure_id": self.related_failure_id,
            "remediation": self.remediation,
            "recommended_actions": self.recommended_actions,
            "has_sensitive_data": self.has_sensitive_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagnosticRecord":
        """Create a diagnostic record from a dictionary."""
        return cls(
            diagnostic_id=data["diagnostic_id"],
            code=cls._parse_code(data.get("code")),
            severity=cls._parse_severity(data.get("severity", "INFO")),
            is_blocking=data.get("is_blocking", False),
            summary=data.get("summary", ""),
            details=data.get("details", {}),
            source=data.get("source"),
            runtime_id=data.get("runtime_id"),
            entity_id=data.get("entity_id"),
            task_id=data.get("task_id"),
            timestamp_utc=data.get("timestamp_utc", time.time()),
            monotonic_time=data.get("monotonic_time", time.monotonic()),
            related_event_ids=data.get("related_event_ids", []),
            related_failure_id=data.get("related_failure_id"),
            remediation=data.get("remediation"),
            recommended_actions=data.get("recommended_actions", []),
            has_sensitive_data=data.get("has_sensitive_data", False)
        )
    
    @staticmethod
    def _parse_code(code_value: Any) -> DiagnosticCode:
        """Parse a code value into a DiagnosticCode enum."""
        if isinstance(code_value, DiagnosticCode):
            return code_value
        
        if isinstance(code_value, str):
            try:
                return DiagnosticCode[code_value]
            except KeyError:
                pass
        
        # Return a generic diagnostic code for unrecognized values
        return DiagnosticCode.RUNTIME_STATE_INVALID
    
    @staticmethod
    def _parse_severity(severity_value: Any) -> DiagnosticSeverity:
        """Parse a severity value into a DiagnosticSeverity enum."""
        if isinstance(severity_value, DiagnosticSeverity):
            return severity_value
        
        if isinstance(severity_value, str):
            try:
                return DiagnosticSeverity[severity_value.upper()]
            except KeyError:
                pass
        
        # Default to INFO
        return DiagnosticSeverity.INFO
    
    @classmethod
    def create(
        cls,
        code: DiagnosticCode,
        summary: str,
        severity: Optional[DiagnosticSeverity] = None,
        is_blocking: bool = False,
        source: Optional[str] = None,
        runtime_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        task_id: Optional[str] = None,
        **details
    ) -> "DiagnosticRecord":
        """
        Create a new diagnostic record.
        
        Args:
            code: Machine-readable classification
            summary: Human-readable summary
            severity: DiagnosticSeverity (defaults to WARNING for errors, INFO otherwise)
            is_blocking: Whether this blocks normal operation
            source: Component that generated this diagnostic
            runtime_id: Runtime instance identifier
            entity_id: Affected entity (if any)
            task_id: Task context (if any)
            **details: Additional diagnostic information
            
        Returns:
            A new DiagnosticRecord instance
        """
        if severity is None:
            # Default severity based on code type
            if code in (
                DiagnosticCode.EXECUTION_FAILED,
                DiagnosticCode.INTEGRITY_INVARIANT_VIOLATION,
                DiagnosticCode.DEPENDENCY_RESOLUTION_FAILED
            ):
                severity = DiagnosticSeverity.ERROR
            else:
                severity = DiagnosticSeverity.INFO
        
        return cls(
            diagnostic_id=f"diag_{time.monotonic_ns()}",
            code=code,
            severity=severity,
            is_blocking=is_blocking,
            summary=summary,
            details=details,
            source=source,
            runtime_id=runtime_id,
            entity_id=entity_id,
            task_id=task_id
        )


# =============================================================================
# Diagnostic Report (Collection of Records)
# =============================================================================

@dataclass(frozen=True)
class DiagnosticReport:
    """
    A collection of diagnostic records for a specific scope.
    
    Usage:
        report = DiagnosticReport(
            subject="runtime",
            records=[record1, record2, ...],
            timestamp=time.monotonic()
        )
        
        # Check overall status
        if report.has_critical:
            # Handle critical diagnostics
            pass
        
        # Get diagnostics by severity
        warnings = report.get_by_severity(DiagnosticSeverity.WARNING)
    """
    
    subject: str  # What these diagnostics are about (entity_id, scope, etc.)
    records: List[DiagnosticRecord]
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    @property
    def count(self) -> int:
        """Return total number of diagnostic records."""
        return len(self.records)
    
    @property
    def has_critical(self) -> bool:
        """Check if any record is critical."""
        return any(r.is_critical for r in self.records)
    
    @property
    def has_blocking(self) -> bool:
        """Check if any blocking diagnostics exist."""
        return any(r.is_blocking for r in self.records)
    
    def get_by_severity(self, severity: DiagnosticSeverity) -> List[DiagnosticRecord]:
        """Get all records with the specified severity."""
        return [r for r in self.records if r.severity == severity]
    
    def get_by_code(self, code: DiagnosticCode) -> List[DiagnosticRecord]:
        """Get all records matching the specified diagnostic code."""
        return [r for r in self.records if r.code == code]
    
    def get_errors(self) -> List[DiagnosticRecord]:
        """Get all error-level and critical diagnostics."""
        return [
            r for r in self.records
            if r.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.CRITICAL)
        ]
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "subject": self.subject,
            "timestamp_utc": self.timestamp_utc,
            "monotonic_time": self.monotonic_time,
            "count": len(self.records),
            "has_critical": self.has_critical,
            "has_blocking": self.has_blocking,
            "records": [r.to_serializable() for r in self.records]
        }


# =============================================================================
# Diagnostic Record Factories
# =============================================================================

def create_diagnostic_record(
    code: DiagnosticCode,
    summary: str,
    **kwargs
) -> DiagnosticRecord:
    """
    Create a diagnostic record with common defaults.
    
    Args:
        code: Machine-readable classification
        summary: Human-readable summary
        **kwargs: Additional DiagnosticRecord parameters
        
    Returns:
        A new DiagnosticRecord instance
    """
    return DiagnosticRecord.create(code=code, summary=summary, **kwargs)


def create_error_diagnostic(
    summary: str,
    source: Optional[str] = None,
    runtime_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    **details
) -> DiagnosticRecord:
    """Create an ERROR-level diagnostic record."""
    return DiagnosticRecord.create(
        code=DiagnosticCode.RUNTIME_STATE_INVALID,
        summary=summary,
        severity=DiagnosticSeverity.ERROR,
        source=source,
        runtime_id=runtime_id,
        entity_id=entity_id,
        task_id=task_id,
        **details
    )


def create_warning_diagnostic(
    summary: str,
    source: Optional[str] = None,
    runtime_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    **details
) -> DiagnosticRecord:
    """Create a WARNING-level diagnostic record."""
    return DiagnosticRecord.create(
        code=DiagnosticCode.RUNTIME_STATE_INVALID,
        summary=summary,
        severity=DiagnosticSeverity.WARNING,
        source=source,
        runtime_id=runtime_id,
        entity_id=entity_id,
        task_id=task_id,
        **details
    )


def create_critical_diagnostic(
    summary: str,
    source: Optional[str] = None,
    runtime_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    is_blocking: bool = True,
    **details
) -> DiagnosticRecord:
    """Create a CRITICAL-level diagnostic record."""
    return DiagnosticRecord.create(
        code=DiagnosticCode.RUNTIME_STATE_INVALID,
        summary=summary,
        severity=DiagnosticSeverity.CRITICAL,
        is_blocking=is_blocking,
        source=source,
        runtime_id=runtime_id,
        entity_id=entity_id,
        task_id=task_id,
        **details
    )


__all__ = [
    # Diagnostic codes (machine-readable)
    "DiagnosticCode",
    
    # Severity levels
    "DiagnosticSeverity",
    
    # Record types
    "DiagnosticRecord",
    "DiagnosticReport",
    
    # Factories
    "create_diagnostic_record",
    "create_error_diagnostic",
    "create_warning_diagnostic",
    "create_critical_diagnostic",
]