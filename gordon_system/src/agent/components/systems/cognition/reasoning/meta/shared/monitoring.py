# Reasoning Monitoring - Phase 7.13
# ==================================

"""
Canonical Reasoning Monitoring definition.

Monitoring evaluates ongoing reasoning execution for progress, quality,
and resource consumption.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MonitorKind(Enum):
    """Types of monitoring observations."""
    
    PROGRESS = "progress"                     # Reasoning progress tracking
    CONFIDENCE = "confidence"                 # Confidence in results
    RESOURCE_USAGE = "resource_usage"         # Resource consumption
    QUALITY = "quality"                       # Output quality metrics
    DEADLOCK = "deadlock"                     # Stagnation detection
    DIVERGENCE = "divergence"                 # Divergence detection


@dataclass(frozen=True)
class MonitoringMetric:
    """
    A single monitoring metric observation.
    
    Metrics provide quantitative measurements of reasoning execution.
    """
    
    # Identity
    metric_id: str                          # Unique metric identifier
    
    # Metric details
    monitor_kind: MonitorKind               # What kind of metric?
    name: str                               # Human-readable name
    
    # Value
    value: float                            # Current metric value
    
    # Timing
    collected_at_utc: float = field(default_factory=time.time)
    
    # Metadata
    unit: Optional[str] = None              # Unit of measurement
    confidence: Optional[float] = None      # Confidence in the value


@dataclass(frozen=True)
class MonitoringEvent:
    """
    An event detected by monitoring.
    
    Events represent significant observations from monitoring execution.
    """
    
    # Identity
    event_id: str                           # Unique event identifier
    
    # Event type
    kind: MonitorKind                       # What kind of event?
    severity: str = "info"                  # info, warn, error
    
    # Description
    description: str                        # Human-readable description
    
    # Timing
    detected_at_utc: float = field(default_factory=time.time)
    
    # Context
    related_metric_ids: List[str] = field(default_factory=list)  # Associated metrics


@dataclass(frozen=True)
class ReasoningMonitoring:
    """
    Monitoring results for reasoning execution.
    
    A monitoring result contains:
        - Identity and provenance
        - Collected metrics
        - Detected events
        - Provenance tracking
    
    Monitoring remains continuous and independent of reasoning execution.
    """
    
    # Identity
    monitoring_id: str                      # Unique monitoring identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Monitored reasoners
    monitored_reasoners: List[str]          # IDs being monitored
    
    # Collected metrics
    collected_metrics: List[MonitoringMetric] = field(default_factory=list)
    
    # Detected events
    detected_events: List[MonitoringEvent] = field(default_factory=list)
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate monitoring duration."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return time.time() - self.started_at_utc
    
    def record_metric(
        self,
        kind: MonitorKind,
        name: str,
        value: float,
        unit: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> ReasoningMonitoring:
        """Record a new metric and return updated monitoring."""
        return dataclass_replace(
            self,
            collected_metrics=self.collected_metrics + [MonitoringMetric(
                metric_id=f"metric:{uuid.uuid4().hex[:16]}",
                monitor_kind=kind,
                name=name,
                value=value,
                unit=unit,
                confidence=confidence,
            )]
        )
    
    def record_event(
        self,
        kind: MonitorKind,
        description: str,
        severity: str = "info",
        related_metric_ids: Optional[List[str]] = None,
    ) -> ReasoningMonitoring:
        """Record a new event and return updated monitoring."""
        if related_metric_ids is None:
            related_metric_ids = []
        
        return dataclass_replace(
            self,
            detected_events=self.detected_events + [MonitoringEvent(
                event_id=f"event:{uuid.uuid4().hex[:16]}",
                kind=kind,
                description=description,
                severity=severity,
                detected_at_utc=time.time(),
                related_metric_ids=related_metric_ids,
            )]
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        monitored_reasoners: List[str],
    ) -> ReasoningMonitoring:
        """Create a new monitoring session."""
        return cls(
            monitoring_id=f"monitoring:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            monitored_reasoners=monitored_reasoners,
        )
    
    def to_completed(self) -> ReasoningMonitoring:
        """Mark monitoring as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReasoningMonitoring",
    "MonitoringMetric",
    "MonitoringEvent",
    "MonitorKind",
]