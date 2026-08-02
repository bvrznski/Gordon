# Core Observability Infrastructure
# ==================================

"""
Core runtime observability.

Provides structured runtime visibility with:
- Structured event records
- Health reporting
- Metrics and trace contracts
- Logger adapter contract
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class LogSeverity(Enum):
    """Logging severity levels."""
    
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class EventRecord:
    """
    Structured event record for observability.
    
    Args:
        timestamp: Monotonic timestamp
        severity: Event severity level
        category: Event category (e.g., "lifecycle", "execution")
        message: Human-readable message
        attributes: Additional key-value pairs
    """
    
    timestamp: float
    severity: LogSeverity
    category: str
    message: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def with_attribute(self, key: str, value: Any) -> "EventRecord":
        """Return a copy with an additional attribute."""
        new_attrs = dict(self.attributes)
        new_attrs[key] = value
        return EventRecord(
            timestamp=self.timestamp,
            severity=self.severity,
            category=self.category,
            message=self.message,
            attributes=new_attrs
        )


@dataclass(frozen=True)
class HealthState:
    """Health state enumeration."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class HealthReport:
    """
    Health status report for a component or the runtime.
    
    Args:
        overall_state: Combined health state
        components: Component-specific health reports
        timestamp: When report was generated
        issues: List of identified issues
    """
    
    overall_state: str  # HealthState value
    components: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: 0.0)
    issues: List[str] = field(default_factory=list)
    
    @classmethod
    def healthy(cls) -> "HealthReport":
        """Create a healthy report."""
        return cls(overall_state=HealthState.HEALTHY, timestamp=0.0)
    
    @classmethod
    def unhealthy(cls, issues: Optional[List[str]] = None) -> "HealthReport":
        """Create an unhealthy report."""
        return cls(
            overall_state=HealthState.UNHEALTHY,
            issues=issues or []
        )
    
    @property
    def is_healthy(self) -> bool:
        return self.overall_state == HealthState.HEALTHY


class MetricsSink:
    """
    Contract for metrics collection.
    
    Implementations should provide efficient, non-blocking metric recording.
    """
    
    async def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a counter increment."""
        pass
    
    async def record_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a gauge value."""
        pass
    
    async def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a histogram observation."""
        pass


class TraceSink:
    """
    Contract for distributed tracing.
    """
    
    async def start_span(
        self,
        name: str,
        parent_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> "TraceSpan":
        """Start a new trace span."""
        return TraceSpan(name=name)
    
    async def end_span(self, span_id: str) -> None:
        """End a trace span."""
        pass


class TraceSpan:
    """A single trace span."""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.id = id(self)
    
    async def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        pass
    
    async def record_event(self, event_name: str) -> None:
        """Record an event in the span."""
        pass
    
    async def end(self) -> None:
        """End the span."""
        pass


class LoggerAdapter:
    """
    Contract for logger adapter.
    
    Adapts various logging implementations to a common interface.
    """
    
    async def log(
        self,
        severity: LogSeverity,
        message: str,
        category: Optional[str] = None,
        **attributes
    ) -> None:
        """Log a message."""
        pass
    
    async def trace(self, message: str, **attributes) -> None:
        await self.log(LogSeverity.TRACE, message, **attributes)
    
    async def debug(self, message: str, **attributes) -> None:
        await self.log(LogSeverity.DEBUG, message, **attributes)
    
    async def info(self, message: str, **attributes) -> None:
        await self.log(LogSeverity.INFO, message, **attributes)
    
    async def warning(self, message: str, **attributes) -> None:
        await self.log(LogSeverity.WARNING, message, **attributes)
    
    async def error(self, message: str, **attributes) -> None:
        await self.log(LogSeverity.ERROR, message, **attributes)
    
    async def critical(self, message: str, **attributes) -> None:
        await self.log(LogSeverity.CRITICAL, message, **attributes)


class StandardLibraryLoggerAdapter(LoggerAdapter):
    """
    Adapter that uses Python's standard library logging.
    
    Does NOT configure the global root logger automatically.
    """
    
    def __init__(self, logger_name: Optional[str] = None) -> None:
        import logging
        self._logger = logging.getLogger(logger_name or "core.observability")
    
    async def log(
        self,
        severity: LogSeverity,
        message: str,
        category: Optional[str] = None,
        **attributes
    ) -> None:
        """Log a message to standard library logger."""
        import time
        
        # Convert severity
        if severity == LogSeverity.TRACE:
            level_func = self._logger.debug
        elif severity == LogSeverity.DEBUG:
            level_func = self._logger.debug
        elif severity == LogSeverity.INFO:
            level_func = self._logger.info
        elif severity == LogSeverity.WARNING:
            level_func = self._logger.warning
        elif severity == LogSeverity.ERROR:
            level_func = self._logger.error
        else:  # CRITICAL
            level_func = self._logger.critical
        
        # Format message with category and attributes
        full_message = message
        if category:
            full_message = f"[{category}] {message}"
        
        # Log with attributes as extra (if supported)
        try:
            level_func(full_message, extra={"attributes": attributes})
        except Exception:
            # Fallback if logger doesn't support extra params well
            self._logger.info("%s | attrs=%s", full_message, attributes)


__all__ = [
    "LogSeverity",
    "EventRecord",
    "HealthState",
    "HealthReport",
    "MetricsSink",
    "TraceSink",
    "TraceSpan",
    "LoggerAdapter",
    "StandardLibraryLoggerAdapter",
]
