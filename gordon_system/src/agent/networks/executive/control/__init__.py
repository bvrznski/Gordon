# Gordon Executive Network - Phase 4.4.7 Control Allocation and Modulation
# ========================================================================

"""
Executive Control Allocation and Modulation Specification.

This is Phase 4.4.7: Executive Control Allocation and Modulation.

The Control Allocation subsystem determines:

    WHERE executive control is needed;
    WHY control is needed;
    WHICH executive structures should receive control;
    WHAT form that control should take;
    HOW strong the proposed control should be;
    HOW long the control should remain semantically active;
    WHICH control allocations should persist;
    WHICH allocations should be reduced or released;
    WHICH allocations are incompatible;
    WHICH allocations exceed safe executive capacity.

This phase is the canonical bridge between:

Executive Demand
        ↓
Control Allocation
        ↓
Control Modulation Proposals
        ↓
External owner review or execution
        ↓
Performance and outcome feedback

IMPORTANT:
==========
This phase allocates SEMANTIC executive control. It does NOT allocate:

    * CPU, GPU, memory;
    * tokens, processes, workers;
    * runtime time slices;
    * service capacity;
    * operating-system priority;
    * queue position.

The Control Allocation subsystem determines how Gordon's active cognitive
organization should be maintained, intensified, relaxed, redirected,
constrained, or released — without directly modifying any subsystem state.

ARCHITECTURAL PRINCIPLES:
========================

Semantic Control:
    Control is semantic regulation, NOT runtime orchestration.
    
Immutable Contracts:
    All contracts are deeply immutable dataclasses.
    
Proposal-Based External Effects:
    External effects occur through typed modulation proposals only.
    
Authority-Aware:
    Every allocation identifies explicit authority requirements.

Public API:
    Canonical contracts and proposals (no direct mutation)

VERSION: 1.0.0
COMPATIBILITY: forward (phased implementation)
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only

PHASE DEPENDENCIES:
==================
- Phase 4.4.1 — Executive Network Architecture and Ownership
- Phase 4.4.2 — Executive State and Executive Context
- Phase 4.4.3 — Executive Task Sets and Active Executive Programs
- Phase 4.4.4 — Goal, Commitment, and Priority Coordination
- Phase 4.4.5 — Conflict Monitoring and Executive Demand
- Phase 4.4.6 — Performance, Outcome, and Error Monitoring

PHASE PREPARES FOR:
==================
- Phase 4.4.8 — Cognitive Flexibility, Switching, and Inhibition
- Phase 4.4.9 — Strategy and Policy Coordination
- Phase 4.4.10 — Decision and Action-Selection Coordination
- Phase 4.4.11 — Attention, Motivation, Workspace, and Working-Memory Coordination
- Phase 4.4.12 — Executive Loop, Cycle, and Thread Integration
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, Literal, FrozenSet, Dict, Any
from enum import Enum, auto

# =============================================================================
# PHASE 4.4.7 - CANONICAL DEFINITIONS
# =============================================================================


@dataclass(frozen=True)
class ExecutiveControlSubject:
    """
    The executive reason or undertaking from which control derives.
    """

    subject_id: str
    """Unique identifier for the subject."""

    kind: Literal[
        "executive_program",
        "executive_task_set",
        "goal",
        "commitment",
        "priority_assessment",
        "executive_conflict",
        "executive_error",
        "executive_demand",
        "strategy",
        "plan",
        "reasoning_process",
        "decision_process",
        "action_selection",
        "recovery_process",
        "monitoring_process",
        "communication_process",
        "general_executive_state",
    ]
    """Semantic kind of the subject."""

    revision: int = 1
    """Current revision of the subject (for freshness checking)."""

    owner: Optional[str] = None
    """Owner authority reference for the subject (if external)."""


@dataclass(frozen=True)
class ExecutiveControlTarget:
    """
    The executive structure that should receive or be affected by control.
    """

    target_id: str
    """Unique identifier for the target."""

    kind: Literal[
        "executive_program",
        "executive_task_set",
        "goal_binding",
        "commitment_binding",
        "strategy",
        "rule",
        "constraint",
        "assumption",
        "hypothesis",
        "plan_review",
        "reasoning_engagement",
        "evidence_acquisition",
        "decision_preparation",
        "action_selection",
        "attention_review",
        "focus_stabilization",
        "focus_switch_review",
        "working_memory_maintenance",
        "working_memory_release_review",
        "workspace_review",
        "monitoring",
        "recovery",
        "communication_review",
        "policy_review",
        "security_review",
        "general_executive_state",
    ]
    """Semantic kind of the control target."""

    revision: int = 1
    """Current revision of the target (for freshness checking)."""

    owner: Optional[str] = None
    """Owner authority reference for the target (if external)."""

    scope: Literal["local", "global"] = "local"
    """Scope of the control effect."""

    factuality_class: str = "unknown"
    """Classification of factual accuracy."""

    privacy_classification: str = "internal"
    """Privacy classification of the target."""


@dataclass(frozen=True)
class ExecutiveControlSourceReference:
    """
    Reference to a source that generated demand or evidence for control.
    """

    source_id: str
    """Unique identifier for the source."""

    kind: Literal[
        "executive_demand",
        "executive_priority",
        "executive_conflict",
        "executive_error",
        "performance_assessment",
        "outcome_assessment",
        "progress_assessment",
        "completion_assessment",
        "stagnation_assessment",
        "regression_assessment",
        "policy_requirement",
        "security_requirement",
        "user_request",
        "authority_decision",
        "monitoring_result",
        "attention_projection",
        "motivational_projection",
        "working_memory_projection",
        "workspace_feedback",
        "prediction_error",
        "recovery_result",
        "general_executive_evidence",
    ]
    """Semantic kind of the source."""

    revision: int = 1
    """Revision of the source (for freshness)."""

    lineage_id: Optional[str] = None
    """ID of causal lineage (if any)."""

    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence items."""


