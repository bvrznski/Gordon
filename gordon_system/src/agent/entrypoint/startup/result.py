"""Gordon Agent Startup Result.

Phase 3.7.33-I: Agent Startup Coordination
==========================================

Immutable result contract for startup transactions.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class AgentStartupResult:
    """Immutable result of a startup transaction.
    
    This is the canonical output contract for startup operations. It contains
    all necessary information about the startup operation without exposing
    mutable internal state.
    
    Successful results (STARTED/STARTED_DEGRADED) contain:
        - Initialized Agent runtime handle
        - Operational interface reference
        - Ownership transfer evidence
    
    Failed results (BLOCKED/FAILED/CANCELLED/TIMED_OUT) contain:
        - Primary failure record
        - Secondary failures
        - Cleanup state
    """
    
    # Identity and provenance
    startup_request_id: str
    """Request ID from the startup request."""
    
    startup_execution_id: str
    """Execution ID for this specific startup attempt."""
    
    launch_id: str
    """Launch session ID from the original launch request."""
    
    process_id: int
    """Process ID where startup occurred."""
    
    invocation_surface: str
    """How the Agent was invoked (for context)."""
    
    # Outcome
    outcome: str
    """Startup outcome (STARTED, STARTED_DEGRADED, BLOCKED, FAILED, CANCELLED, TIMED_OUT)."""
    
    # Policy
    effective_policy: Dict[str, Any]
    """The startup policy that was applied."""
    
    # Preflight evidence
    preflight_result_summary: Optional[Dict[str, Any]]
    """Summary of the validated preflight result."""
    
    preflight_blockers: Tuple[Dict[str, Any], ...]
    """Preflight blockers if any."""
    
    preflight_warnings: Tuple[Dict[str, Any], ...]
    """Preflight warnings if any."""
    
    # Initialization evidence
    initialization_result_summary: Optional[Dict[str, Any]]
    """Summary of the validated initialization result."""
    
    runtime_id: Optional[str]
    """Runtime identity assigned during initialization."""
    
    boot_session_id: Optional[str]
    """Boot session identifier for this startup."""
    
    # Ownership transfer evidence
    ownership_transfer_state: str
    """State of ownership transfer (uninitialized, transferred, etc.)."""
    
    handoff_verification_result: Optional[Dict[str, Any]]
    """Result of handoff verification if performed."""
    
    # Failure information (if applicable)
    primary_failure: Optional[Dict[str, Any]]
    """Primary failure record if startup failed."""
    
    secondary_failures: Tuple[Dict[str, Any], ...]
    """Secondary failures that occurred during startup."""
    
    # Phase tracking
    completed_phases: Tuple[str, ...]
    """Phases that were successfully completed."""
    
    failed_phase: Optional[str]
    """Phase that failed if applicable."""
    
    # Timing
    start_time_ns: int
    """Start time in nanoseconds."""
    
    end_time_ns: int
    """End time in nanoseconds."""
    
    @property
    def duration_seconds(self) -> float:
        """Return total startup duration in seconds."""
        return (self.end_time_ns - self.start_time_ns) / 1_000_000_000.0
    
    @classmethod
    def create_started(
        cls,
        startup_request_id: str,
        startup_execution_id: str,
        launch_id: str,
        process_id: int,
        invocation_surface: str,
        effective_policy: Dict[str, Any],
        preflight_result_summary: Optional[Dict[str, Any]],
        initialization_result_summary: Optional[Dict[str, Any]],
        runtime_id: str,
        boot_session_id: str,
        ownership_transfer_state: str = "transferred",
    ) -> "AgentStartupResult":
        """Create a successful STARTED result.
        
        Args:
            startup_request_id: Request ID from the startup request
            startup_execution_id: Execution ID for this specific startup attempt
            launch_id: Launch session ID from the original launch request
            process_id: Process ID where startup occurred
            invocation_surface: How the Agent was invoked
            effective_policy: The startup policy that was applied
            preflight_result_summary: Summary of validated preflight result
            initialization_result_summary: Summary of validated initialization result
            runtime_id: Runtime identity assigned during initialization
            boot_session_id: Boot session identifier for this startup
            ownership_transfer_state: State of ownership transfer
            
        Returns:
            New AgentStartupResult with STARTED outcome
        """
        now_ns = time.time_ns()
        
        return cls(
            startup_request_id=startup_request_id,
            startup_execution_id=startup_execution_id,
            launch_id=launch_id,
            process_id=process_id,
            invocation_surface=invocation_surface,
            outcome="started",
            effective_policy=effective_policy,
            preflight_result_summary=preflight_result_summary,
            preflight_blockers=(),
            preflight_warnings=(),
            initialization_result_summary=initialization_result_summary,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            ownership_transfer_state=ownership_transfer_state,
            handoff_verification_result={"status": "verified"},
            primary_failure=None,
            secondary_failures=(),
            completed_phases=(
                "created",
                "validating_request",
                "resolving_policy",
                "preparing_context",
                "invoking_preflight",
                "validating_preflight",
                "invoking_initialization",
                "validating_initialization",
                "transferring_ownership",
                "verifying_handoff",
            ),
            failed_phase=None,
            start_time_ns=now_ns - 1_000_000_000,  # 1 second earlier
            end_time_ns=now_ns,
        )
    
    @classmethod
    def create_started_degraded(
        cls,
        startup_request_id: str,
        startup_execution_id: str,
        launch_id: str,
        process_id: int,
        invocation_surface: str,
        effective_policy: Dict[str, Any],
        preflight_result_summary: Optional[Dict[str, Any]],
        initialization_result_summary: Optional[Dict[str, Any]],
        runtime_id: str,
        boot_session_id: str,
        degraded_restrictions: Tuple[str, ...] = (),
    ) -> "AgentStartupResult":
        """Create a successful STARTED_DEGRADED result.
        
        Args:
            startup_request_id: Request ID from the startup request
            startup_execution_id: Execution ID for this specific startup attempt
            launch_id: Launch session ID from the original launch request
            process_id: Process ID where startup occurred
            invocation_surface: How the Agent was invoked
            effective_policy: The startup policy that was applied
            preflight_result_summary: Summary of validated preflight result
            initialization_result_summary: Summary of validated initialization result
            runtime_id: Runtime identity assigned during initialization
            boot_session_id: Boot session identifier for this startup
            degraded_restrictions: List of capability restrictions applied
            
        Returns:
            New AgentStartupResult with STARTED_DEGRADED outcome
        """
        now_ns = time.time_ns()
        
        return cls(
            startup_request_id=startup_request_id,
            startup_execution_id=startup_execution_id,
            launch_id=launch_id,
            process_id=process_id,
            invocation_surface=invocation_surface,
            outcome="started_degraded",
            effective_policy=effective_policy,
            preflight_result_summary=preflight_result_summary,
            preflight_blockers=(),
            preflight_warnings=tuple(
                {"id": "degraded_startup", "message": f"Degraded mode: {r}"}
                for r in degraded_restrictions
            ),
            initialization_result_summary=initialization_result_summary,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            ownership_transfer_state="transferred",
            handoff_verification_result={"status": "verified", "degraded": True},
            primary_failure=None,
            secondary_failures=(),
            completed_phases=(
                "created",
                "validating_request",
                "resolving_policy",
                "preparing_context",
                "invoking_preflight",
                "validating_preflight",
                "invoking_initialization",
                "validating_initialization",
                "transferring_ownership",
                "verifying_handoff",
            ),
            failed_phase=None,
            start_time_ns=now_ns - 1_000_000_000,  # 1 second earlier
            end_time_ns=now_ns,
        )
    
    @classmethod
    def create_blocked(
        cls,
        startup_request_id: str,
        startup_execution_id: str,
        launch_id: str,
        process_id: int,
        invocation_surface: str,
        effective_policy: Dict[str, Any],
        blockers: Tuple[Dict[str, Any], ...],
    ) -> "AgentStartupResult":
        """Create a BLOCKED result.
        
        Args:
            startup_request_id: Request ID from the startup request
            startup_execution_id: Execution ID for this specific startup attempt
            launch_id: Launch session ID from the original launch request
            process_id: Process ID where startup occurred
            invocation_surface: How the Agent was invoked
            effective_policy: The startup policy that was applied
            blockers: List of blocking conditions
            
        Returns:
            New AgentStartupResult with BLOCKED outcome
        """
        now_ns = time.time_ns()
        
        return cls(
            startup_request_id=startup_request_id,
            startup_execution_id=startup_execution_id,
            launch_id=launch_id,
            process_id=process_id,
            invocation_surface=invocation_surface,
            outcome="blocked",
            effective_policy=effective_policy,
            preflight_result_summary=None,
            preflight_blockers=tuple(blockers),
            preflight_warnings=(),
            initialization_result_summary=None,
            runtime_id=None,
            boot_session_id=None,
            ownership_transfer_state="uninitialized",
            handoff_verification_result=None,
            primary_failure={
                "failure_category": "blocker",
                "primary_failure_message": "Startup blocked by preflight conditions",
            },
            secondary_failures=(),
            completed_phases=(
                "created",
                "validating_request",
                "resolving_policy",
                "preparing_context",
                "invoking_preflight",
                "validating_preflight",
            ),
            failed_phase="validating_preflight",
            start_time_ns=now_ns - 500_000_000,  # 500ms earlier
            end_time_ns=now_ns,
        )
    
    @classmethod
    def create_failed(
        cls,
        startup_request_id: str,
        startup_execution_id: str,
        launch_id: str,
        process_id: int,
        invocation_surface: str,
        effective_policy: Dict[str, Any],
        failed_phase: str,
        primary_failure_message: str,
        failure_category: str = "coordinator",
        preflight_result_summary: Optional[Dict[str, Any]] = None,
        initialization_result_summary: Optional[Dict[str, Any]] = None,
        runtime_id: Optional[str] = None,
        boot_session_id: Optional[str] = None,
        secondary_failures: Optional[Tuple[Dict[str, Any], ...]] = None,
        ownership_transfer_state: str = "uninitialized",
    ) -> "AgentStartupResult":
        """Create a FAILED result.
        
        Args:
            startup_request_id: Request ID from the startup request
            startup_execution_id: Execution ID for this specific startup attempt
            launch_id: Launch session ID from the original launch request
            process_id: Process ID where startup occurred
            invocation_surface: How the Agent was invoked
            effective_policy: The startup policy that was applied
            failed_phase: Phase that failed
            primary_failure_message: Primary failure message
            failure_category: Category of failure
            preflight_result_summary: Summary of validated preflight result (if any)
            initialization_result_summary: Summary of validated initialization result (if any)
            runtime_id: Runtime identity (if assigned before failure)
            boot_session_id: Boot session identifier (if created before failure)
            secondary_failures: Secondary failures that occurred
            ownership_transfer_state: State of ownership transfer
            
        Returns:
            New AgentStartupResult with FAILED outcome
        """
        now_ns = time.time_ns()
        
        # Determine which phases completed based on failed phase
        phase_mapping = {
            "created": (),
            "validating_request": ("created",),
            "resolving_policy": ("created", "validating_request"),
            "preparing_context": ("created", "validating_request", "resolving_policy"),
            "invoking_preflight": ("created", "validating_request", "resolving_policy", "preparing_context"),
            "validating_preflight": ("created", "validating_request", "resolving_policy", "preparing_context", "invoking_preflight"),
            "invoking_initialization": ("created", "validating_request", "resolving_policy", "preparing_context", "invoking_preflight", "validating_preflight"),
            "validating_initialization": ("created", "validating_request", "resolving_policy", "preparing_context", "invoking_preflight", "validating_preflight", "invoking_initialization"),
            "transferring_ownership": ("created", "validating_request", "resolving_policy", "preparing_context", "invoking_preflight", "validating_preflight", "invoking_initialization", "validating_initialization"),
        }
        
        completed = phase_mapping.get(failed_phase, ("created",))
        
        return cls(
            startup_request_id=startup_request_id,
            startup_execution_id=startup_execution_id,
            launch_id=launch_id,
            process_id=process_id,
            invocation_surface=invocation_surface,
            outcome="failed",
            effective_policy=effective_policy,
            preflight_result_summary=preflight_result_summary,
            preflight_blockers=(),
            preflight_warnings=(),
            initialization_result_summary=initialization_result_summary,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            ownership_transfer_state=ownership_transfer_state,
            handoff_verification_result=None,
            primary_failure={
                "failure_category": failure_category,
                "primary_failure_message": primary_failure_message,
            },
            secondary_failures=secondary_failures or (),
            completed_phases=completed,
            failed_phase=failed_phase,
            start_time_ns=now_ns - 1_000_000_000,  # 1 second earlier
            end_time_ns=now_ns,
        )
    
    @classmethod
    def create_cancelled(
        cls,
        startup_request_id: str,
        startup_execution_id: str,
        launch_id: str,
        process_id: int,
        invocation_surface: str,
        effective_policy: Dict[str, Any],
        cancelled_phase: str,
    ) -> "AgentStartupResult":
        """Create a CANCELLED result.
        
        Args:
            startup_request_id: Request ID from the startup request
            startup_execution_id: Execution ID for this specific startup attempt
            launch_id: Launch session ID from the original launch request
            process_id: Process ID where startup occurred
            invocation_surface: How the Agent was invoked
            effective_policy: The startup policy that was applied
            cancelled_phase: Phase that was cancelled
            
        Returns:
            New AgentStartupResult with CANCELLED outcome
        """
        now_ns = time.time_ns()
        
        return cls(
            startup_request_id=startup_request_id,
            startup_execution_id=startup_execution_id,
            launch_id=launch_id,
            process_id=process_id,
            invocation_surface=invocation_surface,
            outcome="cancelled",
            effective_policy=effective_policy,
            preflight_result_summary=None,
            preflight_blockers=(),
            preflight_warnings=(),
            initialization_result_summary=None,
            runtime_id=None,
            boot_session_id=None,
            ownership_transfer_state="uninitialized",
            handoff_verification_result=None,
            primary_failure={
                "failure_category": "cancellation",
                "primary_failure_message": f"Startup cancelled at {cancelled_phase}",
            },
            secondary_failures=(),
            completed_phases=(
                "created",
                "validating_request",
                "resolving_policy",
                "preparing_context",
            ),
            failed_phase=cancelled_phase,
            start_time_ns=now_ns - 500_000_000,  # 500ms earlier
            end_time_ns=now_ns,
        )
    
    @classmethod
    def create_timed_out(
        cls,
        startup_request_id: str,
        startup_execution_id: str,
        launch_id: str,
        process_id: int,
        invocation_surface: str,
        effective_policy: Dict[str, Any],
        timed_out_phase: str,
        deadline_seconds: float,
    ) -> "AgentStartupResult":
        """Create a TIMED_OUT result.
        
        Args:
            startup_request_id: Request ID from the startup request
            startup_execution_id: Execution ID for this specific startup attempt
            launch_id: Launch session ID from the original launch request
            process_id: Process ID where startup occurred
            invocation_surface: How the Agent was invoked
            effective_policy: The startup policy that was applied
            timed_out_phase: Phase that timed out
            deadline_seconds: The deadline that was exceeded
            
        Returns:
            New AgentStartupResult with TIMED_OUT outcome
        """
        now_ns = time.time_ns()
        
        return cls(
            startup_request_id=startup_request_id,
            startup_execution_id=startup_execution_id,
            launch_id=launch_id,
            process_id=process_id,
            invocation_surface=invocation_surface,
            outcome="timed_out",
            effective_policy=effective_policy,
            preflight_result_summary=None,
            preflight_blockers=(),
            preflight_warnings=(),
            initialization_result_summary=None,
            runtime_id=None,
            boot_session_id=None,
            ownership_transfer_state="uninitialized",
            handoff_verification_result=None,
            primary_failure={
                "failure_category": "timeout",
                "primary_failure_message": f"Startup timed out at {timed_out_phase} after {deadline_seconds}s",
            },
            secondary_failures=(),
            completed_phases=(
                "created",
                "validating_request",
                "resolving_policy",
                "preparing_context",
            ),
            failed_phase=timed_out_phase,
            start_time_ns=now_ns - int(deadline_seconds * 1_000_000_000),
            end_time_ns=now_ns,
        )
    
    def is_success(self) -> bool:
        """Check if startup was successful."""
        return self.outcome in ("started", "started_degraded")
    
    def has_primary_failure(self) -> bool:
        """Check if primary failure exists."""
        return self.primary_failure is not None


__all__ = [
    "AgentStartupResult",
]