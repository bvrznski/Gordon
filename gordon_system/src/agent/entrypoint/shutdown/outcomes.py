"""Gordon Agent Shutdown Outcomes.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination
======================================================

Shutdown outcome enumeration and ownership state tracking.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple


# =============================================================================
# SHUTDOWN OUTCOME MODEL
# =============================================================================


class AgentShutdownOutcome(Enum):
    """Explicit shutdown outcomes.
    
    Semantics:
        SHUTDOWN_COMPLETE: Canonical runtime shutdown and terminal-state 
                          verification succeeded
        SHUTDOWN_COMPLETE_WITH_RESIDUALS: Terminal shutdown completed under 
                                          policy, but bounded residual evidence remains
        SHUTDOWN_FORCED: Graceful shutdown did not complete and canonical forced 
                         shutdown succeeded
        SHUTDOWN_FAILED: The runtime could not be brought to an accepted terminal state
        SHUTDOWN_CANCELLED: Shutdown was cancelled before entering an irreversible 
                           or mandatory containment boundary
        SHUTDOWN_TIMED_OUT: The shutdown transaction exceeded its approved total deadline
        ALREADY_SHUT_DOWN: The target runtime was already terminal and identity 
                          verification succeeded
        SHUTDOWN_IN_PROGRESS: Another valid shutdown transaction owns the target 
                            runtime shutdown
        INVALID_RUNTIME: The target runtime identity or ownership evidence is invalid
    """
    
    # Success states
    SHUTDOWN_COMPLETE = "shutdown_complete"
    SHUTDOWN_COMPLETE_WITH_RESIDUALS = "shutdown_complete_with_residuals"
    ALREADY_SHUT_DOWN = "already_shut_down"
    
    # Failure states
    SHUTDOWN_FAILED = "shutdown_failed"
    SHUTDOWN_FORCED = "shutdown_forced"
    SHUTDOWN_CANCELLED = "shutdown_cancelled"
    SHUTDOWN_TIMED_OUT = "shutdown_timed_out"
    
    # Duplicate/invalid states
    SHUTDOWN_IN_PROGRESS = "shutdown_in_progress"
    INVALID_RUNTIME = "invalid_runtime"


# =============================================================================
# OWNERSHIP STATE TRACKING
# =============================================================================


class AgentShutdownOwnershipState(Enum):
    """Runtime ownership state during shutdown transaction.
    
    States:
        OPERATIONAL: Runtime is currently under operational control
        TRANSFERRING: Ownership transfer in progress
        SHUTDOWN_OWNED: Shutdown authority now owns the runtime
        ALREADY_SHUTDOWN_OWNED: Runtime was already shutdown-owned
    """
    
    OPERATIONAL = "operational"
    TRANSFERRING = "transferring"
    SHUTDOWN_OWNED = "shutdown_owned"
    ALREADY_SHUTDOWN_OWNED = "already_shutdown_owned"


@dataclass(frozen=True)
class AgentShutdownOwnershipTransfer:
    """Records an ownership transfer from operational to shutdown control.
    
    Args:
        from_owner: Previous owner (e.g., "operational_runner")
        to_owner: New owner (always "shutdown_coordinator" for this module)
        timestamp_ns: When transfer occurred
        runtime_id: Runtime being transferred
        boot_session_id: Boot session at time of transfer
        accepted: Whether transfer was accepted by shutdown coordinator
    """
    
    from_owner: str
    to_owner: str = "shutdown_coordinator"
    timestamp_ns: int = field(default_factory=time.time_ns)
    runtime_id: str = ""
    boot_session_id: str = ""
    accepted: bool = True
    
    @property
    def timestamp_utc(self) -> datetime:
        """Return UTC timestamp from ns time."""
        return datetime.utcfromtimestamp(self.timestamp_ns / 1_000_000_000.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for diagnostics."""
        return {
            "from_owner": self.from_owner,
            "to_owner": self.to_owner,
            "timestamp_utc": self.timestamp_utc.isoformat() if hasattr(self, '_timestamp') else str(self.timestamp_ns),
            "runtime_id": self.runtime_id[:8] if self.runtime_id else "",
            "boot_session_id": self.boot_session_id[:8] if self.boot_session_id else "",
            "accepted": self.accepted,
        }


