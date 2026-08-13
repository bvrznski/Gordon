# Phase 3.11.13 - Stream-to-Stage Integration
# ===========================================
#
# Canonical Runtime Integration:
# Structural Execution Axis ↔ Semantic Continuity Axis
#
# Structural Execution Axis:
#     Thread → Loop → Cycle → Stage → Capability → System → Core
#
# Semantic Continuity Axis:
#     Stream → Generation → Ordered Record → Commit → Cursor → Replay
#
# This package implements the canonical integration between these axes.
# Neither axis owns the other. They coordinate through explicit contracts.

"""
Phase 3.11.13: Network Activation Stream Integration

This module implements the canonical bridge between:
- Structural Execution (Thread → Loop → Cycle → Stage)
- Semantic Streams (Generation → Ordered Record → Commit)

Integration Points:

1. STAGE INPUT SELECTION
   - Deterministic selection of committed stream records for stage consumption
   - Many-to-many relationship: one stage may consume from many streams
   - One stream may contribute to many stages

2. INPUT SNAPSHOTS
   - Immutable, bounded snapshots of selected input records
   - Cursor positions preserved at snapshot time
   - Alignment support for multi-stream inputs

3. STAGE ADMISSION
   - Explicit admission decisions (ADMIT/WAIT/REJECT/SKIP)
   - Lifecycle, capacity, trust, privacy, security validation
   - Stream, stage, activation admission remain distinct layers

4. NETWORK ELIGIBILITY
   - Networks eligible for one admitted stage
   - Eligibility based on stage kind, network descriptor, policy
   - Multiple networks may be eligible per stage

5. ACTIVATION REQUESTS & PLANS
   - Immutable activation requests from stages to networks
   - Activation plans with capability invocation order
   - Atomic publication of activation transitions

6. CAPABILITY INVOCATION
   - Capability projections from input snapshots
   - System usage through public contracts
   - Output validation before stream routing

7. OUTPUT ROUTING & COMMIT
   - Explicit output route descriptors
   - Deterministic commit ordering within streams
   - Cursor progression according to policy

8. REPLAY SAFETY
   - Replay activation distinct from live execution
   - Historical authorization never reused
   - No Action side effects during replay

Ownership Model:

    Execution Layer (Thread/Loop/Cycle/Stage):
        Owns scheduling, admission decisions, deadline enforcement
        
    Stream Infrastructure:
        Owns ordered records, subscriptions, cursors, delivery
        
    Network Layer (via Loop policies):
        Owns functional coalitions, capability coordination
        
    Capability Layer:
        Owns cognitive transformations, typed outputs
        
    System Layer:
        Owns canonical state, state transitions
        
    Core Layer:
        Owns runtime infrastructure

Integration Invariants:

    I-001: Selection never advances cursors
    I-002: Admission never activates networks directly
    I-003: Activation planning is distinct from execution
    I-004: Capability outputs are not stream commits
    I-005: Network activation grants no Action authority
    I-006: Replay never triggers live side effects
    I-007: Cross-stream global ordering not claimed without contract
    I-008: Input selection is deterministic given same state
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Any,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto
import time
import uuid

# =============================================================================
# IDENTITY TYPES - Stream-Stage Integration
# =============================================================================


@dataclass(frozen=True)
class StageInputSelectionId:
    """Unique identifier for one stage-input selection operation."""
    value: str

    @classmethod
    def generate(cls) -> "StageInputSelectionId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class InputSnapshotId:
    """Unique identifier for one input snapshot."""
    value: str

    @classmethod
    def generate(cls) -> "InputSnapshotId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class StageAdmissionId:
    """Unique identifier for one stage admission decision."""
    value: str

    @classmethod
    def generate(cls) -> "StageAdmissionId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class NetworkActivationRequestId:
    """Unique identifier for one network activation request."""
    value: str

    @classmethod
    def generate(cls) -> "NetworkActivationRequestId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class NetworkActivationPlanId:
    """Unique identifier for one activation plan."""
    value: str

    @classmethod
    def generate(cls) -> "NetworkActivationPlanId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class CapabilityInvocationId:
    """Unique identifier for one capability invocation."""
    value: str

    @classmethod
    def generate(cls) -> "CapabilityInvocationId":
        return cls(value=str(uuid.uuid4()))


# =============================================================================
# STAGE INPUT SELECTION TYPES
# =============================================================================


class SelectionStatus(Enum):
    """Status of an input selection operation."""
    PENDING = "pending"
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class StreamRecordReference:
    """
    Reference to one committed stream record for stage consumption.
    
    This is a lightweight reference that preserves identity without
    copying large payloads.
    """
    record_id: str  # StreamRecordId.value
    stream_id: str  # StreamId.value
    position: int   # Sequence number within generation
    generation_id: str  # StreamGenerationId.value


@dataclass(frozen=True)
class SelectedRecord:
    """One record selected for stage consumption."""
    reference: StreamRecordReference
    provenance: str = ""  # How this record was selected
    alignment_key: Optional[str] = None  # For cross-stream alignment


@dataclass(frozen=True)
class InputSelectionPolicy:
    """
    Policy for selecting records from streams.
    
    Defines constraints on selection without being executable logic.
    """
    max_records_per_stream: int = 100  # Bounded fan-in
    min_required_streams: int = 1      # Minimum streams required
    optional_streams_allowed: bool = True
    alignment_policy: "AlignmentPolicy" = field(
        default_factory=lambda: AlignmentPolicy.CORRELATION_ID
    )
    freshness_window_seconds: float = 30.0  # Maximum age for records


@dataclass(frozen=True)
class InputSelectionResult:
    """
    Result of one input selection operation.
    
    This is the output of deterministic selection logic.
    """
    selection_id: StageInputSelectionId
    stage_id: str
    cycle_id: str
    
    # Selection state
    selected_record_references: List[SelectedRecord]
    excluded_records: Dict[str, str]  # record_id -> exclusion reason
    cursor_snapshots: Dict[str, int]  # stream_id -> snapshot position
    
    # Policy info
    selection_policy_version: int = 1
    created_at_utc: float = field(default_factory=time.time)
    
    # Context
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: str = "stage_selection"
    
    # Status
    status: SelectionStatus = SelectionStatus.PENDING
    
    @property
    def record_count(self) -> int:
        return len(self.selected_record_references)
    
    @property
    def stream_count(self) -> int:
        unique_streams = set(r.reference.stream_id for r in self.selected_record_references)
        return len(unique_streams)


# =============================================================================
# INPUT ALIGNMENT TYPES
# =============================================================================


class AlignmentPolicy(Enum):
    """Policy for cross-stream record alignment."""
    NONE = "none"                         # No alignment, select independently
    CORRELATION_ID = "correlation_id"     # Align by correlation ID
    CAUSATION_ID = "causation_id"         # Align by causation ID
    EVENT_TIME_WINDOW = "event_time_window"  # Align within time window
    COMMIT_TIME_WINDOW = "commit_time_window"  # Align within commit window
    CANONICAL_SEQUENCE = "canonical_sequence"  # Align by sequence number


@dataclass(frozen=True)
class AlignmentContext:
    """Context for alignment decisions."""
    stream_id: str
    record_count: int
    min_alignment_key: Optional[str] = None
    max_alignment_key: Optional[str] = None
    alignment_policy: AlignmentPolicy = AlignmentPolicy.NONE


# =============================================================================
# INPUT SNAPSHOT TYPES
# =============================================================================


@dataclass(frozen=True)
class StageInputSnapshot:
    """
    Immutable snapshot of selected inputs for one stage.
    
    This represents the complete input state at a point in time.
    """
    snapshot_id: InputSnapshotId
    thread_id: str
    loop_id: str
    cycle_id: str
    stage_id: str
    
    # Selected records (references, not full payloads)
    selected_records: List[SelectedRecord]
    
    # Cursor snapshots at selection time
    cursor_snapshots: Dict[str, int]  # stream_id -> position
    
    # Alignment summary
    alignment_summary: str = ""  # Human-readable alignment info
    
    # Policy & context
    input_policy_version: int = 1
    created_at_utc: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    
    # Provenance
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: str = "stage_input_snapshot"
    
    @property
    def record_count(self) -> int:
        return len(self.selected_records)
    
    @property
    def stream_ids(self) -> List[str]:
        """Get unique stream IDs in this snapshot."""
        unique = []
        seen = set()
        for r in self.selected_records:
            if r.reference.stream_id not in seen:
                seen.add(r.reference.stream_id)
                unique.append(r.reference.stream_id)
        return unique


# =============================================================================
# STAGE ADMISSION TYPES
# =============================================================================


class AdmissionDecision(Enum):
    """Decision of stage admission evaluation."""
    ADMIT = "admit"                 # Stage may proceed
    WAIT = "wait"                   # Wait for more inputs/capabilities
    ADMIT_DEGRADED = "admit_degraded"  # Proceed with degraded mode
    SKIP = "skip"                   # Skip this stage (e.g., precondition not met)
    REJECT = "reject"               # Reject (e.g., invalid input, policy violation)
    CANCEL = "cancel"               # Cancel stage execution
    FAIL = "fail"                   # Fail immediately


@dataclass(frozen=True)
class StageAdmissionContext:
    """Context for admission evaluation."""
    snapshot: StageInputSnapshot
    cycle_progression_state: str  # e.g., CycleProgressionState.ACTIVE.value
    thread_health_status: str     # e.g., "healthy", "degraded"
    
    # Resource availability (at time of decision)
    network_availability: Dict[str, bool]  # network_id → available
    capability_availability: Dict[str, bool]  # capability_id → available
    
    # Policy constraints
    trust_threshold: float = 0.5      # Minimum trust score
    privacy_level: str = "standard"   # e.g., "standard", "restricted"
    security_classification: str = "internal"


@dataclass(frozen=True)
class StageAdmissionResult:
    """
    Result of stage admission evaluation.
    
    This is distinct from stream admission (which determines if a record
    enters the stream) and activation admission (which determines if an
    activation may proceed).
    """
    admission_id: StageAdmissionId
    stage_id: str
    cycle_id: str
    
    decision: AdmissionDecision
    reason: str  # Human-readable explanation
    
    # Context at time of decision
    input_snapshot_id: Optional[str] = None
    admitted_at_utc: float = field(default_factory=time.time)
    
    # If waiting, what's needed?
    wait_condition: Optional[str] = None  # e.g., "awaiting optional stream"
    
    # If admitting degraded, what's missing?
    degradation_details: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def is_admitted(self) -> bool:
        return self.decision in {
            AdmissionDecision.ADMIT,
            AdmissionDecision.ADMIT_DEGRADED
        }
    
    def is_skipped(self) -> bool:
        return self.decision == AdmissionDecision.SKIP


# =============================================================================
# NETWORK ELIGIBILITY TYPES
# =============================================================================


class NetworkEligibilityStatus(Enum):
    """Status of network eligibility evaluation."""
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"         # Doesn't meet criteria
    WAITING = "waiting"               # Waiting for dependencies
    CANCELLED = "cancelled"           # Cancelled by policy


@dataclass(frozen=True)
class NetworkEligibilityContext:
    """Context for network eligibility evaluation."""
    stage_id: str
    cycle_id: str
    input_snapshot_id: Optional[str] = None
    
    # Stage properties that affect eligibility
    stage_kind: str = ""              # e.g., "perception", "reasoning"
    stage_objective: str = ""         # Semantic purpose
    
    # Available resources
    available_capabilities: List[str] = field(default_factory=list)
    available_systems: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class NetworkEligibilityResult:
    """
    Result of network eligibility evaluation for one stage.
    
    Multiple networks may be eligible for one stage.
    One network may be eligible for many stages.
    """
    network_id: str
    status: NetworkEligibilityStatus
    
    # Eligibility evidence
    eligibility_reasons: List[str] = field(default_factory=list)
    ineligibility_reasons: List[str] = field(default_factory=list)
    
    # Context
    evaluated_at_utc: float = field(default_factory=time.time)
    stage_id: str = ""
    cycle_id: str = ""
    
    # If waiting, what's missing?
    wait_condition: Optional[str] = None


# =============================================================================
# ACTIVATION TYPES
# =============================================================================


class ActivationState(Enum):
    """States in activation lifecycle."""
    PLANNED = "planned"
    ADMITTED = "admitted"             # Stage admitted, ready to activate
    STARTING = "starting"
    ACTIVE = "active"
    WAITING = "waiting"               # Waiting for dependencies
    COMPLETING = "completing"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    FAILING = "failing"
    FAILED = "failed"


@dataclass(frozen=True)
class ActivationRequestId:
    """Unique identifier for one activation request."""
    value: str

    @classmethod
    def generate(cls) -> "ActivationRequestId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class NetworkActivationRequest:
    """
    Request from a stage to activate one network.
    
    This is a proposal, not an execution command.
    """
    request_id: ActivationRequestId
    stage_id: str
    cycle_id: str
    
    # Target network
    network_id: str
    
    # Input reference
    input_snapshot_id: Optional[str] = None
    
    # Requested capabilities
    requested_capabilities: List[str] = field(default_factory=list)
    
    # Resource constraints
    resource_budget: Dict[str, int] = field(default_factory=dict)  # e.g., {"cpu": 100}
    deadline: Optional[float] = None  # UTC timestamp
    
    # Priority & policy
    priority: int = 0                 # Higher = more urgent
    requested_by: str = "stage"
    
    # Context
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: str = "stage_activation_request"
    
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class NetworkActivationPlan:
    """
    Validated plan for network activation.
    
    Built before execution, contains all necessary information.
    """
    plan_id: NetworkActivationPlanId
    request_id: ActivationRequestId
    
    network_id: str
    stage_id: str
    cycle_id: str
    
    # Input reference
    input_snapshot_id: Optional[str] = None
    
    # Plan details
    eligible_capabilities: List[str] = field(default_factory=list)
    capability_invocation_order: List[List[str]] = field(
        default_factory=list)  # Lists of parallel groups
    required_systems: List[str] = field(default_factory=list)
    
    # Resource budget (from request, possibly adjusted)
    resource_budget: Dict[str, int] = field(default_factory=dict)
    deadline: Optional[float] = None
    
    # Policies
    cancellation_policy: str = "immediate"  # immediate, wait_for_completion
    failure_policy: str = "fail_stage"      # fail_stage, skip_network
    
    # Context
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_parallel(self) -> bool:
        """Check if this plan has parallel capability groups."""
        return len(self.capability_invocation_order) > 1


@dataclass(frozen=True)
class NetworkActivationContext:
    """
    Immutable context for network activation execution.
    
    Contains everything needed during activation, no live objects.
    """
    activation_id: str
    network_id: str
    
    stage_id: str
    cycle_id: str
    thread_id: str
    loop_id: str
    
    # Input reference (not the full snapshot, just IDs)
    input_snapshot_ref: str  # InputSnapshotId.value
    
    # Capability plan references
    capability_plan_id: Optional[str] = None
    capability_invocation_ids: List[str] = field(default_factory=list)
    
    # System references (by ID, not live objects)
    system_references: List[str] = field(default_factory=list)
    
    # Resource state at start
    resource_budget: Dict[str, int] = field(default_factory=dict)
    deadline: Optional[float] = None
    
    # Context
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: str = "network_activation_context"
    
    created_at_utc: float = field(default_factory=time.time)


# =============================================================================
# CAPABILITY INVOCATION TYPES
# =============================================================================


@dataclass(frozen=True)
class CapabilityInvocationPlan:
    """Plan for one capability invocation within an activation."""
    invocation_id: CapabilityInvocationId
    network_activation_id: str
    
    # Which capability
    capability_id: str
    
    # Input projections from input snapshot
    input_projections: Dict[str, Any] = field(default_factory=dict)
    
    # Required systems (by ID)
    required_systems: List[str] = field(default_factory=list)
    
    # Constraints
    deadline: Optional[float] = None
    priority: int = 0


@dataclass(frozen=True)
class CapabilityOutput:
    """
    Output from one capability invocation.
    
    This is a proposal/artifact, not yet committed to a stream.
    """
    output_id: str
    invocation_id: CapabilityInvocationId
    
    # Artifact reference (not the payload itself)
    artifact_reference: str  # e.g., "artifact:sha256:..."
    
    # Target for routing
    target_owner: Optional[str] = None  # e.g., stream_id or system_id
    
    # Suggested routes
    suggested_routes: List[str] = field(default_factory=list)
    
    # Metadata
    status: str = "produced"
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    created_at_utc: float = field(default_factory=time.time)
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


# =============================================================================
# OUTPUT ROUTE TYPES
# =============================================================================


@dataclass(frozen=True)
class OutputRouteDescriptor:
    """
    Descriptor for one output routing decision.
    
    Maps capability output to target stream(s).
    """
    route_id: str
    invocation_id: CapabilityInvocationId
    
    # Source artifact
    artifact_reference: str
    
    # Target
    target_stream_id: Optional[str] = None  # Canonical stream for commit
    target_owner_id: Optional[str] = None   # Owner of target stream
    
    # Route properties
    priority: int = 0
    expiration: Optional[float] = None  # UTC timestamp
    
    # Delivery expectations
    delivery_expectation: str = "best_effort"  # best_effort, guaranteed
    
    # Commit policy
    commit_policy: str = "canonical_stream_authority"
    
    # Failure handling
    failure_policy: str = "retry_then_fail"
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


# =============================================================================
# ACTIVATION RESULT TYPES
# =============================================================================


class ActivationResultStatus(Enum):
    """Status of network activation completion."""
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    FAILED_BEFORE_INVOCATION = "failed_before_invocation"
    FAILED_DURING_INVOCATION = "failed_during_invocation"
    FAILED_AFTER_PARTIAL = "failed_after_partial"


@dataclass(frozen=True)
class ActivationResult:
    """
    Result of network activation execution.
    
    Contains all outcomes from the activation lifecycle.
    """
    result_id: str
    activation_id: str
    network_id: str
    
    stage_id: str
    cycle_id: str
    
    status: ActivationResultStatus
    
    # Capability results
    capability_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Output artifacts (references)
    output_artifact_references: List[str] = field(default_factory=list)
    
    # Route results (which routes succeeded/failed)
    route_results: Dict[str, str] = field(default_factory=dict)  # route_id → status
    
    # Committed positions (if any outputs committed)
    committed_stream_positions: List[str] = field(default_factory=list)
    
    # Partial failures
    partial_failures: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Status tracking
    deadline_status: str = "unknown"  # met, missed, unknown
    cancellation_status: str = "not_cancelled"
    
    # Resource usage (bounded)
    resource_usage: Dict[str, int] = field(default_factory=dict)
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    created_at_utc: float = field(default_factory=time.time)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "StageInputSelectionId",
    "InputSnapshotId",
    "StageAdmissionId",
    "NetworkActivationRequestId",
    "NetworkActivationPlanId",
    "CapabilityInvocationId",
    
    # Selection types
    "StreamRecordReference",
    "SelectedRecord",
    "InputSelectionPolicy",
    "InputSelectionResult",
    "SelectionStatus",
    
    # Alignment types
    "AlignmentPolicy",
    "AlignmentContext",
    
    # Snapshot types
    "StageInputSnapshot",
    
    # Admission types
    "AdmissionDecision",
    "StageAdmissionContext",
    "StageAdmissionResult",
    
    # Eligibility types
    "NetworkEligibilityStatus",
    "NetworkEligibilityContext",
    "NetworkEligibilityResult",
    
    # Activation types
    "ActivationState",
    "NetworkActivationRequest",
    "NetworkActivationPlan",
    "NetworkActivationContext",
    
    # Capability types
    "CapabilityInvocationPlan",
    "CapabilityOutput",
    
    # Route types
    "OutputRouteDescriptor",
    
    # Result types
    "ActivationResultStatus",
    "ActivationResult",
]