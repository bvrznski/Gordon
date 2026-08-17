# Gordon Phase 5.7.5-I: Presence Engine - Exceptions
# ===============================================================================
"""
Exception types for the Presence Engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PresenceError(Exception):
    """Base exception for presence engine errors."""
    message: str = ""
    
    def __str__(self) -> str:
        return self.message if self.message else "Presence error occurred"


@dataclass
class InvalidAdmission(PresenceError):
    """Raised when admission is invalid according to policy."""
    item_id: str = ""
    reason: str = ""


@dataclass
class InvalidWithdrawal(PresenceError):
    """Raised when withdrawal is invalid (item not in presence)."""
    item_id: str = ""
    current_state: str = ""


@dataclass
class TransitionConflict(PresenceError):
    """Raised when transition conflicts with existing state."""
    item_id: str = ""
    expected_state: str = ""
    actual_state: str = ""


@dataclass
class PublicationFailure(PresenceError):
    """Raised when snapshot publication fails."""
    generation: int = 0


@dataclass
class SnapshotCorruption(PresenceError):
    """Raised when snapshot integrity check fails."""
    snapshot_id: str = ""
    error_detail: str = ""


@dataclass
class InvalidStateTransition(PresenceError):
    """Raised when attempting an invalid state transition."""
    from_state: str = ""
    to_state: str = ""
    
    def __str__(self) -> str:
        return f"Invalid transition: {self.from_state} → {self.to_state}"


@dataclass
class CapacityExceeded(PresenceError):
    """Raised when presence capacity limits are exceeded."""
    limit_type: str = "active"
    current_count: int = 0
    max_count: int = 0
    
    def __str__(self) -> str:
        return (f"Capacity exceeded for {self.limit_type}: "
                f"{self.current_count}/{self.max_count}")