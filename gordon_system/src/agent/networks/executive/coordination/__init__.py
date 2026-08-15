# Gordon Executive Network Coordination Contracts - Phase 4.4.10A.2
# ============================================================================

"""
Executive Coordination Architecture Specification.

This is Phase 4.4.10A.2: Executive Coordination and Runtime Participation.

The Executive Network coordinates with the remainder of Gordon's cognitive
architecture without owning any subsystems. It participates in runtime without
depending on concrete implementations.

ARCHITECTURAL PRINCIPLES:
========================

COORDINATION MODEL:
    Executive coordinates.
    It does not duplicate or own subsystem functionality.
    
PARTICIPATION MODEL:
    Executive participates.
    It does not implement runtime, scheduler, or threads.
    
OWNERSHIP MODEL:
    Subsystem ownership is preserved.
    Coordination never implies authority transfer.

ARCHITECTURAL BOUNDARIES:
========================

EXECUTIVE OWNS (semantic state):
    - Active goals and commitments
    - Task sets and priorities
    - Current mode and strategy
    - Executive state transitions
    - Decision requirements

EXECUTIVE COORDINATES WITH (ownership preserved):
    - Attention Network: Focus allocation requests, attentional feedback
    - Motivation Network: Drive signals, urgency references, priority advice
    - Working Memory: Read semantics, write reservations, salience requests
    - Workspace: Allocation requests, reference sharing, lifecycle awareness
    - Reasoning: Semantic conclusions, evidence evaluation
    - Planning: Plan generation, dependency resolution
    - Strategy: Strategy selection, revision recommendations
    - Goal System: Goal maintenance, progress tracking
    - Commitments: Commitment validation, enforcement
    - Policies: Policy application, compliance verification
    - Security: Authorization checks, permission validation
    - Action Selection: Action candidates, constraints
    - Execution: Task execution, completion feedback
    - Monitoring: State observation, anomaly detection
    - Learning: Pattern recognition, adaptation recommendations
    - Recovery: Error recovery, state restoration
    - Alerting Network: Exogenous attention notifications
    - Focusing Network: Endogenous focus coordination
    - Default Network: Internally oriented cognition coordination
    - Identity: Self-referential processing, continuity
    - Memory: Durable records, associative retrieval
    - World Model: State representation, prediction inputs
    - Prediction: Future state estimation
    - Evaluation: Assessment of products and outcomes
    - Executive State: Current mode, readiness, capacity

NO DUPLICATION:
    Executive NEVER:
        - Computes attention (owned by Attention/Focusing)
        - Maintains memory records (owned by Memory)
        - Generates plans (owned by Planning)
        - Executes actions (owned by Execution)
        - Owns Working Memory (owned by its subsystem)
        - Owns Workspace (shared substrate)
        - Implements runtime (owned by execution environment)
        - Schedules threads/processes
        - Manages coroutines/asyncio

ARCHITECTURAL LAWS:
==================

EXEC-COORD-LAW-001: Executive coordinates.
                    It does not duplicate subsystem functionality.

EXEC-COORD-LAW-002: Executive participates.
                    It does not implement runtime primitives.

EXEC-COORD-LAW-003: Subsystem ownership is preserved.
                    Coordination never implies ownership transfer.

EXEC-COORD-LAW-004: Coordination never implies authority transfer.
                  Executive may request, but subsystems decide implementation.

EXEC-COORD-LAW-005: Executive never owns Attention Network.
                    Focus computation remains computational only.

EXEC-COORD-LAW-006: Executive never owns Motivation Network.
                    Drive state representation is motivation's responsibility.

EXEC-COORD-LAW-007: Executive never owns Working Memory.
                    Active content maintenance is WM's responsibility.

EXEC-COORD-LAW-008: Executive never owns Workspace.
                    Shared substrate remains shared.

EXEC-COORD-LAW-009: Loops remain external runtime constructs.
                  Executive participates, it does not own execution loops.

EXEC-COORD-LAW-010: All runtime participation is implementation-neutral.
                  No scheduler, thread, coroutine, or asyncio concepts.

PHASE STRUCTURE:
===============

Phase 4.4.10A.2 defines:
    - Coordination contracts with all subsystems
    - Runtime participation semantics
    - Loop participation semantics
    - Event participation semantics
    - Synchronization model
    - Architectural laws and invariants

IMPLEMENTATION STATUS:
=====================

This package is entirely runtime-neutral.
It defines semantic contracts, NOT implementations.

No scheduler, loop, coroutine, thread, executor,
asyncio construct, process, callback, or runtime
implementation is introduced here.

VERSION: 1.0.0
COMPATIBILITY: forward (phased implementation)
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only
"""

# =============================================================================
# COORDINATION IDENTITY TYPES
# =============================================================================

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional, Literal
from enum import Enum, auto
import uuid


