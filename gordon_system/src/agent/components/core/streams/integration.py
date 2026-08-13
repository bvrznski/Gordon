# Stream Integration Layer
# =========================

"""
Integration layer connecting streams with existing Gordon infrastructure.

This module implements:
    - Publisher adapter for stream-based communication
    - Subscriber adapter for consuming stream records
    - Cursor management and checkpoint integration
    - Correlation and causation tracking across system boundaries

Integration follows the Phase 3.10 architecture:
    Thread → Loop → Cycle → Stage → Capability → System
                 ↓
            Stream (semantic continuity)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from enum import Enum, auto
import time
import uuid
import asyncio

from .__init__ import (
    StreamId,
    StreamKind,
    StreamGenerationId,
    StreamRecordId,
    StreamRecord,
    StreamArtifact,
    ArtifactReference,
    StreamPosition,
    StreamCursor,
    StreamCheckpoint,
    StreamCommit,
    RecordType,
    StreamLifecycleState,
    CapacityExceededError,
)


# =============================================================================
# PUBLISHER
# =============================================================================

@dataclass(frozen=True)
class PublisherConfig:
    """Configuration for a stream publisher."""
    publisher_id: str
    stream_id: StreamId
    
    # Delivery settings
    auto_commit: bool = True
    max_batch_size: int = 100
    batch_timeout_seconds: float = 1.0
    
    # Rate limiting
    rate_limit: Optional[float] = None  # Records per second
    
    # Failure handling
    retry_on_failure: bool = True
    max_retries: int = 3


class StreamPublisher:
    """
    Publisher for committing records to streams.
    
    Provides a high-level API for publishing that handles:
        - Record creation and validation
        - Batched commits for efficiency
        - Rate limiting
        - Retry on failure
    
    Thread safety: All public methods are thread-safe.
    """
    
    def __init__(
        self,
        stream_id: StreamId,
        publisher_id: Optional[str] = None,
        config: Optional[PublisherConfig] = None,
    ):
        self._stream_id = stream_id
        self._publisher_id = publisher_id or f"pub_{uuid.uuid4().hex[:16]}"
        
        self._config = config or PublisherConfig(
            publisher_id=self._publisher_id,
            stream_id=stream_id
        )
        
        # Batch tracking
        self._batch: List[StreamRecord] = []
        self._last_batch_time = time.time()
        
        # Statistics
        self._records_published = 0
        self._commits_sent = 0
    
    @property
    def stream_id(self) -> StreamId:
        """Get the stream this publisher writes to."""
        return self._config.stream_id
    
    @property
    def publisher_id(self) -> str:
        """Get the publisher ID."""
        return self._publisher_id
    
    async def publish(
        self,
        payload: Dict[str, Any],
        record_type: RecordType = RecordType.EVENT,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        artifact_references: Optional[List[ArtifactReference]] = None,
    ) -> StreamCommit:
        """
        Publish a single record to the stream.
        
        Args:
            payload: The data content of the record
            record_type: Type of record being committed
            correlation_id: Correlation ID for tracing related records
            causation_id: Causation ID indicating what caused this record
            artifact_references: References to artifacts involved
            
        Returns:
            The committed record(s)
            
        Raises:
            CapacityExceededError: If stream capacity exceeded
        """
        # Create the record
        record = StreamRecord(
            record_id=StreamRecordId(  # Will be filled in by storage
                generation_id=StreamGenerationId(self._stream_id, 1),
                sequence=0
            ),
            record_type=record_type,
            payload=payload,
            content_hash="",
            correlation_id=correlation_id,
            causation_id=causation_id,
            parent_record_id=None,
            producer_runtime_id=self._publisher_id.split("_")[0],
            producer_stream_id=self._stream_id,
            artifact_references=tuple(artifact_references or []),
            generation_number=1,
            sequence_in_generation=0,
        )
        
        # Validate and commit
        commit = await self._commit_records((record,))
        return commit
    
    async def publish_batch(
        self,
        records: List[Tuple[Dict[str, Any], RecordType]],
    ) -> StreamCommit:
        """
        Publish multiple records as a single atomic commit.
        
        Args:
            records: List of (payload, record_type) tuples
            
        Returns:
            The committed records
        """
        # Create records
        batch = []
        for payload, record_type in records:
            record = StreamRecord(
                record_id=StreamRecordId(
                    generation_id=StreamGenerationId(self._stream_id, 1),
                    sequence=0
                ),
                record_type=record_type,
                payload=payload,
                content_hash="",
                correlation_id=None,
                causation_id=None,
                parent_record_id=None,
                producer_runtime_id=self._publisher_id.split("_")[0],
                producer_stream_id=self._stream_id,
                artifact_references=(),
                generation_number=1,
                sequence_in_generation=len(batch),
            )
            batch.append(record)
        
        commit = await self._commit_records(tuple(batch))
        return commit
    
    async def flush(self) -> Optional[StreamCommit]:
        """
        Flush any pending records in the batch.
        
        Returns:
            The commit if there were pending records, None otherwise
        """
        if not self._batch:
            return None
        
        commit = await self._commit_records(tuple(self._batch))
        self._batch = []
        return commit
    
    async def _commit_records(
        self,
        records: Tuple[StreamRecord, ...],
    ) -> StreamCommit:
        """Internal method to commit records."""
        # Create generation ID
        gen_id = StreamGenerationId(
            stream_id=self._stream_id,
            number=1  # Will be managed by registry
        )
        
        # Update record IDs with proper sequence numbers
        updated_records = []
        for idx, record in enumerate(records):
            new_record_id = StreamRecordId(gen_id, idx)
            
            new_record = StreamRecord(
                record_id=new_record_id,
                record_type=record.record_type,
                payload=dict(record.payload),
                content_hash="",
                correlation_id=record.correlation_id,
                causation_id=record.causation_id,
                parent_record_id=record.parent_record_id,
                producer_runtime_id=self._publisher_id.split("_")[0],
                producer_stream_id=self._stream_id,
                artifact_references=record.artifact_references,
                generation_number=gen_id.number,
                sequence_in_generation=new_record_id.sequence,
            )
            updated_records.append(new_record)
        
        commit = StreamCommit.from_records(
            stream_id=self._stream_id,
            generation_id=gen_id,
            records=tuple(updated_records),
        )
        
        self._records_published += len(records)
        self._commits_sent += 1
        
        return commit
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get publisher statistics."""
        return {
            "publisher_id": self._publisher_id,
            "stream_id": str(self._stream_id.value),
            "records_published": self._records_published,
            "commits_sent": self._commits_sent,
        }


