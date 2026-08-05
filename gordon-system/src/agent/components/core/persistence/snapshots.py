# Snapshot Manager
# ================

"""
Snapshot capture, storage, and management.

This module provides:
- SnapshotManager: Canonical snapshot authority
- Full and incremental snapshot support
- Manifest generation and validation
- Snapshot retention and discovery
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import uuid
import time


class SnapshotType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIAGNOSTIC = "diagnostic"
    DOMAIN = "domain"


class SnapshotMode(Enum):
    QUIESCENT = "quiescent"
    VERSIONED = "versioned"
    COPY_ON_WRITE = "copy_on_write"
    INCREMENTAL = "incremental"
    BEST_EFFORT_DIAGNOSTIC = "best_effort_diagnostic"


@dataclass(frozen=True)
class SnapshotId:
    value: str
    
    @classmethod
    def generate(cls) -> "SnapshotId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ParentSnapshotRef:
    snapshot_id: SnapshotId
    digest: str


@dataclass(frozen=True)
class SnapshotSection:
    section_id: str
    domain_id: str
    schema_version: int
    storage_key: str
    content_digest: str
    size_bytes: int = 0
    compression: Optional[str] = None
    encrypted: bool = False
    state_version: int = 0
    participant_count: int = 0


@dataclass(frozen=True)
class SnapshotRequest:
    request_id: str
    runtime_id: str
    domains: List[str]
    
    snapshot_type: SnapshotType = SnapshotType.FULL
    mode: SnapshotMode = SnapshotMode.VERSIONED
    
    boot_session_id: Optional[str] = None
    parent_snapshot_id: Optional[SnapshotId] = None
    requires_integrity: bool = True
    quiesce_timeout_seconds: float = 5.0


@dataclass(frozen=True)
class SnapshotResult:
    result_id: str
    request_id: str
    runtime_id: str
    
    status: "SnapshotStatus"
    timestamp: float = field(default_factory=time.monotonic)
    manifest: Optional["SnapshotManifest"] = None
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status == SnapshotStatus.CREATED


@dataclass(frozen=True)
class SnapshotManifest:
    snapshot_id: SnapshotId
    runtime_id: str
    boot_session_id: Optional[str]
    
    snapshot_type: SnapshotType
    capture_mode: SnapshotMode
    
    parent_snapshot_id: Optional[SnapshotId] = None
    chain_depth: int = 0
    
    created_at: float = field(default_factory=time.monotonic)
    
    runtime_state_version: int = 0
    configuration_version: Optional[int] = None
    
    sections: List[SnapshotSection] = field(default_factory=list)
    
    integrity_hash: str = ""
    restorable: bool = False
    creator_id: Optional[str] = None


class SnapshotStatus(Enum):
    REQUESTED = "requested"
    VALIDATING = "validating"
    CAPTURING = "capturing"
    SERIALIZING = "serializing"
    WRITING = "writing"
    VALIDATING_INTEGRITY = "validating_integrity"
    CREATED = "created"
    FAILED = "failed"
    PARTIAL = "partial"


class SnapshotManager:
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        self._snapshots: Dict[SnapshotId, SnapshotManifest] = {}
        self._backend = None
        self._create_count = 0
        self._restore_count = 0
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    async def create_snapshot(
        self,
        request: SnapshotRequest
    ) -> SnapshotResult:
        if not self._validate_snapshot_request(request):
            return SnapshotResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=SnapshotStatus.FAILED,
            )
        
        snapshot_type = request.snapshot_type
        
        if snapshot_type == SnapshotType.INCREMENTAL:
            if not request.parent_snapshot_id:
                return SnapshotResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=self._runtime_id,
                    status=SnapshotStatus.FAILED,
                    error_message="Incremental requires parent"
                )
            
            if request.parent_snapshot_id not in self._snapshots:
                return SnapshotResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=self._runtime_id,
                    status=SnapshotStatus.FAILED,
                    error_message="Parent snapshot not found"
                )
        
        plan = self._create_snapshot_plan(request)
        if not plan:
            return SnapshotResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=SnapshotStatus.FAILED,
                error_message="No capture plan created"
            )
        
        captured = await self._execute_capture(plan, request)
        
        if not captured:
            return SnapshotResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=SnapshotStatus.FAILED,
                error_message="Capture failed"
            )
        
        manifest = self._create_manifest(request, captured)
        
        if not self._validate_snapshot_integrity(manifest):
            return SnapshotResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=SnapshotStatus.PARTIAL,
                error_message="Integrity validation failed"
            )
        
        self._snapshots[manifest.snapshot_id] = manifest
        self._create_count += 1
        
        return SnapshotResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=SnapshotStatus.CREATED,
            manifest=manifest
        )
    
    async def find_snapshot(
        self,
        snapshot_id: Optional[SnapshotId] = None,
        runtime_id: Optional[str] = None,
        before_time: Optional[float] = None,
    ) -> Optional[SnapshotManifest]:
        if snapshot_id:
            return self._snapshots.get(snapshot_id)
        
        candidates = list(self._snapshots.values())
        
        if runtime_id:
            candidates = [s for s in candidates if s.runtime_id == runtime_id]
        
        if before_time:
            candidates = [s for s in candidates if s.created_at < before_time]
        
        if candidates:
            return max(candidates, key=lambda s: s.created_at)
        
        return None
    
    def _validate_snapshot_request(self, request: SnapshotRequest) -> bool:
        if request.runtime_id != self._runtime_id:
            return False
        
        if request.mode == SnapshotMode.QUIESCENT and request.quiesce_timeout_seconds <= 0:
            return False
        
        return True
    
    def _create_snapshot_plan(self, request: SnapshotRequest) -> Optional[Dict[str, Any]]:
        if not request.domains:
            return None
        
        return {
            "runtime_id": request.runtime_id,
            "domains": request.domains,
            "mode": request.mode.value,
            "snapshot_type": request.snapshot_type.value,
        }
    
    async def _execute_capture(
        self,
        plan: Dict[str, Any],
        request: SnapshotRequest
    ) -> Optional[List[Dict[str, Any]]]:
        return []
    
    def _create_manifest(
        self,
        request: SnapshotRequest,
        captured: List[Dict[str, Any]]
    ) -> SnapshotManifest:
        sections = [
            SnapshotSection(
                section_id=str(uuid.uuid4()),
                domain_id=item.get("domain_id", "unknown"),
                schema_version=1,
                storage_key="",
                content_digest="",
                state_version=0,
                participant_count=1,
            )
            for item in captured
        ]
        
        return SnapshotManifest(
            snapshot_id=SnapshotId.generate(),
            runtime_id=request.runtime_id,
            boot_session_id=request.boot_session_id,
            snapshot_type=request.snapshot_type,
            capture_mode=request.mode,
            parent_snapshot_id=request.parent_snapshot_id,
            sections=sections,
            created_at=time.monotonic(),
            restorable=False,
        )
    
    def _validate_snapshot_integrity(self, manifest: SnapshotManifest) -> bool:
        if not manifest.sections:
            return False
        return True
    
    def list_snapshots(self, runtime_id: Optional[str] = None) -> List[SnapshotManifest]:
        result = list(self._snapshots.values())
        
        if runtime_id:
            result = [s for s in result if s.runtime_id == runtime_id]
        
        return result
    
    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "runtime_id": self._runtime_id,
            "snapshots_stored": len(self._snapshots),
            "create_count": self._create_count,
            "restore_count": self._restore_count,
        }


__all__ = [
    "SnapshotType",
    "SnapshotMode",
    "SnapshotId",
    "ParentSnapshotRef",
    "SnapshotSection",
    "SnapshotRequest",
    "SnapshotResult",
    "SnapshotManifest",
    "SnapshotStatus",
    "SnapshotManager",
]