class ExecutiveControlMode(Enum):
    """Semantic modes for executive control."""

    MAINTAIN = "maintain"
    STABILIZE = "stabilize"
    INTENSIFY = "intensify"
    RELAX = "relax"
    REDIRECT = "redirect"
    DISTRIBUTE = "distribute"
    CONCENTRATE = "concentrate"
    GATE = "gate"
    FACILITATE = "facilitate"
    ATTENUATE = "attenuate"
    SUPPRESS_REVIEW = "suppress_review"
    MONITOR = "monitor"
    RECOVER = "recover"
    PREPARE_SWITCH = "prepare_switch"
    PREPARE_DECISION = "prepare_decision"
    RELEASE = "release"
    SUSPEND = "suspend"
    RESTORE = "restore"
    NO_CONTROL_CHANGE = "no_control_change"


class ExecutiveControlPurpose(Enum):
    """Semantic purposes for executive control."""

    MAINTAIN_PROGRAM = "maintain_program"
    MAINTAIN_TASK_SET = "maintain_task_set"
    PRESERVE_GOAL = "preserve_goal"
    PRESERVE_COMMITMENT = "preserve_commitment"
    REDUCE_CONFLICT = "reduce_conflict"
    REDUCE_ERROR = "reduce_error"
    REDUCE_UNCERTAINTY = "reduce_uncertainty"
    ACQUIRE_EVIDENCE = "acquire_evidence"
    IMPROVE_PERFORMANCE = "improve_performance"
    PREVENT_REGRESSION = "prevent_regression"
    BREAK_STAGNATION = "break_stagnation"
    PREPARE_DECISION = "prepare_decision"
    PREPARE_ACTION_SELECTION = "prepare_action_selection"
    SUPPORT_WORKING_MEMORY = "support_working_memory"
    REQUEST_ATTENTION_REVIEW = "request_attention_review"
    STABILIZE_FOCUS = "stabilize_focus"
    PREPARE_SWITCH = "prepare_switch"
    SUPPORT_RECOVERY = "support_recovery"
    MONITOR_RISK = "monitor_risk"
    PRESERVE_POLICY_COMPLIANCE = "preserve_policy_compliance"
    PRESERVE_SECURITY_COMPLIANCE = "preserve_security_compliance"
    PREPARE_COMPLETION = "prepare_completion"
    RELEASE_OBSOLETE_CONTROL = "release_obsolete_control"
    GENERAL_EXECUTIVE_REGULATION = "general_executive_regulation"


class ExecutiveControlDimension(Enum):
    """Dimensions along which control may be applied."""

    ACTIVATION = "activation"
    MAINTENANCE = "maintenance"
    PERSISTENCE = "persistence"
    ACCESSIBILITY = "accessibility"
    SELECTION_BIAS = "selection_bias"
    INTERFERENCE_REDUCTION = "interference_reduction"
    EVIDENCE_ACQUISITION = "evidence_acquisition"
    UNCERTAINTY_REDUCTION = "uncertainty_reduction"
    CONFLICT_REVIEW = "conflict_review"
    ERROR_REVIEW = "error_review"
    PERFORMANCE_REVIEW = "performance_review"
    DECISION_PREPARATION = "decision_preparation"
    ACTION_GATING = "action_gating"
    ATTENTION_REVIEW = "attention_review"
    WORKING_MEMORY_SUPPORT = "working_memory_support"
    MONITORING = "monitoring"
    RECOVERY = "recovery"
    COMMUNICATION_REVIEW = "communication_review"
    AUTHORITY_REVIEW = "authority_review"
    CONTROL_RELEASE = "control_release"
    UNKNOWN = "unknown"


class ExecutiveControlIntensity(Enum):
    """Intensity levels for executive control."""

    NONE = "none"
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    SEVERE = "severe"
    MAXIMUM_SAFE = "maximum_safe"
    UNKNOWN = "unknown"