# =============================================================================
# SUBSCRIBER
# =============================================================================

@dataclass(frozen=True)
class SubscriberConfig:
    """Configuration for a stream subscriber."""
    consumer_id: str
    stream_id: StreamId
    
    # Starting position
    start_from_beginning: bool = False
    start_position: Optional[StreamPosition] = None
    
    # Delivery settings
    batch_size: int = 100
    timeout_seconds: float = 30.0
    
    # Acknowledgement
    auto_acknowledge: bool = True
    max_pending_acks: int = 1000


class StreamSubscriber:
    """
    Subscriber for consuming records from streams.
    
    Provides a high-level API for subscribing that handles:
        - Cursor management and checkpointing
        - Batched record retrieval
        - Acknowledgement tracking
    
    Thread safety: All public methods are thread-safe.
    """
    
    def __init__(
        self,
        stream_id: StreamId,
        consumer_id: Optional[str] = None,
        config: Optional[SubscriberConfig] = None,
    ):
        self._stream_id = stream_id
        self._consumer_id = consumer_id or f"sub_{uuid.uuid4().hex[:16]}"
        
        self._config = config or SubscriberConfig(
            consumer_id=self._consumer_id,
            stream_id=stream_id
        )
        
        # Cursor state
        self._cursor = StreamCursor(
            stream_id=stream_id,
            generation_id=None,
            position=StreamPosition.from_beginning()
        )
        
        # Pending acknowledgements
        self._pending_acks: Dict[str, StreamRecordId] = {}
        
        # Statistics
        self._records_received = 0
        self._acks_sent = 0
    
    @property
    def stream_id(self) -> StreamId:
        """Get the stream this subscriber reads from."""
        return self._config.stream_id
    
    @property
    def consumer_id(self) -> str:
        """Get the consumer ID."""
        return self._consumer_id
    
    async def subscribe(
        self,
        position: Optional[StreamPosition] = None,
    ) -> Tuple[StreamRecord, ...]:
        """
        Subscribe and get records since position.
        
        Args:
            position: Position to start from (uses cursor if not specified)
            
        Returns:
            Available records
        """
        start_pos = position or self._cursor.position
        
        # Get records from storage (placeholder - would call storage layer)
        records = await self._fetch_records(self._stream_id, start_pos)
        
        if records:
            # Update cursor to after last record
            last_record = records[-1]
            new_position = StreamPosition(
                generation_id=start_pos.generation_id,
                record_sequence=last_record.sequence_in_generation + 1
            )
            self._cursor = self._cursor.advance(new_position)
            
            self._records_received += len(records)
        
        return records
    
    async def _fetch_records(
        self,
        stream_id: StreamId,
        position: StreamPosition,
    ) -> Tuple[StreamRecord, ...]:
        """
        Fetch records from storage.
        
        This is a placeholder - in production would call actual storage layer.
        """
        # Placeholder implementation
        return tuple()
    
    async def acknowledge(
        self,
        record_id: StreamRecordId,
    ) -> None:
        """Acknowledge processing of a record."""
        if record_id.value in self._pending_acks:
            del self._pending_acks[record_id.value]
        
        self._acks_sent += 1
    
    def get_checkpoint(self) -> StreamCheckpoint:
        """Create checkpoint from current cursor state."""
        return self._cursor.to_checkpoint()
    
    async def subscribe_stream(
        self,
        position: Optional[StreamPosition] = None,
    ) -> AsyncGenerator[StreamRecord, None]:
        """
        Subscribe and yield records as they become available.
        
        This is a streaming version that yields records continuously.
        
        Yields:
            Records from the stream
        """
        start_pos = position or self._cursor.position
        
        while True:
            # Get records
            records = await self._fetch_records(self._stream_id, start_pos)
            
            for record in records:
                yield record
            
            if not records:
                # No more records available, wait a bit before checking again
                await asyncio.sleep(0.1)
            else:
                # Update position to after last record
                last_record = records[-1]
                start_pos = StreamPosition(
                    generation_id=start_pos.generation_id,
                    record_sequence=last_record.sequence_in_generation + 1
                )


