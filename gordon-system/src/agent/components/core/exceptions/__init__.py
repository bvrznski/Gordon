# Core Runtime Exceptions
# =========================

"""
Core exception hierarchy for runtime errors.

All exceptions preserve cause chains and provide actionable context.
"""

from typing import Optional, Any


class CoreError(Exception):
    """Base exception for all Core runtime errors."""
    
    def __init__(self, message: str, *args: object, cause: Optional[Exception] = None) -> None:
        super().__init__(message, *args)
        self.message = message
        self.cause = cause
    
    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class ConfigurationError(CoreError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        config_key: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.config_key = config_key


class LifecycleError(CoreError):
    """Raised when lifecycle transition is invalid."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.from_state = from_state
        self.to_state = to_state


class DependencyError(CoreError):
    """Raised when dependency resolution fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        missing_dependency: Optional[str] = None,
        cycle_path: Optional[list] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.missing_dependency = missing_dependency
        self.cycle_path = cycle_path


class RegistrationError(CoreError):
    """Raised when registration operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        registry_key: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.registry_key = registry_key


class ExecutionError(CoreError):
    """Raised when execution fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        execution_id: Optional[str] = None,
        timeout: bool = False,
        cancelled: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.execution_id = execution_id
        self.timeout = timeout
        self.cancelled = cancelled


class SchedulingError(CoreError):
    """Raised when scheduling operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        task_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.task_id = task_id


class StateError(CoreError):
    """Raised when state operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        version_conflict: bool = False,
        owner_mismatch: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.version_conflict = version_conflict
        self.owner_mismatch = owner_mismatch


class SynchronizationError(CoreError):
    """Raised when synchronization fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        timeout: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.timeout = timeout


class IntegrityError(CoreError):
    """Raised when integrity validation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        path: Optional[str] = None,
        violations: Optional[list] = None,
        critical: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.path = path
        self.violations = violations or []
        self.critical = critical


class StartupError(CoreError):
    """Raised when startup fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        failed_component: Optional[str] = None,
        partial_success: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.failed_component = failed_component
        self.partial_success = partial_success


class ShutdownError(CoreError):
    """Raised when shutdown fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        failed_service: Optional[str] = None,
        timeout: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.failed_service = failed_service
        self.timeout = timeout


class TaskError(CoreError):
    """Base exception for task-related errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        task_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.task_id = task_id


class TaskCancelledError(TaskError):
    """Raised when a task is cancelled."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        task_id: Optional[str] = None,
        source: Optional[Any] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.task_id = task_id
        self.source = source


class TaskTimeoutError(TaskError):
    """Raised when a task exceeds its execution timeout."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        task_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.task_id = task_id
        self.timeout_seconds = timeout_seconds


class SchedulerError(CoreError):
    """Raised when scheduler operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        task_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.task_id = task_id


__all__ = [
    "CoreError",
    "ConfigurationError",
    "LifecycleError",
    "DependencyError",
    "RegistrationError",
    "ExecutionError",
    "SchedulingError",
    "StateError",
    "SynchronizationError",
    "IntegrityError",
    "StartupError",
    "ShutdownError",
    "TaskError",
    "TaskCancelledError",
    "TaskTimeoutError",
    "SchedulerError",
]