class ExecutiveControlPersistence(Enum):
    """Persistence statuses for executive control."""

    TRANSIENT = "transient"
    SINGLE_ASSESSMENT = "single_assessment"
    SHORT_TERM = "short_term"
    PERSISTENT = "persistent"
    UNTIL_RESULT = "until_result"
    UNTIL_AUTHORITY_DECISION = "until_authority_decision"
    UNTIL_CONFLICT_RESOLVED = "until_conflict_resolved"
    UNTIL_ERROR_RECOVERED = "until_error_recovered"
    UNTIL_GOAL_REVIEW = "until_goal_review"
    UNTIL_PROGRAM_COMPLETION = "until_program_completion"
    RELEASE_RECOMMENDED = "release_recommended"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class ExecutiveControlUrgency(Enum):
    """Urgency levels for executive control."""

    NONE = "none"
    LOW = "low"
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    IMMEDIATE_REVIEW = "immediate_review"
    BLOCKING = "blocking"
    UNKNOWN = "unknown"


class ExecutiveControlScope:
    """Semantic scope of control allocation."""

    LOCAL_PROGRAM = "local_program"
    MULTIPLE_PROGRAMS = "multiple_programs"
    LOCAL_TASK_SET = "local_task_set"
    MULTIPLE_TASK_SETS = "multiple_task_sets"
    SINGLE_GOAL = "single_goal"
    SINGLE_COMMITMENT = "single_commitment"
    SINGLE_STRATEGY = "single_strategy"
    SINGLE_DECISION = "single_decision"
    SINGLE_ACTION_SELECTION = "single_action_selection"
    LOCAL_THREAD = "local_thread"
    LOCAL_TASK = "local_task"
    LOCAL_CONVERSATION = "local_conversation"
    PARTICIPANT_SCOPE = "participant_scope"
    TEMPORAL_SCOPE = "temporal_scope"
    AUTHORITY_SCOPE = "authority_scope"
    PRIVACY_SCOPE = "privacy_scope"

    @classmethod
    def is_local(cls, scope: str) -> bool:
        return scope.startswith("local_") or scope == cls.SINGLE_GOAL

    @classmethod
    def is_global(cls, scope: str) -> bool:
        return not cls.is_local(scope)


class ExecutiveControlDirection(Enum):
    """Direction of control change."""

    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"
    REDIRECT = "redirect"
    DISTRIBUTE = "distribute"
    CONCENTRATE = "concentrate"
    RELEASE = "release"
    SUSPEND = "suspend"
    RESTORE = "restore"
    NO_CHANGE = "no_change"
    UNKNOWN = "unknown"


class ExecutiveControlEligibilityAssessment(Enum):
    """Eligibility assessment for control allocations."""

    ELIGIBLE = "eligible"
    ELIGIBLE_WITH_CONDITIONS = "eligible_with_conditions"
    REQUIRES_AUTHORITY = "requires_authority"
    REQUIRES_EVIDENCE = "requires_evidence"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    BLOCKED_BY_SECURITY = "blocked_by_security"
    INCOMPATIBLE = "incompatible"
    STALE_TARGET = "stale_target"
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"


class ExecutiveControlCompatibilityAssessment(Enum):
    """Compatibility assessment between allocations."""

    COMPATIBLE = "compatible"
    COMPATIBLE_WITH_LIMITATIONS = "compatible_with_limitations"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    INCOMPATIBLE = "incompatible"
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"
    AUTHORITY_DEPENDENT = "authority_dependent"
    UNKNOWN = "unknown"


class ExecutiveControlCapacity(Enum):
    """Semantic executive capacity status."""

    AVAILABLE = "available"
    LIMITED = "limited"
    CONSTRAINED = "constrained"
    NEAR_CAPACITY = "near_capacity"
    SATURATED = "saturated"
    OVERCOMMITTED = "overcommitted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveControlCompetition:
    """Control competition between executive subjects."""

    competitor_ids: Tuple[str, ...]
    priority_values: Tuple[float, ...] = field(default_factory=tuple)
    demand_values: Tuple[float, ...] = field(default_factory=tuple)
    authority_weights: Tuple[str, ...] = field(default_factory=tuple)
    compatibility_assessments: Tuple[str, ...] = field(default_factory=tuple)
    capacity_impact: str = "unknown"
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    confidence_class: str = "unknown"
    provenance_id: Optional[str] = None


@dataclass(frozen=True)
class ExecutiveControlConflict:
    """Control conflicts between allocations."""

    conflict_id: str
    kind: Literal[
        "target_conflict",
        "purpose_conflict",
        "intensity_conflict",
        "persistence_conflict",
        "authority_conflict",
        "policy_conflict",
        "security_conflict",
        "capacity_conflict",
        "program_conflict",
        "task_set_conflict",
        "goal_conflict",
        "commitment_conflict",
        "attention_conflict",
        "working_memory_conflict",
        "decision_conflict",
        "recovery_conflict",
    ]
    allocation_a_id: str
    allocation_b_id: str
    resolution_authority: str = "executive_network_internal"


