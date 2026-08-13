# Action & Feedback Streams Architecture - Phase 3.11.12
# =========================================================

"""
Canonical Semantic Streaming Architecture for Action and Feedback Operations.

This module implements Phase 3.11.12: Action & Feedback Stream Architecture.

Architecture:

    Capability
            │
            ▼
    Action System (owns execution)
            │
            ▼
    Action Streams (canonical semantic transport)
            │
            ▼
    Execution
            │
            ▼
    Feedback Streams (canonical observation transport)
            │
            ▼
    Consumers

Key Principles:
    - Action owns execution, NOT stream transport
    - Feedback owns observation, NOT execution state
    - Streams own semantic continuity and ordering
    - Records are immutable once committed
    - Replay reproduces history, never re-executes actions
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, List
from enum import Enum, auto
import uuid
import time

# Import core stream infrastructure
from ..streams import (
    StreamId,
    StreamKind,
    StreamGenerationId,
    StreamRecordId,
    StreamPosition,
    ProducerId,
    CorrelationId,
    CausationId,
    ArtifactReference,
    RecordType,
    RecordStatus,
)

# Import Action system contracts
from ..action import (
    ActionId,
    InvocationId,
    ToolId,
    EffectorId,
    ActionState,
    ExecutionResult,
    ExecutionStatus,
)


# =============================================================================
# ACTION RECORD TYPES
# =============================================================================

class ActionRecordKind(Enum):
    """
    Kinds of action records that can be published to streams.
    
    These represent the complete lifecycle of an action from proposal
    through completion or failure.
    """
    # Proposal and selection
    PROPOSAL_CREATED = "proposal_created"           # Action proposed
    SELECTION_REQUESTED = "selection_requested"     # Selected for execution
    
    # Authorization
    AUTHORIZATION_REQUESTED = "authorization_requested"
    AUTHORIZATION_GRANTED = "authorization_granted"
    AUTHORIZATION_DENIED = "authorization_denied"
    
    # Dispatch and execution
    DISPATCHED = "dispatched"                       # Sent to executor
    EXECUTION_STARTED = "execution_started"         # Executor began work
    EXECUTION_PROGRESS = "execution_progress"       # Intermediate progress update
    
    # Completion outcomes
    COMPLETED = "completed"                         # Execution succeeded
    PARTIALLY_COMPLETED = "partially_completed"     # Partial success
    FAILED = "failed"                               # Execution failed
    CANCELLED = "cancelled"                         # User/system cancelled
    TIMED_OUT = "timed_out"                         # Timeout reached
    
    # Retry and recovery
    RETRY_REQUESTED = "retry_requested"
    RETRY_SCHEDULED = "retry_scheduled"
    RETRY_EXECUTED = "retry_executed"
    RETRY_ABANDONED = "retry_abandoned"
    
    # Side effects
    SIDE_EFFECT_OCCURRED = "side_effect_occurred"   # External effect observed


class ActionRecordStatus(Enum):
    """
    Status of an action record through its lifecycle.
    """
    PROPOSED = "proposed"       # Created but not yet validated
    VALIDATED = "validated"     # Passed validation, ready for dispatch
    DISPATCHED = "dispatched"   # Sent to execution system
    EXECUTING = "executing"     # Currently executing
    COMPLETED = "completed"     # Execution finished (success or failure)
    OBSERVED = "observed"       # Feedback recorded


@dataclass(frozen=True)
class ActionRecord:
    """
    Immutable record representing an action in the stream.
    
    This is the atomic unit of semantic continuity for action operations.
    It tracks the complete lifecycle without embedding mutable state.
    """
    
    # Identity
    record_id: StreamRecordId
    stream_id: StreamId
    
    # Action identity (separate from record identity)
    action_id: ActionId
    invocation_id: Optional[InvocationId] = None
    
    # Record kind and status
    record_kind: ActionRecordKind
    record_status: ActionRecordStatus = ActionRecordStatus.PROPOSED
    
    # Timestamps
    event_time_utc: float  # When the event occurred (from event's perspective)
    created_at_utc: float = field(default_factory=time.time)  # When record was proposed
    committed_at_utc: Optional[float] = None  # When record entered canonical history
    
    # Position and ordering
    generation_id: StreamGenerationId
    sequence_number: int
    
    # Execution payload (bounded size)
    action_payload: Dict[str, Any]
    
    # Authorization context
    authorization_context: Optional[Dict[str, Any]] = None
    authorization_reference: Optional[str] = None  # Reference to auth record
    
    # Execution reference (for correlation with feedback)
    execution_reference: Optional[str] = None
    execution_target: Optional[str] = None  # Tool/effector being executed
    
    # Correlation and causation
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    parent_record_id: Optional[StreamRecordId] = None  # Previous state transition
    
    # Retry tracking
    retry_count: int = 0
    is_retry: bool = False
    
    # Provenance
    producer: ProducerId
    confidence: float = 1.0  # Confidence in record accuracy (0.0-1.0)
    
    def with_status(self, status: ActionRecordStatus) -> "ActionRecord":
        """Return a new record with updated status."""
        return dataclass_replace(self, record_status=status)
    
    def increment_retry(self) -> "ActionRecord":
        """Return a new record with retry count incremented."""
        return dataclass_replace(
            self,
            retry_count=self.retry_count + 1,
            is_retry=True
        )


@dataclass(frozen=True)
class ActionSideEffect:
    """
    Record of a side effect produced by action execution.
    
    Side effects are observable external artifacts, not implicit behavior.
    Every side effect requires provenance tracking.
    """
    
    # Identity
    effect_id: str  # Unique within the action context
    
    # Effect classification
    effect_type: str  # e.g., "filesystem_write", "network_request", "api_call"
    target: str       # Target system or resource
    operation: str    # e.g., "write", "read", "create", "delete"
    
    # Evidence
    timestamp_utc: float
    evidence: Dict[str, Any]  # Proof of effect (e.g., file path, response body)
    
    # Provenance
    action_id: ActionId
    invocation_id: Optional[InvocationId] = None
    
    # Verification
    verified: bool = False
    verification_reference: Optional[str] = None


@dataclass(frozen=True)
class AuthorizationRecord:
    """
    Immutable record of an authorization decision.
    
    Authorization is separate from execution. This records:
        - Request for authorization
        - Grant or denial
        - Revocation (if applicable)
    """
    
    # Identity
    record_id: StreamRecordId
    
    # Authorization identity
    auth_request_id: str
    action_id: ActionId
    
    # Decision
    decision: "AuthorizationDecision"
    
    # Timestamps
    event_time_utc: float
    granted_at_utc: Optional[float] = None
    
    # Context
    requester: Optional[str] = None
    policy_reference: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None  # Conditions attached to grant
    
    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Correlation
    correlation_id: Optional[CorrelationId] = None


class AuthorizationDecision(Enum):
    """Authorization decision outcomes."""
    REQUESTED = "requested"
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"


# =============================================================================
# FEEDBACK RECORD TYPES
# =============================================================================

class FeedbackRecordKind(Enum):
    """
    Kinds of feedback records that can be published to streams.
    
    Feedback tracks execution observations, NOT execution logic.
    """
    # Execution lifecycle observations
    EXECUTION_STARTED_OBSERVED = "execution_started_observed"
    PROGRESS_UPDATE_OBSERVED = "progress_update_observed"
    EXECUTION_COMPLETED_OBSERVED = "execution_completed_observed"
    
    # Outcome observations
    SUCCESS_OBSERVED = "success_observed"
    FAILURE_OBSERVED = "failure_observed"
    CANCELLATION_OBSERVED = "cancellation_observed"
    TIMEOUT_OBSERVED = "timeout_observed"
    
    # Side effect observations
    SIDE_EFFECT_OBSERVED = "side_effect_observed"
    RESOURCE_CHANGED_OBSERVED = "resource_changed_observed"
    
    # Runtime metrics
    METRIC_UPDATE_OBSERVED = "metric_update_observed"
    LATENCY_OBSERVED = "latency_observed"
    THROUGHPUT_OBSERVED = "throughput_observed"


@dataclass(frozen=True)
class FeedbackRecord:
    """
    Immutable record representing an execution observation.
    
    Feedback records are separate from action records - they observe
    outcomes without owning execution state.
    """
    
    # Identity
    record_id: StreamRecordId
    stream_id: StreamId
    
    # Action reference (what was observed)
    action_id: ActionId
    invocation_id: Optional[InvocationId] = None
    
    # Feedback kind and status
    record_kind: FeedbackRecordKind
    record_status: RecordStatus = RecordStatus.COMMITTED
    
    # Timestamps
    event_time_utc: float  # When the observation was made
    created_at_utc: float = field(default_factory=time.time)
    
    # Position and ordering
    generation_id: StreamGenerationId
    sequence_number: int
    
    # Observation payload (bounded size)
    observation_payload: Dict[str, Any]
    
    # Execution state at time of observation
    execution_state_reference: Optional[str] = None  # Reference to action record
    
    # Metrics (if applicable)
    runtime_metrics: Optional[Dict[str, float]] = None  # e.g., {"cpu_seconds": 0.5, "memory_bytes": 1024}
    
    # Correlation and causation
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[CausationId] = None
    
    # Producer (who made the observation)
    producer: ProducerId


@dataclass(frozen=True)
class ExecutionEvidence:
    """
    Evidence supporting an execution outcome.
    
    This is separate from feedback records - it's the raw evidence
    that feedback observers use to create their records.
    """
    
    # Identity
    evidence_id: str
    
    # What was observed
    action_id: ActionId
    invocation_id: Optional[InvocationId] = None
    
    # Evidence type and content
    evidence_type: str  # e.g., "stdout", "stderr", "exit_code", "http_response"
    evidence_content: Dict[str, Any]
    
    # Timestamps
    captured_at_utc: float
    
    # Integrity verification
    integrity_hash: Optional[str] = None
    
    # Source tracking
    source_reference: Optional[str] = None


# =============================================================================
# ACTION STREAM TYPES
# =============================================================================

class ActionStreamType(Enum):
    """
    Types of action streams available.
    
    Each stream has a specific purpose in the action lifecycle.
    """
    # Request and proposal streams
    ACTION_PROPOSAL = "action_proposal"           # Actions proposed for execution
    
    # Authorization stream
    AUTHORIZATION = "authorization"               # Authorization decisions
    
    # Execution streams
    ACTION_DISPATCH = "action_dispatch"           # Dispatched to executor
    ACTION_EXECUTION = "action_execution"         # Execution progress
    ACTION_COMPLETION = "action_completion"       # Completion outcomes
    
    # Failure and recovery streams
    ACTION_FAILURE = "action_failure"             # Failed actions
    ACTION_CANCELLED = "action_cancelled"         # Cancelled actions
    ACTION_TIMED_OUT = "action_timed_out"         # Timed out actions
    
    # Retry stream
    RETRY = "retry"                               # Retry operations
    
    # Side effect stream
    SIDE_EFFECT = "side_effect"                   # Observed side effects


# =============================================================================
# STREAM ID GENERATORS
# =============================================================================

def make_action_proposal_stream_id() -> StreamId:
    """Create stream ID for action proposal records."""
    return StreamId("action:proposal")


def make_authorization_stream_id() -> StreamId:
    """Create stream ID for authorization records."""
    return StreamId("action:authorization")


def make_action_dispatch_stream_id() -> StreamId:
    """Create stream ID for dispatch records."""
    return StreamId("action:dispatch")


def make_action_execution_stream_id() -> StreamId:
    """Create stream ID for execution progress records."""
    return StreamId("action:execution")


def make_action_completion_stream_id() -> StreamId:
    """Create stream ID for completion outcome records."""
    return StreamId("action:completion")


def make_action_failure_stream_id() -> StreamId:
    """Create stream ID for failure records."""
    return StreamId("action:failure")


def make_action_cancelled_stream_id() -> StreamId:
    """Create stream ID for cancellation records."""
    return StreamId("action:cancelled")


def make_action_timed_out_stream_id() -> StreamId:
    """Create stream ID for timeout records."""
    return StreamId("action:timed_out")


def make_retry_stream_id() -> StreamId:
    """Create stream ID for retry operation records."""
    return StreamId("action:retry")


def make_side_effect_stream_id() -> StreamId:
    """Create stream ID for side effect observation records."""
    return StreamId("feedback:side_effects")


# =============================================================================
# ACTION LIFECYCLE TRACKING
# =============================================================================

@dataclass(frozen=True)
class ActionLifecycleState:
    """
    Current state of an action through its lifecycle.
    
    This is the canonical state tracker - NOT embedded in stream records.
    Stream records track transitions; this tracks current state.
    """
    
    # Identity
    action_id: ActionId
    invocation_id: Optional[InvocationId] = None
    
    # Lifecycle phase
    phase: "ActionLifecyclePhase"
    
    # State within phase
    state: ActionState
    
    # Timestamps
    created_at_utc: float
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Results (only set when complete)
    result_reference: Optional[str] = None  # Reference to execution result record
    error_message: Optional[str] = None
    
    # Retry state
    retry_count: int = 0
    is_retriable: bool = True
    
    # Authorization
    authorized_at_utc: Optional[float] = None
    
    def transition_to(self, new_state: ActionState, phase: "ActionLifecyclePhase" = None) -> "ActionLifecycleState":
        """Return new state with updated values."""
        return dataclass_replace(
            self,
            state=new_state,
            phase=phase or self.phase,
            started_at_utc=self.started_at_utc if new_state != ActionState.RUNNING else time.time(),
            completed_at_utc=self.completed_at_utc if new_state not in [ActionState.SUCCEEDED, ActionState.FAILED] else time.time()
        )


class ActionLifecyclePhase(Enum):
    """Phases of the action lifecycle."""
    PROPOSAL = "proposal"                   # Proposal and validation
    AUTHORIZATION = "authorization"         # Authorization evaluation
    DISPATCH = "dispatch"                   # Dispatch to executor
    EXECUTION = "execution"                 # Execution in progress
    COMPLETION = "completion"               # Completion processing
    OBSERVATION = "observation"             # Feedback observation


# =============================================================================
# BUILDER PATTERN - MUTABLE CONSTRUCTION BEFORE IMMUTABILITY
# =============================================================================

class ActionRecordBuilder:
    """
    Mutable builder for constructing action records.
    
    Usage:
        builder = ActionRecordBuilder(
            stream_id=make_action_proposal_stream_id(),
            generation_id=StreamGenerationId(stream_id, 1),
            record_kind=ActionRecordKind.PROPOSAL_CREATED,
            action_id=action_id
        )
        
        builder.set_authorization(auth_ref)
        builder.set_execution_target(target)
        builder.set_correlation(correlation_id)
        
        record = builder.build()  # Immutable result
    """
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        record_kind: ActionRecordKind,
        action_id: ActionId,
    ):
        self._stream_id = stream_id
        self._generation_id = generation_id
        self._record_kind = record_kind
        self._action_id = action_id
        
        # Mutable fields (before build)
        self._sequence_number: Optional[int] = None
        self._event_time_utc: Optional[float] = None
        self._invocation_id: Optional[InvocationId] = None
        self._record_status = ActionRecordStatus.PROPOSED
        self._action_payload: Dict[str, Any] = {}
        self._authorization_context: Optional[Dict[str, Any]] = None
        self._authorization_reference: Optional[str] = None
        self._execution_reference: Optional[str] = None
        self._execution_target: Optional[str] = None
        self._correlation_id: Optional[CorrelationId] = None
        self._causation_id: Optional[CausationId] = None
        self._parent_record_id: Optional[StreamRecordId] = None
        self._retry_count = 0
        self._producer = ProducerId("unknown")
        self._confidence = 1.0
    
    def set_sequence(self, sequence: int) -> "ActionRecordBuilder":
        """Set the record's sequence number."""
        self._sequence_number = sequence
        return self
    
    def set_event_time(self, utc_time: float) -> "ActionRecordBuilder":
        """Set the event timestamp."""
        self._event_time_utc = utc_time
        return self
    
    def set_invocation_id(self, invocation_id: InvocationId) -> "ActionRecordBuilder":
        """Set the invocation ID."""
        self._invocation_id = invocation_id
        return self
    
    def set_record_status(self, status: ActionRecordStatus) -> "ActionRecordBuilder":
        """Set the record status."""
        self._record_status = status
        return self
    
    def set_payload(self, payload: Dict[str, Any]) -> "ActionRecordBuilder":
        """Set the action payload."""
        self._action_payload = payload
        return self
    
    def set_authorization_context(self, context: Dict[str, Any]) -> "ActionRecordBuilder":
        """Set authorization context."""
        self._authorization_context = context
        return self
    
    def set_authorization_reference(self, reference: str) -> "ActionRecordBuilder":
        """Set authorization record reference."""
        self._authorization_reference = reference
        return self
    
    def set_execution_target(self, target: str) -> "ActionRecordBuilder":
        """Set execution target (tool/effector)."""
        self._execution_target = target
        return self
    
    def set_correlation(self, correlation_id: CorrelationId) -> "ActionRecordBuilder":
        """Set correlation ID."""
        self._correlation_id = correlation_id
        return self
    
    def set_causation(self, causation_id: CausationId) -> "ActionRecordBuilder":
        """Set causation ID."""
        self._causation_id = causation_id
        return self
    
    def set_producer(self, producer_id: ProducerId) -> "ActionRecordBuilder":
        """Set the producer identity."""
        self._producer = producer_id
        return self
    
    def set_confidence(self, confidence: float) -> "ActionRecordBuilder":
        """Set confidence in record accuracy (0.0-1.0)."""
        self._confidence = max(0.0, min(1.0, confidence))
        return self
    
    def increment_retry(self) -> "ActionRecordBuilder":
        """Increment retry count."""
        self._retry_count += 1
        return self
    
    def build(self) -> ActionRecord:
        """
        Build the immutable action record.
        
        This consumes the builder - it cannot be reused after this call.
        """
        if self._sequence_number is None:
            raise ValueError("Sequence number is required")
        
        event_time = self._event_time_utc or time.time()
        record_id = StreamRecordId(self._generation_id, self._sequence_number)
        
        return ActionRecord(
            record_id=record_id,
            stream_id=self._stream_id,
            action_id=self._action_id,
            invocation_id=self._invocation_id,
            record_kind=self._record_kind,
            record_status=self._record_status,
            event_time_utc=event_time,
            created_at_utc=time.time(),
            committed_at_utc=None,
            generation_id=self._generation_id,
            sequence_number=self._sequence_number,
            action_payload=dict(self._action_payload),
            authorization_context=self._authorization_context,
            authorization_reference=self._authorization_reference,
            execution_reference=self._execution_reference,
            execution_target=self._execution_target,
            correlation_id=self._correlation_id,
            causation_id=self._causation_id,
            parent_record_id=self._parent_record_id,
            retry_count=self._retry_count,
            is_retry=self._retry_count > 0,
            producer=self._producer,
            confidence=self._confidence
        )


