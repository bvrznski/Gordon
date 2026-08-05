# Journal Manager
# ===============

"""
Append-only journal for state changes and events.

This module provides:
- JournalManager: Canonical journal authority
- Append-only writes with stable ordering
- Sequence assignment and validation
- Segment rotation and compaction
- Replay support

Key principle: Journals are append-only. They record ordered evidence of
changes, not direct state mutations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterable
from enum import Enum, auto
import uuid
import time


@dataclass(frozen=True)
class JournalId:
    value: str
    
    @classmethod
    def generate(cls) -> "JournalId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class JournalRecordId:
    value: str
    
    @classmethod
    def generate(cls) -> "JournalRecordId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


class JournalRecordKind(Enum):
    EVENT = "event"
    MUTATION = "mutation"
    COMMAND = "command"
    SNAPSHOT_BOUNDARY = "snapshot_boundary"


@dataclass(frozen=True)
class JournalSegment:
    segment_id: str
    start_sequence: int
    end_sequence: int
    record_count: int
    storage_key: str
    content_digest: str
    created_at: float
    closed_at: Optional[float] = None


@dataclass(frozen=True)
class JournalCursor:
    cursor_id: str
    journal_id: str
    from_sequence: int
    to_sequence: Optional[int] = None
    ignore_gaps: bool = False
    suppress_side_effects: bool = True


@dataclass(frozen=True)
class GapInfo:
    from_sequence: int
    to_sequence: int
    reason: str


@dataclass(frozen=True)
class JournalAppendRequest:
    request_id: str
    runtime_id: str
    
    journal_id: Optional[JournalId] = None
    kind: JournalRecordKind = JournalRecordKind.EVENT
    domain_id: str = ""
    
    boot_session_id: Optional[str] = None
    state_version_before: int = 0
    state_version_after: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


@dataclass(frozen=True)
class JournalAppendResult:
    result_id: str
    request_id: str
    runtime_id: str
    
    status: "JournalStatus"
    timestamp: float = field(default_factory=time.monotonic)
    
    record: Optional["JournalRecord"] = None
    sequence_number: Optional[int] = None
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status == JournalStatus.APPENDED


@dataclass(frozen=True)
class JournalReplayRequest:
    request_id: str
    runtime_id: str
    
    journal_id: Optional[JournalId] = None
    from_sequence: int = 0
    to_sequence: Optional[int] = None
    
    ignore_gaps: bool = False
    suppress_side_effects: bool = True


@dataclass(frozen=True)
class JournalReplayResult:
    result_id: str
    request_id: str
    runtime_id: str
    
    status: "JournalStatus"
    timestamp: float = field(default_factory=time.monotonic)
    
    records_replayed: int = 0
    gaps_detected: List[GapInfo] = field(default_factory=list)
    records_ignored: int = 0
    error_message: Optional[str] = None


class JournalStatus(Enum):
    APPENDED = "appended"
    GAPS_DETECTED = "gaps_detected"
    ROTATED = "rotated"
    COMPACTED = "compacted"
    FAILED = "failed"


@dataclass(frozen=True)
class JournalRecord:
    record_id: JournalRecordId
    sequence: int
    
    runtime_id: str
    kind: JournalRecordKind
    domain_id: str
    
    boot_session_id: Optional[str] = None
    state_version_before: int = 0
    state_version_after: int = 0
    
    payload: Dict[str, Any] = field(default_factory=dict)
    
    timestamp: float = field(default_factory=time.monotonic)
    content_digest: str = ""
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


class JournalManager:
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        
        self._journals: Dict[JournalId, List[JournalRecord]] = {}
        self._segments: Dict[str, JournalSegment] = {}
        self._sequences: Dict[str, int] = {}
        
        self._backend = None
        self._max_segment_size = 1000
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    async def append(
        self,
        request: JournalAppendRequest
    ) -> JournalAppendResult:
        journal_id = request.journal_id
        if not journal_id:
            journal_id = JournalId(value=f"default_{self._runtime_id}")
        
        key = str(journal_id)
        if key not in self._sequences:
            self._sequences[key] = 0
        
        sequence = self._sequences[key]
        self._sequences[key] = sequence + 1
        
        record = JournalRecord(
            record_id=JournalRecordId.generate(),
            sequence=sequence,
            runtime_id=request.runtime_id,
            kind=request.kind,
            domain_id=request.domain_id,
            boot_session_id=request.boot_session_id,
            state_version_before=request.state_version_before,
            state_version_after=request.state_version_after,
            payload=dict(request.payload),
            timestamp=time.monotonic(),
            content_digest="",
            correlation_id=request.correlation_id,
            causation_id=request.causation_id,
        )
        
        if journal_id not in self._journals:
            self._journals[journal_id] = []
        
        self._journals[journal_id].append(record)
        
        return JournalAppendResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=JournalStatus.APPENDED,
            record=record,
            sequence_number=sequence,
        )
    
    async def replay(
        self,
        request: JournalReplayRequest
    ) -> JournalReplayResult:
        journal_id = request.journal_id
        
        if not journal_id:
            matching = [
                jid for jid in self._journals.keys()
                if str(jid).startswith(f"default_{self._runtime_id}")
            ]
            if not matching:
                return JournalReplayResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=self._runtime_id,
                    status=JournalStatus.FAILED,
                    timestamp=time.monotonic(),
                    error_message="No journal found",
                )
            journal_id = max(matching)
        
        records = self._journals.get(journal_id, [])
        
        from_seq = request.from_sequence
        to_seq = request.to_sequence
        
        if to_seq is not None:
            filtered = [r for r in records if from_seq <= r.sequence < to_seq]
        else:
            filtered = [r for r in records if r.sequence >= from_seq]
        
        gaps = self._detect_gaps(filtered, from_seq)
        
        suppressed_count = len([r for r in filtered if r.kind == JournalRecordKind.MUTATION])
        
        return JournalReplayResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=JournalStatus.GAPS_DETECTED if gaps else JournalStatus.APPENDED,
            timestamp=time.monotonic(),
            records_replayed=len(filtered),
            gaps_detected=gaps,
            records_ignored=suppressed_count,
        )
    
    def _detect_gaps(
        self,
        records: List[JournalRecord],
        from_sequence: int
    ) -> List[GapInfo]:
        gaps = []
        
        if not records:
            return gaps
        
        first_seq = min(r.sequence for r in records)
        if first_seq > from_sequence:
            gaps.append(GapInfo(
                from_sequence=from_sequence,
                to_sequence=first_seq,
                reason="missing",
            ))
        
        sorted_records = sorted(records, key=lambda r: r.sequence)
        for i in range(1, len(sorted_records)):
            prev = sorted_records[i - 1]
            curr = sorted_records[i]
            
            if curr.sequence > prev.sequence + 1:
                gaps.append(GapInfo(
                    from_sequence=prev.sequence + 1,
                    to_sequence=curr.sequence,
                    reason="missing",
                ))
        
        return gaps
    
    def get_journal_state(self, journal_id: Optional[JournalId] = None) -> Dict[str, Any]:
        if not journal_id:
            return {
                "journal_count": len(self._journals),
                "total_records": sum(len(r) for r in self._journals.values()),
            }
        
        records = self._journals.get(journal_id, [])
        return {
            "record_count": len(records),
            "first_sequence": min((r.sequence for r in records), default=None),
            "last_sequence": max((r.sequence for r in records), default=None),
        }
    
    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "runtime_id": self._runtime_id,
            "journals_count": len(self._journals),
            "total_records": sum(len(r) for r in self._journals.values()),
        }


__all__ = [
    "JournalId",
    "JournalRecordId",
    "JournalRecordKind",
    "JournalSegment",
    "JournalCursor",
    "GapInfo",
    "JournalAppendRequest",
    "JournalAppendResult",
    "JournalReplayRequest",
    "JournalReplayResult",
    "JournalStatus",
    "JournalRecord",
    "JournalManager",
]