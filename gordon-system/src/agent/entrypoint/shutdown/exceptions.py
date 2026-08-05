"""Gordon Agent Shutdown Exceptions.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination
======================================================

Typed exception hierarchy for shutdown transaction failures.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Tuple


# =============================================================================
# BASE EXCEPTIONS
# =============================================================================


@dataclass
class AgentShutdownError(Exception):
    """Base exception for all shutdown-related errors.
    
    This is the parent class for all typed shutdown failures. It preserves
    contextual information about the shutdown transaction for diagnostics.
    
    Args:
        message: Human-readable error description
        shutdown_id: ID of the shutdown transaction
        request_id: ID of the shutdown request (if any)
        execution_id: Execution ID of this coordinator run
        process_id: Process where error occurred
        phase: Phase where error occurred
        cause: Underlying exception or error cause
        secondary_failures: List of related secondary failures
    """
    
    message: str = ""
    shutdown_id: Optional[str] = None
    request_id: Optional[str] = None
    execution_id: Optional[str] = None
    process_id: Optional[int] = None
    phase: Optional[str] = None
    cause: Optional[Exception] = None
    secondary_failures: Tuple["AgentShutdownFailure", ...] = field(default_factory=tuple)
    
    def __str__(self) -> str:
        parts = [f"{type(self).__name__}: {self.message}"]
        
        if self.shutdown_id:
            parts.append(f"shutdown_id={self.shutdown_id[:8]}")
        if self.phase:
            parts.append(f"phase={self.phase}")
        if self.cause:
            parts.append(f"cause={self.cause}")
        
        return "; ".join(parts)
    
    @property
    def is_primary(self) -> bool:
        """Check if this is the primary failure (no cause)."""
        return self.cause is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for diagnostics."""
        result = {
            "type": type(self).__name__,
            "message": self.message[:200] if len(self.message) > 200 else self.message,
        }
        
        if self.shutdown_id:
            result["shutdown_id"] = self.shutdown_id
        if self.phase:
            result["phase"] = self.phase
        
        return result


class AgentShutdownRequestError(AgentShutdownError):
    """Raised when shutdown request validation fails."""
    
    pass


class AgentShutdownTimeoutError(AgentShutdownError):
    """Raised when a shutdown deadline is exceeded.
    
    Args:
        message: Error description
        deadline_seconds: The deadline that was exceeded
        elapsed_seconds: Time elapsed before timeout
    """
    
    def __init__(
        self,
        message: str = "",
        deadline_seconds: float = 0.0,
        elapsed_seconds: float = 0.0,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.deadline_seconds = deadline_seconds
        self.elapsed_seconds = elapsed_seconds


class AgentShutdownDuplicateError(AgentShutdownError):
    """Raised when a duplicate shutdown is detected.
    
    Args:
        existing_shutdown_id: ID of the existing shutdown transaction
    """
    
    def __init__(
        self,
        message: str = "",
        existing_shutdown_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.existing_shutdown_id = existing_shutdown_id


class AgentShutdownIdentityError(AgentShutdownError):
    """Raised when runtime identity validation fails."""
    
    pass


class AgentShutdownOwnershipError(AgentShutdownError):
    """Raised when ownership validation fails."""
    
    pass


# =============================================================================
# DETAILED FAILURE TYPES
# =============================================================================


@dataclass(frozen=True)
class AgentShutdownFailure:
    """Immutable failure record for diagnostics.
    
    Args:
        failure_id: Unique identifier for this failure
        type_name: Name of the exception class
        message: Human-readable description
        phase: Phase where failure occurred
        authority: Authority that reported the failure (e.g., "core", "entrypoint")
        timestamp_ns: When failure occurred
        primary_cause: The primary cause (if this is a secondary failure)
        secondary_failures: Any related secondary failures
        escalation_state: Escalation state when failure occurred
        terminal_state_evidence: Terminal state evidence at time of failure
        retry_eligible: Whether this can be retried
    """
    
    failure_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type_name: str = ""
    message: str = ""
    phase: Optional[str] = None
    authority: str = "unknown"
    timestamp_ns: int = field(default_factory=time.time_ns)
    primary_cause: Optional["AgentShutdownFailure"] = None
    secondary_failures: Tuple["AgentShutdownFailure", ...] = field(default_factory=tuple)
    escalation_state: str = ""
    terminal_state_evidence: Dict[str, Any] = field(default_factory=dict)
    retry_eligible: bool = False
    
    @property
    def timestamp_utc(self) -> datetime:
        """Return UTC timestamp from ns time."""
        return datetime.utcfromtimestamp(self.timestamp_ns / 1_000_000_000.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for diagnostics."""
        result = {
            "failure_id": self.failure_id[:8] if len(self.failure_id) > 8 else self.failure_id,
            "type_name": self.type_name,
            "message": self.message[:100],
            "phase": self.phase,
            "authority": self.authority,
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "primary_cause_failure_id": self.primary_cause.failure_id[:8] if self.primary_cause else None,
            "secondary_count": len(self.secondary_failures),
            "escalation_state": self.escalation_state,
            "retry_eligible": self.retry_eligible,
        }
        
        return result


class AgentShutdownPhaseError(AgentShutdownFailure):
    """Raised when a phase transition is invalid."""
    
    def __init__(self, from_phase: str, to_phase: str, **kwargs):
        message = f"Invalid phase transition from {from_phase} to {to_phase}"
        super().__init__(
            type_name="AgentShutdownPhaseError",
            message=message,
            **kwargs
        )
        self.from_phase = from_phase
        self.to_phase = to_phase


class AgentCoreShutdownInvocationError(AgentShutdownFailure):
    """Raised when Core shutdown invocation fails."""
    
    pass


class AgentCoreShutdownValidationError(AgentShutdownFailure):
    """Raised when Core shutdown result validation fails."""
    
    pass


class AgentGracefulShutdownError(AgentShutdownFailure):
    """Raised during graceful shutdown failure."""
    
    pass


class AgentForcedShutdownError(AgentShutdownFailure):
    """Raised during forced shutdown failure."""
    
    pass


class AgentTerminalVerificationError(AgentShutdownFailure):
    """Raised when terminal-state verification fails."""
    
    pass