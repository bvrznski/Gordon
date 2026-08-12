# Core Correlation and Tracing Model
# ===================================

"""
Correlation, causality, tracing, and span tracking for runtime events.

This module provides:
- Correlation IDs for grouping related operations
- Causation IDs for identifying event relationships
- Trace IDs for end-to-end operation tracking
- Span IDs for bounded work segments within traces
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
import uuid
import time


# =============================================================================
# Tracing Context
# =============================================================================

@dataclass(frozen=True)
class TraceContext:
    """
    Correlation and tracing context for events.
    
    Distinguishes between:
        correlation: groups related operations (e.g., all operations in a request)
        causation: identifies what caused another event
        trace: follows an end-to-end operation
        span: identifies one bounded segment of work
    
    Usage:
        ctx = TraceContext.generate()
        
        # Child operations inherit parent context but get new spans
        child_ctx = ctx.new_child_span()
    """
    
    # Correlation - groups related operations
    correlation_id: str  # e.g., request ID, session ID
    
    # Causation - identifies event relationships
    causation_id: Optional[str] = None  # What caused this event
    
    # Tracing - end-to-end operation tracking
    trace_id: Optional[str] = None      # Full operation trace
    span_id: Optional[str] = None       # Current work segment
    parent_span_id: Optional[str] = None  # Parent span for hierarchy
    
    # Context propagation
    runtime_id: str = ""                # Runtime instance identifier
    
    @classmethod
    def generate(cls, runtime_id: str = "") -> "TraceContext":
        """Generate a new root trace context."""
        return cls(
            correlation_id=str(uuid.uuid4()),
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4()),
            runtime_id=runtime_id
        )
    
    @classmethod
    def from_parent(cls, parent: "TraceContext", causation_id: Optional[str] = None) -> "TraceContext":
        """Create a child context inheriting parent's trace."""
        return cls(
            correlation_id=parent.correlation_id,
            causation_id=causation_id or parent.span_id,
            trace_id=parent.trace_id,
            span_id=str(uuid.uuid4()),
            parent_span_id=parent.span_id,
            runtime_id=parent.runtime_id
        )
    
    def new_child_span(self, causation_id: Optional[str] = None) -> "TraceContext":
        """Create a child context with a new span."""
        return self.from_parent(self, causation_id)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for propagation."""
        return {
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id or "",
            "trace_id": self.trace_id or "",
            "span_id": self.span_id or "",
            "parent_span_id": self.parent_span_id or "",
            "runtime_id": self.runtime_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "TraceContext":
        """Reconstruct context from dictionary."""
        return cls(
            correlation_id=data.get("correlation_id", ""),
            causation_id=data.get("causation_id"),
            trace_id=data.get("trace_id"),
            span_id=data.get("span_id"),
            parent_span_id=data.get("parent_span_id"),
            runtime_id=data.get("runtime_id", "")
        )


# =============================================================================
# Span Status
# =============================================================================

class SpanStatus(Enum):
    """Span execution status."""
    
    RUNNING = "running"       # Currently executing
    SUCCESS = "success"       # Completed successfully
    ERROR = "error"           # Completed with error
    CANCELLED = "cancelled"   # Was cancelled
    TIMEOUT = "timeout"       # Timed out


# =============================================================================
# Span Record
# =============================================================================

@dataclass(frozen=True)
class SpanRecord:
    """
    A single span record for tracing.
    
    Args:
        span_id: Unique span identifier
        trace_id: Trace this span belongs to
        name: Human-readable operation name
        status: Execution status
        start_time: Monotonic time when span started
        end_time: Monotonic time when span ended (or current if running)
        
    Attributes:
        duration_seconds: Total duration in seconds
    """
    
    span_id: str
    trace_id: str
    name: str
    
    status: SpanStatus = SpanStatus.RUNNING
    
    start_time: float = field(default_factory=time.monotonic)
    end_time: Optional[float] = None
    
    parent_span_id: Optional[str] = None
    child_span_ids: List[str] = field(default_factory=list)
    
    attributes: Dict[str, str] = field(default_factory=dict)
    events: List["SpanEvent"] = field(default_factory=list)
    
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate span duration."""
        end = self.end_time if self.end_time is not None else time.monotonic()
        return end - self.start_time
    
    def mark_completed(
        self,
        status: SpanStatus = SpanStatus.SUCCESS,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> "SpanRecord":
        """Return a copy with completed status."""
        return SpanRecord(
            span_id=self.span_id,
            trace_id=self.trace_id,
            name=self.name,
            status=status,
            start_time=self.start_time,
            end_time=time.monotonic(),
            parent_span_id=self.parent_span_id,
            child_span_ids=list(self.child_span_ids),
            attributes=dict(self.attributes),
            events=list(self.events),
            error_message=error_message,
            stack_trace=stack_trace
        )
    
    def add_attribute(self, key: str, value: str) -> "SpanRecord":
        """Return a copy with an added attribute."""
        new_attrs = dict(self.attributes)
        new_attrs[key] = value
        return SpanRecord(
            span_id=self.span_id,
            trace_id=self.trace_id,
            name=self.name,
            status=self.status,
            start_time=self.start_time,
            end_time=self.end_time,
            parent_span_id=self.parent_span_id,
            child_span_ids=list(self.child_span_ids),
            attributes=new_attrs,
            events=list(self.events),
            error_message=self.error_message,
            stack_trace=self.stack_trace
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "name": self.name,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "parent_span_id": self.parent_span_id,
            "child_span_ids": self.child_span_ids,
            "duration_seconds": self.duration_seconds,
            "attributes": self.attributes,
            "error_message": self.error_message
        }


# =============================================================================
# Span Event
# =============================================================================

@dataclass(frozen=True)
class SpanEvent:
    """
    An event within a span.
    
    Args:
        name: Event name (e.g., "operation_start", "checkpoint")
        timestamp: When the event occurred
        attributes: Event-specific data
    """
    
    name: str
    timestamp: float = field(default_factory=time.monotonic)
    attributes: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Tracer Contract
# =============================================================================

class Span:
    """
    Context manager for span lifecycle.
    
    Usage:
        tracer = Tracer()
        
        with tracer.start_span("my_operation") as span:
            # Do work
            span.add_event(SpanEvent(name="checkpoint1"))
            
            if error:
                span.mark_error("Something went wrong")
                raise
    
    Spans are automatically completed when exiting the context.
    """
    
    def __init__(self, record: SpanRecord):
        self._record = record
    
    @property
    def record(self) -> SpanRecord:
        """Get the current span record."""
        return self._record
    
    def add_event(self, event: SpanEvent) -> None:
        """Add an event to this span."""
        new_events = list(self._record.events)
        new_events.append(event)
        
        self._record = SpanRecord(
            span_id=self._record.span_id,
            trace_id=self._record.trace_id,
            name=self._record.name,
            status=self._record.status,
            start_time=self._record.start_time,
            end_time=time.monotonic(),
            parent_span_id=self._record.parent_span_id,
            child_span_ids=list(self._record.child_span_ids),
            attributes=dict(self._record.attributes),
            events=new_events,
            error_message=self._record.error_message,
            stack_trace=self._record.stack_trace
        )
    
    def add_attribute(self, key: str, value: str) -> None:
        """Add an attribute to this span."""
        self._record = self._record.add_attribute(key, value)
    
    def mark_error(self, message: str, stack_trace: Optional[str] = None) -> None:
        """Mark the span as having an error."""
        self._record = SpanRecord(
            span_id=self._record.span_id,
            trace_id=self._record.trace_id,
            name=self._record.name,
            status=SpanStatus.ERROR,
            start_time=self._record.start_time,
            end_time=time.monotonic(),
            parent_span_id=self._record.parent_span_id,
            child_span_ids=list(self._record.child_span_ids),
            attributes=dict(self._record.attributes),
            events=list(self._record.events),
            error_message=message,
            stack_trace=stack_trace
        )
    
    def finish(
        self,
        status: SpanStatus = SpanStatus.SUCCESS,
        error_message: Optional[str] = None
    ) -> None:
        """Finish the span with specified status."""
        self._record = self._record.mark_completed(status, error_message)
    
    def __enter__(self) -> "Span":
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            import traceback
            self.mark_error(str(exc_val), "".join(traceback.format_exception(exc_type, exc_val, exc_tb)))
        
        # Finish with current state
        if self._record.status == SpanStatus.RUNNING:
            self.finish()


class Tracer:
    """
    Context-aware span tracer.
    
    Usage:
        tracer = Tracer()
        
        async def my_function(ctx: TraceContext):
            with tracer.start_span("my_function", ctx) as span:
                # Do work
                pass
        
        async def caller():
            ctx = TraceContext.generate()
            await my_function(ctx)
    """
    
    def __init__(self):
        self._spans: Dict[str, SpanRecord] = {}
    
    def start_span(
        self,
        name: str,
        context: Optional[TraceContext] = None
    ) -> Span:
        """Start a new span."""
        ctx = context or TraceContext.generate()
        
        record = SpanRecord(
            span_id=ctx.span_id or str(uuid.uuid4()),
            trace_id=ctx.trace_id or str(uuid.uuid4()),
            name=name,
            parent_span_id=ctx.parent_span_id
        )
        
        self._spans[record.span_id] = record
        
        return Span(record)
    
    def get_span(self, span_id: str) -> Optional[SpanRecord]:
        """Get a span by ID."""
        return self._spans.get(span_id)
    
    def finish_span(
        self,
        span_id: str,
        status: SpanStatus = SpanStatus.SUCCESS
    ) -> Optional[SpanRecord]:
        """Finish a span and return its record."""
        if span_id in self._spans:
            record = self._spans.pop(span_id)
            return record.mark_completed(status)
        return None
    
    def get_trace_spans(self, trace_id: str) -> List[SpanRecord]:
        """Get all spans for a trace."""
        return [r for r in self._spans.values() if r.trace_id == trace_id]


__all__ = [
    "TraceContext",
    "SpanStatus",
    "SpanRecord",
    "SpanEvent",
    "Span",
    "Tracer",
]