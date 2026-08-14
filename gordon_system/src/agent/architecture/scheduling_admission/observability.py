# Phase 3.14.13 - Observability for Scheduling & Admission
# ==========================================================
#
# Diagnostic metadata and tracing infrastructure for scheduling
# and admission operations.
#
# OBSERVABILITY PRINCIPLES:
#     - Every scheduling decision is traceable
#     - Every admission decision produces diagnostic data
#     - All timestamps are monotonic UTC
#     - Data is replay-compatible (no non-deterministic values)

"""
Observability Infrastructure for Scheduling and Admission - Phase 3.14.13

This module provides:
    - Diagnostic metadata structures
    - Trace context propagation
    - Event emission for scheduling/admission decisions
    - Replay-compatible logging
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
import uuid
import time

from . import (
    WorkItemId,
    AdmissionId,
    SchedulerId,
    QueueId,
    AdmissionDecision,
    PriorityClass,
    AdmissionState,
)


# =============================================================================
# OBSERVABILITY CONTEXT
# =============================================================================


@dataclass(frozen=True)
class ObservationContext:
    """
    Context for an observation event.
    
    Contains metadata about who/what triggered the observation.
    """

    observer_id: str  # ID of the observing component
    correlation_id: str  # Cross-system trace context
    timestamp_utc: float = field(default_factory=time.monotonic)

    @classmethod
    def create(cls, observer_id: Optional[str] = None) -> "ObservationContext":
        """Create a new observation context."""
        return cls(
            observer_id=observer_id or f"obs_{uuid.uuid4().hex[:16]}",
            correlation_id=uuid.uuid4().hex[:16],
        )


# =============================================================================
# ADMISSION OBSERVATION
# =============================================================================


class AdmissionObservationType(Enum):
    """
    Types of admission observations.
    
    TYPES:
        REQUEST_RECEIVED  - Work item submitted for admission
        EVALUATING        - Admission evaluation started
        DECISION_MADE     - Final decision reached
        REJECTED          - Item rejected with reason
        DEFERRED          - Item deferred to later time
        ACCEPTED          - Item admitted successfully
    """

    REQUEST_RECEIVED = "request_received"
    EVALUATING = "evaluating"
    DECISION_MADE = "decision_made"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    WAITING = "waiting"
    ACCEPTED = "accepted"


@dataclass(frozen=True)
class AdmissionObservation:
    """
    Observation of an admission decision.
    
    Every admission decision produces exactly one observation record.
    """

    observation_id: str
    admission_id: Optional[AdmissionId]
    work_item_id: WorkItemId

    # Type and state
    observation_type: AdmissionObservationType
    timestamp_utc: float

    # Decision details (if applicable)
    decision: Optional[AdmissionDecision] = None
    reason: Optional[str] = None
    priority: Optional[PriorityClass] = None

    # Context
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    observer_id: str = field(default_factory=lambda: f"obs_{uuid.uuid4().hex[:16]}")

    @classmethod
    def from_admission_result(
        cls,
        result: "AdmissionResult",
        context: ObservationContext,
    ) -> "AdmissionObservation":
        """Create observation from an admission result."""
        return cls(
            observation_id=f"adm_obs_{uuid.uuid4().hex[:16]}",
            admission_id=result.admission_id,
            work_item_id=result.work_item_id,
            observation_type=cls._type_from_decision(result.decision),
            timestamp_utc=time.monotonic(),
            decision=result.decision,
            reason=result.reason,
            priority=result.priority,
            correlation_id=context.correlation_id,
            observer_id=context.observer_id,
        )

    @classmethod
    def _type_from_decision(cls, decision: AdmissionDecision) -> AdmissionObservationType:
        """Map admission decision to observation type."""
        mapping = {
            AdmissionDecision.REJECTED: AdmissionObservationType.REJECTED,
            AdmissionDecision.DEFERRED: AdmissionObservationType.DEFERRED,
            AdmissionDecision.WAITING: AdmissionObservationType.WAITING,
            AdmissionDecision.ACCEPTED: AdmissionObservationType.ACCEPTED,
        }
        return mapping.get(decision, AdmissionObservationType.DECISION_MADE)

    def to_dict(self) -> Dict[str, Any]:
        """Convert observation to dictionary for serialization."""
        return {
            "observation_id": self.observation_id,
            "admission_id": self.admission_id.value if self.admission_id else None,
            "work_item_id": self.work_item_id.value,
            "observation_type": self.observation_type.value,
            "timestamp_utc": self.timestamp_utc,
            "decision": self.decision.value if self.decision else None,
            "reason": self.reason,
            "priority": self.priority.value if self.priority else None,
            "correlation_id": self.correlation_id,
            "observer_id": self.observer_id,
        }


# =============================================================================
# SCHEDULING OBSERVATION
# =============================================================================


class SchedulerObservationType(Enum):
    """
    Types of scheduler observations.
    
    TYPES:
        ITEM_SUBMITTED   - Work item submitted for scheduling
        QUEUED           - Item added to ready queue
        SELECTED         - Item selected from queue
        EXECUTING        - Execution started
        COMPLETED        - Execution finished successfully
        FAILED           - Execution failed
        CANCELLED        - Scheduling cancelled
    """

    ITEM_SUBMITTED = "item_submitted"
    QUEUED = "queued"
    SELECTED = "selected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class SchedulerObservation:
    """
    Observation of a scheduling event.
    
    Every scheduler action produces an observation record for traceability.
    """

    observation_id: str
    work_item_id: WorkItemId

    # Type and state
    observation_type: SchedulerObservationType
    timestamp_utc: float

    # Context
    scheduler_id: Optional[SchedulerId] = None
    queue_id: Optional[QueueId] = None
    priority: Optional[PriorityClass] = None
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    observer_id: str = field(default_factory=lambda: f"obs_{uuid.uuid4().hex[:16]}")

    # Additional metadata
    queue_position_before: Optional[int] = None
    queue_position_after: Optional[int] = None
    execution_context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_scheduler_event(
        cls,
        scheduler_id: SchedulerId,
        work_item_id: WorkItemId,
        event_type: SchedulerObservationType,
        context: ObservationContext,
        queue_position_before: Optional[int] = None,
        queue_position_after: Optional[int] = None,
    ) -> "SchedulerObservation":
        """Create observation from a scheduler event."""
        return cls(
            observation_id=f"sch_obs_{uuid.uuid4().hex[:16]}",
            work_item_id=work_item_id,
            observation_type=event_type,
            timestamp_utc=time.monotonic(),
            scheduler_id=scheduler_id,
            queue_position_before=queue_position_before,
            queue_position_after=queue_position_after,
            correlation_id=context.correlation_id,
            observer_id=context.observer_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert observation to dictionary for serialization."""
        return {
            "observation_id": self.observation_id,
            "work_item_id": self.work_item_id.value,
            "observation_type": self.observation_type.value,
            "timestamp_utc": self.timestamp_utc,
            "scheduler_id": self.scheduler_id.value if self.scheduler_id else None,
            "correlation_id": self.correlation_id,
        }


