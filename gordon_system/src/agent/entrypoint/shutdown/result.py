"""Gordon Agent Shutdown Result.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination
======================================================

Immutable shutdown result returned to the process entrypoint.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple


# Import types from outcomes module
from .outcomes import AgentShutdownOutcome


# =============================================================================
# SHUTDOWN RESULT
# =============================================================================


@dataclass(frozen=True)
class AgentShutdownResult:
    """Immutable shutdown result returned to process entrypoint.
    
    A successful result should preserve applicable:
        - shutdown request ID
        - shutdown execution ID
        - shutdown intent ID
        - process ID, launch ID, startup ID
        - runtime ID, boot-session ID
        - outcome (SHUTDOWN_COMPLETE, etc.)
        - effective shutdown policy
        - Core shutdown result or bounded summary
        - admission-close result
        - graceful-shutdown result
        - escalation evidence
        - forced-shutdown result
        - terminal-state evidence
        - residual resources
        - warnings
        - phase history
        - start/end time, duration
        - process-exit recommendation
        - provenance
    
    A non-success result should additionally preserve:
        - primary failure
        - secondary failures
        - failed phase
        - cancellation evidence
        - timeout evidence
        - residual ownership state
        - retry eligibility
        - operator guidance
    
    Architecture boundaries:
        This owns:
            - Result identity and immutable artifacts
            - Evidence for verification
        
        This does NOT own:
            - Mutable Core internals
            - Active runtime handles
            - Component instances
    """
    
    # Identity and provenance
    request_id: str
    """Shutdown request ID."""
    
    execution_id: str
    """Shutdown execution ID."""
    
    intent_id: str
    """Intent ID from the original shutdown intent."""
    
    process_id: int
    """Process where shutdown occurred."""
    
    launch_id: str
    """Launch session ID."""
    
    startup_id: str
    """Startup operation ID."""
    
    runtime_id: str
    """Runtime that was shut down."""
    
    boot_session_id: str
    """Boot session for this runtime."""
    
    # Outcome and policy
    outcome: AgentShutdownOutcome
    """Final shutdown outcome."""
    
    effective_policy: Dict[str, Any]
    """Effective shutdown policy used."""
    
    requested_urgency: Optional[str] = None
    """Urgency requested in the intent."""
    
    effective_urgency: Optional[str] = None
    """Urgency that was effectively applied."""
    
    # Core shutdown result (bounded summary)
    core_shutdown_result_summary: Optional[Dict[str, Any]] = None
    
    admission_close_result: Optional[Dict[str, Any]] = None
    
    graceful_shutdown_result: Optional[Dict[str, Any]] = None
    escalation_evidence: Optional[Dict[str, Any]] = None
    
    forced_shutdown_result: Optional[Dict[str, Any]] = None
    
    terminal_state_evidence: Optional[Dict[str, Any]] = None
    
    # Residuals and warnings
    residual_resources: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Phase history (for diagnostics)
    phase_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timing
    start_time_ns: int = field(default_factory=time.time_ns)
    end_time_ns: Optional[int] = None
    
    @property
    def duration_seconds(self) -> float:
        """Return total shutdown duration in seconds."""
        if self.end_time_ns is not None:
            return (self.end_time_ns - self.start_time_ns) / 1_000_000_000.0
        return (time.time_ns() - self.start_time_ns) / 1_000_000_000.0
    
    @property
    def start_time_utc(self) -> datetime:
        """Return UTC start time."""
        return datetime.utcfromtimestamp(self.start_time_ns / 1_000_000_000.0)
    
    @property
    def end_time_utc(self) -> Optional[datetime]:
        """Return UTC end time (if available)."""
        if self.end_time_ns is not None:
            return datetime.utcfromtimestamp(self.end_time_ns / 1_000_000_000.0)
        return None
    
    # Failure information
    primary_failure: Optional[Dict[str, Any]] = None
    
    secondary_failures: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    failed_phase: Optional[str] = None
    
    cancellation_evidence: Optional[Dict[str, Any]] = None
    
    timeout_evidence: Optional[Dict[str, Any]] = None
    
    # Process integration
    process_exit_recommendation: str = "exit_clean"
    """Recommended process exit action."""
    
    provenance: str = "entrypoint.shutdown.coordinator"
    """Source of the result."""
    
    def __post_init__(self) -> None:
        """Validate result consistency."""
        # Ensure terminal results have evidence
        if self.outcome in (
            AgentShutdownOutcome.SHUTDOWN_COMPLETE,
            AgentShutdownOutcome.SHUTDOWN_FAILED,
        ):
            if self.terminal_state_evidence is None:
                raise ValueError("Terminal outcome requires terminal-state evidence")
        
        # Ensure success outcomes don't have primary failures
        if self.outcome in (
            AgentShutdownOutcome.SHUTDOWN_COMPLETE,
            AgentShutdownOutcome.ALREADY_SHUT_DOWN,
            AgentShutdownOutcome.SHUTDOWN_COMPLETE_WITH_RESIDUALS,
        ):
            if self.primary_failure is not None:
                raise ValueError("Success outcome should not have primary failure")
    
    @classmethod
    def create_completed(
        cls,
        request_id: str,
        execution_id: str,
        intent_id: str,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str,
        boot_session_id: str,
        effective_policy: Dict[str, Any],
        core_shutdown_result_summary: Dict[str, Any],
        terminal_state_evidence: Dict[str, Any],
        phase_history: Tuple[Dict[str, Any], ...] = (),
        residual_resources: Tuple[Dict[str, Any], ...] = (),
        warnings: Tuple[str, ...] = (),
    ) -> "AgentShutdownResult":
        """Create a successful SHUTDOWN_COMPLETE result."""
        return cls(
            request_id=request_id,
            execution_id=execution_id,
            intent_id=intent_id,
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            outcome=AgentShutdownOutcome.SHUTDOWN_COMPLETE,
            effective_policy=effective_policy,
            core_shutdown_result_summary=core_shutdown_result_summary,
            terminal_state_evidence=terminal_state_evidence,
            phase_history=phase_history,
            residual_resources=residual_resources,
            warnings=warnings,
            process_exit_recommendation="exit_clean",
        )
    
    @classmethod
    def create_completed_with_residuals(
        cls,
        request_id: str,
        execution_id: str,
        intent_id: str,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str,
        boot_session_id: str,
        effective_policy: Dict[str, Any],
        core_shutdown_result_summary: Dict[str, Any],
        terminal_state_evidence: Dict[str, Any],
        residual_resources: Tuple[Dict[str, Any], ...] = (),
        warnings: Tuple[str, ...] = (),
    ) -> "AgentShutdownResult":
        """Create a SHUTDOWN_COMPLETE_WITH_RESIDUALS result."""
        return cls(
            request_id=request_id,
            execution_id=execution_id,
            intent_id=intent_id,
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            outcome=AgentShutdownOutcome.SHUTDOWN_COMPLETE_WITH_RESIDUALS,
            effective_policy=effective_policy,
            core_shutdown_result_summary=core_shutdown_result_summary,
            terminal_state_evidence=terminal_state_evidence,
            residual_resources=residual_resources,
            warnings=warnings,
            process_exit_recommendation="exit_clean",
        )
    
    @classmethod
    def create_failed(
        cls,
        request_id: str,
        execution_id: str,
        intent_id: str,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str,
        boot_session_id: str,
        effective_policy: Dict[str, Any],
        primary_failure: Dict[str, Any],
        phase: Optional[str] = None,
        secondary_failures: Tuple[Dict[str, Any], ...] = (),
    ) -> "AgentShutdownResult":
        """Create a SHUTDOWN_FAILED result."""
        return cls(
            request_id=request_id,
            execution_id=execution_id,
            intent_id=intent_id,
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            outcome=AgentShutdownOutcome.SHUTDOWN_FAILED,
            effective_policy=effective_policy,
            primary_failure=primary_failure,
            secondary_failures=secondary_failures,
            failed_phase=phase,
            process_exit_recommendation="exit_unclean",
        )
    
    @classmethod
    def create_timed_out(
        cls,
        request_id: str,
        execution_id: str,
        intent_id: str,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str,
        boot_session_id: str,
        effective_policy: Dict[str, Any],
        deadline_seconds: float,
    ) -> "AgentShutdownResult":
        """Create a SHUTDOWN_TIMED_OUT result."""
        return cls(
            request_id=request_id,
            execution_id=execution_id,
            intent_id=intent_id,
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            outcome=AgentShutdownOutcome.SHUTDOWN_TIMED_OUT,
            effective_policy=effective_policy,
            timeout_evidence={
                "deadline_seconds": deadline_seconds,
                "elapsed_seconds": 0.0,
            },
            process_exit_recommendation="exit_unclean",
        )
    
    @classmethod
    def create_invalid_runtime(
        cls,
        request_id: str,
        execution_id: str,
        intent_id: str,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str = "",
        boot_session_id: str = "",
        effective_policy: Optional[Dict[str, Any]] = None,
    ) -> "AgentShutdownResult":
        """Create an INVALID_RUNTIME result."""
        return cls(
            request_id=request_id,
            execution_id=execution_id,
            intent_id=intent_id,
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id or "unknown",
            boot_session_id=boot_session_id or "unknown",
            outcome=AgentShutdownOutcome.INVALID_RUNTIME,
            effective_policy=effective_policy or {},
            primary_failure={
                "failure_id": str(uuid.uuid4()),
                "type_name": "InvalidRuntimeError",
                "message": f"Invalid runtime identity: {runtime_id}",
                "phase": "VALIDATING_RUNTIME_IDENTITY",
            },
            process_exit_recommendation="exit_unclean",
        )
    
    @classmethod
    def create_already_terminal(
        cls,
        request_id: str,
        execution_id: str,
        intent_id: str,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str,
        boot_session_id: str,
        effective_policy: Dict[str, Any],
    ) -> "AgentShutdownResult":
        """Create an ALREADY_SHUT_DOWN result."""
        return cls(
            request_id=request_id,
            execution_id=execution_id,
            intent_id=intent_id,
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            outcome=AgentShutdownOutcome.ALREADY_SHUT_DOWN,
            effective_policy=effective_policy,
            terminal_state_evidence={
                "is_terminal": True,
                "admission_closed": True,
                "intake_fenced": True,
            },
            process_exit_recommendation="exit_clean",
        )
    
    @classmethod
    def create_in_progress(
        cls,
        request_id: str,
        existing_execution_id: str,
        intent_id: str,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str,
        boot_session_id: str,
        effective_policy: Dict[str, Any],
    ) -> "AgentShutdownResult":
        """Create a SHUTDOWN_IN_PROGRESS result."""
        return cls(
            request_id=request_id,
            execution_id=existing_execution_id,
            intent_id=intent_id,
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            outcome=AgentShutdownOutcome.SHUTDOWN_IN_PROGRESS,
            effective_policy=effective_policy,
            primary_failure={
                "failure_id": str(uuid.uuid4()),
                "type_name": "DuplicateShutdownError",
                "message": f"Shutdown already in progress (execution: {existing_execution_id[:8]})",
                "phase": "FENCING_DUPLICATE_SHUTDOWN",
            },
            process_exit_recommendation="exit_clean",
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for diagnostics."""
        result = {
            "request_id": self.request_id[:8] if len(self.request_id) > 8 else self.request_id,
            "execution_id": self.execution_id[:8] if len(self.execution_id) > 8 else self.execution_id,
            "intent_id": self.intent_id[:8] if len(self.intent_id) > 8 else self.intent_id,
            "process_id": self.process_id,
            "launch_id": self.launch_id[:8] if len(self.launch_id) > 8 else self.launch_id,
            "startup_id": self.startup_id[:8] if len(self.startup_id) > 8 else self.startup_id,
            "runtime_id": self.runtime_id[:8] if len(self.runtime_id) > 8 else self.runtime_id,
            "boot_session_id": self.boot_session_id[:8] if len(self.boot_session_id) > 8 else self.boot_session_id,
            "outcome": self.outcome.value,
            "effective_policy_summary": {
                k: v for k, v in list(self.effective_policy.items())[:10]
            } if isinstance(self.effective_policy, dict) else str(self.effective_policy),
            "duration_seconds": round(self.duration_seconds, 3),
            "start_time_utc": self.start_time_utc.isoformat(),
        }
        
        if self.end_time_utc:
            result["end_time_utc"] = self.end_time_utc.isoformat()
        
        return result