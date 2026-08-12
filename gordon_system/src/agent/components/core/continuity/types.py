# Continuity Types and Enums
# ============================

"""
Additional type definitions for continuity infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, Tuple, Optional


# =============================================================================
# CHECKPOINT CONSISTENCY MODES
# =============================================================================

class CheckpointConsistencyMode(Enum):
    """
    Consistency model for checkpoint creation.
    
    Different modes trade off between consistency guarantees and runtime disruption:
        
        QUIESCENT:
            - Briefly pause mutation admission
            - Capture from a quiesced state
            - Strongest consistency guarantee
            
        GENERATION_BASED:
            - Use versioned state with generation IDs
            - No admission pause required
            - Weaker but faster consistency
            
        IMMUTABLE_SNAPSHOT:
            - Capture from an immutable snapshot
            - No runtime disruption
            - Requires subsystem to maintain snapshots
    """
    
    QUIESCENT = "QUIESCENT"
    GENERATION_BASED = "GENERATION_BASED"
    IMMUTABLE_SNAPSHOT = "IMMUTABLE_SNAPSHOT"


# =============================================================================
# CHECKPOINT REASONS
# =============================================================================

class CheckpointReason(Enum):
    """
    Reasons for creating a checkpoint.
    
    Used to determine the importance and urgency of checkpoint creation.
    """
    
    PERIODIC = "PERIODIC"  # Scheduled periodic checkpoint
    IMPORTANT_TRANSITION = "IMPORTANT_TRANSITION"  # Important state transition
    PRE_SHUTDOWN = "PRE_SHUTDOWN"  # Pre-shutdown checkpoint for crash recovery
    PRE_RESTART = "PRE_RESTART"  # Pre-restart checkpoint
    MANUAL = "MANUAL"  # Manual/external trigger
    RECOVERY_BASELINE = "RECOVERY_BASELINE"  # Creating baseline after recovery
    MAINTENANCE = "MAINTENANCE"  # Maintenance-related checkpoint


# =============================================================================
# LEDGER RECORD KINDS
# =============================================================================

class LedgerRecordKind(Enum):
    """
    Kinds of records that may appear in the continuity ledger.
    
    The ledger records operational transitions relevant to crash recovery.
    It is NOT:
        - A full event bus
        - Cognitive memory
        - An audit system for all operations
        
    It only records transitions that affect recovery decisions.
    """
    
    # Runtime lifecycle
    RUNTIME_STARTED = "RUNTIME_STARTED"
    RUNTIME_READY = "RUNTIME_READY"
    
    # Task lifecycle (if resumable)
    TASK_ACCEPTED = "TASK_ACCEPTED"
    TASK_STARTED = "TASK_STARTED"
    TASK_CHECKPOINTED = "TASK_CHECKPOINTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    
    # Action lifecycle
    ACTION_ADMITTED = "ACTION_ADMITTED"
    ACTION_STARTED = "ACTION_STARTED"
    ACTION_SIDE_EFFECT_CONFIRMED = "ACTION_SIDE_EFFECT_CONFIRMED"
    ACTION_COMPLETED = "ACTION_COMPLETED"
    ACTION_FAILED = "ACTION_FAILED"
    
    # Transaction lifecycle
    TRANSACTION_PREPARED = "TRANSACTION_PREPARED"
    TRANSACTION_COMMITTED = "TRANSACTION_COMMITTED"
    TRANSACTION_ROLLED_BACK = "TRANSACTION_ROLLED_BACK"
    
    # Resource lifecycle
    RESOURCE_ACQUIRED = "RESOURCE_ACQUIRED"
    RESOURCE_RELEASED = "RESOURCE_RELEASED"
    
    # Service lifecycle
    SERVICE_STARTED = "SERVICE_STARTED"
    SERVICE_DEGRADED = "SERVICE_DEGRADED"
    SERVICE_FAILED = "SERVICE_FAILED"
    SERVICE_STOPPED = "SERVICE_STOPPED"
    
    # Checkpoint lifecycle
    CHECKPOINT_STARTED = "CHECKPOINT_STARTED"
    CHECKPOINT_COMMITTED = "CHECKPOINT_COMMITTED"
    CHECKPOINT_FAILED = "CHECKPOINT_FAILED"
    
    # Recovery lifecycle
    RECOVERY_STARTED = "RECOVERY_STARTED"
    RECOVERY_COMPLETED = "RECOVERY_COMPLETED"
    RECOVERY_FAILED = "RECOVERY_FAILED"
    
    # Shutdown lifecycle
    SHUTDOWN_STARTED = "SHUTDOWN_STARTED"
    SHUTDOWN_COMPLETED = "SHUTDOWN_COMPLETED"


# =============================================================================
# CHECKPOINT STATUS
# =============================================================================

class CheckpointStatus(Enum):
    """
    Status of a checkpoint transaction.
    
    A checkpoint moves through these states:
        PREPARING → WRITING → VALIDATING → COMMITTED
        
    Or fails at any point and goes to REJECTED/CORRUPT.
    """
    
    PREPARING = "PREPARING"
    WRITING = "WRITING"
    VALIDATING = "VALIDATING"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"
    CORRUPT = "CORRUPT"
    SUPERSEDED = "SUPERSEDED"


# =============================================================================
# RESTORATION STATUS
# =============================================================================

class RestorationStatus(Enum):
    """
    Status of a restoration operation.
    
    Possible outcomes:
        SUCCEEDED: All required participants restored successfully
        SUCCEEDED_WITH_DEGRADATION: Required succeeded, optional failed
        PARTIALLY_SUCCEEDED: Some required succeeded
        FAILED: Too many failures to continue
        CANCELLED: Operation was cancelled
        TIMED_OUT: Deadline exceeded
    """
    
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    SUCCEEDED_WITH_DEGRADATION = "SUCCEEDED_WITH_DEGRADATION"
    PARTIALLY_SUCCEEDED = "PARTIALLY_SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


# =============================================================================
# INTERRUPTION CLASSIFICATION
# =============================================================================

class InterruptionClassification(Enum):
    """
    Classification of an interrupted operation after restoration.
    
    Used to determine what action should be taken for each operation
    that was in progress when the runtime was interrupted.
    """
    
    COMPLETED = "COMPLETED"  # Evidence shows it completed (idempotent)
    NOT_STARTED = "NOT_STARTED"  # Never started, can restart
    SAFE_TO_RESUME = "SAFE_TO_RESUME"  # Can safely resume from checkpoint
    SAFE_TO_RETRY = "SAFE_TO_RETRY"  # Can safely retry (idempotent)
    REQUIRES_RECONCILIATION = "REQUIRES_RECONCILIATION"  # Needs human review
    REQUIRES_ROLLBACK = "REQUIRES_ROLLBACK"  # Must be rolled back
    REQUIRES_COMPENSATION = "REQUIRES_COMPENSATION"  # Needs compensation action
    EXTERNAL_STATE_UNCERTAIN = "EXTERNAL_STATE_UNCERTAIN"  # Side effects unknown
    NON_RECOVERABLE = "NON_RECOVERABLE"  # Cannot recover, abandon
    ABANDONED = "ABANDONED"  # Abandoned due to policy or constraints


# =============================================================================
# HEALTH STATES
# =============================================================================

class ContinuityHealth(Enum):
    """
    Health status of the continuity infrastructure.
    """
    
    CONFIGURED = "CONFIGURED"  # Configured but not initialized
    INITIALIZED = "INITIALIZED"  # Initialized but not ready
    READY = "READY"  # Ready for operations
    CHECKPOINTING = "CHECKPOINTING"  # Currently creating a checkpoint
    RECOVERING = "RECOVERING"  # Currently in recovery
    DEGRADED = "DEGRADED"  # Some functionality unavailable
    NO_VALID_CHECKPOINT = "NO_VALID_CHECKPOINT"  # No usable checkpoint exists
    LEDGER_DEGRADED = "LEDGER_DEGRADED"  # Ledger has issues
    STORAGE_UNAVAILABLE = "STORAGE_UNAVAILABLE"  # Storage backend down
    FAILED = "FAILED"  # Infrastructure failure
    STOPPING = "STOPPING"  # shutting down
    STOPPED = "STOPPED"  # Fully stopped


# =============================================================================
# CHECKPOINT REQUEST
# =============================================================================

@dataclass(frozen=True)
class CheckpointRequest:
    """
    Request to create a checkpoint.
    
    All fields are optional with sensible defaults where possible.
    """
    
    reason: CheckpointReason = CheckpointReason.PERIODIC
    consistency_mode: CheckpointConsistencyMode = CheckpointConsistencyMode.GENERATION_BASED
    participant_scope: Literal["ALL", "REQUIRED_ONLY", "SPECIFIED"] = "ALL"
    required_participants: Tuple[str, ...] = ()
    optional_participants: Tuple[str, ...] = ()
    quiescence_timeout_seconds: float = 5.0
    checkpoint_timeout_seconds: float = 30.0
    ledger_position_hint: Optional[int] = None  # Hint about where to start recording after this checkpoint
    
    @classmethod
    def for_periodic(cls) -> "CheckpointRequest":
        """Create a request for periodic checkpointing."""
        return cls(reason=CheckpointReason.PERIODIC)
    
    @classmethod
    def for_shutdown(cls) -> "CheckpointRequest":
        """Create a request for shutdown checkpoint."""
        return cls(
            reason=CheckpointReason.PRE_SHUTDOWN,
            consistency_mode=CheckpointConsistencyMode.QUIESCENT,
        )
    
    @classmethod
    def for_recovery_baseline(cls, runtime_generation: str) -> "CheckpointRequest":
        """Create a request for recovery baseline checkpoint."""
        return cls(reason=CheckpointReason.RECOVERY_BASELINE)