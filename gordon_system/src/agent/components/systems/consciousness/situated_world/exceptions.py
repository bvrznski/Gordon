# Gordon Phase 5.7.7: Situated World - Exceptions
# =================================================

"""
Canonical exception hierarchy for the Situated World capability.

All exceptions inherit from WorldError to enable consistent error handling.
"""

from __future__ import annotations

from typing import Any


class WorldError(Exception):
    """Base exception for all Situated World errors."""
    
    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


class WorldStateError(WorldError):
    """Exception raised when world state is invalid or inconsistent."""
    
    def __init__(
        self,
        message: str,
        current_state: dict[str, Any] | None = None,
        expected_state: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.current_state = current_state
        self.expected_state = expected_state


class WorldTransitionError(WorldError):
    """Exception raised when a world transition fails or is invalid."""
    
    def __init__(
        self,
        message: str,
        from_generation: int | None = None,
        to_generation: int | None = None,
        transition_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.from_generation = from_generation
        self.to_generation = to_generation
        self.transition_id = transition_id


class WorldSnapshotError(WorldError):
    """Exception raised when a snapshot operation fails."""
    
    def __init__(
        self,
        message: str,
        snapshot_id: str | None = None,
        generation: int | None = None,
    ) -> None:
        super().__init__(message)
        self.snapshot_id = snapshot_id
        self.generation = generation


class WorldIdentityError(WorldError):
    """Exception raised when entity/relation identity validation fails."""
    
    def __init__(
        self,
        message: str,
        identity: str | None = None,
        kind: str | None = None,
    ) -> None:
        super().__init__(message)
        self.identity = identity
        self.kind = kind


class WorldIntegrityError(WorldError):
    """Exception raised when world state integrity is compromised."""
    
    def __init__(
        self,
        message: str,
        violated_constraint: str | None = None,
        affected_entities: tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(message)
        self.violated_constraint = violated_constraint
        self.affected_entities = affected_entities or ()


class WorldSecurityError(WorldError):
    """Exception raised when a security boundary is violated."""
    
    def __init__(
        self,
        message: str,
        attempted_action: str | None = None,
        identity_ref: str | None = None,
    ) -> None:
        super().__init__(message)
        self.attempted_action = attempted_action
        self.identity_ref = identity_ref


class WorldReplayError(WorldError):
    """Exception raised when replay fails to reproduce deterministic state."""
    
    def __init__(
        self,
        message: str,
        expected_state_id: str | None = None,
        actual_state_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.expected_state_id = expected_state_id
        self.actual_state_id = actual_state_id


class WorldConcurrencyError(WorldError):
    """Exception raised when concurrent access would violate determinism."""
    
    def __init__(
        self,
        message: str,
        waiting_reader_count: int | None = None,
        pending_writers: bool | None = None,
    ) -> None:
        super().__init__(message)
        self.waiting_reader_count = waiting_reader_count
        self.pending_writers = pending_writers


class WorldLifecycleError(WorldError):
    """Exception raised when lifecycle operations are invalid."""
    
    def __init__(
        self,
        message: str,
        current_state: str | None = None,
        requested_state: str | None = None,
    ) -> None:
        super().__init__(message)
        self.current_state = current_state
        self.requested_state = requested_state