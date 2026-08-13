# Core Observability Errors
# ==========================

"""
Canonical exception hierarchy for observability subsystems.

This module defines the failure models for:
- Telemetry collection and export
- Metrics processing
- Tracing operations
- Logging pipelines
- Analytics computations
- Governance enforcement
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


# =============================================================================
# BASE EXCEPTION CLASSES
# =============================================================================

class ObservabilityError(Exception):
    """
    Base exception for all observability-related errors.
    
    This is the canonical root of the observability exception hierarchy.
    All observability subsystems should use exceptions derived from this class.
    """
    
    def __init__(
        self,
        message: str,
        subsystem: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        self.message = message
        self.subsystem = subsystem or "unknown"
        self.context = context or {}
        super().__init__(self._format_message(**kwargs))
    
    def _format_message(self, **kwargs) -> str:
        """Format the full error message with all available information."""
        parts = [f"[{self.subsystem}] {self.message}"]
        
        if kwargs:
            details = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            parts.append(f"({details})")
        
        if self.context:
            ctx_str = "; ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"[context: {ctx_str}]")
        
        return " - ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "type": type(self).__name__,
            "subsystem": self.subsystem,
            "message": self.message,
            "context": self.context,
        }


class TelemetryError(ObservabilityError):
    """Base exception for telemetry-related errors."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(message, subsystem="telemetry", context=context, **kwargs)


