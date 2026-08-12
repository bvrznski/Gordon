"""Gordon Agent Entrypoint Exit Status Codes.

Phase 3.7.29-I: Agent Process Entrypoint
========================================

Semantic exit status codes for Agent process termination.

All exit statuses follow POSIX conventions:
- 0: Success
- 1-125: Application-specific failures
- 126: Command found but not executable
- 127: Command not found
- 128+: Fatal error signals
"""
from __future__ import annotations

from enum import IntEnum, auto


class AgentExitStatus(IntEnum):
    """Semantic exit status codes for Agent processes.

    These codes are used to communicate the outcome of the Agent process
    to the operating system and parent processes.
    """

    # Base success code (POSIX: 0)
    SUCCESS = 0
    """Process completed successfully."""

    # Application errors (1-99)
    INVALID_USAGE = auto()
    """Invalid command-line usage or arguments."""

    CONFIGURATION_FAILURE = auto()
    """Configuration loading or validation failed."""

    PROCESS_HOST_FAILURE = auto()
    """Process-host initialization failed."""

    INITIALIZATION_FAILURE = auto()
    """Agent initialization failed."""

    LOAD_FAILURE = auto()
    """Component loading failed (e.g., missing __load__.py)."""

    CORE_CONSTRUCTION_FAILURE = auto()
    """Core authority construction failed."""

    ASSEMBLY_FAILURE = auto()
    """Runtime assembly failed."""

    INTEGRITY_FAILURE = auto()
    """Integrity check failed."""

    ACTIVATION_FAILURE = auto()
    """Runtime activation failed."""

    READINESS_FAILURE = auto()
    """Readiness evaluation failed."""

    ADMISSION_FAILURE = auto()
    """Admission opening failed."""

    BRIDGE_FAILURE = auto()
    """Agent–Assistant bridge initialization failed."""

    OPERATIONAL_FAILURE = auto()
    """Operational runner failed."""

    HEALTH_FAILURE = auto()
    """Health check failure during operation."""

    RECOVERY_FAILURE = auto()
    """Recovery action failed."""

    SHUTDOWN_FAILURE = auto()
    """Canonical shutdown request failed."""

    TERMINAL_VERIFICATION_FAILURE = auto()
    """Terminal state verification failed."""

    # Signal-related (128-159, POSIX convention)
    INTERRUPTED = 130
    """Process interrupted by SIGINT."""

    TERMINATED = 143
    """Process terminated by SIGTERM."""

    # Internal errors (200-255 range)
    INTERNAL_ERROR = 200
    """Unspecified internal error (unexpected exception)."""

    UNEXPECTED_EXCEPTION = auto()
    """Unexpected exception escaped all handlers."""

    DEADLINE_EXCEEDED = auto()
    """Operation exceeded configured deadline."""

    RESOURCE_EXHAUSTED = auto()
    """Resource limit exceeded."""

    @property
    def is_success(self) -> bool:
        """Check if this represents successful completion."""
        return self == AgentExitStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Check if this represents a failure condition."""
        return self != AgentExitStatus.SUCCESS

    @property
    def signal_based(self) -> bool:
        """Check if this exit status was caused by a signal."""
        return self in (
            AgentExitStatus.INTERRUPTED,
            AgentExitStatus.TERMINATED,
        )


# =============================================================================
# EXIT STATUS MAPPING
# =============================================================================


class ExitStatusCodeMapper:
    """Maps various failure types to canonical exit statuses.

    This is a pure mapping class with no state. It provides deterministic
    translation from internal failures to shell-compatible exit codes.
    """

    # Map of exception classes to exit statuses
    EXCEPTION_TO_EXIT: dict[type[Exception], AgentExitStatus] = {
        KeyboardInterrupt: AgentExitStatus.INTERRUPTED,
        SystemExit: lambda e: AgentExitStatus(e.code)
        if isinstance(e.code, int) and 0 <= e.code <= 255
        else AgentExitStatus.SUCCESS,
    }

    @classmethod
    def map_exception(cls, exc: Exception) -> AgentExitStatus:
        """Map an exception to its canonical exit status.

        Args:
            exc: The exception that occurred

        Returns:
            Canonical exit status code
        """
        # Check for exact type match first
        exc_type = type(exc)
        if exc_type in cls.EXCEPTION_TO_EXIT:
            handler = cls.EXCEPTION_TO_EXIT[exc_type]
            if callable(handler):
                return handler(exc)
            return handler

        # Check parent classes
        for base_type, exit_status in cls.EXCEPTION_TO_EXIT.items():
            if isinstance(exc, base_type):
                if callable(exit_status):
                    return exit_status(exc)
                return exit_status

        # Default to internal error for unclassified exceptions
        return AgentExitStatus.INTERNAL_ERROR

    @classmethod
    def map_failure(cls, failure_type: str) -> AgentExitStatus:
        """Map a failure type string to its canonical exit status.

        Args:
            failure_type: String identifier of the failure category

        Returns:
            Canonical exit status code
        """
        FAILURE_MAP: dict[str, AgentExitStatus] = {
            "invalid_usage": AgentExitStatus.INVALID_USAGE,
            "configuration": AgentExitStatus.CONFIGURATION_FAILURE,
            "process_host": AgentExitStatus.PROCESS_HOST_FAILURE,
            "initialization": AgentExitStatus.INITIALIZATION_FAILURE,
            "load": AgentExitStatus.LOAD_FAILURE,
            "core_construction": AgentExitStatus.CORE_CONSTRUCTION_FAILURE,
            "assembly": AgentExitStatus.ASSEMBLY_FAILURE,
            "integrity": AgentExitStatus.INTEGRITY_FAILURE,
            "activation": AgentExitStatus.ACTIVATION_FAILURE,
            "readiness": AgentExitStatus.READINESS_FAILURE,
            "admission": AgentExitStatus.ADMISSION_FAILURE,
            "bridge": AgentExitStatus.BRIDGE_FAILURE,
            "operational": AgentExitStatus.OPERATIONAL_FAILURE,
            "health": AgentExitStatus.HEALTH_FAILURE,
            "recovery": AgentExitStatus.RECOVERY_FAILURE,
            "shutdown": AgentExitStatus.SHUTDOWN_FAILURE,
            "terminal_verification": AgentExitStatus.TERMINAL_VERIFICATION_FAILURE,
        }

        return FAILURE_MAP.get(failure_type, AgentExitStatus.INTERNAL_ERROR)


# =============================================================================
# EXIT STATUS HELPERS
# =============================================================================


def format_exit_status(status: AgentExitStatus) -> str:
    """Format an exit status for display.

    Args:
        status: Exit status to format

    Returns:
        Human-readable description
    """
    descriptions = {
        AgentExitStatus.SUCCESS: "Success",
        AgentExitStatus.INVALID_USAGE: "Invalid usage or arguments",
        AgentExitStatus.CONFIGURATION_FAILURE: "Configuration failure",
        AgentExitStatus.PROCESS_HOST_FAILURE: "Process host initialization failed",
        AgentExitStatus.INITIALIZATION_FAILURE: "Agent initialization failed",
        AgentExitStatus.LOAD_FAILURE: "Component loading failed",
        AgentExitStatus.CORE_CONSTRUCTION_FAILURE: "Core construction failed",
        AgentExitStatus.ASSEMBLY_FAILURE: "Runtime assembly failed",
        AgentExitStatus.INTEGRITY_FAILURE: "Integrity check failed",
        AgentExitStatus.ACTIVATION_FAILURE: "Runtime activation failed",
        AgentExitStatus.READINESS_FAILURE: "Readiness evaluation failed",
        AgentExitStatus.ADMISSION_FAILURE: "Admission opening failed",
        AgentExitStatus.BRIDGE_FAILURE: "Agent–Assistant bridge failed",
        AgentExitStatus.OPERATIONAL_FAILURE: "Operational runner failed",
        AgentExitStatus.HEALTH_FAILURE: "Health check failure",
        AgentExitStatus.RECOVERY_FAILURE: "Recovery action failed",
        AgentExitStatus.SHUTDOWN_FAILURE: "Shutdown request failed",
        AgentExitStatus.TERMINAL_VERIFICATION_FAILURE: "Terminal verification failed",
        AgentExitStatus.INTERRUPTED: "Interrupted (SIGINT)",
        AgentExitStatus.TERMINATED: "Terminated (SIGTERM)",
        AgentExitStatus.INTERNAL_ERROR: "Internal error",
        AgentExitStatus.UNEXPECTED_EXCEPTION: "Unexpected exception",
        AgentExitStatus.DEADLINE_EXCEEDED: "Deadline exceeded",
        AgentExitStatus.RESOURCE_EXHAUSTED: "Resource exhausted",
    }
    return descriptions.get(status, f"Unknown exit status ({status})")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AgentExitStatus",
    "ExitStatusCodeMapper",
    "format_exit_status",
]