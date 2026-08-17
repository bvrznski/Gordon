# Gordon Phase 5.7.4-I: Temporal Context Engine - Exceptions
# ===============================================================================
"""
Exception types for the Temporal Context Engine.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass
class ContinuityViolation(Exception):
    """
    Raised when temporal continuity is violated.
    
    This indicates that a transition attempted to break the bounded
    continuity requirements of the Temporal Context Engine.
    """
    continuity_window_id: str
    """ID of the affected continuity window."""
    
    violation_type: str
    """Type of violation (e.g., 'generation_gap', 'retention_overflow')."""
    
    details: str = ""
    """Additional context about the violation."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the violation occurred."""
    
    def __str__(self) -> str:
        return (
            f"ContinuityViolation[{self.continuity_window_id}]: "
            f"{self.violation_type} - {self.details}"
        )


@dataclass
class SnapshotCorruption(Exception):
    """
    Raised when a temporal snapshot is detected as corrupted.
    
    This indicates that published snapshot integrity has been compromised,
    possibly due to memory corruption or invalid state transition.
    """
    snapshot_id: str
    """ID of the corrupted snapshot."""
    
    corruption_type: str
    """Type of corruption (e.g., 'integrity_check', 'version_mismatch')."""
    
    affected_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that failed integrity checks."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When corruption was detected."""
    
    def __str__(self) -> str:
        return (
            f"SnapshotCorruption[{self.snapshot_id}]: "
            f"{self.corruption_type} in {len(self.affected_fields)} fields"
        )


@dataclass
class TransitionFailure(Exception):
    """
    Raised when a temporal transition fails to commit.
    
    This indicates that the transition authority rejected or failed to
    apply a requested state change.
    """
    transition_id: str
    """ID of the failed transition."""
    
    failure_reason: str
    """Human-readable reason for failure."""
    
    attempted_generation: int = 0
    """Generation number that was attempted."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the failure occurred."""
    
    def __str__(self) -> str:
        return (
            f"TransitionFailure[{self.transition_id}]: "
            f"generation {self.attempted_generation}: {self.failure_reason}"
        )


@dataclass
class InvalidRetentionReference(Exception):
    """
    Raised when a retention reference is invalid.
    
    This indicates that a referenced previous-generation context does not
    exist, has expired, or violates bounded history constraints.
    """
    retention_id: str
    """ID of the invalid retention."""
    
    reference: str
    """Invalid reference value."""
    
    reason: str = ""
    """Reason why the reference is invalid."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the error occurred."""
    
    def __str__(self) -> str:
        return (
            f"InvalidRetentionReference[{self.retention_id}]: "
            f"{self.reference}: {self.reason}"
        )


@dataclass
class InvalidProtentionExpectation(Exception):
    """
    Raised when a protentional expectation is invalid.
    
    This indicates that an expectation exceeds bounded limits or violates
    the distinction between immediate expectations and planning/prediction.
    """
    protention_id: str
    """ID of the invalid protention."""
    
    expectation: str
    """Invalid expectation value."""
    
    reason: str = ""
    """Reason why the expectation is invalid."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the error occurred."""
    
    def __str__(self) -> str:
        return (
            f"InvalidProtentionExpectation[{self.protention_id}]: "
            f"{self.expectation}: {self.reason}"
        )


@dataclass
class InvalidContinuityWindow(Exception):
    """
    Raised when a continuity window is in an invalid state.
    
    This indicates that the window's bounds have been violated, its
    internal state has become corrupted, or it cannot transition properly.
    """
    continuity_window_id: str
    """ID of the invalid window."""
    
    current_state: str
    """Current (invalid) state of the window."""
    
    expected_state: Optional[str] = None
    """State that was expected."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the error occurred."""
    
    def __str__(self) -> str:
        if self.expected_state:
            return (
                f"InvalidContinuityWindow[{self.continuity_window_id}]: "
                f"state={self.current_state}, expected={self.expected_state}"
            )
        return (
            f"InvalidContinuityWindow[{self.continuity_window_id}]: "
            f"state={self.current_state}"
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ContinuityViolation",
    "SnapshotCorruption",
    "TransitionFailure",
    "InvalidRetentionReference",
    "InvalidProtentionExpectation",
    "InvalidContinuityWindow",
)