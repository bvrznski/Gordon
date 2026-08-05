"""Gordon Agent Startup Policy.

Phase 3.7.33-I: Agent Startup Coordination
==========================================

Immutable policy configuration for a single startup transaction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional


class AgentStartupMode(Enum):
    """Startup mode options."""
    
    NORMAL = "normal"
    SAFE = "safe"
    OFFLINE = "offline"
    VALIDATION_ONLY = "validation_only"
    DEGRADED = "degraded"


class AgentBridgePolicy(Enum):
    """Assistant bridge policy options."""
    
    REQUIRED = "required"
    OPTIONAL = "optional"
    DISABLED = "disabled"
    LOCAL_TEST_DOUBLE = "local_test_double"


@dataclass(frozen=True)
class AgentStartupPolicy:
    """Immutable startup policy configuration.
    
    This policy is derived from the launch request and governs how
    the startup coordinator behaves. It must be immutable to ensure
    deterministic behavior.
    
    Policy ownership:
        - Policy identity comes from launch request
        - Policy values are validated at startup start
        - Policy is preserved in all results
    
    Architecture boundaries:
        This owns:
            - Policy values (flags, timeouts, modes)
            - Decision rules (rollback vs shutdown)
            
        This does NOT own:
            - Runtime resources
            - Component instances
            - Mutable state
    """
    
    # Mode and operational constraints
    startup_mode: AgentStartupMode
    """Overall startup mode."""
    
    bridge_policy: AgentBridgePolicy
    """Assistant bridge policy."""
    
    safe_mode_enabled: bool
    """Enable safe mode restrictions."""
    
    offline_mode_enabled: bool
    """Enable offline mode restrictions."""
    
    validation_only: bool
    """Validation-only mode (stop after certain phases)."""
    
    degraded_allowed: bool
    """Whether degraded startup is permitted."""
    
    # Deadline configuration
    startup_deadline_seconds: float
    """Maximum time for complete startup transaction."""
    
    preflight_deadline_seconds: float
    """Maximum time for preflight invocation."""
    
    initialization_deadline_seconds: float
    """Maximum time for initialization invocation."""
    
    handoff_deadline_seconds: float
    """Maximum time for handoff verification."""
    
    rollback_deadline_seconds: float
    """Maximum time for rollback request."""
    
    shutdown_deadline_seconds: float
    """Maximum time for shutdown request."""
    
    # Retry configuration
    max_preflight_rechecks: int
    """Maximum number of preflight recheck attempts."""
    
    max_initialization_retries: int
    """Maximum number of initialization retry attempts."""
    
    retry_backoff_base_seconds: float
    """Base backoff time between retries."""
    
    retry_backoff_max_seconds: float
    """Maximum backoff time between retries."""
    
    # Behavior configuration
    require_strict_preflight_validation: bool
    """Whether to reject PASS_WITH_WARNINGS."""
    
    rollback_on_initialization_failure: bool
    """Whether to attempt rollback on init failure."""
    
    shutdown_after_transfer_failure: bool
    """Whether to request shutdown after ownership transfer failure."""
    
    # Identity and provenance
    policy_id: str
    """Unique identifier for this policy instance."""
    
    launch_id: str
    """Launch session ID that generated this policy."""
    
    generation: int
    """Policy generation number (incremented on configuration changes)."""
    
    @classmethod
    def create_default(cls, launch_id: str) -> "AgentStartupPolicy":
        """Create a default policy with sensible defaults.
        
        Args:
            launch_id: Launch session ID from the request
            
        Returns:
            New AgentStartupPolicy instance
        """
        import time
        
        return cls(
            startup_mode=AgentStartupMode.NORMAL,
            bridge_policy=AgentBridgePolicy.OPTIONAL,
            safe_mode_enabled=False,
            offline_mode_enabled=False,
            validation_only=False,
            degraded_allowed=False,
            startup_deadline_seconds=30.0,
            preflight_deadline_seconds=15.0,
            initialization_deadline_seconds=25.0,
            handoff_deadline_seconds=10.0,
            rollback_deadline_seconds=10.0,
            shutdown_deadline_seconds=15.0,
            max_preflight_rechecks=1,
            max_initialization_retries=2,
            retry_backoff_base_seconds=0.5,
            retry_backoff_max_seconds=30.0,
            require_strict_preflight_validation=True,
            rollback_on_initialization_failure=True,
            shutdown_after_transfer_failure=False,
            policy_id=str(time.time_ns()),
            launch_id=launch_id,
            generation=1,
        )
    
    @classmethod
    def from_launch_request(
        cls,
        request: dict,
        policy_id: Optional[str] = None,
        generation: int = 1,
    ) -> "AgentStartupPolicy":
        """Create a policy derived from a launch request.
        
        Args:
            request: The launch request dictionary
            policy_id: Optional explicit policy ID (auto-generated if not provided)
            generation: Policy generation number
            
        Returns:
            New AgentStartupPolicy instance with values from request
        """
        import time
        
        # Extract mode information from request
        mode = request.get("mode", {})
        
        return cls(
            startup_mode=cls._derive_startup_mode(mode),
            bridge_policy=cls._derive_bridge_policy(mode),
            safe_mode_enabled=mode.get("safe_mode_enabled", False),
            offline_mode_enabled=mode.get("offline_mode_enabled", False),
            validation_only=mode.get("is_validation_only", False),
            degraded_allowed=mode.get("degraded_allowed", False),
            startup_deadline_seconds=request.get("startup_deadline_seconds", 30.0),
            preflight_deadline_seconds=request.get("preflight_deadline_seconds", 15.0),
            initialization_deadline_seconds=request.get("initialization_deadline_seconds", 25.0),
            handoff_deadline_seconds=mode.get("handoff_deadline_seconds", 10.0),
            rollback_deadline_seconds=mode.get("rollback_deadline_seconds", 10.0),
            shutdown_deadline_seconds=mode.get("shutdown_deadline_seconds", 15.0),
            max_preflight_rechecks=mode.get("max_preflight_rechecks", 1),
            max_initialization_retries=mode.get("max_initialization_retries", 2),
            retry_backoff_base_seconds=mode.get("retry_backoff_base_seconds", 0.5),
            retry_backoff_max_seconds=mode.get("retry_backoff_max_seconds", 30.0),
            require_strict_preflight_validation=mode.get(
                "require_strict_preflight_validation", True
            ),
            rollback_on_initialization_failure=mode.get(
                "rollback_on_initialization_failure", True
            ),
            shutdown_after_transfer_failure=mode.get(
                "shutdown_after_transfer_failure", False
            ),
            policy_id=policy_id or str(time.time_ns()),
            launch_id=request.get("launch_identity", {}).get("launch_id", ""),
            generation=generation,
        )
    
    @classmethod
    def _derive_startup_mode(cls, mode: dict) -> AgentStartupMode:
        """Derive startup mode from mode dictionary."""
        if mode.get("is_validation_only", False):
            return AgentStartupMode.VALIDATION_ONLY
        elif mode.get("offline_mode_enabled", False):
            return AgentStartupMode.OFFLINE
        elif mode.get("safe_mode_enabled", False):
            return AgentStartupMode.SAFE
        else:
            return AgentStartupMode.NORMAL
    
    @classmethod
    def _derive_bridge_policy(cls, mode: dict) -> AgentBridgePolicy:
        """Derive bridge policy from mode dictionary."""
        bridge_value = mode.get("bridge_policy", "optional")
        if isinstance(bridge_value, str):
            bridge_value = bridge_value.lower()
        
        mapping = {
            "required": AgentBridgePolicy.REQUIRED,
            "optional": AgentBridgePolicy.OPTIONAL,
            "disabled": AgentBridgePolicy.DISABLED,
            "local_test_double": AgentBridgePolicy.LOCAL_TEST_DOUBLE,
        }
        
        return mapping.get(bridge_value, AgentBridgePolicy.OPTIONAL)
    
    def with_mode(self, mode: AgentStartupMode) -> "AgentStartupPolicy":
        """Return a new policy with updated startup mode."""
        return dataclass_replace(self, startup_mode=mode)
    
    def with_bridge_policy(self, bridge_policy: AgentBridgePolicy) -> "AgentStartupPolicy":
        """Return a new policy with updated bridge policy."""
        return dataclass_replace(self, bridge_policy=bridge_policy)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace that handles frozen dataclasses.
    
    Since our dataclasses are @dataclass(frozen=True), we need a way to create
    modified copies. This uses the underlying __dict__ to create new instances.
    """
    import copy
    
    cls = type(instance)
    new_dict = copy.copy(instance.__dict__)
    new_dict.update(kwargs)
    
    return cls(**new_dict)


__all__ = [
    "AgentStartupPolicy",
    "AgentStartupMode",
    "AgentBridgePolicy",
]