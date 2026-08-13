# Stream Telemetry Layer - Phase 3.11.16
# ========================================

"""
Canonical Stream Telemetry implementation.

Telemetry is PASSIVE event collection and export:
- It NEVER influences execution flow
- It NEVER triggers actions or reactions
- It ONLY collects, aggregates, and exports events

Event types:
- publication: Record published to stream
- subscription: Record consumed by subscriber  
- replay: Historical record replayed
- checkpoint: Checkpoint created or restored
- routing: Message routed between streams
- delivery: Record delivered to subscriber
- backpressure: Backpressure signal triggered
- integrity: Integrity check result
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time
import uuid

# =============================================================================
# TELEMETRY EVENT TYPES
# =============================================================================


class TelemetryEventType(Enum):
    """
    Canonical telemetry event types.
    
    Categories:
        - STREAM_EVENTS: Stream lifecycle events
        - PUBLISH_EVENTS: Publication-related events  
        - SUBSCRIBE_EVENTS: Subscription-related events
        - REPLAY_EVENTS: Replay-related events
        - ROUTING_EVENTS: Routing decisions
        - INTEGRITY_EVENTS: Integrity verification
        - RESOURCE_EVENTS: Resource utilization changes
    """
    # Stream lifecycle events
    STREAM_CREATED = "stream_created"
    STREAM_ACTIVATED = "stream_activated"
    STREAM_PAUSED = "stream_paused"
    STREAM_RESUMED = "stream_resumed"
    STREAM_CLOSED = "stream_closed"
    STREAM_FAILED = "stream_failed"
    
    # Publication events
    PUBLICATION_ATTEMPTED = "publication_attempted"
    PUBLICATION_SUCCEEDED = "publication_succeeded"
    PUBLICATION_REJECTED = "publication_rejected"
    
    # Subscription events  
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_SUBSCRIBED = "subscription_subscribed"
    SUBSCRIPTION_ACKNOWLEDGED = "subscription_acknowledged"
    SUBSCRIPTION_COMPLETED = "subscription_completed"
    
    # Replay events
    REPLAY_REQUESTED = "replay_requested"
    REPLAY_STARTED = "replay_started"
    REPLAY_COMPLETED = "replay_completed"
    REPLAY_FAILED = "replay_failed"
    
    # Routing events
    ROUTING_DECIDED = "routing_decided"
    ROUTING_PERFORMED = "routing_performed"
    ROUTING_DELAYED = "routing_delayed"
    
    # Delivery events
    RECORD_DELIVERED = "record_delivered"
    DELIVERY_FAILED = "delivery_failed"
    
    # Backpressure events
    BACKPRESSURE_TRIGGERED = "backpressure_triggered"
    BACKPRESSURE_RELEASED = "backpressure_released"
    
    # Integrity events
    INTEGRITY_VERIFIED = "integrity_verified"
    INTEGRITY_FAILURE = "integrity_failure"
    
    # Checkpoint events
    CHECKPOINT_CREATED = "checkpoint_created"
    CHECKPOINT_RESTORED = "checkpoint_restored"
    
    # Resource events
    RESOURCE_UTILIZATION_CHANGED = "resource_utilization_changed"


class TelemetryLevel(Enum):
    """Severity/level of telemetry event."""
    DEBUG = "debug"           # Detailed diagnostic information
    INFO = "info"             # General informational messages
    NOTICE = "notice"         # Normal but significant message
    WARNING = "warning"       # Warning about potential issue
    ERROR = "error"           # Error condition detected
    CRITICAL = "critical"     # Critical failure requiring attention


@dataclass(frozen=True)
class TelemetryRecord:
    """
    Immutable telemetry record.
    
    A single telemetry observation. Records are immutable and never
    influence the system they observe.
    """
    
    # Identity
    event_id: str                   # Unique ID for this event
    sequence_number: int            # Order in stream
    
    # Event metadata
    timestamp_utc: float            # When event occurred
    event_type: TelemetryEventType  # What happened?
    level: TelemetryLevel           # Severity level
    
    # Context
    stream_id: Optional[str] = None     # Which stream?
    component_id: Optional[str] = None  # Which component?
    
    # Payload data (bounded, serializable)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Correlation (for tracing across streams)
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    
    # Source information
    source_component: str = "unknown"  # Where did it originate?
    source_timestamp_utc: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "event_id": self.event_id,
            "sequence_number": self.sequence_number,
            "timestamp_utc": self.timestamp_utc,
            "event_type": self.event_type.value,
            "level": self.level.value,
            "stream_id": self.stream_id,
            "component_id": self.component_id,
            "payload": dict(self.payload),
            "correlation_id": self.correlation_id,
            "parent_event_id": self.parent_event_id,
            "source_component": self.source_component,
            "source_timestamp_utc": self.source_timestamp_utc,
        }

    @classmethod
    def create(
        cls,
        event_type: TelemetryEventType,
        level: TelemetryLevel = TelemetryLevel.INFO,
        stream_id: Optional[str] = None,
        component_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> "TelemetryRecord":
        """Create a new telemetry record."""
        return cls(
            event_id=f"te-{time.monotonic_ns()}-{uuid.uuid4().hex[:8] if 'uuid' in dir() else hash(time.time()) % 1000:04d}",
            sequence_number=0,  # Will be set by manager
            timestamp_utc=time.time(),
            event_type=event_type,
            level=level,
            stream_id=stream_id,
            component_id=component_id,
            payload=dict(payload or {}),
            correlation_id=correlation_id,
            source_component="telemetry",
        )


@dataclass(frozen=True)
class StreamTelemetryEvent:
    """
    Telemetry event for a specific stream.
    
    Contains all telemetry records related to a single stream's activity.
    """
    
    # Identity
    stream_id: str                  # Which stream?
    telemetry_session_id: str       # Session identifier
    
    # Records
    records: Tuple[TelemetryRecord, ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    first_record_at_utc: Optional[float] = None
    last_record_at_utc: Optional[float] = None
    
    # Statistics
    record_count: int = 0           # Number of records
    
    def __post_init__(self):
        """Post-initialization to set computed fields."""
        if self.records:
            object.__setattr__(self, 'record_count', len(self.records))
            timestamps = [r.timestamp_utc for r in self.records]
            object.__setattr__(self, 'first_record_at_utc', min(timestamps))
            object.__setattr__(self, 'last_record_at_utc', max(timestamps))


@dataclass(frozen=True)
class StreamTelemetryEnvelope:
    """
    Envelope containing telemetry records for export.
    
    Used to batch and transport telemetry data safely.
    Contains only bounded data - no live objects or references.
    """
    
    # Identity
    envelope_id: str                # Unique ID for this batch
    
    # Metadata
    created_at_utc: float           # When envelope was created
    source_system: str              # Source system identifier
    
    # Records
    records: Tuple[TelemetryRecord, ...] = field(default_factory=tuple)
    
    # Context
    stream_ids: Tuple[str, ...]     # All streams in this batch
    event_types: Tuple[str, ...]    # All event types present
    
    # Export metadata
    export_timestamp_utc: Optional[float] = None  # When exported
    export_destination: Optional[str] = None      # Where it's going
    
    def __post_init__(self):
        """Post-initialization to set computed fields."""
        if self.records:
            stream_ids = tuple(set(r.stream_id for r in self.records if r.stream_id))
            event_types = tuple(set(r.event_type.value for r in self.records))
            object.__setattr__(self, 'stream_ids', stream_ids)
            object.__setattr__(self, 'event_types', event_types)


# =============================================================================
# TELEMETRY EXPORT BATCH
# =============================================================================


@dataclass(frozen=True)
class TelemetryExportBatch:
    """
    Batch of telemetry records ready for export.
    
    Represents the final form of telemetry data before external export.
    All records are immutable and safe to share externally.
    """
    
    # Identity
    batch_id: str                   # Unique ID for this batch
    
    # Metadata
    created_at_utc: float           # When batch was assembled
    record_count: int = 0           # Number of records
    
    # Records (deep copy, immutable)
    records: Tuple[TelemetryRecord, ...] = field(default_factory=tuple)
    
    # Summary statistics
    event_type_counts: Dict[str, int] = field(default_factory=dict)
    stream_ids_seen: Tuple[str, ...] = field(default_factory=tuple)
    
    def __post_init__(self):
        """Post-initialization to compute summary statistics."""
        if self.records:
            object.__setattr__(self, 'record_count', len(self.records))
            
            # Count event types
            counts: Dict[str, int] = {}
            stream_ids_set: set = set()
            for record in self.records:
                et = record.event_type.value
                counts[et] = counts.get(et, 0) + 1
                if record.stream_id:
                    stream_ids_set.add(record.stream_id)
            
            object.__setattr__(self, 'event_type_counts', counts)
            object.__setattr__(self, 'stream_ids_seen', tuple(sorted(stream_ids_set)))

    def get_summary(self) -> str:
        """Get a human-readable summary of the batch."""
        events = ", ".join(f"{k}: {v}" for k, v in self.event_type_counts.items())
        return f"Batch {self.batch_id[:8]}: {self.record_count} records [{events}]"


# =============================================================================
# TELEMETRY EXPORTER (PROTOCOL)
# =============================================================================


from typing import Protocol, runtime_checkable


@runtime_checkable
class TelemetryExporter(Protocol):
    """
    Protocol for telemetry exporters.
    
    Exporters receive telemetry batches and send them to external systems
    (logs, metrics databases, tracing backends, etc.).
    
    CRITICAL: Export is PASSIVE. It never modifies the source data
    or influences execution behavior.
    """
    
    async def initialize(self) -> None:
        """Initialize the exporter."""
        ...
    
    async def shutdown(self) -> None:
        """Shutdown the exporter cleanly."""
        ...
    
    async def export(
        self,
        batch: TelemetryExportBatch
    ) -> bool:
        """
        Export a batch of telemetry records.
        
        This method is PASSIVE. It should NEVER:
            - Modify any source data
            - Trigger any side effects in the system
            - Influence execution flow
        
        Args:
            batch: The telemetry batch to export
            
        Returns:
            True if export succeeded, False otherwise
            
        Note: Export failure does not affect stream operation.
        """
        ...
    
    async def flush(self) -> int:
        """
        Flush any pending records.
        
        Returns:
            Number of records flushed
        """
        ...


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_telemetry_record(
    event_type: TelemetryEventType,
    level: TelemetryLevel = TelemetryLevel.INFO,
    stream_id: Optional[str] = None,
    component_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> TelemetryRecord:
    """
    Create a new telemetry record.
    
    This is the canonical factory for creating telemetry events.
    
    Args:
        event_type: What type of event occurred
        level: Severity level
        stream_id: Optional stream identifier
        component_id: Optional component identifier
        payload: Optional additional data
        
    Returns:
        Immutable TelemetryRecord instance
        
    Note: This function is PASSIVE - it only constructs the record.
    """
    return TelemetryRecord.create(
        event_type=event_type,
        level=level,
        stream_id=stream_id,
        component_id=component_id,
        payload=payload,
    )


def create_telemetry_envelope(
    stream_id: str,
    records: Tuple[TelemetryRecord, ...],
) -> StreamTelemetryEnvelope:
    """
    Create a telemetry envelope for a stream.
    
    Args:
        stream_id: Which stream these records belong to
        records: The telemetry records
        
    Returns:
        Immutable StreamTelemetryEnvelope instance
    """
    return StreamTelemetryEnvelope(
        envelope_id=f"env-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
        created_at_utc=time.time(),
        source_system="telemetry",
        records=records,
    )


def create_export_batch(
    records: Tuple[TelemetryRecord, ...],
) -> TelemetryExportBatch:
    """
    Create a telemetry export batch.
    
    Args:
        records: The telemetry records to batch
        
    Returns:
        Immutable TelemetryExportBatch instance
    """
    return TelemetryExportBatch(batch_id=f"batch-{time.monotonic_ns()}", records=records)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Event types
    "TelemetryEventType",
    "TelemetryLevel",
    
    # Records
    "TelemetryRecord",
    "StreamTelemetryEvent",
    "StreamTelemetryEnvelope",
    "TelemetryExportBatch",
    
    # Exporter protocol
    "TelemetryExporter",
    
    # Factory functions
    "create_telemetry_record",
    "create_telemetry_envelope",
    "create_export_batch",
]