# =============================================================================
# TERMINAL STATE MODEL
# =============================================================================


class AgentTerminalState(Enum):
    """Terminal runtime states.
    
    States:
        TERMINATED_CLEAN: All cleanup completed successfully
        TERMINATED_WITH_RESIDUALS: Terminal shutdown completed but residuals remain
        TERMINATED_FORCED: Forced termination (graceful failed)
        TERMINATION_FAILED: Runtime could not reach terminal state
        TERMINATION_UNKNOWN: Cannot determine terminal state
    """
    
    TERMINATED_CLEAN = "terminated_clean"
    TERMINATED_WITH_RESIDUALS = "terminated_with_residuals"
    TERMINATED_FORCED = "terminated_forced"
    TERMINATION_FAILED = "termination_failed"
    TERMINATION_UNKNOWN = "terminal_unknown"


@dataclass(frozen=True)
class AgentTerminalStateEvidence:
    """Evidence supporting terminal state determination.
    
    Args:
        is_terminal: Whether runtime is in terminal state
        admission_closed: Whether admission was closed
        intake_fenced: Whether intake was fenced
        scheduler_terminal: Whether Scheduler is terminal
        executor_terminal: Whether Executor is terminal
        workers_terminal: Whether workers are terminal or have residuals
        components_stopped: All components stopped or explicitly residual
        runtime_state_terminal: Runtime state is terminal
    """
    
    is_terminal: bool = False
    admission_closed: bool = False
    intake_fenced: bool = False
    scheduler_terminal: bool = False
    executor_terminal: bool = False
    workers_terminal: bool = False
    components_stopped: Tuple[str, ...] = field(default_factory=tuple)
    residuals: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def is_clean(self) -> bool:
        """Check if terminal state was achieved cleanly (no residuals)."""
        return self.is_terminal and len(self.residuals) == 0
    
    @classmethod
    def from_core_result(cls, core_result: Dict[str, Any]) -> "AgentTerminalStateEvidence":
        """Derive evidence from Core shutdown result.
        
        Args:
            core_result: Result from Core shutdown authority
            
        Returns:
            AgentTerminalStateEvidence based on Core evidence
        """
        return cls(
            is_terminal=core_result.get("terminated", False),
            admission_closed=core_result.get("admission_closed", False),
            intake_fenced=core_result.get("intake_fenced", False),
            scheduler_terminal=core_result.get("scheduler_terminal", False),
            executor_terminal=core_result.get("executor_terminal", False),
            workers_terminal=core_result.get("workers_terminal", False),
        )


@dataclass(frozen=True)
class AgentResidualResource:
    """Represents a residual resource that could not be fully cleaned.
    
    Args:
        residual_id: Unique identifier for this residual
        type: Resource type (worker, socket, model_context, gpu_allocation, etc.)
        owner: Owner of the resource
        runtime_id: Runtime it belonged to
        cleanup_status: "released" or "residual"
        severity: "info", "warning", or "error"
        safety_impact: Description of potential safety impact
        retry_eligible: Whether this can be retried
        operator_guidance: Guidance for human operators
    """
    
    residual_id: str
    type: str  # worker, socket, model_context, gpu_allocation, etc.
    owner: str
    runtime_id: str = ""
    cleanup_status: str = "residual"
    severity: str = "warning"
    safety_impact: str = ""
    retry_eligible: bool = False
    operator_guidance: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for diagnostics."""
        return {
            "residual_id": self.residual_id[:8] if len(self.residual_id) > 8 else self.residual_id,
            "type": self.type,
            "owner": self.owner[:8] if len(self.owner) > 8 else self.owner,
            "runtime_id": self.runtime_id[:8] if self.runtime_id else "",
            "cleanup_status": self.cleanup_status,
            "severity": self.severity,
            "safety_impact": self.safety_impact[:100],  # Bounded
            "retry_eligible": self.retry_eligible,
        }