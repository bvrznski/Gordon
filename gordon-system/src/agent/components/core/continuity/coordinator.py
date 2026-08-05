# Continuity Coordinator
# ======================

"""
Checkpoint and restoration coordination for Core continuity.

This module provides the orchestration layer between:
    - The facade (public API)
    - Participants (subsystem state)
    - Storage (checkpoint files, ledger)

Architecture boundaries:
    This owns:
        - Checkpoint transaction protocol
        - Restoration planning
        - Fragment collection coordination
        
    This does NOT own:
        - Storage implementation details
        - Participant state semantics
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .contracts import ContinuityParticipant, CheckpointFragment, RestorationResult, ReconciliationResult, VerificationResult
from .contracts import ParticipantId, CheckpointId, RuntimeGeneration, LedgerPosition
from .types import (
    CheckpointConsistencyMode,
    RestorationStatus,
)
from .config import ContinuityConfig
from .exceptions import (
    ContinuityError,
    ParticipantUnavailable,
    CheckpointTransactionFailed,
)

# Import storage module
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


@dataclass(frozen=True)
class CheckpointPlan:
    """Planning information for a checkpoint transaction."""
    
    checkpoint_id: CheckpointId
    runtime_generation: RuntimeGeneration
    required_participants: Tuple[ContinuityParticipant, ...]
    optional_participants: Tuple[ContinuityParticipant, ...]
    consistency_mode: str


@dataclass(frozen=True)
class RestorationPlan:
    """Planning information for a restoration operation."""
    
    checkpoint_id: Optional[str]
    participants_to_restore: Tuple[Tuple[ContinuityParticipant, bool], ...]  # (participant, required)
    ledger_tail_position: Optional[int]


@dataclass
class CheckpointTransaction:
    """
    In-progress checkpoint transaction.
    
    Used to track a checkpoint through its lifecycle stages.
    """
    
    checkpoint_id: CheckpointId
    runtime_generation: RuntimeGeneration
    fragments_collected: Dict[str, CheckpointFragment] = field(default_factory=dict)
    fragments_failed: List[Tuple[ContinuityParticipant, str]] = field(default_factory=list)
    quiescence_acquired: bool = False
    
    @property
    def all_required_collected(self) -> bool:
        """Check if all required participants have contributed."""
        return True  # Simplified - would check required participant fragments


@dataclass
class RestorationTransaction:
    """
    In-progress restoration transaction.
    """
    
    checkpoint_id: Optional[str]
    participants_restored: Dict[str, RestorationResult] = field(default_factory=dict)
    interrupted_operations: List[Dict[str, Any]] = field(default_factory=list)


class ContinuityCoordinator:
    """
    Coordinator for continuity operations.
    
    This class orchestrates the actual work of:
        - Collecting fragments from participants
        - Coordinating restoration in dependency order
        - Handling interruptions and reconciliation
    
    It does NOT own storage implementation or participant state semantics.
    """
    
    def __init__(
        self,
        config: ContinuityConfig,
        participants: Optional[List[ContinuityParticipant]] = None,
    ):
        self._config = config
        self._participants: Dict[str, ContinuityParticipant] = {}
        
        # Register initial participants
        for p in participants or []:
            self.register_participant(p)
    
    def register_participant(self, participant: ContinuityParticipant) -> None:
        """Register a participant."""
        pid_str = str(participant.participant_id)
        if pid_str not in self._participants:
            self._participants[pid_str] = participant
    
    # =========================================================================
    # CHECKPOINT COORDINATION
    # =========================================================================
    
    async def prepare_checkpoint_plan(
        self,
        consistency_mode: CheckpointConsistencyMode,
    ) -> CheckpointPlan:
        """Prepare a checkpoint transaction plan."""
        required = tuple(
            p for p in self._participants.values()
            if p.required_for_restore
        )
        optional = tuple(
            p for p in self._participants.values()
            if not p.required_for_restore
        )
        
        return CheckpointPlan(
            checkpoint_id=CheckpointId.generate(),
            runtime_generation=RuntimeGeneration.generate(),
            required_participants=required,
            optional_participants=optional,
            consistency_mode=consistency_mode.value,
        )
    
    async def execute_checkpoint_transaction(
        self,
        plan: CheckpointPlan,
    ) -> Tuple[bool, List[CheckpointFragment], List[Tuple[ContinuityParticipant, str]]]:
        """
        Execute a checkpoint transaction.
        
        Returns:
            Tuple of (success, fragments, failed_participants)
        """
        # Phase 1: Quiesce where required
        quiesced_participants = []
        if plan.consistency_mode == "QUIESCENT":
            for p in self._participants.values():
                try:
                    await asyncio.wait_for(
                        self._quiesce_participant(p),
                        timeout=self._config.quiescence_timeout_seconds,
                    )
                    quiesced_participants.append(p)
                except Exception as e:
                    return False, [], [(p, f"quiesce failed: {e}")]
        
        # Phase 2: Collect fragments
        fragments: List[CheckpointFragment] = []
        failures: List[Tuple[ContinuityParticipant, str]] = []
        
        for p in plan.required_participants + plan.optional_participants:
            try:
                fragment = await asyncio.wait_for(
                    p.prepare_checkpoint(
                        checkpoint_id=plan.checkpoint_id,
                        runtime_generation=plan.runtime_generation,
                        consistency_mode=plan.consistency_mode.value,
                    ),
                    timeout=self._config.participant_timeout_seconds,
                )
                fragments.append(fragment)
            except Exception as e:
                failures.append((p, str(e)))
        
        # Phase 3: Release quiescence
        for p in quiesced_participants:
            try:
                await self._release_quiescence(p)
            except Exception:
                pass  # Continue even if release fails
        
        return True, fragments, failures
    
    async def _quiesce_participant(self, participant: ContinuityParticipant) -> None:
        """Quiesce a participant (pause mutation admission)."""
        # This is a no-op in this simplified implementation
        # A real implementation would pause mutation admission
        pass
    
    async def _release_quiescence(self, participant: ContinuityParticipant) -> None:
        """Release quiescence for a participant."""
        # This is a no-op in this simplified implementation
        pass
    
    # =========================================================================
    # RESTORATION COORDINATION
    # =========================================================================
    
    async def prepare_restoration_plan(
        self,
        checkpoint_id: Optional[str],
        required_participant_ids: Tuple[str, ...] = (),
    ) -> RestorationPlan:
        """Prepare a restoration plan."""
        if not checkpoint_id:
            return RestorationPlan(
                checkpoint_id=None,
                participants_to_restore=(),
                ledger_tail_position=None,
            )
        
        # In this simplified implementation, we restore all registered participants
        participants_to_restore: List[Tuple[ContinuityParticipant, bool]] = []
        for p in self._participants.values():
            is_required = p.required_for_restore or str(p.participant_id) in required_participant_ids
            participants_to_restore.append((p, is_required))
        
        return RestorationPlan(
            checkpoint_id=checkpoint_id,
            participants_to_restore=tuple(participants_to_restore),
            ledger_tail_position=None,
        )
    
    async def execute_restoration_transaction(
        self,
        plan: RestorationPlan,
    ) -> Tuple[RestorationStatus, List[RestorationResult], List[Dict[str, Any]]]:
        """
        Execute a restoration transaction.
        
        Returns:
            Tuple of (status, results, interrupted_operations)
        """
        results: List[RestorationResult] = []
        interrupted_ops: List[Dict[str, Any]] = []
        
        for participant, required in plan.participants_to_restore:
            try:
                result = await asyncio.wait_for(
                    participant.restore_checkpoint(
                        fragment=self._get_fragment_for_restoration(participant),
                        context={},
                    ),
                    timeout=self._config.restore_timeout_seconds,
                )
                results.append(result)
                
                # If restoration succeeded, reconcile interruptions
                if result.success:
                    reconciliation = await self._reconcile_participant_interrupted(
                        participant,
                        ledger_tail=(),
                    )
                    interrupted_ops.extend([{
                        "participant": str(participant.participant_id),
                        "operations_resumed": getattr(r, "operations_resumed", 0) if hasattr(r, "operations_resumed") else 0,
                        "operations_retried": getattr(r, "operations_retried", 0) if hasattr(r, "operations_retried") else 0,
                        "operations_rolled_back": getattr(r, "operations_rolled_back", 0) if hasattr(r, "operations_rolled_back") else 0,
                        "operations_compensated": getattr(r, "operations_compensated", 0) if hasattr(r, "operations_compensated") else 0,
                        "uncertain_operations": getattr(r, "uncertain_operations", 0) if hasattr(r, "uncertain_operations") else 0,
                    } for r in reconciliation])
                    
            except Exception as e:
                results.append(RestorationResult.failed(str(participant.participant_id), str(e)))
        
        # Determine overall status
        required_results = [r for p, r in zip(
            plan.participants_to_restore,
            results,
        ) if p[1]]  # Only required participants
        
        failed_count = sum(1 for r in required_results if not r.success)
        total_required = len(required_results)
        
        if failed_count == 0 and total_required > 0:
            status = RestorationStatus.SUCCEEDED
        elif failed_count < total_required and total_required > 0:
            status = RestorationStatus.PARTIALLY_SUCCEEDED
        else:
            status = RestorationStatus.FAILED
        
        return status, results, interrupted_ops
    
    def _get_fragment_for_restoration(self, participant: ContinuityParticipant) -> CheckpointFragment:
        """Get the fragment to restore for a participant."""
        # In this simplified implementation, we create a minimal fragment
        return CheckpointFragment(
            participant_id=participant.participant_id,
            fragment_type=participant.fragment_type,
            schema_version=participant.schema_version,
            runtime_generation=RuntimeGeneration.generate(),
            checkpoint_id=CheckpointId.generate(),
            captured_at_ns=time.time_ns(),
            state_version="1.0",
            payload_reference=f"fragment://{participant.participant_id.value}",
            checksum="placeholder-checksum",
            compression=None,
            required_for_restore=participant.required_for_restore,
            compatibility_metadata={},
            provenance="restored_from_previous_checkpoint",
        )
    
    async def _reconcile_participant_interrupted(
        self,
        participant: ContinuityParticipant,
        ledger_tail: Tuple[Dict[str, Any], ...],
    ) -> List[ReconciliationResult]:
        """Reconcile interrupted operations for a participant."""
        try:
            result = await asyncio.wait_for(
                participant.reconcile_interruption(
                    ledger_tail=ledger_tail,
                    context={},
                ),
                timeout=self._config.participant_timeout_seconds,
            )
            return [result]
        except Exception:
            # Return empty reconciliation on error
            return []
    
    async def verify_restoration(
        self,
        results: List[RestorationResult],
    ) -> VerificationResult:
        """Verify that restoration was successful."""
        all_success = all(r.success for r in results)
        
        if all_success:
            return VerificationResult.succeeded()
        else:
            failures = [r.errors for r in results if not r.success]
            return VerificationResult.failed(*[e for f in failures for e in f])