class FeedbackRecordBuilder:
    """
    Mutable builder for constructing feedback records.
    """
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        record_kind: FeedbackRecordKind,
        action_id: ActionId,
    ):
        self._stream_id = stream_id
        self._generation_id = generation_id
        self._record_kind = record_kind
        self._action_id = action_id
        
        # Mutable fields (before build)
        self._sequence_number: Optional[int] = None
        self._event_time_utc: Optional[float] = None
        self._invocation_id: Optional[InvocationId] = None
        self._observation_payload: Dict[str, Any] = {}
        self._execution_state_reference: Optional[str] = None
        self._runtime_metrics: Optional[Dict[str, float]] = None
        self._correlation_id: Optional[CorrelationId] = None
        self._causation_id: Optional[CausationId] = None
        self._producer = ProducerId("unknown")
    
    def set_sequence(self, sequence: int) -> "FeedbackRecordBuilder":
        """Set the record's sequence number."""
        self._sequence_number = sequence
        return self
    
    def set_event_time(self, utc_time: float) -> "FeedbackRecordBuilder":
        """Set the event timestamp."""
        self._event_time_utc = utc_time
        return self
    
    def set_invocation_id(self, invocation_id: InvocationId) -> "FeedbackRecordBuilder":
        """Set the invocation ID."""
        self._invocation_id = invocation_id
        return self
    
    def set_observation_payload(self, payload: Dict[str, Any]) -> "FeedbackRecordBuilder":
        """Set the observation payload."""
        self._observation_payload = payload
        return self
    
    def set_execution_state_reference(self, reference: str) -> "FeedbackRecordBuilder":
        """Set execution state reference."""
        self._execution_state_reference = reference
        return self
    
    def set_runtime_metrics(self, metrics: Dict[str, float]) -> "FeedbackRecordBuilder":
        """Set runtime metrics."""
        self._runtime_metrics = metrics
        return self
    
    def set_correlation(self, correlation_id: CorrelationId) -> "FeedbackRecordBuilder":
        """Set correlation ID."""
        self._correlation_id = correlation_id
        return self
    
    def set_causation(self, causation_id: CausationId) -> "FeedbackRecordBuilder":
        """Set causation ID."""
        self._causation_id = causation_id
        return self
    
    def set_producer(self, producer_id: ProducerId) -> "FeedbackRecordBuilder":
        """Set the producer identity."""
        self._producer = producer_id
        return self
    
    def build(self) -> FeedbackRecord:
        """
        Build the immutable feedback record.
        
        This consumes the builder - it cannot be reused after this call.
        """
        if self._sequence_number is None:
            raise ValueError("Sequence number is required")
        
        event_time = self._event_time_utc or time.time()
        record_id = StreamRecordId(self._generation_id, self._sequence_number)
        
        return FeedbackRecord(
            record_id=record_id,
            stream_id=self._stream_id,
            action_id=self._action_id,
            invocation_id=self._invocation_id,
            record_kind=self._record_kind,
            record_status=RecordStatus.COMMITTED,
            event_time_utc=event_time,
            created_at_utc=time.time(),
            generation_id=self._generation_id,
            sequence_number=self._sequence_number,
            observation_payload=dict(self._observation_payload),
            execution_state_reference=self._execution_state_reference,
            runtime_metrics=self._runtime_metrics,
            correlation_id=self._correlation_id,
            causation_id=self._causation_id,
            producer=self._producer
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_action_record(
    stream_id: StreamId,
    generation_id: StreamGenerationId,
    record_kind: ActionRecordKind,
    action_id: ActionId,
) -> ActionRecordBuilder:
    """
    Create an action record builder.
    
    Args:
        stream_id: The target stream
        generation_id: The generation to commit to
        record_kind: Type of record to create
        action_id: The action being recorded
        
    Returns:
        Mutable builder for constructing the record
    """
    return ActionRecordBuilder(
        stream_id=stream_id,
        generation_id=generation_id,
        record_kind=record_kind,
        action_id=action_id
    )


def create_feedback_record(
    stream_id: StreamId,
    generation_id: StreamGenerationId,
    record_kind: FeedbackRecordKind,
    action_id: ActionId,
) -> FeedbackRecordBuilder:
    """
    Create a feedback record builder.
    
    Args:
        stream_id: The target stream
        generation_id: The generation to commit to
        record_kind: Type of feedback record
        action_id: The action being observed
        
    Returns:
        Mutable builder for constructing the record
    """
    return FeedbackRecordBuilder(
        stream_id=stream_id,
        generation_id=generation_id,
        record_kind=record_kind,
        action_id=action_id
    )


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Record types
    "ActionRecordKind",
    "ActionRecordStatus",
    "ActionRecord",
    "ActionSideEffect",
    "AuthorizationRecord",
    "AuthorizationDecision",
    "FeedbackRecordKind",
    "FeedbackRecord",
    "ExecutionEvidence",
    
    # Stream IDs
    "ActionStreamType",
    "make_action_proposal_stream_id",
    "make_authorization_stream_id",
    "make_action_dispatch_stream_id",
    "make_action_execution_stream_id",
    "make_action_completion_stream_id",
    "make_action_failure_stream_id",
    "make_action_cancelled_stream_id",
    "make_action_timed_out_stream_id",
    "make_retry_stream_id",
    "make_side_effect_stream_id",
    
    # Lifecycle
    "ActionLifecycleState",
    "ActionLifecyclePhase",
    
    # Builders
    "ActionRecordBuilder",
    "FeedbackRecordBuilder",
    
    # Utilities
    "create_action_record",
    "create_feedback_record",
]