@dataclass(frozen=True)
class ExecutiveControlDependency:
    """Dependencies between control allocations."""

    dependency_id: str
    kind: Literal[
        "requires",
        "precedes",
        "follows",
        "depends_on_result",
        "depends_on_authority",
        "depends_on_evidence",
        "depends_on_conflict_resolution",
        "depends_on_error_recovery",
        "blocked_by",
        "enables",
        "releases",
        "supersedes",
    ]
    dependent_allocation_id: str
    depended_upon_allocation_id: str
    condition_description: Optional[str] = None


class ExecutiveControlAllocationId:
    """Unique identifier for an executive control allocation."""

    value: str

    @classmethod
    def generate(cls) -> "ExecutiveControlAllocationId":
        import uuid
        return cls(value=f"alloc_{uuid.uuid4().hex[:16]}")


class ExecutiveControlAllocationRevision:
    """Revision tracking for executive control allocations."""

    number: int = 1
    source_id: Optional[str] = None

    @classmethod
    def initial(cls) -> "ExecutiveControlAllocationRevision":
        return cls(number=1)

    @classmethod
    def from_source(cls, source_id: str, base_number: int = 1) -> "ExecutiveControlAllocationRevision":
        return cls(number=base_number, source_id=source_id)


class ExecutiveControlAllocationStatus(Enum):
    """Status of an executive control allocation."""

    PROPOSED = "proposed"
    VALIDATING = "validating"
    ELIGIBLE = "eligible"
    ACCEPTED_INTERNAL = "accepted_internal"
    WAITING_FOR_AUTHORITY = "waiting_for_authority"
    ACTIVE = "active"
    PARTIALLY_ACTIVE = "partially_active"
    SUSPENDED = "suspended"
    REDUCTION_PROPOSED = "reduction_proposed"
    RELEASE_PROPOSED = "release_proposed"
    RELEASED = "released"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"
    INVALID = "invalid"


class ExecutiveControlAllocationAssessment(Enum):
    """Assessment outcome for control allocations."""

    ALLOCATION_JUSTIFIED = "allocation_justified"
    ALLOCATION_JUSTIFIED_WITH_LIMITATIONS = "allocation_justified_with_limitations"
    MAINTAIN_EXISTING_ALLOCATION = "maintain_existing_allocation"
    REDUCE_EXISTING_ALLOCATION = "reduce_existing_allocation"
    REDIRECT_EXISTING_ALLOCATION = "redirect_existing_allocation"
    RELEASE_EXISTING_ALLOCATION = "release_existing_allocation"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REQUIRES_AUTHORITY = "requires_authority"
    INCOMPATIBLE = "incompatible"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    NOT_JUSTIFIED = "not_justified"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveControlComposition:
    """Control composition combines compatible control allocations."""

    composition_id: str
    constituent_allocation_ids: Tuple[str, ...]
    combined_intensity: str
    capacity_impact: str
    conflicting_allocations: Tuple[str, ...] = field(default_factory=tuple)
    provenance_id: Optional[str] = None


@dataclass(frozen=True)
class ExecutiveControlDecomposition:
    """A broad demand decomposed into component allocations."""

    decomposition_id: str
    original_demand_id: str
    component_allocations: Tuple[Dict[str, Any], ...]
    max_depth: int
    omitted_components_summary: Optional[str] = None


@dataclass(frozen=True)
class ExecutiveControlDistribution:
    """Control distribution pattern across targets."""

    distribution_id: str
    allocation_ids: Tuple[str, ...]
    distribution_pattern: Literal[
        "single_target",
        "primary_and_supporting",
        "balanced_multi_target",
        "priority_weighted",
        "demand_weighted",
        "authority_constrained",
        "capacity_constrained",
        "temporary_distribution",
        "review_only",
    ]
    weights: Optional[Tuple[float, ...]] = None


class ExecutiveControlReallocationAssessment(Enum):
    """Assessment of need for reallocation."""

    REALLOCATION_JUSTIFIED = "reallocation_justified"
    MAINTAIN_EXISTING = "maintain_existing"
    REDUCTION_RECOMMENDED = "reduction_recommended"
    INTENSIFICATION_RECOMMENDED = "intensification_recommended"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REQUIRES_AUTHORITY = "requires_authority"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveControlReallocationProposal:
    """Proposal for reallocation."""

    proposal_id: str
    source_allocation_id: str
    target_allocation_ids: Tuple[str, ...]
    reallocation_kind: Literal[
        "intensify",
        "relax",
        "redirect",
        "distribute",
        "release",
    ]
    new_intensity: Optional[str] = None
    new_targets: Optional[Tuple[str, ...]] = None


@dataclass(frozen=True)
class ExecutiveControlIntensificationAssessment:
    """Assessment of need for intensification."""

    assessment_id: str
    allocation_id: str
    is_justified: bool
    justification_reasons: Tuple[str, ...]
    capacity_check_result: str
    prior_effectiveness: Optional[str] = None
    saturation_check_result: Optional[str] = None


