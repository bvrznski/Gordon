# Monitoring Supervision Contract - Phase 7.22
# ============================================

"""
Canonical Execution Supervision.

Supervision determines execution progress, completion status, and anomalies.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class SupervisionState(Enum):
    """States of supervision."""
    
    PENDING = "pending"                         # Not yet started
    ACTIVE = "active"                           # Currently supervising
    PAUSED = "paused"                           # Temporarily suspended
    COMPLETED = "completed"                     # Supervision finished
    FAILED = "failed"                           # Supervision failed


@dataclass(frozen=True)
class ProgressMetrics:
    """
    Metrics tracking execution progress.
    """
    
    # Completion tracking
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    
    # Timing metrics
    started_at_utc: Optional[float] = None
    estimated_completion_utc: Optional[float] = None
    
    # Velocity metrics
    tasks_per_second: float = 0.0
    average_task_duration_seconds: float = 0.0
    
    # Resource usage
    resource_usage_percentage: float = 0.0


@dataclass(frozen=True)
class ExecutionSupervision:
    """
    Supervision results for an execution session.
    
    A supervision result contains:
        - Identity and provenance
        - Supervised execution reference
        - Progress metrics
        - Anomalies detected
        - State tracking
    
    Supervision remains independent of the actual execution.
    """
    
    # Identity
    supervision_id: str                       # Unique supervision identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Supervised execution
    supervised_execution: str                 # ID of what is being supervised
    execution_type: str = "unknown"           # Type of execution (e.g., "tool_call", "reasoning_session")
    
    # Progress tracking
    progress_metrics: ProgressMetrics = field(default_factory=ProgressMetrics)
    
    # Supervision state
    supervision_state: SupervisionState = SupervisionState.PENDING
    
    # Anomalies
    detected_anomalies: List[str] = field(default_factory=list)  # References to anomaly IDs
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def duration_seconds(self) -> float:
        """Calculate supervision duration."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def completion_ratio(self) -> float:
        """Calculate completion ratio (0.0 to 1.0)."""
        if self.progress_metrics.total_tasks == 0:
            return 0.0
        return self.progress_metrics.completed_tasks / self.progress_metrics.total_tasks
    
    @property
    def is_completed(self) -> bool:
        """Check if supervision completed."""
        return self.supervision_state == SupervisionState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if supervision failed."""
        return self.supervision_state == SupervisionState.FAILED
    
    def update_progress(
        self,
        total_tasks: int = None,
        completed_tasks: int = None,
        pending_tasks: int = None,
        tasks_per_second: float = None,
    ) -> ExecutionSupervision:
        """Update progress metrics and return new instance."""
        new_metrics = dataclass_replace(
            self.progress_metrics,
            total_tasks=total_tasks if total_tasks is not None else self.progress_metrics.total_tasks,
            completed_tasks=completed_tasks if completed_tasks is not None else self.progress_metrics.completed_tasks,
            pending_tasks=pending_tasks if pending_tasks is not None else self.progress_metrics.pending_tasks,
            tasks_per_second=tasks_per_second if tasks_per_second is not None else self.progress_metrics.tasks_per_second,
        )
        
        return dataclass_replace(
            self,
            progress_metrics=new_metrics,
        )
    
    def add_anomaly(self, anomaly_id: str) -> ExecutionSupervision:
        """Add a detected anomaly."""
        new_anomalies = list(self.detected_anomalies)
        if anomaly_id not in new_anomalies:
            new_anomalies.append(anomaly_id)
        
        return dataclass_replace(
            self,
            detected_anomalies=new_anomalies,
        )
    
    def to_state(self, new_state: SupervisionState) -> ExecutionSupervision:
        """Update supervision state."""
        completed_at = None
        if new_state == SupervisionState.COMPLETED or new_state == SupervisionState.FAILED:
            completed_at = time.time()
        
        return dataclass_replace(
            self,
            supervision_state=new_state,
            completed_at_utc=completed_at,
        )
    
    def start(self) -> ExecutionSupervision:
        """Mark supervision as active."""
        return dataclass_replace(
            self,
            supervision_state=SupervisionState.ACTIVE,
            started_at_utc=time.time(),
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        supervised_execution: str,
        execution_type: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> ExecutionSupervision:
        """Create a new supervision session."""
        return cls(
            supervision_id=f"supervision:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            supervised_execution=supervised_execution,
            execution_type=execution_type,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionSupervision",
    "ProgressMetrics",
    "SupervisionState",
]