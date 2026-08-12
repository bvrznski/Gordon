"""Gordon Agent Startup Exceptions.

Phase 3.7.33-I: Agent Startup Coordination
==========================================

Typed exception hierarchy for startup coordination failures.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Tuple


@dataclass(frozen=True)
class AgentStartupFailure:
    """Immutable failure record for a startup transaction.
    
    This is the canonical output contract for failed startups. It contains
    full diagnostic information while preserving the primary failure and
    maintaining rollback eligibility evidence.
    """
    
    # Identity
    startup_id: str
    """Unique startup operation ID."""
    
    launch_id: str
    """Launch session ID from request."""
    
    process_id: int
    """Process ID where failure occurred."""
    
    preflight_id: Optional[str]
    """Preflight execution ID if applicable."""
    
    init_id: Optional[str]
    """Initialization execution ID if applicable."""
    
    runtime_id: Optional[str]
    """Runtime identity (if assigned before failure)."""
    
    boot_session_id: Optional[str]
    """Boot session identifier (if created)."""
    
    # Failure classification
    failed_phase: str
    """The startup phase that failed."""
    
    failure_category: str
    """Category of failure (request, policy, context, preflight, init, etc.)."""
    
    primary_failure_message: str
    """Primary failure message or exception description."""
    
    primary_failure_type: Optional[str]
    """Type/class name of the primary exception if available."""
    
    # Secondary failures (non-cascading)
    secondary_failures: Tuple[str, ...]
    """Secondary failure messages that did not cascade."""
    
    # Recovery evidence
    partial_construction_summary: str
    """Summary of what was partially constructed before failure."""
    
    rollback_eligible: bool
    """Whether rollback is eligible for this failure."""
    
    shutdown_eligible: bool
    """Whether shutdown is eligible for this failure."""
    
    retry_eligible: bool
    """Whether startup can be retried."""
    
    # Diagnostics reference (bounded, secret-safe)
    diagnostics_ref: Optional[str]
    """Reference to detailed diagnostics if available."""
    
    # Provenance
    timestamp_ns: int
    """Unix timestamp in nanoseconds when failure occurred."""
    
    @classmethod
    def create(
        cls,
        startup_id: str,
        launch_id: str,
        process_id: int,
        failed_phase: str,
        failure_category: str,
        primary_failure_message: str,
        preflight_id: Optional[str] = None,
        init_id: Optional[str] = None,
        runtime_id: Optional[str] = None,
        boot_session_id: Optional[str] = None,
        secondary_failures: Optional[Tuple[str, ...]] = None,
        partial_construction_summary: str = "none",
        rollback_eligible: bool = True,
        shutdown_eligible: bool = False,
        retry_eligible: bool = False,
    ) -> "AgentStartupFailure":
        """Create a new startup failure record.
        
        Args:
            startup_id: Unique startup operation ID
            launch_id: Launch session ID from request
            process_id: Process ID where failure occurred
            failed_phase: The startup phase that failed
            failure_category: Category of failure
            primary_failure_message: Primary failure message
            preflight_id: Preflight execution ID if applicable
            init_id: Initialization execution ID if applicable
            runtime_id: Runtime identity (if assigned)
            boot_session_id: Boot session identifier (if created)
            secondary_failures: Secondary failure messages
            partial_construction_summary: Summary of what was constructed
            rollback_eligible: Whether rollback is eligible
            shutdown_eligible: Whether shutdown is eligible
            retry_eligible: Whether startup can be retried
            
        Returns:
            New AgentStartupFailure instance
        """
        now_ns = time.time_ns()
        
        return cls(
            startup_id=startup_id,
            launch_id=launch_id,
            process_id=process_id,
            preflight_id=preflight_id,
            init_id=init_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            failed_phase=failed_phase,
            failure_category=failure_category,
            primary_failure_message=primary_failure_message,
            primary_failure_type=None,  # Would be set in full implementation
            secondary_failures=secondary_failures or (),
            partial_construction_summary=partial_construction_summary,
            rollback_eligible=rollback_eligible,
            shutdown_eligible=shutdown_eligible,
            retry_eligible=retry_eligible,
            diagnostics_ref=None,
            timestamp_ns=now_ns,
        )


class AgentStartupError(Exception):
    """Base exception for startup coordination errors.
    
    This is the root of the startup exception hierarchy. All startup-related
    exceptions should inherit from this class to enable proper error handling.
    """
    
    def __init__(
        self,
        message: str,
        startup_id: Optional[str] = None,
        launch_id: Optional[str] = None,
        process_id: Optional[int] = None,
        failed_phase: Optional[str] = None,
        failure_category: Optional[str] = None,
        primary_failure_message: Optional[str] = None,
    ):
        """Initialize the exception.
        
        Args:
            message: Error message
            startup_id: Startup operation ID if available
            launch_id: Launch session ID if available
            process_id: Process ID if available
            failed_phase: Phase that failed if known
            failure_category: Category of failure if known
            primary_failure_message: Primary failure message if available
        """
        self.startup_id = startup_id
        self.launch_id = launch_id
        self.process_id = process_id
        self.failed_phase = failed_phase
        self.failure_category = failure_category
        self.primary_failure_message = primary_failure_message
        
        super().__init__(message)


class AgentStartupRequestError(AgentStartupError):
    """Exception raised when startup request validation fails."""
    
    pass


class AgentStartupPolicyError(AgentStartupError):
    """Exception raised when startup policy resolution fails."""
    
    pass


class AgentStartupContextError(AgentStartupError):
    """Exception raised when startup context construction fails."""
    
    pass


class AgentStartupPhaseError(AgentStartupError):
    """Exception raised when an invalid phase transition occurs."""
    
    pass


class AgentStartupPreflightInvocationError(AgentStartupError):
    """Exception raised when preflight invocation fails."""
    
    pass


class AgentStartupPreflightValidationError(AgentStartupError):
    """Exception raised when preflight result validation fails."""
    
    pass


class AgentStartupInitializationInvocationError(AgentStartupError):
    """Exception raised when initialization invocation fails."""
    
    pass


class AgentStartupInitializationValidationError(AgentStartupError):
    """Exception raised when initialization result validation fails."""
    
    pass


class AgentStartupOwnershipTransferError(AgentStartupError):
    """Exception raised when ownership transfer fails."""
    
    pass


class AgentStartupHandoffError(AgentStartupError):
    """Exception raised when handoff verification fails."""
    
    pass


class AgentStartupRollbackHandoffError(AgentStartupError):
    """Exception raised when rollback handoff fails."""
    
    pass


class AgentStartupShutdownHandoffError(AgentStartupError):
    """Exception raised when shutdown handoff fails."""
    
    pass


class AgentStartupCancellationError(AgentStartupError):
    """Exception raised when startup is cancelled."""
    
    pass


class AgentStartupTimeoutError(AgentStartupError):
    """Exception raised when startup exceeds a deadline."""
    
    def __init__(
        self,
        message: str,
        startup_id: Optional[str] = None,
        launch_id: Optional[str] = None,
        process_id: Optional[int] = None,
        failed_phase: Optional[str] = None,
        failure_category: Optional[str] = None,
        deadline_seconds: Optional[float] = None,
    ):
        """Initialize the timeout exception.
        
        Args:
            message: Error message
            startup_id: Startup operation ID if available
            launch_id: Launch session ID if available
            process_id: Process ID if available
            failed_phase: Phase that timed out if known
            failure_category: Category of failure if known
            deadline_seconds: The deadline that was exceeded if known
        """
        self.deadline_seconds = deadline_seconds
        super().__init__(
            message,
            startup_id,
            launch_id,
            process_id,
            failed_phase,
            failure_category,
        )


class AgentStartupInternalError(AgentStartupError):
    """Exception raised for internal startup coordinator errors."""
    
    pass


__all__ = [
    "AgentStartupFailure",
    # Exception classes
    "AgentStartupError",
    "AgentStartupRequestError",
    "AgentStartupPolicyError",
    "AgentStartupContextError",
    "AgentStartupPhaseError",
    "AgentStartupPreflightInvocationError",
    "AgentStartupPreflightValidationError",
    "AgentStartupInitializationInvocationError",
    "AgentStartupInitializationValidationError",
    "AgentStartupOwnershipTransferError",
    "AgentStartupHandoffError",
    "AgentStartupRollbackHandoffError",
    "AgentStartupShutdownHandoffError",
    "AgentStartupCancellationError",
    "AgentStartupTimeoutError",
    "AgentStartupInternalError",
]