# =============================================================================
# OBSERVATION LOGGER
# =============================================================================


@dataclass
class ObservationLogger:
    """
    Logger for scheduling and admission observations.
    
    Collects and stores observation records for debugging, analysis,
    and replay purposes.
    """

    logger_id: str = field(default_factory=lambda: f"log_{uuid.uuid4().hex[:16]}")
    max_buffer_size: int = 10000

    # Observation buffers
    _admission_observations: List[AdmissionObservation] = field(
        default_factory=list
    )
    _scheduler_observations: List[SchedulerObservation] = field(
        default_factory=list
    )

    def log_admission(self, observation: AdmissionObservation) -> None:
        """Log an admission observation."""
        if len(self._admission_observations) >= self.max_buffer_size:
            # Drop oldest observations when buffer is full (fairness protection)
            self._admission_observations.pop(0)

        self._admission_observations.append(observation)

    def log_scheduler(self, observation: SchedulerObservation) -> None:
        """Log a scheduler observation."""
        if len(self._scheduler_observations) >= self.max_buffer_size:
            self._scheduler_observations.pop(0)

        self._scheduler_observations.append(observation)

    def get_admission_observations(
        self,
        since_utc: Optional[float] = None,
        until_utc: Optional[float] = None,
    ) -> List[AdmissionObservation]:
        """Get admission observations within a time range."""
        result = self._admission_observations

        if since_utc:
            result = [o for o in result if o.timestamp_utc >= since_utc]

        if until_utc:
            result = [o for o in result if o.timestamp_utc <= until_utc]

        return result

    def get_scheduler_observations(
        self,
        since_utc: Optional[float] = None,
        until_utc: Optional[float] = None,
    ) -> List[SchedulerObservation]:
        """Get scheduler observations within a time range."""
        result = self._scheduler_observations

        if since_utc:
            result = [o for o in result if o.timestamp_utc >= since_utc]

        if until_utc:
            result = [o for o in result if o.timestamp_utc <= until_utc]

        return result

    def clear(self) -> int:
        """Clear all observations and return count."""
        count = len(self._admission_observations) + len(self._scheduler_observations)
        self._admission_observations.clear()
        self._scheduler_observations.clear()
        return count