@dataclass(frozen=True)
class CoordinationId:
    """Unique identifier for a coordination event."""
    value: str = field(default_factory=lambda: f"coord_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def generate(cls) -> "CoordinationId":
        return cls(value=f"coord_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class CoordinationRequestReference:
    """Immutable reference to a coordination request."""
    request_id: str = field(default_factory=lambda: f"coord_req_{uuid.uuid4().hex[:16]}")
    timestamp_utc: float = 0.0
    
    @classmethod
    def at_time(cls, timestamp_utc: float) -> "CoordinationRequestReference":
        return cls(timestamp_utc=timestamp_utc)


@dataclass(frozen=True)
class CoordinationResponseReference:
    """Immutable reference to a coordination response."""
    response_id: str = field(default_factory=lambda: f"coord_resp_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def generate(cls) -> "CoordinationResponseReference":
        return cls()


@dataclass(frozen=True)
class CoordinationOutcomeReference:
    """Immutable reference to a coordination outcome."""
    outcome_id: str = field(default_factory=lambda: f"coord_outcome_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def generate(cls) -> "CoordinationOutcomeReference":
        return cls()


# =============================================================================
# COORDINATION STATE KINDS - Semantic executive states (NOT runtime states)
# =============================================================================


class CoordinationStateKind(Enum):
    """
    Kinds of coordination state transitions.
    
    These are semantic state descriptions, NOT process or thread states:
        INACTIVE: Not currently coordinating
        DORMANT: Ready to coordinate but not activated
        WAITING: Awaiting external conditions
        ACTIVE: Actively coordinating
        COORDINATING: In the midst of coordination
        DELIBERATING: Evaluating options before deciding
        SUSPENDED: Temporarily suspended by external request
        INTERRUPTED: Interrupted by higher-priority event
        RECOVERING: Recovering from error state
        COMPLETED: Coordination cycle completed successfully
    
    These are NOT:
        - Process states
        - Thread states
        - Scheduler states
        - Runtime activation flags
    """
    
    INACTIVE = "inactive"
    DORMANT = "dormant"
    WAITING = "waiting"
    ACTIVE = "active"
    COORDINATING = "coordinating"
    DELIBERATING = "deliberating"
    SUSPENDED = "suspended"
    INTERRUPTED = "interrupted"
    RECOVERING = "recovering"
    COMPLETED = "completed"


# =============================================================================
# SUBSYSTEM OWNERSHIP CONSTANTS - Canonical subsystem identifiers
# =============================================================================


class SubsystemKind(Enum):
    """
    Kinds of cognitive subsystems.
    
    Each represents a canonical subsystem that Executive coordinates with
    while preserving ownership.
    """
    
    # Attention-related
    ATTENTION_NETWORK = "attention_network"
    FOCUSING_NETWORK = "focusing_network"
    ALERTING_NETWORK = "alerting_network"
    
    # Motivation-related
    MOTIVATION_NETWORK = "motivation_network"
    
    # Memory-related
    WORKING_MEMORY = "working_memory"
    MEMORY_SYSTEM = "memory_system"
    
    # Cognition-related
    REASONING = "reasoning"
    PLANNING = "planning"
    STRATEGY = "strategy"
    PREDICTION = "prediction"
    
    # Execution-related
    EXECUTION = "execution"
    ACTION_SELECTION = "action_selection"
    
    # Meta-cognition
    GOAL_SYSTEM = "goal_system"
    COMMITMENTS = "commitments"
    POLICIES = "policies"
    SECURITY = "security"
    
    # Monitoring and learning
    MONITORING = "monitoring"
    LEARNING = "learning"
    RECOVERY = "recovery"
    
    # Default network (internally oriented cognition)
    DEFAULT_NETWORK = "default_network"
    
    # Identity and evaluation
    IDENTITY = "identity"
    MEMORY2 = "memory"
    WORLD_MODEL = "world_model"
    EVALUATION = "evaluation"
    WORKSPACE = "workspace"


# =============================================================================
# COORDINATION CONTRACT TYPES - For each subsystem interaction
# =============================================================================


@dataclass(frozen=True)
class CoordinationContract:
    """
    Semantic contract for subsystem coordination.
    
    This defines HOW Executive interacts with a subsystem, NOT WHAT the
    subsystem does internally. Subsystem implementation details remain
    private to that subsystem.
    """
    
    subsystem_kind: SubsystemKind
    """Which subsystem this contract governs."""
    
    request_type: str
    """Type of coordination request (e.g., 'read', 'write', 'evaluate')."""
    
    response_type: str
    """Expected response type (e.g., 'assessment', 'proposal', 'result')."""
    
    ownership_preserved: bool = True
    """True if subsystem retains full ownership."""
    
    authority_transfer: Literal["none", "advisory", "binding"] = "none"
    """Level of authority transfer (none for semantic contracts)."""
    
    visibility: Literal["public", "protected", "private"] = "public"
    """Visibility level of this contract."""


# =============================================================================
# COORDINATION DIRECTIONS - Executive  Subsystem interaction direction
# =============================================================================


class CoordinationDirection(Enum):
    """
    Direction of coordination.
    
    EXECUTIVE -> SUBSYSTEM: Executive makes requests, provides projections
    SUBSYSTEM -> EXECUTIVE: Subsystem provides assessments, feedback
    
    These are NOT data flow directions; they describe the semantic
    relationship between systems.
    """
    
    # Executive -> Subsystem (request/projection)
    EXECUTIVE_TO_SUBSYSTEM = "executive_to_subsystem"
    
    # Subsystem -> Executive (assessment/feedback)
    SUBSYSTEM_TO_EXECUTIVE = "subsystem_to_executive"


# =============================================================================
# ATTENTION COORDINATION
# =============================================================================


@dataclass(frozen=True)
class AttentionCoordinationRequest:
    """
    Request to the Attention Network.
    
    EXECUTIVE PROPOSAL -> ATTENTION COMPUTATION
    
    Executive does NOT compute attention. Executive requests attentional
    resources and provides focus priorities as advisory context.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Focus priority (Executive recommendation, not directive)
    focus_priority: float = 0.5
    """Priority for attention allocation (0.0 to 1.0)."""
    
    # Attentional constraints
    max_duration_seconds: Optional[float] = None
    """Maximum duration for this focus period."""
    
    interruption_cost: Optional[float] = None
    """Estimated cost of interrupting this focus."""
    
    deadline_utc: Optional[float] = None
    """Deadline for attention allocation."""
    
    # Context
    task_relevance: float = 0.5
    """How relevant is current task to active goals."""
    
    urgency: Literal["low", "medium", "high", "critical"] = "medium"
    """Urgency level of this request."""
    
    # Request type
    request_kind: Literal[
        "focus_request",
        "release_focus",
        "prioritize_targets",
        "adjust_precision",
        "suppress_distractions"
    ] = "focus_request"


@dataclass(frozen=True)
class AttentionCoordinationResponse:
    """
    Response from the Attention Network.
    
    ATTENTION COMPUTATION -> EXECUTIVE ASSESSMENT
    
    The Attention Network produces assessments of focus conditions,
    not executive decisions. Executive interprets these.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Assessment
    recommended_primary_target: Optional[str] = None
    """Recommended primary attention target."""
    
    secondary_targets: Tuple[str, ...] = ()
    """Secondary attention targets."""
    
    precision_recommendation: float = 0.5
    """Recommended precision level (0.0 to 1.0)."""
    
    persistence_recommendation: float = 0.5
    """Recommended persistence level (0.0 to 1.0)."""
    
    resource_demand_estimate: float = 0.5
    """Estimated resource demand (0.0 to 1.0)."""
    
    confidence_level: float = 0.5
    """Confidence in assessment (0.0 to 1.0)."""
    
    stability_information: Literal["stable", "fluctuating", "unstable"] = "stable"
    """Current attentional stability."""
    
    # Executive decision is NOT part of this response
    # Executive makes its own decision based on this assessment


# =============================================================================
# MOTIVATION COORDINATION
# =============================================================================


@dataclass(frozen=True)
class MotivationCoordinationRequest:
    """
    Request to the Motivation Network.
    
    EXECUTIVE PROPOSAL -> MOTIVATIONAL SIGNALS
    
    Motivation proposes drive states and urgency signals.
    Executive decides how to act on them.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    goal_reference: Optional[str] = None
    """Reference to the goal being pursued."""
    
    current_drive_state: Literal["low", "medium", "high", "urgent"] = "medium"
    """Current drive state assessment."""
    
    urgency: Literal["low", "medium", "high", "critical"] = "medium"
    """Urgency of achieving goal."""
    
    # Request type
    request_kind: Literal[
        "drive_reference",
        "urgency_assessment",
        "priority_recommendation",
        "conflict_resolution",
        "inhibition_request"
    ] = "priority_recommendation"


@dataclass(frozen=True)
class MotivationCoordinationResponse:
    """
    Response from the Motivation Network.
    
    MOTIVATION -> EXECUTIVE ADVICE
    
    Motivation provides drive signals and urgency references.
    Executive interprets these as advice, not commands.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Drive state assessment
    primary_drive: Literal["approach", "avoidance", "neutral"] = "neutral"
    """Primary motivational drive."""
    
    urgency_reference: float = 0.5
    """Urgency reference (0.0 to 1.0)."""
    
    persistence_reference: float = 0.5
    """Persistence reference (0.0 to 1.0)."""
    
    priority_adjustment: float = 0.0
    """Priority adjustment recommendation (-1.0 to 1.0)."""
    
    conflict_indicators: Tuple[str, ...] = ()
    """Any identified motivational conflicts."""
    
    inhibition_recommendation: Literal["none", "partial", "full"] = "none"
    """Recommended inhibition level."""


# =============================================================================
# WORKING MEMORY COORDINATION
# =============================================================================


@dataclass(frozen=True)
class WorkingMemoryCoordinationRequest:
    """
    Request to Working Memory.
    
    EXECUTIVE REQUESTS -> WM STATE ACCESS
    
    Executive NEVER owns Working Memory. Executive may request
    access, reservations, or salience adjustments.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Access type
    access_kind: Literal["read", "write", "reserve", "snapshot"] = "read"
    
    # Content specification
    content_ids: Tuple[str, ...] = ()
    """IDs of WM contents to access."""
    
    salience_adjustment: Optional[float] = None
    """Requested salience adjustment (-1.0 to 1.0)."""
    
    retention_duration_seconds: Optional[int] = None
    """Requested retention duration for write operations."""
    
    # Context window
    context_window_size: int = 1
    """Number of items to include in context window."""
    
    # Ownership note: Executive does NOT own WM contents,
    # only requests access to them


@dataclass(frozen=True)
class WorkingMemoryCoordinationResponse:
    """
    Response from Working Memory.
    
    WM -> EXECUTIVE STATE PROJECTION
    
    WM provides projections of its state, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State projection
    accessible_content: Tuple[str, ...] = ()
    """Content IDs that are accessible."""
    
    salience_values: Dict[str, float] = field(default_factory=dict)
    """Salience values for content (content_id -> value)."""
    
    context_window: Tuple[str, ...] = ()
    """Items in current context window."""
    
    capacity_remaining: int = 0
    """Remaining WM capacity."""
    
    reservation_status: Literal["granted", "denied", "pending"] = "granted"
    """Status of any requested reservations."""


# =============================================================================
# WORKSPACE COORDINATION
# =============================================================================


@dataclass(frozen=True)
class WorkspaceCoordinationRequest:
    """
    Request to Workspace.
    
    EXECUTIVE REQUESTS -> WORKSPACE STATE
    
    Workspace is a shared substrate. Executive does NOT own it.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Request type
    request_kind: Literal[
        "allocate",
        "release",
        "reference",
        "collaborate"
    ] = "allocate"
    
    # Allocation details (for allocate)
    workspace_size: int = 1
    """Number of slots requested."""
    
    isolation_level: Literal["shared", "isolated"] = "shared"
    """Isolation level for workspace."""
    
    # Reference details (for reference requests)
    workspace_id: Optional[str] = None
    """ID of existing workspace to reference."""


@dataclass(frozen=True)
class WorkspaceCoordinationResponse:
    """
    Response from Workspace.
    
    WORKSPACE -> EXECUTIVE ASSIGNMENT
    
    Workspace assigns or confirms allocation, but does not
    become owned by Executive.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Allocation result
    assigned_workspace_ids: Tuple[str, ...] = ()
    """IDs of allocated workspace slots."""
    
    isolation_granted: bool = True
    """Whether requested isolation level was granted."""
    
    collaboration_participants: Tuple[str, ...] = ()
    """Other participants in shared workspace (if any)."""
    
    lifecycle_status: Literal["allocated", "released", "expired"] = "allocated"
    """Current lifecycle status of allocation."""


# =============================================================================
# REASONING COORDINATION
# =============================================================================


@dataclass(frozen=True)
class ReasoningCoordinationRequest:
    """
    Request to Reasoning.
    
    EXECUTIVE REQUEST -> SEMANTIC CONCLUSIONS
    
    Executive coordinates with reasoning for semantic conclusions,
    but does NOT perform reasoning itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Reasoning context
    query_context: str = ""
    """Context or problem description."""
    
    evidence_provided: Tuple[str, ...] = ()
    """Evidence available for reasoning."""
    
    constraints: Tuple[str, ...] = ()
    """Constraints that must be satisfied."""
    
    # Request type
    request_kind: Literal[
        "semantic_conclusion",
        "evidence_evaluation",
        "constraint_satisfaction",
        "inconsistency_detection"
    ] = "semantic_conclusion"


@dataclass(frozen=True)
class ReasoningCoordinationResponse:
    """
    Response from Reasoning.
    
    REASONING -> EXECUTIVE CONCLUSIONS
    
    Reasoning produces semantic conclusions, not executive decisions.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Conclusions
    semantic_conclusions: Tuple[str, ...] = ()
    """Semantic conclusions drawn."""
    
    confidence_level: float = 0.5
    """Confidence in conclusions (0.0 to 1.0)."""
    
    evidence_strength: Literal["strong", "moderate", "weak"] = "moderate"
    """Strength of supporting evidence."""
    
    inconsistency_flags: Tuple[str, ...] = ()
    """Any inconsistencies detected."""


# =============================================================================
# PLANNING COORDINATION
# =============================================================================


@dataclass(frozen=True)
class PlanningCoordinationRequest:
    """
    Request to Planning.
    
    EXECUTIVE REQUEST -> PLAN GENERATION
    
    Executive coordinates with planning for plan generation,
    but does NOT generate plans itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    goal_reference: str = ""
    """Goal to be achieved."""
    
    current_state: Tuple[str, ...] = ()
    """Current state description."""
    
    constraints: Tuple[str, ...] = ()
    """Constraints for plan generation."""
    
    # Request type
    request_kind: Literal[
        "plan_generation",
        "plan_evaluation",
        "dependency_resolution",
        "plan_revision"
    ] = "plan_generation"


@dataclass(frozen=True)
class PlanningCoordinationResponse:
    """
    Response from Planning.
    
    PLANNING -> EXECUTIVE PROPOSALS
    
    Planning produces plans as proposals, not executive decisions.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Plan proposals
    plan_proposals: Tuple[str, ...] = ()
    """Generated plan proposals."""
    
    confidence_level: float = 0.5
    """Confidence in plans (0.0 to 1.0)."""
    
    feasibility_rating: Literal["feasible", "partially_feasible", "infeasible"] = "feasible"
    """Feasibility assessment."""
    
    dependency_graph: Tuple[Tuple[str, str], ...] = ()
    """Dependencies between plan steps (from -> to pairs)."""


# =============================================================================
# STRATEGY COORDINATION
# =============================================================================


@dataclass(frozen=True)
class StrategyCoordinationRequest:
    """
    Request to Strategy.
    
    EXECUTIVE REQUESTS -> STRATEGIC ASSESSMENTS
    
    Executive coordinates with strategy for strategic assessments,
    but does NOT select strategies itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    current_strategy: Optional[str] = None
    """Currently active strategy."""
    
    goal_alignment: float = 0.5
    """How well current strategy aligns with goals."""
    
    environmental_conditions: Tuple[str, ...] = ()
    """Environmental conditions affecting strategy selection."""
    
    # Request type
    request_kind: Literal[
        "strategy_assessment",
        "strategy_recommendation",
        "revision_proposal"
    ] = "strategy_assessment"


@dataclass(frozen=True)
class StrategyCoordinationResponse:
    """
    Response from Strategy.
    
    STRATEGY -> EXECUTIVE ASSESSMENTS
    
    Strategy provides strategic assessments, not executive decisions.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Assessments
    current_strategy_assessment: Literal["valid", "suboptimal", "inappropriate"] = "valid"
    """Assessment of current strategy."""
    
    recommended_strategies: Tuple[str, ...] = ()
    """Recommended alternative strategies."""
    
    confidence_level: float = 0.5
    """Confidence in assessment (0.0 to 1.0)."""
    
    transition_cost: Optional[float] = None
    """Estimated cost of switching strategies."""


# =============================================================================
# GOAL SYSTEM COORDINATION
# =============================================================================


@dataclass(frozen=True)
class GoalCoordinationRequest:
    """
    Request to Goal System.
    
    EXECUTIVE REQUESTS -> GOAL STATE
    
    Executive coordinates with goal system for goal state,
    but does NOT own or maintain goals itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    active_goals: Tuple[str, ...] = ()
    """Currently active goal IDs."""
    
    progress_metrics: Dict[str, float] = field(default_factory=dict)
    """Goal progress metrics (goal_id -> percentage)."""
    
    # Request type
    request_kind: Literal[
        "goal_assessment",
        "progress_update",
        "priority_adjustment"
    ] = "goal_assessment"


@dataclass(frozen=True)
class GoalCoordinationResponse:
    """
    Response from Goal System.
    
    GOAL SYSTEM -> EXECUTIVE STATE
    
    Goal system provides goal state projections, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State projection
    active_goals: Tuple[str, ...] = ()
    """Currently active goals."""
    
    progress_estimates: Dict[str, float] = field(default_factory=dict)
    """Estimated progress (goal_id -> percentage)."""
    
    priority_ordering: Tuple[str, ...] = ()
    """Goals ordered by priority."""
    
    completion_predictions: Dict[str, Optional[float]] = field(default_factory=dict)
    """Predicted completion times (goal_id -> timestamp or None)."""


# =============================================================================
# COMMITMENTS COORDINATION
# =============================================================================


@dataclass(frozen=True)
class CommitmentCoordinationRequest:
    """
    Request to Commitments.
    
    EXECUTIVE REQUESTS -> COMMITMENT STATUS
    
    Executive coordinates with commitment system for validation,
    but does NOT own commitments itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    proposed_commitments: Tuple[str, ...] = ()
    """Commitments being proposed."""
    
    current_commitments: Tuple[str, ...] = ()
    """Currently active commitments."""
    
    # Request type
    request_kind: Literal[
        "commitment_validation",
        "conflict_check",
        "enforcement_status"
    ] = "commitment_validation"


@dataclass(frozen=True)
class CommitmentCoordinationResponse:
    """
    Response from Commitments.
    
    COMMITMENTS -> EXECUTIVE VALIDATION
    
    Commitments provides validation results, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Validation result
    is_valid: bool = True
    """Are proposed commitments valid?"""
    
    conflicting_commitments: Tuple[str, ...] = ()
    """Any conflicts with existing commitments."""
    
    enforcement_status: Literal["active", "suspended", "expired"] = "active"
    """Current enforcement status."""
    
    validation_details: Tuple[str, ...] = ()
    """Detailed validation information."""


# =============================================================================
# POLICIES COORDINATION
# =============================================================================


@dataclass(frozen=True)
class PolicyCoordinationRequest:
    """
    Request to Policies.
    
    EXECUTIVE REQUESTS -> POLICY APPLICATION
    
    Executive coordinates with policies for compliance verification,
    but does NOT own policy authority itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    proposed_action: str = ""
    """Action being proposed."""
    
    context_data: Dict[str, Any] = field(default_factory=dict)
    """Context data for policy evaluation."""
    
    # Request type
    request_kind: Literal[
        "policy_application",
        "compliance_check",
        "constraint_verification"
    ] = "policy_application"


@dataclass(frozen=True)
class PolicyCoordinationResponse:
    """
    Response from Policies.
    
    POLICIES -> EXECUTIVE COMPLIANCE STATE
    
    Policies provides compliance assessments, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Compliance result
    is_compliant: bool = True
    """Is the proposed action compliant with policies?"""
    
    violated_policies: Tuple[str, ...] = ()
    """Any violated policies."""
    
    applicable_constraints: Tuple[str, ...] = ()
    """Constraints that apply to this action."""
    
    compliance_confidence: float = 0.5
    """Confidence in compliance assessment (0.0 to 1.0)."""


# =============================================================================
# SECURITY COORDINATION
# =============================================================================


@dataclass(frozen=True)
class SecurityCoordinationRequest:
    """
    Request to Security.
    
    EXECUTIVE REQUESTS -> AUTHORIZATION STATE
    
    Executive coordinates with security for authorization verification,
    but does NOT own authorization authority itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    requested_action: str = ""
    """Action requesting authorization."""
    
    resource_ids: Tuple[str, ...] = ()
    """Resources being accessed."""
    
    context_data: Dict[str, Any] = field(default_factory=dict)
    """Context data for authorization."""
    
    # Request type
    request_kind: Literal[
        "authorization_check",
        "permission_validation",
        "access_grant"
    ] = "authorization_check"


@dataclass(frozen=True)
class SecurityCoordinationResponse:
    """
    Response from Security.
    
    SECURITY -> EXECUTIVE AUTHORIZATION STATE
    
    Security provides authorization assessments, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Authorization result
    is_authorized: bool = True
    """Is the requested action authorized?"""
    
    denied_reasons: Tuple[str, ...] = ()
    """Reasons for denial (if not authorized)."""
    
    required_permissions: Tuple[str, ...] = ()
    """Permissions required for this action."""
    
    authorization_confidence: float = 0.5
    """Confidence in authorization assessment (0.0 to 1.0)."""


# =============================================================================
# EXECUTION COORDINATION
# =============================================================================


@dataclass(frozen=True)
class ExecutionCoordinationRequest:
    """
    Request to Execution.
    
    EXECUTIVE REQUESTS -> TASK EXECUTION
    
    Executive coordinates with execution for task performance,
    but does NOT perform execution itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    task_specification: str = ""
    """Specification of task to execute."""
    
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    """Resource requirements for execution."""
    
    timeout_seconds: Optional[float] = None
    """Execution timeout."""
    
    # Request type
    request_kind: Literal[
        "task_execution",
        "task_monitoring",
        "task_cancellation"
    ] = "task_execution"


@dataclass(frozen=True)
class ExecutionCoordinationResponse:
    """
    Response from Execution.
    
    EXECUTION -> EXECUTIVE STATUS
    
    Execution provides execution status, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Status
    is_executing: bool = False
    """Is the task currently executing?"""
    
    progress_percentage: float = 0.0
    """Execution progress (0.0 to 1.0)."""
    
    completion_status: Optional[str] = None
    """Completion status if finished."""
    
    error_messages: Tuple[str, ...] = ()
    """Any errors encountered."""


# =============================================================================
# MONITORING COORDINATION
# =============================================================================


@dataclass(frozen=True)
class MonitoringCoordinationRequest:
    """
    Request to Monitoring.
    
    EXECUTIVE REQUESTS -> STATE OBSERVATION
    
    Executive coordinates with monitoring for state observation,
    but does NOT implement monitoring itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    monitored_entities: Tuple[str, ...] = ()
    """Entities to monitor."""
    
    metrics: Tuple[str, ...] = ()
    """Metrics to track."""
    
    threshold: Optional[float] = None
    """Alert threshold for anomalies."""
    
    # Request type
    request_kind: Literal[
        "state_observation",
        "anomaly_detection",
        "trend_analysis"
    ] = "state_observation"


@dataclass(frozen=True)
class MonitoringCoordinationResponse:
    """
    Response from Monitoring.
    
    MONITORING -> EXECUTIVE OBSERVATION
    
    Monitoring provides observation results, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Observation result
    entity_states: Dict[str, Any] = field(default_factory=dict)
    """Observed states of monitored entities."""
    
    anomaly_detected: bool = False
    """Was an anomaly detected?"""
    
    anomaly_details: Tuple[str, ...] = ()
    """Details about any anomalies."""
    
    trend_data: Tuple[Tuple[str, float], ...] = ()
    """Trend data (metric_name -> value pairs)."""


# =============================================================================
# LEARNING COORDINATION
# =============================================================================


@dataclass(frozen=True)
class LearningCoordinationRequest:
    """
    Request to Learning.
    
    EXECUTIVE REQUESTS -> ADAPTATION RECOMMENDATIONS
    
    Executive coordinates with learning for adaptation recommendations,
    but does NOT implement learning itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    experience_data: Tuple[str, ...] = ()
    """Experience data to learn from."""
    
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    """Performance metrics for learning."""
    
    # Request type
    request_kind: Literal[
        "adaptation_recommendation",
        "pattern_recognition",
        "optimization_suggestion"
    ] = "adaptation_recommendation"


@dataclass(frozen=True)
class LearningCoordinationResponse:
    """
    Response from Learning.
    
    LEARNING -> EXECUTIVE RECOMMENDATIONS
    
    Learning provides adaptation recommendations, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Recommendations
    adaptation_recommendations: Tuple[str, ...] = ()
    """Recommended adaptations."""
    
    confidence_level: float = 0.5
    """Confidence in recommendations (0.0 to 1.0)."""
    
    evidence_summary: Tuple[str, ...] = ()
    """Evidence supporting recommendations."""
    
    potential_impacts: Dict[str, str] = field(default_factory=dict)
    """Potential impacts of adaptations (name -> description)."""


# =============================================================================
# RECOVERY COORDINATION
# =============================================================================


@dataclass(frozen=True)
class RecoveryCoordinationRequest:
    """
    Request to Recovery.
    
    EXECUTIVE REQUESTS -> RECOVERY ACTIONS
    
    Executive coordinates with recovery for error handling,
    but does NOT implement recovery itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    failure_description: str = ""
    """Description of failure."""
    
    affected_components: Tuple[str, ...] = ()
    """Components affected by failure."""
    
    error_state: Dict[str, Any] = field(default_factory=dict)
    """Current error state."""
    
    # Request type
    request_kind: Literal[
        "recovery_proposal",
        "rollback_recommendation",
        "state_restoration"
    ] = "recovery_proposal"


@dataclass(frozen=True)
class RecoveryCoordinationResponse:
    """
    Response from Recovery.
    
    RECOVERY -> EXECUTIVE RECOMMENDATIONS
    
    Recovery provides recovery recommendations, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Recommendations
    is_recoverable: bool = True
    """Can the system recover from this failure?"""
    
    recovery_actions: Tuple[str, ...] = ()
    """Proposed recovery actions."""
    
    rollback_points: Tuple[str, ...] = ()
    """Available rollback points."""
    
    estimated_recovery_time_seconds: Optional[float] = None
    """Estimated time to recover."""
    
    risk_assessment: Literal["low", "medium", "high", "critical"] = "low"
    """Risk assessment of recovery actions."""


# =============================================================================
# ALERTING COORDINATION
# =============================================================================


@dataclass(frozen=True)
class AlertingCoordinationRequest:
    """
    Request to Alerting Network.
    
    EXECUTIVE REQUESTS -> EXOGENOUS ALERTS
    
    Executive coordinates with alerting for exogenous attention,
    but does NOT compute alerts itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    current_alerts: Tuple[str, ...] = ()
    """Currently active alerts."""
    
    priority_context: Literal["low", "medium", "high", "critical"] = "medium"
    """Priority context for alert evaluation."""
    
    # Request type
    request_kind: Literal[
        "alert_acknowledgement",
        "priority_assessment",
        "suppression_request"
    ] = "alert_acknowledgement"


@dataclass(frozen=True)
class AlertingCoordinationResponse:
    """
    Response from Alerting Network.
    
    ALERTING -> EXECUTIVE ASSESSMENT
    
    Alerting provides alert assessments, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Assessment
    alerts_requiring_attention: Tuple[str, ...] = ()
    """Alerts that require executive attention."""
    
    priority_adjustment: float = 0.0
    """Priority adjustment recommendation (-1.0 to 1.0)."""
    
    urgency_level: Literal["low", "medium", "high", "critical"] = "medium"
    """Urgency level of alerts."""
    
    recommended_action: Literal[
        "acknowledge",
        "prioritize",
        "suppress",
        "escalate"
    ] = "prioritize"


# =============================================================================
# DEFAULT NETWORK COORDINATION
# =============================================================================


@dataclass(frozen=True)
class DefaultNetworkCoordinationRequest:
    """
    Request to Default Network.
    
    EXECUTIVE REQUESTS -> INTERNALLY ORIENTED COGNITION
    
    Executive coordinates with default network for internally oriented cognition,
    but does NOT own this network itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    coordination_mode: Literal[
        "internally_oriented",
        "external_focus_transition",
        "idle_maintenance"
    ] = "externally_oriented"
    
    requested_processes: Tuple[str, ...] = ()
    """Internally oriented processes to coordinate."""
    
    context_data: Dict[str, Any] = field(default_factory=dict)
    """Context data for coordination."""
    
    # Request type
    request_kind: Literal[
        "initiate_process",
        "monitor_state",
        "terminate_process"
    ] = "initiate_process"


@dataclass(frozen=True)
class DefaultNetworkCoordinationResponse:
    """
    Response from Default Network.
    
    DEFAULT NETWORK -> EXECUTIVE COGNITION PROPOSALS
    
    Default network provides internally oriented cognition proposals,
    not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State projection
    active_processes: Tuple[str, ...] = ()
    """Currently active internally oriented processes."""
    
    cognitive_proposals: Tuple[str, ...] = ()
    """Proposed cognition results from default network."""
    
    confidence_level: float = 0.5
    """Confidence in proposals (0.0 to 1.0)."""
    
    resource_demand_estimate: float = 0.5
    """Estimated resource demand (0.0 to 1.0)."""


# =============================================================================
# IDENTITY COORDINATION
# =============================================================================


@dataclass(frozen=True)
class IdentityCoordinationRequest:
    """
    Request to Identity.
    
    EXECUTIVE REQUESTS -> SELF-REFERENTIAL PROCESSING
    
    Executive coordinates with identity for self-referential processing,
    but does NOT own identity itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    self_referential_context: str = ""
    """Context for self-referential processing."""
    
    consistency_check_required: bool = False
    """Is consistency check required?"""
    
    # Request type
    request_kind: Literal[
        "continuity_assessment",
        "consistency_check",
        "role_assignment"
    ] = "continuity_assessment"


@dataclass(frozen=True)
class IdentityCoordinationResponse:
    """
    Response from Identity.
    
    IDENTITY -> EXECUTIVE SELF-STATE
    
    Identity provides self-state projections, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State projection
    continuity_status: Literal["stable", "disrupted", "recovered"] = "stable"
    """Current identity continuity status."""
    
    consistency_level: float = 0.5
    """Consistency with existing identity (0.0 to 1.0)."""
    
    role_assignments: Tuple[str, ...] = ()
    """Assigned roles for current context."""
    
    self_assessment: Dict[str, Any] = field(default_factory=dict)
    """Self-assessment data."""


# =============================================================================
# MEMORY COORDINATION
# =============================================================================


@dataclass(frozen=True)
class MemoryCoordinationRequest:
    """
    Request to Memory.
    
    EXECUTIVE REQUESTS -> DURABLE RECORD ACCESS
    
    Executive coordinates with memory for durable record access,
    but does NOT own memory records itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    record_ids: Tuple[str, ...] = ()
    """IDs of records to access."""
    
    association_context: Optional[str] = None
    """Context for associative retrieval."""
    
    freshness_threshold_seconds: Optional[int] = None
    """Maximum acceptable age for records."""
    
    # Request type
    request_kind: Literal[
        "record_retrieval",
        "associative_search",
        "provenance_verification"
    ] = "record_retrieval"


@dataclass(frozen=True)
class MemoryCoordinationResponse:
    """
    Response from Memory.
    
    MEMORY -> EXECUTIVE RECORD PROJECTION
    
    Memory provides record projections, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State projection
    retrieved_records: Tuple[str, ...] = ()
    """Retrieved record IDs."""
    
    provenance_info: Dict[str, Any] = field(default_factory=dict)
    """Provenance information for records."""
    
    freshness_status: Literal["fresh", "stale", "expired"] = "fresh"
    """Freshness status of retrieved records."""
    
    confidence_level: float = 0.5
    """Confidence in retrieved data (0.0 to 1.0)."""


# =============================================================================
# WORLD MODEL COORDINATION
# =============================================================================


@dataclass(frozen=True)
class WorldModelCoordinationRequest:
    """
    Request to World Model.
    
    EXECUTIVE REQUESTS -> STATE REPRESENTATION
    
    Executive coordinates with world model for state representation,
    but does NOT own the model itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    current_state_request: bool = True
    """Is this a request for current state?"""
    
    prediction_horizon_seconds: Optional[int] = None
    """Time horizon for predictions."""
    
    query_context: str = ""
    """Context for state queries."""
    
    # Request type
    request_kind: Literal[
        "state_query",
        "prediction_request",
        "inconsistency_detection"
    ] = "state_query"


@dataclass(frozen=True)
class WorldModelCoordinationResponse:
    """
    Response from World Model.
    
    WORLD MODEL -> EXECUTIVE STATE PROJECTION
    
    World model provides state projections, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State projection
    current_state_representation: Dict[str, Any] = field(default_factory=dict)
    """Current state representation."""
    
    predicted_states: Tuple[Dict[str, Any], ...] = ()
    """Predicted future states."""
    
    consistency_level: float = 0.5
    """Consistency with known facts (0.0 to 1.0)."""
    
    uncertainty_estimate: float = 0.5
    """Uncertainty in state representation (0.0 to 1.0)."""


# =============================================================================
# PREDICTION COORDINATION
# =============================================================================


@dataclass(frozen=True)
class PredictionCoordinationRequest:
    """
    Request to Prediction.
    
    EXECUTIVE REQUESTS -> FUTURE STATE ESTIMATION
    
    Executive coordinates with prediction for future state estimation,
    but does NOT implement prediction itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    current_state: Dict[str, Any] = field(default_factory=dict)
    """Current state for prediction."""
    
    action_sequence: Tuple[str, ...] = ()
    """Proposed action sequence to predict."""
    
    time_horizon_seconds: int = 60
    """Prediction time horizon in seconds."""
    
    # Request type
    request_kind: Literal[
        "future_state_estimation",
        "outcome_prediction",
        "uncertainty_quantification"
    ] = "future_state_estimation"


@dataclass(frozen=True)
class PredictionCoordinationResponse:
    """
    Response from Prediction.
    
    PREDICTION -> EXECUTIVE ESTIMATES
    
    Prediction provides estimates, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Estimates
    predicted_states: Tuple[Dict[str, Any], ...] = ()
    """Predicted future states."""
    
    confidence_levels: Dict[str, float] = field(default_factory=dict)
    """Confidence in predictions (state_id -> value)."""
    
    uncertainty_estimate: float = 0.5
    """Overall uncertainty estimate (0.0 to 1.0)."""
    
    alternative_predictions: Tuple[Dict[str, Any], ...] = ()
    """Alternative predicted scenarios."""


# =============================================================================
# EVALUATION COORDINATION
# =============================================================================


@dataclass(frozen=True)
class EvaluationCoordinationRequest:
    """
    Request to Evaluation.
    
    EXECUTIVE REQUESTS -> ASSESSMENT
    
    Executive coordinates with evaluation for assessments,
    but does NOT implement evaluation itself.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Context
    content_to_evaluate: str = ""
    """Content to evaluate."""
    
    criteria: Tuple[str, ...] = ()
    """Evaluation criteria."""
    
    context_data: Dict[str, Any] = field(default_factory=dict)
    """Context for evaluation."""
    
    # Request type
    request_kind: Literal[
        "quality_assessment",
        "completeness_check",
        "consistency_verification"
    ] = "quality_assessment"


@dataclass(frozen=True)
class EvaluationCoordinationResponse:
    """
    Response from Evaluation.
    
    EVALUATION -> EXECUTIVE ASSESSMENT
    
    Evaluation provides assessment results, not ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # Assessment
    quality_score: float = 0.5
    """Quality score (0.0 to 1.0)."""
    
    completeness_percentage: float = 0.5
    """Completeness percentage (0.0 to 1.0)."""
    
    consistency_level: float = 0.5
    """Consistency with known facts (0.0 to 1.0)."""
    
    assessment_details: Tuple[str, ...] = ()
    """Detailed assessment information."""


# =============================================================================
# EXECUTIVE STATE COORDINATION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateCoordinationRequest:
    """
    Request for executive state coordination.
    
    Used when external systems need to coordinate with the current
    executive state without owning it.
    """
    
    request_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State reference
    state_reference: Optional[str] = None
    """Reference to specific executive state."""
    
    state_kind: Literal[
        "active_goals",
        "current_mode",
        "task_set",
        "strategy",
        "priority_ordering"
    ] = "current_mode"
    
    # Request type
    request_kind: Literal[
        "state_read",
        "state_projection",
        "transition_request"
    ] = "state_projection"


@dataclass(frozen=True)
class ExecutiveStateCoordinationResponse:
    """
    Response from executive state coordination.
    
    Provides projections of executive state without ownership transfer.
    """
    
    response_id: CoordinationId = field(default_factory=CoordinationId.generate)
    timestamp_utc: float = 0.0
    
    # State projection
    current_mode: str = "idle"
    """Current executive mode."""
    
    active_goals: Tuple[str, ...] = ()
    """Currently active goals."""
    
    priority_ordering: Tuple[str, ...] = ()
    """Goals ordered by priority."""
    
    task_set_state: Dict[str, Any] = field(default_factory=dict)
    """Current task set state."""
    
    strategy_reference: Optional[str] = None
    """Reference to current strategy."""


# =============================================================================
# COORDINATION CONTRACT REGISTRY - All subsystem contracts
# =============================================================================


EXECUTIVE_COORDINATION_CONTRACTS: Tuple[CoordinationContract, ...] = (
    CoordinationContract(
        subsystem_kind=SubsystemKind.ATTENTION_NETWORK,
        request_type="focus_request",
        response_type="attention_assessment",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.FOCUSING_NETWORK,
        request_type="focus_request",
        response_type="focus_assessment",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.ALERTING_NETWORK,
        request_type="alert_acknowledgement",
        response_type="alert_assessment",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.MOTIVATION_NETWORK,
        request_type="drive_reference",
        response_type="motivation_assessment",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.WORKING_MEMORY,
        request_type="read",
        response_type="wm_projection",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.MEMORY_SYSTEM,
        request_type="record_retrieval",
        response_type="memory_projection",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.REASONING,
        request_type="semantic_conclusion",
        response_type="reasoning_result",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.PLANNING,
        request_type="plan_generation",
        response_type="plan_proposal",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.STRATEGY,
        request_type="strategy_assessment",
        response_type="strategy_assessment",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.GOAL_SYSTEM,
        request_type="goal_assessment",
        response_type="goal_state_projection",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.COMMITMENTS,
        request_type="commitment_validation",
        response_type="validation_result",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.POLICIES,
        request_type="policy_application",
        response_type="compliance_assessment",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.SECURITY,
        request_type="authorization_check",
        response_type="authorization_result",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.EXECUTION,
        request_type="task_execution",
        response_type="execution_status",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.MONITORING,
        request_type="state_observation",
        response_type="observation_result",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.LEARNING,
        request_type="adaptation_recommendation",
        response_type="learning_recommendation",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.RECOVERY,
        request_type="recovery_proposal",
        response_type="recovery_recommendation",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.DEFAULT_NETWORK,
        request_type="initiate_process",
        response_type="cognition_proposal",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.IDENTITY,
        request_type="continuity_assessment",
        response_type="identity_state_projection",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.MEMORY_SYSTEM,
        request_type="record_retrieval",
        response_type="memory_projection",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.WORLD_MODEL,
        request_type="state_query",
        response_type="world_model_projection",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.PREDICTION,
        request_type="future_state_estimation",
        response_type="prediction_result",
        ownership_preserved=True,
        authority_transfer="none"
    ),
    CoordinationContract(
        subsystem_kind=SubsystemKind.EVALUATION,
        request_type="quality_assessment",
        response_type="evaluation_result",
        ownership_preserved=True,
        authority_transfer="none"
    ),
)

# =============================================================================
# IMPORT RUNTIME PARTICIPATION SEMANTICS
# =============================================================================

from gordon_system.src.agent.networks.executive.coordination.runtime import (
    ExecutiveActivationKind,
    ExecutiveInvocationKind,
    ExecutiveParticipationKind,
    ExecutiveCycleParticipation,
    ExecutiveSchedulingParticipation,
    ExecutiveWakeConditions,
    ExecutiveSleepConditions,
    ExecutiveSuspensionKind,
    ExecutiveResumptionKind,
    ExecutiveInterruptionKind,
    ExecutiveCancellationKind,
    ExecutivePreemptionKind,
    ExecutiveSynchronizationKind,
    ExecutiveEventParticipation,
    ExecutiveRuntimeTransition,
    ExecutiveExecutionBoundary,
    ExecutiveFailureParticipation,
    ExecutiveRecoveryParticipationKind,
    ExecutiveIdleParticipation,
    ExecutiveShutdownParticipation,
    ExecutiveLoopParticipation,
    ExecutiveStateParticipation,
    CoordinationBarrier,
    VisibilityGuarantee,
    OrderingGuarantee,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "CoordinationId",
    "CoordinationRequestReference",
    "CoordinationResponseReference",
    "CoordinationOutcomeReference",
    
    # Runtime participation (from runtime.py)
    "ExecutiveActivationKind",
    "ExecutiveInvocationKind",
    "ExecutiveParticipationKind",
    "ExecutiveCycleParticipation",
    "ExecutiveSchedulingParticipation",
    "ExecutiveWakeConditions",
    "ExecutiveSleepConditions",
    "ExecutiveSuspensionKind",
    "ExecutiveResumptionKind",
    "ExecutiveInterruptionKind",
    "ExecutiveCancellationKind",
    "ExecutivePreemptionKind",
    "ExecutiveSynchronizationKind",
    "ExecutiveEventParticipation",
    "ExecutiveRuntimeTransition",
    "ExecutiveExecutionBoundary",
    "ExecutiveFailureParticipation",
    "ExecutiveRecoveryParticipationKind",
    "ExecutiveIdleParticipation",
    "ExecutiveShutdownParticipation",
    "ExecutiveLoopParticipation",
    "ExecutiveStateParticipation",
    "CoordinationBarrier",
    "VisibilityGuarantee",
    "OrderingGuarantee",
    
    # State kinds
    "CoordinationStateKind",
    
    # Subsystem identifiers
    "SubsystemKind",
    
    # Contracts
    "CoordinationContract",
    "EXECUTIVE_COORDINATION_CONTRACTS",
    
    # Direction
    "CoordinationDirection",
    
    # Attention coordination
    "AttentionCoordinationRequest",
    "AttentionCoordinationResponse",
    
    # Motivation coordination
    "MotivationCoordinationRequest",
    "MotivationCoordinationResponse",
    
    # Working memory coordination
    "WorkingMemoryCoordinationRequest",
    "WorkingMemoryCoordinationResponse",
    
    # Workspace coordination
    "WorkspaceCoordinationRequest",
    "WorkspaceCoordinationResponse",
    
    # Reasoning coordination
    "ReasoningCoordinationRequest",
    "ReasoningCoordinationResponse",
    
    # Planning coordination
    "PlanningCoordinationRequest",
    "PlanningCoordinationResponse",
    
    # Strategy coordination
    "StrategyCoordinationRequest",
    "StrategyCoordinationResponse",
    
    # Goal system coordination
    "GoalCoordinationRequest",
    "GoalCoordinationResponse",
    
    # Commitments coordination
    "CommitmentCoordinationRequest",
    "CommitmentCoordinationResponse",
    
    # Policies coordination
    "PolicyCoordinationRequest",
    "PolicyCoordinationResponse",
    
    # Security coordination
    "SecurityCoordinationRequest",
    "SecurityCoordinationResponse",
    
    # Execution coordination
    "ExecutionCoordinationRequest",
    "ExecutionCoordinationResponse",
    
    # Monitoring coordination
    "MonitoringCoordinationRequest",
    "MonitoringCoordinationResponse",
    
    # Learning coordination
    "LearningCoordinationRequest",
    "LearningCoordinationResponse",
    
    # Recovery coordination
    "RecoveryCoordinationRequest",
    "RecoveryCoordinationResponse",
    
    # Alerting coordination
    "AlertingCoordinationRequest",
    "AlertingCoordinationResponse",
    
    # Default network coordination
    "DefaultNetworkCoordinationRequest",
    "DefaultNetworkCoordinationResponse",
    
    # Identity coordination
    "IdentityCoordinationRequest",
    "IdentityCoordinationResponse",
    
    # Memory coordination
    "MemoryCoordinationRequest",
    "MemoryCoordinationResponse",
    
    # World model coordination
    "WorldModelCoordinationRequest",
    "WorldModelCoordinationResponse",
    
    # Prediction coordination
    "PredictionCoordinationRequest",
    "PredictionCoordinationResponse",
    
    # Evaluation coordination
    "EvaluationCoordinationRequest",
    "EvaluationCoordinationResponse",
    
    # Executive state coordination
    "ExecutiveStateCoordinationRequest",
    "ExecutiveStateCoordinationResponse",
]