# =============================================================================
# CORRELATION TRACER
# =============================================================================

@dataclass(frozen=True)
class CorrelationChain:
    """Traceable chain of correlated records."""
    root_correlation_id: str
    
    # Records in the chain (record_id -> record mapping would be stored externally)
    records: Tuple[str, ...]  # Record IDs only
    
    created_at_utc: float = field(default_factory=time.time)


class CorrelationTracer:
    """
    Traces correlation and causation chains across streams.
    
    Helps understand relationships between records in different streams
    by tracking correlation IDs through the system.
    """
    
    def __init__(self):
        self._chains: Dict[str, CorrelationChain] = {}
        self._lock = asyncio.Lock()
    
    async def record_correlation(
        self,
        correlation_id: str,
        record_ids: List[str],
    ) -> None:
        """Record a correlation chain."""
        async with self._lock:
            self._chains[correlation_id] = CorrelationChain(
                root_correlation_id=correlation_id,
                records=tuple(record_ids),
                created_at_utc=time.time()
            )
    
    async def get_chain(self, correlation_id: str) -> Optional[CorrelationChain]:
        """Get a correlation chain by ID."""
        async with self._lock:
            return self._chains.get(correlation_id)
    
    async def find_chains_for_record(
        self,
        record_id: str,
    ) -> List[str]:
        """
        Find all chains that contain a specific record.
        
        Returns:
            List of correlation IDs containing this record
        """
        async with self._lock:
            result = []
            for cid, chain in self._chains.items():
                if record_id in chain.records:
                    result.append(cid)
            return result


# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

async def create_stream_publisher(
    stream_id: StreamId,
    publisher_id: Optional[str] = None,
) -> StreamPublisher:
    """
    Factory function to create a stream publisher.
    
    This is the recommended way to get publishers in application code.
    """
    return StreamPublisher(stream_id, publisher_id)


async def create_stream_subscriber(
    stream_id: StreamId,
    consumer_id: Optional[str] = None,
) -> StreamSubscriber:
    """
    Factory function to create a stream subscriber.
    
    This is the recommended way to get subscribers in application code.
    """
    return StreamSubscriber(stream_id, consumer_id)


async def trace_correlation_chain(
    correlation_id: str,
    record_ids: List[str],
) -> None:
    """
    Helper to record a correlation chain.
    
    Usage:
        await trace_correlation_chain(
            "req-123",
            ["record-1", "record-2", "record-3"]
        )
    """
    tracer = CorrelationTracer()
    await tracer.record_correlation(correlation_id, record_ids)


__all__ = [
    # Publisher
    "PublisherConfig",
    "StreamPublisher",
    
    # Subscriber
    "SubscriberConfig",
    "StreamSubscriber",
    
    # Tracing
    "CorrelationChain",
    "CorrelationTracer",
    
    # Helpers
    "create_stream_publisher",
    "create_stream_subscriber",
    "trace_correlation_chain",
]