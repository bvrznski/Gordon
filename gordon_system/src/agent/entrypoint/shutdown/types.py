"""Gordon Agent Shutdown Types.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination
======================================================

Immutable data models for shutdown intent, request, and context.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple


# =============================================================================
# SHUTDOWN REASON MODEL
# =============================================================================


class AgentShutdownReason(Enum):
    """Typed shutdown reasons.
    
    Possible sources:
        - OPERATOR_REQUEST: Human operator requested shutdown
        - PROCESS_SIGNAL: Process received signal (SIGINT/SIGTERM)
        - PARENT_SYSTEM_REQUEST: Parent system requested termination
        - STARTUP_FAILURE_AFTER_TRANSFER: Startup failed after ownership transfer
        - RUNTIME_FAILURE: Runtime encountered unrecoverable error
        - INTEGRITY_FAILURE: Runtime integrity verification failed
        - READINESS_FAILURE: Readiness checks failed
        - ADMISSION_FAILURE: Admission control failure
        - RESOURCE_EXHAUSTION: System resource exhaustion
        - SECURITY_FAILURE: Security violation detected
        - MAINTENANCE: Scheduled maintenance shutdown
        - DEPLOYMENT_REPLACEMENT: Deployment replacement required
        - SYSTEM_SHUTDOWN: System-level shutdown
        - VALIDATION_COMPLETE: Validation task completed
        - TEST_COMPLETE: Test task completed
        - INTERNAL_ERROR: Internal shutdown request (no external cause)
        - UNKNOWN: Unrecognized or missing reason
    """
    
    OPERATOR_REQUEST = "operator_request"
    PROCESS_SIGNAL = "process_signal"
    PARENT_SYSTEM_REQUEST = "parent_system_request"
    STARTUP_FAILURE_AFTER_TRANSFER = "startup_failure_after_transfer"
    RUNTIME_FAILURE = "runtime_failure"
    INTEGRITY_FAILURE = "integrity_failure"
    READINESS_FAILURE = "readiness_failure"
    ADMISSION_FAILURE = "admission_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    SECURITY_FAILURE = "security_failure"
    MAINTENANCE = "maintenance"
    DEPLOYMENT_REPLACEMENT = "deployment_replacement"
    SYSTEM_SHUTDOWN = "system_shutdown"
    VALIDATION_COMPLETE = "validation_complete"
    TEST_COMPLETE = "test_complete"
    INTERNAL_ERROR = "internal_error"
    UNKNOWN = "unknown"


# =============================================================================
# SHUTDOWN URGENCY MODEL
# =============================================================================


class AgentShutdownUrgency(Enum):
    """Typed shutdown urgency levels.
    
    Semantics:
        GRACEFUL: Close admission, allow bounded work draining, deactivate in
                  canonical order, flush state, release resources, verify terminal
        EXPEDITED: Reduced draining and flush budgets while preserving canonical
                   ownership and cleanup order
        FORCED: Cancel outstanding work, stop runtime responsibilities under
                canonical forced policy, release resources, preserve residual evidence
        EMERGENCY: Minimal safe containment path defined by Core policy. Preserve
                   evidence even where full cleanup cannot complete.
    """
    
    GRACEFUL = "graceful"
    EXPEDITED = "expedited"
    FORCED = "forced"
    EMERGENCY = "emergency"


# =============================================================================
# SHUTDOWN MODE MODEL (requested mode vs effective urgency)
# =============================================================================


class AgentShutdownMode(Enum):
    """Requested shutdown modes (not automatically effective).
    
    Requested mode is not automatically the effective mode. The effective
    mode may escalate according to policy and runtime evidence.
    """
    
    GRACEFUL = "graceful"
    FAST = "fast"
    FORCE = "force"
    CONTAINMENT = "containment"
    VALIDATION_CLEANUP = "validation_cleanup"
    PROCESS_EXIT = "process_exit"


# =============================================================================
# SHUTDOWN INTENT
# =============================================================================


@dataclass(frozen=True)
class AgentShutdownIntent:
    """Immutable shutdown intent from process boundary or operational handoff.
    
    This represents the original intent that triggered shutdown. It must be
    immutable and preserve all relevant information for diagnostics and audit.
    
    Architecture boundaries:
        This owns:
            - Intent identity (intent_id, timestamp)
            - Process/launch/startup/runtime/boot-session identities
            - Source, reason, urgency, requested mode
            - Correlation, causation, provenance
        
        This does NOT own:
            - Runtime resources
            - Core registries
            - Active handles
            - Mutable state
    """
    
    intent_id: str
    """Unique identifier for this shutdown intent."""
    
    process_id: int
    """Process ID where shutdown was requested."""
    
    launch_id: str
    """Launch session ID from startup."""
    
    startup_id: str
    """Startup operation ID from startup."""
    
    runtime_id: str
    """Runtime ID being shut down."""
    
    boot_session_id: str
    """Boot session ID for this runtime instance."""
    
    source: AgentShutdownReason
    """Origin of the shutdown intent."""
    
    reason: str
    """Human-readable explanation for shutdown."""
    
    urgency: AgentShutdownUrgency = AgentShutdownUrgency.GRACEFUL
    """Requested shutdown urgency level."""
    
    requested_mode: AgentShutdownMode = AgentShutdownMode.GRACEFUL
    """Requested shutdown mode (may escalate)."""
    
    requested_deadline_seconds: Optional[float] = None
    """Optional deadline for graceful shutdown."""
    
    operator_message: Optional[str] = None
    """Message from human operator (if any)."""
    
    system_message: Optional[str] = None
    """System-generated message about shutdown."""
    
    error_cause: Optional[Exception] = None
    """Underlying exception or error cause (for failures)."""
    
    originating_phase: str = "unknown"
    """Phase where shutdown was triggered."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation chain reference."""
    
    provenance: str = "unknown"
    """Source of the shutdown request."""
    
    timestamp_ns: int = field(default_factory=time.time_ns)
    """Timestamp when intent was created."""
    
    @property
    def timestamp_utc(self) -> datetime:
        """Return UTC timestamp from ns time."""
        return datetime.utcfromtimestamp(self.timestamp_ns / 1_000_000_000.0)
    
    @classmethod
    def create(
        cls,
        process_id: int,
        launch_id: str,
        startup_id: str,
        runtime_id: str,
        boot_session_id: str,
        source: AgentShutdownReason,
        reason: str,
        urgency: AgentShutdownUrgency = AgentShutdownUrgency.GRACEFUL,
        requested_mode: AgentShutdownMode = AgentShutdownMode.GRACEFUL,
        **kwargs,
    ) -> "AgentShutdownIntent":
        """Create a new shutdown intent.
        
        Args:
            process_id: Process ID
            launch_id: Launch session ID
            startup_id: Startup operation ID
            runtime_id: Runtime being shut down
            boot_session_id: Boot session for this runtime
            source: Reason/source of shutdown
            reason: Human-readable explanation
            urgency: Requested urgency level
            requested_mode: Requested shutdown mode
            **kwargs: Additional optional fields
            
        Returns:
            New AgentShutdownIntent instance
        """
        return cls(
            intent_id=str(uuid.uuid4()),
            process_id=process_id,
            launch_id=launch_id,
            startup_id=startup_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            source=source,
            reason=reason,
            urgency=urgency,
            requested_mode=requested_mode,
            **kwargs
        )
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Return bounded summary for diagnostics."""
        return {
            "intent_id": self.intent_id[:8],
            "process_id": self.process_id,
            "launch_id": self.launch_id[:8],
            "startup_id": self.startup_id[:8],
            "runtime_id": self.runtime_id[:8],
            "boot_session_id": self.boot_session_id[:8],
            "source": self.source.value,
            "reason": self.reason[:100],  # Bounded
            "urgency": self.urgency.value,
            "requested_mode": self.requested_mode.value,
        }


# =============================================================================
# SHUTDOWN REQUEST
# =============================================================================


@dataclass(frozen=True)
class AgentShutdownRequest:
    """Immutable shutdown request for coordinator execution.
    
    This is derived from the intent and policy, validated, and ready for
    coordinator execution. It must be immutable.
    
    Architecture boundaries:
        This owns:
            - Request identity (request_id, execution_id)
            - Shutdown context (context, policy)
            - Runtime and ownership evidence
        
        This does NOT own:
            - Mutable Core internals
            - Active runtime handles
            - Component collections
            - Worker collections
    """
    
    request_id: str
    """Unique identifier for this shutdown request."""
    
    execution_id: str
    """Unique execution ID for this coordinator run."""
    
    intent: AgentShutdownIntent
    """The validated shutdown intent."""
    
    process_identity: Dict[str, Any]
    """Process identity information."""
    
    launch_identity: Dict[str, Any]
    """Launch identity information."""
    
    startup_identity: Dict[str, Any]
    """Startup identity information."""
    
    runtime_identity: Dict[str, Any]
    """Runtime identity information (validated)."""
    
    boot_session_identity: Dict[str, Any]
    """Boot session identity information (validated)."""
    
    effective_policy: AgentShutdownPolicy
    """Effective shutdown policy for this request."""
    
    runtime_shutdown_facade: Optional[Any] = None
    """Optional Core shutdown facade reference (not owned)."""
    
    ownership_evidence: Optional[Dict[str, Any]] = None
    """Evidence of operational-to-shutdown ownership transfer."""
    
    cancellation_context: Dict[str, Any] = field(default_factory=dict)
    """Cancellation context for this request."""
    
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Correlation ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation chain reference."""
    
    provenance: str = "entrypoint.shutdown"
    """Source of the request."""
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Return bounded summary for diagnostics."""
        return {
            "request_id": self.request_id[:8],
            "execution_id": self.execution_id[:8],
            "intent_summary": self.intent.summary,
            "policy_id": self.effective_policy.policy_id[:8],
            "urgency": self.effective_policy.urgency.value if hasattr(self.effective_policy, 'urgency') else "unknown",
        }