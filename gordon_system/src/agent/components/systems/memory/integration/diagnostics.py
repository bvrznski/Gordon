# Integration Diagnostics - Phase 5.1.7 Diagnostic Information System
# ==================================================================

"""
Memory Integration Diagnostics: Collects and provides diagnostic information.

Diagnostics provide:
    - Runtime state information
    - Error details for troubleshooting
    - Performance bottleneck identification
    - Contract violation detection

Diagnostic Laws:
    DIAGNOSTICS-LAW-001: Diagnostics must be available for all operations
    DIAGNOSTICS-LAW-002: Diagnostic data must be inspectable
    DIAGNOSTICS-LAW-003: Diagnostics must preserve privacy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# DIAGNOSTIC SEVERITY
# =============================================================================


class DiagnosticSeverity(Enum):
    """
    Severity levels for diagnostics.
    
    | Level       | Description                                      |
    |-------------|--------------------------------------------------|
    | DEBUG       | Debug information                                |
    | INFO        | Informational messages                           |
    | WARNING     | Warning conditions                               |
    | ERROR       | Error conditions                                 |
    | CRITICAL    | Critical failures                                |
    """
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# =============================================================================
# DIAGNOSTIC CATEGORY
# =============================================================================


class DiagnosticCategory(Enum):
    """
    Categories for diagnostic messages.
    
    | Category     | Description                                     |
    |--------------|-------------------------------------------------|
    | REQUEST      | Request processing                              |
    | RESPONSE     | Response generation                             |
    | AUTHORIZATION| Authorization decisions                         |
    | VALIDATION   | Validation results                              |
    | LATENCY      | Latency measurements                            |
    | CONTRACT     | Contract violations                             |
    | SESSION      | Session management                              |
    | SYSTEM       | System-level events                             |
    """
    
    REQUEST = "request"
    RESPONSE = "response"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    LATENCY = "latency"
    CONTRACT = "contract"
    SESSION = "session"
    SYSTEM = "system"


# =============================================================================
# DIAGNOSTIC ENTRY
# =============================================================================


@dataclass(frozen=True)
class DiagnosticEntry:
    """
    A single diagnostic entry.
    
    Fields:
        timestamp_utc: When was this diagnostic generated?
        severity:      What is the severity level?
        category:      What category does this belong to?
        
        message:       Human-readable message
        code:          Machine-readable code
        
        # Context
        request_id:    Request ID (if applicable)
        consumer:      Consumer name (if applicable)
        
        # Additional data
        details:       Additional structured data
    """
    
    timestamp_utc: float                    # When generated
    
    severity: DiagnosticSeverity = DiagnosticSeverity.INFO
    category: DiagnosticCategory = DiagnosticCategory.SYSTEM
    
    message: str = ""
    code: str = ""
    
    request_id: Optional[str] = None
    consumer: Optional[str] = None
    
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# SESSION DIAGNOSTIC
# =============================================================================


@dataclass(frozen=True)
class SessionDiagnostic:
    """
    Diagnostic information about an integration session.
    
    Fields:
        session_id:      Unique session identifier
        
        # Lifecycle
        started_at:     When was the session started?
        ended_at:       When did the session end? (or None if active)
        duration_ms:    Total duration in milliseconds
        
        # Statistics
        request_count:   Number of requests in session
        response_count:  Number of responses in session
        
        # Diagnostics
        entries:         Diagnostic entries for this session
    """
    
    session_id: str                         # Unique identifier
    
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    duration_ms: float = 0.0
    
    request_count: int = 0
    response_count: int = 0
    
    entries: Tuple[DiagnosticEntry, ...] = field(default_factory=tuple)


# =============================================================================
# INTEGRATION DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class IntegrationDiagnostics:
    """
    Complete diagnostics for an integration.
    
    Fields:
        integration_type: Which integration is this?
        
        # Session info
        session_id:      Current session ID
        
        # Counters
        total_requests:  Total requests processed
        total_responses: Total responses generated
        
        # Diagnostics
        entries:         Recent diagnostic entries
        warnings:        Number of warnings
        errors:          Number of errors
        
        # Time range
        started_at:      When did diagnostics collection start?
        last_activity:   When was the last activity?
    """
    
    integration_type: str                   # e.g., "perception", "workspace"
    
    session_id: str = ""
    
    total_requests: int = 0
    total_responses: int = 0
    
    entries: Tuple[DiagnosticEntry, ...] = field(default_factory=tuple)
    warnings: int = 0
    errors: int = 0
    
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)


# =============================================================================
# DIAGNOSTICS COLLECTOR
# =============================================================================


class DiagnosticsCollector:
    """
    Collector for integration diagnostics.
    
    Collects, stores, and provides access to diagnostic information
    for troubleshooting and monitoring.
    
    Usage:
        collector = DiagnosticsCollector()
        
        # Record diagnostics
        collector.record_entry("perception", 
                              DiagnosticSeverity.INFO,
                              "request_processed")
        
        # Get diagnostics for an integration
        diag = collector.get_diagnostics("perception")
    """
    
    def __init__(self, max_entries: int = 1000):
        self._diagnostics: Dict[str, IntegrationDiagnostics] = {}
        self._sessions: Dict[str, SessionDiagnostic] = {}
        self.max_entries = max_entries
    
    def record_entry(self, integration_type: str,
                     severity: DiagnosticSeverity,
                     message: str,
                     category: Optional[DiagnosticCategory] = None,
                     request_id: Optional[str] = None,
                     consumer: Optional[str] = None,
                     **kwargs) -> None:
        """Record a diagnostic entry."""
        if integration_type not in self._diagnostics:
            self._init_diagnostics(integration_type)
        
        diag = self._diagnostics[integration_type]
        
        # Create new entry
        entry = DiagnosticEntry(
            timestamp_utc=time.time(),
            severity=severity,
            category=category or DiagnosticCategory.SYSTEM,
            message=message,
            code=self._generate_code(severity, category),
            request_id=request_id,
            consumer=consumer,
            details=kwargs
        )
        
        # Update counters
        new_warnings = diag.warnings
        new_errors = diag.errors
        
        if severity == DiagnosticSeverity.WARNING:
            new_warnings = diag.warnings + 1
        elif severity == DiagnosticSeverity.ERROR:
            new_errors = diag.errors + 1
        
        # Add entry (keeping only recent ones)
        new_entries = list(diag.entries) + [entry]
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        self._diagnostics[integration_type] = dataclass_replace(diag,
                                                                 entries=tuple(new_entries),
                                                                 warnings=new_warnings,
                                                                 errors=new_errors,
                                                                 last_activity=time.time())
    
    def start_session(self, integration_type: str) -> str:
        """Start a new diagnostic session."""
        import uuid
        
        session_id = str(uuid.uuid4())
        
        self._sessions[session_id] = SessionDiagnostic(session_id=session_id)
        
        # Link to integration diagnostics
        if integration_type not in self._diagnostics:
            self._init_diagnostics(integration_type)
        
        diag = self._diagnostics[integration_type]
        self._diagnostics[integration_type] = dataclass_replace(diag,
                                                                 session_id=session_id)
        
        return session_id
    
    def end_session(self, session_id: str) -> None:
        """End a diagnostic session."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            self._sessions[session_id] = dataclass_replace(session,
                                                            ended_at=time.time(),
                                                            duration_ms=(session.ended_at or time.time()) - session.started_at)
    
    def record_request(self, integration_type: str, 
                       request_id: Optional[str] = None) -> None:
        """Record a request in diagnostics."""
        if integration_type not in self._diagnostics:
            self._init_diagnostics(integration_type)
        
        diag = self._diagnostics[integration_type]
        self._diagnostics[integration_type] = dataclass_replace(diag,
                                                                 total_requests=diag.total_requests + 1,
                                                                 last_activity=time.time())
        
        # Record in session too
        if diag.session_id and diag.session_id in self._sessions:
            session = self._sessions[diag.session_id]
            self._sessions[diag.session_id] = dataclass_replace(session,
                                                                  request_count=session.request_count + 1)
    
    def record_response(self, integration_type: str,
                        success: bool = True) -> None:
        """Record a response in diagnostics."""
        if integration_type not in self._diagnostics:
            self._init_diagnostics(integration_type)
        
        diag = self._diagnostics[integration_type]
        self._diagnostics[integration_type] = dataclass_replace(diag,
                                                                 total_responses=diag.total_responses + 1,
                                                                 last_activity=time.time())
    
    def get_diagnostics(self, integration_type: str) -> Optional[IntegrationDiagnostics]:
        """Get diagnostics for an integration."""
        return self._diagnostics.get(integration_type)
    
    def get_all_diagnostics(self) -> Dict[str, IntegrationDiagnostics]:
        """Get all diagnostics."""
        return dict(self._diagnostics)
    
    def get_session_diagnostics(self, session_id: str) -> Optional[SessionDiagnostic]:
        """Get diagnostics for a specific session."""
        return self._sessions.get(session_id)
    
    def _init_diagnostics(self, integration_type: str) -> None:
        """Initialize diagnostics for a new integration."""
        self._diagnostics[integration_type] = IntegrationDiagnostics(
            integration_type=integration_type
        )
    
    def _generate_code(self, severity: DiagnosticSeverity,
                       category: Optional[DiagnosticCategory]) -> str:
        """Generate a machine-readable diagnostic code."""
        cat_prefix = category.value[0].upper() if category else "S"
        sev_prefix = severity.value[0].upper()
        
        # Simple counter-based codes
        count = 1
        for k in self._diagnostics.get(severity.value, {}).get("codes", {}):
            count += 1
        
        code = f"{cat_prefix}{sev_prefix}{count:03d}"
        
        if severity.value not in self._diagnostics:
            self._diagnostics[severity.value] = {"codes": {code: True}}
        else:
            self._diagnostics[severity.value]["codes"][code] = True
        
        return code


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace (Python 3.7 compatible)."""
    fields = instance.__dataclass_fields__
    return type(instance)(
        **{f.name: kwargs.get(f.name, getattr(instance, f.name)) 
           for f in fields.values()}
    )