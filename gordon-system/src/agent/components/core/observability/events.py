# Core Runtime Events
# ====================

"""
Structured runtime event model for observability.

This module provides:
- Typed event envelope with correlation and causality tracking
- Event categories, severity levels, and domains
- Immutable event records with redaction support
- Bounded history storage
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum, auto
import time
import uuid


# =============================================================================
# Event Severity Levels
# =============================================================================

class EventSeverity(Enum):
    """
    Event severity levels for observability.
    
    Severity ordering (lowest to highest): TRACE < DEBUG < INFO < NOTICE < 
    WARNING < ERROR < CRITICAL < FATAL
    
    Usage:
        - TRACE: Verbose internal debugging information
        - DEBUG: Detailed diagnostic information
        - INFO: General operational information
        - NOTICE: Notable events that don't require action
        - WARNING: Potential issues or unexpected states
        - ERROR: Failed operations, recoverable errors
        - CRITICAL: Serious failures requiring attention
        - FATAL: System-impacting failures
    """
    
    TRACE = auto()      # Verbose debugging
    DEBUG = auto()      # Detailed diagnostics
    INFO = auto()       # Operational information
    NOTICE = auto()     # Notable but non-actionable events
    WARNING = auto()    # Potential issues
    ERROR = auto()      # Recoverable failures
    CRITICAL = auto()   # Serious failures
    FATAL = auto()      # System-impacting failures
    
    @property
    def is_critical(self) -> bool:
        """Check if this severity requires immediate attention."""
        return self in (EventSeverity.CRITICAL, EventSeverity.FATAL)
    
    @property
    def is_error(self) -> bool:
        """Check if this severity represents an error condition."""
        return self in (EventSeverity.ERROR, EventSeverity.CRITICAL, 
                        EventSeverity.FATAL)


# =============================================================================
# Event Categories
# =============================================================================

class EventCategory(Enum):
    """
    Event category classification.
    
    Categories group events by their operational context and domain.
    """
    
    # Lifecycle categories
    LIFECYCLE = "lifecycle"       # Entity lifecycle transitions
    DEPENDENCY = "dependency"     # Dependency resolution and binding
    
    # Registry categories
    REGISTRY = "registry"         # Registration operations
    
    # Bootstrap categories
    BOOTSTRAP = "bootstrap"       # Startup initialization
    PREFLIGHT = "preflight"       # Pre-startup validation
    LOADING = "loading"           # Module/component loading
    
    # Initialization categories
    INITIALIZATION = "initialization"  # Component initialization
    
    # Execution categories
    EXECUTION = "execution"       # Task execution
    SCHEDULING = "scheduling"     # Task scheduling
    CANCELLATION = "cancellation" # Task cancellation
    TIMEOUT = "timeout"           # Operation timeouts
    
    # Resource categories
    RESOURCE = "resource"         # Resource allocation and release
    
    # Health categories
    HEALTH = "health"             # Health state changes
    INTEGRITY = "integrity"       # Integrity validation results
    RECOVERY = "recovery"         # Recovery operations
    
    # Shutdown categories
    SHUTDOWN = "shutdown"         # Shutdown operations
    
    # Security categories
    SECURITY = "security"         # Security-related events
    
    # Diagnostic categories
    DIAGNOSTIC = "diagnostic"     # General diagnostics


# =============================================================================
# Event Envelope
# =============================================================================

@dataclass(frozen=True)
class RuntimeEvent:
    """
    Structured runtime event envelope.
    
    Provides:
    - Unique event identification with correlation and causation tracking
    - Timestamps for both wall-clock and monotonic time
    - Contextual information (runtime, entity, task identifiers)
    - Payload with domain-specific data
    - Redaction control for sensitive information
    
    Events are immutable and hashable by their identifier.
    """
    
    # Event identification
    event_id: str  # Unique event UUID
    event_type: str  # Machine-readable type (e.g., "lifecycle.transition")
    
    # Causality tracking
    correlation_id: Optional[str] = None  # Groups related events
    causation_id: Optional[str] = None    # Identifies the causing event
    
    # Context identifiers
    runtime_id: str = ""                   # Runtime instance identifier
    source_entity_id: Optional[str] = None  # Entity that generated this event
    task_id: Optional[str] = None          # Task context (if any)
    parent_task_id: Optional[str] = None   # Parent task (for hierarchy)
    
    # Tracing identifiers
    trace_id: Optional[str] = None      # End-to-end trace identifier
    span_id: Optional[str] = None       # Span within the trace
    
    # Timestamps
    timestamp_utc: float = field(default_factory=time.time)  # UTC wall-clock time (Unix epoch seconds)
    monotonic_time: float = field(default_factory=time.monotonic)  # Monotonic time for ordering
    
    # Event content (must have defaults after fields with defaults)
    category: str = ""  # EventCategory value or custom string
    severity: int = 0  # EventSeverity value (INFO=3, default to 0 for safety)
    message: str = ""  # Human-readable summary
    
    # Payload with domain-specific data
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Redaction status
    redacted_fields: Set[str] = field(default_factory=set)  # Fields that were redacted
    is_redacted: bool = False  # Whether the event contains sensitive data
    
    def __hash__(self) -> int:
        """Hash by event_id for set/dict operations."""
        return hash(self.event_id)
    
    def with_correlation(self, correlation_id: str) -> "RuntimeEvent":
        """Return a copy with the specified correlation ID."""
        return RuntimeEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            correlation_id=correlation_id,
            causation_id=self.causation_id,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            parent_task_id=self.parent_task_id,
            trace_id=self.trace_id,
            span_id=self.span_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            category=self.category,
            severity=self.severity,
            message=self.message,
            payload=dict(self.payload),
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def with_causation(self, causation_id: str) -> "RuntimeEvent":
        """Return a copy with the specified causation ID."""
        return RuntimeEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            correlation_id=self.correlation_id,
            causation_id=causation_id,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            parent_task_id=self.parent_task_id,
            trace_id=self.trace_id,
            span_id=self.span_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            category=self.category,
            severity=self.severity,
            message=self.message,
            payload=dict(self.payload),
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def with_runtime_context(
        self,
        runtime_id: str,
        entity_id: Optional[str] = None,
        task_id: Optional[str] = None,
        parent_task_id: Optional[str] = None
    ) -> "RuntimeEvent":
        """Return a copy with runtime and task context."""
        return RuntimeEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            runtime_id=runtime_id,
            source_entity_id=entity_id,
            task_id=task_id,
            parent_task_id=parent_task_id,
            trace_id=self.trace_id,
            span_id=self.span_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            category=self.category,
            severity=self.severity,
            message=self.message,
            payload=dict(self.payload),
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def with_trace_context(
        self,
        trace_id: str,
        span_id: Optional[str] = None
    ) -> "RuntimeEvent":
        """Return a copy with tracing identifiers."""
        return RuntimeEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            parent_task_id=self.parent_task_id,
            trace_id=trace_id,
            span_id=span_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            category=self.category,
            severity=self.severity,
            message=self.message,
            payload=dict(self.payload),
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def with_payload(self, key: str, value: Any) -> "RuntimeEvent":
        """Return a copy with an additional payload entry."""
        new_payload = dict(self.payload)
        new_payload[key] = value
        return RuntimeEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            parent_task_id=self.parent_task_id,
            trace_id=self.trace_id,
            span_id=self.span_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            category=self.category,
            severity=self.severity,
            message=self.message,
            payload=new_payload,
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def with_severity(self, severity: EventSeverity) -> "RuntimeEvent":
        """Return a copy with updated severity."""
        return RuntimeEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            parent_task_id=self.parent_task_id,
            trace_id=self.trace_id,
            span_id=self.span_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            category=self.category,
            severity=severity.value,
            message=self.message,
            payload=dict(self.payload),
            redacted_fields=set(self.redacted_fields),
            is_redacted=self.is_redacted
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert event to a JSON-serializable dictionary.
        
        This preserves all fields except the frozen dataclass structure.
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "runtime_id": self.runtime_id,
            "source_entity_id": self.source_entity_id,
            "task_id": self.task_id,
            "parent_task_id": self.parent_task_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "timestamp_utc": self.timestamp_utc,
            "monotonic_time": self.monotonic_time,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "payload": self.payload,
            "redacted_fields": list(self.redacted_fields),
            "is_redacted": self.is_redacted
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuntimeEvent":
        """Create an event from a dictionary."""
        # Convert severity int back to EventSeverity enum value if needed
        severity = data.get("severity", EventSeverity.INFO.value)
        if isinstance(severity, EventSeverity):
            severity = severity.value
        
        return cls(
            event_id=data["event_id"],
            event_type=data.get("event_type", "unknown"),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            runtime_id=data.get("runtime_id", ""),
            source_entity_id=data.get("source_entity_id"),
            task_id=data.get("task_id"),
            parent_task_id=data.get("parent_task_id"),
            trace_id=data.get("trace_id"),
            span_id=data.get("span_id"),
            timestamp_utc=data["timestamp_utc"],
            monotonic_time=data.get("monotonic_time", data["timestamp_utc"]),
            category=data.get("category", ""),
            severity=severity,
            message=data.get("message", ""),
            payload=data.get("payload", {}),
            redacted_fields=set(data.get("redacted_fields", [])),
            is_redacted=data.get("is_redacted", False)
        )


# =============================================================================
# Event Factories
# =============================================================================

def create_event(
    event_type: str,
    message: str,
    category: Optional[str] = None,
    severity: EventSeverity = EventSeverity.INFO,
    runtime_id: str = "",
    source_entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    parent_task_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    causation_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    **payload
) -> RuntimeEvent:
    """
    Create a new runtime event.
    
    Args:
        event_type: Machine-readable type (e.g., "lifecycle.transition")
        message: Human-readable summary
        category: EventCategory value or custom string
        severity: Event severity level
        runtime_id: Runtime instance identifier
        source_entity_id: Entity that generated this event
        task_id: Task context identifier
        parent_task_id: Parent task for hierarchy
        correlation_id: Groups related events
        causation_id: Identifies the causing event
        trace_id: End-to-end trace identifier
        span_id: Span within the trace
        **payload: Domain-specific data
    
    Returns:
        A new RuntimeEvent instance
    """
    now = time.monotonic()
    
    return RuntimeEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        correlation_id=correlation_id,
        causation_id=causation_id,
        runtime_id=runtime_id,
        source_entity_id=source_entity_id,
        task_id=task_id,
        parent_task_id=parent_task_id,
        trace_id=trace_id,
        span_id=span_id,
        timestamp_utc=time.time(),
        monotonic_time=now,
        category=category or EventCategory.DIAGNOSTIC.value,
        severity=severity.value,
        message=message,
        payload=payload
    )


def create_lifecycle_event(
    entity_id: str,
    from_state: str,
    to_state: str,
    runtime_id: str = "",
    task_id: Optional[str] = None,
    **payload
) -> RuntimeEvent:
    """Create a lifecycle transition event."""
    message = f"Entity {entity_id} transitioning from {from_state} to {to_state}"
    
    return create_event(
        event_type="lifecycle.transition",
        message=message,
        category=EventCategory.LIFECYCLE.value,
        severity=EventSeverity.INFO,
        runtime_id=runtime_id,
        source_entity_id=entity_id,
        task_id=task_id,
        from_state=from_state,
        to_state=to_state,
        **payload
    )


def create_error_event(
    error: Exception,
    message: Optional[str] = None,
    runtime_id: str = "",
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    recoverable: bool = True,
    **payload
) -> RuntimeEvent:
    """Create an error event with exception context."""
    if message is None:
        message = f"Error occurred: {type(error).__name__}"
    
    return create_event(
        event_type="execution.error",
        message=message,
        category=EventCategory.EXECUTION.value,
        severity=EventSeverity.ERROR,
        runtime_id=runtime_id,
        source_entity_id=entity_id,
        task_id=task_id,
        exception_type=type(error).__name__,
        exception_message=str(error),
        recoverable=recoverable,
        **payload
    )


def create_warning_event(
    message: str,
    runtime_id: str = "",
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    **payload
) -> RuntimeEvent:
    """Create a warning event."""
    return create_event(
        event_type="runtime.warning",
        message=message,
        category=EventCategory.DIAGNOSTIC.value,
        severity=EventSeverity.WARNING,
        runtime_id=runtime_id,
        source_entity_id=entity_id,
        task_id=task_id,
        **payload
    )


def create_critical_event(
    message: str,
    runtime_id: str = "",
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    **payload
) -> RuntimeEvent:
    """Create a critical event requiring immediate attention."""
    return create_event(
        event_type="runtime.critical",
        message=message,
        category=EventCategory.DIAGNOSTIC.value,
        severity=EventSeverity.CRITICAL,
        runtime_id=runtime_id,
        source_entity_id=entity_id,
        task_id=task_id,
        **payload
    )


def create_fatal_event(
    message: str,
    runtime_id: str = "",
    entity_id: Optional[str] = None,
    task_id: Optional[str] = None,
    **payload
) -> RuntimeEvent:
    """Create a fatal event indicating system failure."""
    return create_event(
        event_type="runtime.fatal",
        message=message,
        category=EventCategory.DIAGNOSTIC.value,
        severity=EventSeverity.FATAL,
        runtime_id=runtime_id,
        source_entity_id=entity_id,
        task_id=task_id,
        **payload
    )


__all__ = [
    # Severity
    "EventSeverity",
    
    # Categories
    "EventCategory",
    
    # Event types
    "RuntimeEvent",
    
    # Factories
    "create_event",
    "create_lifecycle_event",
    "create_error_event",
    "create_warning_event",
    "create_critical_event",
    "create_fatal_event",
]