@dataclass(frozen=True)
class ExecutiveControlIntensificationProposal:
    """Proposal for intensification."""

    proposal_id: str
    allocation_id: str
    new_intensity: str
    justification_reasons: Tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveControlRelaxationAssessment:
    """Assessment of need for relaxation."""

    assessment_id: str
    allocation_id: str
    is_justified: bool
    justification_reasons: Tuple[str, ...]
    mandatory_controls_preserved: bool


@dataclass(frozen=True)
class ExecutiveControlRelaxationProposal:
    """Proposal for relaxation."""

    proposal_id: str
    allocation_id: str
    new_intensity: Optional[str] = None
    release_conditions: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutiveControlStabilizationAssessment:
    """Assessment of need for stabilization."""

    assessment_id: str
    current_variability_class: str
    is_stabilization_justified: bool
    recommended_stable_intensity: Optional[str] = None


@dataclass(frozen=True)
class ExecutiveControlStabilizationProposal:
    """Proposal for stabilization."""

    proposal_id: str
    target_allocation_ids: Tuple[str, ...]
    stable_intensity: str
    expected_variability_reduction: Optional[float] = None


@dataclass(frozen=True)
class ExecutiveControlSuspensionAssessment:
    """Assessment of need for suspension."""

    assessment_id: str
    allocation_id: str
    is_suspension_justified: bool
    justification_reasons: Tuple[str, ...]
    restoration_conditions: Tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveControlSuspensionProposal:
    """Proposal for suspension."""

    proposal_id: str
    allocation_id: str
    suspension_duration: Optional[str] = None


@dataclass(frozen=True)
class ExecutiveControlRestorationAssessment:
    """Assessment of need for restoration."""

    assessment_id: str
    suspended_allocation_id: str
    is_restoration_justified: bool
    justification_reasons: Tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveControlRestorationProposal:
    """Proposal for restoration."""

    proposal_id: str
    suspended_allocation_id: str
    restored_intensity: Optional[str] = None


@dataclass(frozen=True)
class ExecutiveControlReleaseAssessment:
    """Assessment of need for release."""

    assessment_id: str
    allocation_id: str
    is_release_justified: bool
    release_reasons: Tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveControlReleaseProposal:
    """Proposal for control release."""

    proposal_id: str
    allocation_id: str
    release_conditions_satisfied: Tuple[str, ...]
    followup_actions: Tuple[str, ...] = field(default_factory=tuple)


class ExecutiveControlReleaseCondition(Enum):
    """Conditions under which control should be released."""

    TARGET_COMPLETED = "target_completed"
    CONFLICT_RESOLVED = "conflict_resolved"
    ERROR_RECOVERED = "error_recovered"
    EVIDENCE_ACQUIRED = "evidence_acquired"
    AUTHORITY_DECISION_RECEIVED = "authority_decision_received"
    PROGRAM_TERMINATED = "program_terminated"
    TASK_SET_REPLACED = "task_set_replaced"
    ALLOCATION_SUPERSEDED = "allocation_superseded"
    CONTROL_INEFFECTIVE = "control_ineffective"
    CONTROL_EXCESSIVE = "control_excessive"
    EXPIRATION_REACHED = "expiration_reached"
    POLICY_CHANGED = "policy_changed"
    SECURITY_REQUIREMENT_CHANGED = "security_requirement_changed"


@dataclass(frozen=True)
class ExecutiveControlExpiration:
    """Expiration conditions for control allocations."""

    expiration_id: str
    allocation_id: str
    expiration_kind: Literal[
        "time_bound",
        "event_bound",
        "result_bound",
        "authority_bound",
        "program_bound",
        "task_set_bound",
        "conflict_bound",
        "error_bound",
        "monitoring_bound",
    ]
    expiration_value: Optional[str] = None


@dataclass(frozen=True)
class TopDownModulationProposal:
    """
    A top-down modulation proposal to alter a target's activation or state.

    A modulation proposal must not contain:
        * callback;
        * concrete provider;
        * service endpoint;
        * mutable subsystem object;
        * runtime queue;
        * execution command.
    """

    proposal_id: str
    target_id: str
    target_kind: str
    target_revision: int
    modulation_kind: Literal[
        "maintenance",
        "stabilization",
        "facilitation",
        "amplification",
        "attenuation",
        "suppression_review",
        "gating",
        "release",
        "refresh",
        "accessibility_increase",
        "accessibility_decrease",
        "evidence_acquisition",
        "monitoring_increase",
        "monitoring_decrease",
        "review_request",
        "switch_preparation",
        "recovery_support",
        "decision_support",
    ]
    direction: Literal["increase", "decrease", "maintain"]
    requested_intensity: str
    persistence: str
    purpose: Optional[str] = None
    supporting_allocation_id: Optional[str] = None
    expected_effect: Optional[str] = None
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    authority_required: Optional[str] = None
    expiration: Optional[str] = None
    confidence_class: str = "unknown"
    limitations: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutiveFacilitationProposal:
    """Proposal to facilitate a target's engagement."""

    proposal_id: str
    target_kind: Literal[
        "planning",
        "reasoning",
        "evidence_acquisition",
        "decision_preparation",
        "working_memory_maintenance",
        "focus_stabilization",
        "monitoring",
        "recovery",
        "communication_preparation",
    ]
    intensity: str
    persistence: str


