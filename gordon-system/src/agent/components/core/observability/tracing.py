# Core Tracing Manager
# ====================

"""
Tracing infrastructure for distributed trace management in Gordon.

This module provides:
- TraceManager: Canonical authority for distributed tracing
- Span hierarchy with parent-child relationships
- Distributed context propagation across subsystems
- Runtime-scoped trace state (one per runtime)

Tracing is OBSERVATIONAL - it never changes runtime behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, ContextManager, Generator
from enum import Enum, auto
import threading
import time
import uuid

from .models import TraceId, SpanId, LogContext


# =============================================================================
# SPAN IMPLEMENTATION
# =============================================================================

@dataclass(frozen=True)
class SpanRecord:
    """
    Immutable record of a single span.
    
    Args:
        span_id: Unique identifier for this span
        trace_id: Trace this span belongs to
        name: Human-readable operation name
        status: Span execution status
        start_time: When span started (monotonic time)
        end_time: When span ended, if completed
        parent_span_id: Parent span in hierarchy
        
    Attributes:
        duration_seconds: Total duration in seconds
        child_count: Number of child spans
    """
    
    span_id: str
    trace_id: str
    name: str
    
    status: "SpanStatus" = field(default="running")
    
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
        """Calculate span duration in seconds."""
        end = self.end_time if self.end_time is not None else time.monotonic()
        return end - self.start_time
    
    @property
    def child_count(self) -> int:
        """Return number of child spans."""
        return len(self.child_span_ids)
    
    def mark_completed(
        self,
        status: "SpanStatus" = "success",
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> "SpanRecord":
        """Return a copy with completed status."""
        from dataclasses import replace
        return replace(
            self,
            status=status,
            end_time=time.monotonic(),
            error_message=error_message,
            stack_trace=stack_trace
        )
    
    def add_child_span(self, child_span_id: str) -> "SpanRecord":
        """Return a copy with a new child span ID."""
        from dataclasses import replace
        return replace(
            self,
            child_span_ids=self.child_span_ids + [child_span_id]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "name": self.name,
            "status": self.status if isinstance(self.status, str) else self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "parent_span_id": self.parent_span_id,
            "child_span_ids": self.child_span_ids,
            "duration_seconds": self.duration_seconds,
            "attributes": self.attributes,
            "error_message": self.error_message
        }


class SpanStatus(Enum):
    """Span execution status."""
    
    RUNNING = "running"       # Currently executing
    SUCCESS = "success"       # Completed successfully
    ERROR = "error"           # Completed with error
    CANCELLED = "cancelled"   # Was cancelled
    TIMEOUT = "timeout"       # Timed out


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
# TRACE IMPLEMENTATION
# =============================================================================

@dataclass(frozen=True)
class TraceSnapshot:
    """
    Snapshot of a complete trace at a point in time.
    
    Contains all spans belonging to a single trace for debugging
    and analysis purposes.
    """
    
    trace_id: str
    timestamp_utc: float = field(default_factory=time.time)
    
    # All spans in this trace (root span first, then children)
    spans: List[SpanRecord] = field(default_factory=list)
    
    @property
    def root_span(self) -> Optional[SpanRecord]:
        """Get the root span (no parent)."""
        for span in self.spans:
            if span.parent_span_id is None:
                return span
        return None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate total trace duration."""
        if not self.spans:
            return 0.0
        
        min_start = min(s.start_time for s in self.spans)
        max_end = max(
            (s.end_time or time.monotonic()) for s in self.spans
        )
        return max_end - min_start
    
    @property
    def span_count(self) -> int:
        """Return number of spans in trace."""
        return len(self.spans)
    
    @property
    def success_count(self) -> int:
        """Return count of successful spans."""
        return sum(1 for s in self.spans if s.status == SpanStatus.SUCCESS)
    
    @property
    def error_count(self) -> int:
        """Return count of errored spans."""
        return sum(1 for s in self.spans if s.status == SpanStatus.ERROR)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "timestamp_utc": self.timestamp_utc,
            "span_count": self.span_count,
            "duration_seconds": self.duration_seconds,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "spans": [s.to_dict() for s in self.spans]
        }


# =============================================================================
# TRACE CONTEXT MANAGER
# =============================================================================

