# Gordon Executive Network - Control Allocation Models
# =====================================================

"""
Control Allocation models for Phase 4.4.7.

This module contains the canonical immutable control allocation model and related
types for determining semantic executive control configuration.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, Literal, FrozenSet
from enum import Enum, auto


@dataclass(frozen=True)
class ExecutiveControlAllocation:
    """
    Immutable representation of an executive control allocation.

    An allocation answers:

        Which target should receive control?
        What kind of control should it receive?
        How strong should that control be?
        How persistent should it be?
        Which competing allocations should be reduced?
        Which external owner must review or apply the resulting proposal?
    """

    # Identity
    allocation_id: str
    revision: int = 1
    schema_version: str = "1.0.0"

    # Core allocation data
    subject: str  # ExecutiveControlSubject reference
    targets: Tuple[str, ...]
    sources: Tuple[str, ...]  # ExecutiveControlSourceReference references

    purpose: str  # ExecutiveControlPurpose value
    mode: str  # ExecutiveControlMode value
    dimensions: Tuple[str, ...]  # ExecutiveControlDimension values
    direction: str  # ExecutiveControlDirection value

    intensity: str  # ExecutiveControlIntensity value
    persistence: str  # ExecutiveControlPersistence value
    urgency: str  # ExecutiveControlUrgency value
    scope: str  # ExecutiveControlScope value

    # Assessments
    eligibility: str  # ExecutiveControlEligibilityAssessment value
    compatibility: str  # ExecutiveControlCompatibilityAssessment value
    dependencies: Tuple[str, ...] = field(default_factory=tuple)  # Dependency IDs

    authority: Optional[str] = None
    status: str = "proposed"  # ExecutiveControlAllocationStatus value

    # Evidence
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    opposing_evidence: Tuple[str, ...] = field(default_factory=tuple)

    # Quality metrics
    confidence_class: str = "unknown"
    completeness_class: str = "unknown"
    limitations: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_internal(self) -> bool:
        """Check if this allocation applies internally."""
        return self.authority is None or self.authority == "executive_network_internal"

    @property
    def is_external_proposal(self) -> bool:
        """Check if this allocation requires external review."""
        return not self.is_internal

    @classmethod
    def initial(
        cls,
        subject: str,
        targets: Tuple[str, ...],
        sources: Tuple[str, ...],
        purpose: str,
        mode: str = "maintain",
        intensity: str = "moderate",
        persistence: str = "short_term",
        urgency: str = "normal",
        scope: str = "local_program",
    ) -> "ExecutiveControlAllocation":
        """Create an initial allocation with minimal required fields."""
        return cls(
            allocation_id=f"alloc_{cls._generate_id()}",
            subject=subject,
            targets=targets,
            sources=sources,
            purpose=purpose,
            mode=mode,
            intensity=intensity,
            persistence=persistence,
            urgency=urgency,
            scope=scope,
        )

    @classmethod
    def _generate_id(cls) -> str:
        """Generate a unique allocation ID."""
        import uuid
        return f"alloc_{uuid.uuid4().hex[:16]}"


@dataclass(frozen=True)
class ExecutiveControlAllocationRequest:
    """Request for control allocation processing."""

    request_id: str
    purpose: Literal[
        "assess_control_need",
        "allocate_control",
        "reassess_control",
        "intensify_control",
        "relax_control",
        "redirect_control",
        "distribute_control",
        "stabilize_control",
        "suspend_control",
        "restore_control",
        "release_control",
        "assess_control_capacity",
        "assess_control_compatibility",
        "prepare_modulation",
        "general_control_coordination",
    ]
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


@dataclass(frozen=True)
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
    entries: Tuple[dict, ...]
    max_entries: int = 1000

    def append(self, entry: dict) -> "ExecutiveControlHistory":
        new_entries = self.entries + (entry,)
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        return ExecutiveControlHistory(
            history_id=self.history_id,
            entries=new_entries,
            max_entries=self.max_entries,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveControlAllocation",
    "ExecutiveControlAllocationRequest",
    "ExecutiveControlAllocationScope",
    "ExecutiveControlAllocationPlan",
    "ExecutiveControlAllocationProduct",
    "ExecutiveControlAllocationOutcome",
    "ExecutiveControlAllocationContinuation",
    "ExecutiveControlState",
    "ExecutiveControlHistory",
)