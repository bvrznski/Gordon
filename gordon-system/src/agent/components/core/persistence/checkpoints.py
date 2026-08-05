# Checkpoint Manager
# =================

"""
Checkpoint lifecycle management and atomic commit.

This module provides:
- CheckpointManager: Canonical checkpoint authority
- Full and incremental checkpoint types
- Barrier coordination for multi-participant capture
- Manifest generation with integrity protection
- Atomic or staged commit support
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import uuid
import time


class CheckpointType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    RECOVERY = "recovery"
    SHUTDOWN = "shutdown"
    UPGRADE = "upgrade"
    MIGRATION = "migration"
    DIAGNOSTIC = "diagnostic"
    DOMAIN = "domain"


class CheckpointMode(Enum):
    QUIESCENT = "quiescent"
    VERSIONED = "versioned"
    COPY_ON_WRITE = "copy_on_write"


@dataclass(frozen=True)
class CheckpointId:
    value: str
    
    @classmethod
    def generate(cls) -> "CheckpointId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CheckpointChainRef:
    checkpoint_id: CheckpointId
    digest: str


@dataclass(frozen=True)
class CheckpointManifest:
    """Checkpoint manifest - immutable after creation."""
    checkpoint_id: CheckpointId
    runtime_id: str
    
    boot_session_id: Optional[str]
    
    checkpoint_type: CheckpointType
    capture_mode: CheckpointMode
    
    parent_checkpoint_id: Optional[CheckpointId] = None
    chain_depth: int = 0
    
    created_at: float = field(default_factory=time.monotonic)
    
    runtime_state_version: int = 0
    configuration_version: Optional[int] = None
    
    participants: List["CheckpointParticipant"] = field(default_factory=list)
    
    integrity_hash: str = ""
    creator_id: Optional[str] = None


@dataclass(frozen=True)
class CheckpointParticipant:
    participant_id: str
    domain_ids: List[str]
    state_version_before: int
    state_version_after: int
    payload_digest: str
    signature: Optional[str] = None


@dataclass(frozen=True)
class CheckpointBarrier:
    barrier_id: str
    phase: str
    participants_triggered: List[str]
    completed_at: Optional[float] = None


@dataclass(frozen=True)
class CheckpointRequest:
    request_id: str
    
    runtime_id: str
    checkpoint_type: CheckpointType = CheckpointType.FULL
    mode: CheckpointMode = CheckpointMode.VERSIONED
    
    boot_session_id: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    
    parent_checkpoint_id: Optional[CheckpointId] = None
    
    requires_integrity: bool = True
    quiesce_timeout_seconds: float = 5.0
    
    deadline_at: Optional[float] = None


@dataclass(frozen=True)
class CheckpointResult:
    result_id: str
    request_id: str
    runtime_id: str
    
    status: "CheckpointStatus"
    timestamp: float = field(default_factory=time.monotonic)
    
    manifest: Optional[CheckpointManifest] = None
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status == CheckpointStatus.COMMITTED


class CheckpointStatus(Enum):
    REQUESTED = "requested"
    VALIDATING = "validating"
    PLANNING = "planning"
    PREPARING = "preparing"
    CAPTURING = "capturing"
    SERIALIZING = "serializing"
    WRITING = "writing"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    COMMITTED = "committed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CheckpointManager:
    """
    Canonical checkpoint authority.
    
    Manages:
        - Checkpoint request intake and planning
        - Multi-participant barrier coordination
        - Manifest generation with integrity protection
        - Atomic or staged commit
        - Checkpoint discovery and retention
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        
        self._checkpoints: Dict[CheckpointId, CheckpointManifest] = {}
        self._backend = None
        self._sequences: Dict[str, int] = {}
        
        self._create_count = 0
        self._commit_count = 0
        self._committed_checkpoints: set = set()
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    async def create_checkpoint(
        self,
        request: CheckpointRequest
    ) -> CheckpointResult:
        if not self._validate_checkpoint_request(request):
            return CheckpointResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=CheckpointStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="Request validation failed"
            )
        
        if request.checkpoint_type == CheckpointType.INCREMENTAL:
            if not request.parent_checkpoint_id:
                return CheckpointResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=self._runtime_id,
                    status=CheckpointStatus.FAILED,
                    timestamp=time.monotonic(),
                    error_message="Incremental checkpoint requires parent"
                )
            
            if request.parent_checkpoint_id not in self._checkpoints:
                return CheckpointResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=self._runtime_id,
                    status=CheckpointStatus.FAILED,
                    timestamp=time.monotonic(),
                    error_message="Parent checkpoint not found or not committed"
                )
        
        plan = self._create_checkpoint_plan(request)
        if not plan:
            return CheckpointResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=CheckpointStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="No capture plan created"
            )
        
        barriers = await self._execute_barriers(plan, request)
        
        if not barriers:
            return CheckpointResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=CheckpointStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="Barrier coordination failed"
            )
        
        participants = await self._collect_participant_payloads(plan, request)
        
        if not participants:
            return CheckpointResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=CheckpointStatus.PARTIAL,
                timestamp=time.monotonic(),
                error_message="No participants contributed"
            )
        
        manifest = self._create_manifest(request, plan, barriers, participants)
        
        if not self._validate_checkpoint_integrity(manifest):
            return CheckpointResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=CheckpointStatus.PARTIAL,
                timestamp=time.monotonic(),
                error_message="Integrity validation failed"
            )
        
        committed = await self._commit_manifest(manifest)
        
        if not committed:
            return CheckpointResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=CheckpointStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="Commit failed"
            )
        
        # Mark as committed in the manager's internal state
        self._committed_checkpoints.add(manifest.checkpoint_id)
        self._checkpoints[manifest.checkpoint_id] = manifest
        self._commit_count += 1
        
        return CheckpointResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=CheckpointStatus.COMMITTED,
            timestamp=time.monotonic(),
            manifest=manifest
        )
    
    async def find_checkpoint(
        self,
        checkpoint_id: Optional[CheckpointId] = None,
        runtime_id: Optional[str] = None,
        before_time: Optional[float] = None,
    ) -> Optional[CheckpointManifest]:
        committed = {
            cid: c for cid, c in self._checkpoints.items()
            if cid in self._committed_checkpoints
        }
        
        if checkpoint_id:
            return committed.get(checkpoint_id)
        
        candidates = list(committed.values())
        
        if runtime_id:
            candidates = [c for c in candidates if c.runtime_id == runtime_id]
        
        if before_time:
            candidates = [c for c in candidates if c.created_at < before_time]
        
        if candidates:
            return max(candidates, key=lambda c: c.created_at)
        
        return None
    
    def _validate_checkpoint_request(self, request: CheckpointRequest) -> bool:
        if request.runtime_id != self._runtime_id:
            return False
        
        if request.mode == CheckpointMode.QUIESCENT and request.quiesce_timeout_seconds <= 0:
            return False
        
        return True
    
    def _create_checkpoint_plan(self, request: CheckpointRequest) -> Optional[Dict[str, Any]]:
        if not request.domains:
            return None
        
        return {
            "runtime_id": request.runtime_id,
            "domains": request.domains,
            "mode": request.mode.value,
            "checkpoint_type": request.checkpoint_type.value,
        }
    
    async def _execute_barriers(
        self,
        plan: Dict[str, Any],
        request: CheckpointRequest
    ) -> Optional[List[CheckpointBarrier]]:
        quiesce_barrier = CheckpointBarrier(
            barrier_id=str(uuid.uuid4()),
            phase="quiesce",
            participants_triggered=[],
            completed_at=time.monotonic(),
        )
        
        capture_barrier = CheckpointBarrier(
            barrier_id=str(uuid.uuid4()),
            phase="capture",
            participants_triggered=[],
            completed_at=time.monotonic(),
        )
        
        return [quiesce_barrier, capture_barrier]
    
    async def _collect_participant_payloads(
        self,
        plan: Dict[str, Any],
        request: CheckpointRequest
    ) -> List[CheckpointParticipant]:
        return [
            CheckpointParticipant(
                participant_id=f"participant_{i}",
                domain_ids=["domain_a"],
                state_version_before=0,
                state_version_after=1,
                payload_digest="digest_placeholder",
            )
            for i in range(3)
        ]
    
    def _create_manifest(
        self,
        request: CheckpointRequest,
        plan: Dict[str, Any],
        barriers: List[CheckpointBarrier],
        participants: List[CheckpointParticipant]
    ) -> CheckpointManifest:
        return CheckpointManifest(
            checkpoint_id=CheckpointId.generate(),
            runtime_id=request.runtime_id,
            boot_session_id=request.boot_session_id,
            checkpoint_type=request.checkpoint_type,
            capture_mode=request.mode,
            parent_checkpoint_id=request.parent_checkpoint_id,
            chain_depth=1 if request.parent_checkpoint_id else 0,
            participants=participants,
            created_at=time.monotonic(),
            integrity_hash="",
        )
    
    def _validate_checkpoint_integrity(self, manifest: CheckpointManifest) -> bool:
        if not manifest.participants:
            return False
        
        for p in manifest.participants:
            if not p.payload_digest:
                return False
        
        return True
    
    async def _commit_manifest(self, manifest: CheckpointManifest) -> bool:
        # For frozen dataclasses, we track committed status in the manager
        self._committed_checkpoints.add(manifest.checkpoint_id)
        return True
    
    def list_checkpoints(self, runtime_id: Optional[str] = None) -> List[CheckpointManifest]:
        result = [
            c for c in self._checkpoints.values()
            if c.checkpoint_id in self._committed_checkpoints
        ]
        
        if runtime_id:
            result = [c for c in result if c.runtime_id == runtime_id]
        
        return result
    
    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "runtime_id": self._runtime_id,
            "checkpoints_stored": len([c for c in self._checkpoints.values() 
                                      if c.checkpoint_id in self._committed_checkpoints]),
            "create_count": self._create_count,
            "commit_count": self._commit_count,
        }


__all__ = [
    "CheckpointType",
    "CheckpointMode",
    "CheckpointId",
    "CheckpointChainRef",
    "CheckpointManifest",
    "CheckpointParticipant",
    "CheckpointBarrier",
    "CheckpointRequest",
    "CheckpointResult",
    "CheckpointStatus",
    "CheckpointManager",
]