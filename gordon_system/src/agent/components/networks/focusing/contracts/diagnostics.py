# Focusing Network Diagnostics Contracts
# =======================================

"""
Diagnostics contracts for the FocusingNetwork Phase 4.2.8.

These define observational interfaces for diagnostics without exposing
implementation details. The FocusingNetwork sends diagnostics but never owns
the storage or processing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
from datetime import datetime


# =============================================================================
# DIAGNOSTICS SINK - Primary interface for diagnostic output
# =============================================================================

@dataclass(frozen=True)
class DiagnosticsSink:
    """
    Sink for diagnostic events from the FocusingNetwork.
    
    Receives all diagnostic events but never owns or modifies them.
    The FocusingNetwork sends to this sink but doesn't control its storage.
    
    PROPERTIES:
        • Observational only - no computation
        • Versioned for compatibility tracking
        • External ownership of stored data
    """
    
    # Sink identity
    sink_id: str = field(default_factory=lambda: f"diag_sink_{id(datetime.utcnow()):x}")
    """Unique identifier for this diagnostics sink."""
    
    # Configuration
    enabled: bool = True
    """Whether this sink is active."""
    
    verbosity_level: int = 1
    """Level of detail to emit (0=silent, 5=verbose)."""
    
    # Timestamp tracking
    first_event_utc: Optional[datetime] = None
    """When the first event was received."""
    
    last_event_utc: Optional[datetime] = None
    """When the last event was received."""
    
    event_count: int = 0
    """Total number of events received."""
    
    # Event buffering (implementation detail - not exposed)
    _buffer_size: int = field(default=1000, repr=False)
    """Maximum buffer size for events."""
    
    def receive_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Receive a diagnostic event.
        
        Args:
            event_type: Type of event (e.g., 'assessment', 'trace')
            data: Event-specific data dictionary
        """
        if not self.enabled:
            return
        
        self.event_count += 1
        now = datetime.utcnow()
        if self.first_event_utc is None:
            object.__setattr__(self, "first_event_utc", now)
        object.__setattr__(self, "last_event_utc", now)
    
    def receive_trace(self, trace_type: str, data: Dict[str, Any]) -> None:
        """
        Receive a trace event.
        
        Args:
            trace_type: Type of trace (e.g., 'pipeline_start', 'stage_complete')
            data: Trace-specific data dictionary
        """
        self.receive_event("trace", {"type": trace_type, **data})
    
    def receive_metric(self, metric_name: str, value: float) -> None:
        """
        Receive a metric event.
        
        Args:
            metric_name: Name of the metric
            value: Numeric value
        """
        self.receive_event("metric", {"name": metric_name, "value": value})


# =============================================================================
# PIPELINE TRACE CONSUMER - Traces pipeline execution
# =============================================================================

