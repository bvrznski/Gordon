# Stream Event Inspection Layer - Phase 3.11.16
# ==============================================

"""
Canonical Stream Event Inspection implementation.

Event Inspection is PASSIVE record-level visibility:
- It NEVER modifies records or execution flow
- It NEVER triggers actions or decisions
- It ONLY provides read-only inspection of events

Supported inspections:
- Record-level visibility for all stream operations
- Event sequence analysis
- Timing and ordering verification
- Record metadata extraction
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# RECORD INSPECTION CONTEXT
# =============================================================================


@dataclass(frozen=True)
class RecordInspectionContext:
    """
    Immutable context for record inspection.
    
    Contains the stream and position information needed to inspect a record.
    """
    
    # Identity
    inspection_id: str              # Unique ID for this inspection
    
    # Timestamps
    requested_at_utc: float         # When inspection was requested
    
    # Stream context
    stream_id: str                  # Which stream?
    component_id: Optional[str] = None  # Which component?
    
    # Position
    position_in_stream: int = 0     # Position within stream (sequence number)
    
    # Inspection scope
    include_payload: bool = False   # Include full record payload?
    include_metadata: bool = True   # Include metadata?
    include_correlation: bool = True  # Include correlation info?
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "inspection_id": self.inspection_id,
            "requested_at_utc": self.requested_at_utc,
            "stream_id": self.stream_id,
            "component_id": self.component_id,
            "position_in_stream": self.position_in_stream,
            "include_payload": self.include_payload,
            "include_metadata": self.include_metadata,
            "include_correlation": self.include_correlation,
        }


# =============================================================================
# INSPECTION RESULT
# =============================================================================


@dataclass(frozen=True)
class InspectionResult:
    """
    Immutable result of a record inspection.
    
    Contains the inspected information without modifying any source data.
    """
    
    # Identity
    inspection_id: str              # Reference to original inspection request
    
    # Timestamps
    completed_at_utc: float         # When inspection completed
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # Record identity
    record_id: Optional[str] = None     # ID of inspected record (if available)
    
    # Inspection results
    found: bool = False             # Was the record found?
    
    # Inspected data
    metadata: Dict[str, Any] = field(default_factory=dict)  # Record metadata
    payload: Optional[Dict[str, Any]] = None  # Full payload (if requested)
    correlation_info: Dict[str, str] = field(default_factory=dict)  # Correlation IDs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "inspection_id": self.inspection_id,
            "completed_at_utc": self.completed_at_utc,
            "stream_id": self.stream_id,
            "record_id": self.record_id,
            "found": self.found,
            "metadata": dict(self.metadata),
            "payload": self.payload,
            "correlation_info": dict(self.correlation_info),
        }


# =============================================================================
# RECORD INSPECTOR (PROTOCOL)
# =============================================================================


from typing import Protocol, runtime_checkable


@runtime_checkable
class RecordInspector(Protocol):
    """
    Protocol for record inspection.
    
    CRITICAL PRINCIPLE: Inspector is PASSIVE. It NEVER:
        - Modifies stream data or behavior
        - Triggers any side effects
        - Influences execution flow
        
    It only:
        - Reads and extracts information
        - Provides read-only views of records
        - Preserves original record state
    """
    
    async def initialize(self) -> None:
        """Initialize the inspector."""
        ...
    
    async def shutdown(self) -> None:
        """Shutdown the inspector cleanly."""
        ...
    
    async def inspect_record(
        self,
        context: RecordInspectionContext,
    ) -> InspectionResult:
        """
        Inspect a specific record.
        
        Args:
            context: Inspection context with stream and position info
            
        Returns:
            Immutable InspectionResult instance
            
        Note: This method is PASSIVE - it only reads the record.
        """
        ...
    
    async def inspect_stream_records(
        self,
        stream_id: str,
        start_position: int = 0,
        limit: int = 1000,
    ) -> Tuple[InspectionResult, ...]:
        """Inspect multiple records from a stream."""
        ...


# =============================================================================
# STREAM EVENT INSPECTOR (PROTOCOL)
# =============================================================================


@runtime_checkable
class StreamEventInspector(Protocol):
    """
    Protocol for inspecting stream events.
    
    Provides visibility into all events flowing through a stream.
    """
    
    async def initialize(self) -> None:
        """Initialize the inspector."""
        ...
    
    async def shutdown(self) -> None:
        """Shutdown the inspector cleanly."""
        ...
    
    async def get_event_sequence(
        self,
        stream_id: str,
        start_position: int = 0,
        limit: int = 1000,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Get sequence of events from a stream.
        
        Args:
            stream_id: Which stream to inspect
            start_position: Starting position (inclusive)
            limit: Maximum number of events to return
            
        Returns:
            Tuple of event records (read-only views)
            
        Note: This method is PASSIVE - it only reads events.
        """
        ...
    
    async def get_event_summary(
        self,
        stream_id: str,
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a stream's events.
        
        Returns:
            Dictionary with event count and timing info
        """
        ...


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_record_inspection_context(
    stream_id: str,
    position_in_stream: int = 0,
) -> RecordInspectionContext:
    """Create a new record inspection context."""
    return RecordInspectionContext(
        inspection_id=f"inspect-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
        requested_at_utc=time.time(),
        stream_id=stream_id,
        position_in_stream=position_in_stream,
    )


def create_inspection_result(
    inspection_id: str,
    stream_id: str,
    record_id: Optional[str] = None,
    found: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> InspectionResult:
    """Create a new inspection result."""
    return InspectionResult(
        inspection_id=inspection_id,
        completed_at_utc=time.time(),
        stream_id=stream_id,
        record_id=record_id,
        found=found,
        metadata=dict(metadata or {}),
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
    # Context and results
    "RecordInspectionContext",
    "InspectionResult",
    
    # Inspector protocols
    "RecordInspector",
    "StreamEventInspector",
    
    # Factory functions
    "create_record_inspection_context",
    "create_inspection_result",
    "dataclass_replace",
]