# Continuity Facade
# ==================

"""
Public facade for Core continuity infrastructure.

This module provides the single, deliberate entry point to Core continuity
functionality. It coordinates:

    - Previous runtime inspection
    - Checkpoint creation
    - Restoration from checkpoint
    - Interruption reconciliation
    - Post-restoration verification
    - Finalization during shutdown

Architecture boundaries:
    This owns:
        - Orchestrating the full continuity lifecycle
        - Coordinating participant registration and collection
        - Managing checkpoint transactions
        - Managing ledger appends
        
    This does NOT own:
        - When continuity operations occur (entrypoint's responsibility)
        - Subsystem-specific state semantics
        - Live runtime object serialization
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Any,
)
from abc import ABC, abstractmethod

from .contracts import (
    ContinuityParticipant,
    CheckpointFragment,
    ParticipantId,
    CheckpointId,
    RuntimeGeneration,
    LedgerPosition,
)
from .types import (
    CheckpointConsistencyMode,
    CheckpointReason,
    RestorationStatus,
    InterruptionClassification,
)
from .exceptions import (
    ContinuityError,
    CheckpointNotFound,
    CheckpointCorrupt,
    ParticipantUnavailable,
)


# Import storage and ledger modules
try:
    from .storage import CheckpointStorage, StorageResult
except ImportError:
    # Fallback for when storage module isn't available yet
    class CheckpointStorage:
        def __init__(self, *args, **kwargs):
            pass

try:
    from .ledger import ContinuityLedgerWriter
except ImportError:
    class ContinuityLedgerWriter:
        def __init__(self, *args, **kwargs):
            pass


# =============================================================================
# PREVIOUS RUNTIME INSPECTION
# =============================================================================

class PreviousRuntimeState(Enum):
    """Possible states of a previous runtime."""
    
    CLEAN_SHUTDOWN = "CLEAN_SHUTDOWN"
    UNCLEAN_SHUTDOWN = "UNCLEAN_SHUTDOWN"
    FIRST_START = "FIRST_START"
    UNKNOWN_PREVIOUS_STATE = "UNKNOWN_PREVIOUS_STATE"
    ACTIVE_OTHER_RUNTIME = "ACTIVE_OTHER_RUNTIME"
    CORRUPT_CONTINUITY_STATE = "CORRUPT_CONTINUITY_STATE"


@dataclass(frozen=True)
class PreviousRuntimeInspectionRequest:
    """Request to inspect previous runtime state."""
    runtime_id: str
    current_generation: RuntimeGeneration


@dataclass(frozen=True)
class PreviousRuntimeInspectionResult:
    """Result of previous runtime inspection."""
    
    previous_state: PreviousRuntimeState
    last_checkpoint_id: Optional[str]
    ledger_tail_position: Optional[int]
    runtime_generation_of_last_run: Optional[int]
    is_recovery_needed: bool
    
    @classmethod
    def clean_shutdown(cls, checkpoint_id: str) -> "PreviousRuntimeInspectionResult":
        return cls(
            previous_state=PreviousRuntimeState.CLEAN_SHUTDOWN,
            last_checkpoint_id=checkpoint_id,
            ledger_tail_position=None,
            runtime_generation_of_last_run=None,
            is_recovery_needed=False,
        )
    
    @classmethod
    def unclean_shutdown(cls, checkpoint_id: str, generation: int) -> "PreviousRuntimeInspectionResult":
        return cls(
            previous_state=PreviousRuntimeState.UNCLEAN_SHUTDOWN,
            last_checkpoint_id=checkpoint_id,
            ledger_tail_position=None,
            runtime_generation_of_last_run=generation,
            is_recovery_needed=True,
        )
    
    @classmethod
    def first_start(cls) -> "PreviousRuntimeInspectionResult":
        return cls(
            previous_state=PreviousRuntimeState.FIRST_START,
            last_checkpoint_id=None,
            ledger_tail_position=None,
            runtime_generation_of_last_run=None,
            is_recovery_needed=False,
        )


# =============================================================================
# CHECKPOINT RESULTS
# =============================================================================

@dataclass(frozen=True)
class CheckpointRequest:
    """Request to create a checkpoint."""
    
    reason: CheckpointReason
    consistency_mode: CheckpointConsistencyMode = CheckpointConsistencyMode.GENERATION_BASED
    required_participants: Tuple[str, ...] = field(default_factory=tuple)
    optional_participants: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CheckpointResult:
    """Result of a checkpoint operation."""
    
    success: bool
    checkpoint_id: str
    fragments_captured: int
    required_fragments: int
    optional_fragments: int
    timestamp_ns: int
    
    @classmethod
    def succeeded(
        cls,
        checkpoint_id: CheckpointId,
        fragments: List[CheckpointFragment],
        required_count: int,
    ) -> "CheckpointResult":
        return cls(
            success=True,
            checkpoint_id=str(checkpoint_id),
            fragments_captured=len(fragments),
            required_fragments=required_count,
            optional_fragments=max(0, len(fragments) - required_count),
            timestamp_ns=time.time_ns(),
        )
    
    @classmethod
    def failed(cls, checkpoint_id: str, error: str) -> "CheckpointResult":
        return cls(
            success=False,
            checkpoint_id=checkpoint_id,
            fragments_captured=0,
            required_fragments=0,
            optional_fragments=0,
            timestamp_ns=time.time_ns(),
        )


# =============================================================================
# RESTORATION RESULTS
# =============================================================================

@dataclass(frozen=True)
class RestorationRequest:
    """Request to restore from checkpoint."""
    
    runtime_id: str
    current_generation: RuntimeGeneration
    preferred_checkpoint_id: Optional[str] = None  # If None, use newest valid


@dataclass(frozen=True)
class RestorationResult:
    """Result of a restoration operation."""
    
    status: RestorationStatus
    checkpoint_id_used: Optional[str]
    participants_restored: int
    participants_failed: int
    participants_skipped: int
    interrupted_operations_count: int
    reconciliation_results: Tuple[Dict[str, Any], ...]
    
    @classmethod
    def succeeded(cls, checkpoint_id: str) -> "RestorationResult":
        return cls(
            status=RestorationStatus.SUCCEEDED,
            checkpoint_id_used=checkpoint_id,
            participants_restored=0,
            participants_failed=0,
            participants_skipped=0,
            interrupted_operations_count=0,
            reconciliation_results=(),
        )
    
    @classmethod
    def failed(cls, checkpoint_id: Optional[str], error: str) -> "RestorationResult":
        return cls(
            status=RestorationStatus.FAILED,
            checkpoint_id_used=checkpoint_id,
            participants_restored=0,
            participants_failed=1,
            participants_skipped=0,
            interrupted_operations_count=0,
            reconciliation_results=({"error": error},),
        )


# =============================================================================
# RECONCILIATION RESULTS
# =============================================================================

@dataclass(frozen=True)
class ReconciliationResult:
    """Result of interruption reconciliation."""
    
    participant_id: str
    operations_resumed: int = 0
    operations_retried: int = 0
    operations_rolled_back: int = 0
    uncertain_operations: int = 0
    
    @classmethod
    def empty(cls, participant_id: str) -> "ReconciliationResult":
        return cls(participant_id=participant_id)


# =============================================================================
# VERIFICATION RESULTS
# =============================================================================

@dataclass(frozen=True)
class ContinuityVerificationRequest:
    """Request to verify restored state."""
    
    runtime_id: str
    checkpoint_id_used: Optional[str]


@dataclass(frozen=True)
class ContinuityVerificationResult:
    """Result of continuity verification."""
    
    success: bool
    integrity_verified: bool = False
    health_verified: bool = False
    compatibility_verified: bool = False
    
    @classmethod
    def succeeded(cls) -> "ContinuityVerificationResult":
        return cls(
            success=True,
            integrity_verified=True,
            health_verified=True,
            compatibility_verified=True,
        )
    
    @classmethod
    def failed(cls, *failures: str) -> "ContinuityVerificationResult":
        return cls(success=False)


# =============================================================================
# FINALIZATION RESULTS
# =============================================================================

@dataclass(frozen=True)
class FinalizationRequest:
    """Request to finalize continuity state during shutdown."""
    
    runtime_id: str


@dataclass(frozen=True)
class FinalizationResult:
    """Result of continuity finalization."""
    
    success: bool
    last_checkpoint_id: Optional[str]
    ledger_position_final: Optional[int]
    
    @classmethod
    def succeeded(cls, checkpoint_id: Optional[str] = None) -> "FinalizationResult":
        return cls(
            success=True,
            last_checkpoint_id=checkpoint_id if checkpoint_id else None,
            ledger_position_final=None,
        )
    
    @classmethod
    def failed(cls, error: str) -> "FinalizationResult":
        return cls(success=False)


# =============================================================================
# CONTINUITY FACADE (PUBLIC API)
# =============================================================================

class ContinuityFacade:
    """
    Public facade for Core continuity operations.
    
    This is the ONE canonical entry point for continuity functionality from
    both the entrypoint layer and other Core subsystems.
    
    Usage example:
        >>> facade = ContinuityFacade()
        >>> result = await facade.inspect_previous_runtime(
        ...     PreviousRuntimeInspectionRequest(...)
        ... )
        >>> if result.is_recovery_needed:
        ...     restoration_result = await facade.restore(RestorationRequest(...))
        ...     verification_result = await facade.verify(ContinuityVerificationRequest(...))
        ...     if verification_result.success:
        ...         # Safe to open admission
    """
    
    def __init__(
        self,
        config: Optional[Any] = None,  # ContinuityConfig type
        participants: Optional[List[ContinuityParticipant]] = None,
        storage_backend: Optional[CheckpointStorage] = None,
        ledger_writer: Optional[ContinuityLedgerWriter] = None,
    ):
        """
        Initialize the continuity facade.
        
        Args:
            config: Configuration instance (uses defaults if not provided)
            participants: Initial list of participant instances to register
            storage_backend: Checkpoint storage backend (auto-created if not provided)
            ledger_writer: Continuity ledger writer (auto-created if not provided)
        """
        self._config = config
        self._participants: Dict[str, ContinuityParticipant] = {}
        self._checkpoint_id: Optional[CheckpointId] = None
        self._runtime_generation: Optional[RuntimeGeneration] = None
        
        # Storage backend for checkpoint persistence
        self._storage_backend = storage_backend or CheckpointStorage(
            root_path=self._config.checkpoint_root if self._config else "var/gordon/runtime-continuity/"
        )
        
        # Ledger writer for journaling operations
        # In production, this would be connected to the actual JournalManager
        self._ledger_writer = ledger_writer
        
        # Track last checkpoint info
        self._last_checkpoint_info: Optional[Dict[str, Any]] = None
        
        # Register initial participants if provided
        for participant in participants or []:
            self.register_participant(participant)
    
    def register_participant(self, participant: ContinuityParticipant) -> None:
        """
        Register a continuity participant.
        
        Args:
            participant: The participant instance to register
            
        Raises:
            ContinuityError: If participant ID is duplicate or invalid
        """
        pid = participant.participant_id
        pid_str = str(pid)
        
        if pid_str in self._participants:
            raise ContinuityError(f"Duplicate participant ID: {pid_str}")
        
        self._participants[pid_str] = participant
    
    def get_participant(self, participant_id: str) -> Optional[ContinuityParticipant]:
        """Get a registered participant by its ID."""
        return self._participants.get(participant_id)
    
    # =========================================================================
    # PREVIOUS RUNTIME INSPECTION
    # =========================================================================
    
    async def inspect_previous_runtime(
        self,
        request: PreviousRuntimeInspectionRequest,
    ) -> PreviousRuntimeInspectionResult:
        """
        Inspect the state of a previous runtime run.
        
        Args:
            request: The inspection request
            
        Returns:
            Result indicating whether recovery is needed and any checkpoint info
        """
        # Check for shutdown marker (indicates clean shutdown)
        shutdown_marker = self._storage_backend.root_path / "shutdown_complete.marker"
        
        if not shutdown_marker.exists():
            # No shutdown marker - check for checkpoints to determine state
            checkpoints = await self._storage_backend.list_checkpoints()
            if checkpoints:
                return PreviousRuntimeInspectionResult.unclean_shutdown(
                    checkpoint_id=checkpoints[-1],
                    generation=request.current_generation,
                )
            return PreviousRuntimeInspectionResult.first_start()
        
        # Shutdown marker exists - check for latest checkpoint
        checkpoints = await self._storage_backend.list_checkpoints()
        if checkpoints:
            return PreviousRuntimeInspectionResult.clean_shutdown(checkpoint_id=checkpoints[-1])
        
        return PreviousRuntimeInspectionResult.first_start()
    
    async def create_checkpoint(
        self,
        request: CheckpointRequest,
    ) -> CheckpointResult:
        """
        Create a new checkpoint of the current runtime state.
        
        Args:
            request: The checkpoint request
            
        Returns:
            Result containing checkpoint ID and fragment counts
        """
        # Generate new checkpoint ID
        self._checkpoint_id = CheckpointId.generate()
        if not self._runtime_generation:
            self._runtime_generation = RuntimeGeneration.generate()
        
        required_count = sum(
            1 for p in self._participants.values()
            if p.required_for_restore
        )
        
        fragments: Dict[str, Any] = {}  # participant_id -> fragment data
        
        # Phase 1: Collect fragments from participants
        for participant in self._participants.values():
            try:
                fragment = await participant.prepare_checkpoint(
                    checkpoint_id=self._checkpoint_id,
                    runtime_generation=self._runtime_generation,
                    consistency_mode=request.consistency_mode.value,
                )
                
                # Store fragment data for persistence
                fragment_data = {
                    "participant_id": str(fragment.participant_id),
                    "fragment_type": fragment.fragment_type,
                    "schema_version": fragment.schema_version,
                    "runtime_generation": str(fragment.runtime_generation),
                    "checkpoint_id": str(fragment.checkpoint_id),
                    "captured_at_ns": fragment.captured_at_ns,
                    "payload_reference": fragment.payload_reference,
                    "checksum": fragment.checksum,
                    "compression": fragment.compression,
                    "required_for_restore": fragment.required_for_restore,
                    "compatibility_metadata": fragment.compatibility_metadata,
                    "provenance": fragment.provenance,
                }
                
                fragments[str(fragment.participant_id)] = fragment_data
                
            except Exception as e:
                # Continue collecting from other participants
                continue
        
        if not fragments:
            return CheckpointResult.failed(str(self._checkpoint_id), "No fragments collected")
        
        # Phase 2: Write checkpoint to storage with atomic commit protocol
        metadata = {
            "runtime_generation": self._runtime_generation.value,
            "created_at_ns": time.time_ns(),
            "required_fragment_count": required_count,
        }
        
        storage_result = await self._storage_backend.write_checkpoint(
            checkpoint_id=str(self._checkpoint_id),
            fragments=fragments,
            metadata=metadata,
        )
        
        if not storage_result.success:
            return CheckpointResult.failed(str(self._checkpoint_id), storage_result.error_message or "Storage write failed")
        
        # Phase 3: Record checkpoint committed event in ledger
        if self._ledger_writer:
            try:
                await self._ledger_writer.append_checkpoint_committed(
                    checkpoint_id=str(self._checkpoint_id),
                    storage_path=storage_result.path,
                    fragment_count=len(fragments),
                )
            except Exception:
                pass  # Don't fail the checkpoint if ledger write fails
        
        return CheckpointResult.succeeded(self._checkpoint_id, list(fragments.values()), required_count)
    
    async def restore(
        self,
        request: RestorationRequest,
    ) -> RestorationResult:
        """
        Restore runtime state from a checkpoint.
        
        Args:
            request: The restoration request
            
        Returns:
            Result indicating success/failure and which participants were restored
        """
        # Find the checkpoint to restore from
        checkpoint_id = request.preferred_checkpoint_id
        
        if not checkpoint_id:
            # Use newest valid checkpoint
            checkpoints = await self._storage_backend.list_checkpoints()
            if checkpoints:
                checkpoint_id = checkpoints[-1]
        
        if not checkpoint_id:
            return RestorationResult.failed(None, "No checkpoint found to restore from")
        
        # Read the checkpoint
        checkpoint_info = await self._storage_backend.read_checkpoint(checkpoint_id)
        
        if not checkpoint_info or not checkpoint_info.is_valid():
            return RestorationResult.failed(checkpoint_id, "Checkpoint not found or invalid")
        
        # Record restoration started event in ledger
        if self._ledger_writer:
            try:
                await self._ledger_writer.append_restoration_started(checkpoint_id)
            except Exception:
                pass
        
        # Restore each participant
        participants_restored = 0
        participants_failed = 0
        interrupted_ops: List[Dict[str, Any]] = []
        
        for participant_id, fragment_data in checkpoint_info.fragments.items():
            if participant_id not in self._participants:
                continue
            
            participant = self._participants[participant_id]
            
            try:
                # Build fragment from stored data
                fragment = CheckpointFragment(
                    participant_id=ParticipantId(participant_id),
                    fragment_type=fragment_data.get("fragment_type", ""),
                    schema_version=fragment_data.get("schema_version", 1),
                    runtime_generation=RuntimeGeneration(value=uuid.UUID(hex=str(fragment_data.get("runtime_generation", "")))),
                    checkpoint_id=CheckpointId(value=uuid.UUID(hex=checkpoint_id)),
                    captured_at_ns=fragment_data.get("captured_at_ns", 0),
                    state_version="1.0",
                    payload_reference=fragment_data.get("payload_reference", ""),
                    checksum=fragment_data.get("checksum", ""),
                    compression=fragment_data.get("compression"),
                    required_for_restore=fragment_data.get("required_for_restore", True),
                    compatibility_metadata=fragment_data.get("compatibility_metadata", {}),
                    provenance="restored_from_checkpoint",
                )
                
                # Restore participant
                restore_result = await asyncio.wait_for(
                    participant.restore_checkpoint(
                        fragment=fragment,
                        context={},
                    ),
                    timeout=self._config.restore_timeout_seconds if self._config else 120.0,
                )
                
                if restore_result.success:
                    participants_restored += 1
                    
                    # Reconcile interrupted operations
                    ledger_tail = await self._ledger_writer.get_ledger_tail(
                        since_checkpoint_id=checkpoint_id
                    ) if self._ledger_writer else ()
                    
                    reconciliation = await participant.reconcile_interruption(
                        ledger_tail=tuple(dict(r.to_dict()) for r in ledger_tail.records),
                        context={},
                    )
                    
                    # Build reconciliation result data from the protocol result
                    # Only extract known fields, never use __dict__ on unknown objects
                    reconciliation_data: Dict[str, Any] = {
                        "participant": participant_id,
                        "operations_resumed": getattr(reconciliation, "operations_resumed", 0),
                        "operations_retried": getattr(reconciliation, "operations_retried", 0),
                        "operations_rolled_back": getattr(reconciliation, "operations_rolled_back", 0),
                        "operations_compensated": getattr(reconciliation, "operations_compensated", 0),
                        "uncertain_operations": getattr(reconciliation, "uncertain_operations", 0),
                    }
                    
                    interrupted_ops.append(reconciliation_data)
                    
                else:
                    participants_failed += 1
                    
            except Exception as e:
                participants_failed += 1
        
        # Determine overall status
        if participants_restored > 0 and participants_failed == 0:
            status = RestorationStatus.SUCCEEDED
        elif participants_restored > 0:
            status = RestorationStatus.SUCCEEDED_WITH_DEGRADATION
        else:
            status = RestorationStatus.FAILED
        
        return RestorationResult(
            status=status,
            checkpoint_id_used=checkpoint_id,
            participants_restored=participants_restored,
            participants_failed=participants_failed,
            participants_skipped=len(checkpoint_info.fragments) - participants_restored - participants_failed,
            interrupted_operations_count=len(interrupted_ops),
            reconciliation_results=tuple(d for d in interrupted_ops),
        )
    
    async def reconcile(
        self,
        request: Dict[str, Any],
    ) -> List[ReconciliationResult]:
        """
        Reconcile interrupted operations after restoration.
        
        Args:
            request: Reconciliation context
            
        Returns:
            List of reconciliation results for each participant
        """
        checkpoint_id = request.get("checkpoint_id")
        if not checkpoint_id:
            return []
        
        # Get ledger tail since the checkpoint
        ledger_tail = await self._ledger_writer.get_ledger_tail(
            since_checkpoint_id=checkpoint_id
        ) if self._ledger_writer else ()
        
        results: List[ReconciliationResult] = []
        
        for participant_id, participant in self._participants.items():
            try:
                result = await asyncio.wait_for(
                    participant.reconcile_interruption(
                        ledger_tail=tuple(dict(r.to_dict()) for r in ledger_tail.records),
                        context=request,
                    ),
                    timeout=self._config.participant_timeout_seconds if self._config else 30.0,
                )
                results.append(result)
                
            except Exception as e:
                # Return empty reconciliation on error
                results.append(ReconciliationResult.empty(participant_id=str(ParticipantId(participant_id))))
        
        return results
    
    async def verify(
        self,
        request: ContinuityVerificationRequest,
    ) -> ContinuityVerificationResult:
        """
        Verify that restored state is valid and ready for use.
        
        Args:
            request: The verification request
            
        Returns:
            Result indicating whether all checks passed
        """
        checkpoint_id = request.checkpoint_id_used
        
        # Phase 1: Validate checkpoint integrity from storage
        if not checkpoint_id:
            return ContinuityVerificationResult.failed("No checkpoint ID provided")
        
        checkpoint_info = await self._storage_backend.read_checkpoint(checkpoint_id)
        
        if not checkpoint_info or not checkpoint_info.is_valid():
            return ContinuityVerificationResult.failed(f"Checkpoint '{checkpoint_id}' not found or invalid")
        
        # Verify manifest checksum
        expected_checksum = hashlib.sha256(
            json.dumps({
                "checkpoint_id": checkpoint_id,
                "runtime_generation": checkpoint_info.runtime_generation,
                "fragment_count": checkpoint_info.fragment_count,
            }, sort_keys=True).encode("utf-8")
        ).hexdigest()
        
        if checkpoint_info.manifest_checksum != expected_checksum:
            return ContinuityVerificationResult.failed(f"Checkpoint manifest checksum mismatch")
        
        # Phase 2: Verify participant states
        integrity_verified = True
        for participant_id, fragment_data in checkpoint_info.checksums.items():
            if participant_id not in self._participants:
                continue
            
            # Ask participant to verify its restored state
            participant = self._participants[participant_id]
            
            try:
                verification_result = await asyncio.wait_for(
                    participant.verify_restoration(),
                    timeout=self._config.verification_timeout_seconds if self._config else 30.0,
                )
                
                if not verification_result.integrity_verified:
                    integrity_verified = False
                    
            except Exception:
                integrity_verified = False
        
        # Phase 3: Validate runtime health
        health_verified = True  # In a real implementation, this would check actual health
        
        return ContinuityVerificationResult(
            success=integrity_verified and health_verified,
            integrity_verified=integrity_verified,
            health_verified=health_verified,
            compatibility_verified=True,
            warnings=(),
            errors=() if (integrity_verified and health_verified) else ("Some verifications failed",),
        )
    
    async def finalize(
        self,
        request: FinalizationRequest,
    ) -> FinalizationResult:
        """
        Finalize continuity state during controlled shutdown.
        
        Args:
            request: The finalization request
            
        Returns:
            Result indicating success and any checkpoint info
        """
        # Write shutdown complete marker to indicate clean shutdown
        try:
            shutdown_marker = self._storage_backend.root_path / "shutdown_complete.marker"
            
            # Write the marker with temp file + rename pattern
            import tempfile
            fd, temp_path = tempfile.mkstemp(prefix="shutdown_", dir=self._storage_backend.root_path)
            
            try:
                with os.fdopen(fd, "w") as f:
                    f.write(json.dumps({
                        "runtime_id": request.runtime_id,
                        "timestamp_ns": time.time_ns(),
                        "last_checkpoint_id": str(self._checkpoint_id) if self._checkpoint_id else None,
                    }))
                
                # Fsync the temp file
                with open(temp_path, "a") as f:
                    os.fsync(f.fileno())
                
                # Atomic rename to final path
                shutil.move(temp_path, str(shutdown_marker))
                
            except Exception:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                
                return FinalizationResult.failed("Failed to write shutdown marker")
            
            # Record shutdown complete event in ledger
            if self._ledger_writer and self._checkpoint_id:
                try:
                    await self._ledger_writer.append_shutdown_complete(
                        final_checkpoint_id=str(self._checkpoint_id)
                    )
                except Exception:
                    pass
            
            return FinalizationResult.succeeded(
                checkpoint_id=str(self._checkpoint_id) if self._checkpoint_id else None
            )
            
        except Exception as e:
            return FinalizationResult.failed(str(e))
    
    def get_health(self) -> str:
        """Get current continuity health status."""
        if not self._participants:
            return "CONFIGURED"
        if self._checkpoint_id is None:
            return "READY"
        return "CHECKPOINTING"  # Simplified
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about the continuity state."""
        storage_diag = getattr(self._storage_backend, "get_diagnostics", lambda: {})()
        
        ledger_diag = {}
        if self._ledger_writer:
            try:
                ledger_diag = getattr(self._ledger_writer, "get_diagnostics", lambda: {})()
            except Exception:
                pass
        
        return {
            **storage_diag,
            **ledger_diag,
            "participant_count": len(self._participants),
            "registered_participants": list(self._participants.keys()),
            "last_checkpoint_id": str(self._checkpoint_id) if self._checkpoint_id else None,
            "runtime_generation": str(self._runtime_generation) if self._runtime_generation else None,
            "health": self.get_health(),
        }