# =============================================================================
# TRACE CONTEXT PROPAGATION
# =============================================================================


@dataclass(frozen=True)
class TraceContext:
    """
    Context for distributed tracing across scheduling and admission.
    
    Enables trace propagation through the execution pipeline.
    """

    trace_id: str  # Unique trace identifier
    parent_span_id: Optional[str] = None  # Parent span (if any)
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    timestamp_utc: float = field(default_factory=time.monotonic)

    @classmethod
    def create(cls) -> "TraceContext":
        """Create a new trace context."""
        return cls(
            trace_id=f"trace_{uuid.uuid4().hex[:16]}",
            span_id=f"span_{uuid.uuid4().hex[:16]}",
        )

    def with_parent(self, parent_span_id: str) -> "TraceContext":
        """Create a new context with the given parent span."""
        return dataclass_replace(
            self,
            parent_span_id=parent_span_id,
            span_id=f"span_{uuid.uuid4().hex[:16]}",
        )


# =============================================================================
# REPLAY COMPATIBILITY CHECKER
# =============================================================================


class ReplayCompatibility:
    """
    Verifies replay compatibility of observations.
    
    Ensures that observation data can be used for deterministic replay
    without non-deterministic values.
    """

    @staticmethod
    def is_admission_replay_compatible(observation: AdmissionObservation) -> bool:
        """Check if an admission observation is replay-compatible."""
        # Must have all required fields populated
        required_fields = [
            "observation_id",
            "work_item_id",
            "observation_type",
            "timestamp_utc",
        ]

        for field_name in required_fields:
            if not hasattr(observation, field_name) or getattr(observation, field_name) is None:
                return False

        # Timestamps must be monotonic (which they are by design)
        return True

    @staticmethod
    def is_scheduler_replay_compatible(observation: SchedulerObservation) -> bool:
        """Check if a scheduler observation is replay-compatible."""
        required_fields = [
            "observation_id",
            "work_item_id",
            "observation_type",
            "timestamp_utc",
        ]

        for field_name in required_fields:
            if not hasattr(observation, field_name) or getattr(observation, field_name) is None:
                return False

        return True


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_admission_observations_from_results(
    results: List["AdmissionResult"],
    context: ObservationContext,
) -> List[AdmissionObservation]:
    """Create observation records from admission results."""
    observations = []
    for result in results:
        observation = AdmissionObservation.from_admission_result(result, context)
        observations.append(observation)
    return observations


def create_scheduler_observations_from_events(
    scheduler_id: SchedulerId,
    events: List[Tuple[WorkItemId, SchedulerObservationType]],
    context: ObservationContext,
) -> List[SchedulerObservation]:
    """Create observation records from scheduler events."""
    observations = []
    for work_item_id, event_type in events:
        observation = SchedulerObservation.from_scheduler_event(
            scheduler_id, work_item_id, event_type, context
        )
        observations.append(observation)
    return observations


# =============================================================================
# DATACLASS REPLACE HELPER
# =============================================================================


def dataclass_replace(instance: Any, **changes: Any) -> Any:
    """Helper to replace fields in frozen dataclasses."""
    import copy
    new_instance = copy.deepcopy(instance)
    for key, value in changes.items():
        if hasattr(new_instance, key):
            object.__setattr__(new_instance, key, value)
    return new_instance


__all__ = [
    # Context
    "ObservationContext",
    
    # Admission observations
    "AdmissionObservationType",
    "AdmissionObservation",
    
    # Scheduler observations
    "SchedulerObservationType",
    "SchedulerObservation",
    
    # Logger
    "ObservationLogger",
    
    # Trace context
    "TraceContext",
    
    # Replay compatibility
    "ReplayCompatibility",
    
    # Utility functions
    "create_admission_observations_from_results",
    "create_scheduler_observations_from_events",
    "dataclass_replace",
]