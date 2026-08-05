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


class AssemblyError(CoreError):
    """Raised when runtime assembly fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        missing_authority: Optional[str] = None,
        wiring_error: bool = False,
        validation_failed: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.missing_authority = missing_authority
        self.wiring_error = wiring_error
        self.validation_failed = validation_failed


class ActivationError(CoreError):
    """Raised when runtime activation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        failed_component: Optional[str] = None,
        partial_success: bool = False,
        primary_cause: Optional[Exception] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.failed_component = failed_component
        self.partial_success = partial_success
        self.primary_cause = primary_cause


class RuntimeStateTransitionError(CoreError):
    """Raised when runtime state transition fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
        version_conflict: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.from_state = from_state
        self.to_state = to_state
        self.version_conflict = version_conflict


# =============================================================================
# OBSERVABILITY EXCEPTIONS (Phase 3.8.6)
# =============================================================================

class ObservabilityError(CoreError):
    """Base exception for all observability-related errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        subsystem: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.subsystem = subsystem


class TelemetryError(ObservabilityError):
    """Raised when telemetry operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        event_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="telemetry", cause=cause)
        self.event_type = event_type


class MetricsError(ObservabilityError):
    """Raised when metrics operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        metric_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="metrics", cause=cause)
        self.metric_name = metric_name


class TraceError(ObservabilityError):
    """Raised when tracing operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="tracing", cause=cause)
        self.trace_id = trace_id
        self.span_id = span_id


class LoggingError(ObservabilityError):
    """Raised when logging operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        log_level: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="logging", cause=cause)
        self.log_level = log_level


class DiagnosticsError(ObservabilityError):
    """Raised when diagnostics operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        diagnostic_code: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="diagnostics", cause=cause)
        self.diagnostic_code = diagnostic_code


class HealthError(ObservabilityError):
    """Raised when health evaluation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        subject_id: Optional[str] = None,
        state: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="health", cause=cause)
        self.subject_id = subject_id
        self.state = state


class CollectorError(ObservabilityError):
    """Raised when telemetry collectors fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        collector_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="collector", cause=cause)
        self.collector_type = collector_type


class ExporterError(ObservabilityError):
    """Raised when telemetry exporters fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        exporter_type: Optional[str] = None,
        batch_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="exporter", cause=cause)
        self.exporter_type = exporter_type
        self.batch_id = batch_id


class TraceCollectionError(TelemetryError):
    """Raised when trace collection fails."""


class MetricsCollectionError(MetricsError):
    """Raised when metrics collection fails."""


class LoggingPipelineError(LoggingError):
    """Raised when logging pipeline operations fail."""


class SamplingError(ObservabilityError):
    """Raised when sampling decisions fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        policy: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="sampling", cause=cause)
        self.policy = policy


class CorrelationError(ObservabilityError):
    """Raised when correlation propagation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        correlation_id: Optional[str] = None,
        context_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, subsystem="correlation", cause=cause)
        self.correlation_id = correlation_id
        self.context_type = context_type


class HealthEvaluationError(HealthError):
    """Raised when health evaluation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        probe_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.probe_name = probe_name


__all__ = [
    # Core exceptions
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
    "AssemblyError",
    "ActivationError",
    "RuntimeStateTransitionError",
    
    # Observability exceptions (Phase 3.8.6)
    "ObservabilityError",
    "TelemetryError",
    "MetricsError",
    "TraceError",
    "LoggingError",
    "DiagnosticsError",
    "HealthError",
    "CollectorError",
    "ExporterError",
    "TraceCollectionError",
    "MetricsCollectionError",
    "LoggingPipelineError",
    "SamplingError",
    "CorrelationError",
    "HealthEvaluationError",
]