@dataclass(frozen=True)
class ExecutiveAttenuationProposal:
    """Proposal to attenuate a target's engagement."""

    proposal_id: str
    target_kind: Literal[
        "low_value_cognitive_engagement",
        "repetitive_reasoning",
        "resolved_conflict_review",
        "obsolete_monitoring",
        "superseded_strategy_support",
        "excessive_control",
        "low_relevance_workspace_review",
        "stale_evidence_maintenance",
    ]
    intensity: str
    release_conditions: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutiveGatingProposal:
    """Proposal to gate a target's progression."""

    proposal_id: str
    target_kind: Literal[
        "decision_commitment",
        "action_selection_progression",
        "communication_release",
        "program_activation",
        "task_set_activation",
        "strategy_commitment",
        "completion_acceptance",
    ]
    gate_status: Literal["open", "open_with_conditions", "review_required", "hold", "block_proposed", "authority_required"]
    conditions: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutiveMaintenanceProposal:
    """Proposal to maintain a target's active relevance."""

    proposal_id: str
    target_kind: Literal[
        "goal_binding",
        "commitment_binding",
        "task_set_rule",
        "assumption",
        "hypothesis",
        "working_memory_reference",
        "focus_requirement",
        "monitoring_condition",
        "decision_criterion",
    ]
    persistence: str


@dataclass(frozen=True)
class ExecutiveBiasProposal:
    """Proposal to express a relative preference toward a target."""

    proposal_id: str
    target_kind: Literal[
        "executive_program",
        "goal",
        "decision_criterion",
        "evidence_source",
        "strategy_review_path",
        "action_selection_constraint",
        "working_memory_item",
        "focus_candidate",
    ]
    preference_strength: str


class ExecutiveControlAllocationRequestPurpose(Enum):
    """Purposes for control allocation requests."""

    ASSESS_CONTROL_NEED = "assess_control_need"
    ALLOCATE_CONTROL = "allocate_control"
    REASSESS_CONTROL = "reassess_control"
    INTENSIFY_CONTROL = "intensify_control"
    RELAX_CONTROL = "relax_control"
    REDIRECT_CONTROL = "redirect_control"
    DISTRIBUTE_CONTROL = "distribute_control"
    STABILIZE_CONTROL = "stabilize_control"
    SUSPEND_CONTROL = "suspend_control"
    RESTORE_CONTROL = "restore_control"
    RELEASE_CONTROL = "release_control"
    ASSESS_CONTROL_CAPACITY = "assess_control_capacity"
    ASSESS_CONTROL_COMPATIBILITY = "assess_control_compatibility"
    PREPARE_MODULATION = "prepare_modulation"
    GENERAL_CONTROL_COORDINATION = "general_control_coordination"


@dataclass(frozen=True)
class ExecutiveControlAllocationRequest:
    """Request for control allocation processing."""

    request_id: str
    purpose: ExecutiveControlAllocationRequestPurpose
    executive_state_reference_id: Optional[str] = None
    executive_context_reference_id: Optional[str] = None
    program_references: Tuple[str, ...] = field(default_factory=tuple)
    task_set_references: Tuple[str, ...] = field(default_factory=tuple)
    demand_references: Tuple[str, ...] = field(default_factory=tuple)
    conflict_references: Tuple[str, ...] = field(default_factory=tuple)
    error_references: Tuple[str, ...] = field(default_factory=tuple)
    performance_references: Tuple[str, ...] = field(default_factory=tuple)
    priority_references: Tuple[str, ...] = field(default_factory=tuple)
    existing_allocation_ids: Tuple[str, ...] = field(default_factory=tuple)
    authority_decisions: Tuple[str, ...] = field(default_factory=tuple)
    scope: Optional[str] = None
    expected_products: Tuple[str, ...] = field(default_factory=tuple)


class ExecutiveControlAllocationScope:
    """Bounded limits for control allocation processing."""

    max_programs: int = 10
    max_task_sets: int = 20
    max_targets: int = 50
    max_demands: int = 100
    max_allocations: int = 100
    max_active_allocations: int = 50
    max_dimensions: int = 20
    max_dependencies: int = 30
    max_compatibility_comparisons: int = 100
    max_competitions: int = 20
    max_conflicts: int = 30
    max_modulation_proposals: int = 50
    max_release_proposals: int = 20
    temporal_scope_seconds: float = 3600.0
    thread_scope_limit: int = 10
    authority_scope_limit: int = 5


class ExecutiveControlAllocationPlan:
    """Declarative plan for control allocation processing."""

    plan_id: str
    steps: Tuple[str, ...]
    validation_required: bool = True
    boundedness_check_required: bool = True
    determinism_guaranteed: bool = True


