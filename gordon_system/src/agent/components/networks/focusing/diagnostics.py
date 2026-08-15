# Focusing Network - Diagnostics
# ================================
#
# Phase 4.2.7: Diagnostic infrastructure for the computational pipeline.
#
# This module provides comprehensive diagnostics capture for all pipeline stages.
#

"""
Diagnostics Infrastructure for FocusingNetwork Pipeline.

Captures and reports on:
    - Pipeline timing at each stage
    - Input/output summaries
    - Assessment summaries  
    - Confidence traces
    - Priority traces
    - Competition traces
    - Precision traces
    - Suppression traces
    - Allocation traces
    - State transitions
    - History evolution

All diagnostics remain read-only and are emitted through sinks.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple, Dict, Any, Optional, List


@dataclass(frozen=True)
class DiagnosticEvent:
    """
    Immutable diagnostic event emitted during pipeline execution.
    
    Contains timestamped metadata about a single pipeline operation.
    """
    
    # Event identity
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    
    # Timing
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    elapsed_ms: float = 0.0
    
    # Context
    event_source: str
    event_stage: str
    computation_id: str = ""
    
    # Event details
    event_type: str
    description: str
    
    # Data summary (not full data - that would be too large)
    input_count: int = 0
    output_count: int = 0
    confidence_value: Optional[float] = None
    score_value: Optional[float] = None
    
    @classmethod
    def create_pipeline_start(cls, computation_id: str) -> "DiagnosticEvent":
        """Create a pipeline start event."""
        return cls(
            event_source="pipeline",
            event_stage="start",
            event_type="pipeline_start",
            description="Pipeline execution started",
            computation_id=computation_id,
        )
    
    @classmethod
    def create_pipeline_end(cls, computation_id: str, elapsed_ms: float) -> "DiagnosticEvent":
        """Create a pipeline end event."""
        return cls(
            event_source="pipeline",
            event_stage="end",
            event_type="pipeline_end",
            description=f"Pipeline execution completed in {elapsed_ms:.2f}ms",
            computation_id=computation_id,
            elapsed_ms=elapsed_ms,
        )
    
    @classmethod
    def create_stage_start(cls, stage_name: str, computation_id: str) -> "DiagnosticEvent":
        """Create a stage start event."""
        return cls(
            event_source="stage",
            event_stage=stage_name.lower(),
            event_type="stage_start",
            description=f"Stage '{stage_name}' started",
            computation_id=computation_id,
        )
    
    @classmethod
    def create_stage_end(cls, stage_name: str, computation_id: str, elapsed_ms: float) -> "DiagnosticEvent":
        """Create a stage end event."""
        return cls(
            event_source="stage",
            event_stage=stage_name.lower(),
            event_type="stage_end",
            description=f"Stage '{stage_name}' completed in {elapsed_ms:.2f}ms",
            computation_id=computation_id,
            elapsed_ms=elapsed_ms,
        )
    
    @classmethod
    def create_input_validation(
        cls, 
        computation_id: str, 
        valid: bool, 
        error_message: Optional[str] = None
    ) -> "DiagnosticEvent":
        """Create an input validation event."""
        return cls(
            event_source="validation",
            event_stage="input",
            event_type="input_validation" if valid else "input_invalid",
            description=f"Input validation {'passed' if valid else 'failed'}: {error_message or ''}",
            computation_id=computation_id,
        )
    
    @classmethod
    def create_assessment_generated(
        cls, 
        assessment_name: str,
        computation_id: str,
        confidence: Optional[float] = None,
        score: Optional[float] = None,
    ) -> "DiagnosticEvent":
        """Create an assessment generated event."""
        return cls(
            event_source="assessment",
            event_stage=assessment_name.lower(),
            event_type="assessment_generated",
            description=f"Assessment '{assessment_name}' generated",
            computation_id=computation_id,
            confidence_value=confidence,
            score_value=score,
        )


@dataclass(frozen=True)
class PipelineDiagnostics:
    """
    Complete diagnostics snapshot for a single pipeline execution.
    
    Contains all diagnostic events from start to finish of one computation.
    """
    
    # Identity
    diagnostics_id: str = field(default_factory=lambda: f"diag_{uuid.uuid4().hex[:12]}")
    computation_id: str
    
    # Timing
    started_at: datetime
    ended_at: datetime
    total_elapsed_ms: float
    
    # Events (chronological order)
    events: Tuple[DiagnosticEvent, ...]
    
    # Summary counts
    stage_start_count: int = 0
    stage_end_count: int = 0
    assessment_generated_count: int = 0
    validation_event_count: int = 0
    
    @classmethod
    def create_empty(cls, computation_id: str) -> "PipelineDiagnostics":
        """Create empty diagnostics for a computation."""
        return cls(
            diagnostics_id=f"diag_{uuid.uuid4().hex[:12]}",
            computation_id=computation_id,
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            total_elapsed_ms=0.0,
            events=tuple(),
        )
    
    def with_event(self, event: DiagnosticEvent) -> "PipelineDiagnostics":
        """Add an event to the diagnostics."""
        return dataclass_replace(
            self,
            events=self.events + (event,),
            stage_start_count=self.stage_start_count + (1 if event.event_type == "stage_start" else 0),
            stage_end_count=self.stage_end_count + (1 if event.event_type == "stage_end" else 0),
            assessment_generated_count=self.assessment_generated_count + (1 if event.event_type == "assessment_generated" else 0),
            validation_event_count=self.validation_event_count + (1 if event.event_source == "validation" else 0),
        )
    
    def with_timing(self, started_at: datetime, ended_at: datetime) -> "PipelineDiagnostics":
        """Update timing information."""
        return dataclass_replace(
            self,
            started_at=started_at,
            ended_at=ended_at,
            total_elapsed_ms=(ended_at - started_at).total_seconds() * 1000,
        )


@dataclass(frozen=True)
class DiagnosticsCollector:
    """
    Collector for diagnostic events during pipeline execution.
    
    RESPONSIBILITIES:
        - Collect all DiagnosticEvent instances
        - Maintain chronological order
        - Provide read-only access to collected diagnostics
        
    NOT RESPONSIBLE FOR:
        - Emitting to external systems (that's the sink)
        - Modifying existing events
        - Making decisions based on diagnostics
    
    Usage:
        collector = DiagnosticsCollector()
        
        # Use during pipeline execution
        collector.collect(event)
        
        # Get final diagnostics snapshot
        snapshot = collector.get_snapshot(started_at, ended_at)
    """
    
    # Collected events in chronological order
    _events: List[DiagnosticEvent] = field(default_factory=list, repr=False)
    
    @property
    def event_count(self) -> int:
        """Return the number of collected events."""
        return len(self._events)
    
    def collect(self, event: DiagnosticEvent) -> None:
        """
        Collect a diagnostic event.
        
        Args:
            event: The diagnostic event to collect
        """
        self._events.append(event)
    
    def get_snapshot(self, started_at: datetime, ended_at: datetime) -> PipelineDiagnostics:
        """
        Get a frozen snapshot of all collected diagnostics.
        
        Args:
            started_at: When the computation started
            ended_at: When the computation ended
            
        Returns:
            Complete diagnostics snapshot
        """
        return PipelineDiagnostics(
            diagnostics_id=f"diag_{uuid.uuid4().hex[:12]}",
            computation_id=self._get_computation_id(),
            started_at=started_at,
            ended_at=ended_at,
            total_elapsed_ms=(ended_at - started_at).total_seconds() * 1000,
            events=tuple(self._events),
            stage_start_count=sum(1 for e in self._events if e.event_type == "stage_start"),
            stage_end_count=sum(1 for e in self._events if e.event_type == "stage_end"),
            assessment_generated_count=sum(1 for e in self._events if e.event_type == "assessment_generated"),
            validation_event_count=sum(1 for e in self._events if e.event_source == "validation"),
        )
    
    def _get_computation_id(self) -> str:
        """Extract computation ID from first event or generate one."""
        if self._events:
            return self._events[0].computation_id
        return f"comp_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class DiagnosticsSink:
    """
    Sink for diagnostic events - receives and processes them.
    
    This is a pass-through interface. Actual sinks are implemented elsewhere.
    
    NOT RESPONSIBLE FOR:
        - Storing diagnostics
        - Aggregating statistics
        - Emitting to external systems
        
    These are responsibility of implementations that use this interface.
    """
    
    # Configuration
    enabled: bool = True
    verbosity: int = 1
    
    def emit(self, event: DiagnosticEvent) -> None:
        """
        Emit a diagnostic event.
        
        Args:
            event: The diagnostic event to emit
        """
        if not self.enabled:
            return
        
        # Implementation can add actual emission here
        pass


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    Creates a new copy with specified fields updated while maintaining
    immutability guarantees.
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {
            f.name: getattr(obj, f.name)
            for f in obj.__dataclass_fields__.values()
        }
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Object {obj} is not a dataclass")


# Pipeline stages as constants
PIPELINE_STAGES = (
    "PriorityAggregation",
    "RelevanceEvaluation", 
    "CompetitionResolution",
    "SuppressionRecommendation",
    "PrecisionEstimation",
    "PersistenceUpdate",
    "BiasGeneration",
    "ResourceAllocation",
    "AssessmentComposition",
)