@dataclass(frozen=True)
class PipelineTraceConsumer:
    """
    Consumer of pipeline execution traces.
    
    Receives trace events about pipeline stages without exposing how tracing
    is implemented. Only the trace data, not the tracing mechanism.
    
    PROPERTIES:
        • Observational only - no computation
        • Versioned for compatibility tracking
        • External ownership of trace storage
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"pipeline_trace_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Trace data
    pipeline_start_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Pipeline start trace events."""
    
    stage_start_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Stage start trace events."""
    
    stage_end_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Stage end trace events."""
    
    pipeline_end_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Pipeline end trace events."""
    
    def receive_pipeline_start(self, data: Dict[str, Any]) -> None:
        """Record a pipeline start event."""
        object.__setattr__(
            self,
            "pipeline_start_events",
            self.pipeline_start_events + (data,)
        )
    
    def receive_stage_start(self, stage_name: str, data: Dict[str, Any]) -> None:
        """Record a stage start event."""
        event = {"stage": stage_name, **data}
        object.__setattr__(
            self,
            "stage_start_events",
            self.stage_start_events + (event,)
        )
    
    def receive_stage_end(self, stage_name: str, data: Dict[str, Any]) -> None:
        """Record a stage end event."""
        event = {"stage": stage_name, **data}
        object.__setattr__(
            self,
            "stage_end_events",
            self.stage_end_events + (event,)
        )
    
    def receive_pipeline_end(self, data: Dict[str, Any]) -> None:
        """Record a pipeline end event."""
        object.__setattr__(
            self,
            "pipeline_end_events",
            self.pipeline_end_events + (data,)
        )


# =============================================================================
# ASSESSMENT TRACE CONSUMER - Traces assessment generation
# =============================================================================

@dataclass(frozen=True)
class AssessmentTraceConsumer:
    """
    Consumer of assessment trace events.
    
    Receives traces about assessment generation without exposing how tracing
    is implemented. Only the trace data, not the tracing mechanism.
    
    PROPERTIES:
        • Observational only - no computation
        • Versioned for compatibility tracking
        • External ownership of trace storage
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"assessment_trace_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Trace data
    assessment_generated_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events when assessments are generated."""
    
    feature_computed_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events when features are computed."""
    
    assessment_complete_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events when assessments are completed."""
    
    def receive_assessment_generated(
        self,
        assessment_type: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Record an assessment generation event.
        
        Args:
            assessment_type: Type of assessment (e.g., 'priority', 'relevance')
            data: Assessment-specific data
        """
        event = {"assessment_type": assessment_type, **data}
        object.__setattr__(
            self,
            "assessment_generated_events",
            self.assessment_generated_events + (event,)
        )
    
    def receive_feature_computed(
        self,
        feature_name: str,
        value: float,
    ) -> None:
        """
        Record a feature computation event.
        
        Args:
            feature_name: Name of the computed feature
            value: Computed feature value
        """
        event = {"feature_name": feature_name, "value": value}
        object.__setattr__(
            self,
            "feature_computed_events",
            self.feature_computed_events + (event,)
        )
    
    def receive_assessment_complete(
        self,
        assessment_id: str,
        overall_score: float,
    ) -> None:
        """
        Record an assessment completion event.
        
        Args:
            assessment_id: ID of the completed assessment
            overall_score: Final overall score
        """
        event = {"assessment_id": assessment_id, "overall_score": overall_score}
        object.__setattr__(
            self,
            "assessment_complete_events",
            self.assessment_complete_events + (event,)
        )


# =============================================================================
# STATE TRACE CONSUMER - Traces state transitions
# =============================================================================

@dataclass(frozen=True)
class StateTraceConsumer:
    """
    Consumer of state transition traces.
    
    Receives traces about state changes without exposing how tracing is
    implemented. Only the trace data, not the tracing mechanism.
    
    PROPERTIES:
        • Observational only - no computation
        • Versioned for compatibility tracking
        • External ownership of trace storage
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"state_trace_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Trace data
    state_transition_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events when states transition."""
    
    focus_shift_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events when focus shifts to new target."""
    
    state_snapshot_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events when state snapshots are captured."""
    
    def receive_state_transition(self, transition_data: Dict[str, Any]) -> None:
        """Record a state transition event."""
        object.__setattr__(
            self,
            "state_transition_events",
            self.state_transition_events + (transition_data,)
        )
    
    def receive_focus_shift(
        self,
        from_target_id: Optional[str],
        to_target_id: Optional[str],
    ) -> None:
        """
        Record a focus shift event.
        
        Args:
            from_target_id: ID of the previously focused target (if any)
            to_target_id: ID of the newly focused target
        """
        event = {
            "from_target_id": from_target_id,
            "to_target_id": to_target_id,
        }
        object.__setattr__(
            self,
            "focus_shift_events",
            self.focus_shift_events + (event,)
        )
    
    def receive_state_snapshot(self, snapshot_data: Dict[str, Any]) -> None:
        """Record a state snapshot event."""
        object.__setattr__(
            self,
            "state_snapshot_events",
            self.state_snapshot_events + (snapshot_data,)
        )


# =============================================================================
# PERFORMANCE TRACE CONSUMER - Traces performance metrics
# =============================================================================