class ExecutiveControlAllocationProduct(Enum):
    """Products that can be produced by control allocation."""

    CONTROL_NEED_ASSESSMENT = "control_need_assessment"
    CONTROL_ELIGIBILITY_ASSESSMENT = "control_eligibility_assessment"
    CONTROL_COMPATIBILITY_ASSESSMENT = "control_compatibility_assessment"
    CONTROL_CAPACITY_ASSESSMENT = "control_capacity_assessment"
    CONTROL_COMPETITION = "control_competition"
    CONTROL_CONFLICT = "control_conflict"
    CONTROL_ALLOCATION = "control_allocation"
    CONTROL_ALLOCATION_ASSESSMENT = "control_allocation_assessment"
    CONTROL_COMPOSITION = "control_composition"
    CONTROL_DECOMPOSITION = "control_decomposition"
    CONTROL_DISTRIBUTION = "control_distribution"
    CONTROL_REALLOCATION_ASSESSMENT = "control_reallocation_assessment"
    CONTROL_INTENSIFICATION_ASSESSMENT = "control_intensification_assessment"
    CONTROL_RELAXATION_ASSESSMENT = "control_relaxation_assessment"
    CONTROL_STABILIZATION_ASSESSMENT = "control_stabilization_assessment"
    CONTROL_SUSPENSION_ASSESSMENT = "control_suspension_assessment"
    CONTROL_RESTORATION_ASSESSMENT = "control_restoration_assessment"
    CONTROL_RELEASE_ASSESSMENT = "control_release_assessment"
    TOP_DOWN_MODULATION_PROPOSAL = "top_down_modulation_proposal"
    FACILITATION_PROPOSAL = "facilitation_proposal"
    ATTENUATION_PROPOSAL = "attenuation_proposal"
    GATING_PROPOSAL = "gating_proposal"
    MAINTENANCE_PROPOSAL = "maintenance_proposal"
    BIAS_PROPOSAL = "bias_proposal"
    NO_MEANINGFUL_RESULT = "no_meaningful_result"


class ExecutiveControlAllocationOutcome(Enum):
    """Outcomes of control allocation processing."""

    CONTROL_ALLOCATED_INTERNALLY = "control_allocated_internally"
    CONTROL_ALLOCATION_PROPOSED = "control_allocation_proposed"
    CONTROL_MAINTAINED = "control_maintained"
    CONTROL_INTENSIFICATION_PROPOSED = "control_intensification_proposed"
    CONTROL_RELAXATION_PROPOSED = "control_relaxation_proposed"
    CONTROL_REDIRECTION_PROPOSED = "control_redirection_proposed"
    CONTROL_DISTRIBUTION_PROPOSED = "control_distribution_proposed"
    CONTROL_STABILIZATION_PROPOSED = "control_stabilization_proposed"
    CONTROL_SUSPENSION_PROPOSED = "control_suspension_proposed"
    CONTROL_RESTORATION_PROPOSED = "control_restoration_proposed"
    CONTROL_RELEASE_PROPOSED = "control_release_proposed"
    MODULATION_PROPOSED = "modulation_proposed"
    GATING_REVIEW_PROPOSED = "gating_review_proposed"
    MAINTENANCE_PROPOSED = "maintenance_proposed"
    FACILITATION_PROPOSED = "facilitation_proposed"
    ATTENUATION_PROPOSED = "attenuation_proposed"
    CAPACITY_LIMIT_IDENTIFIED = "capacity_limit_identified"
    CONTROL_CONFLICT_IDENTIFIED = "control_conflict_identified"
    OVERLOAD_IDENTIFIED = "overload_identified"
    PARTIAL_PROGRESS = "partial_progress"
    WAITING_FOR_CONTEXT = "waiting_for_context"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    WAITING_FOR_AUTHORITY = "waiting_for_authority"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NO_CONTROL_CHANGE = "no_control_change"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ExecutiveControlAllocationContinuation(Enum):
    """Advisory continuation recommendations."""

    COMPLETE = "complete"
    CONTINUE_CONTROL_ASSESSMENT = "continue_control_assessment"
    REASSESS_CONTROL = "reassess_control"
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    REQUEST_DEMAND_REASSESSMENT = "request_demand_reassessment"
    REQUEST_CONFLICT_REASSESSMENT = "request_conflict_reassessment"
    REQUEST_PERFORMANCE_REASSESSMENT = "request_performance_reassessment"
    REQUEST_ERROR_REASSESSMENT = "request_error_reassessment"
    REQUEST_PRIORITY_REVIEW = "request_priority_review"
    REQUEST_PROGRAM_REVIEW = "request_program_review"
    REQUEST_TASK_SET_REVIEW = "request_task_set_review"
    REQUEST_STRATEGY_REVIEW = "request_strategy_review"
    REQUEST_ATTENTION_REVIEW = "request_attention_review"
    REQUEST_WORKING_MEMORY_REVIEW = "request_working_memory_review"
    REQUEST_WORKSPACE_REVIEW = "request_workspace_review"
    REQUEST_DECISION_REVIEW = "request_decision_review"
    REQUEST_ACTION_SELECTION_REVIEW = "request_action_selection_review"
    REQUEST_SWITCH_REVIEW = "request_switch_review"
    REQUEST_INHIBITION_REVIEW = "request_inhibition_review"
    REQUEST_MONITORING = "request_monitoring"
    REQUEST_RECOVERY = "request_recovery"
    REQUEST_POLICY_REVIEW = "request_policy_review"
    REQUEST_SECURITY_REVIEW = "request_security_review"
    REQUEST_AUTHORITY_REVIEW = "request_authority_review"
    WAIT_FOR_RESULT = "wait_for_result"
    WAIT_FOR_AUTHORITY = "wait_for_authority"
    SUSPEND = "suspend"
    FAIL = "fail"
    CANCEL = "cancel"


