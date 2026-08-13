# Stream Logging Layer - Phase 3.11.16
# ======================================

"""
Canonical Stream Logging implementation.

Logging is PASSIVE structured record creation:
- It NEVER influences execution flow
- It NEVER modifies stream state
- It ONLY records events for later inspection

Supported log types:
- publication: Publication events (attempt, success, failure)
- routing: Routing decisions and outcomes
- replay: Replay operations (request, start, complete, failure)
- checkpoint: Checkpoint creation and validation
- failures: Error and failure records
- diagnostics: Diagnostic event logs
- integrity: Integrity check results
- authorization: Authorization decision logs
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# LOG SEVERITY
# =============================================================================


class LogSeverity(Enum):
    """Severity level of a log record."""
    DEBUG = "debug"           # Detailed technical information
    INFO = "info"             # General informational message
    NOTICE = "notice"         # Normal but significant message
    WARNING = "warning"       # Warning about potential issue
    ERROR = "error"           # Error condition detected
    CRITICAL = "critical"     # Critical failure requiring attention


# =============================================================================
# STRUCTURED LOG ENTRY
# =============================================================================


@dataclass(frozen=True)
class StructuredLogEntry:
    """
    Immutable structured log entry.
    
    A single log record with structured fields for easy parsing and analysis.
    Log entries are never modified after creation.
    """
    
    # Identity
    log_id: str                     # Unique ID for this log entry
    
    # Timestamp
    timestamp_utc: float            # When log was created
    
    # Severity
    severity: LogSeverity           # Severity level
    
    # Stream context
    stream_id: Optional[str] = None     # Which stream?
    component_id: Optional[str] = None  # Which component?
    
    # Message and metadata
    message: str                    # Human-readable message
    category: str                   # e.g., "publication", "routing"
    
    # Structured data (bounded, serializable)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "log_id": self.log_id,
            "timestamp_utc": self.timestamp_utc,
            "severity": self.severity.value,
            "stream_id": self.stream_id,
            "component_id": self.component_id,
            "message": self.message,
            "category": self.category,
            "context": dict(self.context),
        }

    @classmethod
    def create(
        cls,
        message: str,
        severity: LogSeverity = LogSeverity.INFO,
        stream_id: Optional[str] = None,
        component_id: Optional[str] = None,
        category: str = "general",
        context: Optional[Dict[str, Any]] = None,
    ) -> "StructuredLogEntry":
        """Create a new structured log entry."""
        return cls(
            log_id=f"log-{time.monotonic_ns()}-{hash(message) % 1000:04d}",
            timestamp_utc=time.time(),
            severity=severity,
            stream_id=stream_id,
            component_id=component_id,
            message=message,
            category=category,
            context=dict(context or {}),
        )


# =============================================================================
# STREAM LOG RECORD
# =============================================================================


@dataclass(frozen=True)
class StreamLogRecord:
    """
    Immutable log record for a specific stream.
    
    Contains all log entries related to a single stream's activity.
    Used for monitoring and read-only inspection.
    """
    
    # Identity
    stream_id: str                  # Which stream?
    log_session_id: str             # Session identifier
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    
    # Log entries
    entries: Tuple[StructuredLogEntry, ...] = field(default_factory=tuple)
    
    # Statistics
    total_entries: int = 0          # Number of log entries
    error_count: int = 0            # Error count
    warning_count: int = 0          # Warning count
    
    def __post_init__(self):
        """Post-initialization to set computed fields."""
        if self.entries:
            object.__setattr__(self, 'total_entries', len(self.entries))
            
            errors = sum(1 for e in self.entries if e.severity == LogSeverity.ERROR)
            warnings = sum(1 for e in self.entries if e.severity == LogSeverity.WARNING)
            
            object.__setattr__(self, 'error_count', errors)
            object.__setattr__(self, 'warning_count', warnings)

    def filter_by_severity(
        self,
        severity: LogSeverity
    ) -> Tuple[StructuredLogEntry, ...]:
        """Filter entries by severity level."""
        return tuple(e for e in self.entries if e.severity == severity)


# =============================================================================
# STREAM LOGGER (PROTOCOL)
# =============================================================================


from typing import Protocol, runtime_checkable


@runtime_checkable
class StreamLogger(Protocol):
    """
    Protocol for stream logging.
    
    CRITICAL PRINCIPLE: Logger is PASSIVE. It NEVER:
        - Modifies stream data or behavior
        - Triggers any side effects
        - Influences execution flow
        
    It only:
        - Creates log records
        - Maintains structured format
        - Preserves deterministic order
    """
    
    async def initialize(self) -> None:
        """Initialize the logger."""
        ...
    
    async def shutdown(self) -> None:
        """Shutdown the logger cleanly."""
        ...
    
    async def log(
        self,
        message: str,
        severity: LogSeverity = LogSeverity.INFO,
        stream_id: Optional[str] = None,
        component_id: Optional[str] = None,
        category: str = "general",
        context: Optional[Dict[str, Any]] = None,
    ) -> StructuredLogEntry:
        """
        Create and store a log entry.
        
        Args:
            message: Human-readable log message
            severity: Severity level
            stream_id: Optional stream identifier
            component_id: Optional component identifier
            category: Log category
            context: Additional structured data
            
        Returns:
            Immutable StructuredLogEntry instance
            
        Note: This method is PASSIVE - it only creates the record.
        """
        ...
    
    async def get_logs_for_stream(
        self,
        stream_id: str,
        limit: int = 1000,
        before_utc: Optional[float] = None,
    ) -> StreamLogRecord:
        """Get log records for a specific stream."""
        ...


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_log_entry(
    message: str,
    severity: LogSeverity = LogSeverity.INFO,
    stream_id: Optional[str] = None,
    category: str = "general",
) -> StructuredLogEntry:
    """
    Create a new structured log entry.
    
    Args:
        message: Human-readable log message
        severity: Severity level
        stream_id: Optional stream identifier
        category: Log category
        
    Returns:
        Immutable StructuredLogEntry instance
    """
    return StructuredLogEntry.create(
        message=message,
        severity=severity,
        stream_id=stream_id,
        category=category,
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
    "LogSeverity",
    
    # Log entries and records
    "StructuredLogEntry",
    "StreamLogRecord",
    
    # Logger protocol
    "StreamLogger",
    
    # Factory functions
    "create_log_entry",
    "dataclass_replace",
]