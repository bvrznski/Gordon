"""Gordon Agent Startup Outcomes.

Phase 3.7.33-I: Agent Startup Coordination
==========================================

Immutable outcome values for startup results.
"""
from __future__ import annotations

from enum import Enum, auto


class AgentStartupOutcome(Enum):
    """Possible outcomes of a startup transaction.
    
    These outcomes represent the final state of a startup operation and
    determine what happens next in the system lifecycle.
    
    Outcome semantics:
        STARTED: Preflight and initialization completed successfully,
                 ownership was transferred to initialized Agent boundary.
        
        STARTED_DEGRADED: Startup completed under an explicitly approved
                          degraded policy. Some capabilities may be unavailable.
        
        BLOCKED: A valid subordinate result (typically preflight) prevented
                 startup from progressing. This is not a failure - it's a
                 legitimate blocking condition.
        
        FAILED: The startup transaction or subordinate authority failed.
                This indicates an error state.
        
        CANCELLED: Startup was explicitly cancelled (by signal, deadline,
                   or external request).
        
        TIMED_OUT: Startup exceeded an approved deadline. This is a distinct
                   outcome from cancellation - it's time-based termination.
    
    Transition rules:
        Only STARTED and policy-approved STARTED_DEGRADED may proceed to operation.
        BLOCKED, FAILED, CANCELLED, and TIMED_OUT must trigger cleanup/rollback/shutdown.
    """
    
    # Successful outcomes
    STARTED = "started"
    """Startup completed successfully with full functionality."""
    
    STARTED_DEGRADED = "started_degraded"
    """Startup completed under approved degraded policy."""
    
    # Blocking outcomes (not failures)
    BLOCKED = "blocked"
    """Valid subordinate result prevented startup from progressing."""
    
    # Failure outcomes
    FAILED = "failed"
    """Startup transaction or subordinate authority failed."""
    
    CANCELLED = "cancelled"
    """Startup was explicitly cancelled."""
    
    TIMED_OUT = "timed_out"
    """Startup exceeded an approved deadline."""
    
    @property
    def is_success(self) -> bool:
        """Check if this outcome indicates successful startup.
        
        Only STARTED and STARTED_DEGRADED are considered success.
        """
        return self in (AgentStartupOutcome.STARTED, AgentStartupOutcome.STARTED_DEGRADED)
    
    @property
    def is_failure(self) -> bool:
        """Check if this outcome indicates a failure condition."""
        return self not in (
            AgentStartupOutcome.STARTED,
            AgentStartupOutcome.STARTED_DEGRADED,
        )
    
    @property
    def requires_cleanup(self) -> bool:
        """Check if this outcome requires cleanup/rollback/shutdown."""
        return not self.is_success
    
    @classmethod
    def from_string(cls, value: str) -> "AgentStartupOutcome":
        """Parse a string into an outcome.
        
        Args:
            value: String representation of the outcome
            
        Returns:
            Corresponding AgentStartupOutcome
            
        Raises:
            ValueError: If the string doesn't match any outcome
        """
        mapping = {
            "started": cls.STARTED,
            "started_degraded": cls.STARTED_DEGRADED,
            "blocked": cls.BLOCKED,
            "failed": cls.FAILED,
            "cancelled": cls.CANCELLED,
            "timed_out": cls.TIMED_OUT,
        }
        
        return mapping.get(value.lower(), cls.FAILED)


class AgentStartupOwnershipState(Enum):
    """States of startup ownership transition.
    
    This tracks where we are in the ownership transfer from startup
    coordinator to initialized runtime.
    """
    
    UNINITIALIZED = "uninitialized"
    """No resources owned yet."""
    
    LAUNCH_OWNED = "launch_owned"
    """Launch request is owned by launch context."""
    
    STARTUP_OWNED = "startup_owned"
    """Startup context owns startup request and context."""
    
    PREFLIGHT_OWNED = "preflight_owned"
    """Preflight result created, owned by startup context."""
    
    INITIALIZATION_OWNED = "initialization_owned"
    """Initialization in progress, partial runtime may exist."""
    
    TRANSFERRED = "transferred"
    """Runtime ownership transferred to initialized Agent boundary."""
    
    ROLLBACK_COMPLETE = "rollback_complete"
    """Rollback completed, no ownership retained."""
    
    SHUTDOWN_COMPLETE = "shutdown_complete"
    """Shutdown completed, resources released."""
    
    @property
    def has_ownership(self) -> bool:
        """Check if we have active ownership of a runtime."""
        return self in (
            AgentStartupOwnershipState.TRANSFERRED,
            AgentStartupOwnershipState.INITIALIZATION_OWNED,
        )


class AgentStartupHandoffStatus(Enum):
    """Status of startup-to-operation handoff."""
    
    NOT_ATTEMPTED = "not_attempted"
    """Handoff not yet attempted."""
    
    IN_PROGRESS = "in_progress"
    """Handoff verification in progress."""
    
    VERIFIED = "verified"
    """Handoff verified successfully."""
    
    FAILED = "failed"
    """Handoff failed - runtime state invalid or missing."""
    
    PENDING = "pending"
    """Waiting for runtime to be ready for handoff."""
    
    @property
    def is_valid(self) -> bool:
        """Check if handoff status represents valid operation entry point."""
        return self == AgentStartupHandoffStatus.VERIFIED


__all__ = [
    "AgentStartupOutcome",
    "AgentStartupOwnershipState",
    "AgentStartupHandoffStatus",
]