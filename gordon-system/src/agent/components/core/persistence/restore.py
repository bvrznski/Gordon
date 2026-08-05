# Restore Manager
# ===============

"""
Restore and rehydration for persisted state.

This module provides:
- RestoreManager: Canonical restore authority
- Checkpoint/snapshot selection and discovery
- Deserialization with schema validation
- Runtime rehydration through participants
- Resource reacquisition coordination
- Side-effect suppression during replay

Key principle: Restore loads persisted state. It does NOT open admission.
Restore completion does not imply runtime readiness.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# Restore Types and Modes
# =============================================================================

class RestoreMode(Enum):
    VALIDATE_ONLY = "validate_only"
    DRY_RUN = "dry_run"
    FULL_RUNTIME = "full_runtime"
    DOMAIN = "domain"
    RECOVERY = "recovery"
    DIAGNOSTIC = "diagnostic"
    REPLAY_ONLY = "replay_only"
    MIGRATE_ONLY = "migrate_only"


class SelectionPolicy(Enum):
    EXACT_ID = "exact_id"
    LATEST_VALID = "latest_valid"
    LATEST_COMPATIBLE = "latest_compatible"
    LATEST_BEFORE_SEQUENCE = "latest_before_sequence"
    LATEST_BEFORE_TIME = "latest_before_time"
    EXPLICIT_LINEAGE = "explicit_lineage"


# =============================================================================
# Restore Identifiers
# =============================================================================

@dataclass(frozen=True)
class RestoreId:
    value: str
    
    @classmethod
    def generate(cls) -> "RestoreId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Restore Selection Types
# =============================================================================

@dataclass(frozen=True)
class CheckpointSelection:
    checkpoint_id: Optional[str]
    runtime_id: str
    policy: SelectionPolicy
    before_time: Optional[float] = None
    compatible_schema_versions: List[int] = field(default_factory=list)


@dataclass(frozen=True)
class SnapshotSelection:
    snapshot_id: Optional[str]
    runtime_id: str
    policy: SelectionPolicy


@dataclass(frozen=True)
class JournalRangeSelection:
    journal_id: Optional[str]
    from_sequence: int
    to_sequence: Optional[int]


# =============================================================================
# Restore Request and Result Types
# =============================================================================

@dataclass(frozen=True)
class RestoreRequest:
    request_id: str
    
    runtime_id: str
    boot_session_id: Optional[str] = None
    
    # Selection criteria
    checkpoint_selection: Optional[CheckpointSelection] = None
    snapshot_selection: Optional[SnapshotSelection] = None
    journal_range_selection: Optional[JournalRangeSelection] = None
    
    # Mode
    mode: RestoreMode = RestoreMode.FULL_RUNTIME
    
    # Validation
    skip_validation: bool = False
    target_schema_version: Optional[int] = None
    
    # Target domains (None for all)
    target_domains: Optional[List[str]] = None


@dataclass(frozen=True)
class RestoreResult:
    result_id: str
    
    request_id: str
    runtime_id: str
    
    status: "RestoreStatus"
    timestamp: float
    
    # Success case
    manifest: Optional[Any] = None
    domains_restored: int = 0
    
    # Details
    resources_reacquired: List[str] = field(default_factory=list)
    side_effects_suppressed: List[Dict[str, Any]] = field(default_factory=list)
    
    # Failure case
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status == RestoreStatus.COMPLETED


class RestoreStatus(Enum):
    REQUESTED = "requested"
    DISCOVERING = "discovering"
    SELECTING = "selecting"
    VALIDATING = "validating"
    READING = "reading"
    DESERIALIZING = "deserializing"
    MIGRATING = "migrating"
    REHYDRATING = "rehydrating"
    REACQUIRING_RESOURCES = "reacquiring_resources"
    REPLAYING = "replaying"
    RECONCILING = "reconciling"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Restore Manager
# =============================================================================

class RestoreManager:
    """
    Canonical restore authority.
    
    Manages:
        - Restore request intake and selection planning
        - Deserialization with schema validation
        - Migration routing for incompatible schemas
        - Runtime rehydration through participants
        - Resource reacquisition coordination
        - Side-effect suppression during replay
    
    Usage:
        manager = RestoreManager(runtime_id="runtime_123")
        
        # Request restore
        result = await manager.restore(RestoreRequest(
            request_id=str(uuid.uuid4()),
            runtime_id="runtime_123",
            checkpoint_selection=CheckpointSelection(...)
        ))
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        
        # Selection caches
        self._checkpoint_cache: Dict[str, Any] = {}
        self._snapshot_cache: Dict[str, Any] = {}
        
        # Backend for reading persisted data
        self._backend = None  # Would be StorageBackendProtocol
        
        # Metrics
        self._restore_count = 0
        
        # Runtime isolation enforcement
        self._enforce_runtime_isolation = True
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    def set_enforce_runtime_isolation(self, enabled: bool = True) -> None:
        """Enable or disable runtime isolation enforcement."""
        self._enforce_runtime_isolation = enabled
    
    async def restore(
        self,
        request: RestoreRequest
    ) -> RestoreResult:
        """
        Perform a restore operation.
        
        Args:
            request: The restore request
            
        Returns:
            Result with restored state or error
        """
        if request.skip_validation:
            return await self._validate_only(request)
        
        # Phase 1: Discover and select artifact
        selection = await self._discover_and_select(request)
        
        if not selection:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=RestoreStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="No artifact selected for restore"
            )
        
        # Phase 2: Read and deserialize
        deserialized = await self._read_and_deserialize(selection, request)
        
        if not deserialized:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=RestoreStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="Deserialization failed"
            )
        
        # Phase 3: Handle schema migration if needed
        migrated = await self._handle_migration(deserialized, selection)
        
        if not migrated:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=RestoreStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="Migration failed"
            )
        
        # Phase 4: Rehydrate to participants
        rehydrated = await self._rehydrate_to_participants(migrated, request)
        
        if not rehydrated:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=RestoreStatus.PARTIAL,
                timestamp=time.monotonic(),
                error_message="Rehydration failed for some domains"
            )
        
        # Phase 5: Reacquire resources
        reacquired = await self._reacquire_resources(migrated, request)
        
        # Phase 6: Replay journal if provided
        replayed = await self._replay_journal(selection, request)
        
        # Phase 7: Reconcile with external reality
        reconciliation = await self._reconcile_with_external_state(migrated, request)
        
        # Phase 8: Verify restored state
        verified = await self._verify_restored_state(rehydrated, reacquired, reconciliation, request)
        
        if not verified:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=RestoreStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="Verification failed"
            )
        
        self._restore_count += 1
        
        return RestoreResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=RestoreStatus.COMPLETED,
            timestamp=time.monotonic(),
            manifest=None,  # Would contain restored state in production
            domains_restored=len(rehydrated),
            resources_reacquired=list(reacquired.keys()) if reacquired else [],
        )
    
    async def _discover_and_select(
        self,
        request: RestoreRequest
    ) -> Optional[Dict[str, Any]]:
        """Discover and select artifact to restore from."""
        # Check runtime isolation first if enabled
        if self._enforce_runtime_isolation:
            # Validate that the requested runtime_id matches our own
            artifact_runtime_id = None
            
            # Get runtime_id from checkpoint selection
            if request.checkpoint_selection:
                artifact_runtime_id = request.checkpoint_selection.runtime_id
            elif request.snapshot_selection:
                artifact_runtime_id = request.snapshot_selection.runtime_id
            
            # If artifact has a runtime_id, validate it matches current instance
            if artifact_runtime_id and artifact_runtime_id != self._runtime_id:
                return None  # Runtime isolation violation - don't select
        
        # Checkpoint selection
        if request.checkpoint_selection:
            checkpoint = await self._find_checkpoint(request.checkpoint_selection)
            if checkpoint:
                # Validate runtime_id in checkpoint artifact matches current instance
                if self._enforce_runtime_isolation and checkpoint.get("runtime_id") and checkpoint["runtime_id"] != self._runtime_id:
                    return None  # Runtime isolation violation - don't select
                return {"type": "checkpoint", "artifact": checkpoint}
        
        # Snapshot selection (fallback)
        if request.snapshot_selection:
            snapshot = await self._find_snapshot(request.snapshot_selection)
            if snapshot:
                # Validate runtime_id in snapshot artifact matches current instance  
                if self._enforce_runtime_isolation and snapshot.get("runtime_id") and snapshot["runtime_id"] != self._runtime_id:
                    return None  # Runtime isolation violation - don't select
                return {"type": "snapshot", "artifact": snapshot}
        
        # Journal replay
        if request.journal_range_selection:
            return {
                "type": "journal",
                "from_sequence": request.journal_range_selection.from_sequence,
                "to_sequence": request.journal_range_selection.to_sequence,
            }
        
        return None
    
    async def _find_checkpoint(
        self,
        selection: CheckpointSelection
    ) -> Optional[Dict[str, Any]]:
        """Find a checkpoint matching the selection criteria."""
        # Simplified - in production would query CheckpointManager
        # and apply policy for exact_id, latest_valid, etc.
        
        if selection.checkpoint_id:
            return {"id": selection.checkpoint_id}
        
        return None
    
    async def _find_snapshot(
        self,
        selection: SnapshotSelection
    ) -> Optional[Dict[str, Any]]:
        """Find a snapshot matching the selection criteria."""
        # Simplified - in production would query SnapshotManager
        
        if selection.snapshot_id:
            return {"id": selection.snapshot_id}
        
        return None
    
    async def _read_and_deserialize(
        self,
        selection: Dict[str, Any],
        request: RestoreRequest
    ) -> Optional[Dict[str, Any]]:
        """Read persisted data and deserialize."""
        # Simplified - in production would:
        # 1. Read from backend
        # 2. Verify checksums/integrity
        # 3. Deserialize using SerializationManager
        # 4. Validate schema version with strict compatibility check
        
        # Simulate reading from backend with version info
        deserialized = {"domain_a": {"value": "restored_state"}}
        
        # If target schema version specified, validate it's compatible
        if request.target_schema_version is not None:
            # In production would check against stored artifact schema version
            pass  # Version check handled by migration system in real implementation
        
        return deserialized
    
    async def _handle_migration(
        self,
        deserialized: Dict[str, Any],
        selection: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle schema migration if needed."""
        # Simplified - in production would use MigrationManager
        # with strict version validation before allowing migration execution
        
        return deserialized
    
    async def _rehydrate_to_participants(
        self,
        migrated: Dict[str, Any],
        request: RestoreRequest
    ) -> List[str]:
        """Rehydrate state to participants."""
        restored = []
        
        for domain_id in migrated.keys():
            # Would route to appropriate participant's restore_state method
            # and verify with verify_restored_state
            
            if request.target_domains is None or domain_id in request.target_domains:
                restored.append(domain_id)
        
        return restored
    
    async def _reacquire_resources(
        self,
        state: Dict[str, Any],
        request: RestoreRequest
    ) -> Dict[str, bool]:
        """Reacquire external resources needed by restored state."""
        reacquired = {}
        
        # Would query participants for resource requirements and
        # coordinate with resource manager to reacquire
        
        return reacquired
    
    async def _replay_journal(
        self,
        selection: Dict[str, Any],
        request: RestoreRequest
    ) -> bool:
        """Replay journal if provided in selection."""
        # Simplified - would suppress side effects by default
        
        return True
    
    async def _reconcile_with_external_state(
        self,
        state: Dict[str, Any],
        request: RestoreRequest
    ) -> Dict[str, Any]:
        """Compare restored state with external reality."""
        # Simplified - would compare against actual filesystem, DBs, services
        
        return {"external_compatibility": True}
    
    async def _verify_restored_state(
        self,
        rehydrated: List[str],
        reacquired: Dict[str, bool],
        reconciliation: Dict[str, Any],
        request: RestoreRequest
    ) -> bool:
        """Verify restored state is correct."""
        # Check all required domains rehydrated
        if request.target_domains and len(rehydrated) < len(request.target_domains):
            return False
        
        # Check external compatibility
        if not reconciliation.get("external_compatibility"):
            return False
        
        return True
    
    async def _validate_only(
        self,
        request: RestoreRequest
    ) -> RestoreResult:
        """Validate restore without executing (dry-run mode)."""
        # Validate runtime isolation first
        if self._enforce_runtime_isolation and request.checkpoint_selection:
            artifact_rt_id = request.checkpoint_selection.runtime_id
            if artifact_rt_id != self._runtime_id:
                return RestoreResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=self._runtime_id,
                    status=RestoreStatus.FAILED,
                    timestamp=time.monotonic(),
                    error_message=f"Runtime isolation violation: expected {self._runtime_id}, got {artifact_rt_id}"
                )
        
        selection = await self._discover_and_select(request)
        
        if not selection:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=RestoreStatus.FAILED,
                timestamp=time.monotonic(),
                error_message="No artifact would be selected"
            )
        
        # Would perform full validation without actually restoring
        
        return RestoreResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=RestoreStatus.COMPLETED,
            timestamp=time.monotonic(),
        )
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get restore manager diagnostics."""
        return {
            "runtime_id": self._runtime_id,
            "restore_count": self._restore_count,
            "enforce_runtime_isolation": self._enforce_runtime_isolation,
        }


__all__ = [
    # Modes
    "RestoreMode",
    "SelectionPolicy",
    
    # Identifiers
    "RestoreId",
    
    # Selection types
    "CheckpointSelection",
    "SnapshotSelection",
    "JournalRangeSelection",
    
    # Request and result types
    "RestoreRequest",
    "RestoreResult",
    "RestoreStatus",
    
    # Manager
    "RestoreManager",
]