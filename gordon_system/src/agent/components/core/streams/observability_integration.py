# Stream Observability Integration - Phase 3.11.16
# ================================================

"""
Integration layer between Stream subsystem and Observability.

This module provides passive instrumentation hooks that connect stream operations
to the observability architecture WITHOUT modifying execution behavior.

CRITICAL PRINCIPLE: All integration is PASSIVE. It only:
    - Records metric points
    - Emits telemetry events
    - Creates diagnostic findings (read-only)
    - Logs structured records
    
It NEVER:
    - Modifies stream state or data
    - Influences scheduling decisions
    - Triggers recovery or remediation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# Import from streams modules
# Import from streams modules - use absolute imports
from stream_registry import StreamRegistry
from publisher_subscriber import (
    PublisherDescriptor,
    SubscriberDescriptor,
    SubscriptionState,
)
from lifecycle import StreamLifecycleState
from checkpoints import CheckpointDescriptor

# Import from observability modules - use absolute imports
from observability.metrics import (
    StreamMetricType,
    create_stream_metric_point,
    StreamMetricsAccumulator,
)
from observability.telemetry import (
    TelemetryEventType,
    TelemetryLevel,
    create_telemetry_record,
    TelemetryExportBatch,
)
from observability.diagnostics import (
    DiagnosticSeverity,
    create_diagnostic_finding,
)


# =============================================================================
# OBSERVABILITY INTEGRATION CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class ObservabilityIntegrationConfig:
    """
    Immutable configuration for observability integration.
    
    Defines which observability layers are active and their settings.
    All settings are read-only - they never modify stream behavior.
    """
    
    # Metrics collection
    collect_metrics: bool = True
    metric_aggregation_window_seconds: float = 60.0
    
    # Telemetry collection
    collect_telemetry: bool = True
    telemetry_sampling_rate: float = 1.0  # 1.0 = all events, 0.5 = 50%
    
    # Diagnostics
    enable_diagnostics: bool = True
    diagnostic_threshold_backlog: int = 1000
    
    # Logging
    enable_logging: bool = True
    log_level: str = "info"  # debug, info, notice, warning, error, critical


# =============================================================================
# STREAM OBSERVABILITY INTEGRATION
# =============================================================================


class StreamObservabilityIntegration:
    """
    Passive observability integration for stream operations.
    
    This class provides instrumentation hooks that connect stream operations
    to the observability architecture WITHOUT modifying execution behavior.
    
    CRITICAL PRINCIPLE: All methods are PASSIVE. They only record observations.
    """
    
    def __init__(
        self,
        config: ObservabilityIntegrationConfig = None,
        metrics_accumulator: StreamMetricsAccumulator = None,
    ):
        """Initialize the integration with optional configuration."""
        self._config = config or ObservabilityIntegrationConfig()
        self._metrics = metrics_accumulator or StreamMetricsAccumulator()
        
        # Timestamp tracking for rate calculations
        self._start_time_utc = time.time()
    
    def record_stream_creation(
        self,
        stream_id: str,
        lifecycle_state: Optional[StreamLifecycleState] = None,
    ) -> None:
        """
        Record a stream creation event.
        
        This method is PASSIVE - it only records metric observations.
        It never modifies the stream or affects its behavior.
        """
        if not self._config.collect_metrics:
            return
        
        # Record metrics
        self._metrics.increment_publication()
        self._metrics.record(
            StreamMetricType.STREAM_COUNT,
            value=1.0,
            stream_id=stream_id,
            labels={"operation": "create"},
        )
        
        # Emit telemetry event
        if self._config.collect_telemetry:
            create_telemetry_record(
                TelemetryEventType.STREAM_CREATED,
                level=TelemetryLevel.INFO,
                stream_id=stream_id,
            )
    
    def record_stream_activation(
        self,
        stream_id: str,
        lifecycle_state: Optional[StreamLifecycleState] = None,
    ) -> None:
        """Record a stream activation event."""
        if not self._config.collect_metrics:
            return
        
        self._metrics.record(
            StreamMetricType.STREAM_COUNT,
            value=1.0,
            stream_id=stream_id,
            labels={"operation": "activate"},
        )
        
        if self._config.collect_telemetry:
            create_telemetry_record(
                TelemetryEventType.STREAM_ACTIVATED,
                level=TelemetryLevel.INFO,
                stream_id=stream_id,
            )
    
    def record_publication(
        self,
        stream_id: str,
        publisher_id: str,
        record_count: int = 1,
        succeeded: bool = True,
        rejected: bool = False,
    ) -> None:
        """
        Record a publication event.
        
        Args:
            stream_id: Which stream
            publisher_id: Which publisher
            record_count: Number of records published
            succeeded: Whether publication succeeded
            rejected: Whether publication was rejected (backpressure)
            
        This method is PASSIVE - it only records metric observations.
        """
        if not self._config.collect_metrics:
            return
        
        # Record counters
        for _ in range(record_count):
            self._metrics.increment_publication()
        
        # Record rate metrics
        elapsed = time.time() - self._start_time_utc
        if elapsed > 0:
            rate = record_count / elapsed
            self._metrics.record(
                StreamMetricType.PUBLICATION_RATE,
                value=rate,
                stream_id=stream_id,
                component_id=publisher_id,
            )
        
        # Record success/failure metrics
        if succeeded:
            self._metrics.record(
                StreamMetricType.PUBLICATION_COUNT,
                value=float(record_count),
                stream_id=stream_id,
                labels={"result": "success"},
            )
        else:
            self._metrics.record(
                StreamMetricType.REJECTION_RATE,
                value=float(record_count),
                stream_id=stream_id,
                component_id=publisher_id,
                labels={"reason": "failure" if not succeeded else "backpressure"},
            )
        
        # Emit telemetry event
        if self._config.collect_telemetry:
            level = TelemetryLevel.ERROR if rejected else TelemetryLevel.INFO
            event_type = (
                TelemetryEventType.PUBLICATION_REJECTED
                if rejected
                else TelemetryEventType.PUBLICATION_SUCCEEDED
            )
            create_telemetry_record(
                event_type,
                level=level,
                stream_id=stream_id,
                component_id=publisher_id,
            )
    
    def record_subscription(
        self,
        stream_id: str,
        subscriber_id: str,
        record_count: int = 1,
        succeeded: bool = True,
        lag_records: int = 0,
    ) -> None:
        """
        Record a subscription event.
        
        Args:
            stream_id: Which stream
            subscriber_id: Which subscriber
            record_count: Number of records consumed
            succeeded: Whether subscription succeeded
            lag_records: Current cursor lag in records
            
        This method is PASSIVE - it only records metric observations.
        """
        if not self._config.collect_metrics:
            return
        
        # Record counters
        for _ in range(record_count):
            self._metrics.increment_subscription()
        
        # Record rate metrics
        elapsed = time.time() - self._start_time_utc
        if elapsed > 0:
            rate = record_count / elapsed
            self._metrics.record(
                StreamMetricType.SUBSCRIPTION_RATE,
                value=rate,
                stream_id=stream_id,
                component_id=subscriber_id,
            )
        
        # Record cursor lag metrics
        self._metrics.record(
            StreamMetricType.CURSOR_LAG_RECORDS,
            value=float(lag_records),
            stream_id=stream_id,
            component_id=subscriber_id,
        )
        
        # Emit telemetry event
        if self._config.collect_telemetry:
            level = TelemetryLevel.WARNING if lag_records > 1000 else TelemetryLevel.INFO
            create_telemetry_record(
                TelemetryEventType.SUBSCRIPTION_SUBSCRIBED,
                level=level,
                stream_id=stream_id,
                component_id=subscriber_id,
            )
    
    def record_replay(
        self,
        stream_id: str,
        subscriber_id: str,
        records_replayed: int = 0,
        success: bool = True,
        duration_seconds: float = 0.0,
    ) -> None:
        """Record a replay event."""
        if not self._config.collect_metrics:
            return
        
        self._metrics.increment_replay()
        
        if duration_seconds > 0:
            rate = records_replayed / duration_seconds
            self._metrics.record(
                StreamMetricType.REPLAY_RATE,
                value=rate,
                stream_id=stream_id,
                component_id=subscriber_id,
            )
        
        if self._config.collect_telemetry:
            create_telemetry_record(
                TelemetryEventType.REPLAY_COMPLETED if success else TelemetryEventType.REPLAY_FAILED,
                level=TelemetryLevel.INFO,
                stream_id=stream_id,
                component_id=subscriber_id,
            )
    
    def record_checkpoint(
        self,
        stream_id: str,
        checkpoint_id: str,
        success: bool = True,
        duration_seconds: float = 0.0,
    ) -> None:
        """Record a checkpoint event."""
        if not self._config.collect_metrics:
            return
        
        self._metrics.increment_checkpoint()
        
        if duration_seconds > 0:
            self._metrics.record(
                StreamMetricType.CHECKPOINT_RATE,
                value=1.0 / duration_seconds if duration_seconds > 0 else 0.0,
                stream_id=stream_id,
            )
        
        if self._config.collect_telemetry:
            create_telemetry_record(
                TelemetryEventType.CHECKPOINT_CREATED if success else TelemetryEventType.CHECKPOINT_RESTORED,
                level=TelemetryLevel.INFO,
                stream_id=stream_id,
                component_id=checkpoint_id,
            )
    
    def record_lifecycle_transition(
        self,
        stream_id: str,
        from_state: StreamLifecycleState,
        to_state: StreamLifecycleState,
    ) -> None:
        """Record a lifecycle state transition."""
        if not self._config.collect_metrics:
            return
        
        # Record state-based metrics
        if to_state == StreamLifecycleState.ACTIVE:
            self._metrics.record(
                StreamMetricType.STREAM_COUNT,
                value=1.0,
                stream_id=stream_id,
                labels={"state": "active"},
            )
        
        # Emit telemetry event
        if self._config.collect_telemetry:
            create_telemetry_record(
                TelemetryEventType.STREAM_PAUSED
                if to_state == StreamLifecycleState.PAUSED
                else TelemetryEventType.STREAM_RESUMED
                if from_state == StreamLifecycleState.PAUSED and to_state == StreamLifecycleState.ACTIVE
                else TelemetryEventType.STREAM_FAILED
                if to_state == StreamLifecycleState.FAILED
                else TelemetryEventType.STREAM_CLOSED
                if to_state == StreamLifecycleState.CLOSED
                else TelemetryEventType.STREAM_CREATED,
                level=TelemetryLevel.INFO,
                stream_id=stream_id,
            )
    
    def record_backpressure(
        self,
        stream_id: str,
        active: bool = True,
        backlog_size: int = 0,
    ) -> None:
        """Record a backpressure event."""
        if not self._config.collect_metrics:
            return
        
        # Record congestion metrics
        self._metrics.record(
            StreamMetricType.CONGESTION_LEVEL,
            value=min(1.0, backlog_size / 1000.0),  # Normalize to 0-1 range
            stream_id=stream_id,
        )
        
        if active:
            self._metrics.record(
                StreamMetricType.BACKPRESSURE_ACTIVE,
                value=1.0,
                stream_id=stream_id,
            )
        
        # Emit telemetry event
        if self._config.collect_telemetry:
            create_telemetry_record(
                TelemetryEventType.BACKPRESSURE_TRIGGERED
                if active
                else TelemetryEventType.BACKPRESSURE_RELEASED,
                level=TelemetryLevel.WARNING if backlog_size > 10000 else TelemetryLevel.INFO,
                stream_id=stream_id,
            )
    
    def generate_diagnostics_report(
        self,
        stream_id: str,
        current_backlog: int = 0,
        cursor_lag: int = 0,
        total_publications: int = 0,
        total_subscriptions: int = 0,
    ) -> "ObservabilityDiagnosticReport":
        """
        Generate a diagnostics report for a stream.
        
        This method is PASSIVE - it only reads current state and reports findings.
        It never modifies the stream or triggers any remediation.
        
        Returns:
            Immutable diagnostic report
        """
        if not self._config.enable_diagnostics:
            return ObservabilityDiagnosticReport.create_empty(stream_id)
        
        findings = []
        
        # Check backlog size
        if current_backlog > self._config.diagnostic_threshold_backlog:
            findings.append(
                create_diagnostic_finding(
                    category="backpressure",
                    finding_type="high_backlog",
                    message=f"Stream {stream_id} has high backlog: {current_backlog}",
                    severity=DiagnosticSeverity.WARNING,
                    stream_id=stream_id,
                )
            )
        
        # Check cursor lag
        if cursor_lag > 1000:
            findings.append(
                create_diagnostic_finding(
                    category="cursor",
                    finding_type="high_cursor_lag",
                    message=f"Stream {stream_id} has high cursor lag: {cursor_lag}",
                    severity=DiagnosticSeverity.WARNING,
                    stream_id=stream_id,
                )
            )
        
        return ObservabilityDiagnosticReport(
            report_id=f"diag-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
            created_at_utc=time.time(),
            stream_id=stream_id,
            findings=tuple(findings),
        )


# =============================================================================
# OBSERVABILITY DIAGNOSTIC REPORT
# =============================================================================


@dataclass(frozen=True)
class ObservabilityDiagnosticReport:
    """
    Immutable diagnostic report from observability integration.
    
    Contains findings without modifying any stream state.
    Used for read-only inspection of stream health and behavior.
    """
    
    # Identity
    report_id: str                  # Unique ID for this report
    
    # Timestamps
    created_at_utc: float           # When report was generated
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # Findings
    findings: Tuple[Any, ...] = field(default_factory=tuple)
    
    def has_findings(self) -> bool:
        """Check if this report contains any diagnostic findings."""
        return len(self.findings) > 0
    
    def get_critical_findings(self) -> Tuple[Any, ...]:
        """Get only critical severity findings."""
        return tuple(f for f in self.findings if hasattr(f, 'severity') and str(getattr(f, 'severity', '')).lower().startswith('critical'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "report_id": self.report_id,
            "created_at_utc": self.created_at_utc,
            "stream_id": self.stream_id,
            "findings_count": len(self.findings),
        }
    
    @classmethod
    def create_empty(cls, stream_id: str) -> "ObservabilityDiagnosticReport":
        """Create an empty report for a stream."""
        return cls(
            report_id=f"diag-{time.monotonic_ns()}-{hash(stream_id) % 1000:04d}",
            created_at_utc=time.time(),
            stream_id=stream_id,
            findings=tuple(),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_observability_integration(
    config: Optional[ObservabilityIntegrationConfig] = None,
    metrics_accumulator: Optional[StreamMetricsAccumulator] = None,
) -> StreamObservabilityIntegration:
    """
    Create a new observability integration instance.
    
    Args:
        config: Configuration for observability layers
        metrics_accumulator: Optional metrics accumulator
        
    Returns:
        New StreamObservabilityIntegration instance
    """
    return StreamObservabilityIntegration(
        config=config or ObservabilityIntegrationConfig(),
        metrics_accumulator=metrics_accumulator or StreamMetricsAccumulator(),
    )


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) 
                      for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Configuration
    "ObservabilityIntegrationConfig",
    
    # Integration classes
    "StreamObservabilityIntegration",
    
    # Diagnostic report
    "ObservabilityDiagnosticReport",
    
    # Factory functions
    "create_observability_integration",
    "dataclass_replace",
]