# Core Observability Manager
# ===========================

"""
Orchestration and coordination of observability infrastructure for Gordon.

This module provides:
- ObservabilityManager: Canonical authority orchestrating all observability
- Unified API for logging, tracing, telemetry, metrics, diagnostics
- Runtime-scoped observability (one per runtime)
- Correlation propagation across subsystems

Observability is OBSERVATIONAL - it never changes runtime behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import threading
import time
import uuid

from .models import (
    LogLevel,
    LogRecord,
    create_log,
    TelemetryEvent,
    TraceId,
    SpanId,
)
from .logging_manager import LoggingManager, ConsoleSink, MemorySink, FakeSink
from .correlation_manager import CorrelationManager, CorrelationContext
from .metrics_manager import MetricsManager, Counter, Gauge, Histogram
from .telemetry_manager import TelemetryManager, NoOpExporter, FakeExporter
from .diagnostics_manager import DiagnosticsManager


# =============================================================================
# OBSERVABILITY CONFIGURATION
# =============================================================================

@dataclass
class ObservabilityConfig:
    """Configuration for the observability system."""
    
    # Runtime identity
    runtime_id: str = ""
    
    # Sampling configuration
    log_sample_rate: float = 1.0  # 1.0 = 100%, sample all logs
    log_sampling_policy: str = "always"  # always, never, probabilistic
    
    # History limits
    max_log_history: int = 10000
    max_telemetry_events: int = 10000
    max_diagnostics_findings: int = 1000
    
    # Export configuration
    enable_console_logging: bool = True
    console_level_threshold: str = "TRACE"
    
    # Correlation configuration
    enable_correlation_propagation: bool = True


# =============================================================================
# OBSERVABILITY MANAGER
# =============================================================================

class ObservabilityManager:
    """
    Canonical authority for observability orchestration.
    
    Provides a unified interface to all observability subsystems:
        - LoggingManager: Structured logging with sinks
        - CorrelationManager: Runtime correlation state
        - MetricsManager: Metric collection (counters, gauges, histograms)
        - TelemetryManager: Event collection and export
        - DiagnosticsManager: Diagnostic findings and reports
    
    INVAR: Exactly one ObservabilityManager exists per runtime.
    INVAR: Observability is observational - never changes runtime behavior.
    
    Usage:
        # Create manager (one per runtime)
        config = ObservabilityConfig(runtime_id="runtime_123")
        observability = ObservabilityManager(config)
        
        # Use unified logging API
        observability.log.info("Task started", task_id="abc")
        observability.log.error("Task failed", exception=e, task_id="abc")
        
        # Use metrics
        counter = observability.metrics.create_counter("tasks.completed")
        counter.inc()
        
        # Get diagnostic report
        report = observability.diagnostics.get_report("runtime")
    """
    
    def __init__(
        self,
        config: Optional[ObservabilityConfig] = None,
    ) -> None:
        import uuid
        
        actual_config = config or ObservabilityConfig()
        self._runtime_id = actual_config.runtime_id or str(uuid.uuid4())
        
        # Thread-safe state
        self._lock = threading.RLock()
        
        # Initialize subsystems with proper configuration
        self._init_logging(actual_config)
        self._init_correlation(actual_config)
        self._init_metrics(actual_config)
        self._init_telemetry(actual_config)
        self._init_diagnostics(actual_config)
    
    def _init_logging(self, config: ObservabilityConfig) -> None:
        """Initialize the LoggingManager."""
        import random
        
        # Create sampling config based on policy
        from .logging_manager import SamplingPolicy, SamplingConfig
        
        policy_str = config.log_sampling_policy.lower()
        
        if policy_str == "never":
            policy = SamplingPolicy.NEVER
        elif policy_str == "probabilistic":
            policy = SamplingPolicy.PROBABILISTIC
        elif policy_str == "error_priority":
            policy = SamplingPolicy.ERROR_PRIORITY
        else:
            policy = SamplingPolicy.ALWAYS
        
        sampling_config = SamplingConfig(
            policy=policy,
            sample_rate=config.log_sample_rate
        )
        
        self._logging = LoggingManager(
            runtime_id=self._runtime_id,
            sampling_config=sampling_config,
            max_history=config.max_log_history
        )
        
        # Add console sink if enabled
        if config.enable_console_logging:
            self._logging.add_sink(ConsoleSink())
    
    def _init_correlation(self, config: ObservabilityConfig) -> None:
        """Initialize the CorrelationManager."""
        self._correlation = CorrelationManager(
            runtime_id=self._runtime_id,
        )
    
    def _init_metrics(self, config: ObservabilityConfig) -> None:
        """Initialize the MetricsManager."""
        self._metrics = MetricsManager(runtime_id=self._runtime_id)
    
    def _init_telemetry(self, config: ObservabilityConfig) -> None:
        """Initialize the TelemetryManager."""
        self._telemetry = TelemetryManager(
            runtime_id=self._runtime_id,
            max_events_per_batch=config.max_telemetry_events // 10,
            max_history_size=config.max_telemetry_events
        )
    
    def _init_diagnostics(self, config: ObservabilityConfig) -> None:
        """Initialize the DiagnosticsManager."""
        self._diagnostics = DiagnosticsManager(
            runtime_id=self._runtime_id,
            max_findings_per_scope=config.max_diagnostics_findings,
            retention_seconds=3600.0  # 1 hour default
        )
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    # ------------------------------------------------------------------
    # Subsystem Accessors (for direct access to each manager)
    # ------------------------------------------------------------------
    
    @property
    def log(self) -> LoggingManager:
        """Access the LoggingManager directly."""
        return self._logging
    
    @property
    def correlation(self) -> CorrelationManager:
        """Access the CorrelationManager directly."""
        return self._correlation
    
    @property
    def metrics(self) -> MetricsManager:
        """Access the MetricsManager directly."""
        return self._metrics
    
    @property
    def telemetry(self) -> TelemetryManager:
        """Access the TelemetryManager directly."""
        return self._telemetry
    
    @property
    def diagnostics(self) -> DiagnosticsManager:
        """Access the DiagnosticsManager directly."""
        return self._diagnostics
    
    # ------------------------------------------------------------------
    # Convenience Methods (unified API)
    # ------------------------------------------------------------------
    
    # --- Logging convenience methods ---
    
    def debug(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a DEBUG-level message."""
        return self._logging.debug(message, runtime_id=self._runtime_id, **payload)
    
    def info(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log an INFO-level message."""
        return self._logging.info(message, runtime_id=self._runtime_id, **payload)
    
    def notice(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a NOTICE-level message."""
        return self._logging.notice(message, runtime_id=self._runtime_id, **payload)
    
    def warning(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a WARNING-level message."""
        return self._logging.warning(message, runtime_id=self._runtime_id, **payload)
    
    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **payload
    ) -> bool:
        """Log an ERROR-level message."""
        return self._logging.error(message, exception=exception, runtime_id=self._runtime_id, **payload)
    
    def critical(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a CRITICAL-level message."""
        return self._logging.critical(message, runtime_id=self._runtime_id, **payload)
    
    # --- Correlation convenience methods ---
    
    def get_correlation_id(self) -> str:
        """Get current correlation ID from correlation manager."""
        return self._correlation.get_correlation_id()
    
    # ------------------------------------------------------------------
    # Tracing Integration
    # ------------------------------------------------------------------
    
    def trace_context(
        self,
        span_name: str,
        trace_id: Optional[str] = None,
    ):
        """
        Create a tracing context for span-scoped correlation.
        
        Usage:
            with observability.trace_context("my_operation"):
                # All logs/metrics in this scope will have the same trace/span
                pass
        
        Args:
            span_name: Human-readable operation name
            trace_id: Parent trace ID (optional)
            
        Returns:
            Context manager for span context
        """
        return self._correlation.span_context(
            span_name=span_name,
            trace_id=trace_id or str(TraceId.generate())
        )
    
    # ------------------------------------------------------------------
    # Metrics convenience methods ---
    
    def record_counter(
        self,
        name: str,
        amount: float = 1.0,
        **tags
    ) -> None:
        """Record a counter value."""
        self._metrics.record_counter(name, amount)
        
        # Also emit as telemetry event if enabled
        event = TelemetryEvent(
            runtime_id=self._runtime_id,
            event_type="metric",
            name=name,
            value=amount,
            tags=tags
        )
        self._telemetry.collect(event)
    
    def set_gauge(
        self,
        name: str,
        value: float,
        **tags
    ) -> None:
        """Set a gauge value."""
        self._metrics.set_gauge(name, value)
        
        # Also emit as telemetry event if enabled
        event = TelemetryEvent(
            runtime_id=self._runtime_id,
            event_type="metric",
            name=name,
            value=value,
            tags=tags
        )
        self._telemetry.collect(event)
    
    def observe_histogram(
        self,
        name: str,
        value: float,
        **tags
    ) -> None:
        """Record a histogram observation."""
        self._metrics.observe_histogram(name, value)
        
        # Also emit as telemetry event if enabled
        event = TelemetryEvent(
            runtime_id=self._runtime_id,
            event_type="metric",
            name=f"{name}_value",
            value=value,
            tags=tags
        )
        self._telemetry.collect(event)
    
    # ------------------------------------------------------------------
    # Diagnostics convenience methods ---
    
    def info_finding(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> None:
        """Generate an INFO-level diagnostic finding."""
        self._diagnostics.info(source, code, title, **evidence)
    
    def warning_finding(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> None:
        """Generate a WARNING-level diagnostic finding."""
        self._diagnostics.warning(source, code, title, **evidence)
    
    def error_finding(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> None:
        """Generate an ERROR-level diagnostic finding."""
        self._diagnostics.error(source, code, title, **evidence)
    
    def critical_finding(
        self,
        source: str,
        code: str,
        title: str,
        **evidence
    ) -> None:
        """Generate a CRITICAL-level diagnostic finding."""
        self._diagnostics.critical(source, code, title, **evidence)
    
    # ------------------------------------------------------------------
    # Export and Reporting ---
    
    def get_runtime_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive runtime report.
        
        Returns:
            Dictionary containing logs, metrics, diagnostics snapshot
        """
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "timestamp_utc": time.time(),
                
                # Logs
                "logs": {
                    "count": self._logging.history_size,
                    "emitted_total": self._logging.total_emitted,
                    "dropped_total": self._logging.total_dropped,
                },
                
                # Metrics
                "metrics": self._metrics.get_snapshot().to_serializable(),
                
                # Diagnostics
                "diagnostics": self._diagnostics.capture_snapshot().__dict__,
                
                # Telemetry
                "telemetry": {
                    "count": self._telemetry.get_event_count(),
                    "collected_total": self._telemetry.total_collected,
                    "exported_total": self._telemetry.total_exported,
                },
            }
    
    def export_all(self):
        """
        Export all telemetry data to registered exporters.
        
        Returns:
            Number of events exported
        """
        import asyncio
        
        return asyncio.run(self._telemetry.export_all())
    
    # ------------------------------------------------------------------
    # Lifecycle ---
    
    async def close(self) -> None:
        """Close the manager and all subsystems."""
        await self._logging.close()
        await self._telemetry.close()


# =============================================================================
# RUNTIME OBSERVABILITY CONTAINER
# =============================================================================

class RuntimeObservability:
    """
    Container for runtime-scoped observability infrastructure.
    
    Provides a single entry point to all observability functionality
    for a specific runtime instance.
    
    Usage:
        # Create with default config
        obs = RuntimeObservability()
        
        # Or with custom config
        config = ObservabilityConfig(
            runtime_id="my_runtime",
            log_sample_rate=0.1,  # Sample at 10%
        )
        obs = RuntimeObservability(config)
    """
    
    def __init__(self, config: Optional[ObservabilityConfig] = None) -> None:
        self._manager = ObservabilityManager(config)
    
    @property
    def manager(self) -> ObservabilityManager:
        """Get the underlying observability manager."""
        return self._manager
    
    # Delegates to manager for convenience
    @property
    def log(self) -> LoggingManager:
        return self._manager.log
    
    @property
    def correlation(self) -> CorrelationManager:
        return self._manager.correlation
    
    @property
    def metrics(self) -> MetricsManager:
        return self._manager.metrics
    
    @property
    def telemetry(self) -> TelemetryManager:
        return self._manager.telemetry
    
    @property
    def diagnostics(self) -> DiagnosticsManager:
        return self._manager.diagnostics
    
    # Convenience methods
    def debug(self, message: str, **payload) -> bool:
        return self._manager.debug(message, **payload)
    
    def info(self, message: str, **payload) -> bool:
        return self._manager.info(message, **payload)
    
    def warning(self, message: str, **payload) -> bool:
        return self._manager.warning(message, **payload)
    
    def error(self, message: str, exception: Optional[Exception] = None, **payload) -> bool:
        return self._manager.error(message, exception=exception, **payload)
    
    async def close(self) -> None:
        """Close all observability subsystems."""
        await self._manager.close()


__all__ = [
    "ObservabilityConfig",
    "ObservabilityManager",
    "RuntimeObservability",
]