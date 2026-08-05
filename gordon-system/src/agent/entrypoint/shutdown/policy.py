"""Gordon Agent Shutdown Policy.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination
======================================================

Immutable shutdown policies that control graceful-to-forced escalation,
deadlines, and behavior during shutdown transactions.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


# =============================================================================
# SHUTDOWN POLICY
# =============================================================================


@dataclass(frozen=True)
class AgentShutdownPolicy:
    """Immutable shutdown policy for a single transaction.
    
    Defines behavior for shutdown including deadlines, escalation rules,
    and handling of various failure modes. Must be immutable to ensure
    deterministic behavior across the transaction.
    
    Architecture boundaries:
        This owns:
            - Policy identity (policy_id)
            - All deadline values
            - Escalation rules
            - Duplicate/idempotency behavior
        
        This does NOT own:
            - Mutable runtime state
            - Active connections
            - Resource handles
    """
    
    policy_id: str
    """Unique identifier for this policy instance."""
    
    # Timeouts/deadlines (all in seconds)
    graceful_deadline_seconds: float = 30.0
    """Maximum time allowed for graceful shutdown phase."""
    
    forced_deadline_seconds: float = 15.0
    """Maximum time allowed for forced shutdown phase."""
    
    verification_deadline_seconds: float = 10.0
    """Maximum time allowed for terminal-state verification."""
    
    total_shutdown_deadline_seconds: float = 60.0
    """Absolute maximum total shutdown time."""
    
    # Escalation behavior
    graceful_to_forced_escalation: bool = True
    """Whether to escalate from graceful to forced on timeout/failure."""
    
    emergency_containment_policy: bool = False
    """Whether emergency containment is active."""
    
    # Duplicate handling
    duplicate_request_behavior: str = "return_existing"
    """Behavior for repeated requests (return_existing, reject, merge)."""
    
    idempotency_enabled: bool = True
    """Whether to enforce idempotency for repeated requests."""
    
    # Cancellation behavior
    cancellation_enabled: bool = True
    """Whether shutdown can be cancelled (before irreversible boundary)."""
    
    retry_behavior: str = "none"
    """Retry policy (none, bounded)."""
    
    max_retry_attempts: int = 1
    """Maximum retry attempts for eligible failures."""
    
    # Outcome handling
    exit_recommendation_on_success: str = "exit_clean"
    """Recommended process exit on success."""
    
    exit_recommendation_on_failure: str = "exit_unclean"
    """Recommended process exit on failure."""
    
    allow_degraded_terminal_state: bool = False
    """Whether degraded terminal state is acceptable."""
    
    diagnostics_enabled: bool = True
    """Whether to generate diagnostics during shutdown."""
    
    # Runtime handling
    validate_runtime_identity: bool = True
    """Whether to validate runtime identity before shutdown."""
    
    validate_boot_session: bool = True
    """Whether to validate boot session identity."""
    
    reject_assistant_runtime: bool = True
    """Whether to reject Assistant runtimes."""
    
    def __post_init__(self) -> None:
        """Validate policy values."""
        if self.graceful_deadline_seconds <= 0:
            raise ValueError("graceful_deadline_seconds must be positive")
        if self.forced_deadline_seconds <= 0:
            raise ValueError("forced_deadline_seconds must be positive")
        if self.total_shutdown_deadline_seconds < (
            self.graceful_deadline_seconds + self.forced_deadline_seconds
        ):
            raise ValueError(
                "total_shutdown_deadline_seconds must accommodate graceful and forced phases"
            )
    
    @classmethod
    def create_default(cls) -> "AgentShutdownPolicy":
        """Create a default policy with sensible defaults."""
        return cls(policy_id=str(uuid.uuid4()))
    
    @classmethod
    def from_launch_request(
        cls,
        launch_request: Dict[str, Any],
    ) -> "AgentShutdownPolicy":
        """Derive shutdown policy from launch request.
        
        Args:
            launch_request: The original launch request
            
        Returns:
            New AgentShutdownPolicy instance
        """
        # Extract any user-specified overrides
        graceful_deadline = 30.0
        forced_deadline = 15.0
        
        return cls(
            policy_id=str(uuid.uuid4()),
            graceful_deadline_seconds=graceful_deadline,
            forced_deadline_seconds=forced_deadline,
            total_shutdown_deadline_seconds=graceful_deadline + forced_deadline,
        )
    
    def derive_forced_policy(self) -> "AgentShutdownPolicy":
        """Create a forced shutdown policy from this one."""
        return dataclass_replace(
            self,
            graceful_to_forced_escalation=False,
            emergency_containment_policy=True,
        )
    
    @property
    def effective_urgency(self) -> str:
        """Determine effective urgency based on configuration."""
        if self.emergency_containment_policy:
            return "emergency"
        elif not self.graceful_to_forced_escalation:
            return "forced"
        else:
            return "graceful"


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace that handles frozen dataclasses."""
    import copy
    
    cls = type(instance)
    new_dict = copy.copy(instance.__dict__)
    new_dict.update(kwargs)
    
    return cls(**new_dict)


# =============================================================================
# DEFAULT POLICIES
# =============================================================================


class DefaultShutdownPolicy:
    """Named default shutdown policies for common scenarios."""
    
    GRACEFUL = AgentShutdownPolicy(
        policy_id="default.graceful",
        graceful_deadline_seconds=30.0,
        forced_deadline_seconds=15.0,
        total_shutdown_deadline_seconds=60.0,
        graceful_to_forced_escalation=True,
        emergency_containment_policy=False,
    )
    
    FORCED = AgentShutdownPolicy(
        policy_id="default.forced",
        graceful_deadline_seconds=5.0,
        forced_deadline_seconds=10.0,
        total_shutdown_deadline_seconds=20.0,
        graceful_to_forced_escalation=False,
        emergency_containment_policy=True,
    )
    
    EMERGENCY = AgentShutdownPolicy(
        policy_id="default.emergency",
        graceful_deadline_seconds=1.0,
        forced_deadline_seconds=5.0,
        total_shutdown_deadline_seconds=10.0,
        graceful_to_forced_escalation=False,
        emergency_containment_policy=True,
    )
    
    VALIDATION = AgentShutdownPolicy(
        policy_id="default.validation",
        graceful_deadline_seconds=10.0,
        forced_deadline_seconds=5.0,
        total_shutdown_deadline_seconds=20.0,
        graceful_to_forced_escalation=False,
        emergency_containment_policy=False,
    )