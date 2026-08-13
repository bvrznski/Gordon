# Stream Storage Interface
# ========================

"""
Storage abstraction for persistent stream records and checkpoints.

This module defines interfaces and base classes for storing:
    - Stream records (commits with ordered data)
    - Checkpoints (consumer positions for recovery)
    - History and replay capabilities

Storage implementations handle:
    - Durability guarantees
    - Bounded retention policies
    - Integrity verification
    - Efficient range queries
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time

from .__init__ import (
    StreamId,
    StreamGenerationId,
    StreamRecordId,
    StreamRecord,
    StreamCommit,
    StreamCheckpoint,
    StreamPosition,
    StreamNotFoundError,
)


class StorageBackend(Enum):
    """Supported storage backends."""
    MEMORY = "memory"
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    REDIS = "redis"
    S3 = "s3"


@dataclass
class StorageConfig:
    """Configuration for stream storage."""
    backend: StorageBackend = StorageBackend.MEMORY
    connection_string: str = ":memory:"
    
    # Retention policy
    max_records: int = 100000
    max_age_seconds: int = 86400  # 24 hours
    
    # Integrity
    enable_integrity_verification: bool = True
    hash_algorithm: str = "sha256"
    
    # Performance
    batch_commit_size: int = 100
    use_transaction: bool = True


# =============================================================================
# RECORD RETENTION POLICY
# =============================================================================

class RetentionPolicy(Enum):
    """Strategies for handling expired records."""
    DELETE = "delete"           # Remove expired records immediately
    ARCHIVE = "archive"         # Move to archive storage
    IGNORE = "ignore"           # Leave in place but don't return


@dataclass(frozen=True)
class StreamStoragePolicy:
    """
    Storage policy for a specific stream.
    
    These policies override the global defaults on a per-stream basis.
    """
    retention_seconds: int = 86400
    max_records: int = 100000
    min_retained_generations: int = 3
    
    backpressure_threshold: float = 0.8
    
    replay_window_seconds: int = 3600  # Default 1 hour replay window
    max_replay_records: int = 10000


# =============================================================================
# STORAGE INTERFACE
# =============================================================================

class StreamStorage(ABC):
    """
    Abstract base class for stream storage implementations.
    
    All storage backends must implement these methods to ensure
    consistent behavior across different persistence layers.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend."""
        ...
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the storage backend cleanly."""
        ...
    
    # -------------------------------------------------------------------------
    # COMMIT OPERATIONS
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def commit(
        self,
        commit: StreamCommit,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> bool:
        """
        Persist a commit to storage.
        
        Args:
            commit: The commit to persist
            policy: Storage policy for this stream
            
        Returns:
            True if commit succeeded, False otherwise
        """
        ...
    
    @abstractmethod
    async def get_commit(
        self,
        record_id: StreamRecordId,
    ) -> Optional[StreamCommit]:
        """
        Retrieve a specific commit by record ID.
        
        Args:
            record_id: The record to retrieve
            
        Returns:
            The commit containing the record, or None if not found
        """
        ...
    
    # -------------------------------------------------------------------------
    # RANGE READ OPERATIONS
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def read_range(
        self,
        stream_id: StreamId,
        start_position: StreamPosition,
        end_position: Optional[StreamPosition] = None,
        limit: Optional[int] = None,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Tuple[StreamRecord, ...]:
        """
        Read a range of records from storage.
        
        Args:
            stream_id: Stream to read from
            start_position: Starting position (inclusive)
            end_position: Ending position (exclusive), or None for all
            limit: Maximum number of records to return
            policy: Storage policy for this stream
            
        Returns:
            Tuple of records in range
        """
        ...
    
    @abstractmethod
    async def read_all_records(
        self,
        stream_id: StreamId,
        generation_id: Optional[StreamGenerationId] = None,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Tuple[StreamRecord, ...]:
        """
        Read all records for a stream (or specific generation).
        
        Args:
            stream_id: Stream to read from
            generation_id: Specific generation, or None for all
            policy: Storage policy for this stream
            
        Returns:
            Tuple of all matching records
        """
        ...
    
    # -------------------------------------------------------------------------
    # POSITION & PAGINATION
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def get_latest_position(
        self,
        stream_id: StreamId,
    ) -> Optional[StreamPosition]:
        """
        Get the latest position in a stream.
        
        Args:
            stream_id: Stream to query
            
        Returns:
            Latest position, or None if stream has no records
        """
        ...
    
    @abstractmethod
    async def get_position_at_time(
        self,
        stream_id: StreamId,
        timestamp_utc: float,
    ) -> Optional[StreamPosition]:
        """
        Get the position in a stream at a specific time.
        
        Args:
            stream_id: Stream to query
            timestamp_utc: Unix timestamp
            
        Returns:
            Position that was current at the given time, or None if not found
        """
        ...
    
    # -------------------------------------------------------------------------
    # CHECKPOINT OPERATIONS
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def save_checkpoint(
        self,
        checkpoint: StreamCheckpoint,
    ) -> bool:
        """
        Save a consumer checkpoint.
        
        Args:
            checkpoint: The checkpoint to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        ...
    
    @abstractmethod
    async def load_checkpoint(
        self,
        stream_id: StreamId,
        consumer_id: str,
    ) -> Optional[StreamCheckpoint]:
        """
        Load a previously saved checkpoint.
        
        Args:
            stream_id: Stream the checkpoint belongs to
            consumer_id: Consumer who owned the checkpoint
            
        Returns:
            The loaded checkpoint, or None if not found
        """
        ...
    
    @abstractmethod
    async def delete_checkpoint(
        self,
        stream_id: StreamId,
        consumer_id: str,
    ) -> bool:
        """
        Delete a saved checkpoint.
        
        Args:
            stream_id: Stream the checkpoint belongs to
            consumer_id: Consumer who owned the checkpoint
            
        Returns:
            True if deleted, False if not found
        """
        ...
    
    # -------------------------------------------------------------------------
    # HISTORY & REPLAY
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def replay_from(
        self,
        stream_id: StreamId,
        position: StreamPosition,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Tuple[Tuple[StreamRecord, ...], Optional[StreamPosition]]:
        """
        Replay records from a given position.
        
        Args:
            stream_id: Stream to replay
            position: Starting position (inclusive)
            policy: Storage policy for this stream
            
        Returns:
            Tuple of (records, next_position) or empty tuple if no more records
        """
        ...
    
    @abstractmethod
    async def get_replay_boundary(
        self,
        stream_id: StreamId,
        current_time_utc: float,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Optional[StreamPosition]:
        """
        Get the earliest position that can be replayed.
        
        This is determined by retention policies - older records may have
        been deleted and cannot be replayed.
        
        Args:
            stream_id: Stream to query
            current_time_utc: Current time for calculating boundaries
            policy: Storage policy for this stream
            
        Returns:
            Earliest repliable position, or None if no valid history
        """
        ...
    
    # -------------------------------------------------------------------------
    # INTEGRITY & VALIDATION
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def verify_integrity(
        self,
        stream_id: Optional[StreamId] = None,
    ) -> Dict[str, Any]:
        """
        Verify storage integrity.
        
        Args:
            stream_id: Specific stream to check, or None for all
            
        Returns:
            Dictionary with verification results and any errors
        """
        ...
    
    @abstractmethod
    async def cleanup_expired(
        self,
        current_time_utc: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Remove expired records according to retention policies.
        
        Args:
            current_time_utc: Current time for expiry calculations
            
        Returns:
            Dictionary with cleanup statistics
        """
        ...
    
    # -------------------------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------------------------
    
    @abstractmethod
    async def get_statistics(
        self,
        stream_id: Optional[StreamId] = None,
    ) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Args:
            stream_id: Specific stream to query, or None for all
            
        Returns:
            Dictionary with storage statistics
        """
        ...


# =============================================================================
# MEMORY STORAGE IMPLEMENTATION
# =============================================================================

class MemoryStreamStorage(StreamStorage):
    """
    In-memory implementation of StreamStorage for testing and development.
    
    This implementation stores everything in memory and is not durable across
    restarts. It's intended for testing, local development, or ephemeral streams.
    """
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self._config = config or StorageConfig()
        
        # Data structures
        self._commits: Dict[str, StreamCommit] = {}  # commit_id -> commit
        self._record_index: Dict[str, Tuple[str, int]] = {}  # record_id -> (commit_id, index)
        self._stream_positions: Dict[StreamId, StreamPosition] = {}
        
        # Checkpoints
        self._checkpoints: Dict[Tuple[StreamId, str], StreamCheckpoint] = {}
        
        # Statistics
        self._commit_count = 0
        self._read_count = 0
    
    async def initialize(self) -> None:
        """Initialize memory storage (no-op)."""
        pass
    
    async def shutdown(self) -> None:
        """Shutdown memory storage (no-op)."""
        self._commits.clear()
        self._record_index.clear()
    
    # -------------------------------------------------------------------------
    # COMMIT OPERATIONS
    # -------------------------------------------------------------------------
    
    async def commit(
        self,
        commit: StreamCommit,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> bool:
        """Persist a commit to memory."""
        if not commit.verify_integrity():
            raise ValueError("Commit integrity verification failed")
        
        # Store the commit
        self._commits[commit.commit_id] = commit
        
        # Build index for each record in the commit
        for idx, record in enumerate(commit.records):
            record_key = record.record_id.value
            self._record_index[record_key] = (commit.commit_id, idx)
        
        # Update stream position if this is a new record
        stream_id = commit.stream_id
        current_pos = self._stream_positions.get(stream_id)
        new_seq = max(r.sequence_in_generation for r in commit.records)
        
        new_position = StreamPosition(
            generation_id=commit.generation_id,
            record_sequence=new_seq
        )
        
        if current_pos is None or new_position.record_sequence > current_pos.record_sequence:
            self._stream_positions[stream_id] = new_position
        
        self._commit_count += 1
        return True
    
    async def get_commit(
        self,
        record_id: StreamRecordId,
    ) -> Optional[StreamCommit]:
        """Retrieve a commit by record ID."""
        if record_id.value in self._record_index:
            commit_id, _ = self._record_index[record_id.value]
            return self._commits.get(commit_id)
        return None
    
    # -------------------------------------------------------------------------
    # RANGE READ OPERATIONS
    # -------------------------------------------------------------------------
    
    async def read_range(
        self,
        stream_id: StreamId,
        start_position: StreamPosition,
        end_position: Optional[StreamPosition] = None,
        limit: Optional[int] = None,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Tuple[StreamRecord, ...]:
        """Read records in a range from memory."""
        result = []
        
        for commit_id, commit in self._commits.items():
            if commit.stream_id != stream_id:
                continue
            
            for record in commit.records:
                seq = record.sequence_in_generation
                
                # Check start position
                if seq < start_position.record_sequence:
                    continue
                
                # Check end position
                if end_position is not None and seq >= end_position.record_sequence:
                    continue
                
                result.append(record)
                
                # Apply limit
                if limit is not None and len(result) >= limit:
                    break
            
            if limit is not None and len(result) >= limit:
                break
        
        self._read_count += 1
        return tuple(result)
    
    async def read_all_records(
        self,
        stream_id: StreamId,
        generation_id: Optional[StreamGenerationId] = None,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Tuple[StreamRecord, ...]:
        """Read all records for a stream."""
        result = []
        
        for commit in self._commits.values():
            if commit.stream_id != stream_id:
                continue
            
            if generation_id is not None and commit.generation_id != generation_id:
                continue
            
            result.extend(commit.records)
        
        return tuple(result)
    
    # -------------------------------------------------------------------------
    # POSITION & PAGINATION
    # -------------------------------------------------------------------------
    
    async def get_latest_position(
        self,
        stream_id: StreamId,
    ) -> Optional[StreamPosition]:
        """Get the latest position in a stream."""
        return self._stream_positions.get(stream_id)
    
    async def get_position_at_time(
        self,
        stream_id: StreamId,
        timestamp_utc: float,
    ) -> Optional[StreamPosition]:
        """
        Get position at a specific time.
        
        In memory storage, we don't track timestamps for individual records
        well enough to accurately answer this. Return None or latest.
        """
        return self._stream_positions.get(stream_id)
    
    # -------------------------------------------------------------------------
    # CHECKPOINT OPERATIONS
    # -------------------------------------------------------------------------
    
    async def save_checkpoint(
        self,
        checkpoint: StreamCheckpoint,
    ) -> bool:
        """Save a checkpoint in memory."""
        key = (checkpoint.stream_id, "default")
        self._checkpoints[key] = checkpoint
        return True
    
    async def load_checkpoint(
        self,
        stream_id: StreamId,
        consumer_id: str,
    ) -> Optional[StreamCheckpoint]:
        """Load a checkpoint from memory."""
        key = (stream_id, consumer_id)
        return self._checkpoints.get(key)
    
    async def delete_checkpoint(
        self,
        stream_id: StreamId,
        consumer_id: str,
    ) -> bool:
        """Delete a checkpoint from memory."""
        key = (stream_id, consumer_id)
        if key in self._checkpoints:
            del self._checkpoints[key]
            return True
        return False
    
    # -------------------------------------------------------------------------
    # HISTORY & REPLAY
    # -------------------------------------------------------------------------
    
    async def replay_from(
        self,
        stream_id: StreamId,
        position: StreamPosition,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Tuple[Tuple[StreamRecord, ...], Optional[StreamPosition]]:
        """Replay records from a given position."""
        records = await self.read_range(stream_id, position)
        
        if not records:
            next_pos = position
        else:
            last_record = records[-1]
            next_pos = StreamPosition(
                generation_id=position.generation_id,
                record_sequence=last_record.sequence_in_generation + 1
            )
        
        return records, next_pos
    
    async def get_replay_boundary(
        self,
        stream_id: StreamId,
        current_time_utc: float,
        policy: Optional[StreamStoragePolicy] = None,
    ) -> Optional[StreamPosition]:
        """Get earliest replayable position."""
        # Memory storage doesn't expire records, so boundary is always 0
        return StreamPosition.from_beginning()
    
    # -------------------------------------------------------------------------
    # INTEGRITY & VALIDATION
    # -------------------------------------------------------------------------
    
    async def verify_integrity(
        self,
        stream_id: Optional[StreamId] = None,
    ) -> Dict[str, Any]:
        """Verify integrity of stored data."""
        results = {
            "total_commits": len(self._commits),
            "verified": True,
            "errors": []
        }
        
        for commit in self._commits.values():
            if not commit.verify_integrity():
                results["verified"] = False
                results["errors"].append(f"Corrupted commit: {commit.commit_id}")
        
        return results
    
    async def cleanup_expired(
        self,
        current_time_utc: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Clean up expired records (no-op for memory)."""
        # Memory storage doesn't expire records
        return {
            "records_deleted": 0,
            "bytes_freed": 0
        }
    
    # -------------------------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------------------------
    
    async def get_statistics(
        self,
        stream_id: Optional[StreamId] = None,
    ) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            "commits_stored": len(self._commits),
            "record_index_size": len(self._record_index),
            "checkpoints_stored": len(self._checkpoints),
            "total_commits_processed": self._commit_count,
            "total_reads_performed": self._read_count,
        }
        
        if stream_id:
            # Filter stats for specific stream
            stream_commits = [c for c in self._commits.values() if c.stream_id == stream_id]
            stats["stream_commits"] = len(stream_commits)
        
        return stats


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "StorageBackend",
    "RetentionPolicy",
    
    # Config and policy
    "StorageConfig",
    "StreamStoragePolicy",
    
    # Interfaces
    "StreamStorage",
    
    # Implementations
    "MemoryStreamStorage",
]