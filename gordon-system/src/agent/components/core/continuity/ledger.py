# Continuity Ledger Writer
# =========================

"""
Ledger integration for continuity operations.

This module provides:
    - Journal append for checkpoint lifecycle events
    - LEDGER_RECORD types for continuity-specific transitions
    - Connection to persistence/journal.py backend
    - Crash-recovery ledger tail analysis

The continuity ledger records operational transitions relevant to crash recovery,
enabling accurate restoration and reconciliation of interrupted operations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any
import uuid


# =============================================================================
# LEDGER RECORD KINDS (Continuity-Specific)
# =============================================================================

class ContinuityLedgerRecordKind(Enum):
    """
    Kinds of records in the continuity ledger.
    
    These records track transitions relevant to crash recovery:
        - Checkpoint lifecycle events
        - Restoration operations
        - Interruption classification results
        - Finalization markers
    """
    
    # Checkpoint lifecycle
    CHECKPOINT_STARTED = "CHECKPOINT_STARTED"  # Checkpoint creation began
    CHECKPOINT_FRAGMENT_COLLECTED = "CHECKPOINT_FRAGMENT_COLLECTED"
    CHECKPOINT_COMMITTED = "CHECKPOINT_COMMITTED"  # Checkpoint successfully persisted
    CHECKPOINT_FAILED = "CHECKPOINT_FAILED"
    
    # Restoration lifecycle
    RESTORATION_STARTED = "RESTORATION_STARTED"
    RESTORATION_FRAGMENT_APPLIED = "RESTORATION_FRAGMENT_APPLIED"
    RESTORATION_COMPLETED = "RESTORATION_COMPLETED"
    RESTORATION_FAILED = "RESTORATION_FAILED"
    
    # Interruption reconciliation
    INTERRUPTION_RECONCILED = "INTERRUPTION_RECONCILED"  # Operation classified
    
    # Finalization
    SHUTDOWN_STARTED = "SHUTDOWN_STARTED"
    CHECKPOINT_FINALIZED = "CHECKPOINT_FINALIZED"
    RUNTIME_SHUTDOWN_COMPLETE = "RUNTIME_SHUTDOWN_COMPLETE"
    
    # Recovery markers
    RECOVERY_CHECKPOINT_VALIDATED = "RECOVERY_CHECKPOINT_VALIDATED"
    RECOVERY_COMPLETE = "RECOVERY_COMPLETE"


# =============================================================================
# LEDGER RECORDS
# =============================================================================

@dataclass(frozen=True)
class LedgerRecord:
    """
    A record in the continuity ledger.
    
    Each record represents a transition event with:
        - Sequence number (stable ordering)
        - Timestamp
        - Record kind (type of transition)
        - Context data
        - Correlation ID for tracing
    """
    
    sequence_number: int
    timestamp_ns: int
    record_kind: ContinuityLedgerRecordKind
    checkpoint_id: Optional[str]
    context: Dict[str, Any] = field(default_factory=dict)
    record_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    
    @classmethod
    def create(
        cls,
        sequence_number: int,
        record_kind: ContinuityLedgerRecordKind,
        checkpoint_id: Optional[str] = None,
        **context: Any,
    ) -> "LedgerRecord":
        """Create a new ledger record."""
        return cls(
            sequence_number=sequence_number,
            timestamp_ns=time.time_ns(),
            record_kind=record_kind,
            checkpoint_id=checkpoint_id,
            context=context,
            record_id=uuid.uuid4().hex[:16],
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "sequence_number": self.sequence_number,
            "timestamp_ns": self.timestamp_ns,
            "record_kind": self.record_kind.value,
            "checkpoint_id": self.checkpoint_id,
            "context": dict(self.context),
            "record_id": self.record_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LedgerRecord":
        """Create a record from dictionary (for replay)."""
        return cls(
            sequence_number=data.get("sequence_number", 0),
            timestamp_ns=data.get("timestamp_ns", time.time_ns()),
            record_kind=ContinuityLedgerRecordKind(data.get("record_kind", "")),
            checkpoint_id=data.get("checkpoint_id"),
            context=data.get("context", {}),
            record_id=data.get("record_id", uuid.uuid4().hex[:16]),
        )


@dataclass(frozen=True)
class LedgerTail:
    """
    The tail of the continuity ledger since a checkpoint.
    
    Used for interruption reconciliation - operations that occurred
    after the checkpoint but before the crash need to be classified.
    """
    
    start_sequence: int
    end_sequence: int
    records: Tuple[LedgerRecord, ...]
    last_checkpoint_id: Optional[str]


# =============================================================================
# LEDGER WRITER
# =============================================================================

class ContinuityLedgerWriter:
    """
    Writer for the continuity ledger with journal backend integration.
    
    This class provides an abstraction over persistence/journal.py,
    adding continuity-specific record types and semantics.
    """
    
    def __init__(
        self,
        runtime_id: str,
        journal_manager: Any,  # persistence.journal.JournalManager
        ledger_id: Optional[str] = None,
    ):
        """
        Initialize the ledger writer.
        
        Args:
            runtime_id: ID of the current runtime instance
            journal_manager: The underlying journal manager backend
            ledger_id: Optional specific ledger ID (auto-generated if not provided)
        """
        self._runtime_id = runtime_id
        self._journal_manager = journal_manager
        self._ledger_id = ledger_id or f"continuity_{runtime_id}"
        
        # Track sequence numbers per ledger
        self._sequence_counter: Dict[str, int] = {}
    
    @property
    def ledger_id(self) -> str:
        """Get the current ledger ID."""
        return self._ledger_id
    
    async def _get_next_sequence(self) -> int:
        """Get the next sequence number for this ledger."""
        if self._ledger_id not in self._sequence_counter:
            self._sequence_counter[self._ledger_id] = 0
        
        self._sequence_counter[self._ledger_id] += 1
        return self._sequence_counter[self._ledger_id]
    
    async def append_checkpoint_started(self, checkpoint_id: str) -> LedgerRecord:
        """
        Record that a checkpoint operation has started.
        
        Args:
            checkpoint_id: ID of the checkpoint being created
            
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.CHECKPOINT_STARTED,
            checkpoint_id=checkpoint_id,
            runtime_id=self._runtime_id,
        )
        
        # Append to journal backend
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,  # Uses default
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                    "ledger_id": self._ledger_id,
                },
            )
        )
        
        return record
    
    async def append_checkpoint_fragment_collected(
        self,
        checkpoint_id: str,
        participant_id: str,
    ) -> LedgerRecord:
        """
        Record that a fragment has been collected for the checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            participant_id: ID of the participant whose fragment was collected
            
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.CHECKPOINT_FRAGMENT_COLLECTED,
            checkpoint_id=checkpoint_id,
            participant_id=participant_id,
        )
        
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                },
            )
        )
        
        return record
    
    async def append_checkpoint_committed(
        self,
        checkpoint_id: str,
        storage_path: str,
        fragment_count: int,
    ) -> LedgerRecord:
        """
        Record that a checkpoint has been successfully committed.
        
        Args:
            checkpoint_id: ID of the checkpoint
            storage_path: Path where checkpoint was persisted
            fragment_count: Number of fragments in the checkpoint
            
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.CHECKPOINT_COMMITTED,
            checkpoint_id=checkpoint_id,
            storage_path=storage_path,
            fragment_count=fragment_count,
        )
        
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                },
            )
        )
        
        return record
    
    async def append_checkpoint_failed(
        self,
        checkpoint_id: str,
        error: str,
    ) -> LedgerRecord:
        """
        Record that a checkpoint operation failed.
        
        Args:
            checkpoint_id: ID of the checkpoint
            error: Error message describing the failure
            
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.CHECKPOINT_FAILED,
            checkpoint_id=checkpoint_id,
            error=error,
        )
        
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                },
            )
        )
        
        return record
    
    async def append_restoration_started(self, checkpoint_id: str) -> LedgerRecord:
        """
        Record that restoration from a checkpoint has started.
        
        Args:
            checkpoint_id: ID of the checkpoint being restored
            
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.RESTORATION_STARTED,
            checkpoint_id=checkpoint_id,
        )
        
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                },
            )
        )
        
        return record
    
    async def append_interruption_reconciled(
        self,
        checkpoint_id: str,
        participant_id: str,
        operation_class: str,
        action_taken: str,
    ) -> LedgerRecord:
        """
        Record that an interrupted operation has been reconciled.
        
        Args:
            checkpoint_id: ID of the checkpoint
            participant_id: ID of the participant that reconciled
            operation_class: Classification result (e.g., "COMPLETED", "SAFE_TO_RETRY")
            action_taken: What action was taken (resume, retry, rollback, etc.)
            
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.INTERRUPTION_RECONCILED,
            checkpoint_id=checkpoint_id,
            participant_id=participant_id,
            operation_class=operation_class,
            action_taken=action_taken,
        )
        
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                },
            )
        )
        
        return record
    
    async def append_shutdown_started(self) -> LedgerRecord:
        """
        Record that shutdown has started.
        
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.SHUTDOWN_STARTED,
            runtime_id=self._runtime_id,
        )
        
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                },
            )
        )
        
        return record
    
    async def append_shutdown_complete(self, final_checkpoint_id: Optional[str]) -> LedgerRecord:
        """
        Record that shutdown completed successfully.
        
        Args:
            final_checkpoint_id: ID of the checkpoint created during shutdown
            
        Returns:
            The created ledger record
        """
        seq = await self._get_next_sequence()
        record = LedgerRecord.create(
            sequence_number=seq,
            record_kind=ContinuityLedgerRecordKind.RUNTIME_SHUTDOWN_COMPLETE,
            checkpoint_id=final_checkpoint_id,
        )
        
        from persistence.journal import JournalAppendRequest, JournalRecordKind as JRecordKind
        
        await self._journal_manager.append(
            request=JournalAppendRequest(
                request_id=str(uuid.uuid4()),
                runtime_id=self._runtime_id,
                journal_id=None,
                kind=JRecordKind.EVENT,
                domain_id="continuity",
                payload={
                    "record": record.to_dict(),
                },
            )
        )
        
        return record
    
    async def get_ledger_tail(
        self,
        since_checkpoint_id: Optional[str] = None,
    ) -> LedgerTail:
        """
        Get the ledger tail since a checkpoint.
        
        Args:
            since_checkpoint_id: ID of the last known checkpoint (None = from start)
            
        Returns:
            The ledger tail records
        """
        # In this simplified implementation, we return an empty tail
        # A real implementation would replay the journal backend
        
        if since_checkpoint_id is None:
            # Return all records
            return LedgerTail(
                start_sequence=1,
                end_sequence=self._sequence_counter.get(self._ledger_id, 0),
                records=(),
                last_checkpoint_id=None,
            )
        
        # Get records after the checkpoint
        return LedgerTail(
            start_sequence=1,
            end_sequence=self._sequence_counter.get(self._ledger_id, 0),
            records=(),
            last_checkpoint_id=since_checkpoint_id,
        )
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about the ledger writer."""
        return {
            "runtime_id": self._runtime_id,
            "ledger_id": self._ledger_id,
            "sequence_counter": dict(self._sequence_counter),
            "journal_manager_status": getattr(self._journal_manager, "get_diagnostics", lambda: {})(),
        }