@dataclass(frozen=True)
class PerformanceTraceConsumer:
    """
    Consumer of performance trace events.
    
    Receives traces about performance metrics without exposing how tracing is
    implemented. Only the trace data, not the tracing mechanism.
    
    PROPERTIES:
        • Observational only - no computation
        • Versioned for compatibility tracking
        • External ownership of trace storage
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"perf_trace_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Performance metrics (results only, no measurement logic)
    assessment_duration_ms: float = 0.0
    """Duration of most recent assessment in milliseconds."""
    
    pipeline_duration_ms: float = 0.0
    """Duration of most recent pipeline execution in milliseconds."""
    
    stage_durations_ms: Dict[str, float] = field(default_factory=dict)
    """Durations for each pipeline stage."""
    
    event_count: int = 0
    """Total number of performance events received."""
    
    def record_assessment_duration(self, duration_ms: float) -> None:
        """
        Record an assessment duration.
        
        Args:
            duration_ms: Duration in milliseconds
        """
        self.assessment_duration_ms = duration_ms
    
    def record_pipeline_duration(self, duration_ms: float) -> None:
        """
        Record a pipeline execution duration.
        
        Args:
            duration_ms: Duration in milliseconds
        """
        self.pipeline_duration_ms = duration_ms
    
    def record_stage_duration(
        self,
        stage_name: str,
        duration_ms: float,
    ) -> None:
        """
        Record a pipeline stage duration.
        
        Args:
            stage_name: Name of the pipeline stage
            duration_ms: Duration in milliseconds
        """
        object.__setattr__(
            self,
            "stage_durations_ms",
            {**self.stage_durations_ms, stage_name: duration_ms}
        )


# =============================================================================
# EXPLAINABILITY CONSUMER - Traces explainability data
# =============================================================================

@dataclass(frozen=True)
class ExplainabilityConsumer:
    """
    Consumer of explainability trace events.
    
    Receives traces about assessment reasoning without exposing how tracing is
    implemented. Only the trace data, not the tracing mechanism.
    
    PROPERTIES:
        • Observational only - no computation
        • Versioned for compatibility tracking
        • External ownership of trace storage
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"explain_trace_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Explainability data (reasons, not computation)
    reason_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events with reasoning information."""
    
    evidence_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events with supporting evidence."""
    
    explanation_complete_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Events when explanations are complete."""
    
    def receive_reason(
        self,
        reason_type: str,
        description: str,
        confidence: Optional[float] = None,
    ) -> None:
        """
        Record a reasoning event.
        
        Args:
            reason_type: Type of reasoning (e.g., 'priority_high', 'focus_shift')
            description: Human-readable explanation
            confidence: Confidence in this reasoning (0.0 to 1.0)
        """
        event = {
            "reason_type": reason_type,
            "description": description,
            "confidence": confidence,
        }
        object.__setattr__(
            self,
            "reason_events",
            self.reason_events + (event,)
        )
    
    def receive_evidence(
        self,
        evidence_name: str,
        value: float,
    ) -> None:
        """
        Record supporting evidence for reasoning.
        
        Args:
            evidence_name: Name of the evidence
            value: Evidence value
        """
        event = {"evidence_name": evidence_name, "value": value}
        object.__setattr__(
            self,
            "evidence_events",
            self.evidence_events + (event,)
        )
    
    def receive_explanation_complete(
        self,
        explanation_id: str,
        target_ids: Tuple[str, ...],
    ) -> None:
        """
        Record completion of an explanation.
        
        Args:
            explanation_id: ID of the completed explanation
            target_ids: IDs of targets this explanation covers
        """
        event = {
            "explanation_id": explanation_id,
            "target_ids": target_ids,
        }
        object.__setattr__(
            self,
            "explanation_complete_events",
            self.explanation_complete_events + (event,)
        )


# =============================================================================
# EXTERNAL INTERFACES - Protocol definitions for external systems
# =============================================================================

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class DiagnosticsSinkProvider(Protocol):
    """
    Protocol for providing diagnostics sink to the FocusingNetwork.
    
    Allows external systems to supply diagnostics sinks without coupling to
    the FocusingNetwork implementation.
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @abstractmethod
    def get_diagnostics_sink(self) -> DiagnosticsSink:
        """Get the diagnostics sink for this provider."""
        ...
    
    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered diagnostics to storage."""


__all__ = [
    # Primary diagnostic interface
    "DiagnosticsSink",
    # Trace consumers (observational only)
    "PipelineTraceConsumer",
    "AssessmentTraceConsumer",
    "StateTraceConsumer",
    "PerformanceTraceConsumer",
    "ExplainabilityConsumer",
    # External provider interface
    "DiagnosticsSinkProvider",
]