# Persistence Events
# ==================

"""
Events emitted by persistence operations for monitoring and debugging.

This module provides:
- State capture events
- Snapshot, journal, checkpoint lifecycle events
- Restore and rehydration events
- Error detection events (drift, corruption)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import time


# =============================================================================
# State Capture Events
# =============================================================================

@dataclass(frozen=True)
class StateCaptureStarted:
    """State capture operation has started."""
    
    event_id: str
    runtime_id: str
    request_id: str
    domains: List[str]
    mode: str
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        request_id: str,
        domains: List[str],
        mode: str = "versioned",
    ) -> "StateCaptureStarted":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=request_id,
            artifact_id=None,
            state_domain=None,
            logical_sequence=0,
            request_id=request_id,
            domains=domains,
            mode=mode,
        )


@dataclass(frozen=True)
class StateCaptureCompleted:
    """State capture operation has completed."""
    
    event_id: str
    runtime_id: str
    request_id: str
    domains_captured: int
    domains_failed: int
    total_state_size_bytes: int
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        request_id: str,
        domains_captured: int,
        domains_failed: int,
        state_size_bytes: int,
    ) -> "StateCaptureCompleted":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=request_id,
            artifact_id=None,
            state_domain=None,
            logical_sequence=0,
            request_id=request_id,
            domains_captured=domains_captured,
            domains_failed=domains_failed,
            total_state_size_bytes=state_size_bytes,
        )


@dataclass(frozen=True)
class SnapshotCreated:
    """A snapshot has been created."""
    
    event_id: str
    runtime_id: str
    snapshot_id: str
    snapshot_type: str
    domain_count: int
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        snapshot_id: str,
        snapshot_type: str,
        domain_count: int,
    ) -> "SnapshotCreated":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=snapshot_id,
            artifact_id=snapshot_id,
            state_domain=None,
            logical_sequence=0,
            snapshot_id=snapshot_id,
            snapshot_type=snapshot_type,
            domain_count=domain_count,
        )


# =============================================================================
# Journal Events
# =============================================================================

@dataclass(frozen=True)
class JournalRecordAppended:
    """A record has been appended to a journal."""
    
    event_id: str
    runtime_id: str
    journal_id: str
    sequence_number: int
    record_kind: str
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        journal_id: str,
        sequence_number: int,
        record_kind: str = "event",
    ) -> "JournalRecordAppended":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=journal_id,
            artifact_id=f"{journal_id}:{sequence_number}",
            state_domain=None,
            logical_sequence=sequence_number,
            journal_id=journal_id,
            sequence_number=sequence_number,
            record_kind=record_kind,
        )


@dataclass(frozen=True)
class JournalSegmentRotated:
    """A journal segment has been rotated."""
    
    event_id: str
    runtime_id: str
    old_segment_id: str
    new_segment_id: str
    record_count_in_old_segment: int
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        old_segment_id: str,
        new_segment_id: str,
        record_count: int,
    ) -> "JournalSegmentRotated":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=new_segment_id,
            artifact_id=new_segment_id,
            state_domain=None,
            logical_sequence=0,
            old_segment_id=old_segment_id,
            new_segment_id=new_segment_id,
            record_count_in_old_segment=record_count,
        )


# =============================================================================
# Checkpoint Events
# =============================================================================

@dataclass(frozen=True)
class CheckpointRequested:
    """A checkpoint has been requested."""
    
    event_id: str
    runtime_id: str
    checkpoint_type: str
    domains: List[str]
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        checkpoint_type: str,
        domains: List[str],
    ) -> "CheckpointRequested":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=None,
            artifact_id=None,
            state_domain=None,
            logical_sequence=0,
            checkpoint_type=checkpoint_type,
            domains=domains,
        )


@dataclass(frozen=True)
class CheckpointCommitted:
    """A checkpoint has been successfully committed."""
    
    event_id: str
    runtime_id: str
    checkpoint_id: str
    participant_count: int
    total_size_bytes: int
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        checkpoint_id: str,
        participant_count: int,
        size_bytes: int,
    ) -> "CheckpointCommitted":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=checkpoint_id,
            artifact_id=checkpoint_id,
            state_domain=None,
            logical_sequence=0,
            checkpoint_id=checkpoint_id,
            participant_count=participant_count,
            total_size_bytes=size_bytes,
        )


# =============================================================================
# Restore Events
# =============================================================================

@dataclass(frozen=True)
class RestoreRequested:
    """A restore operation has been requested."""
    
    event_id: str
    runtime_id: str
    restore_type: str
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    source_artifact_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        restore_type: str,
        source_artifact_id: Optional[str] = None,
    ) -> "RestoreRequested":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=None,
            artifact_id=source_artifact_id,
            state_domain=None,
            logical_sequence=0,
            restore_type=restore_type,
            source_artifact_id=source_artifact_id,
        )


@dataclass(frozen=True)
class RestoreCompleted:
    """A restore operation has completed."""
    
    event_id: str
    runtime_id: str
    domains_restored: int
    resources_reacquired: int
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        domains_restored: int,
        resources_reacquired: int,
    ) -> "RestoreCompleted":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=None,
            artifact_id=None,
            state_domain=None,
            logical_sequence=0,
            domains_restored=domains_restored,
            resources_reacquired=resources_reacquired,
        )


# =============================================================================
# Drift and Corruption Detection Events
# =============================================================================

class PersistenceDriftKind(Enum):
    """Type of drift detected."""
    
    STATE_MISMATCH = "state_mismatch"
    MANIFEST_DRIFT = "manifest_drift"
    BACKEND_INDEX_DRIFT = "backend_index_drift"
    CHECKPOINT_CHAIN_BROKEN = "checkpoint_chain_broken"


@dataclass(frozen=True)
class PersistenceDriftDetected:
    """Persistence drift has been detected."""
    
    event_id: str
    runtime_id: str
    drift_kind: str
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        drift_kind: PersistenceDriftKind,
        artifact_id: Optional[str] = None,
        expected: Optional[str] = None,
        actual: Optional[str] = None,
    ) -> "PersistenceDriftDetected":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=None,
            artifact_id=artifact_id,
            state_domain=None,
            logical_sequence=0,
            drift_kind=drift_kind.value,
            expected_value=expected,
            actual_value=actual,
        )


class PersistenceCorruptionKind(Enum):
    """Type of corruption detected."""
    
    PAYLOAD_CORRUPTION = "payload_corruption"
    METADATA_CORRUPTION = "metadata_corruption"
    CHECKSUM_MISMATCH = "checksum_mismatch"


@dataclass(frozen=True)
class PersistenceCorruptionDetected:
    """Persistence corruption has been detected."""
    
    event_id: str
    runtime_id: str
    corruption_kind: str
    artifact_id: str
    
    transaction_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    expected_digest: Optional[str] = None
    actual_digest: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        corruption_kind: PersistenceCorruptionKind,
        artifact_id: str,
        expected_digest: Optional[str] = None,
        actual_digest: Optional[str] = None,
    ) -> "PersistenceCorruptionDetected":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=None,
            state_domain=None,
            logical_sequence=0,
            corruption_kind=corruption_kind.value,
            artifact_id=artifact_id,
            expected_digest=expected_digest,
            actual_digest=actual_digest,
        )


# =============================================================================
# Retention Events
# =============================================================================

@dataclass(frozen=True)
class RetentionApplied:
    """Retention policy has been applied."""
    
    event_id: str
    runtime_id: str
    artifacts_retained: int
    artifacts_deleted: int
    
    transaction_id: Optional[str] = None
    artifact_id: Optional[str] = None
    state_domain: Optional[str] = None
    logical_sequence: int = 0
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        retained: int,
        deleted: int,
    ) -> "RetentionApplied":
        return cls(
            event_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            transaction_id=None,
            artifact_id=None,
            state_domain=None,
            logical_sequence=0,
            artifacts_retained=retained,
            artifacts_deleted=deleted,
        )


# =============================================================================
# Event Publisher
# =============================================================================

class PersistenceEventPublisher:
    """
    Publishes persistence events for monitoring and debugging.
    
    Usage:
        publisher = PersistenceEventPublisher()
        
        # Subscribe to events
        @publisher.subscribe(StateCaptureStarted)
        def handle_capture_started(event: StateCaptureStarted):
            logger.info(f"Capture started for {event.domains}")
        
        # Publish events
        event = StateCaptureStarted.create(runtime_id, request_id, domains)
        publisher.publish(event)
    """
    
    def __init__(self) -> None:
        self._subscribers: Dict[type, List[Any]] = {}
        self._event_count = 0
    
    def subscribe(
        self,
        event_type: type,
        handler: Any,
    ) -> None:
        """Subscribe to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: Any) -> None:
        """Publish an event to all subscribers."""
        event_type = type(event)
        
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    if hasattr(handler, '__call__'):
                        handler(event)
                except Exception:
                    # Don't let one handler failure affect others
                    pass
        
        self._event_count += 1
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get publisher diagnostics."""
        return {
            "subscribers_by_event_type": {
                str(k): len(v)
                for k, v in self._subscribers.items()
            },
            "total_events_published": self._event_count,
        }


__all__ = [
    # State capture events
    "StateCaptureStarted",
    "StateCaptureCompleted",
    "SnapshotCreated",
    
    # Journal events
    "JournalRecordAppended",
    "JournalSegmentRotated",
    
    # Checkpoint events
    "CheckpointRequested",
    "CheckpointCommitted",
    
    # Restore events
    "RestoreRequested",
    "RestoreCompleted",
    
    # Error detection events
    "PersistenceDriftKind",
    "PersistenceDriftDetected",
    "PersistenceCorruptionKind",
    "PersistenceCorruptionDetected",
    
    # Retention events
    "RetentionApplied",
    
    # Publisher
    "PersistenceEventPublisher",
]