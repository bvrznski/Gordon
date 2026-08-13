# Stream Tracing Layer - Phase 3.11.16
# ======================================

"""
Canonical Stream Tracing implementation.

Tracing is PASSIVE deterministic tracking of record flow:
- It NEVER modifies execution flow
- It NEVER duplicates records (deterministic trace)
- It ONLY tracks and preserves references to existing records

Supported traces:
- Perception Record → Consciousness Record → Reasoning Record
  ↓                          ↓                        ↓
- Memory Record → Action Record → Feedback Record

All traces maintain explicit references.
No record duplication occurs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# TRACE SPAN STATUS
# =============================================================================


class SpanStatus(Enum):
    """Status of a trace span."""
    IN_PROGRESS = "in_progress"     # Span is currently active
    COMPLETED = "completed"         # Span finished successfully
    ERROR = "error"                 # Span ended with error
    CANCELLED = "cancelled"         # Span was cancelled


# =============================================================================
# TRACE SPAN EVENT
# =============================================================================


@dataclass(frozen=True)
class SpanEvent:
    """
    Event within a trace span.
    
    Represents an annotation or timestamp within the span lifecycle.
    """
    
    event_id: str                   # Unique ID for this event
    timestamp_utc: float            # When event occurred
    event_type: str                 # e.g., "received", "processed", "delivered"
    description: Optional[str] = None  # Human-readable description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "event_id": self.event_id,
            "timestamp_utc": self.timestamp_utc,
            "event_type": self.event_type,
            "description": self.description,
        }


# =============================================================================
# TRACE SPAN
# =============================================================================


@dataclass(frozen=True)
class TraceSpan:
    """
    Immutable trace span representing a single operation.
    
    A span represents one unit of work within the trace (e.g., publication,
    subscription, routing). Spans form a tree structure via parent references.
    
    CRITICAL: Span NEVER modifies the stream or records it traces.
    """
    
    # Identity
    span_id: str                    # Unique ID for this span
    trace_id: str                   # ID of entire trace (all spans)
    
    # Parent reference (None = root span)
    parent_span_id: Optional[str]   # Parent span ID
    
    # Operation info
    operation_name: str             # e.g., "publish", "subscribe", "route"
    span_status: SpanStatus         # Current status
    
    # Timestamps
    start_time_utc: float           # When span started
    end_time_utc: Optional[float]   # When span ended (None if still active)
    
    # Record references (NOT copies - just references!)
    record_references: Tuple[str, ...] = field(default_factory=tuple)  # Record IDs traced
    
    # Events within this span
    events: Tuple[SpanEvent, ...] = field(default_factory=tuple)
    
    def end(self, status: SpanStatus = SpanStatus.COMPLETED) -> "TraceSpan":
        """Create a new span marked as ended."""
        return dataclass_replace(
            self,
            span_status=status,
            end_time_utc=time.time(),
        )

    def add_event(
        self,
        event_type: str,
        description: Optional[str] = None,
    ) -> "TraceSpan":
        """Create a new span with an additional event."""
        event = SpanEvent(
            event_id=f"evt-{time.monotonic_ns()}-{hash(event_type) % 1000:04d}",
            timestamp_utc=time.time(),
            event_type=event_type,
            description=description,
        )
        return dataclass_replace(self, events=self.events + (event,))

    def add_record_reference(self, record_id: str) -> "TraceSpan":
        """Create a new span with an additional record reference."""
        return dataclass_replace(
            self,
            record_references=self.record_references + (record_id,)
        )


# =============================================================================
# TRACE CONTEXT
# =============================================================================


@dataclass(frozen=True)
class TraceContext:
    """
    Immutable context for tracing.
    
    Contains trace IDs and parent references for correlating spans across
    stream boundaries.
    """
    
    # Identity
    trace_id: str                   # ID of entire trace
    span_id: str                    # Current span ID
    
    # Parent reference (for nested traces)
    parent_span_id: Optional[str] = None
    
    # Trace metadata
    is_sampled: bool = True         # Is this trace being sampled?
    trace_flags: Dict[str, Any] = field(default_factory=dict)
    
    def to_headers(self) -> Dict[str, str]:
        """Convert context to header-like key-value pairs."""
        return {
            "trace-id": self.trace_id,
            "span-id": self.span_id,
            **({"parent-span-id": self.parent_span_id} if self.parent_span_id else {}),
        }

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> "TraceContext":
        """Create context from header-like key-value pairs."""
        return cls(
            trace_id=headers.get("trace-id", ""),
            span_id=headers.get("span-id", ""),
            parent_span_id=headers.get("parent-span-id"),
        )


# =============================================================================
# TRACED RECORD
# =============================================================================


@dataclass(frozen=True)
class TracedRecord:
    """
    Record with tracing information attached.
    
    Contains a reference to the original record plus trace context.
    NEVER copies or modifies the original record data.
    """
    
    # Original record reference (NOT a copy!)
    record_id: str                  # ID of traced record
    
    # Trace context
    trace_context: TraceContext     # Tracing context for this record
    
    # Record metadata
    record_type: str                # e.g., "perception", "consciousness"
    timestamp_utc: float            # When record was created
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "record_id": self.record_id,
            "trace_context": self.trace_context.to_headers(),
            "record_type": self.record_type,
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# RECORD FLOW TRACE
# =============================================================================


@dataclass(frozen=True)
class RecordFlowTrace:
    """
    Complete trace of a record's flow through the system.
    
    Represents the full journey: Perception → Consciousness → Reasoning
                                  ↓          ↓             ↓
                               Memory → Action → Feedback
    
    Contains references to all spans in the trace tree.
    """
    
    # Identity
    trace_id: str                   # Unique ID for this trace
    root_record_id: str             # Original record that started the trace
    
    # Timestamps
    start_time_utc: float           # When trace began
    end_time_utc: Optional[float]   # When trace ended (None if in progress)
    
    # Span tree
    span_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    # Record references at each stage
    record_references_by_stage: Dict[str, Tuple[str, ...]] = field(
        default_factory=dict  # e.g., {"perception": ("rec-1",), "action": ("rec-2",)}
    )
    
    def complete(self) -> "RecordFlowTrace":
        """Mark trace as completed."""
        return dataclass_replace(
            self,
            end_time_utc=time.time(),
        )

    def add_span_id(self, span_id: str) -> "RecordFlowTrace":
        """Add a span ID to the trace."""
        return dataclass_replace(
            self,
            span_ids=self.span_ids + (span_id,)
        )

    def add_record_at_stage(
        self,
        stage_name: str,
        record_id: str
    ) -> "RecordFlowTrace":
        """Add a record reference at a specific stage."""
        existing = self.record_references_by_stage.get(stage_name, ())
        new_refs = existing + (record_id,)
        return dataclass_replace(
            self,
            record_references_by_stage={
                **self.record_references_by_stage,
                stage_name: new_refs
            }
        )


# =============================================================================
# DETERMINISTIC TRACE MANAGER (PROTOCOL)
# =============================================================================


from typing import Protocol, runtime_checkable


@runtime_checkable
class DeterministicTraceManager(Protocol):
    """
    Protocol for deterministic trace management.
    
    CRITICAL PRINCIPLE: Trace manager is PASSIVE. It NEVER:
        - Modifies stream data or behavior
        - Triggers any side effects
        - Influences execution flow
        
    It only:
        - Tracks record references
        - Maintains span hierarchy
        - Preserves trace context
    """
    
    async def start_trace(
        self,
        root_record_id: str,
        record_type: str,
        parent_context: Optional[TraceContext] = None,
    ) -> TraceContext:
        """Start a new trace for a record."""
        ...
    
    async def end_trace(self, context: TraceContext) -> RecordFlowTrace:
        """End a trace and return the complete trace record."""
        ...
    
    async def add_span(
        self,
        context: TraceContext,
        operation_name: str,
        record_reference: Optional[str] = None,
    ) -> str:
        """
        Add a span to the current trace.
        
        Returns span ID for reference.
        """
        ...
    
    async def get_trace(self, trace_id: str) -> Optional[RecordFlowTrace]:
        """Get a complete trace by ID."""
        ...


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_span(
    operation_name: str,
    start_time_utc: Optional[float] = None,
) -> TraceSpan:
    """
    Create a new trace span.
    
    Args:
        operation_name: Name of the operation being traced
        start_time_utc: When operation started (now if not specified)
        
    Returns:
        Immutable TraceSpan instance
    """
    return TraceSpan(
        span_id=f"span-{time.monotonic_ns()}-{hash(operation_name) % 1000:04d}",
        trace_id=f"trace-{time.monotonic_ns()}",
        parent_span_id=None,
        operation_name=operation_name,
        span_status=SpanStatus.IN_PROGRESS,
        start_time_utc=start_time_utc or time.time(),
        end_time_utc=None,
    )


def create_trace_context() -> TraceContext:
    """Create a new trace context."""
    return TraceContext(
        trace_id=f"trace-{time.monotonic_ns()}",
        span_id=f"span-{time.monotonic_ns()}-root",
    )


def create_traced_record(
    record_id: str,
    record_type: str,
    trace_context: Optional[TraceContext] = None,
) -> TracedRecord:
    """
    Create a traced record reference.
    
    Args:
        record_id: ID of the original record
        record_type: Type of record (perception, consciousness, etc.)
        trace_context: Trace context for this record
        
    Returns:
        Immutable TracedRecord instance
    """
    return TracedRecord(
        record_id=record_id,
        trace_context=trace_context or create_trace_context(),
        record_type=record_type,
        timestamp_utc=time.time(),
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
    # Status and events
    "SpanStatus",
    "SpanEvent",
    
    # Span and context
    "TraceSpan",
    "TraceContext",
    "TracedRecord",
    
    # Complete traces
    "RecordFlowTrace",
    
    # Manager protocol
    "DeterministicTraceManager",
    
    # Factory functions
    "create_span",
    "create_trace_context",
    "create_traced_record",
    "dataclass_replace",
]