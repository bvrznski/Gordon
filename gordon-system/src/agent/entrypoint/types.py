"""Gordon Agent Entrypoint Type Definitions.

Phase 3.7.29-I: Agent Process Entrypoint
========================================

Immutable type models for Agent entrypoint operations.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any,
    Dict,
    Final,
    List,
    Optional,
    Sequence,
    Tuple,
)


# =============================================================================
# AGENT INVOCATION SURFACE
# =============================================================================


class AgentInvocationSurface(Enum):
    """Agent invocation surface identifier.

    Represents how the Agent was invoked. All surfaces must converge on the
    same canonical entrypoint path.
    """

    MODULE_EXECUTION = "python -m agent"
    TOP_LEVEL_LAUNCHER = "gordon --mode agent"
    CONSOLE_SCRIPT = "gordon-agent"

    @property
    def cli_short_name(self) -> str:
        """Return a short CLI-friendly name."""
        return {
            AgentInvocationSurface.MODULE_EXECUTION: "-m",
            AgentInvocationSurface.TOP_LEVEL_LAUNCHER: "--mode agent",
            AgentInvocationSurface.CONSOLE_SCRIPT: "gordon-agent",
        }[self]

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return {
            AgentInvocationSurface.MODULE_EXECUTION: "Python module execution",
            AgentInvocationSurface.TOP_LEVEL_LAUNCHER: "Top-level Gordon launcher (Agent mode)",
            AgentInvocationSurface.CONSOLE_SCRIPT: "Console script entrypoint",
        }[self]


# =============================================================================
# AGENT RUN MODES
# =============================================================================


class AgentRunMode(Enum):
    """Agent operational run modes.

    Each mode defines specific initialization and operational semantics.
    """

    DEFAULT = auto()
    """Default interactive/foreground operation."""

    SERVICE = auto()
    """Service daemon mode - runs until explicit shutdown request."""

    INTERACTIVE = auto()
    """Interactive shell mode - reads from terminal."""

    BOUNDED_TASK = auto()
    """Bounded task mode - completes after single task or timeout."""

    VALIDATION_ONLY = auto()
    """Validation-only mode - check config and initialization without full operation."""

    DIAGNOSTIC = auto()
    """Diagnostic mode - run diagnostic checks only."""

    SAFE = auto()
    """Safe mode - restricted operation with minimal capabilities."""

    OFFLINE = auto()
    """Offline mode - operate without external network access."""


# =============================================================================
# BRIDGE POLICY
# =============================================================================


class AgentBridgePolicy(Enum):
    """Agent–Assistant bridge policy.

    Controls how the Agent interacts with the Assistant process.
    """

    REQUIRED = "required"
    """Assistant must be available; failure is fatal."""

    OPTIONAL = "optional"
    """Assistant may be unavailable; operation continues without it."""

    DISABLED = "disabled"
    """Assistant bridge is disabled entirely."""

    LOCAL_TEST_DOUBLE = "local_test_double"
    """Use local test double for Assistant (testing only)."""

    @property
    def is_required(self) -> bool:
        """Check if Assistant is required."""
        return self == AgentBridgePolicy.REQUIRED

    @property
    def is_optional(self) -> bool:
        """Check if Assistant is optional."""
        return self == AgentBridgePolicy.OPTIONAL

    @property
    def is_disabled(self) -> bool:
        """Check if bridge is disabled."""
        return self == AgentBridgePolicy.DISABLED


# =============================================================================
# AGENT LAUNCH MODE
# =============================================================================


@dataclass(frozen=True)
class AgentLaunchMode:
    """Immutable launch mode configuration.

    Combines run mode and additional constraints.
    """

    run_mode: AgentRunMode
    """The primary operational mode."""

    bridge_policy: AgentBridgePolicy = AgentBridgePolicy.OPTIONAL
    """Assistant bridge policy for this launch."""

    safe_mode_enabled: bool = False
    """Enable safe mode restrictions."""

    offline_mode_enabled: bool = False
    """Enable offline mode restrictions."""

    validation_only: bool = False
    """Validation-only mode (no full operation)."""

    @property
    def is_service(self) -> bool:
        """Check if running as a service."""
        return self.run_mode == AgentRunMode.SERVICE

    @property
    def is_interactive(self) -> bool:
        """Check if running in interactive mode."""
        return self.run_mode == AgentRunMode.INTERACTIVE

    @property
    def is_bounded_task(self) -> bool:
        """Check if running a bounded task."""
        return self.run_mode == AgentRunMode.BOUNDED_TASK

    @property
    def is_validation_only(self) -> bool:
        """Check if validation-only mode is enabled."""
        return self.validation_only

    @property
    def is_safe_mode(self) -> bool:
        """Check if safe mode is enabled."""
        return self.safe_mode_enabled

    @property
    def is_offline(self) -> bool:
        """Check if offline mode is enabled."""
        return self.offline_mode_enabled


# =============================================================================
# PROCESS IDENTITIES
# =============================================================================


@dataclass(frozen=True)
class AgentProcessIdentity:
    """Immutable process identity.

    Unique identifier for this specific process instance.
    """

    process_id: int
    """OS process ID."""

    launch_id: str
    """Launch session ID (deterministic, not unique across launches)."""

    parent_process_id: Optional[int]
    """Parent OS process ID if available."""

    invocation_surface: AgentInvocationSurface
    """How this process was invoked."""

    @property
    def short_id(self) -> str:
        """Return a short printable ID."""
        return f"proc-{self.process_id}"


@dataclass(frozen=True)
class AgentLaunchIdentity:
    """Immutable launch identity.

    Identifies a specific launch attempt within the process.
    """

    launch_id: str
    """Unique launch identifier."""

    timestamp_ns: int
    """Unix timestamp in nanoseconds."""

    invocation_surface: AgentInvocationSurface
    """How this launch was invoked."""

    @classmethod
    def create(cls, invocation_surface: AgentInvocationSurface) -> "AgentLaunchIdentity":
        """Create a new launch identity with auto-generated IDs."""
        import uuid
        import time

        return cls(
            launch_id=str(uuid.uuid4()),
            timestamp_ns=time.time_ns(),
            invocation_surface=invocation_surface,
        )


@dataclass(frozen=True)
class AgentRuntimeIdentity:
    """Immutable runtime identity.

    Assigned by the canonical initialization authority.
    """

    runtime_id: str
    """Unique runtime identifier."""

    boot_session_id: str
    """Boot session identifier."""

    @classmethod
    def empty(cls) -> "AgentRuntimeIdentity":
        """Return an empty/runtime identity for pre-initialization contexts."""
        return cls(
            runtime_id="uninitialized",
            boot_session_id="uninitialized",
        )


@dataclass(frozen=True)
class AgentSystemIdentity:
    """Immutable system-level identity.

    Assigned by the top-level Gordon launcher if present.
    """

    system_id: Optional[str]
    """Gordon system-wide identifier."""

    parent_system_id: Optional[str]
    """Parent system identifier (if any)."""

    @classmethod
    def create(
        cls, system_id: Optional[str] = None, parent_system_id: Optional[str] = None
    ) -> "AgentSystemIdentity":
        """Create a new system identity."""
        return cls(
            system_id=system_id,
            parent_system_id=parent_system_id,
        )


# =============================================================================
# CONFIGURATION REQUEST
# =============================================================================


@dataclass(frozen=True)
class AgentConfigurationRequest:
    """Immutable configuration request.

    Specifies where and how to load configuration.
    """

    config_path: Optional[str] = None
    """Explicit configuration file path."""

    profile: str = "default"
    """Configuration profile name."""

    environment: str = "production"
    """Environment context (development, staging, production)."""

    deployment_mode: str = "standalone"
    """Deployment mode (standalone, cluster, containerized)."""

    @property
    def is_default_profile(self) -> bool:
        """Check if using default profile."""
        return self.profile == "default"

    @property
    def is_production_environment(self) -> bool:
        """Check if in production environment."""
        return self.environment == "production"


# =============================================================================
# LAUNCH REQUEST (IMMUTABLE)
# =============================================================================


@dataclass(frozen=True)
class AgentLaunchRequest:
    """Immutable Agent launch request.

    All fields must be populated at construction time. No mutable state
    or runtime objects are contained.
    """

    # Identity
    process_identity: AgentProcessIdentity
    """Process-level identity."""

    launch_identity: AgentLaunchIdentity
    """Launch-specific identity."""

    system_identity: AgentSystemIdentity
    """System-wide identity (if any)."""

    runtime_identity: AgentRuntimeIdentity
    """Runtime identity (assigned during initialization)."""

    # Mode and constraints
    mode: AgentLaunchMode
    """Launch mode configuration."""

    # Configuration
    config_request: AgentConfigurationRequest = field(
        default_factory=AgentConfigurationRequest
    )
    """Configuration loading request."""

    # Deadlines
    startup_deadline_seconds: float = 30.0
    """Maximum time allowed for initialization."""

    shutdown_deadline_seconds: float = 15.0
    """Maximum time allowed for graceful shutdown."""

    # Operational
    log_level: str = "INFO"
    """Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""

    structured_output: bool = False
    """Enable structured JSON output."""

    development_mode: bool = False
    """Enable development features (debug logging, etc.)."""

    # Provenance
    raw_arguments: Tuple[str, ...] = field(default_factory=tuple)
    """Raw command-line arguments as passed to main()."""

    causation_id: Optional[str] = None
    """Causation event ID if invoked in response to another event."""

    correlation_id: Optional[str] = None
    """Correlation context ID for tracing."""

    @property
    def is_validation_only(self) -> bool:
        """Check if validation-only mode."""
        return self.mode.is_validation_only

    @property
    def is_safe_mode(self) -> bool:
        """Check if safe mode enabled."""
        return self.mode.is_safe_mode

    @property
    def is_offline(self) -> bool:
        """Check if offline mode enabled."""
        return self.mode.is_offline

    @classmethod
    def create(
        cls,
        invocation_surface: AgentInvocationSurface = AgentInvocationSurface.MODULE_EXECUTION,
        raw_arguments: Sequence[str] = tuple(),
    ) -> "AgentLaunchRequest":
        """Create a new launch request with default values.

        This is the canonical factory for launch requests. All fields are
        populated at construction time.
        """
        # Generate identities
        process_id = os.getpid()
        parent_pid = os.getppid() if hasattr(os, 'getppid') else None

        return cls(
            process_identity=AgentProcessIdentity(
                process_id=process_id,
                launch_id="placeholder_launch_id",  # Will be replaced by launch identity
                parent_process_id=parent_pid,
                invocation_surface=invocation_surface,
            ),
            launch_identity=AgentLaunchIdentity.create(invocation_surface),
            system_identity=AgentSystemIdentity(system_id=None, parent_system_id=None),
            runtime_identity=AgentRuntimeIdentity.empty(),
            mode=AgentLaunchMode(
                run_mode=AgentRunMode.DEFAULT,
                bridge_policy=AgentBridgePolicy.OPTIONAL,
            ),
            raw_arguments=tuple(raw_arguments),
        )

    def with_runtime_identity(self, runtime_id: str, boot_session_id: str) -> "AgentLaunchRequest":
        """Return a new request with the given runtime identity."""
        return dataclasses_replace(
            self,
            runtime_identity=AgentRuntimeIdentity(
                runtime_id=runtime_id,
                boot_session_id=boot_session_id,
            ),
        )

    def with_mode(self, mode: AgentLaunchMode) -> "AgentLaunchRequest":
        """Return a new request with the given mode."""
        return dataclasses_replace(self, mode=mode)

    def with_config_request(
        self, config_request: AgentConfigurationRequest
    ) -> "AgentLaunchRequest":
        """Return a new request with the given configuration request."""
        return dataclasses_replace(self, config_request=config_request)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclasses_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace that handles frozen dataclasses.

    Since our dataclasses are @dataclass(frozen=True), we need a way to create
    modified copies. This uses the underlying __dict__ to create new instances.
    """
    import copy

    # Get the class and create a dict from current values
    cls = type(instance)
    new_dict = copy.copy(instance.__dict__)
    new_dict.update(kwargs)

    # Create a new instance with updated values
    return cls(**new_dict)


# =============================================================================
# TYPE ALIASES FOR EXPORT
# =============================================================================

# Export key types at module level for convenience
__all__ = [
    "AgentInvocationSurface",
    "AgentRunMode",
    "AgentBridgePolicy",
    "AgentLaunchMode",
    "AgentProcessIdentity",
    "AgentLaunchIdentity",
    "AgentRuntimeIdentity",
    "AgentSystemIdentity",
    "AgentConfigurationRequest",
    "AgentLaunchRequest",
]