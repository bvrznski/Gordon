# Continuity Exceptions
# =====================

"""
Exception hierarchy for continuity operations.
"""


class ContinuityError(Exception):
    """Base exception for all continuity-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class CheckpointNotFound(ContinuityError):
    """No valid checkpoint was found."""
    
    def __init__(self, runtime_id: str, generation: int):
        super().__init__(
            f"No valid checkpoint found for runtime '{runtime_id}', generation {generation}",
            runtime_id=runtime_id,
            generation=generation,
        )


class CheckpointCorrupt(ContinuityError):
    """A checkpoint was found but is corrupted or invalid."""
    
    def __init__(self, checkpoint_id: str, reason: str):
        super().__init__(
            f"Checkpoint '{checkpoint_id}' is corrupt: {reason}",
            checkpoint_id=checkpoint_id,
            reason=reason,
        )


class ParticipantUnavailable(ContinuityError):
    """A required participant is not available for checkpoint/restore."""
    
    def __init__(self, participant_id: str, operation: str):
        super().__init__(
            f"Participant '{participant_id}' is unavailable for {operation}",
            participant_id=participant_id,
            operation=operation,
        )


class LedgerCorrupt(ContinuityError):
    """The continuity ledger is corrupted or inconsistent."""
    
    def __init__(self, position: int, reason: str):
        super().__init__(
            f"Ledger corruption at position {position}: {reason}",
            position=position,
            reason=reason,
        )


class ParticipantRegistrationError(ContinuityError):
    """Error registering a participant with the continuity system."""
    
    def __init__(self, participant_id: str, reason: str):
        super().__init__(
            f"Cannot register participant '{participant_id}': {reason}",
            participant_id=participant_id,
            reason=reason,
        )


class CheckpointTransactionFailed(ContinuityError):
    """Checkpoint transaction failed at some stage."""
    
    def __init__(self, checkpoint_id: str, stage: str, errors: tuple[str, ...]):
        super().__init__(
            f"Checkpoint '{checkpoint_id}' failed at {stage}: {', '.join(errors)}",
            checkpoint_id=checkpoint_id,
            stage=stage,
            errors=errors,
        )


class RestorationFailed(ContinuityError):
    """Restoration from checkpoint failed."""
    
    def __init__(self, checkpoint_id: str, failed_participants: tuple[str, ...], partial_success: bool = False):
        super().__init__(
            f"Restoration from '{checkpoint_id}' {'partial' if partial_success else 'fully'} failed. "
            f"Failed participants: {', '.join(failed_participants)}",
            checkpoint_id=checkpoint_id,
            failed_participants=failed_participants,
            partial_success=partial_success,
        )


class VerificationFailed(ContinuityError):
    """Post-restoration verification failed."""
    
    def __init__(self, checkpoint_id: str, failures: tuple[str, ...]):
        super().__init__(
            f"Verification failed for checkpoint '{checkpoint_id}': {', '.join(failures)}",
            checkpoint_id=checkpoint_id,
            failures=failures,
        )


class LedgerWriteFailed(ContinuityError):
    """Failed to write a ledger record."""
    
    def __init__(self, sequence: int, record_kind: str, reason: str):
        super().__init__(
            f"Ledger write failed at seq {sequence} ({record_kind}): {reason}",
            sequence=sequence,
            record_kind=record_kind,
            reason=reason,
        )


class LedgerFlushFailed(ContinuityError):
    """Failed to flush the ledger to persistent storage."""
    
    def __init__(self, position: int, reason: str):
        super().__init__(
            f"Ledger flush failed at seq {position}: {reason}",
            position=position,
            reason=reason,
        )


class StorageUnavailable(ContinuityError):
    """Storage backend for continuity artifacts is unavailable."""
    
    def __init__(self, storage_type: str, reason: str):
        super().__init__(
            f"Continuity {storage_type} storage unavailable: {reason}",
            storage_type=storage_type,
            reason=reason,
        )


class ParticipantTimeout(ContinuityError):
    """Participant failed to respond within timeout."""
    
    def __init__(self, participant_id: str, operation: str, timeout_seconds: float):
        super().__init__(
            f"Participant '{participant_id}' timed out during {operation} (timeout: {timeout_seconds}s)",
            participant_id=participant_id,
            operation=operation,
            timeout_seconds=timeout_seconds,
        )


class IncompatibleCheckpoint(ContinuityError):
    """Checkpoint exists but is incompatible with current runtime."""
    
    def __init__(self, checkpoint_id: str, reason: str):
        super().__init__(
            f"Checkpoint '{checkpoint_id}' is incompatible: {reason}",
            checkpoint_id=checkpoint_id,
            reason=reason,
        )


class ConcurrentRuntimeDetected(ContinuityError):
    """Another runtime process is using the same continuity state."""
    
    def __init__(self, previous_runtime_id: str, current_process_id: int):
        super().__init__(
            f"Concurrent runtime detected: previous '{previous_runtime_id}' "
            f"conflicts with current process {current_process_id}",
            previous_runtime_id=previous_runtime_id,
            current_process_id=current_process_id,
        )