@dataclass(frozen=True)
class ExecutiveControlState:
    """Bounded control state subordinate to canonical ExecutiveState."""

    state_id: str
    active_internal_allocation_ids: Tuple[str, ...]
    pending_modulation_proposal_ids: Tuple[str, ...]
    suspended_allocation_ids: Tuple[str, ...]
    allocations_waiting_for_authority: Tuple[str, ...]
    allocation_conflict_ids: Tuple[str, ...]
    capacity_summary: str
    competition_summary: Optional[str] = None
    latest_effectiveness_assessment_id: Optional[str] = None
    latest_release_assessment_id: Optional[str] = None
    superseded_allocation_ids: Tuple[str, ...] = field(default_factory=tuple)
    active_composition_id: Optional[str] = None
    active_distribution_id: Optional[str] = None
    executive_state_revision: int = 1
    executive_context_revision: int = 1
    control_state_revision: int = 1


@dataclass(frozen=True)
class ExecutiveControlHistory:
    """Bounded history of control allocations and transitions."""

    history_id: str
    entries: Tuple[Dict[str, Any], ...]
    max_entries: int = 1000

    def append(self, entry: Dict[str, Any]) -> "ExecutiveControlHistory":
        new_entries = self.entries + (entry,)
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        return ExecutiveControlHistory(
            history_id=self.history_id,
            entries=new_entries,
            max_entries=self.max_entries,
        )


# =============================================================================
# EXPORTS - Canonical public API
# =============================================================================

__all__: Tuple[str, ...] = (
    # Subjects, targets, sources
    "ExecutiveControlSubject",
    "ExecutiveControlTarget",
    "ExecutiveControlSourceReference",

    # Control properties
    "ExecutiveControlMode",
    "ExecutiveControlPurpose",
    "ExecutiveControlDimension",
    "ExecutiveControlDirection",
    "ExecutiveControlIntensity",
    "ExecutiveControlPersistence",
    "ExecutiveControlUrgency",
    "ExecutiveControlScope",
    "ExecutiveControlEligibilityAssessment",
    "ExecutiveControlCompatibilityAssessment",
    "ExecutiveControlCapacity",

    # Competition, conflict, dependency
    "ExecutiveControlCompetition",
    "ExecutiveControlConflict",
    "ExecutiveControlDependency",

    # Allocation identity and status
    "ExecutiveControlAllocationId",
    "ExecutiveControlAllocationRevision",
    "ExecutiveControlAllocationStatus",
    "ExecutiveControlAllocationAssessment",

    # Composition and distribution
    "ExecutiveControlComposition",
    "ExecutiveControlDecomposition",
    "ExecutiveControlDistribution",

    # Reallocation lifecycle
    "ExecutiveControlReallocationAssessment",
    "ExecutiveControlReallocationProposal",
    "ExecutiveControlIntensificationAssessment",
    "ExecutiveControlIntensificationProposal",
    "ExecutiveControlRelaxationAssessment",
    "ExecutiveControlRelaxationProposal",
    "ExecutiveControlStabilizationAssessment",
    "ExecutiveControlStabilizationProposal",
    "ExecutiveControlSuspensionAssessment",
    "ExecutiveControlSuspensionProposal",
    "ExecutiveControlRestorationAssessment",
    "ExecutiveControlRestorationProposal",
    "ExecutiveControlReleaseAssessment",
    "ExecutiveControlReleaseProposal",
    "ExecutiveControlReleaseCondition",
    "ExecutiveControlExpiration",

    # Modulation proposals
    "TopDownModulationProposal",
    "ExecutiveFacilitationProposal",
    "ExecutiveAttenuationProposal",
    "ExecutiveGatingProposal",
    "ExecutiveMaintenanceProposal",
    "ExecutiveBiasProposal",

    # Request and plan
    "ExecutiveControlAllocationRequestPurpose",
    "ExecutiveControlAllocationRequest",
    "ExecutiveControlAllocationScope",
    "ExecutiveControlAllocationPlan",

    # Products and outcomes
    "ExecutiveControlAllocationProduct",
    "ExecutiveControlAllocationOutcome",
    "ExecutiveControlAllocationContinuation",

    # State and history
    "ExecutiveControlState",
    "ExecutiveControlHistory",
)