class SpanContextManager:
    """
    Context manager for span lifecycle.
    
    Usage:
        with tracer.start_span("my_operation") as span:
            # Do work
            pass
        
        # Span is automatically finished
    """
    
    def __init__(
        self,
        trace_manager: "TraceManager",
        name: str,
        parent_span_id: Optional[str] = None
    ):
        self._trace_manager = trace_manager
        self._name = name
        self._parent_span_id = parent_span_id
        self._span_record: Optional[SpanRecord] = None
    
    def __enter__(self) -> "SpanContextManager":
        """Start the span."""
        span_id = str(SpanId.generate())
        trace_id = str(TraceId.generate())  # New trace for root spans
        
        self._span_record = SpanRecord(
            span_id=span_id,
            trace_id=trace_id,
            name=self._name,
            parent_span_id=self._parent_span_id
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finish the span."""
        if self._span_record is not None:
            error_msg = None
            stack_trace = None
            
            if exc_type is not None:
                import traceback
                error_msg = str(exc_val)
                stack_trace = "".join(
                    traceback.format_exception(exc_type, exc_val, exc_tb)
                )
            
            finished_record = self._span_record.mark_completed(
                status=SpanStatus.ERROR if exc_type else SpanStatus.SUCCESS,
                error_message=error_msg,
                stack_trace=stack_trace
            )
            
            # Store the span record
            self._trace_manager._store_span(finished_record)


# =============================================================================
# TRACE MANAGER
# =============================================================================

class TraceManager:
    """
    Canonical authority for distributed tracing.
    
    Provides:
        - Span creation with parent-child relationships
        - Trace context propagation across subsystems
        - Distributed trace state management
        - Span hierarchy tracking
    
    INVAR: Exactly one TraceManager exists per runtime.
    INVAR: Tracing is observational - never changes runtime behavior.
    
    Usage:
        # Create manager (runtime-scoped)
        manager = TraceManager(runtime_id="runtime_123")
        
        # Start a root span
        with manager.start_span("root_operation") as root:
            # Start nested child span
            with manager.start_span("child_operation", parent_span_id=root.span_id):
                # Do work in child context
                pass
        
        # Get trace snapshot for analysis
        snapshot = manager.get_trace_snapshot(trace_id)
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
        max_spans_per_trace: int = 1000,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        self._max_spans_per_trace = max(max_spans_per_trace, 100)
        
        # Thread-safe state
        self._lock = threading.RLock()
        
        # Active spans by span_id
        self._active_spans: Dict[str, SpanRecord] = {}
        
        # Completed spans storage (bounded per trace)
        self._trace_spans: Dict[str, List[SpanRecord]] = {}
        
        # Statistics
        self._total_spans_created = 0
        self._total_traces_completed = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    def _store_span(self, record: SpanRecord) -> None:
        """Store a span record in active or completed storage."""
        with self._lock:
            # Remove from active if present
            if record.span_id in self._active_spans:
                del self._active_spans[record.span_id]
            
            # Add to trace spans (bounded)
            trace_id = record.trace_id
            if trace_id not in self._trace_spans:
                self._trace_spans[trace_id] = []
            
            # Enforce limit - remove oldest if needed
            while len(self._trace_spans[trace_id]) >= self._max_spans_per_trace:
                self._trace_spans[trace_id].pop(0)
            
            self._trace_spans[trace_id].append(record)
            self._total_spans_created += 1
    
    # ------------------------------------------------------------------
    # Span Creation
    # ------------------------------------------------------------------
    
    def start_span(
        self,
        name: str,
        parent_span_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> SpanContextManager:
        """
        Start a new span.
        
        Args:
            name: Human-readable operation name
            parent_span_id: Parent span ID for nesting (optional)
            trace_id: Trace ID for distributed tracing (optional, generates if not provided)
            
        Returns:
            Context manager that finishes span on exit
        """
        return SpanContextManager(
            self,
            name=name,
            parent_span_id=parent_span_id
        )
    
    def start_active_span(
        self,
        name: str,
        parent_span_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> SpanRecord:
        """
        Start a span and return it for manual control.
        
        Args:
            name: Human-readable operation name
            parent_span_id: Parent span ID (optional)
            trace_id: Trace ID (optional, generates if not provided)
            
        Returns:
            The started SpanRecord (call mark_completed when done)
        """
        from dataclasses import replace
        
        if trace_id is None:
            trace_id = str(TraceId.generate())
        
        span_id = str(SpanId.generate())
        
        record = SpanRecord(
            span_id=span_id,
            trace_id=trace_id,
            name=name,
            parent_span_id=parent_span_id
        )
        
        with self._lock:
            self._active_spans[record.span_id] = record
        
        return record
    
    def finish_span(
        self,
        span_record: SpanRecord,
        status: SpanStatus = SpanStatus.SUCCESS,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """
        Manually finish a span started with start_active_span.
        
        Args:
            span_record: The span to finish
            status: Completion status
            error_message: Error message if failed
            stack_trace: Stack trace if failed
        """
        finished = span_record.mark_completed(
            status=status,
            error_message=error_message,
            stack_trace=stack_trace
        )
        
        # Update any active parent spans with child reference
        if finished.parent_span_id is not None:
            with self._lock:
                if finished.parent_span_id in self._active_spans:
                    parent = self._active_spans[finished.parent_span_id]
                    updated_parent = parent.add_child_span(finished.span_id)
                    self._active_spans[finished.parent_span_id] = updated_parent
        
        self._store_span(finished)
    
    def add_span_event(
        self,
        span_record: SpanRecord,
        event_name: str,
        **attributes
    ) -> None:
        """
        Add an event to a span.
        
        Args:
            span_record: The span to add the event to
            event_name: Name of the event
            **attributes: Event-specific data
        """
        from dataclasses import replace
        
        new_event = SpanEvent(
            name=event_name,
            timestamp=time.monotonic(),
            attributes=attributes
        )
        
        new_record = replace(
            span_record,
            events=span_record.events + [new_event]
        )
        
        with self._lock:
            if span_record.span_id in self._active_spans:
                self._active_spans[span_record.span_id] = new_record
    
    def add_span_attribute(
        self,
        span_record: SpanRecord,
        key: str,
        value: str
    ) -> None:
        """
        Add an attribute to a span.
        
        Args:
            span_record: The span to modify
            key: Attribute key
            value: Attribute value
        """
        from dataclasses import replace
        
        new_attrs = dict(span_record.attributes)
        new_attrs[key] = value
        
        new_record = replace(
            span_record,
            attributes=new_attrs
        )
        
        with self._lock:
            if span_record.span_id in self._active_spans:
                self._active_spans[span_record.span_id] = new_record
    
    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------
    
    def get_trace_snapshot(self, trace_id: str) -> Optional[TraceSnapshot]:
        """
        Get a snapshot of all spans for a trace.
        
        Args:
            trace_id: The trace to retrieve
            
        Returns:
            TraceSnapshot with all spans in the trace, or None if not found
        """
        with self._lock:
            if trace_id not in self._trace_spans:
                return None
            
            # Sort spans by start time (root first, then children)
            spans = sorted(
                self._trace_spans[trace_id],
                key=lambda s: s.start_time
            )
            
            return TraceSnapshot(
                trace_id=trace_id,
                timestamp_utc=time.time(),
                spans=spans
            )
    
    def get_span(self, span_id: str) -> Optional[SpanRecord]:
        """Get a span by its ID."""
        with self._lock:
            # Check active first
            if span_id in self._active_spans:
                return self._active_spans[span_id]
            
            # Check completed spans
            for trace_id, spans in self._trace_spans.items():
                for span in spans:
                    if span.span_id == span_id:
                        return span
            
            return None
    
    def get_active_trace_ids(self) -> List[str]:
        """Get all active trace IDs."""
        with self._lock:
            return list(self._trace_spans.keys())
    
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    
    @property
    def total_spans_created(self) -> int:
        """Return total spans created."""
        return self._total_spans_created
    
    @property
    def active_span_count(self) -> int:
        """Return count of active spans."""
        with self._lock:
            return len(self._active_spans)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tracing statistics."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "total_spans_created": self._total_spans_created,
                "total_traces_completed": self._total_traces_completed,
                "active_span_count": len(self._active_spans),
                "trace_count": len(self._trace_spans),
            }
    
    def close(self) -> None:
        """Close the manager and release resources."""
        with self._lock:
            self._active_spans.clear()
            # Note: We keep completed traces for inspection


__all__ = [
    "SpanRecord",
    "SpanStatus",
    "SpanEvent",
    "TraceSnapshot",
    "SpanContextManager",
    "TraceManager",
]