class MetricsError(ObservabilityError):
    """Base exception for metrics-related errors."""
    
    def __init__(
        self,
        message: str,
        metric_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if metric_name:
            ctx["metric_name"] = metric_name
        super().__init__(message, subsystem="metrics", context=ctx, **kwargs)


class TraceError(ObservabilityError):
    """Base exception for tracing-related errors."""
    
    def __init__(
        self,
        message: str,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if trace_id:
            ctx["trace_id"] = trace_id
        if span_id:
            ctx["span_id"] = span_id
        super().__init__(message, subsystem="tracing", context=ctx, **kwargs)


class LoggingError(ObservabilityError):
    """Base exception for logging-related errors."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(message, subsystem="logging", context=context, **kwargs)


class ExportError(ObservabilityError):
    """Base exception for export pipeline errors."""
    
    def __init__(
        self,
        message: str,
        exporter_name: Optional[str] = None,
        batch_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if exporter_name:
            ctx["exporter_name"] = exporter_name
        if batch_id:
            ctx["batch_id"] = batch_id
        super().__init__(message, subsystem="export", context=ctx, **kwargs)


class AnalyticsError(ObservabilityError):
    """Base exception for analytics pipeline errors."""
    
    def __init__(
        self,
        message: str,
        pipeline_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if pipeline_name:
            ctx["pipeline_name"] = pipeline_name
        super().__init__(message, subsystem="analytics", context=ctx, **kwargs)


class GovernanceError(ObservabilityError):
    """Base exception for observability governance errors."""
    
    def __init__(
        self,
        message: str,
        policy_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if policy_name:
            ctx["policy_name"] = policy_name
        super().__init__(message, subsystem="governance", context=ctx, **kwargs)


class InstrumentationError(ObservabilityError):
    """Base exception for instrumentation-related errors."""
    
    def __init__(
        self,
        message: str,
        hook_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if hook_type:
            ctx["hook_type"] = hook_type
        super().__init__(message, subsystem="instrumentation", context=ctx, **kwargs)


# =============================================================================
# SPECIFIC ERROR TYPES
# =============================================================================

class MetricsCollectionError(MetricsError):
    """Raised when metrics collection fails."""
    
    def __init__(
        self,
        message: str,
        metric_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(message, metric_name=metric_name, context=context, **kwargs)


class TraceCollectionError(TraceError):
    """Raised when trace collection fails."""
    
    def __init__(
        self,
        message: str,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(message, trace_id=trace_id, span_id=span_id, context=context, **kwargs)


class LogPipelineError(LoggingError):
    """Raised when log pipeline processing fails."""
    
    def __init__(
        self,
        message: str,
        sink_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if sink_name:
            ctx["sink_name"] = sink_name
        super().__init__(message, context=ctx, **kwargs)


class ExportPipelineError(ExportError):
    """Raised when export pipeline processing fails."""
    
    def __init__(
        self,
        message: str,
        exporter_name: Optional[str] = None,
        batch_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(message, exporter_name=exporter_name, batch_id=batch_id, context=context, **kwargs)


class AnalyticsPipelineError(AnalyticsError):
    """Raised when analytics pipeline processing fails."""
    
    def __init__(
        self,
        message: str,
        pipeline_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(message, pipeline_name=pipeline_name, context=context, **kwargs)


class GovernanceViolationError(GovernanceError):
    """Raised when a telemetry governance policy is violated."""
    
    def __init__(
        self,
        message: str,
        policy_name: Optional[str] = None,
        violated_by: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if policy_name:
            ctx["policy_name"] = policy_name
        if violated_by:
            ctx["violated_by"] = violated_by
        super().__init__(message, policy_name=policy_name, context=ctx, **kwargs)


class TelemetryOrchestrationError(ObservabilityError):
    """Raised when telemetry orchestration fails."""
    
    def __init__(
        self,
        message: str,
        component: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if component:
            ctx["component"] = component
        super().__init__(message, subsystem="orchestration", context=ctx, **kwargs)


class SamplingError(ObservabilityError):
    """Raised when sampling configuration or processing fails."""
    
    def __init__(
        self,
        message: str,
        sample_rate: Optional[float] = None,
        policy: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if sample_rate is not None:
            ctx["sample_rate"] = sample_rate
        if policy:
            ctx["policy"] = policy
        super().__init__(message, subsystem="sampling", context=ctx, **kwargs)


class CorrelationError(ObservabilityError):
    """Raised when correlation processing fails."""
    
    def __init__(
        self,
        message: str,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if correlation_id:
            ctx["correlation_id"] = correlation_id
        super().__init__(message, subsystem="correlation", context=ctx, **kwargs)


class DashboardError(ObservabilityError):
    """Raised when dashboard generation or rendering fails."""
    
    def __init__(
        self,
        message: str,
        dashboard_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if dashboard_name:
            ctx["dashboard_name"] = dashboard_name
        super().__init__(message, subsystem="dashboard", context=ctx, **kwargs)


class ProfilingError(ObservabilityError):
    """Raised when profiling operations fail."""
    
    def __init__(
        self,
        message: str,
        profile_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ctx = dict(context or {})
        if profile_type:
            ctx["profile_type"] = profile_type
        super().__init__(message, subsystem="profiling", context=ctx, **kwargs)


# =============================================================================
# ERROR UTILITIES
# =============================================================================

def error_to_dict(error: ObservabilityError) -> Dict[str, Any]:
    """
    Convert an observability error to a dictionary for logging/export.
    
    Args:
        error: The error instance to convert
        
    Returns:
        Dictionary representation suitable for JSON serialization
    """
    result = {
        "error_type": type(error).__name__,
        "subsystem": error.subsystem,
        "message": str(error),
    }
    
    if hasattr(error, 'context') and error.context:
        result["context"] = error.context
    
    return result


def log_error_chain(errors: List[ObservabilityError]) -> str:
    """
    Format a chain of errors for logging.
    
    Args:
        errors: List of errors to format
        
    Returns:
        Multi-line string with all errors formatted
    """
    if not errors:
        return "No errors"
    
    lines = [f"Error chain ({len(errors)} errors):"]
    for i, error in enumerate(errors, 1):
        lines.append(f"  {i}. [{error.subsystem}] {type(error).__name__}: {error.message}")
    
    return "\n".join(lines)


__all__ = [
    # Base exceptions
    "ObservabilityError",
    "TelemetryError",
    "MetricsError",
    "TraceError",
    "LoggingError",
    "ExportError",
    "AnalyticsError",
    "GovernanceError",
    "InstrumentationError",
    
    # Specific error types
    "MetricsCollectionError",
    "TraceCollectionError",
    "LogPipelineError",
    "ExportPipelineError",
    "AnalyticsPipelineError",
    "GovernanceViolationError",
    "TelemetryOrchestrationError",
    "SamplingError",
    "CorrelationError",
    "DashboardError",
    "ProfilingError",
    
    # Utilities
    "error_to_dict",
    "log_error_chain",
]