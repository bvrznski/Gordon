# Continuity Participant Contracts
# =================================

"""
Continuity participant contract definitions.

This module defines the interface that subsystems must implement to participate
in checkpoint-based crash recovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    Protocol,
    Optional,
    Tuple,
    Any,
    Dict,
)
from uuid import UUID, uuid4


# =============================================================================
# TYPES AND IDENTIFIERS
# =============================================================================

@dataclass(frozen=True)
class ParticipantId:
    """
    Unique identifier for a continuity participant.
    
    Each subsystem that wants to participate in crash recovery must have
    a stable, unique participant ID. The ID should be deterministic based on
    the subsystem's canonical authority.
    """
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CheckpointId:
    """
    Unique identifier for a checkpoint.
    
    Generated per checkpoint transaction, used to link fragments together.
    """
    value: UUID

    @classmethod
    def generate(cls) -> "CheckpointId":
        """Generate a new random checkpoint ID."""
        return cls(value=UUID(uuid4()))
    
    def __str__(self) -> str:
        return f"cp-{self.value.hex[:16]}"


@dataclass(frozen=True)
class RuntimeGeneration:
    """
    Identifier for a specific runtime instance.
    
    Every process start gets a new runtime generation. Used to distinguish
    between state from different runs and stale state.
    """
    value: UUID

    @classmethod
    def generate(cls) -> "RuntimeGeneration":
        """Generate a new runtime generation ID."""
        return cls(value=UUID(uuid4()))
    
    def __str__(self) -> str:
        return f"gen-{self.value.hex[:16]}"


@dataclass(frozen=True)
class LedgerPosition:
    """
    Position in the continuity ledger.
    
    Used to track where we are in the append-only log of operational transitions.
    """
    sequence_number: int
    record_id: UUID

    def __str__(self) -> str:
        return f"seq-{self.sequence_number}:{self.record_id.hex[:8]}"


# =============================================================================
# CHECKPOINT FRAGMENT
# =============================================================================

@dataclass(frozen=True)
class CheckpointFragment:
    """
    A fragment of state captured during checkpoint.
    
    Each participant produces exactly one fragment per checkpoint. The fragment
    contains:
        - Metadata about what was captured
        - A reference to the actual state (not the state itself)
        - Integrity verification data
    
    The payload content remains participant-owned and must be deterministically
    reconstructable from the reference.
    """
    participant_id: ParticipantId
    fragment_type: str  # e.g., "lifecycle_state", "scheduler_metadata"
    schema_version: int
    runtime_generation: RuntimeGeneration
    checkpoint_id: CheckpointId
    captured_at_ns: int  # Unix timestamp in nanoseconds
    state_version: str  # Version of the state being captured
    payload_reference: str  # Storage path or encoded data
    checksum: str  # SHA256 hex of payload
    compression: Optional[str]  # e.g., "zlib", None for uncompressed
    required_for_restore: bool  # False if this is optional metadata
    compatibility_metadata: Dict[str, Any]
    provenance: str  # How the fragment was created

    @property
    def is_optional(self) -> bool:
        """Check if this fragment is optional for restoration."""
        return not self.required_for_restore


# =============================================================================
# RESTORATION AND RECONCILIATION RESULTS
# =============================================================================

@dataclass(frozen=True)
class RestorationResult:
    """
    Result of restoring a participant's state from a checkpoint.
    
    Each participant returns a result indicating whether its state was
    successfully restored and any warnings or errors encountered.
    """
    participant_id: ParticipantId
    success: bool
    restored_state_version: Optional[str]
    restored_from_checkpoint_id: Optional[CheckpointId]
    warnings: Tuple[str, ...]
    errors: Tuple[str, ...]

    @classmethod
    def succeeded(cls, participant_id: ParticipantId, state_version: str) -> "RestorationResult":
        """Create a successful restoration result."""
        return cls(
            participant_id=participant_id,
            success=True,
            restored_state_version=state_version,
            restored_from_checkpoint_id=None,
            warnings=(),
            errors=(),
        )

    @classmethod
    def failed(cls, participant_id: ParticipantId, error_message: str) -> "RestorationResult":
        """Create a failed restoration result."""
        return cls(
            participant_id=participant_id,
            success=False,
            restored_state_version=None,
            restored_from_checkpoint_id=None,
            warnings=(),
            errors=(error_message,),
        )


@dataclass(frozen=True)
class ReconciliationResult:
    """
    Result of reconciling interrupted state after restoration.
    
    Indicates how each interrupted operation was classified and what
    action should be taken.
    """
    participant_id: ParticipantId
    operations_reconciled: int
    operations_resumed: int
    operations_retried: int
    operations_rolled_back: int
    operations_compensated: int
    operations_unchanged: int
    uncertain_operations: int
    non_recoverable_operations: int

    @classmethod
    def empty(cls, participant_id: ParticipantId) -> "ReconciliationResult":
        """Create an empty reconciliation result."""
        return cls(
            participant_id=participant_id,
            operations_reconciled=0,
            operations_resumed=0,
            operations_retried=0,
            operations_rolled_back=0,
            operations_compensated=0,
            operations_unchanged=0,
            uncertain_operations=0,
            non_recoverable_operations=0,
        )


@dataclass(frozen=True)
class VerificationResult:
    """
    Result of post-restoration verification.
    
    Indicates whether the restored state passes integrity and readiness checks.
    """
    success: bool
    integrity_verified: bool
    health_verified: bool
    compatibility_verified: bool
    warnings: Tuple[str, ...]
    errors: Tuple[str, ...]

    @classmethod
    def succeeded(cls) -> "VerificationResult":
        """Create a successful verification result."""
        return cls(
            success=True,
            integrity_verified=True,
            health_verified=True,
            compatibility_verified=True,
            warnings=(),
            errors=(),
        )

    @classmethod
    def failed(cls, *errors: str) -> "VerificationResult":
        """Create a failed verification result."""
        return cls(
            success=False,
            integrity_verified=False,
            health_verified=False,
            compatibility_verified=False,
            warnings=(),
            errors=errors,
        )


# =============================================================================
# CONTINUITY PARTICIPANT PROTOCOL
# =============================================================================

class ContinuityParticipant(Protocol):
    """
    Protocol for continuity participants.
    
    Subsystems that want to participate in crash recovery must implement this
    protocol. Each participant is responsible for:
        
        1. Capturing its owned state during checkpoint (via prepare_checkpoint)
        2. Restoring its state from a checkpoint fragment (restore_checkpoint)
        3. Reconciling interrupted operations after restoration (reconcile_interruption)
        4. Verifying the restored state is valid (verify_restoration)
    
    Key Constraints:
        - Must have a stable, deterministic participant_id
        - Fragment content must be reconstructable from the reference
        - Never serialize live objects (locks, threads, sockets, etc.)
        - State ownership remains with the subsystem
    
    Example implementations:
        - Lifecycle authority: captures current lifecycle state
        - Scheduler: captures admitted but not started tasks
        - Action runtime: captures in-flight action states
        - Communication runtime: captures subscription and queue state
        - Memory runtime: captures transaction descriptors
    """
    
    @property
    def participant_id(self) -> ParticipantId:
        """Return the stable, unique identifier for this participant."""
        ...
    
    @property
    def fragment_type(self) -> str:
        """
        Return a category string for this participant's fragments.
        
        Used for organization and filtering of checkpoint fragments.
        Examples: "lifecycle", "scheduler", "action_runtime", "communication"
        """
        ...
    
    @property
    def schema_version(self) -> int:
        """Return the schema version of this participant's checkpoint fragments."""
        return 1
    
    @property
    def required_for_restore(self) -> bool:
        """
        Return True if this participant must be restored for the runtime to continue.
        
        If False, restoration continues even if this participant fails.
        """
        return True
    
    async def prepare_checkpoint(
        self,
        checkpoint_id: CheckpointId,
        runtime_generation: RuntimeGeneration,
        consistency_mode: str,
    ) -> CheckpointFragment:
        """
        Capture a snapshot of this participant's state for the checkpoint.
        
        Args:
            checkpoint_id: The ID of this checkpoint transaction
            runtime_generation: The current runtime generation being checkpointed
            consistency_mode: One of "QUIESCENT", "GENERATION_BASED", "IMMUTABLE_SNAPSHOT"
            
        Returns:
            A CheckpointFragment containing the captured state reference and metadata
            
        Implementation notes:
            - Must be idempotent (can be called multiple times)
            - Quiescent mode: temporarily pause mutation admission
            - Generation-based: use versioned state with generation check
            - Immutable snapshot: capture from immutable snapshot if available
            - Never serialize live objects directly
            - Return a reference to the state, not the state itself
            
        Raises:
            ContinuityError: If checkpoint cannot be captured
        """
        ...
    
    async def restore_checkpoint(
        self,
        fragment: CheckpointFragment,
        context: Dict[str, Any],
    ) -> RestorationResult:
        """
        Restore this participant's state from a checkpoint fragment.
        
        Args:
            fragment: The checkpoint fragment to restore from
            context: Additional restoration context (participant dependency info)
            
        Returns:
            RestorationResult indicating success/failure and any warnings
            
        Implementation notes:
            - Must be idempotent
            - Only reconstruct descriptors, not live objects
            - Reconnect through canonical subsystem interfaces
            - Validate the fragment against current software version
            - Return detailed result with any warnings or errors
        """
        ...
    
    async def reconcile_interruption(
        self,
        ledger_tail: Tuple[Dict[str, Any], ...],
        context: Dict[str, Any],
    ) -> ReconciliationResult:
        """
        Reconcile interrupted operations after restoration.
        
        Args:
            ledger_tail: The verified tail of the continuity ledger since the checkpoint
            context: Additional reconciliation context
            
        Returns:
            ReconciliationResult indicating how each operation was classified
            
        Implementation notes:
            - Classify operations as: RESUMED, RETRIED, ROLLED_BACK, COMPENSATED,
              UNCHANGED, UNCERTAIN, NON_RECOVERABLE
            - Never replay actions with uncertain external side effects
            - Defer to subsystem's own interruption classification logic
        """
        ...
    
    async def verify_restoration(self) -> VerificationResult:
        """
        Verify that the restored state is valid and ready for use.
        
        Returns:
            VerificationResult indicating whether integrity, health, and
            compatibility checks passed
            
        Implementation notes:
            - Must be deterministic (same state → same result)
            - Check only what this participant can verify
            - Report specific warnings/errors, not just pass/fail
        """
        ...